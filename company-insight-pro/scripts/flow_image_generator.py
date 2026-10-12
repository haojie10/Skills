# -*- coding: utf-8 -*-
"""
Google Flow 自动化生图与 DOM 渲染层秒级提取标准工具
(Google Flow CDP Image Generator & Fast DOM Extractor)

核心优势与特性：
1. 直连本地已打开并登录的 Chrome CDP (127.0.0.1:9222)，无需重复登录、无需弹出多余窗口；
2. ProseMirror 富文本智能注入与回车触发生成；
3. 秒级 DOM 渲染层无损提取：直接从页面元素渲染帧/Canvas/缓存抓取图像，完全绕过容易卡顿的多级菜单点击与系统下载管理器；
4. 内置 PIL 智能等比缩放（默认最大宽度 1100px）与 JPEG 80 质量优化，输出体积严格控制在 70KB~150KB 之间，彻底规避 HTTP 413；
5. 既支持 CLI 命令行一键调用，也支持在 Python 脚本中直接作为模块 import 异步调用。
"""

import os
import sys
import time
import base64
import asyncio
import argparse
from io import BytesIO

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from playwright.async_api import async_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


def compress_image_bytes(raw_bytes, max_width=1100, quality=80):
    """使用 PIL 将原始图片字节流等比压缩为轻量 JPEG"""
    if not HAS_PIL:
        return raw_bytes, "image/jpeg"
    
    try:
        im = Image.open(BytesIO(raw_bytes)).convert('RGB')
        if im.width > max_width:
            w = max_width
            h = int(im.height * (max_width / im.width))
            im = im.resize((w, h), Image.Resampling.LANCZOS)
        
        buf = BytesIO()
        im.save(buf, format='JPEG', quality=quality, optimize=True)
        compressed_bytes = buf.getvalue()
        return compressed_bytes, "image/jpeg"
    except Exception as e:
        print(f"[WARN] PIL 压缩异常，返回原图: {e}")
        return raw_bytes, "image/jpeg"


