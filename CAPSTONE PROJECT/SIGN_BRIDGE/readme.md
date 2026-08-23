# 🤟 SignBridge — Fingerspelling-to-Speech Communication Assistant

A camera-based accessibility assistant that translates fingerspelled American Sign Language (ASL) gestures into text and spoken audio in real time, with AI-powered sentence cleanup using Google Gemini.

---

## 1. Problem Statement

Over 70 million deaf or hard-of-hearing individuals worldwide rely on sign language for daily communication. However, the vast majority of the general public does not understand sign language or fingerspelling. This creates significant communication barriers in everyday scenarios such as healthcare visits, customer service interactions, and social exchanges.

While full natural sign language involves continuous spatial motion, facial expressions, and complex grammar, **fingerspelling (spelling words letter-by-letter using static handshapes)** is a fundamental component of ASL used for names, technical terms, and everyday communication. 

---

## 2. Solution Overview

**SignBridge** bridges this accessibility gap by providing an easy-to-use, browser-accessible fingerspelling communication assistant:

1. **Captures** static hand gestures via a webcam (using single-letter photo capture or continuous live streaming).
2. **Detects & Normalizes** hand landmarks using MediaPipe Hand Landmarker (21 keypoints, 63 3D coordinate features).
3. **Classifies** the handshape into an ASL letter using a trained Random Forest classifier (24 classes: A–Y, excluding motion-based letters J and Z).
4. **Builds** words and sentences dynamically with real-time offline dictionary suggestions.
5. **Contextualizes & Cleans** raw fingerspelled text using **Google Gemini 2.0 Flash** to fix typos, add punctuation, and format natural sentences without hallucinating content.
6. **Converts** the finalized sentence into spoken English audio using Google Text-to-Speech (`gTTS`).
7. **Collects Human Feedback** by allowing users to correct misclassifications on the spot, appending corrected landmark samples to `data/landmarks.csv` for continuous model improvement.

---

## 3. Key Features

- **📸 Click Mode (Primary / Reliable)**: Single-frame capture per letter. High reliability, ideal for noisy environments, low bandwidth, or evaluation demos.
- **🎥 Live Mode (Continuous)**: Real-time background webcam stream with stability detection (holds letter for steady frames before auto-committing).
- **💡 Real-time Word Suggestions**: Instant offline word completion powered by dictionary prefix matching (`pyspellchecker`).
- **🤖 Gemini AI Sentence Reconstruction**: Transforms raw character sequences (e.g., `HELO HW ARE YOU`) into grammatically clean output (`Hello, how are you?`).
- **🎤 Integrated Text-to-Speech**: Generates MP3 audio directly in memory without temp files on the server.
- **🔄 Human-in-the-Loop Feedback**: Mispredicted letters can be corrected on the spot, saving landmark vectors back into `landmarks.csv` for future retraining.
- **📊 Session Analytics & Data Editor**: Displays historical predictions and live letter frequency bar charts using Pandas.

---

## 4. System Architecture & Data Flow

```
┌─────────────────┐       ┌──────────────────────┐       ┌─────────────────────┐
│  Webcam Input   │ ────> │ MediaPipe Landmarker │ ────> │  RandomForest ML    │
│  (Click/Live)   │       │ (21 points -> 63 3D) │       │ (24 ASL Classes)    │
└─────────────────┘       └──────────────────────┘       └──────────┬──────────┘
                                                                    │ predicted letter
                                                                    ▼
┌─────────────────┐       ┌──────────────────────┐       ┌─────────────────────┐
│  gTTS Engine    │ <──── │  Gemini 2.0 Flash    │ <──── │  Session Buffer     │
│ (Audio Output)  │       │ (Sentence Cleanup)   │       │  (Word / Sentence)  │
└─────────────────┘       └──────────────────────┘       └─────────────────────┘
```

### Module Responsibilities

| Module | Description |
| :--- | :--- |
| `app.py` | Main Streamlit interface, session state manager, dashboard layout, and tab navigation. |
| `classify.py` | Loads `model.pkl` once via `@st.cache_resource` and performs inference on 63-element feature vectors. |
| `hand_utils.py` | MediaPipe Tasks API integration, extracts 21 hand landmarks, applies wrist-relative origin normalization and scaling. |
| `live_processor.py` | `streamlit-webrtc` background thread video processor for frame sub-sampling and stability tracking. |
| `gemini_helper.py` | Gemini API client with strict system prompt to reconstruct sentences without hallucinating details. |
| `tts_helper.py` | Converts text string to in-memory MP3 audio bytes using `gTTS`. |
| `word_suggest.py` | Fast offline dictionary lookup for prefix autocompletion. |
| `collect_data.py` | CLI webcam tool to collect raw landmark CSV samples per letter. |
| `train_classifier.py` | Trains `RandomForestClassifier` on `data/landmarks.csv` and serializes `model.pkl`. |

