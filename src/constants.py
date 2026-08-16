from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
SEED_DIR = DATA_DIR / "seed"
EXPORT_DIR = DATA_DIR / "exports"
DB_PATH = DATA_DIR / "app.db"
CONFIG_DIR = ROOT_DIR / "config"
TEMPLATE_DIR = ROOT_DIR / "templates"

APP_NAME = "SmartFactory Change Impact Analyzer"
APP_NAME_VI = "Hệ thống hỗ trợ phân tích tác động yêu cầu thay đổi"
APP_SHORT_NAME = "SmartFactory"
APP_SUBTITLE = "Change Impact Analyzer"
DISCLAIMER = ""

PRIORITIES = ["Low", "Medium", "High", "Critical"]
CHANGE_TYPES = [
    "New Feature", "Enhancement", "Business Rule Change", "Workflow Change",
    "UI Change", "SLA Change", "Role and Permission Change", "Reporting Change", "Other",
]
CR_STATUSES = ["Draft", "Analyzed", "Reviewed"]
REVIEW_STATUSES = ["Draft", "Need Clarification", "Confirmed"]
IMPACT_LEVELS = ["Low", "Medium", "High", "Critical", "Need Review"]
ARTEFACT_TYPES = ["module", "role", "user_story", "business_rule", "sop", "test_case"]
