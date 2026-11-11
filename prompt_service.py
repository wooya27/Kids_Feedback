#  하는 일: 아이 정보 + 기록 + RAG 검색 근거(Top-3)를 **글 한 덩어리(프롬프트)**로 조립
#   비유: 주문서 작성


def format_rag_context(rag_result):
    """rag_search 결과(dict)를 프롬프트에 넣을 '근거 블록' 문자열로 만든다.
    - Top-3 각 청크를 출처·유사도와 함께 번호로 나열한다(생성에서 어떤 근거를 썼는지 추적 가능).
    - 근거가 약하면(low_relevance) '지침을 지어내지 말라'는 안내를 덧붙인다.
    - 예전처럼 문자열이 그대로 들어오면 그대로 사용(하위 호환).
    """
    if isinstance(rag_result, str):
        return rag_result, False
    if not rag_result or not rag_result.get("hits"):
        return "[검색된 지도 근거 없음]", True

    low = rag_result.get("low_relevance", False)
    lines = []
    for i, h in enumerate(rag_result["hits"], 1):
        src = h.get("source_file", "?")
        title = h.get("title", "")
        score = h.get("score")
        lines.append(f"(근거{i}) [출처: {src} | 제목: {title} | 유사도: {score}]\n{h.get('text','')}")
    block = "\n\n".join(lines)
    if low:
        block += ("\n\n[주의] 위 근거들의 관련도가 낮습니다(근거 부족). "
                  "확실한 근거가 없는 구체적 지도 방법을 지어내지 말고, "
                  "일반적이고 안전한 범위에서만 작성하세요.")
    return block, low


def build_prompt(child, records, rag_context):
    # child       = 아이 한 명 정보 (child.name, child.age ... 점으로 꺼냄)
    # records     = 그 아이의 수업기록 리스트
    # rag_context = rag_search가 돌려준 결과(dict: Top-3 hits + 출처/점수)  ← P0-5에서 구조 변경

    # ── 1) 기록 리스트를 글로 만든다 (한 기록 = 한 줄) ──
    records_text = ""
    for r in records:
        records_text += f"- {r.lesson_date}: 활동 {r.activity}, 태도 {r.attitude}, 강사메모 {r.teacher_note}\n"

    # ── 2) RAG 근거(Top-3)를 출처와 함께 글로 만든다 ──
    guide_text, _low = format_rag_context(rag_context)

    # ── 3) 위에서 만든 글을 끼워서 프롬프트 조립 ──
    prompt = f"""[역할]
당신은 아동 줄넘기 수업 강사를 돕는 AI 피드백 코치입니다.

[아이 프로필]
- 이름: {child.name}
- 나이: {child.age}
- 수준: {child.level}
- 외우기용 특징: {child.memory_hint}
- 성향: {child.personality}
- 좋아하는 피드백 방식: {child.preferred_feedback}
- 주의할 점: {child.caution_note}
- 준비물 특이사항: {child.material_note}
- 강사 메모: {child.teacher_memo}

[최근 수업 기록]
{records_text}

[지도 가이드 — 검색된 근거 Top-3]
{guide_text}

[작성 규칙]
1. 아이의 성향과 좋아하는 피드백 방식을 반영하세요.
2. 외우기용 특징은 학부모용 피드백에 직접 노출하지 마세요.
3. 주의할 점은 강사용 메모에만 반영하세요.
4. 학부모용 피드백에는 따뜻하고 자연스러운 표현만 사용하세요.
5. 다른 아이와 비교하지 마세요.
6. 진단처럼 보이는 표현을 사용하지 마세요.
7. 다음 목표는 최근 기록보다 조금 도전적인 수준으로 제안하세요.
8. 위 [지도 가이드]의 근거에 기반해 작성하되, 근거가 부족하면 지어내지 마세요.

[출력 형식]
아래 JSON 형식으로만 출력하세요.

{{
  "next_goal": "...",
  "teacher_feedback": "...",
  "parent_feedback": "..."
}}

"""
    return prompt
