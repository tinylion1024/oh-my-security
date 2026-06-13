# 子域名接管 - 独立开发者版

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
你废弃的子域名（如 `blog.example.com`）CNAME指向GitHub Pages等第三方服务，但服务已注销，攻击者注册该服务并绑定你的子域名，你的域名被用来托管恶意内容。

### 一分钟识别
你的域名是否有以下风险：
- [ ] 存在指向第三方服务的CNAME记录
- [ ] 第三方服务账号已注销但CNAME未删除
- [ ] 未定期审计子域名使用情况
- [ ] 使用泛域名解析
→ 勾选≥1项，即需关注此风险

### 一句话防御
**定期审计子域名 + 及时清理失效CNAME**：定期检查所有子域名，确保指向的服务仍然有效且在你的控制之下。

### 快速行动清单
1. [ ] 立即行动项：列出所有子域名和CNAME记录（今天可完成，免费）
2. [ ] 短期行动项：验证每个CNAME指向的服务是否有效（本周可完成，免费）
3. [ ] 长期行动项：建立子域名变更管理流程（规划中，免费）

### 推荐工具
- 免费：Sublist3r、Amass（子域名枚举）
- 低成本：SecurityTrails、Shodan

### 验证方法
- [ ] 使用 dig 检查所有子域名的CNAME
- [ ] 访问每个子域名确认服务正常
- [ ] 使用子域名扫描工具发现遗忘的子域名

---

## L2 小团队版（理解版）

### 场景还原
你之前使用GitHub Pages托管博客，配置了CNAME：`blog.example.com` → `yourname.github.io`。后来你关闭了GitHub Pages仓库，但忘记删除DNS中的CNAME记录。

攻击者发现这个CNAME记录，注册了一个名为 `yourname.github.io` 的GitHub仓库，启用了GitHub Pages，绑定了 `blog.example.com`。现在：
1. `blog.example.com` 解析到攻击者控制的GitHub Pages
2. 攻击者在你的子域名上托管钓鱼页面
3. 用户访问 `blog.example.com` 看到的是攻击者的内容
4. 由于是你的域名，用户信任并可能泄露敏感信息

### 攻击路径（简化版）
1. **发现目标**：攻击者扫描发现你的子域名CNAME
2. **识别服务**：发现指向已失效的第三方服务
3. **接管服务**：在第三方服务注册/绑定该域名
4. **托管恶意内容**：钓鱼页面、恶意软件等

### 常见可接管服务

| 服务 | CNAME示例 | 接管条件 |
|------|-----------|----------|
| GitHub Pages | *.github.io | 仓库已删除 |
| Heroku | *.herokuapp.com | App已删除 |
| AWS S3 | *.s3.amazonaws.com | Bucket已删除 |
| Azure | *.azurewebsites.net | App已删除 |
| Shopify | *.myshopify.com | 商店已关闭 |
| Tumblr | *.tumblr.com | 博客已删除 |
| Zendesk | *.zendesk.com | 账户已关闭 |
| Desk | *.desk.com | 账户已关闭 |

### 防御实施（低成本方案）

#### 方案A：定期审计 + 及时清理（推荐）

**核心原则**：定期审计 + 变更管理。

**工具/服务**：Sublist3r、Amass、dig

**配置步骤**：

1. **枚举所有子域名**：
   ```bash
   # 使用 Sublist3r
   python sublist3r.py -d example.com -o subdomains.txt

   # 使用 Amass
   amass enum -d example.com -o subdomains.txt
   ```

2. **检查CNAME记录**：
   ```bash
   # 批量检查CNAME
   for sub in $(cat subdomains.txt); do
       cname=$(dig +short CNAME $sub)
       if [ -n "$cname" ]; then
           echo "$sub -> $cname"
       fi
   done
   ```

