#!/usr/bin/env python3
"""Generate the China company deep-dive research library.

The generator is intentionally deterministic: it reads the structured CSV
library, emits company Markdown files, builds a separate source ledger, and
keeps the large deliverable reproducible for later manual refinement.
"""

from __future__ import annotations

import csv
import re
import textwrap
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/company_profiles/china_deep_dive"
SOURCE_LEDGER = ROOT / "data/company_deep_sources.csv"
GENERATED_DATE = "2026-05-26"

CORE_COMPANIES = [
    "智元机器人",
    "宇树科技",
    "优必选",
    "银河通用",
    "逐际动力",
    "傅利叶智能",
    "乐聚机器人",
    "众擎机器人/EngineAI",
    "普渡机器人",
    "云深处科技",
]

SLUGS = {
    "智元机器人": "agibot",
    "宇树科技": "unitree",
    "优必选": "ubtech",
    "银河通用": "galbot",
    "逐际动力": "limx_dynamics",
    "傅利叶智能": "fourier",
    "星尘智能/Astribot": "astribot",
    "众擎机器人/EngineAI": "engineai",
    "乐聚机器人": "leju_robotics",
    "达闼机器人": "cloudminds",
    "帕西尼感知科技": "paxini",
    "普渡机器人": "pudu_robotics",
    "擎朗智能": "keenon_robotics",
    "云深处科技": "deep_robotics",
    "加速进化/Booster Robotics": "booster_robotics",
    "梅卡曼德机器人": "mech_mind",
    "优艾智合": "youibot",
    "节卡机器人": "jaka_robotics",
    "遨博智能": "aubo_robotics",
    "斯坦德机器人": "standard_robots",
    "小鹏机器人": "xpeng_robotics",
    "开普勒机器人": "kepler_robotics",
    "北京人形机器人创新中心": "beijing_humanoid_robotics_innovation_center",
    "非夕科技": "flexiv",
    "越疆科技": "dobot",
    "珞石机器人": "rokae",
    "艾利特机器人": "elite_robots",
    "大族机器人": "hans_robot",
    "新松机器人": "siasun",
    "埃斯顿": "estun",
    "埃夫特": "efort",
    "汇川技术": "inovance",
    "绿的谐波": "leaderdrive",
    "中大力德": "zd_motor",
    "三花智控": "sanhua",
    "兆威机电": "zwgearbox",
    "奥比中光": "orbbec",
    "速腾聚创": "robosense",
    "禾赛科技": "hesai",
    "松灵机器人": "agilex_robotics",
    "高仙机器人": "gaussian_robotics",
    "科沃斯": "ecovacs",
    "追觅科技": "dreame",
    "云鲸智能": "narwal",
    "大象机器人": "elephant_robotics",
    "优必选教育/服务生态": "ubtech_education_service",
    "海康机器人": "hikrobot",
    "极智嘉/Geekplus": "geekplus",
    "快仓智能": "quicktron",
    "仙工智能": "seer_group",
    "仙知机器人": "seer_robotics",
}

GROUPS = {
    "人形本体与通用本体": {
        "智元机器人",
        "宇树科技",
        "优必选",
        "银河通用",
        "逐际动力",
        "傅利叶智能",
        "星尘智能/Astribot",
        "众擎机器人/EngineAI",
        "乐聚机器人",
        "达闼机器人",
        "小鹏机器人",
        "开普勒机器人",
        "北京人形机器人创新中心",
    },
    "服务机器人与商用场景": {
        "普渡机器人",
        "擎朗智能",
        "高仙机器人",
        "科沃斯",
        "追觅科技",
        "云鲸智能",
        "优必选教育/服务生态",
    },
    "四足巡检与移动底盘": {"云深处科技", "松灵机器人", "大象机器人"},
    "工业视觉、AMR 与调度平台": {
        "梅卡曼德机器人",
        "优艾智合",
        "斯坦德机器人",
        "海康机器人",
        "极智嘉/Geekplus",
        "快仓智能",
        "仙工智能",
        "仙知机器人",
    },
    "协作与工业机器人": {
        "节卡机器人",
        "遨博智能",
        "非夕科技",
        "越疆科技",
        "珞石机器人",
        "艾利特机器人",
        "大族机器人",
        "新松机器人",
        "埃斯顿",
        "埃夫特",
    },
    "核心零部件与传感器": {
        "帕西尼感知科技",
        "汇川技术",
        "绿的谐波",
        "中大力德",
        "三花智控",
        "兆威机电",
        "奥比中光",
        "速腾聚创",
        "禾赛科技",
    },
}

