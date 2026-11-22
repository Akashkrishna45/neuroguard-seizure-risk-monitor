# NeuroGuard AI: Predictive Seizure Risk Assessment

A real-time wearable-style monitoring system that tracks physiological signals and estimates a patient's seizure risk, alerting caregivers before a situation becomes critical.

## Overview

Seizures are unpredictable, and caregivers often have little or no warning. NeuroGuard AI uses an ESP32 edge node to continuously acquire multiple biosignals, scores the patient's current risk, and notifies caregivers automatically.

## Features

- Real-time acquisition of **PPG heart rate, pulse oximetry (SpO₂), tri-axial accelerometry, EEG and GPS location** on an ESP32 edge node
- **Hybrid risk engine** combining a threshold-based scoring algorithm with a supervised machine learning classifier
- Three-level risk grading: **SAFE**, **WARNING** and **CRITICAL**
- **Live dashboard** with neuro-risk forecasting
- **Patient-specific baseline calibration** to reduce false alarms
- **Automated caregiver alerts** when risk escalates

## System Architecture

1. **Sensing layer:** PPG/SpO₂, accelerometer, EEG and GPS inputs
2. **Edge node:** ESP32 acquires and pre-processes the signals in real time
3. **Risk engine:** threshold-based scoring plus a supervised ML classifier
4. **Dashboard and alerts:** live visualization, risk forecasting and caregiver notifications

## Risk Levels

| Level | Meaning |
|---|---|
| SAFE | Signals are within the patient's calibrated baseline |
| WARNING | Early deviations detected; heightened monitoring |
| CRITICAL | High seizure risk; caregiver alert triggered |

## Tech Stack

- **Hardware:** ESP32, PPG/pulse oximetry sensor, tri-axial accelerometer, EEG input, GPS module
- **Firmware:** C/C++ (Arduino framework)
- **Software:** Python, machine learning classifier, web-based live dashboard

## How It Works

1. The ESP32 samples heart rate, SpO₂, motion, EEG and location in real time.
2. The patient's baseline is calibrated so alerts are personalized.
3. A threshold-based algorithm and a supervised ML classifier each contribute to a risk score.
4. The score is mapped to SAFE, WARNING or CRITICAL.
5. The dashboard updates live, forecasts neuro-risk, and caregivers are alerted automatically when risk rises.

## My Role

Solo project built at HowNwhy Education. I handled hardware integration, firmware, risk-scoring algorithm, ML classifier, dashboard and alert system end to end.

## Future Work

- Validation on larger datasets
- Mobile app for caregivers
- On-device (TinyML) inference

## Disclaimer

This is a research and educational prototype, **not a certified medical device**. It must not be used for clinical diagnosis or treatment decisions.

## Author

**Akash Krishna**
ECE Graduate | Embedded Systems | Edge AI
[LinkedIn](https://linkedin.com/in/akash-krishna-729685343) | akashkrishna221@gmail.com
