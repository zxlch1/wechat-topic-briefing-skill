# WeChat Topic Briefing Skill

一个用于处理微信公众号文章的 Codex Skill 工具包。它可以从链接文本或本机微信内置浏览器历史中生成 `links.md`，批量抓取公众号文章正文，按主题筛选资料，并生成专题总结、学习材料和音频概览脚本/MP3。

> 说明：本工具不包含任何个人数据、账号信息或示例私有链接。请在自己的本地工作区中运行，并自行确认你有权处理对应文章内容。

## 功能

- 从原始文本或文件中提取 `mp.weixin.qq.com` 链接并生成 `links.md`
- 从 Windows 微信内置浏览器历史中抽取公众号文章链接
- 批量抓取微信公众号文章正文并保存为 Markdown
- 根据主题关键词生成专题文章索引和压缩语料
- 辅助 Codex 生成中文专题总结、FAQ、学习指南、思维导图和研究建议
- 使用 Edge TTS 生成中文 MP3 音频概览

## 目录结构

```text
wechat-topic-briefing-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── requirements.txt
├── agents/
│   └── openai.yaml
└── scripts/
    ├── generate_links.py
    ├── extract_wechat_history_links.py
    ├── fetch_wechat_markdown.py
    ├── build_topic_pack.py
    └── generate_edge_tts.py
```

## 安装

将整个目录复制到 Codex skills 目录，例如：

```powershell
Copy-Item -Recurse .\wechat-topic-briefing-skill "$env:USERPROFILE\.codex\skills\wechat-topic-briefing"
```

安装可选依赖：

```powershell
python -m pip install -r requirements.txt
```

`edge-tts` 只在需要生成 MP3 音频时使用；如果只做链接抽取、抓取和总结，可以不安装。

## 使用方式

在 Codex 中可以这样调用：

```text
用 $wechat-topic-briefing 读取 links.md，按“AI+催化”主题生成专题总结和录音。
```

或者：

```text
用 $wechat-topic-briefing 从本机微信可读历史中抽取公众号文章，筛选“AI4S/催化”相关文章，生成学习包。
```

## 脚本说明

### 1. 从文本生成 links.md

```powershell
python scripts/generate_links.py input_urls.txt --out links.md
```

`input_urls.txt` 可以是任意包含 URL 的文本。

### 2. 从本机微信内置浏览器历史抽取链接

```powershell
python scripts/extract_wechat_history_links.py --out links.md --audit wechat_history_links.md
```

注意：

- 该脚本读取的是 Windows 微信内置浏览器历史数据库，不保证等同于微信收藏夹。
- 脚本会先复制可读的 `History` 数据库副本，再查询副本，不会修改微信原始文件。
- 如果微信版本、数据目录或权限不同，可能无法抽取到链接。

### 3. 批量抓取文章正文

```powershell
python scripts/fetch_wechat_markdown.py links.md sources_wechat
```

输出：

- `sources_wechat/*.md`
- `sources_wechat/_failures.md`

部分微信文章可能因权限、风控、删除、转载页或格式变化而失败。

### 4. 构建主题语料

```powershell
python scripts/build_topic_pack.py `
  --source-dir sources_wechat `
  --out-dir topic_pack `
  --topic "AI + 催化" `
  --keywords "催化,AI4S,AI for Science,分子,化学合成,反应,DFT,单原子,氧空位,CARE,CATDA,Catal-GPT,ReactionSeek"
```

输出：

- `topic_pack/index.md`
- `topic_pack/corpus_compact.md`

建议人工检查 `index.md`，排除误入主题的文章。

### 5. 生成音频

先准备一个中文音频脚本文本，例如 `audio_script.txt`，再运行：

```powershell
python scripts/generate_edge_tts.py audio_script.txt audio/topic_overview.mp3
```

## 隐私与合规

- 本仓库不包含个人微信账号、微信 ID、聊天记录、收藏内容或本机路径。
- 请不要把自己生成的 `links.md`、`sources_wechat/`、`topic_pack/`、`audio/` 等私人产物提交到公开仓库。
- 公众号文章可能受版权保护。公开分享时应只分享摘要、引用少量必要内容，并保留来源链接。
- 如果用于学术总结，微信公众号文章应视为二手资料，正式引用应回溯到论文、DOI、官方文档或原始报告。

## 推荐 .gitignore

```gitignore
links.md
wechat_history_links.md
wechat_history_copies/
sources_wechat/
topic_pack/
audio/
*.sqlite
*.db
```

## 许可证

MIT License。详见 [LICENSE](LICENSE)。

