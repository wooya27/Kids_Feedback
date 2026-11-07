# 채용 포트폴리오 플랜 (v2) — DAY 3 학습문서

> 기준 문서: `plan/Kids_Feedback_채용포트폴리오_업데이트_v2.md`
> DAY 3 목표: **사람이 직접 호출하던 프로젝트를, 자동 실행되고 다른 환경에서도 도는 프로젝트로 만든다. (n8n + Docker + E2E)**

> ⚠️ **상태:** 이 PC에 n8n/Docker가 아직 **설치 안 됨.** 그래서 오늘은 **핵심 파일 작성 + 설명**까지 완료했고,
> **실제 실행(`docker compose up`, n8n 워크플로)** 은 설치 후에 하면 바로 돌아가는 상태로 준비해 둠.

---

## 🧭 DAY 3 안에서 지금 위치

| 작업 | 내용 | 상태 |
|---|---|---|
| 작업 1 | n8n에서 Kids_Feedback API 자동 호출 | 🟡 n8n 컨테이너 기동 완료(5679), GUI 워크플로 작성만 남음 |
| **작업 2** | **Docker로 실행환경 묶기** | ✅ **빌드+실행 성공** (api 컨테이너 /health ok) |
| **작업 3** | **전체 E2E 실행** | ✅ **컨테이너에서 피드백 생성 완주** (id=1, elapsed 14.55s) |

### 🏁 전체 스택 Docker 실행 (2026-11-08)
| 컨테이너 | 호스트 포트 | 내부 | 상태 |
|---|---|---|---|
| api (FastAPI) | 8001 | 8000 | E2E 완주 |
| db (PostgreSQL 16) | 5432* | 5432 | seed.py로 유리+기록2건 |
| n8n 2.46.6 | 5679 | 5678 | 부팅 완료 |
*호스트 5432는 로컬 Postgres가 점유 → 컨테이너 db는 내부망(db:5432)으로만 접근. seeding은 `docker compose exec api python seed.py`로.

### 🐞 Docker가 잡아낸 버그 (포폴 스토리) — 라이브러리 버전 차이
- 증상: 컨테이너 E2E에서 `400 JSON mode is not enabled for api version v1. Use v1beta`.
- 원인: 컨테이너가 받은 `google-genai`는 최신(3.x)이라 기본 API가 `v1` → JSON 모드 미지원. 로컬은 구버전(2.10)이라 기본 `v1beta`라 됐음.
- 해결: `genai.Client(..., http_options={"api_version": "v1beta"})` 명시 → 버전 무관 동작.
- 교훈: **"내 PC에선 됨"의 정체(의존성 버전 차이)를 Docker E2E가 잡아냈다.** = Docker를 쓰는 이유 그 자체.

> ✅ **실행 결과(2026-11-08):** `docker compose up -d --build db api` → 이미지 빌드 성공,
> `kids_feedback-api`(host 8001→컨테이너 8000) + `kids_feedback-db`(postgres:16) 기동.
> `http://127.0.0.1:8001/health` → `{"status":"ok"}`. 컨테이너 로그에 `Application startup complete`
> = **api 컨테이너가 db 컨테이너에 연결 성공**(env `DATABASE_URL`의 host=`db`가 작동).
> ⚠️ 포트: 이 PC는 8000을 다른 앱이 점유 → compose에서 `8001:8000`으로 매핑.
> ⚠️ db는 빈 상태 → `/feedbacks/generate`는 데이터 seeding 전엔 404(정상).

---

## 📋 중간보고서 — DAY 3 작업 2 (Docker)

### 무엇을 했나
다른 PC에서도 똑같이 돌게 **실행환경을 파일로 고정**했다. 그 과정에서 Docker가 강제하는 **진짜 문제 2개**를 해결.

### 해결한 문제 2개 (핵심 학습)
1. **의존성 미기록** — `pyproject.toml`에 `fastapi`, `ruff`만 있었음. 코드가 쓰는 `sqlalchemy/psycopg2/google-genai/langgraph`는 venv엔 있지만 기록이 없어 **컨테이너엔 없음**.
   → `requirements.txt`에 실제 사용 패키지를 모두 적음 + `pyproject.toml`도 맞춤.
2. **DB 주소 하드코딩** — `database.py`가 `host="localhost"`. Docker에선 api 컨테이너의 localhost는 자기 자신 → db 컨테이너를 못 찾음.
   → `DATABASE_URL`을 **환경변수로** 빼고(없으면 localhost 기본값), compose에서 host를 `db`(서비스 이름)로 주입.

### 만든/고친 파일
| 파일 | 역할 |
|---|---|
| `Dockerfile` | 실행환경 만드는 설명서 (파이썬→패키지설치→소스복사→실행) |
| `docker-compose.yml` | api + db + n8n 3개 컨테이너를 한 번에 정의·연결 |
| `requirements.txt` | 컨테이너가 설치할 실제 패키지 목록 |
| `.env.example` | 비밀값 템플릿 (복사해서 .env 만들기) |
| `database.py` | DATABASE_URL을 env에서 읽도록 수정 (fallback=localhost) |
| `pyproject.toml` | 실제 의존성 반영 |

