import re
from typing import Dict, List, Set, Tuple, Optional
from app.models.schemas import KeywordItem, KeywordAnalysis
from app.engine.rules import SKILL_SYNONYMS, COMMON_TECH_SKILLS


def clean_token(text: str) -> str:
    """Normalizes text for token matching."""
    return re.sub(r'[^\w\s\+\#\./\-]', ' ', text.lower()).strip()


def extract_skills_from_text(text: str) -> Dict[str, int]:
    """
    Extracts known skills and tools from text, along with their occurrence counts.
    Returns {canonical_skill_name: frequency}.
    """
    cleaned = clean_token(text)
    words = set(cleaned.split())
    
    skill_counts: Dict[str, int] = {}

    # Check known synonym canonical groups
    for canonical, synonyms in SKILL_SYNONYMS.items():
        count = 0
        for syn in synonyms:
            # Word boundary regex search
            escaped_syn = re.escape(syn)
            matches = re.findall(rf'(?:\b|_){escaped_syn}(?:\b|_)', cleaned)
            count += len(matches)
        
        if count > 0:
            skill_counts[canonical] = count

    # Check standalone common skills not in synonyms
    for skill in COMMON_TECH_SKILLS:
        if skill not in skill_counts:
            escaped = re.escape(skill)
            matches = re.findall(rf'(?:\b|_){escaped}(?:\b|_)', cleaned)
            if matches:
                skill_counts[skill] = len(matches)

    return skill_counts


def parse_job_description_requirements(jd_text: str) -> Tuple[Set[str], Set[str]]:
    """
    Parses Job Description into:
    - required_skills: Set[str]
    - preferred_skills: Set[str]
    """
    lines = jd_text.splitlines()
    required_lines = []
    preferred_lines = []
    
    current_mode = "required"  # default assumption for JD lines
    
    req_header_pat = re.compile(
        r'^(?:requirements|qualifications|must\s+have|minimum\s+qualifications|what\s+you\s+need|basic\s+qualifications)',
        re.IGNORECASE
    )
    pref_header_pat = re.compile(
        r'^(?:preferred\s+qualifications|nice\s+to\s+have|bonus|plus|desired\s+skills)',
        re.IGNORECASE
    )

    for line in lines:
        stripped = line.strip().lower()
        if req_header_pat.search(stripped):
            current_mode = "required"
            continue
        elif pref_header_pat.search(stripped):
            current_mode = "preferred"
            continue
            
        if current_mode == "preferred":
            preferred_lines.append(line)
        else:
            required_lines.append(line)

    req_text = "\n".join(required_lines)
    pref_text = "\n".join(preferred_lines)

    req_skills_map = extract_skills_from_text(req_text)
    pref_skills_map = extract_skills_from_text(pref_text)

    # Any skill in preferred that isn't in required
    preferred_skills = set(pref_skills_map.keys()) - set(req_skills_map.keys())
    required_skills = set(req_skills_map.keys())

    # If nothing was parsed as preferred, treat top skills as required
    if not required_skills and not preferred_skills:
        all_skills = extract_skills_from_text(jd_text)
        required_skills = set(all_skills.keys())

    return required_skills, preferred_skills


def analyze_keywords(resume_text: str, jd_text: Optional[str] = None) -> KeywordAnalysis:
    """
    Evaluates keyword matches, synonyms, and gaps between resume and job description.
    If jd_text is None, evaluates general resume skill breadth.
    """
    resume_skills_map = extract_skills_from_text(resume_text)
    resume_text_lower = clean_token(resume_text)

    if not jd_text or not jd_text.strip():
        # Resume-only mode: identify skills present in resume
        matched_items = [
            KeywordItem(
                skill=skill.title(),
                importance="general",
                matched=True,
                match_type="exact",
                frequency_in_resume=freq
            )
            for skill, freq in sorted(resume_skills_map.items(), key=lambda x: -x[1])
        ]
        return KeywordAnalysis(
            total_jd_keywords=len(matched_items),
            matched_exact=matched_items,
            matched_synonyms=[],
            missing_required=[],
            missing_preferred=[],
            other_resume_skills=[s.title() for s in resume_skills_map.keys()]
        )

    # Job description provided:
    required_skills, preferred_skills = parse_job_description_requirements(jd_text)
    all_jd_skills = required_skills | preferred_skills

    matched_exact: List[KeywordItem] = []
    matched_synonyms: List[KeywordItem] = []
    missing_required: List[KeywordItem] = []
    missing_preferred: List[KeywordItem] = []

    for canonical in all_jd_skills:
        importance = "preferred" if canonical in preferred_skills else "required"
        synonyms = SKILL_SYNONYMS.get(canonical, {canonical})

        # Check if canonical name exists in resume text
        exact_found = False
        if re.search(rf'\b{re.escape(canonical)}\b', resume_text_lower):
            exact_found = True
            matched_exact.append(KeywordItem(
                skill=canonical.title(),
                importance=importance,
                matched=True,
                match_type="exact",
                frequency_in_resume=resume_skills_map.get(canonical, 1)
            ))
            continue

        # Check if any synonym exists in resume text
        synonym_found = None
        for syn in synonyms:
            if re.search(rf'\b{re.escape(syn)}\b', resume_text_lower):
                synonym_found = syn
                break

        if synonym_found:
            matched_synonyms.append(KeywordItem(
                skill=canonical.title(),
                importance=importance,
                matched=True,
                match_type="synonym",
                matched_via=synonym_found,
                frequency_in_resume=resume_skills_map.get(canonical, 1)
            ))
        else:
            item = KeywordItem(
                skill=canonical.title(),
                importance=importance,
                matched=False,
                match_type="missing",
                frequency_in_resume=0
            )
            if importance == "required":
                missing_required.append(item)
            else:
                missing_preferred.append(item)

    other_skills = [
        s.title() for s in resume_skills_map.keys()
        if s not in all_jd_skills
    ]

    return KeywordAnalysis(
        total_jd_keywords=len(all_jd_skills),
        matched_exact=matched_exact,
        matched_synonyms=matched_synonyms,
        missing_required=missing_required,
        missing_preferred=missing_preferred,
        other_resume_skills=sorted(other_skills)
    )
