"""
collect_data.py

Run this LOCALLY on your own machine (needs a real webcam — this won't
work in a sandbox/server environment).

Why collect your own data instead of downloading a dataset?
- Public ASL landmark datasets exist but come with format/licensing/
  quality inconsistencies that eat your limited time.
- MediaPipe + a classifier trained on YOUR hand, in YOUR lighting, with
  YOUR camera, is far more reliable for a live demo than a model trained
  on someone else's hands.
- 30-50 photos per letter takes about 5-10 minutes per letter. Start
  with a smaller set of letters if you're short on time (see LETTERS
  below) and expand later.

Controls while running:
    - Show the letter's handshape to the camera
    - Press SPACE to capture a sample
    - Press N to move to the next letter
    - Press Q to quit early (keeps everything captured so far)

Output: data/landmarks.csv  (one row per captured sample)
"""

import cv2
import csv
import os
from hand_utils import extract_landmarks_from_bgr

# Start with a smaller, high-value set if you're short on time.
# A-I-L-O-U-Y-etc are easier/more distinct shapes to classify reliably.
# Expand to the full alphabet once the pipeline works end-to-end.
LETTERS = list("ABCDEFGHIKLMNOPQRSTUVWXY")  # J and Z involve motion, skip for static capture

SAMPLES_PER_LETTER = 40
OUTPUT_CSV = "data/landmarks.csv"


def main():
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(OUTPUT_CSV)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam. Check your camera permissions/index.")
        return

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)

        for letter in LETTERS:
            print(f"\n=== Letter '{letter}' — show the sign, press SPACE to capture ===")
            count = 0
            while count < SAMPLES_PER_LETTER:
                ret, frame = cap.read()
                if not ret:
                    continue

                landmarks, annotated = extract_landmarks_from_bgr(frame)

                display = annotated.copy()
                cv2.putText(
                    display,
                    f"Letter: {letter}  Captured: {count}/{SAMPLES_PER_LETTER}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 0),
                    2,
                )
                if landmarks is None:
                    cv2.putText(
                        display, "No hand detected", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2,
                    )

                cv2.imshow("Data Collection - SignBridge", display)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    cap.release()
                    cv2.destroyAllWindows()
                    print("Stopped early. Data saved so far.")
                    return
                elif key == ord("n"):
                    break
                elif key == ord(" ") and landmarks is not None:
                    writer.writerow([letter] + landmarks)
                    count += 1

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nDone. Saved samples to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()