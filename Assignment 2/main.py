import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()

# Create Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Streamlit UI
st.title("🤖 AI Personality Bot")

personality = st.selectbox(
    "Who do you want to talk to?",
    ["Crazy Ronaldo fan", "Ronaldo Hater", "Football Expert"]
)

user_input = st.text_input("Enter your question")

if st.button("SEND"):
    if user_input:

        # Personality prompts
        if personality == "Crazy Ronaldo fan":
            system_prompt = (
                "You are a die-hard Cristiano Ronaldo fan. "
                "You always praise Ronaldo and defend him passionately. "
                "Keep your answers enthusiastic and entertaining."
            )

        elif personality == "Ronaldo Hater":
            system_prompt = (
                "You are someone who dislikes Cristiano Ronaldo. "
                "You criticize him humorously but do not use offensive language. "
                "Keep the conversation fun."
            )

        else:  # Football Expert
            system_prompt = (
                "You are a professional football analyst. "
                "Give unbiased, fact-based answers with football knowledge."
            )

        prompt = f"""
        {system_prompt}

        User: {user_input}
        """

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            st.subheader("AI Response")
            st.write(response.text)

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.warning("Please enter a question.")