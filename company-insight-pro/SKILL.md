---
name: company-insight-pro
description: 360度企业战略情报洞察工具。用于为特定企业生成深度战略情报报告，涵盖财务穿透、组织架构、采购逻辑、用户舆情及出口准入合规性分析。当用户需要调研潜在海外客户、竞争对手或合作伙伴时触发。
---

# Company Insight Pro (360° 企业战略情报洞察)

本技能用于对全球任意企业（尤其是大型零售商、品牌商、供应链巨头）进行 360 度多维度的商业与战略情报穿透，并生成一份高颜值、交互式、自包含的 HTML 战略情报报告，并自动上传发布至 GlobalTradeBuddy 平台。

## 工作流与执行步骤

### 0. 前置查重拦截（强制执行，避免重复生成）

在启动深度全网搜索和报告撰写之前，**必须先检查平台是否已有该企业的情报研报**：
1. 运行查重脚本（或调用 API）：
   ```bash
   python bin/check_report.py --company "目标公司/品牌名 (如: Action, Screwfix, Auchan)"
   ```
2. **判断逻辑**：
   - **若已存在相关报告**：脚本会输出匹配报告的【报告 ID】、【标准主体名】、【标题】与【查看链接】。立即向用户汇报已有报告详情，并询问：
     > *“平台报告大厅中已收录《[报告标题]》（报告 ID：`[report_id]`，查看链接：[url]）。请问您是直接查阅现有报告，还是需要基于最新数据重新生成并覆盖更新？”*
     - 若用户指示仅需查阅，则直接结束，无需重复消耗 Token；
     - **若用户明确要求重新生成并覆盖更新**：**必须记录该已有报告的 `[report_id]` 与 `[标准主体名]`**，在生成 HTML 时：
       ① 沿用该标准主体名作为 `<meta name="company_name">`；
       ② 在 HTML `<head>` 中注入 `<meta name="target_report_id" content="[report_id]">`；
       ③ 发布时使用 `--target-id [report_id]` 强制执行原地更新覆盖，保证原有报告 URL 和已解锁状态不变。
   - **若不存在该报告**：直接进入下一步开始深度调研（新建模式）。

### 1. 深度调研阶段

- **全网搜索**：使用 `search_web` 或 `read_url_content` 搜索目标公司的最新年度报告、官网新闻中心、行业新闻、以及其在亚洲/中国的采购办事处/实体名称与主要竞争对手。
- **财务数据获取**：重点关注最新财年或季度的全年销售额（营业额）、EBITDA 以及未来 3-5 年的投资计划。
- **合规审计核查**：搜索该公司对供应商的特定审计要求（如 SMETA、BSCI、EcoVadis 分数要求）以及区域性环保法律法规准入限制（如法国 AGEC 法案等）。

### 2. 报告结构化

报告必须包含以下核心板块，**每个独立模块必须附带主要信息的来源链接**，详细要求见 [报告板块指南](references/report-sections.md)：

- **概览与历史**：千字概览（必须包含最新的全年销售额/营业额）、渠道店铺结构、注册及网址信息与历史大事件。
- **渠道深挖与竞争格局**：（针对零售商适用）渠道分布可视化、地理布局、主要市场竞争对手格局及消费人群画像。
- **自有品牌分析**：（针对零售商/渠道商适用）梳理不同品类的自主品牌（自有品牌）矩阵定位、所辖细分品类及对华贴牌采购商机。
- **财务与市场**：财务穿透与市场占位，重点拆解品类营收（非食品类占比）。
- **业务单元与决策链**：重点突出采购组织结构与亚洲采购办公室具体注册实体，把"找哪个部门、找谁、在哪提交"讲清楚。
- **供应链与合规**：采购图谱、主要供应商及其供应品类（供应商名称必须为具体公司名，不得为关联公司），以及合规红线。该板块梳理出的供应商名称将同步填入 `<meta name="suppliers">` 标签。
- **用户舆情**：用户之声与产品改进方向。
- **痛点与战略**：企业痛点与供应商实战建议。

### 3. 交互式报告生成

- **元数据注入（强制要求）**：生成的 HTML 文档 `<head>` 区域必须注入以下精确的 `<meta>` 标签（多值标签使用英文半角逗号 `,` 分割）：

  ```html
  <meta name="category" content="customer">
  <meta name="summary" content="[150字以内的报告摘要说明]">
  <meta name="company_name" content="[有且仅有一个标准公司主名，如 BAUHAUS AG]">
  <meta name="company_aliases" content="[公司别名/曾用名列表，如 德国包豪斯, Bauhaus, Baus]">
  <meta name="company_website" content="[公司官方网站网址，如 https://www.bauhaus.info]">
  <meta name="competitors" content="[同业竞争对手简称列表，如 OBI, Hornbach, toom]">
  <meta name="products" content="[产品与品类列表，如 建材, 五金工具, 园艺]">
  <meta name="regions" content="[市场地区列表，如 德国, 欧洲]">
  <meta name="channels" content="[产品销售分销渠道简称列表，若主体本身就是渠道商则留空。如无法查证到真实公司名则留空]">
  <meta name="suppliers" content="[核心供应商简称列表（必须为具体公司名，且不得为该报告公司的关联公司），如 Würth, Kärcher。如无法查证到真实公司名则留空]">
  <meta name="customers" content="[核心买方/大客户简称列表（必须为具体公司名，且不得为该报告公司的关联公司），如 德国电信, 法兰克福机场。如无法查证到真实公司名则留空]">
  <meta name="sister_parents" content="[姐妹公司/母公司/同属集团简称列表，如 InterBauhaus。如无法查证到真实公司名则留空]">
  ```

  **实体名称规范化（强制要求）：**
  - 所有实体名称（包括公司主名、供应商、买方客户、竞争对手、姐妹公司）**一律必须去除法律后缀**（如 `AG`, `GmbH`, `LLC`, `Inc`, `Ltd`, `Co., Ltd.`, `PLC`, `SA`, `SAS`, `BV`, `SE` 等），仅保留干净的商业主体名称（如 `BAUHAUS AG` → `BAUHAUS`，`Fiskars Brands Inc.` → `Fiskars`）。

  **产品品类命名规范（强制要求）：**
  - `products` meta 标签中的品类名称以及报告正文中所有产品/品类的描述，**必须严格对齐** `C:/Users/066/.gemini/config/skills/company-insight-pro/references/GTB产品结构.xlsx`（本 Skill 自带）中的**54个标准行业名称**（即「行业名称 (Category CN)」列）。
  - 禁止使用自定义的品类简称（如"日用百货""服装鞋帽""家装维修"），必须分别替换为标准名称（如"家居用品""男女装/童装/内衣/鞋""五金/工具/建筑及装饰材料"）。

