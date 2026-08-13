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


########
### 2단계 : 실행
########

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

''' 실행결과(열면 긺 주의)
[확인] C:\Users\lecra\Desktop\LifeFitDB\data 안의 csv 4개


⏳ [customers_v2.csv] 파일을 확인하는 중...
✅ 10.8 KB · 100행 · 11칸

    💬 customer_id                  C001
    💬 name                         전기태
    💬 gender                       M
    💬 age                          74
    💬 phone                        010-4949-1773
    💬 email                        sungmin70@example.com
    💬 city                         동대문구
    💬 city_dong                    전농제1동
    💬 work_city                    영등포구
    💬 work_dong                    영등포동
    💬 joined_at                    2024-03-30

⏳ [master_dataset_v3.csv] 파일을 확인하는 중...
✅ 210.4 KB · 427행 · 62칸

    💬 시도_명칭                        서울
    💬 구                            종로구
    💬 행정동명                         청운효자동
    💬 행정동ID_8자리                    11010720
    💬 hnet_code                    11110515
    💬 면적_m2                        2570477.37785328
    💬 면적_km2                       2.57047737785328
    💬 CCTV_수                       165.0
    💬 버스정류장_수                      29.0
    💬 의료기관_수                       8.0
    💬 학교_수                         138.0
    💬 학원_수                         15.0
    💬 쓰레기통_수                       14.0
    💬 건물_수                         2246.0
    💬 공원_수                         2.0
    💬 대형점포_수                       1.0
    💬 경찰관서_수                       2.0
    💬 소방관서_수                       1.0
    💬 지하철역_수                       0.0
    💬 점포_수                         10950.0
    💬 범죄발생_구                       2981
    💬 소음민원_구                       2200
    💬 CCTV설치_구                     1872
    💬 녹지면적_구                       228451
    💬 학교녹지면적_구                     17469
    💬 재해위험지구_구                     2
    💬 소음_주간_구                      62.2875
    💬 소음_야간_구                      56.85
    💬 초미세먼지_구                      19.60666666666667
    💬 CCTV_밀도                      64.19041125263621
    💬 버스정류장_밀도                     11.281951068645151
    💬 의료기관_밀도                      3.1122623637641795
    💬 학교_밀도                        53.6865257749321
    💬 학원_밀도                        5.8354919320578365
    💬 쓰레기통_밀도                      5.446459136587315
    💬 건물_밀도                        873.7676586267935
    💬 공원_밀도                        0.7780655909410449
    💬 대형점포_밀도                      0.3890327954705224
    💬 경찰관서_밀도                      0.7780655909410449
    💬 소방관서_밀도                      0.3890327954705224
    💬 지하철역_밀도                      0.0
    💬 점포_밀도                        4259.909110402221
    💬 문화시설_수                       14
    💬 공연시설_수                       3
    💬 기타문화_수                       5
    💬 도서관_수                        2
    💬 전시시설_수                       4
    💬 무료문화시설_수                     12
    💬 문화시설_밀도                      5.45
    💬 공연시설_밀도                      1.17
    💬 기타문화_밀도                      1.95
    💬 도서관_밀도                       0.78
    💬 전시시설_밀도                      1.56
    💬 무료문화시설_밀도                    4.67
    💬 총전입                          1017
    💬 총전출                          1314
    💬 순이동                          -297
    💬 전입률_퍼센트                      21.01
    💬 전출률_퍼센트                      27.15
    💬 이동률_퍼센트                      48.16
    💬 순이동률_퍼센트                     -6.14
    💬 거주안정성_점수                     71.7

⏳ [nemotron.csv] 파일을 확인하는 중...
✅ 438.4 MB · 행수 미확인 · 26칸

    💬 uuid                         03b4f36a18e6469386d0286dddd513c8
    💬 professional_persona         전기태 씨는 광주 서구의 하역 현장에서 수십 년간 짐을 쌓아 올리며, 지렛대 원리를 이용해 무거운 자재를 효 ...
    💬 sports_persona               전기태 씨는 주말마다 무등산 자락을 느릿느릿 걸으며 땀을 흘리고, 내려오는 길에 단골 목욕탕에서 친구들과 엉 ...
    💬 arts_persona                 전기태 씨는 거실 소파에 깊숙이 파묻혀 텔레비전에서 나오는 옛날 가요 프로그램을 보며 젊은 시절의 추억에 젖 ...
    💬 travel_persona               전기태 씨는 아내와 함께 전국의 역사 유적지를 찾아다니며 옛 조상들의 발취를 느끼는 여행을 즐깁니다. 화려한 ...
    💬 culinary_persona             전기태 씨는 일주일에 한 번 배달 짜장면과 탕수육을 시켜 먹는 날을 손꼽아 기다리며, 2주에 한 번은 아내와 ...
    💬 family_persona               전기태 씨는 전·월세 아파트에서 평생의 동반자인 아내와 단출하게 살아가며, 투박한 전라도 사투리로 서로를 챙 ...
    💬 persona                      전기태 씨는 광주 서구에서 평생 하역 일을 하며 살아온 70대 가장으로, 투박한 손마디에 삶의 흔적이 배어  ...
    💬 cultural_background          광주 서구에서 평생을 보내며 투박하지만 정겨운 전라도 사투리가 몸에 배어 있고, 시장통 사람들과 어울려 왁자 ...
    💬 skills_and_expertise         수십 년간 하역 현장에서 다져진 감각으로 짐의 무게 중심을 한눈에 파악해 가장 효율적으로 쌓아 올리는 요령이 ...
    💬 skills_and_expertise_list    ['적재물 무게 중심 파악 및 효율적 배치', '현장 자재 결속 및 고정 기술', '하역 작업 동선 최적화' ...
    💬 hobbies_and_interests        주말이면 무등산 자락을 천천히 걸으며 땀을 빼고, 내려오는 길에 단골 목욕탕에서 뜨거운 물에 몸을 담그며 동 ...
    💬 hobbies_and_interests_list   ['무등산 둘레길 산책', '동네 대중사우나 이용', '전통시장 맛집 탐방', '트로트 프로그램 시청', ' ...
    💬 career_goals_and_ambitions   큰 욕심 없이 지금처럼 매일 아침 정해진 시간에 출근해 땀 흘려 일하며 건강을 유지하는 것에 만족합니다. 무 ...
    💬 sex                          남자
    💬 age                          74
    💬 marital_status               배우자있음
    💬 military_status              비현역
    💬 family_type                  배우자와 거주
    💬 housing_type                 아파트
    💬 education_level              초등학교
    💬 bachelors_field              해당없음
    💬 occupation                   하역 및 적재 관련 단순 종사원
    💬 district                     광주-서구
    💬 province                     광주
    💬 country                      대한민국

⏳ [user_preferences.csv] 파일을 확인하는 중...
✅ 6.5 KB · 100행 · 14칸

    💬 customer_id                  C001
    💬 건물유형                         빌라
    💬 거래형태                         월세
    💬 금액                           52
    💬 건축면적                         24
    💬 층수                           옥탑
    💬 준공년도                         최근 5년
    💬 녹지                           2
    💬 안전                           2
    💬 교통                           2
    💬 상권                           2
    💬 의료                           1
    💬 교육                           4
    💬 문화                           5
'''






