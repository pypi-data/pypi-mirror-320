from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_instance_string import ResourceInstanceString

@dataclass
class ExteriorWarning_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The brakeLightCenterWarning property
    brake_light_center_warning: Optional[ResourceInstanceString] = None
    # The brakeLightLeftWarning property
    brake_light_left_warning: Optional[ResourceInstanceString] = None
    # The brakeLightRightWarning property
    brake_light_right_warning: Optional[ResourceInstanceString] = None
    # The daytimeRunningLightLeftWarning property
    daytime_running_light_left_warning: Optional[ResourceInstanceString] = None
    # The daytimeRunningLightRightWarning property
    daytime_running_light_right_warning: Optional[ResourceInstanceString] = None
    # The fogLightFrontWarning property
    fog_light_front_warning: Optional[ResourceInstanceString] = None
    # The fogLightRearWarning property
    fog_light_rear_warning: Optional[ResourceInstanceString] = None
    # The hazardLightsWarning property
    hazard_lights_warning: Optional[ResourceInstanceString] = None
    # The highBeamLeftWarning property
    high_beam_left_warning: Optional[ResourceInstanceString] = None
    # The highBeamRightWarning property
    high_beam_right_warning: Optional[ResourceInstanceString] = None
    # The lowBeamLeftWarning property
    low_beam_left_warning: Optional[ResourceInstanceString] = None
    # The lowBeamRightWarning property
    low_beam_right_warning: Optional[ResourceInstanceString] = None
    # The positionLightFrontLeftWarning property
    position_light_front_left_warning: Optional[ResourceInstanceString] = None
    # The positionLightFrontRightWarning property
    position_light_front_right_warning: Optional[ResourceInstanceString] = None
    # The positionLightRearLeftWarning property
    position_light_rear_left_warning: Optional[ResourceInstanceString] = None
    # The positionLightRearRightWarning property
    position_light_rear_right_warning: Optional[ResourceInstanceString] = None
    # The registrationPlateLightWarning property
    registration_plate_light_warning: Optional[ResourceInstanceString] = None
    # The reverseLightsWarning property
    reverse_lights_warning: Optional[ResourceInstanceString] = None
    # The sideMarkLightsWarning property
    side_mark_lights_warning: Optional[ResourceInstanceString] = None
    # The turnIndicationFrontLeftWarning property
    turn_indication_front_left_warning: Optional[ResourceInstanceString] = None
    # The turnIndicationFrontRightWarning property
    turn_indication_front_right_warning: Optional[ResourceInstanceString] = None
    # The turnIndicationRearLeftWarning property
    turn_indication_rear_left_warning: Optional[ResourceInstanceString] = None
    # The turnIndicationRearRightWarning property
    turn_indication_rear_right_warning: Optional[ResourceInstanceString] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> ExteriorWarning_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: ExteriorWarning_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return ExteriorWarning_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .resource_instance_string import ResourceInstanceString

        from .resource_instance_string import ResourceInstanceString

        fields: Dict[str, Callable[[Any], None]] = {
            "brakeLightCenterWarning": lambda n : setattr(self, 'brake_light_center_warning', n.get_object_value(ResourceInstanceString)),
            "brakeLightLeftWarning": lambda n : setattr(self, 'brake_light_left_warning', n.get_object_value(ResourceInstanceString)),
            "brakeLightRightWarning": lambda n : setattr(self, 'brake_light_right_warning', n.get_object_value(ResourceInstanceString)),
            "daytimeRunningLightLeftWarning": lambda n : setattr(self, 'daytime_running_light_left_warning', n.get_object_value(ResourceInstanceString)),
            "daytimeRunningLightRightWarning": lambda n : setattr(self, 'daytime_running_light_right_warning', n.get_object_value(ResourceInstanceString)),
            "fogLightFrontWarning": lambda n : setattr(self, 'fog_light_front_warning', n.get_object_value(ResourceInstanceString)),
            "fogLightRearWarning": lambda n : setattr(self, 'fog_light_rear_warning', n.get_object_value(ResourceInstanceString)),
            "hazardLightsWarning": lambda n : setattr(self, 'hazard_lights_warning', n.get_object_value(ResourceInstanceString)),
            "highBeamLeftWarning": lambda n : setattr(self, 'high_beam_left_warning', n.get_object_value(ResourceInstanceString)),
            "highBeamRightWarning": lambda n : setattr(self, 'high_beam_right_warning', n.get_object_value(ResourceInstanceString)),
            "lowBeamLeftWarning": lambda n : setattr(self, 'low_beam_left_warning', n.get_object_value(ResourceInstanceString)),
            "lowBeamRightWarning": lambda n : setattr(self, 'low_beam_right_warning', n.get_object_value(ResourceInstanceString)),
            "positionLightFrontLeftWarning": lambda n : setattr(self, 'position_light_front_left_warning', n.get_object_value(ResourceInstanceString)),
            "positionLightFrontRightWarning": lambda n : setattr(self, 'position_light_front_right_warning', n.get_object_value(ResourceInstanceString)),
            "positionLightRearLeftWarning": lambda n : setattr(self, 'position_light_rear_left_warning', n.get_object_value(ResourceInstanceString)),
            "positionLightRearRightWarning": lambda n : setattr(self, 'position_light_rear_right_warning', n.get_object_value(ResourceInstanceString)),
            "registrationPlateLightWarning": lambda n : setattr(self, 'registration_plate_light_warning', n.get_object_value(ResourceInstanceString)),
            "reverseLightsWarning": lambda n : setattr(self, 'reverse_lights_warning', n.get_object_value(ResourceInstanceString)),
            "sideMarkLightsWarning": lambda n : setattr(self, 'side_mark_lights_warning', n.get_object_value(ResourceInstanceString)),
            "turnIndicationFrontLeftWarning": lambda n : setattr(self, 'turn_indication_front_left_warning', n.get_object_value(ResourceInstanceString)),
            "turnIndicationFrontRightWarning": lambda n : setattr(self, 'turn_indication_front_right_warning', n.get_object_value(ResourceInstanceString)),
            "turnIndicationRearLeftWarning": lambda n : setattr(self, 'turn_indication_rear_left_warning', n.get_object_value(ResourceInstanceString)),
            "turnIndicationRearRightWarning": lambda n : setattr(self, 'turn_indication_rear_right_warning', n.get_object_value(ResourceInstanceString)),
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

        writer.write_object_value("brakeLightCenterWarning", self.brake_light_center_warning)
        writer.write_object_value("brakeLightLeftWarning", self.brake_light_left_warning)
        writer.write_object_value("brakeLightRightWarning", self.brake_light_right_warning)
        writer.write_object_value("daytimeRunningLightLeftWarning", self.daytime_running_light_left_warning)
        writer.write_object_value("daytimeRunningLightRightWarning", self.daytime_running_light_right_warning)
        writer.write_object_value("fogLightFrontWarning", self.fog_light_front_warning)
        writer.write_object_value("fogLightRearWarning", self.fog_light_rear_warning)
        writer.write_object_value("hazardLightsWarning", self.hazard_lights_warning)
        writer.write_object_value("highBeamLeftWarning", self.high_beam_left_warning)
        writer.write_object_value("highBeamRightWarning", self.high_beam_right_warning)
        writer.write_object_value("lowBeamLeftWarning", self.low_beam_left_warning)
        writer.write_object_value("lowBeamRightWarning", self.low_beam_right_warning)
        writer.write_object_value("positionLightFrontLeftWarning", self.position_light_front_left_warning)
        writer.write_object_value("positionLightFrontRightWarning", self.position_light_front_right_warning)
        writer.write_object_value("positionLightRearLeftWarning", self.position_light_rear_left_warning)
        writer.write_object_value("positionLightRearRightWarning", self.position_light_rear_right_warning)
        writer.write_object_value("registrationPlateLightWarning", self.registration_plate_light_warning)
        writer.write_object_value("reverseLightsWarning", self.reverse_lights_warning)
        writer.write_object_value("sideMarkLightsWarning", self.side_mark_lights_warning)
        writer.write_object_value("turnIndicationFrontLeftWarning", self.turn_indication_front_left_warning)
        writer.write_object_value("turnIndicationFrontRightWarning", self.turn_indication_front_right_warning)
        writer.write_object_value("turnIndicationRearLeftWarning", self.turn_indication_rear_left_warning)
        writer.write_object_value("turnIndicationRearRightWarning", self.turn_indication_rear_right_warning)
        writer.write_additional_data_value(self.additional_data)
    

