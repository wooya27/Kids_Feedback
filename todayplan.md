# 오늘 작업 계획 — 2026-07-09 (목)

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
