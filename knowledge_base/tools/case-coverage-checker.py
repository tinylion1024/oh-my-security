#!/usr/bin/env python3
"""
案例覆盖度检查器
检查 indie 核心案例是否符合质量标准

用法:
    python case-coverage-checker.py
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# 配置
KNOWLEDGE_BASE_PATH = Path(__file__).parent.parent
CORE_CASES_PATH = KNOWLEDGE_BASE_PATH / "cases" / "indie" / "core"
EXTENDED_CASES_PATH = KNOWLEDGE_BASE_PATH / "cases" / "indie" / "extended"

# 质量检查项
L1_CHECKS = [
    ("一分钟识别", r"##\s*一分钟识别|###\s*一分钟识别"),
    ("一句话防御", r"##\s*一句话防御|###\s*一句话防御|一句话防御"),
    ("推荐工具", r"##\s*推荐工具|###\s*推荐工具|推荐工具"),
]

L2_CHECKS = [
    ("攻击路径", r"##\s*攻击路径|###\s*攻击路径"),
    ("防御方案", r"##\s*防御方案|###\s*防御方案"),
    ("代码示例", r"```python|```javascript|```typescript|```bash"),
]


def check_case_file(file_path: Path) -> Dict:
    """检查单个案例文件"""
    result = {
        "file": str(file_path.relative_to(KNOWLEDGE_BASE_PATH)),
        "exists": True,
        "tier": None,
        "l1_passed": False,
        "l2_passed": False,
        "l1_missing": [],
        "l2_missing": [],
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

    # 检查 tier
    tier_match = re.search(r"tier适用[：:]\s*L(\d)", content)
    if tier_match:
        result["tier"] = int(tier_match.group(1))

    # L1 检查
    for name, pattern in L1_CHECKS:
        if not re.search(pattern, content, re.IGNORECASE):
            result["l1_missing"].append(name)

    result["l1_passed"] = len(result["l1_missing"]) == 0

    # L2 检查（仅当 tier 包含 L2 时）
    if result["tier"] and result["tier"] >= 2:
        for name, pattern in L2_CHECKS:
            if not re.search(pattern, content, re.IGNORECASE):
                result["l2_missing"].append(name)
        result["l2_passed"] = len(result["l2_missing"]) == 0
    else:
        result["l2_passed"] = True  # 不需要 L2

    return result


def check_directory(directory: Path) -> List[Dict]:
    """检查目录下所有案例"""
    results = []
    if not directory.exists():
        return results

    for md_file in directory.rglob("*.md"):
        results.append(check_case_file(md_file))

    return results


def generate_report(core_results: List[Dict], extended_results: List[Dict]) -> str:
    """生成检查报告"""
    report = []
    report.append("# 案例覆盖度检查报告")
    report.append("")
    report.append(f"**检查时间**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 核心案例统计
    report.append("## 核心案例 (L1+L2)")
    report.append("")
    total = len(core_results)
    l1_passed = sum(1 for r in core_results if r["l1_passed"])
    l2_passed = sum(1 for r in core_results if r["l2_passed"])

    report.append(f"- 总数: {total}")
    report.append(f"- L1 通过: {l1_passed}/{total} ({l1_passed/total*100:.1f}%)" if total > 0 else "- L1 通过: 0/0")
    if total > 0:
        report.append(f"- L2 通过: {l2_passed}/{total} ({l2_passed/total*100:.1f}%)")
    report.append("")

    # 扩展案例统计
    report.append("## 扩展案例 (L1骨架版)")
    report.append("")
    ext_total = len(extended_results)
    ext_l1_passed = sum(1 for r in extended_results if r["l1_passed"])

    report.append(f"- 总数: {ext_total}")
    if ext_total > 0:
        report.append(f"- L1 通过: {ext_l1_passed}/{ext_total} ({ext_l1_passed/ext_total*100:.1f}%)")
    report.append("")

    # 未通过的案例
    report.append("## 需要修复的案例")
    report.append("")

    failed = [r for r in core_results + extended_results if not r["l1_passed"] or not r["l2_passed"]]
    if failed:
        for r in failed[:20]:  # 最多显示 20 个
            issues = []
            if not r["l1_passed"]:
                issues.append(f"L1缺失: {', '.join(r['l1_missing'])}")
            if not r["l2_passed"]:
                issues.append(f"L2缺失: {', '.join(r['l2_missing'])}")
            report.append(f"- {r['file']}: {'; '.join(issues)}")
    else:
        report.append("✅ 所有案例检查通过！")

    return "\n".join(report)


def main():
    """主函数"""
    print("检查核心案例...")
    core_results = check_directory(CORE_CASES_PATH)

    print("检查扩展案例...")
    extended_results = check_directory(EXTENDED_CASES_PATH)

    print("\n生成报告...\n")
    report = generate_report(core_results, extended_results)
    print(report)

    # 保存报告
    report_path = KNOWLEDGE_BASE_PATH / "tools" / "coverage-report.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"\n报告已保存到: {report_path}")

    # 返回退出码
    all_passed = all(r["l1_passed"] and r["l2_passed"] for r in core_results + extended_results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
