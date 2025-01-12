import json
from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel


class AppSyncJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder with support for Pydantic models, nested structures,
    lists, AppSync-compatible date/datetime serialization, Decimal type, and bytes.
    """

    def default(self, obj: Any) -> Any:
        # Handle datetime and date for AppSync (ISO 8601 format with 'Z' for UTC)
        if isinstance(obj, datetime):
            return obj.astimezone(timezone.utc).isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()

        # Handle Decimal type
        if isinstance(obj, Decimal):
            return float(obj)

        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            # Serialize Pydantic models to dictionary
            return obj.model_dump()

        # Handle bytes type
        if isinstance(obj, bytes):
            return bool(obj)

        # Default handling for other objects
        return super().default(obj)


class UniversalEncoder(object):
    def __init__(self, data: Any):
        super().__init__()
        self.data = data

    def to_dynamodb(self) -> Dict[str, Any]:
        def dynamodb_enocde(value):
            """
            Recursively encode a Python object into DynamoDB-compatible native types.

            :param value: The value to encode (can be a primitive type, Pydantic model, list, dict, set, etc.)
            :return: A DynamoDB-compatible value
            """
            if value is None:
                return None
            elif isinstance(value, (str, int, float, bool)):
                return value  # Directly return DynamoDB-compatible primitives
            elif isinstance(value, (datetime, date)):
                return value.isoformat()  # Convert datetime/date to ISO 8601 string
            elif isinstance(value, list):
                return [dynamodb_enocde(v) for v in value]  # Recursively process lists
            elif isinstance(value, set):
                return list(value)  # DynamoDB supports lists, not sets, so convert to list
            elif isinstance(value, dict):
                return {k: dynamodb_enocde(v) for k, v in value.items()}  # Recursively process dicts
            elif isinstance(value, BaseModel):
                return dynamodb_enocde(value.dict())  # Convert Pydantic model to dict and process recursively
            elif isinstance(value, Enum):
                return value.value
            else:
                raise TypeError(f"Unsupported type for DynamoDB encoding: {type(value)}")

        return dynamodb_enocde(self.data)

    def to_json(self, **kwargs):
        kwargs.setdefault("cls", AppSyncJSONEncoder)
        return json.dumps(self.data, **kwargs)

    def to_appsync(self) -> Any:
        """
        Recursively serialize a Pydantic object or other Python objects into a format
        compatible with AppSync, including proper datetime conversion to AWSDateTime.

        :param item: Pydantic object, list, or dict
        :return: AppSync-compatible dictionary or value
        """

        def pydantic_to_appsync(item):
            def serialize_value(value):
                if isinstance(value, datetime):
                    # Convert datetime to ISO 8601 with 'Z' for UTC
                    return value.astimezone(timezone.utc).isoformat()
                elif isinstance(value, BaseModel):
                    # Recursively serialize Pydantic models
                    return pydantic_to_appsync(value)
                elif isinstance(value, list):
                    # Recursively serialize each item in a list
                    return [serialize_value(v) for v in value]
                elif isinstance(value, dict):
                    # Recursively serialize each key-value pair in a dictionary
                    return {k: serialize_value(v) for k, v in value.items()}
                elif isinstance(value, Enum):
                    return value.value

                return value  # Return as-is for other types

            if isinstance(item, BaseModel):
                # Start serialization for Pydantic models
                return {k: serialize_value(v) for k, v in item.model_dump().items()}
            elif isinstance(item, list):
                # Serialize lists directly
                return [serialize_value(v) for v in item]
            elif isinstance(item, dict):
                # Serialize dictionaries directly
                return {k: serialize_value(v) for k, v in item.items()}
            else:
                # Return non-complex types as-is
                return serialize_value(item)

        return pydantic_to_appsync(self.data)


def to_dynamodb(item):
    return UniversalEncoder(item).to_dynamodb()


def to_json(item):
    return UniversalEncoder(item).to_json()


def to_appsync(item):
    return UniversalEncoder(item).to_appsync()
