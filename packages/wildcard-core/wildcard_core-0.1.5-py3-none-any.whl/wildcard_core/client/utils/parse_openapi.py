from typing import List, Dict, Optional, Any, Union, Set
from wildcard_core.models import APIService
from wildcard_core.tool_registry.tools.rest_api.types.api_types import (
    APISchema,
    ArrayParameterSchema,
    AllOfParameterSchema,
    OneOfParameterSchema,
    AnyOfParameterSchema,
    EndpointSchema,
    Parameter,
    ParameterIn,
    ParameterSchema,
    ParameterSchemaRef,
    ParameterSchemaType,
    ObjectParameterSchema,
    PrimitiveParameterSchema,
    RequestBody,
    Response,
    ResponseContent,
    SecurityRequirement,
    APITag,
    SecuritySchemeBuilder,
    SecuritySchemeUnion,
    Server,
    APIInfo,
    ExternalDocumentation,
    Discriminator,
    PrimitiveTypesList,
)
from wildcard_core.client.utils.helpers import debug_print
import hashlib
import json
from enum import Enum
from pydantic import BaseModel
from wildcard_core.client.utils.handle_merge_openapi import merge_allof_schemas

def get_nullish_key(obj: Dict[str, Optional[Any]], key: str, default: Optional[Any] = None) -> Optional[Any]:
    """Get value from dict, return default if key missing or value is None"""
    return obj.get(key, default) if obj.get(key) is not None else default


def parse_single_endpoint(path: str, methods: Dict[str, Any], components: Dict[str, Any], 
                         function_id: str, parsed_outer_security: List[SecurityRequirement]) -> EndpointSchema:
    """Parse a single endpoint from the OpenAPI spec"""
    method, details = next(iter(methods.items()))
    debug_print(f"Method: {method}")
    debug_print(f"Details: {details}")
    
    # Get function_id from x-uuid if available, otherwise use the generated one
    endpoint_function_id = details.get("x-uuid", function_id)
    
    parsed_security = parse_security_requirements(get_nullish_key(details, "security", []))    
    endpoint_security = parsed_security + parsed_outer_security if parsed_security or parsed_outer_security else None
    
    parsed_parameters = parse_parameters(get_nullish_key(details, "parameters", []), components)
    debug_print(f"Parsed Parameters: {parsed_parameters}")

    request_body_dict = get_nullish_key(details, "requestBody")
    request_body = parse_request_body(request_body_dict, components) if request_body_dict else None
    debug_print(f"Parsed Request Body: {request_body}")

    responses = parse_responses(get_nullish_key(details, "responses", {}), components)

    return construct_endpoint_schema(
        method=method,
        path=path,
        details=details,
        parameters=parsed_parameters,
        request_body=request_body,
        responses=responses,
        function_id=endpoint_function_id,
        security=endpoint_security
    )

def parse_all_endpoints(paths: Dict[str, Any], components: Dict[str, Any], 
                       function_id: str, parsed_outer_security: List[SecurityRequirement]) -> List[EndpointSchema]:
    """Parse all endpoints from the OpenAPI spec using parse_single_endpoint"""
    endpoints = []
    
    for path, methods in paths.items():
        for method in methods:
            debug_print(f"Processing {method.upper()} {path}")
            
            # Generate fallback function ID if x-uuid is not present
            fallback_function_id = f"{function_id}_{method}_{path}".replace("/", "_").replace("{", "").replace("}", "")
            single_method_dict = {method: methods[method]}
            
            endpoint = parse_single_endpoint(
                path=path,
                methods=single_method_dict,
                components=components,
                function_id=fallback_function_id,
                parsed_outer_security=parsed_outer_security
            )
            endpoints.append(endpoint)
    
    return endpoints

