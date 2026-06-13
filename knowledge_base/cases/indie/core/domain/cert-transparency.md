# 证书透明度泄露 - 独立开发者版

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
你的内部测试域名、即将发布的新产品域名在证书透明度日志中公开可见，攻击者提前发现你的新产品计划、内部系统架构，造成商业机密泄露。

### 一分钟识别
你的域名证书是否暴露敏感信息：
- [ ] 内部测试域名使用了公开信任的SSL证书
- [ ] 新产品发布前域名已出现在CT日志中
- [ ] 证书包含敏感的内部系统名称
- [ ] 未使用内部CA或自签名证书
→ 勾选≥1项，即需关注此风险

### 一句话防御
**内部系统使用自签名证书或内部CA**：只有需要公网访问的系统才使用公开信任的证书，内部系统使用内部CA签发的证书。

### 快速行动清单
1. [ ] 立即行动项：检查CT日志中是否有内部域名（今天可完成，免费）
2. [ ] 短期行动项：评估内部系统证书策略（本周可完成，免费）
3. [ ] 长期行动项：部署内部CA或使用自签名证书（规划中，免费/低成本）

### 推荐工具
- 免费：crt.sh（CT日志查询）、Google Certificate Transparency
- 低成本：内部CA（如 Smallstep、Vault PKI）

### 验证方法
- [ ] 在 crt.sh 查询公司域名
- [ ] 检查是否暴露了不应公开的子域名
- [ ] 评估泄露信息的影响

---

## L2 小团队版（理解版）

### 场景还原
你的公司正在秘密开发新产品 `superapp.example.com`，计划在两周后发布。为了让测试团队测试，你提前申请了SSL证书。

但是，证书透明度（CT）日志公开记录了所有公开信任的证书颁发。竞争对手通过监控CT日志，发现了 `superapp.example.com` 这个域名，从而：

1. 推测出新产品名称
2. 提前注册相关社交媒体账号
3. 甚至提前发布类似产品
4. 通过域名了解你的技术栈

### 信息泄露内容

CT日志中的证书包含：
- 域名（CN和SAN）
- 证书颁发时间
- 证书颁发机构
- 组织名称

攻击者可以分析出：
- 新产品/功能名称
- 内部系统架构
- 部署时间线
- 技术选型（通过域名命名规律）

### 防御实施（低成本方案）

#### 方案A：内部系统使用内部CA（推荐）

**核心原则**：内网系统不使用公开信任的证书。

**工具/服务**：Smallstep、Vault PKI、自签名证书

**配置步骤**：

1. **部署内部CA**：
   ```bash
   # 使用 Smallstep
   step ca init --name="Internal CA" --provisioner="admin" --dns="ca.internal" --address=":443"

   # 为内部系统签发证书
   step ca certificate "gitlab.internal" gitlab.crt gitlab.key
   ```

2. **在客户端信任内部CA**：
   ```bash
   # 分发CA证书到客户端
   step ca bootstrap --ca-url="https://ca.internal" --fingerprint="..."
   ```

3. **使用自签名证书（小规模）**：
   ```bash
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=internal.example.com"
   ```

**局限性**：
- 需要在客户端安装CA证书
- 增加运维复杂度

#### 方案B：使用CAA记录限制证书颁发

**核心原则**：限制哪些CA可以为你的域名颁发证书。

**配置步骤**：
```
; 只允许特定CA颁发证书
example.com.     IN CAA 0 issue "letsencrypt.org"
example.com.     IN CAA 0 issuewild ";"
; 禁止其他CA颁发
```

**成本**：免费

**注意**：CAA记录无法阻止已经颁发的证书出现在CT日志中，但可以防止未经授权的证书颁发。

### 决策树
```
域名是否需要公网访问？
├── 是 → 使用公开信任的证书（不可避免CT记录）
│   └── 考虑使用通用域名减少信息泄露
└── 否 → 使用内部CA或自签名证书（方案A）
```

### 代码示例（CT日志监控）

