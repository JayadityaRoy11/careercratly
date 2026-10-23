from __future__ import annotations

import re
from typing import Any

from app.data.loader import get_role, load_interview, load_roles

_WORD = re.compile(r"[a-z0-9+#]+(?:[ /-]?[a-z0-9+#]+)*", re.I)


def list_questions(*, role: str, difficulty: str) -> dict[str, Any]:
    bank = load_interview()
    resolved_role = _resolve_role_name(role)
    difficulty_key = difficulty.strip().lower()
    if difficulty_key not in {"easy", "medium", "hard"}:
        difficulty_key = "medium"
    pack = bank.get(resolved_role) or bank.get("default") or {}
    questions = pack.get(difficulty_key) or bank["default"][difficulty_key]
    return {
        "role": resolved_role,
        "difficulty": difficulty_key,
        "questions": [
            {"id": item["id"], "question": item["question"]}
            for item in questions
        ],
    }


def evaluate_answer(*, role: str, question: str, answer: str) -> dict[str, Any]:
    expected = _expected_keywords(role=role, question=question)
    answer_lower = answer.lower()
    hits = [kw for kw in expected if kw.lower() in answer_lower]
    missing = [kw for kw in expected if kw.lower() not in answer_lower]
    keyword_coverage = 0 if not expected else round(100 * len(hits) / len(expected))

    words = _WORD.findall(answer)
    sentences = [part for part in re.split(r"[.!?]+", answer) if part.strip()]
    structure_score = 0
    if len(words) >= 40:
        structure_score += 40
    elif len(words) >= 20:
        structure_score += 25
    elif len(words) >= 8:
        structure_score += 10
    if len(sentences) >= 3:
        structure_score += 30
    elif len(sentences) >= 2:
        structure_score += 20
    if re.search(r"\b(because|for example|first|then|finally|therefore)\b", answer, re.I):
        structure_score += 30
    structure_score = min(100, structure_score)

    technical_relevance = min(
        100,
        round(0.75 * keyword_coverage + 0.25 * min(100, len(words) * 2)),
    )
    score = round(0.5 * keyword_coverage + 0.3 * technical_relevance + 0.2 * structure_score)

    strengths: list[str] = []
    if keyword_coverage >= 60:
        strengths.append("Covers several expected technical keywords.")
    if structure_score >= 60:
        strengths.append("Answer has a readable structure.")
    if len(words) >= 40:
        strengths.append("Enough detail for a prototype text evaluation.")

    suggestions: list[str] = []
    if missing:
        suggestions.append("Mention: " + ", ".join(missing[:6]) + ".")
    if len(words) < 25:
        suggestions.append("Expand the answer with a concrete example and outcome.")
    if structure_score < 50:
        suggestions.append("Use a short structure: context, approach, result.")

    return {
        "score": score,
        "keyword_coverage": keyword_coverage,
        "technical_relevance": technical_relevance,
        "structure_score": structure_score,
        "strengths": strengths or ["Keep answers specific to the role and tools."],
        "missing_keywords": missing,
        "suggestions": suggestions,
    }


def _resolve_role_name(role: str) -> str:
    found = get_role(role)
    if found:
        return found["name"]
    bank = load_interview()
    for name in bank:
        if name.lower() == role.strip().lower():
            return name
    return "default"


def _expected_keywords(*, role: str, question: str) -> list[str]:
    bank = load_interview()
    resolved = _resolve_role_name(role)
    packs = bank.get(resolved) or bank.get("default") or {}
    normalized_q = question.strip().lower()
    for level in packs.values():
        for item in level:
            if item["question"].strip().lower() == normalized_q:
                return list(item.get("keywords") or [])
    fallback = get_role(role)
    if fallback:
        return list(fallback["required_skills"][:6])
    if load_roles():
        return ["project", "impact", "stack"]
    return []
