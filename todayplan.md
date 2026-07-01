# 오늘 작업 계획 — 2026-07-01 (수) · 2일차

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

## 세션 2 (30분) — Day 6 통합 테스트
- [ ] 아이 3명 등록 (위축형 / 승부욕형 / 평범형)
- [ ] 각 아이별 수업 기록 2~3개 입력
- [ ] 3명 피드백 생성 → 성향 따라 톤 다르게 나오는지 확인
- [ ] 없는 record_id / child_id 요청 → 404 뜨는지 확인
- 결과: 3명 피드백 + 예외처리 정상 동작 확인

`🔴 10분 휴식` (구현 2세트 후 → 복습 예약)

---

## 세션 3 (30분) — Day 7 1주차 README
- [ ] API 명세 (엔드포인트 목록 + 입력/출력)
- [ ] ERD (children ─ lesson_records ─ feedbacks 관계)
- [ ] 1주차 회고 (배운 것 / 어려웠던 것 / 다음 주 RAG 준비)
- 결과: README.md 완성 → 1주차 종료

`🔴 7분 휴식`

---

## 세션 4 (20분) — 당일 복습 🧠 (구현 2세트 후 필수)
- [ ] 오늘 개념 3개 "안 보고 떠올리기 → 확인 → 한 줄 설명"
  - `json.loads` (문자열 → 딕셔너리)
  - `HTTPException` 404 예외처리
  - 함수 호출 — [[project_func_call_revisit]]
- 완료 기준: 내 말로 30초 설명 가능한지

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
