#!/usr/bin/env python3
"""Extract mp.weixin.qq.com article links from local WeChat embedded-browser History DBs."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


def canonical(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def candidate_history_paths() -> list[Path]:
    appdata = Path(os.environ.get("APPDATA", ""))
    roots = [
        appdata / "Tencent" / "xwechat" / "radium" / "web" / "profiles",
        appdata / "Tencent" / "WeChat" / "radium" / "web" / "profiles",
    ]
    paths: list[Path] = []
    for root in roots:
        if root.exists():
            paths.extend(root.glob("*/History"))
            paths.extend(root.glob("*/History.wxbak"))
    return [p for p in paths if p.is_file()]


def read_rows(db_path: Path, copy_dir: Path) -> list[tuple[str, str]]:
    copy_dir.mkdir(parents=True, exist_ok=True)
    copied = copy_dir / f"{db_path.parent.name}_{db_path.name}.sqlite"
    try:
        shutil.copy2(db_path, copied)
    except Exception:
        return []
    try:
        con = sqlite3.connect(copied)
        return con.execute(
            "select url, title from urls where url like '%mp.weixin.qq.com/s/%'"
        ).fetchall()
    except Exception:
        return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="links.md")
    parser.add_argument("--audit", default="wechat_history_links.md")
    parser.add_argument("--copies-dir", default="wechat_history_copies")
    args = parser.parse_args()

    seen: set[str] = set()
    items: list[tuple[str, str]] = []
    for db in candidate_history_paths():
        for url, title in read_rows(db, Path(args.copies_dir)):
            clean = canonical(url)
            if not re.match(r"^https://mp\.weixin\.qq\.com/s/[^/?#]+$", clean):
                continue
            if clean in seen:
                continue
            seen.add(clean)
            items.append((clean, title or ""))

    if not items:
        print("No WeChat article links found in readable local browser history.")
        return 1

    Path(args.out).write_text(
        "# Links\n\n" + "\n".join(url for url, _ in items) + "\n",
        encoding="utf-8",
    )
    audit_lines = [
        "# WeChat embedded-browser article links",
        "",
        "> Extracted from local WeChat browser history. This is not guaranteed to equal Favorites.",
        "",
    ]
    for url, title in items:
        audit_lines.append(f"- {url}" + (f"  # {title}" if title else ""))
    Path(args.audit).write_text("\n".join(audit_lines) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} and {args.audit} with {len(items)} URL(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

