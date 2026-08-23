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

SYSTEM_PROMPT = """\
You are a communication assistant embedded in SignBridge, an application \
that helps deaf or mute users communicate through ASL fingerspelling. \
The user spells words letter-by-letter in front of a webcam, and a \
machine-learning model recognizes each letter. You will receive the raw, \
concatenated text output from this recognition process.

Your job:
1. Reconstruct the most likely intended word(s) and sentence.
2. Correct obvious recognition errors (e.g. missing letters, or an \
   occasional wrong letter due to hand-detection noise).
3. Add proper punctuation and capitalization.
4. Preserve the user's original meaning — NEVER invent new content, \
   add information the user didn't spell, or elaborate beyond what \
   was spelled.
5. If the input is ambiguous, pick the most common everyday \
   interpretation rather than guessing at something unusual.
6. If the input is very short (one or two words), just clean those \
   words — don't expand them into a full sentence.

Respond with ONLY the cleaned sentence. No explanation, no preamble, \
no commentary.
"""


@st.cache_resource
def _get_model():
    """Configures Gemini and returns a GenerativeModel instance.
    Returns None if no API key is available."""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT,
        )
    except Exception:
        return None


def clean_sentence(raw_text: str, word_count: int = 0) -> str:
    """
    raw_text: the buffered fingerspelled string, e.g. "HELO HW ARE YOU"
    word_count: number of completed words in the sentence (used as context)
    returns: a cleaned, natural sentence, e.g. "Hello, how are you?"
    """
    model = _get_model()
    if model is None:
        st.info(
            "Gemini API key is not configured in `.streamlit/secrets.toml`. "
            "Displaying raw fingerspelled input directly.",
            icon=":material/info:",
        )
        return raw_text

    # Dynamic context helps Gemini understand the input better
    context_parts = [f'Raw fingerspelled input: "{raw_text}"']
    if word_count > 0:
        context_parts.append(
            f"(The user spelled {word_count} word(s) in this sentence.)"
        )

    prompt = "\n".join(context_parts)

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # If Gemini fails (quota, network, etc.), return raw text
        # so the app doesn't crash — user still sees their input
        st.warning(f"Gemini cleanup unavailable: {e}. Showing raw text.")
        return raw_text