import pandas as pd
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier

df = pd.read_csv("neuroguard_dataset_1000.csv")

X = df[['HeartRate', 'SpO2', 'Motion', 'Fall']]
y = df['Risk']

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X, y)

importance = model.feature_importances_

plt.figure(figsize=(8,5))
plt.bar(X.columns, importance)

plt.xlabel("Features")
plt.ylabel("Importance")
plt.title("Feature Importance")

plt.show()