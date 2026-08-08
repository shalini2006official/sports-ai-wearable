import cv2
import mediapipe as mp

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


def analyze_video(video_path):

    cap = cv2.VideoCapture(video_path)

    total_frames = 0
    detected_frames = 0

    while True:

        success, frame = cap.read()

        if not success:
            break

        total_frames += 1

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = pose.process(rgb)

        if result.pose_landmarks:
            detected_frames += 1

    cap.release()

    return {
        "total_frames": total_frames,
        "pose_detected": detected_frames
    }