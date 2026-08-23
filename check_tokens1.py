"""검증 : 우리 청크 중 임베딩 상한을 넘는 게 있나"""

import statistics
from transformers import AutoTokenizer, logging as hf_logging
hf_logging.set_verbosity_error()

from core.config import DATA_DIR, EMBED_MODEL
from core.io import read_csv

MAX_TOKENS = 512
tok = AutoTokenizer.from_pretrained(EMBED_MODEL)

_, rows = read_csv(DATA_DIR / "kb_chunk.csv")

# "passage: " 접두사도 토큰을 먹으므로 붙여서 센다
counts = [len(tok.encode(f"passage: {r['text']}")) for r in rows]
over = [n for n in counts if n > MAX_TOKENS]

print(f"청크 {len(counts):,}개")
print(f"토큰 최소 {min(counts)} / 중앙 {int(statistics.median(counts))} / 최대 {max(counts)}")
print(f"상한 초과: {len(over)}개 ({len(over)/len(counts)*100:.1f}%)")