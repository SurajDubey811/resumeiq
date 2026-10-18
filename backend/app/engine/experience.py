import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from app.models.schemas import ExtractedSection, JobComparison, Deduction


SENIORITY_RANKS = {
    "intern": 1,
    "junior": 2,
    "entry": 2,
    "associate": 2,
    "mid": 3,
    "senior": 4,
    "lead": 5,
    "staff": 6,
    "principal": 7,
    "manager": 5,
    "director": 6,
    "vp": 7,
}


def estimate_years_of_experience(text: str) -> float:
    """
    Estimates total years of experience by scanning date ranges (e.g. 2018 - 2023, 2021 - Present).
    """
    current_year = datetime.now().year
    # Match patterns like: 2018 - 2022, 2019 - Present, 05/2017 to 08/2021
    year_range_pattern = re.compile(
        r'\b(20\d{2}|19\d{2})\s*(?:-|–|—|to)\s*(20\d{2}|19\d{2}|present|current)\b',
        re.IGNORECASE
    )
    
    ranges = year_range_pattern.findall(text)
    if not ranges:
        # Fallback: check phrases like "5+ years of experience" in resume
        exp_phrase = re.search(r'(\d+)\+?\s*years(?:\s+of)?\s+experience', text, re.IGNORECASE)
        if exp_phrase:
            return float(exp_phrase.group(1))
        return 2.0  # Conservative baseline fallback
    
    total_years = 0.0
    seen_intervals: List[Tuple[int, int]] = []

    for start_str, end_str in ranges:
        start_yr = int(start_str)
        if end_str.lower() in ("present", "current"):
            end_yr = current_year
        else:
            end_yr = int(end_str)
            
        if 1980 <= start_yr <= current_year and start_yr <= end_yr <= current_year + 1:
            duration = max(0.5, end_yr - start_yr)
            total_years += duration
            seen_intervals.append((start_yr, end_yr))

    # Avoid duplicate years if intervals overlap
    return min(30.0, max(1.0, round(total_years, 1)))


def extract_required_years_from_jd(jd_text: str) -> Optional[int]:
    """Finds required years of experience in job description (e.g. '5+ years required')."""
    match = re.search(r'(\d+)\+?\s*years(?:\s+of)?\s*(?:relevant\s+)?experience', jd_text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_seniority(text: str) -> Optional[str]:
    """Extracts seniority level from title or introductory text."""
    lower = text.lower()
    for title in ["principal", "staff", "director", "manager", "lead", "senior", "junior", "intern"]:
        if re.search(rf'\b{title}\b', lower):
            return title.capitalize()
    return None


def evaluate_experience(
    sections: List[ExtractedSection],
    resume_text: str,
    jd_text: Optional[str] = None
) -> Tuple[float, float, str, List[str], List[Deduction], List[str], JobComparison]:
    """
    Evaluates experience alignment (Max 25 pts).
    Returns (points_earned, max_points, summary, evidence, deductions, recommendations, job_comparison)
    """
    max_points = 25.0
    points = max_points
    evidence: List[str] = []
    deductions: List[Deduction] = []
    recommendations: List[str] = []

    exp_sections = [s for s in sections if s.name == "experience"]
    has_exp_section = len(exp_sections) > 0
    exp_content = "\n".join([s.content for s in exp_sections]) if exp_sections else resume_text
    
    total_years = estimate_years_of_experience(exp_content)
    seniority_found = extract_seniority(resume_text[:500]) or "Professional"

    job_comp = JobComparison(
        years_experience_found=total_years,
        seniority_match=seniority_found
    )

    if not has_exp_section:
        loss = 10.0
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Missing dedicated 'Work Experience' section",
            evidence="No section explicitly labeled 'Experience', 'Work History', or 'Employment' was found.",
            fix_suggestion="Create a clearly marked 'Work Experience' or 'Professional Experience' section header."
        ))
    else:
        evidence.append(f"Detected dedicated Work Experience section with ~{total_years} estimated years of experience.")

    # Check bullet points volume and quality
    total_bullets = sum(len(s.bullets) for s in exp_sections)
    if total_bullets < 3:
        loss = 4.0
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Insufficient experience bullet points",
            evidence=f"Found only {total_bullets} bullet points in work experience.",
            fix_suggestion="Add 3-5 structured bullet points per role describing your responsibilities and achievements."
        ))
    else:
        evidence.append(f"Contains {total_bullets} detailed experience bullet points.")

    # If Job Description is provided, compare required experience
    if jd_text and jd_text.strip():
        req_years = extract_required_years_from_jd(jd_text)
        job_comp.years_experience_required = req_years
        
        if req_years:
            if total_years < req_years:
                gap = req_years - total_years
                loss = min(8.0, gap * 2.0)
                points -= loss
                deductions.append(Deduction(
                    points_lost=loss,
                    reason=f"Years of experience gap ({total_years} yrs found vs {req_years}+ yrs requested)",
                    evidence=f"Job requires {req_years}+ years; resume shows approximately {total_years} years.",
                    fix_suggestion=f"Highlight freelance, academic, or earlier projects that contribute toward the {req_years}-year requirement."
                ))
            else:
                evidence.append(f"Meets or exceeds required experience: {total_years} years found vs {req_years} years required.")

        # Seniority alignment
        jd_seniority = extract_seniority(jd_text[:300])
        if jd_seniority:
            job_comp.seniority_match = f"Resume: {seniority_found} / Target: {jd_seniority}"
            jd_rank = SENIORITY_RANKS.get(jd_seniority.lower(), 3)
            res_rank = SENIORITY_RANKS.get(seniority_found.lower(), 3)
            if res_rank < jd_rank - 1:
                loss = 3.0
                points -= loss
                deductions.append(Deduction(
                    points_lost=loss,
                    reason=f"Seniority level mismatch (Target: {jd_seniority})",
                    evidence=f"Target role is {jd_seniority}, but resume positions at {seniority_found} level.",
                    fix_suggestion=f"Frame your responsibilities with more senior leadership verbs (e.g., 'Spearheaded', 'Mentored', 'Architected')."
                ))

    earned = max(0.0, min(max_points, round(points, 1)))
    summary = f"Experience scored {earned}/{max_points} points based on {total_years} estimated years and role depth."
    
    if not recommendations and deductions:
        for d in deductions:
            recommendations.append(d.fix_suggestion)

    return earned, max_points, summary, evidence, deductions, recommendations, job_comp
