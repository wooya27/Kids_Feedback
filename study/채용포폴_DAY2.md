# 채용 포트폴리오 플랜 (v2) — DAY 2 학습문서

> 기준 문서: `plan/Kids_Feedback_채용포트폴리오_업데이트_v2.md`
> DAY 2 목표: **어제 만든 직선 흐름을 `검색 → 생성 → 검토` 단계로 나누고, 조건 분기를 한 번 경험한다.**

---

## 🧭 DAY 2 안에서 지금 위치

| 작업 | 내용 | 상태 |
|---|---|---|
| 작업 1 | LangGraph 최소 구조 (START→retrieve→generate→END) | ✅ 완료 |
| **작업 2** | **review Node + 조건 분기(Conditional Edge) 1개** | ✅ **이번에 완료** |
| **작업 3** | **Logging + run_id + 일부러 오류 내보기** | ✅ **이번에 완료** |

---

## 📋 중간보고서 — DAY 2 작업 1

### 무엇을 했나
처음 쓰는 **LangGraph**로, 처리 단계를 블록(Node)으로 쪼개고 데이터 가방(State)으로 이어 흐르게 하는 **최소 뼈대**를 만들었다.

### 만든 파일
```
graph/
├─ __init__.py          # 패키지 표시 (빈 파일, 보일러플레이트)
└─ feedback_graph.py     # ← 오늘 만든 것
```

### 구조
```
START → retrieve(가방에 rag_context 채움) → generate(가방에 feedback 채움) → END
```

### 실행 결과 (성공)
```
retrieve 실행 - lesson_record_id: 1
generate 실행 - rag_context: 임시 지도 기준 ...   ← retrieve가 채운 값을 generate가 읽음(=State 전달 성공)
최종 가방: {'lesson_record_id': 1, 'rag_context': '...', 'feedback': '...'}
```

### 완료 기준 체크
- [x] `feedback_graph.py` 생성
- [x] State 정의 (TypedDict 5칸)
- [x] `retrieve` / `generate` Node 생성
- [x] `START → retrieve → generate → END` 연결 + 실행 성공
- [ ] (다음 작업) review Node + Conditional Edge

> ⚠️ 지금 retrieve/generate는 **가짜 값**을 넣는 연습용. 진짜 DB/RAG/LLM 연결은 다음 작업에서.

---

## ⌨️ 꼭 알아야 하는 명령어

```powershell
# langgraph 설치 (이번에 함) — pip로 venv에 직접
.venv\Scripts\python.exe -m pip install langgraph

# tenacity 충돌 해결: google-genai가 tenacity<9.2.0 요구 → 낮춤
.venv\Scripts\python.exe -m pip install "tenacity<9.2.0"

# 그래프 실행 (PowerShell, 루트에서)
cd C:\Users\USER\GITHUB\Kids_Feedback
$env:PYTHONIOENCODING="utf-8"
.venv\Scripts\python.exe graph\feedback_graph.py
```

- 💡 함정: `uv add langgraph` 가 **파일 잠김(os error 5)** 으로 실패 → 켜둔 서버/다른 프로세스가 venv 파일을 쥐고 있을 때 발생. 서버 끄거나 `pip install`로 우회.
- 💡 함정: langgraph가 `tenacity`를 최신으로 올려 `google-genai`와 충돌 → **버전 핀 고정**으로 해결(`tenacity<9.2.0`).

---

## 💻 꼭 알아야 하는 코드

### 1) State = TypedDict (데이터 가방 이름표)
```python
from typing import TypedDict, Optional
class FeedbackState(TypedDict):
    lesson_record_id: int
    rag_context: Optional[str]   # 아직 안 채워졌으면 None일 수 있음 → Optional
```

### 2) Node = state 받아 "바꿀 칸만" dict로 반환
```python
def retrieve(state: FeedbackState) -> dict:
    return {"rag_context": "..."}   # 가방 전체가 아니라 바꿀 칸만! LangGraph가 합쳐줌
```

