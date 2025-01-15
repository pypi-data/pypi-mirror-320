from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .tyre_pressure import TyrePressure

@dataclass
class TyrePressureResponse(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The data property
    data: Optional[TyrePressure] = None
    # The operationId property
    operation_id: Optional[str] = None
    # The status property
    status: Optional[int] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> TyrePressureResponse:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: TyrePressureResponse
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return TyrePressureResponse()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .tyre_pressure import TyrePressure

        from .tyre_pressure import TyrePressure

        fields: Dict[str, Callable[[Any], None]] = {
            "data": lambda n : setattr(self, 'data', n.get_object_value(TyrePressure)),
            "operationId": lambda n : setattr(self, 'operation_id', n.get_str_value()),
            "status": lambda n : setattr(self, 'status', n.get_int_value()),
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
        from .tyre_pressure import TyrePressure

        writer.write_object_value("data", self.data)
        writer.write_str_value("operationId", self.operation_id)
        writer.write_int_value("status", self.status)
        writer.write_additional_data_value(self.additional_data)
    

