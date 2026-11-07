# Kids_Feedback — 3일 실무기술 체험 + 채용 포트폴리오 완성 플랜
> 목표: 3일 안에 기술을 “완벽히 공부”하는 것이 아니라, **Kids_Feedback 프로젝트 안에서 실제로 실행 → 추적 → 수정 → 구현 → 설명**까지 한 번 경험한다.
>
> 동시에 최종 포트폴리오에서는 단순히 기술을 사용했다는 것보다 **업무 문제 → 자동화 설계 → AI 구현 → 검수 → 운영 → 평가 → 배포**까지 설명할 수 있는 결과물을 만든다.


---

# 포트폴리오 최종 포지셔닝

이 프로젝트를 최종적으로 다음 한 문장으로 설명할 수 있어야 한다.

> **강사가 학생별 수업 기록과 지도 기준을 반복해서 확인하며 작성하던 피드백 업무를, PostgreSQL + RAG + LangGraph + LLM + Human Review + n8n으로 자동화한 교육 피드백 생성·검수 시스템**

## 해결하려는 업무 문제

```text
강사
↓
학생의 최근 수업 기록 확인
↓
이전 기록 다시 확인
↓
관련 지도 기준 찾기
↓
개별 피드백 작성
↓
수정
↓
저장
```

반복되는 조회·검색·초안 작성 때문에 시간이 오래 걸리고, 피드백 품질이 작성자와 상황에 따라 달라질 수 있다.

## AS-IS → TO-BE

### AS-IS

```text
수업 기록 확인
↓
학생 이전 기록 확인
↓
지도 기준 직접 검색
↓
피드백 직접 작성
↓
수정
↓
저장
```

### TO-BE

```text
수업 기록 ID 입력
↓
학생 + 최근 수업 자동 조회
↓
RAG로 관련 지도 기준 검색
↓
LLM 피드백 초안 생성
↓
LangGraph 검토
↓
Human Review
↓
승인 / 수정 / 거절
↓
DB 저장
↓
n8n으로 외부 시스템과 자동 연동
```

## 채용에서 보여줄 증거

최종 포트폴리오에는 아래 6가지를 남긴다.

```text
1. 업무 문제를 어떻게 정의했는가
2. 왜 RAG / LangGraph / n8n이 필요했는가
3. 데이터가 시스템 안에서 어떻게 이동하는가
4. 실패하면 어디서 어떻게 복구하는가
5. 생성 결과를 사람이 어떻게 검수하는가
6. 실제 테스트에서 얼마나 안정적으로 동작하는가
```

> `DAY 1 / DAY 2 / DAY 3` 구조는 **학습용 문서에서만 사용**한다.  
> 최종 GitHub / Notion 포트폴리오에서는 `문제 → 설계 → 구현 → 평가 → 배포 → 결과` 순서로 보여준다.

---

## 0. 이번 3일의 학습 원칙


### ADHD 맞춤 규칙
- 하루 작업은 **최대 3개**
- 한 작업은 **20~40분**
- 긴 이론 공부 금지
- 매 작업마다 **작은 기능 1개 완성**
- 막히면 “실패”가 아니라 **오늘 배울 개념이 생긴 것**
- 복습은 노트 정리보다 **안 보고 30초 설명**
- 지금 할 일은 항상 **1개만 본다**

### 기존 코드 공부 방식
이미 구현된 기능은 다시 만들지 않는다.

```text
파일 확인
↓
이 파일이 무슨 기술인지 확인
↓
누가 이 파일을 호출하는지 확인
↓
입력 데이터 확인
↓
처리 확인
↓
출력 확인
↓
다음 파일 확인
↓
직접 실행
↓
30초 설명
```

### 없는 기능 공부 방식

```text
왜 필요한지 이해
↓
어디에 넣을지 결정
↓
최소 코드 작성
↓
실행
↓
오류 확인
↓
수정
↓
30초 설명
```

---

# 최종 목표 흐름

