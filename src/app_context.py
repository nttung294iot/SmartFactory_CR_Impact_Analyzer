from __future__ import annotations

from typing import Any

from .bm25_retriever import BM25Retriever
from .constants import DB_PATH, SEED_DIR
from .database import Database
from .evaluation_service import EvaluationService
from .impact_analyzer import ImpactAnalyzer
from .rule_engine import RuleEngine
from .seed_loader import SeedLoader
from .synonym_service import SynonymService
from .text_preprocessor import TextPreprocessor
from .utils import load_json


class AppContext:
    """Application service container used by Streamlit pages and tests."""

    def __init__(self, db_path=DB_PATH) -> None:
        self.database = Database(db_path)
        SeedLoader(self.database).ensure_seeded()
        self.refresh()

    def refresh(self) -> None:
        self.knowledge_base = self.database.list_knowledge_base()
        self.rules = self.database.list_rules()
        self.synonyms = self.database.list_synonyms()
        self.settings = self.database.get_settings()
        self.synonym_service = SynonymService(self.synonyms)
        self.preprocessor = TextPreprocessor(self.synonym_service)
        self.retriever = BM25Retriever(self.knowledge_base)
        self.rule_engine = RuleEngine(self.rules)
        self.impact_analyzer = ImpactAnalyzer(self.rules, self.knowledge_base)

    def run_analysis(self, cr: dict[str, Any], overrides: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        settings = dict(self.settings)
        settings.update(overrides or {})
        preprocessing = self.preprocessor.process_change_request(
            cr,
            phrase_normalization=bool(settings.get("phrase_normalization", True)),
            synonym_expansion=bool(settings.get("synonym_expansion", True)),
        )
        matches = self.rule_engine.match(
            preprocessing, threshold=float(settings.get("rule_threshold", 0.30))
        )[:3]
        matched_modules = sorted({
            module_id
            for match in matches
            if not match.get("is_fallback", False)
            for module_id in match.get("module_mappings", [])
        })
        retrieved = self.retriever.retrieve(
            preprocessing,
            top_k=int(settings.get("top_k", 10)),
            minimum_score=float(settings.get("minimum_bm25_score", 0.0)),
            module_ids=matched_modules or None,
            metadata_filter=bool(settings.get("metadata_filter", True)),
        )
        result = self.impact_analyzer.analyze(cr, preprocessing, retrieved, matches)
        if persist:
            self.database.save_change_request(cr)
            self.database.save_analysis(result)
        return result

    def run_evaluation(self) -> dict[str, Any]:
        samples = load_json(SEED_DIR / "sample_change_requests.json", [])
        ground_truth = load_json(SEED_DIR / "evaluation_ground_truth.json", [])
        return EvaluationService().run(samples, ground_truth, lambda cr: self.run_analysis(cr, persist=False), k=int(self.settings.get("top_k", 10)))
