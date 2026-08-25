# 🤟 SignBridge

**Fingerspelling → text → Gemini cleanup → speech.**

SignBridge is a browser-based ASL fingerspelling communication assistant built as an internship capstone project.

![Bundled ASL reference chart](image_sign.jpg)

## Quick Start

```bash
git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
cd "MerAi-internship-Projects/CAPSTONE PROJECT/SIGN_BRIDGE"
pip install -r "../../requirements.txt"
streamlit run app.py
```

---

## Key Features

- 📸 **Click Mode (Reliable)**: Photo-by-photo static recognition with instant visual feedback, confidence score, correction mechanism, and word autocomplete suggestions.
- 📹 **Live Mode (Continuous)**: WebRTC background streamer with stability detection (6-frame hold threshold) and auto-commit.
- 🎨 **Data Collection Studio**: Interactive camera interface for collecting gesture landmarks, viewing dataset statistics, training candidate models, and deploying candidates to production.
- 🤖 **Gemini AI Cleanup**: Natural language post-processing via Google GenAI SDK (`google-genai`), transforming raw fingerspelling into punctuated, natural sentences without hallucinating.
- 🔊 **Text-to-Speech**: gTTS audio generator returning in-memory MP3 bytes for immediate playback.
- 📊 **Session Analytics**: Persistent session log, editable history table, and live letter frequency progress bars.

---

## System Architecture

```
Camera Stream / Photo
        │
        ▼
MediaPipe Hand Landmarker (21 3D points)
        │
        ▼
Wrist-Relative & Scale Normalization (63 numeric features)
        │
        ▼
Random Forest Classifier (200 trees)
        │
        ▼
Word Buffer & Offline Suggestions (pyspellchecker)
        │
        ▼
Sentence Buffer ──► Gemini 2.0 Flash (google-genai SDK) ──► gTTS ──► Speech Audio
```

---

## Machine Learning Pipeline & Governance

- **Feature Vector**: 63 floats (21 hand joints $\times$ $x,y,z$), normalized relative to Landmark 0 (wrist) and scaled by wrist-to-middle-MCP distance.
- **Model Architecture**: Scikit-Learn `RandomForestClassifier` (200 trees).
- **Static vs. Motion Signs**: Static fingerspelling gestures (A–I, K–O) are active classification targets. Motion-based gestures (J and Z) are excluded from static prediction targets.
- **Candidate Workflow**: Data Collection Studio trains candidate models to `model_candidate.pkl`. Promoted models are deployed to active production `model.pkl` with automated resource cache invalidation (`load_model.clear()`).

---

## Configuration & Environment Variables

Gemini AI cleanup is optional. To enable Gemini cleanup locally, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

If no key is configured, SignBridge gracefully falls back to displaying raw fingerspelled text without crashing.

---

## Cloud Deployment (Streamlit Community Cloud)

1. Repository: `Prabhav77777/MerAi-internship-Projects`
2. Main file path: `CAPSTONE PROJECT/SIGN_BRIDGE/app.py`
3. Add `GEMINI_API_KEY` under **App Settings → Secrets**.
4. Hand landmark model (`hand_landmarker.task`) is bundled and loaded in-memory via `model_asset_buffer`, ensuring compatibility with read-only cloud filesystems.

---

Developer: **Prabhav Agrawal** · **MerAI Internship Capstone Deliverable**
