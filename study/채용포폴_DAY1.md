# 채용 포트폴리오 플랜 (v2) — DAY 1 학습문서

> 기준 문서: `plan/Kids_Feedback_채용포트폴리오_업데이트_v2.md`
> DAY 1 목표: **API 요청 하나가 DB → RAG → LLM → DB 저장까지 어떻게 이동하는지 추적하고, 끊겨 있던 `RAG → Prompt` 연결을 완성한다.**

---

## 🧭 DAY 1 안에서 지금 위치

| 작업 | 내용 | 상태 |
|---|---|---|
| 작업 1 | 서버 실행 + 파일 호출 순서 추적 | ✅ 이미 함 (Day 1~5 때) |
| 작업 2 | PostgreSQL 데이터가 Python으로 오는 과정 추적 | ✅ 이미 함 (Day 3 ORM 조회) |
| **작업 3** | **🔥 RAG 검색 결과(`found`)를 실제 Prompt에 연결** | ✅ **이번에 완료** |

> 작업 1·2는 이미 구현/이해한 흐름이라 "다시 만들지 않는다" 원칙대로 복습으로 대체.
> 실제로 손댄 건 **작업 3**이고, 그게 그동안 멈춰 있던 지점이었음.

---

## 📋 중간보고서 — DAY 1 작업 3

### 무엇을 했나
RAG가 찾아온 지도 자료(`found`)가 프롬프트까지 전달되지 않고 **버려지던 문제**를 고쳤다.

### 고치기 전 (문제)
```
라우터:  found = rag_search(question)   ← 만들어졌지만
라우터:  prompt = build_prompt(child, records)   ← found를 안 넘김 → 버려짐
프롬프트: build_prompt(child, records)   ← found 받을 자리가 없음
```

### 고친 후 (해결) — 파일 2개, 3곳
| 파일 | 위치 | 변경 |
|---|---|---|
| `prompt_service.py` | `def` 줄 | `build_prompt(child, records)` → `build_prompt(child, records, found)` |
| `prompt_service.py` | 프롬프트 본문 | `[지도 가이드]\n{found}` 구역 추가 (`[최근 수업 기록]`과 `[작성 규칙]` 사이) |
| `routers/feedbacks_router.py` | 호출 줄 | `build_prompt(child, records)` → `build_prompt(child, records, found)` |

### 데이터 흐름 (이번에 이은 부분 🔗)
```
lesson_record_id 입력
      ↓
LessonRecord 조회 → child_id → Child 조회
      ↓
question 문장 생성 (child.personality + record.activity)
      ↓
found = rag_search(question)        ← RAG가 지도 자료 1조각 찾음
      ↓  🔗 이번에 연결한 곳
build_prompt(child, records, found) ← found가 [지도 가이드]로 들어감
      ↓
Gemini → JSON 피드백
      ↓
Feedback 테이블 저장
```

### 완료 기준 체크
- [x] `found`가 더 이상 버려지지 않는다
- [x] 프롬프트에 `[지도 가이드]`가 들어간다
- [x] 문법 이상 없음(ast 파싱 통과)
- [x] `/feedbacks/generate` 실제 호출 성공 → 피드백 3필드 생성 + DB 저장(id:6) 확인 (TypeError 없음 = 3-인자 전달 OK)
- [ ] 커밋: `git commit -m "feat: connect RAG context to feedback prompt"`

---

## ⌨️ 꼭 알아야 하는 명령어

```powershell
# 서버 실행 (PowerShell) — ⚠️ main.py가 api/ 폴더로 옮겨졌으므로 api.main:app
cd C:\Users\USER\GITHUB\Kids_Feedback
$env:PYTHONIOENCODING="utf-8"             # 한글 깨짐 방지 (cp949 → utf-8)
.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8001
#   ↑ 반드시 venv 파이썬으로. 8000번은 다른 프로젝트(audit 앱)가 쓰고 있어서 8001 사용.

# 문법만 빠르게 검사 (서버 안 띄우고)
python -c "import ast; ast.parse(open('prompt_service.py', encoding='utf-8').read())"

# 확인 주소
# http://127.0.0.1:8001/health   → 서버 살아있나  (→ {"status":"ok"})
# http://127.0.0.1:8001/docs     → Swagger, 여기서 API 직접 호출

# 저장
git add .
git commit -m "feat: connect RAG context to feedback prompt"
```

