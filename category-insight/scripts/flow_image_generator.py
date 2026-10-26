# -*- coding: utf-8 -*-
"""
Google Flow 生图适配器 (flow_image_generator.py)
在 macOS 环境下自动委托并执行原生的 Node.js AppleScript/Chrome 自动化生图驱动 (google_flow_native.js)，
无需启动 Playwright 调试端口或单独配置 CDP，完美适配本地 Chrome。

支持功能：
1. 命令行调用：python flow_image_generator.py <prompt> <output_path>
2. Python API 异步调用：await generate_single_image(prompt, output_path)
3. 序列化串行生图：await generate_images_sequence(items)
4. 支持自动调用 embed_images 中的 PIL 等比压缩与体积优化
"""

import os
import sys
import time
import subprocess
import asyncio
from io import BytesIO

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MAC_NATIVE_SCRIPT = os.path.join(CURRENT_DIR, "google_flow_native.js")


def compress_image_to_jpeg(image_path: str, max_width: int = 900, quality: int = 82) -> bool:
    """若存在 PIL，对落盘图片进行等比缩放与 JPEG 质量压缩，严格控制体积"""
    if not HAS_PIL or not os.path.exists(image_path):
        return False
    try:
        im = Image.open(image_path).convert("RGB")
        if im.width > max_width:
            w = max_width
            h = int(im.height * (max_width / im.width))
            im = im.resize((w, h), Image.Resampling.LANCZOS)
        im.save(image_path, format="JPEG", quality=quality, optimize=True)
        return True
    except Exception as e:
        print(f"[WARN] PIL 压缩异常: {e}")
        return False


def run_mac_native_flow(prompt: str, output_path: str, timeout_seconds: int = 120) -> bool:
    """调用 macOS 专属 google_flow_native.js 执行生图"""
    if not os.path.exists(MAC_NATIVE_SCRIPT):
        raise FileNotFoundError(f"未找到 macOS 专用脚本: {MAC_NATIVE_SCRIPT}")

    cmd = [
        "node",
        MAC_NATIVE_SCRIPT,
        "--prompt", prompt,
        "-o", output_path,
        "--timeout", str(timeout_seconds * 1000)
    ]

    print(f"[FlowEngine:Mac] 启动 macOS 原生 Flow 驱动: {output_path}")
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        if res.stderr:
            print(f"[FlowEngine:Mac] 错误输出: {res.stderr.strip()}", file=sys.stderr)
        return False

    if not os.path.exists(output_path) or os.path.getsize(output_path) < 1024:
        print(f"[FlowEngine:Mac] 输出文件异常或不存在: {output_path}", file=sys.stderr)
        return False

    # PIL 进一步优化压缩与规范化尺寸
    compress_image_to_jpeg(output_path)
    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"[FlowEngine:Mac] [OK] 生图成功落盘: {output_path} ({file_size_kb:.1f} KB)")
    return True


async def generate_single_image(
    prompt: str,
    output_path: str,
    cdp_url: str = "http://127.0.0.1:9222",
    max_wait_seconds: int = 120,
    max_width: int = 900,
    quality: int = 82
) -> bool:
    """
    单张阻塞式生图接口（与原 Python 接口完全保持兼容）
    """
    loop = asyncio.get_event_loop()
    success = await loop.run_in_executor(
        None,
        run_mac_native_flow,
        prompt,
        output_path,
        max_wait_seconds
    )
    if not success:
        raise RuntimeError(f"Google Flow 生图失败: {output_path}")

    # 冷却 3 秒，防止连续打扰界面
    await asyncio.sleep(3)
    return True


async def generate_images_sequence(items: list, cdp_url: str = "http://127.0.0.1:9222") -> bool:
    """
    严格按顺序逐张生成图片列表：
    items = [{"id": "hero", "prompt": "...", "output": "path.jpg"}, ...]
    """
    for idx, item in enumerate(items):
        print(f"\n========================================================")
        print(f"[任务 {idx+1}/{len(items)}] 开始生成: {item.get('id', '')} - {item.get('name', '')}")
        print(f"输出路径: {item['output']}")
        print(f"========================================================")

        success = False
        for attempt in range(1, 4):
            try:
                success = await generate_single_image(
                    prompt=item["prompt"],
                    output_path=item["output"]
                )
                if success:
                    break
            except Exception as e:
                print(f"[FlowEngine:Mac] [WARN] 第 {idx+1} 张第 {attempt} 次生成异常: {e}")
                await asyncio.sleep(4)

        if not success:
            raise RuntimeError(f"第 {idx+1} 张图片生成失败，流程中止")

    print("\n[FlowEngine:Mac] [ALL SUCCESS] 全部序列图片已生成并压缩完毕！")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python flow_image_generator.py <prompt> <output_path>")
        sys.exit(1)
    prompt_arg = sys.argv[1]
    output_arg = sys.argv[2]
    asyncio.run(generate_single_image(prompt_arg, output_arg))
