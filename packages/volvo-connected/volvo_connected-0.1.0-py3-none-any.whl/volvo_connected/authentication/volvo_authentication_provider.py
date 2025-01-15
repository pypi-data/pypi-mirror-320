from typing import Any, Dict
from kiota_abstractions.headers_collection import HeadersCollection
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.authentication.authentication_provider import AuthenticationProvider
from kiota_abstractions.authentication.base_bearer_token_authentication_provider import BaseBearerTokenAuthenticationProvider
from kiota_abstractions.authentication.access_token_provider import AccessTokenProvider

class VolvoAuthenticationProvider(BaseBearerTokenAuthenticationProvider):
    """ Volvo authentication provider that adds the VCC API key to the headers, and calls the access token provider to add the bearer token.
    
    ARGS:
        vcc_api_key (str): The VCC API key (see https://developer.volvocars.com/apis/connected-vehicle/v2/details/)
        access_token_provider (AccessTokenProvider): The access token provider to use to get the bearer token

    """

    VCC_API_KEY_HEADER = "vcc-api-key"
    AUTHORIZATION_HEADER = "Authorization"
    def __init__(self, vcc_api_key: str, access_token_provider: AccessTokenProvider):
        if not vcc_api_key:
            raise ValueError("VCC API key cannot be null or empty")
        if not access_token_provider:
            raise TypeError("Access token provider cannot be null")

        super().__init__(access_token_provider)
        #self._access_token_provider = access_token_provider
        self._vcc_api_key = vcc_api_key

    async def authenticate_request(self, request: RequestInformation, additional_authentication_context: Dict[str, Any] = {}) -> None:
        """" Authenticates the request by adding the VCC API key to the headers, and calling the access token provider to add the bearer token """

        # Check if the request is null
        if not request:
            raise Exception("Request cannot be null")
        
        # Initialize the headers collection if it does not exist
        if not request.headers:
            request.headers = HeadersCollection()

        # Remove the VCC API key if it exists
        # if self.VCC_API_KEY_HEADER in request.headers:
        #     request.headers.remove(self.VCC_API_KEY_HEADER)
        
        # Add the VCC API key to the headers
        request.headers.add('vcc-api-key', [self._vcc_api_key])

        # if not request.headers.contains(self.AUTHORIZATION_HEADER):
        #     token = await self._access_token_provider.get_authorization_token(
        #         request.url, additional_authentication_context
        #     )
        #     if token:
        #         request.headers.add(self.AUTHORIZATION_HEADER, [f'Bearer {token}'])

        # Call the base class authenticate_request method (which calls the access token provider)
        await super().authenticate_request(request, additional_authentication_context)

