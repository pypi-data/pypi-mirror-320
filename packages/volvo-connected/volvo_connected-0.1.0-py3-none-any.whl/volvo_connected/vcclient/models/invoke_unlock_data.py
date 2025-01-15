from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .invoke_unlock_data_invoke_status import InvokeUnlock_data_invokeStatus

@dataclass
class InvokeUnlock_data(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The invokeStatus property
    invoke_status: Optional[InvokeUnlock_data_invokeStatus] = None
    # The message property
    message: Optional[str] = None
    # The readyToUnlock property
    ready_to_unlock: Optional[bool] = None
    # The readyToUnlockUntil property
    ready_to_unlock_until: Optional[int] = None
    # The vin property
    vin: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> InvokeUnlock_data:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: InvokeUnlock_data
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return InvokeUnlock_data()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .invoke_unlock_data_invoke_status import InvokeUnlock_data_invokeStatus

        from .invoke_unlock_data_invoke_status import InvokeUnlock_data_invokeStatus

        fields: Dict[str, Callable[[Any], None]] = {
            "invokeStatus": lambda n : setattr(self, 'invoke_status', n.get_enum_value(InvokeUnlock_data_invokeStatus)),
            "message": lambda n : setattr(self, 'message', n.get_str_value()),
            "readyToUnlock": lambda n : setattr(self, 'ready_to_unlock', n.get_bool_value()),
            "readyToUnlockUntil": lambda n : setattr(self, 'ready_to_unlock_until', n.get_int_value()),
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
        from .invoke_unlock_data_invoke_status import InvokeUnlock_data_invokeStatus

        writer.write_enum_value("invokeStatus", self.invoke_status)
        writer.write_str_value("message", self.message)
        writer.write_bool_value("readyToUnlock", self.ready_to_unlock)
        writer.write_int_value("readyToUnlockUntil", self.ready_to_unlock_until)
        writer.write_str_value("vin", self.vin)
        writer.write_additional_data_value(self.additional_data)
    