### 3) 조립 = 등록 → 화살표 → compile → invoke
```python
from langgraph.graph import StateGraph, START, END
builder = StateGraph(FeedbackState)
builder.add_node("retrieve", retrieve)
builder.add_node("generate", generate)
builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", END)
graph = builder.compile()
graph.invoke({"lesson_record_id": 1})   # 가방에 입력만 넣고 출발
```

---

## 🧠 꼭 알아야 하는 개념

| 개념 | 한 줄 정의 | 비유 |
|---|---|---|
| **State** | 단계 사이에서 들고 다니는 데이터 가방 | 택배 상자 (각 단계가 내용물 추가) |
| **Node** | 실제 작업 한 덩어리(함수). state 받아 바꿀 칸만 반환 | 공장 작업대 1개 |
| **Edge** | "이 작업 끝나면 다음은 저기" 화살표 | 컨베이어 벨트 |
| **START / END** | 그래프의 시작점 / 끝점 (예약어) | 입구 / 출구 |
| **compile()** | 등록·연결한 설계도를 실행 가능한 그래프로 굳힘 | 공장 가동 버튼 |
| **invoke(입력)** | 가방에 입력 넣고 START부터 실행 | 상자 올리고 벨트 켜기 |
| **TypedDict** | dict인데 "어떤 키가 들어갈지" 이름표를 미리 붙인 것 | 칸 이름 적힌 서랍 |

> **왜 LangGraph를 쓰나 (면접 한 줄):** 직선 흐름은 함수 하나로 충분하지만,
> "결과가 이상하면 다시 검색" 같은 **분기/반복**이 생기면 `if` 떡칠로 엉킨다.
> 단계를 Node로 쪼개고 State로 넘기면 **분기를 edge로 깔끔히 관리**할 수 있다. (다음 작업에서 조건 분기 실습)

---

## 🎤 30초 설명 (코드 닫고 말하기)
> LangGraph는 AI 처리 단계를 Node(작업대)로 나누고, State(데이터 가방)에 담아 다음 단계로 전달하는 도구다.
> 오늘은 RAG 검색(retrieve)과 LLM 생성(generate)을 각각 Node로 나누고 START→retrieve→generate→END로 연결했다.
> generate가 retrieve가 채운 rag_context를 읽은 것이 State 전달이 됐다는 증거다.

---

# 📋 중간보고서 — DAY 2 작업 2 (review + 조건 분기)

### 무엇을 했나
`review` Node를 추가하고, 결과 품질에 따라 **그래프가 스스로 경로를 바꾸는 Conditional Edge(조건 분기)** 를 1개 넣었다.

### 구조
```
START → retrieve → generate → review → decide ─┬─ "end"   → END
                                   ▲            └─ "retry" → retrieve (되돌아감)
                                   │
              (1차 생성이 필수필드 누락 → retry로 다시 돎)
```

### 실행 결과 (분기 실제 작동)
```
retrieve → generate(attempt 1) → review False (parent_feedback 없음)  → retry
retrieve → generate(attempt 2) → review True  (3필드 다 참)           → end → END
```
→ **결과를 보고 "다시 돌아가"를 스스로 선택**했고, 2차엔 통과해 무한루프 없이 종료.

### 완료 기준 체크
- [x] `review` Node 추가
- [x] 정상/실패 상태값 (`review_ok`) 추가
- [x] Conditional Edge 1개 연결
- [x] 입력으로 END까지 이동 확인 (retry 1회 후 END)

---

## 💻 꼭 알아야 하는 코드 (작업 2 — Conditional Edge)

```python
# 1) 판단 함수: state를 보고 "라벨"(문자열)을 돌려준다
def decide(state) -> str:
    return "end" if state.get("review_ok") else "retry"

# 2) 조건 분기 등록: 라벨 → 갈 곳 지도
builder.add_conditional_edges(
    "review",                           # 이 노드 다음에
    decide,                             # 이 함수로 판단해서
    {"end": END, "retry": "retrieve"},  # 돌려준 라벨로 경로 선택
)
```

