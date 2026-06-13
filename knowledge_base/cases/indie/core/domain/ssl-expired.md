# SSL证书过期 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: domain（域名安全）
- **严重程度**: high（高）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
SSL证书过期后，用户访问网站时浏览器显示"不安全"警告，用户流失，搜索引擎排名下降，你的损失：流量和信誉。

### 一分钟识别
你的SSL证书是否有以下风险：
- [ ] 证书有效期少于30天
- [ ] 未设置证书到期提醒
- [ ] 使用手动续期而非自动续期
- [ ] 不清楚证书颁发机构和到期日期
→ 勾选≥1项，即需关注此风险

### 一句话防御
**启用自动续期 + 设置多级告警**：使用Let's Encrypt自动续期，并在证书到期前30天、7天设置邮件告警。

### 快速行动清单
1. [ ] 立即行动项：检查所有域名证书有效期（今天可完成，免费）
2. [ ] 短期行动项：配置自动续期（本周可完成，免费）
3. [ ] 长期行动项：设置证书到期监控告警（本周可完成，免费/低成本）

### 推荐工具
- 免费：Let's Encrypt（Certbot）、Caddy（自动HTTPS）
- 低成本：UptimeRobot、Pingdom 监控

### 验证方法
- [ ] 使用 `openssl s_client` 检查证书有效期
- [ ] 配置证书到期自动告警
- [ ] 测试自动续期流程

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品 `mysaas.com` 使用付费SSL证书，某天早上收到用户反馈无法访问网站。检查发现SSL证书已于昨晚过期，浏览器阻止了用户访问。

由于你忘记续期，导致了以下后果：
1. 用户无法登录，投诉电话打爆客服
2. 支付回调失败，订单无法完成
3. 搜索引擎收录的HTTPS链接全部失效
4. 品牌信誉受损，用户质疑安全性

更糟糕的是，续期后搜索引擎需要数周才能恢复收录。

### 攻击路径（简化版）
这不是攻击，而是运维失误：
1. **证书过期**：管理员忘记续期
2. **浏览器拦截**：用户看到安全警告
3. **服务中断**：HTTPS请求被拒绝
4. **连锁反应**：SEO下降、用户流失

### 防御实施（低成本方案）

#### 方案A：Let's Encrypt 自动续期（推荐）

**核心原则**：自动化 + 监控告警。

**工具/服务**：Certbot、Caddy、Traefik

**配置步骤**：

1. **安装 Certbot**：
   ```bash
   # Ubuntu/Debian
   sudo apt install certbot python3-certbot-nginx

   # CentOS/RHEL
   sudo yum install certbot python3-certbot-nginx
   ```

2. **申请证书**：
   ```bash
   # Nginx
   sudo certbot --nginx -d example.com -d www.example.com

   # 独立模式
   sudo certbot certonly --standalone -d example.com
   ```

3. **配置自动续期**：
   ```bash
   # 测试续期（不实际续期）
   sudo certbot renew --dry-run

   # Certbot 会自动添加 cron 任务
   # 查看 cron 任务
   sudo systemctl list-timers | grep certbot
   ```

4. **Nginx 配置**：
   ```nginx
   server {
       listen 443 ssl http2;
       server_name example.com;

       ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

       # 自动续期后重载
       ssl_trusted_certificate /etc/letsencrypt/live/example.com/chain.pem;
   }
   ```

**局限性**：
- 每90天需要续期
- 需要服务器能访问外网

#### 方案B：使用 Caddy 自动HTTPS

**工具/服务**：Caddy Server

**优势**：
- 完全自动化的HTTPS
- 自动申请、续期证书
- 配置简单

**配置步骤**：
```caddyfile
# Caddyfile
example.com {
    reverse_proxy localhost:8080
    # Caddy 自动处理 HTTPS 和证书续期
}
```

**成本**：免费

### 决策树
```
你的服务器是否支持Certbot？
├── 是 → 使用 Let's Encrypt 自动续期（方案A）
└── 否 → 切换到 Caddy/Traefik（方案B）
```

### 代码示例（证书监控）

