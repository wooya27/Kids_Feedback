# evaluate.py
# 포트폴리오 '평가 지표'를 실제 실행 결과로 계산한다.
#   1) API E2E 성공률      2) 필수 JSON 형식 성공률   3) RAG 검색 성공률
#   4) 평균 응답시간        5) Human Review 승인/수정/거절률   6) 실패요청 처리율
#
# 측정하지 않은 수치는 만들지 않는다. 모든 숫자는 아래 실행에서 나온 것.
# ⚠️ 컨테이너 안에서 실행(= 라이브와 동일 환경):
#     docker compose cp evaluate.py api:/app/evaluate.py
#     docker compose exec api python evaluate.py
#
# Human Review 승인/수정/거절은 '사람의 판단'이라 100% 객관화할 수 없다.
# 그래서 아래 REVIEW RULE(품질 프록시)로 '시뮬레이션 검수'를 적용하고,
# 결과 문서에 "실제 강사 검수가 아닌 규칙 기반 시뮬레이션"이라고 명시한다.

import json
import time
import statistics
import urllib.request
import urllib.error
from datetime import datetime, timezone

from database import SessionLocal
from models import LessonRecord, Child
from rag.rag_service import embed_feedback, cos_sim, data as rag_data

API = "http://localhost:8000"
REQUIRED = ["next_goal", "teacher_feedback", "parent_feedback"]
RAG_THRESHOLD = 0.70        # 이 유사도 이상이면 'RAG 근거 검색 성공'으로 본다
REPEAT_FIRST_N = 9          # 앞 9개 기록을 한 번 더 돌려 일관성까지 확인(→ 유효 30건)
ERROR_IDS = [999999, 0, -1, 888888, 123456]   # 존재하지 않는 수업기록(실패 케이스)


