"""
live_processor.py
Continuous webcam mode: runs on every video frame in the background,
overlays the detected letter directly on the video, and auto-commits
a letter once the same prediction has been held steady for a short
moment — no photo-click needed per letter.

This uses streamlit-webrtc, which streams video through the browser,
so it works both locally and once deployed (unlike a plain cv2.imshow
window, which only works on your own machine).

Performance note: running full hand-landmark detection on every single
frame at 30fps is expensive and causes visible lag. We only run
detection every PROCESS_EVERY_N_FRAMES frames and reuse the last
result in between — this keeps the video smooth while still updating
the prediction several times per second.
"""

import threading
import time

import cv2
import av
from streamlit_webrtc import VideoProcessorBase

from hand_utils import extract_landmarks_from_bgr
from classify import predict_letter

# Only run the (expensive) detection+classification every Nth frame.
# At ~24-30fps input, 3 means we still classify ~8-10 times/second —
# plenty responsive, far less laggy.
PROCESS_EVERY_N_FRAMES = 3

# How many *processed* frames (not raw frames) the same letter must
# be held for before it auto-commits. At ~8-10 classifications/sec,
# 6 is roughly half a second of holding.
STABILITY_FRAMES = 6

# Minimum confidence to accept a prediction as "detected" at all.
# Live webcam frames are noisier than the still photos used for
# training, so this is intentionally more lenient than Click Mode.
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

        annotated = img  # default: raw frame, overwritten below if we detect

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

                    if confidence < CONFIDENCE_THRESHOLD:
                        letter = None

                    if letter == self.current_letter:
                        self.stable_count += 1
                    else:
                        self.current_letter = letter
                        self.stable_count = 1

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
                        self.last_added_display = letter
                        self.last_added_display_time = now
        else:
            # Skip detection this frame, but still draw the hand-free
            # raw frame so the video stays smooth and responsive.
            pass

        with self.lock:
            display_letter = self.current_letter
            display_conf = self.current_confidence
            display_count = min(self.stable_count, STABILITY_FRAMES)
            hand_visible = self.hand_visible
            show_added_flash = (
                self.last_added_display is not None
                and (time.time() - self.last_added_display_time) < 1.0
            )
            flash_letter = self.last_added_display

        # ---- On-screen overlay (always drawn, every frame, cheap) ----
        h, w = annotated.shape[:2]

        if not hand_visible:
            label = "Show your hand..."
            color = (0, 0, 255)  # red
        elif display_letter:
            label = f"Detected: {display_letter} ({display_conf:.0%})"
            color = (0, 255, 0)  # green
        else:
            label = "Detecting... (low confidence)"
            color = (0, 165, 255)  # orange

        cv2.putText(annotated, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Stability progress bar
        bar_w = 200
        cv2.rectangle(annotated, (10, 45), (10 + bar_w, 65), (80, 80, 80), 1)
        filled = int(bar_w * (display_count / STABILITY_FRAMES))
        if filled > 0:
            cv2.rectangle(annotated, (10, 45), (10 + filled, 65), color, -1)

        # Big "Added: X" flash for ~1 second right after a commit
        if show_added_flash:
            cv2.putText(
                annotated, f"Added: {flash_letter}", (10, h - 20),
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