import os
import aiohttp
import json
from typing import Any, Dict, List, Optional, Callable, Set, Tuple, Union
from urllib.parse import urljoin
from aiohttp import ClientResponse
from pydantic import BaseModel
from wildcard_core.auth import AuthStatus, AuthHelper
from wildcard_core.auth.auth_helper import AuthRequiredError
from wildcard_core.auth.auth_status import OAuthStatus
from wildcard_core.auth.oauth_helper import OAuthCredentialsRequiredException, OAuthCredentialsRequiredInfo
from wildcard_core.models import ActionType
from wildcard_core.models.IdRegistry import IdRegistry
from wildcard_core.tool_registry import RegistryDirectory
from wildcard_core.tool_registry.tools.rest_api import RestAPIHandler
from wildcard_core.tool_search.utils.api_service import APIService
from wildcard_core.tool_registry.tools.rest_api.types import APISchema, AuthConfig, AuthType, BaseAuthConfig, OAuth2Flows, OAuth2AuthConfig, AuthConfigBuilder
from wildcard_core.events.types import OAuthCompletionData, ResumeToolExecutionInfo
from wildcard_core.tool_search.types import SearchEndpointsRequest
from wildcard_core.tool_search.utils.helpers import ensure_sync, load_config, aiohttp_with_exponential_backoff
from wildcard_core.tool_search.utils.parse_openapi import openapi_to_api_schema
from wildcard_core.logging.types import WildcardLogger, NoOpLogger
from wildcard_core.tool_search.responseProcessing.IResponseProcessor import ProcessedResponse

