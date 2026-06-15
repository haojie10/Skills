const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');
const html2pptx = require('./html2pptx.js');

// 基础常量
const SCRATCH_DIR = 'C:/Users/066/.gemini/antigravity/brain/d160cf64-2927-4f09-808d-8f1c50f0a2a7/scratch';
const SLIDES_DIR = path.join(SCRATCH_DIR, 'slides');
const IMAGES_DIR = 'images';

// 确保 slides 目录存在
if (!fs.existsSync(SLIDES_DIR)) {
    fs.mkdirSync(SLIDES_DIR, { recursive: true });
}

// 公共 CSS 样式
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
    background-color: #FFFFFF;
    color: #2D3436;
}
.slide-dark {
    background-color: #2D3436;
    color: #FFFFFF;
}
.top-bar {
    position: absolute;
    top: 0;
    left: 0;
    width: 720pt;
    height: 4pt;
    background-color: #EA5504;
}
h1 {
    font-size: 20pt;
    font-weight: bold;
    margin: 0;
    padding: 0;
}
.light-title {
    color: #2D3436;
}
.dark-title {
    color: #FFFFFF;
}
h2 {
    font-size: 13pt;
    font-weight: bold;
    margin: 0 0 6pt 0;
    padding: 0;
}
.light-subtitle {
    color: #EA5504;
}
.dark-subtitle {
    color: #EA5504;
}
p, li {
    font-size: 10pt;
    line-height: 1.5;
    margin: 0 0 6pt 0;
}
ul, ol {
    margin: 0;
    padding-left: 15pt;
}
li {
    margin-bottom: 4pt;
}
.container {
    padding: 25pt 35pt 20pt 35pt;
    width: 720pt;
    height: 405pt;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}
.header-area {
    height: 35pt;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #DCDDE1;
    margin-bottom: 12pt;
}
.header-area-dark {
    height: 35pt;
    display: flex;
    align-items: center;
    border-bottom: 1px solid #4A5568;
    margin-bottom: 12pt;
}
.content-area {
    height: 310pt;
    display: flex;
    flex-direction: row;
    justify-content: space-between;
}
.col-full {
    width: 650pt;
    height: 100%;
}
.col-left-45 {
    width: 290pt;
    height: 100%;
}
.col-right-55 {
    width: 345pt;
    height: 100%;
}
.col-left-50 {
    width: 315pt;
    height: 100%;
}
.col-right-50 {
    width: 315pt;
    height: 100%;
}
.col-left-55 {
    width: 345pt;
    height: 100%;
}
.col-right-45 {
    width: 290pt;
    height: 100%;
}
.card-gray {
    background-color: #F8F9FA;
    border-left: 4pt solid #EA5504;
    padding: 12pt;
    border-radius: 4pt;
    margin-bottom: 10pt;
}
.card-gray-dark {
    background-color: #2D3436;
    border-left: 4pt solid #EA5504;
    padding: 12pt;
    border-radius: 4pt;
    margin-bottom: 10pt;
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
    border: 2px solid #EA5504;
    box-shadow: 2px 2px 8px rgba(234, 85, 4, 0.15);
}
.logo-img {
    position: absolute;
    right: 25pt;
    bottom: 12pt;
    height: 15pt;
    width: auto;
}
`;

// 11 页幻灯片的数据定义
const SLIDES_DATA = [
    // 01: 封面页 (Dark)
    {
        filename: 'slide01.html',
        html: `<!DOCTYPE html>
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
<div class="cover-container">
    <div>
        <p style="font-size: 13pt; color: #EA5504; font-weight: bold; margin-bottom: 15pt; text-transform: uppercase; letter-spacing: 2px;">Howstoday 品类开发汇报</p>
        <h1 style="font-size: 26pt; font-weight: bold; line-height: 1.3; color: #FFFFFF; margin-bottom: 12pt;">发光壁挂绿植环 (LED Leaf Wall Rings)<br>欧美品类洞察与产品提案</h1>
        <p style="font-size: 12pt; color: #DCDDE1; margin-top: 10pt; line-height: 1.6;">打造轻资产、高附加值的家居壁饰，以照明技术赋能传统假植</p>
    </div>
    <div style="margin-top: 50pt; border-top: 1px solid #4A5568; padding-top: 15pt; display: flex; justify-content: space-between; align-items: center;">
        <p style="font-size: 10pt; color: #A4B0BE; margin: 0;">汇报部门：Howstoday 项目组 &nbsp;|&nbsp; 汇报时间：2026年6月</p>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-white.png" class="logo-img">
