# CDN 配置错误 (CDN Misconfiguration)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-003 |
| 分类 | 数据安全 / 基础设施安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

CDN 配置不当导致源站 IP 泄露、敏感内容被缓存、访问控制失效或中间人攻击，造成数据泄露或服务被滥用。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **源站 IP 泄露** - 通过 DNS 历史记录、子域名、错误响应等方式可发现真实服务器 IP
- [ ] **敏感内容缓存** - 用户私有数据、API 响应、认证令牌被 CDN 缓存并分发
- [ ] **访问控制缺失** - CDN 未正确转发认证信息或未限制回源访问

### 🔍 典型场景

```
场景 1: 源站 IP 泄露
直接访问源站 IP: http://192.168.1.100
绕过 CDN 的 WAF 和速率限制
结果: 攻击者可对源站进行 DDoS 攻击或暴力破解

场景 2: 敏感响应缓存
API 响应头缺失: Cache-Control: no-store
CDN 缓存用户私有数据
结果: 用户 A 的数据被用户 B 访问

场景 3: 回源未限制
CDN 回源请求未携带签名
攻击者直接访问源站 API
结果: 绕过 CDN 的访问控制
```

---

## 一句话防御

**配置源站访问白名单、禁用敏感路径缓存、设置正确的缓存控制头、启用 HTTPS 强制跳转、实施回源签名验证。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **Censys** | 源站 IP 发现检测 | https://search.censys.io/ |
| **Shodan** | 互联网设备扫描 | https://www.shodan.io/ |
| **Cloudflare's Origin CA** | 回源证书配置 | https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/ |
| **CDN Finder** | CDN 提供商检测 | https://www.cdnplanet.com/tools/cdnfinder/ |

---

## 快速缓解措施

### 1. 限制源站访问
```nginx
# Nginx 配置：仅允许 CDN IP 访问
# Cloudflare IP 列表：https://www.cloudflare.com/ips/
allow 173.245.48.0/20;
allow 103.21.244.0/22;
deny all;
```

### 2. 正确的缓存控制
```nginx
# 禁止缓存私有数据
location /api/user {
    add_header Cache-Control "no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0";
    add_header Pragma "no-cache";
    add_header Expires "0";
}

# 允许缓存公开资源
location /static {
    add_header Cache-Control "public, max-age=31536000, immutable";
}
```

### 3. 回源签名验证
```javascript
// Cloudflare Workers 示例
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

async function handleRequest(request) {
  const signature = request.headers.get('X-Origin-Signature');
  const expected = await generateSignature(request.url, ORIGIN_SECRET);

  if (signature !== expected) {
    return new Response('Forbidden', { status: 403 });
  }

  return fetch(request);
}
```

---

## 相关案例

- [CASE-EXT-DATA-001 缓存污染](./cache-poisoning.md)
- [CASE-EXT-DATA-006 配置文件暴露](./config-exposure.md)

---

## 参考标准

- OWASP ASVS v4.0 - V12: Files and Resources
- NIST SP 800-52 - TLS Guidelines
- Cloudflare Best Practices
- AWS CloudFront Security Best Practices
