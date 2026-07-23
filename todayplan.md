# 오늘 작업 계획 — 2026-07-22 (수)

## 🎯 이번 목표: Day 10 ① — 찾은 조각을 LLM에 넣어 최종 피드백 만들기 (RAG 결승선)
> 지금은 확장 금지. search.py에서 뽑은 조각 1개 → 프롬프트에 끼워넣기 → generate_feedback() 호출. 이 흐름 하나만 닫는다.
> 손대지 말 것: 커밋 안 된 Day 9 ④, 아직 안 닫힌 Day 7 README.

## 세션 (30분) — RAG + LLM 통합 첫 연결  ✅ 완료 (Day 10 결승선 통과 🏁)
- [x] 찾은 조각을 변수에 담기 (`found = data[best]["text"]`)
- [x] llm_service의 `generate_feedback` 재사용 (함수 옮겨옴)
- [x] 프롬프트 문자열 만들기: f-string에 `{found}` + `{question}` 끼워넣기
- [x] 호출 → 결과 print
- [x] 결과 확인: 위축형 가이드를 근거로 한 피드백 문장이 출력됨 ✅
- 📝 `study/day10.md` 0번(전체 흐름 지도) + 2번(오늘 한 것)에 정리
- 💡 큰 깨달음: RAG 검색은 이미 만든 것(Day 9 ④) → 다음엔 함수로 포장해 웹에 옮기기만

- ✅ (추가로 함) 검색 3단계를 `def rag_search(question)` 함수로 포장 완료
- ✅ 커밋·푸시까지 끝냄 (`5c9fd29`, `ccee9a4`) — working tree clean

---

# 📋 다음에 할 일 (뭐해야하냐 물으면 여기부터)

## 🔜 다음 세션 — Day 10 마무리: RAG를 웹서버에 붙이기 (40~60분)
> 목표: 지금 `search.py`에만 있는 `rag_search()`를 실제 피드백 API(`feedbacks_router.py`)의 ④ 자리에 끼워서, 웹 요청 한 번에 RAG까지 돌게 만들기.
> 지금은 확장 금지 — 이 연결 하나만 닫는다.

- [x] `rag_search()`를 재사용 가능하게 옮기기 → **`rag/rag_service.py` 신규 모듈로 분리 완료** ✅
      - 옮긴 것: import 5개 / `data`(vectors.json) / `client` / `embed_feedback` / `cos_sim` / `rag_search`
      - 안 옮긴 것(중요): 확인용 `print` 2줄, `generate_feedback`(llm_service 담당), 맨 아래 실행부
      - 💡 개념: **함수를 복사해도 그 함수가 쓰던 재료는 안 따라온다** (이름은 "그 파일 안에서만" 찾음)
      - 💡 모듈에 실행 코드를 두면 import 순간 API가 호출됨 → 모듈엔 `def`만
      - ✅ 확인: `python -c "...from Kids_Feedback.rag.rag_service import rag_search..."` → 조각 출력, 잡print 없음
      - ⚠️ 관찰: 짧은 질문("소심한 애가 처음으로 발표했어요")은 엉뚱한 조각(어린 동생)이 뽑힘 → 질문 문장 만들기 단계에서 다룰 것
- [x] `feedbacks_router.py`의 ④ 자리: 수업 기록으로 질문 문장 만들기 → `found = rag_search(질문)` ✅
      - 12번 줄 `from rag.rag_service import rag_search` / 33~34번 줄 `question` + `found`
      - 질문 문장 설계: `child.personality`(어떤 아이) + `record.activity`(무슨 상황) → 조각 생김새를 닮게
      - 🔴 여기서 막힌 것 = **함수 호출** (또 나옴!) → [[project_func_call_revisit]]
        1. `found = (question)` — 괄호만 있고 **이름이 없으면 호출이 아님**. `(5)`가 그냥 `5`인 것과 같음
        2. `from rag import rag_service`(파일 통째) vs `from rag.rag_service import rag_search`(함수만) 차이
        - 외울 것: **호출 = 이름 + 괄호. 한 몸.**

