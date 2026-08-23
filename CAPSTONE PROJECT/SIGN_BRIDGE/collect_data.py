"""
collect_data.py

Captures hand landmark samples from webcam and appends them to data/landmarks.csv.

Supports both OpenCV window mode and Terminal mode (if cv2.imshow is unavailable).
"""

import os
import csv
import cv2
from hand_utils import extract_landmarks_from_bgr

LETTERS = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
SAMPLES_PER_LETTER = 30
OUTPUT_CSV = "data/landmarks.csv"

def safe_destroy_windows():
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

def main():
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(OUTPUT_CSV)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Could not open webcam (index 0). Check camera connection/permissions.")
        return

    # Check GUI support up front
    ret, test_frame = cap.read()
    gui_supported = True
    if ret:
        try:
            cv2.imshow("Test", test_frame)
            cv2.waitKey(1)
            safe_destroy_windows()
        except Exception:
            gui_supported = False

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)

        if gui_supported:
            print("\n--- OpenCV Window Data Collection ---")
            print("  - Show hand shape to camera")
            print("  - Press [SPACE] to capture sample")
            print("  - Press [N] to move to next letter")
            print("  - Press [Q] to quit\n")

            for letter in LETTERS:
                print(f"=== Letter '{letter}' — show sign & press SPACE to capture ===")
                count = 0
                while count < SAMPLES_PER_LETTER:
                    ret, frame = cap.read()
                    if not ret:
                        continue

                    landmarks, annotated = extract_landmarks_from_bgr(frame)
                    display = annotated.copy()
                    
                    cv2.putText(
                        display, f"Letter: {letter}  Captured: {count}/{SAMPLES_PER_LETTER}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
                    )
                    if landmarks is None:
                        cv2.putText(
                            display, "No hand detected", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                        )

                    try:
                        cv2.imshow("SignBridge - Data Collection", display)
                        key = cv2.waitKey(1) & 0xFF
                    except Exception:
                        break

                    if key == ord("q"):
                        cap.release()
                        safe_destroy_windows()
                        print("\nStopped early. Data saved.")
                        return
                    elif key == ord("n"):
                        break
                    elif key == ord(" ") and landmarks is not None:
                        writer.writerow([letter] + landmarks)
                        count += 1
                        print(f"Captured '{letter}' sample {count}/{SAMPLES_PER_LETTER}")

        else:
            print("\n⚠️ OpenCV GUI windows (cv2.imshow) are unavailable in this environment.")
            print("--- Terminal Webcam Capture Mode ---")
            print("  - Show hand shape to your webcam")
            print("  - Press [ENTER] to capture 5 consecutive samples for the letter")
            print("  - Type 'n' + ENTER to advance to next letter")
            print("  - Type 'q' + ENTER to quit\n")

            for letter in LETTERS:
                print(f"\n==========================================")
                print(f"👉 Target Letter: '{letter}'")
                print(f"==========================================")
                count = 0
                
                while count < SAMPLES_PER_LETTER:
                    cmd = input(f"[{letter}] ({count}/{SAMPLES_PER_LETTER} collected) Press ENTER to capture batch (or 'n'=next, 'q'=quit): ").strip().lower()
                    if cmd == 'q':
                        cap.release()
                        print("\nStopped early. Data saved.")
                        return
                    elif cmd == 'n':
                        break
                    
                    # Capture 5 frames over 1.5 seconds
                    captured_batch = 0
                    for _ in range(15):
                        ret, frame = cap.read()
                        if not ret:
                            continue
                        landmarks, _ = extract_landmarks_from_bgr(frame)
                        if landmarks is not None:
                            writer.writerow([letter] + landmarks)
                            captured_batch += 1
                            count += 1
                            if captured_batch >= 5 or count >= SAMPLES_PER_LETTER:
                                break
                    
                    if captured_batch > 0:
                        print(f"  ✅ Captured {captured_batch} samples for letter '{letter}'! (Total: {count}/{SAMPLES_PER_LETTER})")
                    else:
                        print("  ⚠️ No hand detected in front of camera — please position your hand clearly and try again.")

    cap.release()
    safe_destroy_windows()
    print(f"\n🎉 Collection complete! All samples saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()