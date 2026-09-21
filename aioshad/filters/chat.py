from __future__ import annotations
from typing import Any, List, Set, Union, Optional
from .base import Filter
from ..enums import ChatType


class IsGroup(Filter):
    """Matches if message is from a Group."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        guid = getattr(event, "chat_guid", "") or getattr(getattr(event, "chat", None), "guid", "")
        if guid.startswith("g0"):
            return True
        chat = getattr(event, "chat", None)
        return getattr(chat, "type", None) == ChatType.GROUP


class IsChannel(Filter):
    """Matches if message is from a Channel."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        guid = getattr(event, "chat_guid", "") or getattr(getattr(event, "chat", None), "guid", "")
        if guid.startswith("c0"):
            return True
        chat = getattr(event, "chat", None)
        return getattr(chat, "type", None) == ChatType.CHANNEL


class IsGroupOrChannel(Filter):
    """Matches if message is from a Group or Channel."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        guid = getattr(event, "chat_guid", "") or getattr(getattr(event, "chat", None), "guid", "")
        if guid.startswith("g0") or guid.startswith("c0"):
            return True
        chat = getattr(event, "chat", None)
        return getattr(chat, "type", None) in (ChatType.GROUP, ChatType.CHANNEL)


class IsPrivate(Filter):
    """Matches if message is from a private user chat (DM)."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        guid = getattr(event, "chat_guid", "") or getattr(getattr(event, "chat", None), "guid", "")
        if guid.startswith("u0"):
            return True
        chat = getattr(event, "chat", None)
        return getattr(chat, "type", None) == ChatType.PRIVATE or (not guid.startswith("g0") and not guid.startswith("c0"))


class ChatTypeFilter(Filter):
    """Matches specific ChatType enum value."""
    def __init__(self, chat_type: Union[ChatType, str]):
        self.chat_type = chat_type

    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        chat = getattr(event, "chat", None)
        chat_type = getattr(chat, "type", None)
        if chat_type:
            return chat_type == self.chat_type
        guid = getattr(event, "chat_guid", "")
        if self.chat_type == ChatType.GROUP and guid.startswith("g0"):
            return True
        if self.chat_type == ChatType.CHANNEL and guid.startswith("c0"):
            return True
        if self.chat_type == ChatType.PRIVATE and not guid.startswith("g0") and not guid.startswith("c0"):
            return True
        return False


class IsMe(Filter):
    """Matches messages sent by the selfbot itself."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        if getattr(event, "is_outgoing", False):
            return True
        bot = kwargs.get("bot") or kwargs.get("client")
        if bot and hasattr(bot, "session"):
            return getattr(event, "author_guid", None) == bot.session.user_guid
        return False


class IsAdmin(Filter):
    """Matches messages sent by specified admin GUIDs."""
    def __init__(self, *admin_guids: str):
        self.admin_guids: Set[str] = set(admin_guids)

    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        author_guid = getattr(event, "author_guid", None) or getattr(event, "sender_id", None)
        return author_guid in self.admin_guids
