# tests/test_feedback_api.py
# P1-3 검증: Human Review에서 수정 본문을 원본과 별도로 저장하고,
# 승인 전에는 최종본 전달을 막는다. 상태 전이도 검사한다.

import pytest
from datetime import date
from models import Child, LessonRecord, Feedback


@pytest.fixture()
def feedback_row(db_session):
    """AI 원본 초안 1건을 DB에 직접 심고 feedback_id를 돌려준다."""
    child = Child(name="아이", age=8, personality="위축형")
    db_session.add(child)
    db_session.flush()
    rec = LessonRecord(child_id=child.id, lesson_date=date(2026, 11, 1), activity="줄넘기")
    db_session.add(rec)
    db_session.flush()
    fb = Feedback(child_id=child.id, lesson_record_id=rec.id,
                  next_goal="원본목표", teacher_feedback="원본강사", parent_feedback="원본학부모")
    db_session.add(fb)
    db_session.commit()
    return fb.id


def test_edited_stores_body_and_preserves_original(client, db_session, feedback_row):
    res = client.patch(f"/feedbacks/{feedback_row}/review", json={
        "review_status": "edited",
        "review_comment": "학부모 문장 더 쉽게",
        "edited_parent_feedback": "수정된 학부모 문장",
    })
    assert res.status_code == 200, res.text
    body = res.json()
    # 원본 보존
    assert body["parent_feedback"] == "원본학부모"
    # 수정본 저장 (안 보낸 필드는 원본 복사)
    assert body["edited_parent_feedback"] == "수정된 학부모 문장"
    assert body["edited_next_goal"] == "원본목표"
    assert body["review_status"] == "edited"


def test_final_returns_edited_when_edited(client, feedback_row):
    client.patch(f"/feedbacks/{feedback_row}/review", json={
        "review_status": "edited", "edited_parent_feedback": "수정본"})
    res = client.get(f"/feedbacks/{feedback_row}/final")
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["final"]["parent_feedback"] == "수정본"
    assert data["original_draft"]["parent_feedback"] == "원본학부모"   # 서로 다른 값으로 조회 가능


def test_final_returns_original_when_approved(client, feedback_row):
    client.patch(f"/feedbacks/{feedback_row}/review", json={"review_status": "approved"})
    res = client.get(f"/feedbacks/{feedback_row}/final")
    assert res.status_code == 200
    assert res.json()["final"]["parent_feedback"] == "원본학부모"


def test_final_blocked_before_approval(client, feedback_row):
    # pending 상태 → 최종본 전달 차단
    res = client.get(f"/feedbacks/{feedback_row}/final")
    assert res.status_code == 409


def test_rejected_blocks_final(client, feedback_row):
    client.patch(f"/feedbacks/{feedback_row}/review", json={"review_status": "rejected"})
    res = client.get(f"/feedbacks/{feedback_row}/final")
    assert res.status_code == 409


def test_invalid_transition_locked_after_approved(client, feedback_row):
    client.patch(f"/feedbacks/{feedback_row}/review", json={"review_status": "approved"})
    # approved는 확정 → 다시 edited로 못 바꿈
    res = client.patch(f"/feedbacks/{feedback_row}/review", json={
        "review_status": "edited", "edited_parent_feedback": "x"})
    assert res.status_code == 409


def test_edited_without_body_rejected(client, feedback_row):
    res = client.patch(f"/feedbacks/{feedback_row}/review", json={"review_status": "edited"})
    assert res.status_code == 400


def test_invalid_status_rejected(client, feedback_row):
    res = client.patch(f"/feedbacks/{feedback_row}/review", json={"review_status": "maybe"})
    assert res.status_code == 400


def test_feedbacks_are_isolated_per_child(client, db_session):
    """학생별 데이터 혼선 방지: GET /feedbacks/{child_id}는 그 아이 것만 돌려준다."""
    c1 = Child(name="아이1", age=8); c2 = Child(name="아이2", age=9)
    db_session.add_all([c1, c2]); db_session.flush()
    r1 = LessonRecord(child_id=c1.id, lesson_date=date(2026, 11, 1), activity="a")
    r2 = LessonRecord(child_id=c2.id, lesson_date=date(2026, 11, 1), activity="b")
    db_session.add_all([r1, r2]); db_session.flush()
    db_session.add_all([
        Feedback(child_id=c1.id, lesson_record_id=r1.id, next_goal="g1",
                 teacher_feedback="t1", parent_feedback="p1"),
        Feedback(child_id=c2.id, lesson_record_id=r2.id, next_goal="g2",
                 teacher_feedback="t2", parent_feedback="p2"),
    ])
    db_session.commit()

    res = client.get(f"/feedbacks/{c1.id}")
    assert res.status_code == 200
    data = res.json()
    assert all(f["child_id"] == c1.id for f in data)
    assert len(data) == 1
