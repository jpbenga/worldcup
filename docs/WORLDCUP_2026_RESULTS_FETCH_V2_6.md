# World Cup 2026 Results Fetch V2.6

V2.6 published a separate results overlay for all `72` release-candidate fixtures. The fetch used `api_football` and made `1` API request(s). It found `1` finished, `0` live and `71` not-started fixtures.

Pre-match predictions were not opened for writing or recalculated. Results remain a separate evaluation layer. When the API key or result data is unavailable, this script still publishes a complete status file and reports `result_available: false`.

Statuses are normalized into not-started, live, finished, postponed, cancelled
or unknown. Only the cached raw API response and the separate V2.6 result
artifacts are written. Credentials are loaded through the existing local
configuration and are never included in logs or published JSON.
