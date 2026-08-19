import sqlite3, statistics


import csv, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.config import DB_PATH

con = sqlite3.connect(DB_PATH)
for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    n = con.execute(f"SELECT COUNT(*) FROM {r[0]}").fetchone()[0]
    print(f"{r[0]:24s} {n:,}")
    
IND = ["녹지","안전","교통","상권","의료","교육","문화"]
rows = con.execute(f"SELECT {', '.join(IND)} FROM user_preferences").fetchall()
import statistics
print("교육 평균:", round(statistics.mean(r[5] for r in rows), 2))