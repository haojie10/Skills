# -*- coding: utf-8 -*-
"""
Market Graphic / Company Insight Pro Report Publisher
自动将 Base64 嵌入完成的自包含 HTML 企业洞察报告上传并发布至 GlobalTradeBuddy 平台。
支持全新发布以及指定 target_report_id 的原地覆盖更新。
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error

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

def publish_report_file(html_path, target_url=None, api_key=None, target_id=None):
    if not os.path.exists(html_path):
        print(f"[ERR] File not found: {html_path}")
        return False

    env_vars = find_and_load_env()
    gtb_api_url = target_url or env_vars.get('GTB_API_URL', 'https://marketgraphic.cn')
    agent_api_key = api_key or env_vars.get('AGENT_API_KEY', 'automation_agent_secret')

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

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
                return True
            else:
                print(f"[ERR] Failed to publish: {res.get('error')}")
                return False
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8') if e.fp else str(e)
        print(f"[ERR] HTTP {e.code} Error during upload: {err_msg}")
        return False
    except Exception as e:
        print(f"[ERR] Network or system error: {e}")
        return False

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Publish Company Insight HTML report to GlobalTradeBuddy platform.")
    parser.add_argument("html_path", help="Path to the generated HTML report file.")
    parser.add_argument("--url", help="Target API URL (optional)")
    parser.add_argument("--key", help="Agent API Key (optional)")
    parser.add_argument("--target-id", help="Target Report ID to overwrite (optional, for updating existing reports)")

    args = parser.parse_args()
    success = publish_report_file(args.html_path, target_url=args.url, api_key=args.key, target_id=args.target_id)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
