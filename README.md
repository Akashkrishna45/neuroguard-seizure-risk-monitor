# NeuroGuard AI: Predictive Seizure Risk Assessment

A real-time, wearable-style monitoring system that tracks physiological signals
and estimates a patient's seizure risk, alerting caregivers before a situation
becomes critical.

## Overview
Seizures are unpredictable, and caregivers often have little or no warning.
NeuroGuard AI continuously reads multiple biosignals on an ESP32 edge node,
scores the patient's current risk, and notifies caregivers automatically.

## Features
- Real-time acquisition of **PPG heart rate, pulse oximetry (SpO₂),
  tri-axial accelerometry, EEG and GPS location**
- **Hybrid risk engine**: a threshold-based scoring algorithm combined with a
  supervised ML classifier
- Three-level risk grading: **SAFE / WARNING / CRITICAL**
- **Live dashboard** with neuro-risk forecasting
- **Patient-specific baseline calibration** to reduce false alarms
- **Automated caregiver alerts** with patient location

## System Architecture
[Insert block diagram: Sensors → ESP32 → Wi-Fi → Backend/ML → Dashboard → Alerts]

1. **Sensing layer**: PPG/SpO₂ sensor, accelerometer, EEG front-end, GPS module
2. **Edge node**: ESP32 samples and pre-processes the signals
3. **Risk engine**: threshold scoring + ML classifier
4. **Dashboard and alerts**: live visualization, forecasting, caregiver notification

## Hardware
| Component | Purpose |
|---|---|
| ESP32 | Edge processing and connectivity |
| [PPG/SpO₂ sensor, e.g. MAX30102] | Heart rate and oxygen saturation |
| [Accelerometer, e.g. MPU6050] | Motion and fall/convulsion detection |
| [EEG module] | Brain activity |
| [GPS module] | Patient location |

## Software and Tech Stack
ESP32 firmware (C/C++ / Arduino), Python, scikit-learn, [dashboard framework], [communication protocol, e.g. MQTT/HTTP]

## How It Works
1. Signals are sampled in real time on the ESP32.
2. Features such as heart rate variability, SpO₂ drops and movement
   patterns are extracted.
3. The threshold algorithm and ML model each contribute to a risk score.
4. The score is mapped to SAFE, WARNING or CRITICAL.
5. The dashboard updates live and caregivers are alerted when risk rises.

## Results
- [Model accuracy / precision / recall: add your numbers]
- [Alert latency]
- [Dataset or testing method]

## Getting Started
```bash
git clone https://github.com/<your-username>/neuroguard-ai.git
cd neuroguard-ai
pip install -r requirements.txt
```
- Wiring diagram: `hardware/wiring.png`
- Flash the firmware in `firmware/` to the ESP32
- Run the dashboard: `python software/app.py`

## My Role
Solo project: hardware design, firmware, ML model, dashboard and
alert system, built at HowNwhy Education.

## Future Work
- Larger clinical-style datasets and validation
- Mobile app for caregivers
- On-device (TinyML) inference

## Disclaimer
This is a research and educational prototype, not a certified medical device.
It must not be used for clinical diagnosis or treatment decisions.

## Author
**Akash Krishna**: [LinkedIn](https://linkedin.com/in/akash-krishna-729685343) | akashkrishna221@gmail.com
