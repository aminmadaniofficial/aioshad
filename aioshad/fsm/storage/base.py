from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union


class BaseStorage(ABC):
    """
    Abstract base storage for FSM states and data.
    Supports both integer and string (GUID) chat/user identifiers.
    """
    @abstractmethod
    async def set_state(
        self, chat_id: Union[str, int], user_id: Union[str, int], state: Optional[str] = None
    ) -> None:
        pass

    @abstractmethod
    async def get_state(
        self, chat_id: Union[str, int], user_id: Union[str, int]
    ) -> Optional[str]:
        pass

    @abstractmethod
    async def set_data(
        self, chat_id: Union[str, int], user_id: Union[str, int], data: Dict[str, Any]
    ) -> None:
        pass

    @abstractmethod
    async def get_data(
        self, chat_id: Union[str, int], user_id: Union[str, int]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def update_data(
        self, chat_id: Union[str, int], user_id: Union[str, int], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def clear(
        self, chat_id: Union[str, int], user_id: Union[str, int]
    ) -> None:
        pass
