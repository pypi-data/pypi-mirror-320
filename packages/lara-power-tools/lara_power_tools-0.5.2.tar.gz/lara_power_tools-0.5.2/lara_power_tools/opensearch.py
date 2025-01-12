import os

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

service = "es"
region = "us-east-1"
credentials = boto3.Session().get_credentials()

awsauth = None
client = None
if credentials:
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    client = OpenSearch(
        hosts=[{"host": os.getenv("OPENSEARCH_ENDPOINT"), "port": 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=300,
    )
