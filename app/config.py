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

