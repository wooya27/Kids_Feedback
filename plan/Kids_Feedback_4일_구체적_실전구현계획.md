# Kids_Feedback — AI Backend / RAG 4일 집중 실전 구현 계획

> 기준 문서  
> - Notion `구체적 플랜 프롬프트`
> - Notion `Kids_Feedback — AI Backend/RAG 취업형 실행 기획 v4`
>
> 목표: 코드를 많이 만드는 것이 아니라, **현재 프로젝트의 전체 흐름을 이해하고 직접 수정·디버깅·설명할 수 있는 상태**까지 4일 안에 끌어올린다.

---

# 0. 이 계획을 사용하는 방법

## 가장 중요한 규칙

이 계획은 길지만 **한 번에 전부 보지 않는다.**

매일 큰 목표는 최대 3개만 본다.

```text
오늘의 큰 목표 1
↓
지금 하는 블록 1개
↓
실행
↓
결과 확인
↓
내 말로 설명
↓
다음 블록
```

각 블록을 완료할 때는 단순히 코드가 실행되는 것으로 끝내지 않는다.

**완료 = 구현 + 실행 확인 + 작은 수정 + 오류/예외 확인 + 안 보고 설명**

막히면 이렇게 바꾼다.

```text
"왜 안 되지?"
↓
"지금 내가 모르는 개념이 뭐지?"
↓
개념 1개만 확인
↓
다시 실행
```

---

# 1. 프로젝트 현재 위치

현재 프로젝트 상태:

```text
학생/프로필 CRUD                    ✅
수업 기록 CRUD                      ✅
PostgreSQL 저장                     ✅
LLM JSON 피드백 생성                ✅
Feedback 저장                       ✅
JSON 벡터 기반 RAG 검색             ✅

RAG 결과 → 실제 LLM Prompt 연결     ▶ 현재
Human Review                       ⬜
LLM Schema/실패 처리               ⬜
pgVector 검색                      ⬜
RAG 평가                           ⬜
Streamlit 전체 업무 연결            ⬜
Docker Compose                     ⬜
pytest / GitHub Actions            ⬜
README / 면접 설명                 ⬜
```

## 최종 전체 흐름

```text
강사
↓
Streamlit
학생 선택 + 수업 기록 입력
↓
FastAPI
↓
PostgreSQL
학생 프로필 + 최근 수업 기록 조회
↓
RAG Query 생성
↓
Embedding
↓
pgVector
Top-3 지도 가이드 검색
↓
content + source + score
↓
근거 충분?
├─ 아니오 → REVIEW_REQUIRED
└─ 예
   ↓
학생 데이터 + Retrieved Context
   ↓
LLM
   ↓
Structured JSON
   ↓
Schema Validation
   ↓
정상?
├─ 아니오 → 1회 재시도 → REVIEW_REQUIRED
└─ 예
   ↓
AI Feedback 저장
↓
Human Review
↓
수정 / 승인 / 반려
↓
generated_text + reviewed_text + status
↓
PostgreSQL 저장
```

---

# 2. 4일 전체 일정

| Day | 큰 목표 | 핵심 결과 |
|---|---|---|
| Day 1 | RAG와 LLM 연결 | 검색한 근거가 실제 피드백 생성에 사용됨 |
| Day 2 | LLM 안정화 + Human Review | AI 실패를 처리하고 사람 수정/승인 이력을 저장 |
| Day 3 | PostgreSQL + SQL + pgVector + RAG 평가 | JSON 벡터를 DB 벡터 검색으로 전환하고 품질 검증 |
| Day 4 | Streamlit E2E + Docker + Test/CI | 화면에서 업무 완료, 재현 가능한 실행환경과 테스트 확보 |

하루 기준 권장 시간:

```text
블록 30~50분
+
블록 사이 5~10분 휴식
+
하루 5~6블록
=
약 4~5시간
```

---

# DAY 1 — RAG 검색 결과를 실제 LLM 피드백 생성에 연결

## 오늘의 큰 목표 3개

1. 현재 `/feedbacks/generate` 전체 흐름을 찾는다.
2. RAG 검색 결과를 `content/source/score` 형태로 정리하고 Prompt에 넣는다.
3. 정상/근거 부족/학생 없음을 직접 테스트하고 설명한다.

## 오늘 끝나면 보여야 하는 결과

```text
학생 + 최근 수업
↓
RAG 검색
↓
Top-3 지도 가이드
↓
LLM Prompt에 실제 삽입
↓
근거 기반 피드백
```

---

## 블록 1 — `/feedbacks/generate` 코드 흐름 추적

**예상: 30~40분**

### 📍 지금 무엇을 하는가

새 코드를 먼저 쓰지 않는다.

현재 이미 만들어진 `POST /feedbacks/generate`가 어떤 파일과 함수를 거치는지 찾아서 **프로젝트 지도**를 만든다.

### 🧒 아주 쉽게 설명하면

택배가 어디서 출발해서 어느 물류센터를 거쳐 우리 집까지 오는지 먼저 추적하는 것이다.

코드를 수정하기 전에:

```text
요청이 어디로 들어오고
↓
어디서 DB를 읽고
↓
어디서 RAG를 부르고
↓
어디서 LLM을 부르고
↓
어디서 저장하는지
```

부터 찾는다.

### 왜 필요한가

이 흐름을 모르고 코드를 추가하면:

