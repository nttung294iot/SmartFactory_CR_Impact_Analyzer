from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.constants import SEED_DIR

rules = json.load(open(SEED_DIR / "rules.json", encoding="utf-8"))
gt = json.load(open(SEED_DIR / "evaluation_ground_truth.json", encoding="utf-8"))

print("=== Rules ===")
for r in rules:
    print(r['id'], '|', r['name'], '| required:', r['required_keywords'], '| modules:', r['module_mappings'])

print()
print("=== CR coverage ===")
covered = set()
for g in gt:
    print(g['cr_id'], '->', g['expected_rule_categories'])
    for cat in g['expected_rule_categories']:
        covered.add(cat)

print()
print("=== Covered categories ===")
for c in sorted(covered):
    print(' ', c)

print()
print("=== Rules NOT covered by any CR sample ===")
for r in rules:
    if r['name'] not in covered and r['category'] != 'Generic Fallback':
        print(' MISSING:', r['id'], '|', r['name'], '| modules:', r['module_mappings'])
