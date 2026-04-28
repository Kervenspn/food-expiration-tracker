import os
import cv2
import time
from datetime import datetime

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def capture_image():
    cap = cv2.VideoCapture(0)

    #Check camera opens
    if not cap.isOpened():
        print("Camera not opened")
        return None

    #Warm-up very important
    time.sleep(1)

    frame = None

    #Read multiple frames to stabilize image
    for _ in range(10):
        ret, frame = cap.read()

    cap.release()

    #Check pictured captured
    if not ret or frame is None:
        print("Failed to capture image")
        return None

    #Save image
    filename = f"cap_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    cv2.imwrite(file_path, frame)

    print(f"Image saved: {file_path}")

    return file_path