```python
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict

logger = logging.getLogger(__name__)

class CTLogMonitor:
    """证书透明度日志监控"""

    def __init__(self, domain: str):
        self.domain = domain
        self.crt_sh_url = "https://crt.sh"

    def query_ct_logs(self) -> List[Dict]:
        """查询CT日志中的证书记录"""
        try:
            # 使用 crt.sh API
            response = requests.get(
                f"{self.crt_sh_url}/json",
                params={"q": f"%.{self.domain}"},
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"CT日志查询失败: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"CT日志查询异常: {e}")
            return []

    def analyze_certificates(self, days: int = 30) -> Dict:
        """分析最近N天的证书颁发情况"""
        certs = self.query_ct_logs()

        now = datetime.utcnow()
        cutoff = now - timedelta(days=days)

        recent_certs = []
        subdomains = set()

        for cert in certs:
            # 解析颁发时间
            not_before = datetime.strptime(
                cert.get('not_before', ''),
                '%Y-%m-%d %H:%M:%S'
            ) if cert.get('not_before') else None

            if not_before and not_before > cutoff:
                recent_certs.append({
                    'id': cert.get('id'),
                    'domain': cert.get('name_value'),
                    'issuer': cert.get('issuer_name'),
                    'not_before': cert.get('not_before'),
                    'not_after': cert.get('not_after'),
                })

                # 提取子域名
                for name in cert.get('name_value', '').split('\n'):
                    name = name.strip()
                    if name.endswith(f'.{self.domain}'):
                        subdomains.add(name)

        return {
            'domain': self.domain,
            'total_certs': len(certs),
            'recent_certs': len(recent_certs),
            'recent_details': recent_certs,
            'discovered_subdomains': sorted(list(subdomains)),
        }

    def check_sensitive_exposure(self, sensitive_patterns: List[str]) -> List[Dict]:
        """检查是否暴露敏感域名"""
        certs = self.query_ct_logs()
        exposures = []

        for cert in certs:
            domain = cert.get('name_value', '')
            for pattern in sensitive_patterns:
                if pattern.lower() in domain.lower():
                    exposures.append({
                        'domain': domain,
                        'pattern': pattern,
                        'issuer': cert.get('issuer_name'),
                        'not_before': cert.get('not_before'),
                    })

        return exposures

    def generate_report(self) -> str:
        """生成CT日志监控报告"""
        analysis = self.analyze_certificates(days=90)

        report = f"""# 证书透明度日志监控报告

## 域名: {self.domain}

### 统计信息
- 总证书数: {analysis['total_certs']}
- 最近90天证书: {analysis['recent_certs']}
- 发现的子域名: {len(analysis['discovered_subdomains'])}

### 发现的子域名
"""
        for subdomain in analysis['discovered_subdomains']:
            report += f"- {subdomain}\n"

        if analysis['recent_certs']:
            report += "\n### 最近颁发的证书\n\n"
            report += "| 域名 | 颁发时间 | 过期时间 |\n"
            report += "|------|----------|----------|\n"
            for cert in analysis['recent_certs'][:20]:
                report += f"| {cert['domain']} | {cert['not_before']} | {cert['not_after']} |\n"

        return report


# 使用示例
if __name__ == "__main__":
    # 监控证书透明度
    monitor = CTLogMonitor("example.com")

    # 检查敏感信息暴露
    sensitive = ['admin', 'internal', 'staging', 'dev', 'test', 'vpn']
    exposures = monitor.check_sensitive_exposure(sensitive)

    if exposures:
        print("发现敏感域名暴露:")
        for exp in exposures:
            print(f"  - {exp['domain']} (匹配: {exp['pattern']})")
    else:
        print("未发现敏感信息暴露")

    # 生成完整报告
    print(monitor.generate_report())
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **证书策略**：
   - 明确公网/内网证书使用规范
   - 证书命名规范
   - 证书审批流程

2. **内部PKI**：
   - 部署企业内部CA
   - 自动化证书管理
   - 客户端信任分发

3. **监控告警**：
   - 实时监控CT日志
   - 异常证书告警
   - 敏感域名监控

4. **安全意识**：
   - 开发团队培训
   - 域名命名规范
   - 发布流程安全

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级证书管理案例。

---

## 延伸阅读

- [证书透明度官方网站](https://certificate.transparency.dev/)
- [crt.sh CT日志查询](https://crt.sh/)
- [Google CT政策](https://www.google.com/intl/en/chrome/certificate-transparency/)
- [Smallstep 内部CA](https://smallstep.com/)
