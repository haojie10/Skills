"""
MDS 列对齐 JSON → 产品业务批量导入模版 通用写入脚本

功能：
  读取一个列对齐 JSON 文件（Key 为 A-BB 列字母），
  将数据逐行写入「产品业务批量导入模版.xlsx」，生成最终导入文件。

特性：
  - 自动识别图片列（E, F-N, AL）并嵌入缩放后的图片
  - 统一应用边框、居中对齐、自动换行样式
  - 行高统一为 80，图片缩放至 100x100
  - 从第 4 行开始写入（前 3 行为模版表头）

用法：
  python write_from_json.py <input_json> [output_xlsx] [template_xlsx]

  参数说明：
    input_json    - 必填，列对齐 JSON 文件路径
    output_xlsx   - 可选，输出 Excel 文件名（默认：<input_json前缀>_MDS导入模版.xlsx）
    template_xlsx - 可选，模版文件路径（默认：产品业务批量导入模版.xlsx）

示例：
  python write_from_json.py tianyuan.json
  python write_from_json.py tianyuan.json 天元_MDS导入模版.xlsx
  python write_from_json.py tianyuan.json output.xlsx custom_template.xlsx
"""

import json
import os
import sys
import openpyxl
from openpyxl.drawing.image import Image
from openpyxl.styles import Border, Side, Alignment

# NOTE: 图片列列表 —— 值为图片绝对路径时自动嵌入
IMAGE_COLUMNS = {"E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "AL"}

# NOTE: 样式常量
THIN_SIDE = Side(style='thin')
BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)
ALIGNMENT = Alignment(horizontal='center', vertical='center', wrap_text=True)

# NOTE: 模版表头占 3 行，数据从第 4 行开始
START_ROW = 4
ROW_HEIGHT = 80
IMG_SIZE = 100


def writeJsonToTemplate(
    inputJson: str,
    outputXlsx: str = "",
    templatePath: str = "产品业务批量导入模版.xlsx"
):
    """
    将列对齐 JSON 文件写入 MDS 导入模版

    Args:
        inputJson: 列对齐 JSON 文件路径
        outputXlsx: 输出 Excel 文件名，为空时自动生成
        templatePath: 模版文件路径
    """
    if not os.path.exists(inputJson):
        raise FileNotFoundError(f"JSON 文件不存在: {inputJson}")

    if not os.path.exists(templatePath):
        raise FileNotFoundError(f"模版文件不存在: {templatePath}")

    # 自动生成输出文件名
    if not outputXlsx:
        baseName = os.path.splitext(os.path.basename(inputJson))[0]
        outputXlsx = f"{baseName}_MDS导入模版.xlsx"

    with open(inputJson, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("JSON 文件内容必须是非空数组")

    print(f"[*] 加载模版: {templatePath}")
    wb = openpyxl.load_workbook(templatePath)
    ws = wb.active

    print(f"[*] 写入 {len(data)} 行数据...")

    for i, item in enumerate(data):
        currentRow = START_ROW + i
        ws.row_dimensions[currentRow].height = ROW_HEIGHT

        for colLetter, value in item.items():
            # 跳过非列字母的辅助字段（如 _raw_context）
            if colLetter.startswith("_"):
                continue

            colIdx = openpyxl.utils.column_index_from_string(colLetter)
            cell = ws.cell(row=currentRow, column=colIdx)

            # 处理图片列：值为图片路径且文件存在时嵌入图片
            if colLetter in IMAGE_COLUMNS and value and isinstance(value, str) and os.path.exists(value):
                try:
                    img = Image(value)
                    original_width = img.width
                    original_height = img.height
                    if original_width and original_height:
                        if original_width > original_height:
                            img.width = IMG_SIZE
                            img.height = int((IMG_SIZE / original_width) * original_height)
                        else:
                            img.height = IMG_SIZE
                            img.width = int((IMG_SIZE / original_height) * original_width)
                    else:
                        img.width = IMG_SIZE
                        img.height = IMG_SIZE
                    ws.add_image(img, f"{colLetter}{currentRow}")
                    cell.value = ""
                except Exception as e:
                    print(f"  [!] 图片插入失败 {colLetter}{currentRow}: {e}")
                    cell.value = value
            else:
                cell.value = value

            # 应用统一样式
            cell.border = BORDER
            cell.alignment = ALIGNMENT

    print(f"[*] 保存至: {outputXlsx}")
    try:
        wb.save(outputXlsx)
    except (PermissionError, OSError):
        import time
        alt_name = f"{os.path.splitext(outputXlsx)[0]}_{int(time.time())}.xlsx"
        print(f"  [!] 无法写入 {outputXlsx} (可能文件已打开)。尝试保存为: {alt_name}")
        wb.save(alt_name)
        outputXlsx = alt_name
        
    print(f"[*] 完成！共写入 {len(data)} 行。")
    return outputXlsx


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    inputPath = sys.argv[1]
    outputPath = sys.argv[2] if len(sys.argv) > 2 else ""
    template = sys.argv[3] if len(sys.argv) > 3 else "产品业务批量导入模版.xlsx"

    writeJsonToTemplate(inputPath, outputPath, template)
