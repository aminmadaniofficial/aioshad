from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Union

from aioshad.types.message import Message

if TYPE_CHECKING:
    from aioshad.client.client import Client


class Conversation:
    """
    Asynchronous Context Manager for linear, interactive conversations with a user or chat.
    
    Example:
        ```python
        async with client.conversation(chat_guid="u0...") as conv:
            await conv.send_message("Please enter your name:")
            name_msg = await conv.get_response(timeout=60)
            print(f"User name: {name_msg.text}")
        ```
    """

    def __init__(
        self,
        client: Client,
        chat_guid: str,
        timeout: Optional[float] = None,
    ) -> None:
        self.client = client
        self.chat_guid = chat_guid
        self.timeout = timeout
        self._queue: asyncio.Queue[Message] = asyncio.Queue()
        self._closed: bool = False

    async def __aenter__(self) -> Conversation:
        self.client._register_conversation(self)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        self._closed = True
        self.client._unregister_conversation(self)

    def is_closed(self) -> bool:
        return self._closed

    def put_message(self, message: Message) -> None:
        if not self._closed:
            self._queue.put_nowait(message)

    async def get_response(self, timeout: Optional[float] = None) -> Message:
        """Awaits and returns the next incoming message in this conversation."""
        if self._closed:
            raise RuntimeError("Conversation is already closed.")
        effective_timeout = timeout if timeout is not None else self.timeout
        if effective_timeout is not None:
            return await asyncio.wait_for(self._queue.get(), timeout=effective_timeout)
        return await self._queue.get()

    async def send_message(
        self,
        text: str,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        return await self.client.send_message(
            object_guid=self.chat_guid,
            text=text,
            reply_to_message_id=reply_to_message_id,
        )

    async def send_photo(
        self,
        photo: Union[str, bytes, Path],
        caption: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        return await self.client.send_photo(
            object_guid=self.chat_guid,
            photo=photo,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
        )

    async def send_file(
        self,
        file: Union[str, bytes, Path],
        file_name: Optional[str] = None,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        return await self.client.send_file(
            object_guid=self.chat_guid,
            file=file,
            file_name=file_name,
            caption=caption,
            reply_to_message_id=reply_to_message_id,
        )