### 🔴 여기서 멈춤 (집중력 바닥) — 다음에 이어서
- [ ] `build_prompt(child, records)` 에 `found` 받을 자리 하나 추가 (`def build_prompt(child, records, found)`)
- [ ] 프롬프트의 `[작성 규칙]` 위에 `[지도 가이드]` 칸 만들고 `{found}` 끼워넣기
- [ ] 라우터 40번 줄도 같이 고치기: `build_prompt(child, records, found)`
      - ⚠️ 파일 2개를 **동시에** 고쳐야 함 (한 쪽만 고치면 `TypeError: 인자 개수 안 맞음`)
- ℹ️ 지금 에디터의 `"found" is not accessed` 경고는 정상 — 위 3줄 하면 사라짐
- [ ] Swagger `/feedbacks/generate` 로 테스트 → RAG 자료가 반영된 피드백 나오는지 확인
- [ ] 결과 확인: RAG 붙이기 전/후 피드백이 달라지는지 비교 ✅
- 끝나면: study/day10.md 에 "웹 통합" 파트 추가 + 커밋·푸시

## 📅 내일 — Day 11 준비: Streamlit "개념만" 보기 (코드 X, 30분)
> ⚠️ 새 기술(처음 배움). 내일은 **화면 만들기 전에 개념·감만 잡는 세션.** 코드는 그다음.
> 목표: "Streamlit이 뭐고 왜 쓰고, 우리 프로젝트에서 무슨 역할인지" 내 말로 설명할 수 있으면 끝.

- [ ] Streamlit이 뭔지 (파이썬만으로 웹 화면 만드는 도구 = 우리 5부품 중 ① 프론트엔드)
- [ ] 왜 쓰나: HTML/JS 몰라도 파이썬 몇 줄로 버튼·입력창·표가 나옴 → 데모/프로토타입에 최적
- [ ] 핵심 감만: `st.title()`, `st.text_input()`, `st.button()`, `st.write()` 뭐 하는 애들인지 눈으로
- [ ] 우리 그림에 위치시키기: Streamlit(화면) → FastAPI(API 호출) → 결과 표시 (day10.md 0번 지도의 ①↔②)
- [ ] 공식 문서 훑기: https://docs.streamlit.io (Get started)
- [ ] 완료 기준: "Streamlit은 ___이고, 우리 프로젝트에선 ___ 역할" 한 문장 말하기
- 📝 study 폴더에 Day11_예습_Streamlit.md 로 개념 메모 (선택)

---

# 🗺️ 전체 남은 로드맵 (참고용 — 세션마다 하나씩만)
- [ ] **Day 10 마무리** — RAG 웹 통합 (다음 세션, 40~60분)
- [ ] **Day 11** — Streamlit 개념(내일) → 화면1: 아이 목록·프로필·입력 (2~3시간)
- [ ] **Day 12** — Streamlit 화면2: 피드백 생성 버튼·카드·이력 (1.5~2시간)
- [ ] **Day 13** — 성장 그래프 + 데모 시나리오 (1~2시간)
- [ ] **Day 14** — README 최종 정리 (1시간)
- [ ] **Day 7** — 1주차 README (API 명세·ERD·회고) ← 계속 미뤄진 것 (30~40분)
> 진도 약 65~70%. 두뇌(백엔드+RAG)는 넘었고, 남은 실질 작업 ≈ 7~9시간(절반이 Streamlit).

---

# (이전) 오늘 작업 계획 — 2026-07-20 (월)

## 🎯 이번 목표: Day 9 ② `embed()` — 조각 1개 → 벡터
> for문 연습은 **건너뜀** (kids.py에서 이미 직접 써서 성공 → `study/연습_for문.md`는 막힐 때만 참고)
> 지금은 확장 금지. 조각 **1개**만 벡터로 바꾸고 닫는다. 전체 조각 8개 반복은 다음 세션.

