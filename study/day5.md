# Day 5 — 피드백 생성 API + LLM 결과 DB 저장

> 작성 중 (2026-07-01). 세션 끝날 때마다 채워 넣는 중.

---

## 📌 나중에 다시 설명 들을 것 (지금은 넘어감)

### `json.load` vs `json.loads` 차이 ✅ 복습 완료 (2026-07-08, 아래 "복습 세션" 참고)
- **한 줄 직관:** `loads` = "load **s**tring" → 문자열(string)을 읽을 때. s가 문자열 표시.
- `json.load(파일)` : **파일**을 열어서 읽을 때 (파일 객체를 넘김)
- `json.loads(문자열)` : **문자열**을 읽을 때 (그냥 텍스트를 넘김)
- 우리 상황: `result`는 LLM이 돌려준 **문자열**이니까 → `json.loads(result)` 를 씀.
- 하는 일: `'{"next_goal": "..."}'` (문자열) → `{"next_goal": "..."}` (파이썬 딕셔너리)로 바꿔줌.
  → 그래야 `data["next_goal"]` 처럼 값을 꺼낼 수 있음.
- ❓ 왜 문자열/파일을 구분하는지, 반대(딕셔너리→문자열)는 `json.dumps`인 것 → **다음 복습 때 다시 설명**.

---

## 오늘 배운 핵심 개념 (세션 1 완료 — Day 5 ③)

### 1. LLM 결과를 DB에 저장하는 흐름
```python
data = json.loads(result)          # 문자열 → 딕셔너리
new_feedback = Feedback(           # 딕셔너리 값으로 "선반 규격 상자" 만들기
    child_id=child.id,
    lesson_record_id=record.id,
    next_goal=data["next_goal"],
    teacher_feedback=data["teacher_feedback"],
    parent_feedback=data["parent_feedback"],
)
db.add(new_feedback); db.commit(); db.refresh(new_feedback)   # 저장 3종 세트
return new_feedback
```
- `data["key"]`의 key는 딕셔너리에 **실제로 있는 이름과 글자까지 똑같아야** 함 (틀리면 `KeyError`). key 이름은 프롬프트에서 지정한 JSON 형식(`next_goal` 등) 그대로.

### 2. `FeedbackResponse` 스키마 (돌려줄 데이터 모양)
- 기준 = models.py의 `Feedback` 테이블 칸들. 돌려줄 것: id/child_id/lesson_record_id/next_goal/teacher/parent/created_at.
- `class Config: from_attributes = True` 필요 → **DB 객체(`.점`으로 읽음)를 Pydantic이 읽을 수 있게 허락**. 없으면 에러. (Pydantic v1 `orm_mode` → v2 `from_attributes`, Day 3에서 만난 거)
- **들여쓰기 규칙:** 왼쪽 끝 = 독립 클래스(형제) / 안으로 들여쓰면 = 바깥 것의 부품(자식). `Config`는 Response 안(자식), 두 스키마는 서로 남남(형제).

### 3. `List[...]` 응답
- `.all()`은 여러 개(리스트) → `response_model=List[FeedbackResponse]`로 감싸야 함. `from typing import List` 필요.

### 4. 404 예외처리 `HTTPException`
```python
from fastapi import HTTPException
if record is None:                 # .first()는 못 찾으면 None
    raise HTTPException(status_code=404, detail="...")
if not feedbacks:                  # 빈 리스트 []는 not이 True
    raise HTTPException(status_code=404, detail="...")
```
- `raise` = 에러를 일부러 발생. `404` = 표준 "없음" 신호. 없는 ID로 크래시(500) 나기 전에 깔끔히 막음.

### 5. Swagger 200 vs 422 헷갈림 (해결)
- 위쪽 **"Server response"의 Code** = 진짜 결과 / 아래쪽 **"Responses" 표** = 그냥 "이럴 수도 있어요" 문서.
- path에 값 받는 API엔 FastAPI가 자동으로 422 설명을 붙임 → 실제로 난 에러 아님.

---

## 🧠 복습 세션 (2026-07-08) — 파고들어서 확실히 잡은 것들

> 방식: 안 보고 떠올리기 → 확인 → 질문 → 한 줄 설명. 아래는 그때 헷갈렸다가 정리한 내용.

