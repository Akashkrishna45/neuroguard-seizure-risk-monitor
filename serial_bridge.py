import serial
import csv
import time
import random
import math

SERIAL_PORT = "COM3"  # Change to your port
BAUD_RATE = 115200
OUTPUT_FILE = "live_sensor_data.csv"
HARDWARE_MODE = False  # Set True when ESP32 connected

def simulate_eeg():
    """Generate realistic EEG signal"""
    t = time.time()
    alpha = 100 * math.sin(2 * math.pi * 10 * t)
    beta = 40 * math.sin(2 * math.pi * 20 * t)
    theta = 60 * math.sin(2 * math.pi * 6 * t)
    noise = random.uniform(-30, 30)
    
    # Occasional spikes (5% chance)
    if random.random() < 0.05:
        spike = random.uniform(300, 600)
        return alpha + beta + theta + noise + spike, "Abnormal"
    
    eeg = alpha + beta + theta + noise
    waves = {"Alpha": abs(alpha), "Beta": abs(beta), "Theta": abs(theta)}
    dominant = max(waves, key=waves.get)
    
    return eeg, dominant

def calculate_risk(hr, spo2, motion, fall, eeg):
    """Calculate NRI risk score"""
    nri = 0
    
    if hr > 120: nri += 40
    elif hr > 100: nri += 20
    if spo2 < 90: nri += 30
    elif spo2 < 95: nri += 15
    if motion > 15000: nri += 30
    elif motion > 8000: nri += 15
    if fall == 1: nri += 10
    if abs(eeg) > 400: nri += 20
    
    if nri >= 70: return 2  # CRITICAL
    elif nri >= 30: return 1  # WARNING
    return 0  # SAFE

def main():
    ser = None
    
    # Try hardware connection
    if HARDWARE_MODE:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            print(f"✅ Hardware connected: {SERIAL_PORT}")
        except Exception as e:
            print(f"⚠️ Hardware failed: {e}")
            print("🔄 Falling back to simulation...")
    
    # Create CSV with headers
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'heart_rate', 'spo2', 'accel', 
                        'motion', 'fall', 'eeg', 'dominant_wave', 'risk'])
    
    print("🚀 NeuroGuard Serial Bridge Running...")
    print("Format: HR, SpO2, Motion, Fall, EEG, Wave, Risk")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            if ser and ser.in_waiting:
                # Read from hardware
                line = ser.readline().decode().strip()
                values = line.split(',')
                
                if len(values) >= 6:
                    hr = float(values[0])
                    spo2 = float(values[1])
                    accel = float(values[2])
                    motion = float(values[3])
                    fall = int(values[4])
                    eeg, wave = simulate_eeg()  # EEG still simulated until BioAmp arrives
                    risk = calculate_risk(hr, spo2, motion, fall, eeg)
                    
                    print(f"📟 HARDWARE | HR:{hr:.1f} SpO2:{spo2:.1f} Risk:{risk}")
            else:
                # SIMULATION MODE
                hr = 75 + random.uniform(-5, 20)  # Varies 70-95
                spo2 = 98 + random.uniform(-3, 1)  # Varies 95-99
                accel = random.uniform(0.9, 1.1)
                motion = random.uniform(1000, 8000)
                fall = 1 if random.random() < 0.02 else 0  # 2% fall chance
                eeg, wave = simulate_eeg()
                risk = calculate_risk(hr, spo2, motion, fall, eeg)
                
                print(f"💻 SIM | HR:{hr:.1f} SpO2:{spo2:.1f} EEG:{eeg:.1f} Risk:{risk} [{wave}]")
            
            # Write to CSV (shared with Streamlit)
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, round(hr,1), round(spo2,1), 
                                round(accel,2), int(motion), fall, 
                                round(eeg,1), wave, risk])
            
            time.sleep(2)  # Match Streamlit refresh rate
            
        except KeyboardInterrupt:
            print("\n🛑 Stopping...")
            if ser: ser.close()
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()