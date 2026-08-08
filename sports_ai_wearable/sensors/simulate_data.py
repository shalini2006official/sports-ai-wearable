import random
import time
import json
import math

# ─── Activity Detection from Acceleration ────────────────────
def detect_activity(ax, ay, az):
    magnitude = math.sqrt(ax**2 + ay**2 + az**2)
    if magnitude > 2.5:   return "Jumping"
    elif magnitude > 1.8: return "Running"
    elif magnitude > 1.2: return "Walking"
    else:                  return "Resting"

# ─── Simulate Wrist Data (ESP32 #1) ──────────────────────────
# Has: MPU6050 + MAX30102
def simulate_wrist():
    ax = round(random.uniform(-2.0, 2.0), 2)
    ay = round(random.uniform(-2.0, 2.0), 2)
    az = round(random.uniform(-2.0, 2.0), 2)
    return {
        "device":      "wrist",
        "esp32_id":    1,
        "heart_rate":  random.randint(60, 180),
        "spo2":        random.randint(95, 100),       # Blood oxygen %
        "steps":       random.randint(0, 5),
        "accel_x":     ax,
        "accel_y":     ay,
        "accel_z":     az,
        "activity":    detect_activity(ax, ay, az),
        "temperature": round(random.uniform(36.0, 37.5), 1),  # Body temp
        "timestamp":   time.strftime("%H:%M:%S")
    }

# ─── Simulate Waist Data (ESP32 #2) ──────────────────────────
# Has: MPU6050 only — posture & core movement
def simulate_waist():
    ax = round(random.uniform(-1.5, 1.5), 2)
    ay = round(random.uniform(-1.5, 1.5), 2)
    az = round(random.uniform(-1.5, 1.5), 2)
    # Spine tilt angle from vertical
    spine_tilt = round(math.degrees(math.atan2(
        math.sqrt(ax**2 + ay**2), abs(az))), 1)
    return {
        "device":       "waist",
        "esp32_id":     2,
        "accel_x":      ax,
        "accel_y":      ay,
        "accel_z":      az,
        "spine_tilt":   spine_tilt,
        "posture":      "Good" if spine_tilt < 15 else ("Fair" if spine_tilt < 30 else "Bad"),
        "core_activity": detect_activity(ax, ay, az),
        "timestamp":    time.strftime("%H:%M:%S")
    }

# ─── Simulate Ankle Data (ESP32 #3) ──────────────────────────
# Has: MPU6050 only — steps & stride
def simulate_ankle():
    ax = round(random.uniform(-2.5, 2.5), 2)
    ay = round(random.uniform(-2.5, 2.5), 2)
    az = round(random.uniform(-2.5, 2.5), 2)
    magnitude = math.sqrt(ax**2 + ay**2 + az**2)
    stride = round(random.uniform(0.4, 0.9), 2) if magnitude > 1.5 else 0.0
    return {
        "device":       "ankle",
        "esp32_id":     3,
        "accel_x":      ax,
        "accel_y":      ay,
        "accel_z":      az,
        "steps":        random.randint(0, 3),
        "stride_length": stride,               # meters
        "cadence":      random.randint(0, 5),  # steps per second
        "foot_activity": detect_activity(ax, ay, az),
        "timestamp":    time.strftime("%H:%M:%S")
    }

# ─── Combine All 3 Devices ───────────────────────────────────
def generate_all_sensor_data():
    wrist = simulate_wrist()
    waist = simulate_waist()
    ankle = simulate_ankle()

    # Save to shared data files so dashboard can read them
    with open("../data/wrist_data.json", "w") as f:
        json.dump(wrist, f)
    with open("../data/waist_data.json", "w") as f:
        json.dump(waist, f)
    with open("../data/ankle_data.json", "w") as f:
        json.dump(ankle, f)

    return wrist, waist, ankle

if __name__ == "__main__":
    print("✅ Simulating 3 ESP32 devices... Press Ctrl+C to stop.\n")
    print("📡 ESP32 #1 — Wrist  (MPU6050 + MAX30102)")
    print("📡 ESP32 #2 — Waist  (MPU6050)")
    print("📡 ESP32 #3 — Ankle  (MPU6050)\n")

    while True:
        wrist, waist, ankle = generate_all_sensor_data()

        print(f"─── {time.strftime('%H:%M:%S')} ───────────────────────")
        print(f"⌚ WRIST  | HR: {wrist['heart_rate']} bpm | SpO2: {wrist['spo2']}% | Temp: {wrist['temperature']}°C | Activity: {wrist['activity']}")
        print(f"🎽 WAIST  | Tilt: {waist['spine_tilt']}° | Posture: {waist['posture']} | Core: {waist['core_activity']}")
        print(f"👟 ANKLE  | Steps: {ankle['steps']} | Stride: {ankle['stride_length']}m | Cadence: {ankle['cadence']}/s | Foot: {ankle['foot_activity']}")
        print()

        time.sleep(1)