from abc import ABC, abstractmethod
from typing import Any, Dict

class SwaggerMiddleware(ABC):
    """Base class for Swagger middleware implementations."""
    
    @abstractmethod
    async def before_execute(self, operationId: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called before the swagger operation is executed.
        Can modify the input kwargs or perform any pre-processing.
        
        Args:
            operationId: The swagger operation ID being executed
            kwargs: The arguments that will be passed to the operation
            
        Returns:
            Modified kwargs to be passed to the operation
        """
        pass
        
    @abstractmethod
    async def after_execute(self, operationId: str, result: Any) -> Any:
        """
        Called after the swagger operation is executed.
        Can modify the result or perform any post-processing.
        
        Args:
            operationId: The swagger operation ID that was executed
            result: The result returned from the operation
            
        Returns:
            Modified result
        """
        pass 