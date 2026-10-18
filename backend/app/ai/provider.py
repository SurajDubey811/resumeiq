from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.schemas import ImprovementSuggestion, ExtractedSection


class BaseAIProvider(ABC):
    """Abstract interface for resume analysis and revision providers."""

    @abstractmethod
    async def suggest_improvements(
        self,
        resume_text: str,
        job_description: Optional[str] = None,
        sections: Optional[List[ExtractedSection]] = None,
        focus_areas: Optional[List[str]] = None
    ) -> List[ImprovementSuggestion]:
        """Generates evidence-backed revision suggestions for resume bullets or sections."""
        pass
