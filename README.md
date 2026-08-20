## HAMVPN Subscription Page

HAMVPN interface for the open-source Remnawave Subscription Page. It keeps the upstream API and
client compatibility while providing a branded, device-first connection flow.

### Build

```bash
docker build --build-arg VCS_REF="$(git rev-parse HEAD)" -t hamvpn/subscription-page:latest .
```

### Design principles

- truthful subscription status before technical details;
- three-step device connection flow;
- 44px minimum touch targets and visible keyboard focus;
- low-cost motion with reduced-motion support;
- no credentials or production configuration in the image.

Based on [Remnawave Subscription Page](https://github.com/remnawave/subscription-page) and
distributed under AGPL-3.0.

# Contributors

Check [open issues](https://github.com/remnawave/subscription-page/issues) to help the progress of this project.

<p align="center">
Thanks to the all contributors who have helped improve Remnawave:
</p>
<p align="center">
<a href="https://github.com/remnawave/subscription-page/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=remnawave/subscription-page" />
</a>
</p>
