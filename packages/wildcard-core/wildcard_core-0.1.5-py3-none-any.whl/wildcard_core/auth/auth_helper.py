from typing import Optional, Set, Tuple, Dict
from wildcard_core.tool_registry.tools.rest_api.types import APISchema, AuthConfig, AuthType, OAuth2SecurityScheme
from wildcard_core.auth.oauth_helper import OAuth2Helper, OAuth2AuthConfig
from wildcard_core.auth.auth_status import AuthStatus


class AuthRequiredError(Exception):
    """Exception raised when an API is missing authentication configuration."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class AuthHelper:
    """Helper class for managing various authentication types."""

    def __init__(self, api_schema: APISchema):
        """Initialize AuthHelper with API schema.
        
        Args:
            api_schema: The API schema containing authentication schemes
        """
        self.api_schema = api_schema
        self._auth_schemes: Dict[str, AuthConfig] = {}
        self._oauth2_helper: Optional[OAuth2Helper] = None
        self._extract_auth_schemes()

    def _extract_auth_schemes(self) -> None:
        """Extract authentication schemes from the API schema."""
        if not self.api_schema.securitySchemes:
            return
        
        # print(f"Security schemes: {self.api_schema.securitySchemes}")

        for scheme_name, scheme in self.api_schema.securitySchemes.items():
            self._auth_schemes[scheme_name] = scheme
            if isinstance(scheme, OAuth2SecurityScheme):
                self._oauth2_helper = OAuth2Helper(self.api_schema)

        # print(f"Auth schemes: {self._auth_schemes}")

    def is_auth_required(self) -> bool:
        """Check if any authentication is required by the API schema.
        
        Returns:
            True if authentication is required, False otherwise.
        """
        return bool(self.api_schema.endpoints and self.api_schema.securitySchemes)

    # TODO: This is slightly broken. It's not getting the apiKey scheme unless the scheme name is also apiKey.
    def get_required_auth_types(self) -> Set[AuthType]:
        """Retrieve all required authentication types from the API schema.
        
        Returns:
            A set of required AuthType enums.
        """
        auth_types = set()
        if not self.api_schema.endpoints:
            return auth_types

        for endpoint in self.api_schema.endpoints:
            if endpoint.security:
                for security_requirement in endpoint.security:
                    for scheme_name in security_requirement.requirements.keys():
                        scheme = self._auth_schemes.get(scheme_name)
                        if scheme:
                            auth_types.add(scheme.type)
        return auth_types

    def check_auth_requirements(
        self, 
        auth_config: Optional[AuthConfig] = None
    ) -> AuthStatus:
        """Check if authentication is required and if so, determine the type and necessary actions.
        
        Args:
            auth_config: Optional AuthConfig to check
        
        Returns:
            AuthStatus: An instance containing authentication status information.
        """
        if not self.is_auth_required():
            return AuthStatus(auth_required=False)

        required_auth_types = self.get_required_auth_types()
        # print(f"Auth config: {auth_config}")
        
        # print(f"Required auth types: {required_auth_types}")
        
        # Auth Config exists and is one of the required auth types
        if auth_config and auth_config.type != AuthType.NONE and auth_config.type in required_auth_types:
            if auth_config.type == AuthType.OAUTH2 and self._oauth2_helper is not None:
                return self._oauth2_helper.check_oauth_requirements(auth_config)
            return AuthStatus(auth_required=False)
        else:
            # print("OAuth2 helper: ", self._oauth2_helper)
            # Matching Auth Config does not exist or Auth Config is NONE
            if AuthType.OAUTH2 in required_auth_types and self._oauth2_helper is not None:
                # print("Checking OAuth2 requirements")
                return self._oauth2_helper.check_oauth_requirements(auth_config)

            # Ranked precedence of missing auth types
            auth_type_order = [AuthType.API_KEY, AuthType.BEARER, AuthType.BASIC]
            auth_type_messages = {
                AuthType.API_KEY: "API Key is missing.",
                AuthType.BEARER: "Bearer token is missing.",
                AuthType.BASIC: "Basic authentication credentials are missing."
            }
            
            missing_info = None
            for auth_type in auth_type_order:
                if auth_type in required_auth_types and auth_config.type != auth_type:
                    missing_info = auth_type_messages[auth_type]
                    break

        return AuthStatus(auth_required=True, message=missing_info, required_auth_types=required_auth_types)

    def resolve_auth(
        self, 
        auth_config: AuthConfig
    ) -> Optional[Dict[str, str]]:
        """Resolve the appropriate authentication headers based on the AuthConfig.
        
        Args:
            auth_config: The AuthConfig instance containing authentication details
        
        Returns:
            A dictionary of headers to be added to the API request
        """
        if isinstance(auth_config, OAuth2AuthConfig) and self._oauth2_helper:
            return {
                "Authorization": f"Bearer {auth_config.token}"
            }
        elif auth_config.type == AuthType.BEARER:
            return {
                "Authorization": f"Bearer {auth_config.token}"
            }
        elif auth_config.type == AuthType.BASIC:
            return {
                "Authorization": f"Basic {auth_config.credentials}"
            }
        elif auth_config.type == AuthType.API_KEY:
            # Assuming the API key should be added to the headers with a specific name
            return {
                "x-api-key": auth_config.key_value
            }
        elif auth_config.type == AuthType.NONE:
            return {}
        else:
            # Handle other auth types or raise an exception
            return None
        