import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

# parent 를 두 번 올라가야 프로젝트 뿌리다
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "life.db"

# .env 를 읽어 환경변수로 올린다
load_dotenv()                      # .env 를 읽어 환경변수로 올린다

API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not API_KEY:
    raise RuntimeError("API 키가 없다. .env 파일을 확인해라.")


MODEL = "claude-haiku-4-5-20251001"

# py -m pip install anthropic

# ── 임베딩 ────────────────────────────────────
# 저장할 때와 검색할 때 반드시 같은 모델을 써야 한다.
# 모델이 다르면 벡터 차원부터 달라서(e5-small 384, bge-m3 1024)
# 저장해 둔 벡터를 아예 못 쓴다
EMBED_MODEL = "intfloat/multilingual-e5-small"

# ── 추천 지표 ─────────────────────────────────
# user_preferences 의 칸 이름이자 08번 점수 계산의 기준.
# 순서가 바뀌면 위치로 값을 꺼내는 코드가 조용히 깨지므로 여기서만 관리한다
INDICATORS = ["녹지", "안전", "교통", "상권", "의료", "교육", "문화"]