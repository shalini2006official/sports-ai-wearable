"""
server.py
─────────────────────────────────────────────────────────────
Unified REST API for the Sports AI Wearable React dashboard.

- Keeps the existing ESP32 ingestion endpoints (POST /wrist, /waist, /ankle)
- Adds GET /api/sensors/live  -> one combined JSON payload for the frontend
- Adds GET /api/sessions      -> past session history
- If no real ESP32 has posted recently, automatically falls back to
  simulated values (same shape), so the frontend always has data to show.
- CORS enabled so a React app running on a different port/origin can call it.

Install:  pip install flask flask-cors
Run:      python server.py
Serves:   http://localhost:5000
─────────────────────────────────────────────────────────────
"""
import json
import math
import os
import random
import time
from matplotlib import path
import serial
import threading
from flask import Flask, jsonify, request
from flask_cors import CORS
from ai.predict import predict_fatigue
from database.database import init_db
from database.crud import save_session
from database.crud import get_all_sessions
from database.crud import get_latest_session
from ai.gemini_coach import generate_coaching_advice
from werkzeug.utils import secure_filename
from ai.frame_extractor import extract_frames
from ai.vision_coach import analyze_frames
from report_generator import generate_report
from flask import send_file
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

WRIST_FILE = os.path.join(DATA_DIR, "wrist_data.json")
WAIST_FILE = os.path.join(DATA_DIR, "waist_data.json")
ANKLE_FILE = os.path.join(DATA_DIR, "ankle_data.json")
HISTORY_FILE = os.path.join(DATA_DIR, "session_history.json")

app = Flask(__name__)
latest_ai_analysis = ""
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
init_db(app)
CORS(app)  # allow requests from a React dev server on a different origin

# Tracks the last time each device sent REAL data via POST
last_real_update = {"wrist": 0, "waist": 0, "ankle": 0}
REAL_DATA_TIMEOUT = 8  # seconds — if no POST within this window, use simulated values

# new code 
live_sensor = {
    "heart_rate": 0,
    "spo2": 98
}


def read_serial():
    global live_sensor

    ser = serial.Serial("COM5", 115200, timeout=1)

    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()

            if line.startswith("IR"):
                parts = line.split()

                # Example:
                # IR = 77088 BPM = 77 Beat = 0

                ir = int(parts[2])
                bpm = int(parts[5])

                live_sensor["heart_rate"] = bpm
                live_sensor["spo2"] = 98

        except Exception as e:
            print("Serial Error:", e)

            #end new code
# ─── Activity classification ──────────────────────────────────
def detect_activity(ax, ay, az):
    m = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
    if m > 2.5:
        return "Sprinting"
    if m > 1.8:
        return "Running"
    if m > 1.2:
        return "Walking"
    return "Idle"


# ─── Simulators (used only when no real ESP32 data is fresh) ──
def simulate_wrist():
    ax, ay, az = (round(random.uniform(-2.0, 2.0), 2) for _ in range(3))
    gx, gy, gz = (round(random.uniform(-40, 40), 1) for _ in range(3))
    return {
        "heart_rate": random.randint(65, 175),
        "spo2": random.randint(94, 100),
        "steps": random.randint(0, 5),
        "accel_x": ax, "accel_y": ay, "accel_z": az,
        "gyro_x": gx, "gyro_y": gy, "gyro_z": gz,
        "activity": detect_activity(ax, ay, az),
        "temperature": round(random.uniform(36.0, 37.5), 1),
    }


def simulate_waist():
    ax, ay, az = (round(random.uniform(-1.5, 1.5), 2) for _ in range(3))
    tilt = round(math.degrees(math.atan2(math.sqrt(ax ** 2 + ay ** 2), abs(az) or 0.01)), 1)
    return {
        "accel_x": ax, "accel_y": ay, "accel_z": az,
        "spine_tilt": tilt,
        "posture": "Good" if tilt < 15 else ("Fair" if tilt < 30 else "Bad"),
    }


def simulate_ankle():
    ax, ay, az = (round(random.uniform(-2.5, 2.5), 2) for _ in range(3))
    m = math.sqrt(ax ** 2 + ay ** 2 + az ** 2)
    return {
        "accel_x": ax, "accel_y": ay, "accel_z": az,
        "steps": random.randint(0, 3),
        "stride_length": round(random.uniform(0.4, 0.9), 2) if m > 1.5 else 0.0,
        "cadence": random.randint(0, 5),
    }


