from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent

# parent 를 두 번 올라가야 프로젝트 뿌리다
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "life.db"


# CLAUDE API 추가
# 키는 코드에 적지 않는다. 환경변수에서 읽는다
API_KEY = os.environ["ANTHROPIC_API_KEY"]

MODEL = "claude-haiku-4-5-20251001"