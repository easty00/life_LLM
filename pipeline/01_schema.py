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

# 2단계

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


# ------------------------------------------------------------------------------

# 3단계 : PK 찾기

"""
다음은 수업의 infer_pk 차례예요. 미리 짚어드릴 게 하나 있어요.

수업 규칙은 **"이름이 _id로 끝나는 칸 중, 값이 안 겹치는 것"**이었죠. 그런데 저번에 봤듯 우리 데이터엔:

nemotron.csv의 열쇠는 uuid — _id로 안 끝남
master_dataset_v3.csv는 한 칸으로 안 되고 구 + 행정동명을 합쳐야 열쇠가 됨

이 두 개가 수업 규칙 그대로는 안 잡혀요. is_code_column을 이미 만들어두셨으니, PK 후보를 "이름이 _id로 끝나는 것"이 아니라 "코드 컬럼인 것"으로 바꾸는 방향이 자연스러울 것 같아요.
"""

# PK를 찾아주는 함수
def infer_pk(columns, rows):
    # 1) 칸 하나로 되는지 먼저 본다 (기존 로직)
    for col in columns:
        # 코드 컬럼이 아니면 제외
        if not is_code_column(col):
            continue
        
        # value 값이 빈 문자열은 제외
        values = [r[col] for r in rows]
        if "" in values:
            continue
        
        # value 값이 중복되지 않으면 그건 PK
        if len(set(values)) == len(values):
            return [col]    # 리스트로 통일 (2)번과 형태 맞추려고)
    
    # 2) 칸 하나로 안 되면, 코드 컬럼 두 개씩 짝지어 시도한다
    code_cols = [c for c in columns if is_code_column(c) or c in ("구", "행정동명")]

    for i in range(len(code_cols)):
        for j in range(i + 1, len(code_cols)):
            c1, c2 = code_cols[i], code_cols[j]
            combo = [r[c1] + "|" + r[c2] for r in rows]
            if len(set(combo)) == len(rows):
                return [c1, c2]
        
    # 위의 조건이 모두 만족하지 않는다면 PK가 없음
    return None

#if __name__ == "__main__":
#    for name in ["customers_v2.csv", "master_dataset_v3.csv", "nemotron.csv"]:
#        path = DATA_DIR / name
#        columns, rows = read_csv(path, limit=500)
#        pk = infer_pk(columns, rows)
#        print(f"{name:24s} PK: {pk}")

""" 출력결과
customers_v2.csv         PK: customer_id
master_dataset_v3.csv    PK: None
nemotron.csv             PK: uuid
"""


# 복합키(master_dataset_v3.csv)
columns, rows = read_csv(DATA_DIR / "master_dataset_v3.csv", limit=500)

gu_values = [r["구"] for r in rows]
dong_values = [r["행정동명"] for r in rows]

#print("구 종류 수:", len(set(gu_values)))          # 25개뿐 -> 중복 많음
#print("행정동명 종류 수:", len(set(dong_values)))   # 427개 나와야 하는데 1개 부족
""" # 중복된 행정구를 찾아본다.
from collections import Counter

dong_values = [r["행정동명"] for r in rows]
counts = Counter(dong_values)

for name, n in counts.items():
    if n > 1:
        print(f"{name}  {n}번 나옴")  #신사동이 중복됨

for r in rows:
    if r["행정동명"] == "신사동":
        print(r["구"], r["행정동명"]) # 관악구 신사동, 강남구 신사동
"""
# 구+동 조합 확인
combo = [r["구"] + "|" + r["행정동명"] for r in rows]

#print("합친 값 종류 수:", len(set(combo)))
#print("전체 행 수:", len(rows))             # 둘 다 427개로 일치


# 안전한 PK를 만들기 위한 함수 추가 (infer_pk에 2) 추가함)

""" 정상출력확인
if __name__ == "__main__":
    path = DATA_DIR / "master_dataset_v3.csv"
    columns, rows = read_csv(path, limit=500)
    pk = infer_pk(columns, rows)
    print("PK:", pk)
"""

# ------------------------------------------------------------------------------

# 4단계 : FK 찾기

