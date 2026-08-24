#!/usr/bin/env node
/**
 * 将 GTB 四段式新闻 JSON 组装为平台 HTML 并 POST 发布到 GTB 平台
 * 对齐 report-news 技能：四段式深度结构 + og:image 配图 + 54 品类标签 + 权威来源链接
 *
 * 用法:
 *   node publish-news.js                          # 发布当前目录下所有 *.json
 *   node publish-news.js /path/to/dir             # 发布指定目录下所有 *.json
 *   node publish-news.js /path/to/item.json       # 发布单个 JSON 文件
 *   node publish-news.js <dir> --keep             # 发布成功后保留 JSON（默认自动删除）
 *
 * 默认行为：发布成功的 JSON 会被自动删除（过程文件不残留）；发布失败的保留，
 * 以便修复后重试。传入 --keep 则全部保留。
 *
 * 配置（必需，从项目根 .env 或环境变量读取，脚本不内置任何默认密钥）:
 *   GTB_API_URL   GTB 平台地址，如 http://124.222.201.143:3000
 *   AGENT_API_KEY 发布鉴权密钥（Bearer token）
 * 缺少配置时脚本立即报错退出，不会静默使用默认值。
 */
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

/** 从项目根 .env 加载配置（Node 20.12+ 内置 process.loadEnvFile，无第三方依赖；文件不存在则跳过） */
function loadDotEnv() {
  const candidates = [
    path.join(__dirname, '..', '..', '..', '.env'), // 技能所在的项目根
    path.resolve(process.cwd(), '.env')             // 当前运行目录
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) {
      try {
        process.loadEnvFile(p); // 已有的环境变量优先，不会被 .env 覆盖
        return p;
      } catch (e) {
        console.warn(`⚠️  加载 ${p} 失败: ${e.message}`);
      }
    }
  }
  return null;
}

const envFile = loadDotEnv();
if (envFile) console.log(`📄 已加载配置: ${envFile}`);

const GTB_API_URL = process.env.GTB_API_URL;
const API_KEY = process.env.AGENT_API_KEY;

if (!GTB_API_URL || !API_KEY) {
  console.error('❌ 缺少必要配置：GTB_API_URL 或 AGENT_API_KEY 未设置。');
  console.error('   请在项目根目录创建 .env（可参考 .env.example），或在运行时注入环境变量：');
  console.error('   GTB_API_URL="https://你的平台地址" AGENT_API_KEY="你的密钥" node publish-news.js <目录或JSON>');
  process.exit(1);
}

/** 解析参数: 可能是目录或单个 JSON 文件 */
function resolveTargets(argv) {
  if (argv.length === 0) {
    // 默认当前目录下所有 *.json
    return fs.readdirSync(__dirname).filter(f => f.endsWith('.json')).map(f => path.join(__dirname, f));
  }
  const targets = [];
  for (const arg of argv) {
    const p = path.resolve(arg);
    if (!fs.existsSync(p)) {
      console.error(`⚠️  路径不存在, 跳过: ${p}`);
      continue;
    }
    const stat = fs.statSync(p);
    if (stat.isDirectory()) {
      targets.push(...fs.readdirSync(p).filter(f => f.endsWith('.json')).map(f => path.join(p, f)));
    } else if (p.endsWith('.json')) {
      targets.push(p);
    }
  }
  return targets;
}

