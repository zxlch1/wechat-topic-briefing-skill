#!/usr/bin/env python3
"""Fetch WeChat article URLs from links.md and save clean Markdown files."""

from __future__ import annotations

import html
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


MOBILE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 MicroMessenger/8.0.49 Safari/604.1"
)


def safe_print(text: str) -> None:
    enc = sys.stdout.encoding or "utf-8"
    print(text.encode(enc, errors="replace").decode(enc, errors="replace"), flush=True)


def extract_urls(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"https?://[^\s)\]>\"']+", text)


def fetch_url(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": MOBILE_UA})
    with urllib.request.urlopen(request, timeout=40) as response:
        return response.read().decode("utf-8", errors="replace")


def decode_js_string(value: str) -> str:
    value = re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), value)
    return html.unescape(value.replace(r"\/", "/").replace(r"\n", "\n").replace(r"\'", "'").replace(r"\\", "\\"))


def first_match(pattern: str, text: str, default: str = "") -> str:
    match = re.search(pattern, text, re.S)
    return html.unescape(match.group(1).strip()) if match else default


class MarkdownExtractor(HTMLParser):
    block_tags = {"p", "section", "div", "blockquote", "li", "h1", "h2", "h3", "h4"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v or "" for k, v in attrs}
        if tag in {"script", "style"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "br":
            self.parts.append("\n")
        elif tag in self.block_tags:
            self.parts.append("\n\n")
        elif tag == "img":
            src = attrs_dict.get("data-src") or attrs_dict.get("src")
            alt = attrs_dict.get("alt", "image")
            if src:
                self.parts.append(f"\n\n![{alt}]({html.unescape(src)})\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1
            return
        if not self.skip_depth and tag in self.block_tags:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth and data.strip():
            self.parts.append(data.replace("\xa0", " "))

    def markdown(self) -> str:
        text = "".join(self.parts)
        lines = []
        for line in text.splitlines():
            clean = re.sub(r"[ \t]+", " ", line).strip()
            if clean:
                lines.append(clean)
            elif lines and lines[-1] != "":
                lines.append("")
        return "\n".join(lines).strip()


def html_to_markdown(article_html: str) -> str:
    parser = MarkdownExtractor()
    parser.feed(article_html)
    return parser.markdown()


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\r\n]+', "", name)
    name = re.sub(r"\s+", "_", name).strip("._ ")
    return name[:90] or "article"


def extract_article(page: str, url: str) -> tuple[str, str]:
    title = first_match(r'<meta property="og:title" content="([^"]+)"', page)
    if not title:
        title = first_match(r"var msg_title = '([^']+)'", page, "untitled")
    author = first_match(r'<meta name="author" content="([^"]*)"', page, "unknown")
    created = first_match(r"create_time:\s*'([^']+)'", page, "unknown")
    content_match = re.search(r"content_noencode:\s*'([\s\S]*?)',\s*source_url", page)
    if content_match:
        body_html = decode_js_string(content_match.group(1))
    else:
        content_match = re.search(r'<div[^>]+id="js_content"[^>]*>([\s\S]*?)</div>', page)
        if not content_match:
            raise ValueError("Could not find WeChat article body")
        body_html = content_match.group(1)
    markdown = "\n".join(
        [f"# {title}", "", f"- Source: {url}", f"- Author: {author}", f"- Created: {created}", "", html_to_markdown(body_html), ""]
    )
    return title, markdown


def main() -> int:
    links_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("links.md")
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("sources_wechat")
    output_dir.mkdir(parents=True, exist_ok=True)
    urls = extract_urls(links_path)
    failures: list[tuple[str, str]] = []

    for index, url in enumerate(urls, 1):
        safe_print(f"[{index}/{len(urls)}] fetching {url}")
        try:
            title, markdown = extract_article(fetch_url(url), url)
            out_path = output_dir / f"{index:03d}_{sanitize_filename(title)}.md"
            out_path.write_text(markdown, encoding="utf-8")
            safe_print(f"  -> {out_path}")
        except Exception as exc:
            failures.append((url, str(exc)))
            safe_print(f"  !! failed: {exc}")

    if failures:
        lines = ["# Fetch failures", ""]
        for url, error in failures:
            lines.extend([f"- {url}", f"  - {error}"])
        (output_dir / "_failures.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

