# Changelog

## 0.1.0 – 2026-05-26

Initial release.

- `FirefoxRelayClient` with sync API
- Full CRUD for `/relayaddresses/` (random masks)
- Exception hierarchy: `RelayError` + auth/permission/limit/not-found/validation/ratelimit/server
- Tested against live Firefox Relay API
