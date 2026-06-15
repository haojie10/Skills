const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx.js');

// 目录与路径常量
const SCRATCH_DIR = 'C:/Users/066/.gemini/antigravity/brain/d160cf64-2927-4f09-808d-8f1c50f0a2a7/scratch';
const OUTPUT_SLIDES_DIR = path.join(SCRATCH_DIR, 'planters_slides');
const IMAGES_DIR = path.join(SCRATCH_DIR, 'images');

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_SLIDES_DIR)) {
    fs.mkdirSync(OUTPUT_SLIDES_DIR, { recursive: true });
}

// 统一使用的公共 CSS 样式，符合 html2pptx 验证标准 (720pt x 405pt)
const COMMON_CSS = `
* {
    box-sizing: border-box;
}
html, body {
    margin: 0;
    padding: 0;
    width: 720pt;
    height: 405pt;
    font-family: Arial, "Microsoft YaHei", sans-serif;
    overflow: hidden;
    position: relative;
}
.slide-light {
    background-color: #F5F5F5;
    color: #2D3436;
}
.slide-dark {
    background-color: #2D3436;
    color: #FFFFFF;
}
.top-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 46pt;
    background: #2D3436;
    z-index: 2;
    display: flex;
    align-items: center;
    padding: 0 30pt;
}
.top-title {
    color: #FFFFFF;
    font-size: 15pt;
    font-weight: bold;
}
.orange-dot {
    width: 8pt;
    height: 8pt;
    background: #EA5504;
    border-radius: 50%;
    display: inline-block;
    margin-right: 10pt;
}
.slide-num {
    position: absolute;
    right: 30pt;
    color: #EA5504;
    font-size: 9pt;
    font-weight: bold;
}
.logo-area {
    position: absolute;
    right: 16pt;
    bottom: 8pt;
    z-index: 10;
}
.content-area {
    position: absolute;
    top: 60pt; left: 30pt; right: 30pt; bottom: 20pt;
    display: flex;
    gap: 16pt;
}
p, li {
    font-size: 8.5pt;
    line-height: 1.5;
    margin: 0 0 5pt 0;
}
h2 {
    font-size: 11pt;
    font-weight: bold;
    margin: 0;
    padding: 0;
}
ul, ol {
    margin: 0;
    padding-left: 12pt;
}
li {
    margin-bottom: 4pt;
}
.col-3 {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 8pt;
}
.col-50 {
    width: 315pt;
    height: 100%;
}
.card-border {
    border: 1px solid #DCDDE1;
    background-color: #FFFFFF;
    padding: 12pt;
    border-radius: 6pt;
    height: 100%;
    display: flex;
    flex-direction: column;
}
.card-border.highlight {
    border: 2px solid #2d6a4f;
    box-shadow: 2px 2px 8px rgba(45, 106, 79, 0.15);
}
.card-green {
    background-color: #E8F5E9;
    border-left: 4pt solid #2d6a4f;
    padding: 10pt 12pt;
    border-radius: 4pt;
    margin-bottom: 6pt;
}
.card-orange {
    background-color: #FFF3EE;
    border-left: 4pt solid #EA5504;
    padding: 10pt 12pt;
    border-radius: 4pt;
    margin-bottom: 6pt;
}
`;

