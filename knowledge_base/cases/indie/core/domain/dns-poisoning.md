# DNS污染 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: domain（域名安全）
- **严重程度**: critical（严重）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户访问你的网站时，DNS解析被劫持指向恶意服务器，用户看到的是钓鱼页面或广告页面，你的品牌信誉受损，用户数据泄露。

### 一分钟识别
你的域名是否有以下风险：
- [ ] 未启用DNSSEC
- [ ] 使用不可信的DNS服务器
- [ ] DNS记录未加密传输
- [ ] 未监控DNS解析状态
→ 勾选≥1项，即需关注此风险

### 一句话防御
**启用DNSSEC + 使用可信DNS服务商**：DNSSEC通过数字签名防止DNS数据被篡改，Cloudflare、AWS Route53等主流服务商均支持免费启用。

### 快速行动清单
1. [ ] 立即行动项：检查当前DNS服务商是否支持DNSSEC（今天可完成，免费）
2. [ ] 短期行动项：启用DNSSEC（本周可完成，免费）
3. [ ] 长期行动项：配置DNS监控告警（规划中，免费/低成本）

### 推荐工具
- 免费：Cloudflare DNS（自动DNSSEC）、AWS Route53
- 低成本：DNS监控服务（如 DNSPerf、Catchpoint）

### 验证方法
- [ ] 使用 dnsviz.net 可视化DNSSEC状态
- [ ] 使用 dig 检查DNSSEC签名
- [ ] 从不同网络环境测试DNS解析

---

## L2 小团队版（理解版）

### 场景还原
你的电商网站 `myshop.com` 突然收到大量用户投诉：访问网站时看到了奇怪的广告页面，或者浏览器提示"连接不安全"。检查发现，某些地区的用户DNS解析被劫持，指向了恶意服务器。

攻击者在ISP或网络中间节点注入了伪造的DNS响应，将你的域名解析到他们控制的IP。用户在该IP上看到的是：
1. 钓鱼页面（窃取登录凭证）
2. 广告页面（赚取广告费）
3. 恶意软件下载页面

由于DNS查询默认使用UDP协议且无验证，攻击者可以轻易伪造DNS响应。

### 攻击路径（简化版）
1. **网络位置优势**：攻击者控制ISP或中间网络节点
2. **监听DNS请求**：识别目标域名的DNS查询
3. **注入伪造响应**：返回恶意IP而非真实IP
4. **用户访问恶意服务器**：钓鱼、广告、恶意软件

### 防御实施（低成本方案）

#### 方案A：启用DNSSEC（推荐）

**核心原则**：数字签名验证DNS数据完整性。

**工具/服务**：Cloudflare、AWS Route53、Google Cloud DNS

**配置步骤**：

1. **Cloudflare 启用DNSSEC**：
   ```
   Cloudflare Dashboard → DNS → Settings → DNSSEC → Enable
   ```
   Cloudflare会自动处理所有DNSSEC配置，包括：
   - 生成DNSSEC密钥
   - 签名DNS记录
   - 在注册商配置DS记录

2. **在域名注册商配置DS记录**：
   Cloudflare会提供DS记录，需要在注册商后台添加：
   ```
   类型: DS
   名称: @
   密钥标签: [Cloudflare提供的值]
   算法: 13 (ECDSAP256SHA256)
   摘要类型: 2
   摘要: [Cloudflare提供的摘要]
   ```

3. **验证DNSSEC**：
   ```bash
   # 使用 dig 验证DNSSEC
   dig +dnssec example.com

   # 查看AD标志（Authenticated Data）
   # flags: qr rd ra ad; 表示DNSSEC验证通过
   ```

**局限性**：
- 需要注册商支持DNSSEC
- 配置相对复杂（但Cloudflare简化了流程）

#### 方案B：使用DoH/DoT加密DNS

**工具/服务**：Cloudflare 1.1.1.1、Google 8.8.8.8

**优势**：
- 加密DNS查询，防止中间人攻击
- 无需额外配置DNSSEC

**配置步骤**：
```nginx
# Nginx 配置 DoT
resolver 1.1.1.1 valid=300s;
resolver_timeout 5s;
```

**成本**：免费

### 决策树
```
你的DNS服务商是否支持DNSSEC？
├── 是 → 启用DNSSEC（方案A）
└── 否 → 切换到支持DNSSEC的服务商（如Cloudflare）
    └── 启用DNSSEC
```