# Entry point for parsing OpenAPI spec
def openapi_to_api_schema(result: Dict[str, Any], function_id: str, api_id: APIService, parse_all: bool = False) -> APISchema:
    """Convert OpenAPI spec to APISchema model"""
    components = get_nullish_key(result, "components", {})
    
    debug_print(f"Components: {components}")

    parsed_security_schemes = parse_security_schemes(components)
    debug_print(f"Parsed Security Schemes: {parsed_security_schemes}")

    parsed_tags = parse_tags(get_nullish_key(result, "tags", []))
    debug_print(f"Parsed Tags: {parsed_tags}")

    parsed_servers = parse_servers(get_nullish_key(result, "servers", []))
    debug_print(f"Parsed Servers: {parsed_servers}")

    parsed_info = parse_info(get_nullish_key(result, "info", {}))
    debug_print(f"Parsed Info: {parsed_info}")

    parsed_external_docs = parse_external_docs(get_nullish_key(result, "externalDocs"))
    debug_print(f"Parsed External Docs: {parsed_external_docs}")

    paths = get_nullish_key(result, "paths", {})
    if not paths:
        debug_print(f"RESULT: {result}")
        raise ValueError("No paths found in OpenAPI specification.")

    parsed_outer_security = parse_security_requirements(get_nullish_key(result, "security", []))

    if parse_all:
        endpoints = parse_all_endpoints(paths, components, function_id, parsed_outer_security)
    else:
        path, methods = next(iter(paths.items()))
        endpoints = [parse_single_endpoint(path, methods, components, function_id, parsed_outer_security)]

    api_schema = APISchema(
        id=api_id,
        name=get_nullish_key(result, "name", parsed_info.title if parsed_info else "Unnamed API"),
        description=get_nullish_key(result, "description", parsed_info.description if parsed_info else ""),
        base_url=get_base_url_from_servers(parsed_servers),
        endpoints=endpoints,
        version=parsed_info.version if parsed_info else None,
        securitySchemes=parsed_security_schemes if parsed_security_schemes else None,
        tags=parsed_tags if parsed_tags else None,
        servers=parsed_servers if parsed_servers else None,
        info=parsed_info,
        externalDocs=parsed_external_docs,
    )

    return api_schema


def _resolve_ref(ref: str, components: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a $ref in the OpenAPI spec"""
    if not ref.startswith("#/components/"):
        raise ValueError(f"Unsupported ref format: {ref}")
    parts = ref.lstrip("#/").split("/")
    ref_obj = components
    for part in parts[1:]:
        ref_obj = ref_obj.get(part)
        if ref_obj is None:
            raise ValueError(f"Reference {ref} cannot be resolved.")
    if not isinstance(ref_obj, dict):
        raise ValueError(f"Reference {ref} does not point to a valid object.")
    return ref_obj


def parse_security_schemes(components: Dict[str, Any]) -> Dict[str, SecuritySchemeUnion]:
    """Parse security schemes from components section using discriminated unions"""
    security_schemes = components.get("securitySchemes", {})
    parsed_security_schemes: Dict[str, SecuritySchemeUnion] = {}
    
    for name, scheme in security_schemes.items():
        if "$ref" in scheme:
            scheme = _resolve_ref(scheme["$ref"], components)
            
        debug_print(f"Scheme: {scheme}")
        parsed_scheme = SecuritySchemeBuilder(scheme=scheme)
        parsed_security_schemes[name] = parsed_scheme.scheme
    
    return parsed_security_schemes


def parse_security_requirements(security: List[Dict[str, List[str]]]) -> List[SecurityRequirement]:
    """Parse security requirements list"""
    parsed_security: List[SecurityRequirement] = []
    for sec_req in security:
        parsed_security.append(SecurityRequirement(requirements=sec_req))
    return parsed_security


def parse_tags(tags: List[Dict[str, Any]]) -> List[APITag]:
    """Parse API tags list"""
    parsed_tags: List[APITag] = []
    for tag in tags:
        external_docs = tag.get("externalDocs")
        parsed_external_docs = parse_external_docs(external_docs) if external_docs else None
        parsed_tags.append(
            APITag(
                name=tag.get("name", ""),
                description=tag.get("description"),
                externalDocs=parsed_external_docs,
            )
        )
    return parsed_tags


def parse_servers(servers: List[Dict[str, Any]]) -> List[Server]:
    """Parse server information list, preferring HTTPS URLs when equivalent HTTP URLs exist"""
    url_map = {}
    for server in servers:
        url = server.get("url", "")
        stripped_url = url.replace("https://", "").replace("http://", "")
        # Prefer HTTPS if available
        if stripped_url not in url_map or url.startswith("https://"):
            url_map[stripped_url] = server

    parsed_servers = [
        Server(
            url=server.get("url", ""),
            description=server.get("description"),
            variables=server.get("variables"),
        )
        for server in url_map.values()
    ]

    return parsed_servers


def get_base_url_from_servers(servers: List[Server]) -> str:
    """Get base URL from servers list, using first server and resolving variables"""
    if not servers:
        return ""

    server = servers[0]
    url = server.url
    variables = server.variables or {}

    for var_name, var_info in variables.items():
        placeholder = f"{{{var_name}}}"
        default_value = var_info.get("default", "")
        url = url.replace(placeholder, default_value)

    return url


def parse_info(info: Dict[str, Any]) -> APIInfo:
    """Parse API info object"""
    return APIInfo(
        title=info.get("title", "Unnamed API"),
        version=info.get("version", "1.0.0"),
        description=info.get("description"),
        termsOfService=info.get("termsOfService"),
        contact=info.get("contact"),
        license=info.get("license"),
    )


def parse_external_docs(external_docs: Optional[Dict[str, Any]]) -> ExternalDocumentation:
    """Parse external documentation object"""
    if not external_docs:
        return ExternalDocumentation(url="")

    return ExternalDocumentation(
        description=external_docs.get("description"),
        url=external_docs.get("url", ""),
    )

def parse_schema(
    schema_dict: Dict[str, Any],
    components: Dict[str, Any],
    required: bool = False,
    cache: Optional[Dict[str, Union['ParameterSchema', List['ParameterSchema']]]] = None,
    seen_refs: Optional[Set[str]] = None,
) -> Union['ParameterSchema', List['ParameterSchema']]:
    """Recursively parse schema and its nested structures, including anyOf, oneOf, and allOf with memoization."""
    
    if cache is None:
        cache = {}
    if seen_refs is None:
        seen_refs = set()
    
    # Determine a unique key for the schema
    if "$ref" in schema_dict:
        ref = schema_dict["$ref"]
        cache_key = f"ref::{ref}"
        
        if ref in seen_refs:
            return ParameterSchemaRef(ref=ref, type=ParameterSchemaType.CIRCULAR)
        
        # Create a new set for the recursive path
        new_seen_refs = seen_refs.copy()
        new_seen_refs.add(ref)
    else:
        # Generate a hash for inline schemas based on their content
        schema_str = str(sorted(schema_dict.items()))
        schema_hash = hashlib.sha256(schema_str.encode('utf-8')).hexdigest()
        cache_key = f"inline::{schema_hash}"
        new_seen_refs = seen_refs  # No change for inline schemas
    
    # Check if the schema has already been parsed
    if cache_key in cache:
        return cache[cache_key]
    
    debug_print(f"PARSING SCHEMA: {schema_dict}")
    
    # Resolve any $ref at the current level
    if "$ref" in schema_dict:
        resolved_schema = _resolve_ref(schema_dict["$ref"], components)
    else:
        resolved_schema = schema_dict
    
    # Handle allOf
    if "allOf" in resolved_schema:
        debug_print("Handling allOf")
        allof_schemas = [
            parse_schema(subschema, components, required, cache, new_seen_refs) 
            for subschema in resolved_schema["allOf"]
        ]
        allof_schemas = [schema for schema in allof_schemas if schema is not None]
        all_of_schema = AllOfParameterSchema(
            type=ParameterSchemaType.ALL_OF,
            allOf=allof_schemas,
            example=resolved_schema.get("example"),
            examples=resolved_schema.get("examples"),
        )
        cache[cache_key] = all_of_schema
        return all_of_schema
    # Handle anyOf
    elif "anyOf" in resolved_schema:
        debug_print("Handling anyOf")
        anyof_schemas = [
            parse_schema(subschema, components, required, cache, new_seen_refs) 
            for subschema in resolved_schema["anyOf"]
        ]
        anyof_schemas = [schema for schema in anyof_schemas if schema is not None]
        any_of_schema = AnyOfParameterSchema(
            type=ParameterSchemaType.ANY_OF,
            anyOf=anyof_schemas,
            example=resolved_schema.get("example"),
            examples=resolved_schema.get("examples"),
        )
        cache[cache_key] = any_of_schema
        return any_of_schema
    elif "oneOf" in resolved_schema:
        debug_print("Handling oneOf")
        oneof_schemas = [
            parse_schema(subschema, components, required, cache, new_seen_refs) 
            for subschema in resolved_schema["oneOf"]
        ]
        oneof_schemas = [schema for schema in oneof_schemas if schema is not None]
        one_of_schema = OneOfParameterSchema(
            type=ParameterSchemaType.ONE_OF,
            oneOf=oneof_schemas,
            example=resolved_schema.get("example"),
            examples=resolved_schema.get("examples"),
        )
        cache[cache_key] = one_of_schema
        return one_of_schema
    
    type_ = resolved_schema.get("type", "string")
    
    if isinstance(type_, list):
        # Handle cases where type is a list, e.g., ["string", "null"]. Return a list of schemas, each with one type
        parsed_schemas = [
            parse_schema({**resolved_schema, "type": t}, components, required, cache, new_seen_refs) 
            for t in type_
        ]
        cache[cache_key] = parsed_schemas
        return parsed_schemas

    # Regular cases flow
    try:
        parameterSchemaType = ParameterSchemaType(type_)
    except ValueError:
        raise ValueError(f"Unsupported parameter type: {type_}")
    
    debug_print(f"Type: {parameterSchemaType}")
    
    if parameterSchemaType in PrimitiveTypesList:
        # Handle primitive types                
        schema = PrimitiveParameterSchema(
            type=parameterSchemaType,
            description=resolved_schema.get("description"),
            format=resolved_schema.get("format"),
            example=resolved_schema.get("example"),
            enum=resolved_schema.get("enum"),
            required=resolved_schema.get("required", required)
        )
        cache[cache_key] = schema
        return schema
    elif parameterSchemaType == ParameterSchemaType.ARRAY:
        # Handle array types
        items_schema = resolved_schema.get("items", {})
        items = parse_schema(dict(items_schema), components, required=True, cache=cache, seen_refs=new_seen_refs)
        schema = ArrayParameterSchema(
            type=ParameterSchemaType.ARRAY,
            items=items,
            example=resolved_schema.get("example"),
            description=resolved_schema.get("description"),
        )
        cache[cache_key] = schema
        return schema
    elif parameterSchemaType == ParameterSchemaType.OBJECT:
        # Handle object types
        properties_dict = resolved_schema.get("properties", {})
        properties = {
            k: parse_schema(
                dict(v), 
                components,
                required=k in resolved_schema.get("required", []),
                cache=cache,
                seen_refs=new_seen_refs
            ) 
            for k, v in properties_dict.items()
        }

        # Handle discriminator if present
        discriminator = None
        if "discriminator" in resolved_schema:
            disc = resolved_schema["discriminator"]
            discriminator = Discriminator(
                propertyName=disc["propertyName"],
                mapping=disc.get("mapping")
            )
            debug_print(f"Discriminator found: {discriminator}")

        debug_print(f"Properties: {properties}")
        schema = ObjectParameterSchema(
            type=ParameterSchemaType.OBJECT,
            properties=properties,
            required=list(set(resolved_schema.get("required", []) or [])),
            description=resolved_schema.get("description"),
            discriminator=discriminator,
            example=resolved_schema.get("example"),
        )
        cache[cache_key] = schema
        return schema
    elif parameterSchemaType == ParameterSchemaType.CIRCULAR:
        return ParameterSchemaRef(ref=resolved_schema["$ref"], type=ParameterSchemaType.CIRCULAR)
    else:
        raise ValueError(f"Unsupported parameter type: {type_}")

def parse_parameters(parameters: List[Dict[str, Any]], components: Dict[str, Any]) -> List[Parameter]:
    """Parse endpoint parameters list"""
    
    parsed_parameters: List[Parameter] = []
    for param in parameters:
        if "$ref" in param:
            param = _resolve_ref(param["$ref"], components)
        
        schema_dict = param.get("schema", {})
        
        schema = parse_schema(schema_dict, components=components, required=param.get("required", False))
        
        parsed_parameters.append(
            Parameter(
                in_=ParameterIn(param.get("in", "query").lower()),
                name=param.get("name", ""),
                description=param.get("description"),
                schema_=schema,
                required=param.get("required", False)
            )
        )
    return parsed_parameters


def parse_request_body(request_body: Dict[str, Any], components: Dict[str, Any]) -> Optional[RequestBody]:
    """Parse request body object"""
    if not request_body:
        return None

    if "$ref" in request_body:
        request_body = _resolve_ref(request_body["$ref"], components)
      
    debug_print(f"PARSED REQUEST BODY: {request_body}")

    parsed_content: Dict[str, ResponseContent] = {}
    for content_type, content_details in request_body.get("content", {}).items():
        schema_dict = content_details.get("schema", {})
        schema_dict = parse_schema(schema_dict, required=False, components=components)
    
        example = content_details.get("example")
        if isinstance(example, dict) and "$ref" in example:
            example = _resolve_ref(example["$ref"], components)

        examples = content_details.get("examples", {})
        parsed_examples = {}
        for example_key, example_value in examples.items():
            if isinstance(example_value, dict):
                if "$ref" in example_value:
                    parsed_examples[example_key] = _resolve_ref(example_value["$ref"], components)
                else:
                    parsed_examples[example_key] = json.dumps(example_value)
            else:
                parsed_examples[example_key] = example_value
                
        content_model = {
            "schema": schema_dict,
            "example": example,
            "examples": parsed_examples,
            # **{k: v for k, v in content_details.items() if k not in ["schema", "example", "examples", "description"]}
        }

        parsed_content[content_type] = content_model
        
    return RequestBody(
        description=request_body.get("description"),
        content=parsed_content,
        required=request_body.get("required", False)
    )


def parse_responses(responses: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Response]:
    """Parse endpoint responses dict and resolve inner $ref references in content.schema"""
    parsed_responses: Dict[str, Response] = {}
    for status_code, resp in responses.items():
        if "$ref" in resp:
            resp = _resolve_ref(resp["$ref"], components)
        content = resp.get("content", {})
        parsed_content: Dict[str, ResponseContent] = {}
        for mime, mime_details in content.items():
            schema_dict = mime_details.get("schema", {})
            schema_dict = parse_schema(schema_dict, required=False, components=components)
            parsed_content[mime] = ResponseContent(
                description=mime_details.get("description", ""),
                content={
                    "schema": schema_dict,
                    **{k: v for k, v in mime_details.items() if k not in ["description", "schema"]}
                }
            )
        parsed_responses[status_code] = Response(
            status_code=status_code,
            description=resp.get("description", ""),
            content=parsed_content if parsed_content else None,
        )
    
    return parsed_responses


def construct_endpoint_schema(
    method: str,
    path: str,
    details: Dict[str, Any],
    parameters: List[Parameter],
    request_body: Optional[RequestBody],
    responses: Dict[str, Response],
    function_id: str,
    security: Optional[List[SecurityRequirement]]
) -> EndpointSchema:
    """Construct endpoint schema from parsed components"""
    return EndpointSchema(
        endpoint_id=function_id,
        path=path,
        method=method.lower(),
        description=details.get("description"),
        parameters=parameters if parameters else None,
        requestBody=request_body if request_body else None,
        responses=responses if responses else None,
        security=security if security else None,
    )