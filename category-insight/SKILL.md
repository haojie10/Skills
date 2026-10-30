---
name: category-insight
description: |
  针对特定零售市场（如北美、加拿大、欧洲、亚太）和不同渠道进行特定品类的深度调研与横向对比，并生成一份高颜值的 HTML 可视化报告与概念产品设计图，并自动上传发布至 GlobalTradeBuddy 平台。
  触发条件：
  - 用户提到「品类洞察」「品类调研」「渠道对比分析」「竞品对比」「市场洞察」「Category Insight」「上传平台」
  - 用户要求分析某个特定渠道的特定产品（如 Dollarama 的泳帽、Dollar General 的手持风扇、Canadian Tire 的纸袋等）并形成报告
  - 用户需要一份针对制造企业的研发升级建议与产品设计图
---

# Category Insight (品类深度洞察与渠道对比)

本技能用于针对特定零售市场（如北美、加拿大、欧洲、亚太等）和不同渠道（如 Dollarama、Dollar General、Target、Walmart、Costco、Amazon 等），对特定产品品类进行深度商业情报调研与横向对比，生成高颜值、交互式的自包含 HTML 报告，并自动上传发布至 GlobalTradeBuddy 平台。

## 完整执行流程与标准

### 第一步：锁定要素与深度检索

1. **锁定核心要素**：
   - **目标品类**：具体产品品类（如：泳帽 / 硅胶泳帽、手持风扇、牛皮纸袋、超细纤维抹布等）。
   - **目标区域与渠道**：目标国家/市场（如美国、加拿大、德国、全美连锁商超）及核心调研渠道（如 Dollarama vs Canadian Tire vs Walmart）。
   - **自动化直通原则**：无需进行任何平台查重探测，收到任务立即直接开始全自动深度调研与内容生产。
2. **检索真实市场信息**：
   - 使用 `search_web` 收集该渠道中目标品类的在售商品、品牌分布、价格带、包装形式、规格参数与热销卖点。
   - 提取消费者的真实痛点（亚马逊差评、Reddit 讨论、专业测评网站等）。

### 第二步：结构化分析与 HTML 报告生成

1. **五大核心分析模块**（严格遵循 [方法论](references/methodology.md)）：
   - **品类矩阵分析**：梳理各渠道的核心 SKU、价格区间、材质规格、主打功能。
   - **多渠道横向对比**：从定位、定价策略、包装视觉、目标客群四个维度进行深度对比。
   - **用户痛点与差评诊断**：提炼消费者抱怨最多的 Top 3~5 核心痛点。
   - **中国制造差距诊断**：从工业设计、材料应用、包装环保性、成本控制等维度剖析当前国产出海产品的痛点。
   - **研发升级建议与产品创新方案**：提供 2~3 个具体的产品升级提案（每款提案需覆盖：适用人群画像、解决的具体痛点、精益降本与差异化工程设计）。（注：最终报告中严禁出现“反堆料”字样，卡片开发建议统一为「3. 开发建议：」）。
2. **视觉与元数据规范**：
   - 遵循暖沙极简设计规范（暖白背景 `#fdfbf7`、主卡片 `#f6f3ec`、强调色 `#ff641e`、无 Emoji、系统无衬线字体）。
   - 在 HTML `<head>` 中必须注入标准 `<meta>` 标签：
     - `<meta name="category" content="product">`
     - `<meta name="summary" content="...">`
     - `<meta name="products" content="...">`（品类名必须对齐 GTB 54 标准行业分类）
     - `<meta name="regions" content="...">`
     - `<meta name="channels" content="...">`

### 第三步：自包含嵌入与自动发布上线

1. **单文件 Base64 嵌入与 Logo 保护**：
   - 报告中的所有配图和概念设计图必须使用 Base64 编码内嵌至单个 HTML 文件中；
   - 必须保留母版 `assets/report-template.html` 中的官方 Market Graphic Base64 Logo（长 23,250 字符，严禁人工截断）；
   - 执行 `python scripts/embed_images.py <html_path>`，该脚本已内置自动缩放压缩、Base64 内嵌及**官方 Logo 自动检测与自愈补全**机制，彻底杜绝 Logo 丢失。
2. **一键自动发布至平台**：
   - 报告生成并通过本地自检后，调用发布脚本推送至平台：
     ```bash
     python C:/Users/066/.gemini/config/skills/category-insight/scripts/publish_report.py <path_to_html>
     ```

---

## 质量与配图规范（强制门禁）

- **配图数量标准**：
  1. **线下实体渠道**（如 MediaMarkt / Target / Dollarama / Costco 等）：**必须配置 4 张大图**（1 张商超门头/展柜 Hero Banner + 3 张独立产品概念创新升级款）；
  2. **纯电商渠道**（如 Amazon / 独立站等）：**标配 3 张独立产品概念图**。
- **生图降级与严格串行标准（铁律）**：
  - 原生生图配额耗尽时，自动调用标准脚本 `~/.gemini/config/skills/category-insight/scripts/flow_image_generator.py`（直连 Chrome 9222 端口）；
  - **必须严格遵循单张阻塞式串行执行流程**：
    `[Prompt 注入] -> [点击生成] -> [阻塞监听 naturalWidth >= 500 & complete] -> [HTTP 拉取无损原图流] -> [PIL 压缩落盘] -> [磁盘校验通过] -> [冷却 3 秒] -> [才允许开始下一张]`；
  - **严禁并发或在上一张未完成时抢跑写入下一张 Prompt**，彻底杜绝 Flow 任务被冲掉、重复生图和图片错位。
- **自包含嵌入与清理**：
  - 报告必须为**单文件 HTML**（所有图片经 PIL 压缩后以 Base64 内嵌）；
  - 任务结束后，**必须自动删除**所有过程中产生的临时图片，仅保留最终的 `.html` 报告。
- **命名规范**：最终报告文件必须以 `品类-市场-insight.html`（短横线命名）命名。
- **自动化上线**：必须确保报告已通过 `publish_report.py` 成功推送至 `https://marketgraphic.cn` 平台并反馈 Report ID。


