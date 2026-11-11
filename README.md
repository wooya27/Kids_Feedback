# Kids_Feedback — 아동 줄넘기 수업 피드백 자동화

> 강사가 수업 기록만 넣으면, **RAG 지도 근거 + LLM**으로 학생 맞춤 피드백 초안을 만들고,
> **강사가 검수·수정·승인**한 뒤에만 학부모용 최종본이 나가는 자동화 워크플로.
> AX/DX · AI Solution · Automation Engineer 포트폴리오용 프로젝트.

⚠️ **표기 원칙:** 아래에서 '구현됨'과 '계획/실행 예정'을 구분한다. 성과 수치(Hit@k, 승인률 등)는
**실측 후에만** 기재하며, 지도 문서는 모두 *전문가 검증 전 자체 작성 가이드*다. 모든 데이터는 합성(가짜)이다.

---

## 1. 문제 정의
- 강사가 아이마다 성향·수업 상황을 고려해 피드백을 **수동 작성**하면 시간이 많이 들고 편차가 크다.
- 아이 특성에 맞는 **지도 근거**를 매번 떠올리기 어렵다.
- 학부모용 표현에는 과장·진단·낙인 표현이 섞이면 안 된다(민감).

## 2. AS-IS → TO-BE
| 구분 | AS-IS | TO-BE |
|---|---|---|
| 피드백 작성 | 강사 수동 | DB+RAG+LLM 자동 **초안** |
| 지도 근거 | 강사 기억 | 지도 문서 **Top-3 검색**(출처·점수 포함) |
| 품질/안전 | 사람 눈 | 검증 실패 시 **DB 저장 차단** + 강사 최종 검수 |
| 트리거 | 수동 | n8n Webhook(동적 수업 ID) |

## 3. 아키텍처 (실제 구현)
```
외부 POST ─▶ n8n Webhook ─(검증·동적 ID)─▶ FastAPI /feedbacks/generate
                                                │
                                   LangGraph: retrieve ─▶ generate ─▶ review ─▶ decide
                                   (DB조회+RAG)  (LLM+JSON+스키마검증)  (통과/재시도/실패)
                                                │  review_ok=True 일 때만 저장
                                                ▼
                                   PostgreSQL(children/lesson_records/feedbacks)
                                                │
                           강사 검수: PATCH /feedbacks/{id}/review (approved/edited/rejected)
                                                ▼
                           GET /feedbacks/{id}/final (승인·수정만 최종본 전달)
```
- **구성:** FastAPI(API) · PostgreSQL(DB) · n8n(자동화) — `docker-compose.yml`로 한 네트워크.
- **LLM:** Gemini `gemini-2.5-flash`(생성, JSON 모드) · `gemini-embedding-001`(임베딩 3072차원).
- **RAG:** JSON 기반 코사인 유사도 Top-3(현 규모 102청크엔 충분, pgvector는 필요 입증 시 전환).

## 4. ERD (핵심 3테이블)
```
children (1) ──< lesson_records (1) ──< feedbacks
  id                id                    id
  name, age         child_id(FK)          child_id(FK), lesson_record_id(FK)
  personality       lesson_date           next_goal/teacher_feedback/parent_feedback (AI 원본)
  preferred_...     activity, attitude    edited_* (강사 수정본, 원본 별도 보존)
                    performance...        review_status/comment/reviewed_at
```

## 5. 핵심 API
| 메서드 | 경로 | 설명 |
|---|---|---|
| POST | `/feedbacks/generate` | 수업기록 ID로 피드백 생성. 검증 실패면 **502(저장 안 함)** |
| PATCH | `/feedbacks/{id}/review` | 강사 검수(approved/edited/rejected). edited면 수정본 저장 |
| GET | `/feedbacks/{id}/final` | 최종본 전달(승인·수정만, 그 외 409) |
| GET | `/feedbacks/{child_id}` | 학생별 피드백 조회(학생 간 격리) |
| GET | `/health` | 헬스체크 |

