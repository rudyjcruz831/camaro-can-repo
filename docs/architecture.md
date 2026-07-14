# System Architecture

## Overview

```
Phone (Shortcut/Tasker)
      |
      v
Secure tunnel (Tailscale/WireGuard) - encrypted, no open ports to the internet
      |
      v
Raspberry Pi API (Go) - checks auth token, builds CAN frame
      |
      v
Waveshare 2-Channel Isolated CAN HAT - sends frame on body CAN bus
      |
      v
Body Control Module - executes lock/unlock
```

## Design decisions

- **Why a VPN tunnel instead of exposing the Pi directly:** this system can unlock a real
  car — no open ports, ever. Tailscale/WireGuard means only devices you've explicitly
  authorized can reach the Pi's API at all.
- **Why an auth token on the API, in addition to the tunnel:** defense in depth — the
  tunnel controls network reachability, the token controls whether a request is honored.
- **Why Go for the API:** reusing the same pattern as the existing Pi home-automation
  project (Go API + local CAN tooling), so this project extends known-working
  infrastructure instead of starting from scratch.

## Open questions

- Exact CAN ID / data bytes for door lock and unlock (see `can-notes.md`)
- Whether the BCM requires the frame to be sent at a specific bus timing/rate to be
  accepted, or a single frame is sufficient
- Remote start: feasibility depends on whether the ECU's safety interlocks can be
  satisfied without a factory or aftermarket remote-start module (see threat-model.md)
