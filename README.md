# 2012 Chevrolet Camaro 1LT — CAN Bus Reverse Engineering Project

A personal project to connect a Raspberry Pi 3 to a 2012 Chevrolet Camaro 1LT via OBD2, capture and analyze CAN bus traffic, and eventually control body functions (door locks) remotely via phone — without a key fob or subscription service.

---

## Project Goals

- [x] Understand CAN bus architecture and protocols
- [x] Identify OBD2 pin assignments on the physical connector
- [x] Map wire colors on iKKEGOL OBD2 breakout cable
- [ ] Connect Raspberry Pi + Waveshare HAT to high speed GMLAN (Phase 4)
- [ ] Capture live CAN frames with candump
- [ ] Reverse engineer SWCAN body bus (Phase 5)
- [ ] Control door locks remotely from phone
- [ ] Build wake-on-demand system using ESP32
- [ ] Full phone-based remote control system

---

## Hardware

| Component | Model | Notes |
|---|---|---|
| Single board computer | Raspberry Pi 3 | Headless setup |
| CAN HAT | Waveshare 2-Channel Isolated CAN HAT (B087RJ6XGG) | MCP2515 controller + SN65HVD230 transceiver |
| OBD2 breakout cable | iKKEGOL 16-pin male breakout (B002EJ69CT) | All 16 pins connected, open wire ends |
| Soldering station | WEP 882D | Temperature controlled |
| Prototype PCB kit | Smraza 104pcs (B07NM68FXK) | For permanent build |
| SOIC-8 breakout board | Stargazer (B07R5QR9P3) | For TH8056 SWCAN transceiver chip |
| SWCAN transceiver | TH8056KDC-AAA-008-SP (Melexis) | Ordered from eBay — replacement for discontinued NCV7356 |

### Pending Orders
- TH8056KDC-AAA-008-SP x5 — eBay
- ESP32 development board — Amazon (Phase 6)
- 5V relay module — Amazon (Phase 6)
- 12V to 5V 3A buck converter — Amazon (Phase 6)

---

## Vehicle Architecture

### 2012 Chevrolet Camaro 1LT — Dual CAN Bus System

The Camaro uses GM's GMLAN protocol built on ISO 15765-2 (ISO-TP), consisting of two separate CAN buses:

```
┌─────────────────────────────────────────────────────┐
│           HIGH SPEED GMLAN (HS-CAN)                 │
│           500 kbps — OBD2 Pins 6 and 14             │
│           Max 16 nodes                              │
│                                                     │
│  ECM ── TCM ── ABS ── Instrument Cluster            │
│  (Engine) (Trans) (Brakes)                          │
└──────────────────┬──────────────────────────────────┘
                   │
                  BCM (Gateway)
                   │
┌──────────────────┴──────────────────────────────────┐
│           SINGLE WIRE CAN (SWCAN)                   │
│           33.333 kbps — OBD2 Pin 1                  │
│           Max 32 nodes                              │
│                                                     │
│  BCM ── Door Locks ── Windows ── HVAC               │
│  ── Interior Lighting ── Immobilizer                │
│  ── Mirrors ── Infotainment                         │
└─────────────────────────────────────────────────────┘
```

**Key architectural notes:**
- BCM acts as gateway between both buses
- Door locks and body control live on SWCAN — not accessible via standard OBD2 gateway
- Immobilizer lives on SWCAN — handles engine start authorization
- OnStar module (if equipped) connects to SWCAN and cellular network simultaneously
- OBD2 port exposes HS-CAN directly on pins 6/14 and SWCAN on pin 1

---

## OBD2 Connector — Standard Pinout

```
 ┌─────────────────────────────────┐
 │  1   2   3   4   5   6   7   8  │
 │  9  10  11  12  13  14  15  16  │
 └─────────────────────────────────┘
```

