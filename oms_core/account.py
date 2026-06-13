"""
账号安全审计模块 - Oh-My-Security

检测账号相关代码中的常见安全问题:
- 弱密码检测
- 缺少MFA/2FA
- 密码复用风险
- Session安全配置
- 登录频率限制
- 撞库风险检测
"""
import os
import re
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SecurityFinding:
    """安全发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 安全类别
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    recommendation: str


# 密码强度评估标准
PASSWORD_STRENGTH_CRITERIA = {
    "length": {"min": 8, "recommended": 12},
    "has_uppercase": r"[A-Z]",
    "has_lowercase": r"[a-z]",
    "has_digit": r"[0-9]",
    "has_special": r"[!@#$%^&*(),.?\":{}|<>]",
    "common_patterns": [
        "password", "123456", "qwerty", "abc123", "admin", "letmein",
        "welcome", "monkey", "dragon", "master", "login", "root"
    ]
}

# 账号安全最佳实践指南
ACCOUNT_SECURITY_GUIDE = """
# 账号安全最佳实践指南

## 1. 密码安全

### 密码强度要求
- **最小长度**: 至少 12 位字符（8 位为最低要求）
- **复杂度**: 必须包含大小写字母、数字和特殊字符
- **唯一性**: 每个账户使用不同密码
- **避免模式**: 不使用字典词汇、个人信息或常见模式

### 密码存储
- **加密方式**: 使用 bcrypt、Argon2 或 PBKDF2 进行哈希
- **加盐**: 每个密码使用唯一的随机盐值
- **禁止**: 明文存储、MD5、SHA1 单次哈希

## 2. 多因素认证 (MFA/2FA)

### 实现方式
- **TOTP (Time-based OTP)**: 推荐，基于时间的一次性密码
- **SMS OTP**: 次选，存在 SIM 卡劫持风险
- **硬件密钥**: 最安全，如 YubiKey
- **备用码**: 提供一次性备用码以防丢失 MFA 设备

### 推荐场景
- 登录验证
- 敏感操作（修改密码、绑定手机等）
- 大额交易
- 管理员操作

## 3. Session 安全

### Cookie 配置
- **HttpOnly**: 防止 XSS 窃取 Cookie
- **Secure**: 仅 HTTPS 传输
- **SameSite**: 防止 CSRF 攻击
- **过期时间**: 合理设置，不要过长

### Session 管理
- 登录后重新生成 Session ID
- 限制并发登录数量
- 异常登录检测（IP 变化、设备变化）
- 提供强制登出功能

## 4. 登录频率限制

### 限制策略
- **IP 限制**: 同一 IP 每分钟最多 5 次尝试
- **账户锁定**: 连续失败 5 次后锁定 15 分钟
- **验证码**: 失败 3 次后显示验证码
- **渐进延迟**: 每次失败后延迟递增

## 5. 撞库防护

### 检测与防护
- **异常登录检测**: IP 变化、设备变化、地理位置突变
- **密码泄露检查**: 对接 Have I Been Pwned API
- **蜜罐账号**: 设置假账号检测撞库攻击
- **验证码触发**: 可疑登录时强制验证码

## 6. 其他安全措施

### 登录日志
- 记录所有登录尝试（成功/失败）
- 记录 IP、设备、时间、地理位置
- 异常登录告警通知

### 设备管理
- 显示已登录设备列表
- 支持远程登出指定设备
- 新设备登录邮件通知

### 密码重置
- 使用随机令牌，一次性有效
- 令牌过期时间短（如 1 小时）
- 发送邮件确认身份
- 重置后强制登出所有设备
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


