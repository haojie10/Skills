import json
import sys
import re
import os
from collections import Counter

# NOTE: 业务规则常量 (与 references/business-rules.md 保持一致)
EXPECTED_BCD = {
    "B": "Western Europe+UK+Australia",
    "C": "Eastern Europe+Russia",
    "D": "North America"
}
ALLOWED_AP = {"BK", "CB", "WB", "PB", "BP", "OTHER"}
# 所有必须为纯英文的列
ENGLISH_COLUMNS = {"P", "R", "T", "V", "X", "Z", "AB", "AD", "AF", "AH", "AJ", "AO"}
BRAND_COLUMN = "BB"
EXPECTED_BRAND = "Howstoday"

# 标题禁止参数正则 (Rule 4)
# 匹配: 150g, 5.5V, 0.2W, 300mah, 16*2835, BH-HY-001, HY-001, GSPC-001 等
PROHIBITED_TITLE_PATTERNS = [
    re.compile(r'[a-zA-Z]{2,}-\d+', re.I),  # 型号如 BH-HY-001
    re.compile(r'\d+g', re.I),              # 重量如 150g
    re.compile(r'\d+\.?\d*[VvWw]', re.I),   # 电压/功率如 5.5V, 0.2W
    re.compile(r'\d+mah', re.I),            # 电池如 300mah
    re.compile(r'\d+\*\d+', re.I),          # 规格如 16*2835
    re.compile(r'\d+LED', re.I),            # LED数量如 12LED
]

# 通用占位符正则 (Rule 6)
PLACEHOLDER_SP_NAMES = re.compile(r'亮点|卖点[一二三四五]|Point\s*\d+|Feature\s*\d+', re.I)

CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fa5]')


