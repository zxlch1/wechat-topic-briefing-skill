#!/usr/bin/env python3
"""Build a focused topic corpus from crawled Markdown files."""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_KEYWORDS = ["AI", "LLM", "Agent", "RAG", "知识图谱", "催化", "分子", "化学", "材料", "反应"]


def title_of(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def compact(text: str, max_chars: int) -> str:
    lines = []
    for line in text.splitlines():
        clean = line.strip()
        if clean and not clean.startswith("!["):
            lines.append(clean)
    return "\n".join(lines)[:max_chars]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", default="sources_wechat")
    parser.add_argument("--out-dir", default="topic_pack")
    parser.add_argument("--topic", default="topic")
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS))
    parser.add_argument("--min-score", type=int, default=8)
    parser.add_argument("--max-chars-per-file", type=int, default=3500)
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    selected = []
    for path in sorted(Path(args.source_dir).glob("*.md")):
        if path.name == "_failures.md":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        s = sum(lower.count(k.lower()) for k in keywords)
        title = title_of(text, path.name)
        title_hit = any(k.lower() in title.lower() for k in keywords)
        if s >= args.min_score or title_hit:
            selected.append((s, path, title, text))
    selected.sort(key=lambda x: (-x[0], x[1].name))

    index = [f"# {args.topic} topic index", ""]
    corpus = [f"# {args.topic} compact corpus", ""]
    for i, (s, path, title, text) in enumerate(selected, 1):
        index.append(f"{i}. `{path.name}` | score={s} | {title}")
        corpus.extend([f"## {i}. {title}", "", f"- File: `{path}`", f"- Score: {s}", "", compact(text, args.max_chars_per_file), ""])
    (out_dir / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    (out_dir / "corpus_compact.md").write_text("\n".join(corpus) + "\n", encoding="utf-8")
    print(f"Selected {len(selected)} file(s) into {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

