# [업데이트 단계 8] P1-4 테스트 자동화 마무리 + P2 문서/보안

---

## 1. P1-4 — 회귀 테스트 전체 (22개, 키 불필요)

| 파일 | 수 | 검증 내용 |
|---|---:|---|
| `tests/test_feedback_graph.py` | 6 | 정상 저장 / 깨진JSON·필드누락·빈값 **미저장(502)** / 재시도 성공 / 404 |
| `tests/test_rag.py` | 5 | 전체 청킹(빈·중복 0) / chunk_id 유일 / Top-3 정렬·다양성 / 근거없음 플래그 |
| `tests/test_feedback_api.py` | 9 | 검수 수정본 저장·원본보존 / 최종본 전달차단(409) / 상태전이 / **학생별 격리** |
| `tests/test_webhook.py` | 2 | n8n 동적 ID 표현식 / 검증 노드·배선 |

- **외부 LLM/Embedding은 Mock/Fake로 대체**(단위 테스트). 실제 외부호출 E2E는 도커에서 별도.
- 실행: `python -m pytest -q` → **22 passed**.

### 테스트가 키 없이 도는 3가지 장치
1. **SQLite 인메모리** + `get_db` override (PostgreSQL 불필요).
2. `monkeypatch`로 `generate_feedback`·`rag_search`·`embed_feedback`·`data`를 가짜로 교체.
3. n8n/워크플로는 **JSON 구조 정적 검증**(실행 없이).

---

## 2. P2 — 문서·보안·데모

### P2-2 README (`README.md`)
문제정의 / AS-IS·TO-BE / 아키텍처(실제) / ERD / 핵심 API / 실행법 / `.env.example` / RAG 설계 / 테스트·평가 / **한계** / 보안 / 데모.
- **구현됨 vs 계획**을 구분, 성과 수치는 '측정 예정'으로 둠.
- `render.yaml`은 배포 설정일 뿐 → 동작 검증된 공개 URL만 기재한다고 명시.

### P2-3 보안·개인정보
- 합성 데이터만 사용, `.env`는 gitignore, 로그에 개인정보 미기록.
- **인증·접근 제어 미구현**을 한계로 명시(공개 데모 전 보완).
- 지도 문서 = 참고자료(검증 전)임을 명확화.

### P2-1 데모 (`docs/demo_checklist.md`)
개인화 비교 / n8n 동적 ID 2건 / 검증실패 미저장 / 검수 원본→수정→최종. (실제 캡처는 도커 실행 후)

---

## 3. 전체 산출물 지도 (이번 업데이트)
```
rag_docs/            15개 문서(메타 라인 포함)
rag/build_index.py   전체 인덱서(+--report-only)
rag/rag_service.py   Top-3 검색(출처·점수·근거부족)
prompt_service.py    Top-3 근거 주입
graph/feedback_graph.py  생성 3단 검증(파싱→스키마→리뷰)
routers/feedbacks_router.py  저장 차단 + 검수 수정본 + /final 게이트
models.py/schemas.py edited_* 컬럼
evals/   rag_questions.json(48) · evaluate_retrieval.py · compare_rag_variants.py
docs/    rag_documents_index · rag_index_build_report · rag_evaluation · rag_quality_comparison · demo_checklist
tests/   22개 (graph/rag/api/webhook)
evaluate.py  지표명 정정 + p50/p95
README.md    포트폴리오 문서
```

## 4. 남은 '키 필요' 실행 (도커에서 한 번에)
```bash
docker compose up -d --build
docker compose exec api python -m rag.build_index            # 실제 인덱스
docker compose exec api python -m evals.evaluate_retrieval   # Hit@1/@3
docker compose exec api python -m evals.compare_rag_variants # 전/후 비교
docker compose exec api python seed_eval.py && docker compose exec api python evaluate.py  # 35회 지표
```
→ 실행 후 나온 수치를 `docs/rag_evaluation.md`·`README.md`·포트폴리오에 **실측값으로** 채운다.

## 5. 한 줄 요약
> 핵심 회귀 22개를 키 없이 재현 가능하게 묶고, README·보안·데모 가이드로 '구현된 것'과 '측정/캡처 예정'을 정직하게 분리했다.