// 定义 Slide 01 到 Slide 12 的内容
const SLIDES_HTML = {
    // 01: 封面
    's01_cover.html': `<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; }
html { background: #1a1a2e; }
body {
  width: 720pt; height: 405pt; margin: 0; padding: 0;
  font-family: Arial, sans-serif;
  display: flex;
  position: relative;
  overflow: hidden;
}
.bg-left {
  width: 290pt;
  background: #2D3436;
  height: 100%;
  position: absolute;
  left: 0; top: 0;
  z-index: 1;
}
.accent-bar {
  position: absolute;
  left: 290pt;
  top: 0;
  width: 8pt;
  height: 100%;
  background: #EA5504;
  z-index: 2;
}
.bg-right {
  position: absolute;
  left: 298pt; right: 0; top: 0; bottom: 0;
  background: #F5F5F5;
  z-index: 1;
}
.left-content {
  position: absolute;
  left: 0; top: 0;
  width: 290pt; height: 405pt;
  z-index: 3;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 30pt 25pt;
}
.tag-line {
  background: #EA5504;
  color: #FFFFFF;
  padding: 4pt 10pt;
  font-size: 8pt;
  font-weight: bold;
  letter-spacing: 2pt;
  display: inline-block;
  margin-bottom: 12pt;
  width: fit-content;
}
.main-title {
  color: #FFFFFF;
  font-size: 20pt;
  font-weight: bold;
  line-height: 1.3;
  margin-bottom: 8pt;
}
.sub-title {
  color: #EA5504;
  font-size: 10pt;
  font-weight: bold;
  margin-bottom: 12pt;
}
.desc {
  color: #AAAAAA;
  font-size: 8.5pt;
  line-height: 1.5;
  border-top: 1pt solid rgba(255,255,255,0.12);
  padding-top: 8pt;
}
.meta-row {
  position: absolute;
  bottom: 20pt;
  left: 25pt;
  color: #777777;
  font-size: 7.5pt;
}
.right-content {
  position: absolute;
  left: 315pt; right: 15pt;
  top: 15pt; bottom: 15pt;
  z-index: 3;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.kpi-block {
  background: #FFFFFF;
  border-radius: 6pt;
  padding: 8pt 12pt;
  border-left: 4pt solid #EA5504;
}
.kpi-num {
  font-size: 18pt;
  font-weight: bold;
  color: #2D3436;
  line-height: 1.1;
  margin-bottom: 2pt;
}
.kpi-label {
  font-size: 8pt;
  color: #666666;
  margin: 0;
}
.kpi-sub {
  font-size: 7.5pt;
  color: #999999;
  margin: 2pt 0 0 0;
}
.kpi-row {
  display: flex;
  gap: 8pt;
}
.kpi-block-small {
  flex: 1;
  background: #FFFFFF;
  border-radius: 6pt;
  padding: 6pt 8pt;
  border-top: 3pt solid #2d6a4f;
}
.kpi-num-small {
  font-size: 14pt;
  font-weight: bold;
  color: #2d6a4f;
  line-height: 1.1;
  margin-bottom: 2pt;
}
.scope-box {
  background: #2D3436;
  border-radius: 6pt;
  padding: 8pt 12pt;
}
.scope-title {
  color: #EA5504;
  font-size: 8.5pt;
  font-weight: bold;
  margin-bottom: 6pt;
}
.scope-list {
  margin: 0;
  padding-left: 10pt;
  color: #CCCCCC;
}
.scope-list li {
  font-size: 7.5pt;
  margin-bottom: 2pt;
  color: #CCCCCC;
}
</style>
</head>
<body>
<div class="bg-left"></div>
<div class="accent-bar"></div>
<div class="bg-right"></div>

<div class="left-content">
  <div class="tag-line"><p>CATEGORY INSIGHT REPORT</p></div>
  <div class="main-title"><p>发光壁饰绿植<br>环境灯市场洞察</p></div>
  <div class="sub-title"><p>Biophilic Wall Planters &amp; Sconces</p></div>
  <div class="desc">
    <p>覆盖 Artika · Mavinza · Etsy苔藓品类<br>The Mossiah · Hugbel 五大竞品深度解析<br>含社媒评价、价格带、渠道策略与研发建议</p>
  </div>
  <div class="meta-row">
    <p>品类开发调研部门 · Howstoday · 2025年</p>
  </div>
</div>

<div class="right-content">
  <div class="kpi-block">
    <p class="kpi-num">$29.9 – $399</p>
    <p class="kpi-label">欧美市场主流价格带</p>
    <p class="kpi-sub">平均溢价空间 200–300%</p>
  </div>
  <div class="kpi-row">
    <div class="kpi-block-small">
      <p class="kpi-num-small">5家</p>
      <p class="kpi-label">深度调研竞品</p>
    </div>
    <div class="kpi-block-small">
      <p class="kpi-num-small">3款</p>
      <p class="kpi-label">研发概念提案</p>
    </div>
    <div class="kpi-block-small">
      <p class="kpi-num-small">4+星</p>
      <p class="kpi-label">头部产品评分</p>
    </div>
  </div>
  <div class="scope-box">
    <p class="scope-title">▌ 调研覆盖维度</p>
    <ul class="scope-list">
      <li>产品规格 · 价格 · 渠道分布</li>
      <li>社媒声量 · 用户评价 · 痛点提炼</li>
      <li>消费人群画像 · 购买决策路径</li>
      <li>供应链透视 · 竞争格局分析</li>
      <li>差异化研发建议与概念设计</li>
    </ul>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 02: 调研背景与目标
    's02_background.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.context-card {
  background: #2D3436;
  border-radius: 8pt;
  padding: 14pt 16pt;
  flex: 1;
}
.card-title {
  border-bottom: 1pt solid rgba(255,255,255,0.1);
  padding-bottom: 5pt;
  margin-bottom: 8pt;
}
.card-title p {
  color: #EA5504;
  font-size: 9pt;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 1pt;
  margin: 0;
}
.card-body {
  color: #CCCCCC;
  font-size: 8.5pt;
  line-height: 1.55;
}
.card-body b {
  color: #FFFFFF;
}
.trigger-card {
  background: #FFFFFF;
  border-radius: 8pt;
  padding: 12pt 16pt;
  border-left: 5pt solid #EA5504;
}
.trigger-title {
  color: #2D3436;
  font-size: 9pt;
  font-weight: bold;
  margin-bottom: 7pt;
}
.scope-card {
  background: #FFFFFF;
  border-radius: 8pt;
  padding: 12pt 16pt;
  border-top: 4pt solid #2d6a4f;
}
.scope-title {
  color: #2d6a4f;
  font-size: 9pt;
  font-weight: bold;
  margin-bottom: 8pt;
}
.scope-table-row {
  display: flex;
  gap: 6pt;
  margin-bottom: 5pt;
}
.scope-label {
  color: #888888;
  font-size: 7.5pt;
  width: 70pt;
  flex-shrink: 0;
}
.scope-value {
  color: #2D3436;
  font-size: 7.5pt;
  font-weight: bold;
  flex: 1;
}
.product-box {
  background: #FFF3EE;
  border-radius: 8pt;
  padding: 12pt 16pt;
  border: 1pt solid #FFCCAA;
}
.product-title {
  color: #EA5504;
  font-size: 9pt;
  font-weight: bold;
  margin-bottom: 8pt;
}
.product-list {
  margin: 0;
  padding-left: 10pt;
}
.product-list li {
  color: #333333;
  font-size: 8pt;
  margin-bottom: 4pt;
}
.product-list li b {
  color: #2D3436;
}
.trigger-list {
  margin: 0;
  padding-left: 10pt;
}
.trigger-list li {
  color: #555555;
  font-size: 8pt;
  margin-bottom: 4pt;
}
.trigger-list li b {
  color: #2D3436;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">调研背景与目标</p>
  <p class="slide-num">01 / 10</p>
</div>

<div class="content-area">
  <div class="col-50" style="display: flex; flex-direction: column; gap: 10pt;">
    <div class="context-card">
      <div class="card-title"><p>▌ 调研触发背景</p></div>
      <p class="card-body">
        公司现有三款产品：<b>Mini USB Ivy Wall Ring</b>、<b>Wireless Sensor Moss Ring</b>、<b>Modular Smart Forest Wall</b>，均处于欧美发光壁饰绿植环境灯细分赛道。<br><br>
        为强化研发决策依据，需对标竞品生态，掌握<b>市场规模、消费偏好、渠道格局</b>与<b>技术差距</b>，为下一代产品迭代提供数据支撑。
      </p>
    </div>
    <div class="trigger-card">
      <p class="trigger-title">▌ 我们的三款在研产品</p>
      <ul class="trigger-list">
        <li><b>Mini USB Ivy Wall Ring</b>：USB 供电，常青藤仿植物圆环壁饰</li>
        <li><b>Wireless Sensor Moss Ring</b>：无线感应，真苔藓材质环形情景灯</li>
        <li><b>Modular Smart Forest Wall</b>：模块化拼接，IP65 防水户内外绿植壁饰</li>
      </ul>
    </div>
  </div>

  <div class="col-50" style="display: flex; flex-direction: column; gap: 10pt;">
    <div class="scope-card">
      <p class="scope-title">▌ 调研范围 &amp; 方法</p>
      <div class="scope-table-row">
        <p class="scope-label">调研市场</p>
        <p class="scope-value">欧美（美国/加拿大/欧洲）</p>
      </div>
      <div class="scope-table-row">
        <p class="scope-label">竞品来源</p>
        <p class="scope-value">直营官网 + 亚马逊 + Etsy</p>
      </div>
      <div class="scope-table-row">
        <p class="scope-label">渠道维度</p>
        <p class="scope-value">DTC / Amazon / 手工艺电商</p>
      </div>
      <div class="scope-table-row">
        <p class="scope-label">数据来源</p>
        <p class="scope-value">官网定价 + 社媒评价挖掘</p>
      </div>
      <div class="scope-table-row">
        <p class="scope-label">调研时间</p>
        <p class="scope-value">2025年第二季度</p>
      </div>
    </div>
    <div class="product-box">
      <p class="product-title">▌ 核心调研问题</p>
      <ul class="product-list">
        <li><b>Q1：</b>竞品如何定价？主要价格带分布？</li>
        <li><b>Q2：</b>消费者核心诉求和痛点是什么？</li>
        <li><b>Q3：</b>主流购买渠道与决策路径？</li>
        <li><b>Q4：</b>我方产品的研发差异化空间？</li>
      </ul>
    </div>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 03: 欧美品类矩阵 (核心产品定位与售价)
    's03_matrix_specs1.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">欧美品类矩阵：核心定位与价格带分布</p>
  <p class="slide-num">02 / 10</p>
</div>

<div class="content-area">
  <!-- 低端极简 -->
  <div class="col-3">
    <div class="card-border">
      <p style="font-size: 8pt; color: #7F8C8D; font-weight: bold; margin-bottom: 2pt;">低端极简有线档</p>
      <div style="border-bottom: 2px solid #DCDDE1; padding-bottom: 4pt; margin-bottom: 6pt;">
        <h2 style="color: #2D3436; font-size: 11pt;">极简有线 / 漫射照明</h2>
      </div>
      <p style="margin-top: 4pt;"><b>核心产品定位：</b></p>
      <p style="color: #555;">极简壁挂式环境灯，提供基础氛围背光。以金属或塑料环形为主，通常需要外挂USB线或预留墙体硬线。</p>
      <p style="margin-top: 4pt;"><b>代表售价区间：</b></p>
      <p style="color: #E74C3C; font-size: 11pt; font-weight: bold;">$59.99 – $79.99 USD</p>
      <ul>
        <li>Artika Bloomfield/Halo: $59.99</li>
        <li>Mavinza 18W Wall Lamp: $79.99</li>
        <li>以极致性价比在建材超市和独立站起量走量。</li>
      </ul>
    </div>
  </div>
  
  <!-- 中端苔藓 -->
  <div class="col-3">
    <div class="card-border highlight">
      <p style="font-size: 8pt; color: #2d6a4f; font-weight: bold; margin-bottom: 2pt;">中端高溢价核心档</p>
      <div style="border-bottom: 2px solid #2d6a4f; padding-bottom: 4pt; margin-bottom: 6pt;">
        <h2 style="color: #2d6a4f; font-size: 11pt;">天然永生 / 艺术美学</h2>
      </div>
      <p style="margin-top: 4pt;"><b>核心产品定位：</b></p>
      <p style="color: #555;">亲生命植物氛围灯，融合法国进口永生苔藓、枯木等天然材质，以温暖漫射背光为主，主打高溢价家居软装艺术品。</p>
      <p style="margin-top: 4pt;"><b>代表售价区间：</b></p>
      <p style="color: #2d6a4f; font-size: 11pt; font-weight: bold;">$190.00 – $1,080.00+ USD</p>
      <ul>
        <li>The Mossiah Mood Lamp: ~$190</li>
        <li>Etsy MrwoodstudioUA: $231 – $1,080+</li>
        <li>主打高端手工定制、礼品与场景体验溢价。</li>
      </ul>
    </div>
  </div>
  
  <!-- 高端防水 -->
  <div class="col-3">
    <div class="card-border">
      <p style="font-size: 8pt; color: #7F8C8D; font-weight: bold; margin-bottom: 2pt;">高端工装与阳台档</p>
      <div style="border-bottom: 2px solid #DCDDE1; padding-bottom: 4pt; margin-bottom: 6pt;">
        <h2 style="color: #2D3436; font-size: 11pt;">几何工业 / 场景延伸</h2>
      </div>
      <p style="margin-top: 4pt;"><b>核心产品定位：</b></p>
      <p style="color: #555;">半户外与庭院防水置物架壁挂灯。采用黑色压铸铝几何大框架，具备高承重置物板与IP65防雨，拓展至阳台庭院。</p>
      <p style="margin-top: 4pt;"><b>代表售价区间：</b></p>
      <p style="color: #D35400; font-size: 11pt; font-weight: bold;">~$250.00 USD</p>
      <ul>
        <li>Hugbel Hexagonal Sconce: ~$250</li>
        <li>依据 40/60/80cm 尺寸形成价格带</li>
        <li>工装和高档住宅阳台背景墙首选。</li>
      </ul>
    </div>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 04: 欧美品类矩阵 (光源规格与核心材质工艺)
    's04_matrix_specs2.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">欧美品类矩阵：光源与核心材质工艺</p>
  <p class="slide-num">03 / 10</p>
</div>

<div class="content-area">
  <!-- 低端极简 -->
  <div class="col-3">
    <div class="card-border">
      <p style="font-size: 8pt; color: #7F8C8D; font-weight: bold; margin-bottom: 2pt;">低端极简有线档</p>
      <div style="border-bottom: 2px solid #DCDDE1; padding-bottom: 4pt; margin-bottom: 6pt;">
        <h2 style="color: #2D3436; font-size: 11pt;">有线低压 / 仿真假植</h2>
      </div>
      <p style="margin-top: 4pt;"><b>光源与电源规格：</b></p>
      <p style="color: #555;">18W 左右集成 LED，支持多档色温。无内置电池，需外接 Micro-USB 线或预留墙体电线，拖线破坏美观。</p>
      <p style="margin-top: 4pt;"><b>核心材质与工艺：</b></p>
      <p style="color: #555;">铁艺烤漆（哑光黑）、铝合金外壳或ABS塑料。绿植主要为仿真塑料常青藤或空盆，工业质感一般。</p>
    </div>
  </div>
  
  <!-- 中端苔藓 -->
  <div class="col-3">
    <div class="card-border highlight">
      <p style="font-size: 8pt; color: #2d6a4f; font-weight: bold; margin-bottom: 2pt;">中端高溢价核心档</p>
      <div style="border-bottom: 2px solid #2d6a4f; padding-bottom: 4pt; margin-bottom: 6pt;">
        <h2 style="color: #2d6a4f; font-size: 11pt;">锂电无线 / 永生真苔</h2>
      </div>
      <p style="margin-top: 4pt;"><b>光源与电源规格：</b></p>
      <p style="color: #555;">3W–5W 低功耗 LED。内置电池并配 USB-C 充电，免除拉线烦恼；支持三色无级调光与光敏/人感传感控制。</p>
      <p style="margin-top: 4pt;"><b>核心材质与工艺：</b></p>
      <p style="color: #555;">法国进口防腐永生苔藓，辅以天然软木皮、山藤与干树枝，纯手工贴花装配，具有极佳自然触感。</p>
    </div>
  </div>
  
  <!-- 高端防水 -->
  <div class="col-3">
    <div class="card-border">
      <p style="font-size: 8pt; color: #7F8C8D; font-weight: bold; margin-bottom: 2pt;">高端工装与阳台档</p>
      <div style="border-bottom: 2px solid #DCDDE1; padding-bottom: 4pt; margin-bottom: 6pt;">
        <h2 style="color: #2D3436; font-size: 11pt;">硬线高亮 / 压铸耐候</h2>
      </div>
      <p style="margin-top: 4pt;"><b>光源与电源规格：</b></p>
      <p style="color: #555;">12W–24W 集成高亮 LED，宽压适配墙体硬线。全环防水布线与高透防护罩，具备无感防眩光设计。</p>
      <p style="margin-top: 4pt;"><b>核心材质与工艺：</b></p>
      <p style="color: #555;">压铸铝合金灯体、户外氟碳抗UV耐腐蚀涂层喷砂、IP65 防尘防水等级。置物架具有高强度负重结构。</p>
    </div>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 05: 行业痛点与消费者 VOC 深度挖掘 (VOC & Pain Points)
    's05_voc_painpoints.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.col-left {
    width: 250pt;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}
.col-right {
    width: 410pt;
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 8pt;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">行业痛点与消费者 VOC 深度挖掘</p>
  <p class="slide-num">04 / 10</p>
</div>

<div class="content-area" style="justify-content: space-between;">
  <!-- 左栏：原生饼图占位符 -->
  <div class="col-left">
    <p style="font-size: 9.5pt; font-weight: bold; color: #2D3436; margin-bottom: 12pt; text-align: center;">欧美发光绿植墙饰差评成因分析</p>
    <div id="voc-planters-chart" class="placeholder" style="width: 240pt; height: 180pt; background-color: #EFEFEF; border: 1px dashed #CCCCCC; border-radius: 6pt;"></div>
  </div>
  
  <!-- 右栏：四大核心痛点解析 -->
  <div class="col-right">
    <div class="card-orange" style="margin-bottom: 4pt;">
      <h2 style="color: #D35400; font-size: 9.5pt; margin-bottom: 2pt;">1. 线缆外露，破坏极简美学 (占比 40%)</h2>
      <p style="color: #555; margin: 0;">有线款在未预留暗线时，长垂USB线极其难看，而干电池款 2 周就耗尽，用户频繁换电体验极差。</p>
    </div>
    
    <div class="card-orange" style="margin-bottom: 4pt;">
      <h2 style="color: #D35400; font-size: 9.5pt; margin-bottom: 2pt;">2. LED 烘烤导致植物加速干枯变黄 (占比 30%)</h2>
      <p style="color: #555; margin: 0;">灯具普遍缺乏散热垫和对流风道，光照与热阻效应使活体植物水分蒸干，假植塑料叶片也极易老化异味。</p>
    </div>
    
    <div class="card-orange" style="margin-bottom: 4pt;">
      <h2 style="color: #D35400; font-size: 9.5pt; margin-bottom: 2pt;">3. 结构封死积灰，无法水冲清洗 (占比 20%)</h2>
      <p style="color: #555; margin: 0;">仿真叶片和永生苔藓极易积尘，但电路与植物被热熔胶焊死，不能直接摘下清洗，导致墙饰蒙灰泛黑。</p>
    </div>
    
    <div class="card-orange" style="margin-bottom: 0;">
      <h2 style="color: #D35400; font-size: 9.5pt; margin-bottom: 2pt;">4. 高端手作无法量产，极易潮湿发霉 (占比 10%)</h2>
      <p style="color: #555; margin: 0;">Etsy 等手工苔藓墙价格突破几百美金，且防潮性极低，雨季极易吸水滋生霉菌，缺乏智能环境自调节。</p>
    </div>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 06: 欧美市场机会与三大产品真空带 (Gap Analysis)
    's06_gap_analysis.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.gap-card {
    background: #FFFFFF;
    border: 1px solid #DCDDE1;
    border-radius: 6pt;
    padding: 10pt 14pt;
    flex: 1;
    display: flex;
    flex-direction: column;
    border-left: 5pt solid #2d6a4f;
}
.gap-card.orange {
    border-left-color: #EA5504;
}
.gap-tag {
    font-size: 7.5pt;
    font-weight: bold;
    color: #FFFFFF;
    background-color: #2d6a4f;
    padding: 2pt 6pt;
    border-radius: 3pt;
    width: fit-content;
    margin-bottom: 6pt;
}
.gap-tag.orange {
    background-color: #EA5504;
}
.gap-desc {
    color: #555555;
    font-size: 8.5pt;
    line-height: 1.5;
    margin: 4pt 0 0 0;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">欧美市场机会与三大产品空白点诊断</p>
  <p class="slide-num">05 / 10</p>
</div>

<div class="content-area" style="gap: 12pt;">
  <!-- 空白点 1 -->
  <div class="gap-card">
    <span class="gap-tag">价格与技术真空</span>
    <h2 style="color: #2D3436; margin: 0;">$100 - $180 轻奢级无线智能灯断档</h2>
    <p class="gap-desc">低端 $50 塑料灯与 Etsy $300+ 手工苔藓画之间存在价格真空。以高质感金属/实木工艺，辅以锂电和 PIR 人体感应，可实现墙面无线净化，满足中产家庭“轻硬装重软装”需求。</p>
  </div>
  
  <!-- 空白点 2 -->
  <div class="gap-card orange">
    <span class="gap-tag orange">功能与促生真空</span>
    <h2 style="color: #2D3436; margin: 0;">双向光源融合缺失（补光 + 氛围）</h2>
    <p class="gap-desc">现有灯具只提供单一的 3000K 漫射光，缺乏特制植物促生光谱（Grow Light）。设计内圈提供高显指全光谱促生光、外圈提供暖白氛围光的“双向补光绿植环”是活性活体盆栽上墙的关键。</p>
  </div>
  
  <!-- 空白点 3 -->
  <div class="gap-card">
    <span class="gap-tag">工装与场景真空</span>
    <h2 style="color: #2D3436; margin: 0;">免接线“积木拼接”模块森林墙空白</h2>
    <p class="gap-desc">大型苔藓画沉重且不便物流，布线极其昂贵。开发六角形标准铝框模块，边缘镶嵌强磁导电极片，拼接直接通电，支持 APP 调光及浇灌定时提醒，能颠覆性降低高端商用施工成本。</p>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 07: R&D 提案一：无线智能感应苔藓环 (Aero-Moss Wireless Smart Sconce)
    's07_concept_aero.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.concept-details {
    display: flex;
    flex-direction: column;
    gap: 8pt;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">研发提案一：无线智能感应苔藓环 (Aero-Moss)</p>
  <p class="slide-num">06 / 10</p>
</div>

<div class="content-area">
  <!-- 左栏：规格文本 -->
  <div class="col-50">
    <div class="card-border highlight" style="padding: 16pt;">
      <span style="font-size: 8pt; background-color: #E8F5E9; color: #2d6a4f; padding: 2pt 6pt; border-radius: 3pt; font-weight: bold; width: fit-content; margin-bottom: 6pt;">主力推荐 · 中端高毛利</span>
      <h2 style="font-size: 13pt; color: #2d6a4f; margin-bottom: 10pt;">Aero-Moss Wireless Smart Sconce</h2>
      
      <div class="concept-details">
        <p><b>商业定位：</b>玄关/走廊无线环境照明与高端绿植软装</p>
        <p><b>成本定价：</b>出厂成本约 <b>$10.30</b> / 套，对标欧美零售价 <b>$69 - $89</b></p>
        
        <div style="margin-top: 4pt; border-top: 1px solid #E2E8F0; padding-top: 8pt;">
          <p style="font-weight: bold; color: #2d6a4f; margin: 0 0 6pt 0;">▌ 核心降维技术突破</p>
        </div>
        <ul>
          <li><b>双感应低功耗主控</b>：集成人体红外(PIR)与环境光敏(LDR)，静态电流 < 5uA，暗光下人来即亮，渐亮渐熄，实现墙面无线净化。</li>
          <li><b>超长无线电池续航</b>：内置 2000mAh 聚合物锂电池，支持 Type-C 快充。在日常感应模式下，一次充电可无线续航 6 个月。</li>
          <li><b>卡扣式无胶滑槽结构</b>：铝圈内侧微型轨道定位，仿真假植及永生苔藓配重件可滑入卡紧，10秒无损拆卸，可直接浸水冲洗积尘。</li>
        </ul>
      </div>
    </div>
  </div>
  
  <!-- 右栏：概念设计图 -->
  <div class="col-50" style="display: flex; justify-content: center; align-items: center; background-color: #FFFFFF; border-radius: 6pt; border: 1px solid #DCDDE1; overflow: hidden; padding: 6pt;">
    <img src="../images/wireless_moss_ring.png" style="max-width: 100%; max-height: 290pt; object-fit: contain; border-radius: 4pt; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 08: R&D 提案二：生态双光源活性植物环 (Biophilic Dual-Light Active Ring)
    's08_concept_biophilic.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.concept-details {
    display: flex;
    flex-direction: column;
    gap: 8pt;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">研发提案二：生态双光源活性植物环 (Dual-Light)</p>
  <p class="slide-num">07 / 10</p>
</div>

<div class="content-area">
  <!-- 左栏：规格文本 -->
  <div class="col-50">
    <div class="card-border" style="padding: 16pt; border-left: 4pt solid #EA5504;">
      <span style="font-size: 8pt; background-color: #FFF3EE; color: #EA5504; padding: 2pt 6pt; border-radius: 3pt; font-weight: bold; width: fit-content; margin-bottom: 6pt;">生态极客 · 高端科技线</span>
      <h2 style="font-size: 13pt; color: #EA5504; margin-bottom: 10pt;">Biophilic Dual-Light Active Ring</h2>
      
      <div class="concept-details">
        <p><b>商业定位：</b>专为挂墙活性真植（如气生、多肉）设计的双向光源床灯</p>
        <p><b>成本定价：</b>出厂成本约 <b>$22.00</b> / 套，对标欧美零售价 <b>$180+</b></p>
        
        <div style="margin-top: 4pt; border-top: 1px solid #E2E8F0; padding-top: 8pt;">
          <p style="font-weight: bold; color: #EA5504; margin: 0 0 6pt 0;">▌ 核心降维技术突破</p>
        </div>
        <ul>
          <li><b>双向分立促生/环境光谱</b>：后侧内藏 2200K 漫射暖光氛围，前内侧向下集成 5000K 高显指(CRI 97)植物补光 LED，促进植物健康生长。</li>
          <li><b>隐形空气散热导流槽</b>：灯环采用型材弯铝工艺，背面铝板开设对流孔。灯带导热垫紧贴铝型材，灯体温升控制在5°C以内，防止绿植受热干瘪。</li>
          <li><b>磁吸式快拆不锈钢托盘</b>：盆钵以高强钕铁硼磁吸模块与灯体固定，一拉即可轻松摘下清洗，彻底解决灌溉难、积尘滴水的痛点。</li>
        </ul>
      </div>
    </div>
  </div>
  
  <!-- 右栏：概念设计图 -->
  <div class="col-50" style="display: flex; justify-content: center; align-items: center; background-color: #FFFFFF; border-radius: 6pt; border: 1px solid #DCDDE1; overflow: hidden; padding: 6pt;">
    <img src="../images/biophilic_active_ring.png" style="max-width: 100%; max-height: 290pt; object-fit: contain; border-radius: 4pt; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 09: R&D 提案三：几何拼接模块智能森林墙 (Hexa-Forest Modular Smart Wall)
    's09_concept_hexa.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.concept-details {
    display: flex;
    flex-direction: column;
    gap: 8pt;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">研发提案三：几何拼接模块智能森林墙 (Hexa-Forest)</p>
  <p class="slide-num">08 / 10</p>
</div>

<div class="content-area">
  <!-- 左栏：规格文本 -->
  <div class="col-50">
    <div class="card-border" style="padding: 16pt; border-left: 4pt solid #2D3436;">
      <span style="font-size: 8pt; background-color: #E2E8F0; color: #2D3436; padding: 2pt 6pt; border-radius: 3pt; font-weight: bold; width: fit-content; margin-bottom: 6pt;">工装硬线 · 别墅阳台系统</span>
      <h2 style="font-size: 13pt; color: #2D3436; margin-bottom: 10pt;">Hexa-Forest Modular Smart Wall</h2>
      
      <div class="concept-details">
        <p><b>商业定位：</b>写字楼大堂、别墅、咖啡馆外墙磁吸拼接智能置物森林墙</p>
        <p><b>成本定价：</b>出厂价约 <b>$35.00</b> / 单元，对标欧美工程单价 <b>$150+</b> / 单元</p>
        
        <div style="margin-top: 4pt; border-top: 1px solid #E2E8F0; padding-top: 8pt;">
          <p style="font-weight: bold; color: #2D3436; margin: 0 0 6pt 0;">▌ 核心降维技术突破</p>
        </div>
        <ul>
          <li><b>边缘磁吸电极无线通电</b>：正六边形压铸铝框，拼接时模块边缘触点自动锁紧通电，仅需引入一路电源线，大幅节约布线施工成本。</li>
          <li><b>全天候 IP65 级户外耐候</b>：结构全密封阻胶走线，氟碳抗UV涂层，配以防霉阻燃仿真聚氨酯假植，抗狂风暴雨暴晒。</li>
          <li><b>IoT 智控与高承重置物板</b>：置物槽承重达 10kg，APP/涂鸦智控色彩；内置低功耗湿度传感器，土壤干燥自动报警推送。</li>
        </ul>
      </div>
    </div>
  </div>
  
  <!-- 右栏：概念设计图 -->
  <div class="col-50" style="display: flex; justify-content: center; align-items: center; background-color: #FFFFFF; border-radius: 6pt; border: 1px solid #DCDDE1; overflow: hidden; padding: 6pt;">
    <img src="../images/modular_forest_wall.png" style="max-width: 100%; max-height: 290pt; object-fit: contain; border-radius: 4pt; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 10: 供应链协同与生产基地协同布局 (Supply Chain)
    's10_supply_chain.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.sc-card {
    background: #FFFFFF;
    border: 1px solid #DCDDE1;
    border-radius: 6pt;
    padding: 12pt;
    flex: 1;
}
.sc-title {
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 4pt;
    margin-bottom: 8pt;
}
.sc-title p {
    font-size: 10pt;
    font-weight: bold;
    color: #2d6a4f;
    margin: 0;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">供应链协同与“中山电控+东莞假植”跨界闭环</p>
  <p class="slide-num">09 / 10</p>
</div>

<div class="content-area" style="gap: 14pt;">
  <!-- 中山优势 -->
  <div class="sc-card" style="border-top: 4pt solid #EA5504;">
    <div class="sc-title"><p style="color: #EA5504;">▌ 中山：五金拉弯与电控核心优势</p></div>
    <ul>
      <li style="margin-bottom: 6pt;"><b>型材拉弯五金成本压降</b>：发挥古镇及周边型材铝挤、拉弯、喷涂工艺，将灯圈五金框成本控制在 <b>$4.00</b> 以内。</li>
      <li style="margin-bottom: 6pt;"><b>智能低功耗主控集成</b>：基于中山成熟的LED板贴片配套，定制 PIR+LDR 低功耗芯片和电池管理，将双感应电控板成本压缩至 <b>$2.60</b>。</li>
      <li style="margin-bottom: 0;"><b>低压锂电池集成封测</b>：采购优质大牌A级聚合物锂包，由中山总装厂协同完成密闭阻燃壳体封测，保障产品充放电安全。</li>
    </ul>
  </div>
  
  <!-- 东莞/惠州优势 -->
  <div class="sc-card" style="border-top: 4pt solid #2d6a4f;">
    <div class="sc-title"><p style="color: #2d6a4f;">▌ 东莞/惠州：仿真绿植与模具积淀</p></div>
    <ul>
      <li style="margin-bottom: 6pt;"><b>高仿真哑光过胶叶面</b>：利用横沥/石排仿真植物制造基地，叶片触感肉质逼真、色牢度高、抗紫外线。单套假植配件成本低至 <b>$2.20</b>。</li>
      <li style="margin-bottom: 6pt;"><b>滑轨卡座注塑预埋工艺</b>：在绿植枝干注塑阶段，精密预埋耐磨卡接底座。该模具配合铝框内轨滑槽实现10秒卡入无损快拆。</li>
      <li style="margin-bottom: 0;"><b>一站式跨界总装出运</b>：东莞配件寄至中山，在中山总装厂完成灯串走线卡装、全检测试、彩盒打包，由中山一站式发往港口。</li>
    </ul>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 11: 欧美市场安全准入、防灾红线与开发路线图 (Compliance & Roadmap)
    's11_compliance_end.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.roadmap-step {
    border-left: 3px solid #2d6a4f;
    padding-left: 10pt;
    margin-bottom: 8pt;
    position: relative;
}
.roadmap-dot {
    width: 9pt;
    height: 9pt;
    background-color: #2d6a4f;
    border-radius: 50%;
    position: absolute;
    left: -6pt;
    top: 2pt;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar">
  <div class="orange-dot"></div>
  <p class="top-title">欧美市场准入合规红线与开发路线图</p>
  <p class="slide-num">10 / 10</p>
</div>

<div class="content-area">
  <!-- 左栏：安规准入 -->
  <div class="col-50">
    <div class="card-border" style="padding: 14pt;">
      <div style="border-bottom: 2px solid #E2E8F0; padding-bottom: 4pt; margin-bottom: 10pt;">
        <h2 style="color: #2D3436; font-size: 10pt;">▌ 欧美商超与大型项目安规消防红线</h2>
      </div>
      <ul>
        <li style="margin-bottom: 8pt;"><b>美国超市 B2C 门槛</b>：电学部分需通过 <b>UL 153</b> (便携式灯具) 或 <b>UL 588</b> (节日彩灯串) 认证；低压锂电需满足 UN 38.3。电池盒需螺丝双锁防儿童误吞。</li>
        <li style="margin-bottom: 8pt;"><b>欧盟 REACH 与 RoHS 指令</b>：作为常态室内挂饰，严格限制仿真植物增塑剂（邻苯二甲酸酯类）超标，PU 材质必须符合欧盟环保标准。</li>
        <li style="margin-bottom: 0;"><b>高端工装消防生死红线</b>：写字楼/酒店商用拼接绿墙必须通过英国 <b>BS5852</b> 防火烟测，或美国 <b>NFPA 701</b> 阻燃等级（注塑中添加阻燃母粒）。</li>
      </ul>
    </div>
  </div>
  
  <!-- 右栏：开发路线图 -->
  <div class="col-50">
    <div class="card-border" style="padding: 14pt; border-left: 4pt solid #2d6a4f;">
      <div style="border-bottom: 2px solid #2d6a4f; padding-bottom: 4pt; margin-bottom: 12pt;">
        <h2 style="color: #2d6a4f; font-size: 10pt;">▌ 研发量产出海路线规划 (全周期 6 个月)</h2>
      </div>
      
      <div class="roadmap-step">
        <div class="roadmap-dot"></div>
        <p style="font-weight: bold; margin-bottom: 1pt; color: #2D3436;">第 1-2 个月：打样测试与假植开模</p>
        <p style="color: #666; margin: 0;">完成中山超低功耗(PIR+LDR)感应板调试；东莞厂完成卡扣假植枝干的注塑开模与快拆拼装测试。</p>
      </div>
      
      <div class="roadmap-step">
        <div class="roadmap-dot"></div>
        <p style="font-weight: bold; margin-bottom: 1pt; color: #2D3436;">第 3 个月：送检认证与可靠性环境测试</p>
        <p style="color: #666; margin: 0;">制作首批成品送样。申请 UL 588、REACH 等报告；工装阻燃假叶送检消防防火等级，中高端型号做 IP65 淋雨及高低温测试。</p>
      </div>
      
      <div class="roadmap-step" style="margin-bottom: 0;">
        <div class="roadmap-dot"></div>
        <p style="font-weight: bold; margin-bottom: 1pt; color: #2D3436;">第 4-6 个月：买手对接与海外众筹发货</p>
        <p style="color: #666; margin: 0;">送样美国 Costco、Lowe's 采购部；首批货于 Wayfair 众筹首发以迭代软件调光算法；通过后展开超市大宗量产分销。</p>
      </div>
    </div>
  </div>
</div>

<div class="logo-area">
  <img src="../images/logo-orange.png" style="width: 60pt; height: auto;">
</div>
</body>
</html>`,

    // 12: 结束页 (slide12.html)
    's12_thanks_page.html': `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.cover-container {
    padding: 60pt 45pt;
    width: 720pt;
    height: 405pt;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
</style>
</head>
<body class="slide-dark">
<div class="top-bar"></div>
<div class="cover-container" style="justify-content: center; align-items: center; text-align: center;">
    <div>
        <p style="font-size: 13pt; color: #EA5504; font-weight: bold; margin-bottom: 15pt; text-transform: uppercase; letter-spacing: 2px;">Ningbo Howstoday Imp. & Exp. Co., Ltd.</p>
        <h1 style="font-size: 30pt; font-weight: bold; line-height: 1.3; color: #FFFFFF; margin-bottom: 15pt;">汇报完毕，谢谢观看</h1>
        <p style="font-size: 11pt; color: #BDC5C9; margin-top: 10pt; line-height: 1.6;">发光壁饰绿植环境灯 (Biophilic Wall Planters) 欧美市场品类洞察<br>Howstoday 品类开发汇报小组</p>
    </div>
</div>
<img src="../images/logo-white.png" class="logo-img" style="position: absolute; right: 25pt; bottom: 12pt; height: 18pt; width: auto;">
</body>
</html>`
};