def read_or_simulate(device, filepath, sim_fn):
    fresh = (time.time() - last_real_update[device]) < REAL_DATA_TIMEOUT
    if fresh and os.path.exists(filepath):
        try:
            with open(filepath) as f:
                return json.load(f), True  # True = real data
        except Exception:
            pass
    return sim_fn(), False  # False = simulated


# ─── AI coaching (same logic as ai/coaching.py, JSON-shaped) ──
def analyze(hr, steps, activity, max_hr=190):
    hr_zone = (hr / max_hr) * 100
    advice = []
    level = "info"
    if hr_zone > 90:
        advice.append({"priority": "critical", "text": "Heart rate critically high — stop and rest immediately."})
        level = "critical"
    elif hr_zone > 75:
        advice.append({"priority": "warning", "text": "High intensity — monitor your breathing closely."})
        level = "warning"
    elif hr_zone > 50:
        advice.append({"priority": "info", "text": "Optimal training zone — keep this pace."})
    else:
        advice.append({"priority": "info", "text": "Low intensity — you have room to push harder."})

    if activity == "Running" and hr > 160:
        advice.append({"priority": "warning", "text": "Slow your running pace to avoid overexertion."})
    elif activity == "Idle" and hr > 100:
        advice.append({"priority": "warning", "text": "Heart rate is high even at rest — take a longer break."})
    elif activity == "Sprinting":
        advice.append({"priority": "warning", "text": "High-impact activity — land softly to protect joints."})

    if steps > 500:
        advice.append({"priority": "info", "text": f"{steps} steps so far — stay hydrated."})

    return advice, round(hr_zone, 1), level


# ─── ESP32 ingestion endpoints (unchanged behavior) ────────────

@app.route("/wrist", methods=["POST"])
def post_wrist():
    data = request.get_json(force=True)
    data["timestamp"] = time.strftime("%H:%M:%S")
    with open(WRIST_FILE, "w") as f:
        json.dump(data, f)
    last_real_update["wrist"] = time.time()
    return jsonify({"status": "ok"})


@app.route("/waist", methods=["POST"])
def post_waist():
    data = request.get_json(force=True)
    data["timestamp"] = time.strftime("%H:%M:%S")
    with open(WAIST_FILE, "w") as f:
        json.dump(data, f)
    last_real_update["waist"] = time.time()
    return jsonify({"status": "ok"})


@app.route("/ankle", methods=["POST"])
def post_ankle():
    data = request.get_json(force=True)
    data["timestamp"] = time.strftime("%H:%M:%S")
    with open(ANKLE_FILE, "w") as f:
        json.dump(data, f)
    last_real_update["ankle"] = time.time()
    return jsonify({"status": "ok"})


# ─── Combined live payload for the React dashboard ─────────────
@app.route("/api/sensors/live", methods=["GET"])
def live():
    wrist, wrist_real = read_or_simulate("wrist", WRIST_FILE, simulate_wrist)
    waist, waist_real = read_or_simulate("waist", WAIST_FILE, simulate_waist)
    ankle, ankle_real = read_or_simulate("ankle", ANKLE_FILE, simulate_ankle)

    # hr = wrist.get("heart_rate", 0)
    # spo2 = wrist.get("spo2", 0)
    hr = live_sensor["heart_rate"]
    spo2 = live_sensor["spo2"]
    steps = wrist.get("steps", 0)
    activity = wrist.get("activity", "Idle")
    advice, hr_zone, level = analyze(hr, steps, activity)

    fatigue = predict_fatigue(
    heart_rate=hr,
    spo2=spo2,
    steps=steps,
    activity=activity,
    temperature=wrist.get("temperature", 36.8),
    cadence=ankle.get("cadence", 0),
    stride_length=ankle.get("stride_length", 0.0),
    posture=waist.get("posture", "Good"),
)
    print("=" * 40)
    print("AI Prediction")
    print(f"Heart Rate : {hr}")
    print(f"SpO2       : {spo2}")
    print(f"Activity   : {activity}")
    print(f"Posture    : {waist.get('posture')}")
    print(f"Fatigue    : {fatigue}")
    print("=" * 40)
    performance = round(min(99, max(35, 100 - fatigue * 0.3 + (10 if 50 < hr_zone < 85 else -5))))

    payload = {
        "hr": hr,
        "spo2": spo2,
        "accel": {"x": wrist.get("accel_x", 0), "y": wrist.get("accel_y", 0), "z": wrist.get("accel_z", 0)},
        "gyro": {"x": wrist.get("gyro_x", 0), "y": wrist.get("gyro_y", 0), "z": wrist.get("gyro_z", 0)},
        "movement": round(math.sqrt(wrist.get("accel_x", 0) ** 2 + wrist.get("accel_y", 0) ** 2) * 10, 1),
        "activity": activity,
        "fatigue": fatigue,
        "performance": performance,
        "hr_zone_pct": hr_zone,
        "alert_level": level,
        "steps": steps,
        "temperature": wrist.get("temperature"),
        "posture": waist.get("posture"),
        "spine_tilt": waist.get("spine_tilt"),
        "stride_length": ankle.get("stride_length"),
        "cadence": ankle.get("cadence"),
        "ai_coach": advice,
        "sources": {
            "wrist": "live" if wrist_real else "simulated",
            "waist": "live" if waist_real else "simulated",
            "ankle": "live" if ankle_real else "simulated",
        },
        "timestamp": time.strftime("%H:%M:%S"),
    }
    
    save_session({
    "heart_rate": hr,
    "spo2": spo2,
    "fatigue": fatigue,
    "performance": performance,
    "activity": activity,
    "posture": waist.get("posture", "Good"),
    "steps": steps,
    "cadence": ankle.get("cadence", 0),
    "stride_length": ankle.get("stride_length", 0),
    "temperature": wrist.get("temperature", 36.5)
})

    return jsonify(payload)