```text
강사 / 외부 시스템
        ↓
       n8n
        ↓
FastAPI /feedbacks/generate
        ↓
PostgreSQL
학생 + 최근 수업기록 조회
        ↓
       RAG
관련 지도 기준 검색
        ↓
    LangGraph
검색 → 생성 → 검토
        ↓
      Gemini
피드백 JSON 생성
        ↓
자동 검증
필수 필드 / 빈 값 / RAG 근거 확인
        ↓
PostgreSQL Feedback 저장
        ↓
   Human Review
승인 / 수정 / 거절
        ↓
review_status / review_comment 저장

Docker
→ 실행 환경 고정

Logging + run_id
→ 처리 단계·오류·응답시간 추적

Evaluation
→ 테스트 케이스 / 성공률 / 수정률 확인

Cloud
→ 최종 포트폴리오 단계에서 실제 URL 배포

Git
→ 변경 이력
```

## 3일과 최종 포트폴리오의 범위 구분

### 3일 안에 반드시

```text
API → DB → RAG → LLM → LangGraph → DB
n8n 호출
Docker 실행
Logging
정상 / 실패 요청 확인
3분 설명
```

### 3일 이후 포트폴리오 마감 단계에서 추가

```text
Human Review 상태 저장
30~50개 테스트 케이스
평가 지표
Cloud 배포
README / Architecture / Demo 정리
```

> 3일 안에 전부 끝내려고 하지 않는다.  
> **3일은 구현 흐름 이해**, 그 이후는 **채용 결과물 완성** 단계다.

---

# DAY 1 — 이미 있는 Backend를 이해하고 RAG를 진짜 연결하기

## 오늘의 목표

> **API 요청 하나가 DB → RAG → LLM → DB 저장까지 어떻게 이동하는지 직접 추적하고, 현재 끊겨 있는 `RAG → Prompt` 연결을 완성한다.**

오늘 다룰 기술:

```text
Python
FastAPI
REST API
Pydantic
SQLAlchemy
PostgreSQL
SQL
RAG
Embedding
Vector Search
LLM API
JSON
```

---

## ▶ 작업 1 — 서버 실행 + 파일 호출 순서 추적
**시간: 30분**

### 지금 볼 파일
```text
Kids_Feedback/main.py
Kids_Feedback/routers/feedbacks_router.py
Kids_Feedback/schemas.py
```

### 먼저 실행

저장소 루트에서:

```bash
cd Kids_Feedback
fastapi dev main.py
```

안 되면:

```bash
uvicorn main:app --reload
```

### 확인

브라우저:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

### 사람 말로 흐름 번역

```text
실행 명령
↓
main.py
↓
app = FastAPI()
↓
feedbacks_router 등록
↓
POST /feedbacks/generate 대기
```

### 코드에서 찾을 것

`main.py`

```text
FastAPI()
include_router()
/health
```

`schemas.py`

```text
FeedbackGenerate
```

`feedbacks_router.py`

```text
@router.post("/generate")
```

### 데이터 형태

입력:

```json
{
  "lesson_record_id": 1
}
```

↓ Pydantic

```text
FeedbackGenerate 객체
```

↓ Router

```text
payload.lesson_record_id
```

### 완료 기준
- [ ] `/health`가 `ok`를 반환한다.
- [ ] `/docs`에서 `/feedbacks/generate`를 찾았다.
- [ ] `lesson_record_id`가 어느 파일에서 처음 받아지는지 찾았다.

### 30초 설명
코드를 닫고 말한다.

> FastAPI 서버는 `main.py`에서 시작하고 Router를 등록합니다. 사용자가 `/feedbacks/generate`로 JSON을 보내면 Pydantic의 `FeedbackGenerate`가 입력 형태를 확인하고 `feedbacks_router.py`가 실제 처리를 시작합니다.

### 막히면
서버가 안 켜지면 오늘 배울 개념은:

```text
실행환경
패키지 설치
모듈 경로
```

이다. 다른 작업으로 넘어가지 말고 **에러 첫 줄 + 마지막 줄만 확인**한다.

---

## 작업 2 — PostgreSQL 데이터가 Python으로 오는 과정 추적
**시간: 30분**

### 지금 볼 파일

```text
database.py
models.py
feedbacks_router.py
```

### 사람이 이해할 흐름

```text
FastAPI Router
↓
get_db()
↓
SessionLocal
↓
SQLAlchemy
↓
PostgreSQL
↓
LessonRecord
↓
Child
```

### `database.py`에서 볼 것

