# evals/compare_rag_variants.py
# P1-1: RAG 개선이 '검색 점수'뿐 아니라 '실제 피드백 품질'에도 도움이 되는지 비교한다.
#
# 같은 활동을 한 서로 다른 성향의 합성 학생에게, 동일 조건(같은 모델/프롬프트 틀)에서
#   (A) RAG 미사용   (B) 현재 Top-1   (C) 개선 Top-3
# 세 가지 생성 결과를 뽑아 evals/rag_variant_outputs.json 에 저장한다. (사람이 직접 평가)
#
# ⚠️ Gemini 키 필요. 실행:
#   docker compose exec api python -m evals.compare_rag_variants
#   (또는 로컬 .env 키)  python -m evals.compare_rag_variants

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from datetime import date, datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.rag_service import rag_search          # noqa: E402
from prompt_service import build_prompt          # noqa: E402
from llm_service import generate_feedback        # noqa: E402

OUT_PATH = ROOT / "evals" / "rag_variant_outputs.json"

# 같은 활동(양발 모아 뛰기) + 성향만 다른 합성 학생 3명
STUDENTS = [
    dict(name="합성A", age=8, level="초급", personality="위축형(소심하고 실수를 두려워함)",
         preferred_feedback="구체적 칭찬 + 다음 한 걸음"),
    dict(name="합성B", age=9, level="초급", personality="산만형(주의가 쉽게 흩어지고 충동적)",
         preferred_feedback="짧고 명확한 지시"),
    dict(name="합성C", age=8, level="초급", personality="완벽주의형(실수를 크게 두려워함)",
         preferred_feedback="과정 인정"),
]
ACTIVITY = ("양발 모아 뛰기", "3번 중 2번 성공", "실수할까봐 머뭇거림", "착지에서 균형 무너짐")


def _child(d):
    return SimpleNamespace(memory_hint=None, caution_note=None, material_note=None,
                           teacher_memo=None, **d)


def _record():
    a, p, att, diff = ACTIVITY
    return SimpleNamespace(lesson_date=date(2026, 11, 1), activity=a, performance=p,
                           attitude=att, difficulty=diff, teacher_note="1회차")


def _gen(child, records, rag_context):
    prompt = build_prompt(child, records, rag_context)
    raw = generate_feedback(prompt)
    try:
        return json.loads(raw)
    except Exception:
        return {"_parse_error": raw[:200]}


def main():
    results = []
    for s in STUDENTS:
        child = _child(s)
        records = [_record()]
        question = f"질문: {child.personality} 아이가 {ACTIVITY[0]}를 했을 때 뭐라고 말해주나요?"
        full = rag_search(question, k=3)
        top1 = {"hits": full["hits"][:1], "best_score": full["best_score"],
                "low_relevance": full["low_relevance"], "query": question}
        none = {"hits": [], "best_score": 0.0, "low_relevance": True, "query": question}

        results.append({
            "student": s["name"], "personality": s["personality"], "activity": ACTIVITY[0],
            "retrieved_top3": [{"source": h["source_file"], "score": h["score"]} for h in full["hits"]],
            "A_no_rag": _gen(child, records, none),
            "B_top1": _gen(child, records, top1),
            "C_top3": _gen(child, records, full),
        })
        print(f"[{s['name']}] 생성 완료 (A/B/C)")

    OUT_PATH.write_text(json.dumps(
        {"generated_at": datetime.now(timezone.utc).isoformat(),
         "note": "A=RAG미사용 / B=Top-1 / C=Top-3. 사람이 직접 품질 평가할 것.",
         "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n저장: {OUT_PATH}")
    print("→ docs/rag_quality_comparison.md 의 평가 기준으로 사람이 채점하세요.")


if __name__ == "__main__":
    main()
