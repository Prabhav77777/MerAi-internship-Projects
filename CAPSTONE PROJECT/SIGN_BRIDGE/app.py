"""
app.py
SignBridge — Fingerspelling-to-Speech Communication Assistant

Two capture modes, both feeding the same word/sentence buffer:
  - Click Mode: take a photo per letter, confirm/retry (most reliable).
               Wrong predictions can be corrected on the spot, and the
               correction is appended to data/landmarks.csv so the next
               training run learns from real mistakes.
  - Live Mode: continuous webcam feed, letter auto-detected on screen
               and auto-added once held steady for a moment

Pipeline after either mode:
  letters -> word (with offline suggestions) -> sentence
  -> Gemini cleans up the sentence -> gTTS speaks it aloud

Run locally with:  streamlit run app.py
"""

import csv
import os

import streamlit as st
import pandas as pd
from datetime import datetime

from hand_utils import extract_landmarks_from_bgr, bytes_to_bgr_image
from classify import predict_letter
from gemini_helper import clean_sentence
from tts_helper import text_to_speech_bytes
from word_suggest import suggest_words
from live_processor import LiveSignProcessor

from streamlit_webrtc import webrtc_streamer

st.set_page_config(page_title="SignBridge", page_icon="🤟", layout="wide")

LANDMARKS_CSV = "data/landmarks.csv"


def save_training_sample(landmarks, letter):
    """Appends a confirmed (or corrected) sample to the training CSV,
    so mistakes caught during testing/demo directly improve the next
    training run. Same format as collect_data.py writes."""
    if landmarks is None:
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
    "show_correction": False,
    "final_sentence": "",
    "audio_bytes": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------- Header ----------
st.title("🤟 SignBridge")
st.caption(
    "A fingerspelling-to-speech assistant for the deaf/mute community. "
    "Sign letters, build words with suggestions, and speak full sentences aloud."
)


def add_letter(letter, confidence):
    """Shared helper: both capture modes call this to append a letter."""
    st.session_state.current_word += letter
    st.session_state.history_log.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "letter": letter,
        "confidence": round(confidence, 2),
    })


def render_word_and_sentence_builder(key_prefix):
    """Shared UI: current word, suggestions, sentence buffer, controls.
    Used by both Click Mode and Live Mode so they share one buffer.
    key_prefix must be unique per call site (both tabs render every
    rerun, so widget keys would otherwise collide)."""
    st.divider()
    st.write("**Current word:**", st.session_state.current_word or "_(empty)_")

    if st.session_state.current_word:
        suggestions = suggest_words(st.session_state.current_word)
        if suggestions:
            st.caption("Suggestions (tap to complete the word):")
            sug_cols = st.columns(len(suggestions))
            for i, word in enumerate(suggestions):
                with sug_cols[i]:
                    if st.button(word, key=f"{key_prefix}_sug_{word}_{i}", use_container_width=True):
                        st.session_state.sentence_buffer += word + " "
                        st.session_state.current_word = ""
                        st.rerun()

    st.write("**Sentence so far:**", st.session_state.sentence_buffer or "_(empty)_")

    w1, w2, w3 = st.columns(3)
    with w1:
        if st.button("␣ End word", use_container_width=True, key=f"{key_prefix}_end_word"):
            if st.session_state.current_word:
                st.session_state.sentence_buffer += st.session_state.current_word + " "
                st.session_state.current_word = ""
    with w2:
        if st.button("🗑️ Clear word", use_container_width=True, key=f"{key_prefix}_clear_word"):
            st.session_state.current_word = ""
    with w3:
        if st.button("♻️ Reset sentence", use_container_width=True, key=f"{key_prefix}_reset_sentence"):
            st.session_state.sentence_buffer = ""
            st.session_state.current_word = ""
            st.session_state.final_sentence = ""
            st.session_state.audio_bytes = None


# ---------- Mode tabs ----------
tab_click, tab_live = st.tabs(["📸 Click Mode (reliable)", "🎥 Live Mode (continuous)"])

