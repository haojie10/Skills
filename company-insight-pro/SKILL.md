---
name: company-insight-pro
description: 360度企业战略情报洞察工具。用于为特定企业生成深度战略情报报告，涵盖财务穿透、组织架构、采购逻辑、用户舆情及出口准入合规性分析。当用户需要调研潜在海外客户、竞争对手或合作伙伴时触发。
---

# Company Insight Pro (360° 企业战略情报洞察)

本技能用于对全球任意企业（尤其是大型零售商、品牌商、供应链巨头）进行 360 度多维度的商业与战略情报穿透，并生成一份高颜值、高结构化、卡片式排版、交互式、自包含的 HTML 战略情报报告，并自动上传发布至 GlobalTradeBuddy 平台。

---

## 极简三步闭环工作流 (Three-Step Streamlined Workflow)

```
[步骤 0 & 1: 认领与查重] ──> [步骤 2: 深度穿透调研] ──> [步骤 3: 一键自愈构建、发布与回写]
```

### 1. 任务认领与前置查重门禁 (Claim & Check)

#### 认领模式（当用户指示“认领下一个任务”时）：
1. **禁止读取或修改本地静态清单文件**，直接向云端发起原子认领请求：
   ```python
   import urllib.request, json
   req = urllib.request.Request(
       'https://marketgraphic.cn/api/agent/tasks/claim',
       data=json.dumps({"worker_name": "antigravity", "tag": "antigravity"}).encode('utf-8'),
       headers={'Content-Type': 'application/json', 'Authorization': 'Bearer automation_agent_secret'}
   )
   res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
   # 记录 task_id = res['task']['id'], company_name = res['task']['company_name']
   ```
2. **运行查重门禁脚本**：
   ```bash
   python scripts/check_report.py --company "目标公司名"
   ```
   * 🚨 **【品类报告与客户报告物理隔离铁律（严禁跨类别覆盖）】**：
     * 平台报告分为两大独立资产体系：**品类出海洞察报告（`category='product'`）** 与 **客户战略情报报告（`category='customer'`）**。
     * 渠道商/零售商往往既有针对其具体销售品类的专项洞察报告（如《英国 Argos 脱毛器品类研报》），也有全方位战略调研报告（《Argos 360° 企业战略情报报告》），二者属于并行互补资产，互不冲突！
     * **绝对严禁使用 `--target-id` 覆盖品类报告**！`--target-id` 仅且必须用于**同一家企业旧版 customer 报告的版本迭代升级**。平台后端已部署安全防御锁，任何试图跨类型篡改覆盖的行为都将被强制拦截。
   * **若退出码为 10（已存在）**：
     * **默认行为**：停止后续调用，输出查重卡片并询问用户是“跳过任务”还是“覆盖更新（`--target-id [已有客户报告ID]`）”。
     * **自动跳过**：直接调用 `/api/agent/tasks/complete` 回写完成并结束任务。
   * **若退出码为 0（无重复）**：立即进入下一步调研。

---

### 2. 深度穿透调研 (Deep Research)

使用 `search_web` 穿透以下 8 大核心维度（每模块附带一手来源链接）：
1. **概览与历史（500-800字）**：创立与发展历程、所有权架构、最新财年营业收入（Turnover / Revenue）、门店数及业态分布、行业地位与核心优势、对华直采战略定位。
2. **财务与市场（【真实财报门禁（Truth-First）】）**：
   * **硬核财报优先原则**：目标国官方商业登记与审计系统（如英国 Companies House, 俄罗斯 Spark/Checko/Audit-it, 拉脱维亚 Lursoft/Firmas, 西班牙 BORME/Einforma, 德国 Bundesanzeiger, 美国 SEC 等）披露的历史净营业额（Turnover / Revenue）与净利润，**必须逐年精准采用真实披露数据**，严禁人为平滑曲线或捏造历史趋势！
   * **实数与估算严格隔离**：仅在官方未公开具体年份数据时允许合理插值，且**未披露年份必须显式标注「(E)」或「(Est.)」**，严禁将估算包装为审计实数。
