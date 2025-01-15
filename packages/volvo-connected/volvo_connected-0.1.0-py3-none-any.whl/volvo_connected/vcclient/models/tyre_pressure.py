from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .r_instance import RInstance

@dataclass
class TyrePressure(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The frontLeft property
    front_left: Optional[RInstance] = None
    # The frontRight property
    front_right: Optional[RInstance] = None
    # The rearLeft property
    rear_left: Optional[RInstance] = None
    # The rearRight property
    rear_right: Optional[RInstance] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TyrePressure:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TyrePressure
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TyrePressure()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .r_instance import RInstance

        from .r_instance import RInstance

        fields: Dict[str, Callable[[Any], None]] = {
            "frontLeft": lambda n : setattr(self, 'front_left', n.get_object_value(RInstance)),
            "frontRight": lambda n : setattr(self, 'front_right', n.get_object_value(RInstance)),
            "rearLeft": lambda n : setattr(self, 'rear_left', n.get_object_value(RInstance)),
            "rearRight": lambda n : setattr(self, 'rear_right', n.get_object_value(RInstance)),
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
        from .r_instance import RInstance

        writer.write_object_value("frontLeft", self.front_left)
        writer.write_object_value("frontRight", self.front_right)
        writer.write_object_value("rearLeft", self.rear_left)
        writer.write_object_value("rearRight", self.rear_right)
        writer.write_additional_data_value(self.additional_data)
    

