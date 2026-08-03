import requests as rq
import streamlit as st
st.title("Image Generation with AI")
st.sidebar.title("styles available")
style = st.sidebar.write("anime")
style = st.sidebar.write("cartoon")
style = st.sidebar.write("sketch")
style = st.sidebar.write("realistic")
prompt1=st.text_input("Enter your prompt for image generation:")
url1 = "https://image.pollinations.ai/prompt/" + prompt1+"style=anime"
response1 = rq.get(url1)

url2 = "https://image.pollinations.ai/prompt/" + prompt1+"style=cartoon"
response2 = rq.get(url2)

url3 = "https://image.pollinations.ai/prompt/" + prompt1+"style=sketch"
response3 = rq.get(url3)

url4 = "https://image.pollinations.ai/prompt/" + prompt1+"style=realistic"
response4 = rq.get(url4)
if st.button("Generate Image"):
    st.write("Generating images for the prompt: ", prompt1)
    with st.spinner("Generating image..."):
        if response1.status_code == 200:
            st.image(response1.content, caption="Anime Style")
        if response2.status_code == 200:
            st.image(response2.content, caption="Cartoon Style")
        if response3.status_code == 200:
            st.image(response3.content, caption="Sketch Style")
        if response4.status_code == 200:
            st.image(response4.content, caption="Realistic Style")
