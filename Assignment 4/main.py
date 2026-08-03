import streamlit as st
import requests
import random
from PIL import Image
from io import BytesIO


st.set_page_config(
    page_title="AI Image Studio",
    page_icon="🎨"
)


st.title("🎨 AI Image Studio")


prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo",
    "A futuristic city floating above clouds",
    "A dragon sleeping inside an ancient library",
    "A robot exploring an underwater civilization"
]


st.sidebar.title("Image Settings")


art_style = st.sidebar.selectbox(
    "Art Style",
    [
        "Anime",
        "Realistic",
        "Cyberpunk",
        "Fantasy",
        "3D Render"
    ]
)


width = st.sidebar.slider(
    "Image Width",
    256,
    1024,
    512
)


height = st.sidebar.slider(
    "Image Height",
    256,
    1024,
    512
)


magic = st.sidebar.checkbox(
    "✨ Enable Magic Enhance"
)


prompt = st.text_input(
    "Enter your image prompt"
)


def generate_image(prompt):

    full_prompt = f"{prompt}, {art_style} style"

    if magic:
        full_prompt += (
            ", masterpiece, 8k resolution, "
            "highly detailed, trending on artstation, "
            "unreal engine 5 render"
        )


    url = (
        f"https://image.pollinations.ai/prompt/"
        f"{full_prompt}"
        f"?width={width}&height={height}"
    )


    try:

        response = requests.get(
            url,
            timeout=30
        )

        image = Image.open(
            BytesIO(response.content)
        )

        return image


    except:

        st.error(
            "Image generation failed"
        )

        return None



if st.button("Generate Image"):

    if prompt:

        image = generate_image(prompt)

        if image:

            st.session_state.image = image
            st.session_state.name = f"{art_style}_image.png"


if st.button("🎲 Surprise Me!"):

    random_prompt = random.choice(
        prompts
    )

    st.write(
        "Prompt:",
        random_prompt
    )

    image = generate_image(
        random_prompt
    )

    if image:

        st.session_state.image = image
        st.session_state.name = "surprise_image.png"



if "image" in st.session_state:

    st.image(
        st.session_state.image,
        caption="Generated Image"
    )


    buffer = BytesIO()

    st.session_state.image.save(
        buffer,
        format="PNG"
    )


    st.download_button(
        "Download Image",
        buffer.getvalue(),
        file_name=st.session_state.name,
        mime="image/png"
    )