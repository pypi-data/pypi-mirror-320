import asyncio
import base64
import aiohttp

from typing import Any, Dict, Optional, List, Tuple, Union
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.tool_registry.tools.base import BaseAction
from wildcard_core.tool_registry.tools.rest_api.types import (
    AuthConfig,
    AuthType,
    BearerAuthConfig,
    ApiKeyAuthConfig,
    BasicAuthConfig,
    OAuth2AuthConfig,
    APISchema,
    ArrayParameterSchema,
    EndpointSchema,
    ObjectParameterSchema,
    Parameter,
    ParameterIn,
    PrimitiveParameterSchema,
)
from wildcard_core.tool_registry.tools.base import BaseAction
from wildcard_core.tool_registry.tools.utils.helpers import is_base64_urlsafe
from wildcard_core.tool_registry.tools.utils.validate_schemas import validate_and_process_body_data
from wildcard_core.client.utils.helpers import debug_print
from urllib.parse import urljoin


class RestAPIHandler(BaseAction):
    """
    Generic handler for executing REST API calls based on OpenAPI specifications.
    Supports various authentication methods.
    """

    def __init__(
        self,
        name: str = "",
        action_id: str = "",
        schema: APISchema = None,
        description: str = "",
        base_url: str = "",
        auth: Optional[AuthConfig] = None,
        logger: WildcardLogger = None
    ):
        """
        Initializes the RestAPIHandler with necessary parameters.

        Args:
            name (str): Name of the action.
            action_id (str): Unique identifier for the action.
            schema (APISchema): Schema detailing the API call.
            description (str): Description of the action.
            base_url (str): Base URL for the API.
            auth (Optional[AuthConfig]): Authentication details.
        """
        super().__init__(name, action_id, schema, description, logger)
        self.base_url = base_url
        self.auth = auth

    @classmethod
    def valid_fields(cls) -> List[str]:
        return ["name", "action_id", "schema", "description", "base_url", "auth"]

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if key in self.valid_fields():
                setattr(self, key, value)

    def set_schema(self, schema: APISchema) -> None:
        self.schema = schema

    def _get_api_key_details(self) -> Optional[Tuple[str, ParameterIn, str]]:
        """
        Extracts API key name, location, and value from the security schemes and auth config.

        Returns:
            Optional[Tuple[str, ParameterIn, str]]: Tuple of (key_name, location, key_value) if found
        """
        if not self.schema.securitySchemes or not self.schema.endpoints:
            return None

        # Access the security requirements from the first endpoint
        endpoint_security = self.schema.endpoints[0].security
        if not endpoint_security:
            return None

        for requirement in endpoint_security:
            for scheme_name, scopes in requirement.requirements.items():
                scheme = self.schema.securitySchemes.get(scheme_name)
                if scheme and scheme.type == AuthType.API_KEY:
                    key_name = scheme.name
                    location = scheme.in_
                    key_value: Optional[str] = None
                    if isinstance(self.auth, ApiKeyAuthConfig):
                        key_value = self.auth.key_value
                    if key_name and location and key_value:
                        return (key_name, location, key_value)
        return None

    def _handle_auth(
        self,
        headers: Dict[str, str],
        params: Dict[str, str]
    ) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Consolidates all authentication handling into a single method.

        Args:
            headers (Dict[str, str]): Existing headers.
            params (Dict[str, str]): Existing query parameters.

        Returns:
            Tuple[Dict[str, str], Dict[str, str]]: Updated headers and params with authentication info.
        """
        if not self.auth:
            return headers, params

        auth_type = AuthType(self.auth.type)

        if auth_type == AuthType.BEARER and isinstance(self.auth, BearerAuthConfig):
            headers['Authorization'] = f"Bearer {self.auth.token}"
        elif auth_type == AuthType.API_KEY and isinstance(self.auth, ApiKeyAuthConfig):
            api_key_details = self._get_api_key_details()
            if api_key_details:
                key_name, location, key_value = api_key_details
                if location == ParameterIn.HEADER:
                    headers[key_name] = key_value
                elif location == ParameterIn.QUERY:
                    params[key_name] = key_value
        elif auth_type == AuthType.OAUTH2 and isinstance(self.auth, OAuth2AuthConfig):
            token_type = self.auth.token_type or 'Bearer'
            headers['Authorization'] = f"{token_type} {self.auth.token}"
        elif auth_type == AuthType.BASIC and isinstance(self.auth, BasicAuthConfig):
            if isinstance(self.auth.credentials, str):
                headers['Authorization'] = f"Basic {self.auth.credentials}"
            else:
                joined_credentials = f"{self.auth.credentials.username}:{self.auth.credentials.password}"
                credentials = joined_credentials if not self.auth.credentials.base64_encode else base64.b64encode(joined_credentials.encode('utf-8')).decode('utf-8')
                headers['Authorization'] = f"Basic {credentials}"

        return headers, params

    def _get_content_type_and_schema(self, endpoint: EndpointSchema) -> Tuple[str, Dict[str, Any]]:
        """
        Determines which content type to use based on the endpoint schema.
        Supports multiple content types with priority ordering.

        Args:
            endpoint (EndpointSchema): The endpoint schema.

        Returns:
            Tuple[str, Dict[str, Any]]: Selected content type and its corresponding schema
        """
        request_body = endpoint.requestBody
        content_types = request_body.content if request_body else {}

        preferred_types = [
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "application/xml",
            "text/plain",
            "application/octet-stream"
            "message/cpim",
            "message/delivery-status",
            "message/disposition-notification",
            "message/external-body",
            "message/feedback-report",
            "message/global",
            "message/global-delivery-status",
            "message/global-disposition-notification",
            "message/global-headers",
            "message/http",
            "message/imdn+xml",
            "message/news",
            "message/partial",
            "message/rfc822",
            "message/s-http",
            "message/sip",
            "message/sipfrag",
            "message/tracking-status",
            "message/vnd.si.simp",
            "message/vnd.wfa.wsc"
        ]

        for content_type in preferred_types:
            if content_type in content_types:
                return content_type, content_types[content_type]['schema']

        if content_types:
            first_content_type = next(iter(content_types))
            return first_content_type, content_types[first_content_type]['schema']

        return None, None

    def _resolve_request_body(
        self,
        data: Dict[str, Any],
        content_type: str
    ) -> Dict[str, Any]:
        """
        Resolves the request body based on content type.
        """        
        request_kwargs: Dict[str, Any] = {}
        
        # Don't include body/json for GET requests
        if not data:
            return request_kwargs

        if content_type == 'application/x-www-form-urlencoded':
            request_kwargs['data'] = data
        elif content_type == 'multipart/form-data':
            request_kwargs['files'] = {
                k: v for k, v in data.items()
                if hasattr(v, 'read') or isinstance(v, (bytes, tuple))
            }
            request_kwargs['data'] = {
                k: v for k, v in data.items()
                if k not in request_kwargs.get('files', {})
            }
        elif content_type == 'application/octet-stream':
            request_kwargs['data'] = data
        elif content_type == 'text/plain':
            request_kwargs['data'] = str(next(iter(data.values())) if data else '')
        elif content_type == 'application/json':
            request_kwargs['json'] = data
        elif content_type.startswith("message/"):
            # message_data = data.get("message", {})
            # resource_data = message_data.get("resource", {})
            
            # if "message" in data:
            #     request_kwargs['json'] = data["message"]
            # elif "resource" in data:
            #     request_kwargs['json'] = data["resource"]
            # else:
            request_kwargs['json'] = data
            
            # TODO: Verify this works beyond GMAIL - in gmail you can send message/* content types by getting the "message" field from the response and then sending as application/json request
            
            # if "raw" in data:
            #     raw_data = data["raw"]
            #     if raw_data("format", None) == "byte":
            #         if not is_base64_urlsafe(raw_data):
            #             # Encode only if not already encoded
            #             raw_data = base64.urlsafe_b64encode(raw_data.encode('utf-8')).decode('utf-8')
                    
            #         request_kwargs["data"]["raw"] = raw_data
            # elif "raw" in resource_data:
            #     raw_data = resource_data["raw"]
            #     if not is_base64_urlsafe(raw_data):
            #         # Encode only if not already encoded
            #         raw_data = base64.urlsafe_b64encode(raw_data.encode('utf-8')).decode('utf-8')
            #     request_kwargs["data"]["resource"] = {
            #         "raw": raw_data
            #     }
        else:
            request_kwargs['data'] = data

        return request_kwargs

    def _process_parameters(
        self,
        kwargs: Dict[str, Any],
        params: Dict[str, str],
        data: Dict[str, Any],
        headers: Dict[str, str],
        url: str,
        endpoint: EndpointSchema,
    ) -> Tuple[Dict[str, str], Dict[str, Any], Dict[str, str], str]:
        """
        Process API parameters based on their location (query, body, header, path).

        Args:
            kwargs (Dict[str, Any]): Input parameters for the API call
            params (Dict[str, str]): Existing query parameters
            data (Dict[str, Any]): Existing request body data
            headers (Dict[str, str]): Existing request headers
            url (str): The API endpoint URL
            endpoint (EndpointSchema): The endpoint schema

        Returns:
            Tuple containing updated params, data, headers dictionaries, and the updated URL
        """
        
        # Process nested parameters or requestBody if present
        processed_kwargs = {}
        if "parameters" in kwargs:
            processed_kwargs.update(kwargs["parameters"])
        if "requestBody" in kwargs:
            if isinstance(kwargs["requestBody"], dict):
                processed_kwargs.update(kwargs["requestBody"])
            elif isinstance(kwargs["requestBody"], list) and len(kwargs["requestBody"]) == 1:
                processed_kwargs.update(kwargs["requestBody"][0])
            else:
                raise ValueError(f"malformed requestBody: {type(kwargs['requestBody'])}")
        # Include any other top-level kwargs
        processed_kwargs.update({
            k: v for k, v in kwargs.items() 
            if k not in ["parameters", "requestBody"]
        })

        # Use processed_kwargs instead of kwargs for the rest of the function
        parameters: Optional[List[Parameter]] = endpoint.parameters
        exclude_from_body = set()
        if parameters:
            for param in parameters:
                location = param.in_
                name = param.name
                value = processed_kwargs.get(name)

                if value is not None:
                    schema = param.schema_
                    # Handle based on the schema type
                    if isinstance(schema, PrimitiveParameterSchema):
                        if location == ParameterIn.QUERY:
                            params[name] = str(value)
                        elif location == ParameterIn.BODY:
                            if schema.format == "byte":
                                if not is_base64_urlsafe(value):
                                    # Encode only if not already encoded
                                    value = base64.urlsafe_b64encode(value.encode('utf-8')).decode('utf-8')
                                    
                            data[name] = value
                        elif location == ParameterIn.HEADER:
                            headers[name] = str(value)
                        elif location == ParameterIn.PATH:
                            url = url.replace(f"{{{name}}}", str(value))
                            exclude_from_body.add(name) # do not include path params in the body
                    elif isinstance(schema, ArrayParameterSchema):
                        if location == ParameterIn.QUERY:
                            params[name] = ','.join(map(str, value))
                        elif location == ParameterIn.BODY:
                            data[name] = value
                        elif location == ParameterIn.HEADER:
                            headers[name] = ','.join(map(str, value))
                        else:
                            raise ValueError(f"Unsupported parameter location '{location}' for array type.")
                    elif isinstance(schema, ObjectParameterSchema):
                        if location == ParameterIn.BODY:
                            data[name] = value
                        else:
                            raise ValueError(f"Unsupported parameter location '{location}' for object type.")
                    else:
                        raise ValueError(f"Unsupported schema type for parameter '{name}'.")

        # Process Request Body based on content type and schema
        content_type, body_schema = self._get_content_type_and_schema(endpoint)

        # Add content type to headers
        if content_type:
            if content_type.startswith("message/"):
                headers["Content-Type"] = "application/json"
            else:
                headers["Content-Type"] = content_type

        # If the content type expects a body, merge data accordingly
        # Here, assume body_schema is a dict representing the schema
        if content_type:
            # Merge any remaining kwargs into data based on body_schema
            # This assumes that kwargs not used in parameters should be part of the body
            
            # TODO: we can do static validation here
            
            # Prune processed_kwargs of any keys that are already in params, headers, or exclude_from_body
            processed_kwargs = {
                k: v for k, v in processed_kwargs.items()
                if k not in params and k not in headers and k not in exclude_from_body
            }
            
            validate_and_process_body_data(processed_kwargs, body_schema, data)
            # if hasattr(body_schema, "format") and body_schema.format:
            #     if not is_base64_urlsafe(value):
            #         # Encode only if not already encoded
            #         value = base64.urlsafe_b64encode(value.encode('utf-8')).decode('utf-8')
            # data[key] = value
                    
        elif content_type is None and body_schema is not None:
            raise ValueError(f"No content type found for {endpoint.method} {endpoint.path} with non empty body schema {body_schema}")
        
        return params, data, headers, url

    def sync_execute(self, **kwargs) -> Union[Dict[str, Any], str]:
        """
        Synchronously executes the REST API call based on the provided kwargs and authentication details.
        Warning: This is a blocking call and should not be used in an async or event loop.
        """
        return asyncio.run(self.execute(**kwargs))
    
    async def execute(self, **kwargs) -> Union[Dict[str, Any], str]:
        """
        Executes the REST API call based on the provided kwargs and authentication details.

        Args:
            **kwargs: Arguments required for the API call.

        Returns:
            Union[Dict[str, Any], str]: Response from the API call.
        """
        
        if not self.schema.endpoints:
            raise ValueError("No endpoints defined in the API schema.")

        endpoint: EndpointSchema = self.schema.endpoints[0]
        method = endpoint.method.upper()
        path = endpoint.path

        def join_url(base_url: str, path: str) -> str:
            # Ensure base_url has a trailing slash for correct joining
            if not base_url.endswith('/'):
                base_url += '/'
            return urljoin(base_url, path.lstrip('/'))

        url = join_url(self.base_url, path)

        params: Dict[str, str] = {}
        data: Dict[str, Any] = {}
        headers: Dict[str, str] = {
            "Accept": "application/json",
        }

        # Handle authentication
        headers, params = self._handle_auth(headers, params)

        # Process parameters and determine content type
        # This also updates the URL if any path parameters are used
        params, data, headers, url = self._process_parameters(kwargs, params, data, headers, url, endpoint)

        # Resolve request body based on content type
        content_type, _ = self._get_content_type_and_schema(endpoint)
        request_body = self._resolve_request_body(data, content_type)

        request_kwargs: Dict[str, Any] = {
            'params': params,
            'headers': headers,
            **request_body
        }

        debug_print(f"Preparing to make API request:")
        debug_print(f"Method: {method}")
        debug_print(f"URL: {url}")
        debug_print(f"Params: {params}")
        debug_print(f"Data: {data}")
        # print(f"Headers: {headers}")
        debug_print(f"Request body: {request_body}")
        
        self.logger.log("request", {
            "method": method,
            "url": url,
            "params": params,
            "data": data,
            "headers": headers,
            "request_body": request_body
        })
        
        self.logger.log("auth", {
            "auth": self.auth.model_dump(mode="json")
        })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=5.0), **request_kwargs) as response:
                    if response.status in [500, 502, 503, 504, 429] and method in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']:
                        error_text = await response.text()
                        raise aiohttp.ClientError(f"Received status code {response.status}: {error_text}")
                    try:
                        # TODO: Might run into an issue here if the response gets chunked
                        # https://github.com/aio-libs/aiohttp/issues/1766#issuecomment-381697141
                        
                        output = await response.json()
                    except aiohttp.ContentTypeError:
                        output = await response.text()
                    finally:
                        self.logger.log("response", {
                            "status": response.status,
                            "output": output
                        })
                        return output
        except aiohttp.ClientError as e:
            raise aiohttp.ClientError(f"HTTP request failed: {e}") from e