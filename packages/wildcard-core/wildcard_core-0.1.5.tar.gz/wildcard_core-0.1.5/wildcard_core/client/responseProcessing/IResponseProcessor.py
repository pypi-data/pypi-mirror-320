from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel
from wildcard_core.logging.types import WildcardLogger

class ProcessedResponseData(BaseModel):
    """
    A class that represents the processed response from a tool.
    """
    data: Any
    documents: Dict[str, Any]

class ProcessedResponse(BaseModel):
    """
    A class that represents the original response from the tool and the processed response.
    """
    response: Any
    processed_response: ProcessedResponseData


class IResponseProcessor(ABC):
    """Base class for response processors."""
    
    def __init__(self, logger: WildcardLogger):
        self.logger = logger
    
    @abstractmethod
    async def process(self, tool_name: str, result: Dict[str, Any]) -> ProcessedResponse:
        """
        Process the response from the operation.
        """
        pass 

