"""회원 100명 페르소나를 작은 CSV 로 뽑는다 (다른 AI 에게 넘기기 위해)"""

import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DATA_DIR

csv.field_size_limit(10 * 1024 * 1024)

COLUMNS = [
    "customer_id", "persona", "professional_persona", "sports_persona",
    "arts_persona", "travel_persona", "culinary_persona", "family_persona",
    "cultural_background", "career_goals_and_ambitions", "skills_and_expertise_list",
    "hobbies_and_interests_list",
]

with open(DATA_DIR / "nemotron.csv", encoding="utf-8-sig", newline="") as f:
    rows = []
    for i, row in enumerate(csv.DictReader(f), start=1):
        if i > 100:
            break
        row["customer_id"] = f"C{str(i).zfill(3)}"
        rows.append({c: row.get(c, "") for c in COLUMNS})

out = DATA_DIR / "member_persona.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLUMNS)
    w.writeheader()
    w.writerows(rows)

print(f"✅ {out.name} · {len(rows)}줄")