```text
DATABASE_URL
create_engine()
SessionLocal
get_db()
```

### `models.py`에서 볼 것

```text
Child
LessonRecord
Feedback
```

관계:

```text
Child
  ↓ child_id
LessonRecord
  ↓ lesson_record_id
Feedback
```

### Router에서 실제 조회 코드 찾기

```text
LessonRecord 조회
↓
record.child_id
↓
Child 조회
↓
최근 LessonRecord 5개 조회
```

### SQL도 직접 한 번 보기

PostgreSQL에서 같은 개념을 SQL로 생각한다.

```sql
SELECT *
FROM lesson_records
WHERE id = 1;
```

그리고:

```sql
SELECT *
FROM children
WHERE id = <child_id>;
```

**목표는 SQL을 외우는 것이 아니라**

```text
SQLAlchemy ORM 코드
=
SQL을 Python 문법으로 다루는 방법
```

이라는 연결을 이해하는 것.

### 완료 기준
- [ ] `get_db()`가 왜 필요한지 설명 가능
- [ ] `LessonRecord → child_id → Child` 흐름을 찾음
- [ ] ORM 조회와 SQL 조회가 같은 DB 데이터를 보는 것임을 이해

### 30초 설명

> `database.py`는 Python과 PostgreSQL을 연결합니다. Router가 `get_db()`를 통해 Session을 받아 DB에 요청하고, SQLAlchemy 모델을 이용해 `LessonRecord`와 `Child` 데이터를 Python 객체로 가져옵니다.

---

## 작업 3 — 🔥 RAG 검색 결과를 실제 Prompt에 연결
**시간: 40분**

### 현재 상태

현재 Router 안에서는:

```text
question
↓
rag_search(question)
↓
found
```

까지 실행된다.

그런데 다음은:

```text
build_prompt(child, records)
```

이므로 `found`가 LLM에게 전달되지 않는다.

### 오늘 완성할 작은 기능

```text
child
+
records
+
found
↓
build_prompt()
↓
Prompt
↓
Gemini
```

### 수정 위치 1

```text
prompt_service.py
```

현재 개념:

```text
build_prompt(child, records)
```

변경 방향:

```text
build_prompt(child, records, rag_context)
```

Prompt 안에 새 구역 추가:

```text
[관련 지도 기준]
{rag_context}
```

### 수정 위치 2

```text
routers/feedbacks_router.py
```

현재:

```text
found = rag_search(question)
...
prompt = build_prompt(child, records)
```

목표:

```text
found
↓
build_prompt의 세 번째 입력으로 전달
```

### 실행

Swagger `/docs`에서 다시:

```json
{
  "lesson_record_id": 1
}
```

보낸다.

### 확인할 것

```text
API 요청
↓
DB 조회
↓
RAG found
↓
Prompt에 포함
↓
Gemini JSON
↓
Feedback 저장
```

### 완료 기준
- [ ] `found`가 더 이상 버려지지 않는다.
- [ ] Prompt에 `[관련 지도 기준]`이 들어간다.
- [ ] `/feedbacks/generate`가 정상 결과를 반환한다.
- [ ] Feedback DB 저장까지 된다.

### 오늘 Git 저장

```bash
git add .
git commit -m "feat: connect RAG context to feedback prompt"
```

### DAY 1 최종 30초 설명

> 사용자가 수업 기록 ID를 보내면 FastAPI가 요청을 받고 PostgreSQL에서 수업과 학생 정보를 조회합니다. 학생 정보로 RAG 검색을 수행하고, 검색된 지도 기준과 최근 수업 기록을 Prompt에 함께 넣습니다. Gemini가 JSON 피드백을 만들고 결과를 Feedback 테이블에 저장합니다.

---

# DAY 2 — 기존 코드를 LangGraph 흐름으로 묶고 로그 보기

## 오늘의 목표

> **어제 만든 직선 흐름을 `검색 → 생성 → 검토` 단계로 나누고, 조건 분기를 한 번 경험한다.**

오늘 다룰 기술:

```text
LangGraph
State
Node
Edge
Conditional Edge
Agent Workflow
Logging
Debugging
```

---

## ▶ 작업 1 — LangGraph 최소 구조 만들기
**시간: 30분**

