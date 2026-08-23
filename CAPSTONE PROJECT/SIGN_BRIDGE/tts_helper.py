"""
tts_helper.py
Converts the cleaned sentence into speech audio using gTTS (Google
Text-to-Speech). Returns raw audio bytes so Streamlit can play it
straight from memory — no temp files needed on the deployed server.
"""

from gtts import gTTS
from io import BytesIO


def text_to_speech_bytes(text: str) -> bytes:
    tts = gTTS(text=text, lang="en")
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()