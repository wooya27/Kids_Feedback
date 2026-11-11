# [업데이트 단계 1] P0-1 · 검증 실패한 AI 피드백은 저장하지 않기

> 목표: Gemini가 만든 피드백이 **깨진 JSON / 필수필드 누락 / 빈 값 / 타입 오류**면
> DB에 저장하지 않고, 재시도 한도를 넘으면 **명확한 실패(502)** 를 API로 돌려준다.
> 완료기준: 정상 입력은 저장, 잘못된 입력/최종 실패는 `feedbacks` 신규 행 **0건**.

---

## 1. 왜 필요했나 (AS-IS 문제)

- 기존 `graph/feedback_graph.py`: 2회 시도 후 실패해도 그냥 `END`로 나감 → 불량 결과가 그대로 통과.
- 기존 `routers/feedbacks_router.py`: `review_ok`를 **확인하지 않고** 바로 `db.add()` → 불량/누락 데이터가 DB에 저장됨.
- `generate` 노드의 `json.loads(result)`가 **예외를 그대로 터뜨려** 서버가 500으로 죽을 수 있었음.

---

## 2. 알아야 하는 핵심 코드

### (a) 출력 검증용 Pydantic 모델 — `schemas.py`
```python
from pydantic import BaseModel, field_validator

class FeedbackLLMOut(BaseModel):
    next_goal: str            # 타입이 str이 아니면 ValidationError (타입 오류 차단)
    teacher_feedback: str     # 필드가 없으면 ValidationError (누락 차단)
    parent_feedback: str

    @field_validator("next_goal", "teacher_feedback", "parent_feedback")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if v is None or not str(v).strip():      # 공백만/빈 문자열 차단
            raise ValueError("빈 문자열/공백만 있음")
        return str(v).strip()
```
- **포인트:** Pydantic v2는 `int → str` 자동 변환을 **안 해준다** → 숫자가 오면 타입 오류로 잡힘.
- `model_validate(dict)` 호출 시 위 규칙에 걸리면 `ValidationError` 발생.

### (b) 실패를 "구분해서" 기록하는 generate 노드 — `graph/feedback_graph.py`
```python
try:
    result = generate_feedback(prompt)          # LLM 호출
except Exception as e:
    return {..., "error_type": "llm_call_error"}  # 네트워크/쿼터 실패

try:
    parsed = json.loads(result)
except (json.JSONDecodeError, TypeError):
    return {..., "error_type": "json_parse_error"} # JSON 깨짐

try:
    validated = FeedbackLLMOut.model_validate(parsed)
except ValidationError as e:
    return {..., "error_type": "schema_validation_error"} # 누락/빈값/타입

feedback = validated.model_dump()               # 여기 도달 = 검증 통과
```
- 실패 시 **예외를 던지지 않고** `feedback=None`과 `error_type`을 state에 담아 반환 → 그래프가 재시도 분기를 탈 수 있게 함.
- 로그에는 **값이 아니라 "어떤 필드가 왜 틀렸는지"** 만 남긴다(개인정보 보호): `loc:type` 형태.

### (c) 저장 전 마지막 관문 — `routers/feedbacks_router.py`
```python
final = feedback_graph.invoke({...})
if final.get("review_ok") is not True:          # ★ 통과 못하면
    raise HTTPException(status_code=502, detail={ # 저장 안 하고 실패 반환
        "error": "feedback_generation_failed",
        "error_type": final.get("error_type"),
        "attempts": final.get("attempts"),
        "run_id": run_id,
    })
# 여기 아래로는 '검증 통과분'만 도달 → db.add(...)
```

---

## 3. 데이터 흐름 (요청 1건이 지나가는 길)

```
POST /feedbacks/generate {lesson_record_id}
      │
      ├─ (라우터) 수업기록 있나? 없으면 ──────────────▶ 404 (그래프 진입 전 차단)
      │
      ▼  feedback_graph.invoke(...)
  retrieve ─▶ generate ─▶ review ─▶ decide ┐
     │           │          │              │ review_ok=True ─▶ END
   DB조회     LLM호출     feedback가         │ 실패 & 시도<2  ─▶ retrieve (재시도)
   +RAG검색   +JSON파싱    존재하나?         │ 실패 & 시도≥2  ─▶ END (실패인 채)
             +스키마검증
      │
      ▼  (라우터) review_ok is True ?
         ├─ 예 ─▶ db.add + commit ─▶ 200 (저장된 피드백 반환)
         └─ 아니오 ─▶ 502 {error_type, attempts, run_id}  (DB 신규 행 0건)
```

실패 유형 3종: `json_parse_error` / `schema_validation_error` / `llm_call_error`

---

## 4. 구현 흐름 (내가 한 순서)

1. `schemas.py`에 `FeedbackLLMOut` 추가 (검증 규칙 정의).
2. `graph/feedback_graph.py` `generate` 노드를 try/except 3단으로 재작성 (호출→파싱→검증).
3. `review`/`decide`는 "feedback 존재 여부"로 최종 확정하도록 정리.
4. `routers/feedbacks_router.py`에 `review_ok is not True → 502` 관문 추가 (저장 차단).
5. `tests/`에 SQLite + LLM Mock 기반 회귀 테스트 6개 작성.
6. `pytest` 통과 확인.

---

## 5. 알아야 하는 명령어

```bash
# 로컬(도커 없이) 테스트 실행 — SQLite + 가짜 LLM이라 API 키 불필요
python -m pytest tests/test_feedback_graph.py -v

# 전체 테스트
python -m pytest -q

# (실제 환경 확인용) 도커로 띄운 뒤 수동 확인
docker compose up -d --build
curl -X POST http://localhost:8001/feedbacks/generate -H "Content-Type: application/json" -d "{\"lesson_record_id\": 1}"
```

### 테스트가 "진짜 Gemini 없이" 도는 원리 (중요)
- `tests/conftest.py`: PostgreSQL 대신 **메모리 SQLite**, `get_db`를 테스트 세션으로 **교체(override)**.
- `monkeypatch.setattr(graph.feedback_graph, "generate_feedback", 가짜함수)` 로 LLM 응답을 **내가 원하는 값**으로 조종.
- 패치 대상이 `llm_service`가 아니라 `graph.feedback_graph`인 이유: 그 모듈이 `from llm_service import generate_feedback`로 **이름을 자기 쪽으로 가져왔기** 때문. (import 바인딩 개념)

---

## 6. 테스트 결과 (2026-11-12 실행)

```
tests/test_feedback_graph.py::test_valid_feedback_is_saved            PASSED
tests/test_feedback_graph.py::test_bad_json_is_not_saved              PASSED
tests/test_feedback_graph.py::test_missing_field_is_not_saved         PASSED
tests/test_feedback_graph.py::test_blank_field_is_not_saved           PASSED
tests/test_feedback_graph.py::test_retry_then_success_is_saved        PASSED
tests/test_feedback_graph.py::test_missing_lesson_record_returns_404  PASSED
6 passed
```

## 7. 한 줄 요약
> LLM 출력은 `json.loads → Pydantic 검증` 2단 관문을 통과해야만 하고,
> 라우터는 `review_ok is True`일 때만 저장한다. 실패는 502로 분류해 돌려주고 DB는 건드리지 않는다.
