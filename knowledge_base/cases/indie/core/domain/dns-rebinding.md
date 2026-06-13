# DNS重绑定攻击 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: domain（域名安全）
- **严重程度**: high（高）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐ (3/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者利用DNS TTL短时变化的特性，让你的前端JavaScript先连接到他们控制的IP，再重新解析到你的内网IP，从而绕过浏览器同源策略访问你的内网服务。

### 一分钟识别
你的应用是否有以下风险：
- [ ] 前端JavaScript直接访问用户指定的URL
- [ ] 服务端未验证请求目标IP是否为私有地址
- [ ] DNS解析结果未缓存或缓存时间过短
- [ ] WebSocket连接未验证来源
→ 勾选≥1项，即需关注此风险

### 一句话防御
**验证请求目标IP + 禁止访问私有地址**：服务端在代理请求前，解析目标域名并检查IP是否为私有地址（10.x, 172.16.x, 192.168.x, 127.x）。

### 快速行动清单
1. [ ] 立即行动项：检查代码中是否有URL代理功能（今天可完成，免费）
2. [ ] 短期行动项：添加IP地址验证逻辑（本周可完成，免费）
3. [ ] 长期行动项：实施DNS缓存策略（规划中，免费）

### 推荐工具
- 免费：代码修改
- 低成本：安全网关（如 Kong、Traefik）

### 验证方法
- [ ] 测试代理功能是否阻止对内网IP的请求
- [ ] 使用 singularity 工具测试DNS重绑定
- [ ] 检查DNS缓存配置

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有一个"网页预览"功能，用户输入URL，你的服务端获取该URL的内容并返回给前端展示。攻击者：

1. 注册域名 `evil.com`，设置DNS A记录在两个IP之间快速切换：
   - 第一次解析：攻击者的公网IP
   - 后续解析：目标内网IP（如192.168.1.1）

2. 攻击者让浏览器先加载 `http://evil.com` 的恶意JavaScript
3. 恶意脚本发起请求到你的服务器，请求 `http://evil.com`
4. 你的服务端解析 `evil.com`，得到攻击者的IP，建立连接
5. 在保持连接期间，DNS记录变化，再次解析 `evil.com` 得到内网IP
6. 你的服务端继续与内网IP通信，返回敏感信息

### 攻击路径（简化版）
1. **设置恶意域名**：配置DNS重绑定服务器
2. **诱使访问**：让用户/服务器请求恶意域名
3. **DNS重绑定**：DNS解析从公网IP切换到内网IP
4. **绕过同源策略**：访问内网服务获取敏感数据

### 防御实施（低成本方案）

#### 方案A：IP地址验证（推荐）

**核心原则**：验证目标IP + 禁止私有地址。

**配置步骤**：

```python
import socket
import ipaddress
import logging

logger = logging.getLogger(__name__)

# 私有IP地址范围
PRIVATE_IP_RANGES = [
    ipaddress.ip_network('10.0.0.0/8'),      # Class A
    ipaddress.ip_network('172.16.0.0/12'),   # Class B
    ipaddress.ip_network('192.168.0.0/16'),  # Class C
    ipaddress.ip_network('127.0.0.0/8'),     # Loopback
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local
    ipaddress.ip_network('::1/128'),         # IPv6 Loopback
    ipaddress.ip_network('fc00::/7'),        # IPv6 ULA
    ipaddress.ip_network('fe80::/10'),       # IPv6 Link-local
]

def is_private_ip(ip_str: str) -> bool:
    """检查IP是否为私有地址"""
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in PRIVATE_IP_RANGES:
            if ip in network:
                return True
        return False
    except ValueError:
        return True  # 无效IP视为私有

def resolve_and_validate(hostname: str) -> tuple:
    """
    解析域名并验证IP地址

    Returns:
        (is_valid, ip_address, error_message)
    """
    try:
        # 解析所有IP地址
        ips = socket.getaddrinfo(hostname, None)

        for family, _, _, _, sockaddr in ips:
            ip = sockaddr[0]

            if is_private_ip(ip):
                logger.warning(f"拒绝访问私有IP: {hostname} -> {ip}")
                return False, ip, f"不允许访问私有IP地址: {ip}"

        # 返回第一个公网IP
        first_ip = ips[0][4][0]
        return True, first_ip, None

    except socket.gaierror:
        return False, None, "域名解析失败"
    except Exception as e:
        return False, None, str(e)

def safe_fetch_url(url: str) -> dict:
    """
    安全获取URL内容
    """
    from urllib.parse import urlparse
    import requests

    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        return {'error': '无效的URL'}

    # 验证IP地址
    is_valid, ip, error = resolve_and_validate(hostname)

    if not is_valid:
        return {'error': f'安全限制: {error}'}

    # 发起请求
    try:
        response = requests.get(url, timeout=10)
        return {
            'status': 'success',
            'content': response.text[:10000]  # 限制响应大小
        }
    except Exception as e:
        return {'error': str(e)}
```

**局限性**：
- 需要修改现有代码
- 可能影响合法的内网服务访问

#### 方案B：DNS缓存

**核心原则**：缓存DNS结果 + 验证一致性。

```python
import time
from functools import lru_cache

class DNSSecurityCache:
    """安全的DNS缓存"""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self.cache = {}

    def resolve(self, hostname: str) -> list:
        """解析并缓存DNS结果"""
        now = time.time()

        if hostname in self.cache:
            cached_time, ips = self.cache[hostname]
            if now - cached_time < self.ttl:
                return ips

        # 新解析
        ips = self._resolve_fresh(hostname)
        self.cache[hostname] = (now, ips)
        return ips

    def _resolve_fresh(self, hostname: str) -> list:
        """执行DNS解析"""
        try:
            results = socket.getaddrinfo(hostname, None)
            return list(set(sockaddr[0] for _, _, _, _, sockaddr in results))
        except:
            return []

    def validate_consistency(self, hostname: str) -> bool:
        """验证DNS解析一致性"""
        cached_ips = self.resolve(hostname)
        fresh_ips = self._resolve_fresh(hostname)

        # 检查是否有新IP不在缓存中
        new_ips = set(fresh_ips) - set(cached_ips)

        if new_ips:
            logger.warning(f"DNS解析变化检测: {hostname} 新增IP: {new_ips}")
            return False

        return True
```

### 决策树
```
你的应用是否代理用户指定的URL？
├── 是 → 是否验证目标IP？
│   ├── 是 → 验证是否正确？
│   │   ├── 是 → 继续监控
│   │   └── 否 → 修复验证逻辑
│   └── 否 → 立即添加IP验证（方案A）
└── 否 → 风险较低
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **网络层防护**：
   - 防火墙规则限制内网访问
   - 网络隔离策略
   - DNS服务器安全配置

2. **应用层防护**：
   - 输入验证
   - IP地址白名单/黑名单
   - DNS Pinning

3. **监控检测**：
   - 异常DNS请求监控
   - 内网访问日志审计
   - 安全事件告警

4. **安全架构**：
   - 零信任网络架构
   - 服务间认证
   - 最小权限原则

### 相关企业案例

参考 `cases/enterprise/bizsec/` 目录中的企业级网络安全案例。

---

## 延伸阅读

- [DNS重绑定攻击详解](https://en.wikipedia.org/wiki/DNS_rebinding)
- [OWASP DNS重绑定防护](https://owasp.org/www-community/attacks/DNS_Rebinding)
- [Singularity - DNS重绑定测试工具](https://github.com/nccgroup/singularity)
