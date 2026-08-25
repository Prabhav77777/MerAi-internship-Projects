"""
app.py
SignBridge — Fingerspelling-to-Speech Communication Assistant

Two capture modes, both feeding the same word/sentence buffer:
  - Click Mode: take a photo per letter, confirm/retry (most reliable).
               Wrong predictions can be corrected on the spot, and the
               correction is appended to data/landmarks.csv so the next
               training run learns from real mistakes.
  - Live Mode: continuous webcam feed with real-time UI polling, letter auto-detected
               on screen and auto-added once held steady for a moment.

Pipeline after either mode:
  letters -> word (with offline suggestions) -> sentence
  -> Gemini cleans up the sentence -> gTTS speaks it aloud

Run locally with:  streamlit run app.py
"""

import csv
import os
from pathlib import Path

import streamlit as st
import pandas as pd
from datetime import datetime

# Streamlit Community Cloud starts apps from the repository root, while this
# app and its bundled model/assets live in a subdirectory. Resolve all legacy
# relative paths from this file so local and cloud runs use the same files.
PROJECT_DIR = Path(__file__).resolve().parent
os.chdir(PROJECT_DIR)

from hand_utils import (
    bytes_to_bgr_image,
    extract_landmarks_from_bgr,
    get_hand_landmarker_error,
)
from classify import get_supported_letters, predict_letter
from gemini_helper import clean_sentence
from tts_helper import text_to_speech_bytes
from word_suggest import suggest_words

# ---------- Page config ----------
st.set_page_config(
    page_title="SignBridge",
    page_icon=":material/sign_language:",
    layout="wide",
)

LANDMARKS_CSV = "data/landmarks.csv"
ASL_LETTERS = list(get_supported_letters())
STABILITY_FRAMES = 6


def save_training_sample(landmarks, letter):
    """Appends a confirmed (or corrected) sample to the training CSV,
    so mistakes caught during testing/demo directly improve the next
    training run."""
    if landmarks is None or letter not in ASL_LETTERS:
        return
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.exists(LANDMARKS_CSV)
    with open(LANDMARKS_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"p{i}" for i in range(63)]
            writer.writerow(header)
        writer.writerow([letter] + list(landmarks))


# ---------- Session state setup ----------
defaults = {
    "current_word": "",
    "sentence_buffer": "",
    "history_log": [],       # list of dicts -> becomes a DataFrame
    "last_prediction": None,
    "last_confidence": None,
    "last_landmarks": None,
    "prev_confidence": None, # for st.metric delta
    "show_correction": False,
    "processed_img_id": None,
    "raw_sentence": "",
    "final_sentence": "",
    "audio_bytes": None,
    "last_annotated_image": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------- Sidebar ASL Reference Board ----------
with st.sidebar:
    st.subheader(":material/menu_book: ASL Sign Reference")
    st.caption("Fingerspelling guide (A–Z; J and Z use motion)")
    st.image("image_sign.jpg", caption="ASL reference chart — StartASL", width="stretch")
    st.info(
        f"Active static model targets: {', '.join(ASL_LETTERS) or 'unavailable'}. "
        "J and Z require movement and are not active targets.",
        icon=":material/lightbulb:",
    )


# ---------- Header ----------
st.title(":material/sign_language: SignBridge")
st.caption(
    "A fingerspelling-to-speech assistant — sign letters, build words "
    "with suggestions, and speak full sentences aloud."
)

with st.expander(":material/pan_tool: ASL Alphabet Sign Reference Board", expanded=False):
    st.image("image_sign.jpg", caption="ASL reference chart — StartASL", width="stretch")

# ---------- KPI status row ----------
with st.container(horizontal=True):
    st.metric(
        "Detected letter",
        st.session_state.last_prediction or "—",
        border=True,
    )

    conf = st.session_state.last_confidence
    prev_conf = st.session_state.prev_confidence
    delta_str = None
    if conf is not None and prev_conf is not None:
        delta_val = conf - prev_conf
        delta_str = f"{delta_val:+.0%}"
    st.metric(
        "Confidence",
        f"{conf:.0%}" if conf is not None else "—",
        delta=delta_str,
        border=True,
    )

    word_len = len(st.session_state.current_word)
    st.metric("Word length", word_len, border=True)

    sentence_words = st.session_state.sentence_buffer.split()
    st.metric("Sentence words", len(sentence_words), border=True)


def add_letter(letter, confidence):
    """Shared helper: both capture modes call this to append a letter."""
    st.session_state.current_word += letter
    st.session_state.history_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "letter": letter,
        "confidence": round(confidence, 2) if confidence else 1.0,
    })


