#!/usr/bin/env python3
"""
Camaro CAN Bus RPM Reader
2012 Chevrolet Camaro 1LT - High Speed GMLAN
Interface: can1 at 500 kbps

Frame 0C9 - bytes 2 and 3 contain RPM
Formula: RPM = ((byte2 << 8) | byte3) * 0.5

Author: Rudy Cruz
"""

import can
import time
import signal
import sys

# Configuration
CAN_INTERFACE = 'can1'
RPM_FRAME_ID  = 0x0C9
RPM_SCALING   = 0.5

# Track statistics
frame_count = 0
start_time  = time.time()
running     = True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    global running
    running = False
    print("\n\nStopping...")

def decode_rpm(data):
    """
    Decode RPM from frame 0C9 bytes 2 and 3

    Byte layout:
    [0] [1] [2] [3] [4] [5] [6] [7]
              ^---^
              RPM bytes (16-bit big endian)

    Formula: raw = (byte2 << 8) | byte3
             RPM = raw * 0.5
    """
    byte2 = data[2]  # high byte
    byte3 = data[3]  # low byte

    # Combine into 16-bit integer
    # << 8 shifts byte2 left by 8 bits (same as multiplying by 256)
    # | is bitwise OR which combines the two bytes
    raw = (byte2 << 8) | byte3

    # Apply GM scaling factor
    rpm = raw * RPM_SCALING

    return rpm, raw, byte2, byte3

def main():
    global frame_count, running

    # Register Ctrl+C handler
    signal.signal(signal.SIGINT, signal_handler)

    print("=" * 50)
    print("  2012 Camaro CAN Bus RPM Reader")
    print("=" * 50)
    print(f"  Interface : {CAN_INTERFACE}")
    print(f"  Frame ID  : 0x{RPM_FRAME_ID:03X}")
    print(f"  Scaling   : x{RPM_SCALING}")
    print("=" * 50)
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    print()

    try:
        # Connect to CAN bus
        # bustype='socketcan' uses Linux SocketCAN kernel interface
        # same socket the kernel uses for candump
        bus = can.interface.Bus(
            channel=CAN_INTERFACE,
            bustype='socketcan'
        )
        print(f"Connected to {CAN_INTERFACE} successfully")
        print()

    except Exception as e:
        print(f"ERROR: Could not connect to {CAN_INTERFACE}")
        print(f"Make sure interface is up:")
        print(f"  sudo ip link set {CAN_INTERFACE} up type can bitrate 500000")
        print(f"Details: {e}")
        sys.exit(1)

    last_rpm     = 0
    last_print   = time.time()
    rpm_readings = []

    while running:
        try:
            # recv() blocks until a frame arrives or timeout
            # timeout=1.0 means wait max 1 second for a frame
            msg = bus.recv(timeout=1.0)

            if msg is None:
                # No frame received within timeout
                print("WARNING: No frames received - check OBD2 connection")
                continue

            frame_count += 1

            # Only process RPM frames
            if msg.arbitration_id == RPM_FRAME_ID:
                rpm, raw, b2, b3 = decode_rpm(msg.data)
                rpm_readings.append(rpm)

                # Print update every 0.5 seconds to avoid flooding terminal
                now = time.time()
                if now - last_print >= 0.5:
                    # Calculate average RPM over last readings
                    avg_rpm = sum(rpm_readings) / len(rpm_readings)
                    rpm_readings = []  # reset buffer

                    # Build RPM bar visualization
                    # Max RPM for Camaro V6 is 7000
                    max_rpm   = 7000
                    bar_width = 30
                    filled    = int((avg_rpm / max_rpm) * bar_width)
                    bar       = "█" * filled + "░" * (bar_width - filled)

                    # Clear line and print update
                    elapsed = now - start_time
                    print(
                        f"\r  RPM: {avg_rpm:6.0f} "
                        f"[{bar}] "
                        f"| raw=0x{raw:04X} "
                        f"| b2=0x{b2:02X} b3=0x{b3:02X} "
                        f"| frames={frame_count} "
                        f"| {elapsed:.0f}s",
                        end='',
                        flush=True
                    )

                    last_rpm   = avg_rpm
                    last_print = now

        except can.CanError as e:
            print(f"\nCAN error: {e}")
            break

        except Exception as e:
            print(f"\nUnexpected error: {e}")
            break

    # Shutdown
    elapsed = time.time() - start_time
    bus.shutdown()

    print()
    print()
    print("=" * 50)
    print(f"  Session summary")
    print(f"  Duration : {elapsed:.1f} seconds")
    print(f"  Frames   : {frame_count} total")
    print(f"  Rate     : {frame_count/elapsed:.0f} frames/sec")
    print(f"  Last RPM : {last_rpm:.0f}")
    print("=" * 50)

if __name__ == '__main__':
    main()