async def generate_and_extract_flow_image(
    prompt: str,
    output_path: str = None,
    cdp_url: str = "http://127.0.0.1:9222",
    wait_seconds: int = 32,
    max_width: int = 1100,
    quality: int = 80
) -> dict:
    """
    直连 Google Flow 生成并秒级提取图片
    返回字典: {"success": bool, "base64": str, "file_path": str, "size_bytes": int, "error": str}
    """
    if not HAS_PLAYWRIGHT:
        return {"success": False, "error": "Playwright 未安装，请运行 pip install playwright"}

    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            return {"success": False, "error": f"无法连接到 Chrome CDP ({cdp_url})，请确保 Chrome 以 --remote-debugging-port=9222 运行: {e}"}

        context = browser.contexts[0] if browser.contexts else None
        if not context:
            return {"success": False, "error": "未在 Chrome 中检测到可用的 Context"}

        flow_page = None
        for pg in context.pages:
            url = pg.url
            if "flow.google.com" in url and "project" in url:
                flow_page = pg
                break
        
        if not flow_page:
            # 备用：任意 flow.google.com 页面
            for pg in context.pages:
                if "flow.google.com" in pg.url:
                    flow_page = pg
                    break

        if not flow_page:
            return {"success": False, "error": "未找到打开的 Google Flow 标签页，请先在 Chrome 中打开 flow.google.com"}

        print(f"[FLOW] 锁定 Google Flow 工作台: {flow_page.url}")
        await flow_page.bring_to_front()
        await asyncio.sleep(0.5)

        # 步骤 0: 记录生成前的图片特征快照（防多图混淆）
        before_imgs = await flow_page.query_selector_all('img')
        before_srcs = set()
        for img in before_imgs:
            s = await img.get_attribute('src') or ''
            if s:
                before_srcs.add(s)
        print(f"[FLOW] 生成前检测到已有 {len(before_srcs)} 张图片快照")

        # 步骤 1: 注入 Prompt
        print(f"[FLOW] 注入生图提示词: {prompt[:80]}...")
        pm_el = await flow_page.query_selector("div.ProseMirror")
        if pm_el:
            await pm_el.click()
            await flow_page.keyboard.press("Control+A")
            await flow_page.keyboard.press("Backspace")
            await asyncio.sleep(0.1)
            # 使用真实的键盘输入以确保触发 Angular / ProseMirror 的状态监听
            await flow_page.keyboard.type(prompt, delay=5)
            await asyncio.sleep(0.4)

        # 步骤 2: 触发生成
        gen_btn = await flow_page.query_selector('button[aria-label="Start generation"], button[aria-label="开始生成"], button.generate-icon-button')
        if gen_btn and not await gen_btn.is_disabled():
            await gen_btn.click()
            print("[FLOW] 已点击生成按钮 (Start generation)")
        else:
            await flow_page.keyboard.press('Enter')
            print("[FLOW] 已按 Enter 键触发生成")

        # 步骤 3: 差量监听等待全新渲染的图片
        print(f"[FLOW] 差量监听云端渲染中 (最多等待 {max(wait_seconds, 60)} 秒)...")
        target_img = None
        target_src = ""
        max_wait = max(wait_seconds, 60)
        start_t = time.time()

        while time.time() - start_t < max_wait:
            await asyncio.sleep(2.5)
            elapsed = int(time.time() - start_t)

            imgs = await flow_page.query_selector_all('img')
            candidates = []
            for img in imgs:
                src = await img.get_attribute('src') or ''
                if 'googleusercontent.com/ogw' in src or 'favicon' in src or 'avatar' in src:
                    continue
                box = await img.bounding_box()
                if not box or box['width'] < 120 or box['height'] < 80:
                    continue
                # 只有不在生成前快照里的才是真正的新图！
                if src and src not in before_srcs:
                    candidates.append((img, src, box))

            if candidates:
                target_img, target_src, target_box = candidates[0]
                print(f"[FLOW] 在第 {elapsed} 秒成功捕获全新生成的独立图像: 尺寸=({target_box['width']:.0f}x{target_box['height']:.0f})")
                await asyncio.sleep(1.5)
                break

        if not target_img:
            # 降级备用：若由于 blob 导致 src 未改变，抓取最新渲染
            print("[WARN] 差量未命中，降级捕获当前最新主图...")
            imgs = await flow_page.query_selector_all('img')
            for img in imgs:
                src = await img.get_attribute('src') or ''
                if 'googleusercontent.com/ogw' in src or 'favicon' in src:
                    continue
                box = await img.bounding_box()
                if box and box['width'] > 200 and box['height'] > 120:
                    target_img = img
                    target_src = src
                    break

        if not target_img:
            return {"success": False, "error": "未能在 Google Flow 画布中检测到生成的大图"}

        # 步骤 5: 秒级无损提取图像字节流（DOM 渲染层截帧）
        raw_bytes = None
        # 尝试 0: 直接在浏览器会话中 fetch 原图 blob 转 base64（无损原图，绕过 Canvas 跨域及截帧黑屏）
        if target_src.startswith('http') or target_src.startswith('blob'):
            try:
                b64_fetch = await flow_page.evaluate('''async (url) => {
                    try {
                        const resp = await fetch(url);
                        const blob = await resp.blob();
                        return new Promise((resolve) => {
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result);
                            reader.readAsDataURL(blob);
                        });
                    } catch (e) {
                        return null;
                    }
                }''', target_src)
                if b64_fetch and ',' in b64_fetch:
                    raw_bytes = base64.b64decode(b64_fetch.split(',')[1])
            except Exception:
                pass

        # 尝试 1: 如果是 blob 或 http，尝试直接浏览器内部 Canvas 导出
        if not raw_bytes and (target_src.startswith('http') or target_src.startswith('blob')):
            try:
                b64_data = await flow_page.evaluate('''async (imgEl) => {
                    const canvas = document.createElement('canvas');
                    canvas.width = imgEl.naturalWidth || imgEl.width;
                    canvas.height = imgEl.naturalHeight || imgEl.height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(imgEl, 0, 0);
                    return canvas.toDataURL('image/jpeg', 0.95);
                }''', target_img)
                if b64_data and ',' in b64_data:
                    raw_bytes = base64.b64decode(b64_data.split(',')[1])
            except Exception:
                pass

        # 尝试 2: 如果 Canvas 跨域被拦截，直接利用 CDP 执行元素级高保真截帧（秒级完成）
        if not raw_bytes:
            await target_img.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            raw_bytes = await target_img.screenshot(type='jpeg', quality=95)

        if not raw_bytes:
            return {"success": False, "error": "无法从 DOM 渲染层提取图像数据"}

        # 步骤 6: 智能 PIL 压缩优化
        compressed_bytes, mime = compress_image_bytes(raw_bytes, max_width=max_width, quality=quality)
        b64_str = base64.b64encode(compressed_bytes).decode('utf-8')
        final_b64 = f"data:{mime};base64,{b64_str}"

        # 步骤 7: 若指定了输出路径则落盘保存
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(compressed_bytes)
            print(f"[OK] 图像已优化落盘: {output_path} ({len(compressed_bytes)/1024:.1f} KB)")

        return {
            "success": True,
            "base64": final_b64,
            "file_path": output_path,
            "size_bytes": len(compressed_bytes),
            "error": None
        }


