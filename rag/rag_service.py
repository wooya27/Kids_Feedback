import json
import os
import math
from pathlib import Path

from dotenv import load_dotenv
from google import genai

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "rag" / "vectors.json", "r", encoding="utf-8") as f:
    data = json.load(f)

load_dotenv(BASE_DIR / ".env")
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# ── 검색 설정 ──
TOP_K = 3              # Top-3 검색 (기본 k=3)
RELEVANCE_MIN = 0.70  # 이 유사도 미만이면 '근거 부족'으로 본다 (정답률 아님, 유사도 바닥선)
MAX_PER_SOURCE = 2    # 다양성: 같은 문서에서 최대 2청크까지만 (한 문서 쏠림 방지)


def embed_feedback(prompt):
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=prompt
      )
    return response.embeddings[0].values


def cos_sim(a, b):
      dot = sum(x * y for x, y in zip(a, b))
      size_a = math.sqrt(sum(x * x for x in a))
      size_b = math.sqrt(sum(x * x for x in b))
      return dot / (size_a * size_b)


def rag_search(question, k=TOP_K):
    """코사인 유사도 상위 k개 청크를 '출처·점수와 함께' 돌려준다.

    반환:
      {
        "hits": [ {chunk_id, source_file, title, category, score, text}, ... ],  # 점수 내림차순
        "best_score": float,       # 최고 유사도
        "low_relevance": bool,     # best_score < RELEVANCE_MIN → 근거 부족
        "query": question,
      }
    - 다양성: 같은 source_file에서 MAX_PER_SOURCE개를 넘으면 건너뛰어 한 문서 쏠림을 막는다.
      (그래도 k개가 안 차면 남은 상위 청크로 채운다)
    - 근거 부족(low_relevance)이면 프롬프트가 '지침을 지어내지 말라'고 안내하도록 신호를 준다.
    """
    q_vector = embed_feedback(question)

    scored = []
    for d in data:
        scored.append((cos_sim(q_vector, d["vector"]), d))
    scored.sort(key=lambda x: x[0], reverse=True)

    hits = []
    per_src = {}
    leftover = []
    for score, d in scored:
        src = d.get("source_file")
        # 다양성 제약: 같은 문서에서 너무 많이 뽑히면 일단 보류(leftover)
        if src is not None and per_src.get(src, 0) >= MAX_PER_SOURCE:
            leftover.append((score, d))
            continue
        hits.append(_to_hit(score, d))
        if src is not None:
            per_src[src] = per_src.get(src, 0) + 1
        if len(hits) >= k:
            break

    # 다양성 때문에 k개가 안 찼으면 보류분에서 채운다
    for score, d in leftover:
        if len(hits) >= k:
            break
        hits.append(_to_hit(score, d))

    best = hits[0]["score"] if hits else 0.0
    return {
        "hits": hits,
        "best_score": round(best, 4),
        "low_relevance": best < RELEVANCE_MIN,
        "query": question,
    }


def _to_hit(score, d):
    return {
        "chunk_id": d.get("chunk_id"),
        "source_file": d.get("source_file"),
        "title": d.get("title"),
        "category": d.get("category"),
        "score": round(float(score), 4),
        "text": d.get("text", ""),
    }
