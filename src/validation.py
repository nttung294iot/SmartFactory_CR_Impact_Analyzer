from __future__ import annotations

import re
from typing import Any

from pydantic import ValidationError

from .constants import ARTEFACT_TYPES
from .models import Artefact, ChangeRequest


_FIELD_LABELS: dict[str, str] = {
    "title": "Tiêu đề (Title)",
    "requester": "Người yêu cầu (Requester)",
    "priority": "Mức ưu tiên (Priority)",
    "description": "Mô tả thay đổi (Change Description)",
    "reason_for_change": "Lý do thay đổi (Business Reason)",
    "expected_behavior": "Hành vi mong muốn (Expected Behavior)",
}


def validate_change_request(data: dict[str, Any]) -> tuple[bool, list[str], ChangeRequest | None]:
    try:
        model = ChangeRequest(**data)
        return True, [], model
    except ValidationError as exc:
        messages: list[str] = []
        for item in exc.errors():
            field = ".".join(str(x) for x in item["loc"])
            label = _FIELD_LABELS.get(field, field)
            messages.append(f"**{label}** không được để trống.")
        return False, messages, None


def validate_artefact(data: dict[str, Any], existing_ids: set[str], module_ids: set[str], allow_same_id: bool = False) -> list[str]:
    errors: list[str] = []
    try:
        artefact = Artefact(**data)
    except ValidationError as exc:
        return [item["msg"] for item in exc.errors()]
    if artefact.id in existing_ids and not allow_same_id:
        errors.append("ID artefact đã tồn tại.")
    if artefact.type not in ARTEFACT_TYPES:
        errors.append("Type artefact không hợp lệ.")
    if not artefact.title.strip():
        errors.append("Title không được để trống.")
    missing_modules = [item for item in artefact.module_ids if item not in module_ids]
    if missing_modules:
        errors.append(f"Module không tồn tại: {', '.join(missing_modules)}")
    if not re.fullmatch(r"\d+\.\d+", artefact.version):
        errors.append("Version phải có định dạng x.y, ví dụ 1.0.")
    return errors
