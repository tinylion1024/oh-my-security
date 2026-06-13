"""
依赖安全审计模块 - Oh-My-Security

检测项目依赖中的安全问题:
- 已知漏洞扫描
- License 合规性检查
- 供应链投毒风险检测
- 过时依赖识别
- 恶意包特征检测

注意: 本模块内置的漏洞数据库是简化版本，仅包含部分常见漏洞。
生产环境建议配合 npm audit / pip-audit / Snyk 等专业工具使用。
"""
import os
import re
import json
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


# 公开 API
__all__ = [
    'DependencyFinding',
    'scan_dependencies',
    'check_licenses',
    'detect_supply_chain_risk',
    'get_deps_guide',
]


@dataclass
class DependencyFinding:
    """依赖安全发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 漏洞类别
    package: str
    version: str
    description: str
    impact: str
    recommendation: str
    cve_id: str = ""
    license_type: str = ""


# 已知漏洞数据库 (简化版本，仅包含部分常见漏洞示例)
# 注意: 本数据库可能不完整，生产环境建议使用专业漏洞扫描工具:
# - npm: npm audit, Snyk, Dependabot
# - Python: pip-audit, safety, Snyk
# - Go: Nancy, Snyk
# - Rust: cargo-audit
KNOWN_VULNERABILITIES = {
    # npm 包
    "lodash": {
        "4.17.15": {"cve": "CVE-2020-8203", "severity": "HIGH", "desc": "原型污染漏洞"},
        "4.17.14": {"cve": "CVE-2020-8203", "severity": "HIGH", "desc": "原型污染漏洞"},
    },
    "axios": {
        "0.21.0": {"cve": "CVE-2021-3749", "severity": "HIGH", "desc": "SSRF 漏洞"},
        "0.21.1": {"cve": "CVE-2021-3749", "severity": "HIGH", "desc": "SSRF 漏洞"},
    },
    "node-fetch": {
        "2.6.0": {"cve": "CVE-2022-0235", "severity": "MEDIUM", "desc": "信息泄露漏洞"},
    },
    "eventsource": {
        "0.1.6": {"cve": "CVE-2022-1650", "severity": "CRITICAL", "desc": "正则表达式拒绝服务"},
    },
    "minimist": {
        "0.0.8": {"cve": "CVE-2020-7598", "severity": "MEDIUM", "desc": "原型污染漏洞"},
        "1.2.5": {"cve": None, "severity": "LOW", "desc": "版本过旧，建议升级"},
    },
    # Python 包
    "requests": {
        "2.19.0": {"cve": "CVE-2018-18074", "severity": "MEDIUM", "desc": "凭据泄露漏洞"},
    },
    "pyyaml": {
        "5.1": {"cve": "CVE-2020-14343", "severity": "CRITICAL", "desc": "任意代码执行漏洞"},
        "5.2": {"cve": "CVE-2020-14343", "severity": "HIGH", "desc": "任意代码执行漏洞"},
    },
    "jinja2": {
        "2.10": {"cve": "CVE-2019-8341", "severity": "HIGH", "desc": "沙箱逃逸漏洞"},
    },
    "pillow": {
        "6.2.0": {"cve": "CVE-2020-10379", "severity": "HIGH", "desc": "缓冲区溢出漏洞"},
    },
    # Go 包
    "github.com/golang/protobuf": {
        "1.3.1": {"cve": "CVE-2021-3121", "severity": "HIGH", "desc": "反序列化漏洞"},
    },
    # Rust 包
    "openssl": {
        "0.10.32": {"cve": "CVE-2021-3450", "severity": "CRITICAL", "desc": "证书验证绕过"},
    },
}

# 恶意包特征库
MALICIOUS_PACKAGES = {
    # npm 恶意包
    "npmspy": "包含数据窃取代码",
    "node-serialize": "存在远程代码执行漏洞，常被利用",
    "evil-package": "测试用恶意包",
    "crossenv": "窃取环境变量",
    "babelcli": "冒充 babel-cli 的恶意包",
    # Python 恶意包
    "pymafka": "伪造的 Kafka 客户端，包含恶意代码",
    "pypackages": "数据窃取包",
    "python-dateutil": "伪造包，注意不是 dateutil",
    # 通用可疑模式
    "exec": "可疑的命令执行相关包",
    "eval": "可疑的代码执行相关包",
}

# License 风险评估
LICENSE_RISKS = {
    # 高风险 - 传染性 License
    "GPL-2.0": {"risk": "HIGH", "reason": "强 Copyleft，商业代码需开源"},
    "GPL-3.0": {"risk": "HIGH", "reason": "强 Copyleft，商业代码需开源"},
    "AGPL-3.0": {"risk": "CRITICAL", "reason": "网络 Copyleft，SaaS 也需开源"},
    "LGPL-2.1": {"risk": "MEDIUM", "reason": "弱 Copyleft，链接需注意"},
    "LGPL-3.0": {"risk": "MEDIUM", "reason": "弱 Copyleft，链接需注意"},
    "MPL-2.0": {"risk": "MEDIUM", "reason": "文件级 Copyleft"},
    "CDDL-1.0": {"risk": "MEDIUM", "reason": "文件级 Copyleft"},
    "EPL-1.0": {"risk": "MEDIUM", "reason": "弱 Copyleft"},

    # 中风险 - 需要注意
    "Apache-1.1": {"risk": "LOW", "reason": "需保留版权声明"},
    "BSD-3-Clause": {"risk": "LOW", "reason": "宽松，需保留声明"},
    "BSD-2-Clause": {"risk": "LOW", "reason": "宽松，需保留声明"},
    "MIT": {"risk": "LOW", "reason": "宽松，适合商业"},
    "Apache-2.0": {"risk": "LOW", "reason": "宽松，适合商业"},
    "ISC": {"risk": "LOW", "reason": "宽松，类似 MIT"},
    "0BSD": {"risk": "LOW", "reason": "极度宽松"},
    "Unlicense": {"risk": "LOW", "reason": "公共领域"},
    "WTFPL": {"risk": "LOW", "reason": "极度宽松"},
    "Zlib": {"risk": "LOW", "reason": "宽松"},

    # 特殊情况
    "UNLICENSED": {"risk": "HIGH", "reason": "未授权，可能侵权"},
    "PROPRIETARY": {"risk": "CRITICAL", "reason": "专有软件，禁止使用"},
    "CUSTOM": {"risk": "MEDIUM", "reason": "自定义 License，需审查"},
}

# 依赖安全最佳实践指南
DEPS_SECURITY_GUIDE = """
# 依赖安全最佳实践指南

