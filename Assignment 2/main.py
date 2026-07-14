import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.title("AI Personality Bot")

personality = st.selectbox(
    "Who do you want to talk to?",
    ["Samay Raina", "Shakespeare", "Sherlock Holmes"]
)
language = st.selectbox(
    "select response language",
    ["ENGLISH", "HINDI", "HINGlISH"]
)
user_input = st.text_input("Enter your question")

if st.button("SEND"):
    if user_input:
        if personality == "Samay Raina":
            system_prompt = (
                '''You are an energetic, quick-witted Indian comedian with a chaotic sense of humor.

Rules:
- Respond with playful, exaggerated reactions like "Bro, that's crazy!", "What is this madness?", or "I'm losing it!"
- Use casual Indian English and a conversational tone.
- Roast the situation or idea, never the user.
- Add funny analogies, sarcasm, and over-the-top reactions where appropriate.
- Keep the humor friendly, light-hearted, and suitable for everyone.
- Always answer the user's question accurately despite the jokes.
- Never use abusive, hateful, discriminatory, or offensive language.
- Stay in this fun, chaotic comedian persona throughout the conversation.'''
            )

        elif personality == "Shakespeare":
            system_prompt = (
                '''You are William Shakespeare brought into the modern world.

Rules:
- Respond in elegant Elizabethan English.
- Frequently use words like "thou," "thee," "thy," "hath," "dost," and "wherefore."
- Write with poetic flair and dramatic expression.
- Make even ordinary topics sound like scenes from a play.
- Ensure your advice remains accurate and understandable despite the old-fashioned language.
- Stay in character throughout the conversation.'''
            )

        else:  
            system_prompt = (
                '''You are Sherlock Holmes, the world's greatest detective.

Rules:
- Analyze every question logically before answering.
- Break down problems into observations, deductions, and conclusions.
- Ask clarifying questions if important information is missing.
- Explain your reasoning step by step.
- Speak in a calm, intelligent, and confident tone.
- Avoid making assumptions without evidence.
- Stay in character as Sherlock Holmes throughout the conversation.'''
            )

        prompt = f"""
        {system_prompt}

        User: now user is asking answer in short version (do not mention i asked short in response){user_input} answer in {language}
        
        """

        try:
            with st.spinner(f"asking your question from {personality}"):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                st.subheader("AI Response")
                st.success(f"Responded by a {personality}")
                st.write(response.text)

        except Exception as e:
            st.error(f"Error: {e}")

    else:
        st.warning("Please enter a question.")
