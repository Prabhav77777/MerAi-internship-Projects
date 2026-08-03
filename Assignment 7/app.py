"""
Life-OS — Wellbeing Dashboard
MirAI School of Technology | AI Builder Track Capstone

A Streamlit dashboard that visualizes daily screen time and uses the
Gemini API as a brutal-but-fair, holistic AI life coach.
"""

import os
import json
from datetime import datetime

import pandas as pd
import streamlit as st

# google-genai is optional at import time so the app doesn't crash
# if the key isn't configured yet — we handle that gracefully below.
try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Life-OS | Wellbeing Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #1a1d24;
        border: 1px solid #2a2e39;
        border-radius: 10px;
        padding: 15px 15px 10px 15px;
    }
    div[data-testid="stMetricLabel"] { font-size: 0.9rem; color: #9aa0ac; }
    h1, h2, h3 { font-family: 'Segoe UI', sans-serif; }
    .life-os-header {
        padding: 1rem 0 0.5rem 0;
        border-bottom: 1px solid #2a2e39;
        margin-bottom: 1.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────
# PHASE 1 — DATA PIPELINE
# ────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str = "screentime.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "⚠️ `screentime.csv` not found. Make sure it's in the same folder as `app.py`."
    )
    st.stop()

all_dates = sorted(df["Date"].unique())


# ────────────────────────────────────────────────────────────────────────
# PHASE 2 — SIDEBAR CONTROLS
# ────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 Life-OS")
    st.caption("Your personal wellbeing command center")
    st.divider()

    selected_date = st.selectbox(
        "📅 Select a day",
        options=all_dates,
        index=len(all_dates) - 1,  # default to most recent day
        format_func=lambda d: d.strftime("%A, %b %d"),
    )

    daily_goal_minutes = st.slider(
        "🎯 Daily screen time goal (minutes)",
        min_value=30,
        max_value=480,
        value=180,
        step=15,
        help="We'll compare today's actual usage against this goal.",
    )

    st.divider()
    st.caption("🤖 AI Coach Settings")
    coach_tone = st.select_slider(
        "Coach tone",
        options=["Gentle", "Balanced", "Brutal-but-fair"],
        value="Brutal-but-fair",
    )

    st.divider()
    api_key_present = bool(os.environ.get("GEMINI_API_KEY"))
    if api_key_present:
        st.success("Gemini API key detected ✅")
    else:
        st.warning("No `GEMINI_API_KEY` found in environment / `.env`")


# ────────────────────────────────────────────────────────────────────────
# HEADER
# ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="life-os-header">', unsafe_allow_html=True)
st.title("🧠 Life-OS: Wellbeing Dashboard")
st.caption(f"Showing insights for **{selected_date.strftime('%A, %B %d, %Y')}**")
st.markdown("</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────────────────────────────
# PHASE 2 — KPI ROW
# ────────────────────────────────────────────────────────────────────────
day_df = df[df["Date"] == selected_date]

total_minutes_today = int(day_df["Minutes_Used"].sum())
total_hours_today = round(total_minutes_today / 60, 1)

if not day_df.empty:
    top_app_row = day_df.loc[day_df["Minutes_Used"].idxmax()]
    top_app_name = top_app_row["App_Name"]
    top_app_minutes = int(top_app_row["Minutes_Used"])
else:
    top_app_name, top_app_minutes = "—", 0

delta_vs_goal = total_minutes_today - daily_goal_minutes

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="⏱️ Total Screen Time Today",
        value=f"{total_hours_today} hrs",
        delta=f"{total_minutes_today} min",
        delta_color="off",
    )

with col2:
    st.metric(
        label="📱 Most Used App",
        value=top_app_name,
        delta=f"{top_app_minutes} min",
        delta_color="off",
    )

with col3:
    st.metric(
        label="🎯 vs. Daily Goal",
        value=f"{daily_goal_minutes} min goal",
        delta=f"{delta_vs_goal:+d} min",
        delta_color="inverse",  # going OVER goal shows red — correct framing
    )

st.divider()


# ────────────────────────────────────────────────────────────────────────
# PHASE 2 — VISUALIZATIONS
# ────────────────────────────────────────────────────────────────────────
viz_col1, viz_col2 = st.columns([2, 1])

with viz_col1:
    st.subheader("📈 14-Day Screen Time Trend")
    daily_totals = (
        df.groupby("Date")["Minutes_Used"].sum().reset_index().sort_values("Date")
    )
    daily_totals = daily_totals.set_index("Date")
    st.bar_chart(daily_totals, y="Minutes_Used", color="#FF6B6B")

with viz_col2:
    st.subheader("🗂️ Today's Breakdown by Category")
    if not day_df.empty:
        cat_totals = day_df.groupby("Category")["Minutes_Used"].sum().sort_values(
            ascending=False
        )
        st.bar_chart(cat_totals, color="#4ECDC4")
    else:
        st.info("No usage recorded for this day.")

with st.expander("📊 See full category trend across all 14 days"):
    cat_trend = df.pivot_table(
        index="Date", columns="Category", values="Minutes_Used", aggfunc="sum"
    ).fillna(0)
    st.line_chart(cat_trend)

st.divider()


# ────────────────────────────────────────────────────────────────────────
# PHASE 3 — AI INTEGRATION
# ────────────────────────────────────────────────────────────────────────
st.subheader("🤖 Your AI Life Coach")


def summarize_day_for_ai(day_df: pd.DataFrame, goal_minutes: int) -> str:
    """
    PHASE 3, STEP 8 — The Data Bridge.
    Aggregates raw per-app rows into a compact, model-friendly JSON string.
    Gemini never sees the raw DataFrame — only this clean summary.
    """
    if day_df.empty:
        return json.dumps({"total_minutes": 0, "categories": {}, "top_apps": []})

    category_totals = (
        day_df.groupby("Category")["Minutes_Used"].sum().sort_values(ascending=False)
    )
    top_apps = (
        day_df.sort_values("Minutes_Used", ascending=False)
        .head(5)[["App_Name", "Category", "Minutes_Used"]]
        .to_dict(orient="records")
    )

    summary = {
        "total_minutes_used": int(day_df["Minutes_Used"].sum()),
        "daily_goal_minutes": goal_minutes,
        "over_goal_by_minutes": int(day_df["Minutes_Used"].sum() - goal_minutes),
        "minutes_by_category": category_totals.to_dict(),
        "top_5_apps": top_apps,
    }
    return json.dumps(summary, indent=2)


def build_coach_prompt(data_summary: str, tone: str) -> str:
    """
    PHASE 3, STEP 9 — The System Prompt.
    Instructs Gemini to act as a holistic life coach that suggests
    concrete, real-world replacement activities — not generic advice.
    """
    tone_instructions = {
        "Gentle": "Be warm, encouraging, and gentle. Focus on small wins.",
        "Balanced": "Be honest and direct, but supportive and constructive.",
        "Brutal-but-fair": (
            "Be blunt and unflinching about the numbers — call out wasted time "
            "directly and without sugar-coating — but always back it up with "
            "fair, specific, actionable advice. No empty scolding."
        ),
    }

    prompt = f"""
You are "Coach Life-OS," a holistic wellbeing and productivity coach embedded
inside a screen time dashboard. You are analyzing ONE user's screen time data
for a single day, summarized below as JSON.

TONE FOR THIS RESPONSE: {tone_instructions.get(tone, tone_instructions["Balanced"])}

DATA (aggregated, one row per category / top apps):
{data_summary}

Your job:
1. Give a short verdict (1-2 sentences) on how the day went relative to their goal.
2. Identify the ONE category that most deserves attention today, and say why.
3. This is the most important part: for the time-wasting category you flagged,
   suggest 2-3 SPECIFIC, REAL-WORLD physical replacement activities the user
   could swap that time for (e.g. not "exercise more" but "a 20-minute walk
   around the block" or "prepping tomorrow's lunch while a podcast plays").
   Tie the suggested activity's duration roughly to the minutes they could reclaim.
4. End with one small, concrete action they can take in the next hour.

Do NOT simply say "use your phone less." Be specific, be human, and reference
the actual numbers from the data. Keep the whole response under 180 words.
Format your response in Markdown with short paragraphs or a small bullet list.
"""
    return prompt.strip()


def get_severity_level(total_minutes: int, goal_minutes: int) -> str:
    """Determines how loud the UI callout should be."""
    if total_minutes <= goal_minutes:
        return "success"
    elif total_minutes <= goal_minutes * 1.3:
        return "warning"
    else:
        return "error"


def call_gemini_coach(prompt: str) -> str:
    """Sends the prompt to Gemini and returns the text response."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=500,
        ),
    )
    return response.text


data_summary_str = summarize_day_for_ai(day_df, daily_goal_minutes)

with st.expander("🔍 See the data Gemini actually receives"):
    st.code(data_summary_str, language="json")

if st.button("✨ Get My Coaching Report", type="primary", use_container_width=True):
    if not GENAI_AVAILABLE:
        st.error(
            "The `google-genai` package isn't installed. Run "
            "`pip install google-genai` and restart the app."
        )
    elif not os.environ.get("GEMINI_API_KEY"):
        st.error(
            "No `GEMINI_API_KEY` found. Add it to a `.env` file "
            "(`GEMINI_API_KEY=your_key_here`) or your environment variables."
        )
    else:
        with st.spinner("Coach is reviewing your day..."):
            try:
                prompt = build_coach_prompt(data_summary_str, coach_tone)
                ai_response = call_gemini_coach(prompt)

                severity = get_severity_level(total_minutes_today, daily_goal_minutes)
                if severity == "success":
                    st.success("🎉 Great job staying on track today!")
                elif severity == "warning":
                    st.warning("⚠️ A bit over your goal today — here's the breakdown.")
                else:
                    st.error("🚨 Significantly over your goal today. Time for a reset.")

                st.markdown("### 💬 Coach's Report")
                st.markdown(ai_response)

            except Exception as e:
                st.error(f"Something went wrong calling Gemini: {e}")

st.divider()


# ────────────────────────────────────────────────────────────────────────
# PHASE 4 — INNOVATION DELIVERABLE: THE "SHAREABLE" ACCOUNTABILITY LINK
# ────────────────────────────────────────────────────────────────────────
st.subheader("🔗 Accountability Partner Link")

st.query_params["date"] = selected_date.isoformat()
st.query_params["total_minutes"] = str(total_minutes_today)
st.query_params["goal"] = str(daily_goal_minutes)
st.query_params["status"] = "over" if delta_vs_goal > 0 else "under"

shared_status = (
    f"went **{abs(delta_vs_goal)} min over** their goal 😬"
    if delta_vs_goal > 0
    else f"stayed **{abs(delta_vs_goal)} min under** their goal 🎉"
)

st.info(
    f"This page's URL now encodes today's stats — copy it from your browser's "
    f"address bar and send it to an accountability partner. Anyone who opens it "
    f"will see: *\"On {selected_date.strftime('%b %d')}, this user {shared_status}\"*"
)

with st.expander("📎 What gets encoded in the shareable URL"):
    st.code(
        f"?date={selected_date.isoformat()}"
        f"&total_minutes={total_minutes_today}"
        f"&goal={daily_goal_minutes}"
        f"&status={'over' if delta_vs_goal > 0 else 'under'}",
        language="text",
    )

# If someone opens the app via a shared link, greet them with the shared stats
query_params = st.query_params
if "total_minutes" in query_params and "goal" in query_params:
    try:
        shared_total = int(query_params["total_minutes"])
        shared_goal = int(query_params["goal"])
        shared_date = query_params.get("date", "a recent day")
        st.caption(
            f"👀 Viewing shared stats: {shared_total} min used vs. a "
            f"{shared_goal} min goal on {shared_date}."
        )
    except (ValueError, TypeError):
        pass


# ────────────────────────────────────────────────────────────────────────
# FOOTER
# ────────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    f"Life-OS Dashboard · Built with Streamlit + Gemini · "
    f"Last data refresh: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
)
