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
"""
    return prompt
