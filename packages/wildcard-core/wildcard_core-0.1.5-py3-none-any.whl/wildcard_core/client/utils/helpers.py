import inspect
import yaml
from typing import Any, Dict, List, Optional, Union
import asyncio
import json

from aiohttp import ClientResponse, ClientSession, ClientError, ClientTimeout
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from wildcard_core.tool_registry.tools.rest_api.types import Parameter, ParameterSchema, ParameterSchemaType, PrimitiveParameterSchema, ArrayParameterSchema, ObjectParameterSchema, RequestBody, AllOfParameterSchema, OneOfParameterSchema, AnyOfParameterSchema

DEBUG = False  # Set this to True to enable debug prints
def debug_print(message: Any):
    if DEBUG:
        print(message)

@retry(
    retry=retry_if_exception_type((ClientError, asyncio.TimeoutError)),
    wait=wait_exponential(multiplier=1, min=1, max=10) + wait_exponential(multiplier=0.1, min=0, max=1),
    stop=stop_after_attempt(5),
)
async def aiohttp_with_exponential_backoff(
    method: str,
    url: str,
    session: ClientSession,
    status_forcelist: Optional[List[int]] = None,
    allowed_methods: Optional[List[str]] = None,
    timeout: float = 5.0,
    **kwargs
) -> ClientResponse:
    """
    Perform an HTTP request with exponential backoff retry strategy using aiohttp and Tenacity.

    Args:
        method (str): HTTP method (e.g., 'GET', 'POST').
        url (str): The URL to send the request to.
        status_forcelist (List[int], optional): HTTP status codes that trigger a retry.
        allowed_methods (List[str], optional): HTTP methods that are retried.
        timeout (float): Timeout for the request in seconds.
        session (ClientSession, optional): aiohttp session object to reuse.
        **kwargs: Additional arguments to pass to `session.request`.

    Returns:
        ClientResponse: The HTTP response received.

    Raises:
        ClientError: If the request fails after retries.
    """
    if status_forcelist is None:
        status_forcelist = [500, 502, 503, 504, 429]
    if allowed_methods is None:
        allowed_methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']

    debug_print(f"Attempting {method} request to {url} with args {kwargs}")
    response = await session.request(method, url, timeout=ClientTimeout(total=timeout), **kwargs)
    debug_print(f"Received response with status code {response.status}")
    if response.status in status_forcelist and method.upper() in allowed_methods:
        debug_print(f"Status code {response.status} is in status_forcelist. Raising ClientError.")
        raise ClientError(f"Received status code {response.status}")
    return response  # Successful response, exit the function


def load_config(config_path: Optional[str] = None):
    """Load configuration from config.yml file.
    """
    import os
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.yml')
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file: {e}")

def _base_process_schema(schema: ParameterSchema) -> Dict[str, Any]:
    debug_print(f"PROCESSING SCHEMA: {schema}")
        
    # Extract main properties
    result = {
        "type": schema.type,
    }

    # Handle specific schema types
    if isinstance(schema, ObjectParameterSchema):
        nested_schema = {}
        for nested_name, nested_param_schema in schema.properties.items():
            # Determine if the nested property is required
            is_required = (schema.required is not None and nested_name in schema.required) or (hasattr(nested_param_schema, "required") and nested_param_schema.required is True)
            nested_result = _process_schema(nested_param_schema)
            nested_result["description"] = nested_param_schema.description
            nested_result["required"] = "Required" if is_required else "Optional"
            nested_schema[nested_name] = nested_result
        result["properties"] = nested_schema

    elif isinstance(schema, ArrayParameterSchema):
        # Array items are typically required within the array
        result["items"] = _process_schema(schema.items)

    elif isinstance(schema, PrimitiveParameterSchema):
        # Add format and example if present
        if schema.format:
            result["format"] = schema.format
        if schema.enum:
            result["enum"] = schema.enum
        if schema.required is True:
            result["required"] = "Required"

    elif isinstance(schema, AllOfParameterSchema):
        result["allOf"] = schema.allOf
        result["description"] = schema.description
    elif isinstance(schema, OneOfParameterSchema):
        result["oneOf"] = schema.oneOf
        result["description"] = schema.description
    elif isinstance(schema, AnyOfParameterSchema):
        result["anyOf"] = schema.anyOf
        result["description"] = schema.description


    # Add example if present and not already handled
    if hasattr(schema, 'example') and schema.example is not None:
        result["example"] = schema.example

    return result

    
