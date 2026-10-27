# VPNET for iOS

`vpnet_ios.add_vpnet` appends one non-featured VPNET card to the current raw
subscription-page config. It preserves branding, existing apps, other platforms
and defaults. Read the live config first, validate the result against the deployed
schema, snapshot the original privately and PATCH only that config UUID.

The App Store listing (id 6756558545, Green Meadow Media) requires iOS 16+.
The developer's public site https://vpnet-client.com/ does not document an import
URL scheme. Use the existing `copyButton` subscription template rather than an
invented deep link. Actual device import still requires an iPhone test.

Do not commit private subscription links, JWTs or complete production snapshots.
If the subscription-page service caches configs at startup, refresh only that
service and verify the served card, not just the panel API response.

Test: `python -m unittest discover -s ops -p test_vpnet_ios.py`.
