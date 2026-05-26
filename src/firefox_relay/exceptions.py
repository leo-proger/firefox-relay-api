"""Exception hierarchy for firefox_relay."""

from __future__ import annotations

from typing import Any


class RelayError(Exception):
    """Base exception for all firefox_relay errors."""

    def __init__(
            self,
            message: str,
            *,
            status_code: int | None = None,
            response_body: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class RelayAuthError(RelayError):
    """Raised on HTTP 401 — bad or expired API token."""


class RelayPermissionError(RelayError):
    """Raised on HTTP 403 — authenticated but not allowed.

    Common causes: free-tier mask limit reached, premium-only feature,
    account restrictions. Inspect ``message`` / ``response_body`` for details.
    """


class RelayLimitReachedError(RelayPermissionError):
    """Raised when the free-tier mask limit is hit.

    A subclass of :class:`RelayPermissionError` — catching either works.
    """


class RelayNotFoundError(RelayError):
    """Raised on HTTP 404 — resource does not exist."""


class RelayValidationError(RelayError):
    """Raised on HTTP 400 — invalid request data."""


class RelayRateLimitError(RelayError):
    """Raised on HTTP 429 — rate limit exceeded."""

    def __init__(
            self,
            message: str,
            *,
            retry_after: int | None = None,
            status_code: int | None = None,
            response_body: Any = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)
        self.retry_after = retry_after


class RelayServerError(RelayError):
    """Raised on HTTP 5xx — server-side problem."""