---

## 5. Technology Stack

- **Frontend & App Framework**: Python 3.10+, Streamlit 1.62.0
- **Computer Vision**: OpenCV (`opencv-python-headless`), MediaPipe Tasks API (`mediapipe 0.10.x`)
- **Machine Learning**: `scikit-learn` (Random Forest Classifier), `joblib`, `numpy`
- **Generative AI**: `google-generativeai` (Gemini 2.0 Flash)
- **Audio Output**: `gTTS` (Google Text-to-Speech)
- **Data Wrangling**: `pandas`
- **Streaming**: `streamlit-webrtc` (WebRTC streaming for Live Mode)

---

## 6. How It Works: Detailed Pipeline

### 1. Hand Landmark Extraction & Normalization
- MediaPipe detects 21 keypoints on the hand in 3D space $(x, y, z)$.
- **Normalization**: To ensure scale and position invariance (so hand distance/location in frame doesn't alter predictions):
  1. Wrist (Landmark 0) is set as origin: $\vec{P}'_i = \vec{P}_i - \vec{P}_0$.
  2. Scale is normalized by distance to Landmark 9 (middle finger MCP joint): $\vec{P}''_{i} = \frac{\vec{P}'_i}{\|\vec{P}'_9\|}$.
- Output is a flat 63-element vector $(x_0, y_0, z_0, \dots, x_{20}, y_{20}, z_{20})$.

### 2. Machine Learning Letter Classification
- The normalized vector is passed to a Random Forest Classifier trained with 200 trees.
- Returns predicted letter class and class probability (confidence score).

### 3. Word & Sentence Buffer
- Single letters build a word buffer.
- `pyspellchecker` queries the current prefix and returns top candidate completions.
- Completed words are appended to the sentence buffer.

### 4. Gemini AI Cleanup
- When "Finish Sentence" is pressed, the raw string (e.g. `MY NME IS PRABHV`) is sent to Gemini 2.0 Flash.
- **System Prompt**: Enforces strict persona as an ASL communication assistant. Prevents creative hallucination, retains user intent, adds proper punctuation and casing.

### 5. Text-to-Speech
- Cleaned text is rendered to MP3 audio bytes using `gTTS` and played via `st.audio`.

---

## 7. Installation & Local Setup

### Prerequisites
- Python 3.10 or higher
- Webcam connected to your computer

### 1. Clone Repository
```bash
git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
cd "CAPSTONE PROJECT/SIGN_BRIDGE"
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Secrets (Gemini API Key)
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```
*(Get a free API key from [Google AI Studio](https://aistudio.google.com/))*

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```
App will open automatically at `http://localhost:8501`.

---

## 8. Dataset & Model Details

- **Dataset**: `data/landmarks.csv` contains 63 numerical features per sample plus a target `label`.
- **Classes**: 24 static ASL letters (`A, B, C, D, E, F, G, H, I, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y`).
- **Model**: `RandomForestClassifier` (`n_estimators=200`, `random_state=42`).
- **Evaluation Accuracy**: ~97% test accuracy on balanced landmark dataset.

---

## 9. Gemini AI Role & Prompt Engineering

Gemini is **NOT** used for sign recognition (computer vision is handled locally by MediaPipe + scikit-learn). 

Gemini's specific role is **post-processing sentence contextualization**:
- Reconstructs noisy fingerspelled character streams.
- Corrects letter-level typos caused by camera noise.
- Infers spacing, capitalization, and punctuation.
- Strictly prohibited from inventing information beyond what was spelled.

---

## 10. Deployment Details

- **Platform Target**: Streamlit Community Cloud.
- **Secrets Management**: Configured securely via Streamlit Cloud Secrets Manager (`GEMINI_API_KEY`).
- **WebRTC / TURN Configuration**: Live mode is pre-configured with Google STUN servers (`stun:stun.l.google.com:19302`). Click Mode is available as a 100% reliable fallback.

---

## 11. Limitations & Technical Honesty

- **Static Fingerspelling Only**: SignBridge recognizes static single-letter handshapes (A–Y). It does **not** recognize dynamic full-body ASL signs or motion-based letters (J and Z).
- **Lighting & Camera Dependency**: Hand landmark quality depends on adequate lighting and clear contrast between hand and background.
- **Scope**: Designed as an assistive communication prototype and educational capstone project, not a medical or certified translation device.

---

## 12. Author & Acknowledgments

- **Developer**: Prabhav
- **Project**: Internship Final Capstone Project
- **Institution / Program**: MerAI Internship Program