import cv2
import os

def extract_frames(video_path, output_folder="frames", interval=30):
    """
    Extract one frame every 'interval' frames.

    video_path: path of uploaded video
    output_folder: folder where extracted images will be saved
    interval: save every 30th frame
    """

    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    count = 0
    saved = 0

    while True:
        success, frame = cap.read()

        if not success:
            break

        if count % interval == 0:
            filename = os.path.join(output_folder, f"frame_{saved}.jpg")
            cv2.imwrite(filename, frame)
            saved += 1

        count += 1

    cap.release()

    return {
        "total_frames": count,
        "saved_frames": saved,
        "folder": output_folder
    }