3. **渠道与竞品**：门店网络区域分布、核心竞品（至少 3-5 家头部竞品）优劣势对比、消费人群画像。
4. **自有品牌与贴牌**：私有品牌矩阵、覆盖品类、中国制造 OEM/ODM 合作契机。
5. **决策链与机构**：采购组织架构、决策流程、亚洲采购办/对华采购通道。
6. **供应链与合规（【对华采购总盘硬约束与双轨比率模型】）**：核心供应商名单、物流港口与分销中心（DC）、强制性准入认证（如 BSCI/SMETA、SABS、FDA、EAC、EPR）；**必须构建「对华大宗商品采购估值趋势图（ECharts 柱状/折线图）」**：
   * **① 采购成本总盘硬约束（Total Sourcing Cap Constraint）**：
     $$\text{采购总盘 (COGS)} = \text{企业总营收} \times \text{业态采购成本系数（实体零售 40%-50%, 专业批发 65%-75%, 工控B2B 70%-80%）}$$
     任何年份的对华直采金额，在物理上绝不可超过总采购预算！
   * **② 本土/欧美品牌采购 vs 对华源头直采双轨比率（严禁无视企业商业基因）**：
     * **[国际名牌独家/多品牌分销商]**（如名牌厨具、摄影器材、高端电气代理）：欧美/本土品牌提货采购必占 **55% ~ 75%**，对华直采主要为白牌平替、辅料配件，合理占比上限为 **25% ~ 40%**。其直采增速在渗透率达标后**必须收敛至与企业总营收增速（3%~6%）趋同**，严禁单边暴增击穿总盘！
     * **[全自营折扣/大卖场零售商]**（如 Dollarama, Action, TEDi）：轻工日百与通用消耗品对华直采可占 **60% ~ 80%**，出运规模随门店网络扩张同步增长。
     * **[源头制造工厂与装备集团]**（如大型造纸包装、重工）：对华直采集中在“重型设备、关键易损件、耗材网毯”，占其年均机修设备技改预算的 **30% ~ 50%**。
     * **[艺术奢华工坊]**（如意式古典水晶灯、定制艺术品）：核心贵金属与顶级水晶由欧洲垄断，对华采购集中于高精K9毛坯、智能调光模组，占比控制在 **20% ~ 35%**。
   * **③ 真实 FOB 离岸价与物理集装箱 (40HQ) 柜量闭环**：
     * 货值严格以 FOB 口径计算，结合品类单柜标准货值（轻工日百 3~5 万美元/柜；五金小家电 5~8 万美元/柜；机能纺织 8~15 万美元/柜），推算出年度 40HQ 总箱数与月均出运节奏，确保正文阐述与图表数字严密自洽。
7. **用户舆情与痛点**：消费者高频好评与差评吐槽、运营核心痛点（如极端环境失效、防损、物流拥堵）。
8. **供应商实战策略（必须提供 4 条建议卡片，呈 2×2 黄金网格排版）**：
   * ① **选品与产品定制策略**：针对该企业的采购痛点与热销品类，提炼具体的直采/代工产品型号及技术参数。
   * ② **价格带与包装规格建议**：明确目标市场的价格定位、起订量（MOQ）、彩盒包装及多语言标签/条码规范。
   * ③ **质量合规与认证门禁**：列明该企业及目标国强制要求的认证资质（如 CE、EAC、E-mark、RCM、RoHS、BSCI 等）。
   * ④ **渠道切入与对接路径**：指出联系采购办/技术委员会的最佳时机、打样送测流程及跨境物流与结算方案。

---

### 2.5 实体门店判定与 Banner 提示词规范（彻底排除展厅）

在调研中，必须精准识别企业的**商业业态与真实经营场所**，非黑即白地设置 `HAS_PHYSICAL_STORE: true | false`：

#### A. 必须开启生图 & 横幅（`HAS_PHYSICAL_STORE: true`）：
**唯一核心准则**：该企业必须拥有**带自身独立品牌招牌、面向公众消费者或技工客户开放的自营实体商业店铺/门市（Storefront / Retail Shop / Trade Counter）**！

