"""
live_processor.py
Continuous webcam mode: runs on every video frame in the background,
overlays the detected letter directly on the video, and auto-commits
a letter once the same prediction has been held steady for a short
moment — no photo-click needed per letter.

This uses streamlit-webrtc, which streams video through the browser,
so it works both locally and once deployed (unlike a plain cv2.imshow
window, which only works on your own machine).
"""

import threading
import time

import cv2
import av
from streamlit_webrtc import VideoProcessorBase

from hand_utils import extract_landmarks_from_bgr
from classify import predict_letter

# How many consecutive stable frames before a letter auto-commits.
# Roughly maps to "hold the sign steady for about half a second".
STABILITY_FRAMES = 12

# Minimum classifier confidence to accept a prediction at all.
CONFIDENCE_THRESHOLD = 0.6

# Cooldown so a held sign doesn't spam the same letter repeatedly.
# The user must briefly move their hand out of frame (or change the
# sign) before the same letter can be committed again.
COOLDOWN_SECONDS = 1.0


class LiveSignProcessor(VideoProcessorBase):
    def __init__(self):
        self.lock = threading.Lock()
        self.current_letter = None
        self.current_confidence = 0.0
        self.stable_count = 0
        self.last_committed_letter = None
        self.last_committed_time = 0.0
        self.pending_letters = []  # letters ready for the main thread to collect

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        landmarks, annotated = extract_landmarks_from_bgr(img)

        with self.lock:
            if landmarks is None:
                # No hand in frame — reset so the same letter can be
                # signed again after the user resets their hand.
                self.current_letter = None
                self.current_confidence = 0.0
                self.stable_count = 0
                self.last_committed_letter = None
            else:
                letter, confidence = predict_letter(landmarks)

                if confidence < CONFIDENCE_THRESHOLD:
                    letter = None

                if letter == self.current_letter:
                    self.stable_count += 1
                else:
                    self.current_letter = letter
                    self.stable_count = 1

                self.current_confidence = confidence

                now = time.time()
                ready_to_commit = (
                    letter is not None
                    and self.stable_count == STABILITY_FRAMES
                    and (
                        letter != self.last_committed_letter
                        or (now - self.last_committed_time) > COOLDOWN_SECONDS
                    )
                )
                if ready_to_commit:
                    self.pending_letters.append(letter)
                    self.last_committed_letter = letter
                    self.last_committed_time = now

            display_letter = self.current_letter
            display_count = self.stable_count

        # Draw live feedback directly on the video the user sees
        label = display_letter if display_letter else "..."
        progress = min(display_count, STABILITY_FRAMES)
        cv2.putText(
            annotated, f"Detected: {label}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2,
        )
        cv2.rectangle(annotated, (10, 45), (10 + progress * 8, 60), (0, 255, 0), -1)
        cv2.rectangle(annotated, (10, 45), (10 + STABILITY_FRAMES * 8, 60), (0, 255, 0), 1)

        return av.VideoFrame.from_ndarray(annotated, format="bgr24")

    def collect_pending_letters(self):
        """Called from the main Streamlit thread to grab any letters
        that were auto-committed since the last check."""
        with self.lock:
            letters = self.pending_letters[:]
            self.pending_letters.clear()
            return letters