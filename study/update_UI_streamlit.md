# [추가] 강사용 UI (Streamlit) — streamlit_app.py

> 체크리스트 밖 추가 작업. `plan/ui.md` 설계대로 강사용 화면을 만들었다.
> 백엔드 로직은 그대로 두고 **기존 FastAPI에 HTTP로 붙는 '얇은 화면'**만 얹었다.

## 1. 구조 / 데이터 흐름
```
Streamlit(호스트, :8501) ──HTTP──▶ FastAPI(:8001, 도커)
  사이드바: API주소 + 아이 선택(GET /children/)
     ▼
  프로필 카드(아이 정보)
     ▼
  수업기록 선택(GET /lesson/{id}/lesson-records)
     ▼
  [검색 근거 미리보기] → 로컬 rag_search(Top-3) (선택)
     ▼
  [AI 피드백 생성] → POST /feedbacks/generate
     │  200 → 결과 표시 / 502 → "검증 미통과, 저장 안 됨"
     ▼
  강사 검수: segmented_control(승인/수정/거절) → PATCH /feedbacks/{id}/review
     ▼
  최종 전달본: GET /feedbacks/{id}/final (승인/수정만, 그 외 차단 안내)
```

## 2. 알아야 하는 Streamlit 개념(이번에 쓴 것)
- `st.set_page_config(...)`: 탭 제목·아이콘·레이아웃. 스크립트 **맨 위** 1회.
- `st.session_state`: 리런(재실행) 사이에 값 유지. 생성된 피드백을 `st.session_state["feedback"]`에 보관.
- `@st.cache_data(ttl=20)`: GET 결과 캐시(아이·기록). "새로고침" 버튼은 `st.cache_data.clear()`.
- `st.segmented_control`: 2~5개 선택지를 버튼처럼. (라디오보다 권장)
- `st.container(border=True)`: 카드형 묶음. `st.columns`로 지표 3개 배치.
- 버튼은 기본 `width="content"` → 가로 꽉 채우려면 `width="stretch"`. (`use_container_width`는 폐기됨)
- Material 아이콘 `:material/이름:` 사용(이모지 대신).
- 느린 호출은 `st.spinner`, 완료는 `st.toast`.

## 3. 백엔드와의 연결 포인트
- UI는 **로직을 복제하지 않는다.** 생성/검수/최종본 전부 기존 API를 호출.
- 단, "Top-3 근거 미리보기"만 화면에서 직접 `rag.rag_service.rag_search`를 불러 보여준다(생성 API가 근거를 응답에 포함하지 않기 때문). 백엔드가 쓰는 것과 같은 RAG라 결과가 일치.
- `.streamlit/config.toml`: 외형은 CSS 대신 config로(테마 색/반경).

## 4. 실행 / 검증
```bash
docker compose up -d                      # api(8001) 먼저
.venv/Scripts/python.exe -m streamlit run streamlit_app.py   # → http://localhost:8501
```
- 검증(개발용): agent API(`--server.enableAgentApi=true`)로 헤드리스 로드 → `status: ready`, 아이/기록 정상 렌더 확인(2026-11-12). 콘솔 경고 없음.
- 생성 버튼은 유료(LLM)·DB 쓰기라 자동 검증에서는 누르지 않음 — 실제 생성은 화면에서 직접.

## 5. 의존성
- `requirements.txt`에 `streamlit`, `httpx` 추가. UI는 **호스트에서** 실행(도커 아님 — 도커 API를 localhost:8001로 호출).
- `.venv`에 streamlit 1.67 설치됨.

## 6. 한 줄 요약
> 기존 API에 붙는 얇은 Streamlit 화면으로 '아이→생성→검수→최종본' 흐름을 시연 가능하게 만들었다. 로직은 백엔드에 그대로 둠.