def _oai_process_schema(schema: ParameterSchema) -> Dict[str, Any]:
    type_mapping = {
        ParameterSchemaType.STRING: 'string',
        ParameterSchemaType.INTEGER: 'number',
        ParameterSchemaType.NUMBER: 'number',
        ParameterSchemaType.FLOAT: 'number',
        ParameterSchemaType.BOOLEAN: 'boolean',
        ParameterSchemaType.ARRAY: 'array',
        ParameterSchemaType.OBJECT: 'object',
        ParameterSchemaType.NULL: 'string',  # Default to string for null type
    }
    
    debug_print(f"PROCESSING SCHEMA: {schema}")
    
    # Handle case where schema is already a dict
    if isinstance(schema, dict):
        # If it's a dict, ensure it has a type field
        if 'type' not in schema:
            schema['type'] = 'string'  # default to string type
        return schema
        
    # if isinstance(schema, list):
    #     # If schema is a list, process each schema in the list and return a combined representation
    #     return {
    #         "oneOf": [_process_schema(s, openai_mode=True) for s in schema]
    #     }
    
    # Get the type safely
    schema_type = getattr(schema, 'type', None)
    if schema_type is None:
        schema_type = ParameterSchemaType.STRING  # default to string if no type found
        
    # Extract main properties
    result = {
        "type": type_mapping.get(schema_type, 'string'),  # default to string if type not in mapping
    }

    # Handle allOf, oneOf, anyOf
    if isinstance(schema, AllOfParameterSchema):
        result["type"] = "object"
        result["additionalProperties"] = True
    
    elif isinstance(schema, OneOfParameterSchema):
        result["type"] = "object"
        result["additionalProperties"] = True

    elif isinstance(schema, AnyOfParameterSchema):
        result["type"] = "object"
        result["additionalProperties"] = True

    # Handle specific schema types with defensive checks
    if isinstance(schema, ObjectParameterSchema):
        nested_schema = {}
        result["required"] = []
        
        # Safely get properties with a default empty dict
        properties = getattr(schema, 'properties', {}) or {}
        
        for nested_name, nested_param_schema in properties.items():
            # Skip if nested_param_schema is None
            if nested_param_schema is None:
                continue
                
            # Determine if the nested property is required
            schema_required = getattr(schema, 'required', None) or []
            nested_required = getattr(nested_param_schema, 'required', False)
            is_required = nested_name in schema_required or nested_required is True
            
            try:
                nested_result = _process_schema(nested_param_schema, openai_mode=True)
            except Exception as e:
                debug_print(f"Error processing nested schema for {nested_name}: {e}")
                continue
            
            # Skip if nested_result indicates a circular reference
            if nested_result.get('type') == ParameterSchemaType.CIRCULAR:
                continue
            
            # Safely get description
            nested_result["description"] = getattr(nested_param_schema, 'description', '') or f"Parameter: {nested_name}"
            
            if is_required:
                result["required"].append(nested_name)
            nested_schema[nested_name] = nested_result
            
        result["properties"] = nested_schema
        result["type"] = "object"
        result["additionalProperties"] = False

    elif isinstance(schema, ArrayParameterSchema):
        # Array items are typically required within the array
        result["type"] = "array"
        result["items"] = _process_schema(schema.items, openai_mode=True)

        result["required"] = ["items"]
        result["additionalProperties"] = False

    elif isinstance(schema, PrimitiveParameterSchema):
        # Add format and example if present

        if schema.format:
            result["format"] = schema.format
        if schema.enum:
            result["enum"] = schema.enum

        result["type"] = type_mapping.get(schema.type, schema.type)

    # Add example if present and not already handled
    if hasattr(schema, 'example') and schema.example is not None:
        result["example"] = schema.example

    return result

    
def _process_schema(schema: Union[ParameterSchema, List[ParameterSchema]], openai_mode: bool = False) -> Dict[str, Any]:
    if(openai_mode):
        return _oai_process_schema(schema)
    else:
        return _base_process_schema(schema)

def _process_arg(arg: Parameter, openai_mode: bool = False) -> Dict[str, List[Dict[str, Any]]]:
    schema_list = arg.schema_ if isinstance(arg.schema_, list) else [arg.schema_]
    return {
        "description": arg.description or "No description provided",
        "required": "Required" if arg.required else "Optional", 
        "allowed_schemas": [_process_schema(schema, openai_mode=openai_mode) for schema in schema_list]
    }
    
def generate_readable_args_schema(args_list: List[Parameter], openai_mode: bool = False) -> Dict[str, Any]:
    # Process each argument and store it in a structured dictionary
    schema_dict = {arg.name: _process_arg(arg, openai_mode=openai_mode) for arg in args_list}
    return schema_dict

