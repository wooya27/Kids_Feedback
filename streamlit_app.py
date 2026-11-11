"""Kids_Feedback 강사용 UI (Streamlit).

기존 FastAPI 백엔드(기본 http://localhost:8001)에 HTTP로 붙어서,
아이 선택 → 프로필 → 수업기록 선택 → 피드백 생성 → (Top-3 근거) → 강사 검수 → 최종본
흐름을 화면으로 제공한다. 백엔드 로직은 그대로 두고 '얇은 화면'만 얹는다.

실행:
  .venv/Scripts/python.exe -m streamlit run streamlit_app.py
전제: docker compose up -d (api가 localhost:8001 에서 떠 있어야 함)
"""

import httpx
import streamlit as st

st.set_page_config(page_title="Kids Feedback 강사용", page_icon=":material/sports_gymnastics:",
                   layout="centered")

REVIEW_LABELS = {"approved": "승인", "edited": "수정", "rejected": "거절"}


# ── 공통: API 호출 헬퍼 ───────────────────────────────────
def api_base() -> str:
    return st.session_state.get("api_base", "http://localhost:8001").rstrip("/")


def api_get(path: str):
    r = httpx.get(api_base() + path, timeout=30)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=20, show_spinner=False)
def load_children(base: str):
    r = httpx.get(base + "/children/", timeout=30)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=20, show_spinner=False)
def load_records(base: str, child_id: int):
    r = httpx.get(base + f"/lesson/{child_id}/lesson-records", timeout=30)
    r.raise_for_status()
    return r.json()


def rag_preview(personality: str, activity: str):
    """백엔드와 동일한 RAG로 Top-3 근거를 미리 보여준다(로컬 rag_service 사용)."""
    from rag.rag_service import rag_search
    question = f"질문: {personality} 아이가 {activity}를 했을 때 뭐라고 말해주나요?"
    return rag_search(question, k=3)


# ── 사이드바: 연결 + 아이 선택 ────────────────────────────
with st.sidebar:
    st.header("설정", divider="gray")
    st.text_input("API 주소", key="api_base", value=st.session_state.get("api_base", "http://localhost:8001"))
    if st.button("새로고침", icon=":material/refresh:", width="stretch"):
        st.cache_data.clear()
        st.rerun()

    st.subheader("아이 선택")
    try:
        children = load_children(api_base())
    except Exception as e:
        st.error(f"API 연결 실패: {e}")
        st.caption("docker compose up 으로 api(8001)를 먼저 띄우세요.")
        st.stop()

    if not children:
        st.warning("등록된 아이가 없습니다. seed_eval.py 로 합성 데이터를 넣으세요.")
        st.stop()

    options = {f"{c['name']} ({c.get('age','?')}세)": c for c in children}
    picked = st.selectbox("아이", list(options.keys()), label_visibility="collapsed")
    child = options[picked]


# ── 본문 ─────────────────────────────────────────────────
st.title("아동 줄넘기 피드백")
st.caption("AI 초안 → 강사 검수 → 최종 전달 · 모든 데이터는 합성(가짜)입니다")

# 1) 프로필 카드
with st.container(border=True):
    st.subheader(f"{child['name']}", divider="gray")
    c1, c2, c3 = st.columns(3)
    c1.metric("나이", f"{child.get('age','?')}세")
    c2.metric("수준", child.get("level") or "-")
    c3.metric("ID", child["id"])
    if child.get("personality"):
        st.markdown(f"**성향** · {child['personality']}")
    if child.get("preferred_feedback"):
        st.markdown(f"**선호 피드백** · {child['preferred_feedback']}")
    if child.get("caution_note"):
        st.markdown(f"**주의** · {child['caution_note']}")

# 2) 수업 기록 선택
st.subheader("수업 기록", divider="gray")
records = load_records(api_base(), child["id"])
if not records:
    st.info("이 아이의 수업 기록이 없습니다.")
    st.stop()

rec_options = {f"{r['lesson_date']} · {r.get('activity','?')}": r for r in records}
rec_label = st.selectbox("기록 선택", list(rec_options.keys()))
record = rec_options[rec_label]
with st.container(border=True):
    st.markdown(f"**활동** {record.get('activity','-')} · **태도** {record.get('attitude','-')}")
    st.caption(f"수행: {record.get('performance','-')} / 어려움: {record.get('difficulty','-')}")