def check_password_strength(password: str) -> Dict:
    """
    检测密码强度

    Args:
        password: 待检测的密码字符串

    Returns:
        包含强度评分和详细分析的字典
    """
    result = {
        "password": password[:3] + "*" * (len(password) - 3) if len(password) > 3 else "***",
        "length": len(password),
        "score": 0,
        "max_score": 100,
        "level": "weak",
        "checks": {},
        "warnings": [],
        "suggestions": []
    }

    score = 0

    # 1. 长度检查
    length = len(password)
    if length >= 12:
        score += 25
        result["checks"]["length"] = {"pass": True, "detail": f"长度 {length} 位 (推荐 12+ 位)"}
    elif length >= 8:
        score += 15
        result["checks"]["length"] = {"pass": True, "detail": f"长度 {length} 位 (最低要求)"}
        result["suggestions"].append("建议密码长度增加到 12 位以上")
    else:
        result["checks"]["length"] = {"pass": False, "detail": f"长度仅 {length} 位 (太短)"}
        result["warnings"].append("密码长度不足 8 位，非常不安全")

    # 2. 大写字母
    if re.search(PASSWORD_STRENGTH_CRITERIA["has_uppercase"], password):
        score += 15
        result["checks"]["uppercase"] = {"pass": True, "detail": "包含大写字母"}
    else:
        result["checks"]["uppercase"] = {"pass": False, "detail": "缺少大写字母"}
        result["suggestions"].append("添加大写字母增加复杂度")

    # 3. 小写字母
    if re.search(PASSWORD_STRENGTH_CRITERIA["has_lowercase"], password):
        score += 15
        result["checks"]["lowercase"] = {"pass": True, "detail": "包含小写字母"}
    else:
        result["checks"]["lowercase"] = {"pass": False, "detail": "缺少小写字母"}
        result["suggestions"].append("添加小写字母增加复杂度")

    # 4. 数字
    if re.search(PASSWORD_STRENGTH_CRITERIA["has_digit"], password):
        score += 15
        result["checks"]["digit"] = {"pass": True, "detail": "包含数字"}
    else:
        result["checks"]["digit"] = {"pass": False, "detail": "缺少数字"}
        result["suggestions"].append("添加数字增加复杂度")

    # 5. 特殊字符
    if re.search(PASSWORD_STRENGTH_CRITERIA["has_special"], password):
        score += 20
        result["checks"]["special"] = {"pass": True, "detail": "包含特殊字符"}
    else:
        result["checks"]["special"] = {"pass": False, "detail": "缺少特殊字符"}
        result["suggestions"].append("添加特殊字符 (!@#$%^&*) 增加强度")

    # 6. 常见模式检查
    password_lower = password.lower()
    found_patterns = [p for p in PASSWORD_STRENGTH_CRITERIA["common_patterns"]
                      if p in password_lower]

    if found_patterns:
        score -= 30
        result["checks"]["common_pattern"] = {
            "pass": False,
            "detail": f"包含常见弱密码模式: {', '.join(found_patterns)}"
        }
        result["warnings"].append(f"密码包含常见弱密码: {', '.join(found_patterns)}")
    else:
        result["checks"]["common_pattern"] = {"pass": True, "detail": "无常见弱密码模式"}

    # 7. 连续字符检查
    if _has_sequential_chars(password):
        score -= 10
        result["checks"]["sequential"] = {"pass": False, "detail": "包含连续字符 (如 123, abc)"}
        result["warnings"].append("避免使用连续字符")
    else:
        result["checks"]["sequential"] = {"pass": True, "detail": "无连续字符"}

    # 8. 重复字符检查
    if _has_repeated_chars(password):
        score -= 10
        result["checks"]["repeated"] = {"pass": False, "detail": "包含重复字符"}
        result["warnings"].append("避免使用重复字符")
    else:
        result["checks"]["repeated"] = {"pass": True, "detail": "无重复字符"}

    # 计算最终分数
    score = max(0, min(100, score))
    result["score"] = score

    # 确定等级
    if score >= 80:
        result["level"] = "strong"
    elif score >= 60:
        result["level"] = "medium"
    elif score >= 40:
        result["level"] = "weak"
    else:
        result["level"] = "very_weak"

    return result


def _has_sequential_chars(password: str) -> bool:
    """检查是否有连续字符"""
    sequences = [
        "0123456789",
        "abcdefghijklmnopqrstuvwxyz",
        "qwertyuiop",
        "asdfghjkl",
        "zxcvbnm"
    ]

    password_lower = password.lower()
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i:i+3] in password_lower:
                return True
    return False


def _has_repeated_chars(password: str) -> bool:
    """检查是否有重复字符"""
    return bool(re.search(r'(.)\1{2,}', password))