3. **验证服务可用性**：
   ```python
   import requests
   import dns.resolver

   def check_subdomain_takeover(subdomain):
       """检查子域名是否存在接管风险"""
       try:
           # 获取CNAME
           answers = dns.resolver.resolve(subdomain, 'CNAME')
           cname = str(answers[0])

           # 检查服务是否可用
           try:
               response = requests.get(f'http://{subdomain}', timeout=10)
               return {
                   'subdomain': subdomain,
                   'cname': cname,
                   'status': 'ok',
                   'http_status': response.status_code
               }
           except requests.exceptions.ConnectionError:
               # 服务不可达，可能存在接管风险
               return {
                   'subdomain': subdomain,
                   'cname': cname,
                   'status': 'vulnerable',
                   'risk': 'HIGH - 服务不可达，可能存在子域名接管风险'
               }
       except dns.resolver.NoAnswer:
           return {'subdomain': subdomain, 'status': 'no_cname'}
       except Exception as e:
           return {'subdomain': subdomain, 'error': str(e)}
   ```

**局限性**：
- 需要定期执行
- 新增子域名可能被遗漏

#### 方案B：监控告警

**工具/服务**：云监控服务

**配置步骤**：
```python
# 定期执行子域名审计并告警
import smtplib
from datetime import datetime

def audit_and_alert():
    # 1. 枚举子域名
    subdomains = enumerate_subdomains('example.com')

    # 2. 检查接管风险
    vulnerable = []
    for sub in subdomains:
        result = check_subdomain_takeover(sub)
        if result.get('status') == 'vulnerable':
            vulnerable.append(result)

    # 3. 发送告警
    if vulnerable:
        send_alert(vulnerable)
```

### 决策树
```
子域名是否有CNAME记录？
├── 是 → 第三方服务是否仍活跃？
│   ├── 是 → 服务是否在你的控制下？
│   │   ├── 是 → 无风险
│   │   └── 否 → 存在接管风险，立即删除CNAME
│   └── 否 → 存在接管风险，立即删除CNAME
└── 否 → 检查A记录
```

### 代码示例（完整审计工具）

