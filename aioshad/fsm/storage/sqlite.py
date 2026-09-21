from __future__ import annotations
import asyncio
import json
import sqlite3
import pathlib
from typing import Any, Dict, Optional, Union

from .base import BaseStorage
from ..state import State
from ...utils.compat import to_thread


class SQLiteStorage(BaseStorage):
    """
    Persistent SQLite storage backend for FSM.
    Stores conversation states and associated data in a local SQLite database file.
    Supports both integer and string GUID identifiers.
    """

    def __init__(self, db_path: Union[str, pathlib.Path] = "fsm_storage.db") -> None:
        self.db_path = str(db_path)
        self._init_db_sync()

    def _init_db_sync(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS fsm_storage (
                    chat_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    state TEXT,
                    data TEXT,
                    PRIMARY KEY (chat_id, user_id)
                )
                """
            )
            conn.commit()

    async def set_state(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        state: Optional[Union[str, State]] = None,
    ) -> None:
        state_str = state.state if isinstance(state, State) else state
        cid, uid = str(chat_id), str(user_id)

        def _sync_set_state():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO fsm_storage (chat_id, user_id, state, data)
                    VALUES (?, ?, ?, '{}')
                    ON CONFLICT(chat_id, user_id) DO UPDATE SET state = excluded.state
                    """,
                    (cid, uid, state_str),
                )
                conn.commit()

        await to_thread(_sync_set_state)

    async def get_state(self, chat_id: Union[str, int], user_id: Union[str, int]) -> Optional[str]:
        cid, uid = str(chat_id), str(user_id)

        def _sync_get_state() -> Optional[str]:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT state FROM fsm_storage WHERE chat_id = ? AND user_id = ?",
                    (cid, uid),
                )
                row = cursor.fetchone()
                return row[0] if row else None

        return await to_thread(_sync_get_state)

    async def set_data(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        data: Dict[str, Any],
    ) -> None:
        cid, uid = str(chat_id), str(user_id)
        encoded_data = json.dumps(data)

        def _sync_set_data():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO fsm_storage (chat_id, user_id, state, data)
                    VALUES (?, ?, NULL, ?)
                    ON CONFLICT(chat_id, user_id) DO UPDATE SET data = excluded.data
                    """,
                    (cid, uid, encoded_data),
                )
                conn.commit()

        await to_thread(_sync_set_data)

    async def get_data(self, chat_id: Union[str, int], user_id: Union[str, int]) -> Dict[str, Any]:
        cid, uid = str(chat_id), str(user_id)

        def _sync_get_data() -> Dict[str, Any]:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM fsm_storage WHERE chat_id = ? AND user_id = ?",
                    (cid, uid),
                )
                row = cursor.fetchone()
                if row and row[0]:
                    try:
                        return json.loads(row[0])
                    except json.JSONDecodeError:
                        return {}
                return {}

        return await to_thread(_sync_get_data)

    async def update_data(
        self,
        chat_id: Union[str, int],
        user_id: Union[str, int],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        cid, uid = str(chat_id), str(user_id)

        def _sync_update_data() -> Dict[str, Any]:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM fsm_storage WHERE chat_id = ? AND user_id = ?",
                    (cid, uid),
                )
                row = cursor.fetchone()
                current_data: Dict[str, Any] = {}
                if row and row[0]:
                    try:
                        current_data = json.loads(row[0])
                    except json.JSONDecodeError:
                        current_data = {}

                current_data.update(data)
                encoded_data = json.dumps(current_data)

                cursor.execute(
                    """
                    INSERT INTO fsm_storage (chat_id, user_id, state, data)
                    VALUES (?, ?, NULL, ?)
                    ON CONFLICT(chat_id, user_id) DO UPDATE SET data = excluded.data
                    """,
                    (cid, uid, encoded_data),
                )
                conn.commit()
                return current_data

        return await to_thread(_sync_update_data)

    async def clear(self, chat_id: Union[str, int], user_id: Union[str, int]) -> None:
        cid, uid = str(chat_id), str(user_id)

        def _sync_clear():
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM fsm_storage WHERE chat_id = ? AND user_id = ?",
                    (cid, uid),
                )
                conn.commit()

        await to_thread(_sync_clear)
