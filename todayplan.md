# 오늘 작업 계획 — 2026-06-30 (화)

## 항상 함께 적용할 규칙
@.claude/sjy_st.md

## 25~30분 작업 / 7~10분 휴식

---



---

## 🔁 어제(6/29) 못 끝낸 것 — 오늘 먼저 (Day 4 마무리)

### 세션 1 (30분) — Day 4 ② LLM 호출  ✅ 완료
- [x] 🔑 Gemini API 키 발급 → `.env`에 넣기 (완료, 키 형식 확인됨)
- [x] `llm_service.py`에 `generate_feedback(prompt)` 함수 작성 (키/client는 함수 밖, 호출만 함수 안)
- [x] 실행 테스트: 격려 한마디 프롬프트 → Gemini → 피드백 글 출력 성공
- [x] 🐞 venv 미활성화로 ImportError → `(kids-feedback)` 켜고 해결
- [x] 🐞 `gemini-2.0-flash` 429(limit:0) → `gemini-2.5-flash`로 변경 후 성공
- 끝나면 보여야 할 결과: ✅ 터미널에 Gemini 피드백 글 출력됨

`🔴 7분 휴식`

---

### 세션 2 (30분) — Day 4 ③ 프로필 반영  ✅ 완료
- [x] [작성 규칙] 추가: 성향 톤 반영, memory_hint·caution_note 학부모 노출 금지, 비교·진단 금지, 도전적 목표
- [x] [출력 형식] JSON 지정 (next_goal / teacher_feedback / parent_feedback) — `{{ }}` 이스케이프
- [x] 🐞 없는 변수(`recent_records` 등) → `records_text`, `return prompts`→`prompt` 오타 수정
- [x] test_prompt.py로 검증: 유리(위축)/민수(승부욕) → 서로 다른 톤 + 규칙 준수 확인
- [x] 끝나면 보여야 할 결과: ✅ 같은 기록이라도 아이 특징 따라 다른 피드백

`🔴 10분 휴식 — Day 4 완전 종료 ✅✅`

---

## 🆕 오늘 본 작업 — Day 5 (피드백 API·저장)

### 세션 3 (25분) — Day 5 ①  ✅ 완료
- [x] `Feedback` 모델 추가 (id, child_id·lesson_record_id FK, JSON 3개, created_at)
- [x] main.py import에 Feedback 추가 → 서버 재시작 → `create_all`로 feedbacks 테이블 생성
- [x] 개념: Base 상속 → metadata 명단 등록 → create_all이 없는 테이블만 생성

`🔴 7분 휴식`

---

### 세션 4 (30분) — Day 5 ②  ✅ 완료
- [x] `POST /feedbacks/generate`: lesson_record_id 받아 → 아이·최근기록 쿼리 → build_prompt → generate_feedback → 결과 반환
- [x] FeedbackGenerate 스키마(입력=lesson_record_id 하나), feedbacks_router main.py 등록
- [x] 함수 호출 직접 작성: `build_prompt(child, records)`, `generate_feedback(prompt)` ← 오늘 헷갈린 개념 적용 성공
- [x] Swagger에서 lesson_record_id=1 → AI 피드백 생성 확인
- [x] 🐞 `--reload` 대시 누락 / `FeedbackResponse`가 지운 `FeedbackCreate` 참조 → 정리

`🔴 7분 휴식`

---

### 세션 5 (25분) — Day 5 ③  ◀ 내일 여기서 시작 (6/30 중단)
- [ ] LLM 결과 DB 저장 + `GET /children/{id}/feedbacks` + LLM 실패 예외 처리

**[현재 상태]**
- ✅ `llm_service.py`: 깨끗한 JSON 반환하도록 고침 (`config={"response_mime_type":"application/json"}`) → `json.loads` 바로 됨
- ⏳ `feedbacks_router.py` `/generate`는 아직 `return {"result": result}` (저장 안 함)

**[내일 첫 행동]** `feedbacks_router.py`에서:
1. 맨 위 `import json` 추가
2. `return {"result": result}` → 저장 코드로:
   `data = json.loads(result)` → `Feedback(child_id=child.id, lesson_record_id=record.id, next_goal=data["next_goal"], teacher_feedback=data["teacher_feedback"], parent_feedback=data["parent_feedback"])` → `db.add/commit/refresh/return`
3. `GET /feedbacks/{child_id}` 조회 + 없는 ID 404 예외처리

**[다시 시작 문장]** "json.loads로 AI 결과를 딕셔너리로 바꿔서 Feedback에 담아 DB에 저장한다."

`🔴 1일차 종료 — Day 4 완료 + Day 5 2/3 진행 ✅`

> ⬆️ **오늘은 여기까지.** Day 5까지 끝내면 1일차 완료.

---

## ⏭️ 내일(2일차, 수 7/1) 미리보기 — 오늘 손대지 말 것
- Day 6 (통합테스트): 아이 3명 등록 + 기록 입력 + 피드백 생성 테스트 + 없는 ID 예외처리
- Day 7 (1주차 README): API 명세 + ERD + 회고
- 🔁 복습 1세션

---

## 완료

### 2026-06-29
- Day 3 마무리: `GET /lesson/{child_id}/lesson-records`(최근 5개 정렬), main.py 라우터 등록
- 🐞 버그 3개: `orm_mode`→`from_attributes`(Pydantic v2), DB 스키마 재생성(drop+create), 라우터 경로 오타
- Day 4 ①: `prompt_service.py` (프로필 f-string + 기록 for 반복문 조립)
- Day 4 ② 준비: `google-genai`·`python-dotenv` 설치, `.env` 생성 + `.gitignore` 추가

### 2026-06-28
- Day 2 마무리: POST/PATCH children 프로필 필드, Child 모델 lesson_records relationship
- Day 3 ①: lesson_records_router.py 생성, POST /lesson-records 구현