```python
import ssl
import socket
import smtplib
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class SSLMonitor:
    """SSL证书监控"""

    def __init__(self, domains, alert_days=30, warning_days=7):
        """
        Args:
            domains: 域名列表
            alert_days: 提前告警天数
            warning_days: 紧急告警天数
        """
        self.domains = domains
        self.alert_days = alert_days
        self.warning_days = warning_days

    def check_certificate(self, domain, port=443):
        """检查单个域名的证书状态"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()

                    # 解析到期时间
                    not_after = datetime.strptime(
                        cert['notAfter'],
                        '%b %d %H:%M:%S %Y %Z'
                    )
                    not_before = datetime.strptime(
                        cert['notBefore'],
                        '%b %d %H:%M:%S %Y %Z'
                    )

                    now = datetime.utcnow()
                    days_left = (not_after - now).days

                    # 获取颁发者信息
                    issuer = dict(x[0] for x in cert.get('issuer', []))

                    result = {
                        'domain': domain,
                        'status': 'ok',
                        'issuer': issuer.get('organizationName', 'Unknown'),
                        'not_before': not_before.strftime('%Y-%m-%d'),
                        'not_after': not_after.strftime('%Y-%m-%d'),
                        'days_left': days_left,
                        'is_valid': days_left > 0
                    }

                    # 判断状态
                    if days_left <= 0:
                        result['status'] = 'expired'
                        result['severity'] = 'critical'
                    elif days_left <= self.warning_days:
                        result['status'] = 'warning'
                        result['severity'] = 'high'
                    elif days_left <= self.alert_days:
                        result['status'] = 'alert'
                        result['severity'] = 'medium'

                    return result

        except ssl.SSLError as e:
            return {
                'domain': domain,
                'status': 'ssl_error',
                'severity': 'critical',
                'error': str(e)
            }
        except socket.timeout:
            return {
                'domain': domain,
                'status': 'timeout',
                'severity': 'high',
                'error': 'Connection timeout'
            }
        except Exception as e:
            return {
                'domain': domain,
                'status': 'error',
                'severity': 'medium',
                'error': str(e)
            }

    def check_all(self):
        """检查所有域名"""
        results = []
        for domain in self.domains:
            result = self.check_certificate(domain)
            results.append(result)
            logger.info(f"SSL检查: {domain} - {result['status']}")
        return results

    def get_expiring_soon(self):
        """获取即将过期的证书"""
        results = self.check_all()
        expiring = [
            r for r in results
            if r.get('days_left', 0) <= self.alert_days
        ]
        return sorted(expiring, key=lambda x: x.get('days_left', 0))

    def send_alert_email(self, smtp_config, to_emails, expiring_certs):
        """发送告警邮件"""
        if not expiring_certs:
            return

        # 构建邮件内容
        subject = f"[SSL告警] {len(expiring_certs)} 个证书即将过期"
        body = "以下SSL证书即将过期，请及时处理：\n\n"

        for cert in expiring_certs:
            body += f"""
域名: {cert['domain']}
状态: {cert['status']}
剩余天数: {cert.get('days_left', 'N/A')}
到期日期: {cert.get('not_after', 'N/A')}
颁发机构: {cert.get('issuer', 'N/A')}
---
"""
        # 发送邮件（需要配置SMTP）
        # ...

        logger.info(f"发送SSL告警邮件: {subject}")


# 使用示例
if __name__ == "__main__":
    domains = ['example.com', 'api.example.com', 'admin.example.com']
    monitor = SSLMonitor(domains, alert_days=30, warning_days=7)

    # 检查所有证书
    for result in monitor.check_all():
        print(f"{result['domain']}: {result['status']} ({result.get('days_left', 'N/A')} 天)")

    # 获取即将过期的证书
    expiring = monitor.get_expiring_soon()
    if expiring:
        print("\n即将过期的证书:")
        for cert in expiring:
            print(f"  - {cert['domain']}: {cert['days_left']} 天")
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **证书管理**：
   - 使用证书管理平台（Venafi、DigiCert）
   - 统一管理所有证书
   - 自动化证书生命周期

2. **监控告警**：
   - 实时证书状态监控
   - 多渠道告警（邮件、短信、IM）
   - 告警升级机制

3. **应急响应**：
   - 证书过期应急预案
   - 快速续期流程
   - 临时证书方案

4. **合规要求**：
   - 证书审计日志
   - 定期证书盘点
   - 证书策略管理

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级证书管理案例。

---

## 延伸阅读

- [Let's Encrypt 官方文档](https://letsencrypt.org/docs/)
- [Certbot 使用指南](https://certbot.eff.org/)
- [SSL Labs 测试](https://www.ssllabs.com/ssltest/)
- [Mozilla SSL配置指南](https://ssl-config.mozilla.org/)
