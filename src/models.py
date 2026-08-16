from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ChangeRequest(BaseModel):
    id: str = ""
    title: str
    requester: str
    request_date: str = Field(default_factory=lambda: date.today().isoformat())
    department: str = ""
    priority: str
    change_type: str = "Other"
    initial_category: str = "Other"
    description: str
    reason_for_change: str
    current_behavior: str = ""
    expected_behavior: str
    business_value: str = ""
    affected_process: str = ""
    initial_module: str = ""
    expected_deadline: str = ""
    attachment_note: str = ""
    status: str = "Draft"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @field_validator("title", "requester", "priority", "description", "reason_for_change", "expected_behavior")
    @classmethod
    def required_text(cls, value: str) -> str:
        if not str(value).strip():
            raise ValueError("Trường bắt buộc không được để trống.")
        return str(value).strip()


class Artefact(BaseModel):
    id: str
    type: str
    title: str
    description: str
    module_ids: list[str] = []
    role_ids: list[str] = []
    keywords: list[str] = []
    tags: list[str] = []
    related_artifact_ids: list[str] = []
    status: str = "active"
    version: str = "1.0"
    source: str = "simulated"
    language: str = "vi"
    notes: str = ""


class RuleDefinition(BaseModel):
    id: str
    name: str
    category: str
    keywords: list[str] = []
    required_keywords: list[str] = []
    optional_keywords: list[str] = []
    excluded_keywords: list[str] = []
    priority_weight: float = 1.0
    module_mappings: list[str] = []
    artefact_type_mappings: list[str] = []
    risk_templates: list[str] = []
    clarifying_question_templates: list[str] = []
    user_story_template: dict[str, Any] = {}
    business_rule_template: str = ""
    test_scenario_template: dict[str, Any] = {}
    recommended_actions: list[str] = []
    enabled: bool = True


class PreprocessingResult(BaseModel):
    original_text: str
    normalized_text: str
    original_tokens: list[str]
    expanded_tokens: list[str]
    matched_phrases: list[dict[str, str]]
    matched_synonyms: list[dict[str, str]]
    keywords: list[str]
    detected_durations: list[str]
    detected_priorities: list[str]
    detected_roles: list[str]
    detected_equipment: list[str]


class RetrievedArtefact(BaseModel):
    rank: int
    document_id: str
    artefact_type: str
    title: str
    bm25_score: float
    matched_keywords: list[str]
    module_ids: list[str]
    preview: str
    related_artifact_ids: list[str]
    retrieval_reason: str
    selected: bool = True
    ba_note: str = ""


class RuleMatch(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    match_score: float
    matched_keywords: list[str]
    missing_required_keywords: list[str]
    module_mappings: list[str]
    enabled: bool
    is_fallback: bool = False


class AnalysisResult(BaseModel):
    analysis_id: str
    cr_id: str
    summary: str
    preprocessing: dict[str, Any]
    retrieved_artefacts: list[dict[str, Any]]
    rule_matches: list[dict[str, Any]]
    impacted_modules: list[dict[str, Any]]
    artefacts_to_review: list[dict[str, Any]]
    draft_user_stories: list[dict[str, Any]]
    draft_business_rules: list[dict[str, Any]]
    draft_test_scenarios: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    clarifying_questions: list[dict[str, Any]]
    assumptions: list[str]
    dependencies: list[str]
    recommended_actions: list[str]
    traceability_matrix: list[dict[str, Any]]
    processing_time_ms: float
    analysis_status: str = "Analyzed"
    ba_review_status: str = "Draft"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
