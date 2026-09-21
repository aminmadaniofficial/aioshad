from __future__ import annotations

import abc
import base64
import json
import os
import sqlite3
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Optional


@dataclass
class Session:
    """
    Holds persistent authentication credentials and runtime state for a Shad client session.
    """
    phone_number: str = ""
    auth: str = ""
    decode_auth: str = ""
    private_key_pem: str = ""
    tmp_session: str = ""
    key_hex: str = ""
    iv_hex: str = ""
    messenger_host: str = "shadmessenger60.iranlms.ir"
    user_guid: str = ""
    state: int = 0

    def has_auth(self) -> bool:
        """Returns True if the session has an active auth token and encryption key."""
        return bool(self.auth and self.key_hex)

    def get_key(self) -> bytes:
        """Returns the AES encryption key bytes."""
        if self.key_hex:
            return bytes.fromhex(self.key_hex)
        return b""

    def set_key(self, raw_key: bytes) -> None:
        """Sets the AES encryption key bytes."""
        self.key_hex = raw_key.hex()

    def get_iv(self) -> bytes:
        """Returns the AES IV bytes (defaults to 16 null bytes)."""
        if self.iv_hex:
            return bytes.fromhex(self.iv_hex)
        return b"\x00" * 16

    def set_iv(self, iv: bytes) -> None:
        """Sets the AES IV bytes."""
        self.iv_hex = iv.hex()

    def get_base_url(self) -> str:
        """Returns the base HTTPS URL for the active messenger host."""
        return f"https://{self.messenger_host}/"

    def export_string(self) -> str:
        """Exports the session as a base64 encoded JSON string (useful for cloud/env deployments)."""
        data = json.dumps(asdict(self))
        return base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8")

    @classmethod
    def from_string(cls, session_str: str) -> "Session":
        """Loads a Session from a base64 string exported via export_string()."""
        raw = base64.urlsafe_b64decode(session_str.strip().encode("utf-8")).decode("utf-8")
        data = json.loads(raw)
        fields = cls.__dataclass_fields__
        filtered = {k: v for k, v in data.items() if k in fields}
        return cls(**filtered)


class BaseSessionStorage(abc.ABC):
    """Abstract interface for session storage backends."""

    @abc.abstractmethod
    def load(self, phone_number: str) -> Session:
        pass

    @abc.abstractmethod
    def save(self, session: Session) -> None:
        pass

    @abc.abstractmethod
    def exists(self) -> bool:
        pass


class FileSessionStorage(BaseSessionStorage):
    """
    Stores session data in a JSON file on disk.
    Defaults to `{phone_number}.session` in the specified directory.
    """

    def __init__(self, phone_number: str, directory: str = ".") -> None:
        self.phone_number = phone_number
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        # If user passed a file ending with .session directly
        if phone_number.endswith(".session"):
            self._path = phone_number
        else:
            self._path = os.path.join(directory, f"{phone_number}.session")

    def load(self, phone_number: str) -> Session:
        if not os.path.exists(self._path):
            return Session(phone_number=phone_number)
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            fields = Session.__dataclass_fields__
            filtered = {k: v for k, v in data.items() if k in fields}
            return Session(**filtered)
        except Exception:
            return Session(phone_number=phone_number)

    def save(self, session: Session) -> None:
        with open(self._path, "w", encoding="utf-8") as fh:
            json.dump(asdict(session), fh, indent=2)

    def exists(self) -> bool:
        return os.path.exists(self._path)


class SQLiteSessionStorage(BaseSessionStorage):
    """
    Stores multiple sessions inside an SQLite database file.
    Ideal for managing multiple selfbot accounts.
    """

    def __init__(self, phone_number: str, db_path: str = "sessions.db") -> None:
        self.phone_number = phone_number
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    phone_number TEXT PRIMARY KEY,
                    data TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def load(self, phone_number: str) -> Session:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM sessions WHERE phone_number = ?", (phone_number,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                fields = Session.__dataclass_fields__
                filtered = {k: v for k, v in data.items() if k in fields}
                return Session(**filtered)
        return Session(phone_number=phone_number)

    def save(self, session: Session) -> None:
        data_str = json.dumps(asdict(session))
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO sessions (phone_number, data)
                VALUES (?, ?)
                ON CONFLICT(phone_number) DO UPDATE SET data = excluded.data
                """,
                (session.phone_number, data_str),
            )
            conn.commit()

    def exists(self) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM sessions WHERE phone_number = ?", (self.phone_number,))
            return cursor.fetchone() is not None


class MemorySessionStorage(BaseSessionStorage):
    """Keeps session data in memory without persisting to disk."""

    def __init__(self, phone_number: str) -> None:
        self.phone_number = phone_number
        self._session: Optional[Session] = None

    def load(self, phone_number: str) -> Session:
        if self._session is not None:
            return self._session
        return Session(phone_number=phone_number)

    def save(self, session: Session) -> None:
        self._session = session

    def exists(self) -> bool:
        return self._session is not None and self._session.has_auth()


# Backward compatibility alias
SessionStorage = FileSessionStorage
