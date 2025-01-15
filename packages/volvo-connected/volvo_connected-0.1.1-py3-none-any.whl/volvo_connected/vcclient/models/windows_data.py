from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_instance_string import ResourceInstanceString

@dataclass
class Windows_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The frontLeftWindow property
    front_left_window: Optional[ResourceInstanceString] = None
    # The frontRightWindow property
    front_right_window: Optional[ResourceInstanceString] = None
    # The rearLeftWindow property
    rear_left_window: Optional[ResourceInstanceString] = None
    # The rearRightWindow property
    rear_right_window: Optional[ResourceInstanceString] = None
    # The sunroof property
    sunroof: Optional[ResourceInstanceString] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Windows_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Windows_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Windows_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .resource_instance_string import ResourceInstanceString

        from .resource_instance_string import ResourceInstanceString

        fields: Dict[str, Callable[[Any], None]] = {
            "frontLeftWindow": lambda n : setattr(self, 'front_left_window', n.get_object_value(ResourceInstanceString)),
            "frontRightWindow": lambda n : setattr(self, 'front_right_window', n.get_object_value(ResourceInstanceString)),
            "rearLeftWindow": lambda n : setattr(self, 'rear_left_window', n.get_object_value(ResourceInstanceString)),
            "rearRightWindow": lambda n : setattr(self, 'rear_right_window', n.get_object_value(ResourceInstanceString)),
            "sunroof": lambda n : setattr(self, 'sunroof', n.get_object_value(ResourceInstanceString)),
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

        writer.write_object_value("frontLeftWindow", self.front_left_window)
        writer.write_object_value("frontRightWindow", self.front_right_window)
        writer.write_object_value("rearLeftWindow", self.rear_left_window)
        writer.write_object_value("rearRightWindow", self.rear_right_window)
        writer.write_object_value("sunroof", self.sunroof)
        writer.write_additional_data_value(self.additional_data)
    

