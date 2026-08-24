# Technical design

`app.py` owns Streamlit layout, form submission, state, buffers, and analytics. `hand_utils.py` caches MediaPipe and returns a 63-float normalized vector plus annotation. `classify.py` caches `model.pkl`, validates shape, and derives static UI labels. `live_processor.py` provides frame sampling, thresholding, stability detection, and thread-safe transfer.

Session state stores the word/sentence buffers, prediction/confidence, landmarks, annotation, audio, and history. Click Mode reuses its stored annotation rather than running MediaPipe twice. The finishing `st.form` prevents Gemini/gTTS calls on incidental reruns.

The checked-in `hand_landmarker.task` makes normal deployment deterministic. Resources use `st.cache_resource`; Gemini reads an optional `st.secrets` key and raw text remains available on failure. Streamlit Community Cloud can run the app from `CAPSTONE PROJECT/SIGN_BRIDGE/app.py`. WebRTC is STUN-only and can be network-limited. Candidate training preserves `model.pkl` and saves `model_candidate.pkl` for evaluation.
