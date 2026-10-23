"""Pluggable skill extraction.

Set SKILL_EXTRACTOR=spacy (PhraseMatcher, default) or SKILL_EXTRACTOR=llm.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod

from spacy.lang.en import English
from spacy.matcher import PhraseMatcher

from app.data.loader import load_skills, skill_alias_map

_SPECIAL_CHARS = set("#+/.")


class SkillExtractor(ABC):
    name: str

    @abstractmethod
    def extract(self, raw_text: str) -> list[str]:
        """Return canonical skill names found in resume text."""


class SpacyPhraseMatcherExtractor(SkillExtractor):
    """Rule-based extractor using spaCy PhraseMatcher against the master skill list."""

    name = "spacy"

    def __init__(self) -> None:
        self._alias_to_canonical = skill_alias_map()
        self._nlp = English()
        self._matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
        self._regex_terms: list[tuple[re.Pattern[str], str]] = []
        self._build_patterns()

    def _should_use_phrase(self, term: str) -> bool:
        stripped = term.strip()
        if not stripped:
            return False
        if any(ch in stripped for ch in _SPECIAL_CHARS):
            return False
        if len(stripped) <= 2:
            return False
        return True

    def _build_patterns(self) -> None:
        phrases: list = []
        for skill in load_skills():
            canonical = skill["name"]
            terms = [canonical, *(skill.get("aliases") or [])]
            for term in terms:
                if self._should_use_phrase(term):
                    phrases.append(self._nlp.make_doc(term))
                else:
                    pattern = re.compile(
                        rf"(?<![\w+#]){re.escape(term)}(?![\w+#])",
                        re.IGNORECASE,
                    )
                    self._regex_terms.append((pattern, canonical))
        if phrases:
            self._matcher.add("SKILLS", phrases)

    def extract(self, raw_text: str) -> list[str]:
        if not raw_text or not raw_text.strip():
            return []

        found: set[str] = set()
        doc = self._nlp.make_doc(raw_text)
        for _match_id, start, end in self._matcher(doc):
            span = doc[start:end]
            canonical = self._alias_to_canonical.get(span.text.lower())
            if canonical:
                found.add(canonical)

        for pattern, canonical in self._regex_terms:
            if pattern.search(raw_text):
                found.add(canonical)

        return sorted(found)


class LLMSkillExtractor(SkillExtractor):
    """Placeholder for an LLM-based extractor. Swap in via SKILL_EXTRACTOR=llm."""

    name = "llm"

    def extract(self, raw_text: str) -> list[str]:
        raise NotImplementedError(
            "LLM skill extraction is not implemented yet. "
            "Set SKILL_EXTRACTOR=spacy to use the PhraseMatcher extractor."
        )


_extractor: SkillExtractor | None = None


def get_skill_extractor() -> SkillExtractor:
    global _extractor
    if _extractor is None:
        _extractor = SpacyPhraseMatcherExtractor()
    return _extractor
