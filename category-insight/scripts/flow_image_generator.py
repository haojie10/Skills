# -*- coding: utf-8 -*-
"""
Google Flow 官方标准生图引擎 (flow_image_generator.py)
用于 category-insight 技能的可靠生图与无损原图拉取。

【核心工作模式】：
严格单张阻塞式串行执行：
[输入 Prompt] -> [提交生成] -> [阻塞等待云端渲染完成 (naturalWidth>=1000 & complete)] -> 
[直接 HTTP 拉取无损原图流] -> [PIL 高质量等比压缩落盘] -> [落盘校验通过] -> [冷却 3 秒] -> [允许下一张]
"""

import os
import sys
import time
import asyncio
from io import BytesIO
from PIL import Image
from playwright.async_api import async_playwright

def compress_image_to_jpeg(image_bytes: bytes, max_width: int = 900, quality: int = 82) -> bytes:
    """
    高质量等比压缩图片为 JPEG 格式
    """
    im = Image.open(BytesIO(image_bytes)).convert("RGB")
    if im.width > max_width:
        w = max_width
        h = int(im.height * (max_width / im.width))
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()

async def get_flow_page(context):
    """
    在已连接的 Chrome CDP 实例中寻找 Google Flow 标签页
    """
    for pg in context.pages:
        if "flow.google.com" in pg.url:
            return pg
    return None

async def get_rendered_image_urls(page) -> set:
    """
    获取 Flow 页面上所有已完全渲染成功的高清大图 URL (naturalWidth >= 500 且 complete)
    """
    return set(await page.evaluate('''() => {
        return Array.from(document.querySelectorAll('img'))
            .filter(i => {
                const src = i.src || '';
                return src.startsWith('http') 
                    && !src.includes('avatar') 
                    && !src.includes('googleusercontent.com/ogw')
                    && !src.includes('favicon')
                    && i.complete 
                    && i.naturalWidth >= 500;
            })
            .map(i => i.src);
    }'''))

async def generate_single_image(
    prompt: str,
    output_path: str,
    cdp_url: str = "http://127.0.0.1:9222",
    max_wait_seconds: int = 90,
    max_width: int = 900,
    quality: int = 82
) -> bool:
    """
    单张阻塞式生图：生成完毕并保存落盘后才返回 True
    """
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_url)
        context = browser.contexts[0]
        page = await get_flow_page(context)
        if not page:
            raise RuntimeError("未在 Chrome CDP 中检测到 Google Flow 页面 (https://flow.google.com)")

        await page.bring_to_front()
        await asyncio.sleep(0.5)

        # 1. 记录当前已有的大图 URL 快照
        before_urls = await get_rendered_image_urls(page)
        print(f"[FlowEngine] 开始生成前已存在 {len(before_urls)} 张高清大图")

        # 2. 清空并写入新的 Prompt
        await page.evaluate('''() => {
            const el = document.querySelector("div.ProseMirror");
            if (el) {
                el.focus();
                document.execCommand("selectAll", false, null);
                document.execCommand("delete", false, null);
            }
        }''')
        await asyncio.sleep(0.3)

        p_esc = prompt.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ')
        await page.evaluate(f'''() => {{
            const el = document.querySelector("div.ProseMirror");
            if (el) {{
                el.focus();
                document.execCommand("insertText", false, "{p_esc}");
            }}
        }}''')
        await asyncio.sleep(0.5)

        # 3. 提交生成指令
        gen_btn = await page.query_selector('button[aria-label="开始生成"], button[aria-label="Start generation"]')
        if gen_btn:
            await gen_btn.click()
            print("[FlowEngine] 点击生成按钮 (Start generation)")
        else:
            await page.keyboard.press('Enter')
            print("[FlowEngine] 按下 Enter 提交生成")

        # 4. 阻塞轮询，直到检测到全新且已完整渲染的大图 URL
        print(f"[FlowEngine] 等待云端生成与渲染完成 (最多 {max_wait_seconds} 秒)...")
        start_time = time.time()
        new_url = None

        while time.time() - start_time < max_wait_seconds:
            await asyncio.sleep(3)
            elapsed = int(time.time() - start_time)
            current_urls = await get_rendered_image_urls(page)
            diff = current_urls - before_urls
            if diff:
                new_url = list(diff)[0]
                print(f"[FlowEngine] 第 {elapsed} 秒成功捕获到全新渲染大图 URL: {new_url[:70]}...")
                # 额外等待 2 秒确保流传输完全稳定
                await asyncio.sleep(2)
                break
            print(f"[FlowEngine] 正在渲染中... ({elapsed}s)")

        if not new_url:
            raise TimeoutError(f"Flow 生成超时 ({max_wait_seconds}s)，未能捕获到新生成的高清原图！")

        # 5. 通过网络层直接下载原图二进制流
        resp = await context.request.get(new_url)
        if resp.status != 200:
            raise RuntimeError(f"下载原图失败，HTTP 状态码: {resp.status}")
        
        raw_bytes = await resp.body()
        if len(raw_bytes) < 10240:
            raise ValueError(f"下载的原图字节异常过小 ({len(raw_bytes)} 字节)，可能非有效图片！")

        print(f"[FlowEngine] 成功拉取无损原图流: {len(raw_bytes)/1024:.1f} KB")

        # 6. PIL 高质量等比压缩与落盘
        comp_bytes = compress_image_to_jpeg(raw_bytes, max_width=max_width, quality=quality)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(comp_bytes)

        # 7. 终检磁盘文件
        im = Image.open(output_path)
        print(f"[FlowEngine] [OK] 图片成功落盘: {output_path} (尺寸: {im.size}, 大小: {len(comp_bytes)/1024:.1f} KB)")
        
        # 8. 单张完成后执行 3 秒冷却，为下一次调用提供干净的上下文
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
                    output_path=item["output"],
                    cdp_url=cdp_url
                )
                if success:
                    break
            except Exception as e:
                print(f"[FlowEngine] [WARN] 第 {idx+1} 张第 {attempt} 次生成异常: {e}")
                await asyncio.sleep(4)

        if not success:
            raise RuntimeError(f"第 {idx+1} 张图片生成失败，流程中止")

    print("\n[FlowEngine] [ALL SUCCESS] 全部序列图片已严格按顺序生成并落盘完毕！")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python flow_image_generator.py <prompt> <output_path>")
        sys.exit(1)
    prompt_arg = sys.argv[1]
    output_arg = sys.argv[2]
    asyncio.run(generate_single_image(prompt_arg, output_arg))