def render_word_and_sentence_builder(key_prefix):
    """Shared UI: current word, suggestions, sentence buffer, controls.
    Used by both Click Mode and Live Mode so they share one buffer."""

    st.write("**Current word:**", f"`{st.session_state.current_word}`" if st.session_state.current_word else "_(empty)_")

    if st.session_state.current_word:
        suggestions = suggest_words(st.session_state.current_word)
        if suggestions:
            st.caption("Word suggestions (click to auto-complete):")
            sug_cols = st.columns(len(suggestions))
            for i, word in enumerate(suggestions):
                with sug_cols[i]:
                    if st.button(word, key=f"{key_prefix}_sug_{word}_{i}"):
                        st.session_state.sentence_buffer += word + " "
                        st.session_state.current_word = ""
                        st.rerun()

    st.write("**Sentence so far:**", f"`{st.session_state.sentence_buffer}`" if st.session_state.sentence_buffer else "_(empty)_")

    with st.container(horizontal=True):
        if st.button(":material/space_bar: End word", key=f"{key_prefix}_end_word"):
            if st.session_state.current_word:
                st.session_state.sentence_buffer += st.session_state.current_word + " "
                st.session_state.current_word = ""
                st.rerun()
        if st.button(":material/backspace: Backspace", key=f"{key_prefix}_backspace"):
            if st.session_state.current_word:
                st.session_state.current_word = st.session_state.current_word[:-1]
                st.rerun()
        if st.button(":material/delete: Clear word", key=f"{key_prefix}_clear_word"):
            st.session_state.current_word = ""
            st.rerun()
        if st.button(":material/restart_alt: Reset all", key=f"{key_prefix}_reset_sentence"):
            st.session_state.sentence_buffer = ""
            st.session_state.current_word = ""
            st.session_state.final_sentence = ""
            st.session_state.raw_sentence = ""
            st.session_state.audio_bytes = None
            st.session_state.last_prediction = None
            st.session_state.last_landmarks = None
            st.session_state.show_correction = False
            st.rerun()


# ---------- Mode tabs ----------
tab_click, tab_live, tab_collect = st.tabs([
    ":material/photo_camera: Click mode (reliable)",
    ":material/videocam: Live mode (continuous)",
    ":material/add_a_photo: Data Collection Studio (See Yourself Live)",
])

