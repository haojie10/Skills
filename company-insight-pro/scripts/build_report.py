# -*- coding: utf-8 -*-
"""
company-insight-pro / build_report.py
一体化报告构建、纯数据全模块渲染、自愈清洗、门禁校验与平台发布流水线工具。

核心优化特性：
1. 全模块【纯数据模式】（100% Pure-Data Schema）与【HTML片段模式】双轨无缝兼容；
2. 彻底杜绝大段平铺文字，所有模块自动化渲染为 Tailwind 现代高保真 Sand-Card 卡片与精美网格；
3. 全流程自动数据净化（Auto-Sanitization）：自动剥离 Emoji、自动去除法律后缀、净化 Meta HTML；
4. 内置 Google Flow 本地生图闭环（--auto-flow）：精准匹配公司名，生图配额耗尽时直连本地 CDP 9222 自动生图；
5. 一键平台发布与知识图谱自动互联，任务中心原子回写。
"""

import os
import re
import sys
import glob
import io
import json
import base64
import argparse
import urllib.request
import urllib.error

# 强制 UTF-8 跨平台输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# 导入同目录的门禁与发布模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    import validate_insight
    HAS_VALIDATE = True
except ImportError:
    HAS_VALIDATE = False

try:
    import publish_report
    HAS_PUBLISH = True
except ImportError:
    HAS_PUBLISH = False


