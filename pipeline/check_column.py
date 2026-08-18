
import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DATA_DIR

csv.field_size_limit(10 * 1024 * 1024)

with open(DATA_DIR / "user_preferences_v4.csv", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"줄 수: {len(rows)}")

# 거래형태별로 빈칸 규칙이 지켜졌는지
for r in rows:
    t = r["거래형태"]
    bad = []
    if t == "매매" and (r["보증금"] or r["월세"]): bad.append("보증금/월세가 채워짐")
    if t == "전세" and (r["매매가"] or r["월세"]): bad.append("매매가/월세가 채워짐")
    if t == "월세" and r["매매가"]: bad.append("매매가가 채워짐")
    if t == "월세" and not r["월세"]: bad.append("월세가 비었음")
    if bad:
        print(f"  {r['customer_id']} [{t}] {bad}")


from collections import Counter

print("거래형태:", dict(Counter(r["거래형태"] for r in rows)))
print()

for t, col in [("매매", "매매가"), ("전세", "보증금"), ("월세", "보증금"), ("월세", "월세")]:
    v = sorted(int(r[col]) for r in rows if r["거래형태"] == t and r[col])
    if v:
        print(f"{t} {col}: {v[0]:,} ~ {v[-1]:,} (중간 {v[len(v)//2]:,}) · {len(v)}명")
print()

# 재검토 요청한 4명이 어떻게 됐나
for cid in ["C053", "C058", "C075", "C087"]:
    r = next(x for x in rows if x["customer_id"] == cid)
    print(f"{cid} [{r['거래형태']}] 매매가 {r['매매가'] or '-'} / 보증금 {r['보증금'] or '-'} / 월세 {r['월세'] or '-'}")