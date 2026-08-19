## 실행 순서

1. schema.py       CSV → life.db
2. sample_kb.py    18.5만 → 2,500명
3. chunk_kb.py     → 22,500청크
4. embed_kb.py     → 벡터 저장 (5분)
5. embed_member.py 회원 100명 벡터
6. weights.py      검색어 → 가중치
7. recommend.py    가중치 → TOP 5
8. explain.py      → 설명문