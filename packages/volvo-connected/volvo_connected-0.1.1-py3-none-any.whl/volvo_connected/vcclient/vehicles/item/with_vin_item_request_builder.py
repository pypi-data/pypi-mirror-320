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
    from ...models.error_response import ErrorResponse
    from ...models.vehicle_details import VehicleDetails
    from .brakes.brakes_request_builder import BrakesRequestBuilder
    from .commands.commands_request_builder import CommandsRequestBuilder
    from .command_accessibility.command_accessibility_request_builder import CommandAccessibilityRequestBuilder
    from .diagnostics.diagnostics_request_builder import DiagnosticsRequestBuilder
    from .doors.doors_request_builder import DoorsRequestBuilder
    from .engine.engine_request_builder import EngineRequestBuilder
    from .engine_status.engine_status_request_builder import EngineStatusRequestBuilder
    from .fuel.fuel_request_builder import FuelRequestBuilder
    from .odometer.odometer_request_builder import OdometerRequestBuilder
    from .statistics.statistics_request_builder import StatisticsRequestBuilder
    from .tyres.tyres_request_builder import TyresRequestBuilder
    from .warnings.warnings_request_builder import WarningsRequestBuilder
    from .windows.windows_request_builder import WindowsRequestBuilder

class WithVinItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vehicles/{vin}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, Dict[str, Any]]) -> None:
        """
        Instantiates a new WithVinItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vehicles/{vin}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[VehicleDetails]:
        """
        Provides details about the vehicle such as model, model-year etc. Required Scope(s): conve:vehicle_relation
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VehicleDetails]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ...models.error_response import ErrorResponse

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
        from ...models.vehicle_details import VehicleDetails

        return await self.request_adapter.send_async(request_info, VehicleDetails, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Provides details about the vehicle such as model, model-year etc. Required Scope(s): conve:vehicle_relation
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> WithVinItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithVinItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithVinItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def brakes(self) -> BrakesRequestBuilder:
        """
        The brakes property
        """
        from .brakes.brakes_request_builder import BrakesRequestBuilder

        return BrakesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def command_accessibility(self) -> CommandAccessibilityRequestBuilder:
        """
        The commandAccessibility property
        """
        from .command_accessibility.command_accessibility_request_builder import CommandAccessibilityRequestBuilder

        return CommandAccessibilityRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def commands(self) -> CommandsRequestBuilder:
        """
        The commands property
        """
        from .commands.commands_request_builder import CommandsRequestBuilder

        return CommandsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def diagnostics(self) -> DiagnosticsRequestBuilder:
        """
        The diagnostics property
        """
        from .diagnostics.diagnostics_request_builder import DiagnosticsRequestBuilder

        return DiagnosticsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def doors(self) -> DoorsRequestBuilder:
        """
        The doors property
        """
        from .doors.doors_request_builder import DoorsRequestBuilder

        return DoorsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def engine(self) -> EngineRequestBuilder:
        """
        The engine property
        """
        from .engine.engine_request_builder import EngineRequestBuilder

        return EngineRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def engine_status(self) -> EngineStatusRequestBuilder:
        """
        The engineStatus property
        """
        from .engine_status.engine_status_request_builder import EngineStatusRequestBuilder

        return EngineStatusRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def fuel(self) -> FuelRequestBuilder:
        """
        The fuel property
        """
        from .fuel.fuel_request_builder import FuelRequestBuilder

        return FuelRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def odometer(self) -> OdometerRequestBuilder:
        """
        The odometer property
        """
        from .odometer.odometer_request_builder import OdometerRequestBuilder

        return OdometerRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def statistics(self) -> StatisticsRequestBuilder:
        """
        The statistics property
        """
        from .statistics.statistics_request_builder import StatisticsRequestBuilder

        return StatisticsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def tyres(self) -> TyresRequestBuilder:
        """
        The tyres property
        """
        from .tyres.tyres_request_builder import TyresRequestBuilder

        return TyresRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def warnings(self) -> WarningsRequestBuilder:
        """
        The warnings property
        """
        from .warnings.warnings_request_builder import WarningsRequestBuilder

        return WarningsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def windows(self) -> WindowsRequestBuilder:
        """
        The windows property
        """
        from .windows.windows_request_builder import WindowsRequestBuilder

        return WindowsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithVinItemRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

