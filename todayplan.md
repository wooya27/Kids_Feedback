# 오늘 작업 계획 — 2026-06-29

## 항상 함께 적용할 규칙
@.claude/sjy_st.md

## 25~30분 작업 / 7~10분 휴식

---

## 📅 토요일(7/4) 마감 로드맵 — 하루 2 day치 (≈3시간)
> 선택: 전부 다(풀스코프). 하루 약 6세션. 🔴 표시는 막힐 위험 큰 날.

| 날짜 | 할 일 | 비고 |
|------|------|------|
| **월 6/29 (오늘)** | Day 4 — LLM 연결 | ▶ 아래 세션 참고 |
| **화 6/30** | Day 5 (피드백 API·저장) + Day 6 (통합테스트) | |
| **수 7/1** | Day 7 (1주차 README) + Day 8 (RAG 문서 5개) | 가벼움 |
| **목 7/2** | 🔴 Day 9 (임베딩·검색) + Day 10 (RAG 통합) | 가장 어려움 |
| **금 7/3** | 🔴 Day 11 (Streamlit 화면1) + Day 12 (화면2) | |
| **토 7/4** | Day 13 (그래프·데모) + Day 14 (최종 문서) | |

**원칙:** 풀스코프 — Day 14까지 전부 한다. 아무것도 빼지 않음.
**막히면:** 한 작업에서 15분 넘게 에러로 막히면 혼자 끙끙대지 말고 바로 질문 → 빨리 풀고 다음으로.

---

## 세션 1 (30분) — Day 3 마무리 ① ✅ 완료
- [x] `GET /lesson/{child_id}/lesson-records` 구현 (최근 5개, 날짜순 정렬 포함)

`🔴 7분 휴식`

---

## 세션 2 (25분) — Day 3 마무리 ② ✅ 완료
- [x] `main.py`에 lesson_records 라우터 등록
- [x] 🐞 `schemas.py` `orm_mode = True` → `from_attributes = True` (2군데, Pydantic v2)
- [x] 🐞 DB 스키마 불일치 → `drop_all + create_all`로 테이블 재생성 (memory_hint 등 새 컬럼 반영)
- [x] 🐞 라우터 경로 오타 `leasson-records` → `lesson-records`
- [x] 테스트 데이터: 아이 5명 등록 + child_id=1로 수업기록 5개 입력
- [x] `GET /lesson/1/lesson-records` → 최신순 5개 확인

`🔴 7분 휴식`

---

## ✅ Day 3 마무리 완료 (2026-06-29) — 버그 3개 해결

**[참고]**
- 전체 코드 흐름이 헷갈리면 `study/00_전체흐름.md` 먼저 읽기
- 에러 나면 서버 터미널의 빨간 Traceback부터 읽기 (에러 메시지에 답이 있음)

---

## 세션 3 (30분) — Day 4 ① ✅ 완료
- [x] `prompt_service.py` 작성 — 프로필 f-string + 기록 리스트 for 반복문으로 조립

`🔴 7분 휴식`

---

## 세션 4 (30분) — Day 4 ②  ◀ 여기서 중단 (내일 이어서)
- [x] SDK 설치 완료 (`google-genai`, `python-dotenv`)
- [x] `.env` 파일 생성 + `.gitignore`에 추가 (키 숨길 자리 준비됨)
- [ ] 🔑 **다음 첫 행동:** Google AI Studio(`aistudio.google.com`)에서 API 키 발급 → `Kids_Feedback/.env`의 `GEMINI_API_KEY=` 뒤에 붙여넣기
- [ ] `llm_service.py`에 `generate_feedback(prompt)` 함수 작성
  - 구조: `client.models.generate_content(model="gemini-2.0-flash", contents=prompt)` → `response.text` → `return`
- [ ] 실행 테스트: prompt_service의 프롬프트 → Gemini → 피드백 글 나오는지

**[다시 시작 문장]**
- "API 키 발급해서 .env에 넣고, llm_service.py에 Gemini 호출 함수 쓴다."

**[참고]**
- 개념 정리는 `study/day4.md`에 있음 (API/키, 호출 3단계)
- prompt_service.py는 완성됨 — `build_prompt(child, records)` 호출하면 프롬프트 나옴

`🔴 10분 휴식`

---

## 세션 5 (30분) — Day 4 ③
- [ ] 프로필 반영: personality(톤), preferred_feedback(격려), caution_note·memory_hint(강사용)
- [ ] JSON 출력 테스트 (next_goal / teacher_feedback / parent_feedback)
- 끝나면 보여야 할 결과: 같은 기록이라도 아이 특징에 따라 다른 피드백이 나옴

`🔴 10분 휴식 — 여기까지가 오늘 진짜 목표 ✅`

---

## (보너스) 세션 6 (25분) — Day 5 ①
- [ ] feedbacks 테이블 설계 + 모델 추가

`🔴 7분 휴식`

---

## (보너스) 세션 7 (30분) — Day 5 ②
- [ ] `POST /feedbacks/generate` (최근 기록 + 프로필 자동 포함 → LLM 호출)

`🔴 7분 휴식`

---

## (보너스) 세션 8 (25분) — Day 5 ③
- [ ] LLM 결과 DB 저장 + `GET /children/{id}/feedbacks` + LLM 실패 예외 처리

`🔴 10분 휴식`

---

## (보너스) 세션 9 (30분) — Day 6 ①
- [ ] 아이 3명 등록 + 프로필 카드 + 각 기록 3개 이상 입력

`🔴 7분 휴식`

---

## (보너스) 세션 10 (25분) — Day 6 ②
- [ ] 피드백 생성 통합 테스트 + 없는 ID 예외 처리
- [ ] Swagger 캡처 준비 + README API 목록 정리

---

## 완료

### 2026-06-28
- Day 2 마무리: POST/PATCH children 프로필 필드, Child 모델 lesson_records relationship
- Day 3 ①: lesson_records_router.py 생성, POST /lesson-records 구현
