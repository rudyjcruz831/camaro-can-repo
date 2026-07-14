# Threat Model — Camaro CAN Bus Project

Following the Level 0 -> Level 1 -> Level 2 methodology from *The Car Hacker's Handbook*
(Craig Smith), adapted here for a personal DIY project rather than a professional pentest.
The goal is the same as in systems engineering coursework: decompose the system, define
trust boundaries, and identify risks before building.

This is a living document — update it as the project (and your understanding of the
vehicle's network) evolves.

## Level 0 — Bird's-eye view

External inputs to the vehicle, and the vehicle as a single process (1.0):

| Input | Trust level | Notes |
|---|---|---|
| OBD-II port (physical access) | Untrusted (physical) | Your primary access point for this project |
| Key fob (RF) | Untrusted (wireless) | Not currently in scope |
| Bluetooth/infotainment (if present) | Untrusted (wireless) | Not currently in scope |

## Level 1 — Receivers

What each input actually talks to inside the vehicle:

| Receiver | ID | Fed by | Notes |
|---|---|---|---|
| Body Control Module (BCM) | 1.1 | OBD-II via body CAN bus | Owns door locks, likely target for this project |
| Powertrain/Engine ECU | 1.2 | OBD-II via powertrain CAN bus | Out of scope unless pursuing remote start |
| Instrument cluster | 1.3 | Body CAN bus | Useful for noise/context, not a target |

## Level 2 — Receiver breakdown (BCM, since that's this project's target)

| Component | Risk to the project (not just security) | Notes |
|---|---|---|
| Door lock actuator circuit | Low — physically reversible | Worst case: doors don't respond, no lasting damage |
| CAN message misinterpretation | Medium | Sending an unverified frame could trigger an unintended action (e.g. wrong door, dash warning light) |
| Bus flooding / malformed frames | Medium | Could cause the BCM or other modules to behave unexpectedly; always test with `candump` first, never blind-send |
| Safety interlocks (relevant if pursuing remote start) | High | Engine start involves interlocks (park/neutral, brake) enforced by the ECU — not just a CAN message away |

## Working notes / self-risk-rating (adapted DREAD, informal)

For each finding as you reverse-engineer, rate roughly 1 (low) to 3 (high) on:
**Damage potential**, **Reproducibility**, **Ease of causing unintended side effects**.
This isn't for a report — it's to force you to think before you `cansend` something
you haven't fully understood yet.

| Message / action | Damage potential | Reproducibility | Side-effect risk | Notes |
|---|---|---|---|---|
| _(fill in as you find candidate CAN IDs)_ | | | | |

## Summary

This project's attack surface is intentionally narrow: physical OBD-II access to your own
vehicle, targeting only the BCM's door-lock function. Documenting this now — before wiring
up remote/phone access — is what turns "I plugged stuff in and it worked" into a
demonstrable systems-engineering process you can walk an interviewer through.
