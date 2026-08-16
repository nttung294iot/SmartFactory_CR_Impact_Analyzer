from __future__ import annotations

import re
import unicodedata
from collections import Counter
from typing import Any

from .models import PreprocessingResult
from .synonym_service import SynonymService
from .utils import strip_accents, unique_preserve_order


STOPWORDS = {
    "la", "va", "hoac", "cua", "cho", "trong", "khi", "neu", "thi", "duoc", "phai", "se", "mot",
    "nhung", "cac", "the", "he", "thong", "sau", "truoc", "tai", "theo", "co", "can", "yeu", "cau",
    "the", "a", "an", "and", "or", "the", "of", "to", "for", "in", "on", "at", "with", "from", "by",
}

ROLE_TERMS = {
    "technician": "Technician", "maintenance_supervisor": "Maintenance Supervisor",
    "maintenance_manager": "Maintenance Manager", "production_manager": "Production Manager",
    "plant_manager": "Plant Manager", "operator": "Operator", "storekeeper": "Storekeeper",
    "administrator": "System Administrator",
}
EQUIPMENT_TERMS = {
    "cnc_machine": "Máy CNC", "motor": "Động cơ điện", "conveyor": "Băng tải",
    "compressor": "Máy nén khí", "pump": "Máy bơm", "industrial_robot": "Robot công nghiệp",
    "boiler": "Nồi hơi", "injection_molding_machine": "Máy ép nhựa", "equipment": "Thiết bị",
}


class TextPreprocessor:
    """Vietnamese-friendly preprocessing without external NLP services."""

    def __init__(self, synonym_service: SynonymService) -> None:
        self.synonym_service = synonym_service

    @staticmethod
    def _unicode_normalize(text: str) -> str:
        return unicodedata.normalize("NFC", text or "")

    @staticmethod
    def _clean(text: str) -> str:
        text = strip_accents(text.lower())
        # Preserve domain values: P1, percentages, amounts and duration units.
        text = re.sub(r"[^a-z0-9_%.]+", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def _detect_durations(text: str) -> list[str]:
        pattern = r"\b\d+(?:[\.,]\d+)?\s*(?:phut|minute|minutes|gio|hour|hours|ngay|day|days|ngay lam viec|working day|business day)\b"
        return unique_preserve_order(re.findall(pattern, strip_accents(text.lower())))

    @staticmethod
    def _detect_priorities(text: str) -> list[str]:
        normalized = strip_accents(text.lower())
        found: list[str] = []
        for term in ["p1", "p2", "p3", "p4", "critical", "high", "medium", "low"]:
            if re.search(rf"\b{re.escape(term)}\b", normalized):
                found.append(term.upper() if term.startswith("p") else term.title())
        return found

    def process(
        self,
        text: str,
        phrase_normalization: bool = True,
        synonym_expansion: bool = True,
    ) -> PreprocessingResult:
        original = self._unicode_normalize(text)
        if phrase_normalization:
            phrase_text, matched_phrases = self.synonym_service.apply_phrase_normalization(original)
        else:
            phrase_text = self.synonym_service.normalize_key(original)
            matched_phrases = []
        normalized = self._clean(phrase_text)
        original_tokens = [token for token in normalized.split() if token]
        filtered_tokens = [token for token in original_tokens if token not in STOPWORDS or token in ROLE_TERMS or token in EQUIPMENT_TERMS]
        if synonym_expansion:
            expanded_tokens, matched_synonyms = self.synonym_service.expand(filtered_tokens)
        else:
            expanded_tokens, matched_synonyms = filtered_tokens, []

        counts = Counter(expanded_tokens)
        keywords = [item for item, _ in counts.most_common(30) if item not in STOPWORDS]
        roles = unique_preserve_order([label for token, label in ROLE_TERMS.items() if token in expanded_tokens])
        equipment = unique_preserve_order([label for token, label in EQUIPMENT_TERMS.items() if token in expanded_tokens])
        return PreprocessingResult(
            original_text=original,
            normalized_text=normalized,
            original_tokens=original_tokens,
            expanded_tokens=expanded_tokens,
            matched_phrases=matched_phrases,
            matched_synonyms=matched_synonyms,
            keywords=keywords,
            detected_durations=self._detect_durations(original),
            detected_priorities=self._detect_priorities(original),
            detected_roles=roles,
            detected_equipment=equipment,
        )

    def process_change_request(self, cr: dict[str, Any], **kwargs: Any) -> PreprocessingResult:
        fields = [
            cr.get("title", ""), cr.get("description", ""), cr.get("reason_for_change", ""),
            cr.get("current_behavior", ""), cr.get("expected_behavior", ""), cr.get("business_value", ""),
            cr.get("affected_process", ""), cr.get("change_type", ""), cr.get("priority", ""),
        ]
        return self.process("\n".join(item for item in fields if item), **kwargs)