def post_json(path, payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API + path, data=body,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, None


def patch_review(feedback_id, status, comment=None):
    body = json.dumps({"review_status": status, "review_comment": comment}).encode("utf-8")
    req = urllib.request.Request(f"{API}/feedbacks/{feedback_id}/review", data=body,
                                 headers={"Content-Type": "application/json"},
                                 method="PATCH")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code


def rag_max_sim(question):
    """live rag_search와 동일 로직으로, 최고 유사도 점수를 계산한다."""
    qv = embed_feedback(question)
    return max(cos_sim(qv, d["vector"]) for d in rag_data)


def simulated_review(fields_ok, rag_ok):
    """시뮬레이션 검수 규칙(문서에 공개): 실제 강사 판단이 아님.
    - rejected : 필수 필드 누락/빈값 (품질 미달)
    - edited   : 생성은 됐지만 RAG 근거가 약함(threshold 미만) → 강사가 손봐야 함
    - approved : 필드 완전 + RAG 근거 충분 → 그대로 사용
    """
    if not fields_ok:
        return "rejected", "필수 필드 누락"
    if not rag_ok:
        return "edited", "RAG 근거 약함 → 문장 보완 필요"
    return "approved", None


def main():
    db = SessionLocal()
    # DB에서 (기록id → 질문, child) 뽑기 (live retrieve와 같은 질문 포맷)
    records = db.query(LessonRecord).order_by(LessonRecord.id).all()
    questions = {}
    for rec in records:
        child = db.query(Child).filter(Child.id == rec.child_id).first()
        questions[rec.id] = f"질문: {child.personality} 아이가 {rec.activity}를 했을 때 뭐라고 말해주나요?"
    valid_ids = [r.id for r in records]
    db.close()

    # RAG 유사도는 기록당 1번만 계산(반복 케이스는 질문이 같으니 캐시)
    print("RAG 유사도 계산 중...")
    sim_cache = {}
    for rid, q in questions.items():
        try:
            sim_cache[rid] = rag_max_sim(q)
        except Exception as e:
            sim_cache[rid] = None
            print(f"  [경고] 유사도 계산 실패 rid={rid}: {e}")

    # 테스트 케이스 구성: 유효 전체 + 앞 N개 반복 + 에러 케이스
    valid_cases = valid_ids + valid_ids[:REPEAT_FIRST_N]
    results = []
    print(f"\n유효 케이스 {len(valid_cases)}건 생성 시작 (반복 {REPEAT_FIRST_N} 포함)...")
    for i, rid in enumerate(valid_cases, 1):
        t0 = time.perf_counter()
        try:
            status, body = post_json("/feedbacks/generate", {"lesson_record_id": rid})
        except Exception as e:
            # 한 건 실패로 전체 평가가 멈추지 않도록 실패도 기록하고 계속 진행
            status, body = None, None
            print(f"  [경고] 요청 실패 rid={rid}: {type(e).__name__} {e}")
        elapsed = time.perf_counter() - t0
        fields_ok = bool(body) and all(body.get(k) for k in REQUIRED)
        sim = sim_cache.get(rid)
        rag_ok = (sim is not None and sim >= RAG_THRESHOLD)
        row = {
            "kind": "valid", "lesson_record_id": rid, "status": status,
            "elapsed": round(elapsed, 2), "fields_ok": fields_ok,
            "rag_sim": (round(sim, 4) if sim is not None else None), "rag_ok": rag_ok,
            "feedback_id": (body.get("id") if body else None),
        }
        # 생성 성공분에 시뮬레이션 검수 적용
        if status == 200 and row["feedback_id"]:
            decision, comment = simulated_review(fields_ok, rag_ok)
            patch_review(row["feedback_id"], decision, comment)
            row["review"] = decision
        results.append(row)
        print(f"  [{i}/{len(valid_cases)}] rid={rid} status={status} {elapsed:.1f}s "
              f"fields={'OK' if fields_ok else 'X'} sim={row['rag_sim']} review={row.get('review','-')}")
        time.sleep(0.5)  # rate-limit 여유

    # 에러(실패) 케이스
    print(f"\n에러 케이스 {len(ERROR_IDS)}건...")
    for rid in ERROR_IDS:
        status, _ = post_json("/feedbacks/generate", {"lesson_record_id": rid})
        handled = status in (404, 422)
        results.append({"kind": "error", "lesson_record_id": rid, "status": status, "handled": handled})
        print(f"  rid={rid} status={status} handled={'OK' if handled else 'X'}")

    # ── 지표 계산 ──
    valid = [r for r in results if r["kind"] == "valid"]
    errs = [r for r in results if r["kind"] == "error"]
    n = len(valid)
    e2e = sum(1 for r in valid if r["status"] == 200 and r["fields_ok"])
    jsonok = sum(1 for r in valid if r["fields_ok"])
    ragok = sum(1 for r in valid if r["rag_ok"])
    elapseds = [r["elapsed"] for r in valid]
    avg_elapsed = sum(elapseds) / n if n else 0
    median_elapsed = statistics.median(elapseds) if elapseds else 0
    # p95: 하위 95% 지점 (작은 표본에서도 안전하게 인덱스로 계산)
    p95_elapsed = (sorted(elapseds)[min(len(elapseds) - 1, int(round(0.95 * (len(elapseds) - 1))))]
                   if elapseds else 0)
    reviews = [r.get("review") for r in valid if r.get("review")]
    approved = reviews.count("approved")
    edited = reviews.count("edited")
    rejected = reviews.count("rejected")
    nr = len(reviews) or 1
    err_handled = sum(1 for r in errs if r["handled"])
    sims = [r["rag_sim"] for r in valid if r["rag_sim"] is not None]

    def pct(x, total):
        return round(100 * x / total, 1) if total else 0.0

    metrics = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_cases": len(results),
        "valid_cases": n,
        "error_cases": len(errs),
        "api_e2e_success_rate": pct(e2e, n),
        "json_format_success_rate": pct(jsonok, n),
        # ⚠️ 이름 바로잡음: 이건 '정답률'이 아니라 '유사도 임계값(0.70) 통과율'이다.
        #    실제 검색 정답률(Hit@k)은 evals/evaluate_retrieval.py 에서 정답셋으로 따로 측정한다.
        "similarity_threshold_pass_rate": pct(ragok, n),
        "similarity_threshold_pass_rate_note": "유사도 임계값 통과율(정답률 아님). 정답률은 Hit@k(evals/) 참고.",
        "rag_threshold": RAG_THRESHOLD,
        "rag_sim_min": round(min(sims), 4) if sims else None,
        "rag_sim_max": round(max(sims), 4) if sims else None,
        "rag_sim_avg": round(sum(sims) / len(sims), 4) if sims else None,
        "avg_response_sec": round(avg_elapsed, 2),
        "median_response_sec": round(median_elapsed, 2),
        "p95_response_sec": round(p95_elapsed, 2),
        "human_review_simulated": True,
        "human_review_note": "실제 강사 검수가 아니라 규칙 기반 시뮬레이션(simulated_review)임.",
        "review_approved_rate": pct(approved, nr),
        "review_edited_rate": pct(edited, nr),
        "review_rejected_rate": pct(rejected, nr),
        "error_handling_rate": pct(err_handled, len(errs)),
    }

    with open("metrics.json", "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "rows": results}, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 50)
    print("평가 지표 결과")
    print("=" * 50)
    for k, v in metrics.items():
        print(f"{k:28} : {v}")
    print("\nmetrics.json 저장 완료")


if __name__ == "__main__":
    main()
