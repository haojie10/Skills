---
name: raw-to-gtb-news
description: 将外部收集的 raw 资讯素材（英文原文 / Obsidian clippings）按 GTB report-news 规范转换为平台新闻并发布。用于把零散收集的海外行业新闻、零售/供应链动态等 raw 文件，提炼为四段式中文深度资讯（recap 400-500字 + highlights + takeaways 150-200字 + 54标准品类标签），抓取 og:image 配图，组装 HTML 并 POST 发布到 GlobalTradeBuddy 平台 news 板块。触发场景：用户把新闻/资讯文件放入 raw 文件夹，要求"转换成平台新闻""沉淀为资讯""发布到 GTB 平台"等。
---

# Raw 资讯 → GTB 平台新闻 (raw-to-gtb-news)

将 `/raw` 文件夹（或其他位置）中的原始英文资讯素材，转换为 GlobalTradeBuddy (GTB) 平台 `news` 板块的深度中文资讯并发布。产出对齐 `report-news` 技能的"四段式深度结构化输出标准"。

## 输入

原始资讯文件，典型为 Obsidian clippings 格式的 Markdown，YAML frontmatter 含 `title`、`source`（原网页 URL）、`description` 等，正文为英文原文。

## 核心质量红线（强制执行）

1. **真实来源**：`source_url` 必须为素材 frontmatter 中 `source` 字段的真实海外新闻链接，严禁臆造。
2. **深度解析**：`recap` 必须 400~500 字中文，交代事件完整脉络、具体金额/门店数/数据指标、高管表态、行业协会立场。
3. **实操启示**：`takeaways` 必须 150~200 字中文，落到中国出口工厂选品、BOM 成本、关税规避、买家谈判。
4. **标准品类**：`industries` / `tags.products` 必须严格使用 54 个标准行业名称（见 references 或项目 `report-news/references/standard-categories.json`），禁止自创非标词，允许无上限多标签。
5. **真实配图**：优先抓取新闻源页面的 `og:image`（用 `scripts/fetch-og-image.js`）；抓取失败则回退使用素材正文中的真实图片链接。
6. **时效注记**：超过 7 天的旧闻不跳过，但需在 `recap` 中注明报道日期。
7. **图谱隔离**：资讯仅进入 `news` 板块前台展示与 SEO 引流，不写入个人知识图谱。

## 四段式 JSON 结构（每篇一条）

```json
{
  "title": "中文精炼专业标题（突出核心企业/事件）",
  "recap": "400~500字中文深度事实解析",
  "highlights": ["3~5 条关键数据/事实/时间节点"],
  "takeaways": "150~200字中国外贸工厂供应链实操启示",
  "industries": ["54标准品类名1", "品类2"],
  "countries": ["国家1", "国家2"],
  "region": "欧洲",
  "country": "主国家",
  "industry": "主品类（取 industries 首个）",
  "source_url": "真实海外新闻链接",
  "imageUrl": "og:image 高清大图",
  "source_name": "媒体名称",
  "published_date": "YYYY-MM-DD",
  "tags": { "companies": [], "products": [同 industries], "regions": [] }
}
```

## 执行工作流

### 第 1 步：读取并解析 raw 素材
- 读取 `/raw` 中目标 Markdown 文件。
- 从 frontmatter 提取 `title`、`source`（URL）、`published`/`created`（日期）、`description`。
- 通读正文，提取核心事实、数据、人物表态。

### 第 2 步：抓取 og:image 配图
```bash
node .codebuddy/skills/raw-to-gtb-news/scripts/fetch-og-image.js "<source_url>"
```
- 若返回 `NOT_FOUND` 或请求被限流（429），回退使用素材正文中出现的真实图片 URL（如 WordPress `wp-content/uploads` 链接）。

### 第 3 步：生成四段式 JSON
- 按上述 JSON 结构，为每篇素材生成一条深度资讯。
- `recap` / `takeaways` 必须满足字数红线。
- `industries` 智能关联：零售巨头的战略级新闻可关联多个相关品类。
- 存放目录：`/Users/jason/Documents/Antigravity/Project/Globaltradebuddy/news-pipeline/<YYYY-MM-DD>/`
- **这些 JSON 是临时中间产物**：发布成功后将被脚本自动删除，执行完毕不残留冗余文件。若需要留档核对，可另行复制保存。

### 第 4 步：发布到平台
```bash
node .codebuddy/skills/raw-to-gtb-news/scripts/publish-news.js news-pipeline/<YYYY-MM-DD>
```
- 脚本自动将 JSON 组装为平台 HTML（四段式结构 + 来源链接）并 POST 到 `/api/agent/publish`。
- **默认自动清理**：发布成功的 JSON 会被立即删除；发布失败的保留以便修复后重试。
- 如需保留 JSON 可加 `--keep` 参数。
- 检查输出：`✅ 已发布` 且 `忽略品类=[]`（空数组 = 全部品类映射成功）。
- 全部发布成功后，若 `news-pipeline/<date>/` 目录已空，删除该空目录（保持无冗余）。

### 第 5 步：验证
```bash
curl -s "http://124.222.201.143:3000/api/news?pageSize=10"
```
- 确认新发布的资讯出现在列表中（含标题、source_url、industries、countries、published_at）。

### 第 6 步：清理与收尾（强制执行）
- 确认 `news-pipeline/<YYYY-MM-DD>/` 下无残留 JSON（已发布者由脚本自动删除，失败者修复后重发或经用户确认后删除）。
- 发布成功后删除空的 `news-pipeline/<YYYY-MM-DD>/` 目录。
- 整个任务执行后不留下任何过程文件（JSON、临时目录等）；raw 素材本身保持不动。

## 平台与发布规范

- 发布接口、鉴权、请求体、双写逻辑等详细规范见 `references/gtb-news-api.md`。
- 54 标准品类列表见项目 `.antigravity/skills/report-news/references/standard-categories.json`。
- 平台地址与密钥：项目根 `.env` 中 `GTB_API_URL` 与 `AGENT_API_KEY`。

## 资源

- `scripts/publish-news.js`：JSON → HTML → POST 发布（可传目录或单文件；默认发布成功后自动删除 JSON，`--keep` 保留）。
- `scripts/fetch-og-image.js`：抓取新闻源页面的 og:image 高清配图。
- `references/gtb-news-api.md`：平台发布 API 完整参考（请求体、服务端行为、验证接口）。
