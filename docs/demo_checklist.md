# 데모 증거 수집 체크리스트 (P2-1)

> 목표: 포트폴리오 3페이지에 넣을 **실제 동작 증거 2~3개**를 합성 데이터로 캡처한다.
> 모든 캡처에서 개인정보·실명·API 키를 화면에서 제거한다.

## 전제
```bash
docker compose up -d --build
docker compose exec api python -m rag.build_index   # 인덱스 빌드(102청크)
docker compose exec api python seed_eval.py          # 합성 데이터(테스트DB)
```

## 증거 1 — 같은 활동, 다른 성향의 개인화 비교
- [ ] `docker compose exec api python -m evals.compare_rag_variants` 실행.
- [ ] `evals/rag_variant_outputs.json`에서 합성A(위축)/B(산만)/C(완벽)의 **입력 프로필 → Top-3 근거 → JSON 출력** 캡처.
- [ ] RAG 미사용/Top-1/Top-3 차이가 드러나는 부분 표시.

## 증거 2 — n8n 동적 ID 처리 (서로 다른 2건)
- [ ] n8n에 `n8n_workflow_webhook.json` import, Production URL 확인.
- [ ] `curl -X POST <n8n>/webhook/kids -d '{"lesson_record_id": 2}'` / `... 5` 2건 호출.
- [ ] 각 응답의 `lesson_record_id`가 요청값과 **일치**함을 캡처(2↔2, 5↔5).
- [ ] 잘못된 타입(`"abc"`)·누락(`{}`)이 Code 노드에서 **거절**되는 화면.

## 증거 3 — 검증 실패 시 DB 미저장 (안전장치)
- [ ] 정상 생성 1건 → `feedbacks` 행 +1 확인.
- [ ] (가능하면) LLM이 깨진 JSON을 뱉는 상황을 유도하거나 단위테스트 결과로 대체:
      `python -m pytest tests/test_feedback_graph.py -v` → 실패 입력 시 **502 + 행 0건** 캡처.
- [ ] 실패 전후 `SELECT count(*) FROM feedbacks;` 비교.

## 증거 4 — Human Review 원본→수정→최종
- [ ] 생성된 피드백에 `PATCH /feedbacks/{id}/review {review_status:"edited", edited_parent_feedback:"..."}`.
- [ ] `GET /feedbacks/{id}/final`로 **원본 초안 / 수정본 / 최종본**이 서로 다른 값으로 조회됨 캡처.
- [ ] `pending` 상태에서 `/final`이 **409**(전달 차단)인 화면.

## 공통 주의
- [ ] 화면에서 API 키·DB 비밀번호·실명 제거.
- [ ] 모든 데이터가 합성임을 캡션에 명시.
- [ ] 측정 못한 수치는 '향후 검증 예정'으로 표기.
