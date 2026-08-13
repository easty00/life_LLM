"""
01_schema.py — data 폴더의 CSV 를 확인한다
 
수업(cosmetic_admin2/pipeline/01_schema.py)의 방식을 따르되,
우리 데이터에서 깨지던 부분을 고쳤다.
 
이 파일은 수업처럼 def 를 계속 덧붙여 나간다.
지금은 [1단계] 확인 까지만 들어 있다.
"""

import re
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


########
### 2단계 : 실행
########
"""
if __name__ == "__main__":
    paths = sorted(DATA_DIR.glob("*.csv"))
    
    if not paths:
        print(f"[중단] {DATA_DIR} 안에 csv 파일 부재!")
        sys.exit(1)
        
    print(f"[확인] {DATA_DIR} 안의 csv {len(paths)}개")
    print()
    print()
    
    for path in paths:
        # 100MB 가 넘는 파일은 줄 세기를 건너뛴다 (시간이 오래 걸린다)
        big = path.stat().st_size > 100 * 1024 * 1024
        preview(path, count_all=not big)
"""


# ------------------------------------------------------------------------------

"""
뭘 하는 건가

CSV는 전부 글자예요. "46"도 글자고 "홍성민"도 글자죠. 그런데 DB에 넣을 땐 age INTEGER, name TEXT처럼 타입을 정해야 해요. 값들을 보고 타입을 알아맞히는 게 이 단계예요.

수업 코드를 그대로 쓰되, 두 개만 손봐야 해요

수업에서 만드신 looks_int, looks_float, looks_date, infer_type 네 개는 그대로 가져오시면 돼요. 다만 우리 데이터에서 걸리는 게 둘 있어요.

① 숫자처럼 생겼지만 코드인 것
행정동ID_8자리   11010720
hnet_code       11110515

이건 INTEGER로 잡혀요. 그런데 더하거나 평균 낼 값이 아니잖아요. 코드가 INTEGER가 되면 나중에 앞자리 0이 잘리는 사고도 나요.

수업 코드에 이미 비슷한 처리가 있어요 — looks_int에서 전화번호(0으로 시작)를 걸러낸 그 부분이요. 같은 발상으로 이름을 보고 판단하는 규칙을 하나 추가하시면 돼요.

"""

# 이름에 이런 말이 들어가면 계산할 숫자가 아니라 '코드'로 본다
CODE_HINTS = ("code", "코드", "_id", "id_", "uuid", "행정동id")

def is_code_column(column):
    lower = column.lower()
    return any(hint in lower for hint in CODE_HINTS)

# 해당 값이 정수인지 확인하는 삼수    
def looks_int(text):
    # 만약 음수 부호 "="이 있으면 떼서 저장
    body = text[1:] if text.startswith("-") else text
    # 0~9 가 아닌 글자가 섞인 경우
    if not body.isdigit():
        return False # 정수가 아님
    # 만약 정수일 때 앞자리가 0으로 시작하면 전화번호 (조건 2자리 이상일때)
    #print("전화번호임")
    return not (len(body) > 1 and body.startswith("0"))

# 소수 판별 함수
def looks_float(text):
    # float 실수 반환되는지 우선 확인.
    try:
        float(text)
        
    # 위의 모든 경우가 아니면 실수가 아닌게 확실하니 False반환
    except ValueError:
        return False
    
    # 전달된 값에 "."이 없으면 실수 일리가 없으니확실히 false 반환
    if "." not in text:
        return False
         
    # 위의 모든 예외사항 통과하면 얘는 무조건 실수
    return True

# 날짜 판별 함수
def looks_date(text):
    # 정규표현식 \d(숫자)
    # \d{갯수} (숫자가 저 갯수만큼 일때)
    # fullmatch (검증할 정규표현식, 검사할 문자값)
    return re.fullmatch(r"\d{4}-\d{2}-\d{2}",text) is not None #무조건 한글자 검색. 