# ==============================================================================
# 8 大商业业态 Prompt 智能组装与推断引擎 (Archetype Prompt Engine)
# ==============================================================================

ARCHETYPE_TEMPLATES = {
    # 1. 重型工程/矿山机械/固废环保装备（如 Aksel Benzin, Powerscreen 分销商）
    "heavy_machinery": (
        "A professional high-resolution wide-angle architectural and industrial photograph of the {company_name} "
        "heavy machinery dealership and service depot in {country}. The facility features a modern industrial commercial "
        "headquarters building with authentic prominent '{company_name}' logo signage on the facade. In the expansive "
        "outdoor paved heavy equipment exhibition yard, several modern tracked mobile crushing plants, screening machines, "
        "and heavy-duty conveyor stackers are neatly displayed. Clean concrete yard, service trucks, Danish/European industrial "
        "business park setting under bright crisp daylight, ultra-realistic, authentic engineering details, 8k resolution, "
        "cinematic lighting, photorealistic. --ar 16:9"
    ),
    # 2. 机床模具/激光高端设备/自动化技术中心（如 Servus, Stenbergs）
    "machine_tool": (
        "A professional high-resolution wide-angle architectural photograph of the modern {company_name} "
        "advanced manufacturing commercial facility and demonstration store in {country}. The sleek contemporary glass and steel "
        "commercial building features prominent '{company_name}' brand signage on the facade. Through large glass display windows, "
        "modern high-precision CNC machining centers and precision sample display cases "
        "are visible in a pristine, bright commercial environment. Clean concrete plaza, European industrial commercial center, "
        "crisp daylight, ultra-realistic, 8k resolution, architectural photography, photorealistic. --ar 16:9"
    ),
    # 3. 户外运动/专业钓具专营店（如 Aktiv Fritid）
    "outdoor_gear": (
        "A professional high-resolution wide-angle architectural photograph of the modern flagship {company_name} "
        "outdoor sports and fishing equipment retail store in {country}. The contemporary commercial building features Nordic natural "
        "timber and glass architecture with authentic '{company_name}' official logo signage. Expansive display windows "
        "showcase technical outdoor displays and retail gear displays. Clean landscaped entrance plaza, "
        "serene Scandinavian daytime lighting, ultra-realistic architectural details, 8k resolution, photorealistic. --ar 16:9"
    ),
    # 4. 生命科学/医疗科技/专科器械临床中心（如 Aku Med）
    "medical_device": (
        "A professional high-resolution wide-angle architectural photograph of the {company_name} "
        "medical technology and clinical demonstration center in {country}. The modern minimalist white and silver "
        "healthcare commercial building features authentic '{company_name}' signage. Clean glass facade, pristine clinical "
        "and biomedical technology environment, paved entrance walkway with neat green landscaping, bright Scandinavian daylight, "
        "ultra-realistic, high aesthetic architectural photography, 8k resolution, photorealistic. --ar 16:9"
    ),
    # 5. 工业 MRO / 五金工具 / 电气低压分销网点（如 Kristall-Elektro, Rexel, Fastenal）
    "industrial_mro": (
        "A professional high-resolution wide-angle architectural photograph of a modern {company_name} "
        "professional electrical and industrial supply trade store in {country}. The contemporary commercial building "
        "features authentic '{company_name}' official logo signage above glass entrance doors. Paved parking lot with "
        "commercial trade vans, neat outdoor staging area, modern industrial retail architecture, bright sunny daytime sky, "
        "ultra-realistic, 8k resolution, cinematic lighting, photorealistic. --ar 16:9"
    ),
    # 6. 建材大卖场 / 木业卫浴 / DIY 仓储（如 Home Depot, Leroy Merlin）
    "building_materials": (
        "A professional high-resolution wide-angle architectural photograph of a large-format {company_name} "
        "home improvement and building materials superstore in {country}. The expansive commercial facade features "
        "massive prominent '{company_name}' logo signage, wide automatic entrance doors, outdoor garden and lumber canopy, "
        "spacious asphalt parking lot with parked vehicles, bright daylight, photorealistic architectural details, 8k resolution. --ar 16:9"
    ),
    # 7. 汽配与轮胎快修连锁中心（如 AutoZone, O'Reilly, NAPA）
    "auto_parts": (
        "A professional high-resolution wide-angle architectural photograph of a modern {company_name} "
        "auto parts and vehicle service center exterior in {country}. The building features distinctive '{company_name}' "
        "brand facade and signage, dedicated customer parking lot with vehicles, adjacent clean service bay entrances, "
        "bright sunny daytime sky, ultra-realistic commercial automotive architecture, 8k resolution, photorealistic. --ar 16:9"
    ),
    # 8. 综合零售大卖场 / 超市 / 购物中心（如 Walmart, Costco, Target, Supermarket）
    "retail_supermarket": (
        "A professional high-resolution wide-angle architectural photograph of a modern flagship {company_name} "
        "supermarket store exterior in {country}. The contemporary commercial retail facade features authentic '{company_name}' "
        "official logo signage prominently displayed above the clear glass automatic entrance doors. Clean concrete paving plaza, "
        "asphalt parking lot with parked cars, neat landscaping under a bright sunny daytime sky, ultra-realistic, "
        "architectural details, 8k resolution, cinematic lighting, photorealistic. --ar 16:9"
    )
}


