import aiohttp
import importlib
from typing import Callable, Optional
from wildcard_core.logging.types import WildcardLogger
from wildcard_core.tool_registry.tools.base import BaseAction
from wildcard_core.tool_registry.tools.graphql.graphqlHandler import GraphQLHandler
from wildcard_core.tool_registry.tools.rest_api.types import APISchema, AuthConfig
from wildcard_core.auth.auth_types import AuthType

class ShopifyTool(GraphQLHandler):
    
    def __init__(
        self,
        name: str = "",
        operationId: str = "",
        auth: Optional[AuthConfig] = None,
        schema: APISchema = None,
        description: str = "",
        logger: WildcardLogger = None
    ):
        super().__init__(name, operationId, schema, description, logger)
        
        action_function_map = {
            "product_get": self.product_get,
            "product_update": self.product_update,
        }
        
        prefix, func_name = operationId.split('_', 1)
        if prefix != 'shopify':
            raise ValueError(f"Invalid operation prefix: {prefix}")
        
        self.operation = action_function_map.get(func_name, None)
        self.auth = auth        
    
    async def execute(self, **kwargs):
        
        storeId = kwargs.get("storeId")
        
        if not self.auth:
            raise ValueError("Auth is required")
        
        if self.auth:
            self.logger.log("auth", {
                "auth": self.auth.model_dump(mode="json")
            })
        
        if self.auth.type == AuthType.API_KEY:
            accessToken = self.auth.key_value
        else:
            raise ValueError("Invalid auth type", self.auth.type)
        
        if not storeId:
            raise ValueError("Store ID is required")
        
        
        url = f"https://{storeId}.myshopify.com/admin/api/graphql.json"
        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": accessToken
        }
        
        query = self.operation(**kwargs)
        
        payload = {
            "query": query
        }

        self.logger.log("request", {
            "url": url,
            "headers": headers,
            "payload": payload
        })
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                response_data = await response.json()
        
        response_dict = response_data.to_dict() if hasattr(response_data, 'to_dict') else response_data

        if not response_dict:
            raise ValueError("No response data")
        
        # Log Response Data
        self.logger.log("response", {
            "response_data": response_dict
        })
        
        # Post Process Response Data
        
        return response_dict
    
    
    def product_get(self, **kwargs):
        """
        Get products from Shopify
        Args:
            limit (int): The maximum number of products to return
        """
        limit = kwargs.get("limit", 10)
        
        query = f"""
        query GetProducts {{
            products(first: {limit}) {{
                nodes {{
                    id
                    title
                    descriptionHtml
                }}
            }}
        }}
        """
        return query
    
    def product_update(self, **kwargs):
        """
        Update a product in Shopify
        Args:
            productId (str): The ID of the product to update
            title (str): The new title of the product
            descriptionHtml (str): The new description of the product
        """
        
        productId = kwargs.get("productId")
        title = kwargs.get("title")
        descriptionHtml = kwargs.get("descriptionHtml")
        
        # TODO: Validate missing fields?
        
        # Remove prefix if it already exists
        if productId.startswith("gid://shopify/Product/"):
            productId = productId.replace("gid://shopify/Product/", "")
            
        field_to_modify = []
        if title:
            field_to_modify.append(f", title: \"{title}\"")
        if descriptionHtml:
            field_to_modify.append(f", descriptionHtml: \"{descriptionHtml}\"")
        query = f"""
        mutation {{
            productUpdate(input: {{id: "gid://shopify/Product/{productId}"{' '.join(field_to_modify)}}}) {{
                product {{
                    id
                }}
            }}
        }}
        """
        return query