符合生图条件的业态清单：
1. **综合零售大卖场 / 超市 / 折扣杂货连锁**（如 Walmart, Costco, Aldi, Dollarama, Action, B&M, TEDi）
2. **专业建筑材料 / 木业卫浴 / DIY 仓储超市**（如 The Home Depot, Lowe's, Leroy Merlin）
3. **专业电气电工 / 工业 MRO / 五金工具实体批发门市**（如 Kristall-Elektro, Rexel, Sonepar, Fastenal, Würth 门市）
4. **汽配零件 / 轮胎快修连锁实体店**（如 AutoZone, O'Reilly, NAPA）
5. **水暖管道 / 暖通空调 (HVAC) 专业批发门市**（如 Ferguson, Wolseley）
6. **大型家居生活综合商场**（如 IKEA, JYSK）
7. **极少数拥有大量独立临街自营专卖店的知名品牌**（如 Apple Store, Nike 直营专卖店）

#### B. 绝对严禁生图 & 自动彻底移除横幅（`HAS_PHYSICAL_STORE: false`）：
**特别警戒线**：严禁把“展厅 (Showroom)”、办公室样品间或展会展位当成实体门店！以下所有企业**一律禁止生图，完全剥离横幅**：

1. **渠道代销型品牌商（Brand Owners - 进驻他人渠道卖货）**：
   * ❌ **鞋类 / 服装 / 箱包品牌商**：自身无独立专卖店，进驻百货商场、鞋城集合店、买手店代销的；
   * ❌ **餐厨用品 / 炊具餐具 / 厨用刀具品牌商**：自身无专卖大店，进驻商超、厨具集合店代销的；
   * ❌ **照明灯具 / 开关插座 / 低压电器品牌商**：自身无专营门市，进驻建材超市、电气分销商代销的；
   * ❌ **生活小家电 / 消费电子配件品牌商**：进驻电器卖场、超市货架代销的；
   * ❌ **个人护理 / 美妆工具 / 母婴用品品牌商**：进驻药妆店、母婴连锁代销的；
   * ❌ **文具办公 / 礼品玩具 / 运动健身器材品牌商**：进驻文具店、玩具城代销的；
   * ❌ **五金配件 / 紧固件制造品牌商**：通过各级分销代理商网络出货的。
2. **国际贸易与供应链分销商**：
   * ❌ 纯进口商 / 进出口贸易商（Importers / Traders）；
   * ❌ 全国性 / 区域性一级总代与保税批发商（Master Distributors / B2B Wholesalers）；
   * ❌ 跨境采购代表处 / 供应链服务公司。
3. **生产制造型企业**：
   * ❌ 源头实体制造工厂（Factories / Manufacturers）；
   * ❌ OEM / ODM 代工与零部件配套组装厂。
4. **纯线上电商与数字服务企业**：
   * ❌ 纯线上品牌 / 亚马逊大卖 / 跨境独立站卖家（D2C Brands）；
   * ❌ 软件、SaaS 平台与供应链管理服务商。
5. **绝对不算实体门店的“伪实体场景”（严禁以此为借口生图）**：
   * ❌ **公司总部办公大楼内部的样品间、陈列室（Showroom）** —— 算内部办公室，不算实体门市！
   * ❌ **广交会、法兰克福展等各类展会上的临时展位** —— 算短期展会，不算实体店铺！
   * ❌ **封闭式物流仓库、港口堆场、自动化配送中心 (DC)** —— 算仓储设施，不算对外门市！

* **流水线自动化行为**：当 `HAS_PHYSICAL_STORE: false` 时，流水线会自动跳过生图，并从 HTML 中**完全移除顶部店面横幅 DOM 区块**，使 Header 吸顶栏直接置顶展示，保持版面干净专业。

---

### 2.6 竞争对手（Competitors）4段式管道规范与平台裂变支撑

为了让报告发布后，平台能够精准自动裂变出高质量的**待调研新任务**（写入 `research_tasks` 任务池），并且让下一个 Agent 认领任务时能够立即获悉其**官网**和**公司形态**（提前判定是否需要实体店生图 Banner），`COMPETITORS` 必须严格遵循 **4 段式管道格式**：

```text
名称 | 国家 | 官网 | 【形态标签】主营品类与市场定位
```

