from __future__ import annotations

import re
from typing import Any

HEADER_MAP = {
    "summary": re.compile(r"^(summary|objective|profile|about me)\b", re.I),
    "experience": re.compile(r"^(experience|work experience|employment|work history|professional experience)\b", re.I),
    "projects": re.compile(r"^(projects?|personal projects|academic projects|portfolio)\b", re.I),
    "education": re.compile(r"^(education|academic|academics)\b", re.I),
    "skills": re.compile(r"^(skills|technical skills|technologies|tech stack)\b", re.I),
    "certifications": re.compile(r"^(certifications?|certificates|licenses)\b", re.I),
    "achievements": re.compile(r"^(achievements?|awards|honors|accomplishments)\b", re.I),
}

CONTACT_EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
CONTACT_PHONE = re.compile(r"(\+?\d[\d\s\-()]{8,}\d)")
CONTACT_LINK = re.compile(r"https?://[^\s)]+", re.I)
BULLET = re.compile(r"^\s*(?:[-*•]|)\s*(.+)$")
NUMBER = re.compile(r"\b\d+(?:\.\d+)?%?\b")
ACTION = re.compile(
    r"\b(built|developed|designed|implemented|created|led|improved|optimized|deployed|automated|analyzed|trained|engineered)\b",
    re.I,
)
WEAK_LINE = re.compile(r"^(worked on|responsible for|helped with|involved in)\b", re.I)


def build_intelligence(*, text: str, role: dict[str, Any], extracted: list[str]) -> dict[str, Any]:
    sections = _split_sections(text)
    present = {name: bool(body.strip()) for name, body in sections.items()}
    contact = _contact(text)
    bullets = _bullets(sections.get("experience", "") + "\n" + sections.get("projects", ""))
    projects = _projects(sections.get("projects", ""), extracted)
    section_reviews = _section_reviews(sections, extracted, bullets)
    keyword_gap = _keyword_gap(text, extracted, role)
    alignment = _alignment(text, role, extracted, present, bullets)
    roadmap = _roadmap(role, extracted, present, bullets, section_reviews)
    overall = _overall_summary(role, extracted, present, bullets, alignment)

    return {
        "overview": overall,
        "contact": contact,
        "detected_sections": present,
        "missing_sections": [name for name, ok in present.items() if not ok],
        "section_reviews": section_reviews,
        "keyword_gap": keyword_gap,
        "bullet_analysis": bullets,
        "projects_analysis": projects,
        "alignment": alignment,
        "roadmap": roadmap,
        "metric_policy": (
            "Do not invent employers, metrics, or technologies. "
            "Add numbers only when you have the real measurement."
        ),
    }


def _split_sections(text: str) -> dict[str, str]:
    buckets = {key: [] for key in HEADER_MAP}
    buckets["summary"] = []
    current = "summary"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        matched_header = None
        for name, pattern in HEADER_MAP.items():
            if pattern.match(line) and len(line) < 48:
                matched_header = name
                break
        if matched_header:
            current = matched_header
            continue
        buckets[current].append(line)
    return {name: "\n".join(lines) for name, lines in buckets.items()}


def _contact(text: str) -> dict[str, Any]:
    email = CONTACT_EMAIL.search(text)
    phone = CONTACT_PHONE.search(text)
    links = CONTACT_LINK.findall(text)[:5]
    return {
        "email_found": bool(email),
        "phone_found": bool(phone),
        "links_found": links,
        "issues": [
            item
            for item, ok in (
                ("Add an email address if it is missing.", not email),
                ("Add a phone number if you want recruiters to call.", not phone),
            )
            if ok
        ],
    }


def _bullets(block: str) -> dict[str, Any]:
    items = []
    for raw in block.splitlines():
        line = raw.strip().lstrip("-*• ").strip()
        if len(line) < 18:
            continue
        has_action = bool(ACTION.search(line))
        has_number = bool(NUMBER.search(line))
        weak = bool(WEAK_LINE.search(line)) or (not has_action)
        items.append(
            {
                "text": line,
                "has_action": has_action,
                "has_metric": has_number,
                "weak": weak,
                "problem": _bullet_problem(has_action, has_number, weak),
                "suggested_structure": (
                    "Developed [what] using [technology] to [purpose], resulting in [your real measurable result]."
                ),
            }
        )
    weak_items = [item for item in items if item["weak"] or not item["has_metric"]]
    return {
        "count": len(items),
        "items": items[:12],
        "weak_count": len(weak_items),
        "guidance": "Quantify outcomes only with numbers you actually have (time saved, F1-score, dataset size, users).",
    }


def _bullet_problem(has_action: bool, has_number: bool, weak: bool) -> str:
    bits = []
    if weak or not has_action:
        bits.append("vague action")
    if not has_number:
        bits.append("no measurable outcome")
    return ", ".join(bits) or "could be more specific"