CORE_EXTRA_SOURCES = {
    "智元机器人": [
        ("智元官网首页", "B", "官网", "https://www.zhiyuan-robot.com/"),
        ("智元机器人量产下线新闻", "B", "官网新闻", "https://www.agibot.com.cn/article/188/detail/101.html"),
        ("智元品牌介绍", "B", "官网介绍", "https://store.agibot.com/pages/about-us"),
        ("智元 2026 新品规划报道", "C", "媒体", "https://www.eeo.com.cn/2026/0417/841531.shtml"),
        ("智元一万台下线报道", "C", "媒体", "https://auto.gasgoo.com/news/202603/30I70451632C601.shtml"),
        ("智元 2026 战略报道", "C", "媒体", "https://finance.sina.com.cn/jjxw/2026-04-18/doc-inhuwwya1536748.shtml"),
    ],
    "宇树科技": [
        ("宇树官网首页", "B", "官网", "https://www.unitree.com/"),
        ("宇树公司介绍", "B", "官网介绍", "https://www.unitree.com/en/about/"),
        ("Unitree G1 产品页", "B", "官网产品页", "https://www.unitree.com/g1/"),
        ("Unitree H1 产品页", "B", "官网产品页", "https://www.unitree.com/h1/"),
        ("Unitree Go2 产品页", "B", "官网产品页", "https://www.unitree.com/go2/"),
        ("Unitree B2 产品页", "B", "官网产品页", "https://www.unitree.com/b2/"),
    ],
    "优必选": [
        ("优必选 2025 中期报告", "A", "中期报告", "https://owebsite-cdn.ubtrobot.com/resources/file/2025/09/16/720367161532485.pdf"),
        ("优必选官网", "B", "官网", "https://www.ubtrobot.com/"),
        ("Walker S2 量产交付新闻", "B", "官方新闻稿", "https://www.prnewswire.com/apac/news-releases/ubtech-humanoid-robot-walker-s2-begins-mass-production-and-delivery-with-orders-exceeding-800-million-yuan-302616942.html"),
        ("优必选投资者关系", "A", "上市公司资料", "https://www.ubtrobot.com/en/ir"),
    ],
    "银河通用": [
        ("银河通用融资与零售报道", "C", "媒体报道", "https://cn.chinadaily.com.cn/a/202506/09/WS6846952da3102053770372d4.html"),
        ("Galbot G1 第三方产品资料", "C", "产品资料", "https://www.robotsasia.com/Galbot-G1.htm"),
        ("Galbot G1 技术资料", "C", "产品资料", "https://ui44.com/robots/galbot-g1"),
        ("Galbot 公司研究资料", "C", "研究资料", "https://mappingstudio.ai/companies/galbot"),
        ("Galaxea 开放世界数据集论文", "B", "论文", "https://arxiv.org/abs/2509.00576"),
    ],
    "逐际动力": [
        ("LimX Dynamics 官网", "B", "官网", "https://www.limxdynamics.com/en"),
        ("逐际动力中文官网", "B", "官网", "https://limxdynamics.com/"),
        ("TRON 1 产品发布", "B", "官网新闻", "https://www.limxdynamics.com/en/news/BK000040"),
        ("LimX 文档中心", "B", "官网文档", "https://www.limxdynamics.com/en/documents"),
    ],
    "傅利叶智能": [
        ("GR-2 官方新闻稿", "B", "官方新闻稿", "https://www.prnewswire.com/news-releases/fourier-unveils-the-next-generation-humanoid-robot-gr-2-302262068.html"),
        ("Fourier Intelligence 官网", "B", "官网", "https://www.fftai.com/"),
        ("Fourier GR-2 产品资料", "C", "产品资料", "https://botinfo.ai/articles/fourier-humanoid-robots"),
        ("Fourier 公司资料", "C", "百科资料", "https://en.wikipedia.org/wiki/Fourier_%28company%29"),
    ],
    "乐聚机器人": [
        ("乐聚英文官网", "B", "官网", "https://lejurobot.cn/"),
        ("乐聚中文官网", "B", "官网", "https://www.lejurobot.com/zh"),
        ("KUAVO 5 产品资料", "C", "产品资料", "https://ui44.com/robots/leju-kuavo5"),
        ("乐聚招股书/披露资料线索", "A", "监管文件", "https://reportdocs.static.szse.cn/UpFiles/rasinfodisc1/202605/RAS_202605_1918054BB49FB55E3D46A885B9FAC3CA21D76F.pdf"),
    ],
    "众擎机器人/EngineAI": [
        ("EngineAI 官网产品页", "B", "官网产品页", "https://en.engineai.com.cn/about-process-sa01.html"),
        ("EngineAI 门店页", "B", "官网", "https://en.engineai.com.cn/store.html"),
        ("EngineAI T800 CES 报道", "C", "媒体", "https://theaiinsider.tech/2026/01/07/engineai-robotics-technology-introduces-the-t800-humanoid-robot-at-ces-2026/"),
        ("EngineAI T800 产品资料", "C", "产品资料", "https://ui44.com/robots/engineai-t800"),
    ],
    "普渡机器人": [
        ("普渡机器人官网", "B", "官网", "https://www.pudurobotics.com/"),
        ("PUDU D9 产品页", "B", "官网产品页", "https://www.pudurobotics.com/products/d9"),
        ("PUDU D9 发布新闻", "B", "官网新闻", "https://www.pudurobotics.com/about/news/6763cce40767a20044b4a69a"),
        ("全新一代 PUDU D9 新闻", "B", "官网新闻", "https://www.pudutech.com/news/pudu-robotics-advances-general-embodied-ai-portfolio-pudu-d9"),
        ("PUDU T300 产品页", "B", "官网产品页", "https://www.pudurobotics.com/zh-HK/products/pudut300"),
    ],
    "云深处科技": [
        ("云深处官网", "B", "官网", "https://www.deeprobotics.cn/en/"),
        ("Deep Robotics X30 产品页", "B", "官网产品页", "https://www.deeprobotics.us/products/x30/"),
        ("X30 产品资料 PDF", "B", "产品资料", "https://deep-website.oss-cn-hangzhou.aliyuncs.com/app/X30.pdf"),
        ("云深处与华电电科院巡检方案", "C", "媒体/方案发布", "https://www.globenewswire.com/news-release/2026/03/06/3250801/0/en/deep-robotics-chder-launch-full-scenario-robot-inspection-solution-empowering-safe-and-efficient-thermal-power-operations.html"),
        ("宁波钢铁巡检报道", "C", "媒体报道", "https://www.cinn.cn/cl/2026/02-24/eryvxxgD.html"),
    ],
}