</body>
</html>`
    },
    // 02: 品类背景与市场潜力 (Light)
    {
        filename: 'slide02.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">1.0 品类勃兴：亲生命美学与壁挂环境光</h1>
    </div>
    <div class="content-area">
        <div class="col-left-45">
            <div class="card-gray" style="height: 100%;">
                <h2 class="light-subtitle">Biophilic Design 亲生命设计</h2>
                <p>欧美中产阶级正兴起“亲生命设计”家居热潮，追求免维护的绿色植物与温馨的间接照明（Ambient Lighting）的合二为一。</p>
                <p style="margin-top: 15pt;"><b>落地空间局限的最佳解：</b></p>
                <p>在高密度公寓住宅中，落地仿真树占用宝贵的地面空间。而发光壁挂植物圆环挂在墙面上，不仅节约空间，更能在夜间充当玄关与卧室的小夜灯，深得年轻白领青睐。</p>
            </div>
        </div>
        <div class="col-right-55" style="display: flex; flex-direction: column; justify-content: space-between;">
            <div class="card-border" style="height: 120pt; margin-bottom: 10pt;">
                <h2>常态壁饰：避开圣诞红海</h2>
                <p>传统的 Pre-lit 大型圣诞树季节性极强，Q4 结束后销量断崖；而仿真植物墙饰作为常态家居装饰，全年搜索热度维持稳步攀升趋势，具有<b>4.2% 的年复合增长率</b>。</p>
            </div>
            <div class="card-border" style="height: 130pt;">
                <h2>绿色人居与情绪照明双重价值</h2>
                <ul>
                    <li><b>自然触感</b>：高仿真假植叶片提供视觉绿意，舒缓生活压力。</li>
                    <li><b>光影氛围</b>：环形后侧 LED 背光投射在墙面，形成温和、不刺眼的反射氛围光，大幅提升居住质感。</li>
                </ul>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 03: 三档渠道规划 (Light)
    {
        filename: 'slide03.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.col-card-3 {
    width: 200pt;
    height: 100%;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">2.0 三大欧美渠道采购红线与三档规划</h1>
    </div>
    <div class="content-area" style="justify-content: space-between;">
        <!-- 低档 -->
        <div class="col-card-3">
            <div class="card-border">
                <p style="font-size: 8.5pt; color: #7F8C8D; font-weight: bold; margin-bottom: 2pt;">低档定价对标</p>
                <h2 style="color: #EA5504; font-size: 12pt; margin-bottom: 0; padding-bottom: 0;">生活超市 (Target/Lidl)</h2>
                <div style="background-color: #EA5504; height: 1.5pt; margin-top: 3pt; margin-bottom: 6pt;"></div>
                <p style="font-size: 9pt; margin-top: 8pt;"><b>采购红线：低成本约束</b></p>
                <p style="font-size: 9pt; color: #555;">发光款出厂成本必须高出同规格普通无灯款<b>不超过 50%（生死红线）</b>，主打极致性价比。</p>
                <p style="font-size: 9pt; margin-top: 8pt;"><b>对应方案：USB 氛围常青藤环</b></p>
                <p style="font-size: 9pt; color: #555;">极简铁漆环 + 物理 USB 供电 + 6h-18h 物理定时 IC。<b>出厂价控制在 $1.90 左右</b>。</p>
            </div>
        </div>
        <!-- 中档 -->
        <div class="col-card-3">
            <div class="card-border highlight">
                <p style="font-size: 8.5pt; color: #EA5504; font-weight: bold; margin-bottom: 2pt;">推荐核心利润档</p>
                <h2 style="color: #2D3436; font-size: 12pt; margin-bottom: 0; padding-bottom: 0;">DIY园艺中心 (Lowe's)</h2>
                <div style="background-color: #2D3436; height: 1.5pt; margin-top: 3pt; margin-bottom: 6pt;"></div>
                <p style="font-size: 9pt; margin-top: 8pt;"><b>采购红线：无线化与耐候</b></p>
                <p style="font-size: 9pt; color: #555;">买手反感拖线设计。要求免拉线墙面净化，锂电便携性与户外防雨能力。</p>
                <p style="font-size: 9pt; margin-top: 8pt;"><b>对应方案：无线锂电感应苔藓环</b></p>
                <p style="font-size: 9pt; color: #555;">拉丝黄铜圈 + PIR人体红外/LDR光敏双感应 + 2000mAh 隐藏充电锂电池。待机 < 5uA，免接线续航6个月。</p>
            </div>
        </div>
        <!-- 高档 -->
        <div class="col-card-3">
            <div class="card-border">
                <p style="font-size: 8.5pt; color: #7F8C8D; font-weight: bold; margin-bottom: 2pt;">高档工装与商业工程</p>
                <h2 style="color: #7F8C8D; font-size: 12pt; margin-bottom: 0; padding-bottom: 0;">专业设计院/楼宇工装</h2>
                <div style="background-color: #7F8C8D; height: 1.5pt; margin-top: 3pt; margin-bottom: 6pt;"></div>
                <p style="font-size: 9pt; margin-top: 8pt;"><b>采购红线：消防安全与智控</b></p>
                <p style="font-size: 9pt; color: #555;">商用环境必须通过防火阻燃标准。支持多单元模块化拼接与楼宇总线集成。</p>
                <p style="font-size: 9pt; margin-top: 8pt;"><b>对应方案：智能阻燃拼接绿墙</b></p>
                <p style="font-size: 9pt; color: #555;">通过英国 BS5852 / 美国 NFPA 701 最严阻燃，双路 DALI 调光（全光谱促生 + 氛围背光），对接智能中控。</p>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 04: 用户之声 (VOC) (Light)
    {
        filename: 'slide04.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">3.0 用户之声 (VOC) 痛点分类与解析</h1>
    </div>
    <div class="content-area">
        <div class="col-left-55">
            <div class="card-gray" style="height: 100%;">
                <h2 class="light-subtitle" style="margin-bottom: 8pt;">市面普通 LED 壁挂植物环的三大致命硬伤</h2>
                <ul style="padding-left: 12pt;">
                    <li style="font-size: 9.5pt; margin-bottom: 8pt;">
                        <b>1. 散热极差加速老化 (30% 差评)</b>
                        <p style="font-size: 9pt; color: #636E72; margin: 2pt 0 0 0;">灯带在密闭胶套中发热无法散去，导致塑料假叶片在 3 个月内加速开裂、泛黄，甚至散发塑胶异味。</p>
                    </li>
                    <li style="font-size: 9.5pt; margin-bottom: 8pt;">
                        <b>2. 线缆外露/换电繁琐 (40% 差评)</b>
                        <p style="font-size: 9pt; color: #636E72; margin: 2pt 0 0 0;">传统拖线严重破坏极简墙饰美学；低端干电池款每 2 周即电量耗尽，用户频繁更换电池体验极差。</p>
                    </li>
                    <li style="font-size: 9.5pt; margin-bottom: 6pt;">
                        <b>3. 结构焊死积灰难清 (20% 差评)</b>
                        <p style="font-size: 9pt; color: #636E72; margin: 2pt 0 0 0;">电学灯带与绿植叶片用热熔胶粘死，积灰后根本无法水洗，强行冲洗会导致电路短路或叶片脱落。</p>
                    </li>
                </ul>
            </div>
        </div>
        <div class="col-right-45" style="display: flex; flex-direction: column; justify-content: center; align-items: center; padding-left: 10pt;">
            <p style="font-size: 11pt; font-weight: bold; color: #2D3436; margin-bottom: 8pt; text-align: center;">亚马逊/Etsy 发光绿植环差评成因分类</p>
            <!-- 饼图占位符 -->
            <div id="voc-chart" class="placeholder" style="width: 250pt; height: 180pt; background-color: #F5F6FA; border: 1px dashed #BDC3C7; border-radius: 6pt;"></div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 05: 行业标杆对标 (Light)
    {
        filename: 'slide05.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">3.1 欧美三大标杆品牌现状对标</h1>
    </div>
    <div class="content-area" style="flex-direction: column; justify-content: space-between;">
        <!-- 对标 1 -->
        <div class="card-gray" style="border-left-color: #8E44AD; margin-bottom: 6pt; height: 75pt;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3pt;">
                <h2 style="color: #8E44AD; font-size: 11pt;">美学标杆：Terrain (轻奢美学)</h2>
                <p style="font-size: 9pt; font-weight: bold; color: #7F8C8D;">售价区间：$88 - $150</p>
            </div>
            <p style="font-size: 9pt; color: #555;"><b>优势：</b>Stargazer 星光藤蔓备受追捧，复古红铜丝缠绕手作枯枝，艺术质感极佳。<br>
            <b>致命局限：</b>纯插电式供电，无法做墙面无线化；完全依赖变压器拖线，牺牲了现代公寓的极简挂墙美学。</p>
        </div>
        <!-- 对标 2 -->
        <div class="card-gray" style="border-left-color: #2980B9; margin-bottom: 6pt; height: 75pt;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3pt;">
                <h2 style="color: #2980B9; font-size: 11pt;">大众标杆：IKEA (大众平价)</h2>
                <p style="font-size: 9pt; font-weight: bold; color: #7F8C8D;">售价区间：$19.99</p>
            </div>
            <p style="font-size: 9pt; color: #555;"><b>优势：</b>平价，易于购买，具备基础的 LED 常青藤壁饰。<br>
            <b>致命局限：</b>塑料质感重，多采用廉价干电池盒，需手动开关。无智能感应，待机功耗高，电池续航极短。</p>
        </div>
        <!-- 对标 3 -->
        <div class="card-gray" style="border-left-color: #27AE60; height: 75pt; margin-bottom: 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 3pt;">
                <h2 style="color: #27AE60; font-size: 11pt;">定制标杆：Etsy 独立手作店 (高端定制)</h2>
                <p style="font-size: 9pt; font-weight: bold; color: #7F8C8D;">售价区间：$120 - $350</p>
            </div>
            <p style="font-size: 9pt; color: #555;"><b>优势：</b>背光永生苔藓画（Moss Wall Art），实木画框与环形背光，质感与自然感极强。<br>
            <b>致命局限：</b>完全依靠手工贴装，生产效率极低，单价高企，无法进行大规模工业级 B2B 交付。</p>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 06: 照明降维技术 I (Light)
    {
        filename: 'slide06.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">4.0 核心照明降维技术：功耗、感应与结构</h1>
    </div>
    <div class="content-area">
        <div class="col-left-50">
            <div class="card-gray" style="height: 100%;">
                <h2 class="light-subtitle">1. 智能感应与 5uA 功耗控制</h2>
                <p style="font-size: 9pt; color: #7F8C8D; margin-bottom: 8pt;">（解决频繁换电与挂线丑陋的痛点）</p>
                <p>我们开发了集成 **“红外人体感应 (PIR) + 环境光敏 (LDR)”** 二合一的极低静态电流（待机 < 5uA）主控板：</p>
                <ul style="margin-top: 5pt;">
                    <li><b>光感控制</b>：光照变暗时（黄昏后）感应电路自动进入待命状态。</li>
                    <li><b>人体感应</b>：有人走过灯环瞬间唤醒点亮，人走后 5 分钟自动渐暗进入休眠。</li>
                    <li><b>长久续航</b>：搭配 2000mAh 低压锂电，可实现 **6 个月免充电**，墙面完全无线净化。</li>
                </ul>
            </div>
        </div>
        <div class="col-right-50">
            <div class="card-gray" style="height: 100%; border-left-color: #2D3436;">
                <h2 style="color: #2D3436;">2. 环体后侧隐形散热导弯铝槽</h2>
                <p style="font-size: 9pt; color: #7F8C8D; margin-bottom: 8pt;">（解决 LED 发热加速仿真植物老化泛黄痛点）</p>
                <p>植物圆环外框改变以往低成本塑料注塑的做法，跨界采用中山成熟的**拉弯铝型材工艺**：</p>
                <ul style="margin-top: 5pt;">
                    <li><b>铝材框架</b>：五金铝框做大面积物理散热。柔性 COB 灯带紧贴于铝框内壁导热垫上。</li>
                    <li><b>隐形对流</b>：在铝型材后侧开设多孔空气对流排热道。</li>
                    <li><b>降温效果</b>：确保叶片及茎干处长期受热温升控制在常温 5°C 以内，防止变色泛黄。</li>
                </ul>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 07: 照明降维技术 II (Light)
    {
        filename: 'slide07.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">4.1 核心照明降维技术：滑轨插接与促生光谱</h1>
    </div>
    <div class="content-area">
        <div class="col-left-50">
            <div class="card-gray" style="height: 100%;">
                <h2 class="light-subtitle">3. 滑轨卡扣物理快插底架</h2>
                <p style="font-size: 9pt; color: #7F8C8D; margin-bottom: 8pt;">（攻关挂墙假植积灰无法拆洗的死结）</p>
                <p>摒弃用热熔胶将叶片和灯框粘死的落后拼装法：</p>
                <ul style="margin-top: 5pt;">
                    <li><b>无胶组装</b>：铝圆环内壁设计微型滑轨槽，仿真假植枝干底座预埋滑动插脚。</li>
                    <li><b>快拆水洗</b>：假植以物理插脚卡入轨槽定位。当积灰需要清洗或局部部件损坏时，<b>10秒内可一键滑出拆卸</b>。</li>
                    <li><b>工艺降本</b>：免去人工打胶的繁杂工序，利于流水线拼装提效。</li>
                </ul>
            </div>
        </div>
        <div class="col-right-50">
            <div class="card-gray" style="height: 100%; border-left-color: #2D3436;">
                <h2 style="color: #2D3436;">4. 双向全光谱植物促生混合系统</h2>
                <p style="font-size: 9pt; color: #7F8C8D; margin-bottom: 8pt;">（解决真植物无日光必死、纯假植生硬的痛点）</p>
                <p>针对写字楼前台等高端商业场景，设计**“真假混种，光照滋养”**的光谱方案：</p>
                <ul style="margin-top: 5pt;">
                    <li><b>双向出光</b>：后侧内藏 2200K 暖黄灯珠向墙面漫反射投射氛围光；前内侧向下集成特制 **全光谱植物促生 LED**（红光 660nm + 蓝光 450nm，高显指 CRI 97）。</li>
                    <li><b>智能养护</b>：内置时钟芯片，白天 10h 自动输出全光谱生长光滋养真苔藓；夜间智能切换为环境微光呼吸律动。</li>
                </ul>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 08: 产品提报 1 & 2 (Light)
    {
        filename: 'slide08.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.prod-box {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 12pt;
    height: 100%;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">5.0 阶梯化产品提报：提案一 & 提案二</h1>
    </div>
    <div class="content-area">
        <!-- 提案一 -->
        <div class="col-left-50" style="padding-right: 8pt; border-right: 1px solid #DCDDE1;">
            <div class="prod-box">
                <img src="${IMAGES_DIR}/usb_ivy_ring.png" style="width: 110pt; height: 110pt; border-radius: 6pt; object-fit: cover; border: 1px solid #DCDDE1;">
                <div style="flex: 1;">
                    <span style="font-size: 8pt; background-color: #FFEAA7; color: #D63031; padding: 2pt 5pt; border-radius: 3pt; font-weight: bold;">超市款-低档</span>
                    <h2 style="font-size: 11pt; color: #EA5504; margin-top: 6pt;">Mini USB Ivy Wall Ring</h2>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>商业定位：</b>低价位壁挂装饰小夜灯<br>对标零售价 <b>$14.99</b></p>
                    <p style="font-size: 8.5pt; color: #2D3436;"><b>出厂成本：$1.90 / 套</b><br>
                    (五金框架与假叶$1.15，并联灯串控制盒$0.75。溢价率严格控制在 35% 以内，完全满足生活超市买手门槛)</p>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>核心配置：</b>30cm铁皮烤漆环 + 40颗暖白2200K并联防死珠 + 2m极细隐形USB线(带6h/18h定时IC)</p>
                </div>
            </div>
        </div>
        <!-- 提案二 -->
        <div class="col-right-50" style="padding-left: 8pt;">
            <div class="prod-box">
                <img src="${IMAGES_DIR}/wireless_moss_ring.png" style="width: 110pt; height: 110pt; border-radius: 6pt; object-fit: cover; border: 1px solid #DCDDE1;">
                <div style="flex: 1;">
                    <span style="font-size: 8pt; background-color: #55EFC4; color: #00B894; padding: 2pt 5pt; border-radius: 3pt; font-weight: bold;">主力款-中档</span>
                    <h2 style="font-size: 11pt; color: #2D3436; margin-top: 6pt;">Wireless Sensor Moss Ring</h2>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>商业定位：</b>中型玄关/走廊无线环境灯<br>对标零售价 <b>$69.00 - $89.00</b></p>
                    <p style="font-size: 8.5pt; color: #2D3436;"><b>出厂成本：$10.30 / 套</b><br>
                    (40cm拉弯铝环$4.00，高仿真PU苔藓$2.20，2000mAh锂包$1.50，双感应板$2.60。毛利率高)</p>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>核心配置：</b>40cm黄铜圆环 + 隐藏式PIR人体感应/LDR光敏主控 + 锂电USB-C快充 + 滑轨快拆无胶卡扣 + 呼吸调光算法</p>
                </div>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 09: 产品提报 3 & 4 (Light)
    {
        filename: 'slide09.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>
${COMMON_CSS}
.prod-box {
    display: flex;
    flex-direction: row;
    align-items: flex-start;
    gap: 12pt;
    height: 100%;
}
</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">5.1 阶梯化产品提报：提案三 & 提案四</h1>
    </div>
    <div class="content-area">
        <!-- 提案三 -->
        <div class="col-left-50" style="padding-right: 8pt; border-right: 1px solid #DCDDE1;">
            <div class="prod-box">
                <img src="${IMAGES_DIR}/modular_forest_wall.png" style="width: 110pt; height: 110pt; border-radius: 6pt; object-fit: cover; border: 1px solid #DCDDE1;">
                <div style="flex: 1;">
                    <span style="font-size: 8pt; background-color: #D63031; color: #FFFFFF; padding: 2pt 5pt; border-radius: 3pt; font-weight: bold;">工装商用-高档</span>
                    <h2 style="font-size: 11pt; color: #2D3436; margin-top: 6pt;">Modular Smart Forest Wall</h2>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>商业定位：</b>高档酒店/写字楼大堂拼接背景墙<br>对标工程报价单单元 <b>$150+</b></p>
                    <p style="font-size: 8.5pt; color: #2D3436;"><b>出厂成本：$35.00 / 单元</b><br>
                    (拼接五金与阻燃假叶$22，DALI/Zigbee智控驱动与灯带$13. 防火阻燃溢价极高)</p>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>核心配置：</b>几何六角形铝型材框 + 英国BS5852/美国NFPA701消防阻燃假叶 + 楼宇中控无线智控 (DALI调光)</p>
                </div>
            </div>
        </div>
        <!-- 提案四 -->
        <div class="col-right-50" style="padding-left: 8pt;">
            <div class="prod-box">
                <img src="${IMAGES_DIR}/biophilic_active_ring.png" style="width: 110pt; height: 110pt; border-radius: 6pt; object-fit: cover; border: 1px solid #DCDDE1;">
                <div style="flex: 1;">
                    <span style="font-size: 8pt; background-color: #00CEC9; color: #FFFFFF; padding: 2pt 5pt; border-radius: 3pt; font-weight: bold;">生态概念-高档</span>
                    <h2 style="font-size: 11pt; color: #00B894; margin-top: 6pt;">Biophilic Dual-Light Ring</h2>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>商业定位：</b>会议室/写字楼前台混植生态壁灯<br>对标零售价 <b>$180+</b></p>
                    <p style="font-size: 8.5pt; color: #2D3436;"><b>出厂成本：$22.00 / 套</b><br>
                    (60cm白大铝框$11，全光谱促生双路电控与灯带$11. 光谱技术长板应用体现)</p>
                    <p style="font-size: 8.5pt; color: #636E72;"><b>核心配置：</b>60cm白大铝框 + 80%高仿真叶+20%活体真植(空气凤梨) + 白天10h植物促生全光谱(CRI 97) + 夜间烛光呼吸氛围光</p>
                </div>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 10: 供应链协作与安规 (Light)
    {
        filename: 'slide10.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-light">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area">
        <h1 class="light-title">6.0 供应链协同与欧美安规准入</h1>
    </div>
    <div class="content-area">
        <div class="col-left-50" style="padding-right: 8pt;">
            <div class="card-gray" style="height: 100%;">
                <h2 class="light-subtitle">“中山电控+东莞假植”跨界闭环</h2>
                <p style="font-size: 9pt; color: #7F8C8D; margin-bottom: 8pt;">（发挥轻资产、高敏捷的总装协作优势）</p>
                <ul style="padding-left: 12pt;">
                    <li style="font-size: 9pt; margin-bottom: 6pt;">
                        <b>1. 中山（五金电控主场）</b>
                        <p style="font-size: 8.5pt; color: #636E72; margin: 1pt 0 0 0;">发挥中山在铝型材拉弯、COB灯带、电池管理（低静态功耗电路）和安规驱动的绝对成本优势。</p>
                    </li>
                    <li style="font-size: 9pt; margin-bottom: 6pt;">
                        <b>2. 东莞/惠州（绿植工艺主场）</b>
                        <p style="font-size: 8.5pt; color: #636E72; margin: 1pt 0 0 0;">发挥东莞在哑光 PU 过胶假植（高仿真、耐老化、防火阻燃）的制造积淀。在注塑阶段将卡扣骨架预埋进植物支干。</p>
                    </li>
                    <li style="font-size: 9pt; margin-bottom: 0;">
                        <b>3. 中山一站式总装出货</b>
                        <p style="font-size: 8.5pt; color: #636E72; margin: 1pt 0 0 0;">东莞厂绿植配件寄往中山，在中山总装厂进行灯串嵌入、老化测试、包材贴标并一站式出货，降低管理成本。</p>
                    </li>
                </ul>
            </div>
        </div>
        <div class="col-right-50" style="padding-left: 8pt;">
            <div class="card-gray" style="height: 100%; border-left-color: #2D3436;">
                <h2 style="color: #2D3436;">欧美市场准入与消防红线</h2>
                <p style="font-size: 9pt; color: #7F8C8D; margin-bottom: 8pt;">（防范合规风险，锁定核心大客户）</p>
                <ul style="padding-left: 12pt;">
                    <li style="font-size: 9pt; margin-bottom: 6pt;">
                        <b>1. 美国 B2C 超市安规准入</b>
                        <p style="font-size: 8.5pt; color: #636E72; margin: 1pt 0 0 0;">电学部分需通过 <b>UL 153</b> (便携式灯具)，低电压并联灯串符合安全标准；电池盒需配备螺丝锁以符合儿童防吞食标准。</p>
                    </li>
                    <li style="font-size: 9pt; margin-bottom: 6pt;">
                        <b>2. 欧洲 REACH & RoHS 环保指令</b>
                        <p style="font-size: 8.5pt; color: #636E72; margin: 1pt 0 0 0;">挂饰由于是常态家居壁饰，欧盟限制增塑剂（邻苯二甲酸酯类）超标，PU 叶片必须使用环保树脂材料。</p>
                    </li>
                    <li style="font-size: 9pt; margin-bottom: 0;">
                        <b>3. 大型商用消防红线（工装关键）</b>
                        <p style="font-size: 8.5pt; color: #636E72; margin: 1pt 0 0 0;">大型拼接墙面壁饰必须通过英国 <b>BS5852</b> 阻燃测试，或美国 <b>NFPA 701</b> 防火阻燃认证（PU 叶片注塑时必须按比例添加防火改性母粒）。</p>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-orange.png" class="logo-img">
</body>
</html>`
    },
    // 11: 路线图与结语 (Dark)
    {
        filename: 'slide11.html',
        html: `<!DOCTYPE html>
<html>
<head>
<style>${COMMON_CSS}</style>
</head>
<body class="slide-dark">
<div class="top-bar"></div>
<div class="container">
    <div class="header-area-dark">
        <h1 class="dark-title">7.0 发光植物壁挂环开发与出海路线图</h1>
    </div>
    <div class="content-area">
        <div class="col-left-55" style="display: flex; flex-direction: column; justify-content: space-between;">
            <div class="card-gray-dark" style="margin-bottom: 6pt; height: 68pt;">
                <h2 style="color: #EA5504; font-size: 11pt; margin-bottom: 2pt;">阶段一：打样与仿真协同 (M1 - M2)</h2>
                <p style="font-size: 8.5pt; color: #BDC5C9; margin: 0;">完成中山低功耗控制板开发及灯串并联设计。将隐形灯串寄往注塑厂，配合进行主干穿线和叶片物理卡扣模具打样。</p>
            </div>
            <div class="card-gray-dark" style="margin-bottom: 6pt; height: 68pt;">
                <h2 style="color: #EA5504; font-size: 11pt; margin-bottom: 2pt;">阶段二：检测与送审认证 (M3)</h2>
                <p style="font-size: 8.5pt; color: #BDC5C9; margin: 0;">高中低三档首批样品制作。针对低档进行 UL 588 测试，中档进行 IP 65 户外耐候性测试，高档商用骨架送检阻燃消防认证。</p>
            </div>
            <div class="card-gray-dark" style="margin-bottom: 6pt; height: 68pt;">
                <h2 style="color: #EA5504; font-size: 11pt; margin-bottom: 2pt;">阶段三：买手对接与展会拓展 (M4 - M5)</h2>
                <p style="font-size: 8.5pt; color: #BDC5C9; margin: 0;">参展美国 Las Vegas 五金展、德国 Spoga+Gafa 园艺展。对生活超市展示极致性价比，对建材超市主推锂电无线，商用展示中控调光与阻燃。</p>
            </div>
            <div class="card-gray-dark" style="margin-bottom: 0; height: 68pt;">
                <h2 style="color: #EA5504; font-size: 11pt; margin-bottom: 2pt;">阶段四：量产众筹与分销发货 (M6)</h2>
                <p style="font-size: 8.5pt; color: #BDC5C9; margin: 0;">首批中小批量上线 Wayfair 众筹，收集第一手消费者反馈以升级软件呼吸调光算法；通过后随即启动生活超市大宗代工与工装代发分销。</p>
            </div>
        </div>
        <div class="col-right-45" style="display: flex; flex-direction: column; justify-content: center; align-items: center; background-color: #2D3436; padding: 20pt; border-radius: 8pt; border: 1px solid #4A5568;">
            <p style="font-size: 13pt; color: #EA5504; font-weight: bold; margin-bottom: 10pt; text-align: center; text-transform: uppercase;">汇报结束</p>
            <h2 style="font-size: 20pt; color: #FFFFFF; font-weight: bold; margin-bottom: 10pt; text-align: center; font-family: 'Microsoft YaHei', sans-serif;">谢谢观看</h2>
            <p style="font-size: 9.5pt; color: #A4B0BE; text-align: center; line-height: 1.6;">Howstoday 项目组工作汇报<br>2026年6月</p>
        </div>
    </div>
</div>
<img src="${IMAGES_DIR}/logo-white.png" class="logo-img">
</body>
</html>`
    }
];

