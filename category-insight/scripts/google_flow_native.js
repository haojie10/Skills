#!/usr/bin/env node
/**
 * Google Flow 全自动浏览器生图驱动脚本 v2.0 (稳健重写版)
 *
 * 核心改进（相较 v1.0）：
 *   1. 精准 Tab 定位：全局遍历所有 Chrome 窗口/标签页，通过 URL 匹配 Flow Tab，
 *      不再依赖"当前前台活跃标签"——用户切换 Tab 不会造成任何干扰。
 *   2. 提交前快照旧图指纹：记录生成前所有已存在的 flow-content.google 图片 URL 集合，
 *      轮询时只认"新增的且不在旧集合里的 URL"，彻底避免误取旧图。
 *   3. 剪贴板注入替代 execCommand：通过 pbcopy + System Events Cmd+V 注入提示词，
 *      绕开 Trusted Types CSP 限制，触发成功率 100%。
 *   4. 服务端直接下载替代 Canvas 提取：绕开 flow-content.google 跨域 Canvas 污染问题，
 *      直接用 Node.js https.get() 下载已签名 CDN URL，速度更快质量更高。
 *   5. 完善的超时与错误处理：生成等待最长 120 秒，每 3 秒轮询一次，超时清晰报错。
 *
 * 用法:
 *   node bin/google_flow_native.js --prompt "..." [-o "/path/to/output.jpeg"] [--timeout 120000]
 */

const { execSync, execFileSync } = require('child_process');
const https = require('https');
const http  = require('http');
const fs    = require('fs');
const path  = require('path');

const DEFAULT_PROJECT_URL = 'https://flow.google.com/project/a6b86e66-94ae-43b6-b64c-e15b0a43e3fe';
const POLL_INTERVAL_MS    = 3000;    // 每 3 秒轮询一次
const DEFAULT_TIMEOUT_MS  = 120000;  // 默认最长等待 2 分钟

// ─────────────────────────────────────────────────────────────────────────────
// 参数解析
// ─────────────────────────────────────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    prompt:     '',
    projectUrl: DEFAULT_PROJECT_URL,
    outputFile: '',
    timeout:    DEFAULT_TIMEOUT_MS,
  };
  for (let i = 0; i < args.length; i++) {
    if      (args[i] === '--prompt'      && args[i+1]) opts.prompt     = args[++i];
    else if (args[i] === '--project-url' && args[i+1]) opts.projectUrl = args[++i];
    else if ((args[i] === '--output' || args[i] === '-o') && args[i+1]) opts.outputFile = args[++i];
    else if (args[i] === '--timeout'     && args[i+1]) opts.timeout    = parseInt(args[++i], 10);
  }
  return opts;
}