### 代码示例（DNSSEC检查）

```python
import subprocess
import re
import logging

logger = logging.getLogger(__name__)

def check_dnssec(domain: str) -> dict:
    """
    检查域名DNSSEC状态

    Args:
        domain: 要检查的域名

    Returns:
        检查结果字典
    """
    try:
        # 使用 dig 检查DNSSEC
        result = subprocess.run(
            ['dig', '+dnssec', '+multiline', domain],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout

        # 检查是否有DNSKEY记录
        has_dnskey = 'DNSKEY' in output

        # 检查是否有RRSIG记录（资源记录签名）
        has_rrsig = 'RRSIG' in output

        # 检查AD标志（Authenticated Data）
        has_ad_flag = re.search(r'flags:.*\bad\b', output) is not None

        if has_dnskey and has_rrsig and has_ad_flag:
            return {
                'status': 'enabled',
                'message': 'DNSSEC已正确启用',
                'dnskey': has_dnskey,
                'rrsig': has_rrsig,
                'authenticated': has_ad_flag
            }
        elif has_dnskey or has_rrsig:
            return {
                'status': 'partial',
                'message': 'DNSSEC配置可能不完整',
                'dnskey': has_dnskey,
                'rrsig': has_rrsig,
                'authenticated': has_ad_flag
            }
        else:
            return {
                'status': 'disabled',
                'message': 'DNSSEC未启用',
                'recommendation': '建议启用DNSSEC防止DNS污染'
            }

    except subprocess.TimeoutExpired:
        return {'status': 'error', 'message': 'DNS查询超时'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def check_dns_consistency(domain: str, expected_ip: str, dns_servers: list = None) -> dict:
    """
    检查DNS解析一致性

    Args:
        domain: 域名
        expected_ip: 期望的IP地址
        dns_servers: 要检查的DNS服务器列表

    Returns:
        检查结果
    """
    if dns_servers is None:
        dns_servers = [
            '8.8.8.8',      # Google
            '1.1.1.1',      # Cloudflare
            '208.67.222.222',  # OpenDNS
        ]

    results = []
    inconsistencies = []

    for dns_server in dns_servers:
        try:
            result = subprocess.run(
                ['dig', f'@{dns_server}', '+short', 'A', domain],
                capture_output=True,
                text=True,
                timeout=10
            )

            ips = [ip.strip() for ip in result.stdout.strip().split('\n') if ip.strip()]
            primary_ip = ips[0] if ips else None

            results.append({
                'dns_server': dns_server,
                'ip': primary_ip,
                'match': primary_ip == expected_ip
            })

            if primary_ip != expected_ip:
                inconsistencies.append({
                    'dns_server': dns_server,
                    'expected': expected_ip,
                    'actual': primary_ip
                })

        except Exception as e:
            results.append({
                'dns_server': dns_server,
                'error': str(e)
            })

    return {
        'domain': domain,
        'expected_ip': expected_ip,
        'results': results,
        'inconsistencies': inconsistencies,
        'is_consistent': len(inconsistencies) == 0
    }


# 使用示例
if __name__ == "__main__":
    # 检查DNSSEC
    dnssec_result = check_dnssec("example.com")
    print(f"DNSSEC状态: {dnssec_result}")

    # 检查DNS一致性
    consistency = check_dns_consistency("example.com", "93.184.216.34")
    print(f"DNS一致性: {consistency}")
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **DNSSEC部署**：
   - 在所有权威DNS服务器启用DNSSEC
   - 使用强密钥算法（ECDSAP256SHA256）
   - 定期轮换密钥

2. **DNS监控**：
   - 全球DNS解析监控
   - DNS响应时间监控
   - DNS劫持检测

3. **备用DNS**：
   - 多DNS服务商冗余
   - DNS故障切换机制

4. **DoH/DoT部署**：
   - 应用内使用加密DNS
   - 防止本地网络DNS劫持

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级DNS安全案例。

---

## 延伸阅读

- [DNSSEC工作原理](https://www.icann.org/resources/pages/dnssec-what-is-it-why-important-2019-03-20-en)
- [Cloudflare DNSSEC配置](https://developers.cloudflare.com/dns/dnssec/)
- [DNS劫持检测](https://dnsviz.net/)
