from __future__ import annotations

from statistics import mean
from typing import Any, Callable


class EvaluationService:
    """Compute retrieval and rule metrics from the real offline pipeline."""

    @staticmethod
    def _precision_at_k(retrieved: list[str], expected: set[str], k: int) -> float:
        top = retrieved[:k]
        return len(set(top).intersection(expected)) / max(1, len(top))

    @staticmethod
    def _recall_at_k(retrieved: list[str], expected: set[str], k: int) -> float:
        return len(set(retrieved[:k]).intersection(expected)) / max(1, len(expected))

    @staticmethod
    def _reciprocal_rank(retrieved: list[str], expected: set[str]) -> float:
        for index, item in enumerate(retrieved, start=1):
            if item in expected:
                return 1 / index
        return 0.0

    def run(
        self,
        samples: list[dict[str, Any]],
        ground_truth: list[dict[str, Any]],
        analyzer: Callable[[dict[str, Any]], dict[str, Any]],
        k: int = 10,
    ) -> dict[str, Any]:
        gt_map = {item["cr_id"]: item for item in ground_truth}
        rows: list[dict[str, Any]] = []
        for sample in samples:
            result = analyzer(sample)
            gt = gt_map[sample["id"]]
            retrieved_ids = [item["document_id"] for item in result.get("retrieved_artefacts", [])]
            expected_artifacts = set(gt["expected_artifacts"])
            actual_modules = {item["module_id"] for item in result.get("impacted_modules", [])}
            expected_modules = set(gt["expected_modules"])
            actual_categories = {item["category"] for item in result.get("rule_matches", [])}
            expected_categories = set(gt["expected_rule_categories"])
            fallback = any(item.get("is_fallback") for item in result.get("rule_matches", []))
            rows.append({
                "cr_id": sample["id"],
                "precision_at_k": self._precision_at_k(retrieved_ids, expected_artifacts, k),
                "recall_at_k": self._recall_at_k(retrieved_ids, expected_artifacts, k),
                "reciprocal_rank": self._reciprocal_rank(retrieved_ids, expected_artifacts),
                "top_k_hit": float(bool(set(retrieved_ids[:k]).intersection(expected_artifacts))),
                "rule_coverage": len(actual_categories.intersection(expected_categories)) / max(1, len(expected_categories)),
                "fallback": float(fallback),
                "processing_time_ms": result.get("processing_time_ms", 0),
                "impact_module_accuracy": len(actual_modules.intersection(expected_modules)) / max(1, len(expected_modules)),
                "artefact_retrieval_accuracy": len(set(retrieved_ids).intersection(expected_artifacts)) / max(1, len(expected_artifacts)),
            })
        summary = {
            "precision_at_k": mean(row["precision_at_k"] for row in rows),
            "recall_at_k": mean(row["recall_at_k"] for row in rows),
            "mrr": mean(row["reciprocal_rank"] for row in rows),
            "top_k_hit_rate": mean(row["top_k_hit"] for row in rows),
            "rule_coverage": mean(row["rule_coverage"] for row in rows),
            "fallback_rate": mean(row["fallback"] for row in rows),
            "average_processing_time_ms": mean(row["processing_time_ms"] for row in rows),
            "impact_module_accuracy": mean(row["impact_module_accuracy"] for row in rows),
            "artefact_retrieval_accuracy": mean(row["artefact_retrieval_accuracy"] for row in rows),
            "sample_count": len(rows),
            "top_k": k,
        }
        return {"summary": summary, "details": rows}
