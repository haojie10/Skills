---
name: mds-file-converter
description: |
  从供应商提供的产品文档（Excel/PDF/PPT）中提取产品信息和图片，生成列对齐的中间 JSON 文件和临时图片文件夹，
  再根据业务规则将数据写入「产品业务批量导入模版.xlsx」。
  **核心能力：**
  - 使用 universal_extractor.py 一键导出任意格式（PDF/Excel/PPT）的物理层文本和图片。
  - 依赖大模型强大的长上下文和多模态理解能力（One-Shot Reasoning），一次性完成产品的语义映射、智能合并与参数推导。
  - 自动化合规扫描保障最终 Excel 数据质量。
  触发条件：
  - 用户提到「MDS文件转化」「产品提取」「模版填充」「供应商文件转化」
  - 用户要求从 PDF/Excel/PPT 中提取产品信息并写入导入模版
  - 用户要求生成列对齐的 JSON 中间文件
---

# MDS 文件转化器

将供应商产品文档（Excel / PDF / PPT）自动转化为标准化的「产品业务批量导入模版」。本流程采用 AI 认知驱动的现代化工作流，摒弃了脆弱的正则匹配脚本，直接通过统一提取器获取原始素材后，由 AI 一次性完成语义映射和合规生成。

## 工作流程

```
准备环境（复制 Skill 内置模版）
         ↓
源文件 (PDF / Excel / PPT)
         ↓
第一步：物理层通用导出 (Universal Extractor)
   └─ 运行 python scripts/universal_extractor.py <源文件>
   └─ 结果：生成 temp/raw_data.txt（所有文本）和 temp/images/（所有图片）
         ↓
第二步：AI 语义映射与生成 (One-Shot Reasoning)
   ├─ Agent 阅读 raw_data.txt 和图片，自主理解产品 SPU/SKU 结构
   ├─ 一次性生成符合所有业务规则的 target.json（无需提取中间态 _raw_* 字段）
   ├─ 自动生成合规的中文标题（O/P 列）、中英双语卖点（Q-AJ 列）、SKU 级描述（AN/AO 列）
   └─ 智能 Fallback（缺失的包装/箱规由 AI 按公式估算）
         ↓
第三步：数据合规性自动扫描 (Compliance Check)
   └─ 运行 python scripts/check_compliance.py target.json
   └─ 执行 15+ 项严格检测（包含字段完整性、格式规范、数据逻辑等），Errors > 0 严禁写入
         ↓
第四步：写入模版 (Writer)
   └─ 运行 python scripts/write_from_json.py target.json
   └─ 自动加载图片并生成最终的 Excel
```

### 第零步：准备工作环境

> [!IMPORTANT]
> **必须在开始任务前执行此步骤。** Skill 的 `assets/` 目录内置了关键模版文件，
> agent 应先检查工作目录是否已有这些文件，若缺失则从 Skill 内置资源复制过去。

1. 确定工作目录：**源文件所在的目录**（或用户指定的目录）
2. 检查工作目录是否存在以下文件：
   - `产品业务批量导入模版.xlsx`
3. 若文件缺失，从 Skill 内置资源复制：
   - 源路径（Skill 内置）：`assets/产品业务批量导入模版.xlsx`
   - 目标路径：工作目录
4. 确保临时目录 `temp/` 及 `temp/images/` 可以正常使用

### 第〇.五步：阅读参考示例

> [!TIP]
> 在开始生成前，**必须先阅读** `examples/` 目录下的目标格式示例文件，
> 熟悉我们需要的最终 JSON 结构，这是 AI 一次性正确生成的基石。

- **目标格式参考**：[`examples/target_format_example.json`](examples/target_format_example.json)
- 重点关注：
   - SPU 首行 vs 后续 SKU 行的字段填充差异（同 SPU 的后续 SKU 行 A-AJ 列留空）
   - AN/AO 列每行独立填写（尺寸必须取当前 SKU 的实际值）
   - 必须使用 `_spu_id` 等辅助字段建立 SPU 间的分组与关联
   - BA 列（供应商编号）默认为空
   - AW 列（采购价格）源文件没有则为空，AY 也对应留空