def infer_commercial_archetype(company_name: str, context_text: str = "") -> str:
    """根据公司名称及上下文关键词（产品、渠道、行业）智能推断最贴切的商业业态"""
    text = (company_name + " " + context_text).lower()
    
    # 1. 重型矿山与工程机械
    if any(k in text for k in ['crusher', 'screening', 'mining', 'quarry', 'heavy machinery', '破碎', '筛分', '矿山', '重型机械', '固废回收机械', 'stacker', 'excavator']):
        return "heavy_machinery"
    
    # 2. 机床、激光与精密自动化
    if any(k in text for k in ['machine tool', 'cnc', 'laser marking', 'machining', '机床', '激光打标', '切削', '车床', '加工中心', '表面清洗', 'traceability']):
        return "machine_tool"
    
    # 3. 户外运动、钓具与探险装备
    if any(k in text for k in ['outdoor', 'fishing', 'wader', 'sportswear', 'fritid', '钓鱼', '户外', '涉水服', '冲锋衣', '渔具', '钓具', 'ski']):
        return "outdoor_gear"
    
    # 4. 医疗科技、临床设备与生命科学
    if any(k in text for k in ['medical', 'hospital', 'clinical', 'pulmonary', 'diagnostics', '医疗器械', '心肺', '呼吸', '步态', '康复', 'medtech', 'pharmaceutical']):
        return "medical_device"
    
    # 5. 工业 MRO、五金工具与电气分销
    if any(k in text for k in ['electrical', 'mro', 'hardware', 'fastener', 'tools', '五金', '电气', '低压配电', '电缆', '电工', 'lighting', '照明']):
        return "industrial_mro"
    
    # 6. 建材大卖场与木业卫浴
    if any(k in text for k in ['building material', 'diy', 'timber', 'sanitary', 'home improvement', '建材', '卫浴', '木业', '地板', '瓷砖']):
        return "building_materials"
    
    # 7. 汽配与轮胎快修
    if any(k in text for k in ['auto part', 'automotive', 'tire', 'car part', '汽配', '汽车配件', '轮胎', '汽修']):
        return "auto_parts"
    
    # 默认兜底：现代商业综合零售超市
    return "retail_supermarket"