class ToolSearchClient(BaseModel, arbitrary_types_allowed=True):
    api_key: str
    auth_configs: Dict[APIService, AuthConfig] = {}
    _agent_factory: Optional[Callable] = None
    webhook_url: Optional[str] = None
    index_name: Optional[str] = None
    logger: WildcardLogger = NoOpLogger()
        
    def __init__(self, api_key: str, index_name: str = None, webhook_url: str = None, logger: WildcardLogger = NoOpLogger()):
        super().__init__(api_key=api_key, index_name=index_name, webhook_url=webhook_url, logger=logger)
        
    @classmethod
    def patch_from_dict(cls, data: Union[Dict[str, Any], "ToolSearchClient"]) -> "ToolSearchClient":
        """
        Passing the client around in some libraries will cause the client to be serialized as a dict.
        This method patches the client from a dict.
        """
        
        # print("DATA TYPE", type(data))
        
        def patch_auth_configs(auth_configs: Dict[Union[str, APIService], Any]) -> Dict[APIService, AuthConfig]:
            patched_auth_configs = {}
            for api_id, auth_config in auth_configs.items():
                api_service = api_id if isinstance(api_id, APIService) else APIService(api_id)
                patched_auth_configs[api_service] = AuthConfigBuilder(auth_config=auth_config).auth_config
            return patched_auth_configs
        
        auth_configs = data.auth_configs if isinstance(data, ToolSearchClient) else data.get("auth_configs", {})
        
        # print("ORIGINAL AUTH CONFIGS", auth_configs)
        # print("AUTH CONFIGS INPUT TYPE", type(auth_configs))
        if isinstance(data, ToolSearchClient):
            data.auth_configs = patch_auth_configs(data.auth_configs)
            
            # print("AUTH CONFIGS OUTPUT TYPE", type(data.auth_configs))
            
            # print("PATCHED AUTH CONFIGS", data.auth_configs)
            return data
        
        return cls(**data, auth_configs=patch_auth_configs(auth_configs))

    """
    Client class for the Tool Search API.

    Responsible for creating a client object that will be used as context.
    Allows registering authentication configurations for particular APIs.
    """

    async def get_action_schema(self, action_id: str, collection_name: str = None) -> APISchema:
        """
        Get the schema for a function from the API
        """
        config = load_config(os.path.join(os.path.dirname(__file__), 'config.yml'))
        url = config['endpoints'][os.getenv('WILDCARD_ENV', config['env'])]['endpoint_details_url']
        collection_name = collection_name if collection_name else self.index_name
        params = {
            'id': action_id,
        }
        params['collection_name'] = collection_name
            
            
        # print("GETTING SCHEMA", url)
        # print("PARAMS", params)
        # print("COLLECTION NAME", collection_name)
        
        async with aiohttp.ClientSession() as session:
            response = await aiohttp_with_exponential_backoff(
                method='GET',
                url=url,
                session=session,
                params=params
            )
            if response.status != 200:
                raise Exception(f"Failed to get schema for {action_id}: {response.status} {response.text}")
            schema = await response.json(content_type=None)
            
            self.logger.log("openapi_spec", schema)
                        
            # Validate schema
            if schema is None:
                raise Exception(f"No OpenAPI spec content found in schema for {action_id}")
            if "content" not in schema:
                raise Exception(f"No OpenAPI spec content found in schema for {action_id}")
            if "metadata" not in schema:
                raise Exception(f"No metadata found in schema for {action_id}")
            if "api_id" not in schema["metadata"]:
                raise Exception(f"No API ID found in schema for {action_id}")
            
            openapi_spec = schema["content"]
            api_id = APIService(schema["metadata"]["api_id"])
            return openapi_to_api_schema(openapi_spec, action_id, api_id)        

    async def search_endpoints(self, req: SearchEndpointsRequest) -> Dict[str, Any]:
        """
        Search for endpoints that match a query
        Because this is an async method, it is the responsibility of the caller to close the session.
        """
        config = load_config(os.path.join(os.path.dirname(__file__), 'config.yml'))
        limit = req.get('limit', 5)
        index_name = req.get('index_name', self.index_name)
        
        url = config['endpoints'][os.getenv('WILDCARD_ENV', config['env'])]['search_url']
        params = {
            'q': req['q'],
            'limit': limit,
            'search_type': 'multi',
            'vectorize_method': 'jinaai',
            'index_name': index_name,
            'q2': req['q2'],
            'rerank': 'True',
        }
        if index_name:
            params['index_name'] = index_name
        
        
        # print("SEARCHING ENDPOINTS", req, url, params)
        async with aiohttp.ClientSession() as session:
            response = await session.get(url, params=params)
            json_data = await response.json(content_type=None) if response else {}
            return json_data

    def register_api_auth(self, api_id: APIService, auth_config: AuthConfig) -> None:
        """
        Registers an authentication configuration for a specified API.

        Args:
            api_id (APIService): The unique identifier of the API.
            auth_config (AuthConfig): The authentication configuration for the API.
        """
        self.auth_configs[api_id] = auth_config

    def get_api_auth(self, api_id: str) -> AuthConfig:
        """
        Get the authentication configuration for an API
        """
        return self.auth_configs.get(api_id, BaseAuthConfig(type=AuthType.NONE))
    
    def sync_initiate_oauth(self, flows: List[OAuth2Flows], api_service: APIService, webhook_url: str, required_scopes: Optional[Set[str]] = None) -> str:
        return ensure_sync(self.initiate_oauth)(flows, api_service, webhook_url, required_scopes)
        
    async def initiate_oauth(self, flows: List[OAuth2Flows], api_service: APIService, webhook_url: str, required_scopes: Optional[Set[str]] = None) -> str:
        """
        Initiates the OAuth flow by requesting the authorization URL from the auth service.

        Args:
            api_service (str): The API service requiring OAuth.
            required_scopes (set, optional): Scopes required for the OAuth flow.
            webhook_url (str): The webhook URL that listens to Wildcard events. Receives the OAuth tokens.
            flows (List[OAuth2Flows]): The OAuth flows to initiate in the priority order they should be attempted.

        Returns:
            str: The authorization URL to redirect the user.
        """
        
        # TODO: Support multiple flows
        flow = flows[0]
        
        if not flow.authorizationCode:
            raise Exception("ONLY AUTHORIZATION CODE FLOW IS SUPPORTED AT THIS TIME")
        
        config = load_config(os.path.join(os.path.dirname(__file__), 'config.yml'))
        auth_service_start_flow_url = urljoin(config['endpoints'][os.getenv('WILDCARD_ENV', config['env'])]['agentauth_url'], f"oauth_flow/{api_service.value}")

        payload = {
            "api_service": api_service.value,
            "required_scopes": list(required_scopes),
            "flow": flow.model_dump(),
            "webhook_url": webhook_url
        }

        # print("STARTING FLOW", auth_service_start_flow_url)
        # print("PAYLOAD", payload)
        
        try:
            async with aiohttp.ClientSession() as session:
                response = await aiohttp_with_exponential_backoff(
                    method='POST',
                    url=auth_service_start_flow_url,
                    session=session,
                    json=payload
                )
                
                response_json = await response.json()
                return response_json.get("authorization_url")
        except Exception as e:
            raise Exception(f"Failed to initiate OAuth flow for {api_service}: {e}")
        
    async def refresh_token(self, api_service: APIService, webhook_url: str) -> None:
        """
        Refreshes the token for an API
        """
        config = load_config(os.path.join(os.path.dirname(__file__), 'config.yml'))
        auth_service_refresh_token_url = urljoin(config['endpoints'][os.getenv('WILDCARD_ENV', config['env'])]['agentauth_url'], f"refresh_token/{api_service.value}")
        
        payload = {
            "api_service": api_service.value,
            "webhook_url": webhook_url
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                response = await aiohttp_with_exponential_backoff(
                    method='POST',
                    url=auth_service_refresh_token_url,
                    session=session,
                    json=payload
                )
                
                response_json = await response.json()
                # print("REFRESH TOKEN RESPONSE", response_json)
        except Exception as e:
            raise Exception(f"Failed to refresh token for {api_service}: {e}")

    def handle_webhook_callback(self, data: OAuthCompletionData) -> None:
        """Handles the webhook callback by registering the obtained token."""
        self.register_api_auth(
            api_id=data.api_service,
            auth_config=OAuth2AuthConfig(
                type=AuthType.OAUTH2,
                token_type=data.token_type,
                token=data.access_token,
                refresh_token=data.refresh_token,
                expires_at=data.expires_at,
                scopes=set(data.scope)
            )
        )
    
    async def get_auth_status(self, function_id: str) -> Tuple[AuthStatus, Optional[APISchema]]:
        """
        Get the auth status for a functionId
        """
        function = RegistryDirectory.get_action_class(function_id)
        if isinstance(function, RestAPIHandler):
            schema: APISchema = await self.get_action_schema(function_id)
            auth = self.get_api_auth(schema.id)
            return (AuthHelper(schema).check_auth_requirements(auth), schema if schema else None)
        
        
        return (AuthStatus(auth_required=False), None)
        
    async def run_tool_with_args(self, tool_name: ActionType, schema: Optional[APISchema] = None, **kwargs) -> ProcessedResponse:
        tool_id = IdRegistry.get_id(tool = tool_name)
        api_service = tool_name.get_api_service()
        ToolClass = RegistryDirectory.get_action_class(api_service)
        
        if not schema:
            schema: APISchema = await self.get_action_schema(tool_id)
        
        # Check Auth
        auth = self.get_api_auth(api_service)
        auth_helper = AuthHelper(schema)
        auth_status = auth_helper.check_auth_requirements(auth)
        
        if isinstance(auth_status, OAuthStatus) and auth_status.auth_required:
            info = OAuthCredentialsRequiredInfo(
                api_service=api_service,
                flows=auth_status.flows,
                required_scopes=auth_status.required_scopes,
            )
            
            resume_info = ResumeToolExecutionInfo(
                type="tool",
                tool_name=tool_name,
                tool_args=kwargs,
                tool_schema=schema,
            )
            raise OAuthCredentialsRequiredException(info, resume_info)
        elif auth_status.auth_required:
            # Configuration issue with the required API
            raise AuthRequiredError(f"API {tool_name} is missing authentication configuration: {auth_status.message}")
        
        tool = ToolClass(logger=self.logger, auth=auth, operationId=tool_name.value, schema=schema)

        raw_result_dict = await tool.execute(**kwargs)

        #  parse the raw result into the pure response and the supplemental documents like attachments
        #  the response should be a string
         # Apply middleware post-processing if exists
        ResponseProcessorClass = RegistryDirectory.get_response_handler(api_service)
        response_processor = ResponseProcessorClass(self.logger)
        processed_response: ProcessedResponse = await response_processor.process(tool_name, raw_result_dict)
        
        self.logger.log("processed_response", processed_response.model_dump())

        return processed_response
