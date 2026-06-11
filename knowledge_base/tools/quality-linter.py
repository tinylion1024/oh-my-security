#!/usr/bin/env python3
"""
质量检查工具
检查案例和武器的格式规范

用法:
    python quality-linter.py [--fix]
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# 配置
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent
CASES_PATH = KNOWLEDGE_BASE_PATH / "cases" / "indie"
WEAPONS_PATH = KNOWLEDGE_BASE_PATH / "weapons" / "indie"

# 元数据检查
REQUIRED_METADATA = [
    "tier适用",
    "领域",
    "严重程度",
]

# 格式检查
FORMAT_CHECKS = [
    ("标题层级", r"^#{1,3}\s+", "标题应使用 1-3 级"),
    ("列表格式", r"^\s*[-*]\s+", "列表应使用 - 或 *"),
    ("代码块语言", r"```\w+", "代码块应指定语言"),
]


def check_metadata(content: str) -> Dict:
    """检查元数据完整性"""
    result = {
        "has_metadata_section": False,
        "missing_fields": [],
        "values": {}
    }

    # 检查元数据章节
    metadata_match = re.search(r"##\s*元数据\n(.*?)(?=\n##|\n---|\Z)", content, re.DOTALL)
    if metadata_match:
        result["has_metadata_section"] = True
        metadata_content = metadata_match.group(1)

        for field in REQUIRED_METADATA:
            pattern = rf"\*\*{field}[：:]\*\*\s*(.+?)(?=\n|\*|$)"
            match = re.search(pattern, metadata_content)
            if match:
                result["values"][field] = match.group(1).strip()
            else:
                result["missing_fields"].append(field)
    else:
        result["missing_fields"] = REQUIRED_METADATA

    return result


def check_formatting(content: str) -> List[Dict]:
    """检查格式问题"""
    issues = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        # 检查过长行
        if len(line) > 120 and not line.startswith('```'):
            issues.append({
                "line": i,
                "type": "长行",
                "message": f"行长度 {len(line)} > 120 字符"
            })

        # 检查 trailing whitespace
        if line.rstrip() != line:
            issues.append({
                "line": i,
                "type": "尾随空格",
                "message": "行末有多余空格"
            })

    return issues


def check_file(file_path: Path) -> Dict:
    """检查单个文件"""
    result = {
        "file": str(file_path.relative_to(KNOWLEDGE_BASE_PATH)),
        "passed": True,
        "metadata": {},
        "format_issues": [],
        "errors": []
    }

    try:
        content = file_path.read_text(encoding='utf-8')
    except Exception as e:
        result["errors"].append(f"读取失败: {e}")
        result["passed"] = False
        return result

    # 检查元数据
    result["metadata"] = check_metadata(content)
    if result["metadata"]["missing_fields"]:
        result["passed"] = False

    # 检查格式
    result["format_issues"] = check_formatting(content)
    if result["format_issues"]:
        result["passed"] = False

    return result


def check_directory(directory: Path) -> List[Dict]:
    """检查目录下所有文件"""
    results = []
    if not directory.exists():
        return results

    for md_file in directory.rglob("*.md"):
        results.append(check_file(md_file))

    return results


def generate_report(case_results: List[Dict], weapon_results: List[Dict]) -> str:
    """生成检查报告"""
    report = []
    report.append("# 质量检查报告")
    report.append("")
    report.append(f"**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 案例检查
    report.append("## 案例质量")
    report.append("")
    case_total = len(case_results)
    case_passed = sum(1 for r in case_results if r["passed"])

    report.append(f"- 总数: {case_total}")
    if case_total > 0:
        report.append(f"- 通过: {case_passed}/{case_total} ({case_passed/case_total*100:.1f}%)")
    report.append("")

    # 武器检查
    report.append("## 武器质量")
    report.append("")
    weapon_total = len(weapon_results)
    weapon_passed = sum(1 for r in weapon_results if r["passed"])

    report.append(f"- 总数: {weapon_total}")
    if weapon_total > 0:
        report.append(f"- 通过: {weapon_passed}/{weapon_total} ({weapon_passed/weapon_total*100:.1f}%)")
    report.append("")

    # 需要修复的文件
    all_failed = [r for r in case_results + weapon_results if not r["passed"]]
    if all_failed:
        report.append("## 需要修复的文件")
        report.append("")
        for r in all_failed[:20]:
            issues = []
            if r["metadata"].get("missing_fields"):
                issues.append(f"元数据缺失: {', '.join(r['metadata']['missing_fields'])}")
            if r["format_issues"]:
                issues.append(f"格式问题: {len(r['format_issues'])} 个")
            report.append(f"- {r['file']}: {'; '.join(issues)}")
    else:
        report.append("✅ 所有文件检查通过！")

    return "\n".join(report)


def main():
    """主函数"""
    print("检查案例...")
    case_results = check_directory(CASES_PATH)

    print("检查武器...")
    weapon_results = check_directory(WEAPONS_PATH)

    print("\n生成报告...\n")
    report = generate_report(case_results, weapon_results)
    print(report)

    # 保存报告
    report_path = KNOWLEDGE_BASE_PATH / "tools" / "quality-report.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n报告已保存到: {report_path}")

    # 返回退出码
    all_passed = all(r["passed"] for r in case_results + weapon_results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
