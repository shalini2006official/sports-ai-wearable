import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ===========================
# Load Dataset
# ===========================

data = pd.read_excel("dataset/sports_ai_dataset.xlsx")

print("Dataset Loaded Successfully!\n")

# ===========================
# Encode Categorical Columns
# ===========================

activity_encoder = LabelEncoder()
posture_encoder = LabelEncoder()

data["activity"] = activity_encoder.fit_transform(data["activity"])
data["posture"] = posture_encoder.fit_transform(data["posture"])

# ===========================
# Features & Target
# ===========================

X = data[
    [
        "heart_rate",
        "spo2",
        "steps",
        "activity",
        "temperature",
        "cadence",
        "stride_length",
        "posture",
    ]
]

y = data["fatigue_score"]

# ===========================
# Train Test Split
# ===========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

print("Training Samples :", len(X_train))
print("Testing Samples  :", len(X_test))

# ===========================
# Train Model
# ===========================

model = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
)

model.fit(X_train, y_train)

print("\nModel Trained Successfully!")

# ===========================
# Predictions
# ===========================

predictions = model.predict(X_test)

# ===========================
# Evaluation
# ===========================

mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print("\n==============================")
print("MODEL EVALUATION")
print("==============================")
print(f"Mean Absolute Error : {mae:.2f}")
print(f"Mean Squared Error : {mse:.2f}")
print(f"R2 Score           : {r2:.4f}")

# ===========================
# Save Model
# ===========================

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/fatigue_model.pkl")
joblib.dump(activity_encoder, "models/activity_encoder.pkl")
joblib.dump(posture_encoder, "models/posture_encoder.pkl")

print("\nModel Saved Successfully!")
print("Location : models/fatigue_model.pkl")

# ===========================
# Feature Importance
# ===========================

importance = pd.DataFrame(
    {
        "Feature": X.columns,
        "Importance": model.feature_importances_,
    }
)

importance = importance.sort_values(
    by="Importance",
    ascending=False,
)

print("\n==============================")
print("FEATURE IMPORTANCE")
print("==============================")
print(importance)

print("\nFatigue AI Training Completed Successfully!")