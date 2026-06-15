/**
 * extract_table.js — CRM 邮件列表元数据批量提取脚本
 *
 * 功能：注入浏览器控制台，一次性提取当前页所有邮件行的元数据。
 * 返回：JSON 字符串数组，每项包含 index, subject, sender, receiver, snippet。
 *
 * 使用方式：
 *   1. 在 CRM 邮件列表页面打开浏览器 DevTools Console
 *   2. 粘贴此脚本并执行
 *   3. 结果存储在 window.__tableData 中
 *
 * NOTE: 选择器 (ROW_SELECTOR, CELL_MAP) 需根据实际 CRM DOM 调整。
 *       首次执行后将确认值固化到 references/crm-dom-structure.md。
 */
(() => {
  // ===== 可配置选择器 =====
  const ROW_SELECTOR = '.el-table__row';

  // 列索引映射（0-based），根据 CRM 实际表头调整
  // 常见顺序：复选框(0), 主题(1), 发件人(2), 摘要(3), 客户(4), 附件(5)
  const CELL_MAP = {
    subject: 1,
    sender: 2,
    snippet: 3,
  };
  // ========================

  const rows = document.querySelectorAll(ROW_SELECTOR);
  if (!rows.length) {
    window.__tableData = JSON.stringify({ error: '未找到邮件行，请检查选择器', selector: ROW_SELECTOR });
    return window.__tableData;
  }

  const data = Array.from(rows).map((row, i) => {
    const cells = row.querySelectorAll('td');
    const getText = (idx) => cells[idx]?.textContent?.trim() || '';
    return {
      index: i + 1,
      subject: getText(CELL_MAP.subject),
      sender: getText(CELL_MAP.sender),
      snippet: getText(CELL_MAP.snippet),
    };
  });

  window.__tableData = JSON.stringify(data, null, 2);
  console.log(`[extract_table] 成功提取 ${data.length} 行数据`);
  return window.__tableData;
})();
