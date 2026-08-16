from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return normalized.replace("đ", "d").replace("Đ", "D")


def slugify(text: str) -> str:
    text = strip_accents(text.lower())
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "file"


def safe_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def unique_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def parse_json_list(value: str | list[Any] | None) -> list[Any]:
    if isinstance(value, list):
        return value
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []
