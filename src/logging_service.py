from __future__ import annotations

import json
import logging
import logging.config
from pathlib import Path

from .constants import CONFIG_DIR, ROOT_DIR


def configure_logging() -> None:
    config_path = CONFIG_DIR / "logging_config.json"
    if not config_path.exists():
        logging.basicConfig(level=logging.INFO)
        return
    config = json.loads(config_path.read_text(encoding="utf-8"))
    file_handler = config.get("handlers", {}).get("file", {})
    if "filename" in file_handler:
        target = ROOT_DIR / file_handler["filename"]
        target.parent.mkdir(parents=True, exist_ok=True)
        file_handler["filename"] = str(target)
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
