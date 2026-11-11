# tests/test_feedback_graph.py
# P0-1 검증: "검증에 실패한 AI 피드백은 저장하지 않는다"를 자동으로 확인한다.
#
# 가짜 LLM(generate_feedback)과 가짜 RAG(rag_search)를 끼워넣어
# 여러 LLM 응답 시나리오에서 DB 저장이 되는지/안 되는지를 본다.
#
# 패치 위치 주의: graph.feedback_graph 가 `from ... import generate_feedback`,
# `from ... import rag_search` 로 '이름을 자기 모듈로 가져왔기' 때문에,
# 바꿔치기도 graph.feedback_graph.generate_feedback 를 대상으로 해야 한다.

import json
import pytest

import graph.feedback_graph as g
from models import Feedback


@pytest.fixture(autouse=True)
def fake_rag(monkeypatch):
    """모든 테스트에서 RAG는 고정 Top-3 결과(dict)를 돌려주도록(네트워크/키 불필요)."""
    fake_result = {
        "hits": [{"chunk_id": "rag_docs/위축형_칭찬법.md::00", "source_file": "rag_docs/위축형_칭찬법.md",
                  "title": "질문: ...", "category": "성향별", "score": 0.82, "text": "시도를 칭찬한다."}],
        "best_score": 0.82, "low_relevance": False, "query": "q",
    }
    monkeypatch.setattr(g, "rag_search", lambda q: fake_result)


def _set_llm(monkeypatch, responses):
    """generate_feedback이 호출될 때마다 responses를 순서대로 돌려주게 만든다.
    responses가 다 떨어지면 마지막 값을 계속 반환한다(재시도 대비)."""
    box = {"i": 0}

    def fake_generate(prompt):
        i = box["i"]
        box["i"] += 1
        return responses[i] if i < len(responses) else responses[-1]

    monkeypatch.setattr(g, "generate_feedback", fake_generate)


VALID_JSON = json.dumps({
    "next_goal": "양발 모아 5회 연속 성공하기",
    "teacher_feedback": "머뭇거려도 끝까지 시도한 점을 짚어주세요.",
    "parent_feedback": "오늘도 포기하지 않고 끝까지 해냈어요.",
}, ensure_ascii=False)


def _count(db):
    return db.query(Feedback).count()


# ── 1) 정상 입력은 저장된다 (200 + 행 1개) ──
def test_valid_feedback_is_saved(client, db_session, seeded_child, monkeypatch):
    _set_llm(monkeypatch, [VALID_JSON])
    assert _count(db_session) == 0

    res = client.post("/feedbacks/generate", json={"lesson_record_id": seeded_child})

    assert res.status_code == 200, res.text
    assert _count(db_session) == 1
    body = res.json()
    assert body["next_goal"] and body["teacher_feedback"] and body["parent_feedback"]


# ── 2) 잘못된 JSON은 2회 실패 후에도 저장 안 됨 (신규 행 0건) ──
def test_bad_json_is_not_saved(client, db_session, seeded_child, monkeypatch):
    _set_llm(monkeypatch, ["이건 JSON이 아니라 그냥 문장입니다"])

    res = client.post("/feedbacks/generate", json={"lesson_record_id": seeded_child})

    assert res.status_code == 502
    assert res.json()["detail"]["error_type"] == "json_parse_error"
    assert _count(db_session) == 0


# ── 3) 필수 필드 누락은 저장 안 됨 ──
def test_missing_field_is_not_saved(client, db_session, seeded_child, monkeypatch):
    bad = json.dumps({"next_goal": "A", "teacher_feedback": "B"}, ensure_ascii=False)  # parent 없음
    _set_llm(monkeypatch, [bad])

    res = client.post("/feedbacks/generate", json={"lesson_record_id": seeded_child})

    assert res.status_code == 502
    assert res.json()["detail"]["error_type"] == "schema_validation_error"
    assert _count(db_session) == 0


# ── 4) 빈 문자열(공백만) 필드도 저장 안 됨 ──
def test_blank_field_is_not_saved(client, db_session, seeded_child, monkeypatch):
    bad = json.dumps({"next_goal": "   ", "teacher_feedback": "B", "parent_feedback": "C"},
                     ensure_ascii=False)
    _set_llm(monkeypatch, [bad])

    res = client.post("/feedbacks/generate", json={"lesson_record_id": seeded_child})

    assert res.status_code == 502
    assert res.json()["detail"]["error_type"] == "schema_validation_error"
    assert _count(db_session) == 0


# ── 5) 1회 실패 → 2회째 성공이면 저장된다 (재시도 가드 동작 확인) ──
def test_retry_then_success_is_saved(client, db_session, seeded_child, monkeypatch):
    _set_llm(monkeypatch, ["깨진 JSON", VALID_JSON])

    res = client.post("/feedbacks/generate", json={"lesson_record_id": seeded_child})

    assert res.status_code == 200, res.text
    assert _count(db_session) == 1


# ── 6) 없는 수업 ID는 404 (그래프 들어가기 전에 차단) ──
def test_missing_lesson_record_returns_404(client, db_session, monkeypatch):
    _set_llm(monkeypatch, [VALID_JSON])

    res = client.post("/feedbacks/generate", json={"lesson_record_id": 999999})

    assert res.status_code == 404
    assert _count(db_session) == 0
