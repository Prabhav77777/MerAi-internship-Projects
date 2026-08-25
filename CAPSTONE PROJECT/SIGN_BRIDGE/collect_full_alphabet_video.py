"""
collect_full_alphabet_video.py

Designed for full-alphabet ASL video tutorials (like Start ASL), where
a single video demonstrates letters A to Y sequentially.

Modes:
  Mode 1 (Interactive Terminal): Press ENTER in terminal whenever the letter
                                 on screen changes (A -> B -> C ...).
  Mode 2 (Timed Auto): Specify seconds per letter (e.g. 4 seconds) and it
                       automatically labels and extracts all letters!
"""

import os
import csv
import glob
import time
import cv2
from hand_utils import extract_landmarks_from_bgr

OUTPUT_CSV = "data/landmarks.csv"
LETTERS = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]  # All 26 ASL letters (A to Z)

def find_default_video():
    mp4_files = glob.glob("*.mp4") + glob.glob("*.webm") + glob.glob("*.avi") + glob.glob("*.mov")
    if mp4_files:
        return mp4_files[0]
    return "video.mp4"

def process_interactive_mode(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error opening {video_path}")
        return

    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(OUTPUT_CSV)
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print("\n--- Interactive Terminal Mode ---")
    print("Press ENTER in the terminal whenever the video transitions to the NEXT letter.")
    print("Press 'q' + ENTER to stop early.\n")

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)

        for letter in LETTERS:
            print(f"\n👉 Currently extracting letter '{letter}'. (Press ENTER when letter '{letter}' ends / next letter starts)")
            captured_for_letter = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Reached end of video file.")
                    cap.release()
                    print(f"✅ Extracted data saved to {OUTPUT_CSV}")
                    return
                
                cur_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                # Sample 1 frame out of every 5 frames
                if cur_frame % 5 == 0:
                    landmarks, _ = extract_landmarks_from_bgr(frame)
                    if landmarks is not None:
                        writer.writerow([letter] + landmarks)
                        captured_for_letter += 1

                # Non-blocking terminal check or prompt
                # Ask user if letter has changed
                # To prevent blocking every frame, we prompt per letter batch
                break_letter = False
                user_cmd = input(f"   [{letter}] Captured {captured_for_letter} frames so far. Press ENTER for next letter (or 'c' to keep capturing): ").strip().lower()
                if user_cmd == 'q':
                    cap.release()
                    print(f"\nDone! Extracted samples saved to {OUTPUT_CSV}")
                    return
                elif user_cmd != 'c':
                    # User hit ENTER -> advance to next letter!
                    print(f"✓ Saved {captured_for_letter} samples for letter '{letter}'.")
                    break

    cap.release()
    print(f"\n✅ Finished processing video! Samples saved to {OUTPUT_CSV}")


def process_timed_mode(video_path, sec_per_letter, start_offset_sec=0):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Error opening {video_path}")
        return

    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(OUTPUT_CSV)
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    start_frame = int(start_offset_sec * fps)
    frames_per_letter = int(sec_per_letter * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)

        print(f"\n🚀 Starting timed extraction ({sec_per_letter}s per letter)...")
        
        for letter in LETTERS:
            captured_for_letter = 0
            letter_end_frame = cap.get(cv2.CAP_PROP_POS_FRAMES) + frames_per_letter
            
            while cap.get(cv2.CAP_PROP_POS_FRAMES) < letter_end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
                
                cur_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                if cur_frame % 4 == 0:  # sample every 4th frame
                    landmarks, _ = extract_landmarks_from_bgr(frame)
                    if landmarks is not None:
                        writer.writerow([letter] + landmarks)
                        captured_for_letter += 1
            
            print(f"  - Letter '{letter}': extracted {captured_for_letter} hand landmark samples")

    cap.release()
    print(f"\n✅ All done! Saved samples to {OUTPUT_CSV}")


def main():
    default_file = find_default_video()
    print("\n===========================================")
    print(" SignBridge Full-Alphabet Video Extractor")
    print("===========================================")
    prompt_str = f"Enter video filename/path [Press ENTER to use '{default_file}']: "
    user_input = input(prompt_str).strip().strip("'\"")
    
    video_path = user_input if user_input else default_file
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file '{video_path}' not found.")
        return

    print(f"\nVideo file selected: {video_path}")
    print("Choose extraction mode:")
    print("  [1] Timed Auto Mode (e.g. 4 seconds per letter)")
    print("  [2] Interactive Step Mode (Press ENTER when letter changes)")
    
    mode = input("Select mode (1 or 2, default=1): ").strip()
    
    if mode == "2":
        process_interactive_mode(video_path)
    else:
        sec_str = input("How many seconds does each letter sign play for in your video? (default=4): ").strip()
        sec = float(sec_str) if sec_str else 4.0
        
        offset_str = input("Start delay before letter A begins in seconds? (default=0): ").strip()
        offset = float(offset_str) if offset_str else 0.0
        
        process_timed_mode(video_path, sec_per_letter=sec, start_offset_sec=offset)


if __name__ == "__main__":
    main()