def generate_readable_request_body_schema(request_body: RequestBody, openai_mode: bool = False) -> list:
    """
    Convert OpenAPI request body schema into a readable format similar to parameters.
    
    Args:
        request_body (RequestBody): OpenAPI request body schema
        
    Returns:
        list: List of flattened request body properties in readable format
    """
    debug_print(f"REQUEST BODY: {json.dumps(request_body, indent=2, default=str)}")
    if not request_body or not request_body.content:
        debug_print("RETURNING EMPTY READABLE REQUEST BODY", (not request_body))
        debug_print("REQUEST BODY CONTENT", request_body.content if request_body else None)
        return []
    
    readable_properties = []
    
    # Get the first content type (usually application/json or x-www-form-urlencoded)
    content_type = next(iter(request_body.content))
    schema = request_body.content[content_type]["schema"]
    
    debug_print(f"PROCESSING REQUEST BODY SCHEMA: {schema}")

    def get_schema_properties(schema):
        if isinstance(schema, ObjectParameterSchema):
            return {
                "value": schema.properties,
                "type": "default"
            }, schema.required or []
        elif isinstance(schema, AllOfParameterSchema):
            if openai_mode == False: #inside context
                return {
                    "value": schema.allOf,
                    "type": "allOf"
                }, []
            else:
                return {
                    "value": {
                        "allOf": {
                            "type": "object", 
                            "description": " This is an allOf schema. Do not use this schema as a parameter. Populate the properties of the schema with the properties of all of the schemas in the allOf array.",
                            "additionalProperties": True
                        }
                    },
                    "type": "allOf"
                }, []
        elif isinstance(schema, OneOfParameterSchema):
            if openai_mode == False:
                return {
                    "value": schema.oneOf,
                    "type": "oneOf"
                }, []
            else:
                return {
                    "value": {
                        "oneOf": {
                            "type": "object",
                            "description": " This is a oneOf schema. Do not use this schema as a parameter. Populate the properties of the schema with the properties of one of the schemas in the oneOf array.",
                            "additionalProperties": True
                        }
                    },
                    "type": "oneOf"
                }, []
        elif isinstance(schema, AnyOfParameterSchema):
            if openai_mode == False:
                return {
                    "value": schema.anyOf,
                    "type": "anyOf"
                }, []
            else:
                return {
                    "value": {
                        "anyOf": {
                            "type": "object",
                            "description": " This is a anyOf schema. Do not use this schema as a parameter. Populate the properties of the schema with the properties of one or more of the schemas in the anyOf array.",
                            "additionalProperties": True
                        }
                    },
                    "type": "anyOf"
                }, []
            
            # # For these types, combine properties and required fields from all sub-schemas
            # all_properties = {}
            # all_required = []
            
            # sub_schemas = (schema.allOf if isinstance(schema, AllOfParameterSchema) else
            #              schema.oneOf if isinstance(schema, OneOfParameterSchema) else
            #              schema.anyOf)
            
            # for sub_schema in sub_schemas:
            #     if isinstance(sub_schema, ObjectParameterSchema):
            #         sub_props, sub_required = sub_schema.properties, sub_schema.required or []
            #         all_properties.update(sub_props)
            #         all_required.extend(sub_required)
            
            # return all_properties, list(set(all_required))  # Deduplicate required fields
        return schema.get("properties", {}), schema.get("required", [])
    
    def get_schema_attr(schema, attr):
        if isinstance(schema, dict):
            return schema.get(attr, None)
        return getattr(schema, attr, None)
    
    properties, required_props = get_schema_properties(schema)
    if properties and "value" in properties and properties["value"]:
        if properties["type"] in ("allOf", "oneOf", "anyOf"):
            for prop in properties["value"]:
                readable_prop = {
                    "name": schema.type,
                    "description": schema.description,
                    "required": False,
                    "allowed_schemas": [_process_schema(prop, openai_mode=openai_mode)]
                }
                readable_properties.append(readable_prop)
        else:
            for prop_name, prop_details in properties["value"].items():
                readable_prop = {
                    "name": prop_name,
                    "description": get_schema_attr(prop_details, "description"),
                    "required": "Required" if (prop_name in required_props or get_schema_attr(prop_details, "required") is True) else "Optional",
                    "allowed_schemas": [_process_schema(prop_details, openai_mode=openai_mode)]
                }
                readable_properties.append(readable_prop)
    
    debug_print(f"READABLE PROPERTIES: {json.dumps(readable_properties, indent=2, default=str)}")
    return readable_properties

def ensure_sync(func):
    """
    A decorator to ensure an async function can be called synchronously,
    handling cases where an event loop may or may not already exist.
    """
    def wrapper(*args, **kwargs):
        try:
            # If there's an active event loop, use it
            loop = asyncio.get_running_loop()
        except RuntimeError:  # No running event loop
            loop = None

        if loop and loop.is_running():
            # If the loop is running, create a task and wait for it
            return asyncio.run_coroutine_threadsafe(func(*args, **kwargs), loop).result()
        else:
            # Otherwise, start a new event loop and run the coroutine
            return asyncio.run(func(*args, **kwargs))

    return wrapper
