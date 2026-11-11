# [업데이트 단계 2] P0-2 · n8n Webhook의 수업 ID를 동적으로 전달

> 목표: Webhook으로 들어온 `body.lesson_record_id`를 **그대로 우리 API로 전달**한다.
> (기존엔 `{ "lesson_record_id": 1 }`로 **고정**되어 어떤 요청이든 1번만 생성)
> 완료기준: `Webhook 요청 ID == 생성 결과 lesson_record_id`가 서로 다른 2건에서 성립.

---

## 1. 바뀐 워크플로 구조

```
Webhook (POST /webhook/kids)
   │  들어온 JSON은 n8n에서 $json.body 에 담김
   ▼
Validate lesson_record_id (Code 노드)   ← 신규 추가
   │  · 없거나 빈값/정수 아니면 throw → 뒤로 안 감 (잘못된 타입 거절)
   │  · 정수면 { lesson_record_id: <정수> } 로 정리해서 넘김
   ▼
Call Kids_Feedback API (HTTP Request)
   │  jsonBody = { "lesson_record_id": {{ $json.lesson_record_id }} }   ← 동적
   ▼
우리 FastAPI  POST http://api:8000/feedbacks/generate
```

핵심 변경 3가지:
1. HTTP Request의 `jsonBody`를 **고정값 → 표현식**으로 바꿈: `={ "lesson_record_id": {{ $json.lesson_record_id }} }`
2. 그 앞에 **검증 Code 노드** 추가 (누락/타입 오류 거절).
3. 연결선: `Webhook → Validate → HTTP Request`.

---

## 2. 알아야 하는 n8n 개념

- **`$json`** : 현재 노드로 들어온 데이터 아이템. Webhook 노드의 출력에서 요청 본문은 **`$json.body`** 안에 있다.
- **표현식(Expression)** : 필드값을 `=`로 시작하면 n8n이 "이건 고정 문자열이 아니라 계산식"으로 본다. 그 안에서 `{{ ... }}`가 실제 값으로 치환된다.
  - `"{ \"lesson_record_id\": 1 }"` → 항상 1 (고정)
  - `"={ \"lesson_record_id\": {{ $json.lesson_record_id }} }"` → 들어온 값 (동적)
- **Code 노드** (`n8n-nodes-base.code`, typeVersion 2) : 자바스크립트로 아이템을 가공/검증. `return [{ json: {...} }]` 형태로 다음 노드에 넘긴다. `throw new Error(...)`로 흐름을 중단시킬 수 있다.

### Code 노드 핵심 로직
```js
const body = ($input.first().json.body) || {};
let id = body.lesson_record_id;
if (id === undefined || id === null || id === '') throw new Error('lesson_record_id is required');
id = Number(id);
if (!Number.isInteger(id) || id <= 0) throw new Error('lesson_record_id must be a positive integer');
return [{ json: { lesson_record_id: id } }];
```

---

## 3. 왜 '서비스 이름'으로 부르나 (api:8000)

docker-compose 안의 n8n·api·db는 같은 네트워크에 있다.
그래서 n8n에서 우리 API를 부를 때 `localhost`가 아니라 **서비스 이름 `api`** 로 부른다 → `http://api:8000/...`
(호스트 PC에서 직접 부를 땐 `http://localhost:8001/...`, compose가 8001→8000 매핑)

---

## 4. 검증 방법 (완료기준 재현) — 명령어

도커를 띄운 뒤, n8n에 이 워크플로를 import하고 **Webhook URL**을 확인한다.
(n8n UI: Workflows → Import from File → `n8n_workflow_webhook.json` → Production URL 복사)

```bash
docker compose up -d --build

# 서로 다른 수업 ID 2건 호출 (경로의 /webhook/kids 는 n8n이 알려주는 Production URL 기준)
curl -X POST http://localhost:5679/webhook/kids -H "Content-Type: application/json" -d "{\"lesson_record_id\": 2}"
curl -X POST http://localhost:5679/webhook/kids -H "Content-Type: application/json" -d "{\"lesson_record_id\": 5}"

# 잘못된 타입/누락 → Code 노드에서 거절되는지
curl -X POST http://localhost:5679/webhook/kids -H "Content-Type: application/json" -d "{\"lesson_record_id\": \"abc\"}"
curl -X POST http://localhost:5679/webhook/kids -H "Content-Type: application/json" -d "{}"
```

- **확인 포인트:** 각 응답 JSON의 `lesson_record_id`가 **요청에 넣은 값과 같아야** 한다 (2→2, 5→5).
- 우리 API `/feedbacks/generate`는 응답에 `lesson_record_id`를 포함하므로 바로 대조 가능.
- 포트폴리오 증거: n8n 실행 화면 캡처 + 2건의 요청/응답 비교.

> ⚠️ 주의: 이 워크플로를 실제로 돌리려면 Gemini API 호출이 일어나므로 `.env`에 유효한 `GEMINI_API_KEY`가 필요하고, 해당 `lesson_record_id`의 수업기록이 DB에 있어야 한다(없으면 우리 API가 404).

---

## 5. 구현 흐름 (내가 한 순서)
1. `n8n_workflow_webhook.json`에 Code 검증 노드 추가.
2. HTTP Request `jsonBody`를 표현식으로 교체.
3. 연결선 재배선(Webhook→Validate→HTTP).
4. JSON 파싱 유효성 확인(`python -c json.load`).
5. (도커 환경에서) 2건 호출로 ID 일치 확인 — 실행은 사용자 환경에서.

## 6. 한 줄 요약
> 고정 `1` 대신 `{{ $json.lesson_record_id }}` 표현식으로 동적 전달하고,
> 그 앞 Code 노드가 누락/타입오류를 미리 거절한다.
