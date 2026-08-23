"""
live_processor.py
Continuous webcam mode: runs on every video frame in the background,
overlays the detected letter directly on the video, and auto-commits
a letter once the same prediction has been held steady for a short
moment — no photo-click needed per letter.

This uses streamlit-webrtc, which streams video through the browser,
so it works both locally and once deployed.
"""

import threading
import time

import cv2
import av
from streamlit_webrtc import VideoProcessorBase

from hand_utils import extract_landmarks_from_bgr
from classify import predict_letter

PROCESS_EVERY_N_FRAMES = 3
STABILITY_FRAMES = 6
CONFIDENCE_THRESHOLD = 0.45
COOLDOWN_SECONDS = 1.0


class LiveSignProcessor(VideoProcessorBase):
    def __init__(self):
        self.lock = threading.Lock()
        self.frame_count = 0
        self.current_letter = None
        self.current_confidence = 0.0
        self.stable_count = 0
        self.last_committed_letter = None
        self.last_committed_time = 0.0
        self.pending_letters = []       # letters ready for the main thread
        self.last_added_display = None  # for on-screen "Added: X" flash
        self.last_added_display_time = 0.0
        self.hand_visible = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        with self.lock:
            self.frame_count += 1
            run_detection = (self.frame_count % PROCESS_EVERY_N_FRAMES == 0)

        annotated = img

        if run_detection:
            landmarks, annotated = extract_landmarks_from_bgr(img)

            with self.lock:
                if landmarks is None:
                    self.current_letter = None
                    self.current_confidence = 0.0
                    self.stable_count = 0
                    self.last_committed_letter = None
                    self.hand_visible = False
                else:
                    self.hand_visible = True
                    letter, confidence = predict_letter(landmarks)
                    self.current_confidence = confidence

                    if letter is None or confidence < CONFIDENCE_THRESHOLD:
                        letter = None

                    if letter == self.current_letter and letter is not None:
                        self.stable_count += 1
                    else:
                        self.current_letter = letter
                        self.stable_count = 1 if letter is not None else 0

                    now = time.time()
                    ready_to_commit = (
                        letter is not None
                        and self.stable_count >= STABILITY_FRAMES
                        and (
                            letter != self.last_committed_letter
                            or (now - self.last_committed_time) > COOLDOWN_SECONDS
                        )
                    )
                    if ready_to_commit:
                        self.pending_letters.append(letter)
                        self.last_committed_letter = letter
                        self.last_committed_time = now
                        self.last_added_display = letter
                        self.last_added_display_time = now
                        self.stable_count = 0  # reset for next gesture
        else:
            pass

        with self.lock:
            display_letter = self.current_letter
            display_conf = self.current_confidence
            display_count = min(self.stable_count, STABILITY_FRAMES)
            hand_visible = self.hand_visible
            show_added_flash = (
                self.last_added_display is not None
                and (time.time() - self.last_added_display_time) < 1.2
            )
            flash_letter = self.last_added_display

        # On-screen overlay on video frame
        h, w = annotated.shape[:2]

        if not hand_visible:
            label = "Show your hand to camera..."
            color = (0, 0, 255)
        elif display_letter:
            label = f"Detected: {display_letter} ({display_conf:.0%})"
            color = (0, 255, 0)
        else:
            label = "Detecting hand posture..."
            color = (0, 165, 255)

        cv2.putText(annotated, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Progress bar overlay
        bar_w = 200
        cv2.rectangle(annotated, (10, 45), (10 + bar_w, 65), (80, 80, 80), 1)
        filled = int(bar_w * (display_count / float(STABILITY_FRAMES)))
        if filled > 0:
            cv2.rectangle(annotated, (10, 45), (10 + filled, 65), color, -1)

        if show_added_flash:
            cv2.putText(
                annotated, f"ADDED LETTER: {flash_letter}", (10, h - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3,
            )

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")

    def collect_pending_letters(self):
        """Called from the main Streamlit thread to grab any letters
        that were auto-committed since the last check."""
        with self.lock:
            letters = self.pending_letters[:]
            self.pending_letters.clear()
            return letters