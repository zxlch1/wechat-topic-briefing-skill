#!/usr/bin/env python3
"""Generate links.md from raw text files or direct URL arguments."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


URL_RE = re.compile(r"https?://[^\s)\]>\"']+")


def collect_urls(items: list[str]) -> list[str]:
    urls: list[str] = []
    seen: set[str] = set()
    for item in items:
        path = Path(item)
        text = path.read_text(encoding="utf-8") if path.exists() else item
        for match in URL_RE.findall(text):
            url = match.rstrip(".,;，。；")
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="Files or raw strings containing URLs")
    parser.add_argument("--out", default="links.md")
    args = parser.parse_args()

    urls = collect_urls(args.inputs)
    if not urls:
        print("No URLs found.")
        return 1

    Path(args.out).write_text("# Links\n\n" + "\n".join(urls) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} with {len(urls)} URL(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

