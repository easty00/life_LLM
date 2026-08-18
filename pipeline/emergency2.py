import csv
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DATA_DIR

with open(DATA_DIR / "user_preferences_v4.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"줄 수: {len(rows)}")

for k in ["녹지", "안전", "교통", "상권", "의료", "교육", "문화"]:
    vals = [int(r[k]) for r in rows]
    print(f"{k}: 평균 {statistics.mean(vals):.2f} / 표준편차 {statistics.stdev(vals):.2f}")