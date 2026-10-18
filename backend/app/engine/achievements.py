import re
from typing import List, Tuple
from app.models.schemas import ExtractedSection, Deduction
from app.engine.rules import ACTION_VERBS


QUANTIFIABLE_PATTERNS = [
    re.compile(r'\b\d+(?:\.\d+)?%\b'),                                   # 25%, 3.5%
    re.compile(r'\$\d+(?:,\d{3})*(?:\.\d+)?(?:\s*[kKmMbB](?:illion)?)?'), # $500k, $1.2M, $50,000
    re.compile(r'\b\d+\s*(?:k|m|b)\b', re.IGNORECASE),                    # 10k, 5M
    re.compile(r'\b\d+x\b', re.IGNORECASE),                               # 10x, 3x
    re.compile(r'\b\d+\+?\s*(?:users|clients|customers|dau|mau|requests|req/s|rps|tps|events|gb|tb|pb|ms|seconds|minutes|hours|days|weeks|months|engineers|team\s+members)\b', re.IGNORECASE),
    re.compile(r'\b(?:reduced|decreased|increased|boosted|saved|scaled)\s+by\s+\d+', re.IGNORECASE),
]


def extract_quantifiable_metrics(text: str) -> List[str]:
    """Extracts matches of quantifiable outcomes from text."""
    matches = []
    for pat in QUANTIFIABLE_PATTERNS:
        found = pat.findall(text)
        matches.extend(found)
    return list(set(matches))


def evaluate_achievements(
    sections: List[ExtractedSection],
    resume_text: str,
    max_points: float = 10.0
) -> Tuple[float, float, str, List[str], List[Deduction], List[str]]:
    """
    Evaluates evidence of measurable achievements and action-verb framing.
    Avoids completely zeroing out scores for non-metric roles, but rewards demonstrated impact.
    """
    points = max_points
    evidence: List[str] = []
    deductions: List[Deduction] = []
    recommendations: List[str] = []

    # Gather bullets from experience and projects
    relevant_bullets = []
    for s in sections:
        if s.name in ("experience", "projects", "work_history"):
            relevant_bullets.extend(s.bullets)

    if not relevant_bullets:
        # Fallback to lines in resume text
        relevant_bullets = [line.strip() for line in resume_text.splitlines() if len(line.strip()) > 30]

    total_bullets = len(relevant_bullets)
    if total_bullets == 0:
        loss = max_points * 0.6
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="No bulleted achievement statements found",
            evidence="Resume does not use bullet points to delineate separate responsibilities and achievements.",
            fix_suggestion="Format work accomplishments into 3-5 concise bullet points per role."
        ))
        earned = max(0.0, round(points, 1))
        return earned, max_points, "No achievements detected.", evidence, deductions, recommendations

    # 1. Action Verbs Check
    bullets_with_action_verbs = 0
    for bullet in relevant_bullets:
        words = re.findall(r'\b\w+\b', bullet.lower()[:40])
        if any(w in ACTION_VERBS for w in words):
            bullets_with_action_verbs += 1

    action_verb_ratio = bullets_with_action_verbs / total_bullets
    if action_verb_ratio >= 0.5:
        evidence.append(f"Strong action verb usage: {bullets_with_action_verbs}/{total_bullets} bullets start with proactive impact verbs.")
    else:
        loss = max_points * 0.25
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Passive role descriptions",
            evidence=f"Only {bullets_with_action_verbs} of {total_bullets} bullets begin with strong action verbs.",
            fix_suggestion="Start bullet points with strong verbs (e.g. 'Architected', 'Engineered', 'Streamlined') instead of 'Responsible for' or 'Assisted with'."
        ))

    # 2. Measurable Outcomes Check
    bullets_with_metrics = 0
    all_metrics = []
    for bullet in relevant_bullets:
        metrics = extract_quantifiable_metrics(bullet)
        if metrics:
            bullets_with_metrics += 1
            all_metrics.extend(metrics)

    metric_ratio = bullets_with_metrics / total_bullets
    if metric_ratio >= 0.4:
        evidence.append(f"Quantifiable impact demonstrated in {bullets_with_metrics}/{total_bullets} bullets (e.g., {', '.join(all_metrics[:3])}).")
    elif metric_ratio >= 0.2:
        evidence.append(f"Moderate metrics detected in {bullets_with_metrics}/{total_bullets} bullets.")
        loss = max_points * 0.15
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Limited measurable metrics",
            evidence=f"Only {bullets_with_metrics} out of {total_bullets} bullets include concrete numerical metrics.",
            fix_suggestion="Add quantifiable results (e.g. '% increase', 'latency reduced by X ms', 'revenue impacted', 'users served')."
        ))
    else:
        loss = max_points * 0.35
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Lack of quantifiable metrics or business impact",
            evidence="Few or no numeric figures, percentage improvements, or scale indicators were found in your bullets.",
            fix_suggestion="Follow the Google XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'."
        ))

    earned = max(0.0, min(max_points, round(points, 1)))
    summary = f"Measurable impact scored {earned}/{max_points} points ({bullets_with_metrics} metrics in {total_bullets} bullets)."
    
    if not recommendations and deductions:
        for d in deductions:
            recommendations.append(d.fix_suggestion)

    return earned, max_points, summary, evidence, deductions, recommendations
