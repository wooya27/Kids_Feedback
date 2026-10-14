#  하는 일: 아이 정보 + 기록을 **글 한 덩어리(프롬프트)**로 조립
#   비유: 주문서 작성


def build_prompt(child, records):
    # child   = 아이 한 명 정보 (child.name, child.age ... 점으로 꺼냄)
    # records = 그 아이의 수업기록 리스트

    # ── 1) 기록 리스트를 글로 만든다 (한 기록 = 한 줄) ──
    records_text = ""
    for r in records:
        records_text += f"- {r.lesson_date}: 활동 {r.activity}, 태도 {r.attitude}, 강사메모 {r.teacher_note}\n"

    # ── 2) 위에서 만든 글을 끼워서 프롬프트 조립 ──
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

[작성 규칙]
1. 아이의 성향과 좋아하는 피드백 방식을 반영하세요.
2. 외우기용 특징은 학부모용 피드백에 직접 노출하지 마세요.
3. 주의할 점은 강사용 메모에만 반영하세요.
4. 학부모용 피드백에는 따뜻하고 자연스러운 표현만 사용하세요.
5. 다른 아이와 비교하지 마세요.
6. 진단처럼 보이는 표현을 사용하지 마세요.
7. 다음 목표는 최근 기록보다 조금 도전적인 수준으로 제안하세요.

[출력 형식]
아래 JSON 형식으로만 출력하세요.

{{
  "next_goal": "...",
  "teacher_feedback": "...",
  "parent_feedback": "..."
}}

"""
    return prompt