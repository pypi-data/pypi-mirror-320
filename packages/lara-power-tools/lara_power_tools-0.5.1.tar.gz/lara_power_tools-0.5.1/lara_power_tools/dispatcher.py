import threading
import time
from collections import deque
from datetime import datetime
from typing import Generator, Union
import json

import boto3
from pydantic import BaseModel, ValidationError

from lara_power_tools.converters import UniversalEncoder


class BaseEvent(BaseModel):
    source: str
    detail_type: str
    detail: dict


class EventBridgeClient:
    def __init__(
        self,
        service_name: str,
        event_bus_name: str,
        region_name: str = "us-east-1",
        enable_cloudwatch_metrics: bool = False,
        logger=None,
    ):
        """
        Initialize the EventBridgeClient.

        :param service_name: Unique name for the service using this client.
        :param event_bus_name: Name of the EventBridge event bus.
        :param region_name: AWS region where the EventBridge and SQS are hosted.
        :param enable_cloudwatch_metrics: Enable metrics publishing to CloudWatch.
        :param logger: Optional logger instance. Defaults to Lambda Powertools Logger.
        """
        self.service_name = service_name
        self.event_bus_name = event_bus_name
        self.enable_cloudwatch_metrics = enable_cloudwatch_metrics
        self.region_name = region_name

        if not logger:
            from aws_lambda_powertools import Logger

        # Use provided logger or create a new one
        self.logger = logger or Logger(service=service_name)

        # Unique DLQ URL and CloudWatch namespace based on service name
        self.dlq_name = f"{self.service_name}-dlq"
        self.cloudwatch_namespace = f"{self.service_name}-Metrics"

        self.eventbridge_client = boto3.client("events", region_name=self.region_name)
        self.sqs_client = boto3.client("sqs", region_name=self.region_name)
        self.cloudwatch_client = (
            boto3.client("cloudwatch", region_name=self.region_name) if enable_cloudwatch_metrics else None
        )

        self.buffer = deque()
        self.stop_event = threading.Event()
        self.batch_size = 10
        self.publisher_thread = threading.Thread(target=self._publish_loop)
        self.publisher_thread.daemon = True

        # Ensure DLQ exists
        self.dlq_url = self._ensure_dlq()

    def _ensure_dlq(self) -> str:
        """
        Ensure a unique DLQ exists for the service.
        """
        try:
            response = self.sqs_client.create_queue(QueueName=self.dlq_name)
            self.logger.info(f"DLQ '{self.dlq_name}' created or exists.", service_name=self.service_name)
            return response["QueueUrl"]
        except Exception as e:
            self.logger.error(f"Failed to create DLQ '{self.dlq_name}': {e}", service_name=self.service_name)
            raise

    def start_publisher(self):
        """
        Start the background publisher thread.
        """
        self.stop_event.clear()
        self.publisher_thread.start()
        self.logger.info("Event publisher started.", service_name=self.service_name)

    def stop_publisher(self):
        """
        Stop the background publisher thread and publish any remaining events.
        """
        self.stop_event.set()
        self.publisher_thread.join()
        self._publish_remaining_events()
        self.logger.info("Event publisher stopped.", service_name=self.service_name)

    def add_event(self, event: BaseEvent):
        """
        Add a single event to the buffer for publishing.
        """
        try:
            self.buffer.append(
                {
                    "Source": event.source,
                    "DetailType": event.detail_type,
                    "Detail": UniversalEncoder(event.detail).to_json(),
                    "EventBusName": self.event_bus_name,
                    "Time": datetime.utcnow(),
                }
            )
        except ValidationError as e:
            self.logger.error(f"Validation error for event: {event.dict()}, error: {e}", service_name=self.service_name)
            self._send_to_dlq(event.dict())

    def add_events(self, events: Union[Generator[BaseEvent, None, None], list]):
        """
        Add multiple events to the buffer.
        """
        for event in events:
            self.add_event(event)

    def _publish_loop(self):
        """
        Background loop that publishes events in batches.
        """
        while not self.stop_event.is_set():
            if len(self.buffer) >= self.batch_size:
                self._publish_batch()
            time.sleep(0.5)  # Avoid CPU overuse

    def _publish_batch(self):
        """
        Publish a batch of events from the buffer.
        """
        batch = [self.buffer.popleft() for _ in range(min(self.batch_size, len(self.buffer)))]
        response = self.eventbridge_client.put_events(Entries=batch)

        for result, original_event in zip(response["Entries"], batch):
            if "ErrorCode" in result:
                self.logger.error(
                    f"Failed to publish event: {original_event}, error: {result}",
                    service_name=self.service_name,
                )
                self._send_to_dlq(original_event)

    def _publish_remaining_events(self):
        """
        Publish all remaining events in the buffer.
        """
        while self.buffer:
            self._publish_batch()

    def _send_to_dlq(self, event: dict):
        """
        Send an event to the DLQ.
        """
        try:
            self.sqs_client.send_message(QueueUrl=self.dlq_url, MessageBody=str(event))
            self.logger.info("Event sent to DLQ.", service_name=self.service_name)
        except Exception as e:
            self.logger.error(f"Failed to send event to DLQ: {e}", service_name=self.service_name)

    def _publish_metrics(self, namespace: str, metrics: list):
        """
        Publish custom metrics to CloudWatch.
        """
        if not self.cloudwatch_client:
            return

        try:
            metric_data = [
                {
                    "MetricName": metric["MetricName"],
                    "Timestamp": datetime.utcnow(),
                    "Value": metric["Value"],
                    "Unit": metric["Unit"],
                }
                for metric in metrics
            ]
            self.cloudwatch_client.put_metric_data(Namespace=namespace, MetricData=metric_data)
            self.logger.info(
                "Metrics published to CloudWatch.",
                metrics=metric_data,
                service_name=self.service_name,
            )
        except Exception as e:
            self.logger.error(f"Failed to publish metrics to CloudWatch: {e}", service_name=self.service_name)

    def __enter__(self):
        """
        Enter the context manager and start the publisher.
        """
        self.start_publisher()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context manager and stop the publisher, ensuring all events are published.
        """
        self.stop_publisher()
