#!/usr/bin/env node
/**
 * 从海外新闻源网页抓取高清 og:image 配图（report-news 技能红线：必须优先抓取 <meta property="og:image">）
 *
 * 用法:
 *   node fetch-og-image.js <url> [<url>...]
 *
 * 输出: 每条 URL 对应的 og:image 链接；抓取失败时回退到 twitter:image。
 * 若均未找到，输出 NOT_FOUND，此时应回退使用素材正文中的真实图片链接。
 */
const urls = process.argv.slice(2);

async function fetchOgImage(url) {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 15000);
    const res = await fetch(url, {
      signal: ctrl.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'Accept-Language': 'en-US,en;q=0.9'
      }
    });
    clearTimeout(t);
    if (!res.ok) {
      console.log(`URL: ${url}\n  HTTP ${res.status} (${res.statusText}) — 未找到配图\n`);
      return;
    }
    const html = await res.text();
    const og = html.match(/<meta[^>]*?property=["']og:image["'][^>]*?content=["']([^"']+)["']/i)
      || html.match(/<meta[^>]*?content=["']([^"']+)["'][^>]*?property=["']og:image["']/i)
      || html.match(/<meta[^>]*?name=["']twitter:image["'][^>]*?content=["']([^"']+)["']/i);
    console.log(`URL: ${url}`);
    console.log(`  og:image: ${og ? og[1] : 'NOT_FOUND'}\n`);
  } catch (err) {
    console.log(`URL: ${url}\n  ERROR: ${err.message}\n`);
  }
}

(async () => {
  for (const url of urls) {
    await fetchOgImage(url);
  }
})();