/** 组装平台 HTML（report-news 四段式结构，首个 href 为权威来源链接） */
function buildHtml(item) {
  const imgTag = item.imageUrl
    ? `<p><img src="${item.imageUrl}" alt="${item.title}" style="max-width:100%; border-radius:8px; margin-bottom:20px;" /></p>`
    : '';
  return `
<div class="gtb-news-article">
  ${imgTag}
  <h3>📌 核心事实深度解构 (Recap)</h3>
  <p style="line-height: 1.8; color: var(--color-text); font-size: 1.05rem;">${item.recap}</p>

  <h3>📊 关键数据与事实亮点 (Highlights)</h3>
  <ul>
    ${(item.highlights || []).map(h => `<li style="line-height: 1.7; margin-bottom: 6px;">${h}</li>`).join('')}
  </ul>

  <div style="background: rgba(255, 100, 30, 0.04); border-left: 4px solid var(--color-accent, #ff641e); padding: 16px 20px; border-radius: 4px; margin: 24px 0;">
    <h4 style="margin: 0 0 8px 0; color: var(--color-accent, #ff641e);">💡 中国外贸工厂与供应链实操启示 (Takeaways)</h4>
    <p style="margin: 0; line-height: 1.7; font-size: 0.95rem;">${item.takeaways}</p>
  </div>

  <p style="font-size: 0.85rem; color: #888; margin-top: 24px;">
    🔗 权威新闻来源：<a href="${item.source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--color-accent, #ff641e); text-decoration: underline;">${item.source_name || '点击查阅海外媒体报道原文'} ↗</a>
  </p>
</div>`;
}

function postNews(item) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      type: 'article',
      title: item.title,
      summary: (item.recap || '').slice(0, 160) + '...',
      contentHtml: buildHtml(item),
      region: item.region || '欧洲',
      country: item.country || '',
      industry: item.industry || (item.industries && item.industries[0]) || '',
      industries: item.industries || [],
      tags: item.tags || {}
    });

    const url = new URL(GTB_API_URL);
    const isHttps = url.protocol === 'https:';
    const requester = isHttps ? https : http;
    const options = {
      hostname: url.hostname,
      port: url.port || (isHttps ? 443 : 80),
      path: '/api/agent/publish',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'Authorization': `Bearer ${API_KEY}`
      }
    };

    const req = requester.request(options, (res) => {
      let body = '';
      res.setEncoding('utf8');
      res.on('data', c => body += c);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try {
            const resp = JSON.parse(body);
            console.log(`  ✅ 已发布: ${item.title}`);
            console.log(`     id=${resp.id} | 忽略品类=${JSON.stringify(resp.ignoredCategories || [])}`);
          } catch (e) {}
          resolve();
        } else {
          reject(new Error(`HTTP ${res.statusCode}: ${body.slice(0, 300)}`));
        }
      });
    });
    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

async function main() {
  const rawArgs = process.argv.slice(2);
  const keepFiles = rawArgs.includes('--keep');
  const targetArgs = rawArgs.filter(a => a !== '--keep');
  const files = resolveTargets(targetArgs);
  if (files.length === 0) {
    console.error('❌ 未找到任何 JSON 文件');
    process.exit(1);
  }
  console.log(`🚀 开始发布 ${files.length} 条资讯到 ${GTB_API_URL}`);
  if (keepFiles) {
    console.log('💾 --keep 模式：发布后保留 JSON 文件');
  } else {
    console.log('🧹 默认模式：发布成功的 JSON 将自动删除');
  }
  console.log('');

  let ok = 0;
  const removed = [];
  const failed = [];
  for (const f of files) {
    const item = JSON.parse(fs.readFileSync(f, 'utf8'));
    console.log(`📰 ${item.title}`);
    try {
      await postNews(item);
      ok++;
      if (!keepFiles) {
        try {
          fs.unlinkSync(f);
          removed.push(path.basename(f));
        } catch (err) {
          // 发布已成功，清理失败不算发布失败，仅提示手动删除
          console.warn(`  ⚠️ 发布成功但清理失败（请手动删除）: ${path.basename(f)} — ${err.message}`);
        }
      }
    } catch (err) {
      console.error(`  ❌ 发布失败: ${err.message}`);
      failed.push(path.basename(f));
    }
    console.log('');
  }
  console.log(`🎉 完成: ${ok}/${files.length} 条发布成功`);
  if (removed.length > 0) {
    console.log(`🧹 已清理过程文件 (${removed.length}): ${removed.join(', ')}`);
  }
  if (failed.length > 0) {
    console.log(`⚠️  以下文件发布失败已保留，修复后可用 --keep 重试: ${failed.join(', ')}`);
  }
}

main();
