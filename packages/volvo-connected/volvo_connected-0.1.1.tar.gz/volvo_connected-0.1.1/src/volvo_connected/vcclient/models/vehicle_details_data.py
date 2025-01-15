from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .descriptions import Descriptions
    from .images import Images

@dataclass
class VehicleDetails_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The batteryCapacityKWH property
    battery_capacity_k_w_h: Optional[float] = None
    # The descriptions property
    descriptions: Optional[Descriptions] = None
    # The externalColour property
    external_colour: Optional[str] = None
    # The fuelType property
    fuel_type: Optional[str] = None
    # The gearbox property
    gearbox: Optional[str] = None
    # The images property
    images: Optional[Images] = None
    # The modelYear property
    model_year: Optional[int] = None
    # The vin property
    vin: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> VehicleDetails_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: VehicleDetails_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return VehicleDetails_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .descriptions import Descriptions
        from .images import Images

        from .descriptions import Descriptions
        from .images import Images

        fields: Dict[str, Callable[[Any], None]] = {
            "batteryCapacityKWH": lambda n : setattr(self, 'battery_capacity_k_w_h', n.get_float_value()),
            "descriptions": lambda n : setattr(self, 'descriptions', n.get_object_value(Descriptions)),
            "externalColour": lambda n : setattr(self, 'external_colour', n.get_str_value()),
            "fuelType": lambda n : setattr(self, 'fuel_type', n.get_str_value()),
            "gearbox": lambda n : setattr(self, 'gearbox', n.get_str_value()),
            "images": lambda n : setattr(self, 'images', n.get_object_value(Images)),
            "modelYear": lambda n : setattr(self, 'model_year', n.get_int_value()),
            "vin": lambda n : setattr(self, 'vin', n.get_str_value()),
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
        from .descriptions import Descriptions
        from .images import Images

        writer.write_float_value("batteryCapacityKWH", self.battery_capacity_k_w_h)
        writer.write_object_value("descriptions", self.descriptions)
        writer.write_str_value("externalColour", self.external_colour)
        writer.write_str_value("fuelType", self.fuel_type)
        writer.write_str_value("gearbox", self.gearbox)
        writer.write_object_value("images", self.images)
        writer.write_int_value("modelYear", self.model_year)
        writer.write_str_value("vin", self.vin)
        writer.write_additional_data_value(self.additional_data)
    

