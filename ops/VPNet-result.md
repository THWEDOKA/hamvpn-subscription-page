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
