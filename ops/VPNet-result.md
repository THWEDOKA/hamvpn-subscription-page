# VPNET rollout — 2026-10-27

Added the VPNET card alongside INCY and Happ in HAMVPN's current iOS
subscription-page config (goszapravki.com panel). Existing apps, defaults,
branding and other platforms were preserved. The card uses the App Store ID
6756558545 and the standard copy-subscription button; it does not claim an
unverified automatic import scheme.

Validated against SubscriptionPageRawConfigSchema and three unit tests.
The subscription-page service was restarted to refresh its config cache.
The real page and authenticated config endpoint on gos.hamgos.com returned 200;
the served config contains VPNET. The container subsequently reported healthy.
The verification used a temporary account, deleted after testing.

Actual clipboard import and connection in VPNET on an iPhone have not been
tested; server-side checks do not establish device compatibility.

## Mirror-cache correction, same day

The first rollout checked only 77.95.203.212. DNS also resolves the subscription
hostname to 194.226.163.46. Its independent subscription-page process had been
running for two months with a stale startup cache containing only INCY and Happ.
This caused intermittent missing VPNET regardless of browser; the initial
apparent User-Agent difference was DNS round-robin, not a browser-specific rule.

Restarted only the subscription-page container on 194.226.163.46, preserving its
existing image and configuration. No image pull, DNS edit or customer subscription
change. Both origins now return the same config hash and iOS list: VPNET, INCY,
Happ. HTML, frontend assets and authenticated config were tested separately per
IP using curl --resolve with regular hostname/TLS verification.

Browser QA also rendered the second origin's actual frontend through a temporary
loopback-only SSH tunnel: VPNET button and instruction cards visible at iPhone
viewport size, no JavaScript console errors. Desktop iOS selection also checked.
This verifies the instructions UI, not importing into the native VPNET app.

`verify_subpage_origins.py` is the new release check for all DNS origins, using
only a temporary operation-owned account and private evidence files. Six unit
tests cover the instruction builder and origin-check parsing/validation. Future
subscription-page config changes must refresh and verify every active mirror.