with tab_click:
    col_camera, col_status = st.columns([1, 1])

    with col_camera:
        st.subheader("1. Capture a letter")
        img_file = st.camera_input(
            "Show a handshape and take a photo",
            key="click_camera",
        )

        if img_file is not None:
            image_bytes = img_file.getvalue()
            img_id = hash(image_bytes)

            # Process only if a NEW photo was taken
            if img_id != st.session_state.get("processed_img_id"):
                bgr_image = bytes_to_bgr_image(image_bytes)
                landmarks, annotated = extract_landmarks_from_bgr(bgr_image)

                st.session_state.processed_img_id = img_id
                st.session_state.last_landmarks = landmarks
                st.session_state.last_annotated_image = annotated
                st.session_state.show_correction = False

                if landmarks is None:
                    st.session_state.last_prediction = None
                    st.session_state.last_confidence = None
                else:
                    letter, confidence = predict_letter(landmarks)
                    if letter is not None:
                        st.session_state.prev_confidence = st.session_state.last_confidence
                        st.session_state.last_prediction = letter
                        st.session_state.last_confidence = confidence

            # Display landmarks overlay
            if st.session_state.last_landmarks is not None and st.session_state.last_annotated_image is not None:
                st.image(st.session_state.last_annotated_image, channels="BGR", caption="Detected hand landmarks")
            else:
                hand_error = get_hand_landmarker_error()
                if hand_error:
                    st.error(
                        f"Hand detection engine error: {hand_error}",
                        icon=":material/error:",
                    )
                else:
                    st.warning(
                        "No hand detected — try adjusting your position or lighting.",
                        icon=":material/warning:",
                    )

    with col_status:
        st.subheader("2. Confirm & build")

        if st.session_state.last_prediction:
            with st.container(horizontal=True):
                st.metric(
                    "Detected letter",
                    st.session_state.last_prediction,
                    border=True,
                )
                st.metric(
                    "Confidence",
                    f"{st.session_state.last_confidence:.0%}" if st.session_state.last_confidence else "—",
                    border=True,
                )

            st.caption("Was this correct? (Your answer also improves the model)")

            col_add, col_wrg = st.columns(2)
            with col_add:
                if st.button(
                    ":material/check_circle: Correct — add letter",
                    type="primary",
                    key="add_click",
                ):
                    add_letter(
                        st.session_state.last_prediction,
                        st.session_state.last_confidence,
                    )
                    save_training_sample(
                        st.session_state.last_landmarks,
                        st.session_state.last_prediction,
                    )
                    st.toast(f"Added letter '{st.session_state.last_prediction}'!", icon="✅")
                    st.session_state.last_prediction = None
                    st.session_state.last_landmarks = None
                    st.session_state.show_correction = False
                    st.rerun()

            with col_wrg:
                if st.button(
                    ":material/cancel: Wrong letter",
                    key="wrong_click",
                ):
                    st.session_state.show_correction = True
                    st.rerun()

            if st.session_state.get("show_correction"):
                st.write("---")
                st.write("**Correction mode:** Select the actual letter signed:")
                correct_letter = st.selectbox("Actual static ASL letter", ASL_LETTERS, key="correction_select")
                if st.button(
                    ":material/save: Save correction & add this letter",
                    type="primary",
                    key="save_correction_btn",
                ):
                    add_letter(correct_letter, st.session_state.last_confidence or 1.0)
                    save_training_sample(
                        st.session_state.last_landmarks,
                        correct_letter,
                    )
                    st.toast(
                        f"Added corrected letter '{correct_letter}' and saved sample!",
                        icon="✅",
                    )
                    st.session_state.last_prediction = None
                    st.session_state.last_landmarks = None
                    st.session_state.show_correction = False
                    st.rerun()

        render_word_and_sentence_builder(key_prefix="click")


