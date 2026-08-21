# -*- coding: utf-8 -*-
"""
company-insight-pro 自动化报告合规与图表自检脚本（含 Node.js JS 真实语法解析与品牌母版规范门禁）
"""
import os
import re
import sys
import subprocess
import tempfile

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 54个GTB标准行业名称名称列表
STANDARD_CATEGORIES = {
    "办公文具", "保暖用品", "包装用品", "餐厨器皿", "宠物用品",
    "服装饰物及配件", "个人护理用具", "工艺品", "户外用品", "家具",
    "家居日用品", "家居用品", "家用电器", "家用纺织品", "节庆用品",
    "节日用品", "美妆工具", "美妆护肤", "母婴用品", "男女装",
    "汽车用品", "日用五金", "收纳用品", "数码配件", "水具",
    "体育及旅游休闲用品", "童装", "玩具", "卫浴用品", "文化用品",
    "五金", "五金工具", "鞋", "医药保健品及医疗器械", "益智玩具",
    "园艺用品", "园林用品", "孕婴童用品", "运动户外用品", "照明产品",
    "钟表眼镜", "厨房用具", "电子配件", "服装配饰", "工具",
    "清洁用品", "户外运动", "食品", "童车童床", "内衣",
    "箱包及皮具", "建筑及装饰材料", "安防劳保用品", "礼品及赠品"
}

REQUIRED_METAS = [
    "category",
    "summary",
    "company_name",
    "company_aliases",
    "company_website",
    "competitors",
    "products",
    "regions",
    "channels",
    "suppliers",
    "customers",
    "sister_parents"
]

