# SignBridge 🤟

**ASL Fingerspelling → Text → AI Cleanup → Speech**

An assistive communication web application that translates American Sign Language (ASL) fingerspelling into spoken English sentences in real-time.

---

## 🚀 Live Demo

Live application deployed on Streamlit Community Cloud:  
👉 **[https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/](https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/)**

---

## 🎯 Problem Statement

People who communicate primarily using American Sign Language (ASL) fingerspelling often experience daily communication barriers when interacting with individuals who do not understand sign language. Traditional alternative communication methods—such as typing out words on a mobile phone or writing on paper—are often slow, inconvenient, and disruptive to natural conversational flow.

SignBridge addresses this challenge by providing an instant, computer vision-assisted fingerspelling recognition assistant. It detects static hand signs, builds words with intelligent autocomplete, cleans up recognition errors using Generative AI, and vocalizes full spoken sentences aloud.

*(Note: SignBridge is designed as an assistive communication prototype for static ASL fingerspelling recognition and is not a medical device.)*

---

## 💡 Solution

SignBridge combines real-time computer vision, machine learning classification, dictionary-backed word suggestions, large language model (LLM) sentence refinement, and text-to-speech synthesis into a single web application. 

The architecture enforces a strict, intentional separation of engineering responsibilities:

1. **MediaPipe Hand Landmarker**: Extracts 21 3D geometric hand keypoints from raw camera frames.
2. **Random Forest Classifier**: Classifies spatial hand landmark feature vectors into ASL letters.
3. **Application Logic & Buffers**: Manages current word and sentence buffers with offline dictionary prefix suggestions.
4. **Google Gemini LLM (`gemini-2.5-flash`)**: Reconstructs raw fingerspelled sequences into grammatically correct, natural sentences.
5. **Google Text-to-Speech (gTTS)**: Synthesizes the final cleaned text into audible spoken audio.

---

## ✨ Key Features

- 📸 **Click Mode**: Single-shot photo recognition with confidence feedback, visual landmark skeleton overlay, and manual correction controls.
- 📹 **Live Mode**: Real-time continuous video stream using `streamlit-webrtc` with automatic stability detection (6-frame hold threshold) and cooldown buffer.
- 💡 **Offline Word Suggestions**: Prefix-matching dictionary suggestions offering instant one-click word completion.
- 📝 **Interactive Sentence Builder**: Complete editing buffer supporting `End word`, `Backspace`, `Clear word`, and full `Reset`.
- 🤖 **Gemini AI Language Cleanup**: Powered by the modern `google-genai` SDK (`gemini-2.5-flash`), transforming noisy letter buffers into punctuated, natural sentences without inventing new information.
- 🔊 **Text-to-Speech (gTTS)**: Generates in-memory MP3 audio bytes for instant browser playback.
- 📊 **Session Analytics**: Real-time KPI metrics, letter frequency distributions, and interactive session history logs.
- 🎨 **Data Collection Studio**: Developer-facing tool (toggleable from the sidebar) for capturing landmark samples, inspecting dataset statistics, training candidate models (`model_candidate.pkl`), and deploying them to production (`model.pkl`).

---

## 🏗️ System Architecture

```
┌──────────────┐
│  Web Camera  │
└──────┬───────┘
       │ (Raw Video Frame)
       ▼
┌──────────────────────────────────────────────┐
│  MediaPipe Hand Landmarker (Tasks API)        │
│  (Detects 21 3D Hand Landmarks: x, y, z)     │
└──────┬───────────────────────────────────────┘
       │ (21 3D Coordinates)
       ▼
┌──────────────────────────────────────────────┐
│  Origin & Scale Normalization               │
│  (Wrist -> (0,0,0); Scaled by Middle MCP)    │
└──────┬───────────────────────────────────────┘
       │ (63 Floating-Point Feature Vector)
       ▼
┌──────────────────────────────────────────────┐
│  Random Forest Classifier (200 Trees)        │
│  (Predicts ASL Letter Label & Confidence)    │
└──────┬───────────────────────────────────────┘
       │ (Predicted Letter A–Z)
       ▼
┌──────────────────────────────────────────────┐
│  Word & Sentence Builder + Autocomplete      │
│  (Manages Word/Sentence Buffers)             │
└──────┬───────────────────────────────────────┘
       │ (Raw Text Sequence)
       ▼
┌──────────────────────────────────────────────┐
│  Google Gemini API (gemini-2.5-flash)        │
│  (Language Cleanup, Punctuation, Grammar)    │
└──────┬───────────────────────────────────────┘
       │ (Cleaned Natural Sentence)
       ▼
┌──────────────────────────────────────────────┐
│  gTTS Text-to-Speech Engine                  │
│  (Synthesizes MP3 Audio Bytes)               │
└──────┬───────────────────────────────────────┘
       │ (Audio Bytes)
       ▼
┌──────────────┐
│  Audio Speech│
└──────────────┘
```

