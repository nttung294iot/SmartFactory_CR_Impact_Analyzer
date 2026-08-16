from __future__ import annotations

import json
import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator

from .constants import DB_PATH


SCHEMA = """
CREATE TABLE IF NOT EXISTS change_requests (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    requester TEXT NOT NULL,
    request_date TEXT,
    department TEXT,
    priority TEXT NOT NULL,
    change_type TEXT,
    initial_category TEXT,
    description TEXT NOT NULL,
    reason_for_change TEXT NOT NULL,
    current_behavior TEXT,
    expected_behavior TEXT NOT NULL,
    business_value TEXT,
    affected_process TEXT,
    initial_module TEXT,
    expected_deadline TEXT,
    attachment_note TEXT,
    status TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS analyses (
    analysis_id TEXT PRIMARY KEY,
    cr_id TEXT NOT NULL,
    result_json TEXT NOT NULL,
    processing_time_ms REAL NOT NULL,
    matched_rule_count INTEGER DEFAULT 0,
    impacted_module_count INTEGER DEFAULT 0,
    analysis_status TEXT,
    ba_review_status TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (cr_id) REFERENCES change_requests(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS ba_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id TEXT NOT NULL,
    reviewer_name TEXT,
    review_date TEXT,
    review_status TEXT,
    review_comment TEXT,
    review_payload_json TEXT,
    created_at TEXT,
    FOREIGN KEY (analysis_id) REFERENCES analyses(analysis_id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS application_settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS knowledge_base (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    payload_json TEXT NOT NULL,
    updated_at TEXT
);
CREATE TABLE IF NOT EXISTS synonyms (
    id TEXT PRIMARY KEY,
    canonical_term TEXT NOT NULL,
    category TEXT,
    enabled INTEGER NOT NULL DEFAULT 1,
    payload_json TEXT NOT NULL,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_analysis_cr ON analyses(cr_id);
CREATE INDEX IF NOT EXISTS idx_cr_status ON change_requests(status);
CREATE INDEX IF NOT EXISTS idx_kb_type ON knowledge_base(type);
"""