def check_compliance(json_path):
    """
    检查 JSON 数据是否符合 MDS 业务规则
    """
    if not os.path.exists(json_path):
        print(f"Error: File not found: {json_path}")
        return False

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Failed to parse JSON: {e}")
        return False

    errors = 0
    warnings = 0

    # NOTE: 用于去重检测的收集器
    duplicate_detectors = {
        "O": [], "P": [],  # 标题
        "Q": [], "S": [], "U": [],  # 中文卖点
        "R": [], "T": [], "V": []   # 英文卖点
    }
    an_descriptions = []  # 收集所有行的 AN 列值
    
    # 逻辑预警统计
    ap_values = []
    aq_values = []
    ar_values = []
    carton_fields_empty = [] # 记录 AS, AT, AU, AV 是否全为空

    print(f"[*] 开始校验数据合规性: {os.path.basename(json_path)}")

    for i, item in enumerate(data):
        row_num = i + 4  # Excel 中的实际行号 (从第4行开始写入)
        is_spu_head = item.get("_is_spu_head", True)

        # 0. 标题校验 (Rule 4)
        for col in ["O", "P"]:
            title_val = str(item.get(col, ""))
            # 品牌名校验
            if EXPECTED_BRAND.lower() in title_val.lower():
                print(f"  [!] Error: Row {row_num} Col {col} (Title) contains BRAND name '{EXPECTED_BRAND}'")
                errors += 1
            # 型号/参数校验 (仅 SPU 首行检测标题质量)
            if is_spu_head:
                for pattern in PROHIBITED_TITLE_PATTERNS:
                    match = pattern.search(title_val)
                    if match:
                        print(f"  [!] Error: Row {row_num} Col {col} (Title) contains prohibited param/model: '{match.group()}'")
                        errors += 1

        # 1. BCD 市场校验 (仅 SPU 首行)
        if is_spu_head:
            for col, expected in EXPECTED_BCD.items():
                val = item.get(col)
                if val != expected:
                    print(f"  [!] Warning: Row {row_num} Col {col} (Market) is '{val}', expected '{expected}'")
                    warnings += 1

        # 2. 品牌校验 (仅 SPU 首行)
        if is_spu_head:
            brand = item.get(BRAND_COLUMN)
            if brand != EXPECTED_BRAND:
                print(f"  [!] Warning: Row {row_num} Col {BRAND_COLUMN} (Brand) is '{brand}', expected '{EXPECTED_BRAND}'")
                warnings += 1

        # 3. 卖点格式与占位符校验 (Rule 6)
        if is_spu_head:
            # 中文卖点列: Q, S, U
            # 英文卖点列: R, T, V
            for col in ["Q", "R", "S", "T", "U", "V"]:
                val = str(item.get(col, "")).strip()
                if not val: continue
                
                # 检查冒号
                sep = "：" if col in ["Q", "S", "U"] else ":"
                if sep not in val:
                    print(f"  [!] Error: Row {row_num} Col {col} (Selling Point) missing separator '{sep}'")
                    errors += 1
                else:
                    # 检查占位符名称
                    name = val.split(sep)[0].strip()
                    if PLACEHOLDER_SP_NAMES.search(name):
                        print(f"  [!] Error: Row {row_num} Col {col} (Selling Point) uses generic placeholder name: '{name}'")
                        errors += 1

        # 4. 描述结构校验 (Rule 9)
        # AN (中文)
        an_val = str(item.get("AN", "")).strip()
        if an_val:
            # 强化型号前缀检测
            if any(prefix in an_val for prefix in ["型号：", "编号：", "品号：", "Item No", "Model"]):
                print(f"  [!] Error: Row {row_num} Col AN (Desc) should NOT contain Model/Item No labels")
                errors += 1
            if "尺寸：" not in an_val or "材质：" not in an_val:
                print(f"  [!] Error: Row {row_num} Col AN (Desc) missing '尺寸：' or '材质：' keys")
                errors += 1
        
        # AO (英文)
        ao_val = str(item.get("AO", "")).strip()
        if ao_val:
            if any(prefix in ao_val for prefix in ["Model:", "Item No:", "Part No:", "型号", "编号"]):
                print(f"  [!] Error: Row {row_num} Col AO (Desc) should NOT contain Model/Item No labels")
                errors += 1
            if "Size:" not in ao_val or "Material:" not in ao_val:
                print(f"  [!] Error: Row {row_num} Col AO (Desc) missing 'Size:' or 'Material:' keys")
                errors += 1

        # 4b. 型号交叉校验 (Rule 4 & 9) - 检查 AK 列型号是否出现在标题或描述中
        model_id = str(item.get("AK", "")).strip()
        if model_id and len(model_id) > 2: # 忽略过短的型号避免误报
            # 检查标题
            if model_id.lower() in str(item.get("O", "")).lower():
                print(f"  [!] Error: Row {row_num} Col O (CN Title) contains the Model ID '{model_id}' from Col AK")
                errors += 1
            if model_id.lower() in str(item.get("P", "")).lower():
                print(f"  [!] Error: Row {row_num} Col P (EN Title) contains the Model ID '{model_id}' from Col AK")
                errors += 1
            # 检查描述
            if model_id.lower() in an_val.lower():
                print(f"  [!] Error: Row {row_num} Col AN (CN Desc) contains the Model ID '{model_id}' from Col AK")
                errors += 1
            if model_id.lower() in ao_val.lower():
                print(f"  [!] Error: Row {row_num} Col AO (EN Desc) contains the Model ID '{model_id}' from Col AK")
                errors += 1

        # 5. AP 包装简写校验 (SKU 维度必填)
        ap = item.get("AP")
        if not ap:
            print(f"  [!] Error: Row {row_num} Col AP (Packing) is MISSING")
            errors += 1
        elif ap not in ALLOWED_AP:
            print(f"  [!] Error: Row {row_num} Col AP (Packing) '{ap}' is NOT a standard shorthand ({', '.join(ALLOWED_AP)})")
            errors += 1
        ap_values.append(ap)

        # 6. 英文列中文字符检测
        for col in ENGLISH_COLUMNS:
            val = str(item.get(col, ""))
            if CHINESE_PATTERN.search(val):
                print(f"  [!] Error: Row {row_num} Col {col} (English field) contains CHINESE characters: '{val}'")
                errors += 1

        # 7. AY 货币单位校验 (Rule 10)
        aw_val = item.get("AW")
        ay_val = item.get("AY")
        if aw_val is not None and str(aw_val).strip() not in ("", "None"):
            if not ay_val or str(ay_val).strip() in ("", "None"):
                print(f"  [!] Error: Row {row_num} Col AY (Currency) is MISSING but AW (Price) has value '{aw_val}'")
                errors += 1

        # 8. AQ 单包数量校验 (Rule 11)
        aq_val = item.get("AQ")
        if aq_val is None or str(aq_val).strip() in ("", "None"):
            print(f"  [!] Error: Row {row_num} Col AQ (Qty per pack) is MISSING")
            errors += 1
        else:
            try:
                aq_num = int(aq_val)
                aq_values.append(aq_num)
                if aq_num < 1:
                    print(f"  [!] Error: Row {row_num} Col AQ (Qty per pack) is {aq_num}, must be >= 1")
                    errors += 1
                if aq_num > 10:
                    print(f"  [!] Warning: Row {row_num} Col AQ (Qty per pack) is {aq_num}, unusually high. Please confirm.")
                    warnings += 1
            except (ValueError, TypeError):
                print(f"  [!] Error: Row {row_num} Col AQ (Qty per pack) '{aq_val}' is not a valid integer")
                errors += 1

        # 9. AR 外箱装量预警
        ar_val = item.get("AR")
        if ar_val is not None and str(ar_val).strip() not in ("", "None"):
            try:
                ar_values.append(int(ar_val))
            except: pass

        # 10. 箱规缺失预警 (AS, AT, AU, AV)
        is_empty_carton = all(str(item.get(c, "")).strip() in ("", "None") for c in ["AS", "AT", "AU", "AV"])
        carton_fields_empty.append(is_empty_carton)

        # 收集去重检测数据
        if is_spu_head:
            for col in duplicate_detectors.keys():
                val = str(item.get(col, "")).strip()
                if val:
                    duplicate_detectors[col].append(val)

        if an_val:
            an_descriptions.append(an_val)

    # --- 聚合预警 ---

    # AP 全部为 OTHER 预警
    if ap_values and all(v == "OTHER" for v in ap_values):
        print(f"  [!] Warning: ALL products ({len(ap_values)}) are marked as 'OTHER' packing. Please check _raw_desc for specific packing info.")
        warnings += 1

    # AR 全部相同预警
    if len(ar_values) >= 5:
        if len(set(ar_values)) == 1:
            print(f"  [!] Warning: ALL products have the SAME carton qty ({ar_values[0]}). Please check if this matches source data.")
            warnings += 1

    # 箱规全空预警
    if carton_fields_empty and all(carton_fields_empty):
        print(f"  [!] Warning: Carton info (AS/AT/AU/AV) is MISSING for ALL rows. Please try to extract from source.")
        warnings += 1

    # 标题与卖点去重检测 (Rule 6: 多样性红线 10%)
    for col, values in duplicate_detectors.items():
        if len(values) >= 5:
            counter = Counter(values)
            common = counter.most_common(1)
            if common:
                most_common_val, most_common_count = common[0]
                dup_ratio = most_common_count / len(values)
                if dup_ratio > 0.1 and most_common_count > 1:
                    print(f"  [!] Error: Row 4+ Col {col} has excessive DUPLICATION ({dup_ratio:.0%}). Most common: '{str(most_common_val)[:60]}...'")
                    errors += 1

    # 描述去重检测 (Rule 9: 不同产品不应共用相同描述)
    if len(an_descriptions) >= 3:
        an_counter = Counter(an_descriptions)
        an_common = an_counter.most_common(1)
        if an_common:
            most_common_an, most_common_an_count = an_common[0]
            an_dup_ratio = most_common_an_count / len(an_descriptions)
            if an_dup_ratio > 0.5:
                print(f"  [!] Warning: {most_common_an_count}/{len(an_descriptions)} rows ({an_dup_ratio:.0%}) share IDENTICAL description AN: '{str(most_common_an)[:60]}...'")
                warnings += 1

    print(f"\n--- 校验结束: {os.path.basename(json_path)} ---")
    print(f"总计错误 (Errors): {errors}")
    print(f"总计警告 (Warnings): {warnings}")
    
    if errors > 0:
        print("\n[FAILED] 数据包含不合规项，请修正后再执行写入。")
        return False
    else:
        print("\n[PASSED] 数据校验通过！")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_compliance.py <json_path>")
        sys.exit(1)
    
    success = check_compliance(sys.argv[1])
    sys.exit(0 if success else 1)