- 무한루프 방지: `attempts` 카운터로 2차엔 통과하게 설계 (실무에선 "최대 N회 재시도" 가드).
- `all(key in fb for key in REQUIRED)` = 필수 필드 3개가 전부 있는지 한 줄 체크.

## 🧠 꼭 알아야 하는 개념 (작업 2)

| 개념 | 한 줄 정의 |
|---|---|
| **Conditional Edge** | 고정된 A→B가 아니라, **상태를 보고 다음 노드를 고르는** 갈림길 |
| **판단 함수(라우터)** | state를 받아 "어디로 갈지" 라벨(문자열)을 돌려주는 함수 |
| **라벨 → 노드 지도** | `{"end": END, "retry": "retrieve"}` 처럼 라벨을 실제 목적지에 연결 |
| **자동 검증(최소 품질)** | 완벽 평가가 아니라 "필수 필드 존재?" 같은 **통과/탈락 체크** |
| **retry 가드** | 되돌아가는 분기는 **반드시 종료 조건**(횟수/성공)이 있어야 무한루프 안 남 |

> **일반 Workflow vs Agent식 흐름 (면접 한 줄):** Workflow는 정해진 순서대로만 가고,
> Agent식은 **현재 결과를 보고 다음 행동을 바꾼다.** 여기선 피드백이 품질 조건을 통과하면 저장(END),
> 아니면 다시 검색(retrieve)하도록 분기를 만들었다. (= TO-BE 흐름의 "LangGraph 검토" 단계)

## 🎤 30초 설명 (작업 2)
> review 노드가 생성된 피드백이 필수 필드를 갖췄는지 검사하고, decide 함수가 그 결과로 "end/retry" 라벨을 돌려준다.
> Conditional Edge가 그 라벨대로 END로 보내거나 retrieve로 되돌린다. 1차 불량 → 재시도 → 2차 통과로 흐름이 실제로 갈라지는 걸 확인했다.

---

# 📋 중간보고서 — DAY 2 작업 3 (Logging + run_id)

### 무엇을 했나
실제 요청이 도는 라우터(`/feedbacks/generate`)에 **단계별 로그 + run_id(요청 꼬리표)** 를 넣고, 일부러 없는 ID를 보내 **"어디서 멈췄나"** 를 로그로 확인했다.

### 고친 파일
- `api/main.py` — `logging.basicConfig(...)` 로 로그 기본 설정(시간·레벨·메시지)
- `routers/feedbacks_router.py` — `run_id` 생성 + 단계마다 `logger.info(...)` + 총 응답시간 측정

### 로그 위치 (요청 흐름 그대로)
```
feedback request received  →  lesson record loaded  →  child loaded
→  RAG search completed  →  LLM generation completed  →  feedback saved (elapsed)
```

### 실행 결과 (run_id로 2개 요청 분리 추적)
```
[4f2fcd6e] request received(id=1) → ... → feedback saved - id=7, elapsed=13.82s   (정상)
[ca304e0f] request received(id=999999) → ⚠️ STOPPED at DB lookup → 404            (실패)
```
- 👉 **실제 수치 확보:** 응답시간 13.82s, 그중 RAG완료→LLM완료가 ~13s → **병목 = LLM** (로그로 증명).
- 👉 실패 요청은 **DB 조회 단계에서 멈춤**이 WARNING으로 즉시 보임.

### 완료 기준 체크
- [x] 정상 요청 로그 확인 (6단계 + run_id + elapsed)
- [x] 없는 수업기록 요청 → 404
- [x] 어느 단계에서 멈췄는지 로그로 설명 가능 (STOPPED at DB lookup)

---

## ⌨️ 꼭 알아야 하는 명령어 (작업 3)
```powershell
# 로그를 파일로 받으며 서버 실행 → 요청 보낸 뒤 로그 확인
.venv\Scripts\python.exe -m uvicorn api.main:app --port 8002 > srv.log 2>&1
# (다른 창에서) 요청: /docs 또는 curl 로 정상 id=1, 없는 id=999999 두 번
```