def _projects(block: str, extracted: list[str]) -> list[dict[str, Any]]:
    chunks = re.split(r"\n{2,}", block.strip()) if block.strip() else []
    results = []
    for chunk in chunks[:6]:
        title = chunk.splitlines()[0][:80] if chunk.splitlines() else "Untitled project"
        lower = chunk.lower()
        results.append(
            {
                "title": title,
                "detected_signals": {
                    "problem": bool(re.search(r"problem|challenge|to (solve|address)", lower)),
                    "method": bool(re.search(r"using|with|pipeline|model|api", lower)),
                    "dataset": bool(re.search(r"dataset|kaggle|records|corpus", lower)),
                    "result": bool(NUMBER.search(chunk)),
                    "deployment": bool(re.search(r"deploy|docker|aws|hosted|production", lower)),
                },
                "detected_skills": [s for s in extracted if s.lower() in lower][:8],
                "missing_information": [
                    label
                    for label, ok in (
                        ("evaluation metrics — insert the real score if you measured it", not NUMBER.search(chunk)),
                        ("dataset or data source", not re.search(r"dataset|kaggle|records|corpus", lower)),
                        ("deployment or hosting", not re.search(r"deploy|docker|aws|hosted|production", lower)),
                        ("architecture / method", not re.search(r"using|pipeline|architecture|api", lower)),
                    )
                    if ok
                ],
                "recommendations": [
                    "Document architecture if the project has multiple components.",
                    "Mention the evaluation method you actually used.",
                    "Include deployment only if it was deployed.",
                ],
            }
        )
    return results


def _section_reviews(sections: dict[str, str], extracted: list[str], bullets: dict[str, Any]) -> list[dict[str, Any]]:
    reviews = []
    for name, body in sections.items():
        present = bool(body.strip())
        words = len(body.split())
        score = 0
        strengths: list[str] = []
        issues: list[str] = []
        improvements: list[str] = []
        if not present:
            issues.append(f"No labeled {name} section was detected.")
            improvements.append(f"Add a clearly headed {name} section if that content exists.")
        else:
            score += 40
            if words >= 20:
                score += 20
                strengths.append("Section has enough text to review.")
            else:
                issues.append("Section is too short to evidence impact.")
                improvements.append("Expand with concrete tools and outcomes you actually have.")
            if name in {"experience", "projects"}:
                if bullets["count"]:
                    score += 20
                    strengths.append("Contains reviewable bullets or project lines.")
                if bullets["weak_count"]:
                    issues.append("Some bullets are generic (action/result missing).")
                    improvements.append(
                        'Prefer: "Developed [what] using [tech] to [purpose], resulting in [real metric]."'
                    )
                else:
                    score += 20
            if name == "skills" and extracted:
                score += 25
                strengths.append(f"Detected skills include {', '.join(extracted[:4])}.")
            if name == "education" and re.search(r"bachelor|master|b\.tech|btech|university|degree", body, re.I):
                score += 25
                strengths.append("Education credentials appear to be present.")
            if name == "summary" and words >= 12:
                score += 15
                strengths.append("Opening summary/profile text was found.")
            if name == "certifications" and present:
                score += 20
        reviews.append(
            {
                "name": name,
                "status": "present" if present else "missing",
                "score": min(100, score),
                "strengths": strengths or ["Add this section if the experience is real."],
                "issues": issues,
                "improvements": improvements,
            }
        )
    return reviews


def _keyword_gap(text: str, extracted: list[str], role: dict[str, Any]) -> dict[str, Any]:
    required = role["required_skills"]
    preferred = role["preferred_skills"]
    lower = text.lower()
    extracted_set = set(extracted)
    missing = [s for s in required + preferred if s not in extracted_set]
    weak = [
        s
        for s in extracted
        if s in required + preferred and lower.count(s.lower()) == 1
    ]
    return {
        "detected": extracted,
        "missing": missing,
        "weak": weak,
        "placement": [
            {
                "skill": skill,
                "advice": (
                    f"Mention {skill} in a project or experience bullet only if you have genuine experience with it."
                ),
            }
            for skill in missing[:8]
        ],
    }


def _alignment(
    text: str,
    role: dict[str, Any],
    extracted: list[str],
    present: dict[str, bool],
    bullets: dict[str, Any],
) -> dict[str, Any]:
    extracted_set = set(extracted)
    required = role["required_skills"]
    preferred = role["preferred_skills"]
    req_cov = _pct([s for s in required if s in extracted_set], required)
    pref_cov = _pct([s for s in preferred if s in extracted_set], preferred)
    keyword = round(100 * (len([s for s in required + preferred if s in extracted_set]) / max(len(required + preferred), 1)))
    experience = 80 if present["experience"] else 25
    project = 80 if present["projects"] else 30
    if bullets["count"] and bullets["weak_count"] == 0:
        experience = min(100, experience + 10)
        project = min(100, project + 10)
    achievement = 70 if present["achievements"] or bullets["items"] and any(i["has_metric"] for i in bullets["items"]) else 28
    education = 85 if present["education"] else 20
    certification = 80 if present["certifications"] else 15
    missing_req = [s for s in required if s not in extracted_set]
    return {
        "keyword_match": {
            "score": keyword,
            "explanation": f"Role keywords from the {role['name']} profile overlap with detected skills. Missing required: {', '.join(missing_req) or 'none'}.",
        },
        "required_skill_coverage": {
            "score": req_cov,
            "explanation": (
                f"Your resume mentions {', '.join(s for s in required if s in extracted_set) or 'none of the required skills'}. "
                f"Not detected: {', '.join(missing_req) or 'none'}."
            ),
        },
        "preferred_skill_coverage": {
            "score": pref_cov,
            "explanation": f"Preferred skills detected: {', '.join(s for s in preferred if s in extracted_set) or 'none'}.",
        },
        "experience_relevance": {
            "score": experience,
            "explanation": "Experience section detected." if present["experience"] else "No experience heading was found.",
        },
        "project_relevance": {
            "score": project,
            "explanation": "Projects section detected." if present["projects"] else "Add a Projects section if you have academic or personal work.",
        },
        "section_completeness": {
            "score": round(100 * sum(1 for v in present.values() if v) / len(present)),
            "explanation": "Measured from labeled sections: summary, experience, projects, education, skills, certifications, achievements.",
        },
        "achievement_strength": {
            "score": achievement,
            "explanation": "Looks for numbers or an achievements heading. Do not invent percentages.",
        },
        "education_alignment": {
            "score": education,
            "explanation": "Education heading detected." if present["education"] else "Education section missing.",
        },
        "certification_alignment": {
            "score": certification,
            "explanation": "Certifications heading detected." if present["certifications"] else "No certifications section found.",
        },
    }


