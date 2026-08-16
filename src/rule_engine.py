from __future__ import annotations

from typing import Any

from .models import PreprocessingResult, RuleMatch


class RuleEngine:
    """Config-driven coverage scoring for offline Change Request classification."""

    def __init__(self, rules: list[dict[str, Any]]) -> None:
        self.rules = rules

    @staticmethod
    def _token_set(preprocessing: PreprocessingResult | dict[str, Any]) -> set[str]:
        data = preprocessing.model_dump() if hasattr(preprocessing, "model_dump") else preprocessing
        return set(data.get("expanded_tokens", [])) | set(data.get("keywords", []))

    def match(self, preprocessing: PreprocessingResult | dict[str, Any], threshold: float = 0.35) -> list[dict[str, Any]]:
        tokens = self._token_set(preprocessing)
        matches: list[dict[str, Any]] = []
        fallback_rule: dict[str, Any] | None = None
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            if rule.get("category") == "Generic Fallback":
                fallback_rule = rule
                continue
            required = set(rule.get("required_keywords", []))
            optional = set(rule.get("optional_keywords", []))
            excluded = set(rule.get("excluded_keywords", []))
            missing = sorted(required - tokens)
            if missing or excluded.intersection(tokens):
                continue
            required_hits = len(required.intersection(tokens))
            optional_hits = len(optional.intersection(tokens))
            denominator = max(1, len(required) * 2 + len(optional))
            raw = (required_hits * 2 + optional_hits) / denominator
            score = min(1.0, raw * float(rule.get("priority_weight", 1.0)))
            if score < threshold:
                continue
            matched = sorted((required | optional).intersection(tokens))
            matches.append(RuleMatch(
                rule_id=rule["id"], rule_name=rule["name"], category=rule["category"],
                match_score=round(score, 4), matched_keywords=matched,
                missing_required_keywords=[], module_mappings=rule.get("module_mappings", []),
                enabled=True, is_fallback=False,
            ).model_dump())
        matches.sort(key=lambda item: item["match_score"], reverse=True)
        if matches:
            return matches
        fallback = fallback_rule or {
            "id": "RULE-GEN-001", "name": "Generic Fallback", "category": "Generic Fallback",
            "module_mappings": ["MOD-CR"], "enabled": True,
        }
        return [RuleMatch(
            rule_id=fallback["id"], rule_name=fallback["name"], category=fallback["category"],
            match_score=0.0, matched_keywords=[], missing_required_keywords=[],
            module_mappings=fallback.get("module_mappings", ["MOD-CR"]), enabled=True, is_fallback=True,
        ).model_dump()]

    def test_rule(self, rule: dict[str, Any], preprocessing: PreprocessingResult | dict[str, Any]) -> dict[str, Any]:
        original_rules = self.rules
        try:
            self.rules = [rule]
            matches = self.match(preprocessing, threshold=0.0)
            return matches[0] if matches else {"rule_id": rule["id"], "match_score": 0.0, "matched_keywords": []}
        finally:
            self.rules = original_rules
