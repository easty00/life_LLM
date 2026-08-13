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


### 1단계 : 파일 읽기

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
    

