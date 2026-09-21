from __future__ import annotations
from typing import Optional


class AioshadError(Exception):
    """Base exception for all aioshad-related errors."""
    pass


class NetworkError(AioshadError):
    """Exception raised when an HTTP, connection, or transport error occurs."""

    def __init__(self, status: str, message: str = "") -> None:
        self.status = status
        self.message = message
        super().__init__(f"Network error [{status}]: {message}")


class ShadAPIError(AioshadError):
    """Exception raised when the Shad API returns a non-OK status."""

    def __init__(self, status: str, status_det: str = "", message: str = "") -> None:
        self.status = status
        self.status_det = status_det
        msg = message or f"Shad API Error [{status}]: {status_det}"
        super().__init__(msg)


class InvalidAuthError(ShadAPIError):
    """Raised when the session authentication key is invalid or revoked."""
    pass


class NotRegisteredError(ShadAPIError):
    """Raised when the client device is not registered."""
    pass


class FloodWaitError(ShadAPIError):
    """Raised when hit by Shad rate limiting / flood protection."""

    def __init__(self, wait_seconds: int = 5, status_det: str = "") -> None:
        self.wait_seconds = wait_seconds
        super().__init__(
            status="TOO_MANY_REQUESTS",
            status_det=status_det,
            message=f"Rate limit exceeded. Must wait {wait_seconds} seconds.",
        )
