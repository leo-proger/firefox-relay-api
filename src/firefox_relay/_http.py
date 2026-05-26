"""Internal HTTP client. Not part of the public API.

Wraps :mod:`httpx` to:

* attach auth headers,
* parse JSON responses,
* convert HTTP error codes into :class:`RelayError` subclasses.
"""

from __future__ import annotations

from typing import Any

import httpx

from .exceptions import (
    RelayAuthError,
    RelayError,
    RelayLimitReachedError,
    RelayNotFoundError,
    RelayPermissionError,
    RelayRateLimitError,
    RelayServerError,
    RelayValidationError,
)

DEFAULT_BASE_URL = "https://relay.firefox.com/api/v1/"
DEFAULT_TIMEOUT = 30.0
USER_AGENT = "firefox-relay-api-python/0.1.0"


class HttpClient:
    """Thin wrapper around :class:`httpx.Client` with error mapping."""

    def __init__(
            self,
            api_key: str,
            *,
            base_url: str = DEFAULT_BASE_URL,
            timeout: float = DEFAULT_TIMEOUT,
            user_agent: str = USER_AGENT,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty")
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Token {api_key}",
                "Accept": "application/json",
                "User-Agent": user_agent,
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    # ---- HTTP verbs ----

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        return self._request("GET", path, params=params)

    def post(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return self._request("POST", path, json=json)

    def patch(self, path: str, *, json: dict[str, Any] | None = None) -> Any:
        return self._request("PATCH", path, json=json)

    def delete(self, path: str) -> None:
        self._request("DELETE", path)

    # ---- internals ----

    def _request(
            self,
            method: str,
            path: str,
            *,
            params: dict[str, Any] | None = None,
            json: dict[str, Any] | None = None,
    ) -> Any:
        try:
            response = self._client.request(method, path, params=params, json=json)
        except httpx.RequestError as exc:
            raise RelayError(f"Network error: {exc}") from exc

        if response.is_success:
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        self._raise_for_status(response)
        return None  # unreachable, for type checkers

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        status = response.status_code
        try:
            body: Any = response.json()
        except ValueError:
            body = {"detail": response.text}

        if isinstance(body, dict) and "detail" in body:
            message = str(body["detail"])
        else:
            message = f"HTTP {status}"

        if status == 401:
            raise RelayAuthError(message, status_code=status, response_body=body)
        if status == 403:
            # Free-tier mask limit shows up as 403 with a specific message.
            # Mozilla doesn't ship a stable error_code for this, so we fall back
            # to a substring match on the user-visible message.
            if "email masks" in message.lower() and "free account" in message.lower():
                raise RelayLimitReachedError(
                    message, status_code=status, response_body=body
                )
            raise RelayPermissionError(message, status_code=status, response_body=body)
        if status == 404:
            raise RelayNotFoundError(message, status_code=status, response_body=body)
        if status == 400:
            raise RelayValidationError(message, status_code=status, response_body=body)
        if status == 429:
            hdr = response.headers.get("Retry-After")
            retry_after = int(hdr) if hdr and hdr.isdigit() else None
            raise RelayRateLimitError(
                message,
                retry_after=retry_after,
                status_code=status,
                response_body=body,
            )
        if 500 <= status < 600:
            raise RelayServerError(message, status_code=status, response_body=body)

        raise RelayError(message, status_code=status, response_body=body)
