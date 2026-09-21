from __future__ import annotations

import asyncio
import inspect
import logging
import signal
import sys
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)

from aioshad.client.methods import Methods
from aioshad.dispatcher.dispatcher import Dispatcher
from aioshad.exceptions import InvalidAuthError, NotRegisteredError
from aioshad.filters.base import Filter
from aioshad.network import Transport
from aioshad.session import (
    BaseSessionStorage,
    FileSessionStorage,
    MemorySessionStorage,
    Session,
)
from aioshad.types.chat import Chat
from aioshad.types.message import Message
from aioshad.types.user import User

logger = logging.getLogger("aioshad.client")

_POLL_INTERVAL_SECONDS = 1.5
_ERROR_BACKOFF_SECONDS = 5.0
_MAX_CONSECUTIVE_ERRORS = 15


class Client:
    """
    High-performance asynchronous client for Shad Messenger.
    Supports both Telethon/Pyrogram-style decorator `@client.on_message`
    and Aiogram-style Dispatcher & Routers with FSM and Middlewares.
    """

    def __init__(
        self,
        session: Union[str, Session] = "shad",
        phone_number: Optional[str] = None,
        session_directory: str = ".",
        dispatcher: Optional[Dispatcher] = None,
        messenger_host: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self.session_directory = session_directory
        self.proxy = proxy
        self.timeout = timeout

        if isinstance(session, Session):
            self.session = session
            self._storage: BaseSessionStorage = MemorySessionStorage(session.phone_number)
            self._storage.save(session)
            self.phone_number = session.phone_number
        elif isinstance(session, str) and len(session) > 100 and "=" in session:
            # String session
            self.session = Session.from_string(session)
            self._storage = MemorySessionStorage(self.session.phone_number)
            self._storage.save(self.session)
            self.phone_number = self.session.phone_number
        else:
            session_name = str(session).strip()
            self.phone_number = phone_number or (session_name if session_name.replace("+", "").isdigit() else "")
            self._storage = FileSessionStorage(session_name, directory=session_directory)
            self.session = self._storage.load(self.phone_number or session_name)

        if messenger_host:
            self.session.messenger_host = messenger_host

        self.dp: Dispatcher = dispatcher or Dispatcher()
        self._transport: Optional[Transport] = None
        self._methods: Optional[Methods] = None
        self._running: bool = False
        self._polling_task: Optional[asyncio.Task[None]] = None
        self._state: int = self.session.state or 0
        self._conversations: List[Any] = []

    def conversation(self, chat_guid: str, timeout: Optional[float] = None) -> Any:
        """Starts an interactive conversation session with a chat."""
        from aioshad.client.conversation import Conversation
        return Conversation(client=self, chat_guid=chat_guid, timeout=timeout)

    def _register_conversation(self, conv: Any) -> None:
        if conv not in self._conversations:
            self._conversations.append(conv)

    def _unregister_conversation(self, conv: Any) -> None:
        if conv in self._conversations:
            self._conversations.remove(conv)

    @property
    def transport(self) -> Transport:
        if self._transport is None:
            raise RuntimeError("Client transport is not initialized. Call await client.connect() first.")
        return self._transport

    @property
    def methods(self) -> Methods:
        if self._methods is None:
            raise RuntimeError("Client methods are not initialized. Call await client.connect() first.")
        return self._methods

    @property
    def me(self) -> Optional[str]:
        """Returns the user GUID of the logged in account."""
        return self.session.user_guid

    def _bootstrap(self) -> None:
        if self._transport is None:
            self._transport = Transport(
                session=self.session,
                timeout=self.timeout,
                proxy=self.proxy,
            )
            self._methods = Methods(
                session=self.session,
                transport=self._transport,
                storage=self._storage,
                client=self,
            )

    async def connect(self) -> None:
        """Connects to Shad servers and verifies or performs authentication."""
        self._bootstrap()
        methods = self.methods

        if not self.session.has_auth():
            if not self.phone_number:
                self.phone_number = input("Enter phone number (e.g. 0912...): ").strip()
            logger.info("No saved auth found. Initiating login for %s...", self.phone_number)
            await methods.login_flow(self.phone_number)
        else:
            try:
                await methods.register_device()
            except Exception as exc:
                if "INVALID_AUTH" in str(exc):
                    logger.warning("Session auth invalidated or expired. Initiating re-login...")
                    self.session.auth = ""
                    self.session.decode_auth = ""
                    self.session.key_hex = ""
                    self._storage.save(self.session)
                    if not self.phone_number:
                        self.phone_number = input("Enter phone number (e.g. 0912...): ").strip()
                    await methods.login_flow(self.phone_number)
                else:
                    logger.debug("Device register check: %s", exc)

    async def start(self) -> None:
        """Connects and starts the long-polling event loop."""
        if self._transport is None:
            await self.connect()

        logger.info("Starting aioshad dispatcher polling loop...")
        self._running = True
        self._polling_task = asyncio.create_task(self._polling_loop(), name="aioshad_polling")

        loop = asyncio.get_running_loop()

        def _handle_shutdown() -> None:
            logger.info("Shutdown signal received. Stopping client...")
            asyncio.create_task(self.stop())

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _handle_shutdown)
            except (NotImplementedError, ValueError):
                pass

        logger.info("aioshad client is running. Press Ctrl+C to stop.")
        await self.idle()

    def run(self) -> None:
        """Synchronously runs the client start coroutine."""
        try:
            asyncio.run(self.start())
        except (KeyboardInterrupt, SystemExit):
            pass

    async def idle(self) -> None:
        """Waits asynchronously while client polling is active."""
        while self._running:
            await asyncio.sleep(0.5)

    async def stop(self) -> None:
        """Gracefully halts the client, stops polling, and closes connections."""
        self._running = False
        if self._polling_task and not self._polling_task.done():
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        if self._transport:
            await self._transport.close()

        self._storage.save(self.session)
        logger.info("aioshad client stopped and session saved.")

    # -------------------------------------------------------------------------
    # Event Registration
    # -------------------------------------------------------------------------

    def on_message(self, *filters: Any) -> Callable[[Any], Any]:
        """Decorator to register a message handler."""
        return self.dp.message(*filters)

    def on_message_edited(self, *filters: Any) -> Callable[[Any], Any]:
        """Decorator to register a message edited handler."""
        return self.dp.message_edited(*filters)

    # -------------------------------------------------------------------------
    # Polling Loop
    # -------------------------------------------------------------------------

    async def _polling_loop(self) -> None:
        import time

        consecutive_errors = 0
        if self.session.state > 0:
            self._state = self.session.state
        else:
            self._state = int(time.time()) - 150
            self.session.state = self._state

        while self._running:
            try:
                updates = await self.methods.get_chats_updates(self._state)
                consecutive_errors = 0
                data_dict = (
                    updates.get("data")
                    if isinstance(updates.get("data"), dict)
                    else updates
                )
                new_state = int(
                    data_dict.get("state")
                    or data_dict.get("new_state")
                    or self._state
                )
                if new_state > self._state:
                    self._state = new_state
                    self.session.state = self._state

                # Process last messages in chat summaries
                chats: List[Dict[str, Any]] = data_dict.get("chats", [])
                for chat in chats:
                    last_msg = chat.get("last_message")
                    if last_msg:
                        await self._dispatch_message(
                            last_msg, chat.get("object_guid", "")
                        )

                # Process specific message updates
                message_updates = data_dict.get("message_updates", [])
                for item in message_updates:
                    msg = item.get("message") if isinstance(item, dict) else None
                    action = item.get("action") if isinstance(item, dict) else "New"
                    if msg:
                        target_guid = item.get("object_guid", "") or msg.get("object_guid", "")
                        if action == "Edit":
                            await self._dispatch_message(msg, target_guid, event_type="message_edited")
                        else:
                            await self._dispatch_message(msg, target_guid, event_type="message")

                await asyncio.sleep(_POLL_INTERVAL_SECONDS)

            except asyncio.CancelledError:
                break
            except Exception as exc:
                if "NOT_REGISTERED" in str(exc):
                    try:
                        logger.info("Session not registered on server. Re-registering device...")
                        await self.methods.register_device()
                        continue
                    except Exception as reg_exc:
                        logger.error("Auto registration failed: %s", reg_exc)

                if "INVALID_AUTH" in str(exc):
                    logger.critical("Session auth is invalid or revoked. Stopping client.")
                    self._running = False
                    break

                consecutive_errors += 1
                logger.error("Polling error (%d/%d): %s", consecutive_errors, _MAX_CONSECUTIVE_ERRORS, exc)
                if consecutive_errors >= _MAX_CONSECUTIVE_ERRORS:
                    logger.critical("Too many consecutive polling errors. Stopping client.")
                    self._running = False
                    break

                await asyncio.sleep(_ERROR_BACKOFF_SECONDS)

    async def _dispatch_message(
        self, raw_message: Dict[str, Any], object_guid: str, event_type: str = "message"
    ) -> None:
        raw_message.setdefault("object_guid", object_guid)
        message = Message.from_dict(raw_message, client=self)

        for conv in list(self._conversations):
            if conv.chat_guid == message.chat_guid:
                conv.put_message(message)

        try:
            await self.dp.dispatch(
                event_type,
                message,
                chat_id=message.chat_guid,
                user_id=message.author_guid,
                bot=self,
                client=self,
            )
        except Exception as exc:
            logger.error("Error dispatching %s event: %s", event_type, exc)

    # -------------------------------------------------------------------------
    # Direct API Methods Forwarding
    # -------------------------------------------------------------------------

    async def send_message(
        self,
        object_guid: str,
        text: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        file_inline: Optional[Dict[str, Any]] = None,
    ) -> Message:
        return await self.methods.send_message(object_guid, text, reply_to_message_id, file_inline)

    async def edit_message(self, object_guid: str, message_id: str, text: str) -> Message:
        return await self.methods.edit_message(object_guid, message_id, text)

    async def delete_messages(
        self, object_guid: str, message_ids: Union[str, int, List[Union[str, int]]], delete_type: str = "Global"
    ) -> Dict[str, Any]:
        return await self.methods.delete_messages(object_guid, message_ids, delete_type)

    async def delete_message(
        self, object_guid: str, message_id: Union[str, int], delete_type: str = "Global"
    ) -> Dict[str, Any]:
        return await self.methods.delete_message(object_guid, message_id, delete_type)

    async def forward_messages(
        self, from_object_guid: str, to_object_guid: str, message_ids: Union[str, int, List[Union[str, int]]]
    ) -> Dict[str, Any]:
        return await self.methods.forward_messages(from_object_guid, to_object_guid, message_ids)

    async def upload_file(
        self,
        file: Union[str, bytes, Path],
        file_name: Optional[str] = None,
        mime: Optional[str] = None,
        chunk_size: int = 131072,
    ) -> Dict[str, Any]:
        return await self.methods.upload_file(file, file_name, mime, chunk_size)

    async def download_file(
        self, file_inline_or_url: Union[str, Dict[str, Any]], destination: Optional[Union[str, Path]] = None
    ) -> bytes:
        return await self.methods.download_file(file_inline_or_url, destination)

    async def send_photo(
        self,
        object_guid: str,
        photo: Union[str, bytes, Path],
        caption: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> Message:
        return await self.methods.send_photo(object_guid, photo, caption, reply_to_message_id, file_name)

    async def send_file(
        self,
        object_guid: str,
        file: Union[str, bytes, Path],
        file_name: Optional[str] = None,
        mime: Optional[str] = None,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        return await self.methods.send_file(object_guid, file, file_name, mime, caption, reply_to_message_id)

    async def send_voice(
        self,
        object_guid: str,
        voice: Union[str, bytes, Path],
        caption: Optional[str] = None,
        duration: Optional[int] = None,
        reply_to_message_id: Optional[str] = None,
    ) -> Message:
        return await self.methods.send_voice(object_guid, voice, caption, duration, reply_to_message_id)

    async def get_user_info(self, user_guid: Optional[str] = None) -> User:
        return await self.methods.get_user_info(user_guid)

    async def update_profile(
        self, first_name: Optional[str] = None, last_name: Optional[str] = None, bio: Optional[str] = None
    ) -> bool:
        return await self.methods.update_profile(first_name, last_name, bio)

    async def get_chat_info(self, object_guid: str) -> Chat:
        return await self.methods.get_chat_info(object_guid)

    async def get_chat_info_by_username(self, username: str) -> Chat:
        return await self.methods.get_chat_info_by_username(username)

    async def get_chats(self, start_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.methods.get_chats(start_id)

    async def get_messages(
        self, object_guid: str, limit: int = 50, sort: str = "FromMax", max_id: Optional[str] = None, min_id: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.methods.get_messages(object_guid, limit, sort, max_id, min_id)

    async def get_chat_history(
        self, object_guid: str, limit: int = 50, max_id: Optional[str] = None, min_id: Optional[str] = None, sort: str = "FromMax"
    ) -> List[Message]:
        return await self.methods.get_chat_history(object_guid, limit, max_id, min_id, sort)

    async def join_chat_by_link(self, link: str) -> Dict[str, Any]:
        return await self.methods.join_chat_by_link(link)

    async def leave_chat(self, object_guid: str) -> Dict[str, Any]:
        return await self.methods.leave_chat(object_guid)

    async def create_group(self, title: str, member_guids: Optional[List[str]] = None) -> Dict[str, Any]:
        return await self.methods.create_group(title, member_guids)

    async def add_group_members(self, group_guid: str, member_guids: List[str]) -> Dict[str, Any]:
        return await self.methods.add_group_members(group_guid, member_guids)

    async def delete_group_member(self, group_guid: str, member_guid: str) -> Dict[str, Any]:
        return await self.methods.delete_group_member(group_guid, member_guid)

    async def join_voice_chat(
        self, chat_guid: str, voice_chat_id: Optional[str] = None, sdp_offer_data: str = ""
    ) -> Dict[str, Any]:
        return await self.methods.join_voice_chat(chat_guid, voice_chat_id, sdp_offer_data)

    async def leave_voice_chat(self, chat_guid: str, voice_chat_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.methods.leave_voice_chat(chat_guid, voice_chat_id)

    async def get_voice_chat_participants(
        self, chat_guid: str, voice_chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.methods.get_voice_chat_participants(chat_guid, voice_chat_id)

    async def create_voice_chat(self, chat_guid: str) -> Dict[str, Any]:
        return await self.methods.create_voice_chat(chat_guid)

    async def discard_voice_chat(self, chat_guid: str, voice_chat_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.methods.discard_voice_chat(chat_guid, voice_chat_id)

    async def set_voice_chat_state(
        self, chat_guid: str, voice_chat_id: str, activity: str = "Speaking", participant_object_guid: Optional[str] = None
    ) -> Dict[str, Any]:
        return await self.methods.set_voice_chat_state(chat_guid, voice_chat_id, activity, participant_object_guid)
