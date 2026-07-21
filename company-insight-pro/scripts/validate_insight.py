# -*- coding: utf-8 -*-
"""
company-insight-pro 自动化报告合规与图表自检脚本
"""
import os
import re
import sys

# 54个GTB标准行业名称名称列表
STANDARD_CATEGORIES = {
    "家用电器", "电子消费品及信息产品", "电子电气产品", "照明产品", "新能源汽车及智慧出行",
    "车辆", "汽车配件", "摩托车", "自行车", "动力、电力设备", "通用机械及机械基础件",
    "加工机械设备", "工程机械（室内/室外）", "农业机械（室内/室外）", "工业自动化及智能制造",
    "五金", "工具", "新材料及化工产品", "新能源", "日用陶瓷", "餐厨器皿", "家居用品",
    "玻璃工艺品", "工艺陶瓷", "礼品及赠品", "节日用品", "玩具", "编织及藤铁工艺品",
    "家居装饰品", "园林用品", "石材/铁艺制品（室外）", "建筑及装饰材料", "卫浴设备",
    "家具", "钟表眼镜", "个人护理用具", "宠物用品", "男女装", "童装", "内衣",
    "运动服及休闲服", "裘革皮羽绒及制品", "服装饰物及配件", "纺织原料面料", "家用纺织品",
    "地毯及挂毯", "鞋", "箱包", "办公文具", "体育及旅游休闲用品", "医药保健品及医疗器械",
    "食品", "乡村振兴特色产品", "孕婴童用品"
}

# 必须包含的 12 个 Meta 标签
REQUIRED_METAS = [
    "category", "summary", "company_name", "company_aliases", "company_website",
    "competitors", "products", "regions", "channels", "suppliers", "customers",
    "sister_parents"
]

def validate_html(html_path):
    print(f"[*] 开始审计报告: {html_path}")
    
    if not os.path.exists(html_path):
        print(f"[ERROR] 报告文件不存在: {html_path}")
        return False
        
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    success = True
    
    # 1. 审计 Meta 标签
    print("[*] 正在审计 Meta 元数据...")
    meta_values = {}
    for meta in REQUIRED_METAS:
        # 正则提取 <meta name="xxx" content="yyy"> 或 <meta name='xxx' content='yyy'>
        pattern = rf'<meta\s+[^>]*name=["\']{meta}["\']\s+content=["\']([^"\']*)["\']'
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            pattern_rev = rf'<meta\s+[^>]*content=["\']([^"\']*)["\']\s+name=["\']{meta}["\']'
            match = re.search(pattern_rev, content, re.IGNORECASE)
            
        if match:
            val = match.group(1).strip()
            meta_values[meta] = val
            print(f"  [OK] 检出 Meta -> {meta}: \"{val}\"")
        else:
            print(f"  [ERROR] 缺失必需 Meta 标签: {meta}")
            success = False
            
    # 2. 审计标准品类对齐
    if "products" in meta_values and meta_values["products"]:
        print("[*] 正在审计产品品类标准化对齐 (GTB产品分类)...")
        products_list = [p.strip() for p in meta_values["products"].split(",") if p.strip()]
        for p in products_list:
            if p in STANDARD_CATEGORIES:
                print(f"  [OK] 品类对齐: \"{p}\"")
            else:
                print(f"  [ERROR] 品类 \"{p}\" 不符合 GTB 标准行业名称！请对照标准 54 个分类进行映射。")
                success = False
                
    # 3. 审计 Emoji 净化（忽略 HTML 注释）
    print("[*] 正在审计正文及标题 Emoji 净化...")
    clean_content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]')
    emojis = emoji_pattern.findall(clean_content)
    if emojis:
        print(f"  [WARNING] 检测到正文或标题中包含 Emoji: {set(emojis)}，请根据 ui-spec.md 移除并替换为 SVG 图标。")
    else:
        print("  [OK] 未发现正文 Emoji 标识。")
        
    # 4. 审计 ECharts 完整渲染契约 (DOM 与 JS 映射审计)
    print("[*] 正在审计 ECharts 完整渲染与短路初始化检测...")
    
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
            print(f"  [ERROR] 图表 DOM 节点 id=\"{chart_id}\" 存在，但在 JS 代码中未发现独立引用或初始化（可能被逻辑短路如 || 跳过，或未编写对应的 echarts.init 代码）！")
            success = False
        else:
            print(f"  [OK] 图表 id=\"{chart_id}\" 成功在 JS 中被独立获取并绑定。")
            
    # 5. 校验占位符残留
    print("[*] 正在审计模板占位符残留...")
    placeholders = re.findall(r'\{\{[A-Z0-9_]+\}\}', clean_content)
    if placeholders:
        print(f"  [ERROR] 检出未替换的模板占位符: {set(placeholders)}")
        success = False
    else:
        print("  [OK] 无任何模板占位符残留。")
        
    print("--- 审计结论 ---")
    if success:
        print("[SUCCESS] 报告校验完全合格！")
        return True
    else:
        print("[FAIL] 报告中存在合规项错误，请按上方报错信息修改 HTML 文件。")
        return False

if __name__ == "__main__":
    target_file = r"d:\我的APP\客户档案\home-depot-insight-report.html"
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
        
    res = validate_html(target_file)
    sys.exit(0 if res else 1)