def _roadmap(
    role: dict[str, Any],
    extracted: list[str],
    present: dict[str, bool],
    bullets: dict[str, Any],
    reviews: list[dict[str, Any]],
) -> dict[str, list[dict[str, str]]]:
    extracted_set = set(extracted)
    high: list[dict[str, str]] = []
    medium: list[dict[str, str]] = []
    optional: list[dict[str, str]] = []
    for skill in role["required_skills"]:
        if skill not in extracted_set:
            high.append(
                {
                    "issue": f"{skill} not detected",
                    "why": f"Listed as required for {role['name']}.",
                    "what": f"Add a bullet about {skill} only if you have genuine experience.",
                    "benefit": "Improves required-skill coverage in the Resume Match Score.",
                }
            )
    if not present["projects"]:
        high.append(
            {
                "issue": "Projects section missing",
                "why": "Hiring screens often look for applied work.",
                "what": "Add 1–2 real projects with stack, method, and a real outcome if measured.",
                "benefit": "Gives evidence beyond a skills list.",
            }
        )
    if bullets["weak_count"]:
        medium.append(
            {
                "issue": "Generic bullets",
                "why": "Vague lines do not show action, tech, or result.",
                "what": "Rewrite weak bullets with action + technology + task; add a metric only if you have it.",
                "benefit": "Makes experience easier to scan.",
            }
        )
    for skill in role["preferred_skills"]:
        if skill not in extracted_set:
            medium.append(
                {
                    "issue": f"Preferred skill {skill} not detected",
                    "why": "Helps preferred-skill coverage, not a hard gate in this prototype.",
                    "what": f"Mention {skill} only with real experience.",
                    "benefit": "Slightly stronger role alignment.",
                }
            )
    if not present["certifications"]:
        optional.append(
            {
                "issue": "No certifications section",
                "why": "Optional signal for cloud/data roles.",
                "what": "Add certifications you actually hold; otherwise skip.",
                "benefit": "Supports certification alignment if relevant.",
            }
        )
    missing_named = [r["name"] for r in reviews if r["status"] == "missing" and r["name"] in {"summary", "achievements"}]
    for name in missing_named:
        optional.append(
            {
                "issue": f"{name} section missing",
                "why": "Completeness scoring looks for labeled headings.",
                "what": f"Add a short {name} section if you have real content.",
                "benefit": "Improves section completeness.",
            }
        )
    return {"high": high[:6], "medium": medium[:6], "optional": optional[:4]}


def _overall_summary(
    role: dict[str, Any],
    extracted: list[str],
    present: dict[str, bool],
    bullets: dict[str, Any],
    alignment: dict[str, Any],
) -> dict[str, Any]:
    good = [s for s in role["required_skills"] if s in extracted]
    missing = [s for s in role["required_skills"] if s not in extracted]
    return {
        "what_is_good": (
            f"Detected required skills for {role['name']}: {', '.join(good) or 'none yet'}."
        ),
        "why_it_is_good": "Those keywords can be matched to the role profile without claiming a vendor ATS score.",
        "what_is_missing": ", ".join(missing) or "No required skills missing from detection.",
        "why_it_matters": "Required-skill coverage is the largest component of the Resume Match Score.",
        "what_to_change": "Rewrite weak bullets and add missing labeled sections that reflect real work.",
        "how_to_change": "Use action + technology + task, then a real metric if you have one.",
        "skills_to_learn": missing[:6],
        "project_ideas": list(role.get("recommended_project_themes") or []),
        "certifications": list(role.get("recommended_certifications") or []),
        "section_presence": present,
        "weak_bullets": bullets["weak_count"],
        "headline_alignment": alignment["required_skill_coverage"]["score"],
    }


def _pct(matched: list[str], total: list[str]) -> int:
    if not total:
        return 100
    return round(100 * len(matched) / len(total))
