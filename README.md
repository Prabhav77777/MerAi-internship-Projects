# MerAi Internship Projects

A collection of AI-powered applications built during my MerAI internship — featuring **SignBridge** (the final capstone project) alongside Assignments 1–5 exploring computer vision, machine learning, prompt engineering, multimodal AI, text-to-speech, and image generation.

**Author:** [Prabhav Agrawal](https://github.com/Prabhav77777)  
**Repo:** [Prabhav77777/MerAi-internship-Projects](https://github.com/Prabhav77777/MerAi-internship-Projects)  

---

## 🏆 Final Capstone Project: SignBridge

📂 [`CAPSTONE PROJECT/SIGN_BRIDGE/`](CAPSTONE%20PROJECT/SIGN_BRIDGE/)

**SignBridge — ASL Fingerspelling → Text → AI Cleanup → Speech**

An assistive communication web application that translates American Sign Language (ASL) fingerspelling into spoken English sentences in real-time.

### Key Features
- 📸 **Click Mode**: Photo-by-photo letter recognition with confidence feedback, correction mode, and offline word autocomplete suggestions.
- 📹 **Live Mode**: WebRTC video stream processor with stability detection (6-frame hold threshold) and automatic letter entry.
- 🎨 **Data Collection Studio**: Interactive camera studio for landmark collection, dataset inspection, candidate model training, and candidate deployment.
- 🤖 **Gemini AI Cleanup**: Powered by Google GenAI SDK (`google-genai`), turns raw fingerspelled letter sequences into natural, punctuated sentences.
- 🔊 **Text-to-Speech (gTTS)**: Converts cleaned sentences into audio bytes for immediate playback.
- 📊 **Session Analytics & Governance**: Real-time KPI metrics, editable session history log, and letter frequency visualization.

### Pipeline Architecture
`Camera → MediaPipe (21 3D Landmarks) → Wrist/Scale Normalization → Random Forest (200 trees) → Buffers → Gemini 2.0 Flash → gTTS Audio`

### Run SignBridge
```bash
git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
cd "MerAi-internship-Projects/CAPSTONE PROJECT/SIGN_BRIDGE"
pip install -r "../../requirements.txt"
streamlit run app.py
```

---

## Table of Contents

- [Overview](#overview)
- [Capstone Project: SignBridge](#-final-capstone-project-signbridge)
- [Assignment 1: Echo Chamber 9000](#assignment-1-echo-chamber-9000)
- [Assignment 2: AI Personality Bot](#assignment-2-ai-personality-bot)
- [Assignment 3: AI Multiverse](#assignment-3-ai-multiverse)
- [Assignment 4: AI Image Studio](#assignment-4-ai-image-studio)
- [Assignment 5: AI Memory Quest](#assignment-5-ai-memory-quest)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)

---

## Overview

| # | Project / Assignment | What it does | Core concept |
|---|----------------------|--------------|--------------|
| ⭐ | **[SignBridge (Capstone)](#-final-capstone-project-signbridge)** | Translates ASL fingerspelling into text & speech with Gemini cleanup | MediaPipe, Random Forest, Google GenAI SDK, gTTS, WebRTC |
| 1 | [Echo Chamber 9000](#assignment-1-echo-chamber-9000) | Takes a name & message, "transmits" it back, and estimates token count | Streamlit fundamentals |
| 2 | [AI Personality Bot](#assignment-2-ai-personality-bot) | Answers Q&A in a chosen persona (Samay Raina / Shakespeare / Sherlock) | System-prompt & persona engineering |
| 3 | [AI Multiverse](#assignment-3-ai-multiverse) | Full chatbot with 10 personas and conversation memory | Chat state management, persona design |
| 4 | [AI Image Studio](#assignment-4-ai-image-studio) | Generates AI images from text prompts with style/size controls | Image-generation APIs, UI controls |
| 5 | [AI Memory Quest](#assignment-5-ai-memory-quest) | Choice-driven visual novel/RPG with AI story, images, and audio | Structured JSON, multimodal output, game state |

---

## Assignment 1: Echo Chamber 9000

📂 [`Assignment 1/Assignment1.py`](https://github.com/Prabhav77777/MerAi-internship-Projects/blob/main/Assignment%201/Assignment1.py)

A simple "message transmitter" app used to practice core Streamlit widgets and app flow.

**Features**
- Name + message text inputs, submitted via a "Transmit" button
- Input validation with `st.error` / `st.warning` for missing fields
- Success banner echoing the message back to the user
- A rough token-count estimate for the message (`characters ÷ 4`)

**Run it**
```bash
streamlit run "Assignment 1/Assignment1.py"
```

---

## Assignment 2: AI Personality Bot

📂 [`Assignment 2/main.py`](https://github.com/Prabhav77777/MerAi-internship-Projects/blob/main/Assignment%202/main.py)

A Q&A app that answers a single question through **Gemini 2.5 Flash**, staying in character as one of three personas.

**Features**
- Persona selector: **Samay Raina**, **Shakespeare**, or **Sherlock Holmes** — each with its own hand-written system prompt
- Response language selector: English, Hindi, or Hinglish
- Concise-answer instruction baked into the prompt
- Try/except error handling around the API call

**Run it**
```bash
streamlit run "Assignment 2/main.py"
```
> Requires a `GEMINI_API_KEY` — see [Environment Variables](#environment-variables).

---

## Assignment 3: AI Multiverse

📂 [`Assignment 3/main.py`](https://github.com/Prabhav77777/MerAi-internship-Projects/blob/main/Assignment%203/main.py)

The most complete of the early apps: a full chat interface (not just single Q&A) with memory, built on **Gemini 2.5 Flash**.

**Personas available** 🤖 Robot Learning Emotions · 🕰️ Time Traveler · 🌋 Archaeologist · 🦸 Superhero · 🦹 Supervillain · 🧩 Puzzle Master · 🎼 Music Composer · 🧬 Mad Scientist · 🌍 Nature Explorer · 📜 WWII History Narrator

**Features**
- Persistent conversation memory via `st.session_state`, carried into every new prompt
- Sidebar controls: persona picker, language picker (English/Hindi/Hinglish), "Clear Chat" button
- Chat-style UI using `st.chat_message` / `st.chat_input`
- Graceful error display if the Gemini call fails

**Run it**
```bash
streamlit run "Assignment 3/main.py"
```
> Requires a `GEMINI_API_KEY` — see [Environment Variables](#environment-variables).

📹 **Demo video:** [Watch on Google Drive](https://drive.google.com/drive/folders/1JDNsB8H0gyUMQREYY-m9zmmMzFGWfvkb?usp=drive_link)

---

## Assignment 4: AI Image Studio

📂 [`Assignment 4/main.py`](https://github.com/Prabhav77777/MerAi-internship-Projects/blob/main/Assignment%204/main.py)

A text-to-image generator built with the free [Pollinations.ai](https://pollinations.ai/) image API — no Gemini key required.

**Features**
- Text prompt input, with a "🎲 Surprise Me!" button that picks a random built-in prompt
- Art style selector: Anime, Realistic, Cyberpunk, Fantasy, 3D Render
- Adjustable image width/height sliders (256–1024 px)
- Optional "✨ Magic Enhance" toggle that appends quality-boosting keywords to the prompt
- Generated image preview with a one-click PNG download button

**Run it**
```bash
streamlit run "Assignment 4/main.py"
```

📹 **Demo video:** [Watch on Google Drive](https://drive.google.com/file/d/129iN78Hy4z6hSmpo8QY6pDRZf1Rtw5s3/view?usp=drive_link)

---

## Assignment 5: AI Memory Quest

📂 [`Assignment 5/main.py`](https://github.com/Prabhav77777/MerAi-internship-Projects/blob/main/Assignment%205/main.py)

An AI-driven, choice-based visual novel / RPG powered by **Gemini 2.5 Flash**, with generated scene art and narrated audio for every chapter.

**Features**
- Hero setup: name, character class (Fire Mage, Knight, Cyber Warrior, Shadow Assassin), difficulty, story world, and art style
- Gemini generates each chapter as structured JSON (title, story text, image prompt, stat changes, and next-action options)
- Scene illustrations generated via the Pollinations.ai image API
- Chapter narration generated as audio using `gTTS` (Google Text-to-Speech)
- Live hero stats (Health / Power / Wisdom) that update based on story outcomes
- Expandable "Story History" log of all past chapters

**Run it**
```bash
streamlit run "Assignment 5/main.py"
```
> Requires a `GEMINI_API_KEY` — see [Environment Variables](#environment-variables).

📹 **Demo video:** [Watch on Google Drive](https://drive.google.com/file/d/14A3PTlbtSL41F78GDoPkFj8zGgnKL2I0/view?usp=drive_link)

---

## Tech Stack

- **Python 3**
- **[Streamlit](https://streamlit.io/)** — UI framework for all applications
- **[MediaPipe](https://mediapipe.dev/)** — 21 3D hand landmark extraction
- **[scikit-learn](https://scikit-learn.org/)** — Random Forest hand gesture classifier
- **[google-genai](https://pypi.org/project/google-genai/)** — official Google Gen AI SDK (Gemini 2.0 Flash)
- **[gTTS](https://pypi.org/project/gTTS/)** — text-to-speech narration
- **[pyspellchecker](https://pypi.org/project/pyspellchecker/)** — offline word autocomplete
- **[streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc)** — real-time video stream processing

---

## Getting Started

1. **Clone the repo**
   ```bash
   git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
   cd MerAi-internship-Projects
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your Gemini API key**
   Create `.streamlit/secrets.toml` inside `CAPSTONE PROJECT/SIGN_BRIDGE/` (or `.env` in root):
   ```toml
   GEMINI_API_KEY = "your_api_key_here"
   ```
   Get a free key from [Google AI Studio](https://aistudio.google.com/app/apikey).

5. **Run SignBridge Capstone**
   ```bash
   cd "CAPSTONE PROJECT/SIGN_BRIDGE"
   streamlit run app.py
   ```

---

## Project Structure

```
MerAi-internship-Projects/
├── CAPSTONE PROJECT/
│   └── SIGN_BRIDGE/               # 🤟 SignBridge Capstone Project
│       ├── app.py                 # Main Streamlit Application
│       ├── hand_utils.py          # MediaPipe landmark extraction & normalization
│       ├── classify.py            # Random Forest classifier inference
│       ├── constants.py           # Alphabet & motion sign configuration
│       ├── gemini_helper.py       # Google GenAI SDK sentence cleanup
│       ├── tts_helper.py          # gTTS text-to-speech audio synthesis
│       ├── word_suggest.py        # Offline word autocomplete
│       ├── live_processor.py      # WebRTC live video processor
│       ├── train_classifier.py    # Candidate model training script
│       ├── model.pkl              # Active production classifier
│       ├── image_sign.jpg         # ASL reference chart
│       └── docs/                  # Architecture & ML governance docs
├── Assignment 1/
│   └── Assignment1.py             # Echo Chamber 9000
├── Assignment 2/
│   └── main.py                    # AI Personality Bot
├── Assignment 3/
│   └── main.py                    # AI Multiverse
├── Assignment 4/
│   └── main.py                    # AI Image Studio
├── Assignment 5/
│   └── main.py                    # AI Memory Quest
├── requirements.txt               # Unified project dependencies
├── packages.txt                   # Streamlit Cloud system dependencies
└── README.md
```

---

Made with ❤️ by **[Prabhav Agrawal](https://github.com/Prabhav77777)**