- 같은 기능을 두 번 만들 수 있다.
- 잘못된 파일을 수정할 수 있다.
- 에러가 났을 때 어디를 봐야 할지 모른다.

### 해야 할 행동

- [ ] FastAPI 실행 위치 확인
- [ ] `/feedbacks/generate` endpoint가 정의된 위치 찾기
- [ ] endpoint가 호출하는 함수 찾기
- [ ] 학생 프로필을 어디서 조회하는지 찾기
- [ ] 최근 수업 기록을 어디서 조회하는지 찾기
- [ ] 기존 RAG 검색 함수 위치 찾기
- [ ] LLM 호출 함수 위치 찾기
- [ ] Feedback 저장 위치 찾기

### 직접 적을 흐름

```text
POST /feedbacks/generate
↓
[실제 router 파일]
↓
[실제 service/function]
↓
학생 조회:
최근 수업 조회:
RAG 호출:
LLM 호출:
Feedback 저장:
```

> 실제 파일명은 저장소에서 확인한 이름으로 적는다. 모르는 파일명을 추측해서 쓰지 않는다.

### 완료 기준

코드를 안 보고 다음 질문에 답할 수 있다.

> `/feedbacks/generate` 요청 하나가 들어오면 최종 DB 저장까지 어떤 순서로 움직이는가?

---

## 블록 2 — RAG Query가 무엇인지 이해하고 직접 바꿔보기

**예상: 30~40분**

### 📍 지금 무엇을 하는가

RAG가 검색할 때 사용하는 **검색 질문(Query)** 이 무엇으로 만들어지는지 확인한다.

현재 기획 기준 입력:

```text
personality
+
activity
+
teacher_note
↓
RAG Query
```

### 🧒 아주 쉽게 설명하면

RAG는 자료실 직원이다.

직원에게:

> "자료 좀 찾아줘."

라고 하면 엉뚱한 걸 가져올 수 있다.

하지만:

> "줄넘기 수업에서 실패를 두려워하고 새로운 동작을 어려워하는 학생의 지도 방법을 찾아줘."

라고 하면 더 정확한 자료를 찾는다.

즉 **Query는 검색 지시문**이다.

### 해야 할 행동

- [ ] 현재 Query를 만드는 코드 찾기
- [ ] Query에 어떤 학생 정보가 포함되는지 적기
- [ ] 실제 Query 문자열 한 번 출력해보기
- [ ] Query 문장을 조금 바꿔보기
- [ ] 수정 전/후 Top-3 검색 결과가 달라지는지 비교

### 데이터 흐름

```text
Child.personality
LessonRecord.activity
LessonRecord.teacher_note
↓
문자열 조합
↓
query_text
↓
Embedding
↓
검색
```

### 작은 실습

같은 학생에 대해 Query 2개를 비교한다.

```text
A. "줄넘기 수업 피드백"
B. "실패를 두려워하고 새 동작을 어려워하는 학생의 줄넘기 지도 방법"
```

확인:

- 어떤 문서가 검색되는가?
- source가 달라지는가?
- score가 달라지는가?

### 완료 기준

다음 말을 본인 말로 설명할 수 있다.

> "RAG 품질은 LLM만의 문제가 아니라 검색 Query 설계에도 영향을 받습니다."

---

## 블록 3 — RAG 출력 구조를 `content / source / score`로 정리

**예상: 40~50분**

### 📍 지금 무엇을 하는가

RAG가 단순히 문장만 반환하지 않고:

```text
content
source
score
```

를 함께 반환하게 확인/정리한다.

### 각각 무엇인가

```text
content → 실제 검색된 지도 가이드 내용
source  → 그 내용이 어디서 왔는지
score   → Query와 얼마나 가까운지 비교하기 위한 값
```

### 헷갈리지 말 것

`score`는:

> "이 답이 92% 확률로 정답이다."

라는 뜻이 아니다.

Embedding 기반 검색에서 **Query와 문서가 얼마나 가까운지 판단하기 위한 검색 값**이다.

### 해야 할 행동

- [ ] 현재 Retriever 반환값 확인
- [ ] Top-3 각각에 content가 있는지 확인
- [ ] source가 있는지 확인
- [ ] score가 있는지 확인
- [ ] 누락된 값이 있다면 반환 구조에 포함
- [ ] 검색 결과가 없는 경우 확인
- [ ] 낮은 score일 때 `rag_status=insufficient`로 처리할 위치 정하기

### 출력 형태 예시

개념적으로:

```text
retrieved_context = [
    {
        content: "...",
        source: "guide_xxx.md",
        score: ...
    },
    ...
]
```

실제 코드 형태는 기존 프로젝트 구조에 맞춘다.

### 왜 `insufficient`가 필요한가

잘 맞는 자료가 없는데도 LLM에게:

> "이 자료를 근거로 답해."

라고 하면 억지 답변을 만들 수 있다.

그래서:

```text
검색 결과 충분
→ LLM 생성

검색 결과 부족
→ REVIEW_REQUIRED
```

로 구분한다.

### 완료 기준

정상 Query와 일부러 관련 없는 Query를 넣었을 때:

- 정상 검색
- 근거 부족

을 구분할 수 있다.

---

## 블록 4 — Retrieved Context를 실제 LLM Prompt에 삽입

**예상: 40~50분**