#### 1. 公司形态标签标准（必须显式标注其商业业态）：
* **`[实体连锁零售]`**：面向个人消费者的综合超市、大卖场、折扣店、百货（如 Walmart、Costco、Lidl）。
* **`[专业工程分销]`**：面向专业工匠/承包商的实体批发门市（如电气、汽配、五金工具、建材MRO门店）。
* **`[自营独立专卖店]`**：极少数自营专卖连锁（如 Apple Store、IKEA）。
* **`[纯工控B2B/进口商]`**：无实体门市的进口贸易商、全国性一级总代、供应链服务商。
* **`[源头工厂/OEM代工]`**：自建生产基地的设备制造商、零部件代工厂。
* **`[渠道品牌商]`**：无独立实体门市、进驻第三方商超/分销商销售的鞋服、餐厨、照明等品牌商。

#### 2. 规范示例：
```text
ETM|俄罗斯|https://etm.ru|[专业工程分销] 全俄电气与工控综合分销龙头,
Russky Svet|俄罗斯|https://russvet.ru|[专业工程分销] 跨国低压电气与照明工程分销巨头,
Leroy Merlin|俄罗斯|https://leroymerlin.ru|[实体连锁零售] 大型DIY五金建材连锁大卖场
```

---

### 3. 一键自愈构建、发布与回写流水线 (Pipeline)

调研数据存为临时 `report_data.json`，运行统一流水线命令即可完成：**全量纯数据卡片渲染 + 门店形态自动识别与横幅裁剪 + 业态自适应生图 Prompt 注入 + 竞品 4 段式管道智能融合成型 + Emoji/法律后缀自愈清洗 + 本地 Google Flow 自动生图 + 门禁审计 + 知识图谱互联发布 + 任务中心自动回写**！

```bash
# 新建模式（支持一键自动调用本地 Google Flow 业态自适应生图闭环）
python C:/Users/066/.gemini/config/skills/company-insight-pro/scripts/build_report.py \
  --data report_data.json \
  --output "d:/我的APP/客户档案/<区域>/<公司名>_战略情报报告.html" \
  --auto-flow \
  --validate \
  --publish \
  --task-id "<task_id>"

# 覆盖更新模式（指定 --target-id 原地更新）
python C:/Users/066/.gemini/config/skills/company-insight-pro/scripts/build_report.py \
  --data report_data.json \
  --output "d:/我的APP/客户档案/<区域>/<公司名>_战略情报报告.html" \
  --target-id "<已有报告ID>" \
  --auto-flow \
  --validate \
  --publish \
  --task-id "<task_id>"
```

---

## 🎨 全量纯数据标准契约 (100% Pure-Data Schema)

**严禁在 JSON 中手写粗糙无样式的 HTML**！底层流水线已内置高保真 Tailwind 卡片化渲染引擎，只需填入清晰的结构化字段：