## 6. 실행 방법
```bash
# 1) 환경변수: .env.example 복사 후 키 채우기 (비밀키는 깃에 커밋 금지)
cp .env.example .env     # PowerShell: Copy-Item .env.example .env

# 2) 전체 기동 (api + db + n8n)
docker compose up -d --build
curl http://localhost:8001/health

# 3) RAG 인덱스 빌드 (rag_docs 전체 → vectors.json, 102청크)
docker compose exec api python -m rag.build_index
#    키 없이 청킹만 점검:  python -m rag.build_index --report-only

# 4) 테스트 (키 불필요: SQLite + LLM Mock)
python -m pytest -q

# 5) 평가 (키 필요, 테스트DB에서만)
docker compose exec api python -m evals.evaluate_retrieval   # RAG Hit@1/@3
docker compose exec api python seed_eval.py                   # ⚠️ TRUNCATE: 테스트DB 전용
docker compose exec api python evaluate.py                    # API 35회 지표 → metrics.json
```
`.env.example` 항목: `GEMINI_API_KEY`, `POSTGRES_PASSWORD`. `DATABASE_URL`은 compose가 조립.

## 7. RAG 설계 (문서 분류 · 청킹 · 검색)
- **문서:** `rag_docs/` **15개 / 102청크** — 성향별·상황별·성장목표·학부모소통. 각 문서 상단 `> meta:`로 분류·출처·버전. 상세: `docs/rag_documents_index.md`.
- **청킹:** `## 질문` 단위(질문 1개=청크 1개)로 독립 검색되게. 인덱서 `rag/build_index.py`(전체 재생성·빈/중복 검출·원자적 교체).
- **검색:** Top-3 + 출처·유사도 + 다양성(한 문서 최대 2청크) + `low_relevance`(근거 부족 시 '지어내지 말라').
- **평가:** 정답셋 48문항(`evals/rag_questions.json`)으로 Hit@1/@3·부정 안전처리. 방법론: `docs/rag_evaluation.md`.

## 8. 테스트 · 평가
- **자동 테스트(22개, 키 불필요):** 생성/저장, 검증 실패 미저장, 404, RAG Top-3·근거없음, 검수 수정본·전달차단·상태전이, 학생 격리, n8n 매핑. → `python -m pytest`
- **평가:**
  - RAG 검색(2026-11-12 실측, 48문항): 긍정 42문항 **Hit@1 100% · Hit@3 100%**, 부정 안전처리 **83.3%**(5/6).
    ⚠️ 문서·질문을 동일인이 작성한 **자체 평가라 과대평가 가능** — 반드시 이 한계와 함께 해석(상세·실패사례: `docs/rag_evaluation.md`).
  - API 35회(`metrics.json`)·RAG 전/후 품질(`docs/rag_quality_comparison.md`)은 실행 후 수치 기재(측정 예정).

## 9. 한계 (정직하게)
- 지도 문서는 **전문가 검증 전 자체 작성 가이드**. 공식 지도 규정 아님.
- Human Review 시뮬레이션(`evaluate.py`)은 **규칙 기반**이며 실제 강사 검수와 구분.
- 성과 수치는 **실측 후에만** 기재(현재 일부 '측정 예정').
- **인증·접근 제어 미구현** → 공개 데모 전 보완 필요.
- `render.yaml`은 **배포 설정**일 뿐 배포 성공 증거가 아니다. 동작 검증된 공개 URL만 기재한다.

## 10. 보안 · 개인정보
- 실제 아동 개인정보·실명·API 키를 DB·깃·스크린샷·LLM 테스트에 **사용하지 않음**(합성 데이터만).
- `.env`는 `.gitignore` 처리(키 보호). 로그에 개인정보 미기록(실패 로그는 필드명·유형만).

## 11. 데모 증거 (P2-1, 수집 예정)
- 같은 활동·다른 성향 학생의 입력→Top-3 근거→JSON 출력→검수 비교.
- n8n에서 서로 다른 수업 ID 2건 처리 화면.
- 검증 실패 시 DB 미저장 시연.
- 수집 가이드: `docs/demo_checklist.md`.
