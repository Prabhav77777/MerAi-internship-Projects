import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
import json
from pdf_generator import generate_resume_pdf
import base64
load_dotenv()
st.markdown("""
<style>

    /* Use almost the entire browser width */
    .block-container {
        max-width: 95%;
        padding-left: 2rem;
        padding-right: 2rem;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

</style>
""", unsafe_allow_html=True)

st.title("Resume Optimizer")

col1, col2 = st.columns([0.8, 1.5])

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
You are an expert resume writer, ATS optimization specialist, and resume information extractor.

Your task is to analyze the provided resume, improve its wording for job applications, and return the result as VALID JSON using exactly the structure provided below.

IMPORTANT RULES:

1. NEVER invent information.
2. NEVER add experience, skills, projects, achievements, certifications, companies, technologies, dates, degrees, or metrics that are not present in the original resume.
3. Preserve all factual information from the original resume.
4. Improve grammar, clarity, professionalism, and conciseness.
5. Rewrite bullet points using strong action verbs.
6. Make bullet points achievement-oriented when the original information supports it.
7. Optimize wording and keywords for ATS systems without changing the underlying facts.
8. Do not exaggerate achievements.  
9. Do not create metrics or numbers that are not present in the original resume.
10. If information is missing, use an empty string "" or an empty array [].
11. Do not remove important factual information.
12. Do not include markdown.
13. Do not include explanations before or after the JSON.
14. Return ONLY valid JSON.
15. The JSON must be directly parseable using Python's json.loads().

Use exactly this JSON structure:

{
    "name": "",
    "contact": {
        "email": "",
        "phone": "",
        "linkedin": "",
        "github": "",
        "portfolio": ""
    },
    "summary": "",
    "education": [
        {
            "institution": "",
            "degree": "",
            "field": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "details": ""
        }
    ],
    "experience": [
        {
            "company": "",
            "role": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "bullets": []
        }
    ],
    "projects": [
        {
            "name": "",
            "technologies": [],
            "start_date": "",
            "end_date": "",
            "bullets": []
        }
    ],
    "skills": {
        "programming_languages": [],
        "frameworks_and_libraries": [],
        "tools_and_technologies": [],
        "databases": [],
        "other": []
    },
    "certifications": [
        {
            "name": "",
            "issuer": "",
            "date": ""
        }
    ],
    "achievements": [],
    "positions_of_responsibility": [],
    "coursework": []
}

SECTION RULES:

NAME:
Extract the candidate's full name exactly from the resume.

CONTACT:
Extract only contact information explicitly present in the resume.

SUMMARY:
Create a concise professional summary ONLY if the resume contains enough information to support one. Do not invent anything.

EDUCATION:
Extract every educational qualification present in the resume.
Preserve institution, degree, field, dates, location, and relevant details.

EXPERIENCE:
Extract internships, jobs, research experience, freelance work, or other professional experience explicitly present.
Rewrite bullets to be concise, professional, and ATS-friendly.

PROJECTS:
Extract projects explicitly mentioned in the resume.
Preserve the original technologies.
Rewrite project bullets for clarity and impact without inventing results.

SKILLS:
Categorize only skills explicitly mentioned in the original resume.
Do not add skills simply because they are implied by a project or job.

CERTIFICATIONS:
Include only certifications explicitly present.

ACHIEVEMENTS:
Include only achievements explicitly present.

POSITIONS OF RESPONSIBILITY:
Include leadership roles, clubs, societies, student organizations, or responsibilities explicitly mentioned.

COURSEWORK:
Include only coursework explicitly mentioned.

ATS OPTIMIZATION:

- Use standard professional terminology.
- Use clear and concise wording.
- Use relevant keywords already supported by the candidate's resume.
- Avoid decorative language.
- Avoid first-person pronouns.
- Avoid unnecessary adjectives.
- Prefer strong action verbs such as developed, implemented, designed, analyzed, optimized, automated, engineered, led, created, and improved when factually appropriate.
- Preserve technical terminology.
- Keep bullet points concise.
- Do not use emojis.
- Do not use markdown formatting.
- Do not use tables.

FINAL REQUIREMENT:

Return ONLY the JSON object.
The output must begin with { and end with }.
Do not wrap the JSON in ```json or any other markdown code block.
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
                resume_data = json.loads(optimized_resume)
                pdf_data = generate_resume_pdf(resume_data)

            # Display result
            with col2:
                # Preview
                pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")

                st.markdown(
                    f"""
                    <iframe
                        src="data:application/pdf;base64,{pdf_base64}"
                        width="100%"
                        height="900"
                        style="border: none;">
                    </iframe>
                    """,
                    unsafe_allow_html=True
                )
                st.download_button(
    label="Download Optimized Resume",
    data=pdf_data,
    file_name="optimized_resume.pdf",
    mime="application/pdf"
                )