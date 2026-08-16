from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pandas as pd

from src.app_context import AppContext
from src.constants import ROOT_DIR, SEED_DIR
from src.export_service import ExportService
from src.utils import load_json

if __name__ == "__main__":
    output = ROOT_DIR / "sample_outputs"
    output.mkdir(exist_ok=True)
    ctx = AppContext()
    samples = {x["id"]: x for x in load_json(SEED_DIR / "sample_change_requests.json", [])}
    exporter = ExportService()
    for cr_id in ["CR-001", "CR-003"]:
        cr = samples[cr_id]
        result = ctx.run_analysis(cr, persist=False)
        docx_path = exporter.export_docx(cr, result, output)
        xlsx_path = exporter.export_rtm_xlsx(cr, result, output)
        print(docx_path.name, xlsx_path.name)
    evaluation = ctx.run_evaluation()
    (output / "Evaluation_Report.json").write_text(json.dumps(evaluation, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.DataFrame(evaluation["details"]).to_csv(output / "Evaluation_Details.csv", index=False, encoding="utf-8-sig")
    lines = ["# Evaluation Report", "", "Kết quả được tính trực tiếp từ pipeline trên 5 Change Request mẫu.", ""]
    for key, value in evaluation["summary"].items():
        lines.append(f"- **{key}:** {value:.4f}" if isinstance(value, float) else f"- **{key}:** {value}")
    (output / "Evaluation_Report.md").write_text("\n".join(lines), encoding="utf-8")
