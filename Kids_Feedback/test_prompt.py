# 임시 테스트 파일 (Day 4 ③ 확인용 - 나중에 지워도 됨)
# 가짜 아이/기록으로 build_prompt → generate_feedback 흐름을 돌려본다.

from types import SimpleNamespace   # 점(.)으로 꺼낼 수 있는 가짜 객체 만들기
from prompt_service import build_prompt
from llm_service import generate_feedback

# ── 가짜 수업 기록 (둘 다 똑같이 줌) ──
records = [
    SimpleNamespace(lesson_date="2026-06-28", activity="앞으로 줄넘기",
                    attitude="적극적", teacher_note="10개 성공"),
    SimpleNamespace(lesson_date="2026-06-25", activity="앞으로 줄넘기",
                    attitude="조금 위축됨", teacher_note="5개에서 멈춤"),
]

# ── 성격이 다른 아이 2명 ──
유리 = SimpleNamespace(
    name="유리", age=8, level="초급",
    memory_hint="머리 분홍 핀", personality="실패에 민감하고 쉽게 위축됨",
    preferred_feedback="작은 성공도 크게 칭찬", caution_note="혼나면 울 수 있음",
    material_note="줄넘기 자주 안 챙김", teacher_memo="천천히 접근",
)
민수 = SimpleNamespace(
    name="민수", age=9, level="중급",
    memory_hint="안경", personality="승부욕 강하고 도전 좋아함",
    preferred_feedback="목표 제시하며 자극", caution_note="잘난 척할 때 있음",
    material_note="특이사항 없음", teacher_memo="더 어려운 과제 줘도 됨",
)

for child in [유리, 민수]:
    print("=" * 50)
    print(f"[{child.name}] 피드백")
    print("=" * 50)
    prompt = build_prompt(child, records)
    print(generate_feedback(prompt))
    print()
