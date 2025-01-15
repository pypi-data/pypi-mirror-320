from typing import Any, Callable, Dict
from kiota_abstractions.authentication.access_token_provider import AccessTokenProvider, AllowedHostsValidator
class DynamicAccessTokenProvider(AccessTokenProvider):
    """ Dynamic access token provider that calls a function to get the access token.	

    ARGS:	
        access_token_function (Callable[[str], str]): The function to call to get the access token. The function takes a URI as a parameter and returns the access token.
    """
    def __init__(self, access_token_function: Callable[[str], str]):
        if not access_token_function:
            raise ValueError("Access token function cannot be null")
        super().__init__()
        self._access_token_function = access_token_function
    
    async def get_authorization_token(
        self, uri: str, additional_authentication_context: Dict[str, Any] = {}
    ) -> str:
        return self._access_token_function(uri)
    
    async def get_allowed_hosts_validator(self) -> AllowedHostsValidator:
        return AllowedHostsValidator(["api.volvocars.com"])
