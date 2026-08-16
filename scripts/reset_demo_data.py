from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.database import Database
from src.seed_loader import reset_demo_database

if __name__ == "__main__":
    backup = reset_demo_database(Database())
    print(f"Đã reset dữ liệu. Backup: {backup}")
