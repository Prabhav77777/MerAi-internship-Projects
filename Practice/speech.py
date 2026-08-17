import streamlit as st
from streamlit_mic_recorder import speech_to_text

st.title("Speech to Text") 
user=speech_to_text(
    language="en",
    use_container_width=False,
    just_once=True,
    key="STT"
)
l=[]
if user:
    st.write(f"User said: {user}")