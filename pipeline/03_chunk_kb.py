"""
할 일 : 청킹   
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR

csv.field_size_limit(10 * 1024 * 1024)

OUTPUT = DATA_DIR / "kb_chunk.csv"

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
    

# 청킹 대상 - 라이프스타일이 드러나는 서술형 칸들
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

# 너무 짧은 청크는 검색에 도움이 안 되므로 버린다
MIN_LENGTH = 20

def make_chunks(rows):
    """페르소나 한 명을 칸별 청크 여러 개로 쪼갠다."""
    chunks = []
    
    for row in rows :
        for column in CHUNK_COLUMNS:
            text = (row.get(column) or "").strip()
            
            if len(text) < MIN_LENGTH:
                continue
            
            chunks.append({
                "uuid" : row["uuid"],
                "district" : row["district"],
                "category" : column,        # 어느 칸에서 나왔는지
                "text" : text,
            })
    
    return chunks


def save_csv(rows,path) :
    """청크를 CSV 로 저장한다."""
    if not rows:
        print("[중단] 저장할 줄이 없습니다!")
        return
    
    columns = list(rows[0].keys())
    
    with open(path, "w", encoding="utf-8-sig", newline="") as f :
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    size = path.stat().st_size / 1024 / 1024
    print(f"✅ {path.name} 저장 · {len(rows):,}줄 · {size:.1f} MB")


if __name__ == "__main__":
    columns, rows = read_csv(DATA_DIR / "kb_persona.csv")
    chunks = make_chunks(rows)

    print(f"✅ {len(rows):,}명 → 청크 {len(chunks):,}개")
    print(f"   평균 {len(chunks)/len(rows):.1f}개/명")
    print()
    for c in chunks[:3]:
        print(f"   💬 [{c['category']}] {c['text'][:60]}...")
    print()
    
    save_csv(chunks, OUTPUT)









