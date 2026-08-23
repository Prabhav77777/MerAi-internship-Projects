"""
tts_helper.py
Converts the cleaned sentence into speech audio using gTTS (Google
Text-to-Speech). Returns raw audio bytes so Streamlit can play it
straight from memory — no temp files needed on the deployed server.
"""

from gtts import gTTS
from io import BytesIO


def text_to_speech_bytes(text: str) -> bytes | None:
    """Converts text to MP3 audio bytes. Returns None on failure
    (e.g. empty text or network error) instead of crashing."""
    if not text or not text.strip():
        return None

    try:
        tts = gTTS(text=text.strip(), lang="en")
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception:
        # gTTS requires internet — if it fails, the app should still work
        return None