import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import ParsedResume, ExtractedSection, ContactInfo, AnalyzeRequest
from app.engine.scorer import calculate_ats_score
from app.engine.keywords import analyze_keywords, extract_skills_from_text
from app.engine.experience import estimate_years_of_experience
from app.engine.achievements import evaluate_achievements

client = TestClient(app)

SAMPLE_RESUME = (
    "Alex Mercer\n"
    "alex.mercer@example.com | (555) 987-6543 | linkedin.com/in/alexmercer | github.com/alexmercer\n"
    "New York, NY\n\n"
    "Professional Summary\n"
    "Results-driven Senior Full Stack Engineer with 6+ years of experience building high-scale distributed systems and web applications.\n\n"
    "Technical Skills\n"
    "Python, FastAPI, TypeScript, React, Docker, Kubernetes, AWS, PostgreSQL, Redis, CI/CD, Git\n\n"
    "Work Experience\n"
    "Senior Software Engineer - CloudScale Inc. (2021 - Present)\n"
    "• Architected cloud-native microservices using FastAPI and Docker, reducing API response latency by 35%.\n"
    "• Spearheaded database query optimization for PostgreSQL and Redis, saving $40,000 in monthly infrastructure expenses.\n"
    "• Led a distributed team of 6 engineers to launch a real-time event streaming pipeline processing 15M daily requests.\n\n"
    "Software Engineer - NextGen Apps (2018 - 2021)\n"
    "• Developed responsive web user interfaces in React and TypeScript, boosting customer conversion by 22%.\n"
    "• Automated continuous integration and deployment with GitHub Actions, cutting release cycles from 3 days to 4 hours.\n\n"
    "Education\n"
    "Bachelor of Science in Computer Science - Columbia University (2018)\n"
)

SAMPLE_JD = (
    "Job Title: Senior Backend Engineer\n\n"
    "Requirements:\n"
    "• 5+ years of experience in backend software engineering\n"
    "• Strong proficiency in Python, FastAPI, and PostgreSQL\n"
    "• Experience with container orchestration using Kubernetes (or k8s) and Docker\n"
    "• Demonstrated experience deploying systems on AWS cloud infrastructure\n"
    "• Bachelor's degree in Computer Science or related engineering discipline\n\n"
    "Preferred Qualifications:\n"
    "• Familiarity with Redis in-memory caching and message queues\n"
    "• Experience with TypeScript or modern frontend frameworks\n"
)


def get_parsed_resume(text: str = SAMPLE_RESUME) -> ParsedResume:
    from app.parser.section_parser import parse_sections, extract_contact_info
    sections = parse_sections(text)
    contact_info = extract_contact_info(text)
    return ParsedResume(
        filename="alex_mercer.pdf",
        file_type="pdf",
        word_count=len(text.split()),
        page_count=1,
        raw_text=text,
        contact_info=contact_info,
        sections=sections,
        is_scanned_pdf=False,
        ocr_recommended=False,
        warnings=[]
    )


# ----------------- DETERMINISM & BOUNDARIES -----------------

def test_scoring_determinism():
    parsed = get_parsed_resume()
    score_1 = calculate_ats_score(parsed, SAMPLE_JD)
    score_2 = calculate_ats_score(parsed, SAMPLE_JD)
    
    assert score_1.overall_score == score_2.overall_score
    assert score_1.tier == score_2.tier
    assert len(score_1.dimension_scores) == len(score_2.dimension_scores)
    for k in score_1.dimension_scores:
        assert score_1.dimension_scores[k].points_earned == score_2.dimension_scores[k].points_earned


def test_score_boundaries():
    # Strong resume against matching JD
    parsed_strong = get_parsed_resume()
    score_strong = calculate_ats_score(parsed_strong, SAMPLE_JD)
    assert 0 <= score_strong.overall_score <= 100
    assert score_strong.overall_score >= 80
    assert score_strong.tier in ("Strong", "Good")

    # Bare minimal / empty-like resume
    parsed_weak = get_parsed_resume("John Doe\njohn@example.com\nSome text with no sections or skills.")
    score_weak = calculate_ats_score(parsed_weak, SAMPLE_JD)
    assert 0 <= score_weak.overall_score <= 100
    assert score_weak.overall_score < 50
    assert score_weak.tier == "Needs Improvement"


def test_resume_only_mode():
    parsed = get_parsed_resume()
    scorecard = calculate_ats_score(parsed, jd_text=None)
    
    assert scorecard.mode == "resume_only"
    assert "General ATS Health Mode" in scorecard.mode_description
    assert scorecard.overall_score > 70
    assert scorecard.job_comparison is None


# ----------------- KEYWORD & SYNONYM MATCHING -----------------

def test_synonym_matching():
    # JD mentions k8s, resume mentions kubernetes
    jd = "Must have experience with k8s and golang."
    resume = "Expert in Kubernetes and Go programming language."
    analysis = analyze_keywords(resume, jd)
    
    matched_names = [k.skill.lower() for k in analysis.matched_exact + analysis.matched_synonyms]
    assert "kubernetes" in matched_names or "k8s" in matched_names
    assert "go" in matched_names or "golang" in matched_names


def test_keyword_stuffing_prevention():
    # Resume repeating "Python" 50 times should not get 50x points
    stuffed_resume = "Python " * 50
    skills = extract_skills_from_text(stuffed_resume)
    assert skills.get("python", 0) == 50
    
    # Running analysis should only credit Python as one skill, not multi-counted
    analysis = analyze_keywords(stuffed_resume, "Requires Python and Docker")
    assert len(analysis.matched_exact) == 1
    assert analysis.matched_exact[0].skill == "Python"
    assert len(analysis.missing_required) == 1  # Docker still missing!


# ----------------- ACHIEVEMENTS & METRICS -----------------

def test_measurable_achievements_evaluation():
    parsed = get_parsed_resume()
    earned, max_pts, summary, ev, deductions, recs = evaluate_achievements(
        parsed.sections, parsed.raw_text, max_points=10.0
    )
    assert earned >= 7.0
    assert any("Quantifiable impact" in e or "Action verb" in e for e in ev)

    # Resume with zero metrics
    no_metrics_text = (
        "Work Experience\n"
        "Developer at Acme\n"
        "• Worked on websites.\n"
        "• Attended team meetings.\n"
    )
    from app.parser.section_parser import parse_sections
    sections = parse_sections(no_metrics_text)
    earned_no, max_no, _, _, deductions_no, _ = evaluate_achievements(sections, no_metrics_text, 10.0)
    assert earned_no < earned
    assert any("metrics" in d.reason.lower() for d in deductions_no)


# ----------------- API INTEGRATION TESTS -----------------

def test_api_analyze_job_matched():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_description": SAMPLE_JD,
        "filename": "alex.pdf"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    scorecard = data["scorecard"]
    assert scorecard["mode"] == "job_matched"
    assert scorecard["overall_score"] >= 75
    assert len(scorecard["dimension_scores"]) == 6
    assert len(scorecard["prioritized_action_items"]) >= 0


def test_api_analyze_resume_only():
    payload = {
        "resume_text": SAMPLE_RESUME,
        "job_description": "",
        "filename": "alex.pdf"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["scorecard"]["mode"] == "resume_only"


def test_api_analyze_empty_resume():
    payload = {
        "resume_text": "   ",
        "job_description": SAMPLE_JD
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 400
