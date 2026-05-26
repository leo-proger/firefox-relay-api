"""Smoke tests for FirefoxRelayClient using respx to mock httpx."""

from __future__ import annotations

import httpx
import pytest
import respx

from firefox_relay import (
    FirefoxRelayClient,
    RelayAuthError,
    RelayLimitReachedError,
    RelayNotFoundError,
    RelayPermissionError,
    RelayValidationError,
)

BASE_URL = "https://relay.firefox.com/api/v1/"

SAMPLE_MASK = {
    "id": 1,
    "address": "abc123",
    "domain": "mozmail.com",
    "full_address": "abc123@mozmail.com",
    "enabled": True,
    "description": "test",
    "generated_for": "",
    "block_list_emails": False,
    "used_on": None,
    "mask_type": "random",
    "created_at": "2026-01-01T00:00:00Z",
    "last_modified_at": "2026-01-01T00:00:00Z",
    "last_used_at": None,
    "num_forwarded": 0,
    "num_blocked": 0,
    "num_level_one_trackers_blocked": 0,
    "num_replied": 0,
    "num_spam": 0,
}


@pytest.fixture
def client():
    with FirefoxRelayClient(api_key="test-token") as c:
        yield c


@respx.mock
def test_list_relay_addresses(client):
    respx.get(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(200, json=[SAMPLE_MASK])
    )
    masks = client.relay_addresses.list()
    assert len(masks) == 1
    assert masks[0].full_address == "abc123@mozmail.com"
    assert masks[0].enabled is True


@respx.mock
def test_get_relay_address(client):
    respx.get(f"{BASE_URL}relayaddresses/1/").mock(
        return_value=httpx.Response(200, json=SAMPLE_MASK)
    )
    mask = client.relay_addresses.get(1)
    assert mask.id == 1


@respx.mock
def test_create_relay_address(client):
    route = respx.post(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(201, json={**SAMPLE_MASK, "id": 42, "description": "shopping"})
    )
    mask = client.relay_addresses.create(description="shopping")
    assert mask.id == 42
    assert mask.description == "shopping"
    # verify payload
    sent = route.calls.last.request
    assert b'"description":"shopping"' in sent.content
    assert b'"enabled":true' in sent.content


@respx.mock
def test_update_relay_address(client):
    respx.patch(f"{BASE_URL}relayaddresses/1/").mock(
        return_value=httpx.Response(200, json={**SAMPLE_MASK, "description": "renamed"})
    )
    mask = client.relay_addresses.update(1, description="renamed")
    assert mask.description == "renamed"


def test_update_requires_a_field(client):
    with pytest.raises(ValueError):
        client.relay_addresses.update(1)


@respx.mock
def test_delete_relay_address(client):
    respx.delete(f"{BASE_URL}relayaddresses/42/").mock(
        return_value=httpx.Response(204)
    )
    client.relay_addresses.delete(42)


@respx.mock
def test_auth_error_401(client):
    respx.get(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(401, json={"detail": "Invalid token"})
    )
    with pytest.raises(RelayAuthError) as exc_info:
        client.relay_addresses.list()
    assert exc_info.value.status_code == 401


@respx.mock
def test_permission_error_403(client):
    respx.post(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(
            403, json={"detail": "Must be premium to set block_list_emails."}
        )
    )
    with pytest.raises(RelayPermissionError) as exc_info:
        client.relay_addresses.create(block_list_emails=True)
    assert not isinstance(exc_info.value, RelayLimitReachedError)
    assert exc_info.value.status_code == 403


@respx.mock
def test_limit_reached_403(client):
    # Real message Mozilla returns when free account hits 50 masks
    msg = (
        "You\u2019ve used all \u206850\u2069 email masks included with your "
        "free account. You can reuse an existing mask, but using a unique "
        "mask for each account is the most secure option."
    )
    respx.post(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(403, json={"detail": msg})
    )
    with pytest.raises(RelayLimitReachedError) as exc_info:
        client.relay_addresses.create()
    # subclass of RelayPermissionError — both catches work
    assert isinstance(exc_info.value, RelayPermissionError)
    assert "50" in exc_info.value.message


@respx.mock
def test_not_found(client):
    respx.get(f"{BASE_URL}relayaddresses/999/").mock(
        return_value=httpx.Response(404, json={"detail": "Not found."})
    )
    with pytest.raises(RelayNotFoundError):
        client.relay_addresses.get(999)


@respx.mock
def test_validation_error(client):
    respx.post(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(
            400, json={"generated_for": ["This field may not be null."]}
        )
    )
    with pytest.raises(RelayValidationError) as exc_info:
        client.relay_addresses.create()
    assert exc_info.value.status_code == 400
    assert "generated_for" in exc_info.value.response_body


def test_empty_api_key_rejected():
    with pytest.raises(ValueError):
        FirefoxRelayClient(api_key="")


@respx.mock
def test_auth_header_sent(client):
    route = respx.get(f"{BASE_URL}relayaddresses/").mock(
        return_value=httpx.Response(200, json=[])
    )
    client.relay_addresses.list()
    assert route.calls.last.request.headers["Authorization"] == "Token test-token"