### 먼저 왜 필요한가

현재 Router는 많은 일을 한 함수에서 처리한다.

```text
DB 조회
↓
RAG
↓
Prompt
↓
LLM
↓
저장
```

단순하면 괜찮다.

하지만:

```text
검색
↓
생성
↓
검토
↓
문제 있으면 다시 검색
```

처럼 분기가 생기면 흐름 관리가 어려워진다.

그래서 LangGraph를 경험한다.

### 설치

```bash
pip install langgraph
```

### 새 폴더

```text
Kids_Feedback/
└─ graph/
   ├─ __init__.py
   └─ feedback_graph.py
```

### 오늘 처음 만들 구조

```text
START
↓
retrieve
↓
generate
↓
END
```

### State에 담을 최소 데이터

```text
lesson_record_id
child
records
rag_context
feedback
```

### 핵심 개념

```text
State = 단계 사이에서 들고 다니는 데이터 가방
Node = 실제 작업
Edge = 다음 작업으로 가는 화살표
```

### 완료 기준
- [ ] `feedback_graph.py` 파일 생성
- [ ] State 정의
- [ ] `retrieve` / `generate` Node 이름 생성
- [ ] START → retrieve → generate → END 연결

### 30초 설명

> LangGraph는 AI 처리 단계를 Node로 나누고, State에 데이터를 담아 다음 단계로 전달하는 도구입니다. 지금은 RAG 검색과 LLM 생성을 각각 Node로 나누었습니다.

---

## 작업 2 — review Node + 조건 분기 1개
**시간: 40분**

### 오늘 만들 Agent 느낌

```text
retrieve
↓
generate
↓
review
↓
결과 정상?
├─ YES → END
└─ NO  → retrieve
```

### review가 확인할 최소 조건

처음부터 복잡한 AI 평가를 만들지 않는다.

#### 3일 최소 기준

```text
feedback 값이 존재하는가?
필수 JSON 필드가 있는가?
```

필수 필드:

```text
next_goal
teacher_feedback
parent_feedback
```

#### 최종 포트폴리오 기준

3일 이후에는 아래까지 확장한다.

```text
rag_context가 존재하는가?
필수 JSON 필드가 모두 있는가?
각 필드가 빈 문자열이 아닌가?
생성 실패 / 파싱 실패가 발생하지 않았는가?
```

> 여기서 목표는 AI가 피드백의 “정답”을 완벽히 판정하는 것이 아니다.  
> **시스템이 최소 품질 조건을 통과했는지 자동으로 확인하는 것**이 목적이다.

### 중요한 포인트

오늘의 목적은:

```text
완벽한 평가 시스템 ❌
조건에 따라 흐름이 바뀌는 경험 ✅
```

### 완료 기준
- [ ] `review` Node 추가
- [ ] 정상/실패를 나타내는 상태값 추가
- [ ] Conditional Edge 1개 연결
- [ ] 정상 입력으로 END까지 이동 확인

### 포트폴리오 확장 — Human Review 기록

최종 포트폴리오에서는 사람이 검수했다는 사실을 DB에 남긴다.

예:

```text
review_status
- pending
- approved
- edited
- rejected

review_comment
reviewed_at
```

흐름:

```text
AI 피드백 생성
↓
pending
↓
강사 검토
├─ 그대로 사용 → approved
├─ 수정 후 사용 → edited
└─ 사용하지 않음 → rejected
```

이 데이터가 쌓이면 나중에:

```text
AI 초안 승인률
수정률
거절률
```

을 실제 수치로 계산할 수 있다.

### 30초 설명

> 일반 Workflow는 정해진 순서대로만 움직이지만, Agent식 흐름은 현재 결과를 보고 다음 행동을 바꿀 수 있습니다. 여기서는 피드백 결과가 정상인지 확인한 뒤 저장하거나 다시 검색하도록 분기를 만들었습니다.

---

## 작업 3 — Logging 넣고 일부러 오류 내보기
**시간: 25분**

### 왜 Logging을 하나

실무에서는:

```text
"안 됩니다"
```

보다

```text
어디까지 실행됐고
어디서 실패했는지
```

가 중요하다.

### 최소 로그 위치

```text
feedback request received
lesson record loaded
child loaded
RAG search completed
LLM generation completed
feedback saved
```

