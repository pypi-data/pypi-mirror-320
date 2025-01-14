from enum import Enum
from typing import Callable, Dict, Type, Optional
from wildcard_core.tool_registry.tools.DuckDuckGo.actions.search import DuckDuckGoSearch
from wildcard_core.tool_registry.tools.rest_api.RestAPIHandler import RestAPIHandler
from wildcard_core.tool_registry.tools.base import BaseAction
from wildcard_core.tool_registry.tools import GmailTool, ShopifyTool, BraveSearchTool, AirtableTool
from wildcard_core.models import APIService
from wildcard_core.client.responseProcessing.IResponseProcessor import IResponseProcessor
from wildcard_core.client.responseProcessing.services import GmailResponseProcessor, AirtableResponseProcessor, ShopifyResponseProcessor, BraveSearchResponseProcessor

class ClientType(Enum):
    REST = "rest"
    SWAGGER = "swagger"
    GRAPHQL = "graphql"

class RegistryDirectory(Enum):
    """
    Enum mapping function IDs to their corresponding Tool classes.
    Each entry maps a function ID string to the Tool class that implements it.
    """
    def __new__(cls, api_service: APIService, action_class: Type[BaseAction], client_type: ClientType = ClientType.REST, response_processor: Type[IResponseProcessor] = None):
        obj = object.__new__(cls)
        obj._value_ = api_service
        obj.action_class = action_class
        obj.client_type = client_type
        obj.response_processor = response_processor

        return obj

    @classmethod
    def get_response_handler(cls, api_service: APIService) -> Type[IResponseProcessor]:
        entry = cls(api_service)
        if entry.response_processor is None:
            raise ValueError(f"No response processor registered for action ID: {api_service}")
        return entry.response_processor

    @classmethod
    def get_action_class(cls, api_service: APIService) -> Type[BaseAction]:
        """
        Get the Tool class for a given action ID.
        
        Args:
            action_id: The action ID to look up
            
        Returns:
            The corresponding Tool class
            
        Raises:
            ValueError: If action_id is not found in registry
        """
        try:
            entry = cls(api_service)
            if entry.action_class is None:
                raise ValueError(f"No tool class registered for action ID: {api_service}")
            
            return entry.action_class
        except ValueError:
            # Fallback to RestAPIHandler for dynamic REST calls
            return RestAPIHandler
    
    # Tool mappings
    # Gmail API with swagger client
    GMAIL = (APIService.GMAIL, GmailTool, ClientType.SWAGGER, GmailResponseProcessor)  # Pass UsersApi as the swagger client
    AIRTABLE = (APIService.AIRTABLE, AirtableTool, ClientType.SWAGGER, AirtableResponseProcessor)
    SHOPIFY = (APIService.SHOPIFY, ShopifyTool, ClientType.GRAPHQL, ShopifyResponseProcessor)
    BRAVE_SEARCH = (APIService.BRAVE_SEARCH, BraveSearchTool, ClientType.SWAGGER, BraveSearchResponseProcessor)
    
    # Other tools without swagger clients
    DUCKDUCKGO = ("duckduckgo", DuckDuckGoSearch)