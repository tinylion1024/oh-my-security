#!/usr/bin/env python3
"""
武器可用性验证器
检查武器文档中的链接和代码示例

用法:
    python weapon-validator.py
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.request
import urllib.error

# 配置
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent
WEAPONS_PATH = KNOWLEDGE_BASE_PATH / "weapons" / "indie"

# 检查项
REQUIRED_SECTIONS = [
    ("适用场景", r"##\s*适用场景|###\s*适用场景"),
    ("快速上手", r"##\s*快速上手|###\s*快速上手|5分钟"),
    ("成本估算", r"##\s*成本估算|###\s*成本估算"),
    ("迁出成本", r"迁出成本"),
]


def extract_links(content: str) -> List[str]:
    """提取 Markdown 中的链接"""
    pattern = r'https?://[^\s\)\>]+'
    return re.findall(pattern, content)


def check_link(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """检查链接是否有效"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=timeout)
        return True, f"HTTP {response.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"
    except urllib.error.URLError as e:
        return False, str(e.reason)
    except Exception as e:
        return False, str(e)


def check_weapon_file(file_path: Path, check_links: bool = False) -> Dict:
    """检查单个武器文件"""
    result = {
        "file": str(file_path.relative_to(KNOWLEDGE_BASE_PATH)),
        "exists": True,
        "passed": False,
        "missing_sections": [],
        "code_examples": 0,
        "links_total": 0,
        "links_valid": 0,
        "broken_links": [],
        "errors": []
    }

    if not file_path.exists():
        result["exists"] = False
        return result

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["errors"].append(f"读取失败: {e}")
        return result

    # 检查必需章节
    for name, pattern in REQUIRED_SECTIONS:
        if not re.search(pattern, content, re.IGNORECASE):
            result["missing_sections"].append(name)

    # 检查代码示例
    code_blocks = re.findall(r'```', content)
    result["code_examples"] = len(code_blocks) // 2

    # 检查链接
    if check_links:
        links = extract_links(content)
        result["links_total"] = len(links)

        for link in links[:10]:  # 最多检查 10 个链接
            valid, msg = check_link(link)
            if valid:
                result["links_valid"] += 1
            else:
                result["broken_links"].append({"url": link, "error": msg})

    # 判断是否通过
    result["passed"] = (
        len(result["missing_sections"]) == 0 and
        result["code_examples"] >= 1
    )

    return result


def check_directory(directory: Path, check_links: bool = False) -> List[Dict]:
    """检查目录下所有武器"""
    results = []
    if not directory.exists():
        return results

    for md_file in directory.rglob("*.md"):
        results.append(check_weapon_file(md_file, check_links))

    return results


def generate_report(results: List[Dict]) -> str:
    """生成检查报告"""
    report = []
    report.append("# 武器可用性验证报告")
    report.append("")
    report.append(f"**检查时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 统计
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    total_code = sum(r["code_examples"] for r in results)
    total_links = sum(r["links_total"] for r in results)
    valid_links = sum(r["links_valid"] for r in results)
    broken_links = [link for r in results for link in r["broken_links"]]

    report.append("## 统计摘要")
    report.append("")
    report.append(f"- 武器总数: {total}")
    report.append(f"- 检查通过: {passed}/{total} ({passed/total*100:.1f}%)" if total > 0 else "- 检查通过: 0/0")
    report.append(f"- 代码示例总数: {total_code}")
    report.append(f"- 链接总数: {total_links}")
    if total_links > 0:
        report.append(f"- 有效链接: {valid_links}/{total_links} ({valid_links/total_links*100:.1f}%)")
    report.append("")

    # 未通过的武器
    failed = [r for r in results if not r["passed"]]
    if failed:
        report.append("## 需要修复的武器")
        report.append("")
        for r in failed[:20]:
            issues = []
            if r["missing_sections"]:
                issues.append(f"缺失章节: {', '.join(r['missing_sections'])}")
            if r["code_examples"] == 0:
                issues.append("缺少代码示例")
            report.append(f"- {r['file']}: {'; '.join(issues)}")
        report.append("")

    # 失效链接
    if broken_links:
        report.append("## 失效链接")
        report.append("")
        for link in broken_links[:10]:
            report.append(f"- [{link['error']}] {link['url']}")
        report.append("")

    if passed == total and not broken_links:
        report.append("✅ 所有武器检查通过！")

    return "\n".join(report)


def main():
    """主函数"""
    print("检查武器文档...")
    results = check_directory(WEAPONS_PATH, check_links=False)

    print("\n生成报告...\n")
    report = generate_report(results)
    print(report)

    # 保存报告
    report_path = KNOWLEDGE_BASE_PATH / "tools" / "weapon-report.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n报告已保存到: {report_path}")

    # 返回退出码
    all_passed = all(r["passed"] for r in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
