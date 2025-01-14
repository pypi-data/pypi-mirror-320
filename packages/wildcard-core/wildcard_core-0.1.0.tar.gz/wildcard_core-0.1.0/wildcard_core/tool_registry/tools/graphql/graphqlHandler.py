from wildcard_core.tool_registry.tools.base import BaseAction
from typing import Any
import aiohttp
from wildcard_core.tool_registry.tools.rest_api.types.api_types import ParameterIn

class GraphQLHandler(BaseAction):
    """
    Handler for executing GraphQL queries.
    """
        
    async def execute(self, operationId: str, **kwargs) -> Any:
        if not self.operationId:
            raise ValueError("operationId must be set before making API calls")
        
        base_url = self.schema.base_url
        if not base_url:
            raise ValueError("base_url must be set before making API calls")
        
        pass
        
    #     # Retrieve the corresponding endpoint schema using the operationId
    #     endpoint = next((ep for ep in self.schema.endpoints if ep.endpoint_id == operationId), None)
    #     if not endpoint:
    #         raise ValueError(f"OperationId '{operationId}' not found in the API schema.")
        
    #     # Extract path parameters based on the endpoint schema
    #     path_params = {
    #         param.name: kwargs.pop(param.name)
    #         for param in (endpoint.parameters or [])
    #         if param.in_ == ParameterIn.PATH and param.name in kwargs
    #     }
        
    #     # Update the base_url with path parameters
    #     if path_params:
    #         try:
    #             base_url = base_url.format(**path_params)
    #         except KeyError as e:
    #             raise ValueError(f"Missing path parameter: {e.args[0]}")
        
    #     url = f"{base_url}/graphql.json"
    #     headers = {
    #         "Content-Type": "application/json",
    #     }
        
    #     # Translate remaining kwargs to GraphQL query variables
    #     # Construct variable definitions for the query
    #     variable_definitions = ", ".join([f"${key}: {self._get_graphql_type(value)}" for key, value in kwargs.items()])
        
    #     # Construct arguments to pass to the GraphQL operation
    #     arguments = ", ".join([f"{key}: ${key}" for key in kwargs.keys()])
        
    #     # Define the fields you want to retrieve from the GraphQL operation
    #     # This should be customized based on your specific needs
    #     fields = """
    #         id
    #         name
    #         # Add other fields as required
    #     """
        
    #     # Construct the full GraphQL query
    #     query = f"""
    #     query {operationId}({variable_definitions}) {{
    #         {operationId}({arguments}) {{
    #             {fields}
    #         }}
    #     }}
    #     """
        
    #     # Prepare the variables payload
    #     variables = { key: value for key, value in kwargs.items() }
        
    #     payload = {
    #         "query": query,
    #         "variables": variables
    #     }
        
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(url, headers=headers, json=payload) as response:
    #             response.raise_for_status()  # Optional: Raise an error for bad status
    #             return await response.json()
    
    # def _get_graphql_type(self, value):
    #     """
    #     Helper method to determine the GraphQL type based on the Python value.
    #     Customize this method based on your schema requirements.
    #     """
    #     if isinstance(value, int):
    #         return "Int"
    #     elif isinstance(value, float):
    #         return "Float"
    #     elif isinstance(value, bool):
    #         return "Boolean"
    #     elif isinstance(value, list):
    #         return "[String]"  # Example: Adjust based on list contents
    #     else:
    #         return "String"
    
    # def _get_graphql_type(self, value):
    #     """
    #     Helper method to determine the GraphQL type based on the Python value.
    #     Customize this method based on your schema requirements.
    #     """
    #     if isinstance(value, int):
    #         return "Int"
    #     elif isinstance(value, float):
    #         return "Float"
    #     elif isinstance(value, bool):
    #         return "Boolean"
    #     elif isinstance(value, list):
    #         return "[String]"  # Example: Adjust based on list contents
    #     else:
    #         return "String"