- `uvicorn api.main:app` = `api 폴더 안 main.py`의 `app 변수`를 실행. (`패키지.파일:변수`)
- `--reload` = 코드 저장할 때마다 서버 자동 재시작 (개발용).
- 💡 오늘 함정: `uvicorn main:app` → `Could not import module "main"`. 이유는 **main.py가 루트에 없고 api/로 옮겨져서.** 모듈 경로는 "파일 위치" 기준.
- 💡 또 다른 함정: 8000번에 엉뚱한 앱(audit)이 떠 있어서 `/health`가 `Not Found`로 보였음 → **포트는 프로젝트마다 다른 서버가 잡을 수 있다.** `/openapi.json` 경로 목록으로 "이게 내 앱 맞나" 확인.

---

## 💻 꼭 알아야 하는 코드

### 1) 함수의 "받는 쪽"(def)과 "넘기는 쪽"(호출)은 괄호 개수가 같아야 한다
```python
# 받는 쪽 (정의)
def build_prompt(child, records, found):   # 자리 3개
    ...

# 넘기는 쪽 (호출)
prompt = build_prompt(child, records, found)   # 값 3개
```
> 한쪽만 고치면 → `TypeError: build_prompt() takes 2 positional arguments but 3 were given`
> **외울 것: 호출 = 이름 + 괄호. 받는 자리 수 = 넘기는 값 수.**

### 2) f-string 안에 변수 끼워넣기
```python
prompt = f"""[지도 가이드]
{found}

[작성 규칙]
..."""
```
> `f"""..."""` 안의 `{found}`는 그 변수의 실제 값으로 바뀐다.
> 프롬프트 바깥 JSON 예시의 `{{ }}`는 "진짜 중괄호 글자"라서 두 번 쓴 것(이스케이프).

---

## 🧠 꼭 알아야 하는 개념

| 개념 | 한 줄 정의 | 왜 필요했나 |
|---|---|---|
| **매개변수(parameter)** | 함수가 값을 받는 "빈 자리" | `found`를 받으려면 def에 자리를 먼저 뚫어야 함 |
| **인자(argument)** | 호출할 때 그 자리에 실제로 넣는 값 | `build_prompt(..., found)`의 `found` |
| **RAG → Prompt 연결** | 검색한 근거를 LLM이 보도록 프롬프트에 끼우는 것 | 이게 없으면 RAG를 돌려도 LLM이 안 봄 = RAG 한 보람 없음 |
| **프롬프트(prompt)** | LLM에게 주는 "주문서" 글 한 덩어리 | 아이 정보+기록+지도 가이드를 한 글로 조립 |
| **f-string** | `f"...{변수}..."`로 변수를 글에 끼워넣는 문법 | 동적으로 프롬프트를 만들기 위해 |

---

## 🎤 30초 설명 (코드 닫고 말하기)
> 사용자가 수업 기록 ID를 보내면 FastAPI가 받아서 PostgreSQL에서 수업과 학생을 조회한다.
> 학생 성향과 활동으로 질문 문장을 만들어 RAG로 관련 지도 기준을 검색한다.
> **이번에 그 검색 결과를 `build_prompt`의 세 번째 자리로 넘겨 `[지도 가이드]`로 프롬프트에 넣었다.**
> Gemini가 JSON 피드백을 만들고 Feedback 테이블에 저장한다.

## 🔗 관련
- 같은 약점 재등장: **함수 호출** → 메모리 `project_func_call_revisit`
- 이전 RAG 구현: `study/day9.md`, `study/day10.md`
