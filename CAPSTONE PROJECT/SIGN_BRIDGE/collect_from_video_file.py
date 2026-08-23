"""
collect_from_video_file.py

Extracts hand landmarks from a local video file (e.g. video.mp4)
and appends them to data/landmarks.csv.

Supports both interactive GUI mode (press keys) and headless/auto mode
(extracts all valid frames for a chosen letter automatically).
"""

import os
import csv
import glob
import cv2
from hand_utils import extract_landmarks_from_bgr

OUTPUT_CSV = "data/landmarks.csv"

def safe_destroy_windows():
    """Safely destroy OpenCV windows if GUI is available."""
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

def find_default_video():
    mp4_files = glob.glob("*.mp4") + glob.glob("*.webm") + glob.glob("*.avi") + glob.glob("*.mov")
    if mp4_files:
        return mp4_files[0]
    return "video.mp4"

def run_auto_extractor(video_path, label):
    """Headless auto-extractor: processes the video from start to end
    and saves landmarks for the given letter automatically."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error opening {video_path}")
        return

    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(OUTPUT_CSV)
    
    saved_count = 0
    frame_idx = 0
    
    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)

        print(f"\n🚀 Processing video frames for letter '{label}'...")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_idx += 1
            
            # Sample 1 out of every 3 frames for clean diversity
            if frame_idx % 3 == 0:
                landmarks, _ = extract_landmarks_from_bgr(frame)
                if landmarks is not None:
                    writer.writerow([label] + landmarks)
                    saved_count += 1

    cap.release()
    print(f"\n✅ Successfully extracted {saved_count} landmark samples for letter '{label}' into {OUTPUT_CSV}!")

def main():
    os.makedirs("data", exist_ok=True)
    default_file = find_default_video()
    
    print("\n--- SignBridge Video Dataset Collector ---")
    prompt_str = f"Enter video filename or path [Press ENTER to use '{default_file}']: "
    user_input = input(prompt_str).strip().strip("'\"")
    
    video_path = user_input if user_input else default_file
    
    if not os.path.exists(video_path):
        print(f"\n❌ Error: File '{video_path}' was not found.")
        print(f"👉 Please place your video file directly inside the SIGN_BRIDGE folder,")
        print(f"   for example: name your video 'video.mp4' and save it in:")
        print(f"   {os.getcwd()}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"\n❌ Error: Could not open video file {video_path}")
        return

    gui_supported = True
    
    # Try rendering a test frame to check GUI window support
    ret, test_frame = cap.read()
    if ret:
        try:
            cv2.imshow("Test Window", test_frame)
            cv2.waitKey(1)
            safe_destroy_windows()
        except Exception:
            gui_supported = False
        # Reset video back to start frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    if not gui_supported:
        print("\n⚠️ Note: OpenCV GUI windows (cv2.imshow) are not available in this terminal.")
        print("--- Automatic Batch Extractor Mode ---")
        letter = input("Which letter does this video demonstrate? (e.g. A): ").strip().upper()
        cap.release()
        if letter and letter not in ["J", "Z"]:
            run_auto_extractor(video_path, letter)
        else:
            print("Invalid or skipped letter.")
        return

    file_exists = os.path.exists(OUTPUT_CSV)
    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)

        current_label = "A"
        paused = False
        captured_count = 0

        print(f"\n✅ Opened video: {video_path}")
        print("\n--- Interactive Controls ---")
        print("  - Press [A-Y] to select letter label")
        print("  - Press [SPACE] to capture current frame landmark")
        print("  - Press [P] to pause / play video")
        print("  - Press [Q] to save and quit\n")

        while True:
            if not paused:
                ret, frame = cap.read()
                if not ret:
                    print("End of video reached.")
                    break
            
            landmarks, annotated = extract_landmarks_from_bgr(frame)
            display = annotated.copy()

            status = f"Target Letter: {current_label}  |  Captured this session: {captured_count}"
            cv2.putText(display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            if paused:
                cv2.putText(display, "PAUSED (Press P to resume)", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

            try:
                cv2.imshow("SignBridge - Video Collector", display)
                key = cv2.waitKey(30 if not paused else 0) & 0xFF
            except Exception:
                gui_supported = False
                break

            if key == ord("q"):
                break
            elif key == ord("p"):
                paused = not paused
            elif key == ord(" ") and landmarks is not None:
                writer.writerow([current_label] + landmarks)
                captured_count += 1
                print(f"Captured frame for letter '{current_label}' (Total: {captured_count})")
            elif ord("a") <= key <= ord("z"):
                char = chr(key).upper()
                if char in "J" or char in "Z":
                    print(f"Skipping '{char}' (motion-based sign)")
                else:
                    current_label = char
                    print(f"Switched target label to '{current_label}'")

    cap.release()
    safe_destroy_windows()
    print(f"\nDone! Captured {captured_count} landmark samples saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