가능하면 각 요청에 `run_id`를 하나 붙인다.

```text
run_id
request_started_at
rag_completed_at
llm_completed_at
request_completed_at
status
error_stage
```

최종 포트폴리오에서는 이 로그를 이용해:

```text
평균 응답시간
실패 단계
재시도 횟수
E2E 성공률
```

을 설명할 수 있게 한다.

### 오류 테스트

일부러:

```json
{
  "lesson_record_id": 999999
}
```

보낸다.

현재 API의 404 처리와 로그를 같이 확인한다.

### 완료 기준
- [ ] 정상 요청 로그 확인
- [ ] 없는 수업기록 요청
- [ ] 어느 단계에서 멈췄는지 설명 가능

### 오늘 Git 저장

```bash
git add .
git commit -m "feat: add LangGraph workflow and logging"
```

### DAY 2 최종 30초 설명

> 기존에는 Router 안에서 검색과 생성이 순서대로 실행됐습니다. 이를 LangGraph의 Node로 분리하고 State로 데이터를 전달했습니다. Review 결과에 따라 다음 동작을 선택하도록 조건 분기를 만들었고, 로그를 추가해 어느 단계에서 문제가 발생했는지 추적할 수 있게 했습니다.

---

# DAY 3 — n8n 자동화 + Docker + 전체 흐름 설명

## 오늘의 목표

> **사람이 직접 API를 호출하는 프로젝트에서, 자동으로 실행되고 다른 환경에서도 돌릴 수 있는 프로젝트까지 경험한다.**

오늘 다룰 기술:

```text
n8n
Webhook
HTTP Request
Docker
Docker Compose
Environment Variable
Dependency
Git
End-to-End Test
```

---

## ▶ 작업 1 — n8n에서 Kids_Feedback API 자동 호출
**시간: 30분**

### 현재

```text
사람
↓
Swagger
↓
POST /feedbacks/generate
```

### 바꿀 흐름

```text
Webhook
↓
n8n
↓
HTTP Request
↓
FastAPI
↓
Feedback 생성
```

### n8n 최소 Workflow

Node 1:

```text
Webhook
```

Node 2:

```text
HTTP Request
```

HTTP Method:

```text
POST
```

API:

```text
http://localhost:8000/feedbacks/generate
```

Body 예:

```json
{
  "lesson_record_id": 1
}
```

### 여기서 이해할 기술

```text
Webhook
= 어떤 사건이 발생했음을 받는 입구

HTTP Request
= n8n이 FastAPI에게 일을 요청

FastAPI
= 실제 기능 실행
```

### 완료 기준
- [ ] n8n Workflow 실행
- [ ] n8n에서 FastAPI POST 호출
- [ ] 피드백 결과가 n8n에 돌아옴

### 30초 설명

> FastAPI는 피드백 생성 기능을 제공하고, n8n은 그 기능을 언제 실행할지 연결합니다. Webhook으로 시작한 Workflow가 HTTP POST로 Kids_Feedback API를 호출하도록 만들었습니다.

---

## 작업 2 — Docker로 실행환경 묶기
**시간: 40분**

### 먼저 문제 이해

현재 내 PC에는 이미:

```text
Python
FastAPI
SQLAlchemy
Gemini SDK
PostgreSQL
환경변수
```

가 설치되어 있다.

다른 PC에는 없을 수 있다.

그래서 Docker를 사용한다.

### 새 파일

```text
Dockerfile
docker-compose.yml
.env.example
```

### 목표 구조

```text
docker compose
├─ api
│  └─ FastAPI
└─ db
   └─ PostgreSQL
```

### 이때 반드시 확인할 것

현재 `pyproject.toml`에 실제 사용하는 dependency가 모두 기록되어 있는지 확인한다.

코드에서 사용하는 예:

```text
fastapi
sqlalchemy
psycopg2
python-dotenv
google-genai
langgraph
```

**필요한 것만 현재 환경 기준으로 추가한다.**

### 핵심 명령어

```bash
docker compose build
```

뜻:

```text
Dockerfile을 보고 실행환경 만들기
```

```bash
docker compose up
```

뜻:

```text
정의한 컨테이너 실행
```

```bash
docker ps
```