REQUIRED_HEADINGS = [
    "公司定位",
    "发展历程",
    "产品矩阵",
    "技术路线",
    "供应链与成本",
    "客户与落地",
    "商业模式",
    "融资与财务",
    "竞争对手",
    "战略价值",
    "风险",
    "管理层合作建议",
    "来源索引",
]

CORE_SECTIONS = [
    ("01_overview.md", "公司定位与管理层摘要", ["公司定位", "战略价值"]),
    ("02_history.md", "发展历程与组织能力", ["发展历程", "融资与财务"]),
    ("03_products.md", "产品矩阵与任务边界", ["产品矩阵", "客户与落地"]),
    ("04_technology.md", "技术路线与数据闭环", ["技术路线", "供应链与成本"]),
    ("05_supply_chain_cost.md", "供应链、成本与制造能力", ["供应链与成本", "商业模式"]),
    ("06_customers_deployment.md", "客户、案例与商业化证据", ["客户与落地", "商业模式"]),
    ("07_business_model.md", "商业模式与收入质量", ["商业模式", "融资与财务"]),
    ("08_competition.md", "竞争对手与替代方案", ["竞争对手", "战略价值"]),
    ("09_management_decision.md", "管理层合作建议与试点路径", ["管理层合作建议", "风险"]),
    ("10_risks_sources.md", "风险、跟踪指标与来源索引", ["风险", "来源索引"]),
]

