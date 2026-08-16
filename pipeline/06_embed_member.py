"""
할 일 : 회원 100명의 페르소나를 벡터로 만들어 저장

kb_chunk(지식베이스 2,500명)와 별개다.
회원은 user_preferences(가중치 7개)를 갖고 있어서,
검색어와 비슷한 회원을 찾으면 그 사람의 가중치를 가져올 수 있다.
"""

import csv
import json
import sqlite3
import sys
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR, DB_PATH

csv.field_size_limit(10 * 1024 * 1024)

MODEL_NAME = "intfloat/multilingual-e5-small"
MEMBER_COUNT = 100

SOURCE = DATA_DIR / "nemotron.csv"

# 03번과 같은 칸들. 회원도 같은 방식으로 쪼갠다

CHUNK_COLUMNS = [
    "persona",
    "professional_persona",
    "sports_persona",
    "arts_persona",
    "travel_persona",
    "culinary_persona",
    "family_persona",
    "cultural_background",
    "career_goals_and_ambitions",
]

MIN_LENGTH = 20


def read_csv(path, limit=None):
    """CSV 를 읽어 (칸 이름 목록, 줄 목록) 을 돌려준다."""
    
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        if limit is None :
            return fieldnames, list(reader)
        
        rows = []
        
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)
            
        return fieldnames, rows
    

# 회원 읽고 customer_id 붙이기

def load_members(path, count=MEMBER_COUNT) :
    """nemotron.csv 앞 count 명을 읽고 customer_id 를 붙인다.

    원본 CSV 에는 customer_id 칸이 없다.
    customers.csv 의 C001~C100 과 순서로 맞추는 것이 조장님이 잡아둔 규칙이라
    여기서도 같은 방식으로 만든다.
    """
    _, rows = read_csv(path, limit=count)
    
    # zfill(3) 은 앞을 0 으로 채워 자릿수를 맞춘다: 1 -> '001'
    for i, row in enumerate(rows, start=1) :
        row["customer_id"] = f"C{str(i).zfill(3)}"
    
    print(f"✅ 회원 {len(rows)}명 읽음 (C001 ~ C{str(len(rows)).zfill(3)})")
    return rows



