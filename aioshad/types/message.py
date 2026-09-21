from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

if TYPE_CHECKING:
    from aioshad.client.client import Client
    from aioshad.types.chat import Chat
    from aioshad.types.user import User


@dataclass
class Message:
    """Represents a Shad message."""
    id: str
    text: str
    author_guid: str
    chat_guid: str
    message_type: str = "Text"
    reply_to_message_id: Optional[str] = None
    is_edited: bool = False
    time: Optional[int] = None
    file_inline: Optional[Dict[str, Any]] = None
    raw: Dict[str, Any] = field(default_factory=dict, repr=False, compare=False)
    _client: Optional[Client] = field(default=None, repr=False, compare=False)

    @property
    def message_id(self) -> str:
        """Alias for id."""
        return self.id

    @property
    def sender_id(self) -> str:
        """Alias for author_guid for filter and middleware compatibility."""
        return self.author_guid

    @property
    def chat_id(self) -> str:
        """Alias for chat_guid for filter and middleware compatibility."""
        return self.chat_guid

    @property
    def is_outgoing(self) -> bool:
        """Returns True if this message was sent by the currently authenticated client."""
        if self._client and self._client.session:
            return self.author_guid == self._client.session.user_guid
        return False

    def __getitem__(self, key: str) -> Any:
        if hasattr(self, key):
            return getattr(self, key)
        if key in self.raw:
            return self.raw[key]
        inner = self.raw.get("message")
        if isinstance(inner, dict) and key in inner:
            return inner[key]
        raise KeyError(key)

    def get(self, key: str, default: Any = None) -> Any:
        if hasattr(self, key):
            val = getattr(self, key)
            if val is not None:
                return val
        if key in self.raw:
            return self.raw[key]
        inner = self.raw.get("message")
        if isinstance(inner, dict) and key in inner:
            return inner[key]
        return default

    async def reply(self, text: str) -> "Message":
        """Replies to this message with text."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.send_message(
            self.chat_guid,
            text,
            reply_to_message_id=self.id,
        )

    async def reply_photo(
        self,
        photo: Union[str, bytes, Path],
        caption: Optional[str] = None,
    ) -> "Message":
        """Replies to this message with a photo."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.send_photo(
            self.chat_guid,
            photo,
            caption=caption,
            reply_to_message_id=self.id,
        )

    async def reply_file(
        self,
        file: Union[str, bytes, Path],
        file_name: Optional[str] = None,
        mime: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> "Message":
        """Replies to this message with a document/file."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.send_file(
            self.chat_guid,
            file,
            file_name=file_name,
            mime=mime,
            caption=caption,
            reply_to_message_id=self.id,
        )

    async def edit(self, text: str) -> "Message":
        """Edits this message's text."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        edited = await self._client.edit_message(
            self.chat_guid,
            self.id,
            text,
        )
        self.text = edited.text
        self.is_edited = True
        return self

    async def delete(self, delete_type: str = "Global") -> Dict[str, Any]:
        """Deletes this message."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.delete_message(
            self.chat_guid,
            self.id,
            delete_type=delete_type,
        )

    async def forward(self, target_guid: str) -> Dict[str, Any]:
        """Forwards this message to another chat."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.forward_messages(
            from_object_guid=self.chat_guid,
            to_object_guid=target_guid,
            message_ids=[self.id],
        )

    async def get_chat(self) -> "Chat":
        """Retrieves Chat information for this message's chat."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.get_chat_info(self.chat_guid)

    async def get_author(self) -> "User":
        """Retrieves User information for this message's author."""
        if self._client is None:
            raise RuntimeError("Message is not bound to a Client instance.")
        return await self._client.get_user_info(self.author_guid)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], client: Optional[Client] = None) -> "Message":
        raw = data if isinstance(data, dict) else {}
        inner_msg: Dict[str, Any] = raw.get("message") if isinstance(raw.get("message"), dict) else {}
        text = raw.get("text") or inner_msg.get("text") or ""
        is_edited = bool(raw.get("is_edited") or inner_msg.get("is_edited") or False)
        time_val = raw.get("time") or inner_msg.get("time")
        file_inline = raw.get("file_inline") or inner_msg.get("file_inline")

        return cls(
            id=str(raw.get("message_id") or inner_msg.get("message_id") or ""),
            text=text,
            author_guid=raw.get("author_object_guid") or inner_msg.get("author_object_guid") or "",
            chat_guid=raw.get("object_guid") or inner_msg.get("object_guid") or "",
            message_type=raw.get("type") or inner_msg.get("type") or "Text",
            reply_to_message_id=raw.get("reply_to_message_id") or inner_msg.get("reply_to_message_id"),
            is_edited=is_edited,
            time=int(time_val) if time_val and str(time_val).isdigit() else None,
            file_inline=file_inline if isinstance(file_inline, dict) else None,
            raw=raw,
            _client=client,
        )

    def __str__(self) -> str:
        return (
            f"Message(id={self.id!r}, chat={self.chat_guid!r}, "
            f"author={self.author_guid!r}, text={self.text!r})"
        )
