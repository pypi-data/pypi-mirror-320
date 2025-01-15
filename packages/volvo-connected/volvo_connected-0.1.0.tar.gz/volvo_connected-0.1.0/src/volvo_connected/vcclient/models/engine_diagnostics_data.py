from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_instance_string import ResourceInstanceString

@dataclass
class EngineDiagnostics_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The engineCoolantLevelWarning property
    engine_coolant_level_warning: Optional[ResourceInstanceString] = None
    # The oilLevelWarning property
    oil_level_warning: Optional[ResourceInstanceString] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> EngineDiagnostics_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: EngineDiagnostics_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return EngineDiagnostics_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .resource_instance_string import ResourceInstanceString

        from .resource_instance_string import ResourceInstanceString

        fields: Dict[str, Callable[[Any], None]] = {
            "engineCoolantLevelWarning": lambda n : setattr(self, 'engine_coolant_level_warning', n.get_object_value(ResourceInstanceString)),
            "oilLevelWarning": lambda n : setattr(self, 'oil_level_warning', n.get_object_value(ResourceInstanceString)),
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

        writer.write_object_value("engineCoolantLevelWarning", self.engine_coolant_level_warning)
        writer.write_object_value("oilLevelWarning", self.oil_level_warning)
        writer.write_additional_data_value(self.additional_data)
    

