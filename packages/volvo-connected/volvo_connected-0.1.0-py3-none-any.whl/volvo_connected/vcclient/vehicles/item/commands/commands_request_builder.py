from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ....models.command_list_response import CommandListResponse
    from ....models.error_response import ErrorResponse
    from .climatization_start.climatization_start_request_builder import ClimatizationStartRequestBuilder
    from .climatization_stop.climatization_stop_request_builder import ClimatizationStopRequestBuilder
    from .engine_start.engine_start_request_builder import EngineStartRequestBuilder
    from .engine_stop.engine_stop_request_builder import EngineStopRequestBuilder
    from .flash.flash_request_builder import FlashRequestBuilder
    from .honk.honk_request_builder import HonkRequestBuilder
    from .honk_flash.honk_flash_request_builder import HonkFlashRequestBuilder
    from .lock.lock_request_builder import LockRequestBuilder
    from .lock_reduced_guard.lock_reduced_guard_request_builder import LockReducedGuardRequestBuilder
    from .unlock.unlock_request_builder import UnlockRequestBuilder

class CommandsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vehicles/{vin}/commands
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, Dict[str, Any]]) -> None:
        """
        Instantiates a new CommandsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vehicles/{vin}/commands", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[CommandListResponse]:
        """
        Used to list the commands which can be sent to the vehicle
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[CommandListResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ....models.error_response import ErrorResponse

        error_mapping: Dict[str, type[ParsableFactory]] = {
            "400": ErrorResponse,
            "401": ErrorResponse,
            "403": ErrorResponse,
            "404": ErrorResponse,
            "405": ErrorResponse,
            "409": ErrorResponse,
            "415": ErrorResponse,
            "422": ErrorResponse,
            "500": ErrorResponse,
            "503": ErrorResponse,
            "504": ErrorResponse,
        }
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.command_list_response import CommandListResponse

        return await self.request_adapter.send_async(request_info, CommandListResponse, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Used to list the commands which can be sent to the vehicle
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> CommandsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: CommandsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return CommandsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def climatization_start(self) -> ClimatizationStartRequestBuilder:
        """
        The climatizationStart property
        """
        from .climatization_start.climatization_start_request_builder import ClimatizationStartRequestBuilder

        return ClimatizationStartRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def climatization_stop(self) -> ClimatizationStopRequestBuilder:
        """
        The climatizationStop property
        """
        from .climatization_stop.climatization_stop_request_builder import ClimatizationStopRequestBuilder

        return ClimatizationStopRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def engine_start(self) -> EngineStartRequestBuilder:
        """
        The engineStart property
        """
        from .engine_start.engine_start_request_builder import EngineStartRequestBuilder

        return EngineStartRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def engine_stop(self) -> EngineStopRequestBuilder:
        """
        The engineStop property
        """
        from .engine_stop.engine_stop_request_builder import EngineStopRequestBuilder

        return EngineStopRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def flash(self) -> FlashRequestBuilder:
        """
        The flash property
        """
        from .flash.flash_request_builder import FlashRequestBuilder

        return FlashRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def honk(self) -> HonkRequestBuilder:
        """
        The honk property
        """
        from .honk.honk_request_builder import HonkRequestBuilder

        return HonkRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def honk_flash(self) -> HonkFlashRequestBuilder:
        """
        The honkFlash property
        """
        from .honk_flash.honk_flash_request_builder import HonkFlashRequestBuilder

        return HonkFlashRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def lock(self) -> LockRequestBuilder:
        """
        The lock property
        """
        from .lock.lock_request_builder import LockRequestBuilder

        return LockRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def lock_reduced_guard(self) -> LockReducedGuardRequestBuilder:
        """
        The lockReducedGuard property
        """
        from .lock_reduced_guard.lock_reduced_guard_request_builder import LockReducedGuardRequestBuilder

        return LockReducedGuardRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def unlock(self) -> UnlockRequestBuilder:
        """
        The unlock property
        """
        from .unlock.unlock_request_builder import UnlockRequestBuilder

        return UnlockRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class CommandsRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

