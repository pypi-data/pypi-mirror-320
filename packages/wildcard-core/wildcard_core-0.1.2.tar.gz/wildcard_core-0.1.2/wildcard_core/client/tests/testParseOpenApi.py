import logging
import requests
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from wildcard_core.models import APIService
from wildcard_core.client.tests.shared import (
    check_object_validity,
    setup_test_environment,
    extract_endpoint_details,
    generate_readable_schemas,
)
from wildcard_core.client.utils.parse_openapi import openapi_to_api_schema

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PAGE_SIZE = 50
PAGE_WORKERS = 3
ENDPOINT_WORKERS = 10
ENV=os.getenv('ENV', 'prod')

class TestParseOpenAPI(unittest.TestCase):
    """Unit tests for parsing OpenAPI endpoints and generating readable schemas."""

    def setUp(self):
        """Initialize test configuration and endpoints."""
        self.config, self.base_url, self.endpoint_details_url, self.index_name = setup_test_environment(ENV)
        self.search_all_endpoint = self.config['endpoints'][ENV]['endpoint_all_url']
        self.count_endpoint = self.config['endpoints'][ENV]['endpoint_count_url']

    def test_parse_all_endpoints(self):
        """Parse all OpenAPI endpoints and validate their readable schemas."""
        try:
            total_count = self.get_total_endpoints()
            if total_count == 0:
                self.skipTest("No endpoints found to test.")

            total_pages = self.calculate_total_pages(total_count)
            logger.info(f"Total endpoints: {total_count}, Total pages: {total_pages}")

            self.process_all_pages(total_pages)
        except requests.RequestException as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            self.fail(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logger.error(f"Unexpected error: {err}")
            self.fail(f"Unexpected error: {err}")

    def get_total_endpoints(self):
        """Retrieve the total number of OpenAPI endpoints from the count endpoint."""
        count_url = self.config['endpoints'][ENV]['endpoint_count_url']
        params = {}
        if self.index_name is not None:
            params['index_name'] = self.index_name
        logger.info(f"Fetching total count from: {count_url} with params {params}")
        response = requests.get(count_url, params=params)
        response.raise_for_status()
        total_count = response.json().get('count', 0)
        logger.info(f"Total endpoints to fetch: {total_count}")
        return total_count

    def calculate_total_pages(self, total_count):
        """Calculate the number of pages based on total endpoints and page size."""
        return (total_count + PAGE_SIZE - 1) // PAGE_SIZE

    def process_all_pages(self, total_pages):
        """Process all pages concurrently to fetch and parse endpoints."""
        logger.info(f"Processing {total_pages} pages with page size {PAGE_SIZE}.")

        with ThreadPoolExecutor(max_workers=PAGE_WORKERS) as page_executor:
            page_futures = [page_executor.submit(self.process_single_page, page) for page in range(1, total_pages + 1)]
            for future in as_completed(page_futures):
                try:
                    future.result()
                except Exception as e:
                    self.fail(f"Page processing failed: {e}")

    def process_single_page(self, page):
        """Fetch and process a single page of endpoints."""
        endpoints = self.fetch_endpoints(page)
        logger.info(f"Processing {len(endpoints)} endpoints from page {page}.")
        failed_endpoints = 0

        with ThreadPoolExecutor(max_workers=ENDPOINT_WORKERS) as endpoint_executor:
            endpoint_futures = [endpoint_executor.submit(self.parse_and_validate_endpoint, endpoint) for endpoint in endpoints]
            for future in as_completed(endpoint_futures):
                try:
                    future.result()
                except Exception as e:
                    failed_endpoints += 1
                    self.fail(f"Endpoint parsing failed: {e}")


        logger.info(f"Number of failed endpoints: {failed_endpoints}")

    def fetch_endpoints(self, page):
        """Fetch endpoints from a specific page."""
        all_url = self.search_all_endpoint.format(index_name=self.index_name)
        params = {
            'page': page,
            'page_size': PAGE_SIZE
        }
        logger.info(f"Fetching page {page}: {all_url} with params {params}")
        response = requests.get(all_url, params=params, timeout=600)
        response.raise_for_status()
        endpoints = response.json()
        logger.info(f"Fetched {len(endpoints)} endpoints from page {page}.")
        return endpoints

    def parse_and_validate_endpoint(self, endpoint):
        """Parse an individual endpoint and validate its readable schemas."""
        function_id = endpoint.get('id')
        openapi_spec = endpoint.get('content')
        api_id = endpoint.get('metadata', {}).get('api_id')
        api_id = APIService(api_id)

        if not function_id or not openapi_spec or not api_id:
            raise Exception(f"Missing 'id' or 'openapi_spec' or 'api_id' for endpoint: {endpoint}")

        try:
            parameters, request_body_properties, _, security_schemes = extract_endpoint_details(openapi_spec)
            api_schema = openapi_to_api_schema(openapi_spec, function_id, api_id)
            logger.debug(f"Parsed API schema for function_id: {function_id}")

            # Validate security schemes
            if security_schemes:
                for scheme in security_schemes:
                    scheme_type = scheme.get('type')
                    if scheme_type == 'oauth2':
                        scopes = scheme.get('scopes', {})
                        if not scopes:
                            raise ValueError(f"OAuth2 security scheme missing scopes for function_id {function_id}")
                    elif scheme_type in ['apiKey', 'http']:
                        if not scheme.get('name') or not scheme.get('in'):
                            raise ValueError(f"Invalid {scheme_type} security scheme configuration for function_id {function_id}")

            # Generate readable schemas
            readable_schema, readable_request_body = generate_readable_schemas(api_schema)

            # Perform Assertions on Readable Schemas
            check_object_validity(parameters, readable_schema, "Parameters")
            check_object_validity(request_body_properties, readable_request_body, "Request body")
            
        except Exception as e:
            logger.error(f"Error parsing OpenAPI for function_id {function_id}: {e}")
            raise

if __name__ == '__main__':
    unittest.main()
    # Usage:
    # Run this test to validate OpenAPI parsing across all endpoints in the collection
    # Example: python3 -m wildcard_core.tool_search.tests.testParseOpenApi
