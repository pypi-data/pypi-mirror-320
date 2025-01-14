from typing import Optional
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.tool_registry.tools.rest_api.types import AuthConfig
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
from wildcard_core.tool_registry.tools.swagger.swagger_base import SwaggerBaseTool

def get_api_class_path(operationId: str) -> str:
    """Get the appropriate API class path based on the operationId."""
    parts = operationId.split('_')
    if len(parts) < 3:
        raise ValueError(f"Invalid operationId: {operationId}")
        
    if operationId == "airtable_get_user_info":
        return "UserApi"
        
    api_map = {
        "bases": "BasesApi",
        "tables": "TablesApi",
        "records": "RecordsApi",
        "comments": "CommentsApi",
        "fields": "FieldsApi",
        "user": "UserApi"
    }
    
    api_class_path = api_map.get(parts[1], None)
    if not api_class_path:
        raise ValueError(f"Invalid operationId: {operationId}")
    return api_class_path

class AirtableTool(SwaggerBaseTool):
    """Airtable-specific tool that uses the swagger-generated client."""
    
    def __init__(
        self,
        auth: AuthConfig,
        logger: Optional[WildcardLogger],
        operationId: str,
        name: str = "airtable",
        description: str = "Airtable API tool for managing database data",
        schema: APISchema = None
    ):
        super().__init__(
            name=name,
            description=description,
            auth=auth,
            logger=logger,
            client_module="wildcard_integrations.airtable.swagger_client",
            api_class_path=get_api_class_path(operationId),
            operationId=operationId,
            schema=schema
        )
