from __future__ import annotations

import sys
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.database import Database

db = Database()
kb   = db.list_knowledge_base()
rules = db.list_rules()
syns  = db.list_synonyms()
crs   = db.list_change_requests()

counts = Counter(x['type'] for x in kb)
print("=== DB: knowledge_base ===")
for t, n in sorted(counts.items()):
    print(f"  {t:20}: {n}")
print(f"  {'TOTAL':20}: {len(kb)}")
print(f"\nRules   : {len(rules)}")
print(f"Synonyms: {len(syns)}")
print(f"\n=== DB: change_requests ({len(crs)}) ===")
for cr in crs:
    print(f"  {cr['id']} | {cr['priority']:8} | {cr['title']}")