with tab_live:
    col_camera_live, col_status_live = st.columns([1, 1])

    with col_camera_live:
        st.subheader("1. Show a sign — held steady, it auto-adds")
        st.caption(
            "Hold a handshape steady until the bar fills, then it's added "
            "automatically. Move your hand out of frame before repeating "
            "the same letter."
        )

        try:
            from streamlit_webrtc import webrtc_streamer
            from live_processor import LiveSignProcessor

            ctx = webrtc_streamer(
                key="sign-live",
                video_processor_factory=LiveSignProcessor,
                media_stream_constraints={
                    "video": {"width": {"ideal": 640}, "height": {"ideal": 480}},
                    "audio": False,
                },
                rtc_configuration={
                    "iceServers": [
                        {"urls": ["stun:stun.l.google.com:19302"]},
                    ]
                },
            )
        except ImportError:
            ctx = None
            st.warning(
                "Live mode requires `streamlit-webrtc`.",
                icon=":material/videocam_off:",
            )
        except Exception as e:
            ctx = None
            st.warning(
                f"Live mode unavailable: {e}. Use Click Mode instead.",
                icon=":material/videocam_off:",
            )

    with col_status_live:
        st.subheader("2. Live Status & Controls")

        # Fragment decorator continuously polls background WebRTC thread every 0.5s
        @st.fragment(run_every=0.5)
        def render_live_status_fragment():
            if ctx and hasattr(ctx, "video_processor") and ctx.video_processor:
                processor = ctx.video_processor

                # Poll and consume any pending letters committed by background thread
                new_letters = processor.collect_pending_letters()
                if new_letters:
                    for ltr in new_letters:
                        add_letter(ltr, processor.current_confidence)
                    st.toast(f"Auto-added letter: {' '.join(new_letters)}", icon="✅")
                    st.rerun()

                # Get live internal state safely
                with processor.lock:
                    cur_letter = processor.current_letter
                    cur_conf = processor.current_confidence
                    stable_cnt = processor.stable_count
                    hand_vis = processor.hand_visible
                    last_added = processor.last_added_display

                if hand_vis and cur_letter:
                    st.success(
                        f"Detected: **{cur_letter}** ({cur_conf:.0%})",
                        icon=":material/check_circle:",
                    )
                    progress_val = min(stable_cnt / float(STABILITY_FRAMES), 1.0)
                    st.progress(
                        progress_val,
                        text=f"Holding '{cur_letter}' steady ({stable_cnt}/{STABILITY_FRAMES} frames)...",
                    )
                elif hand_vis:
                    st.info(
                        "Hand detected — holding gesture...",
                        icon=":material/hand_gesture:",
                    )
                else:
                    st.caption("Show your hand clearly in front of the camera...")

                if last_added:
                    st.badge(f"Last auto-added letter: {last_added}", color="green")

        if ctx is None:
            st.info(
                "Live mode is not available in this environment. Use Click Mode.",
                icon=":material/info:",
            )
        elif not ctx.state.playing:
            st.info(
                "Click **START** on the video camera stream to begin.",
                icon=":material/play_circle:",
            )
        else:
            render_live_status_fragment()

        render_word_and_sentence_builder(key_prefix="live")


with tab_collect:
    col_collector_cam, col_collector_stats = st.columns([1, 1])

    with col_collector_cam:
        st.subheader("1. Position your hand sign in camera")
        st.caption("See yourself live in your browser camera below:")

        collect_img = st.camera_input(
            "Take a photo to capture landmarks for dataset",
            key="studio_camera",
        )

        target_letter = st.selectbox("Select target static letter:", ASL_LETTERS, key="studio_target_letter")
        st.caption("J and Z are intentionally excluded because this single-frame pipeline cannot validate their motion.")

        if collect_img is not None:
            c_bytes = collect_img.getvalue()
            c_bgr = bytes_to_bgr_image(c_bytes)
            c_landmarks, c_annotated = extract_landmarks_from_bgr(c_bgr)

            st.image(c_annotated, channels="BGR", caption="Landmarks Skeleton Overlay Preview")

            if c_landmarks is None:
                st.warning("No hand detected — adjust position or lighting.", icon=":material/warning:")
            else:
                if st.button(
                    f":material/save: Save Sample for Letter '{target_letter}'",
                    type="primary",
                    key="studio_save_btn",
                ):
                    save_training_sample(c_landmarks, target_letter)
                    st.toast(f"Saved sample for letter '{target_letter}' to dataset!", icon="✅")
                    st.rerun()

    with col_collector_stats:
        st.subheader("2. Dataset Summary & Retrain")

        if os.path.exists(LANDMARKS_CSV):
            dataset_df = pd.read_csv(LANDMARKS_CSV)
            total_samples = len(dataset_df)
            active_dataset_df = dataset_df[dataset_df["label"].isin(ASL_LETTERS)]
            unique_letters = active_dataset_df["label"].nunique() if not active_dataset_df.empty else 0

            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Total Dataset Samples", total_samples, border=True)
            with col_m2:
                st.metric("Active static letters covered", f"{unique_letters}/{len(ASL_LETTERS)}", border=True)

            if not dataset_df.empty:
                st.caption("Samples per active static letter in `data/landmarks.csv`:")
                counts = active_dataset_df["label"].value_counts().reset_index()
                counts.columns = ["Letter", "Samples"]
                st.dataframe(counts, hide_index=True)

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button(":material/model_training: Train Model Now", type="primary", key="retrain_btn"):
                        with st.spinner("Training Random Forest model..."):
                            from train_classifier import main as train_model
                            try:
                                train_model(model_out="model_candidate.pkl")
                                st.success(
                                    "Candidate model saved as `model_candidate.pkl`. The active model was preserved; "
                                    "review evaluation results before replacing it.",
                                    icon="🎉",
                                )
                            except Exception as ex:
                                st.error(f"Training failed: {ex}")

                with col_btn2:
                    if st.button(":material/delete_forever: Clear All Dataset Data", key="clear_dataset_btn"):
                        if os.path.exists(LANDMARKS_CSV):
                            os.remove(LANDMARKS_CSV)
                        st.toast("Cleared all dataset samples!", icon="🗑️")
                        st.rerun()
        else:
            st.info(
                "No samples collected yet. Take a photo on the left to start building your dataset!",
                icon=":material/info:",
            )


