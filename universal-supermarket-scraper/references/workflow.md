# Supermarket Scraper Workflow

### AI 交互模式 (快速/深度)

用户请求时，按照以下模板引导 Browser Subagent：

```markdown
1. 打开网站：{website_url}
2. 在搜索框输入关键词：{keyword} 并点击搜索。
3. 等待结果加载完成后，**直接在当前搜索结果列表页**提取所有可见商品信息。
4. 提取字段：
   - **name**: 商品名称
   - **price**: 售价
   - **image_url**: **务必提取 <img> 标签的 src 属性**，确保是图片链接。
   - **url**: 提取 <a> 标签的 href 属性 (详情页链接)。
   - **description**: 列表页简短描述。
5. 以 JSON 数组形式返回所有结果。
```

---

### Playwright 自动化脚本模式 (Expert Mode)

如果你希望通过命令行处理大规模抓取，请使用以下流程：

1. **执行抓取脚本**：
   ```bash
   python scripts/playwright_scraper.py --url "{website_url}" --keyword "{keyword}" --count 20 --output "scripts/temp_data.json"
   ```
   *注：如需观察过程，可在脚本中将 headless 改为 False。*

2. **执行转换脚本**：
   ```bash
   python scripts/export_to_excel.py "scripts/temp_data.json" "C:/Users/031/Desktop/Output.xlsx"
   ```

3. **分页与滚动处理**：
   脚本已内置 `page.mouse.wheel` 逻辑，会自动处理无限滚动页面。对于传统的「下一页」按钮，脚本逻辑会根据 DOM 结构尝试自动识别。