- **UI 规范强制对齐**：报告设计必须严格遵守 [ui-spec.md](references/ui-spec.md) 中的规范。
  1. **色彩体系**：使用暖沙乳白 `#fdfbf7` 为主背景、暖橘 `#ff641e` 为焦点色，禁用高饱和度红绿蓝紫。
  2. **字体排版**：使用系统无衬线字体，大标题 1.25rem/400，正文 0.85~0.95rem/400。
  3. **圆角与阴影**：主卡片 22px、子容器 14~16px、标签 12px，阴影使用暖沙色系 rgba。
  4. **标签净化**：关联实体标签统一使用 `.report-tag` 轻沙配色，禁用彩色胶囊标签。
  5. **无 Emoji**：禁止任何 Emoji，使用 Feather Icons 风格 SVG 替代。
  6. **按钮样式**：使用 `.sand-btn` 水滴按钮样式。
- **可视化要求**：必须使用 **ECharts** 实现至少两个（推荐三个）交互式图表。
- **图像处理与门店横幅（强制要求）**：
  1. 对于拥有实体门店的渠道商/零售商，报告顶部标题处必须附带一张高质量的实体门店横幅大图（建议使用横屏 21:9 比例的建筑摄影格式）。
  2. **标志真实一致性**：门店图片上的企业品牌标志、名称、颜色及特有外文标识必须与官网或街景中的真实店面及招牌完全一致。
  3. **自包含嵌入**：该图像一律通过 Base64 编码直接嵌入 HTML 模板中，禁止采用任何外部物理链接或相对路径。

### 4. 自动上传到 Globaltradebuddy 平台（强制执行）

报告生成并通过本地自检后，**必须立即调用本技能自带的发布脚本，将生成的自包含 HTML 报告自动推送上传至平台**：

1. 使用 `run_command` 运行 `publish_report.py`：

   - **新建模式**（此前无此报告）：
     ```bash
     python C:/Users/066/.gemini/config/skills/company-insight-pro/scripts/publish_report.py <path/to/your/generated/html>
     ```
   - **覆盖更新模式**（此前已有报告并明确更新）：
     ```bash
     python C:/Users/066/.gemini/config/skills/company-insight-pro/scripts/publish_report.py <path/to/your/generated/html> --target-id <已有报告ID>
     ```

2. **自动发布与真实 ID 校验逻辑（强制要求）**：
   - 该脚本会自动读取 `.env` 中的 `GTB_API_URL` 配置（默认为 `https://marketgraphic.cn`）及 `AGENT_API_KEY`。
   - 解析 HTML 中的 `<meta>` 标签（`company_name`, `summary`, `regions`, `products`, `target_report_id` 等）并校验标准品类名。
   - 向 `/api/agent/publish` 发送 POST 请求。若指定了 `target_report_id`，后端将强制就地执行 `UPDATE` 原报告，保留原有 ID 和解锁状态。
   - **严格禁止预先捏造/猜想 UUID**：终端打印 `[OK] Report published successfully! ID: <真实UUID>`，必须严格以控制台返回的真实 ID 为准。

---

## 质量标准

- **无捏造原则**：联系人邮箱等私密信息如无法获取，必须标注为"无公开信息"，严禁捏造。
- **深度性**：概览模块必须达到 1000 字左右的深度分析，而非简单的列表。
- **落地性**：报告的最后一章必须提供"针对中国供应商的实战建议"。
- **品类名称标准化**：报告全文（包括 meta 标签、ECharts 图表标签、品牌矩阵表格、策略建议）中所有产品/品类名称必须使用 `references/GTB产品结构.xlsx` 中的54个标准行业名称。
- **图表完整渲染契约**：所有在 HTML 中声明了 `class="chart-container"` 且有 ID 的 `div` 占位，在 JS 中必须有独立对应的 `echarts.init()` 初始化及 `setOption` 渲染逻辑。
- **自动化自检**：报告生成并保存后，**必须**运行 `scripts/validate_insight.py` 对生成的 HTML 报告进行合规审计。
- **自包含与清理（强制要求）**：
  1. 报告必须是**单文件 HTML**（图像 Base64 嵌入）。
  2. 任务结束前，**必须删除**所有过程中产生的临时图片、脚本及中间文件，仅保留最终的 HTML 报告。
- **无需浏览器验证**：报告生成并保存后即可视为任务完成，**禁止**自动调用浏览器工具进行视觉验证。