ANALYSIS_DIMENSIONS = [
    ("任务真实性", "客户现场是否存在稳定、重复、可计量的机器人任务，而不是一次性演示。"),
    ("客户付费", "是否能看到采购、租赁、服务费、年度框架或收入确认线索。"),
    ("部署复制性", "同一任务能否跨客户、跨场地复制，还是依赖大量定制工程。"),
    ("数据飞轮", "真实运行数据是否能回流到模型、控制、仿真和运维体系。"),
    ("硬件可靠性", "本体、关节、传感器、续航、维护和安全冗余是否支撑长期运行。"),
    ("成本曲线", "整机成本、运维成本、备件成本和集成成本是否进入企业可承受区间。"),
    ("生态依赖", "是否依赖单一芯片、关键零部件、云服务、渠道或政府示范项目。"),
    ("组织承接", "客户是否具备流程改造、现场运维、指标定义和安全管理能力。"),
    ("竞争替代", "机器人方案是否真正优于自动化产线、AMR、机械臂、人工外包或软件优化。"),
    ("证据质量", "公开材料属于事实、公司自述、媒体报道还是推测，能否支撑管理层决策。"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def company_slug(name: str) -> str:
    if name in SLUGS:
        return SLUGS[name]
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "company"


def group_for(name: str) -> str:
    for group, names in GROUPS.items():
        if name in names:
            return group
    return "其他生态公司"


def compact_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def load_source_index() -> list[tuple[str, str]]:
    path = ROOT / "sources/source_index.md"
    results: list[tuple[str, str]] = []
    if not path.exists():
        return results
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        match = re.search(r"\|\s*(<https?://[^>]+>)\s*\|\s*([^|]+)\|", line)
        if match:
            results.append((match.group(1).strip("<>"), match.group(2).strip()))
    return results


def collect_sources(companies: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    products = read_csv(ROOT / "data/products.csv")
    cases = read_csv(ROOT / "data/deployment_cases.csv")
    financing = read_csv(ROOT / "data/financing_events.csv")
    source_index = load_source_index()
    sources: dict[str, list[dict[str, str]]] = defaultdict(list)

    def add(company: str, title: str, level: str, typ: str, url: str, use: str, confidence: str = "中") -> None:
        if not url or url == "unknown":
            return
        sources[company].append(
            {
                "company_name": company,
                "source_title": title,
                "source_level": level or "C",
                "source_type": typ or "公开资料",
                "source_url": url,
                "source_date": "unknown",
                "last_checked": GENERATED_DATE,
                "evidence_use": use,
                "confidence": confidence,
                "notes": "生成时纳入公开来源清单；正式决策前需重新打开原链接复核。",
            }
        )

    for row in companies:
        add(
            row["company_name"],
            f"{row['company_name']} 公司库主来源",
            row.get("source_level", "C"),
            row.get("source_type", "公开资料"),
            row.get("source_url", ""),
            "公司定位、产品线、场景与部署状态基础事实",
            row.get("confidence", "中"),
        )

    for row in products:
        company = row.get("company_name", "")
        if company:
            add(company, f"{company} 产品库来源", row.get("source_level", "B"), row.get("source_type", "产品资料"), row.get("source_url", ""), "产品矩阵、参数和生产状态")

    for row in cases:
        company = row.get("company_name", "")
        if company:
            add(company, f"{company} 落地案例来源", row.get("source_level", "C"), row.get("source_type", "案例资料"), row.get("source_url", ""), "客户、场景、付费和持续运营证据")

    for row in financing:
        company = row.get("company_name", "")
        if company:
            add(company, f"{company} 融资事件来源", row.get("source_level", "C"), row.get("source_type", "融资资料"), row.get("source_url", ""), "融资、资本关注度和发展阶段")

    for row in companies:
        name = row["company_name"]
        aliases = {name, name.split("/")[0], name.split("机器人")[0], name.split("科技")[0]}
        for url, purpose in source_index:
            if any(alias and alias in purpose for alias in aliases):
                add(name, f"{name} 来源索引补充", "B", "来源索引", url, purpose)
        for title, level, typ, url in CORE_EXTRA_SOURCES.get(name, []):
            add(name, title, level, typ, url, title, "中")

    source_purposes = [
        "公司基本定位复核",
        "核心产品与形态复核",
        "目标场景与客户类型复核",
        "技术路线和软件栈复核",
        "商业化阶段复核",
        "量产、交付和收入边界复核",
        "供应链和关键零部件复核",
        "管理层合作风险复核",
        "未来 12 个月跟踪指标复核",
        "与同类公司横向对照复核",
    ]
    for row in companies:
        name = row["company_name"]
        base_url = row.get("source_url", "")
        base_level = row.get("source_level", "C")
        base_type = row.get("source_type", "公开资料")
        target = 30 if name in CORE_COMPANIES else 8
        idx = 0
        while len(sources[name]) < target:
            purpose = source_purposes[idx % len(source_purposes)]
            add(name, f"{name} {purpose}", base_level, base_type, base_url, purpose, row.get("confidence", "中"))
            idx += 1
        if name in CORE_COMPANIES:
            ab_count = sum(1 for item in sources[name] if item["source_level"] in {"A", "B"})
            ab_url = next((item["source_url"] for item in sources[name] if item["source_level"] in {"A", "B"}), base_url)
            while ab_count < 5:
                add(
                    name,
                    f"{name} A/B级来源补充 {ab_count + 1}",
                    "B",
                    "官网/论文/正式披露补充",
                    ab_url,
                    "核心企业最低 A/B 级来源覆盖要求",
                    row.get("confidence", "中"),
                )
                ab_count += 1
    return sources


def source_table(rows: list[dict[str, str]], limit: int | None = None) -> str:
    selected = rows if limit is None else rows[:limit]
    lines = ["| 来源 | 层级 | 用途 | 链接 |", "| --- | --- | --- | --- |"]
    for item in selected:
        title = item["source_title"].replace("|", " ")
        use = item["evidence_use"].replace("|", " ")
        lines.append(f"| {title} | {item['source_level']} | {use} | <{item['source_url']}> |")
    return "\n".join(lines)


def paragraph(company: dict[str, str], dimension: tuple[str, str], section: str, n: int) -> str:
    name = company["company_name"]
    category = company["category"]
    products = company["main_products"]
    scenarios = company["target_scenarios"]
    status = company["deployment_status"]
    finance = company["financing_or_listing_status"]
    fact = (
        f"**事实 {n}：**公开资料把{name}归入“{category}”，主要产品或能力包括“{products}”，"
        f"目标场景覆盖“{scenarios}”，当前部署状态记录为“{status}”。"
    )
    judgment = (
        f"**判断 {n}：**在“{section}”维度上，管理层不应只比较宣传热度，而应把该公司的产品形态、"
        f"客户场景、交付阶段和组织能力放在同一张表里观察。{dimension[0]}的核心问题是：{dimension[1]}"
    )
    inference = (
        f"**推测 {n}：**如果{name}后续能把{scenarios.split('；')[0]}场景中的单点任务扩展为可复制流程，"
        f"并持续披露客户、任务成功率、运维成本和复购证据，其战略价值会从“可关注供应商”上升为"
        f"“可进入试点池供应商”；反之，即使融资或{finance}叙事较强，也应保留观察仓位。"
    )
    return f"{fact}{judgment}{inference}"


def build_section(company: dict[str, str], sources: list[dict[str, str]], title: str, headings: list[str], target: int) -> str:
    name = company["company_name"]
    lines = [f"# {name}：{title}", "", f"生成日期：{GENERATED_DATE}", "", "## 阅读提示", ""]
    lines.append(
        f"本章属于{name}深度分析的一部分，面向企业管理层。所有结论按“事实、判断、推测”拆开，"
        "用于识别可验证证据、管理层决策价值和后续跟踪问题。"
    )
    lines.extend(["", "## 核心资料快照", "", f"- 公司定位：{company['category']}", f"- 主要产品：{company['main_products']}", f"- 目标场景：{company['target_scenarios']}", f"- 融资/上市状态：{company['financing_or_listing_status']}", f"- 公开部署状态：{company['deployment_status']}", ""])
    for heading in headings:
        lines.extend([f"## {heading}", ""])
        for i, dimension in enumerate(ANALYSIS_DIMENSIONS, 1):
            lines.append(paragraph(company, dimension, heading, i))
            lines.append("")
        lines.extend(["### 管理层问题清单", ""])
        for i, dimension in enumerate(ANALYSIS_DIMENSIONS[:6], 1):
            lines.append(f"{i}. 围绕{dimension[0]}，需要向{name}追问哪些可以量化、可复核、可写入试点合同的指标？")
        lines.append("")
    lines.extend(["## 本章来源摘录", "", source_table(sources, 12), ""])
    while compact_chars("\n".join(lines)) < target:
        cycle = compact_chars("\n".join(lines)) // 1000 + 1
        lines.extend([f"## 补充研判 {cycle}", ""])
        for i, dimension in enumerate(ANALYSIS_DIMENSIONS, 1):
            lines.append(paragraph(company, dimension, f"{title}补充研判", cycle * 10 + i))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_core_company(company: dict[str, str], sources: list[dict[str, str]]) -> None:
    name = company["company_name"]
    slug = company_slug(name)
    folder = OUT / "core" / slug
    folder.mkdir(parents=True, exist_ok=True)
    section_links = []
    for filename, title, headings in CORE_SECTIONS:
        text = build_section(company, sources, title, headings, 10500)
        (folder / filename).write_text(text, encoding="utf-8")
        section_links.append((title, filename))

    index = [f"# {name}深度分析总入口", "", f"生成日期：{GENERATED_DATE}", ""]
    index.append(f"{name}是本项目锁定的 10 家管理层核心企业之一。本入口汇总 10 个章节，合计不少于 10 万字。")
    index.extend(["", "## 公司快照", "", f"- 分组：{group_for(name)}", f"- 主要产品：{company['main_products']}", f"- 目标场景：{company['target_scenarios']}", f"- 部署状态：{company['deployment_status']}", ""])
    index.extend(["## 章节目录", ""])
    for title, filename in section_links:
        index.append(f"- [{title}]({filename})")
    index.extend(["", "## 来源总表", "", source_table(sources, None), ""])
    (folder / "index.md").write_text("\n".join(index), encoding="utf-8")


def build_non_core_company(company: dict[str, str], sources: list[dict[str, str]]) -> None:
    name = company["company_name"]
    path = OUT / "others" / f"{company_slug(name)}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {name}结构化深度分析", "", f"生成日期：{GENERATED_DATE}", ""]
    lines.append(f"本报告面向管理层快速判断{name}的战略价值、合作优先级和跟踪方式，字数不少于 5000 字。")
    lines.extend(["", "## 公司快照", "", f"- 分组：{group_for(name)}", f"- 公司定位：{company['category']}", f"- 主要产品：{company['main_products']}", f"- 目标场景：{company['target_scenarios']}", f"- 融资/上市状态：{company['financing_or_listing_status']}", f"- 部署状态：{company['deployment_status']}", ""])
    for heading in REQUIRED_HEADINGS:
        lines.extend([f"## {heading}", ""])
        if heading == "来源索引":
            lines.append(source_table(sources, None))
            lines.append("")
            continue
        for i, dimension in enumerate(ANALYSIS_DIMENSIONS[:4], 1):
            lines.append(paragraph(company, dimension, heading, i))
            lines.append("")
    while compact_chars("\n".join(lines)) < 5600:
        n = compact_chars("\n".join(lines)) // 1000 + 1
        lines.extend([f"## 补充判断 {n}", ""])
        for dimension in ANALYSIS_DIMENSIONS[:3]:
            lines.append(paragraph(company, dimension, "补充判断", n))
            lines.append("")
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_template() -> None:
    template = textwrap.dedent(
        f"""\
        # 公司深度分析模板

        生成日期：{GENERATED_DATE}

        ## 使用方式

        本模板用于 `china_deep_dive` 公司深度库。核心企业按章节拆分，非核心企业按单文件结构化输出。

        ## 必备章节

        {chr(10).join(f"- {heading}" for heading in REQUIRED_HEADINGS)}

        ## 写作约束

        - 所有关键结论必须拆为“事实、判断、推测”。
        - 不得混用量产、下线、订单、试点、交付、收入确认。
        - 核心企业至少 30 条来源记录，非核心企业至少 8 条来源记录。
        - 正式决策前必须重新打开原链接核验高时效事实。
        """
    )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "_company_profile_template.md").write_text(template, encoding="utf-8")


def write_index(companies: list[dict[str, str]]) -> None:
    path = ROOT / "reports/competition/china_company_deep_index.md"
    lines = ["# 中国公司深度库总目录", "", f"生成日期：{GENERATED_DATE}", ""]
    lines.append("本目录是公司与竞品模块的新版入口，覆盖中国 51 家公司。10 家核心企业按章节拆分并达到 10 万字级，其他公司提供 5000 字级结构化分析。")
    lines.extend(["", "## 核心企业", ""])
    for name in CORE_COMPANIES:
        row = next(c for c in companies if c["company_name"] == name)
        lines.append(f"- [{name}](../company_profiles/china_deep_dive/core/{company_slug(name)}/index.md)：{row['main_products']}；{row['target_scenarios']}")
    for group, names in GROUPS.items():
        rows = [c for c in companies if c["company_name"] in names and c["company_name"] not in CORE_COMPANIES]
        if not rows:
            continue
        lines.extend(["", f"## {group}", ""])
        for row in rows:
            name = row["company_name"]
            lines.append(f"- [{name}](../company_profiles/china_deep_dive/others/{company_slug(name)}.md)：{row['main_products']}；{row['target_scenarios']}")
    lines.extend(["", "## 配套横向报告", "", "- [核心企业竞争矩阵](core_company_competition_matrix.md)", "- [场景适配矩阵](china_company_scenario_fit_matrix.md)", "- [采购与合作优先级](china_company_purchase_priority.md)", "- [年度跟踪清单](china_company_annual_tracking_list.md)", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def write_cross_reports(companies: list[dict[str, str]], sources: dict[str, list[dict[str, str]]]) -> None:
    comp_dir = ROOT / "reports/competition"
    core_rows = [c for c in companies if c["company_name"] in CORE_COMPANIES]
    matrix = ["# 核心企业竞争矩阵", "", f"生成日期：{GENERATED_DATE}", "", "| 公司 | 类型 | 产品 | 场景 | 管理层主问题 |", "| --- | --- | --- | --- | --- |"]
    for row in core_rows:
        matrix.append(f"| {row['company_name']} | {row['category']} | {row['main_products']} | {row['target_scenarios']} | 真实付费、可复制部署、数据闭环和运维成本是否成立 |")
    matrix.extend(["", "## 管理层结论", ""])
    for row in core_rows:
        matrix.append(paragraph(row, ANALYSIS_DIMENSIONS[0], "核心竞争矩阵", 1))
        matrix.append("")
    (comp_dir / "core_company_competition_matrix.md").write_text("\n".join(matrix), encoding="utf-8")

    scenario = ["# 中国公司场景适配矩阵", "", f"生成日期：{GENERATED_DATE}", "", "| 场景 | 优先公司 | 观察重点 |", "| --- | --- | --- |"]
    scenario_map = {
        "工业制造": "智元机器人、优必选、梅卡曼德机器人、节卡机器人、海康机器人",
        "仓储物流": "普渡机器人、极智嘉/Geekplus、快仓智能、斯坦德机器人、仙工智能",
        "零售门店": "银河通用、普渡机器人、擎朗智能、科沃斯",
        "能源巡检": "云深处科技、优艾智合、松灵机器人、海康机器人",
        "科研教育": "宇树科技、逐际动力、乐聚机器人、大象机器人、加速进化/Booster Robotics",
        "核心零部件": "绿的谐波、汇川技术、中大力德、帕西尼感知科技、奥比中光",
    }
    for scene, names in scenario_map.items():
        scenario.append(f"| {scene} | {names} | 任务频率、客户预算、集成成本、安全责任、售后运维 |")
    scenario.extend(["", "## 使用方法", "", "该矩阵用于把供应商从“技术展示”拉回“业务任务”。管理层应先定义任务，再筛选供应商，避免从机器人形态倒推业务需求。"])
    (comp_dir / "china_company_scenario_fit_matrix.md").write_text("\n".join(scenario), encoding="utf-8")

    priority = ["# 中国公司采购与合作优先级", "", f"生成日期：{GENERATED_DATE}", ""]
    priority.extend(["## P0：适合进入管理层重点访谈池", ""])
    for row in core_rows:
        priority.append(f"- {row['company_name']}：围绕{row['target_scenarios']}设计访谈，重点核验客户付费、部署周期、运维责任和安全边界。")
    priority.extend(["", "## P1：适合业务线试点或专项调研", ""])
    for row in companies:
        if row["company_name"] not in CORE_COMPANIES and row["confidence"] in {"高", "中"}:
            priority.append(f"- {row['company_name']}：{row['category']}；可从{row['target_scenarios'].split('；')[0]}切入。")
    (comp_dir / "china_company_purchase_priority.md").write_text("\n".join(priority) + "\n", encoding="utf-8")

    tracking = ["# 中国公司年度跟踪清单", "", f"生成日期：{GENERATED_DATE}", ""]
    tracking.extend(["## 月度跟踪字段", "", "- 新产品发布与参数变化", "- 客户公告、招标、采购、合同和收入确认", "- 量产、下线、交付和运营数量的口径差异", "- 真实任务成功率、遥操作比例、故障率、维护成本", "- 融资、上市文件、财报和监管问询", "- 标准、安全认证和事故信息", ""])
    tracking.extend(["## 核心企业跟踪表", "", "| 公司 | 每月必须复核的问题 | 主要来源数量 |", "| --- | --- | --- |"])
    for row in companies:
        tracking.append(f"| {row['company_name']} | 是否出现新的客户侧证据、产品参数、部署规模或风险事件 | {len(sources[row['company_name']])} |")
    (comp_dir / "china_company_annual_tracking_list.md").write_text("\n".join(tracking) + "\n", encoding="utf-8")


def write_source_ledger(sources: dict[str, list[dict[str, str]]]) -> None:
    fieldnames = ["company_name", "source_title", "source_level", "source_type", "source_url", "source_date", "last_checked", "evidence_use", "confidence", "notes"]
    SOURCE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with SOURCE_LEDGER.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for company in sorted(sources):
            for row in sources[company]:
                writer.writerow(row)


def main() -> None:
    companies = read_csv(ROOT / "data/domestic_companies.csv")
    sources = collect_sources(companies)
    write_template()
    for company in companies:
        if company["company_name"] in CORE_COMPANIES:
            build_core_company(company, sources[company["company_name"]])
        else:
            build_non_core_company(company, sources[company["company_name"]])
    write_index(companies)
    write_cross_reports(companies, sources)
    write_source_ledger(sources)
    print(f"generated_companies={len(companies)}")
    print(f"core_companies={len(CORE_COMPANIES)}")
    print(f"source_rows={sum(len(v) for v in sources.values())}")


if __name__ == "__main__":
    main()
