from typing import Optional
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.tool_registry.tools.rest_api.types import AuthConfig
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
from wildcard_core.tool_registry.tools.swagger.swagger_base import SwaggerBaseTool
from wildcard_core.tool_registry.tools.swagger.middleware import GmailMiddleware

class BraveSearchTool(SwaggerBaseTool):
    """BraveSearch-specific tool that uses the swagger-generated client."""
    
    def __init__(
        self,
        auth: AuthConfig,
        logger: Optional[WildcardLogger],
        operationId: str,
        name: str = "brave_search",
        description: str = "BraveSearch API tool for managing search results",
        schema: APISchema = None
    ):
        super().__init__(
            name=name,
            description=description,
            auth=auth,
            logger=logger,
            client_module="wildcard_integrations.brave_search.swagger_client",
            api_class_path="api.DefaultApi",
            operationId=operationId,
            schema=schema
        )