### ① `json.loads`는 "딕셔너리"가 아니라 "바꿔주는 도구(함수)"
헷갈렸던 점: `json.loads` 자체가 딕셔너리인 줄 앎. → ❌
- **믹서기 비유**로 정리:
  - `json.loads` = **믹서기** (도구/함수)
  - `result` = **사과** (넣는 재료 = 문자열)
  - `data` = **사과주스** (나온 결과물 = 딕셔너리)
- 즉 `data = json.loads(result)` 에서 **딕셔너리는 `data`**지, `json.loads`가 아님.

| 이름 | 정체 |
|---|---|
| `result` | 문자열 (재료) |
| `json.loads` | 함수/도구 (믹서기) |
| `data` | 딕셔너리 (결과물) |

### ② 문자열 vs 딕셔너리 차이 (제일 헷갈렸던 것)
- **문자열** = 글자 덩어리 하나. 앞뒤 **따옴표(`'...'`)로 감싸져 있음.** 겉이 딕셔너리처럼 생겨도 컴퓨터는 그냥 "글자 나열"로만 봄 → 값 못 꺼냄.
- **딕셔너리** = "이름(key) → 값(value)" 서랍장. `{}`로 만들고 따옴표로 안 감쌈 → `data["key"]`로 값 꺼냄.

```python
A = '{"name": "유리"}'   # 문자열 (따옴표로 감쌈)  → A["name"] ❌ 에러
B = {"name": "유리"}     # 딕셔너리               → B["name"] ✅ "유리"
```
- **핵심:** Gemini가 준 건 "종이에 적힌 글(문자열)"이라, 서랍장(딕셔너리)으로 바꿔야(`json.loads`) 값을 꺼냄.
- 왜 바꿔야 DB에 넣나? → DB 테이블은 **칸(컬럼)이 나눠져 있어서**, 통짜 문자열 말고 **칸별로 나눠진 값**이 필요. `data["next_goal"]`처럼 칸별로 꺼내 각 컬럼에 넣음.

### ③ `HTTPException` 404를 "일부러" 던지는 진짜 이유
헷갈렸던 점: "오류가 잘 뜨는지 확인하려고" 던진 줄 앎. → ❌ (그건 결과 확인일 뿐)
- 진짜 이유 2가지:
  1. **터짐 방지** — 못 찾으면 결과가 `None`. 그냥 두면 `None.name`처럼 진행하다 **500으로 꽝**. 그 전에 미리 막음.
  2. **깔끔한 안내** — 손님한테 "그런 아이 **없습니다(404)**"라고 정확히 알려줌.
- `404` = 웹 공용어 "Not Found(못 찾음)". (인터넷 "404 페이지 없음"이 그거)

### ④ "터진다"의 진짜 의미 (500 에러) — 서버가 죽는 게 아님!
헷갈렸던 점: 터지면 서버 다시 구축/못 씀? → ❌ 전혀 아님.
- 서버는 요청을 **하나씩 따로** 처리 → 500 나도 **그 요청 1개만 실패**, 서버는 계속 살아있음. 재시작 필요 없음.
- 식당 비유: 주문 하나 잘못돼도 식당은 계속 영업. 다음 주문은 정상.

### ⑤ 404 vs 500 차이 (둘 다 "요청 1개 실패"인데 뭐가 달라?)
| | **404** | **500** |
|---|---|---|
| 성격 | **일부러** 던짐 (계획된 실패) | 예상 못 하고 **터짐** (사고) |
| 원인 | 없는 걸 찾음 (정상 상황) | 코드가 엉뚱한 데서 꽝 (`None.name`) |
| 손님이 이유 앎? | ✅ "아이 없음" 알려줌 | ❌ "그냥 서버 오류"만 뜸 |
| 내부 노출 | 안전 (메시지 내가 정함) | 위험 (에러 내용 샐 수 있음) |
| 비유 | "그 메뉴 품절이에요" 🙂 | 주방에 불남 🔥 |

- **숫자 규칙:** `4xx` = 손님(요청) 잘못 / `5xx` = 서버 잘못.
- **예외처리 핵심 한 줄:** 500으로 터질 상황을 미리 잡아서 → **404라는 깔끔한 실패로 바꿔주는 것.**
