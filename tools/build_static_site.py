#!/usr/bin/env python3
"""Build the Markdown/CSV static site into the html/ directory."""

from __future__ import annotations

import csv
import html as html_lib
import os
import re
from collections import defaultdict
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
HTML_ROOT = ROOT / "html"
ASSET_DIR = HTML_ROOT / "assets"
GENERATED_DATE = "2026-05-26"


def title_from_md(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("_", " ").replace("-", " ").title()


def csv_title(path: Path) -> str:
    names = {
        "domestic_companies.csv": "中国公司库",
        "overseas_companies.csv": "海外对照公司库",
        "products.csv": "产品库",
        "deployment_cases.csv": "落地案例库",
        "financing_events.csv": "融资事件库",
        "scenario_maturity.csv": "场景成熟度库",
        "company_deep_sources.csv": "公司深度来源库",
    }
    return names.get(path.name, path.stem.replace("_", " ").title())


def rel_href(from_file: Path, target: Path) -> str:
    return os.path.relpath(target, from_file.parent).replace(os.sep, "/")


def html_out_for(path: Path) -> Path:
    return HTML_ROOT / path.relative_to(ROOT).with_suffix(".html")


def collect_items() -> tuple[list[dict[str, object]], dict[Path, Path]]:
    md_files: list[Path] = []
    for base in [ROOT / "reports", ROOT / "docs", ROOT / "sources"]:
        md_files.extend(sorted(p for p in base.rglob("*.md") if not p.name.startswith("_")))
    csv_files = sorted(p for p in (ROOT / "data").glob("*.csv"))
    mapping = {p.resolve(): html_out_for(p) for p in md_files + csv_files}
    items: list[dict[str, object]] = []
    for p in md_files:
        items.append({"kind": "md", "source": p, "out": html_out_for(p), "title": title_from_md(p), "category": classify(p), "rel": p.relative_to(ROOT).as_posix()})
    for p in csv_files:
        items.append({"kind": "csv", "source": p, "out": html_out_for(p), "title": csv_title(p), "category": "数据与证据", "rel": p.relative_to(ROOT).as_posix()})
    order = {"管理层入口": 0, "行业基础课": 1, "公司与竞品": 2, "场景与商业化": 3, "战略决策工具": 4, "数据与证据": 5, "项目文档": 6}
    items.sort(key=lambda item: (order.get(str(item["category"]), 99), str(item["rel"])))
    return items, mapping


def classify(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "reports/management_learning_guide.md" or rel.startswith("reports/executive/"):
        return "管理层入口"
    if rel.startswith("reports/basics/") or rel in {"reports/industry_map.md", "reports/technology_routes.md"}:
        return "行业基础课"
    if rel.startswith("reports/company_profiles/") or rel.startswith("reports/competition/"):
        return "公司与竞品"
    if rel.startswith("reports/scenarios/") or rel in {"reports/commercialization_assessment.md", "reports/scenario_maturity_matrix.md"}:
        return "场景与商业化"
    if rel.startswith("reports/decision_tools/"):
        return "战略决策工具"
    if rel.startswith("sources/"):
        return "数据与证据"
    return "项目文档"


def page_header(current: Path) -> str:
    links = [
        ("目录首页", ROOT / "index.html"),
        ("学习指南", HTML_ROOT / "reports/management_learning_guide.html"),
        ("公司深度库", HTML_ROOT / "reports/competition/china_company_deep_index.html"),
        ("公司库", HTML_ROOT / "data/domestic_companies.html"),
        ("来源库", HTML_ROOT / "data/company_deep_sources.html"),
    ]
    nav = "\n".join(f'<a href="{rel_href(current, target)}">{label}</a>' for label, target in links)
    return f"""<header class="site-header">
  <a class="brand" href="{rel_href(current, ROOT / 'index.html')}"><span class="brand-mark" aria-hidden="true"></span><span>Embodied AI Research</span></a>
  <nav class="nav" aria-label="主导航">{nav}</nav>
</header>"""


def page_shell(current: Path, title: str, body: str, extra_class: str = "") -> str:
    css = rel_href(current, ASSET_DIR / "site.css")
    js = rel_href(current, ASSET_DIR / "site.js")
    favicon = rel_href(current, ASSET_DIR / "learning-map.svg")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html_lib.escape(title)} - 具身智能机器人行业研究</title>
  <link rel="stylesheet" href="{css}">
  <link rel="icon" type="image/svg+xml" href="{favicon}">
</head>
<body class="{extra_class}">
{page_header(current)}
{body}
<script src="{js}"></script>
</body>
</html>
"""


def write_assets(stats: dict[str, int]) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    css = """
:root{--ink:#17202a;--muted:#596579;--line:#d8dee8;--paper:#fbfcfe;--panel:#fff;--blue:#175c9e;--teal:#147d78;--amber:#b7791f;--nav:#101828;--soft:#eef6ff;--shadow:0 14px 36px rgba(16,24,40,.08)}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Arial,sans-serif;color:var(--ink);background:var(--paper);line-height:1.72;letter-spacing:0}a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}.site-header{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;gap:24px;padding:14px 32px;background:rgba(255,255,255,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(12px)}.brand{display:flex;align-items:center;gap:10px;min-width:0;font-weight:700;color:var(--nav)}.brand-mark{width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,var(--blue),var(--teal));display:inline-block;flex:0 0 auto}.nav{display:flex;flex-wrap:wrap;gap:10px;justify-content:flex-end}.nav a{padding:6px 10px;border-radius:6px;color:var(--nav);font-size:14px}.nav a:hover{background:var(--soft);text-decoration:none}.page-shell{width:min(1440px,calc(100% - 48px));margin:0 auto}.hero{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(360px,.9fr);gap:36px;align-items:center;padding:54px 0 28px}.hero h1{margin:0 0 16px;font-size:42px;line-height:1.18;color:var(--nav);letter-spacing:0}.hero p{margin:0 0 18px;color:var(--muted);font-size:17px}.button{display:inline-flex;align-items:center;justify-content:center;min-height:40px;padding:8px 14px;border:1px solid var(--line);border-radius:6px;font-weight:650;color:var(--nav);background:#fff}.button.primary{color:#fff;background:var(--blue);border-color:var(--blue)}.hero-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}.hero-visual{border:1px solid var(--line);border-radius:8px;background:#fff;box-shadow:var(--shadow);padding:16px;min-width:0}.hero-visual img{display:block;width:100%;height:auto}.metric-row{display:grid;grid-template-columns:repeat(6,minmax(120px,1fr));gap:12px;margin:18px 0 32px}.metric{background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px;min-width:0}.metric strong{display:block;font-size:25px;line-height:1.2;color:var(--nav)}.metric span{display:block;margin-top:4px;color:var(--muted);font-size:13px}.band{padding:26px 0;border-top:1px solid var(--line)}.band h2{margin:0 0 14px;color:var(--nav);font-size:24px}.toolbar{display:flex;gap:12px;align-items:center;justify-content:space-between;margin:12px 0 18px}.search{width:min(420px,100%);min-height:40px;border:1px solid var(--line);border-radius:6px;padding:8px 12px;font-size:15px}.card-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.card{display:flex;flex-direction:column;gap:8px;min-height:132px;min-width:0;padding:16px;border:1px solid var(--line);border-radius:8px;background:#fff}.card:hover{box-shadow:var(--shadow);text-decoration:none}.card .tag{width:fit-content;max-width:100%;padding:3px 8px;border-radius:5px;background:#edfafa;color:var(--teal);font-size:12px;font-weight:700}.card strong{color:var(--nav);font-size:16px;line-height:1.42;overflow-wrap:anywhere}.card small{color:var(--muted);overflow-wrap:anywhere}.docs-layout{display:grid;grid-template-columns:260px minmax(0,1fr);gap:30px;padding:30px 0 52px}.sidebar{position:sticky;top:73px;align-self:start;max-height:calc(100vh - 96px);overflow:auto;border-right:1px solid var(--line);padding-right:18px}.sidebar h2{margin:0 0 12px;font-size:16px}.sidebar a{display:block;padding:7px 8px;border-radius:6px;color:var(--nav);font-size:14px;overflow-wrap:anywhere}.sidebar a:hover{background:var(--soft);text-decoration:none}.content{min-width:0;max-width:1040px}.content h1{margin:0 0 18px;font-size:34px;line-height:1.25;color:var(--nav)}.content h2{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);font-size:24px;color:var(--nav)}.content h3{margin-top:24px;font-size:19px;color:#233044}.content p,.content li{color:#2f3a4b}.content code{padding:2px 5px;border-radius:4px;background:#eef2f7;font-size:.95em}.content pre{overflow-x:auto;padding:14px;border-radius:8px;background:#101828;color:#f8fafc}.content blockquote{margin:16px 0;padding:10px 16px;border-left:4px solid var(--teal);background:#edfafa;color:#244}.table-wrap{width:100%;overflow-x:auto;border:1px solid var(--line);border-radius:8px;background:#fff}table{width:100%;border-collapse:collapse;min-width:760px}th,td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{position:sticky;top:0;background:#f3f6fa;color:var(--nav);font-weight:700}tr:nth-child(even) td{background:#fcfdff}.meta{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 20px;color:var(--muted);font-size:13px}.meta span{padding:3px 8px;border-radius:5px;background:#fff7e6;color:#6f4a11}.footer{margin-top:48px;padding:24px 0 40px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}@media(max-width:1180px){.hero{grid-template-columns:1fr}.hero-visual{max-width:760px}.metric-row{grid-template-columns:repeat(3,minmax(120px,1fr))}.card-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:900px){.site-header{align-items:flex-start;flex-direction:column;padding:12px 20px}.page-shell{width:min(100% - 32px,1440px)}.hero h1{font-size:32px}.metric-row{grid-template-columns:repeat(2,minmax(120px,1fr))}.card-grid{grid-template-columns:1fr}.docs-layout{grid-template-columns:1fr}.sidebar{position:static;max-height:none;border-right:0;border-bottom:1px solid var(--line);padding:0 0 16px}}
""".strip()
    (ASSET_DIR / "site.css").write_text(css + "\n", encoding="utf-8")
    (ASSET_DIR / "site.js").write_text(
        "(function(){const i=document.querySelector('[data-search]');if(!i)return;const c=Array.from(document.querySelectorAll('[data-card]'));i.addEventListener('input',()=>{const q=i.value.trim().toLowerCase();for(const x of c)x.style.display=!q||x.textContent.toLowerCase().includes(q)?'':'none';});})();\n",
        encoding="utf-8",
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" role="img" aria-label="具身智能学习包结构图">
<rect width="900" height="520" fill="#fff"/><rect x="40" y="38" width="820" height="444" rx="10" fill="#f8fafc" stroke="#d8dee8"/>
<text x="70" y="86" font-family="Arial, PingFang SC, sans-serif" font-size="30" font-weight="700" fill="#101828">管理层具身智能学习路径</text>
<text x="70" y="122" font-family="Arial, PingFang SC, sans-serif" font-size="16" fill="#596579">从战略问题进入，向公司、场景、证据和行动方案逐层下钻</text>
<g font-family="Arial, PingFang SC, sans-serif" font-size="17" font-weight="700">
<rect x="70" y="170" width="190" height="88" rx="8" fill="#eef6ff" stroke="#175c9e"/><text x="94" y="206" fill="#175c9e">管理层入口</text><text x="94" y="234" font-size="13" font-weight="400" fill="#596579">速读 / 决策地图 / 误区</text>
<rect x="355" y="170" width="190" height="88" rx="8" fill="#edfafa" stroke="#147d78"/><text x="381" y="206" fill="#147d78">行业基础课</text><text x="381" y="234" font-size="13" font-weight="400" fill="#596579">技术栈 / 形态 / 政策</text>
<rect x="640" y="170" width="190" height="88" rx="8" fill="#fff7e6" stroke="#b7791f"/><text x="662" y="206" fill="#8a5a12">公司与竞品</text><text x="662" y="234" font-size="13" font-weight="400" fill="#596579">深度公司库</text>
<rect x="210" y="318" width="210" height="88" rx="8" fill="#f0fdf4" stroke="#287a46"/><text x="236" y="354" fill="#287a46">场景与商业化</text><text x="236" y="382" font-size="13" font-weight="400" fill="#596579">案例 {stats.get('cases', 0)} 条</text>
<rect x="500" y="318" width="210" height="88" rx="8" fill="#fff1f0" stroke="#b42318"/><text x="528" y="354" fill="#b42318">战略决策工具</text><text x="528" y="382" font-size="13" font-weight="400" fill="#596579">成熟度 / 试点 / ROI</text></g>
<text x="70" y="455" font-family="Arial, PingFang SC, sans-serif" font-size="14" fill="#596579">当前包：{stats.get('md', 0)} 个 Markdown、{stats.get('csv', 0)} 个数据表、{stats.get('pages', 0)} 个网页</text></svg>"""
    (ASSET_DIR / "learning-map.svg").write_text(svg, encoding="utf-8")


def card(item: dict[str, object], current: Path) -> str:
    return f"""<a class="card" data-card href="{rel_href(current, item['out'])}">
  <span class="tag">{html_lib.escape(str(item['category']))}</span>
  <strong>{html_lib.escape(str(item['title']))}</strong>
  <small>{html_lib.escape(str(item['rel']))}</small>
</a>"""


def write_markdown_index(items: list[dict[str, object]], stats: dict[str, int]) -> None:
    categories: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        categories[str(item["category"])].append(item)
    lines = ["# 具身智能机器人行业研究交付包索引", "", "本索引汇总当前仓库内面向企业管理层的具身智能机器人战略学习包。内容以中国市场为主，海外标杆作为对照，覆盖管理层速读、行业基础、公司与竞品、场景商业化、战略决策工具和数据证据库。", "", "## 网页入口", "", "- [网页目录 index.html](index.html)", "- [HTML 站点目录](html/index.html)", "- [管理层学习指南](html/reports/management_learning_guide.html)", "- [中国公司深度库](html/reports/competition/china_company_deep_index.html)", "- [公司深度来源库](html/data/company_deep_sources.html)", "", "## 交付范围", ""]
    for label, key in [("Markdown 报告", "md"), ("数据表", "csv"), ("静态 HTML 页面", "pages"), ("中国公司样本", "domestic"), ("公开落地案例", "cases")]:
        lines.append(f"- {label}：{stats.get(key, 0)} 个")
    lines.extend(["", "## 建议阅读路径", "", "### 2 小时管理层速读", "", "- [管理层总览](html/reports/management_learning_guide.html)", "- [中国公司深度库](html/reports/competition/china_company_deep_index.html)", "- [成熟度模型](html/reports/decision_tools/01_maturity_model.html)", "", "### 半天专题学习", "", "- 阅读公司深度库中的核心 10 家企业入口。", "- 结合场景适配矩阵、采购与合作优先级形成内部讨论材料。", "", "### 1 周深读", "", "- 按下面完整目录依次阅读，并把潜在供应商填入成熟度模型、供应商尽调清单和 ROI 模型。", "", "## 完整目录", ""])
    for cat in ["管理层入口", "行业基础课", "公司与竞品", "场景与商业化", "战略决策工具", "数据与证据", "项目文档"]:
        if cat not in categories:
            continue
        lines.extend([f"### {cat}", ""])
        for item in categories[cat]:
            lines.append(f"- [{item['title']}]({rel_href(ROOT / 'index.md', item['out'])}) - 源文件：[`{item['rel']}`]({item['rel']})")
        lines.append("")
    (ROOT / "index.md").write_text("\n".join(lines), encoding="utf-8")


def portal_body(current: Path, items: list[dict[str, object]], stats: dict[str, int]) -> str:
    categories: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        categories[str(item["category"])].append(item)
    metrics = [("Markdown", stats["md"]), ("数据表", stats["csv"]), ("网页", stats["pages"]), ("中国公司", stats["domestic"]), ("落地案例", stats["cases"]), ("来源记录", stats["sources"])]
    metric_html = "".join(f'<div class="metric"><strong>{v}</strong><span>{html_lib.escape(k)}</span></div>' for k, v in metrics)
    sections = []
    for cat in ["管理层入口", "行业基础课", "公司与竞品", "场景与商业化", "战略决策工具", "数据与证据", "项目文档"]:
        if cat in categories:
            sections.append(f'<section class="band"><h2>{cat}</h2><div class="card-grid">{"".join(card(item, current) for item in categories[cat])}</div></section>')
    return f"""<main class="page-shell">
  <section class="hero">
    <div>
      <h1>具身智能机器人行业研究交付包</h1>
      <p>面向企业管理层的战略学习网页目录。新增中国公司深度库，覆盖核心企业长篇分析、其他企业结构化分析、来源表和横向矩阵。</p>
      <div class="hero-actions"><a class="button primary" href="{rel_href(current, HTML_ROOT / 'reports/competition/china_company_deep_index.html')}">进入中国公司深度库</a><a class="button" href="{rel_href(current, ROOT / 'index.md')}">查看 Markdown 索引</a></div>
    </div>
    <figure class="hero-visual"><img src="{rel_href(current, ASSET_DIR / 'learning-map.svg')}" alt="管理层具身智能学习路径图"></figure>
  </section>
  <section class="metric-row" aria-label="交付统计">{metric_html}</section>
  <div class="toolbar"><h2>全站目录</h2><input class="search" data-search type="search" placeholder="搜索报告、数据表或路径"></div>
  {''.join(sections)}
  <footer class="footer">网页由仓库内 Markdown 与 CSV 自动转换生成。核心判断请结合来源索引和证据等级复核。</footer>
</main>"""


def sidebar(current: Path, items: list[dict[str, object]]) -> str:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in items:
        groups[str(item["category"])].append(item)
    parts = []
    for cat in ["管理层入口", "公司与竞品", "数据与证据", "战略决策工具", "场景与商业化", "行业基础课", "项目文档"]:
        if cat not in groups:
            continue
        parts.append(f"<h2>{cat}</h2>")
        for item in groups[cat][:80]:
            parts.append(f'<a href="{rel_href(current, item["out"])}">{html_lib.escape(str(item["title"]))}</a>')
    return "\n".join(parts)


def rewrite_links(rendered: str, source: Path, current: Path, mapping: dict[Path, Path]) -> str:
    def repl(match: re.Match[str]) -> str:
        href = match.group(2)
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return match.group(0)
        raw, _, frag = href.partition("#")
        if not raw:
            return match.group(0)
        target = (source.parent / raw).resolve()
        if target not in mapping:
            target = (ROOT / raw).resolve()
        if target not in mapping:
            return match.group(0)
        new = rel_href(current, mapping[target]) + (f"#{frag}" if frag else "")
        return f'{match.group(1)}{new}{match.group(3)}'
    return re.sub(r'(href=")([^"]+)(")', repl, rendered)


def render_md(item: dict[str, object], items: list[dict[str, object]], mapping: dict[Path, Path]) -> None:
    source = Path(item["source"])
    out = Path(item["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    rendered = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["extra", "toc", "sane_lists", "fenced_code", "tables"])
    rendered = rewrite_links(rendered, source, out, mapping)
    body = f"""<main class="page-shell docs-layout">
  <aside class="sidebar" aria-label="文档目录">{sidebar(out, items)}</aside>
  <article class="content"><div class="meta"><span>源文件：{html_lib.escape(str(item['rel']))}</span><span>生成日期：{GENERATED_DATE}</span></div>{rendered}</article>
</main>"""
    out.write_text(page_shell(out, str(item["title"]), body, "doc-page"), encoding="utf-8")


def render_csv(item: dict[str, object], items: list[dict[str, object]]) -> None:
    source = Path(item["source"])
    out = Path(item["out"])
    out.parent.mkdir(parents=True, exist_ok=True)
    with source.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    headers = rows[0] if rows else []
    body_rows = rows[1:]
    thead = "<tr>" + "".join(f"<th>{html_lib.escape(h)}</th>" for h in headers) + "</tr>"
    tbody = "".join("<tr>" + "".join(f"<td>{html_lib.escape(cell)}</td>" for cell in row) + "</tr>" for row in body_rows)
    body = f"""<main class="page-shell docs-layout">
  <aside class="sidebar" aria-label="文档目录">{sidebar(out, items)}</aside>
  <article class="content"><div class="meta"><span>源文件：{html_lib.escape(str(item['rel']))}</span><span>记录数：{len(body_rows)}</span><span>生成日期：{GENERATED_DATE}</span></div><h1>{html_lib.escape(str(item['title']))}</h1><p>本页由仓库数据表转换生成，用于网页浏览和管理层快速筛选。</p><div class="table-wrap"><table><thead>{thead}</thead><tbody>{tbody}</tbody></table></div></article>
</main>"""
    out.write_text(page_shell(out, str(item["title"]), body, "doc-page"), encoding="utf-8")


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open(encoding="utf-8", newline="") as f:
        return max(sum(1 for _ in csv.reader(f)) - 1, 0)


def main() -> None:
    items, mapping = collect_items()
    stats = {
        "md": sum(1 for item in items if item["kind"] == "md"),
        "csv": sum(1 for item in items if item["kind"] == "csv"),
        "pages": len(items),
        "domestic": count_csv_rows(ROOT / "data/domestic_companies.csv"),
        "cases": count_csv_rows(ROOT / "data/deployment_cases.csv"),
        "sources": count_csv_rows(ROOT / "data/company_deep_sources.csv"),
    }
    write_assets(stats)
    write_markdown_index(items, stats)
    for item in items:
        if item["kind"] == "md":
            render_md(item, items, mapping)
        else:
            render_csv(item, items)
    root_index = ROOT / "index.html"
    root_index.write_text(page_shell(root_index, "网页目录", portal_body(root_index, items, stats), "portal-page"), encoding="utf-8")
    html_index = HTML_ROOT / "index.html"
    html_index.write_text(page_shell(html_index, "HTML 站点目录", portal_body(html_index, items, stats), "portal-page"), encoding="utf-8")
    print(f"html_pages={len(items) + 2}")
    print(f"markdown={stats['md']}")
    print(f"csv={stats['csv']}")


if __name__ == "__main__":
    main()
