from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WeightedSkill:
    name: str
    weight: float


@dataclass(frozen=True)
class MatchResult:
    matched_skills: list[WeightedSkill]
    missing_skills: list[WeightedSkill]
    match_score: float


def score_skills(
    extracted: list[str],
    required: list[WeightedSkill],
) -> MatchResult:
    extracted_set = {name.lower() for name in extracted}
    matched: list[WeightedSkill] = []
    missing: list[WeightedSkill] = []
    matched_weight = 0.0
    total_weight = 0.0

    for skill in required:
        total_weight += skill.weight
        if skill.name.lower() in extracted_set:
            matched.append(skill)
            matched_weight += skill.weight
        else:
            missing.append(skill)

    score = 0.0 if total_weight == 0 else round(100.0 * matched_weight / total_weight, 2)
    return MatchResult(matched_skills=matched, missing_skills=missing, match_score=score)
