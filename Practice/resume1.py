import streamlit as st
import requests
import os
st.title("resume optimizer")
user_input = st.text_area("paste your resume here")
if st.button("submit"):
    if user_input:
        with st.spinner("loading..."):
            url = "https://openrouter.ai/api/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {os.environ["RESUME_API"]}",
                "Content-Type": "application/json",
            }
            data = {
                "model": "openai/gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": f"optimize this resume for job application: {user_input}"
                    }
                ]
            }

            response = requests.post(url, headers=headers, json=data)
            st.write(response.json())
    else:
        st.toast("please enter your resume")




