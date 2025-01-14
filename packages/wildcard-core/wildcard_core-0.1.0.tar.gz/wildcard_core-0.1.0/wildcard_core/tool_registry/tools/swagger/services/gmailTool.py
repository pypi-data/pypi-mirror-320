from typing import Optional
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.tool_registry.tools.rest_api.types import AuthConfig
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
from wildcard_core.tool_registry.tools.swagger.swagger_base import SwaggerBaseTool
from wildcard_core.tool_registry.tools.swagger.middleware import GmailMiddleware

class GmailTool(SwaggerBaseTool):
    """Gmail-specific tool that uses the swagger-generated client."""
    
    def __init__(
        self,
        auth: AuthConfig,
        logger: Optional[WildcardLogger],
        operationId: str,
        name: str = "gmail",
        description: str = "Gmail API tool for managing emails",
        schema: APISchema = None
    ):
        super().__init__(
            name=name,
            description=description,
            auth=auth,
            logger=logger,
            client_module="wildcard_integrations.gmail.swagger_client",
            api_class_path="api.UsersApi",
            operationId=operationId,
            middleware=GmailMiddleware(),
            schema=schema
        )