뜻:

```text
현재 실행 중인 컨테이너 확인
```

```bash
docker compose logs
```

뜻:

```text
컨테이너 로그 확인
```

### 완료 기준
- [ ] Docker image build 성공
- [ ] 최소 FastAPI container 실행
- [ ] `/health` 응답 확인

> 40분 안에 PostgreSQL까지 Docker 연결이 막히면 실패가 아니다.  
> **API Container 실행 + DB 연결이 왜 달라지는지 이해**하면 오늘 최소 목표는 달성이다.

### 30초 설명

> Docker는 코드를 만드는 도구가 아니라 실행환경을 묶는 도구입니다. 필요한 패키지와 실행 방법을 Dockerfile에 기록하면 다른 환경에서도 같은 방식으로 FastAPI를 실행할 수 있습니다.

---

## 작업 3 — 전체 End-to-End 실행 + 3분 설명
**시간: 30분**

### 마지막으로 한 번만 처음부터 끝까지 실행

```text
n8n
↓
POST /feedbacks/generate
↓
FastAPI
↓
PostgreSQL
↓
RAG
↓
LangGraph
↓
Gemini
↓
Feedback JSON
↓
PostgreSQL 저장
↓
로그 확인
```

### 실행하면서 체크

- [ ] n8n이 요청을 보냄
- [ ] FastAPI가 받음
- [ ] LessonRecord 조회
- [ ] Child 조회
- [ ] RAG 검색
- [ ] RAG Context가 Prompt에 들어감
- [ ] LLM JSON 생성
- [ ] LangGraph review 통과
- [ ] Feedback DB 저장
- [ ] 로그에서 전체 흐름 확인
- [ ] 실패 요청 1개가 의도한 단계에서 멈춤
- [ ] 가능하면 `run_id`로 한 요청의 전체 로그를 추적
- [ ] 응답시간을 한 번 기록

### 최종 Git 저장

```bash
git add .
git commit -m "feat: add automation and container workflow"
git push
```


---

# 3일 이후 — 채용 포트폴리오 마감 단계

이 단계부터는 “기술을 해봤다”가 아니라 **결과를 증명한다.**

## 1. 테스트 케이스 30~50개 만들기

실제 개인정보가 아닌 샘플 데이터로 구성한다.

예:

```text
정상 수업 기록
최근 기록이 적은 학생
RAG 근거가 잘 검색되는 경우
RAG 근거가 부족한 경우
존재하지 않는 lesson_record_id
LLM 응답 형식이 깨진 경우
필수 필드가 빠진 경우
```

처음에는 10개로 시작하고, 최종 제출 전 30~50개까지 늘린다.

---

## 2. 포트폴리오 평가 지표 만들기

최소 아래 지표를 실제 실행 결과로 계산한다.

```text
1. API E2E 성공률
2. 필수 JSON 형식 성공률
3. RAG 검색 성공률
4. Human Review 승인률
5. Human Review 수정률
6. 평균 응답시간
```

가능하면 추가:

```text
RAG 근거가 실제 생성 내용에 반영된 비율
재시도 발생률
실패 단계별 건수
```

> 측정하지 않은 수치를 임의로 만들지 않는다.  
> 결과가 낮아도 `문제 → 원인 → 개선`을 설명할 수 있으면 포트폴리오 가치가 있다.

---

## 3. Human Review 결과를 실제 DB에 남기기

최종적으로 아래 상태를 사용한다.

```text
pending
approved
edited
rejected
```

필요하면 API 추가:

```text
PATCH /feedbacks/{feedback_id}/review
```

입력 예:

```json
{
  "review_status": "edited",
  "review_comment": "보호자용 문장을 더 쉽게 수정"
}
```

---

## 4. 운영 실패 시나리오 3개 만들기

최소 3개는 README에 남긴다.

```text
CASE 1
없는 lesson_record_id
→ 404
→ DB 조회 단계에서 중단

CASE 2
RAG 검색 결과 없음
→ fallback
→ 기본 지도 기준 또는 재검색

CASE 3
LLM 응답 형식 오류
→ review 실패
→ retry 또는 fallback
```

가능하면 추가:

```text
n8n → FastAPI 연결 실패
DB 연결 실패
외부 API timeout
중복 요청
```