def sanitize_text(val):
    """递归清洗数据中的 Emoji 字符"""
    if isinstance(val, str):
        return re.sub(r'[\U00010000-\U0010ffff]', '', val)
    elif isinstance(val, dict):
        return {k: sanitize_text(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_text(v) for v in val]
    return val


def clean_legal_suffix(name):
    """去除公司名称中的常见法律后缀"""
    if not name:
        return ""
    cleaned = re.sub(
        r'\b(AG|GmbH|LLC|Inc\.?|Ltd\.?|Corp\.?|PLC|SA|SAS|BV|SE|S\.A\.B\.|Pty\.?|Co\.,\s*Ltd\.?)\b',
        '',
        name,
        flags=re.IGNORECASE
    )
    return re.sub(r'\s+', ' ', cleaned).strip()


def strip_html_tags(text):
    """去除字符串中的所有 HTML 标签"""
    if not isinstance(text, str):
        return ""
    return re.sub(r'<[^>]+>', '', text).strip()


# ==============================================================================
# 纯数据模式辅助生成器 (Pure Data Section Generators) - 严格遵循 Sand-Card UI 规范
# ==============================================================================

def generate_overview_html(overview_data):
    """将概览段落包装为符合规范的缩进排版"""
    if not overview_data:
        return ""
    if isinstance(overview_data, list):
        paras = overview_data
    else:
        # 如果是已有 HTML 且包含 <p>，原样返回
        if "<p" in overview_data:
            return overview_data
        paras = [p.strip() for p in overview_data.split("\n\n") if p.strip()]

    html_parts = []
    for p in paras:
        html_parts.append(f'<p class="text-justify indent-8 text-sm leading-relaxed mb-4 text-[#3c3935]">{p}</p>')
    return "\n".join(html_parts)


def generate_registration_table_html(reg_dict):
    """从键值字典生成与模板 UI 规范 100% 对齐的 2xN 注册信息表格"""
    if not reg_dict or not isinstance(reg_dict, dict):
        return ""
    items = list(reg_dict.items())
    rows = []
    for i in range(0, len(items), 2):
        k1, v1 = items[i]
        if i + 1 < len(items):
            k2, v2 = items[i + 1]
            rows.append(f"""            <tr class="divide-x divide-[rgba(160,109,68,0.06)]">
                <td class="p-2.5 font-medium bg-[#f6f3ec]/60 text-[#7a756f] w-1/4">{k1}</td>
                <td class="p-2.5 text-[#3c3935] w-1/4">{v1}</td>
                <td class="p-2.5 font-medium bg-[#f6f3ec]/60 text-[#7a756f] w-1/4">{k2}</td>
                <td class="p-2.5 text-[#3c3935] w-1/4">{v2}</td>
            </tr>""")
        else:
            rows.append(f"""            <tr class="divide-x divide-[rgba(160,109,68,0.06)]">
                <td class="p-2.5 font-medium bg-[#f6f3ec]/60 text-[#7a756f] w-1/4">{k1}</td>
                <td class="p-2.5 text-[#3c3935] w-3/4" colspan="3">{v1}</td>
            </tr>""")
            
    return f"""<div class="mt-4 overflow-hidden rounded-xl border border-[rgba(160,109,68,0.12)]">
    <table class="w-full text-xs text-left">
        <tbody class="divide-y divide-[rgba(160,109,68,0.06)]">
{"".join(rows)}
        </tbody>
    </table>
</div>"""


def generate_brand_matrix_html(brand_list_or_dict):
    """生成品牌矩阵 8 宫格胶囊卡片"""
    if not brand_list_or_dict:
        return ""
    
    items = []
    title = "核心合作品牌与授权分销矩阵"
    subtitle = "全渠道授权目录"
    
    if isinstance(brand_list_or_dict, dict):
        title = brand_list_or_dict.get("title", title)
        subtitle = brand_list_or_dict.get("subtitle", subtitle)
        raw_items = brand_list_or_dict.get("brands", [])
    elif isinstance(brand_list_or_dict, list):
        raw_items = brand_list_or_dict
    else:
        return str(brand_list_or_dict)

    for item in raw_items:
        if isinstance(item, dict):
            name = item.get("name", "")
            desc = item.get("desc", "")
        elif isinstance(item, str):
            parts = item.split(":") if ":" in item else (item.split("（") if "（" in item else [item, ""])
            name = parts[0].strip()
            desc = parts[1].replace("）", "").replace(")", "").strip() if len(parts) > 1 else ""
        else:
            continue
        
        items.append(f"""<div class="p-2.5 rounded-lg bg-[#f6f3ec] border border-[rgba(160,109,68,0.08)] text-center">
    <strong class="block text-xs text-[#3c3935]">{name}</strong>
    <span class="text-[10px] text-[#7a756f]">{desc}</span>
</div>""")

    return f"""<div class="p-4 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.12)] my-4">
    <div class="flex items-center justify-between mb-3">
        <h4 class="text-xs uppercase font-bold text-[#ff641e] tracking-wider flex items-center gap-1.5">
            <i data-lucide="layers" size="14"></i> {title}
        </h4>
        <span class="text-[10px] text-[#7a756f] font-medium">{subtitle}</span>
    </div>
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
{"".join(items)}
    </div>
</div>"""


def generate_timeline_html(timeline_list):
    """从结构化列表生成符合模板 UI 规范的时间线 HTML"""
    if not timeline_list or not isinstance(timeline_list, list):
        return ""
    items = []
    for item in timeline_list:
        date = item.get("date") or item.get("year", "")
        title = item.get("title", "")
        desc = item.get("desc") or item.get("content", "")
        items.append(f"""<li class="relative pl-2">
    <div class="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-[#ff641e] ring-4 ring-[#fdfbf7]"></div>
    <span class="text-xs font-bold text-[#ff641e]">{date}</span>
    <p class="font-medium text-xs mt-0.5 text-[#3c3935]">{title}</p>
    <p class="text-[11px] text-[#7a756f] leading-relaxed">{desc}</p>
</li>""")
    return "\n".join(items)


def generate_finance_insights_html(insights_list):
    """生成财务核心洞察卡片群"""
    if not insights_list or not isinstance(insights_list, list):
        return ""
    cards = []
    color_map = {
        "red": "text-red-500",
        "amber": "text-amber-500",
        "orange": "text-[#ff641e]",
        "green": "text-green-600",
        "blue": "text-blue-600"
    }
    badge_colors = ["green", "orange", "blue", "red", "amber"]

    for idx, item in enumerate(insights_list):
        title = item.get("title", f"洞察 {idx+1}")
        tag = item.get("tag") or item.get("badge", "核心洞察")
        desc = item.get("desc") or item.get("content", "")
        color_choice = item.get("color") or badge_colors[idx % len(badge_colors)]
        tag_color = color_map.get(color_choice, "text-[#ff641e]")

        cards.append(f"""<div class="p-3.5 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <div class="flex justify-between items-center mb-1">
        <strong class="text-[#3c3935] text-xs font-bold">{title}</strong>
        <span class="text-[10px] {tag_color} font-semibold">{tag}</span>
    </div>
    <p class="text-[#7a756f] leading-relaxed">{desc}</p>
</div>""")

    return f'<div class="space-y-3.5 text-xs">\n' + "\n".join(cards) + "\n</div>"


def generate_channels_grid_html(channels_list):
    """生成 2x2 渠道分布与工程网络结构化卡片网格"""
    if not channels_list or not isinstance(channels_list, list):
        return ""
    cards = []
    default_icons = ["map-pin", "wrench", "shopping-cart", "award", "store", "truck"]
    for idx, item in enumerate(channels_list):
        title = item.get("title", "")
        icon = item.get("icon") or default_icons[idx % len(default_icons)]
        desc = item.get("desc") or item.get("content", "")
        cards.append(f"""<div class="p-3 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <h5 class="font-bold text-[#3c3935] mb-1 flex items-center gap-1.5">
        <i data-lucide="{icon}" size="14" class="text-[#ff641e]"></i> {title}
    </h5>
    <p class="text-[#7a756f] leading-relaxed">{desc}</p>
</div>""")

    return f'<div class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">\n' + "\n".join(cards) + "\n</div>"


def generate_competitors_html(comp_list):
    """从结构化竞品列表生成符合模板 UI 规范的沙色竞品卡片 HTML"""
    if not comp_list or not isinstance(comp_list, list):
        return ""
    cards = []
    for comp in comp_list:
        name = clean_legal_suffix(comp.get("name", ""))
        tag = comp.get("tag") or comp.get("tier", "核心竞品")
        position = comp.get("position") or comp.get("desc", "")
        pros_cons = comp.get("pros_cons") or comp.get("comparison", "")
        
        cards.append(f"""<div class="p-3 bg-[#fdfbf7] rounded-xl border border-[rgba(160,109,68,0.08)] mb-3">
    <div class="flex justify-between items-center mb-1">
        <span class="font-bold text-xs text-[#3c3935]">{name}</span>
        <span class="text-[10px] bg-[#ff641e]/10 text-[#ff641e] px-1.5 py-0.5 rounded font-medium">{tag}</span>
    </div>
    <p class="text-[11px] text-[#7a756f] leading-relaxed mb-1"><strong class="text-[#3c3935]">市场占位：</strong>{position}</p>
    <p class="text-[11px] text-[#7a756f] leading-relaxed"><strong class="text-[#3c3935]">竞争优劣：</strong>{pros_cons}</p>
</div>""")
    return "\n".join(cards)


def generate_brand_table_html(brand_table_list):
    """生成品牌与中国供应链替代机会的精美表格"""
    if not brand_table_list or not isinstance(brand_table_list, list):
        return ""
    rows = []
    for item in brand_table_list:
        cat = item.get("category") or item.get("product", "")
        brands = item.get("brands") or item.get("channel", "")
        oem = item.get("oem") or item.get("opportunity", "")
        rows.append(f"""<tr>
    <td class="p-2.5 font-semibold bg-[rgba(160,109,68,0.02)]">{cat}</td>
    <td class="p-2.5 border-r border-[rgba(160,109,68,0.08)]">{brands}</td>
    <td class="p-2.5 text-[#7a756f]">{oem}</td>
</tr>""")

    return f"""<div class="overflow-x-auto">
    <table class="w-full text-xs text-left text-[#3c3935] border border-[rgba(160,109,68,0.12)] rounded-lg">
        <thead class="bg-[#f6f3ec] text-[#ff641e] font-bold border-b border-[rgba(160,109,68,0.12)]">
            <tr>
                <th class="p-2.5 w-1/4">核心产品大类</th>
                <th class="p-2.5 w-1/3 border-r border-[rgba(160,109,68,0.12)]">主要在售品牌与渠道矩阵</th>
                <th class="p-2.5">中国制造供应链深度切入契机</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-[rgba(160,109,68,0.08)] bg-[#fdfbf7]">
{"".join(rows)}
        </tbody>
    </table>
</div>"""


def generate_oem_opportunity_html(oem_data):
    """生成代工与贴牌商机卡片"""
    if not oem_data:
        return ""
    if isinstance(oem_data, str):
        if "<div" in oem_data:
            return oem_data
        title = "去欧美化后的中国源头工厂直采红利"
        tag = "战略合作高地"
        desc = oem_data
    elif isinstance(oem_data, dict):
        title = oem_data.get("title", "代工与贴牌核心商机洞察")
        tag = oem_data.get("tag", "核心商机")
        desc = oem_data.get("desc", "")
    else:
        return str(oem_data)

    return f"""<div class="p-4 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.12)] space-y-3">
    <div class="flex items-center gap-2">
        <span class="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded">{tag}</span>
        <h5 class="text-xs font-bold text-[#3c3935]">{title}</h5>
    </div>
    <p class="text-xs text-[#7a756f] leading-relaxed">{desc}</p>
</div>"""


def generate_decision_chain_html(decision_list):
    """生成组织架构与采购决策链四象限卡片"""
    if not decision_list or not isinstance(decision_list, list):
        return ""
    cards = []
    color_classes = [
        ("bg-blue-100 text-blue-600"),
        ("bg-[#ff641e]/10 text-[#ff641e]"),
        ("bg-purple-100 text-purple-600"),
        ("bg-amber-100 text-amber-600")
    ]
    for idx, item in enumerate(decision_list):
        step_num = item.get("step") or str(idx + 1)
        role = item.get("role") or item.get("title", "")
        desc = item.get("desc") or item.get("content", "")
        badge_cls = color_classes[idx % len(color_classes)]
        cards.append(f"""<div class="p-3.5 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <div class="flex items-center gap-2 mb-1.5">
        <div class="w-5 h-5 rounded-full {badge_cls} flex items-center justify-center font-bold text-[10px]">{step_num}</div>
        <strong class="text-[#3c3935]">{role}</strong>
    </div>
    <p class="text-[#7a756f]">{desc}</p>
</div>""")

    return f"""<div class="space-y-3 text-xs leading-relaxed">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
{"".join(cards)}
    </div>
</div>"""


def generate_contact_path_html(contact_data):
    """生成关键联系人与商业对接路径"""
    if not contact_data:
        return ""
    if isinstance(contact_data, str) and "<div" in contact_data:
        return contact_data
    
    items = []
    if isinstance(contact_data, dict):
        for k, v in contact_data.items():
            if "http" in str(v):
                val_html = f'<a href="{v}" target="_blank" class="text-blue-500 hover:underline font-mono text-[11px]">{v}</a>'
            else:
                val_html = f'<span class="text-[#7a756f] text-[11px]">{v}</span>'
            items.append(f"""<div class="p-3 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <strong class="text-[#3c3935] block mb-1">{k}</strong>
    {val_html}
</div>""")
    elif isinstance(contact_data, list):
        for item in contact_data:
            title = item.get("title", "")
            val = item.get("value", "")
            val_html = f'<a href="{val}" target="_blank" class="text-blue-500 hover:underline font-mono text-[11px]">{val}</a>' if "http" in val else f'<span class="text-[#7a756f] text-[11px]">{val}</span>'
            items.append(f"""<div class="p-3 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <strong class="text-[#3c3935] block mb-1">{title}</strong>
    {val_html}
</div>""")

    return f'<div class="space-y-2.5 text-xs">\n' + "\n".join(items) + "\n</div>"


def generate_supply_flow_html(flow_list):
    """生成供应链 4 步流程方块"""
    if not flow_list or not isinstance(flow_list, list):
        return ""
    cards = []
    for idx, item in enumerate(flow_list, 1):
        num_str = f"{idx:02d}"
        title = item.get("title") or item.get("name", "")
        desc = item.get("desc") or item.get("content", "")
        cards.append(f"""<div class="p-3 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)] text-center">
    <div class="w-6 h-6 rounded-full bg-blue-100 text-blue-600 font-bold mx-auto mb-1 flex items-center justify-center text-[10px]">{num_str}</div>
    <strong class="block text-[#3c3935]">{title}</strong>
    <span class="text-[10px] text-[#7a756f]">{desc}</span>
</div>""")

    return f'<div class="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">\n' + "\n".join(cards) + "\n</div>"


def generate_compliance_html(compliance_list):
    """生成准入合规与认证红线卡片"""
    if not compliance_list or not isinstance(compliance_list, list):
        return ""
    cards = []
    for item in compliance_list:
        code = item.get("standard") or item.get("title", "")
        badge = item.get("badge") or item.get("level", "强制认证")
        desc = item.get("desc") or item.get("content", "")
        badge_color = "text-red-500" if "强制" in badge or "红线" in badge else "text-amber-500"
        cards.append(f"""<div class="p-2.5 rounded-lg bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <div class="flex justify-between items-center mb-0.5">
        <strong class="text-[#3c3935]">{code}</strong>
        <span class="text-[10px] {badge_color} font-bold">{badge}</span>
    </div>
    <p class="text-[#7a756f] text-[11px]">{desc}</p>
</div>""")

    return f'<div class="space-y-2 text-xs">\n' + "\n".join(cards) + "\n</div>"


def generate_pain_points_html(pain_points_list):
    """生成产品差评与设计痛点卡片"""
    if not pain_points_list or not isinstance(pain_points_list, list):
        return ""
    cards = []
    badge_colors = {
        "严重": "text-red-500",
        "结构性": "text-red-500",
        "高频": "text-amber-500",
        "下沉": "text-amber-500"
    }
    for idx, item in enumerate(pain_points_list, 1):
        title = item.get("title", f"痛点 {idx}")
        tag = item.get("tag") or item.get("level", "严重负评集中区")
        desc = item.get("desc") or item.get("content", "")
        tag_color = "text-red-500" if any(k in tag for k in ["严重", "缺口", "致命", "失效"]) else "text-amber-500"
        cards.append(f"""<div class="p-3.5 rounded-xl bg-[#fdfbf7] border border-[rgba(160,109,68,0.1)]">
    <div class="flex justify-between items-center mb-1">
        <strong class="text-[#3c3935] text-xs font-bold">{title}</strong>
        <span class="text-[10px] {tag_color} font-semibold">{tag}</span>
    </div>
    <p class="text-[#7a756f] leading-relaxed">{desc}</p>
</div>""")

    return "\n".join(cards)


def generate_social_media_html(social_data):
    """生成社交媒体舆情统计卡片"""
    if not social_data:
        return ""
    if isinstance(social_data, str) and "<div" in social_data:
        return social_data
    
    if isinstance(social_data, dict):
        score = social_data.get("score", "综合评分 4.5/5.0")
        satisfaction = social_data.get("satisfaction", "好评率 90%+")
        pros = social_data.get("pros", "")
        cons = social_data.get("cons", "")
        source = social_data.get("source", "")
    else:
        return str(social_data)

    source_html = f'<a href="{source}" target="_blank" class="text-blue-500 hover:underline text-[11px] block mt-1">来源：官方社媒与消费者原声</a>' if source else ""

    return f"""<div class="text-xs text-[#7a756f] leading-relaxed space-y-2">
    <div class="flex items-center gap-2 mb-1">
        <span class="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded">{score}</span>
        <span class="text-[10px] text-[#3c3935] font-semibold">{satisfaction}</span>
    </div>
    <p><strong>高频正面评价：</strong>{pros}</p>
    <p><strong>高频改进诉求：</strong>{cons}</p>
    {source_html}
</div>"""


def generate_improvements_html(improvements_list):
    """生成中国供应商技术改进方案清单"""
    if not improvements_list or not isinstance(improvements_list, list):
        return ""
    items = []
    for item in improvements_list:
        if isinstance(item, dict):
            t = item.get("title", "")
            d = item.get("desc", "")
            items.append(f'<li><strong>{t}：</strong>{d}</li>')
        elif isinstance(item, str):
            items.append(f'<li>{item}</li>')

    return f'<ul class="list-disc pl-4 space-y-1.5 text-[#3c3935] text-[11px]">\n' + "\n".join(items) + "\n</ul>"


def generate_strategies_html(strat_list):
    """从结构化建议列表生成符合模板 UI 规范的实战建议卡片 HTML"""
    if not strat_list or not isinstance(strat_list, list):
        return ""
    cards = []
    for idx, item in enumerate(strat_list, 1):
        step_str = f"策略{['一','二','三','四','五','六','七','八'][idx-1] if idx<=8 else idx}"
        title = item.get("title", "")
        desc = item.get("desc") or item.get("content", "")
        if not title.startswith("策略"):
            title = f"{step_str}：{title}"
        cards.append(f"""<div class="p-6 rounded-2xl bg-[#fdfbf7] text-[#3c3935]">
    <h4 class="text-base font-bold text-[#ff641e] mb-2 flex items-center gap-2">
        <span>{title}</span>
    </h4>
    <p class="text-xs text-[#7a756f] leading-relaxed">{desc}</p>
</div>""")
    return "\n".join(cards)


def auto_expand_pure_data(data_dict):
    """检查并自动将所有纯数据字段转化为标准高保真卡片 HTML 片段"""
    # 1. 概览引导语
    if "OVERVIEW_DATA" in data_dict and not data_dict.get("SECTION_1_OVERVIEW"):
        data_dict["SECTION_1_OVERVIEW"] = generate_overview_html(data_dict["OVERVIEW_DATA"])
    elif "SECTION_1_OVERVIEW" in data_dict and "<p" not in str(data_dict["SECTION_1_OVERVIEW"]):
        data_dict["SECTION_1_OVERVIEW"] = generate_overview_html(data_dict["SECTION_1_OVERVIEW"])

    # 2. 注册信息表
    if "REGISTRATION_DATA" in data_dict and not data_dict.get("SECTION_1_REGISTRATION_TABLE"):
        data_dict["SECTION_1_REGISTRATION_TABLE"] = generate_registration_table_html(data_dict["REGISTRATION_DATA"])

    # 3. 品牌矩阵 8 宫格
    if "BRAND_MATRIX_DATA" in data_dict and not data_dict.get("SECTION_1_BRAND_MATRIX"):
        data_dict["SECTION_1_BRAND_MATRIX"] = generate_brand_matrix_html(data_dict["BRAND_MATRIX_DATA"])

    # 4. 发展历程时间线
    if "TIMELINE_DATA" in data_dict and not data_dict.get("SECTION_1_TIMELINE"):
        data_dict["SECTION_1_TIMELINE"] = generate_timeline_html(data_dict["TIMELINE_DATA"])

    # 5. 财务洞察卡片群
    if "FINANCE_INSIGHTS_DATA" in data_dict and not data_dict.get("SECTION_2_INSIGHTS"):
        data_dict["SECTION_2_INSIGHTS"] = generate_finance_insights_html(data_dict["FINANCE_INSIGHTS_DATA"])

    # 6. 渠道网络 2x2 网格
    if "CHANNELS_GRID_DATA" in data_dict and not data_dict.get("SECTION_3_CHANNEL_ANALYSIS"):
        data_dict["SECTION_3_CHANNEL_ANALYSIS"] = generate_channels_grid_html(data_dict["CHANNELS_GRID_DATA"])

    # 7. 竞争对手卡片
    if "COMPETITORS_DATA" in data_dict and not data_dict.get("SECTION_3_COMPETITION"):
        data_dict["SECTION_3_COMPETITION"] = generate_competitors_html(data_dict["COMPETITORS_DATA"])

    # 8. 品牌表格与供应链替代机会
    if "BRAND_TABLE_DATA" in data_dict and not data_dict.get("SECTION_4_BRAND_TABLE"):
        data_dict["SECTION_4_BRAND_TABLE"] = generate_brand_table_html(data_dict["BRAND_TABLE_DATA"])

    # 9. 代工贴牌商机
    if "OEM_OPPORTUNITY_DATA" in data_dict and not data_dict.get("SECTION_4_OEM_OPPORTUNITY"):
        data_dict["SECTION_4_OEM_OPPORTUNITY"] = generate_oem_opportunity_html(data_dict["OEM_OPPORTUNITY_DATA"])

    # 10. 采购决策链
    if "DECISION_CHAIN_DATA" in data_dict and not data_dict.get("SECTION_5_DECISION_CHAIN"):
        data_dict["SECTION_5_DECISION_CHAIN"] = generate_decision_chain_html(data_dict["DECISION_CHAIN_DATA"])

    # 11. 联系路径
    if "CONTACT_PATH_DATA" in data_dict and not data_dict.get("SECTION_5_CONTACT_PATH"):
        data_dict["SECTION_5_CONTACT_PATH"] = generate_contact_path_html(data_dict["CONTACT_PATH_DATA"])

    # 12. 供应链 4 步流程
    if "SUPPLY_FLOW_DATA" in data_dict and not data_dict.get("SECTION_6_PROCUREMENT"):
        data_dict["SECTION_6_PROCUREMENT"] = generate_supply_flow_html(data_dict["SUPPLY_FLOW_DATA"])

    # 13. 准入合规红线
    if "COMPLIANCE_DATA" in data_dict and not data_dict.get("SECTION_6_COMPLIANCE"):
        data_dict["SECTION_6_COMPLIANCE"] = generate_compliance_html(data_dict["COMPLIANCE_DATA"])

    # 14. 差评与设计痛点
    if "PAIN_POINTS_DATA" in data_dict and not data_dict.get("SECTION_7_PAIN_POINTS"):
        data_dict["SECTION_7_PAIN_POINTS"] = generate_pain_points_html(data_dict["PAIN_POINTS_DATA"])

    # 15. 社交媒体营销
    if "SOCIAL_MEDIA_DATA" in data_dict and not data_dict.get("SECTION_7_SOCIAL_MEDIA"):
        data_dict["SECTION_7_SOCIAL_MEDIA"] = generate_social_media_html(data_dict["SOCIAL_MEDIA_DATA"])

    # 16. 技术改进方案
    if "IMPROVEMENTS_DATA" in data_dict and not data_dict.get("SECTION_7_IMPROVEMENTS"):
        data_dict["SECTION_7_IMPROVEMENTS"] = generate_improvements_html(data_dict["IMPROVEMENTS_DATA"])

    # 17. 供应商实战策略卡片
    if "STRATEGIES_DATA" in data_dict and not data_dict.get("SECTION_8_STRATEGIES"):
        data_dict["SECTION_8_STRATEGIES"] = generate_strategies_html(data_dict["STRATEGIES_DATA"])

    # 18. 图表标题默认值兜底
    data_dict.setdefault("FINANCE_CHART1_TITLE", "营业收入与增长趋势")
    data_dict.setdefault("CHANNEL_CHART_TITLE", "业务业态与区域网络结构")
    data_dict.setdefault("SUPPLY_CHART_TITLE", "对华大宗商品采购估值与品类趋势")

    # 可选字段兜底（若未提供对应数据，自动置为空字符串以彻底消除占位符残留）
    optional_sections = [
        "SECTION_1_BRAND_MATRIX",
        "SECTION_6_LOGISTICS_TIP"
    ]
    for opt_sec in optional_sections:
        if opt_sec not in data_dict:
            data_dict[opt_sec] = ""

    return data_dict


# ==============================================================================
# 图片优化与 Google Flow 自动生图闭环
# ==============================================================================

def find_and_compress_banner(image_path_or_dir, company_name=None, max_width=1200, quality=82, allow_fallback=True):
    """搜索并等比压缩店面横幅图片为轻量 Base64 字符串"""
    target_img_path = None

    if os.path.isfile(image_path_or_dir):
        target_img_path = image_path_or_dir
    elif os.path.isdir(image_path_or_dir):
        candidates = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
            candidates.extend(glob.glob(os.path.join(image_path_or_dir, ext)))
        
        if not candidates:
            return ""

        if company_name:
            c_lower = company_name.lower().replace(" ", "").replace("_", "").replace("-", "")
            matched = [
                f for f in candidates 
                if c_lower in os.path.basename(f).lower().replace(" ", "").replace("_", "").replace("-", "")
            ]
            if matched:
                matched.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                target_img_path = matched[0]

        if not target_img_path and allow_fallback:
            candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            target_img_path = candidates[0]

    if not target_img_path or not os.path.exists(target_img_path):
        return ""

    print(f"[INFO] 锁定门店横幅图片: {target_img_path} (原始大小: {os.path.getsize(target_img_path)} 字节)")

    if HAS_PIL:
        try:
            im = Image.open(target_img_path).convert('RGB')
            if im.width > max_width:
                w = max_width
                h = int(im.height * (max_width / im.width))
                im = im.resize((w, h), Image.Resampling.LANCZOS)
            
            buf = io.BytesIO()
            im.save(buf, format='JPEG', quality=quality, optimize=True)
            compressed_data = buf.getvalue()
            print(f"[OK] 图像已优化压缩至: {len(compressed_data)} 字节")
            return "data:image/jpeg;base64," + base64.b64encode(compressed_data).decode('utf-8')
        except Exception as e:
            print(f"[WARN] PIL 压缩失败，降级为直读: {e}")

    with open(target_img_path, 'rb') as f:
        data = f.read()
    mime = "image/png" if target_img_path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(data).decode('utf-8')


def try_generate_banner_with_flow(company_name, country_name, output_dir=None, data_dict=None):
    """尝试通过本地已开启的 Google Flow CDP (127.0.0.1:9222) 自动生图"""
    print(f"\n[*] 正在启动本地 Google Flow 自动化生图引擎 (目标: {company_name})...")
    flow_script = os.path.join(SCRIPT_DIR, "flow_image_generator.py")
    if not os.path.exists(flow_script):
        print("[WARN] 未找到 flow_image_generator.py，跳过自动生图。")
        return ""

    out_dir = output_dir or os.getcwd()
    clean_name = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]', '_', company_name).strip('_')
    target_img = os.path.join(out_dir, f"{clean_name}_storefront.jpg")

    try:
        import asyncio
        import flow_image_generator

        # 1. 优先使用显式指定的 BANNER_PROMPT
        prompt = ""
        if data_dict and data_dict.get("BANNER_PROMPT"):
            prompt = str(data_dict.get("BANNER_PROMPT")).strip()

        # 2. 如果未指定，使用业态模板引擎结合产品/渠道上下文智能组装
        if not prompt:
            context_parts = []
            archetype = None
            if data_dict:
                archetype = data_dict.get("COMMERCIAL_TYPE") or data_dict.get("ARCHETYPE")
                for k in ["PRODUCTS", "CHANNELS", "INDUSTRY", "SUMMARY"]:
                    if data_dict.get(k):
                        context_parts.append(str(data_dict.get(k)))
            context_text = " ".join(context_parts)

            prompt = flow_image_generator.build_default_storefront_prompt(
                company_name=company_name,
                country=country_name,
                archetype=archetype,
                context_text=context_text
            )

        print(f"[INFO] 正在调用本地 Google Flow (127.0.0.1:9222) 生成图片...")
        print(f"[INFO] 提示词: {prompt[:100]}...")
        res = asyncio.run(flow_image_generator.generate_and_extract_flow_image(
            prompt=prompt,
            output_path=target_img,
            cdp_url="http://127.0.0.1:9222",
            wait_seconds=32
        ))
        if res.get("success") and os.path.exists(target_img):
            print(f"[SUCCESS] Google Flow 成功生成门店图: {target_img}")
            return target_img
    except Exception as e:
        print(f"[WARN] Google Flow 自动化生图未能完成: {e}")

    return ""


