"""Unofficial Python client for Firefox Relay."""

from importlib.metadata import PackageNotFoundError, version

from .client import FirefoxRelayClient
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
from .models import RelayAddress

try:
    __version__ = version("firefox-relay-api")
except PackageNotFoundError:  # package not installed (e.g. running from source)
    __version__ = "0.0.0+unknown"

__all__ = [
    "FirefoxRelayClient",
    "RelayAddress",
    "RelayAuthError",
    "RelayError",
    "RelayLimitReachedError",
    "RelayNotFoundError",
    "RelayPermissionError",
    "RelayRateLimitError",
    "RelayServerError",
    "RelayValidationError",
    "__version__",
]
