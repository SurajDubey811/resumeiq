from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    location: Optional[str] = None
    portfolio: Optional[str] = None


class ExtractedSection(BaseModel):
    name: str = Field(description="Normalized section key (e.g. experience, education, skills, summary, projects, certifications, other)")
    raw_title: str = Field(description="Original section title found in resume")
    content: str = Field(description="Extracted text body for this section")
    bullets: List[str] = Field(default_factory=list, description="Extracted bullet points or distinct achievement lines")


class ParsedResume(BaseModel):
    filename: str
    file_type: str  # "pdf" or "docx"
    page_count: int = 1
    word_count: int = 0
    raw_text: str
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    sections: List[ExtractedSection] = Field(default_factory=list)
    is_scanned_pdf: bool = False
    ocr_recommended: bool = False
    warnings: List[str] = Field(default_factory=list)


class ParseResponse(BaseModel):
    success: bool
    data: Optional[ParsedResume] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    app_name: str


# ----------------- SCORING & ANALYSIS SCHEMAS -----------------

class KeywordItem(BaseModel):
    skill: str
    category: Optional[str] = "Technical"
    importance: Literal["required", "preferred", "general"] = "general"
    matched: bool = False
    match_type: Literal["exact", "synonym", "missing"] = "missing"
    matched_via: Optional[str] = None
    frequency_in_resume: int = 0


class KeywordAnalysis(BaseModel):
    total_jd_keywords: int = 0
    matched_exact: List[KeywordItem] = Field(default_factory=list)
    matched_synonyms: List[KeywordItem] = Field(default_factory=list)
    missing_required: List[KeywordItem] = Field(default_factory=list)
    missing_preferred: List[KeywordItem] = Field(default_factory=list)
    other_resume_skills: List[str] = Field(default_factory=list)


class Deduction(BaseModel):
    points_lost: float
    reason: str
    evidence: str
    fix_suggestion: str


class DimensionScore(BaseModel):
    key: str
    name: str
    points_earned: float
    max_points: float
    score_percentage: float
    status: Literal["strong", "good", "needs_improvement"] = "good"
    summary: str
    evidence: List[str] = Field(default_factory=list)
    deductions: List[Deduction] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ActionItem(BaseModel):
    id: str
    priority: Literal["High", "Medium", "Low"]
    category: str
    title: str
    explanation: str
    example_fix: Optional[str] = None
    suggested_revision: Optional[str] = None


class JobComparison(BaseModel):
    job_title_detected: Optional[str] = None
    seniority_match: Optional[str] = None
    years_experience_required: Optional[int] = None
    years_experience_found: Optional[float] = None
    degree_required: Optional[str] = None
    degree_found: Optional[str] = None
    key_responsibilities_matched: List[str] = Field(default_factory=list)
    key_responsibilities_missing: List[str] = Field(default_factory=list)


class ATSScorecard(BaseModel):
    overall_score: int
    tier: Literal["Strong", "Good", "Fair", "Needs Improvement"]
    mode: Literal["job_matched", "resume_only"]
    mode_description: str
    dimension_scores: Dict[str, DimensionScore]
    keyword_analysis: KeywordAnalysis
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    prioritized_action_items: List[ActionItem] = Field(default_factory=list)
    ats_formatting_warnings: List[str] = Field(default_factory=list)
    job_comparison: Optional[JobComparison] = None


class AnalyzeRequest(BaseModel):
    resume_text: str
    filename: Optional[str] = "resume.pdf"
    job_description: Optional[str] = None
    parsed_resume: Optional[ParsedResume] = None


class AnalyzeResponse(BaseModel):
    success: bool
    scorecard: Optional[ATSScorecard] = None
    error: Optional[str] = None


# ----------------- IMPROVEMENT SCHEMAS -----------------

class ImprovementSuggestion(BaseModel):
    id: str
    section: str
    original_text: str
    suggested_text: str
    rationale: str
    category: str  # e.g., "Metrics & Impact", "Keyword Alignment", "Action Verbs"
    status: Literal["pending", "accepted", "rejected"] = "pending"


class ImproveRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = None
    sections: Optional[List[ExtractedSection]] = None
    focus_areas: Optional[List[str]] = None
    use_ai: bool = False


class ImproveResponse(BaseModel):
    success: bool
    suggestions: List[ImprovementSuggestion] = Field(default_factory=list)
    ai_used: bool = False
    disclaimer: str = ""
    error: Optional[str] = None


class AcceptedChange(BaseModel):
    original_text: str
    suggested_text: str


class ExportRequest(BaseModel):
    resume_text: str
    file_type: str = "pdf"  # "pdf" or "docx"
    filename: Optional[str] = "resume"
    target_format: Optional[str] = None  # "pdf" or "docx"
    accepted_changes: List[AcceptedChange] = Field(default_factory=list)

