"""
gemini_helper.py
Handles the Gemini API call that turns raw fingerspelled letters into a
clean, natural sentence. This is the "AI Integration" piece of the rubric.

Setup:
    1. Get an API key from https://aistudio.google.com/
    2. In Streamlit Cloud: add it under Settings -> Secrets as:
           GEMINI_API_KEY = "your-key-here"
       Locally: create a .streamlit/secrets.toml file with the same line.
"""

import streamlit as st
import google.generativeai as genai

SYSTEM_PROMPT = """You are a communication assistant helping a deaf or \
mute user who is fingerspelling using ASL (American Sign Language). \
You will receive a raw, letter-by-letter string with possible minor \
recognition errors (e.g. missing letters, or an occasional wrong letter \
due to hand-detection noise).

Your job:
1. Reconstruct the most likely intended word(s)/sentence.
2. Correct obvious recognition typos using context.
3. Add proper punctuation and capitalization.
4. Preserve the original meaning — never invent new content or add \
information the user didn't spell.
5. If something is ambiguous, pick the most common/likely everyday \
interpretation.

Respond with ONLY the cleaned sentence. No explanation, no preamble.
"""


def clean_sentence(raw_text: str) -> str:
    """
    raw_text: the buffered fingerspelled string, e.g. "HELO HW ARE YOU"
    returns: a cleaned, natural sentence, e.g. "Hello, how are you?"
    """
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return raw_text  # graceful fallback if key isn't configured yet

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    prompt = f"Raw fingerspelled input: \"{raw_text}\""
    response = model.generate_content(prompt)

    return response.text.strip()