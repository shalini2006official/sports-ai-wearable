import cv2
import numpy as np
import time
import json

# ─── Calculate Angle Between 3 Points ────────────────────────
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - \
              np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return round(angle, 1)

# ─── Posture Analysis ─────────────────────────────────────────
def analyze_posture(angle):
    if angle < 160:
        return "⚠️ BAD POSTURE", (0, 0, 255)
    elif angle < 175:
        return "🔶 FAIR POSTURE", (0, 165, 255)
    else:
        return "✅ GOOD POSTURE", (0, 255, 0)

# ─── Draw Stylish Text ────────────────────────────────────────
def draw_label(frame, text, pos, color, size=0.7, thickness=2):
    x, y = pos
    cv2.rectangle(frame, (x - 5, y - 25), (x + len(text) * 12, y + 5),
                  (20, 20, 20), -1)
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)

# ─── Setup ────────────────────────────────────────────────────
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("✅ Sports AI - Posture Detection Started! Press Q to quit.")

frame_count = 0
fps_start = time.time()
fps = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera not found!")
        break

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    frame_count += 1

    # FPS calculation
    if frame_count % 10 == 0:
        fps = 10 / (time.time() - fps_start)
        fps_start = time.time()

    # ─── Dark overlay header ──────────────────────────────────
    cv2.rectangle(frame, (0, 0), (w, 60), (15, 15, 25), -1)
    cv2.putText(frame, "SPORTS AI WEARABLE - POSTURE DETECTION",
                (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                (56, 189, 248), 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 120, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 100), 1)

    # ─── Detect people ────────────────────────────────────────
    small = cv2.resize(frame, (640, 360))
    scale_x = w / 640
    scale_y = h / 360

    boxes, weights = hog.detectMultiScale(
        small,
        winStride=(8, 8),
        padding=(4, 4),
        scale=1.05
    )

    for i, (x, y, bw, bh) in enumerate(boxes):
        # Scale back to original size
        x  = int(x  * scale_x)
        y  = int(y  * scale_y)
        bw = int(bw * scale_x)
        bh = int(bh * scale_y)

        # ── Estimate key body points from bounding box ────────
        # Head
        head    = (x + bw // 2, y + int(bh * 0.08))
        # Shoulders
        l_sho   = (x + int(bw * 0.2),  y + int(bh * 0.25))
        r_sho   = (x + int(bw * 0.8),  y + int(bh * 0.25))
        # Hips
        l_hip   = (x + int(bw * 0.25), y + int(bh * 0.55))
        r_hip   = (x + int(bw * 0.75), y + int(bh * 0.55))
        # Knees
        l_knee  = (x + int(bw * 0.28), y + int(bh * 0.75))
        r_knee  = (x + int(bw * 0.72), y + int(bh * 0.75))
        # Ankles
        l_ankle = (x + int(bw * 0.28), y + int(bh * 0.95))
        r_ankle = (x + int(bw * 0.72), y + int(bh * 0.95))
        # Mid shoulder & hip
        mid_sho = ((l_sho[0] + r_sho[0]) // 2, (l_sho[1] + r_sho[1]) // 2)
        mid_hip = ((l_hip[0] + r_hip[0]) // 2, (l_hip[1] + r_hip[1]) // 2)

        # ── Calculate angles ──────────────────────────────────
        spine_angle  = calculate_angle(head, mid_sho, mid_hip)
        l_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
        r_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
        avg_knee     = (l_knee_angle + r_knee_angle) / 2

        posture_text, posture_color = analyze_posture(spine_angle)
        # Save posture data to shared file
        posture_data = {
            "posture": posture_text,
            "spine_angle": spine_angle,
            "left_knee": l_knee_angle,
            "right_knee": r_knee_angle,
            "avg_knee": round(avg_knee, 1),
            "players": len(boxes),
            "timestamp": time.strftime("%H:%M:%S")
        }
        with open("../data/posture_data.json", "w") as f:
            json.dump(posture_data, f)
        # ── Draw skeleton ─────────────────────────────────────
        skeleton_color = posture_color

        # Spine line
        cv2.line(frame, head, mid_sho, skeleton_color, 3)
        cv2.line(frame, mid_sho, mid_hip, skeleton_color, 3)

        # Shoulder line
        cv2.line(frame, l_sho, r_sho, (56, 189, 248), 2)

        # Hip line
        cv2.line(frame, l_hip, r_hip, (56, 189, 248), 2)

        # Left leg
        cv2.line(frame, l_hip, l_knee, (130, 100, 255), 2)
        cv2.line(frame, l_knee, l_ankle, (130, 100, 255), 2)

        # Right leg
        cv2.line(frame, r_hip, r_knee, (130, 100, 255), 2)
        cv2.line(frame, r_knee, r_ankle, (130, 100, 255), 2)

        # ── Draw joint points ─────────────────────────────────
        for pt in [head, l_sho, r_sho, mid_sho,
                   l_hip, r_hip, mid_hip,
                   l_knee, r_knee, l_ankle, r_ankle]:
            cv2.circle(frame, pt, 6, (255, 255, 255), -1)
            cv2.circle(frame, pt, 8, skeleton_color, 2)

        # ── Bounding box ──────────────────────────────────────
        cv2.rectangle(frame, (x, y), (x + bw, y + bh),
                      skeleton_color, 2)

        # ── Angle labels ──────────────────────────────────────
        draw_label(frame, f"Spine: {spine_angle}°",
                   (mid_sho[0] + 15, mid_sho[1]),
                   skeleton_color)
        draw_label(frame, f"L Knee: {l_knee_angle}°",
                   (l_knee[0] - 100, l_knee[1]),
                   (200, 150, 255))
        draw_label(frame, f"R Knee: {r_knee_angle}°",
                   (r_knee[0] + 10, r_knee[1]),
                   (200, 150, 255))

        # ── Posture status box ────────────────────────────────
        cv2.rectangle(frame, (x, y - 45), (x + bw, y - 5),
                      (20, 20, 30), -1)
        cv2.putText(frame, f"Player {i+1}: {posture_text}",
                    (x + 5, y - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                    posture_color, 2)

    # ─── Bottom info bar ──────────────────────────────────────
    cv2.rectangle(frame, (0, h - 50), (w, h), (15, 15, 25), -1)

    if len(boxes) > 0:
        status = f"✓ {len(boxes)} Player(s) Detected"
        s_color = (0, 255, 100)
    else:
        status = "Searching for players..."
        s_color = (100, 100, 255)

    cv2.putText(frame, status, (20, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, s_color, 2)
    cv2.putText(frame,
                "GREEN=Good  ORANGE=Fair  RED=Bad Posture",
                (w - 480, h - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (150, 150, 150), 1)

    cv2.imshow("Sports AI Wearable - Posture Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Session ended.")