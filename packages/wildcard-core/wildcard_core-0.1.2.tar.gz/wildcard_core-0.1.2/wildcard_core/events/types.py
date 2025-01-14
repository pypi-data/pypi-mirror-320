from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Generic, TypeVar
from pydantic import BaseModel
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
from wildcard_core.models import APIService

T = TypeVar('T')

class WildcardEvent(str, Enum):
    """
    Events that can be triggered by the agent
    """ 
    START_OAUTH_FLOW = "start_oauth_flow"
    END_OAUTH_FLOW = "end_oauth_flow"
    START_REFRESH_TOKEN = "start_refresh_token"
    END_REFRESH_TOKEN = "end_refresh_token"
    
class WebhookRequest(BaseModel, Generic[T]):
    event: WildcardEvent
    data: T
    
class OAuthCompletionData(BaseModel):
    api_service: APIService
    token_type: str
    access_token: str
    scope: List[str]
    expires_at: Optional[int]
    refresh_token: Optional[str]

class WebhookOAuthCompletion(WebhookRequest[OAuthCompletionData]):
    event: Literal[WildcardEvent.END_OAUTH_FLOW]
    
ResumeExecutionType = Literal["tool"] | Literal["llm"]
    
class ResumeExecutionInfo(BaseModel):
    """
    Information about an interrupt that occurred while the agent was running
    """
    type: ResumeExecutionType
    
class ResumeToolExecutionInfo(ResumeExecutionInfo):
    """
    Information about an interrupt that occurred while a tool was running
    """
    type: Literal["tool"]
    tool_name: str
    tool_args: Dict[str, Any]
    tool_schema: APISchema
    