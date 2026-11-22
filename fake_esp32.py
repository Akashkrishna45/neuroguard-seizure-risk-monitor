import time
import random
import math
import csv

OUTPUT_FILE = "live_sensor_data.csv"

def simulate_sensors():
    """Generate fake sensor data like ESP32 would"""
    t = time.time()
    
    # Heart rate with variation
    hr = 75 + 10 * math.sin(2 * math.pi * 0.1 * t) + random.gauss(0, 3)
    hr = max(60, min(160, hr))
    
    # SpO2
    spo2 = 98 + random.gauss(0, 0.8)
    spo2 = max(90, min(100, spo2))
    
    # Motion
    motion = abs(random.gauss(0, 2000))
    
    # Fall (rare)
    fall = 1 if random.random() < 0.01 else 0
    
    # EEG
    alpha = 100 * math.sin(2 * math.pi * 10 * t)
    beta = 40 * math.sin(2 * math.pi * 20 * t)
    theta = 60 * math.sin(2 * math.pi * 6 * t)
    eeg = alpha + beta + theta + random.gauss(0, 30)
    
    # Occasional spikes
    if random.random() < 0.05:
        eeg += random.uniform(300, 600)
    
    # Risk calculation
    nri = 0
    if hr > 120: nri += 40
    elif hr > 100: nri += 20
    if spo2 < 90: nri += 30
    elif spo2 < 95: nri += 15
    if motion > 15000: nri += 30
    elif motion > 8000: nri += 15
    if fall: nri += 10
    if abs(eeg) > 400: nri += 20
    
    risk = 2 if nri >= 70 else 1 if nri >= 30 else 0
    wave = "Alpha" if abs(alpha) > abs(beta) else "Beta"
    
    return {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "heart_rate": round(hr, 1),
        "spo2": round(spo2, 1),
        "accel": round(random.uniform(0.9, 1.1), 2),
        "motion": int(motion),
        "fall": fall,
        "eeg": round(eeg, 1),
        "dominant_wave": wave,
        "risk": risk
    }

def main():
    # Create CSV with headers
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'timestamp', 'heart_rate', 'spo2', 'accel',
            'motion', 'fall', 'eeg', 'dominant_wave', 'risk'
        ])
        writer.writeheader()
    
    print("🧠 NeuroGuard Fake ESP32 Running...")
    print("Generating sensor data every 2 seconds")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            data = simulate_sensors()
            
            with open(OUTPUT_FILE, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                writer.writerow(data)
            
            print(f"HR:{data['heart_rate']} SpO2:{data['spo2']} "
                  f"EEG:{data['eeg']:.1f} Risk:{data['risk']} [{data['dominant_wave']}]")
            
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\nStopped.")
            break

if __name__ == "__main__":
    main()