import pandas as pd
import random

data = []

for _ in range(1000):

    hr = random.randint(60, 160)
    spo2 = random.randint(80, 100)
    motion = round(random.uniform(0.0, 3.0), 2)
    fall = random.choice([0, 1])

    score = 0

    if hr > 120:
        score += 40
    elif hr > 100:
        score += 20

    if spo2 < 90:
        score += 30
    elif spo2 < 95:
        score += 15

    if motion > 1.5:
        score += 30
    elif motion > 0.8:
        score += 15

    if fall == 1:
        score += 10

    if score >= 70:
        risk = "CRITICAL"
    elif score >= 30:
        risk = "WARNING"
    else:
        risk = "SAFE"

    data.append([hr, spo2, motion, fall, risk])

df = pd.DataFrame(
    data,
    columns=["HeartRate", "SpO2", "Motion", "Fall", "Risk"]
)

df.to_csv("neuroguard_dataset_1000.csv", index=False)

print("Dataset generated successfully!")