with tab_click:
    col_camera, col_status = st.columns([1, 1])

    with col_camera:
        st.subheader("1. Capture a letter")
        img_file = st.camera_input("Show a handshape and take a photo", key="click_camera")

        if img_file is not None:
            image_bytes = img_file.getvalue()
            bgr_image = bytes_to_bgr_image(image_bytes)
            landmarks, annotated = extract_landmarks_from_bgr(bgr_image)

            st.image(annotated, channels="BGR", caption="Detected hand landmarks")

            if landmarks is None:
                st.warning("No hand detected — try adjusting position/lighting.")
                st.session_state.last_prediction = None
                st.session_state.last_landmarks = None
            else:
                letter, confidence = predict_letter(landmarks)
                st.session_state.last_prediction = letter
                st.session_state.last_confidence = confidence
                st.session_state.last_landmarks = landmarks
                st.session_state.show_correction = False

    with col_status:
        st.subheader("2. Confirm & build")

        if st.session_state.last_prediction:
            m1, m2 = st.columns(2)
            m1.metric("Detected Letter", st.session_state.last_prediction)
            m2.metric("Confidence", f"{st.session_state.last_confidence:.0%}")

            st.caption("Was this correct? (Your answer also improves the model)")
            fb1, fb2 = st.columns(2)
            with fb1:
                if st.button("✅ Correct — Add Letter", use_container_width=True, key="add_click"):
                    add_letter(st.session_state.last_prediction, st.session_state.last_confidence)
                    save_training_sample(
                        st.session_state.last_landmarks,
                        st.session_state.last_prediction,
                    )
                    st.session_state.last_prediction = None
                    st.session_state.last_landmarks = None
            with fb2:
                wrong_clicked = st.button("❌ Wrong", use_container_width=True, key="wrong_click")

            if wrong_clicked:
                st.session_state.show_correction = True

            if st.session_state.get("show_correction"):
                correct_letter = st.selectbox(
                    "What letter was it actually?",
                    list("ABCDEFGHIKLMNOPQRSTUVWXY"),
                    key="correction_select",
                )
                if st.button("Save correction & add this letter", key="save_correction"):
                    add_letter(correct_letter, st.session_state.last_confidence)
                    save_training_sample(st.session_state.last_landmarks, correct_letter)
                    st.session_state.last_prediction = None
                    st.session_state.last_landmarks = None
                    st.session_state.show_correction = False
                    st.rerun()

        render_word_and_sentence_builder(key_prefix="click")

with tab_live:
    col_camera, col_status = st.columns([1, 1])

    with col_camera:
        st.subheader("1. Show a sign — held steady, it auto-adds")
        st.caption(
            "Hold a handshape steady until the bar fills, then it's added "
            "automatically. Move your hand out of frame before repeating "
            "the same letter."
        )
        ctx = webrtc_streamer(
            key="sign-live",
            video_processor_factory=LiveSignProcessor,
            media_stream_constraints={
                "video": {"width": {"ideal": 640}, "height": {"ideal": 480}},
                "audio": False,
            },
        )

    with col_status:
        st.subheader("2. Confirm & build")

        # Pull any letters the background video thread has auto-committed
        # since the last time Streamlit rendered, and show a clear
        # confirmation in the main UI (not just the video overlay).
        if ctx.video_processor:
            new_letters = ctx.video_processor.collect_pending_letters()
            if new_letters:
                for letter in new_letters:
                    add_letter(letter, ctx.video_processor.current_confidence)
                st.success(f"✅ Added: {' '.join(new_letters)}")
                st.rerun()

        if not ctx.state.playing:
            st.info("Click **START** on the camera to begin.")

        render_word_and_sentence_builder(key_prefix="live")

    st.info(
        "If the live feed feels unreliable on your network/browser, "
        "Click Mode is the safer fallback for your demo."
    )

# ---------- Finalize: Gemini cleanup + speech ----------
st.divider()
st.subheader("3. Finish & speak")

with st.form("finish_form"):
    submitted = st.form_submit_button("🎤 Finish Sentence → Clean up & Speak", use_container_width=True)
    if submitted:
        raw = (st.session_state.sentence_buffer + st.session_state.current_word).strip()
        if not raw:
            st.warning("Sign something first!")
        else:
            with st.spinner("Cleaning up with Gemini..."):
                cleaned = clean_sentence(raw)
            st.session_state.final_sentence = cleaned
            st.session_state.audio_bytes = text_to_speech_bytes(cleaned)
            st.session_state.sentence_buffer = ""
            st.session_state.current_word = ""

if st.session_state.final_sentence:
    with st.expander("Raw fingerspelled input vs. cleaned sentence", expanded=True):
        st.write("**Cleaned sentence:**", st.session_state.final_sentence)
    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3")

# ---------- History log ----------
st.divider()
st.subheader("Session history")
if st.session_state.history_log:
    df = pd.DataFrame(st.session_state.history_log)
    st.data_editor(df, use_container_width=True, num_rows="dynamic")
else:
    st.caption("No letters captured yet this session.")