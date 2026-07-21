import streamlit as st
import os
import json
import requests

from dotenv import load_dotenv
from google import genai
from PIL import Image
from io import BytesIO
from gtts import gTTS


load_dotenv()


st.set_page_config(
    page_title="AI Memory Quest",
    page_icon="⚔️",
    layout="wide"
)


@st.cache_resource
def get_client():

    key = os.getenv("GEMINI_API_KEY")

    if not key:
        st.error("Gemini API key missing")
        st.stop()

    return genai.Client(api_key=key)


client = get_client()


if "history" not in st.session_state:
    st.session_state.history = []

if "chapter" not in st.session_state:
    st.session_state.chapter = 1

if "current_story" not in st.session_state:
    st.session_state.current_story = None

if "started" not in st.session_state:
    st.session_state.started = False

if "hero" not in st.session_state:
    st.session_state.hero = {
        "name": "",
        "class": "",
        "health": 100,
        "power": 50,
        "wisdom": 50
    }



st.sidebar.title("⚔️ Hero Configuration")


name = st.sidebar.text_input(
    "Hero Name",
    "Prabhav"
)


hero_class = st.sidebar.selectbox(
    "Character Class",
    [
        "Fire Mage",
        "Knight",
        "Cyber Warrior",
        "Shadow Assassin"
    ]
)


difficulty = st.sidebar.selectbox(
    "Difficulty",
    [
        "Easy",
        "Normal",
        "Nightmare"
    ]
)


genre = st.sidebar.selectbox(
    "Story World",
    [
        "Fantasy Kingdom",
        "Cyber World",
        "Space Adventure",
        "Mystery Horror"
    ]
)


style = st.sidebar.selectbox(
    "Art Style",
    [
        "Anime",
        "Realistic",
        "Cinematic",
        "Dark Fantasy"
    ]
)



def generate_story(choice):

    hero = st.session_state.hero

    prompt = f"""

You are an AI game director.

Create an interactive visual novel.

Hero name:
{hero["name"]}

Hero class:
{hero["class"]}

Health:
{hero["health"]}

Power:
{hero["power"]}

Wisdom:
{hero["wisdom"]}

World:
{genre}

Difficulty:
{difficulty}

Art style:
{style}


Player action:
{choice}


Return only JSON.

Format:

{{
"chapter_title":"",
"story_text":"",
"image_prompt":"",
"emotion":"",
"stats_change":
{{
"health":0,
"power":0,
"wisdom":0
}},
"options":[
"choice 1",
"choice 2",
"choice 3"
]
}}

"""


    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        text = response.text

        text = text.replace("```json", "")
        text = text.replace("```", "")

        return json.loads(text)


    except Exception as e:

        st.error("Story generation failed")
        st.write(e)

        return None



def create_image(prompt):

    try:

        url = (
            "https://image.pollinations.ai/prompt/"
            + requests.utils.quote(prompt)
        )

        response = requests.get(
            url,
            timeout=20
        )

        return Image.open(
            BytesIO(response.content)
        )

    except:

        st.toast(
            "Image generation failed"
        )

        return None



def create_audio(text):

    try:

        file = "story.mp3"

        audio = gTTS(
            text=text,
            lang="en"
        )

        audio.save(file)

        return file

    except:

        st.toast(
            "Audio generation failed"
        )

        return None



def update_stats(data):

    for key,value in data.items():

        st.session_state.hero[key] += value


    if st.session_state.hero["health"] < 0:
        st.session_state.hero["health"] = 0



def show_story(data):

    st.session_state.history.append(data)


    st.subheader(
        "📖 " + data["chapter_title"]
    )


    st.write(
        data["story_text"]
    )


    image = create_image(
        data["image_prompt"]
    )

    if image:
        st.image(
            image,
            caption="AI Generated Scene"
        )


    audio = create_audio(
        data["story_text"]
    )

    if audio:
        st.audio(audio)



    update_stats(
        data["stats_change"]
    )


    st.divider()

    st.subheader(
        "Choose your next action"
    )


    for option in data["options"]:

        if st.button(option):

            story = generate_story(option)

            if story:

                st.session_state.chapter += 1
                st.session_state.current_story = story

            st.rerun()



st.title(
    "⚔️ AI Memory Quest"
)



hero = st.session_state.hero


st.sidebar.divider()

st.sidebar.write(
    "❤️ Health:",
    hero["health"]
)

st.sidebar.write(
    "⚔️ Power:",
    hero["power"]
)

st.sidebar.write(
    "🧠 Wisdom:",
    hero["wisdom"]
)



if not st.session_state.started:

    if st.button(
        "Begin Adventure 🚀"
    ):

        st.session_state.hero = {
            "name": name,
            "class": hero_class,
            "health": 100,
            "power": 50,
            "wisdom": 50
        }


        story = generate_story(
            "Start the adventure"
        )


        st.session_state.current_story = story
        st.session_state.started = True

        st.rerun()



if st.session_state.current_story:

    show_story(
        st.session_state.current_story
    )



with st.expander("📚 Story History"):

    for story in st.session_state.history:

        st.write(
            story["story_text"]
        )