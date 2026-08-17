"""
할 일 : 검색어를 가중치 7개로 바꾼다

[B] Claude 가 검색어를 읽고 초안을 만든다
[A] 비슷한 회원을 찾아 그들의 실제 가중치로 보정한다
"""

import json
import sqlite3
import sys
import time
import anthropic
import numpy as np

from pathlib import Path
from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DB_PATH, API_KEY, MODEL


EMBED_MODEL = "intfloat/multilingual-e5-small"
INDICATORS = ["녹지", "안전", "교통", "상권", "의료", "교육", "문화"]

SYSTEM_PROMPT = """당신은 주거지 추천 서비스의 분석 도구입니다.
사용자의 검색어를 읽고, 7개 지표의 중요도를 1~5 점으로 매기세요.

지표 설명:
- 녹지: 공원, 산책로, 자연환경
- 안전: 치안, CCTV, 경찰서
- 교통: 지하철, 버스 접근성
- 상권: 마트, 식당, 카페, 시장
- 의료: 병원, 의원, 약국
- 교육: 학교, 학원
- 문화: 도서관, 공연장, 전시관

규칙:
1. 검색어에서 직접 드러난 것만 높게 주세요. 언급 없는 지표는 3점(보통)입니다.
2. 부정 표현을 주의하세요. "번화가는 싫어요" 는 상권을 낮게(1~2) 주어야 합니다.
3. 반드시 아래 JSON 형식으로만 답하세요. 설명이나 인사말을 붙이지 마세요.

{"녹지": 3, "안전": 3, "교통": 3, "상권": 3, "의료": 3, "교육": 3, "문화": 3}"""

client = anthropic.Anthropic(api_key=API_KEY)

# Claude 초안과 회원 평균을 몇 대 몇으로 섞을지.
# 0.7 이면 Claude 70%, 회원 30%
CLAUDE_RATIO = 0.7


# 함수들
def load_member_vectors(cur):
    """회원 청크 벡터를 전부 꺼낸다."""
    rows = cur.execute(
        "SELECT customer_id, category, text, vector FROM member_chunk"
    ).fetchall()
    
    vectors = np.array([json.loads(r[3]) for r in rows], dtype="float32")
    return rows, vectors


def find_similar_members(query, rows, vectors, model, top_k=5) :
    """검색어와 비슷한 회원을 찾는다.

    청크 단위로 검색하면 한 사람이 여러 번 걸릴 수 있다.
    그래서 사람별 최고 점수만 남기고 상위 top_k 명을 고른다.
    """
    q = model.encode([f"query: {query}"], normalize_embeddings=True)[0]
    scores = vectors @ q
    
    best = {}
    for (customer_id, category, text, _), score in zip(rows, scores):
        if customer_id not in best or score > best[customer_id][0]:
            best[customer_id] = (float(score), category, text)
    
    ranked = sorted(best.items(), key=lambda x: x[1][0], reverse=True)
    return ranked[:top_k]


def ask_claude(query):
    """Claude 에게 가중치 초안을 받는다."""
    res = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
    )
    
    text = res.content[0].text.strip()
    
    # 혹시 ```json 같은 게 붙어 나오면 떼어낸다
    text = text.replace("```json", "").replace("```","").strip()
    
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        print(f"[경고] JSON 파싱 실패: {text[:80]}")
        return {k: 3 for k in INDICATORS}       # 실패하면 전부 보통값
    
    # 7개가 다 있는지, 1~5 범위인지 검사한다
    result = {}
    for key in INDICATORS:
        value = data.get(key, 3)
        result[key] = max(1, min(5, int(value)))
    
    return result


def get_member_weights(cur, customer_ids):
    """회원들의 실제 가중치를 꺼낸다."""
    if not customer_ids:
        return []
    
    # IN (?, ?, ?) 형태를 사람 수만큼 만든다
    marks = ", ".join("?" * len(customer_ids))
    cols = ", ".join(INDICATORS)
    
    rows = cur.execute(
        f"SELECT customer_id, {cols} FROM user_preferences "
        f"WHERE customer_id IN ({marks})",
        customer_ids,
    ).fetchall()
    
    return [
        {"customer_id": r[0], **dict(zip(INDICATORS, r[1:]))}
        for r in rows
    ]


# 합치기
# Claude 초안과 회원 평균을 몇 대 몇으로 섞을지: 위에 적어둠

def blend(draft, member_weights):
    """Claude 초안을 회원들의 실제 가중치로 보정한다."""
    if not member_weights:
        return draft        # 비슷한 회원이 없으면 초안 그대로
    
    final = {}
    for key in INDICATORS:
        # 비슷한 회원들의 평균
        values = [m[key] for m in member_weights]
        member_avg = sum(values) / len(values)
        
        mixed = draft[key] * CLAUDE_RATIO + member_avg * (1 - CLAUDE_RATIO)
        final[key] = round(mixed, 1)
    
    return final


if __name__ == "__main__":
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    rows, vectors = load_member_vectors(cur)
    print(f"✅ 회원 청크 {len(rows)}개")

    model = SentenceTransformer(EMBED_MODEL)
    print()

    for q in ["산책 좋아하고 조용한 데",
              "번화가는 싫어요",
              "애들 학원 보내기 좋은 곳"]:
        print(f"검색어: {q}")

        draft = ask_claude(q)
        print(f"   [B] Claude 초안 : {draft}")

        similar = find_similar_members(q, rows, vectors, model)
        ids = [cid for cid, _ in similar]
        members = get_member_weights(cur, ids)
        print(f"   [A] 유사 회원   : {ids}")

        final = blend(draft, members)
        print(f"   [최종] {final}")
        print()

    con.close()