// 主执行函数
async function main() {
    console.log('开始写入 HTML slide 文件...');
    
    // 写入 Slide 01 到 Slide 12
    for (const [filename, htmlContent] of Object.entries(SLIDES_HTML)) {
        const filepath = path.join(OUTPUT_SLIDES_DIR, filename);
        fs.writeFileSync(filepath, htmlContent, 'utf-8');
        console.log(`已写入: ${filepath}`);
    }

    console.log('\n开始初始化 PptxGenJS 并转换为 PPTX...');
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Howstoday Project Team';
    pptx.title = 'Biophilic Wall Planters Market Insight';

    // 构建一个幻灯片路径列表
    const slideFiles = [
        { name: 's01_cover.html', path: path.join(OUTPUT_SLIDES_DIR, 's01_cover.html') },
        { name: 's02_background.html', path: path.join(OUTPUT_SLIDES_DIR, 's02_background.html') },
        { name: 's03_matrix_specs1.html', path: path.join(OUTPUT_SLIDES_DIR, 's03_matrix_specs1.html') },
        { name: 's04_matrix_specs2.html', path: path.join(OUTPUT_SLIDES_DIR, 's04_matrix_specs2.html') },
        { name: 's05_voc_painpoints.html', path: path.join(OUTPUT_SLIDES_DIR, 's05_voc_painpoints.html') },
        { name: 's06_gap_analysis.html', path: path.join(OUTPUT_SLIDES_DIR, 's06_gap_analysis.html') },
        { name: 's07_concept_aero.html', path: path.join(OUTPUT_SLIDES_DIR, 's07_concept_aero.html') },
        { name: 's08_concept_biophilic.html', path: path.join(OUTPUT_SLIDES_DIR, 's08_concept_biophilic.html') },
        { name: 's09_concept_hexa.html', path: path.join(OUTPUT_SLIDES_DIR, 's09_concept_hexa.html') },
        { name: 's10_supply_chain.html', path: path.join(OUTPUT_SLIDES_DIR, 's10_supply_chain.html') },
        { name: 's11_compliance_end.html', path: path.join(OUTPUT_SLIDES_DIR, 's11_compliance_end.html') },
        { name: 's12_thanks_page.html', path: path.join(OUTPUT_SLIDES_DIR, 's12_thanks_page.html') }
    ];

    // 转换每一页 HTML
    for (let i = 0; i < slideFiles.length; i++) {
        const fileObj = slideFiles[i];
        console.log(`\n[Slide ${i + 1}/${slideFiles.length}] 正在处理 ${fileObj.name}...`);
        
        try {
            const { slide, placeholders } = await html2pptx(fileObj.path, pptx);
            console.log(`[Slide ${i + 1}] HTML 转换成功。发现 ${placeholders.length} 个占位符。`);
            
            // 针对第 5 页 (s05_voc_painpoints.html)，添加原生饼图
            if (fileObj.name === 's05_voc_painpoints.html') {
                const chartArea = placeholders.find(p => p.id === 'voc-planters-chart');
                if (chartArea) {
                    console.log(`[Slide ${i + 1}] 正在将原生饼图添加到占位符: voc-planters-chart`);
                    
                    const pieData = [{
                        name: '差评原因',
                        labels: [
                            '线缆外露/频繁换电(40%)', 
                            '灯珠发热植物焦黄(30%)', 
                            '结构固定积灰难拆洗(20%)', 
                            '手作苔藓易霉难量产(10%)'
                        ],
                        values: [40, 30, 20, 10]
                    }];
                    
                    // 确保颜色不带 '#' 前缀
                    slide.addChart(pptx.charts.PIE, pieData, {
                        x: chartArea.x,
                        y: chartArea.y,
                        w: chartArea.w,
                        h: chartArea.h,
                        showPercent: true,
                        showLegend: true,
                        legendPos: 'r',
                        legendFontSize: 8,
                        chartColors: ['EA5504', '2d6a4f', '2D3436', '7F8C8D']
                    });
                    console.log(`[Slide ${i + 1}] 原生饼图绘制完成。`);
                } else {
                    console.error(`[Slide ${i + 1}] 未找到占位符: voc-planters-chart`);
                }
            }
        } catch (err) {
            console.error(`[Slide ${i + 1}] 转换失败:`, err);
            process.exit(1);
        }
    }

    const outputPptx = path.join(SCRATCH_DIR, 'lighted-wall-planters-presentation.pptx');
    console.log(`\n全部幻灯片转换成功。开始保存 PPT 到 ${outputPptx}...`);
    try {
        await pptx.writeFile({ fileName: outputPptx });
        console.log('PowerPoint 汇报文稿成功生成！');
        
        // 复制一份到工作区根目录下，方便用户直接获取
        const destPath = 'd:/我的APP/品类开发调研/lighted-wall-planters-presentation.pptx';
        fs.copyFileSync(outputPptx, destPath);
        console.log(`已成功将 PPT 复制到工作区目标路径: ${destPath}`);
    } catch (writeErr) {
        console.error('保存 PPT 失败:', writeErr);
        process.exit(1);
    }
}

main().catch(console.error);
