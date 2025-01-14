import sys
import logging
import unittest
import requests

from wildcard_core.models import APIService
from wildcard_core.client.tests.shared import (
    check_object_validity,
    setup_test_environment,
    fetch_endpoint,
    extract_endpoint_details,
    generate_readable_schemas,
)
from wildcard_core.client.utils.parse_openapi import openapi_to_api_schema
from wildcard_core.client.utils.helpers import debug_print

# Configure logging for the test
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestParseOpenAPIById(unittest.TestCase):
    def setUp(self):
        """Set up the test environment by loading configuration."""
        ENV = 'dev' # One of 'dev', 'container', 'prod'
        self.config, self.base_url, self.endpoint_details_url, self.index_name = setup_test_environment(ENV)

    def test_parse_single_endpoint(self):
        """Test parsing a single OpenAPI endpoint by its endpoint ID."""
        # Validate command line arguments
        if len(sys.argv) < 2:
            self.fail("Endpoint ID must be provided as a command line argument.")
        
        endpoint_id = sys.argv[1]
        self.index_name = sys.argv[2] if len(sys.argv) > 2 else self.index_name

        try:
            # Fetch and parse endpoint
            endpoint = fetch_endpoint(self.endpoint_details_url, self.index_name, endpoint_id)
            self.assertIsNotNone(endpoint, f"Endpoint with ID {endpoint_id} should exist.")
            
            openapi_spec = endpoint.get('content')
            self.assertIsNotNone(openapi_spec, f"OpenAPI spec for endpoint ID {endpoint_id} should not be None.")
            
            parameters, request_body_properties, responses = extract_endpoint_details(openapi_spec)

            api_id = endpoint.get('metadata', {}).get('api_id')
            self.assertIsNotNone(api_id, f"API ID for endpoint ID {endpoint_id} should not be None.")
            api_id = APIService(api_id)
            
            # Parse OpenAPI spec into API schema
            logger.info(f"Parsing OpenAPI spec for endpoint ID: {endpoint_id}")
            api_schema = openapi_to_api_schema(openapi_spec, endpoint_id, api_id)
            
            # Validate API schema
            self.assertIsNotNone(api_schema, "Parsed API schema should not be None")
            self.assertEqual(api_schema.id, endpoint_id, "API schema ID should match the endpoint ID")
            logger.info(f"Successfully parsed API schema for endpoint ID: {endpoint_id}")
            debug_print(f"API Schema: {api_schema}")

            # Generate readable schemas
            readable_schema, readable_request_body = generate_readable_schemas(api_schema)
            
            # Perform Assertions on Readable Schemas
            check_object_validity(parameters, readable_schema, "Parameters")
            check_object_validity(request_body_properties, readable_request_body, "Request body")
            
        except requests.RequestException as http_err:
            logger.error(f"HTTP error occurred while fetching endpoint ID {endpoint_id}: {http_err}")
            self.fail(f"HTTP error occurred: {http_err}")
        except Exception as err:
            logger.error(f"Unexpected error while parsing endpoint ID {endpoint_id}: {err}")
            self.fail(f"Unexpected error: {err}")


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'])  # Ignore the first CLI argument for unittest
    # Usage:
    # Run this test with the endpoint ID as a command line argument.
    # Example: python3 -m wildcard_core.tool_search.tests.testParseOpenApiById <endpoint_id>
