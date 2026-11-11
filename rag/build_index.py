# rag/build_index.py
# rag_docs/**/*.md 전체를 읽어 '질문(## ) 단위'로 쪼개고, 각 청크를 임베딩해
# rag/vectors.json 을 '전체 재생성'한다. (같은 입력을 다시 돌려도 중복이 쌓이지 않음)
#
# 실행:
#   docker compose exec api python -m rag.build_index            # 실제 임베딩 + vectors.json 갱신
#   python -m rag.build_index --report-only                      # 임베딩 없이 청킹만 점검(키 불필요)
#
# 안전장치:
#   - 빈 청크 / 중복 청크 / 임베딩 오류를 검출한다.
#   - 임베딩 중 하나라도 실패하면 '완성되지 않은 인덱스'를 서비스에 올리지 않는다(기존 vectors.json 유지).
#   - 임시 파일에 먼저 쓰고 검증 후 원자적 교체(os.replace).

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "rag_docs"
OUT_PATH = BASE_DIR / "rag" / "vectors.json"
REPORT_PATH = BASE_DIR / "docs" / "rag_index_build_report.md"
EMBEDDING_MODEL = "gemini-embedding-001"

# 소제목(청크 경계): ## 또는 ### 로 시작하는 줄. 특정 문자열 하나에만 의존하지 않도록 정규식 사용.
HEADING_RE = re.compile(r"^#{2,3}\s+(.*\S)\s*$")
# 메타 라인 예: > meta: category=성향별; source=자체작성가이드(전문가검증전); version=2026-11-12
META_KV_RE = re.compile(r"(category|source|version)\s*=\s*([^;\n]+)")


def _parse_meta(lines):
    """파일 상단에서 category/source/version 메타를 뽑는다(없으면 기본값)."""
    meta = {"category": "미분류", "source": "unknown", "version": "unknown"}
    for line in lines[:12]:
        if "meta:" in line or "category=" in line:
            for key, val in META_KV_RE.findall(line):
                meta[key] = val.strip()
            break
    return meta


def load_chunks(docs_dir: Path = DOCS_DIR):
    """문서 전체를 순회·청킹한다. (임베딩은 하지 않음 → API 키 불필요)
    반환: (chunks, report)
      chunk = {chunk_id, source_file, title, category, source, version, text}
    """
    files = sorted(docs_dir.glob("**/*.md"))
    chunks = []
    seen_text = {}            # 중복 탐지용 (정규화 텍스트 → chunk_id)
    empty, duplicate, missing_meta = [], [], []
    per_file = {}

    for f in files:
        rel = f.relative_to(BASE_DIR).as_posix()
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        meta = _parse_meta(lines)
        if meta["category"] == "미분류":
            missing_meta.append(rel)

        # 소제목 기준으로 섹션 나누기: heading 줄을 만나면 새 청크 시작
        sections = []            # [(title, [body lines])]
        cur_title, cur_body = None, []
        for line in lines:
            m = HEADING_RE.match(line)
            if m:
                if cur_title is not None:
                    sections.append((cur_title, cur_body))
                cur_title, cur_body = m.group(1).strip(), []
            elif cur_title is not None:
                cur_body.append(line)
        if cur_title is not None:
            sections.append((cur_title, cur_body))

        n_file = 0
        for i, (title, body_lines) in enumerate(sections):
            body = "\n".join(body_lines).strip()
            if not body:                      # 빈 청크(제목만 있고 답이 없음) → 제외
                empty.append(f"{rel}::{i:02d} ({title[:20]})")
                continue
            chunk_text = f"{title}\n{body}".strip()
            norm = re.sub(r"\s+", " ", chunk_text)
            chunk_id = f"{rel}::{i:02d}"
            if norm in seen_text:             # 중복 청크 → 제외
                duplicate.append(f"{chunk_id} == {seen_text[norm]}")
                continue
            seen_text[norm] = chunk_id
            chunks.append({
                "chunk_id": chunk_id,
                "source_file": rel,
                "title": title,
                "category": meta["category"],
                "source": meta["source"],
                "version": meta["version"],
                "text": chunk_text,
            })
            n_file += 1
        per_file[rel] = n_file

    # 카테고리별 집계
    per_cat = {}
    for c in chunks:
        per_cat[c["category"]] = per_cat.get(c["category"], 0) + 1

    report = {
        "doc_count": len(files),
        "chunk_count": len(chunks),
        "per_category": per_cat,
        "per_file": per_file,
        "empty_chunks": empty,
        "duplicate_chunks": duplicate,
        "missing_meta_files": missing_meta,
    }
    return chunks, report


