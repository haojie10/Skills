# -*- coding: utf-8 -*-
"""
company-insight-pro / build_report.py
全自动流水线脚本：
1. 智能模糊匹配最新横幅图片并自动压缩（<=1200px, JPEG质量优化, Base64编码，彻底杜绝 HTTP 413）
2. 基于母版 report-template.html 渲染标准报告
3. 自动执行 validate_insight.py 门禁校验
4. 自动调用 publish_report.py 上传至平台
5. 若携带 task_id，自动向云端任务中心回写完成状态
"""

import os
import re
import sys
import glob
import io
import json
import base64
import argparse
import subprocess
import urllib.request
import urllib.error

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def find_and_compress_banner(image_path_or_dir, company_name=None, max_width=1200, quality=82):
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

        if not target_img_path:
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


def build_html_from_data(data_dict, template_path=None, output_path=None):
    if not template_path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, "assets", "report-template.html")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"母版模板不存在: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    rendered = template
    for key, val in data_dict.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(val))

    leftovers = set(re.findall(r'\{\{[A-Z0-9_]+\}\}', rendered))
    if leftovers:
        print(f"[WARN] 存在未替换的占位符: {leftovers}")

    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        print(f"[OK] 报告生成完成: {output_path} (大小: {os.path.getsize(output_path)} 字节)")

    return rendered


def complete_task(task_id, report_id, api_url="https://marketgraphic.cn", api_key="automation_agent_secret"):
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
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode('utf-8')
            res = json.loads(body)
            if res.get('success'):
                print(f"[OK] 任务中心回写成功 (Task: {task_id}, Report: {report_id})")
                return True
            else:
                print(f"[WARN] 任务中心回写返回: {res.get('message') or res.get('error')}")
                return False
    except Exception as e:
        print(f"[ERR] 任务中心回写失败: {e}")
        return False
