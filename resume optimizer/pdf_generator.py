from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


BASE_DIR = Path(__file__).resolve().parent

template_dir = BASE_DIR / "templates"

env = Environment(
    loader=FileSystemLoader(template_dir)
)


def generate_resume_pdf(resume_data):
    """
    Takes structured resume data and returns
    the generated resume as PDF bytes.
    """

    # Load HTML template
    template = env.get_template("resume.html")

    # Insert resume_data into the template
    html_content = template.render(
        resume=resume_data
    )

    # Convert HTML to PDF in memory
    pdf_buffer = BytesIO()

    HTML(
        string=html_content,
        base_url=str(BASE_DIR)
    ).write_pdf(
        pdf_buffer
    )

    pdf_buffer.seek(0)

    return pdf_buffer.getvalue()
if __name__ == "__main__":

    test_resume = {
        "name": "PRABHAV AGRAWAL",

        "contact": {
            "email": "prabhavagrawal2007@gmail.com",
            "phone": "+91 9257733977",
            "linkedin": "linkedin.com/in/prabhav-agrawal-479971378",
            "github": "github.com/Prabhav77777",
            "portfolio": ""
        },

        "summary": "B.Tech student in Computer Science and Applied Mathematics with strong foundations in Python, C++, backend development, and AI integration.",

        "education": [
            {
                "institution": "IIIT Delhi",
                "degree": "B.Tech",
                "field": "Computer Science and Applied Mathematics",
                "location": "Delhi, India",
                "start_date": "2025",
                "end_date": "2029",
                "details": "CGPA: 8.2/10"
            }
        ],

        "experience": [],

        "projects": [
            {
                "name": "AI Code Review Assistant",
                "technologies": [
                    "Python",
                    "FastAPI",
                    "JavaScript"
                ],
                "start_date": "",
                "end_date": "",
                "bullets": [
                    "Developed an AI-powered code review platform using LLM APIs.",
                    "Designed a RESTful backend using FastAPI.",
                    "Created a responsive web interface."
                ]
            }
        ],

        "skills": {
            "programming_languages": [
                "Python",
                "C++",
                "C",
                "JavaScript"
            ],
            "frameworks_and_libraries": [
                "FastAPI"
            ],
            "tools_and_technologies": [
                "Git",
                "GitHub",
                "VS Code"
            ],
            "databases": [],
            "other": [
                "Data Structures",
                "Algorithms"
            ]
        },

        "certifications": [],

        "achievements": [
            "Google Hack2Skills Prompt Wars Challenge 3 — AIR 108"
        ],

        "positions_of_responsibility": [
            "Member, BYLD – Software Development Club, IIIT Delhi"
        ],

        "coursework": [
            "Introduction to Python",
            "Data Structures & Algorithms"
        ]
    }

    pdf = generate_resume_pdf(test_resume)

    with open("test_resume.pdf", "wb") as file:
        file.write(pdf)

    print("PDF generated successfully!")