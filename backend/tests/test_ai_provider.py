import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ai.mock_provider import LocalRuleBasedRewriter
from app.ai.gemini_provider import GeminiAIProvider
from app.models.schemas import ExtractedSection, ImproveRequest

client = TestClient(app)

SAMPLE_BULLETS_TEXT = (
    "Work Experience\n"
    "Software Engineer - Acme Corp\n"
    "• Responsible for building internal APIs and databases.\n"
    "• Worked on user authentication and session management.\n"
    "• Assisted with cloud migration to AWS.\n"
)


@pytest.mark.asyncio
async def test_local_rewriter_passive_verb_transformation():
    rewriter = LocalRuleBasedRewriter()
    suggestions = await rewriter.suggest_improvements(SAMPLE_BULLETS_TEXT)
    
    assert len(suggestions) > 0
    # Check that passive starters were replaced
    suggested_texts = [s.suggested_text for s in suggestions]
    assert any("Spearheaded" in text for text in suggested_texts)
    assert any("Engineered" in text for text in suggested_texts)
    assert any("Collaborated" in text or "Delivering" in text for text in suggested_texts)
    assert all(s.category is not None for s in suggestions)
    assert all(s.rationale is not None for s in suggestions)


@pytest.mark.asyncio
async def test_local_rewriter_no_hallucinations():
    rewriter = LocalRuleBasedRewriter()
    suggestions = await rewriter.suggest_improvements(SAMPLE_BULLETS_TEXT)
    
    # Should not introduce fake companies or fake degrees
    for s in suggestions:
        assert "Google" not in s.suggested_text
        assert "Stanford" not in s.suggested_text
        assert "Doctorate" not in s.suggested_text


@pytest.mark.asyncio
async def test_gemini_fallback_when_no_key():
    # Instantiating Gemini provider with empty key should gracefully fall back to local rewriter
    provider = GeminiAIProvider(api_key="")
    provider.api_key = ""
    suggestions = await provider.suggest_improvements(SAMPLE_BULLETS_TEXT)
    assert len(suggestions) > 0
    assert any("Spearheaded" in s.suggested_text or "Engineered" in s.suggested_text for s in suggestions)


def test_api_improve_endpoint_local():
    payload = {
        "resume_text": SAMPLE_BULLETS_TEXT,
        "job_description": "Must have Python, Kubernetes, and Docker skills.",
        "use_ai": False
    }
    response = client.post("/api/resumes/improve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ai_used"] is False
    assert "Layer A" in data["disclaimer"]
    assert len(data["suggestions"]) > 0


def test_api_improve_endpoint_empty_text():
    payload = {
        "resume_text": "",
        "use_ai": False
    }
    response = client.post("/api/resumes/improve", json=payload)
    assert response.status_code == 400