### 📍 지금 무엇을 하는가

오늘 가장 중요한 구현이다.

현재 따로 존재하던:

```text
RAG 검색 기능
+
LLM 생성 기능
```

을 실제로 연결한다.

### 연결 전

```text
학생 데이터 → LLM
RAG 검색 → 검색 결과 출력

둘이 따로 존재
```

### 연결 후

```text
학생 데이터
+
RAG 검색 결과
↓
Prompt
↓
LLM
```

### Prompt에서 역할을 나누기

개념적으로:

```text
[학생 정보]
- 성향
- 최근 수업
- 강사 메모

[지도 근거]
- Retrieved Context

[출력 규칙]
- next_goal
- teacher_feedback
- parent_feedback
```

### 해야 할 행동

- [ ] 현재 Prompt 만드는 위치 찾기
- [ ] 학생 데이터 영역 확인
- [ ] Retrieved Context 영역 추가
- [ ] source를 Prompt에 넣을지/응답 메타데이터로만 보낼지 구분
- [ ] Top-3 content가 실제 Prompt에 들어가는지 출력/로그로 확인
- [ ] 동일 학생에서 Context를 바꿨을 때 결과가 달라지는지 확인

### 실무 사고

Prompt에 모든 지도 문서를 넣는 것이 아니라:

```text
전체 문서
↓
RAG가 관련 부분 선택
↓
선택된 Context만 Prompt에 삽입
```

한다.

이게 RAG를 사용하는 핵심 이유다.

### 완료 기준

> "검색한 어떤 문장이 실제 LLM 입력에 들어갔는지"

직접 보여줄 수 있다.

---

## 블록 5 — Swagger E2E 테스트

**예상: 30~40분**

### 테스트 1 — 정상 학생

- [ ] 존재하는 child_id 사용
- [ ] 최근 수업 기록 존재
- [ ] RAG Top-3 반환
- [ ] LLM JSON 반환
- [ ] Feedback 저장

### 테스트 2 — 없는 학생

기대:

```text
404
```

확인할 것:

> "LLM 호출 전에 왜 막아야 하는가?"

### 테스트 3 — RAG 근거 부족

기대 개념:

```text
rag_status = insufficient
또는
review_required
```

### 테스트 결과 기록

```text
정상:
없는 학생:
근거 부족:
```

### 30초 설명

안 보고 말한다.

> "사용자가 피드백 생성을 요청하면 FastAPI가 학생과 최근 수업을 PostgreSQL에서 조회하고, 그 정보로 RAG Query를 만들어 관련 지도 가이드 Top-3를 찾습니다. 검색된 Context를 LLM Prompt에 넣어 피드백을 생성하고 저장합니다."

### Day 1 완료 체크

- [ ] generate endpoint 전체 흐름을 찾았다.
- [ ] RAG Query를 설명할 수 있다.
- [ ] content/source/score를 확인했다.
- [ ] 근거 부족 상태를 구분한다.
- [ ] Retrieved Context가 실제 Prompt에 들어간다.
- [ ] 정상/404/근거 부족을 실행했다.
- [ ] 30초 설명 성공.

---

# DAY 2 — LLM 출력 안정화 + Human Review

## 오늘의 큰 목표 3개

1. LLM 결과를 Schema로 검증한다.
2. 실패를 안전하게 `REVIEW_REQUIRED`로 넘긴다.
3. AI 원문과 사람 수정본/상태를 DB에 남긴다.

## 오늘 끝나면 보여야 하는 결과

```text
LLM
↓
Schema 검증
↓
정상 → AI 초안 저장
실패 → 재시도 → REVIEW_REQUIRED
↓
사람 검수
↓
원문 + 수정본 + 상태 저장
```

---

## 블록 1 — JSON과 Pydantic Schema 차이 이해

**예상: 30~40분**

### 아주 쉽게

JSON은 **택배 상자에 적힌 내용**이고,

Pydantic Schema는:

> "이 상자에는 반드시 이름, 주소, 전화번호가 있어야 한다."

라는 검사표다.

### 현재 기대 출력

```text
next_goal
teacher_feedback
parent_feedback
```

### 확인할 것

- [ ] LLM이 실제 어떤 JSON을 반환하는지 확인
- [ ] 프로젝트의 Response Schema 확인
- [ ] 필수 필드 확인
- [ ] 필드 타입 확인
- [ ] API 응답 Schema와 LLM 내부 결과 Schema가 같은지/다른지 확인

### 완료 기준

다음을 구분한다.

```text
JSON → 데이터 형식
Pydantic Schema → 그 데이터가 규칙에 맞는지 검증
```

---

## 블록 2 — Schema Validation 실패를 일부러 만들어보기

**예상: 40~50분**

### 왜 일부러 실패시키나

정상만 확인하면 디버깅 실력이 늘지 않는다.

실무자는:

```text
정상 경로
+
실패 경로
```

를 같이 본다.

### 실패 예

```text
next_goal 없음
teacher_feedback 없음
숫자가 들어가야 할 곳에 문자열
JSON 자체가 깨짐
```

실제 Schema에 맞는 실패를 선택한다.

### 해야 할 행동

- [ ] 정상 결과 1회
- [ ] 필드 누락 결과 1회
- [ ] 깨진 JSON 또는 잘못된 타입 1회
- [ ] 에러 메시지에서 중요한 부분 찾기
- [ ] 어느 계층에서 실패하는지 기록