def detect_credential_stuffing_risk(code_content: str) -> List[SecurityFinding]:
    """
    检测撞库风险

    检测模式:
    - 登录接口缺少验证码保护
    - 缺少登录频率限制
    - 缺少异常登录检测
    - 密码未加密传输

    Args:
        code_content: 代码内容字符串

    Returns:
        安全发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # 查找登录相关函数
    login_patterns = [
        r'(login|signin|auth).*\(',
        r'@(Post|Get)Mapping.*?(login|signin|auth)',
        r'function\s+(login|signin|auth)',
        r'def\s+(login|signin|auth)',
        r'async\s+(login|signin|auth)',
    ]

    in_login_func = False
    func_start = 0
    func_context = []

    for line_idx, line in enumerate(lines, 1):
        for pattern in login_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                in_login_func = True
                func_start = line_idx
                func_context = [line]
                break

        if in_login_func:
            func_context.append(line)

            # 判断函数结束
            if re.search(r'^(function|def|@|async|class|router|app\.|exports\.)', line) and line_idx > func_start + 5:
                func_code = '\n'.join(func_context)

                # 检查验证码
                captcha_patterns = [
                    r'(captcha|验证码|verif.*code)',
                    r'(recaptcha|hcaptcha)',
                    r'(image.*code|图形验证)',
                ]
                has_captcha = any(re.search(p, func_code, re.IGNORECASE) for p in captcha_patterns)

                if not has_captcha:
                    findings.append(SecurityFinding(
                        severity="HIGH",
                        category="缺少验证码保护",
                        file_path="",
                        line_number=func_start,
                        code_snippet=f"登录函数 {func_context[0].strip()[:50]}...",
                        description="登录接口缺少验证码保护",
                        impact="攻击者可进行暴力破解或撞库攻击",
                        recommendation="在连续登录失败后强制显示验证码"
                    ))

                # 检查频率限制
                rate_limit_patterns = [
                    r'(rate.*limit|频率限制|限流)',
                    r'(throttle|limiter)',
                    r'(redis.*incr|incr.*redis)',
                    r'(login.*attempt|attempt.*count)',
                ]
                has_rate_limit = any(re.search(p, func_code, re.IGNORECASE) for p in rate_limit_patterns)

                if not has_rate_limit:
                    findings.append(SecurityFinding(
                        severity="HIGH",
                        category="缺少登录频率限制",
                        file_path="",
                        line_number=func_start,
                        code_snippet=f"登录函数 {func_context[0].strip()[:50]}...",
                        description="登录接口缺少频率限制",
                        impact="攻击者可无限制尝试密码",
                        recommendation="实现基于 IP 或账户的登录频率限制"
                    ))

                # 检查异常登录检测
                anomaly_patterns = [
                    r'(anomaly|异常|geo|location|ip.*check)',
                    r'(device.*id|指纹|fingerprint)',
                    r'(risk|风险)',
                ]
                has_anomaly = any(re.search(p, func_code, re.IGNORECASE) for p in anomaly_patterns)

                if not has_anomaly:
                    findings.append(SecurityFinding(
                        severity="MEDIUM",
                        category="缺少异常登录检测",
                        file_path="",
                        line_number=func_start,
                        code_snippet=f"登录函数 {func_context[0].strip()[:50]}...",
                        description="登录接口缺少异常登录检测",
                        impact="无法识别撞库攻击或异常登录行为",
                        recommendation="实现 IP 变化检测、设备指纹识别等异常检测机制"
                    ))

                in_login_func = False
                func_context = []

    # 检查密码传输方式
    for line_idx, line in enumerate(lines, 1):
        # 检查密码明文传输
        if re.search(r'(password|passwd|pwd)\s*[:=]\s*(request|req|body|params)', line, re.IGNORECASE):
            context_start = max(0, line_idx - 3)
            context_end = min(len(lines), line_idx + 3)
            context = '\n'.join(lines[context_start:context_end])

            # 检查是否有 HTTPS 或加密传输
            if not re.search(r'(https|ssl|tls|encrypt|bcrypt|hash)', context, re.IGNORECASE):
                findings.append(SecurityFinding(
                    severity="HIGH",
                    category="密码传输安全",
                    file_path="",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    description="密码可能以明文形式传输",
                    impact="密码可能被中间人攻击截获",
                    recommendation="确保使用 HTTPS 传输，前端可对密码进行加密"
                ))

    return findings


def check_mfa_implementation(code_content: str) -> List[SecurityFinding]:
    """
    检查 MFA/2FA 实现情况

    Args:
        code_content: 代码内容字符串

    Returns:
        安全发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # 检查是否缺少 MFA 相关代码
    mfa_patterns = [
        r'(mfa|2fa|totp|otp|authenticator)',
        r'(two.?factor|双因素|两步验证)',
        r'(google.*auth|authenticator)',
        r'(pyotp|speakeasy|otplib)',
    ]

    has_mfa = any(
        re.search(pattern, code_content, re.IGNORECASE)
        for pattern in mfa_patterns
    )

    if not has_mfa:
        # 检查是否有敏感操作
        sensitive_patterns = [
            r'(change.*password|修改密码)',
            r'(bind.*phone|绑定手机)',
            r'(withdraw|提现|transfer|转账)',
            r'(delete.*account|注销账户)',
        ]

        has_sensitive = any(
            re.search(pattern, code_content, re.IGNORECASE)
            for pattern in sensitive_patterns
        )

        if has_sensitive:
            findings.append(SecurityFinding(
                severity="MEDIUM",
                category="缺少 MFA/2FA",
                file_path="",
                line_number=0,
                code_snippet="代码中存在敏感操作但未实现 MFA",
                description="敏感操作缺少多因素认证保护",
                impact="密码泄露后攻击者可直接执行敏感操作",
                recommendation="为敏感操作实现 MFA/2FA 验证"
            ))

    return findings