| Pin | Standard Function | GM/GMLAN Specific |
|---|---|---|
| 1 | Manufacturer discretion | SWCAN (Single Wire CAN) — 33.333 kbps |
| 2 | SAE J1850 Bus+ | Unused on this vehicle |
| 3 | Manufacturer discretion | Unused |
| 4 | Chassis Ground | Chassis Ground |
| 5 | Signal Ground | Signal Ground |
| 6 | CAN High (J2284) | HS-GMLAN CAN-H — 500 kbps |
| 7 | K-Line ISO 9141 | Diagnostic K-Line |
| 8 | Manufacturer discretion | Unused |
| 9 | Manufacturer discretion | Unused |
| 10 | SAE J1850 Bus- | Unused on this vehicle |
| 11 | Manufacturer discretion | Unused |
| 12 | Manufacturer discretion | Possible medium speed GMLAN — under investigation |
| 13 | Manufacturer discretion | Possible medium speed GMLAN — under investigation |
| 14 | CAN Low (J2284) | HS-GMLAN CAN-L — 500 kbps |
| 15 | L-Line ISO 9141 | Diagnostic L-Line |
| 16 | Battery Positive (unswitched) | Always-on 12V |

---

## OBD2 Cable Wire Color Mapping

**Cable:** iKKEGOL 16-pin OBD2 male breakout  
**Note:** Wire colors DO NOT match the product description. Verified by direct multimeter measurement on both the cable wires and the physical OBD2 port pins.

### Verified by Multimeter — Direct Pin Measurement

| Pin | Wire Color | Accessory Voltage | Engine On Voltage | Function | Status |
|---|---|---|---|---|---|
| 1 | Red/white | 1–2.55V fluctuating | Active | SWCAN | Phase 5 — keep taped |
| 4 | Blue | 0V | 0.03V | Chassis GND | ✅ Connect to HAT GND |
| 5 | White | 0V | 0.3V | Signal GND | ⚠️ Verify with continuity test |
| 6 | Green | 2.79V | 2.81V | CAN-H HS-GMLAN | ✅ Connect to HAT CAN-H |
| 12 | Pink | 2.53V | 2.54V | Unknown — possible MS-GMLAN CAN-H | 🔍 Investigate Phase 4 |
| 13 | Gray | 2.37V | 2.38V | Unknown — possible MS-GMLAN CAN-L | 🔍 Investigate Phase 4 |
| 14 | Green/white | 2.22V | 2.26V | CAN-L HS-GMLAN | ✅ Connect to HAT CAN-L |
| 16 | Red | 12V | 12V | Battery+ unswitched | ⚠️ DO NOT CONNECT — keep taped |

### Unconfirmed / Inactive Wires
| Wire Color | Voltage | Notes |
|---|---|---|
| Yellow | 0V | Inactive — manufacturer discretion pin |
| Orange | 0V | Inactive |
| Brown | 0V off / 1–2.55V on | Active when engine running — investigate |
| Baby blue | 0V | Inactive |
| Purple | 0V | Inactive |
| Black | 0V | Inactive |
| Brown/white | 0V | Inactive |
| Black/white | 0V | Inactive |

### ⚠️ Important Notes
- All unused wires taped off individually with electrical tape
- Pin 16 (Red — 12V) double taped — most dangerous wire on connector
- Pin 1 (Red/white — SWCAN) taped and labeled for Phase 5
- White wire (Pin 5) needs continuity test confirmation before connecting
- For door locks:
      Without a key fob you currently have no way to remotely lock or unlock your car at all.

      For remote start:
      This is more complex without a fob. The 2012 Camaro has an immobilizer that reads the transponder chip embedded in your metal key. When you insert the key and turn it the BCM reads that chip and authorizes the ECM to start. Without that physical key transponder present the car will not start even if you send the correct CAN frames.

      So remote start via CAN alone is not possible without solving the immobilizer challenge first. You have two options for that later:

      Option A — Keep the key in the car:
      Mount the metal key near the ignition permanently. The transponder is always present so the immobilizer is always satisfied. Your Pi just needs to send the ignition on CAN frames. Not the most secure but functional.

      Option B — Bypass the immobilizer:
      More complex, involves either cloning the transponder or sending the correct immobilizer authorization frames on SWCAN. This is advanced territory and a Phase 6 goal at earliest.

      The OnStar module has its own stored cryptographic token that the immobilizer recognizes as a valid authorization — essentially the OnStar module IS a permanent electronic key that lives inside the car
---

## Waveshare HAT — Connection Plan

**HAT:** Waveshare 2-Channel Isolated CAN HAT  
**Controllers:** 2x MCP2515  
**Transceivers:** 2x SN65HVD230 (differential CAN only — cannot do SWCAN)  
**Interface:** SPI to Raspberry Pi GPIO

