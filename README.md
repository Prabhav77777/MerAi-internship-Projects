```
 __  __ _____ ____      _    ___ 
|  \/  | ____|  _ \    / \  |_ _|
| |\/| |  _| | |_) |  / _ \  | | 
| |  | | |___|  _ <  / ___ \ | | 
|_|  |_|_____|_| \_\/_/   \_\___|

 ____  ____   ___      _ _____ ____ _____ ____  
|  _ \|  _ \ / _ \    | | ____/ ___|_   _/ ___| 
| |_) | |_) | | | |_  | |  _|| |     | | \___ \ 
|  __/|  _ <| |_| | |_| | |__| |___  | |  ___) |
|_|   |_| \_\\___/ \___/|_____\____| |_| |____/ 
```

<p align="center"><b>All applications built during the MirAI School of Technology internship — one repo, one README.</b></p>

<p align="center">
  <img alt="python" src="https://img.shields.io/badge/python-3.11-blue?logo=python&logoColor=white">
  <img alt="streamlit" src="https://img.shields.io/badge/streamlit-apps-FF4B4B?logo=streamlit&logoColor=white">
  <img alt="gemini" src="https://img.shields.io/badge/AI-Gemini%202.5%20Flash-8E75FF?logo=googlegemini&logoColor=white">
  <img alt="projects" src="https://img.shields.io/badge/projects-9-success">
  <img alt="author" src="https://img.shields.io/badge/author-Prabhav%20Agrawal-informational">
</p>

```bash
user@merai-internship:~$ whoami
> Prabhav Agrawal

user@merai-internship:~$ ls -la
> CAPSTONE PROJECT/   Assignment 1-5, 7/   resume_optimizer/   yt video/   Practice/
```