### 디버깅 순서

```text
에러 메시지
↓
어떤 데이터가 들어왔나?
↓
Schema가 무엇을 기대했나?
↓
어디가 다른가?
```

### 완료 기준

Validation Error를 봤을 때:

> "LLM이 실패했다"

에서 끝나지 않고,

> "어떤 필드가 어떤 규칙을 어겼다"

까지 말할 수 있다.

---

## 블록 3 — 1회 재시도 + `REVIEW_REQUIRED`

**예상: 30~40분**

### 흐름

```text
LLM 호출
↓
Schema 정상?
├─ YES → 저장
└─ NO
   ↓
1회 재시도
   ↓
정상?
├─ YES → 저장
└─ NO → REVIEW_REQUIRED
```

### 왜 무한 재시도를 하지 않는가

- API 비용 증가
- 응답 시간 증가
- 같은 오류가 반복될 수 있음
- 사용자가 왜 기다리는지 모름

### 해야 할 행동

- [ ] Validation 실패를 잡는 위치 확인
- [ ] retry_count 개념 정하기
- [ ] 1회만 다시 요청
- [ ] 계속 실패하면 상태를 `REVIEW_REQUIRED`로 전환
- [ ] 사용자/API 응답에서 실패 상태를 알 수 있게 확인

### 완료 기준

LLM이 이상한 출력을 내도 **서버 전체가 무너지는 대신 업무 상태로 관리**된다.

---

## 블록 4 — Human Review 상태와 DB 관계 이해

**예상: 40~50분**

### 상태

```text
DRAFT
MODIFIED
APPROVED
REJECTED
REVIEW_REQUIRED
```

### 각각 쉬운 의미

```text
DRAFT           → AI가 만든 초안
MODIFIED        → 사람이 수정함
APPROVED        → 사람이 최종 승인
REJECTED        → 사용하지 않기로 함
REVIEW_REQUIRED → 시스템이 자동 확정하면 안 됨
```

### 데이터 관계

```text
Child
↓
LessonRecord
↓
Feedback
↓
FeedbackReview
```

### 왜 Feedback과 FeedbackReview를 나누는가

AI가 만든 결과와 사람이 판단한 결과는 역할이 다르기 때문이다.

```text
Feedback
→ AI가 생성한 것

FeedbackReview
→ 사람이 어떻게 판단/수정했는지
```

### 해야 할 행동

- [ ] 현재 feedbacks 테이블/모델 확인
- [ ] feedback_reviews 존재 여부 확인
- [ ] PK/FK 확인
- [ ] generated_text 위치 확인
- [ ] reviewed_text 위치 확인
- [ ] review_status 위치 확인

### 완료 기준

다음을 설명한다.

> "AI 결과를 덮어쓰지 않고 원문과 수정본을 모두 남기는 이유는 검수 이력과 품질 비교를 가능하게 하기 위해서입니다."

---

## 블록 5 — Review API 구현/보강

**예상: 40~50분**

대상 API:

```text
PATCH /feedbacks/{feedback_id}/review
```

### 입력 개념

```text
feedback_id
reviewed_text
status
```

### 처리

```text
feedback 존재?
↓
현재 AI 원문 확인
↓
사람 수정본 저장
↓
상태 저장
↓
DB commit
```

### 예외

```text
feedback 없음 → 404
잘못된 status → 422 또는 Validation
DB 저장 실패 → 500 계열
```

### 해야 할 행동

- [ ] AI 문장을 그대로 승인
- [ ] AI 문장을 수정 후 승인
- [ ] 반려
- [ ] 존재하지 않는 feedback_id
- [ ] DB에서 결과 확인

### 완료 기준

DB에:

```text
generated_text
reviewed_text
status
```

가 함께 남는다.

---

## 블록 6 — DB 직접 조회 + 30초 설명

**예상: 20~30분**

### 직접 확인

```text
Feedback
↓
FeedbackReview
```

관계를 SQL 또는 현재 DB 도구에서 확인한다.

### 질문

> 왜 API 응답만 보고 끝내면 안 될까?

답:

> 실제 저장이 되었는지 확인해야 하기 때문이다.

### 30초 설명

> "LLM 결과는 바로 최종 결과가 되지 않습니다. 먼저 Schema로 형식을 검증하고 실패하면 한 번 재시도합니다. 계속 실패하면 REVIEW_REQUIRED로 넘깁니다. 정상 생성된 초안도 사람이 수정·승인하며 AI 원문과 수정본을 분리 저장합니다."

### Day 2 완료 체크

- [ ] JSON과 Schema 차이를 설명한다.
- [ ] 일부러 Validation 실패를 만들었다.
- [ ] 1회 재시도 흐름이 있다.
- [ ] REVIEW_REQUIRED가 있다.
- [ ] Human Review 상태를 설명한다.
- [ ] AI 원문과 수정본이 DB에 남는다.
- [ ] Review API 오류도 확인했다.
- [ ] 30초 설명 성공.

---

# DAY 3 — PostgreSQL + SQL + pgVector + RAG 평가

## 오늘의 큰 목표 3개

1. `vectors.json` 기반 검색을 PostgreSQL + pgVector로 옮긴다.
2. SQL로 실제 관계형 데이터를 조회한다.
3. RAG 테스트셋으로 검색 품질을 검증하고 실패 Query를 개선한다.

