from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent

# parent 를 두 번 올라가야 프로젝트 뿌리다
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "life.db"


# CLAUDE API 추가
# 키는 코드에 적지 않는다. 환경변수에서 읽는다
# 학원 PC 처럼 환경변수를 못 넣는 곳에서만 아래 줄에 임시로 키를 붙인다.
# ⚠️ 쓰고 나면 반드시 "" 로 되돌릴 것. 커밋되면 키가 영구히 노출된다
TEMP_KEY = ""
API_KEY = os.environ["ANTHROPIC_API_KEY"]

if not API_KEY:
    raise RuntimeError("API 키가 없다. 환경변수를 등록하거나 TEMP_KEY 에 임시로 넣어라.")

MODEL = "claude-haiku-4-5-20251001"

# py -m pip install anthropic

