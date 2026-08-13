"""
01_schema.py — data 폴더의 CSV 를 확인한다
 
수업(cosmetic_admin2/pipeline/01_schema.py)의 방식을 따르되,
우리 데이터에서 깨지던 부분을 고쳤다.
 
이 파일은 수업처럼 def 를 계속 덧붙여 나간다.
지금은 [1단계] 확인 까지만 들어 있다.
"""

import csv
import sys
from pathlib import Path

# 수업과 동일: 파일이 pipeline/ 안에 있으므로 parent 를 두 번 올라가야 프로젝트 뿌리다
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

# CSV 한 칸에 아주 긴 글이 들어있을 수 있다 (페르소나 서술문).
# 파이썬 기본 상한은 131,072 글자라 그걸 넘으면 에러가 나므로 미리 올려둔다.
csv.field_size_limit(10*1024*1024)

# 타입을 살펴볼 때 읽을 줄 수. 11만 줄을 전부 읽을 필요가 없다.
SAMPLE_SIZE = 500

########
### 1단계 : 파일 읽기
########

def read_csv(path, limit=None):
    """CSV 를 읽어 (칸 이름 목록, 줄 목록) 을 돌려준다.
 
    수업 코드와 다른 점 두 가지 ─
 
    1) encoding 이 "utf-8" 이 아니라 "utf-8-sig" 다.
       윈도우에서 만든 CSV 는 맨 앞에 BOM 이라는 눈에 안 보이는 표식이 붙는다.
       "utf-8" 로 읽으면 그게 글자로 딸려 들어와서 첫 칸 이름이
       'customer_id' 가 아니라 '\ufeffcustomer_id' 가 된다.
       사람 눈엔 같아 보이지만 파이썬은 다른 이름으로 보기 때문에
       나중에 표끼리 이어붙일 때(FK) 연결이 통째로 깨진다.
       "utf-8-sig" 는 그 BOM 을 알아서 떼준다.
 
    2) limit 을 주면 그 줄 수까지만 읽는다.
       nemotron.csv 는 438MB 다. 칸이 어떻게 생겼는지 보는 데
       11만 줄을 전부 메모리에 올릴 이유가 없다.
    """
    
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
    

#if __name__ == "__main__":
#    path = DATA_DIR / "customers_v2.csv"
#    columns, rows = read_csv(path, limit=5)
#
#    print("칸 이름:", columns)
#    print("가져온 줄 수:", len(rows))
#    print()
#    print("첫 번째 줄:", rows[0])
#    '''
#    정상출력 확인
#    칸 이름: ['customer_id', 'name', 'gender', 'age', 'phone', 'email', 'city', 'city_dong', 'work_city', 'work_dong', 'joined_at']
#    가져온 줄 수: 5
#
#    첫 번째 줄: {'customer_id': 'C001', 'name': '전기태', 'gender': 'M', 'age': '74', 'phone': '010-4949-1773', 'email': 'sungmin70@example.com', 'city': '동대문구', 'city_dong': '전농제1동', 'work_city': '영등포구', 'work_dong': '영등포동', 'joined_at': '2024-03-30'}
#    '''
    
def count_rows(path):
    """줄 수만 센다. 줄을 저장하지 않으므로 파일이 커도 메모리를 안 먹는다.
 
    주의: 파일의 '줄바꿈 개수'를 세면 안 된다.
    페르소나 서술문처럼 따옴표 안에 줄바꿈이 들어있는 칸이 있어서,
    실제 데이터 한 줄이 파일에서는 여러 줄일 수 있다.
    그래서 csv 로 제대로 해석하면서 세야 정확하다.
    """
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


#if __name__ == "__main__":
#    path = DATA_DIR / "customers_v2.csv"
#    print(count_rows(path))   # 100 나와야 함 -> 나옴!

def human_size(num_bytes):
    """1234567 -> '1.2 MB' 처럼 사람이 읽기 좋게 바꾼다."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}"
        size /= 1024

#path = DATA_DIR / "customers_v2.csv"

#if __name__ == "__main__":
#    print(human_size(path.stat().st_size))          # -> '10.8 KB'
#    print(human_size(459720304))     # -> '438.4 MB' (nemotron.csv 실제 크기)
#    print(human_size(500))           # -> '500.0 B'  (1024보다 작은 경우)
    
def preview(path, limit=SAMPLE_SIZE, count_all=True):
    """파일 하나를 확인해서 화면에 뿌린다."""
    columns, rows = read_csv(path, limit=limit)
    
    # 큰 파일은 줄 세는 데도 시간이 걸리니 건너뛸 수 있게 했다
    total = count_rows(path) if count_all else None
    total_text = f"{total:,}행" if total is not None else "행수 미확인"
    
    print(f"⏳ [{path.name}] 파일을 확인하는 중...")
    print(f"✅ {human_size(path.stat().st_size)} · {total_text} · {len(columns)}칸")
    print()
    
    # 칸 이름과, 그 칸의 첫 번째 값(비어있지 않은 것)을 나란히 보여준다
    for column in columns:
        # next(조건에 맞는 값들, 없을 때 쓸 기본값)
        # 빈칸이 아닌 첫 값을 하나만 꺼낸다
        example = next((r[column] for r in rows if r[column] not in ("", None)), "")
        example = example.replace("\n", " ")
        
        # 페르소나 서술문은 아주 기니까 잘라서 보여준다
        if len(example) > 60:
            example = example[:60] + " ..."
            
        print(f"    💬 {column:28s} {example}")
    print()    

#if __name__ == "__main__":
#    path = DATA_DIR / "customers_v2.csv"
#    preview(path)
#    ''' 잘 출력됨!
#      [customers_v2.csv] 파일을 확인하는 중...
#✅ 10.8 KB · 100행 · 11칸
#
#    💬 customer_id                  C001
#    💬 name                         전기태
#    💬 gender                       M
#    💬 age                          74
#    💬 phone                        010-4949-1773
#    💬 email                        sungmin70@example.com
#    💬 city                         동대문구
#    💬 city_dong                    전농제1동
#    💬 work_city                    영등포구
#    💬 work_dong                    영등포동
#    💬 joined_at                    2024-03-30
#    '''