## 오늘 끝나면 보여야 하는 결과

```text
vectors.json
   ↓ 이전
PostgreSQL + pgVector
   ↓
Query Embedding
   ↓
Vector Similarity Search
   ↓
Top-3
```

---

## 블록 1 — 현재 `vectors.json` 방식 다시 설명하기

**예상: 30~40분**

### 먼저 사람 말로 번역

현재 방식은:

> 문서의 의미를 숫자 배열로 바꿔 JSON 파일에 저장하고, 질문도 숫자 배열로 만든 뒤 서로 얼마나 비슷한지 Python에서 비교하는 방식.

### 흐름

```text
Markdown
↓
Chunk
↓
Embedding
↓
vectors.json
↓
Query Embedding
↓
Python similarity 계산
↓
Top-K
```

### 확인할 것

- [ ] vectors.json 위치
- [ ] 한 chunk의 필드
- [ ] embedding 차원
- [ ] similarity 계산 위치
- [ ] Top-K 정렬 위치

### 완료 기준

코드를 안 보고 현재 RAG가 검색하는 과정을 설명한다.

---

## 블록 2 — pgVector 테이블 구조 이해/구현

**예상: 40~50분**

### 핵심 개념 3개만

#### PostgreSQL

일반 업무 데이터를 테이블로 저장하는 DB.

#### pgVector

PostgreSQL에 **vector 타입과 벡터 검색 기능**을 추가하는 확장.

#### metadata

벡터만으로는 어떤 문서인지 알기 어렵기 때문에 같이 저장하는 설명 정보.

예:

```text
document_id
source
category
content
embedding
```

### 권장 관계

```text
rag_documents
1
↓
N
rag_chunks
```

### rag_documents

문서 단위 정보:

```text
id
source
title
category
```

### rag_chunks

검색 단위 정보:

```text
id
document_id
content
embedding
```

### 해야 할 행동

- [ ] pgVector extension 확인
- [ ] rag_documents 구조 확인/생성
- [ ] rag_chunks 구조 확인/생성
- [ ] FK 관계 확인
- [ ] embedding vector(n) 차원 확인

### 완료 기준

다음을 구분한다.

```text
content  → 사람이 읽는 글
embedding → 컴퓨터가 유사도를 비교하는 숫자 벡터
metadata → 출처/종류를 추적하는 정보
```

---

## 블록 3 — JSON의 기존 Embedding을 PostgreSQL에 저장

**예상: 40~50분**

### 데이터 이동

```text
vectors.json
↓
각 chunk 읽기
↓
content/source/embedding
↓
rag_documents / rag_chunks INSERT
↓
PostgreSQL
```

### 실무 체크 순서

```text
DB 연결?
↓
테이블 존재?
↓
행 들어갔나?
↓
content 정상?
↓
embedding NULL 아님?
↓
개수 맞나?
```

### 해야 할 행동

- [ ] 이전 전 JSON chunk 개수 기록
- [ ] DB INSERT 실행
- [ ] 저장 후 row count 확인
- [ ] embedding이 NULL인지 확인
- [ ] 임의 1개 chunk 내용 확인
- [ ] source가 연결되는지 확인

### 완료 기준

> "벡터가 저장되었습니다."

가 아니라 SQL/DB 조회로 실제 존재를 확인한다.

---

## 블록 4 — pgVector Top-3 검색

**예상: 40~50분**

### 흐름

```text
사용자 Query
↓
Embedding 모델
↓
query_vector
↓
pgVector
↓
거리 계산
↓
ORDER BY
↓
LIMIT 3
```

### 지금 알아야 할 SQL 개념

```text
vector(n) → 벡터를 저장하는 컬럼 타입
<=>       → cosine distance 계열 비교 연산자
ORDER BY  → 가까운 순으로 정렬
LIMIT 3   → 상위 3개만 가져오기
```

### 헷갈리지 말 것

거리와 유사도는 같은 숫자가 아닐 수 있다.

프로젝트에서 반환하는 `score`가:

- distance인지
- similarity로 변환한 값인지

반드시 확인한다.

### 비교 실습

같은 Query로:

```text
기존 JSON 검색 Top-3
vs
pgVector 검색 Top-3
```

비교한다.

### 완료 기준

> "왜 DB에서 ORDER BY distance LIMIT 3을 하는지"

설명 가능.

---

## 블록 5 — 프로젝트 데이터로 SQL JOIN 연습

**예상: 30~40분**

### 목표

SQL 문법을 외우는 게 아니라 현재 프로젝트 데이터가 어떻게 연결되는지 확인한다.

### 관계

```text
children
↓
lesson_records
↓
feedbacks
↓
feedback_reviews
```

### 확인할 질문

1. 특정 학생의 최근 수업 기록은?
2. 특정 학생의 최근 피드백은?
3. 승인된 피드백만 보고 싶다면?
4. 최신 순으로 3개만 보고 싶다면?

### 핵심 SQL 역할

```text
SELECT   → 무엇을 볼지
FROM     → 어디서 가져올지
JOIN     → 다른 표와 연결
WHERE    → 조건
ORDER BY → 순서
LIMIT    → 개수 제한
```

### ORM과 SQL

ORM이 있어도 SQL을 알아야 하는 이유:

