import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

load_dotenv()

st.title("Resume Optimizer")

col1, col2 = st.columns(2)

with col1:

    # Upload PDF
    uploaded_file = st.file_uploader(
        "Upload your resume (PDF)",
        type=["pdf"]
    )

    # Or paste resume
    user_input = st.text_area(
        "Or paste your resume here"
    )

    # Extract text from PDF
    pdf_text = ""

    if uploaded_file is not None:

        with st.spinner("Extracting text from PDF..."):

            reader = PdfReader(uploaded_file)

            for page in reader.pages:

                text = page.extract_text()

                if text:
                    pdf_text += text + "\n"

        st.success("PDF text extracted successfully!")

    # Decide what text to send to Groq
    if pdf_text.strip():
        resume_text = pdf_text
    else:
        resume_text = user_input

    # Optimize button
    if st.button("Optimize Resume", key="optimize_resume"):

        if not resume_text.strip():

            st.warning(
                "Please upload a PDF or paste your resume."
            )

        else:

            with st.spinner("Optimizing your resume..."):

                client = Groq(
                    api_key=os.environ["GROQ_API_KEY"]
                )

                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",

                    messages=[
                        {
                            "role": "system",
                            "content": """
You are an expert resume writer and ATS optimization specialist.

Optimize the resume for job applications.

Rules:
- Do not invent any information.
- Do not invent experience, skills, projects, or achievements.
- Preserve all factual information.
- Improve grammar and professional wording.
- Make bullet points concise and achievement-oriented.
- Use strong action verbs.
- Optimize for ATS.
- Return ONLY the optimized resume.
"""
                        },
                        {
                            "role": "user",
                            "content": resume_text
                        }
                    ],

                    max_completion_tokens=2500
                )

                optimized_resume = response.choices[0].message.content

            # Display result
            with col2:

                st.subheader("Optimized Resume")

                with st.container(border=True):
                    st.text_area(
                        "Optimized Resume",
                        value=optimized_resume,
                        height=400
                    )