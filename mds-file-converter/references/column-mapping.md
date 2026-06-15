# 列对齐 JSON 结构规范 (A - BB)

JSON 为数组结构，每个元素代表一行数据。Key 严格对齐模版列字母。

## 完整列映射表

| 列 | 字段名 | 类型 | 说明 |
|----|--------|------|------|
| A | 分类 | string | 留空 |
| B | 主要市场1 | string | 默认 `Western Europe+UK+Australia` |
| C | 主要市场2 | string | 默认 `Eastern Europe+Russia` |
| D | 主要市场3 | string | 默认 `North America` |
| E | 主图 | string(path) | 产品主图路径，写入时自动插入图片 |
| F | 图片1 | string(path) | 三视图1 |
| G | 图片2 | string(path) | 三视图2 |
| H | 图片3 | string(path) | 三视图3 |
| I | 图片1.1 | string(path) | 尺寸图1 |
| J | 图片2.1 | string(path) | 尺寸图2 |
| K | 图片3.1 | string(path) | 尺寸图3 |
| L | 图片1.2 | string(path) | 场景图1 |
| M | 图片2.2 | string(path) | 场景图2 |
| N | 图片3.2 | string(path) | 场景图3 |
| O | 标题(中) | string | 约20字电商风格中文标题，禁止含型号 |
| P | 标题(英) | string | Amazon 风格英文标题，禁止含品牌名及型号 |
| Q | 卖点1(中) | string | 由 LLM 根据图片和描述生成的中文核心卖点 |
| R | 卖点1(英) | string | 由 LLM 生成的对应英文核心卖点 |
| S | 卖点2(中) | string | 从源文件额外提取的卖点，由 LLM 整理 |
| T | 卖点2(英) | string | 对应的英文额外卖点 |
| U | 卖点3(中) | string | |
| V | 卖点3(英) | string | |
| W | 卖点4(中) | string | |
| X | 卖点4(英) | string | |
| Y | 卖点5(中) | string | |
| Z | 卖点5(英) | string | |
| AA | 卖点6(中) | string | |
| AB | 卖点6(英) | string | |
| AC | 卖点7(中) | string | |
| AD | 卖点7(英) | string | |
| AE | 卖点8(中) | string | |
| AF | 卖点8(英) | string | |
| AG | 卖点9(中) | string | |
| AH | 卖点9(英) | string | |
| AI | 卖点10(中) | string | |
| AJ | 卖点10(英) | string | |
| AK | 关键词 | string | 搜索关键词 |
| **AL** | **SKU图** | **string(path)** | **SKU 图片路径** |
| AM | 尾缀 | string | 可为空 |
| AN | 产品描述(中) | string | 中文产品长描述 |
| AO | 产品描述(英) | string | 英文产品长描述 |
| AP | 包装方式 | string | 标准简写：BK/CB/WB/PB/BP/OTHER |
| AQ | 单包数量 | number | 通常为 1 |
| AR | 外箱数量 | number | 一个外箱的产品数量 |
| AS | 外箱毛重 | number | 单位 KG |
| AT | 外箱长 | number | 单位 cm |
| AU | 外箱宽 | number | 单位 cm |
| AV | 外箱高 | number | 单位 cm |
| **AW** | **采购价格** | **number** | **纯数字** |
| AX | (空) | string | 留空 |
| **AY** | **币种** | **string** | **默认 "USD"** |
| **AZ** | **MOQ** | **number** | **最小起订量** |
| **BA** | **供应商** | **string** | **如「深圳高丰」** |
| **BB** | **品牌** | **string** | **固定 "Howstoday"** |

## JSON 示例

```json
[
  {
    "A": "厨房置物架",
    "B": "Western Europe+UK+Australia",
    "C": "Eastern Europe+Russia",
    "D": "North America",
    "E": "temp/images/img_r13_c2_1.png",
    "F": "", "G": "", "H": "",
    "I": "", "J": "", "K": "",
    "L": "", "M": "", "N": "",
    "O": "多功能不锈钢厨房置物架台面调料瓶餐具收纳架家用厨房整理架",
    "P": "Multi-Functional Stainless Steel Kitchen Storage Rack Countertop Organizer",
    "Q": "多功能设计：适用于多种厨房场景",
    "R": "Multi-functional: Suitable for various kitchen scenarios",
    "S": "", "T": "", "U": "", "V": "", "W": "", "X": "",
    "Y": "", "Z": "",
    "AA": "", "AB": "", "AC": "", "AD": "",
    "AE": "", "AF": "", "AG": "", "AH": "",
    "AI": "", "AJ": "",
    "AK": "kitchen holder organizer",
    "AL": "temp/images/img_r13_c2_1.png",
    "AM": "",
    "AN": "尺寸：60x40x30cm\n净重：1.5kg\n材质：不锈钢\n包装：彩盒\n产品优势：多功能厨房不锈钢置物架，适用于调料瓶、餐具等收纳",
    "AO": "Size: 60x40x30cm\nNet Weight: 1.5kg\nMaterial: Stainless steel\nPackage: Color box\nAdvantages: Multi-functional stainless steel kitchen holder for spices and utensils",
    "AP": "CB",
    "AQ": 1,
    "AR": 12,
    "AS": 10.5,
    "AT": 60, "AU": 40, "AV": 30,
    "AW": 8.89,
    "AX": "",
    "AY": "USD",
    "AZ": 2000,
    "BA": "深圳高丰",
    "BB": "Howstoday"
  }
]
```

## 辅助字段 (Internal Metadata)

为了提高 AI 增强阶段的质量，提取阶段必须使用以 `_` 开头的辅助字段存储结构化数据。这些字段在写入 Excel 时会被自动忽略。

| 字段名 | 说明 | 来源 |
|--------|------|------|
| `_is_spu_head` | 布尔值，标记该行是否为 SPU 的首行 | 逻辑判断 |
| `_spu_id` | SPU 唯一标识符（通常为型号前缀） | 逻辑提取 |
| `_raw_item_no` | 原始产品型号（如 `BH-HY-001`） | **Rule 19 强制要求** |
| `_raw_size` | 原始尺寸文本（如 `直径7.2cm×高19.5cm`） | **Rule 19 强制要求** |
| `_raw_weight` | 原始净重文本（如 `175g`） | **Rule 19 强制要求** |
| `_raw_material` | 原始材质文本（如 `ABS+PP`） | **Rule 19 强制要求** |
| `_raw_packing` | 原始包装描述（如 `单个装邮购盒`） | **Rule 19 强制要求** |
| `_raw_qty_per_carton`| 原始每箱数量（如 `48`） | **Rule 19 强制要求** |
| `_raw_carton_gw` | 原始外箱毛重（如 `10kg`） | **Rule 19 强制要求** |
| `_raw_carton_meas` | 原始外箱尺寸（如 `520*520*560mm`） | **Rule 19 强制要求** |
| `_raw_price` | 原始价格文本 | **Rule 19 强制要求** |
| `_raw_desc` | 原始完整描述文本 | 上下文参考 |

## 写入规则

- **起始行**: Row 4（前 3 行为模版表头）
- **图片列**: E 和 AL 的值若为 `.png`/`.jpg` 路径且文件存在，则插入图片（100x100）
- **非图片列**: 直接写入文本/数字值
- **SPU 分组**: 同一 SPU 后续 SKU 行的 A~AJ 列以及 BA~BB 列留空
- **样式**: 细边框 + 居中对齐 + 自动换行 + 行高 80
