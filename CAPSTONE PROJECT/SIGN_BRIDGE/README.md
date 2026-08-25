# SignBridge 🤟

> **ASL Fingerspelling → Text → AI Cleanup → Speech**
> 
> An end-to-end accessibility solution converting American Sign Language (ASL) fingerspelling into natural spoken sentences.

---

## 🚀 Live Demo

Live application deployed on Streamlit Community Cloud:  
👉 **[https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/](https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/)**

---

## 🎯 Problem Statement

People who communicate primarily through ASL fingerspelling often face daily communication barriers when interacting with individuals who do not understand sign language. Traditional communication methods like typing on a phone or writing on paper can be slow and disruptive to natural conversation flow. 

SignBridge addresses this gap by providing an instant, vision-based fingerspelling recognition assistant that constructs full spoken sentences in real time.

*(Note: SignBridge is designed as an assistive communication prototype for static ASL fingerspelling recognition and is not a medical device.)*

---

## 💡 Solution

SignBridge combines real-time computer vision, machine learning classification, dictionary-backed word suggestions, large language model (LLM) sentence refinement, and text-to-speech synthesis into a single web application:

1. **Vision Recognition**: MediaPipe tracks 21 3D hand landmarks from a standard webcam stream.
2. **Gesture Classification**: A Random Forest classifier predicts the intended ASL fingerspelled letter.
3. **Interactive Sentence Builder**: Users build words and full sentences with offline prefix auto-completion.
4. **AI Language Cleanup**: Google Gemini transforms raw, fingerspelled letter sequences into grammatically correct, natural sentences.
5. **Speech Output**: gTTS (Google Text-to-Speech) vocalizes the final cleaned sentence aloud.

---

## ✨ Key Features

- **Click Mode**: Single-shot photo mode capturing hand landmarks reliably under diverse lighting conditions.
- **Live Mode**: Real-time continuous camera feed using `streamlit-webrtc` with automatic stability detection, frame sampling, and cooldown buffer.
- **Offline Word Suggestions**: Prefix-matching dictionary suggestions allowing one-click word completion.
- **Interactive Sentence Builder**: Supports backspace, clear word, end word, and full reset controls.
- **Gemini Language Refinement**: Custom system-prompted LLM that fixes missing/misrecognized letters, adds punctuation, and formats sentences without inventing new information.
- **Fail-Soft Speech Synthesis**: Generates in-memory MP3 audio via gTTS; falls back gracefully to raw text if offline.
- **Developer / Data Collection Studio**: Sidebar-toggleable studio for capturing new landmark samples, evaluating class balances, training isolated candidate models (`model_candidate.pkl`), and deploying them to production (`model.pkl`).
- **Session Analytics**: Displays confidence metrics, letter frequency distributions, and interactive history logs.

---

## 🏗️ Architecture

```
        📷 Web Camera Input
                 │
                 ▼
    🖐️ MediaPipe Hand Landmarker (Tasks API)
                 │  (21 3D Coordinates: x, y, z)
                 ▼
    📐 Origin & Scale Normalization
                 │  (Wrist = (0,0,0), scaled by middle MCP distance)
                 ▼
    🔢 63 Numerical Feature Vector
                 │
                 ▼
    🌲 Random Forest Classifier (200 trees)
                 │
                 ▼
    🔤 Predicted ASL Letter (A–Z)
                 │
                 ▼
    📝 Word & Sentence Buffer (with Offline Autocomplete)
                 │
                 ▼
    🤖 Google Gemini API (gemini-2.5-flash)
                 │  (System prompt + dynamic context)
                 ▼
    💬 Cleaned Natural Sentence
                 │
                 ▼
    🔊 gTTS (Google Text-to-Speech Engine)
                 │
                 ▼
    🔈 Audio Speech Output (.mp3)
```

---

## 🧠 Machine Learning Classification

- **Landmark Extraction**: MediaPipe HandLandmarker extracts 21 keypoints per hand in 3D space $(x, y, z)$.
- **Feature Preprocessing**:
  - **Translation Invariance**: Wrist coordinate (Landmark 0) is subtracted from all 21 keypoints, placing origin at $(0,0,0)$.
  - **Scale Invariance**: Keypoints are scaled by the distance between the wrist and middle-finger MCP joint (Landmark 9).
  - Output feature vector: 63 normalized floating-point numbers.
- **Classifier Architecture**: 
  - Model: `RandomForestClassifier(n_estimators=200, random_state=42)`
  - Input: 63 numerical features
  - Target Output: 26 ASL alphabet letters (A–Z)
