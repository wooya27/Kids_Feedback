# [업데이트 단계 7] P1-2 평가지표 이름 바로잡기 + P1-3 Human Review 수정본 저장

---

## 1. P1-2 — `evaluate.py` 지표 정직하게 고치기

### 바뀐 점
- `rag_search_success_rate` → **`similarity_threshold_pass_rate`** 로 이름 변경.
  - 이유: 그 수치는 '정답률'이 아니라 **유사도 임계값(0.70) 통과율**이다. 실제 정답률은 정답셋 기반 Hit@k(`evals/`)로 따로 측정.
  - `..._note` 필드로 "정답률 아님"을 결과 파일에 명시.
- `human_review_simulated: True` + `human_review_note`로 **규칙 기반 시뮬레이션**임을 결과·포트폴리오에 표기.
- 응답시간: 평균뿐 아니라 **중앙값(median)·p95** 추가.
- 한 요청이 실패해도 **전체 평가가 멈추지 않도록** try/except로 감싸고 실패도 기록.

### 데이터 흐름
```
seed_eval.py(테스트DB에 합성 8명/21기록 TRUNCATE 후 시딩)
   ▼
evaluate.py: 유효 21 + 반복 9 + 잘못된 ID 5 = 35회 /feedbacks/generate 호출
   ▼
지표 계산 → metrics.json (api_e2e, json_format, similarity_threshold_pass,
                          avg/median/p95 응답시간, 시뮬레이션 검수율, 에러처리율)
```
> ⚠️ `seed_eval.py`는 `TRUNCATE`를 실행한다 → **격리된 테스트 DB에서만** 실행. 실사용 DB 금지.

---

## 2. P1-3 — Human Review에서 수정 본문 저장 (원본 보존 + 전달 차단)

### 스키마 변경 (`models.py`)
```
# AI 원본(보존): next_goal / teacher_feedback / parent_feedback
# 강사 수정본(별도): edited_next_goal / edited_teacher_feedback / edited_parent_feedback
```
- 원본은 **절대 덮어쓰지 않는다**. 수정본은 edited_* 컬럼에 따로 저장.
- 마이그레이션: `api/main.py`의 `_ensure_review_columns()`에 `ADD COLUMN IF NOT EXISTS edited_*` 추가.

### 상태 전이 검사 (`routers/feedbacks_router.py`)
```python
ALLOWED_TRANSITIONS = {
  "pending":  {"approved","edited","rejected"},
  "edited":   {"approved","edited","rejected"},
  "approved": set(),   # 확정 → 재검수 잠금
  "rejected": set(),
}
```
- 확정(approved/rejected)된 건 다시 바꾸면 **409**.
- `edited`인데 수정 본문이 하나도 없으면 **400**.

### 최종본 전달 차단 (`GET /feedbacks/{id}/final`)
- `approved` → 원본을 최종본으로
- `edited` → 수정본을 최종본으로
- `pending`/`rejected` → **409 (전달 불가)** ← 승인 전 학부모 전달 차단
- 원본·수정본·최종본을 **서로 다른 값으로 조회 가능**.

### 데이터 흐름 (검수)
```
생성 → review_status=pending (최종본 전달 차단)
   │ PATCH /feedbacks/{id}/review
   ├─ approved : 원본이 최종본
   ├─ edited   : edited_* 저장(원본 보존), 수정본이 최종본
   └─ rejected : 폐기, 최종본 없음
   ▼ GET /feedbacks/{id}/final → 승인/수정만 최종본 반환
```

---

## 3. 테스트 (로컬, 키 불필요)
```
tests/test_feedback_api.py (8개):
  edited 저장+원본보존 / final=edited / final=원본(approved) /
  pending·rejected 전달차단(409) / approved후 잠금(409) /
  edited 본문없음(400) / 잘못된 상태(400)
→ 전체 19 passed (graph6 + rag5 + api8)
```
```bash
python -m pytest tests/test_feedback_api.py -v
```

## 4. 실행 명령어 (P1-2는 키 필요 — 도커)
```bash
docker compose exec api python seed_eval.py      # 테스트DB에만!
docker compose exec api python evaluate.py        # metrics.json 생성
```

## 5. 구현 흐름
1. `models.py`에 edited_* 3컬럼 추가.
2. `schemas.py` 입력/응답에 edited_* 반영.
3. 라우터: 상태 전이 검사 + edited 저장 + `/final` 게이트 추가.
4. `api/main.py` 마이그레이션에 컬럼 추가.
5. `evaluate.py` 지표 이름/주석/통계 보강.
6. 테스트 8개 작성, 전체 통과.

## 6. 한 줄 요약
> 원본은 보존하고 수정본은 edited_*에 따로 저장하며, 승인 전에는 /final이 409로 전달을 막는다.
> 평가 지표는 '유사도 통과율'과 '시뮬레이션 검수'임을 이름·주석으로 정직하게 표기했다.