@app.route("/api/sessions", methods=["GET"])
def sessions():

    sessions = get_all_sessions()

    data = []

    for s in sessions:
        data.append({
            "id": s.id,
            "timestamp": str(s.timestamp),
            "heart_rate": s.heart_rate,
            "spo2": s.spo2,
            "fatigue": s.fatigue,
            "performance": s.performance,
            "activity": s.activity,
            "posture": s.posture,
            "steps": s.steps,
            "cadence": s.cadence,
            "stride_length": s.stride_length,
            "temperature": s.temperature
        })

    return jsonify(data)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": time.strftime("%H:%M:%S")})

@app.route("/", endpoint="index")
def index():
    return jsonify({
        "message": "Sports AI Wearable API is running successfully!",
        "status": "OK",
        "available_endpoints": [
            "/api/health",
            "/api/sensors/live",
            "/api/sessions"
        ]
    })


@app.route("/api/coach", methods=["GET"])
def ai_coach():

    latest = get_latest_session()

    if latest is None:
        return jsonify({"error": "No workout data found"}), 404

    workout = {
        "heart_rate": latest.heart_rate,
        "spo2": latest.spo2,
        "fatigue": latest.fatigue,
        "performance": latest.performance,
        "activity": latest.activity,
        "steps": latest.steps,
        "cadence": latest.cadence,
        "stride_length": latest.stride_length,
        "temperature": latest.temperature,
    }

    advice = generate_coaching_advice(workout)

    return jsonify({
        "advice": advice
    })

@app.route("/api/video", methods=["POST"])
def upload_video():

    global latest_ai_analysis

    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    file = request.files["video"]

    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)

    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    file.save(path)

    print("Step 1: Video saved")

    extract_frames(path)
    print("Step 2: Frames extracted")

    advice = analyze_frames("frames")
    print("Step 3: Gemini finished")

    # Save the latest Gemini analysis
    latest_ai_analysis = advice

    return jsonify({
        "message": "Video uploaded successfully",
        "analysis": advice
    })

@app.route("/api/report", methods=["GET"])
def download_report():

    global latest_ai_analysis

    latest = get_latest_session()

    if latest is None:
        return jsonify({"error": "No workout data"}), 404

    sensor = {
        "heart_rate": latest.heart_rate,
        "spo2": latest.spo2,
        "fatigue": latest.fatigue,
        "performance": latest.performance,
    }

    analysis = latest_ai_analysis

    pdf_path = generate_report(sensor, analysis)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="Sports_AI_Report.pdf"
    )
threading.Thread(target=read_serial, daemon=True).start()
if __name__ == "__main__":
    
    print("=" * 60)
    print("  Sports AI Wearable — Unified API")
    print("=" * 60)
    print()
    print("  GET  /api/sensors/live   -> live combined telemetry")
    print("  GET  /api/sessions       -> past session history") 
    print("  GET  /api/health         -> server check")
    print("  POST /wrist /waist /ankle -> real ESP32 devices post here")
    print()
    print("  No ESP32 connected yet? /api/sensors/live auto-simulates.")
    print("  Running on http://localhost:5000")
    print()
    app.run(host="0.0.0.0", port=5000, debug=False)