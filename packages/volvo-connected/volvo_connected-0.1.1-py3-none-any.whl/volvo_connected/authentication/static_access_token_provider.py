from typing import Any, Dict
from kiota_abstractions.authentication.access_token_provider import AccessTokenProvider, AllowedHostsValidator
class StaticAccessTokenProvider(AccessTokenProvider):
    """ Static access token provider that returns a fixed access token.	

    ARGS:	
        access_token (str): The access token to return	
    """
    def __init__(self, access_token: str):
        if not access_token:
            raise ValueError("Access token cannot be null")
        super().__init__()
        self._access_token = access_token
    
    async def get_authorization_token(
        self, uri: str, additional_authentication_context: Dict[str, Any] = {}
    ) -> str:
        return self._access_token
    
    async def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        return AllowedHostsValidator(["api.volvocars.com"])