# 타입 추론 함수 생성
def infer_type(values):
    # 전달된 값에서 빈칸을 제외한 값을 변수에 담음
    seen = [v for v in values if v != ""]
    
    if not seen :
        return "TEXT"
    
    if all (looks_int(v) for v in seen):
        return "INTEGER"

    if all (looks_float(v) for v in seen):
            return "FLOAT"
    
    if all (looks_date(v) for v in seen):
            return "DATE"
    
    return "TEXT"


def describe(path, limit=SAMPLE_SIZE):
    """파일 하나의 칸별 타입을 출력한다."""
    columns, rows = read_csv(path, limit=limit)
    
    print(f"⏳ [{path.stem}] 타입을 추론하는 중...")
    
    for column in columns:
        values = [r[column] for r in rows]
        kind = "TEXT" if is_code_column(column) else infer_type(values)
        print(f"   💬 {column:28s} {kind}")

    print()

# 확인
"""
if __name__ == "__main__":
    path = DATA_DIR / "master_dataset_v3.csv"
    describe(path)
"""

"""
⏳ [master_dataset_v3] 타입을 추론하는 중...
   💬 시도_명칭                        TEXT
   💬 구                            TEXT
   💬 행정동명                         TEXT
   💬 행정동ID_8자리                    TEXT
   💬 hnet_code                    TEXT
   💬 면적_m2                        FLOAT
   💬 면적_km2                       FLOAT
   💬 CCTV_수                       FLOAT
   💬 버스정류장_수                      FLOAT
   💬 의료기관_수                       FLOAT
   💬 학교_수                         FLOAT
   💬 학원_수                         FLOAT
   💬 쓰레기통_수                       FLOAT
   💬 건물_수                         FLOAT
   💬 공원_수                         FLOAT
   💬 대형점포_수                       FLOAT
   💬 경찰관서_수                       FLOAT
   💬 소방관서_수                       FLOAT
   💬 지하철역_수                       FLOAT
   💬 점포_수                         FLOAT
   💬 범죄발생_구                       INTEGER
   💬 소음민원_구                       INTEGER
   💬 CCTV설치_구                     INTEGER
   💬 녹지면적_구                       INTEGER
   💬 학교녹지면적_구                     INTEGER
   💬 재해위험지구_구                     INTEGER
   💬 소음_주간_구                      FLOAT
   💬 소음_야간_구                      FLOAT
   💬 초미세먼지_구                      FLOAT
   💬 CCTV_밀도                      FLOAT
   💬 버스정류장_밀도                     FLOAT
   💬 의료기관_밀도                      FLOAT
   💬 학교_밀도                        FLOAT
   💬 학원_밀도                        FLOAT
   💬 쓰레기통_밀도                      FLOAT
   💬 건물_밀도                        FLOAT
   💬 공원_밀도                        FLOAT
   💬 대형점포_밀도                      FLOAT
   💬 경찰관서_밀도                      FLOAT
   💬 소방관서_밀도                      FLOAT
   💬 지하철역_밀도                      FLOAT
   💬 점포_밀도                        FLOAT
   💬 문화시설_수                       INTEGER
   💬 공연시설_수                       INTEGER
   💬 기타문화_수                       INTEGER
   💬 도서관_수                        INTEGER
   💬 전시시설_수                       INTEGER
   💬 무료문화시설_수                     INTEGER
   💬 문화시설_밀도                      FLOAT
   💬 공연시설_밀도                      FLOAT
   💬 기타문화_밀도                      FLOAT
   💬 도서관_밀도                       FLOAT
   💬 전시시설_밀도                      FLOAT
   💬 무료문화시설_밀도                    FLOAT
   💬 총전입                          INTEGER
   💬 총전출                          INTEGER
   💬 순이동                          INTEGER
   💬 전입률_퍼센트                      FLOAT
   💬 전출률_퍼센트                      FLOAT
   💬 이동률_퍼센트                      FLOAT
   💬 순이동률_퍼센트                     FLOAT
   💬 거주안정성_점수                     FLOAT  
"""









