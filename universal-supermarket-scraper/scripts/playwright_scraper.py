import json
import os
import sys
import time
import argparse
from playwright.sync_api import sync_playwright

def scrape(website_url, keyword, output_file, mode="fast", max_items=20):
    with sync_playwright() as p:
        print(f"[*] 正在启动浏览器引擎...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print(f"[*] 正在访问: {website_url}")
        page.goto(website_url, wait_until="domcontentloaded")
        
        # 1. 智能处理 Cookie 弹窗
        try:
            for btn_text in ["Accept All", "Allow all", "同意", "确定", "OK", "Accept"]:
                btn = page.get_by_role("button", name=btn_text, exact=False)
                if btn.count() > 0 and btn.first.is_visible():
                    btn.first.click(timeout=2000)
                    print(f"[+] 已点击 Cookie 弹窗: {btn_text}")
                    break
        except:
            pass

        # 2. 执行搜索
        print(f"[*] 正在搜索: {keyword}")
        search_selectors = [
            'input[name="q"]', 'input[type="search"]', 
            'input[placeholder*="search" i]', 'input[aria-label*="search" i]', '#search'
        ]
        search_found = False
        for selector in search_selectors:
            locator = page.locator(selector).first
            if locator.count() > 0 and locator.is_visible():
                locator.fill(keyword)
                locator.press("Enter")
                search_found = True
                print(f"[+] 已使用选择器 '{selector}' 进行搜索")
                break
        
        if not search_found:
            print("[!] 未找到搜索框，尝试通过按钮触发...")
            # 部分网站需要点击搜索图标才显示输入框
            search_icon = page.locator('button[aria-label*="search" i], .search-icon').first
            if search_icon.count() > 0:
                search_icon.click()
                time.sleep(1)
                # 再次尝试填充
                for selector in search_selectors:
                    locator = page.locator(selector).first
                    if locator.count() > 0:
                        locator.fill(keyword)
                        locator.press("Enter")
                        search_found = True
                        break

        if not search_found:
            print("[!] 无法搜索，请手动检查或联系开发人员。")
            browser.close()
            return

        print("[*] 等待搜索结果加载...")
        time.sleep(3) # 给页面一点渲染时间

        results = []
        seen_urls = set()
        
        # 3. 抓取逻辑
        print(f"[*] 开始执行抓取 (目标: {max_items} 个商品)...")
        page_num = 1
        
        while len(results) < max_items:
            # 寻找商品卡片
            card_selectors = [
                '.ais-InfiniteHits-item', 'div[class*="product" i]', 
                'div[class*="item" i]', 'article', 'section[class*="card" i]'
            ]
            
            items = []
            for selector in card_selectors:
                found = page.locator(selector).all()
                if len(found) > 0:
                    items = found
                    print(f"[*] 使用选择器 '{selector}' 发现 {len(found)} 个元素")
                    break
            
            if not items:
                print("[!] 未发现商品元素，检查是否有结果...")
                break

            current_round_new = 0
            for item in items:
                if len(results) >= max_items: break
                try:
                    # 提取详情链接
                    link_el = item.locator('a').first
                    link = link_el.get_attribute("href")
                    if not link or "javascript" in link or "#" in link: continue
                    
                    if not link.startswith('http'):
                        link = f"{website_url.rstrip('/')}/{link.lstrip('/')}"
                    
                    if link in seen_urls: continue

                    # 提取图片
                    img = item.locator('img').first
                    img_url = (img.get_attribute("src") or 
                              img.get_attribute("data-src") or 
                              img.get_attribute("srcset") or "")
                    if img_url.startswith("//"): img_url = "https:" + img_url
                    
                    # 提取标题
                    title_el = item.locator('h1, h2, h3, h4, .title, [class*="name" i], strong').first
                    title = title_el.inner_text() if title_el.count() > 0 and title_el.is_visible() else ""
                    if not title:
                        text = item.inner_text().strip()
                        if text: title = text.split('\n')[0]

                    if title and img_url and link:
                        results.append({
                            "name": title.strip(),
                            "image_url": img_url,
                            "url": link,
                            "price": "见页面"
                        })
                        seen_urls.add(link)
                        current_round_new += 1
                except:
                    continue
            
            print(f"[+] 第 {page_num} 页抓取完成，本页新增 {current_round_new} 个，总计 {len(results)}")
            
            if len(results) >= max_items: break

            # 4. 加载更多逻辑 (翻页或滚动)
            next_button = page.locator('a:has-text("Next"), button:has-text("Next"), .page-link:has-text(">"), [aria-label*="next" i]').first
            if next_button.count() > 0 and next_button.is_visible():
                print("[*] 发现翻页按钮，正在跳转下一页...")
                next_button.click()
                time.sleep(3)
                page_num += 1
            else:
                # 尝试滚动加载
                print("[*] 未发现翻页按钮，尝试滚动加载...")
                last_height = page.evaluate("document.body.scrollHeight")
                page.mouse.wheel(0, 3000)
                time.sleep(3)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    print("[*] 页面已到底部，且无翻页按钮。终止抓取。")
                    break
                page_num += 1

        # 5. 保存结果
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results[:max_items], f, ensure_ascii=False, indent=2)
        
        print(f"[+] 任务成功。最终保存 {len(results)} 个结果至 {output_file}")
        browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--output", default="scripts/temp_data.json")
    parser.add_argument("--mode", default="fast")
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()
    
    scrape(args.url, args.keyword, args.output, args.mode, args.count)
