# GTB 平台新闻发布 API 参考

GlobalTradeBuddy 平台新闻（资讯）发布接口规范。对应代码：`pages/api/agent/publish.ts`。

## 端点

```
POST {GTB_API_URL}/api/agent/publish
```

- `GTB_API_URL` **必需**，从项目根 `.env` 读取（参考 `.env.example`）；示例值 `http://124.222.201.143:3000`
- 鉴权：`Authorization: Bearer {AGENT_API_KEY}`，`AGENT_API_KEY` **必需**，从项目根 `.env` 读取，脚本不内置默认密钥
- 请求体上限：20MB

## 请求体（type = "article"）

```json
{
  "type": "article",
  "title": "中文标题",
  "summary": "摘要（≤160 字，取自 recap 开头）",
  "contentHtml": "<div class=\"gtb-news-article\">...</div>",
  "region": "欧洲",
  "country": "瑞典",
  "industry": "家居用品",
  "industries": ["家居用品", "五金", "工具"],
  "tags": {
    "companies": ["Clas Ohlson"],
    "products": ["家居用品", "五金"],
    "regions": ["瑞典", "挪威"]
  }
}
```

## 服务端行为（article 分支）

1. `runDehydration(contentHtml, uploadImage)`：图片脱水——正文中的图片转存静态文件。
2. 写入 `articles` 表（`source='agent'`），含 `region` / `country` / `industry` 字段。
3. 提取实体并写入 `article_entities`（`tags` 字段驱动：companies / products / regions / channels）。
4. **双写 `news` 表**（前台资讯大厅展示用）：`status='published'`，`source_url` 取 contentHtml 中首个 `href`。
5. 关联 `news_industries`：**支持 `industries` 数组，循环写入全部标准品类**（`getStandardCategory` 逐条映射，未匹配则计入 `ignoredCategories`）。`industries` 为空时回退用单个 `industry` 字段。
6. 关联 `news_countries`：仅**单个** `country` 字段映射国家表。

> 发布脚本 `publish-news.js` 会自动将 JSON 的 `industries` 数组传给接口，实现多品类标签完整写入与前台展示（前台 `/api/news` 用 `ARRAY_TO_STRING` 聚合展示全部关联品类）。

## 成功响应

```json
{ "success": true, "id": "uuid", "type": "article", "ignoredCategories": [] }
```

- `ignoredCategories` 非空 = 有品类标签未被 54 标准品类映射，需人工检查修正。

## 失败响应

- `400` 缺少 title 或 contentHtml
- `401` API Key 无效
- `500` 服务端未配置 `AGENT_API_KEY`

## 公开验证接口

- `GET {GTB_API_URL}/api/news?pageSize=5`：返回 news 表列表（含 title / summary / source_url / industries / countries / published_at），用于验证发布是否成功。
- `GET {GTB_API_URL}/api/articles`：articles 表接口（当前线上返回 500，暂用 `/api/news` 验证）。

## 标准品类映射

54 个标准品类列表：`.workbuddy/skills/raw-to-gtb-news/references/standard-categories.json`（7 簇 54 类，来源：`haoiejie10/Global-Trade-Buddy` 仓库的 `report-news` 技能）。

品类标签（`industries` / `tags.products`）必须严格使用该文件中的 54 个标准行业名称，禁止自创非标词。
