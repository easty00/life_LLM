from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# parent 를 두 번 올라가야 프로젝트 뿌리다
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "life.db"

print(DATA_DIR)
print(DB_PATH)
