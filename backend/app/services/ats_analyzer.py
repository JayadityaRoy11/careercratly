from __future__ import annotations

import re
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.data.loader import get_role, load_roles
from app.services.resume_intelligence import build_intelligence
from app.services.skill_extractor import get_skill_extractor

SECTION_PATTERNS = {
    "education": re.compile(r"\b(education|academic|university|bachelor|master|b\.tech|btech)\b", re.I),
    "experience": re.compile(r"\b(experience|employment|work history|intern)\b", re.I),
    "skills": re.compile(r"\b(skills|technical skills|technologies)\b", re.I),
    "projects": re.compile(r"\b(projects?|portfolio|hackathon)\b", re.I),
}

EXPERIENCE_PATTERNS = [
    re.compile(r"\b(\d+)\+?\s*(years?|yrs)\b", re.I),
    re.compile(r"\b(intern(ship)?|project|built|developed|deployed|designed)\b", re.I),
]

RELATED_SKILLS: dict[str, set[str]] = {
    "PostgreSQL": {"SQL", "MySQL"},
    "MySQL": {"SQL", "PostgreSQL"},
    "SQL": {"PostgreSQL", "MySQL"},
    "REST APIs": {"REST", "FastAPI", "Flask", "Django"},
    "REST": {"REST APIs"},
    "pytest": {"Pytest", "Unit Testing"},
    "Pytest": {"pytest", "Unit Testing"},
    "GitHub": {"Git"},
    "Git": {"GitHub"},
    "Generative AI": {"LLMs", "NLP"},
    "LLMs": {"Generative AI", "NLP"},
    "scikit-learn": {"Machine Learning"},
    "Machine Learning": {"scikit-learn"},
    "React": {"JavaScript", "TypeScript"},
    "Node.js": {"JavaScript"},
    "FastAPI": {"Python", "REST APIs"},
}


class UnknownRoleError(Exception):
    def __init__(self, role: str) -> None:
        self.role = role
        self.available = [item["name"] for item in load_roles()]
        super().__init__(f"Unknown target role: {role}")


def analyze_resume_against_role(*, text: str, target_role: str) -> dict[str, Any]:
    role = get_role(target_role)
    if role is None:
        raise UnknownRoleError(target_role)

    extracted = get_skill_extractor().extract(text)
    extracted_set = set(extracted)

    required = list(role["required_skills"])
    preferred = list(role["preferred_skills"])
    optional = list(role["optional_skills"])

    matched_required = [s for s in required if s in extracted_set]
    matched_preferred = [s for s in preferred if s in extracted_set]
    matched_optional = [s for s in optional if s in extracted_set]
    matched_skills = sorted(set(matched_required + matched_preferred + matched_optional + [s for s in extracted if s in required + preferred + optional]))

    missing_required = [s for s in required if s not in extracted_set]
    missing_preferred = [s for s in preferred if s not in extracted_set]
    missing_skills = missing_required + [s for s in missing_preferred if s not in missing_required]

    partial_matches = _partial_matches(extracted_set, set(missing_skills))

    required_coverage = _coverage(matched_required, required)
    preferred_coverage = _coverage(matched_preferred, preferred)
    keyword_relevance = _keyword_relevance(text, role)
    experience_relevance = _experience_relevance(text)
    section_completeness = _section_completeness(text)

    score = round(
        40 * required_coverage
        + 20 * preferred_coverage
        + 15 * keyword_relevance
        + 15 * experience_relevance
        + 10 * section_completeness
    )
    score = max(0, min(100, score))

    strengths = []
    if required_coverage >= 0.7:
        strengths.append("Strong coverage of required skills for this role.")
    if matched_preferred:
        strengths.append("Includes preferred skills: " + ", ".join(matched_preferred[:5]) + ".")
    if section_completeness >= 0.75:
        strengths.append("Resume includes core sections (skills, experience/projects, education).")
    if experience_relevance >= 0.6:
        strengths.append("Experience and project language is present.")

    improvements = []
    for skill in missing_required:
        improvements.append(f"Add evidence of {skill} (project, coursework, or job bullet).")
    if section_completeness < 0.75:
        missing_sections = [name for name, pattern in SECTION_PATTERNS.items() if not pattern.search(text)]
        if missing_sections:
            improvements.append("Add labeled sections: " + ", ".join(missing_sections) + ".")
    if experience_relevance < 0.4:
        improvements.append("Quantify internships or projects with tools used and outcomes.")

    recommended_keywords = missing_required[:8] + [s for s in missing_preferred if s not in missing_required][:5]

    result = {
        "score": score,
        "score_label": "Resume Match Score",
        "target_role": role["name"],
        "target_role_slug": role["slug"],
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "partial_matches": partial_matches,
        "strengths": strengths or ["Keep building role-specific projects and keywords."],
        "improvements": improvements[:10],
        "recommended_keywords": recommended_keywords,
        "recommended_certifications": list(role.get("recommended_certifications") or []),
        "recommended_project_themes": list(role.get("recommended_project_themes") or []),
        "components": {
            "required_skill_coverage": round(required_coverage, 4),
            "preferred_skill_coverage": round(preferred_coverage, 4),
            "keyword_relevance": round(keyword_relevance, 4),
            "experience_project_relevance": round(experience_relevance, 4),
            "resume_section_completeness": round(section_completeness, 4),
        },
        "disclaimer": (
            "This is an explainable prototype Resume Match Score, not a proprietary ATS ranking."
        ),
        "extracted_skills": extracted,
        "intelligence": build_intelligence(text=text, role=role, extracted=extracted),
    }
    result["intelligence"]["alignment"]["overall_score"] = {
        "score": score,
        "explanation": (
            f"Explainable Resume Match Score for {role['name']} from required/preferred skills, "
            "keyword overlap, experience language, and section completeness — not a company ATS rank."
        ),
    }
    return result


def _coverage(matched: list[str], total: list[str]) -> float:
    if not total:
        return 1.0
    return len(matched) / len(total)


def _keyword_relevance(text: str, role: dict[str, Any]) -> float:
    corpus_terms = " ".join(
        role["required_skills"] + role["preferred_skills"] + (role.get("optional_skills") or [])
    )
    if not text.strip() or not corpus_terms.strip():
        return 0.0
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), min_df=1)
    matrix = vectorizer.fit_transform([text, corpus_terms])
    similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    return max(0.0, min(1.0, similarity))


def _experience_relevance(text: str) -> float:
    hits = sum(1 for pattern in EXPERIENCE_PATTERNS if pattern.search(text))
    word_count = len(text.split())
    length_score = min(1.0, word_count / 250)
    return max(0.0, min(1.0, 0.55 * (hits / len(EXPERIENCE_PATTERNS)) + 0.45 * length_score))


def _section_completeness(text: str) -> float:
    present = sum(1 for pattern in SECTION_PATTERNS.values() if pattern.search(text))
    return present / len(SECTION_PATTERNS)


def _partial_matches(extracted: set[str], missing: set[str]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    for skill in sorted(missing):
        related = RELATED_SKILLS.get(skill, set())
        overlap = sorted(related & extracted)
        if overlap:
            results.append(
                {
                    "skill": skill,
                    "related_found": ", ".join(overlap),
                    "note": f"Related skill(s) found: {', '.join(overlap)}",
                }
            )
    return results
