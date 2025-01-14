"""OAuth2 helper module for handling authentication flows and security scopes."""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone
from pydantic import BaseModel

from wildcard_core.tool_registry.tools.rest_api.types import (
    APISchema,
    OAuth2SecurityScheme,
    SecurityRequirement,
    OAuth2AuthConfig,
    OAuth2Flows,
    AuthType
)
from wildcard_core.auth.auth_status import OAuthStatus
from wildcard_core.models import APIService
from wildcard_core.events.types import ResumeExecutionInfo
class OAuth2Flow(BaseModel):
    """Represents an OAuth2 flow configuration."""
    client_id: str
    client_secret: str
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    redirect_uri: Optional[str] = None
    scopes: Set[str] = set()

class OAuthCredentialsRequiredInfo(BaseModel):
    api_service: APIService
    flows: Optional[List[OAuth2Flows]] = None
    required_scopes: Optional[Set[str]] = None
    refresh_only: bool = False
    
        
class OAuthCredentialsRequiredException(Exception):
    """Exception raised when OAuth credentials are required but not available."""
    info: OAuthCredentialsRequiredInfo
    resume_info: Optional[ResumeExecutionInfo] = None
    
    def __init__(self, info: OAuthCredentialsRequiredInfo, resume_info: Optional[ResumeExecutionInfo] = None):
        self.info = info
        self.resume_info = resume_info
        if info.refresh_only:
            super().__init__(f"Need to refresh OAuth credentials for {info.api_service.name}.")
        else:
            super().__init__(f"OAuth credentials required. Please authenticate for {info.api_service.name} with scopes: {info.required_scopes}")

