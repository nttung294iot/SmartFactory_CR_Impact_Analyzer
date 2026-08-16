from __future__ import annotations

from typing import Any


class TraceabilityService:
    """Create a concise Requirement Traceability Matrix."""

    @staticmethod
    def build(cr_id: str, rule_matches: list[dict[str, Any]], impacted_modules: list[dict[str, Any]], artefacts: list[dict[str, Any]], draft_tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        rules = [item for item in rule_matches if not item.get("is_fallback")] or rule_matches
        module_lookup = {item["module_id"]: item for item in impacted_modules}
        selected = [item for item in artefacts if item.get("selected", True)]
        for idx, match in enumerate(rules[:3], start=1):
            mapped = match.get("module_mappings") or ["BA-CONFIRM"]
            related = [item for item in selected if set(item.get("module_ids", [])).intersection(mapped)] or selected[:1]
            if not related:
                related = [{"document_id": "BA-CONFIRM", "artefact_type": "need_review", "module_ids": mapped}]
            for artifact in related[:3]:
                module_id = next((m for m in mapped if m in artifact.get("module_ids", [])), mapped[0])
                module = module_lookup.get(module_id, {})
                test_id = draft_tests[min(idx - 1, len(draft_tests) - 1)].get("test_id", "") if draft_tests else ""
                rows.append({
                    "cr_id": cr_id,
                    "rule_id": match["rule_id"],
                    "module_id": module_id,
                    "artefact_type": artifact.get("artefact_type", ""),
                    "artefact_id": artifact.get("document_id", ""),
                    "test_case_id": test_id,
                    "impact_level": module.get("impact_level", "Need Review"),
                    "review_status": "Draft",
                    "ba_note": "",
                })
        return rows[:10]