---

## ⌨️ 꼭 알아야 하는 명령어 (Docker)

```bash
docker compose build      # Dockerfile 보고 실행환경(이미지) 만들기
docker compose up         # 정의한 컨테이너들 실행  (--build 붙이면 빌드+실행)
docker compose up -d      # 백그라운드로 실행
docker ps                 # 지금 돌아가는 컨테이너 목록
docker compose logs -f    # 컨테이너 로그 실시간 보기
docker compose down       # 다 내리기 (-v 붙이면 볼륨=데이터까지 삭제)
```

**실행 순서 (설치 후):**
```powershell
Copy-Item .env.example .env     # .env 만들고 GEMINI_API_KEY 채우기
docker compose up --build       # 빌드 + 실행
# → http://localhost:8000/health  (API 컨테이너 확인)
# → http://localhost:5678         (n8n 접속)
```
> ⚠️ Docker의 db는 **빈 상태**로 시작 → `/feedbacks/generate`는 데이터 없으면 404.
> **오늘 최소 목표 = API 컨테이너 떠서 `/health` ok.** (데이터 seeding은 이후 단계)

---

## 📋 중간보고서 — DAY 3 작업 1 (n8n)

### 흐름 바꾸기
```
[전]  사람 → Swagger → POST /feedbacks/generate
[후]  Webhook → n8n → HTTP Request → FastAPI → 피드백 생성
```

### n8n 최소 워크플로 (설치 후 만들 것)
```
Node 1: Webhook        (어떤 사건이 발생했음을 받는 입구)
Node 2: HTTP Request   (n8n이 FastAPI에게 일을 요청)
  - Method: POST
  - URL: http://api:8000/feedbacks/generate   (Docker면 'api', 로컬이면 'localhost:8000')
  - Body(JSON): { "lesson_record_id": 1 }
```

### 완료 기준 (설치 후)
- [ ] n8n Workflow 실행
- [ ] n8n에서 FastAPI POST 호출
- [ ] 피드백 결과가 n8n에 돌아옴

---

## 🧠 꼭 알아야 하는 개념 (DAY 3)

| 개념 | 한 줄 정의 | 왜 AX·DX 포폴에 중요 |
|---|---|---|
| **Docker image** | 실행환경을 통째로 구운 "붕어빵 틀" | 내 PC 없이도 같은 결과 재현 |
| **Container** | 이미지로 찍어낸 실제 실행 인스턴스 "붕어빵" | 격리된 환경에서 실행 |
| **docker compose** | 여러 컨테이너를 한 설계도로 묶어 같이 실행 | api+db+n8n 한 번에 |
| **서비스 이름 통신** | 같은 compose 안에선 `localhost` 아니라 **서비스명**(db, api)으로 부름 | 컨테이너 간 연결의 핵심 |
| **환경변수(.env)** | 비밀값·환경차이를 코드 밖으로 분리 | 키를 깃에 안 올리고 환경별 설정 |
| **volume** | 컨테이너 꺼져도 데이터 보존 | DB 데이터 유지 |
| **Webhook** | 사건 발생을 받는 입구(URL) | 사람이 안 눌러도 자동 트리거 |
| **n8n** | 노드 연결로 업무 자동화하는 도구 | "자동 실행" = 업무 자동화 어필의 핵심 |

> **왜 n8n/Docker인가 (면접 한 줄):**
> Docker는 "내 PC에서만 됨"을 없애 **어디서든 같은 실행환경**을 보장하고,
> n8n은 **사람이 API를 직접 누르지 않아도 업무 이벤트로 자동 실행**되게 연결한다.
> → AS-IS(수동)에서 TO-BE(자동)로 가는 마지막 연결 고리.

## 🎤 30초 설명 (DAY 3)
> Docker는 코드를 만드는 도구가 아니라 실행환경을 묶는 도구다. 필요한 패키지와 실행법을 Dockerfile에 적으면 다른 환경에서도 같은 방식으로 FastAPI가 뜬다.
> n8n은 그 API를 "언제 실행할지" 연결한다. Webhook으로 시작한 워크플로가 HTTP POST로 우리 API를 자동 호출한다.

---

## 📝 설치 안내 (실제 실행하려면)
- **Docker Desktop (Windows):** 공식 사이트 docker.com → "Docker Desktop" 다운로드·설치 후 실행.
  - 설치 확인: 터미널에서 `docker --version`, `docker compose version`
- **n8n:** 위 `docker-compose.yml`에 이미 n8n 서비스 포함 → Docker만 깔면 같이 뜸.
  - (Docker 없이 쓰려면 Node.js 설치 후 `npx n8n` 으로도 실행 가능)
- 검색 키워드: "Docker Desktop Windows 설치", "n8n docker compose", "n8n webhook http request node"

## 🔗 관련
- env 분리한 DB 설정: `database.py`
- 로그 수치(응답시간·실패단계): `study/채용포폴_DAY2.md` → 마감단계 평가지표로 집계
- DAY3 작업3(E2E) + 마감단계(테스트케이스·평가지표·Cloud배포·README)는 설치/데이터 준비 후
