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
    from ..models.error_response import ErrorResponse
    from ..models.vehicle_vin import VehicleVin
    from .item.with_vin_item_request_builder import WithVinItemRequestBuilder

class VehiclesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /vehicles
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, Dict[str, Any]]) -> None:
        """
        Instantiates a new VehiclesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/vehicles", path_parameters)
    
    def by_vin(self,vin: str) -> WithVinItemRequestBuilder:
        """
        Gets an item from the ApiSdk.vehicles.item collection
        param vin: Vehicle identifier (VIN)
        Returns: WithVinItemRequestBuilder
        """
        if vin is None:
            raise TypeError("vin cannot be null.")
        from .item.with_vin_item_request_builder import WithVinItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["vin"] = vin
        return WithVinItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> Optional[VehicleVin]:
        """
        Provides all current valid relations between a Volvo Id (user) and its connected vehicles. Returns a list of VINs. Required Scope(s): conve:vehicle_relation
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[VehicleVin]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        from ..models.error_response import ErrorResponse

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
        from ..models.vehicle_vin import VehicleVin

        return await self.request_adapter.send_async(request_info, VehicleVin, error_mapping)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[QueryParameters]] = None) -> RequestInformation:
        """
        Provides all current valid relations between a Volvo Id (user) and its connected vehicles. Returns a list of VINs. Required Scope(s): conve:vehicle_relation
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> VehiclesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: VehiclesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return VehiclesRequestBuilder(self.request_adapter, raw_url)
    
    @dataclass
    class VehiclesRequestBuilderGetRequestConfiguration(RequestConfiguration[QueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

