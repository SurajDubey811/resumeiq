import fitz
import docx
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_RESUME = (
    "Jane Doe\njane@example.com | (555) 123-4567\n"
    "Work Experience\n"
    "• Develop test automation using Behave BDD.\n"
    "• Worked on database optimization.\n"
)


def test_export_pdf_with_accepted_changes():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "file_type": "pdf",
        "filename": "Jane_Doe_Resume.pdf",
        "target_format": "pdf",
        "accepted_changes": [
            {
                "original_text": "Develop test automation using Behave BDD.",
                "suggested_text": "Engineered test automation framework using Behave BDD, expanding coverage to 90%."
            }
        ]
    }
    response = client.post("/api/resumes/export", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "Jane_Doe_Resume_ATS_Optimized.pdf" in response.headers["content-disposition"]
    
    # Verify PDF content with PyMuPDF
    pdf_bytes = response.content
    assert pdf_bytes.startswith(b"%PDF-")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    extracted_text = "".join([page.get_text() for page in doc])
    doc.close()
    
    assert "Jane Doe" in extracted_text
    assert "Engineered test automation framework" in extracted_text
    assert "expanding coverage to 90%" in extracted_text


def test_export_docx_with_accepted_changes():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "file_type": "docx",
        "filename": "Jane_Doe_Resume.docx",
        "target_format": "docx",
        "accepted_changes": [
            {
                "original_text": "Worked on database optimization.",
                "suggested_text": "Spearheaded PostgreSQL database query optimization, reducing latency by 40%."
            }
        ]
    }
    response = client.post("/api/resumes/export", json=payload)
    assert response.status_code == 200
    assert "wordprocessingml.document" in response.headers["content-type"]
    assert "Jane_Doe_Resume_ATS_Optimized.docx" in response.headers["content-disposition"]
    
    # Verify DOCX content with python-docx
    docx_bytes = response.content
    doc = docx.Document(io.BytesIO(docx_bytes))
    full_text = "\n".join([p.text for p in doc.paragraphs])
    
    assert "Jane Doe" in full_text
    assert "Spearheaded PostgreSQL database query optimization" in full_text
    assert "reducing latency by 40%" in full_text

