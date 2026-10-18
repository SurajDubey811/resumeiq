import re
from typing import List, Dict, Tuple, Optional
from app.models.schemas import ContactInfo, ExtractedSection


SECTION_PATTERNS = {
    "summary": [
        r"^(?:professional\s+)?summary$",
        r"^executive\s+summary$",
        r"^profile$",
        r"^about(?:\s+me)?$",
        r"^(?:career\s+)?objective$",
    ],
    "experience": [
        r"^(?:work|professional|relevant|career)?\s*experience$",
        r"^employment(?:\s+history)?$",
        r"^work\s+history$",
        r"^experience\s+and\s+employment$",
    ],
    "education": [
        r"^education$",
        r"^academic\s+(?:background|history|qualifications)$",
        r"^qualifications$",
        r"^degrees\s+(?:and\s+certifications)?$",
    ],
    "skills": [
        r"^(?:technical\s+|core\s+)?skills$",
        r"^technologies(?:\s+and\s+tools)?$",
        r"^core\s+competencies$",
        r"^areas\s+of\s+expertise$",
        r"^technical\s+proficiencies$",
        r"^tools\s+and\s+technologies$",
    ],
    "projects": [
        r"^(?:personal\s+|key\s+|featured\s+|academic\s+)?projects$",
        r"^technical\s+projects$",
    ],
    "certifications": [
        r"^certifications?(?:\s+and\s+licenses)?$",
        r"^licenses?(?:\s+and\s+certifications)?$",
        r"^credentials$",
    ],
    "awards": [
        r"^awards?(?:\s+and\s+honors)?$",
        r"^honors?(?:\s+and\s+awards)?$",
        r"^publications?$",
    ],
}


def extract_contact_info(text: str) -> ContactInfo:
    """Extracts contact info (email, phone, LinkedIn, GitHub, etc.) from raw text."""
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0).rstrip('.') if email_match else None

    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    phone = phone_match.group(0).strip() if phone_match else None

    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    linkedin = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None

    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', text, re.IGNORECASE)
    github = f"https://github.com/{github_match.group(1)}" if github_match else None

    # Location heuristic (e.g. "Seattle, WA" or "San Francisco, CA" or "New York, NY 10001")
    location_match = re.search(
        r'\b([A-Z][a-zA-Z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?|[A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z]+)\b',
        text[:600]
    )
    location = location_match.group(0).strip() if location_match else None

    # Portfolio heuristic (e.g., https://username.dev or .io or .me)
    portfolio_match = re.search(
        r'https?://(?!www\.linkedin\.com|www\.github\.com)[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:/[^\s]*)?',
        text,
        re.IGNORECASE
    )
    portfolio = portfolio_match.group(0).strip() if portfolio_match else None

    return ContactInfo(
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github,
        location=location,
        portfolio=portfolio
    )


def match_section_header(line: str) -> Optional[str]:
    """Matches a line against standard resume section headers."""
    clean_line = line.strip().lower()
    # Remove trailing colons, dashes, numbers
    clean_line = re.sub(r'[:\-–—\d\.]+$', '', clean_line).strip()
    
    if len(clean_line) < 3 or len(clean_line) > 40:
        return None

    for section_name, patterns in SECTION_PATTERNS.items():
        for pat in patterns:
            if re.match(pat, clean_line, re.IGNORECASE):
                return section_name
    return None


def is_header_or_date_line(line: str) -> bool:
    """Detects if a line is a company name, job title, date range, or metadata rather than a bullet."""
    # Date range patterns: 2020 - Present, Apr 2025 – Present, (2021 - 2023)
    if re.search(r'\b(19\d{2}|20\d{2})\s*(?:-|–|—|to)\s*(?:19\d{2}|20\d{2}|present|current)\b', line, re.IGNORECASE):
        return True
    # Multiple pipes often indicate Company | Location | Role
    if line.count('|') >= 1 and ('engineer' in line.lower() or 'developer' in line.lower() or 'lead' in line.lower() or 'sdet' in line.lower() or 'remote' in line.lower()):
        return True
    # Common header indicators
    if re.match(r'^[A-Z][a-zA-Z0-9\s,\.]+\s*\|\s*', line):
        return True
    return False


