# Kids_Feedback — 3일 실무기술 체험 플랜
> 목표: 3일 안에 기술을 “완벽히 공부”하는 것이 아니라, **Kids_Feedback 프로젝트 안에서 실제로 실행 → 추적 → 수정 → 구현 → 설명**까지 한 번 경험한다.

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
학생 + 수업기록 조회
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
PostgreSQL Feedback 저장
        ↓
   Human Review

Docker
→ 실행 환경

Logging
→ 처리 단계·오류 추적

Git
→ 변경 이력
```

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

예:

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

### 최종 Git 저장

```bash
git add .
git commit -m "feat: add automation and container workflow"
git push
```

---

# 3분 프로젝트 설명 템플릿

## 1. 문제

> 강사가 학생별 수업 피드백을 반복해서 작성해야 하는 업무를 줄이기 위해 만든 프로젝트입니다.

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
AWS 정식 배포
대규모 모니터링
성능 최적화
완벽한 pgVector 전환
```

이건 나중에 한다.

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