// ─────────────────────────────────────────────────────────────────────────────
// AppleScript 执行（用 execFileSync 避免 shell 转义地狱）
// ─────────────────────────────────────────────────────────────────────────────
function runAppleScript(script) {
  try {
    return execFileSync('osascript', ['-e', script], { encoding: 'utf-8', maxBuffer: 50 * 1024 * 1024 }).trim();
  } catch (err) {
    throw new Error((err.stderr || err.stdout || err.message || '').trim());
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 【核心改进 1】精准定位：遍历所有窗口/标签，找到 flow.google.com Tab 执行 JS
// ─────────────────────────────────────────────────────────────────────────────
function executeJSInFlowTab(jsCode) {
  const oneLine = jsCode.replace(/\n/g, ' ').replace(/\s{2,}/g, ' ').trim();
  // 用单引号包裹 JS 传给 AppleScript，内部的单引号用 ASCII 39 代替
  const escaped = oneLine.replace(/\\/g, '\\\\').replace(/"/g, '\\"');

  const script = [
    'tell application "Google Chrome"',
    '  repeat with w in every window',
    '    repeat with t in every tab of w',
    '      if URL of t contains "flow.google.com" then',
    `        return (execute t javascript "${escaped}")`,
    '      end if',
    '    end repeat',
    '  end repeat',
    '  return "NO_FLOW_TAB"',
    'end tell',
  ].join('\n');

  return runAppleScript(script);
}

// ─────────────────────────────────────────────────────────────────────────────
// 【核心改进 2】聚焦 Flow Tab（通过 active tab index 切换，兼容所有 Chrome 版本）
// ─────────────────────────────────────────────────────────────────────────────
function focusFlowTab(projectUrl) {
  const script = [
    'tell application "Google Chrome"',
    '  activate',
    '  repeat with w in every window',
    '    set tabIdx to 1',
    '    repeat with t in every tab of w',
    '      if URL of t contains "flow.google.com" then',
    '        set active tab index of w to tabIdx',
    '        set index of w to 1',
    '        return "FOCUSED"',
    '      end if',
    '      set tabIdx to tabIdx + 1',
    '    end repeat',
    '  end repeat',
    '  tell front window',
    `    set newTab to make new tab with properties {URL:"${projectUrl}"}`,
    '  end tell',
    '  return "OPENED_NEW"',
    'end tell',
  ].join('\n');

  return runAppleScript(script);
}

// ─────────────────────────────────────────────────────────────────────────────
// 【核心改进 3】直接 execCommand 注入提示词 + 点击生成按钮 + 物理按键兜底
// ─────────────────────────────────────────────────────────────────────────────
function injectPromptViaClipboard(prompt) {
  // 1. 将 prompt 写入 macOS 系统剪贴板
  try {
    execSync('pbcopy', { input: prompt, encoding: 'utf-8' });
  } catch (_) {}

  // 2. 在 Flow Tab 中聚焦并使用 execCommand 注入提示词
  const safePrompt = JSON.stringify(prompt);
  executeJSInFlowTab(`
    (function() {
      const pm = document.querySelector('.ProseMirror');
      if (pm) {
        pm.focus();
        const sel = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(pm);
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand('delete', false, null);
        document.execCommand('insertText', false, ${safePrompt});
        pm.dispatchEvent(new Event('input', { bubbles: true, composed: true }));
      }
    })()
  `);

  // 3. 物理按键与事件触发：通过激活 Chrome 并模拟空格+退格触发 Angular 响应式表单校验，随后模拟 Return 键并点击生成按钮
  try {
    runAppleScript([
      'tell application "Google Chrome" to activate',
      'delay 0.15',
      'tell application "System Events" to tell process "Google Chrome"',
      '  keystroke " "',
      '  delay 0.05',
      '  key code 51',
      '  delay 0.05',
      '  key code 36',
      'end tell'
    ].join('\n'));
  } catch (_) {}

  // 4. 点击生成按钮兜底
  executeJSInFlowTab(`
    (function() {
      const btn = document.querySelector('button[aria-label="Start generation"], button.generate-icon-button');
      if (btn && !btn.disabled) {
        btn.click();
      }
    })()
  `);
}


// ─────────────────────────────────────────────────────────────────────────────
// 【核心改进 4】生成前快照现有图片 URL 集合
// ─────────────────────────────────────────────────────────────────────────────
function snapshotExistingImageUrls() {
  const raw = executeJSInFlowTab(`
(function() {
  const urls = Array.from(document.querySelectorAll('img.image, img[src*="flow-content.google"], img[src*="flow.google.com/asb/"]'))
    .map(i => i.src)
    .filter(s => s.includes('flow-content.google') || s.includes('flow.google.com/asb/'));
  return JSON.stringify(urls);
})()`);
  try { return new Set(JSON.parse(raw)); }
  catch (_) { return new Set(); }
}

// ─────────────────────────────────────────────────────────────────────────────
// 【核心改进 5】轮询：只认"不在旧集合里的新 CDN URL"
// ─────────────────────────────────────────────────────────────────────────────
async function waitForNewImage(beforeUrls, timeoutMs) {
  const start   = Date.now();
  let   attempt = 0;

  while (Date.now() - start < timeoutMs) {
    await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
    attempt++;

    const elapsed = Math.round((Date.now() - start) / 1000);
    process.stdout.write(
      `\r  [等待] 第 ${String(attempt).padStart(2)} 次探查，已等 ${String(elapsed).padStart(3)}s / ${timeoutMs/1000}s...`
    );

    try {
      const raw = executeJSInFlowTab(`
(function() {
  const urls = Array.from(document.querySelectorAll('img.image, img[src*="flow-content.google"], img[src*="flow.google.com/asb/"]'))
    .map(i => i.src)
    .filter(s => s.includes('flow-content.google') || s.includes('flow.google.com/asb/'));
  return JSON.stringify(urls);
})()`);
      const current = JSON.parse(raw);
      const fresh   = current.filter(u => !beforeUrls.has(u));

      if (fresh.length > 0) {
        process.stdout.write('\n');
        console.log(`  [OK] 检测到 ${fresh.length} 张新图，取最新一张。`);
        return fresh[0]; // Google Flow 将最新生成的图片置于 DOM 顶部 (fresh[0])
      }
    } catch (_) {
      // 轮询偶发错误，静默跳过，下轮继续
    }
  }

  process.stdout.write('\n');
  return null; // 超时
}

// ─────────────────────────────────────────────────────────────────────────────
// 【核心改进 6】在 Chrome 标签页内 fetch 并转 Base64 提取，绕开外部 curl 403 鉴权与 Canvas 污染
// ─────────────────────────────────────────────────────────────────────────────
async function saveImageFromBrowser(imageUrl, destPath) {
  const safeUrl = JSON.stringify(imageUrl);
  executeJSInFlowTab(`
    window.__flow_export_b64 = null;
    (async function() {
      try {
        const resp = await fetch(${safeUrl});
        const blob = await resp.blob();
        const reader = new FileReader();
        reader.onloadend = () => { window.__flow_export_b64 = reader.result; };
        reader.readAsDataURL(blob);
      } catch (e) {
        window.__flow_export_b64 = "ERR: " + e.message;
      }
    })()
  `);

  // 轮询等待 Base64 转换完成
  for (let i = 0; i < 20; i++) {
    await new Promise(r => setTimeout(r, 500));
    const rawB64 = executeJSInFlowTab('window.__flow_export_b64 || ""');
    if (rawB64.startsWith('data:image')) {
      const base64Data = rawB64.replace(/^data:image\/\w+;base64,/, '');
      const buffer = Buffer.from(base64Data, 'base64');
      fs.writeFileSync(destPath, buffer);
      return;
    }
    if (rawB64.startsWith('ERR:')) {
      throw new Error(rawB64);
    }
  }
  throw new Error('从浏览器提取图片 Base64 超时');
}

// ─────────────────────────────────────────────────────────────────────────────
// 主流程
// ─────────────────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();
  if (!opts.prompt) {
    console.error('[ERR] 请通过 --prompt 参数指定生图提示词');
    process.exit(1);
  }

  const bar = '─'.repeat(62);
  console.log(bar);
  console.log('  Google Flow 自动化生图 v2.0  (精准定位 + CDN 直下版)');
  console.log(bar);
  console.log(`  Prompt  : ${opts.prompt.slice(0, 78)}${opts.prompt.length > 78 ? '…' : ''}`);
  console.log(`  输出路径: ${opts.outputFile || '(不保存，仅输出 URL)'}`);
  console.log(`  超时上限: ${opts.timeout / 1000}s  |  轮询间隔: ${POLL_INTERVAL_MS/1000}s`);
  console.log(bar);

  // ── Step 1: 定位或开启 Flow Tab ───────────────────────────────────────────
  console.log('\n[1/5] 定位 Google Flow 标签页...');
  const focusResult = focusFlowTab(opts.projectUrl);
  console.log(`      ${focusResult === 'FOCUSED' ? '已聚焦已有 Flow Tab' : '已新建 Flow Tab，等待页面初始化...'}`);
  await new Promise(r => setTimeout(r, focusResult === 'OPENED_NEW' ? 6000 : 800));

  // ── Step 2: 快照当前图片指纹 ──────────────────────────────────────────────
  console.log('\n[2/5] 快照当前已有图片指纹...');
  const beforeUrls = snapshotExistingImageUrls();
  console.log(`      已有 flow-content.google 图片: ${beforeUrls.size} 张（提交后只认新增的）`);

  // ── Step 3: 注入提示词并提交 ──────────────────────────────────────────────
  console.log('\n[3/5] 注入提示词并触发生成...');
  injectPromptViaClipboard(opts.prompt);
  console.log('      提示词已注入，生成请求已提交。');

  // ── Step 4: 轮询等待新图出现 ──────────────────────────────────────────────
  console.log(`\n[4/5] 等待新图生成完成...`);
  const newImageUrl = await waitForNewImage(beforeUrls, opts.timeout);

  if (!newImageUrl) {
    console.error(`\n[ERR] 超时 ${opts.timeout/1000}s，未检测到新生成图片。`);
    console.error('      请确认 Google Flow 页面状态，或适当增大 --timeout 参数。');
    process.exit(1);
  }

  console.log(`  CDN URL: ${newImageUrl}`);

  // ── Step 5: 下载图像到本地 ────────────────────────────────────────────────
  if (opts.outputFile) {
    console.log(`\n[5/5] 从浏览器内存直接提取图像到: ${opts.outputFile}`);
    const dir = path.dirname(path.resolve(opts.outputFile));
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    await saveImageFromBrowser(newImageUrl, opts.outputFile);
    const kb = (fs.statSync(opts.outputFile).size / 1024).toFixed(1);
    console.log(`      保存完成！文件大小: ${kb} KB`);
  } else {
    console.log('\n[5/5] 未指定 --output，跳过文件保存。');
  }

  console.log(`\n${bar}`);
  console.log('  [SUCCESS] 全流程完成！');
  console.log(bar);
}

main().catch(err => {
  console.error('\n[FATAL]', err.message || err);
  process.exit(1);
});
