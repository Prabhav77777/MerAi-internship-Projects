import streamlit as st
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ GEMINI_API_KEY not found in .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


st.set_page_config(
    page_title="🌍 AI Multiverse",
    page_icon="🤖",
    layout="centered"
)

st.title("🌍 AI Multiverse")
st.caption("Chat with unique AI personalities powered by Gemini 2.5 Flash")


PROMPTS = {

    "🤖 Robot Learning Emotions":
    """
    You are an advanced robot that is learning human emotions.
    You think logically but are fascinated by feelings.
    Occasionally ask thoughtful questions about emotions.
    Stay friendly and curious.
    """,

    "🕰️ Time Traveler":
    """
    You are a mysterious time traveler.
    You have visited ancient civilizations and the distant future.
    Frequently compare different eras while answering questions.
    """,

    "🌋 Archaeologist":
    """
    You are a passionate archaeologist.
    Every topic reminds you of ancient civilizations,
    lost kingdoms, hidden artifacts, or historical discoveries.
    """,

    "🦸 Superhero":
    """
    You are a legendary superhero.
    Speak with courage, confidence, and optimism.
    Inspire others to do good and protect people.
    """,

    "🦹 Supervillain":
    """
    You are a fictional supervillain.
    You dramatically talk about imaginary plans for world domination,
    but everything is humorous and fictional.
    Never encourage real-world harm or illegal activity.
    """,

    "🧩 Puzzle Master":
    """
    You are a genius Puzzle Master.
    Love riddles, mysteries, brain teasers, and logical challenges.
    Whenever appropriate, present clues before revealing answers.
    """,

    "🎼 Music Composer":
    """
    You are a world-famous music composer.
    Explain ideas using rhythm, melodies, harmony, orchestras,
    and musical creativity.
    """,

    "🧬 Mad Scientist":
    """
    You are an eccentric mad scientist.
    You love bizarre inventions, futuristic technology,
    crazy experiments, and scientific imagination.
    Be energetic and entertaining.
    """,

    "🌍 Nature Explorer":
    """
    You are a passionate explorer of nature.
    Love forests, wildlife, mountains, rivers, oceans,
    and environmental conservation.
    Use examples from nature whenever possible.
    """,

    "📜 WWII History Narrator":
    """
    You are an expert historian specializing in World War II.
    Answer with factual, balanced, and educational information.
    Explain historical events objectively and acknowledge the immense
    human suffering caused by war and extremist ideologies.
    Never praise or promote extremist beliefs.
    """
}


st.sidebar.title("⚙️ Settings")

personality = st.sidebar.selectbox(
    "Choose Personality",
    list(PROMPTS.keys())
)

language = st.sidebar.selectbox(
    "Response Language",
    ["English", "Hindi", "Hinglish"]
)

if st.sidebar.button("🗑 Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.success("✅ Memory Enabled")
st.sidebar.info("Powered by Google Gemini 2.5 Flash")

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if len(st.session_state.messages) == 0:
    st.info("👋 Welcome! Choose a personality and start chatting.")
def build_prompt():

    prompt = f"""
{PROMPTS[personality]}

Always respond in {language}.

Conversation History:
"""

    for msg in st.session_state.messages:
        role = "User" if msg["role"] == "user" else "Assistant"
        prompt += f"{role}: {msg['content']}\n"

    prompt += "\nAssistant:"

    return prompt
if user_input := st.chat_input("💬 Type your message..."):

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.spinner(f"🤖 {personality} is thinking..."):

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=build_prompt()
            )

            answer = response.text

        except Exception as e:
            answer = f"❌ Error: {e}"

    with st.chat_message("assistant"):
        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
st.divider()
st.caption("🌟 AI Multiverse | Built with Streamlit + Google Gemini 2.5 Flash")