# ==============================================================================
# 报告构建主函数
# ==============================================================================

def build_html_from_data(data_dict, template_path=None, output_path=None, banner_path=None, auto_flow=False):
    """核心母版替换与自愈渲染函数"""
    if not template_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, "assets", "report-template.html")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"母版模板不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 1. 自动净化数据中的 Emoji 符号
    data_dict = sanitize_text(data_dict)

    # 2. 纯数据模式展开为高保真 HTML 片段
    data_dict = auto_expand_pure_data(data_dict)

    # 3. 规范化 Meta 元数据（去法律后缀、去 HTML 标签）
    company_name = data_dict.get('COMPANY_NAME', '').strip()
    data_dict['COMPANY_NAME'] = clean_legal_suffix(strip_html_tags(company_name))
    
    # 智能规范化 COMPETITORS（确保 4 段式管道：名称|国家|官网|【形态】品类与定位，便于平台精准裂变入库）
    if data_dict.get('COMPETITORS'):
        raw_comps = [c.strip() for c in data_dict['COMPETITORS'].split(',') if c.strip()]
        cleaned_comps = []
        comp_data_map = {}
        if data_dict.get('COMPETITORS_DATA') and isinstance(data_dict['COMPETITORS_DATA'], list):
            for cd in data_dict['COMPETITORS_DATA']:
                c_clean = clean_legal_suffix(cd.get('name', '')).lower()
                if c_clean:
                    comp_data_map[c_clean] = cd

        default_country = data_dict.get('REGIONS', '').split(',')[0].strip() or '全球'

        for c in raw_comps:
            parts = [p.strip() for p in c.split('|')]
            clean_cname = clean_legal_suffix(parts[0])
            matched_obj = comp_data_map.get(clean_cname.lower(), {})

            country = parts[1] if len(parts) > 1 and parts[1] else (matched_obj.get('country') or default_country)
            website = parts[2] if len(parts) > 2 and parts[2] else (matched_obj.get('website') or '')
            desc = parts[3] if len(parts) > 3 and parts[3] else (matched_obj.get('tag') or matched_obj.get('position') or '')

            cleaned_comps.append(f"{clean_cname}|{country}|{website}|{desc}")
        data_dict['COMPETITORS'] = ', '.join(cleaned_comps)
    elif data_dict.get('COMPETITORS_DATA') and isinstance(data_dict['COMPETITORS_DATA'], list):
        comp_pipes = []
        default_country = data_dict.get('REGIONS', '').split(',')[0].strip() or '全球'
        for cd in data_dict['COMPETITORS_DATA']:
            c_name = clean_legal_suffix(cd.get('name', ''))
            c_country = cd.get('country') or default_country
            c_web = cd.get('website', '')
            c_desc = cd.get('tag') or cd.get('position', '')
            if c_name:
                comp_pipes.append(f"{c_name}|{c_country}|{c_web}|{c_desc}")
        if comp_pipes:
            data_dict['COMPETITORS'] = ', '.join(comp_pipes)

    if data_dict.get('SUPPLIERS'):
        raw_sups = [clean_legal_suffix(s.strip()) for s in data_dict['SUPPLIERS'].split(',') if s.strip()]
        data_dict['SUPPLIERS'] = ', '.join(raw_sups)

    for meta_key in ['SUMMARY', 'PRODUCTS', 'REGIONS', 'CHANNELS', 'CUSTOMERS', 'SISTER_PARENTS']:
        if meta_key in data_dict and isinstance(data_dict[meta_key], str):
            data_dict[meta_key] = strip_html_tags(data_dict[meta_key])

    # 4. 判断是否具备实体门店 / 知名品牌展厅并处理横幅
    has_store_val = data_dict.get('HAS_PHYSICAL_STORE')
    if isinstance(has_store_val, bool):
        has_physical_store = has_store_val
    elif isinstance(has_store_val, str):
        has_physical_store = has_store_val.strip().lower() in ['true', '1', 'yes']
    elif 'BANNER_IMAGE_BASE64' in data_dict and data_dict['BANNER_IMAGE_BASE64']:
        has_physical_store = True
    elif banner_path or auto_flow or 'BANNER_ALT' in data_dict or 'BANNER_TITLE' in data_dict:
        has_physical_store = True
    else:
        has_physical_store = False

    if not has_physical_store:
        print("[INFO] 企业类型判定为无实体门店 (HAS_PHYSICAL_STORE=False)，自动跳过生图并剥离顶部店面横幅。")
        template = re.sub(
            r'<!-- ====== 店面横幅.*?<!-- ====== 吸顶标题栏 ====== -->',
            '<!-- ====== 吸顶标题栏 ====== -->',
            template,
            flags=re.DOTALL
        )
        for banner_k in ['BANNER_IMAGE_BASE64', 'BANNER_ALT', 'BANNER_LOCATION', 'BANNER_TITLE']:
            data_dict.pop(banner_k, None)
    else:
        # 处理横幅图片（支持优先本地匹配、传入路径、或调用 Google Flow 生成）
        if not data_dict.get('BANNER_IMAGE_BASE64'):
            b64_banner = ""
            if banner_path:
                b64_banner = find_and_compress_banner(banner_path, company_name, allow_fallback=True)
            if not b64_banner and output_path:
                out_dir = os.path.dirname(os.path.abspath(output_path))
                b64_banner = find_and_compress_banner(out_dir, company_name, allow_fallback=False)
            if not b64_banner:
                b64_banner = find_and_compress_banner(os.getcwd(), company_name, allow_fallback=False)

            # 若未找到且启用了 auto_flow，自动尝试本地生图
            if not b64_banner and auto_flow:
                country = data_dict.get('REGIONS', '').split(',')[0].strip()
                out_dir = os.path.dirname(os.path.abspath(output_path)) if output_path else os.getcwd()
                flow_img = try_generate_banner_with_flow(company_name, country, output_dir=out_dir, data_dict=data_dict)
                if flow_img:
                    b64_banner = find_and_compress_banner(flow_img, company_name, allow_fallback=True)

            # 最后兜底
            if not b64_banner:
                b64_banner = find_and_compress_banner(os.getcwd(), company_name, allow_fallback=True)

            if b64_banner:
                data_dict['BANNER_IMAGE_BASE64'] = b64_banner

    # 5. 替换模板占位符
    rendered = template
    for key, val in data_dict.items():
        placeholder = f"{{{{{key}}}}}"
        if isinstance(val, (dict, list)):
            val_str = json.dumps(val, ensure_ascii=False)
        else:
            val_str = str(val) if val is not None else ""
        rendered = rendered.replace(placeholder, val_str)

    leftovers = set(re.findall(r'\{\{[A-Z0-9_]+\}\}', rendered))
    if leftovers:
        print(f"[WARN] 存在未替换的模板占位符: {leftovers}")

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"[OK] 报告生成完成: {output_path} (大小: {os.path.getsize(output_path)} 字节)")

    return rendered


