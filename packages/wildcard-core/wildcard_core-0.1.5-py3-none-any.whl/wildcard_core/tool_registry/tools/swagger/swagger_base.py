from typing import Optional, Type
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
from wildcard_core.tool_registry.tools.swagger.SwaggerHandler import SwaggerHandler
from wildcard_core.tool_registry.tools.rest_api.types import AuthConfig
from wildcard_core.tool_registry.tools.swagger.middleware import SwaggerMiddleware
import importlib

class SwaggerBaseTool(SwaggerHandler):
    """Base class for swagger-generated tools that handles lazy client loading."""
    
    def __init__(
        self,
        name: str,
        description: str,
        auth: AuthConfig,
        logger: Optional[WildcardLogger],
        client_module: str,
        operationId: str,
        api_class_path: str,
        middleware: Optional[SwaggerMiddleware] = None,
        schema: APISchema = None
    ):
        """
        Initialize the tool with lazy client loading.
        
        Args:
            name: Name of the tool
            description: Description of the tool
            auth: Authentication configuration
            logger: Logger instance
            client_module: Name of the client module (e.g. "wildcard_gmail")
            operationId: Operation ID from the swagger spec
            api_class_path: Import path to the API class (e.g. "api.UsersApi")
            middleware: Optional middleware to use for pre/post processing
        """
        try:
            module = importlib.import_module(client_module)
            for part in api_class_path.split('.'):
                module = getattr(module, part)
            api_class = module
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not import {api_class_path} from {client_module}: {e}")
        
        super().__init__(
            name=name,
            description=description,
            auth=auth,
            logger=logger,
            api_class=api_class,
            client_module=client_module,
            operationId=operationId,
            middleware=middleware,
            schema=schema
        ) 