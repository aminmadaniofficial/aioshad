from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from aioshad.types.message import Message


@dataclass
class MessageUpdate:
    """Represents an incoming message update."""
    message_id: str
    object_guid: str
    message: Message
    action: str = "New"
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass
class ChatUpdate:
    """Represents an update to a chat state."""
    object_guid: str
    last_message: Optional[Message] = None
    unread_count: int = 0
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
