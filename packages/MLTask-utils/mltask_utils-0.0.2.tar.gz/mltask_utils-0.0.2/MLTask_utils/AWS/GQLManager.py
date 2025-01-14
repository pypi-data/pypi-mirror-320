import asyncio
import logging
import os
import sys
from urllib.parse import urlparse

import os
from botocore.credentials import Credentials

from pprint import pprint

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.appsync_auth import AppSyncApiKeyAuthentication, AppSyncIAMAuthentication
from gql.transport.appsync_websockets import AppSyncWebsocketsTransport

# ideally we would like to pass the user credentials along the SNS, SQS pipeline and then invoke the graphql updates with the user creds
# since I don't know how to do that, I will settle for api keys until further notice

# https://github.com/graphql-python/gql/issues/163


class GQLManager:
    def __init__(self, APPSYNC_API_ENDPOINT_URL=None, APPSYNC_API_KEY=None):
        self.APPSYNC_API_ENDPOINT_URL = APPSYNC_API_ENDPOINT_URL if APPSYNC_API_ENDPOINT_URL is not None else os.environ[
            'APPSYNC_API_ENDPOINT_URL']
        self.APPSYNC_API_KEY = APPSYNC_API_KEY if APPSYNC_API_ENDPOINT_URL is not None else os.environ[
            'APPSYNC_API_KEY']
        self.region = os.environ['REGION']
        self.access_key = os.environ['ACCESS_KEY']
        self.secret_key = os.environ['SECERT_KEY']

    def api_key_auth(self):
        if self.APPSYNC_API_ENDPOINT_URL is None or self.APPSYNC_API_KEY is None:
            print("Missing environment variables")
            sys.exit()

        # Extract host from url
        host = str(urlparse(self.APPSYNC_API_ENDPOINT_URL).netloc)

        auth = AppSyncApiKeyAuthentication(
            host=host, api_key=self.APPSYNC_API_KEY)
        return auth

    def iam_auth(self):

        credentials = Credentials(
            access_key=self.access_key,
            secret_key=self.secret_key,
            token=None,   # Optional
        )

        # Extract host from url
        host = str(urlparse(self.APPSYNC_API_ENDPOINT_URL).netloc)
        auth = AppSyncIAMAuthentication(
            host=host,
            credentials=credentials,
            region_name=self.region
        )
        return auth

    def run_query_iam(self, query_string, variables=None):
        # logging.basicConfig(level=logging.DEBUG)
        # logging.getLogger("gql.transport").setLevel(logging.DEBUG)

        auth = self.iam_auth()
        transport = AIOHTTPTransport(
            url=self.APPSYNC_API_ENDPOINT_URL,
            auth=auth
        )
        session = Client(
            transport=transport,
            fetch_schema_from_transport=False,
        )
        query = gql(query_string)
        result = session.execute(query, variable_values=variables)
        return result

        # transport = RequestsHTTPTransport(
        #     url=self.APPSYNC_API_ENDPOINT_URL, auth=auth)
        # client = Client(transport=transport)
        # result = client.execute(query)

        # pprint(result)

    def run_query_api_key(self, query_string, variables=None):
        auth = self.api_key_auth()

        transport = AIOHTTPTransport(
            url=self.APPSYNC_API_ENDPOINT_URL,
            auth=auth
        )
        session = Client(
            transport=transport,
            fetch_schema_from_transport=False,
        )

        query = gql(query_string)
        result = session.execute(query, variable_values=variables)
        return result
        # print(result)

    async def handle_subscription(self):

        # Should look like:
        # https://XXXXXXXXXXXXXXXXXXXXXXXXXX.appsync-api.REGION.amazonaws.com/graphql

        if self.APPSYNC_API_ENDPOINT_URL is None or self.APPSYNC_API_KEY is None:
            print("Missing environment variables")
            sys.exit()

        # Extract host from url
        host = str(urlparse(self.APPSYNC_API_ENDPOINT_URL).netloc)

        print(f"Host: {host}")

        auth = AppSyncApiKeyAuthentication(
            host=host, api_key=self.APPSYNC_API_KEY)

        transport = AppSyncWebsocketsTransport(
            url=self.APPSYNC_API_ENDPOINT_URL, auth=auth)

        async with Client(transport=transport) as session:

            subscription = gql(
                """
            subscription onCreateMessage {
                onCreateMessage {
                message
                }
            }
            """
            )

            print("Waiting for messages...")

            async for result in session.subscribe(subscription):
                print(result)