## 세션 (30분) — embed_feedback() 마무리  ✅ 완료 (Day 9 ② 종료)
- [x] 죽은 코드 `embed(response)` 지우기 — 존재한 적 없는 함수였음 (`NameError`)
- [x] LLM 코드에서 딸려온 `# ```json ...` 주석 정리
- [x] 함수 실제로 **호출** → `vector = embed_feedback(chunks[0])`
- [x] 결과 확인: **3072** + 앞 5개 `[-0.014, 0.010, 0.013, -0.051, 0.006]` ✅
- 📝 `study/day9.md` ② 파트로 정리함 (7~17번 섹션)
- 🔴 **오늘 제일 막힌 것: `def`(만들기) vs 호출(부르기)** → day9.md 11번 섹션, 반드시 재방문
- 🐞 실행환경 에러 2개
  1. `ImportError: genai` = `python`이 기본 파이썬(C:\Python314)을 잡음 → **venv 파이썬** 써야 함
  2. `.env`가 안쪽 폴더에 있어서 못 찾음 → `load_dotenv("Kids_Feedback/.env")`로 경로 지정

### 실행 명령어 (이제 이걸로 고정)
```powershell
cd C:\Users\USER\GITHUB\Kids_Feedback
$env:PYTHONIOENCODING="utf-8"
Kids_Feedback\.venv\Scripts\python.exe Kids_Feedback\rag\kids.py
```

`🔴 10분 휴식`

## 세션 — Day 9 ③ 조각 8개 전부 임베딩 + 저장  ✅ 완료 (Day 9 ③ 종료)
- [x] `for`문으로 `chunks` 8개 → 벡터 8개 (`빈 통 → for → append` 패턴, ①에서 이미 씀)
- [x] `zip(chunks, vectors)`로 `{"text":…, "vector":…}` 묶기
- [x] `json.dump`로 `Kids_Feedback/rag/vectors.json` 저장
- [x] 결과 확인: 항목 **8개**, 0번 벡터 길이 **3072**, 0번 텍스트 `질문:`으로 시작 ✅
- 💡 왜 파일로 저장하나: 임베딩은 **API 호출(돈·시간)**. 한 번 만들어두면 다음부터는 읽기만 하면 됨

## 세션 — Day 9 ④ 검색 (RAG의 마지막 조각)  ✅ 완료 (Day 9 ④ 종료 = RAG 4조각 완성)
- [x] `vectors.json` 읽기 (8개 확인)
- [x] `embed_feedback()` 옮겨오기
- [x] 질문 문장 1개를 벡터화 (`q_vector`, 길이 3072)
- [x] `cos_sim(a, b)` 함수 작성 (내적 ÷ (크기a × 크기b))
- [x] 🔴 8개랑 전부 비교해서 1등 뽑기 (`scores=[]` → `for d in data` → `append` → `best=scores.index(max(scores))`)
- [x] 결과 확인: 질문 "소심한 애가 발표..." → **위축형 칭찬 조각** 뽑힘 ✅ (글자 안 겹쳐도 뜻으로 찾음)
- 📝 `study/day9.md` ④ 파트 + **[21. 전체 흐름]** 섹션에 정리 (RAG 큰 그림)
- 🐞 오늘 함정 6개 전부 **위치(들여쓰기) + print 구분** 싸움 (새 문법 0개)
  1. 중괄호 `{}` → 파이썬은 들여쓰기  2. 돌 대상은 `scores`가 아니라 `data`
  3. `scores=[]`가 for 안 → 매 바퀴 비워짐  4. 질문 벡터를 for 안(API 낭비)
  5. `best=print(...)` → print는 `None` 돌려줌  6. `data["text"]` → 리스트는 숫자 자리 `data[best]`

### ⏭️ 다음 (오늘 손대지 말 것) — RAG 결승선
- Day 10~11: 찾은 조각을 **LLM 프롬프트에 넣어 최종 답 만들기** (3단계) + Streamlit 화면 연결
- ⚠️ `search.py` 위쪽 확인용 print 2줄(`len(data)`, `data[0]`)은 나중에 정리

## 세션 — kids.py 마무리  ✅ 완료 (Day 9 ① 종료)
- [x] `print(chunks)` 들여쓰기 풀기
- [x] 실행 성공 (PowerShell): `cd C:\Users\USER\GITHUB\Kids_Feedback` → `$env:PYTHONIOENCODING="utf-8"` → `python Kids_Feedback\rag\kids.py`
- [x] 확인 완료: `len(chunks)` = **8**, `chunks[0]`이 `질문:`으로 공백 없이 시작 ✅
- 📝 `study/day9.md`에 정리함
- 🐞 오늘 만난 에러 3개 — 전부 코드가 아니라 **실행 환경** 문제였음
  1. `FileNotFoundError` = 상대경로는 **명령어 친 위치** 기준 (파일 위치 아님)
  2. `Kids_Feedback` 폴더가 **두 개** — 상위로 가면 안쪽에 도착함. `ls`로 `rag_docs` 보이는지 확인
  3. `UnicodeEncodeError` = 터미널이 cp949 → `$env:PYTHONIOENCODING="utf-8"` (bash 문법 아님!)

## ⏭️ 그 다음 (오늘 손대지 말 것)
- Day 9 ② `embed()` — 조각 1개 → 벡터
- Day 7 README (API 명세 / ERD / 1주차 회고) ← 아직 안 닫힘

---

# (이전) 오늘 작업 계획 — 2026-07-09 (목)

## 🎯 이번 목표: Day 8 (+ Day 7 README 오늘 안에 닫기)
> 순서 변경 — 의욕 있을 때 RAG 먼저, README는 개념 세션 직후 손 풀기용으로.
> 세션 A: Day 8 RAG 참고자료 (개념 + 문서 쓰기, 코드 X)
> 세션 B: Day 7 README ← **오늘 안에 닫는다. 미루지 않기로 약속함**
> Day 9(임베딩·검색)는 내일. 오늘 손대지 말 것.

## 세션 A (30분) — Day 8 RAG 참고자료
- [x] RAG 개념 잡기 — **찾아서(Retrieval)** 넣는 것. "넣는다"가 아니라 "찾아서 넣는다"
- [x] chunk 기준 세우기 — **조각 1개 = 질문 1개에 대한 대답**
  - ① 요약 테스트: "이 조각은 ___를 말한다" → 하나만 들어가야 함
  - ② 독립 테스트: 조각만 떼어 읽어도 말 되어야 함 (대명사·생략 금지)
  - ③ 크기(2~4문장)는 기준이 아니라 ①②를 지키면 나오는 결과
  - 조각 골격: `[언제/어떤 아이] → [뭘 한다] → [왜 효과적인지]` ← ③이 알맹이
- [x] 참고자료 주제 5개 확정
  1. 승부욕형 훈육법 / 2. 위축형 칭찬법 / 3. 위축형 적극성 키우는법
  4. 평범형 성장법 / 5. 학부모 전달 공통규칙
  - 위축형 2개 경계: **칭찬법=사후(해냈을 때)** vs **적극성=사전(안 나설 때)**
- [x] `rag_docs/위축형_칭찬법.md` — 질문 8개 골격 + 답 채움 (질문2~6 직접 작성, 질문4·5 골격 완벽 / 나머지 초안)
- [x] 조각 2·3 (강사 심부름 / 어린 동생) 작성
- [x] 나머지 자료 4개 (적극성·승부욕·평범형·학부모) — 초안으로 채움 ⚠️ Day 9 후 실제 방식으로 교체 필요
- 🐞 배운 것: 조각=질문1개당 대답1개 / 질문↔대답 어긋나면 검색 실패·딴소리 / 골격 3덩어리 / RAG 안에 chunk·embedding 순서대로 있음 / 자료는 "AI가 모르는 우리만의 것"

`🔴 10분 휴식`

## 세션 B — Day 7 README (오늘 안에)
- [ ] API 명세 (경로는 main.py의 prefix 포함한 전체 주소로)
- [ ] ERD (children ─ lesson_records ─ feedbacks)
- [ ] 1주차 회고

---

# (이전) 오늘 작업 계획 — 2026-07-08 (수)

## 🎯 이번 목표: Day 9까지 (오늘~내일 2일 예상)
> Day 7 README → Day 8 RAG 문서 → 🔴 Day 9 Chunking·임베딩·검색
> Day 9(RAG 핵심)는 머리 맑을 때 새로 시작 — 오늘 못 가도 정상, 밀리면 내일 아침 개념부터.
> Day 10~11(RAG 연결·Streamlit)은 그다음으로 미룸.

---

# (이전) 오늘 작업 계획 — 2026-07-01 (수) · 2일차

## 항상 함께 적용할 규칙
@.claude/sjy_st.md

## 🎯 확정: 토요일(7/4) 완성 고정 → 하루 범위 늘림
> 조건: 뒤쪽 어려운 날(목·금 RAG·Streamlit)엔 **핵심 개념만 내가 손으로 치고, 뼈대·보일러플레이트는 Claude가 깔아준다.** (CLAUDE.md 규칙)

**압축 일정**
| 날 | Day | 무게 |
|---|---|---|
| 수 7/1 (오늘) | Day 5③ + Day 6 + Day 7 | 가벼움 3개 몰아치기 |
| 목 7/2 | 🔴 Day 8 + Day 9 | 최대 고비 |
| 금 7/3 | 🔴 Day 10 + Day 11 | 어려움 |
| 토 7/4 | Day 12 + Day 13 + Day 14 | 마감 |

## 25~30분 작업 / 7~10분 휴식

---

## 세션 1 (25분) — Day 5 ③  ✅ 완료
- [x] `feedbacks_router.py` `import json` + `/generate`에서 LLM 결과 DB 저장 (`json.loads` → `Feedback(...)` → add/commit/refresh)
- [x] `FeedbackResponse` 스키마 작성 (필드 7개 + `from_attributes=True`)
- [x] `GET /feedbacks/{child_id}` 조회 (`response_model=List[FeedbackResponse]`)
- [x] 없는 ID 404 예외처리 (`HTTPException`) — POST record None / GET 빈 리스트 둘 다
- [x] 결과: 저장 200 확인 + 없는 ID 404 확인 ✅
- 🐞 배운 것: `json.load`vs`loads`(문자열=s), 200 vs 문서상 422 구분, class 들여쓰기(형제 vs 부품)

`🔴 7분 휴식`

---

## 세션 2 (30분) — Day 6 통합 테스트  ✅ 완료 (2026-07-07)
- [x] 아이 3명 등록 (위축형 / 승부욕형 / 평범형)
- [x] 각 아이별 수업 기록 입력
- [x] 3명 피드백 생성 → 성향 따라 톤 다르게 나오는지 확인
- [x] 결과: 3명 피드백 정상 동작 확인
- 🐞 배운 것: `422 Invalid control character` = JSON 문자열 안에 줄바꿈 끼어듦 → 한 줄로 압축해서 해결

`🔴 10분 휴식` (구현 2세트 후 → 복습 예약)

---

## 세션 3 (30분) — Day 7 1주차 README
- [ ] API 명세 (엔드포인트 목록 + 입력/출력)
- [ ] ERD (children ─ lesson_records ─ feedbacks 관계)
- [ ] 1주차 회고 (배운 것 / 어려웠던 것 / 다음 주 RAG 준비)
- 결과: README.md 완성 → 1주차 종료

`🔴 7분 휴식`

---

## 세션 4 (20분) — 당일 복습 🧠 (구현 2세트 후 필수)  ✅ 완료 (2026-07-08)
- [x] `json.loads` (문자열 → 딕셔너리) — 도구/결과 구분까지 확실히
- [x] `HTTPException` 404 예외처리 — 없는 값 → "없다" 안내, 500 터짐 방지
- [ ] 함수 호출 — [[project_func_call_revisit]] (Day 8~ 실사용 때 가볍게)
- 완료 기준: 내 말로 30초 설명 가능한지 → 통과
- 📝 파고든 것 5가지 study/day5.md "복습 세션" 섹션에 정리함 (문자열vs딕셔너리, 404vs500 등)

`🔴 오늘 종료 → 1주차(Day1~7) 완성`

---

## ⏭️ 내일(목 7/2) 미리보기 — 오늘 손대지 말 것
- 🔴 Day 8 (RAG 문서 5개) + Day 9 (Chunking·임베딩·검색) — 최대 고비
- RAG = 처음 보는 개념이라 내일 아침 개념 설명부터 시작함

---

## 완료

### 2026-06-30
- Day 4 완전 종료: 프로필 반영 프롬프트(성향 톤 + 노출금지 규칙 + JSON 출력), 유리/민수 톤 차이 검증
- Day 5 ①: `Feedback` 모델 추가 → feedbacks 테이블 생성
- Day 5 ②: `POST /feedbacks/generate`, FeedbackGenerate 스키마, 라우터 등록
- 🐞 `--reload` 오타 / 지운 `FeedbackCreate` 참조 정리, `llm_service` JSON 반환으로 수정

### 2026-06-29
- Day 3 마무리: `GET /lesson/{child_id}/lesson-records`(최근 5개 정렬), main.py 라우터 등록
- 🐞 버그 3개: `orm_mode`→`from_attributes`(Pydantic v2), DB 스키마 재생성, 라우터 경로 오타
- Day 4 ①: `prompt_service.py`

### 2026-06-28
- Day 2 마무리: children 프로필 필드, Child 모델 relationship
- Day 3 ①: lesson_records_router.py POST 구현
