
import csv
import os
import socket
import threading
import time
from datetime import datetime

# ============== CONFIG ==============
WIFI_HOST = "0.0.0.0"
WIFI_PORT = 5000

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(SCRIPT_DIR, "live_sensor_data.csv")

CSV_COLUMNS = [
    "timestamp", "heart_rate", "spo2", "motion", "fall",
    "eeg", "dominant_wave", "risk", "gps_lat", "gps_lon", "gps_fix", "gps_sats"
]

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

# ============== CLIENT HANDLER ==============
def handle_client(conn, addr):
    print(f"ESP32 connected from {addr}")
    buffer = ""
    packet_count = 0

    try:
        while True:
            # NO TIMEOUT - block forever waiting for data
            try:
                data = conn.recv(4096)
            except:
                break

            if not data:
                print(f"ESP32 {addr} closed connection")
                break

            buffer += data.decode("utf-8", errors="ignore")

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
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
                              f"GPS:{lat},{lon} | SATS:{sats} | CSV:{"OK" if success else "FAIL"}")

                        try:
                            conn.sendall(b'OK\n')
                        except:
                            pass
                    else:
                        print(f"Bad CSV ({len(parts)} fields): {line[:60]}")

                except Exception as e:
                    print(f"Process error: {e}")

    except ConnectionResetError:
        print(f"ESP32 reset connection {addr}")
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        try:
            conn.close()
        except:
            pass
        print(f"ESP32 disconnected {addr} | Total packets: {packet_count}")
        print("\nWaiting for ESP32 reconnection...\n")

# ============== SERVER ==============
def run_server():
    print("=" * 70)
    print("  NeuroGuard AI - WiFi Data Bridge (No Timeout)")
    print("=" * 70)
    print(f"  Your IP:      10.14.20.89")
    print(f"  Listening on:   {WIFI_HOST}:{WIFI_PORT}")
    print(f"  CSV output:   {CSV_FILE}")
    print("=" * 70)

    init_csv()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((WIFI_HOST, WIFI_PORT))
    s.listen(5)

    print("\nWaiting for ESP32...\n")

    try:
        while True:
            try:
                s.settimeout(60.0)  # 60 second timeout on accept only
                conn, addr = s.accept()
                handle_client(conn, addr)
            except socket.timeout:
                print("No ESP32 connection in 60s, still listening...")
                continue
    except KeyboardInterrupt:
        print("\nStopping...")
        s.close()

if __name__ == "__main__":
    run_server()