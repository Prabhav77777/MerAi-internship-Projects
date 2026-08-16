import streamlit as st
from dotenv import load_dotenv 
import os
from google import genai

st.title("Chat History with AI")

st.write('created by prabhav')

load_dotenv()  # Load environment variables from .env file

@st.cache_resource
def get_client():
    return genai.Client(api_key=os.getenv("GENAI_API_KEY"))
client = get_client()

if "msg" not in st.session_state:
    st.session_state.msg = []


if "gemini_chat" not in st.session_state:
    st.session_state.gemini_chat = client.chats.create(model="gemini-2.5-flash")

for message in st.session_state.msg:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(f"{message['content']}")
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.write(f"{message['content']}")

user_input = st.chat_input("Enter your message:")
if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.msg.append({"role": "user", "content": user_input})

    with st.spinner("AI is thinking..."):
        try:
            response = st.session_state.gemini_chat.send_message(user_input)
        except Exception as e:
            ai_response = f"❌ Error: {e}"

    with st.chat_message("ai"):
        st.markdown(response.text)

    st.session_state.msg.append({"role": "assistant", "content": response.text})

output="chat history"
for message in st.session_state.msg:
    output += f"\n{message['role']}: {message['content']}"
st.sidebar.title("Chat History Options")
st.sidebar.download_button(
    label="Download Chat History",
    data=output,
    file_name="chat_history.txt",
    mime="text/plain"
)
if st.sidebar.button("Clear Chat History"):
    st.session_state.msg = []
    









 