## 1. 依赖选择原则

### 最小化原则
- 只引入真正需要的依赖
- 避免引入整个库而只用一个函数
- 定期清理未使用的依赖

### 活跃度评估
- 检查最近更新时间（建议 6 个月内）
- 检查 Issue 响应速度
- 检查贡献者数量和社区活跃度
- 检查下载量和 GitHub Stars

### 安全性评估
- 检查是否有已知 CVE
- 检查是否有安全更新版本
- 检查是否维护安全分支

## 2. 版本锁定策略

### 锁文件必须提交
- **npm**: 提交 `package-lock.json`
- **pip**: 提交 `requirements.txt` 并锁定版本
- **Go**: 提交 `go.sum`
- **Rust**: 提交 `Cargo.lock`

### 版本范围限制
```
# 不推荐 - 范围太大
"lodash": "^4.0.0"

# 推荐 - 锁定小版本
"lodash": "^4.17.21"

# 生产环境 - 精确版本
"lodash": "4.17.21"
```

## 3. License 合规检查

### 企业项目禁用 License
- **AGPL-3.0**: SaaS 必须开源
- **GPL-2.0/3.0**: 衍生作品必须开源
- **SSPL**: Server Side Public License，有争议

### 推荐的宽松 License
- MIT
- Apache-2.0
- BSD-2-Clause / BSD-3-Clause
- ISC

### License 兼容性
```
MIT + Apache-2.0 = 兼容
MIT + GPL-3.0 = 兼容 (结果为 GPL-3.0)
Apache-2.0 + GPL-2.0 = 不兼容!
```

## 4. 供应链安全

### 检查包来源
- 使用官方 registry
- 验证包名拼写，防止 typosquatting
- 检查作者可信度
- 警惕新发布的包（可能后门）

### 可疑包特征
- 包名与热门包相似但有细微差别
- 作者历史可疑
- 包含网络请求代码
- 包含 eval、exec 等动态执行
- 发布后立即大量下载（刷量）

### 保护措施
- 使用私有 registry 镜像
- 配置包白名单
- 使用 SRI 校验脚本完整性
- 审计依赖更新

## 5. 定期审计流程

### 自动化检测
```bash
# npm
npm audit
npm audit fix

# pip
pip-audit
safety check

# Go
go list -m -json all | nancy sleuth

# Rust
cargo audit
```

### CI/CD 集成
```yaml
# GitHub Actions 示例
- name: Security Audit
  run: |
    npm audit --audit-level=moderate
    # 或
    pip-audit --desc --ignore-vuln CVE-XXXX-XXXXX
```

### 定期更新
- 每周检查依赖更新
- 每月进行安全审计
- 每季度清理过时依赖

## 6. 应急响应