def check_session_security(code_content: str) -> List[SecurityFinding]:
    """
    检查 Session 安全配置

    Args:
        code_content: 代码内容字符串

    Returns:
        安全发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # Cookie 安全配置检查
    cookie_config_patterns = [
        (r'Session.*Cookie.*Secure\s*=\s*False', "Cookie 未启用 Secure 标志"),
        (r'SESSION_COOKIE_SECURE\s*=\s*False', "Flask Session Cookie 未启用 Secure"),
        (r'HttpOnly\s*=\s*False', "Cookie 未启用 HttpOnly 标志"),
        (r'SameSite\s*=\s*None', "Cookie SameSite 设置为 None (可能有 CSRF 风险)"),
    ]

    for line_idx, line in enumerate(lines, 1):
        for pattern, desc in cookie_config_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(SecurityFinding(
                    severity="HIGH",
                    category="Cookie 安全配置",
                    file_path="",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    description=desc,
                    impact="可能导致会话劫持或 CSRF 攻击",
                    recommendation="启用 HttpOnly、Secure、SameSite 属性"
                ))

    # Session 固定攻击检查
    if re.search(r'(login|signin)', code_content, re.IGNORECASE):
        if not re.search(r'(regenerate|new.*session|session.*id)', code_content, re.IGNORECASE):
            findings.append(SecurityFinding(
                severity="MEDIUM",
                category="Session 固定风险",
                file_path="",
                line_number=0,
                code_snippet="登录后未重新生成 Session ID",
                description="登录成功后可能未重新生成 Session ID",
                impact="可能导致 Session 固定攻击",
                recommendation="登录成功后调用 session_regenerate() 或类似方法"
            ))

    # Session 过期时间检查
    if re.search(r'(session.*expir|SESSION.*EXPIR|sessionExpir)', code_content, re.IGNORECASE):
        # 检查是否设置过长
        for line_idx, line in enumerate(lines, 1):
            if re.search(r'(session.*expir|SESSION.*EXPIR).*=\s*([0-9]+)', line, re.IGNORECASE):
                match = re.search(r'=\s*([0-9]+)', line)
                if match:
                    value = int(match.group(1))
                    # 如果是秒，超过 7 天就警告
                    if value > 604800:
                        findings.append(SecurityFinding(
                            severity="LOW",
                            category="Session 过期时间过长",
                            file_path="",
                            line_number=line_idx,
                            code_snippet=line.strip(),
                            description=f"Session 过期时间设置为 {value} 秒 (超过 7 天)",
                            impact="长时间有效的 Session 增加被盗用风险",
                            recommendation="将 Session 过期时间设置为合理范围 (如 24 小时)"
                        ))

    return findings


def check_password_storage(code_content: str) -> List[SecurityFinding]:
    """
    检查密码存储安全

    Args:
        code_content: 代码内容字符串

    Returns:
        安全发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # 危险的密码存储方式
    dangerous_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', "密码硬编码"),
        (r'(md5|MD5)\s*\(\s*(password|pwd)', "使用 MD5 哈希密码"),
        (r'(sha1|SHA1)\s*\(\s*(password|pwd)', "使用 SHA1 哈希密码"),
        (r'hashlib\.(md5|sha1)\s*\(\s*(password|pwd)', "使用弱哈希算法"),
        (r'base64.*password|password.*base64', "密码 Base64 编码"),
    ]

    for line_idx, line in enumerate(lines, 1):
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(SecurityFinding(
                    severity="CRITICAL",
                    category="密码存储不安全",
                    file_path="",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    description=desc,
                    impact="密码可能被轻易破解或泄露",
                    recommendation="使用 bcrypt、Argon2 或 PBKDF2 进行密码哈希"
                ))

    # 检查是否有安全的密码哈希
    safe_patterns = [
        r'bcrypt',
        r'argon2',
        r'pbkdf2',
        r'scrypt',
    ]

    has_safe_hash = any(re.search(p, code_content, re.IGNORECASE) for p in safe_patterns)

    # 如果有密码处理但没有安全哈希
    if re.search(r'(password|pwd)', code_content, re.IGNORECASE) and not has_safe_hash:
        # 检查是否是存储场景
        if re.search(r'(save|store|insert|update).*password', code_content, re.IGNORECASE):
            findings.append(SecurityFinding(
                severity="HIGH",
                category="密码存储方式不明",
                file_path="",
                line_number=0,
                code_snippet="密码存储代码",
                description="未检测到安全的密码哈希实现",
                impact="密码可能以不安全的方式存储",
                recommendation="使用 bcrypt 或 Argon2 进行密码哈希存储"
            ))

    return findings


