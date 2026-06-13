# WHOIS信息泄露 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: domain（域名安全）
- **严重程度**: medium（中）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的真实姓名、手机号、家庭地址在WHOIS查询中公开可见，攻击者利用这些信息进行社会工程学攻击、身份盗窃或骚扰。

### 一分钟识别
你的域名WHOIS信息是否暴露：
- [ ] 查询WHOIS显示真实姓名
- [ ] 查询WHOIS显示真实手机号
- [ ] 查询WHOIS显示真实地址
- [ ] 查询WHOIS显示个人邮箱
→ 勾选≥1项，即需关注此风险

### 一句话防御
**启用WHOIS隐私保护**：大多数域名注册商提供免费的WHOIS隐私保护服务，一键启用即可隐藏真实信息。

### 快速行动清单
1. [ ] 立即行动项：查询自己域名的WHOIS信息（今天可完成，免费）
2. [ ] 短期行动项：启用WHOIS隐私保护（今天可完成，免费）
3. [ ] 长期行动项：检查历史WHOIS记录（本周可完成，免费）

### 推荐工具
- 免费：注册商自带的WHOIS隐私保护
- 低成本：Domains by Proxy、PrivacyGuard

### 验证方法
- [ ] 使用 whois 命令查询域名
- [ ] 使用在线WHOIS查询工具
- [ ] 确认显示的是代理信息而非真实信息

---

## L2 小团队版（理解版）

### 场景还原
你用真实身份注册了一个域名，因为忘记启用WHOIS隐私保护，任何人都可以通过 `whois example.com` 查到你的：
- 真实姓名
- 手机号码
- 家庭住址
- 电子邮箱

攻击者利用这些信息：
1. **社会工程学攻击**：伪装成注册商客服打电话骗取账户密码
2. **身份盗窃**：收集你的个人信息用于其他欺诈活动
3. **骚扰威胁**：直接联系你进行勒索或骚扰
4. **物理安全风险**：知道你的家庭住址

更糟糕的是，即使现在启用隐私保护，历史WHOIS记录仍然可以在第三方网站（如 DomainTools）上查到。

### 攻击路径（简化版）
1. **信息收集**：攻击者查询你的域名WHOIS
2. **建立档案**：结合其他公开信息建立你的个人档案
3. **社会工程学**：利用信息伪装身份接近你
4. **实施攻击**：钓鱼、诈骗、勒索

### 防御实施（低成本方案）

#### 方案A：启用WHOIS隐私保护（推荐）

**核心原则**：隐藏真实信息 + 使用代理服务。

**工具/服务**：域名注册商隐私保护

**配置步骤**：

1. **Namecheap 启用 WHOIS Guard**：
   ```
   Dashboard → Domain List → Manage → WHOIS Guard → Enable
   ```

2. **GoDaddy 启用 Privacy Protection**：
   ```
   域名设置 → 隐私保护 → 启用
   ```

3. **Cloudflare**：
   Cloudflare Registrar 自动启用WHOIS隐私保护，无需额外配置。

**局限性**：
- 部分域名后缀（如 .us, .cn）不支持隐私保护
- 历史WHOIS记录可能已被第三方存档

#### 方案B：使用代理注册服务

**工具/服务**：Domains by Proxy、NW Technologies

**优势**：
- 完全隐藏真实信息
- 代理接收法律文书

**成本**：$5-20/年

### 决策树
```
你的注册商是否支持WHOIS隐私保护？
├── 是 → 立即启用（方案A）
└── 否 →
    ├── 域名后缀支持隐私保护？→ 切换到支持的注册商
    └── 域名后缀不支持？→ 使用代理注册服务（方案B）
```

### 代码示例（WHOIS检查）

```python
import whois
import re
import logging

logger = logging.getLogger(__name__)

def check_whois_privacy(domain: str) -> dict:
    """
    检查WHOIS隐私保护状态

    Args:
        domain: 域名

    Returns:
        检查结果
    """
    try:
        w = whois.whois(domain)

        # 隐私保护关键词
        privacy_keywords = [
            'privacy', 'protect', 'proxy', 'guard',
            'redacted', 'withheld', 'domains by proxy',
            'whoisguard', 'privacy protect'
        ]

        # 检查registrant信息
        registrant = str(w.registrant or '').lower()
        admin = str(w.admin or '').lower()
        tech = str(w.tech or '').lower()
        email = str(w.emails or '').lower() if w.emails else ''

        # 判断是否启用隐私保护
        is_protected = False
        protection_service = None

        for keyword in privacy_keywords:
            if keyword in registrant or keyword in admin or keyword in tech:
                is_protected = True
                protection_service = keyword
                break

        # 检查是否暴露真实邮箱
        real_email_patterns = [
            r'gmail\.com',
            r'yahoo\.com',
            r'hotmail\.com',
            r'outlook\.com',
            r'qq\.com',
            r'163\.com'
        ]

        exposed_personal_email = False
        for pattern in real_email_patterns:
            if re.search(pattern, email):
                exposed_personal_email = True
                break

        result = {
            'domain': domain,
            'is_protected': is_protected,
            'protection_service': protection_service,
            'exposed_personal_email': exposed_personal_email,
            'raw_data': {
                'registrant': w.registrant,
                'admin': w.admin,
                'emails': w.emails
            }
        }

        # 风险评估
        if not is_protected or exposed_personal_email:
            result['risk_level'] = 'high'
            result['recommendation'] = '建议立即启用WHOIS隐私保护'
        else:
            result['risk_level'] = 'low'
            result['recommendation'] = '隐私保护已启用'

        return result

    except Exception as e:
        logger.error(f"WHOIS查询失败: {domain} - {e}")
        return {
            'domain': domain,
            'error': str(e),
            'risk_level': 'unknown'
        }


def batch_check_whois(domains: list) -> list:
    """
    批量检查域名WHOIS隐私状态

    Args:
        domains: 域名列表

    Returns:
        检查结果列表
    """
    results = []
    for domain in domains:
        result = check_whois_privacy(domain)
        results.append(result)
        logger.info(f"WHOIS检查: {domain} - 保护状态: {result.get('is_protected', False)}")
    return results


# 使用示例
if __name__ == "__main__":
    # 单个域名检查
    result = check_whois_privacy("example.com")
    print(f"隐私保护: {result.get('is_protected', False)}")
    print(f"风险等级: {result.get('risk_level', 'unknown')}")

    # 批量检查
    domains = ['example.com', 'google.com', 'github.com']
    for r in batch_check_whois(domains):
        print(f"{r['domain']}: {r.get('risk_level', 'unknown')}")
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **注册策略**：
   - 使用企业邮箱注册域名
   - 使用公司地址而非个人地址
   - 建立域名注册规范

2. **隐私保护**：
   - 所有域名启用WHOIS隐私保护
   - 使用企业级代理服务
   - 定期审核WHOIS信息

3. **历史记录清理**：
   - 监控第三方WHOIS存档网站
   - 申请删除敏感信息
   - 使用数据删除服务

4. **员工培训**：
   - 域名注册安全培训
   - 社会工程学防范培训
   - 定期安全意识教育

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级域名安全案例。

---

## 延伸阅读

- [ICANN WHOIS政策](https://www.icann.org/resources/pages/whois)
- [GDPR对WHOIS的影响](https://www.icann.org/resources/pages/gdpr-faqs)
- [WHOIS隐私保护服务比较](https://www.namecheap.com/security/whoisguard/)
