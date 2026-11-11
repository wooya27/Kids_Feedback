# tests/test_webhook.py
# P0-2/P1-4: n8n 웹훅 워크플로가 '동적 ID 전달' 구조를 갖췄는지 정적으로 검증한다.
# (n8n 실행 없이 JSON 구조만 확인 — 실제 2건 호출 검증은 도커 환경에서)

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WF = json.loads((ROOT / "n8n_workflow_webhook.json").read_text(encoding="utf-8"))


def _node(name):
    return next(n for n in WF["nodes"] if n["name"] == name)


def test_http_body_is_dynamic_expression():
    """HTTP Request 본문이 고정 1이 아니라 표현식으로 ID를 매핑하는가."""
    http = _node("Call Kids_Feedback API")
    body = http["parameters"]["jsonBody"]
    assert body.startswith("="), "표현식(=)이 아니라 고정값이다"
    assert "$json.lesson_record_id" in body
    assert '"lesson_record_id": 1' not in body   # 고정값 흔적 없어야


def test_validation_node_exists_and_wired():
    """누락/타입오류를 거르는 Code 검증 노드가 있고, Webhook→Validate→HTTP로 연결됐는가."""
    code = _node("Validate lesson_record_id")
    assert code["type"] == "n8n-nodes-base.code"
    js = code["parameters"]["jsCode"]
    assert "lesson_record_id" in js
    assert "throw" in js                          # 잘못된 입력 거절 로직

    conns = WF["connections"]
    assert conns["Webhook"]["main"][0][0]["node"] == "Validate lesson_record_id"
    assert conns["Validate lesson_record_id"]["main"][0][0]["node"] == "Call Kids_Feedback API"
