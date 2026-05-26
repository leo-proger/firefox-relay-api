"""Manual smoke test against a local fx-private-relay backend.

Usage:
    export RELAY_API_KEY=<your-token-from-admin>
    python scripts/smoke_test.py
"""

from __future__ import annotations

import os
import sys

from firefox_relay import FirefoxRelayClient, RelayError

LOCAL_URL = os.environ.get("RELAY_BASE_URL", "http://127.0.0.1:8000/api/v1/")
API_KEY = os.environ.get("RELAY_API_KEY")

if not API_KEY:
    sys.exit("Set RELAY_API_KEY env var (find it in Django admin → Profiles)")


def main() -> None:
    with FirefoxRelayClient(api_key=API_KEY, base_url=LOCAL_URL) as client:
        print(f"→ Base URL: {LOCAL_URL}\n")

        print("1. LIST")
        masks = client.relay_addresses.list()
        print(f"   {len(masks)} mask(s) already exist")
        for m in masks:
            print(f"   - id={m.id} {m.full_address} enabled={m.enabled}")

        print("\n2. CREATE")
        new = client.relay_addresses.create(description="smoke-test")
        print(f"   created id={new.id} {new.full_address}")

        print("\n3. GET")
        fetched = client.relay_addresses.get(new.id)
        assert fetched.id == new.id
        print(f"   ok, description={fetched.description!r}")

        print("\n4. UPDATE")
        renamed = client.relay_addresses.update(new.id, description="renamed")
        assert renamed.description == "renamed"
        print("   description changed")

        print("\n5. DELETE")
        client.relay_addresses.delete(new.id)
        print("   deleted")

        print("\n6. VERIFY DELETION")
        try:
            client.relay_addresses.get(new.id)
        except RelayError as e:
            print(f"   ok, got {type(e).__name__}: {e.message}")

    print("\n✓ all good")


if __name__ == "__main__":
    main()
