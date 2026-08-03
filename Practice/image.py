import streamlit as st

st.title("Image Generation with AI")
st.write("Welcome to the Image Generation app!")

st.sidebar.title("Settings")
st.sidebar.selectbox("Choose Art Style", ["Anime", "Realistic", "Cyberpunk", "Fantasy", "3D Render"])   
st.sidebar.slider("Select Image Size", 1, 100, 30)