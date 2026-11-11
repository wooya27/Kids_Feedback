# [업데이트 단계 5] P0-6 · RAG 검색 정확도 평가셋(48문항) + 평가 코드

> 목표: "문서 많다"가 아니라 **"올바른 근거를 찾는가"**를 사람이 만든 정답셋으로 수치화한다.

---

## 1. 산출물
- `evals/rag_questions.json` — **48문항**(긍정 42 + 부정 6), 각 긍정에 사람이 매핑한 `gold_source_files`.
- `evals/evaluate_retrieval.py` — Hit@1/Hit@3 + 범주별 + 실패사례 산출, 결과를 `evals/retrieval_results.json`에 저장.
- `docs/rag_evaluation.md` — 방법론 + 실행법 + (실행 후 채울) 결과표.

## 2. 꼭 알아야 하는 개념
- **Hit@1 vs Hit@3**: Top-1만 정답이면 Hit@1, Top-3 안에 정답 있으면 Hit@3. 이 둘의 차이가 곧 "Top-1→Top-3로 바꿔서 좋아졌나"의 증거.
- **정답셋(gold)**: 내가(사람이) '이 질문엔 이 문서가 답'이라고 **미리 정해둔 것**. 검색 결과를 이걸로 채점한다. 복수 정답 허용(예: 순서 기다리기 질문은 상황문서 + 산만형문서 둘 다 인정).
- **부정 사례(negative)**: 문서에 답이 없는 질문(줄 길이·환불·날씨). 검색이 `low_relevance=True`로 **안 지어내고 걸러내면** 정답.
- **유사도 ≠ 정답률**: 유사도 임계 통과는 '비슷해 보인다'일 뿐. 실제 맞췄는지는 gold로만 판정.

## 3. 채점 로직 (evaluate_retrieval.py 핵심)
```python
res = rag_search(question, k=3)         # Top-3 + 출처 + low_relevance
srcs = [h["source_file"] for h in res["hits"]]
# 긍정: 검색된 출처가 정답 파일에 있나
top1 = srcs[0] in gold
top3 = any(s in gold for s in srcs[:3])
# 부정: low_relevance 로 안전 처리됐나
neg_ok = res["low_relevance"] is True
```
→ 범주별 Hit@1/Hit@3 집계 + `failure_ids`(Top-3로도 못 맞춘 질문) 목록 저장.

## 4. 실행 명령어 (키 필요 — 나중에 도커에서)
```bash
docker compose exec api python -m rag.build_index            # 먼저 실제 인덱스 빌드
docker compose exec api python -m evals.evaluate_retrieval   # Hit@1/@3 측정
# 결과: evals/retrieval_results.json  (summary 값을 docs/rag_evaluation.md 표에 옮겨 적기)
```

## 5. 로컬에서 미리 점검한 것 (키 없이)
```bash
python -c "import json;spec=json.load(open('evals/rag_questions.json',encoding='utf-8'));print(len(spec['questions']))"
# → 48, 정답파일 누락 0, ID중복 0 확인 완료
```

## 6. 실패 → 개선 루프 (중요)
1. 실행 후 `failure_ids`와 각 질문의 `retrieved`(실제 뽑힌 출처) 확인.
2. 원인 분류: 청크가 너무 큼 / 질문 표현 / 중복 청크.
3. 문서를 더 쪼개거나 표현을 고치고 **재평가**. 과적합 방지용 확인 문항 일부 남김.

## 7. 한 줄 요약
> 48문항 정답셋으로 Hit@1·Hit@3를 재현 가능하게 측정하고, 부정 질문은 '안 지어내고 걸러내는지'로 채점한다.
> 수치는 실행 후 실측값으로만 채운다.