def complete_task(task_id, report_id, api_url="https://marketgraphic.cn", api_key="automation_agent_secret"):
    """向任务中心回写完成状态"""
    endpoint = f"{api_url.rstrip('/')}/api/agent/tasks/complete"
    payload = json.dumps({"task_id": task_id, "report_id": report_id}).encode('utf-8')
    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode('utf-8')
            res = json.loads(body)
            if res.get('success'):
                print(f"[OK] 任务中心回写成功 (Task ID: {task_id} -> Report ID: {report_id})")
                return True
            else:
                print(f"[WARN] 任务中心回写返回: {res.get('message') or res.get('error')}")
                return False
    except Exception as e:
        print(f"[ERR] 任务中心回写失败: {e}")
        return False


def run_pipeline(args):
    """执行一体化流水线（纯 Python 模块调用，无外部 subprocess 损耗）"""
    # 1. 加载数据
    if not os.path.exists(args.data):
        print(f"[ERROR] 数据文件不存在: {args.data}")
        sys.exit(1)

    with open(args.data, "r", encoding="utf-8") as f:
        data_dict = json.load(f)

    # 2. 如果指定了 target_id，注入 meta
    if args.target_id:
        data_dict['TARGET_REPORT_ID'] = args.target_id

    # 3. 渲染生成 HTML（含纯数据展开、自愈清洗及可选 auto-flow 生图）
    rendered_html = build_html_from_data(
        data_dict,
        template_path=args.template,
        output_path=args.output,
        banner_path=args.banner,
        auto_flow=args.auto_flow
    )

    # 4. 门禁审计校验
    if args.validate:
        if not HAS_VALIDATE:
            print("[WARN] 未找到 validate_insight 模块，跳过审计。")
        else:
            print("\n[*] 启动合规与品牌门禁审计...")
            success = validate_insight.validate_html(args.output)
            if not success:
                print("[ERROR] 门禁审计未通过，已阻断后续发布！")
                sys.exit(1)

    # 5. 发布至平台与图谱互联
    if args.publish:
        if not HAS_PUBLISH:
            print("[ERROR] 未找到 publish_report 模块，无法发布。")
            sys.exit(1)

        print("\n[*] 启动平台发布流水线...")
        success, report_id = publish_report.publish_report_file(
            args.output,
            target_url="https://marketgraphic.cn",
            api_key="automation_agent_secret",
            target_id=args.target_id
        )

        if not success or not report_id:
            print("[ERROR] 报告发布失败！")
            sys.exit(1)

        # 6. 如果携带 task_id，完成原子回写
        if args.task_id:
            print(f"\n[*] 正在向任务中心提交任务完成状态...")
            complete_task(args.task_id, report_id)

    # 7. 清理过程临时文件（默认开启或通过 --clean 控制，保持目录整洁，仅保留自包含 HTML 报告）
    if getattr(args, 'clean', True):
        print("\n[*] 正在清理构建过程中的临时文件，仅保留最终自包含 HTML 报告...")
        # 1) 清理数据 JSON
        if os.path.exists(args.data) and ("report_data" in args.data or "temp" in args.data or "scratch" in args.data):
            try:
                os.remove(args.data)
                print(f"  [CLEAN] 已删除临时数据文件: {args.data}")
            except Exception as e:
                print(f"  [WARN] 无法删除临时数据文件: {e}")

        # 2) 清理同级目录下生成的独立横幅图片（已完全内嵌为 Base64）
        if args.output:
            out_dir = os.path.dirname(os.path.abspath(args.output))
            for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
                for img_file in glob.glob(os.path.join(out_dir, ext)):
                    if "_storefront" in img_file or "banner" in img_file.lower():
                        try:
                            os.remove(img_file)
                            print(f"  [CLEAN] 已清理内嵌后冗余图片: {img_file}")
                        except Exception as e:
                            print(f"  [WARN] 无法清理图片文件: {e}")

        # 3) 清理 scratch 目录下的临时生成脚本
        scratch_dir = os.path.join(os.getcwd(), "scratch")
        if os.path.exists(scratch_dir):
            for scratch_f in glob.glob(os.path.join(scratch_dir, "generate_*_data.py")):
                try:
                    os.remove(scratch_f)
                    print(f"  [CLEAN] 已清理 scratch 临时脚本: {scratch_f}")
                except Exception:
                    pass


def cli_main():
    parser = argparse.ArgumentParser(description="Company Insight Pro 报告全自动构建流水线")
    parser.add_argument("--data", type=str, required=True, help="临时数据 JSON 文件路径")
    parser.add_argument("--template", type=str, help="HTML 母版路径（默认使用 assets/report-template.html）")
    parser.add_argument("--output", type=str, required=True, help="输出 HTML 路径")
    parser.add_argument("--banner", type=str, help="横幅图片文件路径或所在目录")
    parser.add_argument("--target-id", type=str, help="覆盖更新时的已有报告 ID")
    parser.add_argument("--auto-flow", action="store_true", help="若无横幅图则自动连接 Google Flow CDP (9222) 生图")
    parser.add_argument("--validate", action="store_true", help="构建后自动执行合规门禁审计")
    parser.add_argument("--publish", action="store_true", help="审计通过后自动发布到 GlobalTradeBuddy 平台")
    parser.add_argument("--task-id", type=str, help="发布成功后向任务中心回写的 task_id")
    parser.add_argument("--no-clean", dest="clean", action="store_false", default=True, help="保留过程临时文件（默认会自动清理）")

    args = parser.parse_args()
    run_pipeline(args)


if __name__ == "__main__":
    cli_main()