"""
01_schema.py
├── read_csv        CSV 읽기 (BOM 처리, limit)
├── count_rows      줄 수 세기 (메모리 안 먹음)
├── human_size       바이트 → 사람이 읽기 좋은 크기
├── preview          파일 하나 요약 출력
├── is_code_column   코드성 칸 판별
├── looks_int/float/date   값 하나가 무슨 타입인지
├── infer_type       칸 전체를 보고 타입 결정
├── describe         파일 하나의 칸별 타입 출력
└── infer_pk         PK 찾기 (단일키 + 복합키)

이제 각 CSV의 PK가 뭔지, 칸 타입이 뭔지까지 자동으로 잡을 수 있게 됐어요. 수업의 01_schema.py가 원래 하려던 걸 우리 데이터로 다 통과시킨 거예요.

수업에서 남은 건 owner_of(PK의 주인 표 찾기)랑 그걸로 FK 연결하는 부분이에요. 이게 되면:

customers.customer_id  ←  user_preferences.customer_id  (FK)
customers.customer_id  ←  nemotron.customer_id            (FK)

이런 관계가 자동으로 잡혀서, 나중에 CREATE TABLE에 FOREIGN KEY를 자동 생성할 수 있는 재료가 돼요.

다만 여기서 하나 미리 알려드릴 게 있어요 — 수업 코드의 owner_of는 표 이름 하나를 다루는 구조인데, 지금 우리는 PK가 리스트(['구', '행정동명'])로 바뀌었죠. master_dataset_v3처럼 복합키를 가진 표는 FK로 연결될 일이 없어서(다른 표가 "구+행정동명"을 참조하진 않으니) 큰 문제는 없을 텐데, 이 부분은 직접 짜보시면서 막히면 말씀해주세요.

***개념 먼저***

수업의 owner_of는 이런 논리였어요:
    def owner_of(column, tables):
        stem = column[:-3]     # 'customer_id' -> 'customer'
        for candidate in (stem, stem+"s", stem+"es"):
            if candidate in tables:
                return candidate
        return None

"칸 이름이 customer_id면, 뒤에 _id를 떼고(customer) 거기에 s나 es를 붙인 이름(customers)의 표를 찾는다"는 거예요. 영어 복수형 규칙에 기댄 방식이죠.

"""

# 별칭 적용
TABLE_ALIAS = {
    "customers_v2": "customers",
}

def table_name(path):
    stem = path.stem
    return TABLE_ALIAS.get(stem, stem)

tables = ["customers", "user_preferences", "nemotron", "master_dataset_v3"]

def owner_of(column, tables):
    stem = column[:-3]     # 'customer_id' -> 'customer'
    for candidate in (stem, stem+"s", stem+"es"):
        if candidate in tables:
            return candidate
    return None


# 제대로 적용되는지 확인
if __name__ == "__main__":
    tables = ["customers", "user_preferences", "nemotron", "master_dataset_v3"]
    print(owner_of("customer_id", tables))   # 'customers' 나와야 함
    print(owner_of("region_id", tables))     # None 나와야 함 (그런 표 없음)

""" 
실제로 우리 데이터에 돌리면 어떻게 되나

user_preferences 표 검사할 때:

customer_id 칸 발견 → owner_of 호출 → customers 표에 PK가 customer_id인 걸 확인 → FK 연결됨

nemotron 표 검사할 때:

customer_id 칸 발견 → 역시 customers로 연결됨
uuid 칸은? → _id로 안 끝나서(is_code_column으로 바꾼 버전이면 코드 컬럼이긴 함) 검사 대상에 들어가긴 하는데, owner_of("uuid", ...)를 해보면 uui를 떼는 이상한 계산이 나와서 None이 나올 거예요. 이건 정상이에요 — uuid는 이 표 자신의 PK지 남의 표를 참조하는 FK가 아니니까요.

master_dataset_v3 검사할 때:

이 표엔 _id로 끝나거나 코드로 보이는 칸이 행정동ID_8자리, hnet_code 정도인데, 이것들의 주인 표(행정동ID, hnet)가 존재하지 않으니 전부 None → FK 없음. 이것도 맞는 결과예요, master_dataset_v3는 다른 표를 참조 안 하니까요.
"""

# ------------------------------------------------------------------------------

# 5단계 : tables 딕셔너리로 전부 묶기












    