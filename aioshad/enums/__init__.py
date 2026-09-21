from __future__ import annotations
from enum import Enum


class ChatType(str, Enum):
    PRIVATE = "User"
    GROUP = "Group"
    CHANNEL = "Channel"
    SERVICE = "Service"
    BOT = "Bot"


class DeleteType(str, Enum):
    GLOBAL = "Global"
    LOCAL = "Local"


class VoiceChatActivity(str, Enum):
    SPEAKING = "Speaking"
    MUTED = "Muted"
    CONNECTING = "Connecting"


class SendCodeType(str, Enum):
    SMS = "SMS"
    APP = "App"


__all__ = (
    "ChatType",
    "DeleteType",
    "VoiceChatActivity",
    "SendCodeType",
)