```json
{
  "CATEGORY": "customer",
  "SUMMARY": "150字以内的报告摘要...",
  "COMPANY_NAME": "企业标准主名（无法律后缀，如 Kristall-Elektro）",
  "COMPANY_ALIASES": "别名列表，如 Kristall Elektro, Кристалл-Электро",
  "COMPANY_WEBSITE": "https://kristall43.ru",
  "REGIONS": "俄罗斯,东欧,独联体",
  "COMPETITORS": "ETM|俄罗斯|https://etm.ru|[专业工程分销] 全俄电气与工控综合分销龙头, Russky Svet|俄罗斯|https://russvet.ru|[专业工程分销] 跨国低压电气与照明工程分销巨头, Leroy Merlin|俄罗斯|https://leroymerlin.ru|[实体连锁零售] 大型DIY五金建材连锁大卖场",
  "_COMPETITORS_COMMENT": "⚠️ COMPETITORS 必须使用 4 段式管道格式：名称|国家|官网|【形态标签】主营品类与市场定位，直接服务于平台任务裂变与下一轮自动化调研",
  "PRODUCTS": "电子电气产品-电线电缆与低压配电,照明产品-LED商业照明,电子电气产品-开关插座与配电箱柜",
  "_PRODUCTS_COMMENT": "⚠️ PRODUCTS 必须包含或使用前缀对齐 GTB 54 标准大类（如：家用电器、餐厨器皿、家具、通用机械及机械基础件、照明产品、电子消费品及信息产品、五金、工具、个人护理用具等），以便后台精准打标",
  "CHANNELS": "专业电气连锁超商,工程与工业直供,数字化商城",
  "SUPPLIERS": "IEK, DKC, EKF, Gauss, TDM Electric",
  "CUSTOMERS": "区域建筑承包商,电力安装施工队,工业制造企业",
  "SISTER_PARENTS": "РАЭК, АО «Кристалл»",
  "TIER_LEVEL": "TIER 2 • 俄罗斯区域电气分销龙头",
  "REPORT_SUBTITLE": "深耕俄罗斯伏尔加-维亚特卡经济区30载的专业电气连锁分销与成套配电领军者",
  "HAS_PHYSICAL_STORE": true,
  "COMMERCIAL_TYPE": "industrial_mro",
  "_COMMERCIAL_TYPE_OPTIONS": "heavy_machinery | machine_tool | outdoor_gear | medical_device | industrial_mro | building_materials | auto_parts | retail_supermarket",
  "BANNER_PROMPT": "可选：显式覆盖的英文超写实生图提示词...",
  "BANNER_ALT": "门店外景实拍",
  "BANNER_LOCATION": "Kirov, Russia",
  "BANNER_TITLE": "Kristall-Elektro 战略情报报告",

  "OVERVIEW_DATA": [
    "第一段（200-300字）：公司创立背景与历史演进、企业性质与所有权结构（如ESOP/上市/家族控股）、总部基地、实体网络规模及行业核心地位...",
    "第二段（200-300字）：主营业务与三大核心垂直领域、商业模式、技术服务特色及核心竞争优势...",
    "第三段（150-200字）：宏观经济与产业红利、战略并购与网络扩张路径、对华供应链合作与中国源头工厂直采战略定位..."
  ],

  "REGISTRATION_DATA": {
    "法定注册主体": "ООО «КРИСТАЛЛ-ЭЛЕКТРО»",
    "统一税号 (ИНН)": "4345462758 / ОГРН 1174350004058",
    "行业协会身份": "俄罗斯电气公司协会（РАЭК / RAEC）核心成员",
    "成立年份": "1994 年",
    "全球总部": "г. Киров, Россия",
    "核心管理层": "Алексей Анатольевич Фурсов (CEO)",
    "主实体营业额": "7.76 亿卢布 (YoY +12.3%)",
    "网络规模": "30+ 家直营大卖场 / 20万+活跃SKU"
  },

  "BRAND_MATRIX_DATA": {
    "title": "核心合作品牌与授权分销矩阵",
    "subtitle": "RAEC 联合采购目录",
    "brands": [
      {"name": "IEK", "desc": "俄本土低压电气龙头"},
      {"name": "DKC", "desc": "工业布线与配电柜体"},
      {"name": "EKF", "desc": "工控与低压配电"},
      {"name": "Gauss", "desc": "高端商业与家居照明"}
    ]
  },

  "TIMELINE_DATA": [
    {"year": "1994 年", "title": "品牌创立", "desc": "成立首家专业电工器材与灯饰门店。"},
    {"year": "2024 年", "title": "全渠道深化", "desc": "荣获全俄最佳客户忠诚度大奖。"}
  ],

  "FINANCE_CHART1_TITLE": "营业收入与增长趋势",
  "CHART1_OPTION": { ... ECharts 配置对象 ... },
  
  "FINANCE_INSIGHTS_DATA": [
    {"title": "洞察 1：营收逆势稳增", "tag": "韧性强劲", "color": "green", "desc": "主实体年营业额超7.7亿卢布..."},
    {"title": "洞察 2：高毛利业务对冲内卷", "tag": "结构优化", "color": "orange", "desc": "成套配电与商业照明毛利率保持在30%+..."}
  ],

  "CHANNEL_CHART_TITLE": "业务业态与区域网络结构",
  "CHART2_OPTION": { ... ECharts 配置对象 ... },

  "CHANNELS_GRID_DATA": [
    {"title": "30+ 实体直营大卖场", "icon": "map-pin", "desc": "覆盖基洛夫及毗邻共和国核心商圈..."},
    {"title": "B2B 工程集成与配电总装", "icon": "wrench", "desc": "自营总装车间直接承接工业配电柜定制..."}
  ],

  "COMPETITORS_DATA": [
    {
      "name": "ETM",
      "tag": "全俄电气分销巨头",
      "position": "俄罗斯最大电气综合分销商，拥有全国性物流枢纽与 iPRO 平台。",
      "pros_cons": "规模极大，但区域定制与本地工程师响应不及区域专营店灵活。"
    }
  ],

  "BRAND_TABLE_DATA": [
    {
      "category": "LED 商业与工业照明",
      "brands": "Gauss, ERA, IEK, Jazzway",
      "oem": "高光效 UFO 工矿灯、防爆三防灯、磁吸轨道灯 OEM/ODM 直采契机极佳。"
    }
  ],

  "OEM_OPPORTUNITY_DATA": {
    "title": "去欧美化后的中国源头工厂直采红利",
    "tag": "战略合作高地",
    "desc": "欧洲巨头撤离后出现巨大空白，急需质量过硬、具备 EAC 认证的中国源头工厂直采..."
  },

  "DECISION_CHAIN_DATA": [
    {"step": "01", "role": "RAEC 联合集采委员会", "desc": "大宗标准电气电缆统谈统采..."},
    {"step": "02", "role": "总部商业采购中心", "desc": "负责新增特色品类与海外对华采购框架协议..."}
  ],

  "CONTACT_PATH_DATA": {
    "官方采购商城": "https://kristall43.ru",
    "供应链热线": "8 (800) 201-68-50",
    "采购专线邮箱": "help@kristall43.ru"
  },

  "SUPPLY_CHART_TITLE": "对华大宗商品采购估值与品类趋势",
  "CHART3_OPTION": {
    "tooltip": {"trigger": "axis", "axisPointer": {"type": "cross"}},
    "legend": {"data": ["对华直采总金额 (百万¥/€/$)", "核心品类一", "核心品类二", "核心品类三"]},
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": true},
    "xAxis": {"type": "category", "data": ["2020", "2021", "2022", "2023", "2024", "2025(E)", "2026(E)"]},
    "yAxis": {"type": "value", "name": "采购金额"},
    "series": [
      {
        "name": "对华直采总金额 (百万¥/€/$)",
        "type": "line",
        "smooth": true,
        "data": [6.5, 9.2, 13.0, 18.5, 24.0, 31.5, 39.0],
        "itemStyle": {"color": "#dc2626"},
        "lineStyle": {"width": 3}
      },
      {
        "name": "核心品类一",
        "type": "bar",
        "stack": "品类结构",
        "data": [3.0, 4.2, 6.0, 8.8, 11.5, 15.0, 19.0],
        "itemStyle": {"color": "#2563eb"}
      },
      {
        "name": "核心品类二",
        "type": "bar",
        "stack": "品类结构",
        "data": [2.2, 3.0, 4.2, 5.8, 7.5, 10.0, 12.5],
        "itemStyle": {"color": "#059669"}
      },
      {
        "name": "核心品类三",
        "type": "bar",
        "stack": "品类结构",
        "data": [1.3, 2.0, 2.8, 3.9, 5.0, 6.5, 7.5],
        "itemStyle": {"color": "#f59e0b"}
      }
    ]
  },

  "SUPPLY_FLOW_DATA": [
    {"title": "源头工厂直采", "desc": "RAEC集采 / 广东浙江电气产区"},
    {"title": "中欧班列清关", "desc": "口岸直通 ➔ 莫斯科/叶卡枢纽"},
    {"title": "中央总仓分拨", "desc": "全项性能抽检 / 配电车间领料"},
    {"title": "全境终端履约", "desc": "30+ 门店自提 / 专车配送"}
  ],

  "COMPLIANCE_DATA": [
    {"standard": "EAC TR CU 004/2011 (LVD)", "badge": "强制认证", "desc": "低电压电气设备安全指令，全系产品必备。"},
    {"standard": "EAC TR CU 020/2011 (EMC)", "badge": "强制认证", "desc": "电磁兼容性指令，LED驱动与智能开关必须达标。"}
  ],

  "SECTION_6_LOGISTICS_TIP": "跨境结算与物流建议：优先采用中俄跨境人民币（RMB / CIPS）直付通道，单票运输周期约 18-25 天。",

  "PAIN_POINTS_DATA": [
    {"title": "传统欧洲备件短缺与价格畸高", "level": "供应链缺口", "desc": "工业设备存量维保急需高兼容性中国元器件平替..."},
    {"title": "高寒环境（-35°C）驱动失效", "level": "工况环境痛点", "desc": "极寒环境下电容冻裂与漏水频发，要求 -40°C 宽温驱动..."}
  ],

  "SOCIAL_MEDIA_DATA": {
    "score": "Yandex / 2GIS 评分 4.6/5.0",
    "satisfaction": "电工好评率 92%",
    "pros": "配件极齐全、配电箱现场可配齐、积分返现划算",
    "cons": "智能家居配件偶有缺货、希望多增加极简轻奢面板",
    "source": "https://vk.com/kristall"
  },

  "IMPROVEMENTS_DATA": [
    {"title": "耐高寒超宽温驱动电源", "desc": "标配 -40°C~+50°C 宽温恒流隔离驱动，内置防雷抗浪涌保护。"},
    {"title": "俄标免零线单火智能开关", "desc": "针对老旧建筑无零线痛点，开发支持 220V 俄标底盒的 Tuya 单火触控面板。"}
  ],

  "STRATEGIES_DATA": [
    {
      "title": "选品与产品定制策略：主打全套 EAC 合规的耐高寒工商业 LED 照明与配电平替",
      "desc": "针对其工程客户高频采购品类，推出具备 TR CU 004/020 认证的高光效工矿灯与磁吸灯具，提供与标准 DIN 导轨兼容的断路器、浪涌保护器，综合降本 40%+。"
    },
    {
      "title": "价格带与包装规格策略：分级定价切入工程直供与零售分销，标配全俄文彩盒",
      "desc": "设置阶梯起订量（零售样单 MOQ 100-300 件，工程批量 MOQ 1000+ 件）；外包装采用高强度瓦楞纸箱及全俄文产品参数标签与 EAN-13 零售条码，适配终端货架直销。"
    },
    {
      "title": "质量合规与认证门禁：筑牢 EAC 准入与高寒可靠性背书，规避海关清关风险",
      "desc": "前置完备 EAC 证书及第三方俄标实验室耐低温（-40°C）检测报告；提供 3-5 年换新质保承诺，解决其核心客户对高寒工况故障的后顾之忧。"
    },
    {
      "title": "渠道切入与对接路径：切入 RAEC 联合集采与商业采购中心，提供快速打样试单",
      "desc": "首选对接总部商业采购中心及 RAEC 联合集采委员会，提供免费工程样品与测试报告；支持中俄跨境人民币（CIPS）直付通道，单票中欧班列 18-25 天快速交付。"
    }
  ]
}
```

---

## 质量与美学审计门禁 (Visual Quality Gates)

1. **结构化卡片全覆盖**：所有文本板块均必须通过 `XXX_DATA` 纯数据结构注入，严禁任何大段无格式裸文本。
2. **自动净化与自愈**：自动剥离 Emoji、去除法律后缀、清洗非法 HTML。
3. **生图双轨自愈（--auto-flow）**：未指定横幅时直连本地 CDP 9222 驱动 Google Flow 自动生成 16:9 现代店面实景图并优化嵌入。
4. **知识图谱互联与任务闭环**：自动互联站内关联企业超链接，发布后自动回写 `/api/agent/tasks/complete`。
5. **过程临时文件自动清理（仅保留 HTML 报告）**：HTML 报告内置高保真 CSS、JS 与 Base64 门店横幅图，属于完全自包含的独立文件。流水线完成发布与回写后，必须自动清理构建过程中产生的中间临时文件（`report_data.json`、生成的本地 `.jpg` 店面图、`scratch/` 脚本等），确保客户档案目录下**仅保留最终的 `.html` 报告文件**。
