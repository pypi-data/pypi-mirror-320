from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .resource_instance_float import ResourceInstanceFloat
    from .resource_instance_integer import ResourceInstanceInteger
    from .r_instance_with_unit import RInstanceWithUnit

@dataclass
class StatisticVals(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The averageEnergyConsumption property
    average_energy_consumption: Optional[ResourceInstanceFloat] = None
    # The averageFuelConsumption property
    average_fuel_consumption: Optional[RInstanceWithUnit] = None
    # The averageSpeed property
    average_speed: Optional[ResourceInstanceInteger] = None
    # The averageSpeedAutomatic property
    average_speed_automatic: Optional[ResourceInstanceInteger] = None
    # The distanceToEmpty property
    distance_to_empty: Optional[RInstanceWithUnit] = None
    # The distanceToEmptyBattery property
    distance_to_empty_battery: Optional[ResourceInstanceInteger] = None
    # The tripMeterAutomatic property
    trip_meter_automatic: Optional[ResourceInstanceFloat] = None
    # The tripMeterManual property
    trip_meter_manual: Optional[ResourceInstanceFloat] = None
    # The tripMeter1 property
    trip_meter1: Optional[RInstanceWithUnit] = None
    # The tripMeter2 property
    trip_meter2: Optional[RInstanceWithUnit] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> StatisticVals:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: StatisticVals
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return StatisticVals()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .resource_instance_float import ResourceInstanceFloat
        from .resource_instance_integer import ResourceInstanceInteger
        from .r_instance_with_unit import RInstanceWithUnit

        from .resource_instance_float import ResourceInstanceFloat
        from .resource_instance_integer import ResourceInstanceInteger
        from .r_instance_with_unit import RInstanceWithUnit

        fields: Dict[str, Callable[[Any], None]] = {
            "averageEnergyConsumption": lambda n : setattr(self, 'average_energy_consumption', n.get_object_value(ResourceInstanceFloat)),
            "averageFuelConsumption": lambda n : setattr(self, 'average_fuel_consumption', n.get_object_value(RInstanceWithUnit)),
            "averageSpeed": lambda n : setattr(self, 'average_speed', n.get_object_value(ResourceInstanceInteger)),
            "averageSpeedAutomatic": lambda n : setattr(self, 'average_speed_automatic', n.get_object_value(ResourceInstanceInteger)),
            "distanceToEmpty": lambda n : setattr(self, 'distance_to_empty', n.get_object_value(RInstanceWithUnit)),
            "distanceToEmptyBattery": lambda n : setattr(self, 'distance_to_empty_battery', n.get_object_value(ResourceInstanceInteger)),
            "tripMeterAutomatic": lambda n : setattr(self, 'trip_meter_automatic', n.get_object_value(ResourceInstanceFloat)),
            "tripMeterManual": lambda n : setattr(self, 'trip_meter_manual', n.get_object_value(ResourceInstanceFloat)),
            "tripMeter1": lambda n : setattr(self, 'trip_meter1', n.get_object_value(RInstanceWithUnit)),
            "tripMeter2": lambda n : setattr(self, 'trip_meter2', n.get_object_value(RInstanceWithUnit)),
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
        from .resource_instance_float import ResourceInstanceFloat
        from .resource_instance_integer import ResourceInstanceInteger
        from .r_instance_with_unit import RInstanceWithUnit

        writer.write_object_value("averageEnergyConsumption", self.average_energy_consumption)
        writer.write_object_value("averageFuelConsumption", self.average_fuel_consumption)
        writer.write_object_value("averageSpeed", self.average_speed)
        writer.write_object_value("averageSpeedAutomatic", self.average_speed_automatic)
        writer.write_object_value("distanceToEmpty", self.distance_to_empty)
        writer.write_object_value("distanceToEmptyBattery", self.distance_to_empty_battery)
        writer.write_object_value("tripMeterAutomatic", self.trip_meter_automatic)
        writer.write_object_value("tripMeterManual", self.trip_meter_manual)
        writer.write_object_value("tripMeter1", self.trip_meter1)
        writer.write_object_value("tripMeter2", self.trip_meter2)
        writer.write_additional_data_value(self.additional_data)
    

