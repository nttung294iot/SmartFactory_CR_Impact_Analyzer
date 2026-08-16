from __future__ import annotations

from datetime import datetime
from typing import Any

try:
    from rank_bm25 import BM25Okapi  # type: ignore
except ImportError:  # Development fallback; production setup installs rank-bm25.
    import math
    from collections import Counter

    class BM25Okapi:  # pragma: no cover - used only when dependency is unavailable
        """Small API-compatible BM25Okapi fallback for offline verification."""
        def __init__(self, corpus, k1=1.5, b=0.75):
            self.corpus = corpus
            self.k1 = k1
            self.b = b
            self.doc_len = [len(doc) for doc in corpus]
            self.avgdl = sum(self.doc_len) / max(1, len(self.doc_len))
            self.df = Counter()
            for doc in corpus:
                for token in set(doc):
                    self.df[token] += 1
            self.n = len(corpus)

        def get_scores(self, query):
            scores = []
            for doc, length in zip(self.corpus, self.doc_len):
                tf = Counter(doc)
                score = 0.0
                for term in query:
                    freq = tf.get(term, 0)
                    if not freq:
                        continue
                    idf = math.log(1 + (self.n - self.df.get(term, 0) + 0.5) / (self.df.get(term, 0) + 0.5))
                    denom = freq + self.k1 * (1 - self.b + self.b * length / max(self.avgdl, 1e-9))
                    score += idf * (freq * (self.k1 + 1) / denom)
                scores.append(score)
            return scores

from .models import PreprocessingResult, RetrievedArtefact
from .utils import unique_preserve_order


class BM25Retriever:
    """Local BM25Okapi index over the editable Knowledge Base."""

    def __init__(self, artefacts: list[dict[str, Any]]) -> None:
        self.artefacts: list[dict[str, Any]] = []
        self.corpus_tokens: list[list[str]] = []
        self.index: BM25Okapi | None = None
        self.last_rebuild: str | None = None
        self.rebuild(artefacts)

    @staticmethod
    def _tokens(text: str) -> list[str]:
        value = str(text).lower()
        phrase_map = {
            "work order": "work_order",
            "phiếu bảo trì": "work_order",
            "lệnh bảo trì": "work_order",
            "emergency work order": "emergency_work_order",
            "preventive maintenance": "preventive_maintenance",
            "bảo trì phòng ngừa": "preventive_maintenance",
            "bảo trì định kỳ": "preventive_maintenance",
            "maintenance manager": "maintenance_manager",
            "quản lý bảo trì": "maintenance_manager",
            "condition monitoring": "condition_monitoring",
            "giám sát tình trạng": "condition_monitoring",
            "nhiệt độ": "temperature",
            "độ rung": "vibration",
            "cảnh báo": "alert",
            "kỹ thuật viên": "technician",
            "nhân viên kỹ thuật": "technician",
            "quá hạn": "overdue",
            "leo thang": "escalation",
        }
        for phrase, canonical in sorted(phrase_map.items(), key=lambda item: len(item[0]), reverse=True):
            value = value.replace(phrase, canonical)
        value = value.replace("/", " ").replace("-", "_")
        return [token for token in value.split() if token]

    def _searchable_tokens(self, item: dict[str, Any]) -> list[str]:
        title = self._tokens(item.get("title", ""))
        keywords = self._tokens(" ".join(item.get("keywords", [])))
        tags = self._tokens(" ".join(item.get("tags", [])))
        description = self._tokens(item.get("description", ""))
        modules = self._tokens(" ".join(item.get("module_ids", [])))
        roles = self._tokens(" ".join(item.get("role_ids", [])))
        # Weight title/keywords/tags by controlled repetition.
        return title * 4 + keywords * 3 + tags * 2 + description + modules * 2 + roles

    def rebuild(self, artefacts: list[dict[str, Any]]) -> None:
        self.artefacts = [item for item in artefacts if item.get("status", "active") == "active"]
        self.corpus_tokens = [self._searchable_tokens(item) for item in self.artefacts]
        self.index = BM25Okapi(self.corpus_tokens or [["empty"]])
        self.last_rebuild = datetime.now().isoformat(timespec="seconds")

    def retrieve(
        self,
        preprocessing: PreprocessingResult | dict[str, Any],
        top_k: int = 10,
        minimum_score: float = 0.0,
        artefact_types: list[str] | None = None,
        module_ids: list[str] | None = None,
        metadata_filter: bool = True,
    ) -> list[dict[str, Any]]:
        if self.index is None:
            return []
        data = preprocessing.model_dump() if hasattr(preprocessing, "model_dump") else preprocessing
        query_tokens = data.get("expanded_tokens") or data.get("original_tokens") or []
        scores = self.index.get_scores(query_tokens)
        query_set = set(query_tokens)
        candidates: list[tuple[float, int]] = []
        for index, score in enumerate(scores):
            item = self.artefacts[index]
            if metadata_filter:
                if artefact_types and item.get("type") not in artefact_types:
                    continue
                if module_ids and not set(module_ids).intersection(item.get("module_ids", [])):
                    continue
            adjusted = float(score) * {
                "business_rule": 1.18,
                "test_case": 1.12,
                "user_story": 1.08,
                "sop": 1.02,
                "role": 0.88,
                "module": 0.72,
            }.get(item.get("type", ""), 1.0)
            if adjusted <= max(0.0, float(minimum_score)):
                continue
            candidates.append((adjusted, index))
        candidates.sort(key=lambda pair: pair[0], reverse=True)
        # Keep the result concise and diverse for a BA review screen.
        selected_candidates: list[tuple[float, int]] = []
        type_counts: dict[str, int] = {}
        quotas = {"module": 1, "role": 1, "user_story": 2, "business_rule": 3, "sop": 1, "test_case": 3}
        for score, index in candidates:
            artefact_type = self.artefacts[index].get("type", "")
            if type_counts.get(artefact_type, 0) >= quotas.get(artefact_type, 2):
                continue
            selected_candidates.append((score, index))
            type_counts[artefact_type] = type_counts.get(artefact_type, 0) + 1
            if len(selected_candidates) >= max(1, top_k):
                break
        result: list[dict[str, Any]] = []
        for rank, (score, index) in enumerate(selected_candidates, start=1):
            item = self.artefacts[index]
            searchable = set(self.corpus_tokens[index])
            matched = sorted(query_set.intersection(searchable))[:15]
            reason_parts = []
            if matched:
                reason_parts.append("Khớp từ khóa: " + ", ".join(matched))
            if item.get("module_ids"):
                reason_parts.append("Module: " + ", ".join(item["module_ids"]))
            result.append(RetrievedArtefact(
                rank=rank, document_id=item["id"], artefact_type=item["type"], title=item["title"],
                bm25_score=round(score, 4), matched_keywords=matched, module_ids=item.get("module_ids", []),
                preview=item.get("description", "")[:260], related_artifact_ids=item.get("related_artifact_ids", []),
                retrieval_reason="; ".join(reason_parts) or "Khớp tổng thể theo BM25", selected=True,
            ).model_dump())
        return result
