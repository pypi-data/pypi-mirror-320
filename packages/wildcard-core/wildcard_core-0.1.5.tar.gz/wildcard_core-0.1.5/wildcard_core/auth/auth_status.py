from typing import List, Optional, Set

from wildcard_core.tool_registry.tools.rest_api.types import AuthType, OAuth2Flows

class AuthStatus:
    """Represents the authentication requirements for an API schema."""
    
    def __init__(
        self,
        auth_required: bool,
        message: Optional[str] = None,
        required_auth_types: Optional[Set[AuthType]] = None,
    ):
        """
        Initialize AuthStatus.

        Args:
            auth_required (bool): Indicates if authentication is required.
            message (Optional[str]): Message describing the authentication status.
            auth_url (Optional[str]): URL for authentication if needed (e.g., OAuth2).
            required_scopes (Optional[Set[str]]): Required scopes for OAuth2 authentication.
            scheme_name (Optional[str]): Name of the authentication scheme.
        """
        self.auth_required = auth_required
        self.message = message
        self.required_auth_types = required_auth_types
        
    def __repr__(self):
        return (
            f"AuthStatus(auth_required={self.auth_required}, "
            f"message={self.message}, "
            f"required_auth_types={self.required_auth_types})"
        )

class OAuthStatus(AuthStatus):
    """Represents the authentication requirements for an API schema."""
    
    def __init__(
        self, 
        auth_required: bool,
        refresh_only: bool,
        message: Optional[str] = None, 
        required_auth_types: Optional[Set[AuthType]] = None,
        flows: Optional[List[OAuth2Flows]] = None,
        required_scopes: Optional[Set[str]] = None,
    ):
        super().__init__(auth_required, message, required_auth_types=required_auth_types)
        self.flows = flows
        self.required_scopes = required_scopes
        self.refresh_only = refresh_only
        
    def __repr__(self):
        return (
            f"OAuthStatus(auth_required={self.auth_required}, "
            f"refresh_only={self.refresh_only}, "
            f"message={self.message}, "
            f"flows={self.flows}, "
            f"required_scopes={self.required_scopes})"
        )
