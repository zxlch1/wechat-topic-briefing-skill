---
name: wechat-topic-briefing
description: Use when the user wants to process WeChat public-account articles or mp.weixin.qq.com links, including generating links.md, extracting readable WeChat embedded-browser history, batch crawling article Markdown, filtering by a topic such as AI+catalysis, creating NotebookLM-style summaries/FAQ/study guides/mind maps, and generating an audio overview recording.
---

# WeChat Topic Briefing

## Purpose

Turn WeChat public-account article links into a local, topic-focused learning package:

```text
raw URLs / local WeChat browser history -> links.md
-> Markdown article corpus
-> topic index + compressed corpus
-> summary / FAQ / study guide / mind map / recommendations
-> audio overview script + MP3
```

## Core Rules

- Treat local WeChat data as private. Do not dump chat text or unrelated records into the conversation.
- WeChat desktop may not expose a readable Favorites database. If favorites cannot be found, state that clearly and use local WeChat embedded-browser history only as a fallback candidate source.
- Keep topic corpora narrow. Do not mix news/campus/social articles into a research topic summary unless the user asks for broad monitoring.
- For scientific topics, label WeChat articles as secondary sources and recommend tracing claims back to DOI, paper, SI, or official source.
- For catalysis or AI4Science, separate hard facts, author claims, inferred trends, and your recommendations.

## Workflow

### 1. Resolve Inputs

Use one of these paths:

- User provides URLs or raw text containing URLs: run `scripts/generate_links.py`.
- User asks to use current WeChat login/favorites/history: run `scripts/extract_wechat_history_links.py`. This scans common Windows `xwechat` browser-history locations, copies readable `History` databases into the workspace, and extracts `mp.weixin.qq.com/s/...` links.
- User has a prepared `links.md`: skip link generation.

Example:

```powershell
python <skill_dir>\scripts\generate_links.py input_urls.txt --out links.md
python <skill_dir>\scripts\extract_wechat_history_links.py --out links.md --audit wechat_history_links.md
```

### 2. Crawl Articles to Markdown

Run:

```powershell
python <skill_dir>\scripts\fetch_wechat_markdown.py links.md sources_wechat
```

This uses a mobile WeChat user agent, extracts WeChat article body HTML, and writes one Markdown file per article. Failed links are recorded in `_failures.md`.

Network access is usually required. If sandboxed network fails, rerun with user approval according to normal escalation rules.

### 3. Build a Topic Corpus

Run:

```powershell
python <skill_dir>\scripts\build_topic_pack.py --source-dir sources_wechat --out-dir topic_pack --topic "AI + 催化" --keywords "催化,AI4S,AI for Science,分子,化学合成,反应,DFT,单原子,氧空位,CARE,CATDA,Catal-GPT,ReactionSeek"
```

Review `topic_pack/index.md`. Manually exclude false positives before writing the final summary.

### 4. Write the Summary Yourself

Use `topic_pack/corpus_compact.md` and selected source files to write a high-signal summary. For research/science topics, prefer this structure:

1. 总体判断
2. 代表路线 / 技术分支
3. 对照表
4. 关键启发
5. 适合用户继续做的方向
6. 风险与证据缺口
7. 使用的本地资料清单

For catalysis, emphasize evidence anchoring, reaction conditions, synthesis-structure-performance relations, and experimental validation.

### 5. Generate Audio

Create a concise audio script from the summary, then run:

```powershell
python <skill_dir>\scripts\generate_edge_tts.py audio_script.txt audio/topic_overview.mp3
```

If `edge_tts` is missing, install `edge-tts` only after approval. If Edge TTS network is blocked, report that audio generation is blocked and keep the script ready.

## Expected Outputs

- `links.md`
- `sources_wechat/*.md`
- `topic_pack/index.md`
- `topic_pack/corpus_compact.md`
- `topic_pack/<topic>_summary.md`
- `topic_pack/<topic>_audio_script.txt`
- `audio/<topic>_overview.mp3`

