# Day 4 학습 정리 — 2026-06-29 (진행 중)

> LLM(생성 AI) 연결 단계. 프롬프트 조립 → API 호출 → 프로필 반영.
> 이 프로젝트는 **Gemini API**(Google AI Studio)로 진행.

---

## 세션 3 — `prompt_service.py` (프롬프트 조립)

### 1. 프롬프트(prompt)란?
AI에게 보내는 **글 한 덩어리**(질문지/지시문). "너는 누구고, 이 정보를 보고, 이런 규칙으로, 이런 형식으로 답해". AI는 이 글을 읽고 답을 만든다. → 프롬프트가 좋아야 답이 좋다.

### 2. 이 파일이 하는 일
아직 AI를 부르지 않는다. **빈칸 채우기**만 한다.
```
템플릿  "이름: {name}"  +  데이터 name="유리"  →  "이름: 유리"
```
(엑셀 메일머지, 양식 빈칸 채우기와 같은 원리)

### 3. f-string — 문자열에 변수 끼우기
문자열 앞에 `f`를 붙이고 `{변수}` 자리에 값이 들어간다.
```python
name = "유리"; age = 12
text = f"이름: {name}, 나이: {age}"   # → 이름: 유리, 나이: 12
```
여러 줄은 `"""..."""`(따옴표 3개)로 감싼다.

### 4. for 반복문 — 리스트를 글로 풀기
`records`는 기록이 여러 개 든 **리스트**. 그냥 `{records}`를 넣으면 객체 덩어리가 찍힌다.
→ 하나씩 꺼내서 글로 옮겨야 한다.
```python
records_text = ""                 # ① 빈 종이에서 시작
for r in records:                 # ② 기록을 하나씩 r에 담아 반복 (5개면 5번)
    records_text += f"- {r.lesson_date}: 활동 {r.activity}\n"   # ③ 한 줄씩 이어붙임
```
- `r`은 기록 한 개 → `r.lesson_date`, `r.activity` 처럼 **점(.)으로 꺼냄** (아이 `child.name`과 같은 원리)
- `+=` = 기존 문자열 뒤에 더 붙이기 (누적)
- `\n` = 줄바꿈(엔터). 없으면 다 한 줄에 붙는다.

### 5. 내가 했던 실수 & 배운 점
- **들여쓰기 = 함수 소속.** `def` 아래 들여쓰기 된 줄만 함수 안. 맨 왼쪽에 붙이면 함수 밖으로 튕긴다.
- **`print` vs `return`:** `print`는 화면에 보여주고 버림. `return`은 값을 호출한 쪽에 건넨다. 다음 파일(llm_service.py)에 넘겨야 하니 `return`.
- **반복문 안에는 "기록 정보"만.** "~을 작성합니다" 같은 AI 지시문은 반복문이 아니라 프롬프트 템플릿(`f"""`)에 들어간다.
- `recent_records`, `today_record`, `rag_context`는 안 만든 변수 → 지금은 안 씀. `rag_context`는 Day 8(RAG) 거.

### 완성 코드 형태
```python
def build_prompt(child, records):
    records_text = ""
    for r in records:
        records_text += f"- {r.lesson_date}: 활동 {r.activity}, 태도 {r.attitude}, 강사메모 {r.teacher_note}\n"

    prompt = f"""[역할]
당신은 아동 줄넘기 수업 강사를 돕는 AI 피드백 코치입니다.

[아이 프로필]
- 이름: {child.name}
... (프로필 필드들) ...

[최근 수업 기록]
{records_text}
"""
    return prompt
```

---

## 세션 4 — `llm_service.py` (Gemini API 호출)  ← 진행 예정

### API / API 키 개념
- **API:** 남의 프로그램(여기선 Gemini)에 일을 시키고 결과를 받아오는 창구.
- **API 키:** 그 창구를 쓸 권한을 증명하는 **비밀번호**. → 코드에 직접 적거나 GitHub에 올리면 안 됨. `.env` 파일에 숨기고 `.gitignore`로 제외.
