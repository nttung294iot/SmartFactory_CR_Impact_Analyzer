from __future__ import annotations

from pathlib import Path
from typing import Any

from .constants import CONFIG_DIR, SEED_DIR
from .database import Database
from .utils import load_json


class SeedLoader:
    """Load simulated JSON seed data into SQLite."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def load_all(self, include_samples: bool = True) -> None:
        self.database.initialize()
        self.database.replace_seed_table("knowledge_base", load_json(SEED_DIR / "knowledge_base.json", []))
        self.database.replace_seed_table("rules", load_json(SEED_DIR / "rules.json", []))
        self.database.replace_seed_table("synonyms", load_json(SEED_DIR / "synonyms.json", []))
        settings = load_json(CONFIG_DIR / "settings.json", {})
        for key, value in settings.items():
            self.database.upsert_setting(key, value)
        if include_samples:
            for item in load_json(SEED_DIR / "sample_change_requests.json", []):
                self.database.save_change_request(item)

    def ensure_seeded(self) -> None:
        self.database.initialize()
        if not self.database.list_knowledge_base() or not self.database.list_rules() or not self.database.list_synonyms():
            self.load_all(include_samples=True)


def reset_demo_database(database: Database) -> Path | None:
    backup = database.backup()
    database.reset()
    SeedLoader(database).load_all(include_samples=True)
    return backup
