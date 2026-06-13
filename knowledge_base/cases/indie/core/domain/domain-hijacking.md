# 域名劫持 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: domain（域名安全）
- **严重程度**: critical（严重）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过社会工程学或入侵你的注册商账户，将你的域名转移到他们控制之下，你的网站、邮件、所有服务瞬间全部瘫痪，损失：全部业务价值。

### 一分钟识别
你的域名是否有以下风险：
- [ ] 注册商账户未启用双因素认证
- [ ] 域名未启用转移锁（Domain Lock）
- [ ] 注册邮箱密码弱或被复用
- [ ] WHOIS信息暴露了真实联系方式
→ 勾选≥1项，即需关注此风险

### 一句话防御
**启用域名锁 + 双因素认证 + WHOIS隐私保护**：这三项配置可在域名注册商后台免费开启，能阻止99%的域名劫持攻击。

### 快速行动清单
1. [ ] 立即行动项：登录域名注册商，启用双因素认证（今天可完成，免费）
2. [ ] 短期行动项：启用域名转移锁（Domain Lock）（今天可完成，免费）
3. [ ] 长期行动项：启用WHOIS隐私保护（本周可完成，免费）

### 推荐工具
- 免费：Cloudflare、Namecheap、GoDaddy 等注册商均提供免费安全功能
- 低成本：企业级域名保护服务（如 MarkMonitor）

### 验证方法
- [ ] 尝试发起域名转移，确认被拒绝
- [ ] 确认需要二次验证才能修改账户信息
- [ ] 查询WHOIS确认信息已隐藏

---

## L2 小团队版（理解版）

### 场景还原
你经营着一个在线教育平台，域名 `learnx.com` 托管在某知名注册商。某天早上，你发现网站无法访问，DNS解析指向了一个陌生的IP。登录注册商时发现账户密码已被修改。

调查发现：攻击者通过撞库攻击获取了你的注册商账户密码（因为你在其他网站使用了相同密码），然后：
1. 关闭了域名转移锁
2. 发起了域名转移到另一家注册商
3. 修改了DNS解析指向攻击者的服务器
4. 在你的网站上挂了钓鱼页面

你的用户访问网站时被引导到钓鱼页面，输入了账号密码。你的品牌信誉受损，用户流失，业务几乎停摆。

### 攻击路径（简化版）
1. **获取账户访问权**：撞库、钓鱼、社会工程学
2. **关闭安全措施**：关闭转移锁、移除2FA
3. **发起域名转移**：转移到攻击者控制的注册商
4. **修改DNS**：指向攻击者服务器
5. **实施攻击**：钓鱼、流量劫持、数据窃取

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：多层防护 + 监控告警。

**工具/服务**：域名注册商安全功能

**配置步骤**：

1. **启用双因素认证（最重要）**：
   - 登录域名注册商后台
   - 找到"账户安全"或"两步验证"设置
   - 推荐使用 TOTP（如 Google Authenticator）而非短信验证

2. **启用域名转移锁**：
   ```
   Namecheap: Domain List → Manage → Security → Domain Lock
   GoDaddy: 域名设置 → 转移保护 → 启用
   Cloudflare: 自动启用（无法关闭）
   ```

3. **启用WHOIS隐私保护**：
   - 隐藏真实姓名、邮箱、电话、地址
   - 防止社会工程学攻击

4. **配置域名监控**：
   ```python
   # 使用免费监控服务
   # 1. UptimeRobot: 监控网站可用性
   # 2. Google Alerts: 设置域名关键词告警
   # 3. Certificate Transparency: 监控证书颁发
   ```

**局限性**：
- 需要定期检查安全设置
- 监控服务可能有延迟

#### 方案B：企业级域名保护

**工具/服务**：MarkMonitor、CSC、BrandShelter

**优势**：
- 企业级安全防护
- 主动监控和响应
- 品牌保护

**成本**：$500-5000/年

### 决策树
```
你的域名是否启用域名锁？
├── 否 → 立即启用（方案A）
└── 是 → 是否启用双因素认证？
    ├── 否 → 立即启用（方案A）
    └── 是 → 是否启用WHOIS隐私？
        ├── 否 → 启用隐私保护（方案A）
        └── 是 → 当前方案基本完善
```

### 代码示例（监控脚本）