# 3) RAG 근거 미리보기 (선택)
with st.expander("검색 근거 미리보기 (Top-3)", icon=":material/search:"):
    if st.button("이 상황의 근거 검색", icon=":material/manage_search:"):
        try:
            with st.spinner("RAG 검색 중…"):
                res = rag_preview(child.get("personality") or "", record.get("activity") or "")
            if res["low_relevance"]:
                st.warning(f"관련 근거가 약합니다 (최고 유사도 {res['best_score']}). 생성 시 지어내지 않도록 처리됩니다.")
            for i, h in enumerate(res["hits"], 1):
                st.markdown(f"**근거 {i}** · `{h['source_file'].split('/')[-1]}` · 유사도 {h['score']}")
                st.caption(h["text"][:160] + ("…" if len(h["text"]) > 160 else ""))
        except Exception as e:
            st.error(f"검색 실패(키/쿼터 확인): {e}")

# 4) 피드백 생성
st.subheader("피드백 생성", divider="gray")
if st.button("AI 피드백 생성", type="primary", icon=":material/auto_awesome:", width="stretch"):
    try:
        with st.spinner("생성 중… (RAG + LLM, 10~20초)"):
            r = httpx.post(api_base() + "/feedbacks/generate",
                           json={"lesson_record_id": record["id"]}, timeout=120)
        if r.status_code == 200:
            st.session_state["feedback"] = r.json()
            st.toast("생성 완료", icon=":material/check_circle:")
        else:
            body = r.json().get("detail", {})
            st.session_state.pop("feedback", None)
            st.error(f"생성 실패 (검증 미통과 → 저장 안 됨): {body.get('error_type', r.status_code)}")
    except Exception as e:
        st.error(f"요청 실패: {e}")

# 5) 생성 결과 + 검수
fb = st.session_state.get("feedback")
if fb and fb.get("lesson_record_id") == record["id"]:
    st.success(f"생성된 피드백 (ID {fb['id']})", icon=":material/draft:")
    with st.container(border=True):
        st.markdown(f"**다음 목표**\n\n{fb['next_goal']}")
        st.divider()
        st.markdown(f"**강사용**\n\n{fb['teacher_feedback']}")
        st.divider()
        st.markdown(f"**학부모용**\n\n{fb['parent_feedback']}")

    st.subheader("강사 검수", divider="gray")
    decision = st.segmented_control("검수 결과", ["approved", "edited", "rejected"],
                                    format_func=lambda s: REVIEW_LABELS[s], default="approved")
    comment = st.text_input("코멘트 (선택)", placeholder="예: 학부모 문장 더 쉽게")

    edited = {}
    if decision == "edited":
        st.caption("원본은 보존되고, 수정본은 따로 저장됩니다.")
        edited["edited_next_goal"] = st.text_area("다음 목표(수정)", value=fb["next_goal"])
        edited["edited_teacher_feedback"] = st.text_area("강사용(수정)", value=fb["teacher_feedback"])
        edited["edited_parent_feedback"] = st.text_area("학부모용(수정)", value=fb["parent_feedback"])

    if st.button("검수 저장", icon=":material/save:", width="stretch"):
        payload = {"review_status": decision, "review_comment": comment or None, **edited}
        try:
            r = httpx.patch(api_base() + f"/feedbacks/{fb['id']}/review", json=payload, timeout=30)
            if r.status_code == 200:
                st.session_state["feedback"] = r.json()
                st.toast(f"{REVIEW_LABELS[decision]} 저장됨", icon=":material/check:")
                st.rerun()
            else:
                st.error(f"저장 실패: {r.json().get('detail', r.status_code)}")
        except Exception as e:
            st.error(f"요청 실패: {e}")

    # 최종본 (승인/수정만 전달 가능)
    if fb.get("review_status") in ("approved", "edited"):
        try:
            final = api_get(f"/feedbacks/{fb['id']}/final")
            with st.container(border=True):
                st.markdown(f"**최종 전달본** ({REVIEW_LABELS.get(final['review_status'], final['review_status'])})")
                st.markdown(final["final"]["parent_feedback"])
        except httpx.HTTPStatusError:
            pass
    elif fb.get("review_status") == "rejected":
        st.info("거절됨 — 최종 전달본이 없습니다.")
    else:
        st.caption("승인 전에는 학부모 최종본이 전달되지 않습니다.")
