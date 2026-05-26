"""Base class for resource managers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._http import HttpClient


class BaseResource:
    """Shared state for all resource managers (just holds the HTTP client)."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http
