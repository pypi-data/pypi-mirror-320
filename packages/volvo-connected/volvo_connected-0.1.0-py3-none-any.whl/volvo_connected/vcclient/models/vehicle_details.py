from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .vehicle_details_data import VehicleDetails_data

@dataclass
class VehicleDetails(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The data property
    data: Optional[VehicleDetails_data] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VehicleDetails:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VehicleDetails
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VehicleDetails()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .vehicle_details_data import VehicleDetails_data

        from .vehicle_details_data import VehicleDetails_data

        fields: Dict[str, Callable[[Any], None]] = {
            "data": lambda n : setattr(self, 'data', n.get_object_value(VehicleDetails_data)),
        }
        return fields
    
    def serialize(self,writer: SerializationWriter) -> None:
        """
        Serializes information the current object
        param writer: Serialization writer to use to serialize this model
        Returns: None
        """
        if writer is None:
            raise TypeError("writer cannot be null.")
        from .vehicle_details_data import VehicleDetails_data

        writer.write_object_value("data", self.data)
        writer.write_additional_data_value(self.additional_data)
    