- **Why Random Forest?**: Because feature extraction converts high-dimensional pixel images into 63 compact geometric features, Random Forest trains in seconds, requires no GPU inference acceleration, and runs reliably on cloud CPU servers.

---

## 🤖 AI Integration & Prompt Engineering

SignBridge maintains a strict functional separation between visual recognition and language processing:
- **Visual Recognition (MediaPipe + Random Forest)**: Handles spatial hand geometry and letter predictions.
- **Language Cleanup (Google Gemini `gemini-2.5-flash`)**: Handles grammar, punctuation, and recognition error correction.

### System Instruction Strategy

Gemini is configured with a strict system instruction to prevent hallucinations:
- **Reconstruct Intended Words**: Fixes missing letters and common OCR/vision typos.
- **Preserve Original Meaning**: Strictly forbidden from inventing facts or elaborating beyond spelled text.
- **Short Input Handling**: Preserves single-word inputs without forcing full sentence expansions.
- **Graceful Fallback**: If `GEMINI_API_KEY` is missing or network connectivity is lost, the application displays raw recognized text directly without crashing.

---

## 📊 Model Evaluation & Metrics

The current production model (`model.pkl`) is evaluated on a held-out test split (80% train, 20% test) across 2,708 dataset samples:

- **Dataset Size**: 2,708 samples (108 webcam-captured + 2,600 standardized landmark samples)
- **Classes**: 26 ASL letters (A–Z)
- **Overall Test Accuracy**: **89%**
- **Macro Average Precision**: **89%**
- **Macro Average Recall**: **89%**
- **Macro Average F1-Score**: **89%**

---

## 🔐 Privacy & Security

- **Secrets Management**: `GEMINI_API_KEY` is retrieved securely via `st.secrets` from `.streamlit/secrets.toml`. No API keys are hardcoded or committed to GitHub.
- **Local Browser Camera Processing**: Video frames are processed in-memory. Image data is not stored permanently unless explicitly saved in the Developer Data Collection Studio.
- **Fail-Soft Architecture**: External API failures do not halt the application.

---

## ☁️ Deployment

- **Hosting Platform**: Streamlit Community Cloud
- **Entrypoint**: `CAPSTONE PROJECT/SIGN_BRIDGE/app.py`
- **Root Requirements File**: `/requirements.txt`
- **Asset Loading**: Uses `Path(__file__).resolve().parent` relative paths for resilient deployment on read-only cloud container filesystems.

---

## ⚠️ Limitations

- **Static Fingerspelling Focus**: Designed primarily for static ASL alphabet fingerspelling.
- **Motion-Based Signs**: Letters J and Z involve dynamic movement paths; static single-frame captures approximate these signs.
- **Lighting & Camera Quality**: Recognition accuracy depends on clear hand visibility and adequate background contrast.
- **Network Dependencies**: AI sentence cleanup (Gemini) and audio generation (gTTS) require active internet access.

---

## 📁 Project Structure

```
CAPSTONE PROJECT/SIGN_BRIDGE/
├── app.py                     # Main Streamlit web application
├── classify.py                # Model loading & letter prediction helper
├── hand_utils.py              # MediaPipe HandLandmarker & skeleton drawing
├── live_processor.py          # WebRTC stream video frame processor
├── constants.py               # Shared target configuration & constants
├── gemini_helper.py           # Google GenAI SDK integration & cleanup
├── tts_helper.py              # gTTS audio generation helper
├── word_suggest.py            # Offline prefix dictionary auto-completion
├── train_classifier.py        # Random Forest model training script
├── collect_data.py            # Landmark sample saving helper
├── model.pkl                  # Production Random Forest classifier
├── model_candidate.pkl        # Isolated candidate model for testing
├── hand_landmarker.task       # MediaPipe float16 model file (~7MB)
├── data/
│   └── landmarks.csv          # 2,708 landmark feature samples
├── docs/                      # Architecture, ML evaluation, and design docs
└── tests/                     # Automated unittest suite
```

---

## 🛠️ Local Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
   cd "MerAi-internship-Projects/CAPSTONE PROJECT/SIGN_BRIDGE"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r ../../requirements.txt
   ```

3. **Set Up Gemini API Key (Optional)**:
   Create `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your_google_gemini_api_key"
   ```

4. **Run Application**:
   ```bash
   streamlit run app.py
   ```

5. **Run Tests**:
   ```bash
   python -m unittest discover tests
   ```

---

## 👨‍💻 Developer

**Prabhav Agrawal**  
*MerAI Internship Capstone Deliverable*  
GitHub Repository: [Prabhav77777/MerAi-internship-Projects](https://github.com/Prabhav77777/MerAi-internship-Projects)  
Live Demo: [Streamlit Community Cloud Deployment](https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/)
