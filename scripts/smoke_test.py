from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app_context import AppContext
from src.constants import SEED_DIR
from src.utils import load_json

if __name__ == "__main__":
    ctx = AppContext()
    samples = load_json(SEED_DIR / "sample_change_requests.json", [])
    for sample in samples:
        result = ctx.run_analysis(sample, persist=False)
        assert result["retrieved_artefacts"], sample["id"]
        assert result["rule_matches"], sample["id"]
        assert result["impacted_modules"], sample["id"]
        assert result["traceability_matrix"], sample["id"]
        print(sample["id"], len(result["retrieved_artefacts"]), len(result["rule_matches"]), len(result["impacted_modules"]))
    print("Smoke test OK")
