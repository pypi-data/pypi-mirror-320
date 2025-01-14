from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.auth.auth_types import AuthConfig
from wildcard_core.tool_registry.tools.rest_api.types.api_types import APISchema
import json
class BaseAction(ABC):
    """Abstract base class for all actions, defining required metadata and execute method."""
    def __init__(
        self,
        name: str = "",
        operationId: str = "",
        schema: APISchema = None,
        description: str = "",
        logger: WildcardLogger = None
    ):
        self.name = name
        self.operationId = operationId
        self.schema = schema
        self.description = description
        self.logger = logger
        
    @classmethod
    def init_from_dict(cls, data: Dict[str, Any]):
        for key, value in data.items():
            setattr(cls, key, value)
        return cls
    
    
    def update_from_dict(self, data: Dict[str, Any]):
        for key, value in data.items():
            setattr(self, key, value)
    
    @abstractmethod
    def execute(self, operationId: str, **kwargs) -> Any:
        """Executes the action using provided arguments."""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Returns a dictionary with action metadata."""
        return {
            "name": self.name,
            "id": self.operationId,
            "schema": self.schema,
            "description": self.description
        }

    def get_auth_config(self) -> Optional[AuthConfig]:
        """
        Retrieves authentication configuration for the action.
        This general method can be overridden by subclasses to provide specific auth configurations.

        Returns:
            Optional[AuthConfig]: Authentication configuration or None.
        """
        return None

class BaseTool(ABC):
    """Represents a tool containing multiple actions."""

    def __init__(
        self,
        name: str,
        tool_id: str,
        description: str,
        actions: List[BaseAction]
    ):
        self.name = name
        self.tool_id = tool_id
        self.description = description
        self.actions = actions

    def add_action(self, action: BaseAction):
        """Registers an action to this tool."""
        self.actions.append(action)
        
    def get_actions_info(self) -> List[Dict[str, Any]]:
        """Returns metadata for all actions within this tool."""
        return [action.get_info() for action in self.actions]
    
    def get_info(self) -> Dict[str, Any]:
        """Returns metadata for this tool."""
        return {
            "name": self.name,
            "id": self.tool_id,
            "description": self.description,
            "actions_count": len(self.actions)
        }