```python
import requests
import whois
import ssl
import socket
import smtplib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DomainMonitor:
    """域名安全监控"""

    def __init__(self, domain, notification_email=None):
        self.domain = domain
        self.notification_email = notification_email

    def check_whois(self):
        """检查WHOIS信息是否泄露"""
        try:
            w = whois.whois(self.domain)

            # 检查是否启用隐私保护
            registrant = str(w.registrant or '').lower()
            admin = str(w.admin or '').lower()

            privacy_keywords = ['privacy', 'protect', 'proxy', 'guard', 'redacted']

            is_protected = any(kw in registrant or kw in admin for kw in privacy_keywords)

            if not is_protected:
                logger.warning(f"WHOIS信息未保护: {self.domain}")
                return {
                    'status': 'warning',
                    'message': 'WHOIS信息可能暴露了真实联系信息',
                    'registrant': w.registrant
                }

            return {
                'status': 'ok',
                'message': 'WHOIS隐私保护已启用'
            }

        except Exception as e:
            logger.error(f"WHOIS查询失败: {e}")
            return {'status': 'error', 'message': str(e)}

    def check_domain_lock(self):
        """检查域名锁状态（需要注册商API）"""
        # 这里需要使用具体注册商的API
        # 示例：Namecheap API
        pass

    def check_dns(self, expected_ip=None):
        """检查DNS解析是否被篡改"""
        try:
            actual_ip = socket.gethostbyname(self.domain)

            if expected_ip and actual_ip != expected_ip:
                logger.critical(f"DNS解析异常: 期望{expected_ip}, 实际{actual_ip}")
                return {
                    'status': 'critical',
                    'message': 'DNS解析可能被篡改',
                    'expected': expected_ip,
                    'actual': actual_ip
                }

            return {
                'status': 'ok',
                'ip': actual_ip
            }

        except socket.gaierror as e:
            logger.critical(f"DNS解析失败: {e}")
            return {'status': 'critical', 'message': '域名无法解析'}

    def check_ssl(self):
        """检查SSL证书"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()

                    # 检查有效期
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_left = (not_after - datetime.utcnow()).days

                    if days_left < 30:
                        logger.warning(f"SSL证书即将过期: {days_left}天")

                    return {
                        'status': 'ok' if days_left > 7 else 'warning',
                        'expiry_date': not_after.strftime('%Y-%m-%d'),
                        'days_left': days_left,
                        'issuer': dict(x[0] for x in cert.get('issuer', [])).get('organizationName', 'Unknown')
                    }

        except Exception as e:
            logger.error(f"SSL检查失败: {e}")
            return {'status': 'error', 'message': str(e)}

    def run_all_checks(self):
        """运行所有检查"""
        results = {
            'domain': self.domain,
            'timestamp': datetime.now().isoformat(),
            'whois': self.check_whois(),
            'dns': self.check_dns(),
            'ssl': self.check_ssl()
        }

        # 检查是否有问题
        issues = []
        for check_name, result in results.items():
            if isinstance(result, dict) and result.get('status') in ['warning', 'critical', 'error']:
                issues.append((check_name, result))

        if issues and self.notification_email:
            self.send_alert(issues)

        return results

    def send_alert(self, issues):
        """发送告警邮件"""
        # 实现邮件告警逻辑
        pass


# 使用示例
if __name__ == "__main__":
    monitor = DomainMonitor("example.com", notification_email="admin@example.com")
    results = monitor.run_all_checks()
    print(results)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **注册商安全**：
   - 选择企业级注册商（MarkMonitor、CSC）
   - 启用企业级双因素认证
   - 域名锁定服务
   - 账户活动审计日志

2. **域名监控**：
   - 实时DNS监控
   - WHOIS变更监控
   - 证书透明度监控
   - 品牌域名监控

3. **应急响应**：
   - 域名劫持应急预案
   - 注册商联系渠道
   - 法律追索准备

4. **品牌保护**：
   - 注册防御性域名
   - 各TLD品牌保护
   - 商标注册

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级域名安全案例。

---

## 延伸阅读

- [ICANN 域名转移政策](https://www.icann.org/resources/pages/transfer-policy-2016-06-01-en)
- [域名劫持防御指南](https://www.icann.org/en/system/files/files/sac-040-en.pdf)
- [OWASP 域名安全](https://cheatsheetseries.owasp.org/cheatsheets/Virtual_Patching_Cheat_Sheet.html)