> ORM이 만들어주는 DB 작업이 결국 어떤 조회를 하는지 이해하고, 성능/오류/관계를 판단하기 위해서.

### 완료 기준

JOIN 하나를 보고:

> "어떤 테이블을 왜 연결하는 쿼리인지"

말할 수 있다.

---

## 블록 6 — RAG 평가 10개 + 실패 Query 1개 개선

**예상: 40~50분**

### 평가 데이터 개념

```text
query
expected_source
```

예:

```text
Query:
"실패를 두려워하는 학생 지도 방법"

Expected:
confidence_guide.md
```

### 평가

```text
Query
↓
Top-3 검색
↓
expected_source가 포함됐나?
├─ YES → 성공
└─ NO → 실패
```

### 목표

약 10개를 평가한다.

목표값은 기획 기준:

```text
Top-3 적합률 80% 목표
```

### 실패 Query 분석 순서

검색이 틀렸을 때 무조건 embedding 모델부터 바꾸지 않는다.

```text
1. Query가 너무 짧거나 애매한가?
2. Chunk가 너무 크거나 작은가?
3. 원문에 필요한 내용이 실제 있는가?
4. Metadata filter가 문제인가?
5. Top-K가 너무 작은가?
6. Embedding 저장/차원이 맞는가?
```

### 개선 전/후 기록

```text
실패 Query:
기존 Top-3:
원인 추정:
수정:
수정 후 Top-3:
결과:
```

### 완료 기준

다음 면접 질문에 답할 수 있다.

> "RAG 검색 품질이 낮을 때 어떤 순서로 디버깅하셨나요?"

---

## Day 3 완료 체크

- [ ] vectors.json 방식 설명 가능.
- [ ] pgVector 역할 설명 가능.
- [ ] embedding이 DB에 저장됨.
- [ ] pgVector Top-3 검색 작동.
- [ ] distance/score 의미 확인.
- [ ] JOIN을 프로젝트 데이터로 확인.
- [ ] 테스트 Query 약 10개 평가.
- [ ] 실패 Query 1개 개선.
- [ ] 검색 실패 디버깅 순서 설명 가능.

---

# DAY 4 — Streamlit E2E + Docker + pytest/CI + 포트폴리오

## 오늘의 큰 목표 3개

1. Swagger 없이 Streamlit에서 전체 업무를 끝낸다.
2. Docker로 프로젝트 실행환경을 재현한다.
3. 테스트/CI/README/면접 설명으로 프로젝트를 마감한다.

## 오늘 끝나면 보여야 하는 결과

```text
다른 사람이 프로젝트를 실행
↓
학생 선택
↓
수업 기록 입력
↓
AI 피드백 생성
↓
근거 확인
↓
수정 / 승인
↓
DB 저장
```

---

## 블록 1 — Streamlit 학생 선택 + 수업 기록 입력

**예상: 40~50분**

### UI의 역할

Streamlit은 AI가 아니다.

**강사가 업무를 수행하는 화면**이다.

```text
사용자
↓
Streamlit
↓
FastAPI
```

### 해야 할 행동

- [ ] 학생 목록 조회
- [ ] 학생 선택
- [ ] 수업 기록 입력 폼
- [ ] FastAPI lesson endpoint 호출
- [ ] 저장 성공 표시
- [ ] 실패 시 에러 표시

### 완료 기준

Swagger를 열지 않고 수업 기록 1건을 저장한다.

---

## 블록 2 — 피드백 생성 + RAG 근거 + Human Review UI

**예상: 40~50분**

### 화면에 최소 표시할 것

```text
학생
최근 수업
AI 피드백
RAG source
RAG score
검수 상태
수정 입력란
승인/반려
```

### 해야 할 행동

- [ ] 피드백 생성 버튼
- [ ] generate API 호출
- [ ] next_goal 표시
- [ ] teacher_feedback 표시
- [ ] parent_feedback 표시
- [ ] source/score 표시
- [ ] 수정 가능 입력
- [ ] 승인 버튼
- [ ] Review API 연결
- [ ] 저장 성공 확인

### 완료 기준

**Streamlit만으로 단건 업무 전체 완료.**

---

## 블록 3 — Docker Compose

**예상: 40~50분**

### 쉽게

Docker는:

> "내 컴퓨터에서는 되는데 다른 컴퓨터에서는 안 돼요."

문제를 줄이기 위한 실행환경 포장 방식이다.

### 이번 프로젝트 서비스

개념적으로:

```text
api → FastAPI
db  → PostgreSQL + pgVector
ui  → Streamlit
```

### 지금 알아야 할 4개

```text
env     → 설정값/API Key/DB 주소
port    → 외부와 통신하는 문
volume  → 컨테이너를 꺼도 DB 데이터 유지
network → 컨테이너끼리 통신
```

### 특히 헷갈릴 것

컨테이너 안에서:

```text
localhost
```

는 내 Windows PC가 아니라 **그 컨테이너 자기 자신**을 의미한다.

### 해야 할 행동

- [ ] Dockerfile 확인/작성
- [ ] docker-compose.yml 확인/작성
- [ ] API 서비스
- [ ] DB 서비스
- [ ] UI 서비스
- [ ] 환경변수 연결
- [ ] `docker compose up`
- [ ] API 접속
- [ ] Streamlit 접속
- [ ] DB 연결 확인

### 오류가 나면 보는 순서

