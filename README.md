# Camaro CAN Bus Project

Reverse engineering and controlling body-electronics functions (starting with door locks) on a
2012 Chevrolet Camaro 1LT using a Raspberry Pi and a Waveshare 2-Channel Isolated CAN HAT,
with the eventual goal of triggering actions (like unlocking doors) remotely from a phone.

## Why this project

- Hands-on embedded systems / hardware-software integration experience
- Directly relevant to aerospace/embedded software roles (real-time systems, physical
  hardware interfacing, safety-conscious design)
- A finish-able, demoable result: unlock the car from a phone

## Repo layout

```
docs/
  threat-model.md      - system threat model (Level 0-2), risk-rated
  architecture.md       - system design: phone -> tunnel -> Pi -> CAN -> vehicle
  can-notes.md           - raw findings: candump captures, arbitration IDs, decoded messages
  progress-log.md        - dated log of what was tried, what worked, what didn't
hardware/
  wiring.md              - CAN HAT wiring, OBD-II pinout notes, photos (add your own)
src/
  (Go/Python code for the Pi-side API and CAN send/receive logic)
```

## Status

- [x] Raspberry Pi set up with Waveshare 2-Channel Isolated CAN HAT
- [x] OBD-II connector wired in, CAN interface reads traffic (`candump`)
- [ ] Identify door lock/unlock CAN message (arbitration ID + data bytes)
- [ ] Verify by replay (`cansend`)
- [ ] Build API endpoint on the Pi to send the lock/unlock frame
- [ ] Secure remote access (Tailscale/WireGuard)
- [ ] Trigger from phone (Shortcuts/Tasker -> HTTPS -> Pi API)
- [ ] Stretch goal: remote start (requires further research into ECU safety interlocks)

## References

- Craig Smith, *The Car Hacker's Handbook* - https://opengarages.org/handbook/ebook/
- [SocketCAN / can-utils](https://github.com/linux-can/can-utils)
