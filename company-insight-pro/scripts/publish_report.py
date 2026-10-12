# -*- coding: utf-8 -*-
"""
Market Graphic / Company Insight Pro Report Publisher
自动将 Base64 嵌入完成的自包含 HTML 企业洞察报告上传并发布至 GlobalTradeBuddy 平台。
支持全新发布以及指定 target_report_id 的原地覆盖更新。
内置大体积 Base64 图片自动压缩与 HTTP 413 自愈重试机制。
"""

import os
import re
import sys
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

def extract_meta(html, name):
    match = re.search(r'<meta[^>]*?name=["\']{}["\'][^>]*?content=(["\'])(.*?)\1'.format(name), html, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(2).strip()
    match_rev = re.search(r'<meta[^>]*?content=(["\'])(.*?)\1[^>]*?name=["\']{}["\']'.format(name), html, re.IGNORECASE | re.DOTALL)
    if match_rev:
        return match_rev.group(2).strip()
    return ''

def auto_compress_html_images(html_content, max_width=1100, quality=75):
    """
    搜索 HTML 中的大体积 Base64 图片并自动在内存中压缩
    """
    if not HAS_PIL:
        return html_content

    def _replace_b64(match):
        mime = match.group(1)
        b64_str = match.group(2)
        if len(b64_str) < 150000: # 小于 150KB 就不压缩了
            return match.group(0)
        try:
            raw_bytes = base64.b64decode(b64_str)
            im = Image.open(io.BytesIO(raw_bytes)).convert('RGB')
            if im.width > max_width:
                w = max_width
                h = int(im.height * (max_width / im.width))
                im = im.resize((w, h), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format='JPEG', quality=quality, optimize=True)
            compressed_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            print(f"[INFO] 内存中自愈压缩图片: {len(b64_str)} -> {len(compressed_b64)} chars")
            return f"data:image/jpeg;base64,{compressed_b64}"
        except Exception as e:
            print(f"[WARN] 自愈压缩失败: {e}")
            return match.group(0)

    pattern = r'data:(image/[a-zA-Z0-9\+\-\.]+);base64,([A-Za-z0-9+/=]{1000,})'
    new_html = re.sub(pattern, _replace_b64, html_content)
    return new_html

def get_platform_reports_index(gtb_api_url, agent_api_key):
    """从平台获取所有已发布的报告列表"""
    all_reports = []
    page = 1
    while True:
        url = f"{gtb_api_url.rstrip('/')}/api/agent/reports?page={page}&pageSize=200"
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
    return all_reports

def auto_link_entities(html_content, gtb_api_url, agent_api_key):
    """
    自动识别报告中的竞争对手、核心供应商与关联企业，若平台已有收录则自动注入高亮超链接
    """
    competitors = extract_meta(html_content, 'competitors')
    suppliers = extract_meta(html_content, 'suppliers')
    sister_parents = extract_meta(html_content, 'sister_parents')

    entities = []
    for field in [competitors, suppliers, sister_parents]:
        if field:
            for e in field.split(','):
                e_clean = e.split('|')[0].strip()
                if e_clean:
                    entities.append(e_clean)

    if not entities:
        return html_content

    # 拆分 head 和 body，只在 body/main 内容中执行超链接注入，严禁触碰 head 与 meta 标签
    head_match = re.search(r'(<head.*?>.*?</head>)', html_content, re.IGNORECASE | re.DOTALL)
    if head_match:
        head_part = html_content[:head_match.end()]
        body_part = html_content[head_match.end():]
    else:
        head_part = ""
        body_part = html_content

    # 常见法律后缀和泛称黑名单，严禁作为独立实体词进行全网知识图谱互联
    LEGAL_STOPWORDS = {
        'ltd', 'inc', 'corp', 'llc', 'gmbh', 'ag', 'plc', 'sa', 'sas', 'bv',
        'se', 'co', 'group', 'company', 'holdings', 'holding', 'international'
    }

    # 去重
    unique_entities = list(dict.fromkeys(entities))
    reports_db = get_platform_reports_index(gtb_api_url, agent_api_key)
    if not reports_db:
        return html_content

    print(f"[INFO] 正在为 {len(unique_entities)} 个关联实体执行平台知识图谱自动互联...")
    linked_count = 0

    for entity in unique_entities:
        clean_word = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', entity).strip().lower()
        if len(clean_word) < 2 or clean_word in LEGAL_STOPWORDS:
            continue
        c_lower = entity.lower()
        # 匹配对应报告
        matched = None
        for r in reports_db:
            title = (r.get('title') or '').lower()
            # 严格使用单词边界匹配，避免短词（如 Ara）误匹配到包含该子串的无关名称（如 Kiara）
            if re.search(rf'(?<![a-zA-Z0-9]){re.escape(c_lower)}(?![a-zA-Z0-9])', title):
                matched = r
                break
        
        if matched:
            rep_id = matched['id']
            rep_url = matched.get('url') or f"https://marketgraphic.cn/reports/{rep_id}"
            rep_title = matched.get('title', '')
            
            # 如果 body 中已经包含了该链接，则无需再自动替换
            if rep_id in body_part or rep_url in body_part:
                continue

            link_html = f'<a href="{rep_url}" target="_blank" rel="noopener noreferrer" class="text-[#ff641e] hover:underline font-semibold inline-flex items-center gap-0.5" title="点击查阅平台已收录报告：《{rep_title}》">{entity} <i data-lucide="external-link" size="11" class="inline opacity-80"></i></a>'
            
            # 智能 HTML 文本节点切分替换，确保只在纯文本中替换，且不破坏现有 <a> / <script> / <style> 标签
            tokens = re.split(r'(<[^>]+>)', body_part)
            in_skip_tag = 0
            linked_for_this_entity = 0

            for i in range(len(tokens)):
                token = tokens[i]
                if token.startswith('<'):
                    tag_match = re.match(r'<(/)?([a-zA-Z0-9]+)', token)
                    if tag_match:
                        is_closing = bool(tag_match.group(1))
                        tag_name = tag_match.group(2).lower()
                        if tag_name in ['a', 'script', 'style', 'button']:
                            if is_closing:
                                in_skip_tag = max(0, in_skip_tag - 1)
                            else:
                                in_skip_tag += 1
                else:
                    if in_skip_tag == 0 and linked_for_this_entity < 2:
                        # 在纯文本节点中精确匹配实体（支持单词边界及中英文紧邻）
                        p = rf'(?<![a-zA-Z0-9]){re.escape(entity)}(?![a-zA-Z0-9])'
                        if re.search(p, token):
                            tokens[i] = re.sub(p, link_html, token, count=1)
                            linked_for_this_entity += 1
                            linked_count += 1
                            print(f"  [OK] 成功互联实体: [{entity}] -> 《{rep_title}》")

            body_part = ''.join(tokens)

    if linked_count > 0:
        print(f"[INFO] 知识图谱互联完成，共成功注入 {linked_count} 个互联跳转锚点。")
    return head_part + body_part

def publish_report_file(html_path, target_url=None, api_key=None, target_id=None):
    if not os.path.exists(html_path):
        print(f"[ERR] File not found: {html_path}")
        return False, None

    env_vars = find_and_load_env()
    gtb_api_url = target_url or env_vars.get('GTB_API_URL', 'https://marketgraphic.cn')
    agent_api_key = api_key or env_vars.get('AGENT_API_KEY', 'automation_agent_secret')

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 1. 自动执行关联企业与竞品的知识图谱超链接注入
    html_content = auto_link_entities(html_content, gtb_api_url, agent_api_key)

    # 2. 如果文件体积预估大于 850KB，预先进行内存自愈压缩
    if len(html_content.encode('utf-8')) > 850 * 1024:
        print(f"[INFO] 检测到 HTML 文件较大 ({len(html_content)} chars)，正在自动优化图片体积...")
        html_content = auto_compress_html_images(html_content)

    # 回写本地文件保持一致
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else os.path.basename(html_path)

    summary = extract_meta(html_content, 'summary')
    regions = extract_meta(html_content, 'regions')
    products = extract_meta(html_content, 'products')
    company_name = extract_meta(html_content, 'company_name')
    meta_target_id = extract_meta(html_content, 'target_report_id')

    final_target_id = (target_id or meta_target_id or '').strip()

    # 强制修正：企业洞察 category meta 必须为 "customer"
    html_content = re.sub(
        r'(<meta\s+name=["\']category["\']\s+content=["\'])[^"\']*(["\'])',
        r'\g<1>customer\2',
        html_content,
        flags=re.IGNORECASE
    )

    region_val = regions.split(',')[0].strip() if regions else "欧洲"
    country_val = regions.split(',')[0].strip() if regions else "欧洲"
    industry_val = products.split(',')[0].strip() if products else "综合零售"

    payload = {
        "type": "report",
        "category": "customer",
        "title": title,
        "summary": summary if summary else title,
        "contentHtml": html_content,
        "region": region_val,
        "country": country_val,
        "industry": industry_val,
        "tags": [p.strip() for p in products.split(',')] if products else ["企业洞察"]
    }

    if final_target_id:
        payload["target_report_id"] = final_target_id
        print(f"[INFO] 🎯 启用目标报告覆盖模式，指定 Report ID: {final_target_id}")

    endpoint = f"{gtb_api_url.rstrip('/')}/api/agent/publish"
    data = json.dumps(payload).encode('utf-8')

    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            'Authorization': f'Bearer {agent_api_key}',
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )

    print(f"[INFO] Publishing company insight report: {os.path.basename(html_path)}")
    print(f"[INFO] Target endpoint: {endpoint}")
    print(f"[INFO] Company: {company_name or 'N/A'}, Title: {title}")

    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode('utf-8')
            res = json.loads(resp_body)
            if res.get('success'):
                report_id = res.get('reportId') or res.get('id') or 'N/A'
                print(f"[OK] Report published successfully! ID: {report_id}")
                print(f"[OK] Online URL: https://marketgraphic.cn/reports/{report_id}")
                return True, report_id
            else:
                print(f"[ERR] Failed to publish: {res.get('error')}")
                return False, None
    except urllib.error.HTTPError as e:
        if e.code == 413:
            print("[WARN] 触发 HTTP 413 (Entity Too Large)，启动深度自愈压缩重试...")
            compressed_html = auto_compress_html_images(html_content, max_width=960, quality=65)
            payload["contentHtml"] = compressed_html
            retry_data = json.dumps(payload).encode('utf-8')
            retry_req = urllib.request.Request(
                endpoint,
                data=retry_data,
                headers={
                    'Authorization': f'Bearer {agent_api_key}',
                    'Content-Type': 'application/json; charset=utf-8'
                },
                method='POST'
            )
            try:
                with urllib.request.urlopen(retry_req) as resp:
                    res = json.loads(resp.read().decode('utf-8'))
                    if res.get('success'):
                        report_id = res.get('reportId') or res.get('id') or 'N/A'
                        print(f"[OK] 自愈重试发布成功！ID: {report_id}")
                        return True, report_id
            except Exception as re_e:
                print(f"[ERR] 重试发布仍失败: {re_e}")
                return False, None

        err_msg = e.read().decode('utf-8') if e.fp else str(e)
        print(f"[ERR] HTTP {e.code} Error during upload: {err_msg}")
        return False, None
    except Exception as e:
        print(f"[ERR] Network or system error: {e}")
        return False, None

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Publish Company Insight HTML report to GlobalTradeBuddy platform.")
    parser.add_argument("html_path", help="Path to the generated HTML report file.")
    parser.add_argument("--url", help="Target API URL (optional)")
    parser.add_argument("--key", help="Agent API Key (optional)")
    parser.add_argument("--target-id", help="Target Report ID to overwrite (optional, for updating existing reports)")

    args = parser.parse_args()
    success, report_id = publish_report_file(args.html_path, target_url=args.url, api_key=args.key, target_id=args.target_id)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