### 发现漏洞时
1. 立即评估影响范围
2. 查找安全补丁版本
3. 升级到安全版本
4. 如果无法升级，考虑打补丁
5. 记录处理过程

### 发现恶意包时
1. 立即移除依赖
2. 检查是否执行了恶意代码
3. 轮换可能泄露的密钥
4. 报告给 registry 维护者
5. 通知受影响的项目

## 7. 工具推荐

### 漏洞扫描
- **npm**: npm audit, Snyk, Dependabot
- **Python**: pip-audit, safety, Snyk
- **Go**: Nancy, Snyk
- **Rust**: cargo-audit

### License 检查
- license-checker (npm)
- pip-licenses (Python)
- go-licenses (Go)
- cargo-license (Rust)

### 供应链安全
- Snyk
- Socket.dev
- OWASP Dependency-Check
- Dependabot
"""


def ask_ai(prompt: str) -> str:
    """
    通过调用本机的 gemini CLI 工具，利用大模型处理 Prompt。
    """
    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"AI 引擎调用失败:\n{result.stderr}"
    except FileNotFoundError:
        return "未找到 gemini CLI 工具。请确保已安装并配置好 Gemini 命令行环境。"
    except Exception as e:
        return f"执行期间发生异常: {e}"


def parse_package_json(file_path: str) -> Dict:
    """
    解析 package.json (npm) 文件

    Args:
        file_path: package.json 文件路径

    Returns:
        解析后的依赖信息字典
    """
    dependencies = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 获取所有依赖类型
        for dep_type in ['dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies']:
            if dep_type in data:
                for pkg, version in data[dep_type].items():
                    # 清理版本字符串 (移除 ^, ~, >= 等前缀)
                    clean_version = re.sub(r'^[^\d]*', '', version.split(' ')[0])
                    dependencies[pkg] = {
                        'version': clean_version,
                        'raw_version': version,
                        'type': dep_type
                    }

        # 获取包名和版本
        project_info = {
            'name': data.get('name', 'unknown'),
            'version': data.get('version', 'unknown'),
        }
    except Exception as e:
        return {'error': str(e)}

    return {
        'project': project_info,
        'dependencies': dependencies,
        'file_path': file_path,
        'type': 'npm'
    }


def parse_requirements_txt(file_path: str) -> Dict:
    """
    解析 requirements.txt (Python) 文件

    Args:
        file_path: requirements.txt 文件路径

    Returns:
        解析后的依赖信息字典
    """
    dependencies = {}
    project_name = os.path.basename(os.path.dirname(file_path))

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue

                # 解析包名和版本
                # 支持格式: pkg==1.0.0, pkg>=1.0.0, pkg~=1.0.0, pkg
                match = re.match(r'^([a-zA-Z0-9_-]+)\s*([=<>~!]+)\s*([\d.]+)?', line)
                if match:
                    pkg_name = match.group(1)
                    operator = match.group(2) or ''
                    version = match.group(3) or 'unknown'
                    dependencies[pkg_name] = {
                        'version': version,
                        'raw_version': line,
                        'operator': operator,
                        'type': 'runtime'
                    }
                elif line and not line.startswith('-'):
                    # 无版本约束
                    pkg_name = line.split('[')[0]  # 处理 extras
                    dependencies[pkg_name] = {
                        'version': 'any',
                        'raw_version': line,
                        'type': 'runtime'
                    }
    except Exception as e:
        return {'error': str(e)}

    return {
        'project': {'name': project_name},
        'dependencies': dependencies,
        'file_path': file_path,
        'type': 'python'
    }


def parse_go_mod(file_path: str) -> Dict:
    """
    解析 go.mod (Go) 文件

    Args:
        file_path: go.mod 文件路径

    Returns:
        解析后的依赖信息字典
    """
    dependencies = {}
    project_name = 'unknown'
    go_version = 'unknown'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析 module 名称
        module_match = re.search(r'module\s+([^\s]+)', content)
        if module_match:
            project_name = module_match.group(1)

        # 解析 Go 版本
        go_match = re.search(r'go\s+([\d.]+)', content)
        if go_match:
            go_version = go_match.group(1)

        # 解析 require 块
        # 格式: require ( ... ) 或 require pkg v1.0.0
        require_block = re.search(r'require\s*\(([^)]+)\)', content, re.DOTALL)
        if require_block:
            for line in require_block.group(1).strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    parts = line.split()
                    if len(parts) >= 2:
                        pkg_path = parts[0]
                        version = parts[1].lstrip('v')
                        dependencies[pkg_path] = {
                            'version': version,
                            'raw_version': line,
                            'type': 'direct' if '// indirect' not in line else 'indirect'
                        }

        # 单行 require
        single_requires = re.findall(r'require\s+([^\s]+)\s+v?([\d.]+)', content)
        for pkg_path, version in single_requires:
            if pkg_path not in dependencies:
                dependencies[pkg_path] = {
                    'version': version,
                    'raw_version': f'{pkg_path} v{version}',
                    'type': 'direct'
                }
    except Exception as e:
        return {'error': str(e)}

    return {
        'project': {'name': project_name, 'go_version': go_version},
        'dependencies': dependencies,
        'file_path': file_path,
        'type': 'go'
    }


def parse_cargo_toml(file_path: str) -> Dict:
    """
    解析 Cargo.toml (Rust) 文件

    Args:
        file_path: Cargo.toml 文件路径

    Returns:
        解析后的依赖信息字典
    """
    dependencies = {}
    project_name = 'unknown'
    rust_version = 'unknown'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 解析 [package] 部分
        name_match = re.search(r'\[package\].*?name\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        if name_match:
            project_name = name_match.group(1)

        version_match = re.search(r'\[package\].*?rust-version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
        if version_match:
            rust_version = version_match.group(1)

        # 解析 [dependencies] 部分
        deps_match = re.search(r'\[dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
        if deps_match:
            deps_content = deps_match.group(1)
            # 格式: pkg = "1.0.0" 或 pkg = { version = "1.0.0" }
            for line in deps_content.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                # 简单版本
                simple_match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', line)
                if simple_match:
                    pkg_name = simple_match.group(1)
                    version = simple_match.group(2)
                    dependencies[pkg_name] = {
                        'version': version,
                        'raw_version': line,
                        'type': 'direct'
                    }
                    continue

                # 复杂版本
                complex_match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*\{.*?version\s*=\s*["\']([^"\']+)["\']', line)
                if complex_match:
                    pkg_name = complex_match.group(1)
                    version = complex_match.group(2)
                    dependencies[pkg_name] = {
                        'version': version,
                        'raw_version': line,
                        'type': 'direct'
                    }

        # 解析 [dev-dependencies]
        dev_deps_match = re.search(r'\[dev-dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
        if dev_deps_match:
            dev_deps_content = dev_deps_match.group(1)
            for line in dev_deps_content.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                simple_match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']([^"\']+)["\']', line)
                if simple_match:
                    pkg_name = simple_match.group(1)
                    version = simple_match.group(2)
                    dependencies[pkg_name] = {
                        'version': version,
                        'raw_version': line,
                        'type': 'dev'
                    }
    except Exception as e:
        return {'error': str(e)}

    return {
        'project': {'name': project_name, 'rust_version': rust_version},
        'dependencies': dependencies,
        'file_path': file_path,
        'type': 'rust'
    }


def detect_lock_files(path: str) -> Dict[str, str]:
    """
    检测项目中的依赖文件

    Args:
        path: 项目根目录

    Returns:
        检测到的依赖文件字典 {类型: 文件路径}
    """
    lock_files = {}

    dep_file_patterns = {
        'npm': ['package.json'],
        'python': ['requirements.txt', 'requirements-dev.txt', 'Pipfile'],
        'go': ['go.mod'],
        'rust': ['Cargo.toml'],
    }

    for lang, files in dep_file_patterns.items():
        for f in files:
            file_path = os.path.join(path, f)
            if os.path.exists(file_path):
                if lang not in lock_files:  # 只记录第一个找到的
                    lock_files[lang] = file_path

    return lock_files


def scan_dependencies(path: str) -> str:
    """
    扫描依赖漏洞

    Args:
        path: 项目目录路径

    Returns:
        格式化的 Markdown 安全报告
    """
    if not os.path.exists(path):
        return f"路径不存在: {path}"

    # 检测依赖文件
    lock_files = detect_lock_files(path)

    if not lock_files:
        return f"""# 依赖漏洞扫描报告

