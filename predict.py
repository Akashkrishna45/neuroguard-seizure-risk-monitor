import joblib
import pandas as pd

model = joblib.load("neuroguard_model.pkl")

print("NeuroGuard AI")

hr = float(input("Heart Rate: "))
spo2 = float(input("SpO2: "))
motion = float(input("Motion: "))
fall = int(input("Fall (0/1): "))

patient = pd.DataFrame(
    [[hr, spo2, motion, fall]],
    columns=["HeartRate", "SpO2", "Motion", "Fall"]
)

prediction = model.predict(patient)

print("\nRisk Level:", prediction[0])