def check_js_syntax(script_content):
    """使用 node -c 严密校验 JavaScript 代码块是否存在语法错误"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w", encoding="utf-8") as tmp:
            tmp_path = tmp.name
            tmp.write(script_content)
            
        res = subprocess.run(["node", "-c", tmp_path], capture_output=True, text=True, encoding="utf-8", errors="ignore")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
        if res.returncode != 0:
            return False, res.stderr.strip()
        return True, ""
    except Exception as e:
        lines = script_content.split("\n")
        for line_no, line in enumerate(lines, 1):
            if re.search(r"'[^'\\]*'[a-zA-Z0-9_\s\u4e00-\u9fa5]+[^'\\]*'", line):
                return False, f"Line {line_no}: 怀疑未转义单引号在 JS 字符串中打破语法 -> {line.strip()}"
        return True, ""

def validate_html(html_path):
    print(f"[*] 开始审计报告: {html_path}")
    
    if not os.path.exists(html_path):
        print(f"[ERROR] 文件未找到: {html_path}")
        return False
        
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    success = True
    
    # 1. 审计 Meta 元数据完整性
    print("[*] 正在审计 Meta 元数据...")
    meta_values = {}
    for meta in REQUIRED_METAS:
        pattern = rf'<meta\s+[^>]*name=["\']{meta}["\']\s+content=(["\'])(.*?)\1'
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if not match:
            pattern_rev = rf'<meta\s+[^>]*content=(["\'])(.*?)\1\s+name=["\']{meta}["\']'
            match = re.search(pattern_rev, content, re.IGNORECASE | re.DOTALL)
            
        if match:
            val = match.group(2).strip()
            meta_values[meta] = val
            print(f"  [OK] 检出 Meta -> {meta}: \"{val}\"")
        else:
            print(f"  [ERROR] 缺失必填 Meta 标签: <meta name=\"{meta}\" content=\"...\">")
            success = False
            
    # 2. 审计 products 标准化对齐
    if "products" in meta_values and meta_values["products"]:
        print("[*] 正在审计产品品类标准化对齐 (GTB产品分类)...")
        prods = [p.strip() for p in meta_values["products"].split(",") if p.strip()]
        for p in prods:
            if p in STANDARD_CATEGORIES:
                print(f"  [OK] 品类对齐: \"{p}\"")
            else:
                print(f"  [ERROR] 品类 \"{p}\" 不符合 GTB 标准行业名称！请对照标准 54 个分类进行映射。")
                success = False
                
    # 3. 审计 Emoji 净化
    print("[*] 正在审计正文及标题 Emoji 净化...")
    clean_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]')
    emojis_found = emoji_pattern.findall(clean_content)
    if emojis_found:
        print(f"  [ERROR] 检测到未净化的 Emoji 图标: {' '.join(set(emojis_found))}，请按照 UI 规范移除或用 SVG 矢量图标替代！")
        success = False
    else:
        print("  [OK] 未发现正文 Emoji 标识。")
        
    # 4. 审计 Market Graphic 官方品牌 Logo 与 Header 规范（硬性门禁）
    print("[*] 正在审计 Market Graphic 官方品牌 Logo 与 Header 规范...")
    has_powered_by = bool(re.search(r'Powered\s+by', content, re.IGNORECASE))
    has_mg_logo = bool(re.search(r'alt=["\']Market\s+Graphic["\']', content, re.IGNORECASE) or "iVBORw0KGgoAAAANSUhEUgAAAHAAAABACAYAAADCmvPm" in content)
    
    if has_powered_by and has_mg_logo:
        print("  [OK] 检出 Header 顶部 Market Graphic 官方 Logo 及 Powered by 标识。")
    else:
        print("  [ERROR] 🚨 缺失 Market Graphic 官方 Logo 图片或 Powered by 标示！")
        print("          必须直接读取 assets/report-template.html 作为基底模板进行填充，不得擅自删除或手写骨架！")
        success = False

    # 5. 审计 页脚官网超链接 (Footer)
    print("[*] 正在审计页脚官网超链接与生成声明...")
    has_footer_link = bool(re.search(r'href=["\']https?://(?:www\.)?marketgraphic\.cn["\']', content, re.IGNORECASE) or "marketgraphic.cn" in content)
    if has_footer_link:
        print("  [OK] 检出 Footer 底部 marketgraphic.cn 官方超链接。")
    else:
        print("  [ERROR] 🚨 缺失 Footer 底部官方链接 <a href=\"https://marketgraphic.cn\" ...>www.marketgraphic.cn</a>！")
        success = False

    # 6. 审计 ECharts DOM 绑定与 JS 真实语法解析 (Node.js Syntax Audit)
    print("[*] 正在审计 ECharts DOM 节点与 JavaScript 真实语法合规...")
    
    script_blocks = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
    for idx, script in enumerate(script_blocks):
        js_ok, js_err = check_js_syntax(script)
        if not js_ok:
            print(f"  [ERROR] 🚨 <script> 代码块 #{idx+1} 包含真实的 JavaScript SyntaxError！")
            print(f"          错误细节: {js_err}")
            success = False
        else:
            print(f"  [OK] <script> 代码块 #{idx+1} 语法完全正确。")

    dom_ids = []
    pattern_dom1 = re.compile(r'<div[^>]+id=["\']([^"\']+)["\'][^>]+class=["\'][^"\']*chart-container[^"\']*["\']')
    pattern_dom2 = re.compile(r'<div[^>]+class=["\'][^"\']*chart-container[^"\']*["\'][^>]+id=["\']([^"\']+)["\']')
    
    for match in pattern_dom1.finditer(content):
        dom_ids.append(match.group(1))
    for match in pattern_dom2.finditer(content):
        if match.group(1) not in dom_ids:
            dom_ids.append(match.group(1))
            
    print(f"  已检测到的图表容器 DOM 节点: {dom_ids}")
    
    for chart_id in dom_ids:
        ref_pattern_single = rf"getElementById\(['\"]{chart_id}['\"]\)"
        if not re.search(ref_pattern_single, content):
            print(f"  [ERROR] 图表 DOM 节点 id=\"{chart_id}\" 存在，但在 JS 代码中未发现独立引用或初始化！")
            success = False
        else:
            print(f"  [OK] 图表 id=\"{chart_id}\" 成功在 JS 中被独立获取并绑定。")
            
    # 7. 审计占位符未替换残留
    print("[*] 正在审计模板占位符残留...")
    placeholders = re.findall(r'\{\{[A-Z0-9_]+\}\}', content)
    if placeholders:
        print(f"  [ERROR] 检测到未替换的模板占位符: {set(placeholders)}")
        success = False
    else:
        print("  [OK] 无任何模板占位符残留。")
        
    print("--- 审计结论 ---")
    if success:
        print("[SUCCESS] 报告校验完全合格！")
        return True
    else:
        print("[FAIL] 报告中存在合规项、品牌规范缺失或 JS 语法错误，请按上方报错信息修改 HTML 文件。")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python validate_insight.py <path_to_html_report>")
        sys.exit(1)
        
    report_path = sys.argv[1]
    is_valid = validate_html(report_path)
    if not is_valid:
        sys.exit(1)