## 💻 꼭 알아야 하는 코드 (작업 3)
```python
import logging, uuid, time
logger = logging.getLogger("feedbacks")          # 이 파일 전용 로거

run_id = uuid.uuid4().hex[:8]                     # 요청마다 고유 꼬리표 8자리
started = time.perf_counter()                     # 시간 재기 시작
logger.info("[%s] feedback request received - lesson_record_id=%s", run_id, payload.lesson_record_id)
...
logger.warning("[%s] STOPPED at DB lookup - lesson record not found", run_id)   # 멈춘 지점 기록
...
elapsed = time.perf_counter() - started           # 총 걸린 시간(초)
logger.info("[%s] feedback saved - id=%s, elapsed=%.2fs", run_id, new_feedback.id, elapsed)
```
- `logging.basicConfig(level=INFO, format=...)` 는 **앱 시작점(api/main.py)에 한 번만**. 각 파일은 `getLogger(이름)`.
- `logger.info("... %s ...", 값)` 처럼 **`%s` + 값**으로 넘겨라 (문자열을 미리 합치지 말 것 — 성능·안전).

## 🧠 꼭 알아야 하는 개념 (작업 3)
| 개념 | 한 줄 정의 | 왜 AX·DX 포폴에 중요 |
|---|---|---|
| **run_id** | 요청 하나를 처음~끝까지 묶는 고유 꼬리표 | 여러 요청 섞여도 "이 요청"만 추적 → 운영 신뢰성 |
| **단계별 로그** | 각 처리 단계 통과를 기록 | "안 돼요"가 아니라 "어디서 멈춤"을 말함 |
| **error_stage** | 실패가 발생한 단계 이름 | 실패 단계별 건수 = 평가 지표 |
| **elapsed(응답시간)** | 요청 처리에 걸린 시간 | 평균 응답시간 지표 + 병목(LLM) 근거 |
| **print vs logging** | logging은 레벨(INFO/WARNING)·시간·출처가 붙는 "운영용 기록" | 실무는 print 아니라 logging |

## 🎤 30초 설명 (작업 3)
> 각 요청에 run_id를 붙이고 단계마다 로그를 남겨, 정상 요청은 6단계가 다 찍히고 총 13.82초가 걸린 걸 확인했다.
> 없는 ID를 보내면 DB 조회 단계에서 WARNING을 남기고 404로 멈춘다 — 어디서 실패했는지 로그로 바로 보인다.

---

---

## ✅ 라이브 통합 완료 (처음엔 데모였다가 실제 API에 연결)
처음 만들 땐 `feedback_graph.py`가 **가짜 값 데모**였고 실제 `/feedbacks/generate`는 라우터의 직선 코드로 돌았다.
그 뒤 **노드를 진짜 작업(DB·RAG·LLM·review)으로 바꾸고, 라우터가 `graph.invoke(...)`를 호출**하도록 교체했다.
이제 실제 요청이 retrieve→generate→review(조건분기)를 **진짜로 통과**한다 (로그의 `review - 필수필드 통과? / LangGraph completed`가 증거).
- State에 `db`, `run_id`를 실어 노드가 조회·로그 가능하게 함
- 404(없는 ID)는 라우터에서 먼저 처리 후 그래프 호출
- review 실패 시 최대 2회 재시도 가드(`MAX_ATTEMPTS`)
- 파일: `graph/feedback_graph.py`(진짜 노드), `routers/feedbacks_router.py`(graph 호출)

## 🔗 관련
- 포트폴리오 확장(마감단계): review_status(pending/approved/edited/rejected) DB 저장 = Human Review 지표
- 로그에서 나온 수치(응답시간·실패단계) → 마감단계 "평가 지표"로 집계
- DAY2 종료 → 다음 DAY3(n8n / Docker / E2E)
