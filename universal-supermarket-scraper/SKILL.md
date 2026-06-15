---
name: universal-supermarket-scraper
description: |
  从商超/电商网站爬取商品信息并导出到 Excel 文件。
  触发条件：
  - 用户提到「爬取/抓取/搜索商品」「商超/超市/电商网站」
  - 用户要求从某个网站搜索关键词并导出产品信息
  - 用户需要「导出到 Excel」的商品数据
---

# Universal Supermarket Scraper

## 概述

这个技能可以从任意商超或电商网站，根据用户指定的关键词搜索并爬取商品信息（名称、型号、图片、描述、价格、链接），然后导出到 Excel 文件。

支持 **Browser Subagent (AI驱动)** 和 **Playwright (自动化脚本)** 双引擎。

## 工作流程

### 第一步：确认参数

与用户确认以下信息：
- **目标网站 URL**（例如 `https://home.bargains/`）
- **搜索关键词**（例如 `marker pen`）
- **输出文件名和路径**（默认保存到桌面）

### 第二步：提取策略 (三选一)

#### 方案 A：快速模式 (推荐)
直接在**搜索结果列表页**提取所有可见信息。
- **优点**：速度快（仅需 1 次页面加载），消耗资源少。
- **缺点**：描述可能不完整。
- **关键点**：确保提取的是 `<img>` 的 `src` 属性作为 `image_url`，而非包裹它的 `<a>` 的 `href`。

#### 方案 B：深度模式
先从列表页获取所有商品链接，然后**逐个访问详情页**。
- **优点**：信息极其完整（含长描述、多图、完整规格）。
- **缺点**：速度较慢，适合小批量（<10个）精准采集。

#### 方案 C：自动化脚本模式 (Expert Mode)
使用预置的 Playwright 脚本进行全自动批量抓取。
- **工具**：`scripts/playwright_scraper.py`
- **优点**：无需人工干预，速度快，支持滚动加载和去重。
- **命令示例**：
  ```bash
  python scripts/playwright_scraper.py --url "https://home.bargains/" --keyword "notebook" --count 10
  ```
- **配置**：脚本支持设置 `headless=False` 以便在本地观察抓取过程。

## 第四步：导出 Excel

使用 `scripts/export_to_excel.py` 脚本将数据（JSON 格式）导出为 Excel 文件。

## 使用注意

1. **反爬机制**：Playwright 脚本在某些高强度防爬网站上可能需要配置 Stealth 插件或代理。
2. **图片路径**：确保提取的是真实媒体资源地址。
3. **环境要求**：Expert Mode 需要本地安装 `playwright` (已预装)。
