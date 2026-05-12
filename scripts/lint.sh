#!/usr/bin/env bash
# wiki lint 脚本

set -e

echo "=== Frontmatter 完整性检查 ==="
find wiki -name "*.md" -not -path "wiki/log.md" | while read f; do
  if ! head -5 "$f" | grep -q "^---"; then
    echo "  MISSING frontmatter: $f"
  fi
done

echo ""
echo "=== 标签空格检查 ==="
grep -r "tags:" wiki --include="*.md" | grep -E "tags:.*[\"'].* .*[\"']" || true

echo ""
echo "=== 死链检查（基本版） ==="
# 收集所有 wikilink 目标
find wiki -name "*.md" -exec grep -oP '\[\[\K[^\]]+' {} + | sed 's/#.*//' | sort -u > /tmp/all_targets.txt
# 收集所有存在的页面
find wiki -name "*.md" | sed 's|wiki/||; s|\.md$||' | sort -u > /tmp/all_pages.txt
# 检查缺失
comm -23 /tmp/all_targets.txt /tmp/all_pages.txt | while read t; do
  echo "  BROKEN link target: $t"
done

echo ""
echo "=== 孤立页面检查 ==="
comm -13 /tmp/all_targets.txt /tmp/all_pages.txt | while read p; do
  echo "  ORPHAN page: $p"
done

echo ""
echo "=== 隐私信息扫描 ==="
grep -rE "/Users/|/home/|C:\\Users\\" wiki --include="*.md" || true

echo ""
echo "Lint 完成"