**扫描路径**: `{path}`

## 未检测到依赖文件

未找到以下任一依赖文件:
- `package.json` (npm)
- `requirements.txt` (Python)
- `go.mod` (Go)
- `Cargo.toml` (Rust)

请确保在项目根目录运行扫描命令。
"""

    all_findings: List[DependencyFinding] = []
    parsed_deps: Dict = {}

    # 解析每种类型的依赖文件
    parsers = {
        'npm': parse_package_json,
        'python': parse_requirements_txt,
        'go': parse_go_mod,
        'rust': parse_cargo_toml,
    }

    for lang, file_path in lock_files.items():
        parser = parsers.get(lang)
        if parser:
            result = parser(file_path)
            if 'error' not in result:
                parsed_deps[lang] = result

    # 检查已知漏洞
    for lang, deps_info in parsed_deps.items():
        deps = deps_info.get('dependencies', {})
        for pkg_name, pkg_info in deps.items():
            version = pkg_info.get('version', '')

            # 检查已知漏洞数据库
            if pkg_name in KNOWN_VULNERABILITIES:
                vuln_versions = KNOWN_VULNERABILITIES[pkg_name]
                if version in vuln_versions:
                    vuln_info = vuln_versions[version]
                    all_findings.append(DependencyFinding(
                        severity=vuln_info['severity'],
                        category="已知漏洞",
                        package=pkg_name,
                        version=version,
                        description=vuln_info['desc'],
                        impact="可能被攻击者利用执行恶意代码或窃取数据",
                        recommendation=f"升级 {pkg_name} 到最新安全版本",
                        cve_id=vuln_info.get('cve', '')
                    ))

            # 检查恶意包
            if pkg_name.lower() in [m.lower() for m in MALICIOUS_PACKAGES.keys()]:
                for mal_pkg, mal_desc in MALICIOUS_PACKAGES.items():
                    if pkg_name.lower() == mal_pkg.lower():
                        all_findings.append(DependencyFinding(
                            severity="CRITICAL",
                            category="恶意包检测",
                            package=pkg_name,
                            version=version,
                            description=f"疑似恶意包: {mal_desc}",
                            impact="可能包含后门或数据窃取代码",
                            recommendation=f"立即移除 {pkg_name}，寻找替代方案"
                        ))
                        break

            # 检查可疑包名模式
            suspicious_patterns = [
                (r'.*-hack', "包名包含 'hack' 关键字"),
                (r'.*-crack', "包名包含 'crack' 关键字"),
                (r'.*-steal', "包名包含 'steal' 关键字"),
                (r'exec.*', "包名与代码执行相关"),
                (r'eval.*', "包名与代码执行相关"),
            ]

            for pattern, desc in suspicious_patterns:
                if re.match(pattern, pkg_name, re.IGNORECASE):
                    all_findings.append(DependencyFinding(
                        severity="MEDIUM",
                        category="可疑包名",
                        package=pkg_name,
                        version=version,
                        description=desc,
                        impact="可能是恶意包或存在安全风险",
                        recommendation="审查该包的来源和用途，考虑移除"
                    ))
                    break

    # 生成报告
    return _generate_scan_report(all_findings, parsed_deps)


def check_licenses(path: str) -> str:
    """
    检查 License 合规性

    Args:
        path: 项目目录路径

    Returns:
        格式化的 Markdown License 合规报告
    """
    if not os.path.exists(path):
        return f"路径不存在: {path}"

    # 检测依赖文件
    lock_files = detect_lock_files(path)

    if not lock_files:
        return f"""# License 合规检查报告