```text
컨테이너 실행 중?
↓
port?
↓
env?
↓
DB hostname?
↓
network?
↓
volume?
```

### 완료 기준

한 명령으로 핵심 서비스가 뜬다.

---

## 블록 4 — pytest 핵심 테스트

**예상: 40~50분**

### 테스트가 필요한 이유

사람이 매번 버튼 눌러 확인하지 않아도:

> "전에 되던 기능이 지금도 되는가?"

를 자동으로 확인한다.

### 우선 테스트할 4개

1. 정상 feedback 생성
2. 없는 학생 → 404
3. Review 저장
4. RAG 검색 결과 반환

### 가능하면 추가

- Schema 실패 처리
- rag_status insufficient

### 테스트 사고방식

```text
입력
↓
기대 결과 정의
↓
실행
↓
실제 결과 비교
```

### 완료 기준

핵심 테스트가 반복 실행되어 통과한다.

---

## 블록 5 — GitHub Actions + 실패 로그 경험

**예상: 30~40분**

### 흐름

```text
git push / PR
↓
GitHub Actions
↓
dependency install
↓
pytest
↓
PASS / FAIL
```

### 왜 일부러 실패시키나

CI Green만 보는 것보다:

> 실패 로그를 보고 원인을 찾을 수 있는가?

가 더 중요하다.

### 해야 할 행동

- [ ] Actions workflow 확인/작성
- [ ] push 시 pytest 실행
- [ ] 정상 Green 확인
- [ ] 테스트 하나를 의도적으로 실패
- [ ] GitHub 로그에서 실패 위치 확인
- [ ] 다시 고쳐 Green 복구

### 완료 기준

CI가 무엇을 대신 검사해주는지 설명 가능.

---

## 블록 6 — README + 3분 면접 설명

**예상: 30~40분**

### README 순서

```text
1. 문제
2. 기존 업무 방식 Before
3. 개선된 업무 방식 After
4. Architecture
5. Data Flow
6. RAG 구조
7. Human Review
8. 예외/품질 관리
9. 실행 방법
10. 테스트
11. 개선 과정
```

### 꼭 넣을 개선 스토리

```text
초기:
vectors.json 기반 수동 벡터 검색

문제:
파일 기반이라 운영형 검색/조회/확장에 한계

개선:
PostgreSQL + pgVector

결과:
업무 데이터와 벡터 검색을 DB 환경에서 관리
```

### 3분 설명 뼈대

#### 0~30초 — 문제

> 강사가 매 수업 후 학생별 학부모 피드백을 반복 작성하는 업무를 자동화하려고 만들었습니다.

#### 30~60초 — 전체 구조

> Streamlit에서 수업 기록을 입력하면 FastAPI가 PostgreSQL에서 학생 정보와 최근 기록을 조회합니다.

#### 60~100초 — RAG

> 학생 성향과 수업 내용을 Query로 만들어 pgVector에서 관련 지도 가이드 Top-3를 검색하고 그 Context를 LLM Prompt에 넣습니다.

#### 100~140초 — 안전장치

> LLM 결과는 Schema로 검증하고 검색 근거가 부족하거나 출력이 실패하면 자동 확정하지 않고 Human Review로 넘깁니다.

#### 140~180초 — 운영

> 강사가 AI 초안을 수정·승인하고 원문과 수정본을 DB에 남기며, Docker/pytest/GitHub Actions로 실행환경과 회귀를 관리했습니다.

### 완료 기준

코드를 보지 않고 3분 설명 가능.

---

# 3. 최종 기술별 도달 목표

## FastAPI — Level 4 목표

할 수 있어야 하는 것:

- endpoint 흐름 찾기
- 새 endpoint 기본 추가
- Request/Response Schema 이해
- 404 / 422 / 500 차이 설명
- Service 호출 흐름 수정

면접 답변:

> "FastAPI를 단순 호출용으로 쓴 게 아니라 학생/수업/피드백/검수 API를 분리하고 예외 상태까지 관리했습니다."

---

## PostgreSQL — Level 4 목표

할 수 있어야 하는 것:

- PK/FK 설명
- 1:N 관계 설명
- INSERT/UPDATE/SELECT 확인
- Review 이력 구조 설명
- DB 저장 실패 지점 찾기

---

## SQL — Level 3~4 목표

할 수 있어야 하는 것:

- SELECT
- WHERE
- JOIN
- ORDER BY
- LIMIT
- 학생→수업→피드백→검수 관계 조회

---

## LLM API — Level 4 목표

할 수 있어야 하는 것:

- Prompt 입력 구성 설명
- Retrieved Context가 왜 들어가는지 설명
- JSON/Schema 실패 구분
- 재시도/Review Required 이유 설명
- 출력 형식 수정

---

## RAG / Embedding — Level 4 목표

할 수 있어야 하는 것:

```text
Document
↓
Chunk
↓
Embedding
↓
Vector Store
↓
Query Embedding
↓
Retrieval
↓
Context
↓
LLM
```

을 안 보고 설명.

검색이 틀릴 때:

```text
Query
→ Chunk
→ 원문
→ Metadata
→ Top-K
→ Embedding/저장
```

순서로 점검.

---

## pgVector — Level 3~4 목표

할 수 있어야 하는 것:

- vector 컬럼 의미
- Embedding 저장
- cosine distance/search 흐름
- Top-K
- JSON 기반 검색과 차이
- source/score 반환

