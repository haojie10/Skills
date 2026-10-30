# -*- coding: utf-8 -*-
"""
Company Insight Pro - 前置查重门禁脚本 (check_report.py)
用于在调研前快速检索 GlobalTradeBuddy 平台报告库，避免重复调研已收录企业。
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error

# 强制 UTF-8 控制台输出，彻底杜绝 Windows GBK 编码崩溃
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def load_env(env_path):
    env_vars = {}
    if not os.path.exists(env_path):
        return env_vars
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, val = line.split('=', 1)
                env_vars[key.strip()] = val.strip()
    return env_vars


def find_and_load_env():
    cur = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.getcwd(), '.env'),
        r"d:\我的APP\Globaltradebuddy\.env"
    ]
    for _ in range(5):
        candidates.append(os.path.join(cur, '.env'))
        cur = os.path.dirname(cur)

    for p in candidates:
        if os.path.exists(p):
            return load_env(p)
    return {}


def clean_name_for_search(name):
    """去除公司名称中的法律后缀、常见行业通用词、多余标点和所有引号/撇号"""
    if not name:
        return ""
    # 移除常见法律后缀
    cleaned = re.sub(
        r'\b(AG|GmbH|LLC|Inc\.?|Ltd\.?|Corp\.?|PLC|SA|SAS|BV|SE|S\.A\.B\.|Co\.,\s*Ltd\.?|S\.p\.A\.|Pty\s*Ltd|Pty\s*Limited|Co\.?|Sp\.\s*z\s*o\.\s*o\.|Sp\s*z\s*o\s*o|Spzoo|Spolka\s*z\s*o\s*o|s\.r\.o\.|sro)\b',
        '',
        name,
        flags=re.IGNORECASE
    )
    # 移除撇号与所有引号（例如 Middy's -> Middys, Lowe's -> Lowes）
    cleaned = re.sub(r"['’`\"“”]", '', cleaned)
    # 移除多余标点和特殊符号
    cleaned = re.sub(r'[\(\)\[\]（）\-—_,\.&+/\\:]', ' ', cleaned).strip()
    return re.sub(r'\s+', ' ', cleaned)


def get_core_tokens(name):
    """获取过滤了通用行业词的核心单词列表"""
    cleaned = clean_name_for_search(name).lower()
    common_words = {
        'the', 'a', 'an', 'shop', 'shops', 'store', 'stores',
        'group', 'holding', 'holdings', 'international', 'global',
        'electrical', 'data', 'merchandising', 'wholesale', 'retail',
        'solutions', 'technologies', 'technology', 'electronics',
        'trading', 'distribution', 'distributors', 'distribuzione',
        'enterprise', 'enterprises', 'company', 'brothers', 'spa',
        'comercial', 'comercio', 'industrias', 'industria', 'sociedad',
        'importadora', 'exportadora', 'corporacion', 'distribuidora',
        'import', 'export', 'imports', 'exports', 'agency',
        'grosshandel', 'großhandel', 'handel', 'handelsgesellschaft',
        'bargain', 'outlet', 'outlets', 'store', 'stores', 'shop', 'shops', 'market', 'supermarket',
        'poland', 'polska', 'germany', 'deutschland', 'france', 'spain', 'espana', 'italy', 'italia',
        'china', 'usa', 'uk', 'netherlands', 'belgium', 'europe',
        '360°', '企业战略情报报告', '战略情报报告', '客户洞察', '深度研报'
    }
    tokens = [w for w in cleaned.split() if w not in common_words and len(w) > 1]
    return tokens, cleaned


def check_company_report(company_name, api_url=None, api_key=None):
    """
    检查平台是否已存在该公司的报告
    返回 (is_duplicate: bool, matched_report: dict or None)
    """
    env_vars = find_and_load_env()
    gtb_api_url = api_url or env_vars.get('GTB_API_URL', 'https://marketgraphic.cn')
    agent_api_key = api_key or env_vars.get('AGENT_API_KEY', 'automation_agent_secret')

    target_tokens, clean_target = get_core_tokens(company_name)
    if not clean_target or len(clean_target) < 2:
        return False, None

    all_reports = []
    page = 1
    target_category = 'customer'
    while True:
        url = f"{gtb_api_url.rstrip('/')}/api/agent/reports?page={page}&pageSize=200&category={target_category}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {agent_api_key}"})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                reports = data.get('reports', [])
                if not reports:
                    break
                all_reports.extend(reports)
                total = data.get('total', 0)
                if len(all_reports) >= total:
                    break
                page += 1
        except Exception as e:
            print(f"[WARN] 获取平台报告索引失败 (page {page}): {e}")
            break

    if not all_reports:
        return False, None

    # 精确匹配、双向包含与核心分词匹配（严格限制仅比对 customer 类型的企业客户报告）
    matched = None
    for r in all_reports:
        # 强安全隔离：非客户调研报告（如品类出海洞察 product 报告）坚决不参与企业查重！
        if r.get('category') and r.get('category') != target_category:
            continue
        title = (r.get('title') or '')
        if any(kw in title for kw in ['品类洞察', '品类调研', '研发升级方案', '渠道调研报告', '渠道深度调研报告', '渠道对比']):
            continue

        rep_company = (r.get('company_name') or '')
        
        # 1. 尝试比对已有报告标题与已有报告主体名
        candidates_to_check = [title, rep_company]
        
        for cand in candidates_to_check:
            if not cand:
                continue
            cand_tokens, cand_clean = get_core_tokens(cand)
            
            # 1.1 完全清洗后相等
            if clean_target == cand_clean:
                matched = r
                break
                
            # 1.2 目标包含已有标题/名称（短名命中长任务名，如已有 "Middys" -> 命中 "Middy's Data & Electrical"）
            if cand_clean and len(cand_clean) >= 3 and re.search(rf'\b{re.escape(cand_clean)}\b', clean_target, re.IGNORECASE):
                matched = r
                break
                
            # 1.3 已有标题包含目标名称（长已有报告命中短目标）
            if clean_target and len(clean_target) >= 3 and re.search(rf'\b{re.escape(clean_target)}\b', cand_clean, re.IGNORECASE):
                matched = r
                break
                
            # 1.4 核心词高重合匹配（如核心品牌词组高度重合）
            if target_tokens and cand_tokens:
                set_target = set(target_tokens)
                set_cand = set(cand_tokens)
                if set_target == set_cand:
                    matched = r
                    break
                if len(set_target) > 1 and len(set_cand) > 1:
                    inter = set_target.intersection(set_cand)
                    if len(inter) / max(len(set_target), len(set_cand)) >= 0.6:
                        matched = r
                        break
        
        if matched:
            break

    if matched:
        return True, matched
    return False, None


def main():
    parser = argparse.ArgumentParser(description="GlobalTradeBuddy 平台报告查重门禁脚本")
    parser.add_argument("--company", required=True, help="目标公司/品牌名称（如: Action, Screwfix, Todo Mundo）")
    parser.add_argument("--url", help="平台 API 地址（可选）")
    parser.add_argument("--key", help="Agent API 密钥（可选）")

    args = parser.parse_args()

    company = args.company.strip()
    print(f"[*] 正在查重目标公司: {company} ...")

    is_dup, report = check_company_report(company, api_url=args.url, api_key=args.key)

    if is_dup and report:
        rep_id = report.get('id')
        rep_title = report.get('title', '')
        rep_url = report.get('url') or f"https://marketgraphic.cn/reports/{rep_id}"
        rep_region = report.get('region') or report.get('country') or '未知'
        rep_date = report.get('createdAt') or report.get('publishedAt') or '近期'

        print("\n========================================================")
        print("[发现重复/已存在] 平台报告大厅中已收录该企业客户报告！")
        print(f"  • 报告标题: 《{rep_title}》")
        print(f"  • 报告 ID  : {rep_id}")
        print(f"  • 市场区域: {rep_region}")
        print(f"  • 发布时间: {rep_date}")
        print(f"  • 在线链接: {rep_url}")
        print("========================================================")
        print("\n[消歧警戒] 🚨 严禁单凭名称巧合直接跳过任务或错误覆盖！")
        print("          请依据《1.1 跨国实体消歧与批判性查重铁律》执行【官网域名 / 所属国家 / 主营品类】三要素批判性二次核查：")
        print("          • 域名同源或同跨国集团分支 ➔ 方可关联跳过或指定 --target-id 覆盖；")
        print(f"          • 独立撞名企业（不同域名/不同品类/不同国别） ➔ 一票否决重复判定，坚决新建独立研报并加注国别区分！\n")
        print(f"[提示] 若确认同源且需全面迭代升级，方可指定 --target-id {rep_id}；独立撞名企业请勿覆盖。\n")
        sys.exit(10)  # 退出码 10 表示查重命中（已存在）
    else:
        print("\n[无重复] 未发现目标公司已发布的战略情报报告，可安全新建。\n")
        sys.exit(0)  # 退出码 0 表示无重复（安全新建）


if __name__ == "__main__":
    main()
