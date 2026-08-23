```
   _____ _             ____       _     _            
  / ____(_)           |  _ \     (_)   | |             
 | (___  _  __ _ _ __ | |_) |_ __ _  __| | __ _  ___   
  \___ \| |/ _` | '_ \|  _ <| '__| |/ _` |/ _` |/ _ \  
  ____) | | (_| | | | | |_) | |  | | (_| | (_| |  __/  
 |_____/|_|\__, |_| |_|____/|_|  |_|\__,_|\__, |\___|  
            __/ |                          __/ |        
           |___/                          |___/         

 fingerspelling -> speech, for the deaf/mute community
```

## What this is

SignBridge lets a user fingerspell words letter-by-letter in front of a
webcam. Each captured photo is run through a hand-landmark detector, a
trained classifier predicts the letter, and once a full sentence is
spelled out, Gemini reconstructs it into natural, punctuated text —
which is then read aloud.

This is a **fingerspelling communication aid**, not a full sign-language
translator. Full ASL involves continuous motion, facial expression, and
grammar that static single-frame recognition can't capture — this tool
focuses on what's actually reliable: static handshape recognition + AI
language reconstruction.

## Architecture

```
 ┌─────────────┐   ┌────────────────┐   ┌───────────────┐
 │  Webcam      │──▶│  MediaPipe      │──▶│  Classifier    │
 │  (photo)     │   │  Hand Landmarks │   │  (RandomForest)│
 └─────────────┘   └────────────────┘   └───────┬───────┘
                                                  │ predicted letter
                                                  ▼
                                        ┌──────────────────┐
                                        │  Session buffer   │
                                        │  (word/sentence)  │
                                        └────────┬─────────┘
                                                  │ raw spelled text
                                                  ▼
                                        ┌──────────────────┐
                                        │   Gemini API      │
                                        │ (cleans sentence) │
                                        └────────┬─────────┘
                                                  │ clean sentence
                                                  ▼
                                        ┌──────────────────┐
                                        │   gTTS (speech)   │
                                        └──────────────────┘
```

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Collect training data (needs a real webcam, run locally)
```bash
python collect_data.py
```
Follow the on-screen prompts: show each letter's handshape, press
SPACE to capture, N for next letter, Q to stop early. Aim for at least
30-40 samples per letter.

### 3. Train the classifier
```bash
python train_classifier.py
```
This produces `model.pkl`, which the app loads at runtime.

### 4. Add your Gemini API key
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-key-here"
```
Get a key at https://aistudio.google.com/

### 5. Run the app
```bash
streamlit run app.py
```

## Deployment

Deployed on **Streamlit Community Cloud**. Add `GEMINI_API_KEY` under
the app's Settings → Secrets in the Cloud dashboard (same format as
`secrets.toml` above).

🔗 Live app: **[add your deployment link here]**

## Tech stack

- **Streamlit** — UI and app framework
- **MediaPipe** — hand landmark detection
- **scikit-learn** — letter classification (RandomForest)
- **Gemini API** — sentence reconstruction & cleanup
- **gTTS** — text-to-speech output
- **Pandas** — session history logging

## Limitations & honesty note

- Recognizes static fingerspelled letters (A-Y, excluding J/Z which
  require motion), not full ASL grammar or continuous signing.
- Classifier accuracy depends on the quality/diversity of training
  photos collected — more samples, varied lighting/angles = better
  results.
- Intended as an assistive communication tool and demo of the
  pipeline, not a certified accessibility product.

## Author

[Your name] — MirAI School of Technology, B.Tech Capstone Project