// 主执行函数
async function main() {
    console.log('开始写入 HTML slide 文件...');
    for (const slideData of SLIDES_DATA) {
        const filepath = path.join(SLIDES_DIR, slideData.filename);
        fs.writeFileSync(filepath, slideData.html, 'utf-8');
        console.log(`已写入: ${filepath}`);
    }

    console.log('\n开始初始化 PptxGenJS 并转换为 PPTX...');
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.author = 'Howstoday Project Team';
    pptx.title = 'LED Leaf Wall Rings Presentation';

    // ==========================================
    // HACK: 动态拦截并修复 Windows 下绝对路径解析的前缀斜杠 BUG
    // ==========================================
    const originalAddSlide = pptx.addSlide.bind(pptx);
    pptx.addSlide = function(...args) {
        const slide = originalAddSlide(...args);
        const originalAddImage = slide.addImage.bind(slide);
        
        slide.addImage = function(options) {
            if (options && options.path && typeof options.path === 'string') {
                let p = options.path;
                // 如果发现是 Unix 风格的绝对路径，例如 /C:/Users/... 去掉开头的 '/'
                if (p.startsWith('/') && p.substring(2, 4) === ':/') {
                    p = p.substring(1);
                    console.log(`[HACK] Fixed Unix-style absolute path: ${options.path} -> ${p}`);
                } else if (p.startsWith('\\') && p.substring(2, 4) === ':\\') {
                    p = p.substring(1);
                    console.log(`[HACK] Fixed Windows-style absolute path with leading slash: ${options.path} -> ${p}`);
                }
                
                // 确保使用 Windows 规范的反斜杠作为路径分隔符，防止底层读文件 API 混淆
                options.path = path.normalize(p);
            }
            return originalAddImage(options);
        };
        return slide;
    };

    // 转换每一页 HTML
    for (let i = 0; i < SLIDES_DATA.length; i++) {
        const slideData = SLIDES_DATA[i];
        const htmlPath = path.join(SLIDES_DIR, slideData.filename);
        console.log(`\n[Slide ${i + 1}/${SLIDES_DATA.length}] 正在处理 ${slideData.filename}...`);
        
        try {
            const { slide, placeholders } = await html2pptx(htmlPath, pptx);
            console.log(`[Slide ${i + 1}] HTML 转换成功。发现 ${placeholders.length} 个占位符。`);
            
            // 针对第 4 页 (slide04.html)，添加原生饼图
            if (slideData.filename === 'slide04.html') {
                const chartArea = placeholders.find(p => p.id === 'voc-chart');
                if (chartArea) {
                    console.log(`[Slide ${i + 1}] 正在将原生饼图添加到占位符: voc-chart`);
                    
                    const pieData = [{
                        name: '差评原因',
                        labels: [
                            '挂线难看/电池换电快(40%)', 
                            '发热导致假叶变色(30%)', 
                            '结构焊死积灰难清(20%)', 
                            '单点烧坏整环熄灭(10%)'
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
                        chartColors: ['8E44AD', 'E74C3C', 'F39C12', '2ECC71']
                    });
                    console.log(`[Slide ${i + 1}] 原生饼图绘制完成。`);
                } else {
                    console.error(`[Slide ${i + 1}] 未找到占位符: voc-chart`);
                }
            }
        } catch (err) {
            console.error(`[Slide ${i + 1}] 转换失败:`, err);
            process.exit(1);
        }
    }

    const outputPptx = path.join(SCRATCH_DIR, 'lighted-wall-rings-presentation.pptx');
    console.log(`\n全部幻灯片转换成功。开始保存 PPT 到 ${outputPptx}...`);
    try {
        await pptx.writeFile({ fileName: outputPptx });
        console.log('PowerPoint 汇报文稿成功生成！');
        
        // 复制一份到工作区根目录下，方便用户直接获取
        const destPath = 'd:/我的APP/品类开发调研/lighted-wall-rings-presentation.pptx';
        fs.copyFileSync(outputPptx, destPath);
        console.log(`已成功将 PPT 复制到工作区目标路径: ${destPath}`);
    } catch (writeErr) {
        console.error('保存 PPT 失败:', writeErr);
        process.exit(1);
    }
}

main().catch(console.error);