### Phase 4 — HS-GMLAN Connection (Channel 1)

```
OBD2 Connector          Waveshare HAT
─────────────          ─────────────
Pin 6  (Green)    ───► Channel 1 CAN-H
Pin 14 (Grn/Wht)  ───► Channel 1 CAN-L
Pin 4  (Blue)     ───► GND
Pin 5  (White)    ───► GND

⚠️ Termination resistor jumper: DISABLE on HAT
   (Camaro already has termination — double termination causes errors)
⚠️ VIO jumper: Set to 3.3V (Pi GPIO is 3.3V logic)
```

### Phase 5 — SWCAN Connection (Channel 2) — FUTURE

```
OBD2 Connector          TH8056 Transceiver      Waveshare HAT
─────────────          ──────────────────      ─────────────
Pin 1 (Red/Wht)   ───► CANH pin          
                        TxD/RxD           ───► Channel 2 MCP2515
                        VCC               ◄─── 3.3V
                        VBAT              ◄─── 12V (from Pin 16)
                        GND               ◄─── GND

Note: TH8056 bypasses built-in SN65HVD230 transceiver on Channel 2
Note: SWCAN bus requires high voltage wakeup pulse before communication
```

---

## HAT Setup — Critical Configuration

Before connecting anything check these jumper settings on the Waveshare HAT:

1. **VIO jumper → 3.3V** — Pi runs 3.3V logic, wrong setting damages HAT
2. **Termination resistor → DISABLED** — car already has 120Ω termination at both ends
3. **SPI must be enabled** in `/boot/config.txt` or Raspberry Pi Imager settings

---

## Raspberry Pi Setup

**OS:** Raspberry Pi OS Lite 64-bit (fresh flash)  
**Hostname:** raspberry-car  
**Access:** SSH over WiFi 

### Flashing with Raspberry Pi Imager
1. Download Raspberry Pi Imager from `raspberrypi.com/software`
2. Select device: Raspberry Pi 3
3. Select OS: Raspberry Pi OS Lite 64-bit
4. Click settings gear and configure:
   - Hostname: `raspberry-car`
   - Enable SSH: yes
   - Username: your choice
   - Password: your choice
   - WiFi SSID and password
   - Country: US

### Software to Install (after SSH connection)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Enable SPI in config
sudo raspi-config
# Interface Options → SPI → Enable

# Install CAN utilities
sudo apt install can-utils -y

# Install Python CAN library
pip install python-can --break-system-packages

# Bring up CAN interface
sudo ip link set can0 up type can bitrate 500000

# Test — start capturing frames
candump can0
```

---

## CAN Bus Concepts — Key Notes

### Why CAN Exists
Replaced hundreds of point-to-point wires in vehicles with a single shared two-wire bus. Every module connects to the same two wires and broadcasts messages with unique IDs. Every module listens to everything and filters for IDs it cares about.

### Differential Signaling
- CAN-H and CAN-L move in opposite directions simultaneously
- Recessive state: both at 2.5V, differential = 0V = bit 1
- Dominant state: CAN-H rises to 3.5V, CAN-L drops to 1.5V, differential = 2V = bit 0
- Receiver reads only the voltage difference — noise hits both wires equally and cancels out

### Arbitration
- All nodes transmit simultaneously, bit by bit
- Dominant 0 overrides recessive 1 on the wire
- Node that transmits 1 but reads back 0 lost arbitration — stops immediately
- Lower ID = more dominant 0 bits = higher priority
- No collision, no retransmission negotiation — resolves in microseconds at hardware level
- Similar to distributed systems leader election but implemented in hardware

### Frame Structure
```
SOF | Arbitration ID | Control | Data (0-8 bytes) | CRC | ACK | EOF
 1b |   11 or 29b    |   6b    |    0-64 bits     | 16b |  2b |  7b
```
- ID identifies message content, not destination — no addresses in CAN
- DLC field (4 bits in Control) specifies how many data bytes follow
- CRC and ACK handled entirely by MCP2515 hardware
- candump output format: `(timestamp) can0 ID#DATA`

