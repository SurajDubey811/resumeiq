from typing import List, Tuple
from app.models.schemas import ExtractedSection, ContactInfo, Deduction


def evaluate_structure(
    sections: List[ExtractedSection],
    contact_info: ContactInfo,
    max_points: float = 10.0
) -> Tuple[float, float, str, List[str], List[Deduction], List[str]]:
    """
    Evaluates resume structure and section completeness (Max 10 pts).
    Standard ATS sections: Experience, Education, Skills, Contact Info, Summary/Objective.
    """
    points = max_points
    evidence: List[str] = []
    deductions: List[Deduction] = []
    recommendations: List[str] = []

    detected_names = set(s.name for s in sections)

    # 1. Contact info check
    missing_contacts = []
    if not contact_info.email:
        missing_contacts.append("Email address")
    if not contact_info.phone:
        missing_contacts.append("Phone number")

    if missing_contacts:
        loss = 2.0 * len(missing_contacts)
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason=f"Missing vital contact details: {', '.join(missing_contacts)}",
            evidence=f"Could not extract {', '.join(missing_contacts)} from the header.",
            fix_suggestion="Ensure your email and phone number are clearly visible at the top of your resume (not hidden in header/footer layers)."
        ))
    else:
        evidence.append("Complete contact details found (email and phone number verified).")

    # 2. Key sections check
    critical_sections = [
        ("experience", "Work Experience", 3.0),
        ("skills", "Skills / Technologies", 2.0),
        ("education", "Education", 2.0),
    ]

    for key, label, penalty in critical_sections:
        if key not in detected_names:
            points -= penalty
            deductions.append(Deduction(
                points_lost=penalty,
                reason=f"Missing standard section: {label}",
                evidence=f"No section corresponding to '{label}' was recognized by standard ATS header heuristics.",
                fix_suggestion=f"Add a distinct section header titled '{label}'."
            ))
        else:
            evidence.append(f"Standard section recognized: {label}.")

    # 3. Summary check
    if "summary" in detected_names:
        evidence.append("Professional Summary / Profile section included.")
    else:
        loss = 1.0
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="No Professional Summary section",
            evidence="A short introductory profile or summary helps both ATS and recruiters quickly grasp your level.",
            fix_suggestion="Include a 2-3 sentence 'Professional Summary' at the top of your resume."
        ))

    earned = max(0.0, min(max_points, round(points, 1)))
    summary = f"Structure scored {earned}/{max_points} points based on section completeness."
    
    if not recommendations and deductions:
        for d in deductions:
            recommendations.append(d.fix_suggestion)

    return earned, max_points, summary, evidence, deductions, recommendations


def evaluate_ats_readability(
    raw_text: str,
    warnings: List[str],
    word_count: int,
    page_count: int,
    max_points: float = 10.0
) -> Tuple[float, float, str, List[str], List[Deduction], List[str]]:
    """
    Evaluates ATS readability, layout hazards, tables, and document length (Max 10 pts).
    """
    points = max_points
    evidence: List[str] = []
    deductions: List[Deduction] = []
    recommendations: List[str] = []

    # 1. Parsing warnings inspection (tables, multi-column, OCR)
    for w in warnings:
        if "multi-column" in w.lower():
            loss = 3.0
            points -= loss
            deductions.append(Deduction(
                points_lost=loss,
                reason="Multi-column layout risk",
                evidence=w,
                fix_suggestion="Use a clean, single-column linear layout to prevent ATS parsers from mixing text blocks across columns."
            ))
        elif "table" in w.lower():
            loss = 2.0
            points -= loss
            deductions.append(Deduction(
                points_lost=loss,
                reason="Table layout risk",
                evidence=w,
                fix_suggestion="Replace tables with standard text and bullet points; some legacy ATS systems read table cells out of order."
            ))
        elif "scanned" in w.lower() or "ocr" in w.lower():
            loss = 6.0
            points -= loss
            deductions.append(Deduction(
                points_lost=loss,
                reason="Image or scanned document",
                evidence=w,
                fix_suggestion="Export your resume directly as a searchable PDF or Word (.docx) document."
            ))

    # 2. Word Count and Page Ratio Check
    if word_count < 150:
        loss = 3.0
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Resume is excessively brief",
            evidence=f"Total word count is only {word_count} words.",
            fix_suggestion="Expand upon your responsibilities, technologies, and achievements."
        ))
    elif word_count > 1800:
        loss = 2.0
        points -= loss
        deductions.append(Deduction(
            points_lost=loss,
            reason="Resume exceeds recommended length",
            evidence=f"Total word count is {word_count} words ({page_count} pages).",
            fix_suggestion="Condense older or less relevant experience to keep resume within 1-2 pages."
        ))
    else:
        evidence.append(f"Optimal word count: {word_count} words across {page_count} page(s).")

    if not deductions:
        evidence.append("Clean formatting with standard ATS-friendly structure and no column/table hazards detected.")

    earned = max(0.0, min(max_points, round(points, 1)))
    summary = f"ATS readability scored {earned}/{max_points} points."
    
    if not recommendations and deductions:
        for d in deductions:
            recommendations.append(d.fix_suggestion)

    return earned, max_points, summary, evidence, deductions, recommendations
