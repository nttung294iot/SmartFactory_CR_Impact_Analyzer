from __future__ import annotations

from typing import Any
import re

from .utils import strip_accents, unique_preserve_order


class SynonymService:
    """Build phrase and token mappings from the editable synonym dictionary."""

    def __init__(self, records: list[dict[str, Any]]) -> None:
        self.records = [item for item in records if item.get("enabled", True)]
        self.phrase_map: dict[str, str] = {}
        self.canonical_to_terms: dict[str, list[str]] = {}
        for item in self.records:
            canonical = item["canonical_term"].strip().lower()
            terms = [canonical] + item.get("vietnamese_synonyms", []) + item.get("english_synonyms", [])
            normalized_terms: list[str] = []
            for term in terms:
                normalized = self.normalize_key(term)
                if normalized:
                    self.phrase_map[normalized] = canonical
                    normalized_terms.append(normalized)
            self.canonical_to_terms[canonical] = unique_preserve_order(normalized_terms)

    @staticmethod
    def normalize_key(text: str) -> str:
        return " ".join(strip_accents(str(text).lower()).split())

    def apply_phrase_normalization(self, text: str) -> tuple[str, list[dict[str, str]]]:
        original = self.normalize_key(text)
        normalized = original
        matched: list[dict[str, str]] = []
        # Detect matches on the original string so overlapping domain phrases
        # such as "phiếu bảo trì khẩn cấp" can preserve both work_order and
        # emergency_maintenance semantics.
        for phrase in sorted(self.phrase_map, key=len, reverse=True):
            canonical = self.phrase_map[phrase]
            pattern = rf"(?<![a-z0-9_]){re.escape(phrase)}(?![a-z0-9_])"
            if re.search(pattern, original):
                matched.append({"phrase": phrase, "canonical": canonical})
                normalized = re.sub(pattern, f" {canonical} ", normalized)
        canonical_terms = [item["canonical"] for item in matched]
        for canonical in canonical_terms:
            if canonical not in normalized.split():
                normalized += f" {canonical}"
        return " ".join(normalized.split()), matched

    def expand(self, tokens: list[str]) -> tuple[list[str], list[dict[str, str]]]:
        expanded = list(tokens)
        matched: list[dict[str, str]] = []
        for token in tokens:
            canonical = self.phrase_map.get(self.normalize_key(token), token)
            if canonical in self.canonical_to_terms:
                expanded.append(canonical)
                matched.append({"term": token, "canonical": canonical})
                # Add compact token forms only; full phrases are already canonicalized.
                for term in self.canonical_to_terms[canonical]:
                    compact = term.replace(" ", "_")
                    expanded.append(compact)
        return unique_preserve_order(expanded), matched