class Database:
    """SQLite persistence for Change Requests, analyses, reviews and configuration data."""

    def __init__(self, db_path: Path | str = DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)

    def backup(self) -> Path | None:
        if not self.db_path.exists():
            return None
        target = self.db_path.with_name(f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        shutil.copy2(self.db_path, target)
        return target

    def reset(self) -> None:
        if self.db_path.exists():
            self.db_path.unlink()
        self.initialize()

    def next_cr_id(self) -> str:
        with self.connect() as conn:
            rows = conn.execute("SELECT id FROM change_requests WHERE id LIKE 'CR-%'").fetchall()
        values = []
        for row in rows:
            try:
                values.append(int(str(row["id"]).split("-")[-1]))
            except ValueError:
                pass
        return f"CR-{max(values, default=0) + 1:03d}"

    def save_change_request(self, data: dict[str, Any]) -> None:
        columns = [
            "id", "title", "requester", "request_date", "department", "priority", "change_type",
            "initial_category", "description", "reason_for_change", "current_behavior", "expected_behavior",
            "business_value", "affected_process", "initial_module", "expected_deadline", "attachment_note",
            "status", "created_at", "updated_at",
        ]
        row = {key: data.get(key, "") for key in columns}
        now = datetime.now().isoformat(timespec="seconds")
        row["created_at"] = row.get("created_at") or now
        row["updated_at"] = now
        placeholders = ",".join(f":{item}" for item in columns)
        updates = ",".join(f"{item}=excluded.{item}" for item in columns if item not in {"id", "created_at"})
        query = f"INSERT INTO change_requests ({','.join(columns)}) VALUES ({placeholders}) ON CONFLICT(id) DO UPDATE SET {updates}"
        with self.connect() as conn:
            conn.execute(query, row)

    def get_change_request(self, cr_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM change_requests WHERE id=?", (cr_id,)).fetchone()
        return dict(row) if row else None

    def list_change_requests(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM change_requests ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]

    def delete_change_request(self, cr_id: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM change_requests WHERE id=?", (cr_id,))

    def save_analysis(self, result: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        payload = {
            "analysis_id": result["analysis_id"], "cr_id": result["cr_id"],
            "result_json": json.dumps(result, ensure_ascii=False),
            "processing_time_ms": float(result.get("processing_time_ms", 0)),
            "matched_rule_count": len(result.get("rule_matches", [])),
            "impacted_module_count": len(result.get("impacted_modules", [])),
            "analysis_status": result.get("analysis_status", "Analyzed"),
            "ba_review_status": result.get("ba_review_status", "Draft"),
            "created_at": result.get("created_at", now), "updated_at": now,
        }
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO analyses VALUES (:analysis_id,:cr_id,:result_json,:processing_time_ms,:matched_rule_count,
                :impacted_module_count,:analysis_status,:ba_review_status,:created_at,:updated_at)
                ON CONFLICT(analysis_id) DO UPDATE SET result_json=excluded.result_json,
                processing_time_ms=excluded.processing_time_ms, matched_rule_count=excluded.matched_rule_count,
                impacted_module_count=excluded.impacted_module_count, analysis_status=excluded.analysis_status,
                ba_review_status=excluded.ba_review_status, updated_at=excluded.updated_at""", payload,
            )

    def get_analysis(self, analysis_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT result_json FROM analyses WHERE analysis_id=?", (analysis_id,)).fetchone()
        return json.loads(row["result_json"]) if row else None

    def latest_analysis_for_cr(self, cr_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT result_json FROM analyses WHERE cr_id=? ORDER BY created_at DESC LIMIT 1", (cr_id,)).fetchone()
        return json.loads(row["result_json"]) if row else None

    def list_analyses(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(
                """SELECT a.analysis_id,a.cr_id,c.title,c.priority,c.initial_category,a.analysis_status,
                a.ba_review_status,a.processing_time_ms,a.matched_rule_count,a.impacted_module_count,a.created_at
                FROM analyses a JOIN change_requests c ON c.id=a.cr_id ORDER BY a.created_at DESC"""
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_analysis(self, analysis_id: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM analyses WHERE analysis_id=?", (analysis_id,))

    def save_review(self, analysis_id: str, reviewer: str, status: str, comment: str, payload: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO ba_reviews (analysis_id,reviewer_name,review_date,review_status,review_comment,review_payload_json,created_at) VALUES (?,?,?,?,?,?,?)",
                (analysis_id, reviewer, now[:10], status, comment, json.dumps(payload, ensure_ascii=False), now),
            )
            conn.execute("UPDATE analyses SET ba_review_status=?, updated_at=? WHERE analysis_id=?", (status, now, analysis_id))

    def list_reviews(self, analysis_id: str) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM ba_reviews WHERE analysis_id=? ORDER BY created_at DESC", (analysis_id,)).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["review_payload"] = json.loads(item.pop("review_payload_json") or "{}")
            result.append(item)
        return result

    def upsert_setting(self, key: str, value: Any) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO application_settings (key,value_json,updated_at) VALUES (?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_at=excluded.updated_at",
                (key, json.dumps(value, ensure_ascii=False), now),
            )

    def get_settings(self) -> dict[str, Any]:
        with self.connect() as conn:
            rows = conn.execute("SELECT key,value_json FROM application_settings").fetchall()
        return {row["key"]: json.loads(row["value_json"]) for row in rows}

    def replace_seed_table(self, table: str, items: list[dict[str, Any]]) -> None:
        if table not in {"knowledge_base", "rules", "synonyms"}:
            raise ValueError("Unsupported seed table")
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(f"DELETE FROM {table}")
            if table == "knowledge_base":
                conn.executemany(
                    "INSERT INTO knowledge_base (id,type,title,description,payload_json,status,updated_at) VALUES (?,?,?,?,?,?,?)",
                    [(x["id"], x["type"], x["title"], x["description"], json.dumps(x, ensure_ascii=False), x.get("status", "active"), now) for x in items],
                )
            elif table == "rules":
                conn.executemany(
                    "INSERT INTO rules (id,name,category,enabled,payload_json,updated_at) VALUES (?,?,?,?,?,?)",
                    [(x["id"], x["name"], x["category"], int(x.get("enabled", True)), json.dumps(x, ensure_ascii=False), now) for x in items],
                )
            else:
                conn.executemany(
                    "INSERT INTO synonyms (id,canonical_term,category,enabled,payload_json,updated_at) VALUES (?,?,?,?,?,?)",
                    [(x["id"], x["canonical_term"], x.get("category", ""), int(x.get("enabled", True)), json.dumps(x, ensure_ascii=False), now) for x in items],
                )

    def upsert_knowledge_base(self, item: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO knowledge_base (id,type,title,description,payload_json,status,updated_at) VALUES (?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET type=excluded.type,title=excluded.title,description=excluded.description,payload_json=excluded.payload_json,status=excluded.status,updated_at=excluded.updated_at""",
                (item["id"], item["type"], item["title"], item["description"], json.dumps(item, ensure_ascii=False), item.get("status", "active"), now),
            )

    def delete_knowledge_base(self, item_id: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM knowledge_base WHERE id=?", (item_id,))

    def list_knowledge_base(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload_json FROM knowledge_base ORDER BY type,id").fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def upsert_rule(self, item: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO rules (id,name,category,enabled,payload_json,updated_at) VALUES (?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET name=excluded.name,category=excluded.category,enabled=excluded.enabled,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (item["id"], item["name"], item["category"], int(item.get("enabled", True)), json.dumps(item, ensure_ascii=False), now),
            )

    def delete_rule(self, rule_id: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM rules WHERE id=?", (rule_id,))

    def list_rules(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload_json FROM rules ORDER BY category,id").fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def upsert_synonym(self, item: dict[str, Any]) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self.connect() as conn:
            conn.execute(
                """INSERT INTO synonyms (id,canonical_term,category,enabled,payload_json,updated_at) VALUES (?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET canonical_term=excluded.canonical_term,category=excluded.category,enabled=excluded.enabled,payload_json=excluded.payload_json,updated_at=excluded.updated_at""",
                (item["id"], item["canonical_term"], item.get("category", ""), int(item.get("enabled", True)), json.dumps(item, ensure_ascii=False), now),
            )

    def delete_synonym(self, synonym_id: str) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM synonyms WHERE id=?", (synonym_id,))

    def list_synonyms(self) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute("SELECT payload_json FROM synonyms ORDER BY canonical_term").fetchall()
        return [json.loads(row["payload_json"]) for row in rows]
