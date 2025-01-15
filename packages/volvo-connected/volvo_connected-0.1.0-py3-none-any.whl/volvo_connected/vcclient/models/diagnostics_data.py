from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_instance_integer import ResourceInstanceInteger
    from .resource_instance_string import ResourceInstanceString

@dataclass
class Diagnostics_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The distanceToService property
    distance_to_service: Optional[ResourceInstanceInteger] = None
    # The engineHoursToService property
    engine_hours_to_service: Optional[ResourceInstanceInteger] = None
    # The serviceTrigger property
    service_trigger: Optional[ResourceInstanceString] = None
    # The serviceWarning property
    service_warning: Optional[ResourceInstanceString] = None
    # The timeToService property
    time_to_service: Optional[ResourceInstanceInteger] = None
    # The washerFluidLevelWarning property
    washer_fluid_level_warning: Optional[ResourceInstanceString] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> Diagnostics_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: Diagnostics_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return Diagnostics_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .resource_instance_integer import ResourceInstanceInteger
        from .resource_instance_string import ResourceInstanceString

        from .resource_instance_integer import ResourceInstanceInteger
        from .resource_instance_string import ResourceInstanceString

        fields: Dict[str, Callable[[Any], None]] = {
            "distanceToService": lambda n : setattr(self, 'distance_to_service', n.get_object_value(ResourceInstanceInteger)),
            "engineHoursToService": lambda n : setattr(self, 'engine_hours_to_service', n.get_object_value(ResourceInstanceInteger)),
            "serviceTrigger": lambda n : setattr(self, 'service_trigger', n.get_object_value(ResourceInstanceString)),
            "serviceWarning": lambda n : setattr(self, 'service_warning', n.get_object_value(ResourceInstanceString)),
            "timeToService": lambda n : setattr(self, 'time_to_service', n.get_object_value(ResourceInstanceInteger)),
            "washerFluidLevelWarning": lambda n : setattr(self, 'washer_fluid_level_warning', n.get_object_value(ResourceInstanceString)),
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
        from .resource_instance_integer import ResourceInstanceInteger
        from .resource_instance_string import ResourceInstanceString

        writer.write_object_value("distanceToService", self.distance_to_service)
        writer.write_object_value("engineHoursToService", self.engine_hours_to_service)
        writer.write_object_value("serviceTrigger", self.service_trigger)
        writer.write_object_value("serviceWarning", self.service_warning)
        writer.write_object_value("timeToService", self.time_to_service)
        writer.write_object_value("washerFluidLevelWarning", self.washer_fluid_level_warning)
        writer.write_additional_data_value(self.additional_data)
    

