from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from aioshad.client.client import Client


@dataclass
class User:
    """Represents a Shad user."""
    guid: str
    first_name: str = ""
    last_name: str = ""
    username: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_deleted: bool = False
    is_verified: bool = False
    raw: Dict[str, Any] = field(default_factory=dict, repr=False)
    _client: Optional[Client] = field(default=None, repr=False, compare=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip() or self.first_name

    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)

    @classmethod
    def from_dict(cls, data: Dict[str, Any], client: Optional[Client] = None) -> "User":
        raw = data if isinstance(data, dict) else {}
        user_dict = raw.get("user", raw) if isinstance(raw.get("user"), dict) else raw

        return cls(
            guid=user_dict.get("user_guid") or user_dict.get("guid") or "",
            first_name=user_dict.get("first_name") or "",
            last_name=user_dict.get("last_name") or "",
            username=user_dict.get("username"),
            phone=user_dict.get("phone"),
            bio=user_dict.get("bio"),
            is_deleted=bool(user_dict.get("is_deleted", False)),
            is_verified=bool(user_dict.get("is_verified", False)),
            raw=raw,
            _client=client,
        )

    def __str__(self) -> str:
        return f"User(guid={self.guid!r}, name={self.full_name!r}, username={self.username!r})"
