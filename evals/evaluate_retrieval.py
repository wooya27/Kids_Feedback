# evals/evaluate_retrieval.py
# RAG 검색 정확도 평가: 사람이 만든 정답셋(rag_questions.json)으로 Hit@1 / Hit@3 를 측정한다.
#
# "문서 개수"가 아니라 "적절한 근거를 찾는가"를 본다.
# - 긍정 질문: 검색된 청크의 source_file 이 gold(정답 파일)에 들어있으면 hit.
#     * Hit@1 = Top-1(가장 비슷한 1개)이 정답인가
#     * Hit@3 = Top-3 안에 정답이 하나라도 있는가   → Top-1 vs Top-3 비교가 바로 이것
# - 부정 질문: 관련 근거가 없어야 정상. low_relevance=True 로 '안전 처리'되면 handled.
#
# ⚠️ 실제 임베딩(=Gemini 키)이 필요하다. 신규 15문서 인덱스(vectors.json) 기준으로만 실행할 것.
# 실행:
#   docker compose exec api python -m evals.evaluate_retrieval
#   (또는 로컬 .env 키로)  python -m evals.evaluate_retrieval

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# 프로젝트 루트를 import 경로에 추가 (python evals/..., python -m evals.... 양쪽 지원)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.rag_service import rag_search  # noqa: E402

QUESTIONS_PATH = ROOT / "evals" / "rag_questions.json"
RESULTS_PATH = ROOT / "evals" / "retrieval_results.json"


def pct(x, total):
    return round(100 * x / total, 1) if total else 0.0


def main():
    spec = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    questions = spec["questions"]

    rows = []
    for q in questions:
        res = rag_search(q["question"], k=3)
        hits = res["hits"]
        srcs = [h["source_file"] for h in hits]
        gold = set(q.get("gold_source_files") or [])

        if q["type"] == "positive":
            top1 = bool(srcs) and srcs[0] in gold
            top3 = any(s in gold for s in srcs[:3])
        else:  # negative
            top1 = top3 = None

        rows.append({
            "id": q["id"], "category": q["category"], "type": q["type"],
            "question": q["question"], "gold": sorted(gold),
            "retrieved": srcs, "scores": [h["score"] for h in hits],
            "best_score": res["best_score"], "low_relevance": res["low_relevance"],
            "hit@1": top1, "hit@3": top3,
        })
        mark = ("neg:handled" if res["low_relevance"] else "neg:MISS") if q["type"] == "negative" \
            else (f"@1={'O' if top1 else 'X'} @3={'O' if top3 else 'X'}")
        print(f"[{q['id']}] {q['category']:5} {mark}  best={res['best_score']}")

    # ── 집계 ──
    pos = [r for r in rows if r["type"] == "positive"]
    neg = [r for r in rows if r["type"] == "negative"]
    n = len(pos)
    hit1 = sum(1 for r in pos if r["hit@1"])
    hit3 = sum(1 for r in pos if r["hit@3"])

    # 범주별
    per_cat = {}
    for r in pos:
        c = r["category"]
        per_cat.setdefault(c, {"n": 0, "h1": 0, "h3": 0})
        per_cat[c]["n"] += 1
        per_cat[c]["h1"] += 1 if r["hit@1"] else 0
        per_cat[c]["h3"] += 1 if r["hit@3"] else 0

    neg_handled = sum(1 for r in neg if r["low_relevance"])
    failures = [r for r in pos if not r["hit@3"]]  # Top-3로도 못 맞춘 실패 사례

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "index_scope": spec.get("_meta", {}).get("index_scope"),
        "positive_count": n,
        "negative_count": len(neg),
        "hit@1_rate": pct(hit1, n),
        "hit@3_rate": pct(hit3, n),
        "per_category": {
            c: {"n": v["n"], "hit@1": pct(v["h1"], v["n"]), "hit@3": pct(v["h3"], v["n"])}
            for c, v in sorted(per_cat.items())
        },
        "negative_handled_rate": pct(neg_handled, len(neg)),
        "failure_ids": [r["id"] for r in failures],
    }

    RESULTS_PATH.write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    # ── 출력 ──
    print("\n" + "=" * 56)
    print("RAG 검색 평가 요약")
    print("=" * 56)
    print(f"긍정 {n}문항  Hit@1 {summary['hit@1_rate']}%   Hit@3 {summary['hit@3_rate']}%  (Top-1 vs Top-3 비교)")
    print(f"부정 {len(neg)}문항  안전처리율 {summary['negative_handled_rate']}%")
    print("\n범주별   n   Hit@1   Hit@3")
    for c, v in summary["per_category"].items():
        print(f"  {c:7} {v['n']:3}  {v['hit@1']:5}%  {v['hit@3']:5}%")
    if failures:
        print("\n[Top-3로도 못 맞춘 실패 사례]")
        for r in failures:
            print(f"  {r['id']} ({r['category']}): gold={r['gold']} / retrieved={r['retrieved']}")
    print(f"\n원시 결과 저장: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
