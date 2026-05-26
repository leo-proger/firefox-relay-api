"""RelayAddresses resource (random email masks)."""

from __future__ import annotations

from ..models import RelayAddress
from ._base import BaseResource


class RelayAddresses(BaseResource):
    """Manage random email masks via ``/api/v1/relayaddresses/``."""

    _path = "relayaddresses/"

    def list(self) -> list[RelayAddress]:
        """Return all relay addresses for the authenticated user."""
        data = self._http.get(self._path)
        return [RelayAddress.from_dict(item) for item in data]

    def get(self, mask_id: int) -> RelayAddress:
        """Fetch a single relay address by id."""
        data = self._http.get(f"{self._path}{mask_id}/")
        return RelayAddress.from_dict(data)

    def create(
        self,
        *,
        description: str = "",
        enabled: bool = True,
        generated_for: str = "",
        block_list_emails: bool = False,
        used_on: str | None = None,
    ) -> RelayAddress:
        """Create a new random email mask.

        Note: ``block_list_emails=True`` requires a premium account.
        """
        payload: dict[str, object] = {
            "enabled": enabled,
            "description": description,
            "generated_for": generated_for,
            "block_list_emails": block_list_emails,
        }
        if used_on is not None:
            payload["used_on"] = used_on
        data = self._http.post(self._path, json=payload)
        return RelayAddress.from_dict(data)

    def update(
        self,
        mask_id: int,
        *,
        description: str | None = None,
        enabled: bool | None = None,
        block_list_emails: bool | None = None,
        used_on: str | None = None,
    ) -> RelayAddress:
        """Partially update a mask. Only provided fields are sent."""
        payload: dict[str, object] = {}
        if description is not None:
            payload["description"] = description
        if enabled is not None:
            payload["enabled"] = enabled
        if block_list_emails is not None:
            payload["block_list_emails"] = block_list_emails
        if used_on is not None:
            payload["used_on"] = used_on
        if not payload:
            raise ValueError("update() requires at least one field to change")
        data = self._http.patch(f"{self._path}{mask_id}/", json=payload)
        return RelayAddress.from_dict(data)

    def delete(self, mask_id: int) -> None:
        """Delete a relay address. Returns nothing on success."""
        self._http.delete(f"{self._path}{mask_id}/")
