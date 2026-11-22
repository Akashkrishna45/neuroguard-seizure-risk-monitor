import csv
import os
import sys
import serial
import serial.tools.list_ports
import time
from datetime import datetime

# ============== CONFIG ==============
BAUD_RATE = 115200
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "live_sensor_data.csv")

CSV_COLUMNS = [
    "timestamp", "heart_rate", "spo2", "motion", "fall",
    "eeg", "dominant_wave", "risk", "gps_lat", "gps_lon", "gps_fix", "gps_sats"
]

# ============== FIND ESP32 PORT ==============
def find_esp32_port():
    """Auto-detect ESP32 COM port. Returns port name or None."""
    ports = serial.tools.list_ports.comports()
    for p in ports:
        # Common ESP32 USB descriptors
        if any(x in (p.description or "").upper() for x in ["CP210", "CH340", "USB-SERIAL", "UART", "ESP32"]):
            return p.device
        if any(x in (p.manufacturer or "").upper() for x in ["SILICON LABS", "WCH", "ESPRESSIF"]):
            return p.device
    # Fallback: list all and let user pick if multiple
    return None

def select_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found! Is the ESP32 connected?")
        sys.exit(1)
    
    print("\nAvailable serial ports:")
    for i, p in enumerate(ports):
        print(f"  [{i}] {p.device} - {p.description} ({p.manufacturer or 'Unknown'})")
    
    auto = find_esp32_port()
    if auto and len(ports) == 1:
        print(f"\nAuto-selected: {auto}")
        return auto
    
    if auto:
        print(f"\nAuto-detected ESP32 at: {auto}")
        use = input(f"Use {auto}? [Y/n]: ").strip().lower()
        if use in ("", "y", "yes"):
            return auto
    
    idx = input("\nEnter port number: ").strip()
    try:
        return ports[int(idx)].device
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)

# ============== CSV ==============
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(CSV_COLUMNS)
        print(f"Created: {CSV_FILE}")

def write_csv_row(hr, spo2, accel, fall, eeg, wave, risk, lat, lon, fix, sats):
    try:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            round(float(hr), 1),
            round(float(spo2), 1),
            round(float(accel), 4),
            int(fall),
            round(float(eeg), 3),
            str(wave),
            str(risk),
            str(lat),
            str(lon),
            int(fix),
            int(sats)
        ]
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(row)
        return True
    except Exception as e:
        print(f"CSV WRITE ERROR: {e}")
        return False

# ============== MAIN ==============
def run_bridge():
    port = select_port()
    
    print("\n" + "=" * 70)
    print("  NeuroGuard AI - Serial Data Bridge")
    print("=" * 70)
    print(f"  Port:       {port}")
    print(f"  Baud:       {BAUD_RATE}")
    print(f"  CSV output: {CSV_FILE}")
    print("=" * 70)

    init_csv()

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        print(f"\nOpened {port} @ {BAUD_RATE} baud")
        print("Waiting for ESP32 data...\n")
    except serial.SerialException as e:
        print(f"Failed to open {port}: {e}")
        sys.exit(1)

    packet_count = 0
    buffer = ""

    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode("utf-8", errors="ignore")
                buffer += data

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line or line.startswith("=") or line.startswith("  "):
                        # Skip debug/header lines from ESP32 boot
                        continue

                    try:
                        parts = line.split(",")
                        if len(parts) >= 11:
                            hr = parts[0]
                            spo2 = parts[1]
                            accel = parts[2]
                            fall = parts[3]
                            eeg = parts[4]
                            wave = parts[5]
                            risk = parts[6]
                            lat = parts[7]
                            lon = parts[8]
                            fix = parts[9]
                            sats = parts[10]

                            success = write_csv_row(hr, spo2, accel, fall, eeg, wave, risk, lat, lon, fix, sats)
                            packet_count += 1

                            print(f"[{packet_count:3d}] {risk:8} | HR:{float(hr):5.1f} SpO2:{float(spo2):5.1f} "
                                  f"ACCEL:{float(accel):7.4f} FALL:{fall} EEG:{float(eeg):6.3f} WAVE:{wave:8} | "
                                  f"GPS:{lat},{lon} | SATS:{sats} | CSV:{'OK' if success else 'FAIL'}")

                        else:
                            print(f"Bad CSV ({len(parts)} fields): {line[:60]}")

                    except Exception as e:
                        print(f"Process error: {e} | Line: {line[:60]}")

            time.sleep(0.01)  # Small delay to prevent CPU spinning

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ser.close()
        print(f"Serial closed. Total packets: {packet_count}")

if __name__ == "__main__":
    run_bridge()