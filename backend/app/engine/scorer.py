from typing import Optional, Dict, List
import uuid

from app.models.schemas import (
    ParsedResume,
    ATSScorecard,
    DimensionScore,
    Deduction,
    ActionItem,
    KeywordAnalysis,
    JobComparison
)
from app.engine.rules import JOB_MATCHED_WEIGHTS, RESUME_ONLY_WEIGHTS, SCORE_TIERS
from app.engine.keywords import analyze_keywords
from app.engine.experience import evaluate_experience
from app.engine.education import evaluate_education
from app.engine.achievements import evaluate_achievements
from app.engine.formatting import evaluate_structure, evaluate_ats_readability


def get_tier(score: int) -> str:
    for threshold, label in SCORE_TIERS:
        if score >= threshold:
            return label
    return "Needs Improvement"


def calculate_ats_score(
    parsed_resume: ParsedResume,
    jd_text: Optional[str] = None
) -> ATSScorecard:
    """
    Main deterministic ATS scoring engine.
    Computes explainable, reproducible scores out of 100 with category breakdowns,
    evidence, deductions, and prioritized recommendations.
    """
    is_job_mode = bool(jd_text and jd_text.strip())
    weights = JOB_MATCHED_WEIGHTS if is_job_mode else RESUME_ONLY_WEIGHTS

    # 1. Keywords & Skills Analysis
    keyword_analysis = analyze_keywords(parsed_resume.raw_text, jd_text if is_job_mode else None)
    
    kw_max = weights["skills_alignment"]
    kw_points = kw_max
    kw_evidence = []
    kw_deductions = []
    kw_recommendations = []

    if is_job_mode:
        total_req = len(keyword_analysis.missing_required) + len(
            [k for k in keyword_analysis.matched_exact + keyword_analysis.matched_synonyms if k.importance == "required"]
        )
        total_pref = len(keyword_analysis.missing_preferred) + len(
            [k for k in keyword_analysis.matched_exact + keyword_analysis.matched_synonyms if k.importance == "preferred"]
        )
        matched_count = len(keyword_analysis.matched_exact) + len(keyword_analysis.matched_synonyms)

        if total_req > 0:
            req_matched = len([k for k in keyword_analysis.matched_exact + keyword_analysis.matched_synonyms if k.importance == "required"])
            req_match_rate = req_matched / total_req
        else:
            req_match_rate = 1.0

        if total_pref > 0:
            pref_matched = len([k for k in keyword_analysis.matched_exact + keyword_analysis.matched_synonyms if k.importance == "preferred"])
            pref_match_rate = pref_matched / total_pref
        else:
            pref_match_rate = 1.0

        # Weighted calculation: required skills count 75%, preferred 25%
        skill_ratio = (req_match_rate * 0.75) + (pref_match_rate * 0.25)
        kw_points = round(kw_max * skill_ratio, 1)

        kw_evidence.append(
            f"Matched {matched_count} out of {keyword_analysis.total_jd_keywords} key skills ({len(keyword_analysis.matched_exact)} exact, {len(keyword_analysis.matched_synonyms)} via synonyms)."
        )

        if keyword_analysis.missing_required:
            missing_names = [k.skill for k in keyword_analysis.missing_required[:5]]
            loss = round(kw_max * (1.0 - req_match_rate) * 0.75, 1)
            kw_deductions.append(Deduction(
                points_lost=loss,
                reason=f"Missing {len(keyword_analysis.missing_required)} required skills from job description",
                evidence=f"Target role specifically lists: {', '.join(missing_names)}",
                fix_suggestion=f"Integrate authentic examples of {', '.join(missing_names[:3])} into your skills and project bullets."
            ))

        if keyword_analysis.matched_synonyms:
            syn_examples = [f"{k.skill} (via '{k.matched_via}')" for k in keyword_analysis.matched_synonyms[:3]]
            kw_evidence.append(f"Recognized synonym mappings: {', '.join(syn_examples)}.")

    else:
        # Resume-only mode
        skill_count = len(keyword_analysis.other_resume_skills)
        if skill_count >= 10:
            kw_points = kw_max
            kw_evidence.append(f"Comprehensive technical skill catalog: {skill_count} relevant proficiencies detected.")
        elif skill_count >= 5:
            kw_points = round(kw_max * 0.8, 1)
            kw_evidence.append(f"Found {skill_count} skills across resume.")
        else:
            kw_points = round(kw_max * 0.5, 1)
            kw_deductions.append(Deduction(
                points_lost=round(kw_max * 0.5, 1),
                reason="Low technical skill density",
                evidence=f"Only {skill_count} distinct technology keywords found.",
                fix_suggestion="Add a dedicated Technical Skills section grouping languages, frameworks, cloud tools, and databases."
            ))

    if not kw_recommendations and kw_deductions:
        kw_recommendations.extend([d.fix_suggestion for d in kw_deductions])

    kw_score_obj = DimensionScore(
        key="skills_alignment",
        name="Skills & Keyword Alignment",
        points_earned=kw_points,
        max_points=kw_max,
        score_percentage=round((kw_points / kw_max) * 100, 1),
        status="strong" if kw_points >= kw_max * 0.8 else ("good" if kw_points >= kw_max * 0.6 else "needs_improvement"),
        summary=f"Scored {kw_points}/{kw_max} based on skill coverage.",
        evidence=kw_evidence,
        deductions=kw_deductions,
        recommendations=kw_recommendations
    )

    # 2. Experience Dimension
    exp_pts, exp_max, exp_sum, exp_ev, exp_ded, exp_rec, job_comp = evaluate_experience(
        parsed_resume.sections,
        parsed_resume.raw_text,
        jd_text if is_job_mode else None
    )
    exp_score_obj = DimensionScore(
        key="relevant_experience",
        name="Relevant Experience & Responsibilities",
        points_earned=exp_pts,
        max_points=exp_max,
        score_percentage=round((exp_pts / exp_max) * 100, 1),
        status="strong" if exp_pts >= exp_max * 0.8 else ("good" if exp_pts >= exp_max * 0.6 else "needs_improvement"),
        summary=exp_sum,
        evidence=exp_ev,
        deductions=exp_ded,
        recommendations=exp_rec
    )

    # 3. Education Dimension
    edu_pts, edu_max, edu_sum, edu_ev, edu_ded, edu_rec, deg_found, deg_req = evaluate_education(
        parsed_resume.sections,
        parsed_resume.raw_text,
        jd_text if is_job_mode else None
    )
    if job_comp:
        job_comp.degree_found = deg_found
        job_comp.degree_required = deg_req

    edu_score_obj = DimensionScore(
        key="education_qualifications",
        name="Education & Qualifications",
        points_earned=edu_pts,
        max_points=edu_max,
        score_percentage=round((edu_pts / edu_max) * 100, 1),
        status="strong" if edu_pts >= edu_max * 0.8 else ("good" if edu_pts >= edu_max * 0.6 else "needs_improvement"),
        summary=edu_sum,
        evidence=edu_ev,
        deductions=edu_ded,
        recommendations=edu_rec
    )

    # 4. Measurable Achievements Dimension
    ach_max = weights["measurable_achievements"]
    ach_pts, ach_max, ach_sum, ach_ev, ach_ded, ach_rec = evaluate_achievements(
        parsed_resume.sections,
        parsed_resume.raw_text,
        max_points=ach_max
    )
    ach_score_obj = DimensionScore(
        key="measurable_achievements",
        name="Measurable Achievements & Impact",
        points_earned=ach_pts,
        max_points=ach_max,
        score_percentage=round((ach_pts / ach_max) * 100, 1),
        status="strong" if ach_pts >= ach_max * 0.8 else ("good" if ach_pts >= ach_max * 0.6 else "needs_improvement"),
        summary=ach_sum,
        evidence=ach_ev,
        deductions=ach_ded,
        recommendations=ach_rec
    )

    # 5. Structure & Completeness Dimension
    str_max = weights["resume_structure"]
    str_pts, str_max, str_sum, str_ev, str_ded, str_rec = evaluate_structure(
        parsed_resume.sections,
        parsed_resume.contact_info,
        max_points=str_max
    )
    str_score_obj = DimensionScore(
        key="resume_structure",
        name="Resume Structure & Section Completeness",
        points_earned=str_pts,
        max_points=str_max,
        score_percentage=round((str_pts / str_max) * 100, 1),
        status="strong" if str_pts >= str_max * 0.8 else ("good" if str_pts >= str_max * 0.6 else "needs_improvement"),
        summary=str_sum,
        evidence=str_ev,
        deductions=str_ded,
        recommendations=str_rec
    )

    # 6. Readability & Formatting Dimension
    read_max = weights["ats_readability"]
    read_pts, read_max, read_sum, read_ev, read_ded, read_rec = evaluate_ats_readability(
        parsed_resume.raw_text,
        parsed_resume.warnings,
        parsed_resume.word_count,
        parsed_resume.page_count,
        max_points=read_max
    )
    read_score_obj = DimensionScore(
        key="ats_readability",
        name="ATS Readability & Formatting",
        points_earned=read_pts,
        max_points=read_max,
        score_percentage=round((read_pts / read_max) * 100, 1),
        status="strong" if read_pts >= read_max * 0.8 else ("good" if read_pts >= read_max * 0.6 else "needs_improvement"),
        summary=read_sum,
        evidence=read_ev,
        deductions=read_ded,
        recommendations=read_rec
    )

    # Overall calculation
    dimension_scores = {
        "skills_alignment": kw_score_obj,
        "relevant_experience": exp_score_obj,
        "education_qualifications": edu_score_obj,
        "measurable_achievements": ach_score_obj,
        "resume_structure": str_score_obj,
        "ats_readability": read_score_obj,
    }

    raw_total = sum(d.points_earned for d in dimension_scores.values())
    overall_score = max(0, min(100, int(round(raw_total))))
    tier = get_tier(overall_score)

    # Aggregate Strengths & Improvement Areas
    strengths = []
    areas_for_improvement = []
    prioritized_actions: List[ActionItem] = []

    for dim in dimension_scores.values():
        if dim.score_percentage >= 80:
            strengths.append(f"{dim.name}: {dim.summary}")
        elif dim.score_percentage < 70:
            areas_for_improvement.append(f"{dim.name}: {dim.summary}")

        for ded in dim.deductions:
            prio = "High" if ded.points_lost >= 4.0 else ("Medium" if ded.points_lost >= 2.0 else "Low")
            prioritized_actions.append(ActionItem(
                id=str(uuid.uuid4())[:8],
                priority=prio,
                category=dim.name,
                title=ded.reason,
                explanation=f"{ded.evidence} (Deduction: -{ded.points_lost} pts)",
                example_fix=ded.fix_suggestion
            ))

    # Sort prioritized actions: High -> Medium -> Low
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    prioritized_actions = sorted(prioritized_actions, key=lambda a: priority_order.get(a.priority, 3))

    mode_description = (
        "Job-Specific Fit Mode: Scored against the requirements and target keywords of the supplied job description."
        if is_job_mode else
        "General ATS Health Mode: Evaluated for industry-standard ATS parsing compliance, structural completeness, quantifiable impact, and formatting without a specific job description."
    )

    return ATSScorecard(
        overall_score=overall_score,
        tier=tier,
        mode="job_matched" if is_job_mode else "resume_only",
        mode_description=mode_description,
        dimension_scores=dimension_scores,
        keyword_analysis=keyword_analysis,
        strengths=strengths,
        areas_for_improvement=areas_for_improvement,
        prioritized_action_items=prioritized_actions,
        ats_formatting_warnings=parsed_resume.warnings,
        job_comparison=job_comp if is_job_mode else None
    )
