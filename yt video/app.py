import re
import streamlit as st
from dotenv import load_dotenv

from youtube_transcript_api import YouTubeTranscriptApi

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)

from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA

load_dotenv()

st.set_page_config(page_title="Chat with YouTube")

st.title("🎥 Chat with YouTube Video")

url = st.text_input("Paste YouTube URL")


def get_video_id(url):
    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?]+)",
        r"shorts/([^?]+)"
    ]

    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)

    return None


if url:

    video_id = get_video_id(url)

    if not video_id:
        st.error("Invalid YouTube URL")
        st.stop()

    try:

        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        text = " ".join(
            chunk["text"]
            for chunk in transcript
        )

        documents = [Document(page_content=text)]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        docs = splitter.split_documents(documents)

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )

        vector_db = FAISS.from_documents(
            docs,
            embeddings,
        )

        retriever = vector_db.as_retriever()

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
        )

        qa = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
        )

        st.success("Transcript Loaded!")

        question = st.text_input("Ask anything about the video")

        if question:

            with st.spinner("Thinking..."):

                answer = qa.run(question)

            st.subheader("Answer")

            st.write(answer)

    except Exception as e:

        st.error(str(e))