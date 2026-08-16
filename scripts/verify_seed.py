import json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

kb   = json.load(open('data/seed/knowledge_base.json', encoding='utf-8'))
crs  = json.load(open('data/seed/sample_change_requests.json', encoding='utf-8'))
gt   = json.load(open('data/seed/evaluation_ground_truth.json', encoding='utf-8'))
syns = json.load(open('data/seed/synonyms.json', encoding='utf-8'))

# Count by type
from collections import Counter
counts = Counter(x['type'] for x in kb)
print("=== knowledge_base.json ===")
for t, n in sorted(counts.items()):
    print(f"  {t:20} : {n}")
print(f"  {'TOTAL':20} : {len(kb)}")

print()
print("=== sample_change_requests.json ===")
for cr in crs:
    print(f"  {cr['id']} | {cr['priority']:8} | {cr['title']}")

print()
print("=== evaluation_ground_truth.json ===")
for g in gt:
    print(f"  {g['cr_id']} -> rules: {g['expected_rule_categories']}")

print()
print(f"=== synonyms.json : {len(syns)} entries ===")

# Validate: all gt artifact IDs exist in KB
kb_ids = {x['id'] for x in kb}
errors = []
for g in gt:
    for aid in g.get('expected_artifacts', []):
        if aid not in kb_ids:
            errors.append(f"  MISSING artefact {aid} in KB (referenced by {g['cr_id']})")
if errors:
    print()
    print("=== ERRORS ===")
    for e in errors: print(e)
    sys.exit(1)
else:
    print()
    print("All ground truth artefact IDs found in KB. OK")