**检查路径**: `{path}`

## 未检测到依赖文件

未找到依赖文件，无法进行 License 检查。
"""

    all_findings: List[DependencyFinding] = []
    license_stats: Dict[str, List[str]] = {}
    parsed_deps: Dict = {}

    # 解析依赖文件
    parsers = {
        'npm': parse_package_json,
        'python': parse_requirements_txt,
        'go': parse_go_mod,
        'rust': parse_cargo_toml,
    }

    for lang, file_path in lock_files.items():
        parser = parsers.get(lang)
        if parser:
            result = parser(file_path)
            if 'error' not in result:
                parsed_deps[lang] = result

    # 常见 License 映射 (简化版本)
    common_licenses = {
        # npm 常见
        'lodash': 'MIT',
        'axios': 'MIT',
        'express': 'MIT',
        'react': 'MIT',
        'vue': 'MIT',
        'webpack': 'MIT',
        'typescript': 'Apache-2.0',
        'eslint': 'MIT',
        # Python 常见
        'requests': 'Apache-2.0',
        'django': 'BSD-3-Clause',
        'flask': 'BSD-3-Clause',
        'numpy': 'BSD-3-Clause',
        'pandas': 'BSD-3-Clause',
        'pyyaml': 'MIT',
        'jinja2': 'BSD-3-Clause',
        'pillow': 'PIL',
        'click': 'BSD-3-Clause',
        # Go 常见
        'github.com/gin-gonic/gin': 'MIT',
        'github.com/golang/protobuf': 'BSD-3-Clause',
        'github.com/gorilla/mux': 'BSD-3-Clause',
        # Rust 常见
        'serde': 'Apache-2.0',
        'tokio': 'MIT',
        'actix-web': 'Apache-2.0',
        'openssl': 'Apache-2.0',
    }

    # 检查每个依赖的 License
    for lang, deps_info in parsed_deps.items():
        deps = deps_info.get('dependencies', {})
        for pkg_name, pkg_info in deps.items():
            # 查找 License
            license_type = common_licenses.get(pkg_name, 'UNKNOWN')

            if license_type != 'UNKNOWN':
                # 记录统计
                if license_type not in license_stats:
                    license_stats[license_type] = []
                license_stats[license_type].append(pkg_name)

                # 检查 License 风险
                if license_type in LICENSE_RISKS:
                    risk_info = LICENSE_RISKS[license_type]
                    if risk_info['risk'] in ['CRITICAL', 'HIGH', 'MEDIUM']:
                        all_findings.append(DependencyFinding(
                            severity=risk_info['risk'],
                            category="License 风险",
                            package=pkg_name,
                            version=pkg_info.get('version', 'unknown'),
                            description=risk_info['reason'],
                            impact="可能导致法律风险或需要开源商业代码",
                            recommendation=f"评估 {pkg_name} ({license_type}) 的使用是否合规",
                            license_type=license_type
                        ))
            else:
                # 未知 License
                if 'UNKNOWN' not in license_stats:
                    license_stats['UNKNOWN'] = []
                license_stats['UNKNOWN'].append(pkg_name)

    # 生成报告
    return _generate_license_report(all_findings, license_stats, parsed_deps)


def detect_supply_chain_risk(path: str) -> str:
    """
    检测供应链投毒风险

    Args:
        path: 项目目录路径

    Returns:
        格式化的 Markdown 供应链风险报告
    """
    if not os.path.exists(path):
        return f"路径不存在: {path}"

    # 检测依赖文件
    lock_files = detect_lock_files(path)

    if not lock_files:
        return f"""# 供应链安全风险检测报告

