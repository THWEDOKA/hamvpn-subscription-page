# RabbitHole for iOS — 2026-11-09

Replaced the VPNET card in the default HAMVPN panel configuration without
changing the order or contents of other cards. iOS now lists RabbitHole, INCY,
and Happ. The new card links to App Store app 6683309629 and uses the existing
subscription-copy button. No deep link or change to subscription exports was
introduced.

The candidate passed the installed schema on all four servers. Only the
subscription-page container was restarted on each origin, one at a time.
All returned healthy. HTTPS checks using the dedicated monitoring probe
verified page, assets and identical application configuration on the main
origin and all three mirrors. Native iPhone import was not tested.

The private panel backup is in `/root/ham-subpage-rabbithole-20261109` on the
bot server. `operation.py rollback` restores only the matching deployment's
panel configuration; refresh the four subscription-page containers after
rollback to discard their startup cache. The deployment timer was stopped
after verification. The Russian release journal entry was saved and read back.
