# [업데이트 단계 4] P0-4 전체 인덱싱 + P0-5 Top-3 검색

> 목표: `rag_docs/` **전체**를 자동 인덱싱(기존엔 1개 문서만)하고,
> 검색을 **Top-1 → Top-3 + 출처·점수 + 근거부족 처리**로 바꾼다.

---

## 1. P0-4 — 전체 문서 자동 인덱싱 (`rag/build_index.py`)

### 하는 일 (데이터 흐름)
```
rag_docs/**/*.md
   │  ① 전체 순회(glob)
   ▼
각 파일을 '## 소제목' 단위로 청킹 (질문 1개 = 청크 1개)
   │  ② 상단 meta 라인에서 category/source/version 파싱
   ▼
청크마다 {chunk_id, source_file, title, category, source, version, text}
   │  ③ 빈 청크·중복 청크 검출(있으면 제외 + 리포트)
   ▼
각 청크 text를 임베딩 → vector (gemini-embedding-001, 3072차원)
   │  ④ 하나라도 실패하면 중단(기존 vectors.json 유지)
   ▼
임시파일에 쓰고 검증 후 os.replace → rag/vectors.json  (전체 재생성)
   │  ⑤ 문서수/청크수/카테고리별/누락을 docs/rag_index_build_report.md 에 기록
```

### 핵심 설계 포인트
- **전체 재생성(full rebuild):** 같은 입력을 다시 돌려도 중복이 쌓이지 않음. `chunk_id = "경로::섹션번호"`로 안정적.
- **청킹은 정규식(`^#{2,3}\s`):** 특정 문자열 하나(`split("##")`)에만 의존하지 않도록. 제목(H1) 앞 서문은 청크에서 제외.
- **안전장치:** 임베딩 실패 시 `SystemExit`로 중단 → **미완성 인덱스를 서비스에 안 올림**. 임시파일→`os.replace` 원자적 교체.
- **키 없이 점검 가능:** `--report-only`는 임베딩 없이 청킹/집계만. (`load_chunks()`는 API 호출 안 함)

### 결과 (2026-11-12 report-only)
- 문서 15개 → 청크 **102개** / 성향별 52·상황별 24·성장목표 7·학부모소통 19
- 빈 청크 0 · 중복 0 · 메타누락 0 → `docs/rag_index_build_report.md`

---

## 2. P0-5 — Top-3 검색 + 출처 + 근거부족 (`rag/rag_service.py`)

### 바뀐 `rag_search(question, k=3)` 반환값
```python
{
  "hits": [ {chunk_id, source_file, title, category, score, text}, ... ],  # 점수 내림차순 (최대 k개)
  "best_score": 0.84,
  "low_relevance": False,   # best_score < RELEVANCE_MIN(0.70) 이면 True = 근거 부족
  "query": "...",
}
```
- 예전: 텍스트 **1개 문자열**만 반환(Top-1) → 지금: **청크·점수·출처 리스트**(Top-3).
- **다양성 제약:** 같은 `source_file`에서 최대 `MAX_PER_SOURCE(2)`개까지만 → 한 문서 쏠림 방지. 모자라면 보류분으로 채움.
- **근거 부족 처리:** 최고 유사도가 임계(0.70) 미만이면 `low_relevance=True`.

### 프롬프트 연결 (`prompt_service.py`)
- `format_rag_context()`가 Top-3를 `(근거1)[출처|제목|유사도] 본문` 형태로 나열 → 생성이 **어떤 근거를 썼는지 추적 가능**.
- `low_relevance`면 "확실한 근거 없는 지도 방법을 지어내지 말라"는 주의 문구를 프롬프트에 추가.
- 하위 호환: 예전처럼 문자열이 와도 그대로 처리.

### ⚠️ 유사도 ≠ 정답률
`RELEVANCE_MIN=0.70`은 **'유사도 바닥선'**일 뿐 정답률이 아니다. 실제로 맞는 문서를 찾았는지는
사람이 만든 정답셋으로 측정(P0-6).

---

## 3. 알아야 하는 명령어
```bash
# (키 불필요) 청킹/집계만 점검 — vectors.json 안 바꿈
python -m rag.build_index --report-only

# (키 필요, 102회 임베딩 호출) 실제 인덱스 재생성
docker compose exec api python -m rag.build_index
#   또는 로컬 .env의 키로:  python -m rag.build_index

# 테스트 (키 불필요: 가짜 데이터/임베딩)
python -m pytest tests/test_rag.py -v
```

## 4. 테스트 결과 (2026-11-12)
```
tests/test_rag.py::test_load_chunks_covers_all_docs          PASSED
tests/test_rag.py::test_chunk_ids_unique_and_text_nonempty   PASSED
tests/test_rag.py::test_top3_returns_three_sorted_hits       PASSED
tests/test_rag.py::test_diversity_limits_same_source         PASSED
tests/test_rag.py::test_low_relevance_flag_when_scores_low   PASSED
(그래프 6 + RAG 5 = 11 passed)
```

## 5. 구현 흐름 (내가 한 순서)
1. `rag/build_index.py` 작성 (순회→청킹→메타파싱→임베딩→원자적 저장→리포트).
2. `--report-only`로 청킹 검증(102청크, 빈/중복 0).
3. `rag/rag_service.py` `rag_search`를 Top-3 구조화 + 다양성 + 근거부족으로 교체(embed/cos_sim/data는 유지 — evaluate.py 호환).
4. `prompt_service.build_prompt`가 Top-3를 출처와 함께 넣도록 수정.
5. `tests/test_rag.py` 작성, 전체 pytest 통과.
6. (남음) 실제 임베딩으로 `vectors.json` 재생성 — 키 사용.

## 6. 한 줄 요약
> build_index가 문서 전체를 질문 단위로 쪼개 안전하게 인덱싱하고,
> rag_search는 출처·점수를 단 Top-3를 돌려주며 근거가 약하면 '지어내지 말라'고 신호를 준다.