def check_account_security(path: str) -> str:
    """
    审计账号相关代码，检测安全问题

    Args:
        path: 代码目录或文件路径

    Returns:
        格式化的 Markdown 安全报告
    """
    if not os.path.exists(path):
        return f"路径不存在: {path}"

    files_to_scan = []
    if os.path.isfile(path):
        files_to_scan.append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            # 过滤不需要扫描的目录
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', 'vendor']]
            for f in files:
                if f.endswith(('.py', '.js', '.ts', '.java', '.php', '.go', '.rs', '.jsx', '.tsx')):
                    files_to_scan.append(os.path.join(root, f))

    if not files_to_scan:
        return "未在目标路径下发现支持扫描的源代码文件。"

    all_findings: List[SecurityFinding] = []
    file_contents: Dict[str, str] = {}

    # 收集所有文件内容
    for fpath in files_to_scan[:20]:  # 限制文件数量
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 10000:
                    content = content[:10000] + "\n...(文件过长，截断)..."
                file_contents[fpath] = content
        except Exception:
            continue

    if not file_contents:
        return "读取文件内容失败或文件全为空。"

    # 对每个文件进行扫描
    for fpath, content in file_contents.items():
        # 检查是否包含账号相关关键词
        account_keywords = ['login', 'auth', 'password', 'session', 'user', 'account',
                           '登录', '密码', '账号', '认证', 'mfa', '2fa', 'otp']
        if not any(kw.lower() in content.lower() for kw in account_keywords):
            continue

        # 执行各项检查
        findings = []
        findings.extend(detect_credential_stuffing_risk(content))
        findings.extend(check_mfa_implementation(content))
        findings.extend(check_session_security(content))
        findings.extend(check_password_storage(content))

        # 为每个发现设置文件路径
        for finding in findings:
            finding.file_path = fpath

        all_findings.extend(findings)

    # 生成报告
    return _generate_report(all_findings, file_contents)


def _generate_report(findings: List[SecurityFinding], file_contents: Dict[str, str]) -> str:
    """生成 Markdown 格式的安全报告"""

    if not findings:
        return """# 账号安全审计报告

## 审计结果

**扫描状态**: 未发现明显的账号安全漏洞

扫描了以下账号相关文件，未检测到常见安全问题。

扫描的安全类型:
- 撞库风险检测
- MFA/2FA 实现
- Session 安全配置
- 密码存储安全

---

*建议定期进行代码审计，确保账号安全。*
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

    report = f"""# 账号安全审计报告

## 漏洞统计

| 严重程度 | 数量 |
|---------|------|
| CRITICAL | {stats['CRITICAL']} |
| HIGH | {stats['HIGH']} |
| MEDIUM | {stats['MEDIUM']} |
| LOW | {stats['LOW']} |
| **总计** | **{len(findings)}** |

## 漏洞详情

"""

    current_severity = None
    for finding in sorted_findings:
        if finding.severity != current_severity:
            current_severity = finding.severity
            severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}
            report += f"\n### {severity_emoji.get(current_severity, '⚪')} {current_severity} 级别问题\n\n"

        report += f"""#### {finding.category}

**文件**: `{finding.file_path}:{finding.line_number}`

