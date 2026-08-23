"""
hand_utils.py
Extracts normalized hand landmarks from an image using MediaPipe's
Tasks API (HandLandmarker) — the current API for mediapipe >= 0.10.x.

Note: earlier mediapipe versions exposed a simpler `mp.solutions.hands`
API. Newer pip builds ship only the Tasks API shown here, which needs
a small model file (hand_landmarker.task, ~7MB) downloaded once —
handled automatically below.
"""

import os
import urllib.request

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)

# Standard 21-point hand skeleton connections (fixed anatomy, doesn't
# change between mediapipe versions) — used only for drawing feedback.
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # index
    (5, 9), (9, 10), (10, 11), (11, 12),     # middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # pinky
    (0, 17),
]


def _ensure_model_downloaded():
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading hand landmark model to {MODEL_PATH} (one-time, ~7MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Download complete.")


_ensure_model_downloaded()

_base_options = mp_python.BaseOptions(model_asset_path=MODEL_PATH)
_options = mp_vision.HandLandmarkerOptions(
    base_options=_base_options,
    running_mode=mp_vision.RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.5,
)
_landmarker = mp_vision.HandLandmarker.create_from_options(_options)


def extract_landmarks_from_bgr(image_bgr):
    """
    Runs MediaPipe HandLandmarker on a single BGR image (OpenCV format).

    Returns:
        landmarks (list[float] or None): 63 numbers (21 points * x,y,z),
            normalized relative to the wrist so it doesn't matter where
            in the frame the hand is. None if no hand was detected.
        annotated_image (np.ndarray): copy of the image with hand
            skeleton drawn on it, useful for showing the user what
            was detected.
    """
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    result = _landmarker.detect(mp_image)

    annotated = image_bgr.copy()

    if not result.hand_landmarks:
        return None, annotated

    hand = result.hand_landmarks[0]  # first detected hand
    h, w, _ = image_bgr.shape

    # Draw skeleton for user feedback
    pixel_points = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
    for start_idx, end_idx in HAND_CONNECTIONS:
        cv2.line(annotated, pixel_points[start_idx], pixel_points[end_idx], (0, 255, 0), 2)
    for point in pixel_points:
        cv2.circle(annotated, point, 4, (0, 0, 255), -1)

    # Convert to a flat list of floats
    points = np.array([[lm.x, lm.y, lm.z] for lm in hand])

    # Normalize: make wrist (landmark 0) the origin, and scale so hand
    # size / distance from camera doesn't affect the reading.
    wrist = points[0]
    points = points - wrist
    scale = np.linalg.norm(points[9])  # middle finger MCP joint, stable reference
    if scale > 1e-6:
        points = points / scale

    return points.flatten().tolist(), annotated


def bytes_to_bgr_image(image_bytes):
    """Converts raw image bytes (e.g. from st.camera_input) to an OpenCV BGR image."""
    file_bytes = np.frombuffer(image_bytes, dtype=np.uint8)
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)