**检测路径**: `{path}`

## 未检测到依赖文件

未找到依赖文件，无法进行供应链风险检测。
"""

    all_findings: List[DependencyFinding] = []
    risk_factors: Dict[str, List[str]] = {
        'typosquatting': [],
        'unmaintained': [],
        'suspicious': [],
        'missing_lock': [],
    }

    parsed_deps: Dict = {}

    # 解析依赖文件
    parsers = {
        'npm': parse_package_json,
        'python': parse_requirements_txt,
        'go': parse_go_mod,
        'rust': parse_cargo_toml,
    }

    for lang, file_path in lock_files.items():
        parser = parsers.get(lang)
        if parser:
            result = parser(file_path)
            if 'error' not in result:
                parsed_deps[lang] = result

    # 常见热门包列表 (用于检测 typosquatting)
    popular_packages = {
        'npm': ['lodash', 'axios', 'express', 'react', 'vue', 'webpack', 'typescript', 'eslint', 'chalk', 'commander'],
        'python': ['requests', 'django', 'flask', 'numpy', 'pandas', 'pytest', 'boto3', 'celery', 'redis', 'jinja2'],
        'go': ['gin', 'gorm', 'logrus', 'viper', 'cobra'],
        'rust': ['serde', 'tokio', 'actix-web', 'clap', 'log'],
    }

    # 检查 typosquatting 风险
    def check_typosquatting(pkg_name: str, popular: List[str]) -> Tuple[bool, str]:
        """检查是否是 typosquatting 包"""
        pkg_lower = pkg_name.lower()
        for pop in popular:
            pop_lower = pop.lower()
            # 检查相似度
            if pkg_lower != pop_lower:
                # Levenshtein 距离
                if len(pkg_lower) >= 3 and len(pop_lower) >= 3:
                    if _levenshtein_distance(pkg_lower, pop_lower) <= 2:
                        return True, pop
        return False, ""

    for lang, deps_info in parsed_deps.items():
        deps = deps_info.get('dependencies', {})
        popular = popular_packages.get(lang, [])

        for pkg_name, pkg_info in deps.items():
            version = pkg_info.get('version', 'unknown')

            # 1. Typosquatting 检测
            is_typo, similar_to = check_typosquatting(pkg_name, popular)
            if is_typo:
                risk_factors['typosquatting'].append(f"{pkg_name} (类似: {similar_to})")
                all_findings.append(DependencyFinding(
                    severity="CRITICAL",
                    category="Typosquatting 风险",
                    package=pkg_name,
                    version=version,
                    description=f"包名与热门包 '{similar_to}' 极其相似，可能是恶意包",
                    impact="可能是攻击者创建的恶意包，窃取数据或执行恶意代码",
                    recommendation=f"确认是否应该使用 '{similar_to}' 而非 '{pkg_name}'"
                ))

            # 2. 恶意包特征检测
            malicious_indicators = [
                (r'.*(-nodejs|-npm|-python|-pip)$', "包名包含语言后缀，可疑"),
                (r'.*(hack|crack|steal|keylog|malware)', "包名包含恶意关键字"),
                (r'.*(free|premium|cracked|bypass)', "包名暗示破解功能"),
            ]

            for pattern, desc in malicious_indicators:
                if re.match(pattern, pkg_name, re.IGNORECASE):
                    risk_factors['suspicious'].append(pkg_name)
                    all_findings.append(DependencyFinding(
                        severity="HIGH",
                        category="可疑包特征",
                        package=pkg_name,
                        version=version,
                        description=desc,
                        impact="可能包含恶意代码",
                        recommendation="审查该包的源代码和作者信息"
                    ))
                    break

    # 检查锁文件是否存在
    lock_file_checks = {
        'npm': ('package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'),
        'python': ('Pipfile.lock', 'poetry.lock'),
        'go': ('go.sum',),
        'rust': ('Cargo.lock',),
    }

    for lang, lock_files_names in lock_file_checks.items():
        if lang in lock_files:
            has_lock = any(os.path.exists(os.path.join(path, lf)) for lf in lock_files_names)
            if not has_lock:
                risk_factors['missing_lock'].append(lang)
                all_findings.append(DependencyFinding(
                    severity="HIGH",
                    category="缺少锁文件",
                    package="项目",
                    version="N/A",
                    description=f"{lang} 项目缺少锁文件 ({', '.join(lock_files_names)})",
                    impact="可能导致依赖版本不一致，增加供应链攻击风险",
                    recommendation="生成并提交锁文件，确保依赖版本一致"
                ))

    # 生成报告
    return _generate_supply_chain_report(all_findings, risk_factors, parsed_deps)


def _levenshtein_distance(s1: str, s2: str) -> int:
    """计算两个字符串的 Levenshtein 距离"""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def get_deps_guide() -> str:
    """
    获取依赖安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return DEPS_SECURITY_GUIDE


