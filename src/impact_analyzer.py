from __future__ import annotations

import re
import time
from collections import defaultdict
from datetime import datetime
from typing import Any

from .models import AnalysisResult, PreprocessingResult
from .traceability_service import TraceabilityService
from .utils import unique_preserve_order


class ImpactAnalyzer:
    """Create concise, editable BA deliverables from retrieved evidence and matched rules."""

    def __init__(self, rules: list[dict[str, Any]], knowledge_base: list[dict[str, Any]]) -> None:
        self.rule_by_id = {item["id"]: item for item in rules}
        self.kb_by_id = {item["id"]: item for item in knowledge_base}
        self.module_names = {item["id"]: item["title"] for item in knowledge_base if item["type"] == "module"}

    @staticmethod
    def _impact_level(score: float, priority: str, fallback: bool) -> str:
        if fallback:
            return "Need Review"
        if priority == "Critical" and score >= 0.55:
            return "Critical"
        if score >= 0.62 or priority == "High":
            return "High"
        if score >= 0.35:
            return "Medium"
        return "Low"

    @staticmethod
    def _condition(cr: dict[str, Any]) -> str:
        text = re.sub(r"\s+", " ", cr.get("description", "")).strip()
        return text[:300] if text else "điều kiện đã được stakeholder xác nhận"

    def analyze(
        self,
        cr: dict[str, Any],
        preprocessing: PreprocessingResult,
        retrieved: list[dict[str, Any]],
        rule_matches: list[dict[str, Any]],
        started_at: float | None = None,
    ) -> dict[str, Any]:
        started = started_at or time.perf_counter()
        rule_matches = rule_matches[:3]
        fallback = bool(rule_matches) and all(item.get("is_fallback", False) for item in rule_matches)

        module_scores: dict[str, float] = defaultdict(float)
        module_evidence: dict[str, list[str]] = defaultdict(list)
        module_rules: dict[str, list[str]] = defaultdict(list)

        for match in rule_matches:
            for module_id in match.get("module_mappings", []):
                module_scores[module_id] = max(module_scores[module_id], float(match.get("match_score", 0)))
                module_evidence[module_id].append(match["rule_id"])
                module_rules[module_id].append(match["rule_id"])
        for item in retrieved:
            if not item.get("selected", True):
                continue
            for module_id in item.get("module_ids", []):
                if not fallback and module_id not in module_scores:
                    continue
                score = min(1.0, float(item.get("bm25_score", 0)) / 10.0)
                module_scores[module_id] = max(module_scores[module_id], score)
                module_evidence[module_id].append(item["document_id"])

        impacted_modules: list[dict[str, Any]] = []
        module_limit = 3 if fallback else 5
        for module_id, score in sorted(module_scores.items(), key=lambda pair: pair[1], reverse=True)[:module_limit]:
            if module_id not in self.module_names:
                continue
            impacted_modules.append({
                "module_id": module_id,
                "module_name": self.module_names[module_id],
                "impact_level": self._impact_level(score, cr.get("priority", "Medium"), fallback),
                "impact_reason": "Tài liệu có nội dung liên quan; BA cần xác nhận phạm vi thực tế." if fallback else "Được xác định từ quy tắc phù hợp và tài liệu liên quan đến Change Request.",
                "evidence": unique_preserve_order(module_evidence[module_id])[:5],
                "related_rule": unique_preserve_order(module_rules[module_id])[:3],
                "ba_decision": "Need Review",
                "ba_note": "",
            })
        if not impacted_modules:
            impacted_modules.append({
                "module_id": "BA-CONFIRM",
                "module_name": "BA cần xác nhận",
                "impact_level": "Need Review",
                "impact_reason": "Thông tin hiện tại chưa đủ để xác định module cụ thể.",
                "evidence": ["Generic Fallback"],
                "related_rule": ["RULE-GEN-001"],
                "ba_decision": "Need Review",
                "ba_note": "",
            })

        allowed_types = {"user_story", "business_rule", "sop", "test_case", "role"}
        mapped_types: set[str] = set()
        for match in rule_matches:
            mapped_types.update(self.rule_by_id.get(match["rule_id"], {}).get("artefact_type_mappings", []))
        artefacts_to_review: list[dict[str, Any]] = []
        for item in retrieved:
            if not item.get("selected", True) or item.get("artefact_type") not in allowed_types:
                continue
            if mapped_types and item["artefact_type"] not in mapped_types and not fallback:
                continue
            artefacts_to_review.append({
                **item,
                "review_group": item["artefact_type"],
                "review_action": "Review" if fallback else "Update",
                "ba_note": item.get("ba_note", ""),
            })
            if len(artefacts_to_review) >= (6 if fallback else 12):
                break

        condition = self._condition(cr)
        detected_role = preprocessing.detected_roles[0] if preprocessing.detected_roles else "[BA xác nhận role]"
        draft_user_stories: list[dict[str, Any]] = []
        draft_business_rules: list[dict[str, Any]] = []
        draft_test_scenarios: list[dict[str, Any]] = []
        risks: list[dict[str, Any]] = []
        questions: list[dict[str, Any]] = []
        recommended_actions: list[str] = []

        for idx, match in enumerate(rule_matches[:2], start=1):
            rule = self.rule_by_id.get(match["rule_id"], {})
            is_fallback = match.get("is_fallback", False)
            story_template = rule.get("user_story_template", {})
            role = detected_role if detected_role != "[BA xác nhận role]" else story_template.get("role", "[BA xác nhận role]")
            capability = story_template.get("capability", "làm rõ nhu cầu và phạm vi thay đổi")
            value = story_template.get("business_value", cr.get("business_value") or "đạt mục tiêu nghiệp vụ")
            draft_user_stories.append({
                "story_id": f"DRAFT-US-{idx:03d}",
                "source_rule": match["rule_id"],
                "user_story": f"As a {role},\nI want {capability},\nso that {value}.",
                "acceptance_criteria": [
                    "Given dữ liệu và cấu hình liên quan đã tồn tại, When điều kiện trong Change Request được thỏa mãn, Then hệ thống thực hiện hành vi đã được BA xác nhận.",
                    "Given điều kiện không được thỏa mãn, When hệ thống xử lý, Then không thực hiện hành vi ngoài phạm vi yêu cầu.",
                ] if not is_fallback else [
                    "Given stakeholder đã xác nhận actor, trigger và expected behavior, When BA cập nhật requirement, Then User Story có tiêu chí chấp nhận rõ ràng.",
                    "Given thông tin còn thiếu, When kết quả được review, Then trạng thái giữ là Need Clarification.",
                ],
                "ba_note": "",
            })
            behavior = rule.get("business_rule_template", "BA cần xác nhận điều kiện và hành vi.")
            draft_business_rules.append({
                "rule_id": f"DRAFT-BR-{idx:03d}",
                "source_rule": match["rule_id"],
                "business_rule": f"DRAFT-BR-{idx:03d}: {condition if not is_fallback else 'Sau khi stakeholder xác nhận điều kiện'} → {behavior}",
                "ba_note": "",
            })
            test_template = rule.get("test_scenario_template", {})
            draft_test_scenarios.append({
                "test_id": f"DRAFT-TS-{idx:03d}",
                "source_rule": match["rule_id"],
                "preconditions": test_template.get("preconditions", "Dữ liệu và cấu hình liên quan tồn tại"),
                "test_steps": test_template.get("test_steps", "Thực hiện yêu cầu sau khi được làm rõ"),
                "expected_result": test_template.get("expected_result", behavior),
                "priority": test_template.get("priority", "Medium"),
                "related_cr": cr["id"],
                "related_module": match.get("module_mappings", []),
                "ba_note": "",
            })
            for risk in rule.get("risk_templates", []):
                if len(risks) >= 3:
                    break
                risks.append({
                    "risk_id": f"RISK-{len(risks)+1:02d}",
                    "risk_description": risk,
                    "risk_level": "High" if cr.get("priority") in {"High", "Critical"} and not is_fallback else "Medium",
                    "source_rule": match["rule_id"],
                    "mitigation_suggestion": "BA xác nhận điều kiện, role, ngoại lệ và tiêu chí kiểm thử trước khi triển khai.",
                    "ba_status": "Open",
                })
            for question in rule.get("clarifying_question_templates", []):
                if len(questions) >= 5:
                    break
                questions.append({
                    "question_id": f"Q-{len(questions)+1:02d}",
                    "question": question,
                    "reason": "Làm rõ phạm vi và giảm rủi ro hiểu sai yêu cầu.",
                    "answer": "",
                    "status": "Open",
                    "source_rule": match["rule_id"],
                })
            recommended_actions.extend(rule.get("recommended_actions", []))

        if fallback and not questions:
            questions = [{
                "question_id": "Q-01",
                "question": "Ai là người sử dụng chính, tiêu chí đánh giá là gì và kết quả được sử dụng trong quy trình nào?",
                "reason": "Yêu cầu chưa đủ thông tin để xác định tác động cụ thể.",
                "answer": "",
                "status": "Open",
                "source_rule": "RULE-GEN-001",
            }]

        assumptions = [
            "Dữ liệu và quy trình trong prototype là dữ liệu mô phỏng.",
            "Các module và artefact được đề xuất cần Business Analyst xác nhận trước khi cập nhật backlog.",
        ]
        dependencies = [
            "Stakeholder cung cấp câu trả lời cho các câu hỏi cần làm rõ.",
            "Tài liệu nghiệp vụ liên quan còn hiệu lực và có ID nhất quán.",
        ]
        rtm = TraceabilityService.build(cr["id"], rule_matches, impacted_modules, artefacts_to_review, draft_test_scenarios)
        processing_ms = round((time.perf_counter() - started) * 1000, 2)
        if fallback:
            summary = "Yêu cầu chưa khớp rõ với các kịch bản nghiệp vụ hiện có. Hệ thống đã gợi ý tài liệu gần nhất và tạo câu hỏi để BA tiếp tục làm rõ trước khi xác định phạm vi tác động."
        else:
            names = ", ".join(item["module_name"] for item in impacted_modules[:3])
            summary = f"Kết quả ban đầu xác định {len(impacted_modules)} module cần xem xét, nổi bật gồm {names}. BA cần rà soát tài liệu, câu hỏi và bản nháp yêu cầu trước khi xác nhận."

        return AnalysisResult(
            analysis_id=f"AN-{cr['id']}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            cr_id=cr["id"],
            summary=summary,
            preprocessing=preprocessing.model_dump(),
            retrieved_artefacts=retrieved[:7],
            rule_matches=rule_matches,
            impacted_modules=impacted_modules,
            artefacts_to_review=artefacts_to_review,
            draft_user_stories=draft_user_stories,
            draft_business_rules=draft_business_rules,
            draft_test_scenarios=draft_test_scenarios[:5],
            risks=risks[:3],
            clarifying_questions=questions[:5],
            assumptions=assumptions,
            dependencies=dependencies,
            recommended_actions=unique_preserve_order(recommended_actions)[:5],
            traceability_matrix=rtm,
            processing_time_ms=processing_ms,
            analysis_status="Analyzed",
            ba_review_status="Draft",
        ).model_dump()
