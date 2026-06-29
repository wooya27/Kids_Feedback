# 오늘 작업 계획 — 2026-06-29

## 항상 함께 적용할 규칙
@.claude/sjy_st.md

## 25~30분 작업 / 7~10분 휴식
## 🎯 오늘 진짜 목표: Day 4까지 / Day 5~6은 여력 보너스

---

## 세션 1 (30분) — Day 3 마무리 ① ✅ 완료
- [x] `GET /lesson/{child_id}/lesson-records` 구현 (최근 5개, 날짜순 정렬 포함)

`🔴 7분 휴식`

---

## 세션 2 (25분) — Day 3 마무리 ②  ◀ 여기서 중단 (버그 발견)
- [x] `main.py`에 lesson_records 라우터 등록
- [ ] 🐞 **버그 수정 먼저!** `schemas.py` 42번·60번 줄 `orm_mode = True` → `from_attributes = True` (2군데)
  - 이유: Pydantic v2에선 `orm_mode`가 `from_attributes`로 이름 바뀜. 옛 이름이라 무시돼서 POST/GET이 500 에러.
  - 고친 뒤 서버는 `--reload`라 자동 재시작됨.
- [ ] 테스트 데이터 입력: 먼저 아이 2~3명(`POST /children/`) → 그 아이로 수업기록 5개(`POST /lesson/`, child_id 동일, lesson_date만 다르게)
- [ ] `GET /lesson/{child_id}/lesson-records`로 최신순 5개 나오는지 확인
- 끝나면 보여야 할 결과: 기록 5개가 최신 날짜 먼저 JSON으로 나옴

`🔴 7분 휴식`

---

## ⏸️ 작업 중단 메모 (2026-06-29)

**[다음 첫 행동]**
- 서버 켜기: `Kids_Feedback/Kids_Feedback` 폴더에서 `uvicorn main:app --reload`
- `schemas.py` 열어서 `orm_mode` 2군데를 `from_attributes`로 고치기

**[다시 시작 문장]**
- "schemas.py의 orm_mode를 from_attributes로 바꾸고, Swagger에서 아이 등록부터 다시 한다."

**[참고]**
- 전체 코드 흐름이 헷갈리면 `study/00_전체흐름.md` 먼저 읽기
- 에러 나면 서버 터미널의 빨간 Traceback부터 읽기 (에러 메시지에 답이 있음)

---

## 세션 3 (30분) — Day 4 ①
- [ ] `prompt_service.py` 작성 (프롬프트 조립 함수)

`🔴 7분 휴식`

---

## 세션 4 (30분) — Day 4 ②
- [ ] `llm_service.py` 작성 (Claude API 호출)

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