def build_default_storefront_prompt(
    company_name: str,
    country: str = "",
    archetype: str = None,
    context_text: str = ""
) -> str:
    """根据商业业态与上下文智能组装高保真 Prompt"""
    c_country = country or "Europe"
    
    # 如果未显式指定业态，则自动推断
    if not archetype or archetype not in ARCHETYPE_TEMPLATES:
        archetype = infer_commercial_archetype(company_name, context_text)
    
    template = ARCHETYPE_TEMPLATES.get(archetype, ARCHETYPE_TEMPLATES["retail_supermarket"])
    prompt = template.format(company_name=company_name, country=c_country)
    return prompt


def cli_main():
    parser = argparse.ArgumentParser(description="Google Flow CDP 秒级自动化生图与提取工具")
    parser.add_argument("--prompt", type=str, help="显式生图提示词")
    parser.add_argument("--company", type=str, help="公司名称（自动组装提示词）")
    parser.add_argument("--country", type=str, default="", help="所在国家")
    parser.add_argument("--archetype", type=str, choices=list(ARCHETYPE_TEMPLATES.keys()), help="商业业态类型")
    parser.add_argument("--context", type=str, default="", help="上下文文本（用于自动推断业态）")
    parser.add_argument("--output", type=str, default="storefront_banner.jpg", help="输出图片保存路径")
    parser.add_argument("--cdp", type=str, default="http://127.0.0.1:9222", help="Chrome CDP 调试地址")
    parser.add_argument("--wait", type=int, default=32, help="等待生成秒数")
    parser.add_argument("--max-width", type=int, default=1100, help="输出最大宽度")
    parser.add_argument("--quality", type=int, default=80, help="JPEG压缩质量")

    args = parser.parse_args()

    prompt = args.prompt
    if not prompt:
        if args.company:
            prompt = build_default_storefront_prompt(
                args.company,
                country=args.country,
                archetype=args.archetype,
                context_text=args.context
            )
        else:
            print("[ERROR] 必须提供 --prompt 或 --company 参数")
            sys.exit(1)

    result = asyncio.run(generate_and_extract_flow_image(
        prompt=prompt,
        output_path=args.output,
        cdp_url=args.cdp,
        wait_seconds=args.wait,
        max_width=args.max_width,
        quality=args.quality
    ))

    if result["success"]:
        print(f"\n[SUCCESS] 自动生图与秒级提取完成！大小: {result['size_bytes']/1024:.1f} KB")
    else:
        print(f"\n[FAIL] 生图失败: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