def _generate_scan_report(findings: List[DependencyFinding], parsed_deps: Dict) -> str:
    """生成漏洞扫描报告"""

    if not findings:
        total_deps = sum(len(deps.get('dependencies', {})) for deps in parsed_deps.values())
        return f"""# 依赖漏洞扫描报告

## 扫描摘要

**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**扫描结果**: 未发现已知漏洞

**扫描依赖数量**: {total_deps}

---

*建议定期执行依赖扫描，保持依赖安全。*
"""

    # 按严重程度分组
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.severity, 4))

    # 统计
    stats = {
        'CRITICAL': len([f for f in findings if f.severity == 'CRITICAL']),
        'HIGH': len([f for f in findings if f.severity == 'HIGH']),
        'MEDIUM': len([f for f in findings if f.severity == 'MEDIUM']),
        'LOW': len([f for f in findings if f.severity == 'LOW']),
    }

    report = f"""# 依赖漏洞扫描报告

## 扫描摘要

**扫描时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 漏洞统计

| 严重程度 | 数量 |
|---------|------|
| CRITICAL | {stats['CRITICAL']} |
| HIGH | {stats['HIGH']} |
| MEDIUM | {stats['MEDIUM']} |
| LOW | {stats['LOW']} |
| **总计** | **{len(findings)}** |

## 扫描范围

"""

    for lang, deps_info in parsed_deps.items():
        deps = deps_info.get('dependencies', {})
        report += f"- **{lang.upper()}**: {deps_info.get('file_path', '')} ({len(deps)} 个依赖)\n"

    report += "\n## 漏洞详情\n\n"

    current_severity = None
    severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}

    for finding in sorted_findings:
        if finding.severity != current_severity:
            current_severity = finding.severity
            report += f"\n### {severity_emoji.get(current_severity, '⚪')} {current_severity} 级别漏洞\n\n"

        cve_info = f" ({finding.cve_id})" if finding.cve_id else ""
        report += f"""#### {finding.package}@{finding.version}

**类别**: {finding.category}{cve_info}

**问题描述**: {finding.description}

**潜在影响**: {finding.impact}

**修复建议**: {finding.recommendation}

---

"""

    # 使用 AI 进行深度分析
    if stats['CRITICAL'] > 0 or stats['HIGH'] > 0:
        report += "\n## AI 深度分析\n\n"

        critical_findings = [f for f in findings if f.severity in ['CRITICAL', 'HIGH']][:5]
        context = "\n".join([
            f"- [{f.severity}] {f.package}@{f.version}: {f.description} ({f.cve_id})"
            for f in critical_findings
        ])

        prompt = f"""作为供应链安全专家，请对以下依赖漏洞进行深度分析：

{context}

请提供:
1. 这些漏洞的攻击场景分析
2. 优先修复顺序建议
3. 替代方案推荐
4. 长期安全策略建议

请用中文回答，保持简洁专业。
"""
        ai_analysis = ask_ai(prompt)
        report += ai_analysis

    return report


