"""검증 : LangChain 임베더가 기존 벡터와 같은 값을 내는가

kb_chunk 에 저장된 벡터는 SentenceTransformer 로 만들었다.
앞으로 검색은 HuggingFaceEmbeddings 로 한다.
같은 모델을 쓰므로 같아야 하지만, 확인 없이 넘어가면
검색 품질이 조용히 떨어져도 원인을 못 찾는다.
"""

import json

import numpy as np

from app.db import query
from app.llm import get_embedder, to_passage

SAMPLE = 5

rows = query(f"SELECT text, vector FROM kb_chunk LIMIT {SAMPLE}")

texts = [r[0] for r in rows]
stored = np.array([json.loads(r[1]) for r in rows], dtype="float32")

# 저장할 때와 똑같이 passage: 를 붙여서 다시 만든다
fresh = np.array(get_embedder().embed_documents([to_passage(t) for t in texts]),
                 dtype="float32")

print(f"저장된 벡터 {stored.shape} · 새로 만든 벡터 {fresh.shape}")
print()

for i in range(SAMPLE):
    # 둘 다 길이가 1이므로 곱하면 코사인 유사도가 나온다.
    # 완전히 같으면 1.0
    sim = float(stored[i] @ fresh[i])
    diff = float(np.abs(stored[i] - fresh[i]).max())
    print(f"  {i+1}번 유사도 {sim:.6f} · 최대 차이 {diff:.8f}")