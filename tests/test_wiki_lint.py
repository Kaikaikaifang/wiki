"""
Wiki Lint 自动化脚本的单元测试。

运行方式: python -m pytest tests/test_wiki_lint.py -v
"""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from wiki_lint import (
    validate_frontmatter,
    validate_tags,
    find_dead_wikilinks,
    find_orphaned_pages,
    scan_privacy_leaks,
    WikiLinter,
)


class TestValidateFrontmatter:
    """测试 frontmatter 完整性检查。"""

    def test_valid_frontmatter(self):
        content = "---\ntitle: 测试\ntype: topic\ntags: [test]\nsource_count: 1\nupdated: 2026-05-09\n---\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert errors == []

    def test_missing_title(self):
        content = "---\ntype: topic\ntags: [test]\nsource_count: 1\nupdated: 2026-05-09\n---\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert any("title" in e for e in errors)

    def test_missing_type(self):
        content = "---\ntitle: 测试\ntags: [test]\nsource_count: 1\nupdated: 2026-05-09\n---\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert any("type" in e for e in errors)

    def test_missing_tags(self):
        content = "---\ntitle: 测试\ntype: topic\nsource_count: 1\nupdated: 2026-05-09\n---\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert any("tags" in e for e in errors)

    def test_missing_updated(self):
        content = "---\ntitle: 测试\ntype: topic\ntags: [test]\nsource_count: 1\n---\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert any("updated" in e for e in errors)

    def test_no_frontmatter(self):
        content = "# 标题\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert any("缺少 frontmatter" in e for e in errors)

    def test_log_no_frontmatter_allowed(self):
        content = "# 操作日志\n\n正文"
        errors = validate_frontmatter("wiki/log.md", content)
        assert errors == []

    def test_invalid_date_format(self):
        content = "---\ntitle: 测试\ntype: topic\ntags: [test]\nsource_count: 1\nupdated: 2026/05/09\n---\n\n正文"
        errors = validate_frontmatter("topics/test.md", content)
        assert any("updated" in e and "格式" in e for e in errors)


class TestValidateTags:
    """测试标签合法性检查。"""

    def test_valid_tags(self):
        content = "---\ntitle: 测试\ntype: topic\ntags: [Agent, 提示词工程]\nsource_count: 1\nupdated: 2026-05-09\n---"
        errors = validate_tags("topics/test.md", content)
        assert errors == []

    def test_tag_with_space(self):
        content = "---\ntitle: 测试\ntype: topic\ntags: [AI Agent, 提示词]\nsource_count: 1\nupdated: 2026-05-09\n---"
        errors = validate_tags("topics/test.md", content)
        assert any("空格" in e for e in errors)

    def test_empty_tags(self):
        content = "---\ntitle: 测试\ntype: topic\ntags: []\nsource_count: 1\nupdated: 2026-05-09\n---"
        errors = validate_tags("topics/test.md", content)
        assert any("空" in e for e in errors)


