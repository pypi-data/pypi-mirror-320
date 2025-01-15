from __future__ import annotations
from dataclasses import dataclass, field
from kiota_abstractions.serialization import AdditionalDataHolder, Parsable, ParseNode, SerializationWriter
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .command_list_item_command import CommandListItem_command

@dataclass
class CommandListItem(AdditionalDataHolder, Parsable):
    # Stores additional data not described in the OpenAPI description found when deserializing. Can be used for serialization as well.
    additional_data: Dict[str, Any] = field(default_factory=dict)

    # The command property
    command: Optional[CommandListItem_command] = None
    # The href property
    href: Optional[str] = None
    
    @staticmethod
    def create_from_discriminator_value(parse_node: ParseNode) -> CommandListItem:
        """
        Creates a new instance of the appropriate class based on discriminator value
        param parse_node: The parse node to use to read the discriminator value and create the object
        Returns: CommandListItem
        """
        if parse_node is None:
            raise TypeError("parse_node cannot be null.")
        return CommandListItem()
    
    def get_field_deserializers(self,) -> Dict[str, Callable[[ParseNode], None]]:
        """
        The deserialization information for the current model
        Returns: Dict[str, Callable[[ParseNode], None]]
        """
        from .command_list_item_command import CommandListItem_command

        from .command_list_item_command import CommandListItem_command

        fields: Dict[str, Callable[[Any], None]] = {
            "command": lambda n : setattr(self, 'command', n.get_enum_value(CommandListItem_command)),
            "href": lambda n : setattr(self, 'href', n.get_str_value()),
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
        from .command_list_item_command import CommandListItem_command

        writer.write_enum_value("command", self.command)
        writer.write_str_value("href", self.href)
        writer.write_additional_data_value(self.additional_data)
    