def _write_report(report, embedded: bool):
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# RAG 인덱스 빌드 리포트",
        "",
        f"- 생성 시각: {datetime.now(timezone.utc).isoformat()}",
        f"- 임베딩 수행: {'예 (vectors.json 갱신됨)' if embedded else '아니오 (--report-only)'}",
        f"- 임베딩 모델: {EMBEDDING_MODEL}",
        f"- 문서 수: **{report['doc_count']}**",
        f"- 청크 수: **{report['chunk_count']}**",
        "",
        "## 카테고리별 청크 수",
        "",
        "| 분류 | 청크 수 |",
        "|---|---:|",
    ]
    for cat, n in sorted(report["per_category"].items()):
        lines.append(f"| {cat} | {n} |")
    lines += ["", "## 파일별 청크 수", "", "| 파일 | 청크 수 |", "|---|---:|"]
    for rel, n in sorted(report["per_file"].items()):
        lines.append(f"| `{rel}` | {n} |")
    lines += ["", f"## 점검 결과",
              f"- 빈 청크: {len(report['empty_chunks'])}건 {report['empty_chunks'] or ''}",
              f"- 중복 청크: {len(report['duplicate_chunks'])}건 {report['duplicate_chunks'] or ''}",
              f"- 메타 누락 파일: {len(report['missing_meta_files'])}건 {report['missing_meta_files'] or ''}"]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(report_only: bool = False):
    chunks, report = load_chunks()
    print(f"문서 {report['doc_count']}개 → 청크 {report['chunk_count']}개")
    print("카테고리별:", report["per_category"])
    if report["empty_chunks"]:
        print("⚠️ 빈 청크:", report["empty_chunks"])
    if report["duplicate_chunks"]:
        print("⚠️ 중복 청크:", report["duplicate_chunks"])

    if report_only:
        _write_report(report, embedded=False)
        print(f"리포트만 작성: {REPORT_PATH}")
        return report

    # ── 실제 임베딩 (API 키 필요) ──
    from rag.rag_service import embed_feedback  # 여기서만 import → report-only는 키 불필요
    data = []
    for i, c in enumerate(chunks, 1):
        try:
            vec = embed_feedback(c["text"])
        except Exception as e:
            # 하나라도 실패하면 미완성 인덱스를 올리지 않는다 → 기존 vectors.json 유지
            raise SystemExit(f"[중단] 임베딩 실패 ({c['chunk_id']}): {type(e).__name__} {e}. "
                             f"기존 vectors.json은 그대로 둔다.")
        row = dict(c)
        row["embedding_model"] = EMBEDDING_MODEL
        row["vector"] = vec
        row["updated_at"] = datetime.now(timezone.utc).isoformat()
        data.append(row)
        if i % 10 == 0 or i == len(chunks):
            print(f"  임베딩 {i}/{len(chunks)}")

    # 검증 후 원자적 교체
    assert len(data) == report["chunk_count"], "청크 수 불일치"
    assert all(r.get("vector") for r in data), "빈 벡터 발견"
    tmp = OUT_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, OUT_PATH)
    _write_report(report, embedded=True)
    print(f"저장 완료: {OUT_PATH} ({len(data)}개 벡터), 리포트: {REPORT_PATH}")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-only", action="store_true",
                    help="임베딩 없이 청킹/집계만 점검(API 키 불필요, vectors.json 안 바꿈)")
    args = ap.parse_args()
    main(report_only=args.report_only)
