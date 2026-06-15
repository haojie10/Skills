---
name: sp-openclaw-web-cli
description: 将任何网站变成命令行 API。适用于需要快速从主流平台（推特、知乎、GitHub、YouTube 等）获取结构化数据，而无需编写复杂爬虫的场景。
---

# OpenClaw: 网页命令行化

## 概述

OpenClaw 是一套强大的 Site 系统适配器，将复杂的网页操作简化为结构化的 CLI 命令。它复用用户的登录态，通过简单的指令即可获取深度信息。

## 常用平台与命令示例

| 类别 | 平台 | 示例操作 |
|---|---|---|
| **搜索** | Google, 百度, 微信搜索 | `bb-browser site search "关键词"` |
| **社交** | Twitter, Reddit, 微博 | `bb-browser site twitter/search "AI"` |
| **技术** | GitHub, StackOverflow, arXiv | `bb-browser site github/repo "owner/repo"` |
| **视频** | YouTube, Bilibili | `bb-browser site youtube/transcript [ID]` |
| **金融** | 雪球, 东方财富 | `bb-browser site xueqiu/stock [代码]` |

## 核心法则

1. **更新仓库**：使用前运行 `bb-browser site update` 以获取最新的社区适配器。
2. **利用 JQ 过滤**：配合 `--jq` 选项直接在命令行对返回的 JSON 数据进行清洗（例如：`--jq '.items[].title'`)。
3. **处理登录态**：如果命令返回 401 错误，说明需要登录。请先打开该站点并手动完成登录，OpenClaw 会自动复用 Cookie。

## 场景应用

- **竞品分析**：一键抓取推特热门讨论或 GitHub 仓库动态。
- **研报收集**：快速获取研报摘要、股票行情或学术论文列表。
- **视频分析**：直接获取 YouTube/B站的字幕，无需下载视频。

## 扩展建议
如果你发现某个网站还没有对应的命令，可以要求我为你“反向工程”该网站的 API，并编写一个新的适配器。

---
> 注意：本技能依赖于 OpenClaw 生态，推荐配合 `bb-browser` 工具使用以获得最佳体验。
