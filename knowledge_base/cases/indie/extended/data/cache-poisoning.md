# 缓存污染 (Cache Poisoning)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-001 |
| 分类 | 数据安全 / 缓存安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

攻击者通过操纵缓存键或缓存响应，将恶意内容注入缓存系统，导致后续用户获取被篡改的数据或遭受 XSS、重定向等攻击。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **未加密缓存键** - 缓存键包含用户可控参数（如 URL 参数、HTTP 头）且未进行规范化处理
- [ ] **缓存响应可操纵** - 响应内容包含用户输入且未转义，或响应头可被注入
- [ ] **缓存元数据泄露** - 缓存系统版本、配置信息暴露在错误响应中

### 🔍 典型场景

```
场景 1: URL 参数污染
原始请求: GET /api/data?x=1
攻击请求: GET /api/data?x=1&poison=<script>alert(1)</script>
缓存键:   /api/data?x=1 (未包含 poison 参数)
结果:     所有访问 /api/data?x=1 的用户收到恶意脚本

场景 2: HTTP 头注入
攻击请求: GET /api/data HTTP/1.1
          X-Forwarded-Host: evil.com
缓存响应: Location: http://evil.com/redirect
结果:     用户被重定向到恶意站点
```

---

## 一句话防御

**对所有缓存键输入进行规范化验证，对缓存响应内容进行严格转义，禁用不必要的缓存头，实施缓存分区和访问控制。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **Cachebuster** | 缓存污染测试工具 | https://github.com/Hakky54/cachebuster |
| **Param Miner** | 参数挖掘与缓存测试 | https://github.com/PortSwigger/param-miner |
| **Burp Suite** | Web 缓存污染检测 | https://portswigger.net/burp/documentation/desktop/tools/engagement-tools/cache-poisoning |
| **OWASP Testing Guide** | 缓存安全测试 | https://owasp.org/www-project-web-security-testing-guide/ |

---

## 快速缓解措施

### 1. 缓存键规范化
```nginx
# Nginx 示例：规范化缓存键
proxy_cache_key "$scheme$host$request_uri";
# 移除不必要的查询参数
proxy_cache_key "$scheme$host$uri";
```

### 2. 禁用危险缓存头
```nginx
# 禁用缓存响应中的用户可控头
proxy_hide_header X-Forwarded-Host;
proxy_hide_header X-Forwarded-Proto;
```

### 3. 输入验证
```javascript
// Node.js 示例
app.use((req, res, next) => {
  // 规范化查询参数
  const allowedParams = ['id', 'page', 'limit'];
  Object.keys(req.query).forEach(param => {
    if (!allowedParams.includes(param)) {
      delete req.query[param];
    }
  });
  next();
});
```

---

## 相关案例

- [CASE-EXT-DATA-003 CDN 配置错误](./cdn-misconfig.md)
- [CASE-EXT-DATA-010 CORS 配置错误](./cors-misconfig.md)

---

## 参考标准

- OWASP ASVS v4.0 - V12: Files and Resources
- CWE-349: Acceptance of Extraneous Untrusted Data With Trusted Data
- RFC 7234 - HTTP Caching