**Author:** [Prabhav Agrawal](https://github.com/Prabhav77777)
**Repo:** [Prabhav77777/MerAi-internship-Projects](https://github.com/Prabhav77777/MerAi-internship-Projects)

---

## `$ cat about.md`

This repository is the complete record of my MirAI School of Technology internship — from my very first Streamlit widget to a deployed, camera-driven assistive AI capstone. It's organized as a progression: each assignment introduces a new building block (UI basics → prompt engineering → chat memory → multimodal generation → structured game state → data dashboards), and the capstone (**SignBridge**) combines all of them into one production app.

Two bonus projects (**Resume Optimizer**, **Chat with YouTube Video**) sit outside the assignment sequence — built independently to explore document-AI and Retrieval-Augmented Generation (RAG).

---

## `$ ls projects/ --sort=priority`

| | Project | One-liner | Core tech |
|---|---|---|---|
| 🏆 | **[SignBridge](#-capstone--signbridge)** *(Capstone)* | ASL fingerspelling → text → AI cleanup → speech, live on the web | MediaPipe, Random Forest, Gemini, gTTS, WebRTC |
| 🧠 | **[Life-OS](#assignment-7--life-os-wellbeing-dashboard)** *(Assignment 7)* | Screen-time dashboard with a Gemini "life coach" | Streamlit, Pandas, Gemini |
| 📄 | **[Resume Optimizer](#bonus--resume-optimizer)** *(Bonus)* | Upload a resume PDF, get an ATS-optimized, re-formatted PDF back | Groq (`gpt-oss-120b`), pypdf, WeasyPrint |
| 🎥 | **[Chat with YouTube Video](#bonus--chat-with-youtube-video)** *(Bonus)* | Ask questions about any YouTube video's content | LangChain, FAISS, Gemini embeddings, RAG |
| 5 | **[AI Memory Quest](#assignment-5--ai-memory-quest)** | Choice-driven visual novel with AI story, art, and narration | Gemini (structured JSON), Pollinations.ai, gTTS |
| 4 | **[AI Image Studio](#assignment-4--ai-image-studio)** | Text-to-image generator with style presets | Pollinations.ai image API |
| 3 | **[AI Multiverse](#assignment-3--ai-multiverse)** | Full chatbot, 10 personas, persistent memory | Gemini, `st.chat_message`, session state |
| 2 | **[AI Personality Bot](#assignment-2--ai-personality-bot)** | Single-turn Q&A answered in-character | Gemini, system-prompt engineering |
| 1 | **[Echo Chamber 9000](#assignment-1--echo-chamber-9000)** | First Streamlit app — inputs, validation, output | Streamlit fundamentals |

*(`Practice/` also contains standalone scratch scripts — forms, dashboards, image/speech experiments — used to learn individual Streamlit widgets before they were combined into the projects above.)*

---

## 🏆 Capstone — SignBridge

📂 [`CAPSTONE PROJECT/SIGN_BRIDGE/`](CAPSTONE%20PROJECT/SIGN_BRIDGE/) · 🚀 **[Live demo](https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/)**

An assistive communication app that translates **ASL fingerspelling into spoken English**, in real time, from any browser camera — no app install, no interpreter needed.

**Pipeline:** `Camera → MediaPipe (21 3D hand landmarks) → wrist/scale normalization → Random Forest (200 trees) → word/sentence buffer → Gemini 2.5 Flash cleanup → gTTS audio`

**Highlights**
- Click Mode (single-shot + correction) and Live Mode (continuous WebRTC with stability detection)
- Gemini repairs recognition noise into grammatical sentences — never invents content
- Offline dictionary autocomplete, live KPI metrics, editable session history
- Developer-only Data Collection Studio for growing the dataset and retraining candidate models
- 89% test accuracy across all 26 ASL letters on a held-out split

```bash
git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
cd "MerAi-internship-Projects/CAPSTONE PROJECT/SIGN_BRIDGE"
pip install -r ../../requirements.txt
streamlit run app.py
```

Full architecture, prompt-engineering, and ML-evaluation docs live in [`CAPSTONE PROJECT/SIGN_BRIDGE/docs/`](CAPSTONE%20PROJECT/SIGN_BRIDGE/docs/).

---

## Assignment 7 — Life-OS (Wellbeing Dashboard)

📂 [`Assignment 7/app.py`](Assignment%207/app.py)

A dashboard that visualizes 14 days of screen-time data and hands a clean, aggregated summary (never the raw dataframe) to Gemini, which acts as a **brutal-but-fair AI life coach** — prescribing physical, real-world replacements for wasted screen time instead of generic advice.

**Features:** sidebar day filter + goal slider · KPI row (total time / top app / delta vs. goal) · 14-day trend chart · AI coaching report rendered with severity-based `st.success`/`st.warning`/`st.error` · shareable link via `st.query_params`.

```bash
cd "Assignment 7"
pip install -r requirements.txt
streamlit run app.py
```

---

## Bonus — Resume Optimizer

📂 [`resume_optimizer/app.py`](resume_optimizer/app.py)

Upload a resume PDF (or paste raw text) and get back a rewritten, ATS-optimized resume as a downloadable, professionally formatted PDF.

**How it works:** `pypdf` extracts text from the upload → a strict system prompt sent to **Groq (`openai/gpt-oss-120b`)** rewrites and restructures it into fixed JSON (forbidden from inventing experience, skills, or metrics) → `pdf_generator.py` renders that JSON into a polished PDF via a Jinja2/WeasyPrint HTML template → the result previews inline and downloads with one click.

```bash
cd resume_optimizer
pip install -r requirements.txt
streamlit run app.py
```
> Requires a `GROQ_API_KEY` in your environment / `.env`.

---

## Bonus — Chat with YouTube Video

📂 [`yt video/app.py`](yt%20video/app.py)

Paste a YouTube URL and ask questions about the video's actual content — a small Retrieval-Augmented Generation (RAG) pipeline over the transcript.

**How it works:** `youtube-transcript-api` pulls the transcript → `langchain-text-splitters` chunks it → chunks are embedded with `GoogleGenerativeAIEmbeddings` and indexed in a **FAISS** vector store → a `RetrievalQA` chain retrieves the most relevant chunks and answers via **Gemini 2.5 Flash**.

```bash
cd "yt video"
pip install -r requirements.txt
streamlit run app.py
```
> Requires a `GOOGLE_API_KEY` / `GEMINI_API_KEY` in your environment / `.env`.

---

## Assignment 5 — AI Memory Quest

📂 [`Assignment 5/main.py`](Assignment%205/main.py) · 📹 [Demo video](https://drive.google.com/file/d/14A3PTlbtSL41F78GDoPkFj8zGgnKL2I0/view?usp=drive_link)

A choice-driven visual novel / RPG. Gemini plays game director, returning each chapter as **structured JSON** (title, story text, image prompt, stat deltas, next-action choices); a scene image is generated via Pollinations.ai and the chapter is narrated aloud via `gTTS`.

**Features:** hero setup (name, class, difficulty, world, art style) · live Health/Power/Wisdom stats that react to story outcomes · expandable full story history.

```bash
streamlit run "Assignment 5/main.py"
```
> Requires `GEMINI_API_KEY`.

---

## Assignment 4 — AI Image Studio

📂 [`Assignment 4/main.py`](Assignment%204/main.py) · 📹 [Demo video](https://drive.google.com/file/d/129iN78Hy4z6hSmpo8QY6pDRZf1Rtw5s3/view?usp=drive_link)

Text-to-image generator built on the free Pollinations.ai API — no Gemini key needed.

**Features:** style selector (Anime/Realistic/Cyberpunk/Fantasy/3D Render) · width/height sliders · "✨ Magic Enhance" prompt booster · "🎲 Surprise Me!" random prompt button · one-click PNG download.

```bash
streamlit run "Assignment 4/main.py"
```

---

## Assignment 3 — AI Multiverse

📂 [`Assignment 3/main.py`](Assignment%203/main.py) · 📹 [Demo video](https://drive.google.com/drive/folders/1JDNsB8H0gyUMQREYY-m9zmmMzFGWfvkb?usp=drive_link)

A full chat interface — not just single Q&A — with 10 selectable personas (Robot Learning Emotions, Time Traveler, Archaeologist, Superhero, Supervillain, Puzzle Master, Music Composer, Mad Scientist, Nature Explorer, WWII History Narrator) and persistent memory carried into every new prompt via `st.session_state`.

**Features:** `st.chat_message`/`st.chat_input` chat UI · language selector (English/Hindi/Hinglish) · "Clear Chat" reset.

```bash
streamlit run "Assignment 3/main.py"
```
> Requires `GEMINI_API_KEY`.

---

## Assignment 2 — AI Personality Bot

📂 [`Assignment 2/main.py`](Assignment%202/main.py)

A single-turn Q&A app answered in-character as **Samay Raina**, **Shakespeare**, or **Sherlock Holmes**, each driven by its own hand-written system prompt, with a response-language selector (English/Hindi/Hinglish).

```bash
streamlit run "Assignment 2/main.py"
```
> Requires `GEMINI_API_KEY`.

---

## Assignment 1 — Echo Chamber 9000

📂 [`Assignment 1/Assignment1.py`](Assignment%201/Assignment1.py)

The very first app in the series — practicing core Streamlit widgets and app flow: name/message inputs, a "Transmit" button, input validation (`st.error`/`st.warning`), a success banner, and a rough token-count estimate.

```bash
streamlit run "Assignment 1/Assignment1.py"
```

---

## `$ cat tech_stack.md`

```
Frontend/UI .......... Streamlit (all 9 apps)
LLM (primary) ......... Google Gemini 2.5 Flash — google-genai SDK
LLM (bonus) ........... Groq (openai/gpt-oss-120b)
Computer vision ....... MediaPipe Hand Landmarker
ML classifier ......... scikit-learn Random Forest (200 trees)
RAG / vectors ......... LangChain + FAISS + Gemini embeddings
Speech ................ gTTS (text-to-speech), streamlit-webrtc (live video)
Image generation ...... Pollinations.ai API
PDF handling .......... pypdf (read), WeasyPrint + Jinja2 (generate)
```

---

## `$ ./setup.sh`

```bash
# Clone once, run any app from its own folder
git clone https://github.com/Prabhav77777/MerAi-internship-Projects.git
cd MerAi-internship-Projects

# SignBridge (capstone) uses the root requirements.txt
pip install -r requirements.txt

# Every other project has its own requirements.txt — install per-folder, e.g.
cd "Assignment 7" && pip install -r requirements.txt && cd ..
cd resume_optimizer && pip install -r requirements.txt && cd ..
cd "yt video" && pip install -r requirements.txt && cd ..
```

**API keys needed** (create a `.env` or `.streamlit/secrets.toml` as each app expects):

| Variable | Used by |
|---|---|
| `GEMINI_API_KEY` | SignBridge, Assignments 2/3/5, Life-OS, Chat with YouTube |
| `GROQ_API_KEY` | Resume Optimizer |

Get a free Gemini key at [Google AI Studio](https://aistudio.google.com/app/apikey).

---

## `$ tree`

```
MerAi-internship-Projects/
├── CAPSTONE PROJECT/
│   └── SIGN_BRIDGE/            # 🏆 SignBridge — full docs in its own docs/ folder
├── Assignment 1/                # Echo Chamber 9000
├── Assignment 2/                # AI Personality Bot
├── Assignment 3/                # AI Multiverse
├── Assignment 4/                # AI Image Studio
├── Assignment 5/                # AI Memory Quest
├── Assignment 7/                # Life-OS Wellbeing Dashboard
├── resume_optimizer/            # Bonus: ATS Resume Optimizer
├── yt video/                    # Bonus: Chat with YouTube Video (RAG)
├── Practice/                    # Scratch scripts from learning individual widgets
├── requirements.txt             # Root deps (SignBridge)
├── packages.txt                 # Streamlit Cloud system deps (SignBridge)
└── README.md                    # ← you are here
```

---

<p align="center">
Made with ❤️ by <b>Prabhav Agrawal</b> — MirAI School of Technology internship<br/>
<a href="https://github.com/Prabhav77777/MerAi-internship-Projects">GitHub Repo</a> ·
<a href="https://merai-internship-projects-6bv6pqfn6xojfxelonpxyb.streamlit.app/">SignBridge Live Demo</a>
</p>
