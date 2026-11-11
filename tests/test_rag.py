# tests/test_rag.py
# P0-4(인덱싱 청킹) + P0-5(Top-3 검색) 로직을 API 키 없이 검증한다.

import pytest

from rag.build_index import load_chunks
import rag.rag_service as rs


# ───────────────── P0-4: 청킹/인덱싱 로직 ─────────────────
def test_load_chunks_covers_all_docs():
    chunks, report = load_chunks()
    # 문서가 여러 개이고, 청크가 충분히 쪼개졌는가
    assert report["doc_count"] >= 10
    assert report["chunk_count"] >= 90
    # 빈 청크/중복/메타누락이 없어야 '완성된 인덱스'
    assert report["empty_chunks"] == []
    assert report["duplicate_chunks"] == []
    assert report["missing_meta_files"] == []
    # 4개 범주가 모두 존재
    assert set(report["per_category"]) >= {"성향별", "상황별", "성장목표", "학부모소통"}


def test_chunk_ids_unique_and_text_nonempty():
    chunks, _ = load_chunks()
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))                 # chunk_id 유일
    assert all(c["text"].strip() for c in chunks)    # 텍스트 비어있지 않음
    # 청크에서 원본 파일 경로를 복원할 수 있어야 함
    assert all(c["source_file"].startswith("rag_docs/") for c in chunks)


# ───────────────── P0-5: Top-3 검색 ─────────────────
FAKE_DATA = [
    {"chunk_id": "a", "source_file": "rag_docs/f1.md", "title": "A", "category": "성향별", "vector": [1.0, 0.0], "text": "A본문"},
    {"chunk_id": "b", "source_file": "rag_docs/f1.md", "title": "B", "category": "성향별", "vector": [0.9, 0.1], "text": "B본문"},
    {"chunk_id": "c", "source_file": "rag_docs/f1.md", "title": "C", "category": "성향별", "vector": [0.8, 0.2], "text": "C본문"},
    {"chunk_id": "d", "source_file": "rag_docs/f2.md", "title": "D", "category": "상황별", "vector": [0.0, 1.0], "text": "D본문"},
]


@pytest.fixture()
def fake_index(monkeypatch):
    monkeypatch.setattr(rs, "data", FAKE_DATA)
    return monkeypatch


def test_top3_returns_three_sorted_hits(fake_index):
    fake_index.setattr(rs, "embed_feedback", lambda q: [1.0, 0.0])  # 쿼리 벡터 = a와 동일
    res = rs.rag_search("아무 질문", k=3)

    assert len(res["hits"]) == 3
    scores = [h["score"] for h in res["hits"]]
    assert scores == sorted(scores, reverse=True)   # 점수 내림차순
    assert res["best_score"] == 1.0
    assert res["low_relevance"] is False
    # 출처/점수/근거가 포함되는가
    assert all({"chunk_id", "source_file", "score", "text"} <= set(h) for h in res["hits"])


def test_diversity_limits_same_source(fake_index):
    """같은 문서(f1)에서 최대 2개까지만 → 3번째 자리는 다른 문서(f2) 청크가 온다."""
    fake_index.setattr(rs, "embed_feedback", lambda q: [1.0, 0.0])
    res = rs.rag_search("아무 질문", k=3)
    srcs = [h["source_file"] for h in res["hits"]]
    assert srcs.count("rag_docs/f1.md") <= rs.MAX_PER_SOURCE
    assert "rag_docs/f2.md" in srcs


def test_low_relevance_flag_when_scores_low(fake_index):
    """쿼리가 어떤 청크와도 안 비슷하면 low_relevance=True (근거 부족)."""
    fake_index.setattr(rs, "embed_feedback", lambda q: [1.0, 0.0])
    # 데이터 전부를 쿼리와 직교에 가깝게 바꾼다 → 유사도 낮음
    fake_index.setattr(rs, "data", [
        {"chunk_id": "x", "source_file": "rag_docs/f9.md", "title": "X", "category": "상황별", "vector": [0.0, 1.0], "text": "X"},
        {"chunk_id": "y", "source_file": "rag_docs/f9.md", "title": "Y", "category": "상황별", "vector": [0.05, 1.0], "text": "Y"},
    ])
    res = rs.rag_search("아무 질문", k=3)
    assert res["best_score"] < rs.RELEVANCE_MIN
    assert res["low_relevance"] is True