class OAuth2Helper:
    """Helper class for managing OAuth2 authentication flows."""
    
    def __init__(self, api_schema: APISchema):
        """Initialize OAuth2Helper with API schema.
        
        Args:
            api_schema: The API schema containing OAuth2 security schemes
        """
        self.api_schema = api_schema
        self._oauth2_schemes: Dict[str, OAuth2SecurityScheme] = {}
        self._extract_oauth2_schemes()
    
    def _extract_oauth2_schemes(self) -> None:
        """Extract OAuth2 security schemes from the API schema."""
        if not self.api_schema.securitySchemes:
            return
            
        for scheme_name, scheme in self.api_schema.securitySchemes.items():
            if isinstance(scheme, OAuth2SecurityScheme):
                self._oauth2_schemes[scheme_name] = scheme

    def get_required_scopes(self) -> Set[str]:
        """Get all required OAuth2 scopes from the API schema.
        
        Returns:
            Set of required OAuth2 scopes
        """
        scopes = set()
        if not self.api_schema.endpoints:
            return scopes
            
        for endpoint in self.api_schema.endpoints:
            if endpoint.security:
                for security_requirement in endpoint.security:
                    scopes.update(self._get_scopes_from_requirement(security_requirement))
        return scopes

    def _get_scopes_from_requirement(self, requirement: SecurityRequirement) -> Set[str]:
        """Extract scopes from a security requirement.
        
        Args:
            requirement: Security requirement containing OAuth2 scopes
            
        Returns:
            Set of OAuth2 scopes from the requirement
        """
        scopes = set()
        for scheme_name, scheme_scopes in requirement.requirements.items():
            if scheme_name in self._oauth2_schemes:
                scopes.update(scheme_scopes)
        return scopes

    def create_auth_config(self, token: str, token_type: str = "Bearer",
                          refresh_token: Optional[str] = None,
                          expires_at: Optional[int] = None) -> OAuth2AuthConfig:
        """Create an OAuth2AuthConfig from token information.
        
        Args:
            token: OAuth2 access token
            token_type: Token type (default: "Bearer")
            refresh_token: Optional refresh token
            expires_at: Optional token expiration timestamp
            
        Returns:
            OAuth2AuthConfig instance
        """
        return OAuth2AuthConfig(
            token=token,
            token_type=token_type,
            refresh_token=refresh_token,
            expires_at=expires_at
        )

    def is_token_expired(self, auth_config: OAuth2AuthConfig) -> bool:
        """Check if the OAuth2 token is expired."""
        if not auth_config.expires_at:
            return False
        
        now = int(datetime.now(timezone.utc).timestamp())
        return now >= auth_config.expires_at
    
    def get_ordered_flows(self) -> List[OAuth2Flows]:
        """Get ordered OAuth2 flows."""
        flows: List[OAuth2Flows] = [scheme.flows for scheme in self._oauth2_schemes.values()]
        ordered_flow_type = ["authorizationCode", "implicit", "password", "clientCredentials"]
        
        def determine_priority(flow: OAuth2Flows) -> int:
            for flow_type in ordered_flow_type:
                if getattr(flow, flow_type, None) is not None:
                    return ordered_flow_type.index(flow_type)
            return len(ordered_flow_type)

        flows.sort(key=determine_priority)        
        return flows

    def get_flow_urls_for_scheme(self, scheme_name: str) -> Optional[Dict[str, str]]:
        """Get OAuth2 flow URLs for a specific security scheme."""
        if scheme_name not in self._oauth2_schemes:
            return None
            
        scheme = self._oauth2_schemes[scheme_name]
        flows = scheme.flows
        
        # Try authorization code flow first
        if flows.authorizationCode:
            return {
                "flow_type": "authorizationCode",
                "scheme_name": scheme_name,
                "auth_url": flows.authorizationCode.authorizationUrl,
                "token_url": flows.authorizationCode.tokenUrl
            }
        
        # Fall back to implicit flow
        if flows.implicit:
            return {
                "flow_type": "implicit",
                "scheme_name": scheme_name,
                "auth_url": flows.implicit.authorizationUrl
            }
        
        # Fall back to password flow
        if flows.password:
            return {
                "flow_type": "password",
                "scheme_name": scheme_name,
                "token_url": flows.password.tokenUrl
            }
        
        # Fall back to client credentials flow
        if flows.clientCredentials:
            return {
                "flow_type": "clientCredentials",
                "scheme_name": scheme_name,
                "token_url": flows.clientCredentials.tokenUrl
            }
        
        return None
    
    def validate_scopes(
        self, 
        required_scopes: Set[str], 
        auth_config: Optional[OAuth2AuthConfig] = None,
        delimiters: Set[str] = {':'}
    ) -> bool:
        """Check if the required scopes are present in the auth config.
        
        Args:
            required_scopes: Set of scopes required for the operation
            auth_config: Optional OAuth2AuthConfig containing authorized scopes
            delimiters: Set of characters used as scope hierarchy delimiters
            
        Returns:
            bool: True if all required scopes are satisfied, False otherwise
            
        Examples:
            # Various hierarchical scope formats:
            auth_scope = {"channels:history"}  # Slack-style
            required = {"channels:history:view"} -> True
            
            auth_scope = {"mail.read"}        # Microsoft-style
            required = {"mail.read.all"} -> True
            
            auth_scope = {"user/profile"}     # Custom-style
            required = {"user/profile/email"} -> True
            
            # Non-hierarchical scopes:
            auth_scope = {"profile", "email"}  # Google-style
            required = {"profile"} -> True
        """
        if not auth_config or not hasattr(auth_config, "scopes"):
            return False
        
        for required_scope in required_scopes:
            # For non-hierarchical scopes, direct membership check
            if required_scope in auth_config.scopes:
                continue
            
            # For hierarchical scopes, check parent-child relationships
            scope_satisfied = False
            
            # Try each delimiter
            for delimiter in delimiters:
                if delimiter in required_scope:
                    required_parts = required_scope.split(delimiter)
                    
                    for auth_scope in auth_config.scopes:
                        # Only process auth_scope with same delimiter
                        if delimiter not in auth_scope:
                            continue
                        
                        auth_parts = auth_scope.split(delimiter)
                        
                        # Check if auth_scope is a parent or exact match of required_scope
                        if len(auth_parts) <= len(required_parts):
                            if all(ap == rp for ap, rp in zip(auth_parts, required_parts)):
                                scope_satisfied = True
                                break
                            
                    if scope_satisfied:
                        break
                    
            if not scope_satisfied:
                return False
            
        return True

    def check_oauth_requirements(
        self, 
        auth_config: Optional[OAuth2AuthConfig] = None
    ) -> OAuthStatus:
        """Check if OAuth2 authentication is required and available.

        Args:
            auth_config: Optional AuthConfig to check

        Returns:
            OAuthStatus object indicating the authentication status.
        """
        if not self.api_schema.endpoints or not self._oauth2_schemes:
            return OAuthStatus(auth_required=False, refresh_only=False)

        # Get required scopes
        scopes = self.get_required_scopes()
        # print("REQUIRED SCOPES: ", scopes)
        if not scopes:
            return OAuthStatus(auth_required=False, refresh_only=False)

        # auth_config.scopes is a set of scopes that we have already authenticated with
        # scopes is a set of scopes that we need to authenticate with
        # If we have valid auth and existing auth config has all required scopes, no need to authenticate
        is_valid_scopes = self.validate_scopes(scopes, auth_config)
        # print("IS VALID SCOPES: ", is_valid_scopes)
        if (
            auth_config
            and auth_config.type == AuthType.OAUTH2
            and is_valid_scopes
        ):
            # Handle Expired Token Logic
            if self.is_token_expired(auth_config):
                if auth_config.refresh_token:
                    # If we're able to refresh, we only need to refresh
                    return OAuthStatus(auth_required=True, refresh_only=True, message="Authentication is valid but token is expired. Use refresh token to continue.", flows=self.get_ordered_flows(), required_scopes=scopes)
                else:
                    # Since we don't have a refresh token, we need to do a full re-authentication
                    return OAuthStatus(auth_required=True, refresh_only=False, message="Authentication is valid but token is expired and no refresh token available.")

            # The token is valid and has all required scopes
            return OAuthStatus(auth_required=False, refresh_only=False, message="Authentication is valid and all required scopes are present.")
        
        priority_flows = self.get_ordered_flows()
        return OAuthStatus(
            auth_required=True,
            refresh_only=False,
            flows=priority_flows,
            required_scopes=scopes,
            message="OAuth2 authentication is required.",
            required_auth_types={AuthType.OAUTH2}
        )