README에는 “무엇이 실패했는지”보다:

```text
어떻게 발견했는가
어디서 멈췄는가
어떻게 복구했는가
```

를 적는다.

---

## 5. Cloud 배포

3일 안에는 하지 않아도 된다.

최종 제출 전에는 최소 FastAPI API가 외부에서 호출되도록 만든다.

후보:

```text
Render
Railway
Google Cloud Run
```

DB:

```text
Managed PostgreSQL
```

최종 확인:

```text
Public URL
↓
/health
↓
/docs
↓
POST /feedbacks/generate
```

> AWS 정식 인프라 구축이 목표가 아니다.  
> **다른 사람이 내 PC 없이도 실행 결과를 확인할 수 있게 만드는 것**이 목표다.

---

## 6. 최종 README 구조

최종 GitHub README에서는 `DAY 1 / DAY 2 / DAY 3`를 앞에 내세우지 않는다.

```text
# Kids Feedback

1. Problem
2. AS-IS
3. TO-BE
4. Architecture
5. Data Flow
6. Why These Technologies
7. RAG
8. LangGraph Workflow
9. Human Review
10. Error / Retry / Logging
11. Evaluation
12. Results
13. Deployment
14. Demo
15. Limitations
16. Next Improvements
```

### README 첫 화면에서 바로 보여줄 것

```text
문제
↓
한 줄 해결책
↓
Architecture 이미지
↓
실제 결과 수치
↓
Demo 링크
```

---

## 7. 최종 포트폴리오 완료 기준

```text
[ ] 문제를 한 문장으로 설명 가능
[ ] AS-IS / TO-BE 작성
[ ] Architecture 작성
[ ] API → DB → RAG → LLM → Review → DB 전체 동작
[ ] Human Review 상태 저장
[ ] 정상 / 실패 / fallback 케이스 확인
[ ] 테스트 케이스 30~50개
[ ] 평가 수치 기록
[ ] Docker 실행
[ ] Cloud URL 확보
[ ] README 작성
[ ] 30초 설명 가능
[ ] 3분 설명 가능
[ ] GitHub에서 다른 사람이 실행 방법을 이해할 수 있음
```

---

# 3분 프로젝트 설명 템플릿


## 1. 문제

> 강사가 학생별 수업 피드백을 작성할 때 최근 수업 기록을 다시 확인하고 관련 지도 기준을 찾아 초안을 작성하는 반복 업무를 줄이기 위해 만든 프로젝트입니다.

### AS-IS

```text
수업 기록 확인
→ 최근 기록 확인
→ 지도 기준 검색
→ 직접 작성
→ 수정
→ 저장
```

### TO-BE

```text
수업 기록 ID
→ 학생/최근 기록 자동 조회
→ RAG 검색
→ LLM 초안
→ LangGraph 검토
→ Human Review
→ 저장
```

## 2. 데이터 흐름

```text
수업기록 ID
↓
FastAPI
↓
PostgreSQL에서 학생·수업 조회
↓
RAG 검색
↓
관련 지도 기준 확보
↓
Prompt
↓
LLM
↓
피드백 JSON
↓
검토
↓
DB 저장
```

## 3. 기술 선택 이유

### FastAPI
> 외부 요청을 받고 Python 기능을 실행하기 위한 API 서버로 사용했습니다.

### PostgreSQL
> 학생, 수업 기록, 생성 피드백을 관계형 데이터로 저장하기 위해 사용했습니다.

### SQLAlchemy
> Python 코드에서 PostgreSQL 데이터를 조회하고 저장하기 위해 사용했습니다.

### RAG
> LLM이 학생 정보만 보고 임의로 답하는 것이 아니라 관련 지도 기준을 먼저 검색하게 하기 위해 사용했습니다.

### LLM
> 학생 정보, 최근 기록, 검색 근거를 바탕으로 개인화된 피드백을 JSON으로 생성합니다.

### LangGraph
> 검색, 생성, 검토 단계를 분리하고 결과에 따라 다음 동작을 선택하기 위해 사용했습니다.

### n8n
> 사람이 직접 API를 누르지 않아도 업무 이벤트를 기준으로 자동 실행되도록 연결했습니다.

