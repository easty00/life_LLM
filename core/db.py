"""
SQLite 조회 기능을 여기 모아둔다.

pipeline/ 은 DB 를 만들고 채우는 역할,
이 파일은 이미 만들어진 표에서 데이터를 꺼내는 역할만 한다.

나중에 다른 DB 로 바꾸더라도 이 파일만 고치면 되도록 분리해 둔다.
"""

import sqlite3

from core.config import DB_PATH, INDICATORS

# check_same_thread=False 는 나중에 Flask 서버를 붙일 때 필요하다.
# SQLite 연결은 기본적으로 만든 스레드에서만 쓸 수 있는데,
# 웹 서버는 요청마다 다른 스레드로 도는 경우가 있어서 막힌다

con = sqlite3.connect(DB_PATH, check_same_thread=False)

def query(sql, params=()):
    """여러 줄을 튜플 목록으로 돌려준다."""
    return con.execute(sql, params).fetchall()


def one(sql, params=()):
    """한 줄만 돌려준다. 없으면 None."""
    return con.execute(sql, params).fetchone()


def dicts(sql, params=()):
    """칸 이름이 붙은 딕셔너리 목록으로 돌려준다.

    query 는 ('종로구', '청운효자동', 0.5) 처럼 튜플이라
    r[0], r[1] 처럼 위치로 꺼내야 한다.
    칸 순서가 바뀌면 조용히 잘못된 값을 읽게 된다.

    dicts 는 r["행정동명"] 처럼 이름으로 꺼낼 수 있다.
    특히 Claude 에게 데이터를 넘길 때는 칸 이름이 있어야
    LLM 이 무엇을 보고 있는지 알 수 있다.
    """
    cur = con.execute(sql, params)
    columns = [c[0] for c in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


# ── 프로젝트 전용 조회 함수 ─────────────────────────────


def member_chunks():
    """회원 청크와 벡터를 전부 꺼낸다. (07번에서 쓰던 것)"""
    return dicts(
        "SELECT customer_id, category, text, vector FROM member_chunk"
    )


def member_weights(customer_ids):
    """회원들의 가중치 7개를 꺼낸다.

    IN (?, ?, ?) 형태를 사람 수만큼 만들어야 하므로
    물음표 개수를 동적으로 맞춘다.
    """
    if not customer_ids:
        return []
    
    marks = ", ".join("?" * len(customer_ids))
    cols = ", ".join(INDICATORS)

    return dicts(
        f"SELECT customer_id, {cols} FROM user_preferences "
        f"WHERE customer_id IN ({marks})",
        tuple(customer_ids),
    )

def region_densities(columns):
    """행정동별 밀도 칸들을 꺼낸다. (08번에서 쓰던 것)

    칸 이름을 밖에서 받는 이유 —
    어떤 밀도 칸을 쓸지는 08번의 INDICATOR_COLUMNS 가 정한다.
    조회 계층은 "무엇을 쓸지" 를 정하지 않고 "꺼내주기만" 한다
    """
    quoted = ", ".join(f'"{c}"' for c in columns)
    return dicts(f'SELECT 구, 행정동명, {quoted} FROM master_dataset_v3')


def kb_chunks():
    """지식베이스 청크와 벡터를 전부 꺼낸다. (09번에서 쓸 것)"""
    return dicts(
        "SELECT chunk_id, uuid, district, category, text, vector FROM kb_chunk"
    )


if __name__ =="__main__":
    print("표 목록:")
    for r in query("SELECT name FROM sqlite_master WHERE type='table'"
                   "AND name NOT LIKE 'sqlite_%' ORDER BY name"):
        n = one(f"SELECT COUNT(*) FROM {r[0]}")[0]
        print(f"    {r[0]:20s} {n:,}")
    print()
    
    print("dicts 예시: ")
    for row in dicts("SELECT 구, 행정동명, 공원_밀도, 학원_밀도 "
                     "FROM master_dataset_v3 LIMIT 3"):
        print(f"    {row}")