---

## 🔄 How SignBridge Works

1. **Sign Selection**: The user selects a target sign and positions their hand in front of the camera (in either Click Mode or Live Mode).
2. **Landmark Extraction**: MediaPipe isolates the hand and extracts 21 keypoint locations $(x, y, z)$.
3. **Feature Preprocessing**: Coordinates are translated relative to wrist Landmark 0 $(0,0,0)$ and normalized for scale using the middle-finger MCP joint (Landmark 9).
4. **Machine Learning Inference**: The 63-element feature vector is fed to a 200-tree Random Forest classifier, producing a letter prediction (e.g., `"H"`) and confidence score.
5. **Word & Sentence Assembly**: The predicted letter is appended to the current word buffer. Word suggestions (e.g., `"Hello"`) appear automatically below the buffer.
6. **AI Sentence Cleanup**: When the user clicks **Finish sentence**, the accumulated raw text (e.g., `"HELO HW ARE YOU"`) is sent to Google Gemini with a targeted system prompt, returning `"Hello, how are you?"`.
7. **Audio Speech Playback**: gTTS converts the cleaned text into audio, allowing the browser to speak the sentence aloud.

---

## 🧠 Machine Learning Pipeline

- **Feature Representation**: MediaPipe outputs 21 3D coordinates $(x, y, z)$ per hand.
- **Normalization Methodology**:
  - **Translation Invariance**: Wrist coordinate $p_0 = (x_0, y_0, z_0)$ is subtracted from all 21 keypoints ($p_i - p_0$), grounding the hand's origin at $(0,0,0)$ regardless of where it appears in the camera frame.
  - **Scale Invariance**: All point coordinates are divided by the Euclidean distance between the wrist and the middle finger MCP joint $\|p_9 - p_0\|_2$, making predictions invariant to camera distance.
  - Result: A compact 63-numerical feature vector.
- **Random Forest Classifier**:
  - `RandomForestClassifier(n_estimators=200, random_state=42)`
  - Target Classes: 26 ASL alphabet letters (A–Z)
  - Train/Test Split: 80% training, 20% held-out test evaluation
- **Why Random Forest?**: Converting raw pixel images into 63 normalized geometric features reduces memory overhead, allows the classifier to train in seconds, requires zero GPU inference hardware, and executes deterministically on cloud CPU servers.

---

## 🤖 AI Integration & Prompt Engineering

SignBridge uses a hybrid architecture that separates vision-based ML classification from Generative AI language processing:

- **Local CV + Machine Learning (MediaPipe + Random Forest)**: Handles deterministic real-time visual gesture classification.
- **Generative AI (Google Gemini `gemini-2.5-flash`)**: Handles natural language reconstruction, grammar correction, and punctuation.

### Why This Architecture Was Chosen
- **Low Latency & High Speed**: Real-time frame classification happens locally/on-server in milliseconds without calling LLMs per frame.
- **Cost & Quota Efficiency**: LLM calls occur only when the user finishes a sentence, avoiding unnecessary API usage.
- **Targeted Utility**: Uses LLMs where they excel—understanding linguistic context, fixing vision typos, and adding punctuation.

### Prompt Engineering Strategy
Gemini is configured with a system instruction designed specifically for assistive fingerspelling:
- **Spelling Error Correction**: Fixes misrecognized adjacent letters (e.g., `"PRABHV"` → `"Prabhav"`).
- **Meaning Preservation**: Explicitly forbids inventing facts, adding unspelled information, or generating conversational filler.
- **Short Input Handling**: Preserves short single-word inputs without expanding them into artificial full sentences.
- **Fail-Soft Fallback**: If Gemini is unreachable or no API key is provided, SignBridge falls back directly to raw text without interrupting user communication.