def _generate_license_report(findings: List[DependencyFinding], license_stats: Dict[str, List[str]], parsed_deps: Dict) -> str:
    """生成 License 合规报告"""

    report = f"""# License 合规检查报告

## 检查摘要

**检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## License 分布统计

| License | 数量 | 风险等级 |
|---------|------|---------|
"""

    for license_type, packages in sorted(license_stats.items(), key=lambda x: -len(x[1])):
        risk = LICENSE_RISKS.get(license_type, {}).get('risk', 'UNKNOWN')
        risk_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢', 'UNKNOWN': '⚪'}
        report += f"| {license_type} | {len(packages)} | {risk_emoji.get(risk, '⚪')} {risk} |\n"

    if findings:
        # 按严重程度分组
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.severity, 4))

        report += "\n## License 风险详情\n\n"

        current_severity = None
        severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}

        for finding in sorted_findings:
            if finding.severity != current_severity:
                current_severity = finding.severity
                report += f"\n### {severity_emoji.get(current_severity, '⚪')} {current_severity} 级别风险\n\n"

            report += f"""#### {finding.package}@{finding.version}

**License**: {finding.license_type}

**问题描述**: {finding.description}

**潜在影响**: {finding.impact}

**修复建议**: {finding.recommendation}

---

"""
    else:
        report += "\n## License 合规状态\n\n"
        report += "> 未发现高风险 License 问题。\n"

    report += """
## License 合规建议

### 企业项目建议

1. **禁止使用**: AGPL-3.0, GPL-2.0/3.0 (强 Copyleft)
2. **谨慎使用**: LGPL, MPL (弱 Copyleft)
3. **推荐使用**: MIT, Apache-2.0, BSD (宽松 License)

### 合规检查流程

1. 引入新依赖时检查 License
2. 记录所有依赖的 License
3. 定期审查 License 变更
4. 保留所有 License 声明文件

---

*建议使用 license-checker 等工具自动化检查。*
"""

    return report


def _generate_supply_chain_report(findings: List[DependencyFinding], risk_factors: Dict[str, List[str]], parsed_deps: Dict) -> str:
    """生成供应链风险报告"""

    report = f"""# 供应链安全风险检测报告

## 检测摘要

**检测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 风险因素统计

| 风险类型 | 数量 | 说明 |
|---------|------|------|
| Typosquatting | {len(risk_factors['typosquatting'])} | 包名与热门包相似 |
| 可疑包 | {len(risk_factors['suspicious'])} | 包含可疑特征 |
| 缺少锁文件 | {len(risk_factors['missing_lock'])} | 未锁定依赖版本 |

"""

    if risk_factors['typosquatting']:
        report += "### Typosquatting 风险包\n\n"
        for pkg in risk_factors['typosquatting']:
            report += f"- {pkg}\n"
        report += "\n"

    if risk_factors['suspicious']:
        report += "### 可疑包\n\n"
        for pkg in risk_factors['suspicious']:
            report += f"- {pkg}\n"
        report += "\n"

    if risk_factors['missing_lock']:
        report += "### 缺少锁文件\n\n"
        for lang in risk_factors['missing_lock']:
            report += f"- {lang} 项目\n"
        report += "\n"

    if findings:
        # 按严重程度分组
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.severity, 4))

        report += "## 风险详情\n\n"

        current_severity = None
        severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}

        for finding in sorted_findings:
            if finding.severity != current_severity:
                current_severity = finding.severity
                report += f"\n### {severity_emoji.get(current_severity, '⚪')} {current_severity} 级别风险\n\n"

            report += f"""#### {finding.package}@{finding.version}

**类别**: {finding.category}

**问题描述**: {finding.description}

**潜在影响**: {finding.impact}

**修复建议**: {finding.recommendation}

---

"""
    else:
        report += "## 检测结果\n\n"
        report += "> 未发现明显的供应链安全风险。\n"

    report += """
## 供应链安全建议

### 依赖选择

1. 只使用官方 registry
2. 验证包名拼写
3. 检查作者可信度
4. 审查包的下载量和评价

### 版本锁定

1. 提交锁文件到版本控制
2. 使用精确版本号
3. 定期更新但保持可控

### 持续监控

1. 集成 Dependabot 或 Snyk
2. 订阅安全公告
3. 定期执行安全扫描

---

*供应链攻击日益增多，建议定期审查依赖安全性。*
"""

    return report


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "."

    print("=" * 60)
    print("依赖漏洞扫描测试")
    print("=" * 60)
    print(scan_dependencies(path))

    print("\n" + "=" * 60)
    print("License 合规检查测试")
    print("=" * 60)
    print(check_licenses(path))

    print("\n" + "=" * 60)
    print("供应链风险检测测试")
    print("=" * 60)
    print(detect_supply_chain_risk(path))
