from report_generator import generate_report

sensor = {
    "heart_rate": 168,
    "spo2": 97,
    "fatigue": 64,
    "performance": 90,
}

analysis = """
Body Posture:
Excellent

Balance:
Good

Footwork:
Needs slight improvement
"""

pdf = generate_report(sensor, analysis)

print(pdf)