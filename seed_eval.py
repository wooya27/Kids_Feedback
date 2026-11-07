# seed_eval.py
# 포트폴리오 '평가지표' 산출용 데이터셋을 DB에 심는다.
# - 다양한 성향(위축형/산만형/완벽주의형/리더형...)의 아이 8명
# - 활동도 'RAG 지도기준(위축형 칭찬법)'과 가까운 것 ~ 먼 것까지 섞음
#   → RAG 검색 성공률이 0%도 100%도 아닌, 설명 가능한 숫자가 나오게 하기 위함
# - 기록이 1개뿐인 학생도 포함(= '최근 기록이 적은 학생' 케이스)
#
# 재현성을 위해 기존 feedbacks/lesson_records/children을 싹 비우고(TRUNCATE) 다시 심는다.
# ⚠️ 컨테이너 안에서 실행해야 Docker db를 가리킨다:
#     docker compose cp seed_eval.py api:/app/seed_eval.py
#     docker compose exec api python seed_eval.py

from datetime import date

from sqlalchemy import text
from database import SessionLocal, engine, Base
from models import Child, LessonRecord, Feedback  # noqa: F401 (테이블 등록용)

Base.metadata.create_all(bind=engine)

# (성향, 활동, 기대 RAG 적합도)  — 활동 텍스트가 위축형 지도기준과 얼마나 겹치냐로 설계
CHILDREN = [
    # name, age, personality, 기록들[(activity, performance, attitude, difficulty)]
    ("유리", 8, "위축형(소심하고 실수를 두려워함)", [
        ("양발 모아 뛰기", "3번 중 2번 성공", "실수할까봐 머뭇거림", "착지에서 균형 무너짐"),
        ("한 발 번갈아 뛰기", "끝까지 시도함", "틀리면 '못해요' 라고 말함", "리듬 유지 어려움"),
        ("친구 앞에서 동작 발표", "작게 성공", "얼굴 빨개지고 소극적", "시선 부담"),
    ]),
    ("서연", 7, "완벽주의형(실수를 크게 두려워함)", [
        ("줄넘기 연속 넘기", "5회 성공", "한 번 걸리자 포기하려 함", "실패 후 재시도 거부"),
        ("훌라후프 허리돌리기", "10초 유지", "완벽히 안 되면 짜증", "지속 시간"),
        ("매트에서 구르기", "성공", "틀릴까봐 긴장", "방향 감각"),
    ]),
    ("민준", 9, "산만형(주의가 쉽게 흩어지고 충동적)", [
        ("규칙 있는 술래잡기", "규칙 자주 잊음", "에너지 넘침", "순서 기다리기"),
        ("박자 맞춰 손뼉치기", "중간에 딴짓", "집중 5분 유지", "지시 끝까지 듣기"),
        ("색깔 순서대로 점프", "순서 섞임", "즐거워함", "순서 기억"),
        ("정지 신호에 멈추기", "절반 성공", "충동 조절 어려움", "억제력"),
    ]),
    ("도윤", 10, "자신감 있는 리더형", [
        ("팀 이어달리기 주장", "팀 1등", "친구들 독려함", "혼자 앞서가려 함"),
        ("블록으로 구조물 쌓기 리더", "완성", "주도적", "역할 분담 양보"),
    ]),
    ("하은", 8, "위축형(낯가림이 심함)", [
        ("처음 만난 친구와 짝활동", "끝까지 참여", "말을 거의 안 함", "먼저 다가가기"),
        ("큰 소리로 숫자 세기", "작은 목소리로 성공", "부끄러워함", "발성 크기"),
    ]),
    ("지호", 9, "산만형(충동적이고 승부욕 강함)", [
        ("피아노 리듬 따라치기", "반복 실수", "지루해함", "집중 유지"),
        ("덧셈 암산 게임", "빠르지만 틀림", "이기려고 서두름", "정확도"),
        ("미로 찾기", "성공", "성급함", "차분히 보기"),
    ]),
    ("수아", 6, "위축형(소극적이고 조용함)", [
        ("친구에게 공 굴려 전달", "성공", "눈 잘 안 마주침", "상호작용 시작"),
    ]),  # 기록 1개 = '최근 기록이 적은 학생' 케이스
    ("건우", 11, "일반형(무난하고 성실함)", [
        ("기초 체력 순환운동", "전 구간 완주", "성실히 참여", "특이사항 없음"),
        ("단체 스트레칭 리드", "무난", "협조적", "없음"),
        ("표적 던지기", "7/10 명중", "집중함", "거리 조절"),
    ]),
]


def main():
    db = SessionLocal()
    try:
        # 재현성: 기존 데이터 싹 비우고 ID도 1부터 다시
        db.execute(text("TRUNCATE feedbacks, lesson_records, children RESTART IDENTITY CASCADE"))
        db.commit()

        n_child = 0
        n_rec = 0
        for name, age, personality, recs in CHILDREN:
            child = Child(
                name=name,
                age=age,
                personality=personality,
                preferred_feedback="구체적 칭찬 + 다음 한 걸음",
            )
            db.add(child)
            db.flush()  # child.id 확보
            n_child += 1
            for i, (activity, performance, attitude, difficulty) in enumerate(recs):
                db.add(LessonRecord(
                    child_id=child.id,
                    lesson_date=date(2026, 11, 1 + i),
                    activity=activity,
                    performance=performance,
                    attitude=attitude,
                    difficulty=difficulty,
                    teacher_note=f"{name} {i+1}회차",
                ))
                n_rec += 1
        db.commit()
        print(f"seeded: children={n_child}, lesson_records={n_rec}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