class TestFindDeadWikilinks:
    """测试死链检测。"""

    def test_no_dead_links(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "existing.md").write_text("# 存在\n")

        content = "[[existing]] 是一个页面"
        dead = find_dead_wikilinks(str(wiki_dir), "topics/test.md", content)
        assert dead == []

    def test_dead_link(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()

        content = "[[nonexistent]] 是一个页面"
        dead = find_dead_wikilinks(str(wiki_dir), "topics/test.md", content)
        assert "nonexistent" in dead

    def test_link_with_heading(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "existing.md").write_text("# 存在\n\n## 章节\n")

        content = "[[existing#章节]]"
        dead = find_dead_wikilinks(str(wiki_dir), "topics/test.md", content)
        assert dead == []

    def test_external_link_ignored(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()

        content = "[外部链接](https://example.com)"
        dead = find_dead_wikilinks(str(wiki_dir), "topics/test.md", content)
        assert dead == []


class TestFindOrphanedPages:
    """测试孤立页面检测。"""

    def test_no_orphans(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "topics" / "a.md").write_text("# A\n\n[[b]]")
        (wiki_dir / "topics" / "b.md").write_text("# B\n\n[[a]]")

        orphans = find_orphaned_pages(str(wiki_dir))
        assert orphans == []

    def test_orphan_found(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "topics" / "a.md").write_text("# A\n")
        (wiki_dir / "topics" / "b.md").write_text("# B\n\n[[a]]")

        orphans = find_orphaned_pages(str(wiki_dir))
        assert "topics/b.md" in orphans

    def test_no_orphan_with_path_prefix(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "sources").mkdir()
        (wiki_dir / "sources" / "ref.md").write_text("# Ref\n")
        (wiki_dir / "topics" / "a.md").write_text("# A\n\n[[sources/ref]]")

        orphans = find_orphaned_pages(str(wiki_dir))
        assert "sources/ref.md" not in orphans


class TestScanPrivacyLeaks:
    """测试隐私信息扫描。"""

    def test_no_leaks(self):
        content = "使用相对路径 `test-weixin/bridge`"
        leaks = scan_privacy_leaks("topics/test.md", content)
        assert leaks == []

    def test_macos_path_leak(self):
        content = "在 /Users/kaikai/projects/ 下运行"
        leaks = scan_privacy_leaks("topics/test.md", content)
        assert any("绝对路径" in e for e in leaks)

    def test_linux_path_leak(self):
        content = "在 /home/user/projects/ 下运行"
        leaks = scan_privacy_leaks("topics/test.md", content)
        assert any("绝对路径" in e for e in leaks)

    def test_api_key_leak(self):
        content = "sk-abc123def456ghi789jkl"
        leaks = scan_privacy_leaks("topics/test.md", content)
        assert any("API Key" in e for e in leaks)

    def test_aws_key_leak(self):
        content = "AKIAIOSFODNN7EXAMPLE"
        leaks = scan_privacy_leaks("topics/test.md", content)
        assert any("API Key" in e for e in leaks)


class TestWikiLinterIntegration:
    """测试 WikiLinter 集成扫描。"""

    def test_full_scan(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "entities").mkdir()
        (wiki_dir / "sources").mkdir()

        # 有效页面
        (wiki_dir / "topics" / "valid.md").write_text(
            "---\ntitle: 有效页面\ntype: topic\ntags: [测试]\nsource_count: 0\nupdated: 2026-05-09\n---\n\n正文\n\n[[overview]]"
        )
        (wiki_dir / "overview.md").write_text(
            "---\ntitle: 综述\ntype: overview\ntags: [索引]\nsource_count: 0\nupdated: 2026-05-09\n---\n\n综述内容"
        )
        # 无效页面：标签有空格
        (wiki_dir / "topics" / "invalid.md").write_text(
            "---\ntitle: 无效页面\ntype: topic\ntags: [AI Agent]\nsource_count: 0\nupdated: 2026-05-09\n---\n\n正文"
        )
        # 孤立页面
        (wiki_dir / "entities" / "orphan.md").write_text(
            "---\ntitle: 孤立页面\ntype: entity\ntags: [测试]\nsource_count: 0\nupdated: 2026-05-09\n---\n\n正文"
        )

        linter = WikiLinter(str(wiki_dir))
        report = linter.run_full_scan()

        assert report["total_pages"] == 4
        assert report["errors"] > 0
        assert any("空格" in e["message"] for e in report["details"])

    def test_report_markdown_output(self, tmp_path):
        wiki_dir = tmp_path / "wiki"
        wiki_dir.mkdir()
        (wiki_dir / "topics").mkdir()
        (wiki_dir / "topics" / "test.md").write_text(
            "---\ntitle: 测试\ntype: topic\ntags: [测试]\nsource_count: 0\nupdated: 2026-05-09\n---\n\n正文"
        )

        linter = WikiLinter(str(wiki_dir))
        report = linter.run_full_scan()
        md = linter.generate_markdown_report(report)

        assert "# Wiki Lint 报告" in md
        assert "扫描页面数" in md


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
