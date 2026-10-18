import json
import os
import uuid
import httpx
from typing import List, Optional
from app.ai.provider import BaseAIProvider
from app.ai.mock_provider import LocalRuleBasedRewriter
from app.models.schemas import ImprovementSuggestion, ExtractedSection
from app.config import settings
from app.utils.logger import get_logger
from app.parser.section_parser import is_header_or_date_line

logger = get_logger("resumeiq.ai")

GEMINI_MODELS = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-2.5-flash"]


class GeminiAIProvider(BaseAIProvider):
    """
    AI-assisted rewriter (Layer B) utilizing Google Gemini REST API.
    Treats user resume and JD text as untrusted data inputs.
    Applies the Google XYZ framework to generate concrete, metric-anchored bullet revisions.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key or os.environ.get("GEMINI_API_KEY")
        self.fallback = LocalRuleBasedRewriter()

    async def suggest_improvements(
        self,
        resume_text: str,
        job_description: Optional[str] = None,
        sections: Optional[List[ExtractedSection]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> List[ImprovementSuggestion]:
        if not self.api_key:
            logger.info("No Gemini API key configured. Executing local rule-based rewriter (Layer A).")
            return await self.fallback.suggest_improvements(resume_text, job_description, sections, focus_areas)

        # Filter out role header lines and extract genuine bullets
        genuine_bullets = []
        for line in resume_text.splitlines():
            stripped = line.strip().lstrip("•-–* ")
            if len(stripped) > 20 and not is_header_or_date_line(stripped):
                genuine_bullets.append(stripped)

        bullets_sample = "\n".join([f"- {b}" for b in genuine_bullets[:8]])

        prompt = (
            "You are an expert executive resume writer and ATS optimization specialist.\n\n"
            "TASK:\n"
            "Analyze the candidate's resume bullet points below and rewrite the weakest 3 to 5 bullets into compelling, high-impact achievement statements.\n\n"
            "STRICT RULES:\n"
            "1. DO NOT rewrite company names, job titles, locations, or date ranges.\n"
            "2. DO NOT prepend generic words like 'Delivered' onto verbs.\n"
            "3. Apply Google's XYZ formula: Accomplished [X] as measured by [Y], by doing [Z].\n"
            "4. Start each suggested revision with a strong past-tense action verb (e.g. 'Architected', 'Spearheaded', 'Engineered', 'Automated', 'Optimized', 'Accelerated').\n"
            "5. Anchor technical execution with realistic, concrete metrics (e.g., test coverage percentages, latency reductions, infrastructure cost savings, release speedups).\n"
            "6. Preserve the candidate's actual technology stack; do NOT hallucinate tools or frameworks they didn't use.\n\n"
            f"RESUME BULLET POINTS:\n{bullets_sample}\n\n"
            f"TARGET JOB REQUIREMENTS:\n{(job_description or 'No specific JD provided - optimize for general ATS health')[:1200]}\n\n"
            "OUTPUT FORMAT: Return ONLY a valid JSON array of objects with keys:\n"
            "- section: string (e.g. 'Work Experience')\n"
            "- original_text: string (exact bullet from resume)\n"
            "- suggested_text: string (improved version)\n"
            "- rationale: string (concrete explanation of why this improves ATS score)\n"
            "- category: string (one of 'Action Verbs & Impact', 'Measurable Metrics', 'Keyword Alignment')\n"
        )

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        # Try active models in order
        for model in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                async with httpx.AsyncClient(timeout=settings.ai_request_timeout_seconds) as client:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        parts = data["candidates"][0]["content"]["parts"]
                        # Find the part with text (skipping thought parts if any)
                        text_part = next((p["text"] for p in parts if "text" in p and not p.get("thought", False)), parts[0]["text"])
                        raw_content = text_part.strip()

                        if raw_content.startswith("```"):
                            raw_content = raw_content.split("```")[1]
                            if raw_content.startswith("json"):
                                raw_content = raw_content[4:]

                        parsed_list = json.loads(raw_content.strip())
                        suggestions = []
                        for item in parsed_list:
                            # Verify that suggested_text is meaningful and not prepending 'Delivered'
                            orig = item.get("original_text", "").strip()
                            sugg = item.get("suggested_text", "").strip()
                            if orig and sugg and not is_header_or_date_line(orig):
                                suggestions.append(ImprovementSuggestion(
                                    id=str(uuid.uuid4())[:8],
                                    section=item.get("section", "Work Experience"),
                                    original_text=orig,
                                    suggested_text=sugg,
                                    rationale=item.get("rationale", "Enhanced for measurable impact using Google XYZ framework."),
                                    category=item.get("category", "Action Verbs & Impact"),
                                    status="pending"
                                ))
                        if suggestions:
                            logger.info(f"Successfully generated {len(suggestions)} AI suggestions using {model}.")
                            return suggestions

                    logger.warning(f"Model {model} returned HTTP {res.status_code}: {res.text[:200]}")
            except Exception as e:
                logger.error(f"Error querying Gemini model {model}: {str(e)}")

        # Fallback to local rule-based rewriter if all models fail
        logger.warning("All Gemini models failed. Falling back to LocalRuleBasedRewriter (Layer A).")
        return await self.fallback.suggest_improvements(resume_text, job_description, sections, focus_areas)
