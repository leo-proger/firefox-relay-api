# firefox-relay-api

Unofficial Python client for [Firefox Relay](https://relay.firefox.com/). Not affiliated with Mozilla.

> ⚠️ The Firefox Relay API is **not officially documented** for third-party use. Endpoints and fields may change without
> notice.

## Install

```bash
pip install firefox-relay-api
```

Requires Python 3.10+.

## Quickstart

Get your API key from [Relay account settings](https://relay.firefox.com/accounts/profile/).

```python
from firefox_relay import FirefoxRelayClient

with FirefoxRelayClient(api_key="your-api-key") as client:
    # Create a mask
    mask = client.relay_addresses.create(description="for shopping")
    print(mask.full_address)  # e.g. abc123@mozmail.com

    # List all masks
    for m in client.relay_addresses.list():
        print(m.full_address, "—", m.description)

    # Rename
    client.relay_addresses.update(mask.id, description="renamed")

    # Disable (stop forwarding) without deleting
    client.relay_addresses.update(mask.id, enabled=False)

    # Delete
    client.relay_addresses.delete(mask.id)
```

## Error handling

All errors inherit from `RelayError`:

```python
from firefox_relay import RelayError, RelayAuthError, RelayRateLimitError

try:
    client.relay_addresses.list()
except RelayAuthError:
    print("Bad or expired API key")
except RelayRateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
except RelayError as e:
    print(f"API error: {e.message} (HTTP {e.status_code})")
```

## Status

`v0.1.0` — MVP, supports random masks (`/relayaddresses/`) only.

Planned for `v0.2`: domain addresses (premium), profile, runtime data, async client.

## License

MIT
