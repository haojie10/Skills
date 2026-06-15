/**
 * extract_body.js — CRM 邮件正文提取脚本（仅最新回复）
 *
 * 功能：从右侧预览面板中提取邮件正文，自动识别并截断历史引用部分，
 *       仅保留最新一条回复，上限 500 字。
 *
 * 使用方式：
 *   1. 先点击邮件列表中的某一行，等待右侧预览面板加载
 *   2. 在浏览器 DevTools Console 中执行此脚本
 *   3. 结果存储在 window.__emailBody 中
 *
 * NOTE: BODY_SELECTOR 需根据实际 CRM DOM 调整。
 */
(() => {
  // ===== 可配置选择器 =====
  // 右侧预览面板中邮件正文的容器选择器
  // 可能是 .email-body, .mail-body, .message-content 等
  const BODY_SELECTORS = [
    '.email-body',
    '.mail-body',
    '.message-content',
    '.email-detail-body',
    '[class*="body"]',
    '[class*="content"]',
  ];

  // 正文最大字符数
  const MAX_CHARS = 500;
  // ========================

  // 尝试多个选择器找到正文容器
  let bodyEl = null;
  for (const sel of BODY_SELECTORS) {
    bodyEl = document.querySelector(sel);
    if (bodyEl && bodyEl.innerText.trim().length > 10) break;
  }

  if (!bodyEl) {
    window.__emailBody = JSON.stringify({ error: '未找到正文容器，请检查选择器' });
    return window.__emailBody;
  }

  const fullText = bodyEl.innerText.trim();

  // 识别引用分隔符，截取最新回复
  const SEPARATORS = [
    /\n-{3,}\s*\n/,                          // --- 分隔线
    /\nOn .+wrote:\s*\n/i,                    // On ... wrote:
    /\n发件人[：:]\s*/,                        // 发件人：
    /\n-----\s*Original Message\s*-----/i,     // -----Original Message-----
    /\n>{2,}\s/,                               // >> 引用
    /\n回复的邮件/,                            // 回复的邮件
    /\n转发的邮件/,                            // 转发的邮件
    /\nFrom:\s+/i,                             // From: header
    /\n____+\n/,                               // ____ 下划线分隔
  ];

  let latestReply = fullText;
  for (const sep of SEPARATORS) {
    const match = fullText.match(sep);
    if (match && match.index > 20) {
      // 确保至少有 20 字的正文再截断
      latestReply = fullText.substring(0, match.index).trim();
      break;
    }
  }

  // 截取上限
  const result = latestReply.length > MAX_CHARS
    ? latestReply.substring(0, MAX_CHARS) + '...'
    : latestReply;

  window.__emailBody = result;
  console.log(`[extract_body] 提取完成，${result.length} 字`);
  return window.__emailBody;
})();
