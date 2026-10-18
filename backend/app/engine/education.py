import re
from typing import List, Tuple, Optional
from app.models.schemas import ExtractedSection, Deduction
from app.engine.rules import DEGREE_LEVELS


def detect_highest_degree(text: str) -> Tuple[int, Optional[str]]:
    """Detects highest educational degree mentioned and returns (level_rank, degree_name)."""
    text_lower = text.lower()
    highest_rank = 0
    highest_name = None

    for deg, rank in DEGREE_LEVELS.items():
        if re.search(rf'\b{re.escape(deg)}\b', text_lower):
            if rank > highest_rank:
                highest_rank = rank
                highest_name = deg.title()

    return highest_rank, highest_name


def evaluate_education(
    sections: List[ExtractedSection],
    resume_text: str,
    jd_text: Optional[str] = None
) -> Tuple[float, float, str, List[str], List[Deduction], List[str], Optional[str], Optional[str]]:
    """
    Evaluates education credentials and certifications (Max 15 pts).
    Returns (points, max_points, summary, evidence, deductions, recommendations, deg_found, deg_required)
    """
    max_points = 15.0
    points = max_points
    evidence: List[str] = []
    deductions: List[Deduction] = []
    recommendations: List[str] = []

    edu_sections = [s for s in sections if s.name in ("education", "academic")]
    has_edu = len(edu_sections) > 0
    edu_text = "\n".join([s.content for s in edu_sections]) if edu_sections else resume_text

    rank_found, deg_found = detect_highest_degree(edu_text)
    
    # Check certifications
    cert_sections = [s for s in sections if s.name == "certifications"]
    has_cert = len(cert_sections) > 0 or bool(re.search(r'\b(certified|certification|license|pmp|aws certified|cka)\b', resume_text, re.IGNORECASE))
    if has_cert:
        evidence.append("Professional certifications or licensures identified.")

    if not has_edu and rank_found == 0:
        loss = 6.0
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Missing Education section or identifiable degree",
            evidence="No clear educational degree or Education section was detected.",
            fix_suggestion="Add a dedicated 'Education' section stating your institution, degree title, and graduation year."
        ))
    else:
        deg_label = deg_found if deg_found else "Degree / Coursework"
        evidence.append(f"Identified education credential: {deg_label}.")

    deg_required = None
    if jd_text and jd_text.strip():
        req_rank, deg_required = detect_highest_degree(jd_text)
        if deg_required and req_rank > 0:
            if rank_found < req_rank and rank_found > 0:
                loss = 4.0
                points -= loss
                deductions.append(Deduction(
                    points_lost=loss,
                    reason=f"Education level below target qualification ({deg_found} vs {deg_required} required)",
                    evidence=f"Job posting lists {deg_required} qualification, while resume reflects {deg_found}.",
                    fix_suggestion=f"Highlight equivalent industry experience or specialized certifications demonstrating {deg_required}-level mastery."
                ))
            elif rank_found >= req_rank:
                evidence.append(f"Meets education requirement ({deg_found} meets or exceeds {deg_required}).")

    earned = max(0.0, min(max_points, round(points, 1)))
    summary = f"Education scored {earned}/{max_points} points."
    
    if not recommendations and deductions:
        for d in deductions:
            recommendations.append(d.fix_suggestion)

    return earned, max_points, summary, evidence, deductions, recommendations, deg_found, deg_required
