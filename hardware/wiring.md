# Hardware Setup

## Components

- Raspberry Pi (model: ___)
- Waveshare 2-Channel Isolated CAN HAT
- OBD-II to DB9/breakout cable

## Wiring notes

- OBD-II pins 6 and 14: CAN High / CAN Low (standard HS-CAN)
- Bus speed: 500 Kbps (typical GM HS-CAN) — confirm with `can-calc-bit-timing` if unsure
- (Add photos of your physical setup here — drop image files in this folder and
  reference them with `![description](filename.jpg)`)

## Bring-up commands

```bash
sudo ip link set can0 type can bitrate 500000
sudo ip link set up can0
ifconfig can0   # confirm interface is up
```
