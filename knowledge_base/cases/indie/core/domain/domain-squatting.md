# 域名抢注 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: domain（域名安全）
- **严重程度**: medium（中）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的域名忘记续费，被抢注者注册并用于钓鱼或勒索，你被迫花高价赎回，你的损失：品牌损失 + 赎回费用（可能数千美元）。

### 一分钟识别
你的域名是否有以下风险：
- [ ] 域名即将到期但未设置自动续费
- [ ] 未设置域名到期提醒
- [ ] 注册邮箱不常用可能错过通知
- [ ] 域名具有品牌价值
→ 勾选≥1项，即需关注此风险

### 一句话防御
**启用自动续费 + 多渠道提醒**：在注册商启用自动续费，并在日历、邮箱、手机设置多重重提醒。

### 快速行动清单
1. [ ] 立即行动项：检查所有域名到期日期（今天可完成，免费）
2. [ ] 短期行动项：启用自动续费（今天可完成，免费）
3. [ ] 长期行动项：设置多渠道到期提醒（本周可完成，免费）

### 推荐工具
- 免费：Google Calendar、手机日历提醒
- 低成本：DomainWatch、DomainTools

### 验证方法
- [ ] 确认域名已启用自动续费
- [ ] 确认多个日历已设置提醒
- [ ] 测试续费流程

---

## L2 小团队版（理解版）

### 场景还原
你的品牌域名 `myapp.com` 即将到期，但你的注册邮箱设置了自动归档，错过了续费提醒。域名过期后进入赎回期，被抢注者注册。

抢注者联系你，要求支付 $5000 才能赎回域名。你的选择：
1. 支付赎金
2. 更换品牌域名（用户流失）
3. 寻求法律途径（时间长、成本高）

无论哪种选择，都会对你的业务造成严重影响。

### 攻击路径（简化版）
1. **监控域名**：抢注者使用工具监控即将到期的有价值域名
2. **抢注**：域名进入公开注册状态后立即注册
3. **利用**：
   - 建立钓鱼网站
   - 向原所有者勒索
   - 重定向流量到竞争对手

### 防御实施（低成本方案）

#### 方案A：自动续费 + 多重提醒（推荐）

**核心原则**：自动化 + 多重保险。

**工具/服务**：域名注册商 + 日历提醒

**配置步骤**：

1. **启用自动续费**：
   ```
   登录注册商 → 域名设置 → 自动续费 → 启用
   ```

2. **添加日历提醒**：
   - 到期前90天：检查续费状态
   - 到期前30天：确认自动续费有效
   - 到期前7天：紧急提醒
   - 到期前1天：最后检查

3. **多邮箱通知**：
   - 设置备用邮箱接收通知
   - 配置邮件转发

**局限性**：
- 需要确保支付方式有效
- 需要定期检查自动续费状态

#### 方案B：长期注册 + 品牌保护

**工具/服务**：域名注册商

**优势**：
- 减少续费频率
- 降低遗忘风险

**配置步骤**：
```
注册域名时选择多年注册（最多10年）
同时注册相关域名：
- myapp.net
- myapp.org
- myapp.io
- myapp.cn
```

**成本**：一次性支付多年费用

### 决策树
```
域名是否启用自动续费？
├── 否 → 立即启用
└── 是 → 支付方式是否有效？
    ├── 否 → 更新支付方式
    └── 是 → 是否设置了提醒？
        ├── 否 → 设置多渠道提醒
        └── 是 → 当前方案完善
```

### 代码示例（域名到期监控）

