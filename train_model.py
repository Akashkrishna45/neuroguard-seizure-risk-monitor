import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv("neuroguard_dataset_1000.csv")

X = df[['HeartRate', 'SpO2', 'Motion', 'Fall']]
y = df['Risk']

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print(f"\nAccuracy: {accuracy*100:.2f}%\n")

print(classification_report(y_test, y_pred))

joblib.dump(model, "neuroguard_model.pkl")

print("Model saved successfully!")