```python
import dns.resolver
import requests
import subprocess
import logging
from typing import List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SubdomainCheck:
    subdomain: str
    cname: str
    status: str
    risk_level: str
    recommendation: str

# 已知的可接管服务指纹
TAKEOVER_FINGERPRINTS = {
    'github.io': 'GitHub Pages',
    'herokuapp.com': 'Heroku',
    'azurewebsites.net': 'Azure',
    's3.amazonaws.com': 'AWS S3',
    'cloudfront.net': 'CloudFront',
    'myshopify.com': 'Shopify',
    'tumblr.com': 'Tumblr',
    'zendesk.com': 'Zendesk',
    'desk.com': 'Desk',
    'helpscoutdocs.com': 'HelpScout',
    'teamwork.com': 'Teamwork',
    'fastly.net': 'Fastly',
}

# 服务不可达的响应特征
VULNERABLE_RESPONSES = [
    "There isn't a GitHub Pages site here",
    "NoSuchBucket",
    "No such app",
    "The page you were looking for doesn't exist",
    "Sorry, this page is no longer available",
    "The specified bucket does not exist",
]

class SubdomainTakeoverScanner:
    """子域名接管扫描器"""

    def __init__(self, domain: str):
        self.domain = domain

    def enumerate_subdomains(self) -> List[str]:
        """枚举子域名"""
        subdomains = set()

        # 添加主域名
        subdomains.add(self.domain)

        # 常见子域名
        common_subs = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'ns2',
            'blog', 'api', 'dev', 'staging', 'test', 'admin', 'portal', 'cdn',
            'app', 'mobile', 'm', 'beta', 'demo', 'shop', 'store', 'support',
            'help', 'docs', 'wiki', 'forum', 'secure', 'vpn', 'remote',
        ]

        for sub in common_subs:
            subdomains.add(f"{sub}.{self.domain}")

        # 使用子域名枚举工具（如果可用）
        try:
            result = subprocess.run(
                ['amass', 'enum', '-passive', '-d', self.domain],
                capture_output=True,
                text=True,
                timeout=120
            )
            for line in result.stdout.strip().split('\n'):
                if line:
                    subdomains.add(line.strip())
        except Exception as e:
            logger.warning(f"Amass 扫描失败: {e}")

        return list(subdomains)

    def check_cname(self, subdomain: str) -> str:
        """检查CNAME记录"""
        try:
            answers = dns.resolver.resolve(subdomain, 'CNAME')
            return str(answers[0]).rstrip('.')
        except dns.resolver.NoAnswer:
            return None
        except dns.resolver.NXDOMAIN:
            return None
        except Exception as e:
            logger.debug(f"CNAME检查失败: {subdomain} - {e}")
            return None

    def check_vulnerability(self, subdomain: str, cname: str) -> SubdomainCheck:
        """检查是否存在接管风险"""
        # 检查是否指向已知的可接管服务
        target_service = None
        for pattern, service in TAKEOVER_FINGERPRINTS.items():
            if pattern in cname:
                target_service = service
                break

        if not target_service:
            return SubdomainCheck(
                subdomain=subdomain,
                cname=cname,
                status='unknown',
                risk_level='low',
                recommendation='手动检查服务状态'
            )

        # 尝试访问服务
        try:
            response = requests.get(
                f'http://{subdomain}',
                timeout=10,
                allow_redirects=False
            )

            # 检查响应内容
            content = response.text.lower()
            for vulnerable_text in VULNERABLE_RESPONSES:
                if vulnerable_text.lower() in content:
                    return SubdomainCheck(
                        subdomain=subdomain,
                        cname=cname,
                        status='vulnerable',
                        risk_level='critical',
                        recommendation=f'立即删除CNAME记录或重新配置{target_service}'
                    )

            return SubdomainCheck(
                subdomain=subdomain,
                cname=cname,
                status='active',
                risk_level='low',
                recommendation='服务正常，继续监控'
            )

        except requests.exceptions.ConnectionError:
            return SubdomainCheck(
                subdomain=subdomain,
                cname=cname,
                status='potentially_vulnerable',
                risk_level='high',
                recommendation=f'服务不可达，可能存在接管风险，请手动确认'
            )
        except Exception as e:
            return SubdomainCheck(
                subdomain=subdomain,
                cname=cname,
                status='error',
                risk_level='medium',
                recommendation=f'检查异常: {str(e)}'
            )

    def scan(self) -> List[SubdomainCheck]:
        """执行完整扫描"""
        results = []
        subdomains = self.enumerate_subdomains()

        logger.info(f"发现 {len(subdomains)} 个子域名")

        for subdomain in subdomains:
            cname = self.check_cname(subdomain)
            if cname:
                check_result = self.check_vulnerability(subdomain, cname)
                results.append(check_result)
                logger.info(f"检查: {subdomain} -> {cname} [{check_result.status}]")

        return results

    def get_vulnerable(self) -> List[SubdomainCheck]:
        """获取存在风险的子域名"""
        results = self.scan()
        return [r for r in results if r.risk_level in ['critical', 'high']]


# 使用示例
if __name__ == "__main__":
    scanner = SubdomainTakeoverScanner("example.com")
    vulnerable = scanner.get_vulnerable()

    if vulnerable:
        print("发现存在接管风险的子域名:")
        for v in vulnerable:
            print(f"  - {v.subdomain} -> {v.cname} [{v.risk_level}]")
            print(f"    建议: {v.recommendation}")
    else:
        print("未发现子域名接管风险")
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **资产管理**：
   - 建立完整的子域名资产清单
   - 变更管理流程
   - 定期审计机制

2. **监控告警**：
   - 实时监控DNS记录变更
   - 自动化子域名扫描
   - 告警响应机制

3. **防御措施**：
   - 避免使用泛域名解析
   - 及时删除失效的DNS记录
   - 第三方服务账户管理

4. **应急响应**：
   - 子域名接管应急预案
   - 快速删除DNS记录流程
   - 通知相关方机制

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级子域名安全案例。

---

## 延伸阅读

- [子域名接管详解](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/02-Configuration_and_Deployment_Management_Testing/10-Test_for_Subdomain_Takeover)
- [Can I take over XYZ](https://github.com/EdOverflow/can-i-take-over-xyz)
- [子域名接管防护指南](https://www.hackerone.com/blog/Guide-Subdomain-Takeovers)
