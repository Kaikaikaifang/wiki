"""
Wiki Lint 自动化脚本。

扫描 wiki 目录，检查 frontmatter 完整性、标签合法性、死链、孤立页面和隐私泄露。

用法:
    python scripts/wiki_lint.py [wiki_dir]

默认扫描当前目录下的 wiki/ 文件夹。
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


def validate_frontmatter(file_path: str, content: str) -> List[str]:
    """检查 frontmatter 完整性。"""
    errors = []
    rel_path = os.path.relpath(file_path)

    if rel_path.endswith("wiki/log.md"):
        return errors

    if not content.startswith("---"):
        errors.append(f"[{rel_path}] 缺少 frontmatter")
        return errors

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        errors.append(f"[{rel_path}] frontmatter 格式错误")
        return errors

    fm = match.group(1)

    required_fields = ["title", "type", "tags", "updated"]
    for field in required_fields:
        if f"{field}:" not in fm:
            errors.append(f"[{rel_path}] 缺少必填字段 `{field}`")

    updated_match = re.search(r'updated:\s*(\d{4}-\d{2}-\d{2})', fm)
    if updated_match:
        date_str = updated_match.group(1)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append(f"[{rel_path}] `updated` 日期格式错误: {date_str}")
    elif "updated:" in fm:
        errors.append(f"[{rel_path}] `updated` 日期格式应为 YYYY-MM-DD")

    return errors


def validate_tags(file_path: str, content: str) -> List[str]:
    """检查标签合法性（无空格）。"""
    errors = []
    rel_path = os.path.relpath(file_path)

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return errors

    fm = match.group(1)
    tags_match = re.search(r'tags:\s*(\[.*?\])', fm)
    if not tags_match:
        return errors

    tags_str = tags_match.group(1)
    tags = re.findall(r'["\']?([^"\',\[\]]+)["\']?', tags_str)

    if not tags or all(not t.strip() for t in tags):
        errors.append(f"[{rel_path}] `tags` 为空")
        return errors

    for tag in tags:
        tag = tag.strip()
        if not tag:
            continue
        if ' ' in tag:
            errors.append(f"[{rel_path}] 标签包含空格: `{tag}`")

    return errors


def find_dead_wikilinks(wiki_dir: str, file_path: str, content: str) -> List[str]:
    """查找死链（wikilink 指向不存在的页面）。"""
    dead = []
    rel_path = os.path.relpath(file_path, wiki_dir)

    links = re.findall(r'\[\[([^\]]+)(?:#[^\]]+)?\]\]', content)

    for link in links:
        page_name = link.split('#')[0].strip()
        if not page_name:
            continue

        found = False
        possible_paths = [
            os.path.join(wiki_dir, f"{page_name}.md"),
            os.path.join(wiki_dir, "topics", f"{page_name}.md"),
            os.path.join(wiki_dir, "entities", f"{page_name}.md"),
            os.path.join(wiki_dir, "sources", f"{page_name}.md"),
        ]

        for pp in possible_paths:
            if os.path.exists(pp):
                found = True
                break

        if not found:
            dead.append(page_name)

    return dead


def find_orphaned_pages(wiki_dir: str) -> List[str]:
    """查找孤立页面（无入链的页面）。"""
    orphans = []
    wiki_path = Path(wiki_dir)

    all_pages = set()
    page_names = {}
    incoming_links = {}

    for md_file in wiki_path.rglob("*.md"):
        rel = md_file.relative_to(wiki_path)
        rel_str = str(rel)
        all_pages.add(rel_str)
        page_names[md_file.stem] = rel_str
        page_names[str(rel.with_suffix(""))] = rel_str
        incoming_links[rel_str] = set()

    for md_file in wiki_path.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        links = re.findall(r'\[\[([^\]]+)(?:#[^\]]+)?\]\]', content)
        source_rel = str(md_file.relative_to(wiki_path))

        for link in links:
            page_name = link.split('#')[0].strip()
            if page_name in page_names:
                incoming_links[page_names[page_name]].add(source_rel)

    excluded = {"index.md", "overview.md", "log.md"}
    for page in all_pages:
        if page in excluded:
            continue
        if not incoming_links.get(page):
            orphans.append(page)

    return orphans


def scan_privacy_leaks(file_path: str, content: str) -> List[str]:
    """扫描隐私信息泄露。"""
    leaks = []
    rel_path = os.path.relpath(file_path)

    path_patterns = [
        r'/Users/[^/\s]+/',
        r'/home/[^/\s]+/',
        r'C:\\Users\\[^/\s]+\\',
    ]
    for pattern in path_patterns:
        if re.search(pattern, content):
            leaks.append(f"[{rel_path}] 发现本地绝对路径泄露")
            break

    key_patterns = [
        r'sk-[a-zA-Z0-9]{20,}',
        r'AKIA[0-9A-Z]{16}',
        r'ghp_[a-zA-Z0-9]{36}',
        r'[a-zA-Z0-9_-]*api[_-]?key[a-zA-Z0-9_-]*[:=]\s*["\']?[a-zA-Z0-9_-]+',
    ]
    for pattern in key_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            leaks.append(f"[{rel_path}] 发现疑似 API Key / Token")
            break

    return leaks


class WikiLinter:
    def __init__(self, wiki_dir: str):
        self.wiki_dir = Path(wiki_dir)
        self.errors = []
        self.warnings = []

    def run_full_scan(self) -> Dict:
        """执行全库扫描。"""
        self.errors = []
        self.warnings = []
        total_pages = 0

        for md_file in self.wiki_dir.rglob("*.md"):
            rel = md_file.relative_to(self.wiki_dir)
            rel_str = str(rel)
            total_pages += 1

            content = md_file.read_text(encoding="utf-8")

            for err in validate_frontmatter(str(md_file), content):
                self.errors.append({"file": rel_str, "message": err, "severity": "error"})

            for err in validate_tags(str(md_file), content):
                self.errors.append({"file": rel_str, "message": err, "severity": "error"})

            dead = find_dead_wikilinks(str(self.wiki_dir), str(md_file), content)
            for d in dead:
                self.errors.append({
                    "file": rel_str,
                    "message": f"[{rel_str}] 死链: [[{d}]]",
                    "severity": "error"
                })

            for leak in scan_privacy_leaks(str(md_file), content):
                self.errors.append({"file": rel_str, "message": leak, "severity": "warning"})

        orphans = find_orphaned_pages(str(self.wiki_dir))
        orphans = find_orphaned_pages(str(self.wiki_dir))
        for o in orphans:
            self.warnings.append({"file": o, "message": f"[{o}] 孤立页面（无入链）", "severity": "warning"})

        return {
            "total_pages": total_pages,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "details": self.errors + self.warnings,
        }

    def generate_markdown_report(self, report: Dict) -> str:
        """生成 Markdown 格式报告。"""
        lines = [
            "# Wiki Lint 报告",
            "",
            f"- 扫描页面数: {report['total_pages']}",
            f"- 错误数: {report['errors']}",
            f"- 警告数: {report['warnings']}",
            "",
        ]

        if report["errors"] > 0:
            lines.append("## 错误")
            for item in report["details"]:
                if item["severity"] == "error":
                    lines.append(f"- {item['message']}")
            lines.append("")

        if report["warnings"] > 0:
            lines.append("## 警告")
            for item in report["details"]:
                if item["severity"] == "warning":
                    lines.append(f"- {item['message']}")
            lines.append("")

        if report["errors"] == 0 and report["warnings"] == 0:
            lines.append("全部通过！")
            lines.append("")

        return "\n".join(lines)


def main():
    wiki_dir = sys.argv[1] if len(sys.argv) > 1 else "wiki"
    wiki_path = Path(wiki_dir)

    if not wiki_path.exists():
        print(f"错误: 目录不存在 {wiki_dir}")
        sys.exit(1)

    linter = WikiLinter(str(wiki_path))
    report = linter.run_full_scan()
    md_report = linter.generate_markdown_report(report)

    print(md_report)

    if report["errors"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
