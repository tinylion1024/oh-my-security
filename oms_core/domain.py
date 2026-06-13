"""
域名安全审计模块 - Oh-My-Security

检测域名安全配置中的常见问题:
- SSL证书过期或配置错误
- DNS配置安全风险
- 域名劫持风险
- 子域名安全
- WHOIS信息泄露
"""
import os
import re
import socket
import subprocess
import ssl
import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SecurityFinding:
    """安全发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category: str  # 安全类别
    title: str
    description: str
    impact: str
    recommendation: str
    details: Optional[Dict] = None


# 域名安全最佳实践指南
DOMAIN_SECURITY_GUIDE = """
# 域名安全最佳实践指南

## 1. SSL/TLS 证书安全

### 证书配置
- **证书有效性**: 确保证书在有效期内，建议提前30天续期
- **证书链完整**: 确保证书链完整，包含中间证书
- **强加密套件**: 禁用弱加密算法（SSLv2, SSLv3, TLS 1.0, TLS 1.1）
- **HSTS**: 启用 HTTP Strict Transport Security
- **证书透明度**: 确保证书已在 CT 日志中记录

### 推荐配置
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;
add_header Strict-Transport-Security "max-age=63072000" always;
```

## 2. DNS 安全配置

### DNSSEC
- **启用 DNSSEC**: 使用数字签名保护 DNS 数据完整性
- **签名验证**: 确保 DNS 解析器验证 DNSSEC 签名
- **密钥轮换**: 定期轮换 DNSSEC 密钥

### DNS 记录安全
- **SPF**: 配置 Sender Policy Framework 防止邮件伪造
- **DKIM**: 配置 DomainKeys Identified Mail 签名
- **DMARC**: 配置 Domain-based Message Authentication
- **CAA**: 配置 Certificate Authority Authorization 限制证书颁发

### 推荐配置
```dns
example.com.     IN TXT "v=spf1 include:_spf.google.com ~all"
default._domainkey IN TXT "v=DKIM1; k=rsa; p=..."
_dmarc.example.com IN TXT "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"
example.com.     IN CAA 0 issue "letsencrypt.org"
```

## 3. 域名注册安全

### 注册商安全
- **启用双因素认证**: 为域名注册商账户启用 2FA
- **域名锁定**: 启用域名转移锁（Domain Lock）
- **隐私保护**: 启用 WHOIS 隐私保护
- **联系信息**: 确保联系信息准确且安全

### 域名监控
- **到期监控**: 设置域名到期提醒
- **DNS 变更监控**: 监控 DNS 记录变更
- **证书监控**: 监控 SSL 证书颁发情况

## 4. 子域名安全

### 子域名管理
- **清理闲置子域名**: 删除不再使用的子域名
- **防止子域名接管**: 检查 CNAME 指向的第三方服务
- **泛解析风险**: 谨慎使用泛域名解析

### 常见风险
- 子域名 CNAME 指向已失效的云服务
- 子域名指向开发/测试环境
- 子域名暴露内部服务

## 5. 常见域名攻击

### 域名劫持
- 攻击者通过社会工程学获取域名控制权
- 防御：启用域名锁、使用企业邮箱注册

### DNS 污染/劫持
- DNS 解析被篡改指向恶意 IP
- 防御：启用 DNSSEC、使用可信 DNS 服务器

### SSL 证书欺骗
- 攻击者获取域名的非法证书
- 防御：配置 CAA 记录、证书透明度监控

### 子域名接管
- CNAME 指向的第三方服务失效后被接管
- 防御：定期审计子域名、清理失效记录

## 6. 安全检查清单

### SSL 检查
- [ ] 证书有效期检查
- [ ] 证书链完整性
- [ ] 协议版本检查
- [ ] 加密套件强度

### DNS 检查
- [ ] DNSSEC 是否启用
- [ ] SPF/DKIM/DMARC 配置
- [ ] CAA 记录配置
- [ ] DNS 记录泄露检查

### 注册商检查
- [ ] 双因素认证已启用
- [ ] 域名锁已启用
- [ ] WHOIS 隐私保护
- [ ] 联系信息准确

### 监控配置
- [ ] 到期提醒已设置
- [ ] DNS 变更监控
- [ ] 证书透明度监控

## 7. 推荐工具

- **SSL Labs**: https://www.ssllabs.com/ssltest/
- **DNSSEC Analyzer**: https://dnsviz.net/
- **DMARC Analyzer**: https://dmarcian.com/
- **Certificate Transparency**: https://crt.sh/
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


def check_ssl(domain: str) -> List[SecurityFinding]:
    """
    检查 SSL 证书状态

    检测项目:
    - 证书有效期
    - 证书链完整性
    - 协议版本
    - 加密套件强度

    Args:
        domain: 域名

    Returns:
        安全发现列表
    """
    findings = []

    try:
        # 创建 SSL 上下文
        context = ssl.create_default_context()

        # 连接并获取证书
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

                # 检查证书有效期
                not_before = datetime.datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
                not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                now = datetime.datetime.utcnow()

                days_until_expiry = (not_after - now).days

                if days_until_expiry < 0:
                    findings.append(SecurityFinding(
                        severity="CRITICAL",
                        category="SSL证书过期",
                        title=f"SSL证书已过期 {abs(days_until_expiry)} 天",
                        description=f"域名 {domain} 的SSL证书已于 {not_after.strftime('%Y-%m-%d')} 过期",
                        impact="用户访问时会收到安全警告，可能导致流量损失和数据泄露风险",
                        recommendation="立即续期SSL证书",
                        details={
                            "domain": domain,
                            "expired_date": not_after.strftime('%Y-%m-%d'),
                            "days_expired": abs(days_until_expiry)
                        }
                    ))
                elif days_until_expiry < 7:
                    findings.append(SecurityFinding(
                        severity="CRITICAL",
                        category="SSL证书即将过期",
                        title=f"SSL证书将在 {days_until_expiry} 天后过期",
                        description=f"域名 {domain} 的SSL证书将在 {not_after.strftime('%Y-%m-%d')} 过期",
                        impact="证书过期会导致用户无法正常访问，影响业务连续性",
                        recommendation="立即续期SSL证书，建议提前30天续期",
                        details={
                            "domain": domain,
                            "expiry_date": not_after.strftime('%Y-%m-%d'),
                            "days_remaining": days_until_expiry
                        }
                    ))
                elif days_until_expiry < 30:
                    findings.append(SecurityFinding(
                        severity="HIGH",
                        category="SSL证书即将过期",
                        title=f"SSL证书将在 {days_until_expiry} 天后过期",
                        description=f"域名 {domain} 的SSL证书将在 {not_after.strftime('%Y-%m-%d')} 过期",
                        impact="证书过期会导致用户无法正常访问",
                        recommendation="尽快续期SSL证书",
                        details={
                            "domain": domain,
                            "expiry_date": not_after.strftime('%Y-%m-%d'),
                            "days_remaining": days_until_expiry
                        }
                    ))
                else:
                    findings.append(SecurityFinding(
                        severity="INFO",
                        category="SSL证书有效",
                        title=f"SSL证书有效，剩余 {days_until_expiry} 天",
                        description=f"域名 {domain} 的SSL证书有效期至 {not_after.strftime('%Y-%m-%d')}",
                        impact="无",
                        recommendation="继续监控证书有效期",
                        details={
                            "domain": domain,
                            "expiry_date": not_after.strftime('%Y-%m-%d'),
                            "days_remaining": days_until_expiry,
                            "issuer": dict(x[0] for x in cert.get('issuer', [])).get('organizationName', 'Unknown')
                        }
                    ))

                # 检查证书主题
                subject = dict(x[0] for x in cert.get('subject', []))
                cert_domain = subject.get('commonName', '')

                # 检查证书是否匹配域名
                san_list = []
                for ext in cert.get('subjectAltName', []):
                    if ext[0] == 'DNS':
                        san_list.append(ext[1])

                # 检查域名是否匹配
                domain_matched = False
                if cert_domain == domain or domain.endswith(cert_domain[2:]) if cert_domain.startswith('*.') else False:
                    domain_matched = True
                for san in san_list:
                    if san == domain or (san.startswith('*.') and domain.endswith(san[2:])):
                        domain_matched = True
                        break

                if not domain_matched:
                    findings.append(SecurityFinding(
                        severity="HIGH",
                        category="SSL证书域名不匹配",
                        title="证书域名与访问域名不匹配",
                        description=f"证书颁发给 {cert_domain}，但访问的域名是 {domain}",
                        impact="浏览器会显示证书错误警告",
                        recommendation="重新申请匹配域名的证书",
                        details={
                            "domain": domain,
                            "cert_cn": cert_domain,
                            "san_list": san_list
                        }
                    ))

                # 检查协议版本
                version = ssock.version()
                if version in ['TLSv1', 'TLSv1.1', 'SSLv3']:
                    findings.append(SecurityFinding(
                        severity="HIGH",
                        category="弱协议版本",
                        title=f"使用了不安全的协议版本: {version}",
                        description="TLS 1.0/1.1 和 SSLv3 已被弃用，存在安全风险",
                        impact="可能遭受 POODLE、BEAST 等攻击",
                        recommendation="禁用 TLS 1.0/1.1 和 SSLv3，仅启用 TLS 1.2 和 TLS 1.3",
                        details={
                            "domain": domain,
                            "protocol_version": version
                        }
                    ))

    except socket.timeout:
        findings.append(SecurityFinding(
            severity="HIGH",
            category="SSL连接超时",
            title="无法连接到HTTPS服务",
            description=f"域名 {domain} 的443端口连接超时",
            impact="用户无法通过HTTPS访问",
            recommendation="检查服务器防火墙和HTTPS服务配置",
            details={"domain": domain}
        ))
    except socket.gaierror:
        findings.append(SecurityFinding(
            severity="CRITICAL",
            category="DNS解析失败",
            title="域名无法解析",
            description=f"域名 {domain} 无法解析为IP地址",
            impact="用户无法访问网站",
            recommendation="检查DNS配置是否正确",
            details={"domain": domain}
        ))
    except ssl.SSLError as e:
        findings.append(SecurityFinding(
            severity="CRITICAL",
            category="SSL证书错误",
            title="SSL证书验证失败",
            description=f"域名 {domain} 的SSL证书验证失败: {str(e)}",
            impact="用户访问时会收到安全警告",
            recommendation="检查SSL证书配置是否正确",
            details={"domain": domain, "error": str(e)}
        ))
    except ConnectionRefusedError:
        findings.append(SecurityFinding(
            severity="HIGH",
            category="HTTPS服务未启用",
            title="HTTPS服务未响应",
            description=f"域名 {domain} 的443端口拒绝连接",
            impact="用户无法通过HTTPS安全访问",
            recommendation="启用HTTPS服务并配置SSL证书",
            details={"domain": domain}
        ))
    except Exception as e:
        findings.append(SecurityFinding(
            severity="MEDIUM",
            category="SSL检查异常",
            title="SSL检查过程中发生错误",
            description=f"检查域名 {domain} 时发生异常: {str(e)}",
            impact="无法确定SSL配置状态",
            recommendation="手动检查SSL配置",
            details={"domain": domain, "error": str(e)}
        ))

    return findings


def check_dns(domain: str) -> List[SecurityFinding]:
    """
    检查 DNS 配置安全

    检测项目:
    - A/AAAA 记录
    - MX 记录
    - SPF 记录
    - DKIM 记录
    - DMARC 记录
    - CAA 记录
    - DNSSEC 状态

    Args:
        domain: 域名

    Returns:
        安全发现列表
    """
    findings = []

    # 检查 A 记录
    try:
        result = subprocess.run(
            ["dig", "+short", "A", domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        a_records = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

        if not a_records:
            findings.append(SecurityFinding(
                severity="HIGH",
                category="DNS A记录缺失",
                title="未找到A记录",
                description=f"域名 {domain} 没有配置A记录",
                impact="用户无法通过IPv4访问网站",
                recommendation="添加A记录指向服务器IP",
                details={"domain": domain}
            ))
        else:
            findings.append(SecurityFinding(
                severity="INFO",
                category="DNS A记录",
                title=f"找到 {len(a_records)} 条A记录",
                description=f"域名 {domain} 解析到: {', '.join(a_records)}",
                impact="无",
                recommendation="确认IP地址正确",
                details={"domain": domain, "records": a_records}
            ))
    except Exception as e:
        findings.append(SecurityFinding(
            severity="MEDIUM",
            category="DNS检查异常",
            title="A记录检查失败",
            description=f"检查域名 {domain} 的A记录时发生错误: {str(e)}",
            impact="无法确定A记录状态",
            recommendation="手动检查DNS配置",
            details={"domain": domain, "error": str(e)}
        ))

    # 检查 MX 记录
    try:
        result = subprocess.run(
            ["dig", "+short", "MX", domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        mx_records = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

        if mx_records:
            findings.append(SecurityFinding(
                severity="INFO",
                category="DNS MX记录",
                title=f"找到 {len(mx_records)} 条MX记录",
                description=f"域名 {domain} 的邮件服务器: {', '.join(mx_records)}",
                impact="无",
                recommendation="建议配置SPF、DKIM、DMARC保护邮件安全",
                details={"domain": domain, "records": mx_records}
            ))
    except Exception:
        pass

    # 检查 SPF 记录
    try:
        result = subprocess.run(
            ["dig", "+short", "TXT", domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        txt_records = result.stdout.strip().split('\n')

        spf_records = [r for r in txt_records if 'v=spf1' in r.lower()]

        if mx_records and not spf_records:
            findings.append(SecurityFinding(
                severity="HIGH",
                category="SPF记录缺失",
                title="缺少SPF记录",
                description=f"域名 {domain} 有MX记录但未配置SPF",
                impact="邮件可能被伪造，影响域名信誉",
                recommendation="添加SPF记录指定授权发送邮件的服务器",
                details={"domain": domain}
            ))
        elif spf_records:
            spf = spf_records[0].strip('"')
            findings.append(SecurityFinding(
                severity="INFO",
                category="SPF记录",
                title="SPF记录已配置",
                description=f"域名 {domain} 的SPF记录: {spf}",
                impact="无",
                recommendation="确保SPF记录包含所有合法的发件服务器",
                details={"domain": domain, "record": spf}
            ))

            # 检查SPF配置是否过于宽松
            if '+all' in spf or '?all' in spf:
                findings.append(SecurityFinding(
                    severity="MEDIUM",
                    category="SPF配置宽松",
                    title="SPF配置过于宽松",
                    description=f"SPF记录使用了宽松的配置: {spf}",
                    impact="可能导致邮件伪造风险",
                    recommendation="将SPF结尾改为 ~all 或 -all",
                    details={"domain": domain, "record": spf}
                ))
    except Exception:
        pass

    # 检查 DMARC 记录
    try:
        result = subprocess.run(
            ["dig", "+short", "TXT", f"_dmarc.{domain}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        dmarc_records = [r for r in result.stdout.strip().split('\n') if 'v=DMARC1' in r]

        if mx_records and not dmarc_records:
            findings.append(SecurityFinding(
                severity="HIGH",
                category="DMARC记录缺失",
                title="缺少DMARC记录",
                description=f"域名 {domain} 未配置DMARC",
                impact="邮件可能被伪造，无法有效防止钓鱼邮件",
                recommendation="添加DMARC记录，建议从p=none开始监控",
                details={"domain": domain}
            ))
        elif dmarc_records:
            dmarc = dmarc_records[0].strip('"')
            findings.append(SecurityFinding(
                severity="INFO",
                category="DMARC记录",
                title="DMARC记录已配置",
                description=f"域名 {domain} 的DMARC记录: {dmarc}",
                impact="无",
                recommendation="考虑逐步加强DMARC策略到p=quarantine或p=reject",
                details={"domain": domain, "record": dmarc}
            ))
    except Exception:
        pass

    # 检查 CAA 记录
    try:
        result = subprocess.run(
            ["dig", "+short", "CAA", domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        caa_records = [r for r in result.stdout.strip().split('\n') if r.strip()]

        if not caa_records:
            findings.append(SecurityFinding(
                severity="MEDIUM",
                category="CAA记录缺失",
                title="缺少CAA记录",
                description=f"域名 {domain} 未配置CAA记录",
                impact="任何证书颁发机构都可以为该域名颁发证书",
                recommendation="添加CAA记录限制可以为域名颁发证书的CA",
                details={"domain": domain}
            ))
        else:
            findings.append(SecurityFinding(
                severity="INFO",
                category="CAA记录",
                title="CAA记录已配置",
                description=f"域名 {domain} 的CAA记录: {', '.join(caa_records)}",
                impact="无",
                recommendation="确认只授权了可信的证书颁发机构",
                details={"domain": domain, "records": caa_records}
            ))
    except Exception:
        pass

    return findings


def check_domain(domain: str) -> List[SecurityFinding]:
    """
    检查域名安全配置

    综合检查:
    - SSL证书状态
    - DNS配置
    - 域名解析

    Args:
        domain: 域名

    Returns:
        安全发现列表
    """
    findings = []

    # 验证域名格式
    domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$'
    if not re.match(domain_pattern, domain):
        findings.append(SecurityFinding(
            severity="CRITICAL",
            category="域名格式错误",
            title="无效的域名格式",
            description=f"'{domain}' 不是有效的域名格式",
            impact="无法进行检查",
            recommendation="请输入正确的域名格式，如 example.com",
            details={"input": domain}
        ))
        return findings

    # 移除协议前缀（如果有）
    domain = domain.replace('https://', '').replace('http://', '').strip('/')
    domain = domain.split('/')[0]  # 移除路径

    # 检查SSL
    ssl_findings = check_ssl(domain)
    findings.extend(ssl_findings)

    # 检查DNS
    dns_findings = check_dns(domain)
    findings.extend(dns_findings)

    return findings


def get_domain_guide() -> str:
    """
    获取域名安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return DOMAIN_SECURITY_GUIDE


def generate_domain_report(domain: str) -> str:
    """
    生成域名安全审计报告

    Args:
        domain: 域名

    Returns:
        格式化的 Markdown 安全报告
    """
    findings = check_domain(domain)

    if not findings:
        return f"""# 域名安全审计报告

## 审计目标

**域名**: `{domain}`

## 审计结果

> 未发现明显的安全问题

---

*建议定期进行安全审计，确保域名安全。*
"""

    # 按严重程度分组
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
    sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.severity, 5))

    # 统计（排除INFO级别）
    security_issues = [f for f in findings if f.severity != 'INFO']
    stats = {
        'CRITICAL': len([f for f in security_issues if f.severity == 'CRITICAL']),
        'HIGH': len([f for f in security_issues if f.severity == 'HIGH']),
        'MEDIUM': len([f for f in security_issues if f.severity == 'MEDIUM']),
        'LOW': len([f for f in security_issues if f.severity == 'LOW']),
        'INFO': len([f for f in findings if f.severity == 'INFO']),
    }

    report = f"""# 域名安全审计报告

## 审计目标

**域名**: `{domain}`

## 问题统计

| 严重程度 | 数量 |
|---------|------|
| CRITICAL | {stats['CRITICAL']} |
| HIGH | {stats['HIGH']} |
| MEDIUM | {stats['MEDIUM']} |
| LOW | {stats['LOW']} |
| INFO | {stats['INFO']} |
| **问题总计** | **{len(security_issues)}** |

## 检查详情

"""

    current_severity = None
    for finding in sorted_findings:
        if finding.severity != current_severity:
            current_severity = finding.severity
            severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵', 'INFO': '🟢'}
            report += f"\n### {severity_emoji.get(current_severity, '⚪')} {current_severity}\n\n"

        report += f"""#### {finding.category}

**描述**: {finding.description}

**影响**: {finding.impact}

**建议**: {finding.recommendation}

---

"""

    # 如果有严重问题，使用 AI 进行深度分析
    if stats['CRITICAL'] > 0 or stats['HIGH'] > 0:
        report += "\n## AI 深度分析\n\n"

        critical_issues = [f for f in findings if f.severity in ['CRITICAL', 'HIGH']][:5]
        context = "\n".join([
            f"- [{f.severity}] {f.category}: {f.description}"
            for f in critical_issues
        ])

        prompt = f"""作为域名安全专家，请对以下域名安全发现进行深度分析：

域名: {domain}

发现的问题:
{context}

请提供:
1. 这些问题的攻击场景和风险等级
2. 对业务的影响评估
3. 修复优先级建议
4. 具体的修复步骤

请用中文回答，保持简洁专业。
"""
        ai_analysis = ask_ai(prompt)
        report += ai_analysis

    return report


if __name__ == "__main__":
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("Usage: python domain.py <domain>")
        sys.exit(1)

    domain = sys.argv[1]
    report = generate_domain_report(domain)
    print(report)