---

## 📊 Model Evaluation

Metrics measured on a held-out test split (80/20 train/test) across the 2,708 dataset samples:

- **Dataset Size**: 2,708 samples (108 camera-captured + 2,600 standardized landmark samples)
- **Covered Classes**: 26 ASL letters (A–Z)
- **Classifier**: 200-Tree Random Forest
- **Overall Accuracy**: **89%**
- **Macro Average Precision**: **89%**
- **Macro Average Recall**: **89%**
- **Macro Average F1-Score**: **89%**

---

## 🎨 UI / UX

- **Dual Interaction Modes**: Click Mode for deliberate photo-by-photo recognition; Live Mode for continuous WebRTC stream capturing.
- **Visual Landmark Overlays**: Draws green skeleton connections and red keypoint nodes over hand gestures to provide visual feedback.
- **Confidence Metrics**: Displays realtime confidence percentages along with delta indicator updates.
- **Editable Session History**: Presents an interactive dataframe log of detected letters, timestamps, and confidence scores.
- **Developer Tools Sidebar Toggle**: Includes a `🛠️ Show Developer Tools` checkbox in the sidebar to reveal or hide the Data Collection Studio on demand.

---

## 🔐 Privacy & Security

- **Secure Secrets Management**: `GEMINI_API_KEY` is loaded securely via `st.secrets` from `.streamlit/secrets.toml`. No API keys are hardcoded or committed to GitHub.
- **In-Memory Camera Processing**: Camera frames are processed in-memory during application execution and are not stored unless explicitly saved in the developer studio.
- **Fail-Soft Resilience**: Third-party API failures (Gemini or gTTS) return raw text and do not crash the core application.

---

## ☁️ Deployment

- **Hosting Platform**: Streamlit Community Cloud
- **Live URL**: [https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/](https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/)
- **Entrypoint**: `CAPSTONE PROJECT/SIGN_BRIDGE/app.py`
- **Root Requirements File**: `/requirements.txt`
- **Deterministic File Loading**: Employs `Path(__file__).resolve().parent` pathing to ensure asset loading works across read-only cloud container filesystems.

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
├── train_classifier.py        # Random Forest model candidate training script
├── collect_data.py            # Landmark sample saving helper
├── model.pkl                  # Production Random Forest classifier
├── model_candidate.pkl        # Isolated candidate model for testing
├── hand_landmarker.task       # MediaPipe float16 model file (~7MB)
├── data/
│   └── landmarks.csv          # 2,708 landmark feature samples
├── docs/                      # Technical design & architecture documentation
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
   pip install -r "../../requirements.txt"
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

## ⚠️ Limitations

- **Static Fingerspelling Focus**: Optimized for static ASL alphabet fingerspelling (letters A through Z).
- **Motion-Based Signs**: Letters J and Z involve dynamic movement paths; static single-frame captures approximate these signs.
- **Lighting & Camera Quality**: Recognition accuracy depends on clear hand visibility and adequate background contrast.
- **Network Dependencies**: AI sentence cleanup (Gemini) and audio speech synthesis (gTTS) require active internet connectivity.
- **Assistive Prototype**: SignBridge is an assistive communication prototype and not a medical or legal translation device.

---

## 🔮 Future Improvements

- **Dataset Expansion**: Collect diverse hand landmark samples across varying lighting conditions and user demographics.
- **Temporal Motion Classification**: Integrate LSTM or 3D CNN models for dynamic ASL signs involving movement.
- **Offline Edge LLM Inference**: Explore local quantized SLMs (Small Language Models) for offline sentence cleanup.
- **Multi-Language TTS**: Support multi-language text-to-speech output options.

---

## 👨‍💻 Developer

**Prabhav Agrawal**  
*MerAI Internship Capstone Deliverable*  
GitHub Repository: [Prabhav77777/MerAi-internship-Projects](https://github.com/Prabhav77777/MerAi-internship-Projects)  
Live Demo: [Streamlit Community Cloud Deployment](https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/)
