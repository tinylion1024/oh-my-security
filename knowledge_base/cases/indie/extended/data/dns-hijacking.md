# DNS 劫持 (DNS Hijacking)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-002 |
| 分类 | 数据安全 / 网络安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

攻击者通过篡改 DNS 解析记录，将合法域名解析到恶意服务器，导致用户访问被重定向到钓鱼站点或恶意内容，造成数据泄露或恶意软件感染。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **DNS 记录异常** - 域名解析到非预期 IP 地址或 CNAME 指向恶意域名
- [ ] **DNSSEC 未启用** - DNS 解析未使用 DNSSEC 签名验证
- [ ] **DNS 服务器配置不当** - DNS 服务器允许未授权的区域传输或动态更新

### 🔍 典型场景

```
场景 1: 注册商账户入侵
攻击者入侵域名注册商账户
修改 A 记录: example.com → 192.168.1.100 (恶意 IP)
结果: 用户访问 example.com 被重定向到恶意站点

场景 2: 中间人 DNS 劫持
攻击者控制本地网络 DNS 服务器
篡改 DNS 响应: api.bank.com → 攻击者控制的服务器
结果: 用户凭证被窃取

场景 3: 子域名接管
子域名 CNAME 指向已废弃的云服务 (如 GitHub Pages)
攻击者注册该云服务账号并接管子域名
结果: 子域名完全被控制
```

---

## 一句话防御

**启用 DNSSEC 验证、强制 DNS over HTTPS/TLS、监控 DNS 记录变更、实施注册商账户多因素认证、定期审计子域名配置。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **DNSSEC Analyzer** | DNSSEC 配置验证 | https://dnssec-analyzer.verisignlabs.com/ |
| **Sublert** | 子域名监控工具 | https://github.com/yassineaboukir/sublert |
| **Can I Take Over XYZ** | 子域名接管检测 | https://github.com/EdOverflow/can-i-take-over-xyz |
| **DNSSpy** | DNS 监控工具 | https://github.com/jvns/dns-spy |
| **Cloudflare DNS** | 安全 DNS 服务 | https://1.1.1.1/ |

---

## 快速缓解措施

### 1. 启用 DNSSEC
```bash
# 使用 Cloudflare 启用 DNSSEC
cfssl gencert -initca ca-csr.json | cfssljson -bare ca -
dnssec-signzone -A -3 $(head -c 1000 /dev/urandom | sha1sum | cut -b 1-16) \
  -N INCREMENT -o example.com -t example.com.zone
```

### 2. 强制 DNS over HTTPS
```javascript
// 浏览器配置
// Firefox: about:preferences -> Network Settings
// Chrome: chrome://settings/security -> Use secure DNS

// 应用层配置 (Node.js)
const { Resolver } = require('dns').promises;
const resolver = new Resolver();
resolver.setServers(['1.1.1.1', '1.0.0.1']);
```

### 3. 监控 DNS 变更
```python
# Python 示例：DNS 监控脚本
import dns.resolver
import smtplib

def check_dns(domain, expected_ip):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        actual_ips = [rdata.address for rdata in answers]
        if expected_ip not in actual_ips:
            send_alert(f"DNS hijacking detected for {domain}")
    except Exception as e:
        send_alert(f"DNS resolution failed for {domain}: {e}")
```

---

## 相关案例

- [CASE-EXT-DATA-003 CDN 配置错误](./cdn-misconfig.md)
- [CASE-EXT-DATA-007 快照泄露](./snapshot-leak.md)

---

## 参考标准

- RFC 4033 - DNS Security Introduction
- RFC 8484 - DNS Queries over HTTPS
- NIST SP 800-81 - Secure DNS Deployment Guide
- CIS DNS Benchmark