### Docker
> 실행환경 차이를 줄이고 같은 환경에서 애플리케이션을 실행하기 위해 사용했습니다.

### Logging
> 요청이 어느 단계까지 처리됐고 어디서 실패했는지 추적하기 위해 사용했습니다.

### Human Review
> AI가 만든 피드백을 자동으로 바로 확정하지 않고, 강사가 승인·수정·거절할 수 있도록 최종 판단 단계를 분리했습니다.

## 4. 결과

최종 포트폴리오에서는 실제 측정한 숫자로 채운다.

```text
테스트 케이스: __건
API E2E 성공률: __%
JSON 형식 성공률: __%
RAG 검색 성공률: __%
Human Review 승인률: __%
Human Review 수정률: __%
평균 응답시간: __초
```

## 5. 한계와 다음 개선

예:

```text
실제 교육 현장 데이터가 아닌 샘플 데이터 기반
RAG 평가 데이터 규모가 작음
사용자 피드백 데이터가 아직 적음
추후 실제 사용자 평가와 더 큰 테스트셋 필요
```

---

# 3일 후 “해봤다” 기준

아래를 전부 외울 필요 없다.

직접 경험했으면 체크한다.

```text
[ ] FastAPI 서버를 직접 실행했다.
[ ] Swagger에서 API를 직접 호출했다.
[ ] JSON이 Pydantic을 거쳐 Router로 들어가는 것을 추적했다.
[ ] PostgreSQL 조회 흐름을 확인했다.
[ ] ORM과 SQL의 관계를 설명할 수 있다.
[ ] RAG 검색 결과를 직접 확인했다.
[ ] RAG 검색 결과를 Prompt에 연결했다.
[ ] LLM JSON 결과를 DB에 저장했다.
[ ] LangGraph State / Node / Edge를 직접 만들었다.
[ ] Conditional Edge를 한 번 구현했다.
[ ] 로그로 오류 위치를 확인했다.
[ ] n8n에서 FastAPI를 호출했다.
[ ] Docker로 FastAPI를 실행했다.
[ ] Git commit / push를 했다.
[ ] 전체 시스템을 3분 안에 설명했다.
[ ] 정상 요청과 실패 요청의 차이를 설명할 수 있다.
[ ] 내가 직접 바꾼 코드와 이유를 설명할 수 있다.
[ ] 최종 포트폴리오에서 추가할 평가/배포 항목을 구분할 수 있다.
```

---

# 이번 3일에 하지 않을 것

```text
Python 문법 강의 완강
SQL 문법 전체 암기
LangGraph 고급 기능
멀티 Agent
Kubernetes
React UI
AWS 정식 인프라 구축
대규모 모니터링
성능 최적화
완벽한 pgVector 전환
```

이건 나중에 한다.

단, **간단한 Cloud 배포(Render / Railway / Cloud Run 등)** 는 3일 학습이 끝난 뒤 포트폴리오 마감 단계에서 진행한다.

이번 목표는:

> **“기술 이름을 많이 아는 것”이 아니라  
> “한 요청이 시스템을 끝까지 지나가는 것을 직접 만들어보고 설명하는 것.”**

---

# 막혔을 때 규칙

## 1. 10분 이상 같은 오류를 보고 있으면

다음 세 가지만 적는다.

```text
내가 하려던 것:
실제로 나온 것:
마지막 정상 단계:
```

## 2. 에러는 이렇게 본다

```text
명령어 실행
↓
에러 마지막 줄
↓
파일명
↓
줄 번호
↓
그 줄의 입력값
```

## 3. 오늘 목표를 줄여도 된다

예:

```text
원래 목표:
Docker + PostgreSQL 완전 연결

↓ 막힘

오늘 최소 목표:
FastAPI Container 실행 + /health 확인
```

작은 기능 하나가 끝나면 그 작업은 완료다.

---

# 매일 끝나기 전 5분 복습

노트 정리하지 않는다.

코드를 닫고 아래 3개만 말한다.

```text
1. 오늘 데이터는 어디서 어디로 이동했나?
2. 오늘 사용한 기술은 왜 필요했나?
3. 오늘 내가 직접 바꾼 것은 무엇인가?
```

말이 막힌 부분만 다음날 첫 5분에 다시 확인한다.
