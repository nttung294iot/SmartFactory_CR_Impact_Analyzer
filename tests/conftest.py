from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.app_context import AppContext
from src.constants import SEED_DIR
from src.database import Database
from src.seed_loader import SeedLoader


@pytest.fixture()
def temp_context(tmp_path: Path) -> AppContext:
    db_path = tmp_path / "test.db"
    db = Database(db_path); db.initialize()
    db.replace_seed_table("knowledge_base", json.loads((SEED_DIR / "knowledge_base.json").read_text(encoding="utf-8")))
    db.replace_seed_table("rules", json.loads((SEED_DIR / "rules.json").read_text(encoding="utf-8")))
    db.replace_seed_table("synonyms", json.loads((SEED_DIR / "synonyms.json").read_text(encoding="utf-8")))
    settings = {"top_k":7,"minimum_bm25_score":0.0,"rule_threshold":0.25,"synonym_expansion":True,"phrase_normalization":True,"metadata_filter":True,"default_export_folder":"data/exports","application_language":"vi"}
    for k,v in settings.items(): db.upsert_setting(k,v)
    return AppContext(db_path)


@pytest.fixture()
def samples():
    return json.loads((SEED_DIR / "sample_change_requests.json").read_text(encoding="utf-8"))
