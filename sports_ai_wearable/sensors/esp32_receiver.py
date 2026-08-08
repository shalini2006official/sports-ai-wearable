"""
esp32_receiver.py
─────────────────────────────────────────────────────────────
Receives REAL data from 3 ESP32 devices over WiFi.
Run this when hardware arrives — replaces simulate_data.py

ESP32 devices send JSON data to this Python server via HTTP POST.

ESP32 #1 (Wrist)  → POST http://YOUR_LAPTOP_IP:5000/wrist
ESP32 #2 (Waist)  → POST http://YOUR_LAPTOP_IP:5000/waist
ESP32 #3 (Ankle)  → POST http://YOUR_LAPTOP_IP:5000/ankle
─────────────────────────────────────────────────────────────
"""

from flask import Flask, request, jsonify
import json
import time
import os

app = Flask(__name__)

DATA_DIR = "../data"
os.makedirs(DATA_DIR, exist_ok=True)

# ─── Wrist Endpoint (ESP32 #1) ────────────────────────────────
@app.route("/wrist", methods=["POST"])
def receive_wrist():
    """
    Receives from ESP32 #1:
    - Heart rate (MAX30102)
    - SpO2 blood oxygen (MAX30102)
    - Acceleration X,Y,Z (MPU6050)
    - Steps, Activity, Temperature
    """
    data = request.get_json()
    data["timestamp"] = time.strftime("%H:%M:%S")
    data["device"] = "wrist"

    with open(f"{DATA_DIR}/wrist_data.json", "w") as f:
        json.dump(data, f)

    print(f"⌚ WRIST  | HR: {data.get('heart_rate','?')} bpm | SpO2: {data.get('spo2','?')}% | Activity: {data.get('activity','?')}")
    return jsonify({"status": "ok"})

# ─── Waist Endpoint (ESP32 #2) ────────────────────────────────
@app.route("/waist", methods=["POST"])
def receive_waist():
    """
    Receives from ESP32 #2:
    - Acceleration X,Y,Z (MPU6050)
    - Spine tilt angle
    - Posture status
    - Core activity
    """
    data = request.get_json()
    data["timestamp"] = time.strftime("%H:%M:%S")
    data["device"] = "waist"

    with open(f"{DATA_DIR}/waist_data.json", "w") as f:
        json.dump(data, f)

    print(f"🎽 WAIST  | Tilt: {data.get('spine_tilt','?')}° | Posture: {data.get('posture','?')}")
    return jsonify({"status": "ok"})

# ─── Ankle Endpoint (ESP32 #3) ────────────────────────────────
@app.route("/ankle", methods=["POST"])
def receive_ankle():
    """
    Receives from ESP32 #3:
    - Acceleration X,Y,Z (MPU6050)
    - Steps count
    - Stride length
    - Cadence (steps/sec)
    - Foot activity
    """
    data = request.get_json()
    data["timestamp"] = time.strftime("%H:%M:%S")
    data["device"] = "ankle"

    with open(f"{DATA_DIR}/ankle_data.json", "w") as f:
        json.dump(data, f)

    print(f"👟 ANKLE  | Steps: {data.get('steps','?')} | Stride: {data.get('stride_length','?')}m")
    return jsonify({"status": "ok"})

# ─── Status Check ─────────────────────────────────────────────
@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "server": "running",
        "time": time.strftime("%H:%M:%S"),
        "message": "Sports AI Wearable receiver ready"
    })

if __name__ == "__main__":
    print("=" * 50)
    print("  Sports AI Wearable — ESP32 Receiver")
    print("=" * 50)
    print()
    print("📡 Waiting for ESP32 devices...")
    print()
    print("  ESP32 #1 Wrist → POST /wrist")
    print("  ESP32 #2 Waist → POST /waist")
    print("  ESP32 #3 Ankle → POST /ankle")
    print()
    print("  Upload arduino_code/wrist_esp32.ino  to ESP32 #1")
    print("  Upload arduino_code/waist_esp32.ino  to ESP32 #2")
    print("  Upload arduino_code/ankle_esp32.ino  to ESP32 #3")
    print()
    print("  Set LAPTOP_IP in each .ino file to your IP address")
    print()

    # Install flask if needed: pip install flask
    app.run(host="0.0.0.0", port=5000, debug=False)