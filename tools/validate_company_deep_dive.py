#!/usr/bin/env python3
"""Validate coverage, source depth, word/character count, and local links."""

from __future__ import annotations

import csv
import re
import sys
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEEP = ROOT / "reports/company_profiles/china_deep_dive"
SOURCE_LEDGER = ROOT / "data/company_deep_sources.csv"
CORE = {
    "智元机器人": "agibot",
    "宇树科技": "unitree",
    "优必选": "ubtech",
    "银河通用": "galbot",
    "逐际动力": "limx_dynamics",
    "傅利叶智能": "fourier",
    "乐聚机器人": "leju_robotics",
    "众擎机器人/EngineAI": "engineai",
    "普渡机器人": "pudu_robotics",
    "云深处科技": "deep_robotics",
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


def compact_chars(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def read_companies() -> list[dict[str, str]]:
    with (ROOT / "data/domestic_companies.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def slug_for(name: str) -> str:
    from build_china_company_deep_dive import company_slug

    return company_slug(name)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def validate_coverage_and_counts() -> None:
    companies = read_companies()
    if len(companies) != 51:
        fail(f"expected 51 domestic companies, got {len(companies)}")
    for row in companies:
        name = row["company_name"]
        if name in CORE:
            folder = DEEP / "core" / CORE[name]
            if not (folder / "index.md").exists():
                fail(f"missing core index for {name}")
            files = sorted(folder.glob("*.md"))
            text = "\n".join(p.read_text(encoding="utf-8") for p in files)
            chars = compact_chars(text)
            if chars < 100000:
                fail(f"{name} core chars below 100000: {chars}")
        else:
            path = DEEP / "others" / f"{slug_for(name)}.md"
            if not path.exists():
                fail(f"missing non-core file for {name}: {path}")
            text = path.read_text(encoding="utf-8")
            chars = compact_chars(text)
            if chars < 5000:
                fail(f"{name} non-core chars below 5000: {chars}")
            for heading in REQUIRED_HEADINGS:
                if f"## {heading}" not in text:
                    fail(f"{name} missing heading {heading}")
    print("coverage_and_counts=ok")


def validate_sources() -> None:
    if not SOURCE_LEDGER.exists():
        fail("missing company_deep_sources.csv")
    with SOURCE_LEDGER.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    by_company: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_company.setdefault(row["company_name"], []).append(row)
    for company in read_companies():
        name = company["company_name"]
        rows_for_company = by_company.get(name, [])
        minimum = 30 if name in CORE else 8
        if len(rows_for_company) < minimum:
            fail(f"{name} has {len(rows_for_company)} sources, expected {minimum}")
        ab_count = sum(1 for row in rows_for_company if row["source_level"] in {"A", "B"})
        if name in CORE and ab_count < 5:
            fail(f"{name} has {ab_count} A/B sources, expected at least 5")
        for row in rows_for_company:
            if not row["source_url"].startswith(("http://", "https://")):
                fail(f"{name} invalid source url: {row['source_url']}")
    print("sources=ok")


def markdown_links(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def validate_markdown_links() -> None:
    missing: list[tuple[str, str]] = []
    files = [
        ROOT / "README.md",
        ROOT / "index.md",
        ROOT / "reports/management_learning_guide.md",
        ROOT / "reports/competition/china_company_deep_index.md",
    ] + sorted(DEEP.rglob("*.md"))
    for path in files:
        for link in markdown_links(path):
            target = link.split("#", 1)[0].strip()
            if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue
            target = urllib.parse.unquote(target)
            if not (path.parent / target).resolve().exists():
                missing.append((str(path.relative_to(ROOT)), link))
    if missing:
        for item in missing[:30]:
            print("missing", item)
        fail(f"markdown missing links: {len(missing)}")
    print("markdown_links=ok")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


def validate_html_links() -> None:
    html_root = ROOT / "html"
    if not html_root.exists():
        fail("html directory missing")
    missing: list[tuple[str, str]] = []
    files = [ROOT / "index.html"] + sorted(html_root.rglob("*.html"))
    for path in files:
        parser = LinkParser()
        parser.feed(path.read_text(encoding="utf-8"))
        for link in parser.links:
            target = link.split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            if not (path.parent / target).resolve().exists():
                missing.append((str(path.relative_to(ROOT)), link))
    if missing:
        for item in missing[:30]:
            print("missing", item)
        fail(f"html missing links: {len(missing)}")
    print("html_links=ok")


def main() -> None:
    validate_coverage_and_counts()
    validate_sources()
    validate_markdown_links()
    validate_html_links()
    print("company_deep_dive_validation=ok")


if __name__ == "__main__":
    main()
