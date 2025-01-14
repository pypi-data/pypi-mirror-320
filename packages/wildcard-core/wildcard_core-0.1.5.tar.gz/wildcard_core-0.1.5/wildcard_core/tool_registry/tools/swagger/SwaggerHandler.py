from typing import Any, Dict, Optional, List, Union
from wildcard_core.logging.types import NoOpLogger, WildcardLogger
from wildcard_core.tool_registry.tools.base import BaseAction
from wildcard_core.tool_registry.tools.rest_api.types import (
    AuthConfig,
    AuthType,
    BearerAuthConfig,
    ApiKeyAuthConfig,
    BasicAuthConfig,
    OAuth2AuthConfig,
)
from importlib import import_module
import base64
import inspect
import inflection
import re
from docstring_parser import DocstringStyle, parse
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
from .middleware import SwaggerMiddleware

class SwaggerHandler(BaseAction):
    """
    Handler for executing API calls using swagger-generated clients.
    """

    def __init__(
        self,
        name: str = "",
        description: str = "",
        auth: Optional[AuthConfig] = None,
        operationId: str = None, 
        logger: WildcardLogger = NoOpLogger(),
        api_class: Optional[Union[type, str]] = None,
        client_module: str = "swagger_client",
        middleware: Optional[SwaggerMiddleware] = None,
        schema: APISchema = None,

    ):
        """
        Initializes the SwaggerHandler with necessary parameters.

        Args:
            name (str): Name of the action.
            description (str): Description of the action.
            auth (Optional[AuthConfig]): Authentication details.
            operationId (str): The operationId to use for the API call.
            logger (WildcardLogger): Logger instance.
            api_class (Optional[Union[type, str]]): The swagger-generated API class to use.
            client_module (str): The client module name.
            middleware (Optional[SwaggerMiddleware]): Middleware to use for pre/post processing.
        """
        super().__init__(name, None, description, logger, schema)
        self.auth = auth
        self.api_class = api_class
        self._api_instance = None
        self._configuration = None
        self.client_module = client_module
        self.logger = logger
        self.operationId = operationId
        self.middleware = middleware
        
    @classmethod
    def valid_fields(cls) -> List[str]:
        return ["name", "description", "auth", "api_class", "operationId"]

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if key in self.valid_fields():
                setattr(self, key, value)
            
    def _configure_auth(self, configuration) -> None:
        """
        Configures authentication for the swagger client.
        """
        if not self.auth:
            return

        auth_type = AuthType(self.auth.type)

        if auth_type == AuthType.BEARER and isinstance(self.auth, BearerAuthConfig):
            configuration.access_token = self.auth.token
        elif auth_type == AuthType.API_KEY and isinstance(self.auth, ApiKeyAuthConfig):
            # Handle API key auth
            if hasattr(configuration, 'api_key'):
                configuration.api_key = {self.auth.key_name: self.auth.key_value}
                if hasattr(configuration, 'api_key_prefix'):
                    configuration.api_key_prefix = {self.auth.key_name: self.auth.key_prefix} if self.auth.key_prefix else {}
        elif auth_type == AuthType.OAUTH2 and isinstance(self.auth, OAuth2AuthConfig):
            configuration.access_token = self.auth.token
        elif auth_type == AuthType.BASIC and isinstance(self.auth, BasicAuthConfig):
            if isinstance(self.auth.credentials, str):
                configuration.username, configuration.password = base64.b64decode(
                    self.auth.credentials.encode('utf-8')
                ).decode('utf-8').split(':')
            else:
                configuration.username = self.auth.credentials.username
                configuration.password = self.auth.credentials.password

    def _get_api_instance(self):
        """
        Gets or creates an API instance with proper configuration.
        """
        if self._api_instance is None:
            if self.api_class is None:
                raise ValueError("api_class must be set before making API calls")

            # Dynamically import Configuration and ApiClient from the specified client module
            api_client_module = import_module(f"{self.client_module}.api_client")
            configuration_module = import_module(f"{self.client_module}.configuration")
            Configuration = configuration_module.Configuration
            ApiClient = api_client_module.ApiClient

            configuration = Configuration()
            self._configure_auth(configuration)
            
            api_client = ApiClient(configuration)
            self._api_instance = self.api_class(api_client)

        return self._api_instance

    async def execute(self, **kwargs) -> Union[Dict[str, Any], str]:
        """
        Executes the API call using the swagger client.

        Args:
            **kwargs: Arguments required for the API call.

        Returns:
            Union[Dict[str, Any], str]: Response from the API call.
        """
        if not self.operationId:
            raise ValueError("operationId must be set before making API calls")

        api_instance = self._get_api_instance()
        method = getattr(api_instance, inflection.underscore(self.operationId), None)
        
        if self.auth:
            self.logger.log("auth", {
                "auth": self.auth.model_dump(mode="json")
            })
        
        if method is None:
            self.logger.log("error", {
                "error": f"Method {self.operationId} not found in API class"
            })
            raise ValueError(f"Method {self.operationId} not found in API class")

        try:
            # Get the method's signature
            sig = inspect.signature(method)
            params = sig.parameters
            
            # Parse docstring to get parameter info
            docstring = method.__doc__ or ""
            parsed_docstring = parse(docstring, DocstringStyle.REST)
            
            # print("DOCSTRING:", parsed_docstring.params)
                    
            # Build parameter info with types
            param_info = {}
            for param in parsed_docstring.params:
                param_info[param.arg_name] = {
                    'description': param.description,
                    'type': param.type_name,
                    'is_optional': param.is_optional,
                }
            
            # Apply middleware pre-processing if exists
            if self.middleware:
                kwargs = await self.middleware.before_execute(self.operationId, kwargs)

            # print("PARAM INFO:", param_info)
            # Convert all kwargs keys to snake_case using inflection
            kwargs = {inflection.underscore(k): v for k, v in kwargs.items()}
            
            
            # Separate positional and keyword arguments
            pos_args = []
            kw_args = {}
            remaining_kwargs = kwargs.copy()
            
            # First identify positional parameters
            positional_params = [
                name for name, param in params.items()
                if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
            ]
        
            # Handle positional parameters
            for name in positional_params:
                if name in kwargs:
                    pos_args.append(kwargs[name])
                    remaining_kwargs.pop(name)
            
            # Process remaining kwargs based on docstring parameters
            for name, value in remaining_kwargs.copy().items():
                if name in param_info:
                    param_data = param_info[name]
                    # For non-model parameters
                    kw_args[name] = value
                    remaining_kwargs.pop(name)
            
            # Special handling for body parameter
            if 'body' in param_info:
                body_param = param_info['body']
                if body_param['type'] and body_param['type'] != 'bool':
                    try:
                        # Try to import the model class for body type
                        model_module = import_module(f"{self.client_module}.models.{inflection.underscore(body_param['type'])}")
                        ModelClass = getattr(model_module, body_param['type'])
                        
                        # print("MODEL CLASS:", ModelClass)
                        
                        # Create model instance from remaining kwargs
                        model_instance = ModelClass(**remaining_kwargs)
                        body_pos = positional_params.index('body') if 'body' in positional_params else -1
                        if body_pos != -1:
                            pos_args.insert(body_pos, model_instance)
                        else:
                            kw_args['body'] = model_instance
                        remaining_kwargs.clear()
                    except (ImportError, AttributeError):
                        # If model import fails, just use remaining kwargs as body
                        if "body" in positional_params:
                            pos_args.insert(0, remaining_kwargs)
                        else:
                            kw_args['body'] = remaining_kwargs
                        remaining_kwargs.clear()
            
            def serialize_kw_args(kw_args):
                if isinstance(kw_args, dict):
                    return {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in kw_args.items()}
                elif isinstance(kw_args, list):
                    return [item.to_dict() if hasattr(item, 'to_dict') else item for item in kw_args]
                else:
                    return kw_args
            
            self.logger.log("request", {
                "operation": self.operationId,
                "original_kwargs": kwargs,
                "positional_args": pos_args,
                "keyword_args": serialize_kw_args(kw_args),
                "remaining_kwargs": remaining_kwargs
                })
            
            # Call the method with both positional and keyword arguments
            response = method(*pos_args, **kw_args)
            
            # Apply middleware post-processing if exists
            if self.middleware:
                response = await self.middleware.after_execute(self.operationId, response)
            
            # Convert response to dict before logging
            response_dict = response.to_dict() if hasattr(response, 'to_dict') else response
            
            # Log response
            self.logger.log("response", {
                "output": response_dict
            })
            
            return response_dict

        except Exception as e:
            self.logger.log("error", str(e))
            raise Exception(str(e))