**代码片段**:
```
{finding.code_snippet}
```

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
            f"- [{f.severity}] {f.category}: {f.description} ({f.file_path}:{f.line_number})"
            for f in critical_findings
        ])

        prompt = f"""作为账号安全专家，请对以下账号安全问题进行深度分析：

{context}

请提供:
1. 这些问题被组合利用的攻击场景
2. 用户账号安全的风险评估
3. 优先修复顺序建议
4. 代码修复的关键检查点

请用中文回答，保持简洁专业。
"""
        ai_analysis = ask_ai(prompt)
        report += ai_analysis

    return report


def get_2fa_guide() -> str:
    """
    获取 2FA 配置指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return """
# 多因素认证 (MFA/2FA) 配置指南

## 什么是 MFA/2FA？

多因素认证 (Multi-Factor Authentication) 要求用户提供两种或以上的验证因素：
- **知识因素**: 密码、PIN 码
- **拥有因素**: 手机、硬件密钥
- **生物因素**: 指纹、人脸

## 实现方式对比

| 方式 | 安全性 | 便捷性 | 成本 | 推荐场景 |
|------|--------|--------|------|----------|
| TOTP | 高 | 高 | 免费 | 通用推荐 |
| SMS OTP | 中 | 高 | 低 | 次选方案 |
| 硬件密钥 | 极高 | 中 | 中 | 高安全场景 |
| 推送认证 | 高 | 极高 | 中 | 移动端优先 |

## TOTP 实现教程

### 1. 后端实现 (Python)

使用 pyotp 库实现 TOTP:

1. 生成用户 TOTP 密钥
2. 生成二维码供用户扫描绑定
3. 验证用户输入的 TOTP 代码

### 2. 前端集成

显示绑定二维码，让用户使用 Google Authenticator 或类似 APP 扫描绑定。

### 3. 验证流程

在用户登录或执行敏感操作时，要求输入 TOTP 验证码进行验证。

## 备用码生成

用户丢失 MFA 设备时的恢复方案：

- 生成 10 个一次性备用码
- 用户保存备用码
- 使用备用码时消耗该码

## 推荐实践

### 何时要求 MFA

1. **登录后** - 可选择跳过 MFA (信任设备)
2. **敏感操作前**:
   - 修改密码
   - 绑定/解绑手机
   - 大额转账
   - 删除账户
   - 查看/导出敏感数据

### 安全建议

- [ ] 强制管理员账户启用 MFA
- [ ] 提供多种 MFA 方式供用户选择
- [ ] 生成并提示保存备用码
- [ ] 记录 MFA 相关操作日志
- [ ] 新设备登录时触发 MFA
- [ ] MFA 失败次数限制

### 常见问题

**Q: 用户丢失 MFA 设备怎么办？**
A: 提供备用码功能，或通过邮箱/手机验证身份后重置 MFA。

**Q: TOTP 时间同步问题？**
A: 使用 valid_window 参数允许前后 1-2 个时间窗口 (30秒/窗口)。

**Q: 如何防止 MFA 疲劳攻击？**
A: 限制推送频率，添加位置/设备信息确认。
"""


def get_account_guide() -> str:
    """
    获取账号安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return ACCOUNT_SECURITY_GUIDE


# Alias for CLI compatibility
audit_account_security = check_account_security


if __name__ == "__main__":
    # 测试密码强度检测
    test_passwords = [
        "password123",
        "P@ssw0rd!",
        "MyS3cur3P@ssword!2024",
        "123456",
        "qwertyuiop",
    ]

    print("=" * 50)
    print("密码强度检测测试")
    print("=" * 50)

    for pwd in test_passwords:
        result = check_password_strength(pwd)
        print(f"\n密码: {result['password']}")
        print(f"强度: {result['level']} ({result['score']}/100)")
        print(f"警告: {result['warnings']}")
        print(f"建议: {result['suggestions']}")

    # 测试撞库风险检测
    test_code = '''
    def login(request):
        email = request.body['email']
        password = request.body['password']
        user = authenticate(email, password)
        if user:
            return {"token": generate_token(user)}
        return {"error": "Invalid credentials"}
    '''

    print("\n" + "=" * 50)
    print("撞库风险检测测试")
    print("=" * 50)

    findings = detect_credential_stuffing_risk(test_code)
    for f in findings:
        print(f"[{f.severity}] {f.category}: {f.description}")