def extract_bullet_points(content: str) -> List[str]:
    """Extracts genuine accomplishment bullet points from a section's text."""
    lines = content.splitlines()
    bullets: List[str] = []
    current_bullet: List[str] = []

    bullet_char_pattern = re.compile(r'^[\s]*[•\-\*–—\u2022\u25cf\u25aa\u25b8\u2713\d+\.]\s*(.*)')

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            if current_bullet:
                bullet_str = " ".join(current_bullet).strip()
                if not is_header_or_date_line(bullet_str) and len(bullet_str) > 15:
                    bullets.append(bullet_str)
                current_bullet = []
            continue

        if is_header_or_date_line(line) and not bullet_char_pattern.match(raw_line):
            # Skip job titles / company header lines
            if current_bullet:
                bullet_str = " ".join(current_bullet).strip()
                if not is_header_or_date_line(bullet_str) and len(bullet_str) > 15:
                    bullets.append(bullet_str)
                current_bullet = []
            continue

        match = bullet_char_pattern.match(raw_line)
        if match:
            if current_bullet:
                bullet_str = " ".join(current_bullet).strip()
                if not is_header_or_date_line(bullet_str) and len(bullet_str) > 15:
                    bullets.append(bullet_str)
            current_bullet = [match.group(1).strip()]
        else:
            if current_bullet:
                # Continuation of current bullet point
                current_bullet.append(line)
            else:
                # Regular line; only include if it looks like an accomplishment sentence
                if len(line) > 25 and (line.endswith('.') or line.endswith(';')) and not is_header_or_date_line(line):
                    bullets.append(line)

    if current_bullet:
        bullet_str = " ".join(current_bullet).strip()
        if not is_header_or_date_line(bullet_str) and len(bullet_str) > 15:
            bullets.append(bullet_str)

    return [b for b in bullets if len(b) > 10 and not is_header_or_date_line(b)]


def parse_sections(raw_text: str) -> List[ExtractedSection]:
    """Segments raw text into structured resume sections."""
    lines = raw_text.splitlines()
    sections: List[ExtractedSection] = []
    
    current_key: Optional[str] = None
    current_title: str = ""
    current_lines: List[str] = []

    # Before first section, capture header/intro
    intro_lines: List[str] = []

    for line in lines:
        matched_key = match_section_header(line)
        if matched_key:
            if current_key is not None:
                content = "\n".join(current_lines).strip()
                sections.append(ExtractedSection(
                    name=current_key,
                    raw_title=current_title,
                    content=content,
                    bullets=extract_bullet_points(content)
                ))
            elif intro_lines:
                intro_content = "\n".join(intro_lines).strip()
                if intro_content:
                    sections.append(ExtractedSection(
                        name="contact_header",
                        raw_title="Contact & Header",
                        content=intro_content,
                        bullets=extract_bullet_points(intro_content)
                    ))

            current_key = matched_key
            current_title = line.strip()
            current_lines = []
        else:
            if current_key is None:
                intro_lines.append(line)
            else:
                current_lines.append(line)

    # Flush last section
    if current_key is not None:
        content = "\n".join(current_lines).strip()
        sections.append(ExtractedSection(
            name=current_key,
            raw_title=current_title,
            content=content,
            bullets=extract_bullet_points(content)
        ))
    elif intro_lines:
        # No headings detected at all; entire resume is one block
        content = "\n".join(intro_lines).strip()
        sections.append(ExtractedSection(
            name="general",
            raw_title="Resume Content",
            content=content,
            bullets=extract_bullet_points(content)
        ))

    return sections
