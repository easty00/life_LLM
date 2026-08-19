"""
검증 : 유사 회원의 가중치가 무작위 회원과 다른가?

다르지 않다면 A(회원 보정)는 노이즈이므로 빼거나 방식을 바꿔야 한다.
"""

import json
import random
import sqlite3
import statistics
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DB_PATH, DATA_DIR, EMBED_MODEL, INDICATORS

QUERIES = [
    ("산책 좋아하고 조용한 데", "녹지"),      # 이 검색어라면 이 지표가 달라야 한다
    ("맛집 탐방이 취미예요", "상권"),
    ("애들 학원 보내기 좋은 곳", "교육"),
    ("초등학생 아이를 키우고 있어요", "교육"),      # ← 추가
    ("아이 교육에 관심이 많아요", "교육"),          # ← 추가
    ("병원 가까운 게 중요해요", "의료"),
]


def load_all(cur):
    rows = cur.execute(
        "SELECT customer_id, category, text, vector FROM member_chunk"
    ).fetchall()
    vectors = np.array([json.loads(r[3]) for r in rows], dtype="float32")

    # 기존: DB에서 읽기
    #cols = ", ".join(INDICATORS)
    #prefs = {}
    #for r in cur.execute(f"SELECT customer_id, {cols} FROM user_preferences"):
    #    prefs[r[0]] = dict(zip(INDICATORS, r[1:]))
    
    # 새 CSV에서 읽기
    import csv
    prefs = {}
    with open(DATA_DIR / "user_preferences_v3.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            prefs[row["customer_id"]] = {k: int(row[k]) for k in INDICATORS}

    return rows, vectors, prefs


def similar_ids(query, rows, vectors, model, top_k=5):
    q = model.encode([f"query: {query}"], normalize_embeddings=True)[0]
    scores = vectors @ q
    best = {}
    for (cid, _, _, _), s in zip(rows, scores):
        if cid not in best or s > best[cid]:
            best[cid] = float(s)
    ranked = sorted(best.items(), key=lambda x: x[1], reverse=True)
    return [cid for cid, _ in ranked[:top_k]]


if __name__ == "__main__":
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    rows, vectors, prefs = load_all(cur)
    model = SentenceTransformer(EMBED_MODEL)
    all_ids = list(prefs.keys())

    random.seed(42)

    for query, indicator in QUERIES:
        # 유사 회원 5명의 해당 지표 평균
        ids = similar_ids(query, rows, vectors, model)
        sim_avg = statistics.mean(prefs[c][indicator] for c in ids)

        # 무작위 5명 평균을 1,000번 뽑아 분포를 만든다
        rand_avgs = []
        for _ in range(1000):
            picked = random.sample(all_ids, 5)
            rand_avgs.append(statistics.mean(prefs[c][indicator] for c in picked))

        rand_mean = statistics.mean(rand_avgs)
        rand_std = statistics.stdev(rand_avgs)

        # 유사 평균이 무작위 분포에서 몇 표준편차 떨어져 있나
        z = (sim_avg - rand_mean) / rand_std

        # 무작위 1,000번 중 유사 평균보다 높은 게 몇 %인가
        pct = sum(1 for v in rand_avgs if v >= sim_avg) / 10

        print(f"검색어: {query}")
        print(f"   [{indicator}] 유사 5명 평균 {sim_avg:.2f} · 무작위 평균 {rand_mean:.2f}±{rand_std:.2f}")
        print(f"   z = {z:+.2f} · 무작위가 이보다 높을 확률 {pct:.0f}%")
        print()    

    for query, indicator in QUERIES:
        ids = similar_ids(query, rows, vectors, model)
        sim_avg = statistics.mean(prefs[c][indicator] for c in ids)

        # 누가 뽑혔는지, 왜 뽑혔는지 확인
        print(f"검색어: {query}")
        for cid in ids:
            # 그 사람의 어느 청크가 걸렸는지 찾기
            best_text = ""
            best_score = -1
            q = model.encode([f"query: {query}"], normalize_embeddings=True)[0]
            for (c, cat, text, _), s in zip(rows, vectors @ q):
                if c == cid and s > best_score:
                    best_score, best_text, best_cat = float(s), text, cat
            print(f"   {cid} [{indicator} {prefs[cid][indicator]}점] ({best_cat}) {best_text[:60]}...")

    con.close()
    
