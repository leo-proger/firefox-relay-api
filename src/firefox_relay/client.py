"""Public Client class – entry point for the library."""

from __future__ import annotations

from ._http import DEFAULT_BASE_URL, DEFAULT_TIMEOUT, HttpClient
from .resources.relay_addresses import RelayAddresses


class FirefoxRelayClient:
    """Top-level client for the Firefox Relay API.

    Example:
        >>> with FirefoxRelayClient(api_key="...") as client:
        ...     masks = client.relay_addresses.list()
        ...     mask = client.relay_addresses.create(description="shopping")
        ...     client.relay_addresses.delete(mask.id)

    Args:
        api_key: API token from https://relay.firefox.com/accounts/profile/
        base_url: Override the API base URL (mostly for testing).
        timeout: Per-request timeout in seconds.
    """

    def __init__(
            self,
            api_key: str,
            *,
            base_url: str = DEFAULT_BASE_URL,
            timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._http = HttpClient(api_key, base_url=base_url, timeout=timeout)
        self.relay_addresses = RelayAddresses(self._http)

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> FirefoxRelayClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
