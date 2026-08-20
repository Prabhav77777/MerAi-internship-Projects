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
