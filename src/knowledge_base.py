from __future__ import annotations

from typing import Any

from .database import Database


class KnowledgeBaseService:
    """CRUD facade for simulated project artefacts."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def list_all(self) -> list[dict[str, Any]]:
        return self.database.list_knowledge_base()

    def get(self, artefact_id: str) -> dict[str, Any] | None:
        return next((item for item in self.list_all() if item["id"] == artefact_id), None)

    def search(self, query: str = "", artefact_type: str = "", module_id: str = "", status: str = "") -> list[dict[str, Any]]:
        query_lower = query.lower().strip()
        result = []
        for item in self.list_all():
            haystack = " ".join([item.get("id", ""), item.get("title", ""), item.get("description", ""), " ".join(item.get("tags", [])), " ".join(item.get("keywords", []))]).lower()
            if query_lower and query_lower not in haystack:
                continue
            if artefact_type and item.get("type") != artefact_type:
                continue
            if module_id and module_id not in item.get("module_ids", []):
                continue
            if status and item.get("status") != status:
                continue
            result.append(item)
        return result

    def upsert(self, item: dict[str, Any]) -> None:
        self.database.upsert_knowledge_base(item)

    def delete(self, artefact_id: str) -> None:
        self.database.delete_knowledge_base(artefact_id)
