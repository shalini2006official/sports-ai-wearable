import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

model = joblib.load(os.path.join(MODEL_DIR, "fatigue_model.pkl"))
activity_encoder = joblib.load(os.path.join(MODEL_DIR, "activity_encoder.pkl"))
posture_encoder = joblib.load(os.path.join(MODEL_DIR, "posture_encoder.pkl"))


def predict_fatigue(
    heart_rate,
    spo2,
    steps,
    activity,
    temperature,
    cadence,
    stride_length,
    posture,
):
    try:
        activity = activity_encoder.transform([activity])[0]
    except ValueError:
        activity = activity_encoder.transform(["Idle"])[0]

    try:
        posture = posture_encoder.transform([posture])[0]
    except ValueError:
        posture = posture_encoder.transform(["Good"])[0]

    sample = pd.DataFrame(
        [[
            heart_rate,
            spo2,
            steps,
            activity,
            temperature,
            cadence,
            stride_length,
            posture,
        ]],
        columns=[
            "heart_rate",
            "spo2",
            "steps",
            "activity",
            "temperature",
            "cadence",
            "stride_length",
            "posture",
        ],
    )

    prediction = model.predict(sample)[0]
    return round(float(prediction), 2)


if __name__ == "__main__":
    fatigue = predict_fatigue(
        heart_rate=135,
        spo2=97,
        steps=6500,
        activity="Running",
        temperature=37.2,
        cadence=168,
        stride_length=1.35,
        posture="Good",
    )

    print("Predicted Fatigue:", fatigue)