### 第一步：物理层通用导出 (Universal Extractor)

不再使用零碎的特定格式解析脚本，直接使用通用导出器将物理信息“压榨”出来。

1. 运行命令：`python scripts/universal_extractor.py <源文档路径>`
2. 脚本会自动在当前目录下创建 `temp/` 文件夹。
3. 产出物：
   - `temp/raw_data.txt`：包含从 PDF/Excel/PPT 导出的所有文本的原始序列。
   - `temp/images/`：存放所有提取出的产品图（按页码或原本顺序命名）。

### 第二步：AI 语义映射与生成 (One-Shot Reasoning)

> [!CAUTION]
> **摒弃提取与增强的两步走逻辑，直接进行一次性生成。**
> Agent 需要结合 `raw_data.txt` 中的文本上下文，以及 `view_file` 或视觉能力查看 `temp/images/` 中的图片，通过强大的推理能力直接映射到最终的 JSON 结构。

**处理要求：**

1. **认知重组**：从乱序的 `raw_data.txt` 中梳理出有意义的产品集合（SPU），判断哪些内容属于同一个产品的不同变体（SKU）。
2. **多模态对齐**：将 `temp/images/` 里的图片文件名与梳理出的 SPU 准确匹配，填入 `E` 和 `AL` 列。
3. **内容创作与填充**：
   - **标题生成（O/P 列）**：电商风格约20字，禁止含型号/电气参数。
   - **卖点生成（Q-AJ 列）**：三级优先级，中英配对，格式：`卖点名称：卖点描述`，每个 SPU 必须独立创作，严禁千篇一律的套话。
   - **产品描述（AN/AO 列）**：按 SKU 维度独立填写，禁止含型号。
4. **智能 Fallback（Rule 15）**：
   - 缺失包装或箱规数据时，由 AI 按产品类型合理估算。
   - 估算值建议通过 `_estimated` 辅助字段标记提醒用户。

> [!IMPORTANT]
> **强制预览确认**：在生成最终的大型 JSON 之前（例如处理完前 3 个产品后），Agent 必须暂停并向用户展示这几个产品的标题、卖点、以及主要 JSON 结构，等待用户确认风格和质量后再继续生成剩余产品。

### 第三步：数据合规性校验 (Compliance Check)

> [!IMPORTANT]
> **最后一道防线：严禁跳过合规性扫描。**
> 在生成 `target.json` 后，必须运行以下命令：
> `python scripts/check_compliance.py target.json`

若脚本输出包含 `Errors`，必须返回上一步修正 JSON 数据，直至校验通过（PASSED）。这是防止错误数据污染最终模版的物理边界。

### 第四步：写入模版 (Writer)

使用通用写入脚本 `scripts/write_from_json.py`：

```bash
python scripts/write_from_json.py target.json [output_xlsx] [template_xlsx]
```

1. 加载 `产品业务批量导入模版.xlsx`
2. 读取 JSON，从**第 4 行**开始逐行写入。
3. 图片列（E, F-N, AL）根据 JSON 中的本地路径自动嵌入并缩放至 100x100。
4. 应用边框、居中对齐，行高设为 80。
5. 任务结束后清理 `temp/` 临时文件夹（Rule 14）。

## 业务规则

详见 [references/business-rules.md](references/business-rules.md)

## 列对齐 JSON 结构规范

详见 [references/column-mapping.md](references/column-mapping.md)

## 关键文件路径

| 文件 | 路径 | 说明 |
|------|------|------|
| 通用提取器 | [`scripts/universal_extractor.py`](scripts/universal_extractor.py) | PDF/PPT/Excel -> raw text + images |
| 通用写入脚本 | [`scripts/write_from_json.py`](scripts/write_from_json.py) | JSON → Excel 写入 |
| 合规性校验脚本 | [`scripts/check_compliance.py`](scripts/check_compliance.py) | 15+ 项自动化合规检测 |
| 业务规则 | [`references/business-rules.md`](references/business-rules.md) | 业务约束规则详情 |
| 列映射规范 | [`references/column-mapping.md`](references/column-mapping.md) | A-BB 列对齐 JSON 结构 |