### SWCAN vs Standard CAN
| | Standard CAN | SWCAN |
|---|---|---|
| Wires | 2 (CAN-H + CAN-L) | 1 + chassis ground |
| Signaling | Differential | Single wire voltage |
| Recessive | 2.5V differential | ~0V |
| Dominant | 2V differential | ~4V |
| Speed | 500 kbps (HS-GMLAN) | 33.333 kbps |
| Noise immunity | Excellent | Moderate |
| Wakeup | Always active | High voltage pulse (12V) |
| Transceiver | SN65HVD230 | TH8056 |
| Protocol | Identical CAN frames | Identical CAN frames |

---

## Phase Roadmap

### Phase 1 — Foundations ✅ Complete
- CAN bus history and why it exists
- Differential signaling and termination
- OSI model mapping for automotive
- Read: TI Introduction to CAN (SLOA101B)

### Phase 2 — CAN Protocol ✅ Complete
- Frame structure byte by byte
- Non-destructive bitwise arbitration
- Error handling and fault confinement
- CAN FD overview
- Read: Car Hacker's Handbook Chapters 1-3

### Phase 3 — OBD2 and Diagnostics 🔄 In Progress
- SAE J1979 OBD2 PIDs
- ISO 14229 UDS protocol
- Multi-bus vehicle architecture
- Read: Car Hacker's Handbook OBD2 chapter

### Phase 4 — Hardware Build 🔄 In Progress
- Raspberry Pi OS fresh flash
- Waveshare HAT SPI configuration
- SocketCAN setup
- Connect to HS-GMLAN pins 6 and 14
- Run candump and capture live frames
- Investigate mystery pins 12 and 13

### Phase 5 — SWCAN Body Bus 📋 Planned
- Order and build TH8056 transceiver circuit
- Connect to SWCAN on pin 1
- Capture SWCAN traffic with candump
- Press door lock button inside car — capture frames
- Isolate door lock frame ID and payload
- Replay frames from Pi — verify door lock works

### Phase 6 — Remote Control System 📋 Planned
- ESP32 always-on wake module (powered from pin 16)
- 12V to 5V buck converter for Pi power
- Ignition-switched power via fuse tap
- REST API on Pi (Go backend)
- Phone app sends commands to Pi
- Wake on demand — ESP32 wakes Pi on command
- SWCAN wakeup pulse before sending commands
- Investigate remote start and immobilizer challenge

---

## Safety and Legal Notes

- This project is performed on a personally owned vehicle
- All CAN bus access is through the OBD2 port or direct wire tap
- No modification to vehicle safety systems (brakes, airbags, steering)
- Pin 16 (12V unswitched) is always taped off when not in use
- SWCAN commands tested in controlled environment only
- Remote start investigation deferred pending immobilizer research

---

## References and Resources

| Resource | URL | Notes |
|---|---|---|
| TI Introduction to CAN | ti.com/lit/an/sloa101b/sloa101b.pdf | Physical layer — Phase 1 reading |
| CSS Electronics CAN intro | csselectronics.com | Best practical CAN tutorials |
| Kvaser CAN protocol | kvaser.com/about-can | Protocol deep dive |
| Linux SocketCAN docs | kernel.org/doc/html/latest/networking/can.html | Kernel driver reference |
| Waveshare HAT wiki | waveshare.com/wiki/2-CH_CAN_HAT | Setup guide for your specific HAT |
| python-can docs | python-can.readthedocs.io | Python CAN library |
| opendbc | github.com/commaai/opendbc | Open vehicle DBC files |
| can-utils | github.com/linux-can/can-utils | candump cansend cansniffer |
| Car Hacker's Handbook | opengarages.org/handbook | Main project reference book |
| Bit timing calculator | bittiming.can-wiki.info | MCP2515 CNF register calculator |
| TH8056 datasheet | melexis.com | SWCAN transceiver reference |

---

## Project Log

| Date | Milestone |
|---|---|
| 2026-07 | Started project — read TI CAN intro document |
| 2026-07 | Studied Car Hacker's Handbook Chapters 1-3 |
| 2026-07 | Identified all 16 OBD2 wire colors with multimeter |
| 2026-07 | Confirmed CAN-H (green) and CAN-L (green/white) |
| 2026-07 | Discovered mystery pins 12/13 — possible second CAN bus |
| 2026-07 | Ordered TH8056 SWCAN transceiver from eBay |
| 2026-07 | Flashing fresh Raspberry Pi OS — in progress |

