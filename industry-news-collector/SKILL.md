---
name: industry-news-collector
description: 自动搜索、分类并格式化特定行业一周内的真实出海快讯。能够按照产品创新、行业大数据、消费者动态、行业机会、人才流动和资本活动等6个维度在不同国家搜集10条资讯，生成符合 GTB 资讯发布 API (JSON 格式) 标准的数据包。
---

# Industry News Collector (行业快讯收集与发布技能)

本技能用于自动搜集出海核心行业（如照明产品、家用电器等）在全球主要目标市场的最新（一周内）资讯，并按规范结构化为 JSON 数据，供 Global Trade Buddy 后台 API 进行一键导入和发布。

## 核心规范与维度

搜集的资讯必须覆盖以下 6 大商业洞察维度：
1. **产品创新 (Product Innovation)**：新技术、新协议支持（如 Matter 协议）、能效突破。
2. **行业大数据 (Big Data)**：权威调研机构的最新市场规模估值、增长预测百分比。
3. **消费者/用户动态 (Consumer Dynamics)**：健康照明（昼夜节律）、智能家居消费者偏好变化。
4. **行业机会 (Opportunities)**：因政策、电价、AI 数据中心爆发拉动的新市场需求。
5. **人才流动 (Talent Flow)**：跨国巨头（如 Signify, OSRAM）的核心高管变动或专业委员会专家入职。
6. **资本活动 (Capital Activities)**：资产收购、战略投资、行业重组。

## 数据真实性与质量标准

- **绝无幻觉原则**：
  - **来源链接必须 100% 真实有效**（例如指向 `iea.org`、`grandviewresearch.com`、`technews.tw`、`smart.lighting`、`trendforce.com` 等官方与权威媒体的新闻地址）。
  - 禁止使用不存在的占位符 URL 或是捏造的新闻地址。
- **图片源规范**：每条资讯需要附带一张相关联的、真实的高清配图 URL（可以使用开放的公共 CDN 图像、或相关公司的官方公开插图链接）。
- **时间限制**：搜集的资讯必须为**最近一周内**的发生事件。

## 执行工作流

### 1. 资讯检索
使用 `search_web` 工具，结合行业词（如 `smart lighting`、`LED efficiency`）以及时间限制、维度词进行精准的搜索。

### 2. 字段映射与大类对齐
- **行业大类 ID 关联**：将资讯的 `industry_ids` 严格对齐数据库 `industries` 中的标准 ID（如“照明产品”大类的 UUID）。
- **国家 ID 关联**：根据资讯涉及的国家，绑定 `countries` 表中对应的标准 UUID。

### 3. API 结构校验
输出的数据必须完全兼容 `/api/admin/news` POST 请求格式：
```json
{
  "title": "快讯标题",
  "summary": "100字以内的摘要",
  "content": "Markdown/HTML 格式的详细快讯正文",
  "source_url": "真实的原文链接",
  "status": "published",
  "industry_ids": ["行业的UUID"],
  "country_ids": ["国家的UUID"]
}
```