```python
import whois
from datetime import datetime, timedelta
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DomainExpiryMonitor:
    """域名到期监控"""

    def __init__(self, domains: List[str], alert_days: int = 90):
        """
        Args:
            domains: 域名列表
            alert_days: 提前告警天数
        """
        self.domains = domains
        self.alert_days = alert_days

    def check_expiry(self, domain: str) -> Dict:
        """检查单个域名到期时间"""
        try:
            w = whois.whois(domain)

            # 获取到期时间
            expiration_date = w.expiration_date
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]

            if not expiration_date:
                return {
                    'domain': domain,
                    'status': 'unknown',
                    'message': '无法获取到期时间'
                }

            # 计算剩余天数
            now = datetime.now()
            days_until_expiry = (expiration_date - now).days

            result = {
                'domain': domain,
                'expiration_date': expiration_date.strftime('%Y-%m-%d'),
                'days_until_expiry': days_until_expiry,
                'auto_renew': None,  # 无法通过WHOIS获取
            }

            # 确定状态
            if days_until_expiry <= 0:
                result['status'] = 'expired'
                result['severity'] = 'critical'
                result['message'] = '域名已过期'
            elif days_until_expiry <= 7:
                result['status'] = 'critical'
                result['severity'] = 'critical'
                result['message'] = f'域名将在{days_until_expiry}天后过期'
            elif days_until_expiry <= 30:
                result['status'] = 'warning'
                result['severity'] = 'high'
                result['message'] = f'域名将在{days_until_expiry}天后过期'
            elif days_until_expiry <= self.alert_days:
                result['status'] = 'alert'
                result['severity'] = 'medium'
                result['message'] = f'域名将在{days_until_expiry}天后过期'
            else:
                result['status'] = 'ok'
                result['severity'] = 'low'
                result['message'] = f'域名状态正常，{days_until_expiry}天后过期'

            return result

        except Exception as e:
            logger.error(f"检查域名失败: {domain} - {e}")
            return {
                'domain': domain,
                'status': 'error',
                'message': str(e)
            }

    def check_all(self) -> List[Dict]:
        """检查所有域名"""
        results = []
        for domain in self.domains:
            result = self.check_expiry(domain)
            results.append(result)
            logger.info(f"域名检查: {domain} - {result['status']}")
        return results

    def get_expiring_soon(self) -> List[Dict]:
        """获取即将到期的域名"""
        results = self.check_all()
        expiring = [
            r for r in results
            if r.get('days_until_expiry', 999) <= self.alert_days
        ]
        return sorted(expiring, key=lambda x: x.get('days_until_expiry', 0))

    def generate_report(self) -> str:
        """生成域名到期报告"""
        results = self.check_all()

        report = "# 域名到期监控报告\n\n"
        report += f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # 按状态分组
        critical = [r for r in results if r.get('severity') == 'critical']
        warning = [r for r in results if r.get('severity') == 'high']
        alert = [r for r in results if r.get('severity') == 'medium']
        ok = [r for r in results if r.get('severity') == 'low']

        if critical:
            report += "## 🚨 紧急\n\n"
            for r in critical:
                report += f"- **{r['domain']}**: {r['message']}\n"
            report += "\n"

        if warning:
            report += "## ⚠️ 警告\n\n"
            for r in warning:
                report += f"- **{r['domain']}**: {r['message']}\n"
            report += "\n"

        if alert:
            report += "## 📢 提醒\n\n"
            for r in alert:
                report += f"- **{r['domain']}**: {r['message']}\n"
            report += "\n"

        report += "## 所有域名状态\n\n"
        report += "| 域名 | 到期日期 | 剩余天数 | 状态 |\n"
        report += "|------|----------|----------|------|\n"
        for r in sorted(results, key=lambda x: x.get('days_until_expiry', 0)):
            report += f"| {r['domain']} | {r.get('expiration_date', 'N/A')} | {r.get('days_until_expiry', 'N/A')} | {r['status']} |\n"

        return report


# 使用示例
if __name__ == "__main__":
    domains = [
        'example.com',
        'example.net',
        'example.org'
    ]

    monitor = DomainExpiryMonitor(domains, alert_days=90)
    report = monitor.generate_report()
    print(report)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **域名管理**：
   - 统一域名管理平台
   - 多年注册策略
   - 自动续费 + 备用支付方式

2. **品牌保护**：
   - 注册防御性域名
   - 商标注册保护
   - 监控相似域名注册

3. **监控告警**：
   - 实时域名状态监控
   - 多渠道告警机制
   - 告警升级流程

4. **应急响应**：
   - 域名抢注应急预案
   - 法律追索准备
   - 媒体沟通预案

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级域名保护案例。

---

## 延伸阅读

- [ICANN 域名生命周期](https://www.icann.org/resources/pages/guide-gtld-life-cycle-2015-08-19-en)
- [域名抢注防护](https://www.icann.org/resources/pages/udrp-2015-03-11-en)
- [域名争议解决政策](https://www.icann.org/resources/pages/dndr-udrp-policy-2015-03-11-en)
