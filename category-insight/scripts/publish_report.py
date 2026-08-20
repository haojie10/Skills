# -*- coding: utf-8 -*-
"""
Market Graphic / Category Insight Report Publisher
自动将 Base64 嵌入完成的自包含 HTML 洞察报告上传并发布至 GlobalTradeBuddy 平台。
内置前置体积防护与图片语法自愈校验。
"""

import os
import re
import sys
import json
import argparse
import urllib.request
import urllib.error

# 尝试导入 embed_images 模块以提供自愈与压缩能力
try:
    from embed_images import embed_images_in_html, sanitize_existing_base64
except ImportError:
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from embed_images import embed_images_in_html, sanitize_existing_base64
    except Exception:
        embed_images_in_html = None
        sanitize_existing_base64 = None

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
    match = re.search(r'<meta[^>]*?name=["\']{}["\'][^>]*?content=["\']([^"\']*)["\']'.format(name), html, re.IGNORECASE)
    if match:
        return match[1].strip()
    match_rev = re.search(r'<meta[^>]*?content=["\']([^"\']*)["\'][^>]*?name=["\']{}["\']'.format(name), html, re.IGNORECASE)
    if match_rev:
        return match_rev[1].strip()
    return ''

def publish_report_file(html_path, target_url=None, api_key=None):
    if not os.path.exists(html_path):
        print(f"[ERR] File not found: {html_path}")
        return False

    # 1. 前置健康自检与体积自愈防护
    file_size_kb = os.path.getsize(html_path) / 1024
    if file_size_kb > 1200 and embed_images_in_html:
        print(f"[INFO] HTML file size is large ({file_size_kb:.1f} KB). Running automatic optimization...")
        try:
            embed_images_in_html(html_path)
        except Exception as e:
            print(f"[WARN] Auto-optimization error: {e}")

    # 读取环境变量
    env_vars = find_and_load_env()
    
    gtb_api_url = target_url or env_vars.get('GTB_API_URL', 'https://marketgraphic.cn')
    agent_api_key = api_key or env_vars.get('AGENT_API_KEY', 'automation_agent_secret')

    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 清洗可能存在的重复 Base64 前缀
    if sanitize_existing_base64:
        html_content = sanitize_existing_base64(html_content)

    # 强制修正：category meta 必须为 "product"（服务端枚举校验）
    html_content = re.sub(
        r'(<meta\s+name=["\']category["\']\s+content=["\'])[^"\']*(["\'])',
        r'\g<1>product\2',
        html_content,
        flags=re.IGNORECASE
    )

    # 提取关键信息
    title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else os.path.basename(html_path)

    summary = extract_meta(html_content, 'summary')
    regions = extract_meta(html_content, 'regions')
    products = extract_meta(html_content, 'products')
    channels = extract_meta(html_content, 'channels')

    # 尝试进行 GTB 标准行业品类自动校验与校正
    try:
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        ref_xlsx = os.path.join(cur_dir, "..", "references", "GTB产品结构.xlsx")
        if os.path.exists(ref_xlsx):
            import openpyxl
            wb = openpyxl.load_workbook(ref_xlsx, data_only=True)
            ws = wb.active
            std_categories = set()
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and row[0]:
                    std_categories.add(str(row[0]).strip())
            
            if products:
                prod_list = [p.strip() for p in products.split(',') if p.strip()]
                invalid_prods = [p for p in prod_list if p not in std_categories]
                if invalid_prods:
                    print(f"[WARN] 检测到以下品类不符合 GTB 54个标准行业名称: {invalid_prods}")
                    print(f"       请确保使用 references/GTB产品结构.xlsx 中的标准行业名称！")
    except Exception as e:
        pass

    region_val = regions.split(',')[0].strip() if regions else "北美"
    country_val = regions.split(',')[0].strip() if regions else "美国"
    industry_val = products.split(',')[0].strip() if products else "家居日用品"

    payload = {
        "type": "report",
        "category": "product",
        "title": title,
        "summary": summary if summary else title,
        "contentHtml": html_content,
        "region": region_val,
        "country": country_val,
        "industry": industry_val,
        "tags": [p.strip() for p in products.split(',')] if products else ["品类洞察"]
    }

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

    final_kb = len(data) / 1024
    print(f"[INFO] Publishing report: {os.path.basename(html_path)} (Payload: {final_kb:.1f} KB)")
    print(f"[INFO] Target endpoint: {endpoint}")
    print(f"[INFO] Title: {title}")

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
        
        # 降级尝试本地开发环境
        if 'localhost' not in gtb_api_url and '127.0.0.1' not in gtb_api_url:
            local_url = "http://localhost:3000/api/agent/publish"
            print(f"[RETRY] Trying local endpoint: {local_url}")
            try:
                local_req = urllib.request.Request(
                    local_url,
                    data=data,
                    headers={
                        'Authorization': f'Bearer {agent_api_key}',
                        'Content-Type': 'application/json; charset=utf-8'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(local_req) as local_resp:
                    res = json.loads(local_resp.read().decode('utf-8'))
                    if res.get('success'):
                        print(f"[OK] Local fallback succeeded! ID: {res.get('reportId') or res.get('id')}")
                        return True
            except Exception as local_e:
                print(f"[ERR] Local retry also failed: {local_e}")

        return False
    except Exception as e:
        print(f"[ERR] Network or system error: {e}")
        return False

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Publish Category Insight HTML report to GlobalTradeBuddy platform.")
    parser.add_argument("html_path", help="Path to the generated HTML report file.")
    parser.add_argument("--url", help="Target API URL (optional)")
    parser.add_argument("--key", help="Agent API Key (optional)")

    args = parser.parse_args()
    success = publish_report_file(args.html_path, target_url=args.url, api_key=args.key)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
