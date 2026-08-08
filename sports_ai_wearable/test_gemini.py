from ai.gemini_coach import generate_coaching_advice

sample = {
    "heart_rate": 170,
    "spo2": 97,
    "fatigue": 63,
    "performance": 82,
    "activity": "Sprinting",
    "steps": 5400,
    "cadence": 178,
    "stride_length": 1.35,
    "temperature": 28
}

print(generate_coaching_advice(sample))