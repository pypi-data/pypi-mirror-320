import logging
import requests

from wildcard_core.client.utils.helpers import (
    generate_readable_args_schema,
    generate_readable_request_body_schema,
    load_config
)
from wildcard_core.client.utils.parse_openapi import _resolve_ref

# Configure logging for shared utilities
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_test_environment(env: str = 'dev'):
    """Set up the test environment by loading configuration."""
    config = load_config()
    
    # Get URLs from config
    base_url = config['endpoints'][env]['base_url']
    endpoint_details_url = config['endpoints'][env]['endpoint_details_url']
    
    # Default collection name
    index_name = config.get('default_search_collection', None)
    
    return config, base_url, endpoint_details_url, index_name


def fetch_endpoint(endpoint_details_url: str, index_name: str, endpoint_id: str) -> dict:
    """Fetch endpoint details from the API."""
    details_url = endpoint_details_url.format(index_name=index_name)
    params = {
        'id': endpoint_id,
    }
    if index_name is not None:
        params['index_name'] = index_name
    
    logger.info(f"Fetching endpoint with ID {endpoint_id} from: {details_url} with params {params}")
    response = requests.get(details_url, params=params)
    response.raise_for_status()
    
    endpoint = response.json()
    if not endpoint:
        logger.warning(f"No endpoint found with ID: {endpoint_id}")
        return None
    
    logger.info(f"Fetched endpoint: {endpoint}")
    return endpoint


def extract_endpoint_details(openapi_spec: dict) -> tuple:
    """Extract key details from OpenAPI spec."""
    paths = openapi_spec.get('paths', {})
    if not paths:
        logger.warning("No paths found in OpenAPI specification.")
        return None, None, None, None   
    
    path, methods = next(iter(paths.items()))
    method, details = next(iter(methods.items()))

    parameters = details.get('parameters', None)
    request_body = details.get('requestBody', None)
    responses = details.get('responses', None)
    
    components = openapi_spec.get('components', {})
    if request_body is not None and "$ref" in request_body:
        request_body = _resolve_ref(request_body["$ref"], components)
        
    security_schemes = components.get('securitySchemes', None)
    
    # logger.debug(f"PARAMETERS: {parameters}")
    logger.debug(f"REQUEST BODY: {request_body}")
    # logger.debug(f"RESPONSES: {responses}")

    # Extract request body properties
    if request_body is None:
        return parameters, None, responses, security_schemes
    
    content_type = next(iter(request_body["content"]))
    logger.debug(f"CONTENT TYPE: {content_type}")
        
    request_body_schema = request_body["content"][content_type]["schema"]
    logger.debug(f"REQUEST BODY SCHEMA: {request_body_schema}")
            
    if request_body_schema is None:
        return parameters, None, responses, security_schemes
    
    request_body_properties = request_body_schema.get("properties", None)
    logger.debug(f"REQUEST BODY PROPERTIES: {request_body_properties}")

    return parameters, request_body_properties or None, responses or None, security_schemes or None


def is_not_empty(obj):
    """Determine if an object is not empty based on its type."""
    if isinstance(obj, (list, dict)):
        return len(obj) > 0
    if isinstance(obj, str):
        return len(obj.strip()) > 0
    if isinstance(obj, (int, float)):
        return obj != 0
    return True


def generate_readable_schemas(api_schema):
    """Generate readable schemas from API schema."""
    readable_schema = generate_readable_args_schema(api_schema.endpoints[0].parameters or [])
    logger.debug(f"READABLE SCHEMA: {readable_schema}")
    readable_request_body = generate_readable_request_body_schema(api_schema.endpoints[0].requestBody)
    logger.debug(f"READABLE REQUEST BODY: {readable_request_body}")
    
    return readable_schema, readable_request_body

def check_object_validity(original_obj, parsed_obj, obj_name):
    """Validate that the parsed object is not None or empty when the original exists."""
    if is_not_empty(original_obj):
        assert parsed_obj is not None, f"{obj_name} should not be None"