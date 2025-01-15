from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_instance_string import ResourceInstanceString

@dataclass
class Doors_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The centralLock property
    central_lock: Optional[ResourceInstanceString] = None
    # The frontLeftDoor property
    front_left_door: Optional[ResourceInstanceString] = None
    # The frontRightDoor property
    front_right_door: Optional[ResourceInstanceString] = None
    # The hood property
    hood: Optional[ResourceInstanceString] = None
    # The rearLeftDoor property
    rear_left_door: Optional[ResourceInstanceString] = None
    # The rearRightDoor property
    rear_right_door: Optional[ResourceInstanceString] = None
    # The tailgate property
    tailgate: Optional[ResourceInstanceString] = None
    # The tankLid property
    tank_lid: Optional[ResourceInstanceString] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Doors_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Doors_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Doors_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .resource_instance_string import ResourceInstanceString

        from .resource_instance_string import ResourceInstanceString

        fields: Dict[str, Callable[[Any], None]] = {
            "centralLock": lambda n : setattr(self, 'central_lock', n.get_object_value(ResourceInstanceString)),
            "frontLeftDoor": lambda n : setattr(self, 'front_left_door', n.get_object_value(ResourceInstanceString)),
            "frontRightDoor": lambda n : setattr(self, 'front_right_door', n.get_object_value(ResourceInstanceString)),
            "hood": lambda n : setattr(self, 'hood', n.get_object_value(ResourceInstanceString)),
            "rearLeftDoor": lambda n : setattr(self, 'rear_left_door', n.get_object_value(ResourceInstanceString)),
            "rearRightDoor": lambda n : setattr(self, 'rear_right_door', n.get_object_value(ResourceInstanceString)),
            "tailgate": lambda n : setattr(self, 'tailgate', n.get_object_value(ResourceInstanceString)),
            "tankLid": lambda n : setattr(self, 'tank_lid', n.get_object_value(ResourceInstanceString)),
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
        from .resource_instance_string import ResourceInstanceString

        writer.write_object_value("centralLock", self.central_lock)
        writer.write_object_value("frontLeftDoor", self.front_left_door)
        writer.write_object_value("frontRightDoor", self.front_right_door)
        writer.write_object_value("hood", self.hood)
        writer.write_object_value("rearLeftDoor", self.rear_left_door)
        writer.write_object_value("rearRightDoor", self.rear_right_door)
        writer.write_object_value("tailgate", self.tailgate)
        writer.write_object_value("tankLid", self.tank_lid)
        writer.write_additional_data_value(self.additional_data)
    