---

## Docker — Level 3 목표

할 수 있어야 하는 것:

- Dockerfile과 Compose 역할 차이
- api/db/ui 서비스 구분
- env/port/volume/network 설명
- container 내부 localhost 문제 판단

---

## pytest / GitHub Actions — Level 3 목표

할 수 있어야 하는 것:

- 정상/실패 케이스 테스트
- API 결과 검증
- push 시 자동 테스트
- 실패 로그에서 위치 찾기

---

# 4. 이 프로젝트에서 일부러 하지 않는 것

## LangGraph

Kids_Feedback에서는 제외.

이유:

현재 단건 피드백 흐름은 일반 Service/함수로 충분하다.

LangGraph의 State/Node/Conditional Edge는 **AuditFlow AI**에서 실제 조건 분기 Workflow를 해결하는 용도로 학습한다.

---

## n8n / Make / Webhook

Kids_Feedback에서는 제외.

이유:

외부 자동화 역량은 AuditFlow AI에서:

```text
Webhook
→ FastAPI
→ IF
→ 후속 처리
```

로 더 자연스럽게 학습한다.

---

## CSV / Google Sheet Batch

현재 4일 필수 범위에서는 제외.

필요하면 나중에:

```text
CSV/Sheet
↓
여러 수업 기록
↓
Batch API
↓
Review Queue
```

로 확장.

---

## MCP / Airflow / BigQuery / Multi-Agent

현재 프로젝트 문제와 규모에 비해 과함.

기술을 많이 넣는 것이 목표가 아니라:

> 왜 이 기술이 이 문제에 필요한지 설명할 수 있는 것

이 목표다.

---

# 5. 매일 시작할 때 보는 체크리스트

## 시작 전 3분

```text
1. 오늘 큰 목표는 무엇인가?
2. 지금 하는 블록은 무엇인가?
3. 이 블록이 끝나면 화면/DB/API에서 무엇이 보여야 하는가?
```

## 막혔을 때

```text
에러 메시지 중요한 한 줄
↓
사람 말로 번역
↓
입력값 확인
↓
현재 데이터 위치 확인
↓
기대한 데이터 형태 확인
↓
실제 데이터 형태 확인
↓
가장 작은 수정
```

## 블록 종료 전

- [ ] 실행했는가?
- [ ] 결과를 직접 봤는가?
- [ ] 한 군데를 직접 바꿔봤는가?
- [ ] 실패/예외를 최소 하나 봤는가?
- [ ] 왜 필요한지 말할 수 있는가?

---

# 6. 4일 후 최종 완료 체크

## 기능

- [ ] RAG 검색 결과가 실제 LLM Prompt에 들어간다.
- [ ] Top-3 content/source/score를 확인할 수 있다.
- [ ] 근거 부족 상태를 구분한다.
- [ ] LLM 결과를 Schema로 검증한다.
- [ ] 실패 시 재시도 후 REVIEW_REQUIRED 처리한다.
- [ ] AI 원문과 사람 수정본을 모두 저장한다.
- [ ] Human Review 상태가 DB에 저장된다.
- [ ] pgVector Top-3 검색이 작동한다.
- [ ] Streamlit에서 단건 업무 전체가 끝난다.

## 이해

- [ ] FastAPI 요청 흐름 설명.
- [ ] PostgreSQL 관계 설명.
- [ ] SQL JOIN 설명.
- [ ] RAG 전체 흐름 설명.
- [ ] Embedding 역할 설명.
- [ ] pgVector를 쓰는 이유 설명.
- [ ] Schema validation 필요성 설명.
- [ ] Human Review 이유 설명.
- [ ] Docker 구성 설명.
- [ ] pytest/CI 이유 설명.

## 디버깅

- [ ] 없는 학생 404 확인.
- [ ] Schema 실패 확인.
- [ ] RAG 근거 부족 확인.
- [ ] RAG 실패 Query 1개 개선.
- [ ] CI 실패 로그를 실제로 확인.

## 포트폴리오

- [ ] README에 문제/구조/흐름/실행법 작성.
- [ ] JSON Vector → pgVector 개선 스토리 기록.
- [ ] RAG 실패 개선 사례 기록.
- [ ] 전체 프로젝트 3분 설명 가능.

---

# 7. 최종적으로 말할 수 있어야 하는 한 문장

> **Kids_Feedback는 FastAPI와 PostgreSQL 기반 교육 업무 시스템에서 학생 프로필과 수업 기록을 조회하고, pgVector RAG로 관련 지도 가이드를 검색해 LLM 피드백 생성에 근거로 사용하며, Schema Validation과 Human Review를 통해 AI 결과를 검증·수정·승인하도록 만든 AI Backend/RAG 프로젝트입니다.**

---

# 8. 가장 중요한 학습 기준

프로젝트가 끝났을 때 목표는:

```text
"AI가 만들어준 코드가 동작한다."
```

가 아니다.

목표는:

```text
"사용자 입력이 어디로 가고,
어떤 데이터가 DB에서 나오고,
왜 RAG를 거치고,
왜 pgVector를 쓰며,
어떻게 LLM에 들어가고,
실패하면 어디에서 잡고,
사람 검수 결과가 어디에 저장되는지
내 말로 설명하고 직접 수정할 수 있다."
```

이다.
