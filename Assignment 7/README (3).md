# 🧠 Life-OS — Wellbeing Dashboard

```
$ whoami
> life-os-dashboard

$ cat mission.txt
> Digital addiction is a modern epidemic.
> This tool doesn't just track your screen time — it coaches you off it.

$ ./run.sh --status
> [ONLINE] Streamlit dashboard: ACTIVE
> [ONLINE] Gemini AI coach: ACTIVE
> [ONLINE] 14-day dataset: LOADED
```

## > overview

Life-OS is a Streamlit dashboard that visualizes 14 days of screen time
data and hands it to Gemini, which acts as a **brutal-but-fair AI life
coach** — analyzing your habits and prescribing real-world, physical
replacements for wasted screen time instead of generic "use your phone
less" advice.

## > tech_stack

```
$ pip list | grep -E "streamlit|pandas|genai"
streamlit      >=1.38.0
pandas         >=2.2.0
google-genai   >=0.3.0
python-dotenv  >=1.0.1
```

## > features

```
[x] Sidebar filters — day selector + adjustable daily goal slider
[x] KPI row — total screen time / top app / delta vs. goal
[x] 14-day trend chart + per-category breakdown
[x] AI coach — aggregates data, sends to Gemini, renders markdown advice
[x] Severity-based UI (st.success / st.warning / st.error)
[x] Shareable accountability link via st.query_params
```

## > quickstart

```bash
$ git clone <your-repo-url>
$ cd life-os

$ python -m venv venv
$ source venv/bin/activate        # Windows: venv\Scripts\activate

$ pip install -r requirements.txt

$ cp .env.example .env
$ # edit .env and add your real GEMINI_API_KEY

$ streamlit run app.py
> Local URL: http://localhost:8501
```

## > project_structure

```
life-os/
├── app.py              # main Streamlit application
├── screentime.csv       # synthetic 14-day screen time dataset
├── requirements.txt      # dependencies
├── .env.example         # template — copy to .env, never commit .env
├── .gitignore
└── README.md
```

## > how_the_ai_coach_works

```
1. Raw CSV rows  ──►  summarize_day_for_ai()
                        │
                        ▼
                  aggregated JSON (category totals, top apps, goal delta)
                        │
                        ▼
2. build_coach_prompt()  ──►  Gemini (gemini-2.5-flash)
                        │
                        ▼
3. Markdown coaching report  ──►  rendered with st.success/warning/error
```

Gemini never sees the raw DataFrame — only a clean, aggregated summary.
This keeps prompts small, cheap, and focused on what actually matters.

## > deployment

```
$ # Streamlit Community Cloud
$ # 1. Push this repo to GitHub (public)
$ # 2. Go to share.streamlit.io → "New app" → select repo/app.py
$ # 3. Add GEMINI_API_KEY under App settings → Secrets:
$ #      GEMINI_API_KEY = "your_key_here"
$ # 4. Deploy
```

## > checklist

```
[x] requirements.txt included
[x] .env hidden via .gitignore before pushing
[x] terminal-style README
[x] st.columns used for professional layout
[x] AI reads CSV data and gives specific lifestyle advice
[ ] deployed to Streamlit Community Cloud  ← do this last
```

---

```
$ echo "built for MirAI School of Technology — AI Builder Track"
```
