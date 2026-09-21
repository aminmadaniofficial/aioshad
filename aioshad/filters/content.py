from __future__ import annotations
from typing import Any, TYPE_CHECKING
from .base import Filter

if TYPE_CHECKING:
    from ..types.message import Message


class IsText(Filter):
    """Filter to check if the message contains non-empty text content."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        text = getattr(event, "text", None)
        return bool(text and text.strip())


class IsMedia(Filter):
    """Filter to check if the message contains any file or photo attachment."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        return getattr(event, "file_inline", None) is not None


class IsPhoto(Filter):
    """Filter to check if the message contains an image."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        file_inline = getattr(event, "file_inline", None)
        if isinstance(file_inline, dict):
            return file_inline.get("type") == "Image"
        return False


class IsVoice(Filter):
    """Filter to check if the message contains a voice note."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        file_inline = getattr(event, "file_inline", None)
        if isinstance(file_inline, dict):
            return file_inline.get("type") == "Voice"
        return False


class IsFile(Filter):
    """Filter to check if the message contains a generic document/file."""
    async def __call__(self, event: Any, **kwargs: Any) -> bool:
        file_inline = getattr(event, "file_inline", None)
        if isinstance(file_inline, dict):
            return file_inline.get("type") in ("File", None)
        return False
