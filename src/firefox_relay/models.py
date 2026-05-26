"""Data models for Firefox Relay API resources."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


def _parse_dt(value: str | None) -> datetime | None:
    """Parse ISO-8601 timestamps from the API (handles trailing 'Z')."""
    if value is None:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _require_dt(data: dict[str, Any], key: str) -> datetime:
    """Parse a required (non-null) datetime field, raising on missing/null."""
    raw = data.get(key)
    if raw is None:
        raise ValueError(f"API response missing required datetime field {key!r}")
    parsed = _parse_dt(raw)
    if parsed is None:  # defensive, _parse_dt only returns None for None input
        raise ValueError(f"Could not parse datetime field {key!r}: {raw!r}")
    return parsed


@dataclass(slots=True)
class RelayAddress:
    """A random email mask returned by ``/api/v1/relayaddresses/``.

    Field names mirror the API response 1:1 to avoid translation surprises.
    """

    id: int
    address: str  # local part, e.g. "abc123"
    domain: str  # e.g. "mozmail.com"
    full_address: str  # e.g. "abc123@mozmail.com"
    enabled: bool
    description: str
    generated_for: str
    block_list_emails: bool
    used_on: str | None
    mask_type: str  # always "random" for this resource
    created_at: datetime
    last_modified_at: datetime
    last_used_at: datetime | None
    num_forwarded: int
    num_blocked: int
    num_level_one_trackers_blocked: int
    num_replied: int
    num_spam: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RelayAddress:
        """Build a RelayAddress from a parsed JSON object."""
        return cls(
            id=data["id"],
            address=data["address"],
            domain=data["domain"],
            full_address=data["full_address"],
            enabled=data["enabled"],
            description=data.get("description", ""),
            generated_for=data.get("generated_for", ""),
            block_list_emails=data.get("block_list_emails", False),
            used_on=data.get("used_on"),
            mask_type=data.get("mask_type", "random"),
            created_at=_require_dt(data, "created_at"),
            last_modified_at=_require_dt(data, "last_modified_at"),
            last_used_at=_parse_dt(data.get("last_used_at")),
            num_forwarded=data.get("num_forwarded", 0),
            num_blocked=data.get("num_blocked", 0),
            num_level_one_trackers_blocked=data.get("num_level_one_trackers_blocked", 0),
            num_replied=data.get("num_replied", 0),
            num_spam=data.get("num_spam", 0),
        )