# ---------- Finalize: Gemini cleanup + speech ----------
st.subheader("3. Finish & speak")

with st.form("finish_form"):
    submitted = st.form_submit_button(
        ":material/record_voice_over: Finish sentence — clean up & speak",
        type="primary",
    )
    if submitted:
        raw = (st.session_state.sentence_buffer + st.session_state.current_word).strip()
        if not raw:
            st.warning(
                "Sign something first!",
                icon=":material/warning:",
            )
        else:
            st.session_state.raw_sentence = raw
            word_count = len(raw.split())
            with st.spinner("Cleaning up with Gemini..."):
                cleaned = clean_sentence(raw, word_count=word_count)
            st.session_state.final_sentence = cleaned
            audio = text_to_speech_bytes(cleaned)
            st.session_state.audio_bytes = audio
            st.session_state.sentence_buffer = ""
            st.session_state.current_word = ""

if st.session_state.final_sentence:
    with st.expander(
        ":material/compare_arrows: Raw fingerspelled input vs. cleaned sentence",
        expanded=True,
    ):
        col_raw, col_clean = st.columns(2)
        with col_raw:
            st.markdown("**Raw fingerspelled input**")
            st.code(st.session_state.raw_sentence, language=None)
        with col_clean:
            st.markdown("**Cleaned by Gemini**")
            st.code(st.session_state.final_sentence, language=None)

    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3")
    else:
        st.caption("Audio generation failed — check your internet connection.")

# ---------- Session history + analytics ----------
st.subheader("Session history")
if st.session_state.history_log:
    df = pd.DataFrame(st.session_state.history_log)

    col_table, col_chart = st.columns([3, 2])
    with col_table:
        st.data_editor(df, num_rows="dynamic")
    with col_chart:
        freq_df = df["letter"].value_counts().reset_index()
        freq_df.columns = ["Letter", "Count"]
        st.dataframe(
            freq_df,
            column_config={
                "Letter": st.column_config.TextColumn("Letter", width="small"),
                "Count": st.column_config.ProgressColumn(
                    "Frequency",
                    format="%d",
                    min_value=0,
                    max_value=int(freq_df["Count"].max()) if not freq_df.empty else 1,
                ),
            },
            hide_index=True,
        )
        st.caption("Letter frequency this session")
else:
    st.caption("No letters captured yet this session.")
