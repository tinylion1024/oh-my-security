# CORS 配置错误 (CORS Misconfiguration)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-010 |
| 分类 | 数据安全 / Web 安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

CORS（跨域资源共享）配置过于宽松，允许任意域名或恶意站点读取用户敏感数据，导致数据泄露或 CSRF 攻击。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **Access-Control-Allow-Origin 设置为 \*** - 允许任意域名访问 API
- [ ] **反射 Origin 头** - 服务器直接将请求的 Origin 头作为 `Access-Control-Allow-Origin` 返回
- [ ] **凭证允许跨域** - `Access-Control-Allow-Credentials: true` 配合宽松的 Origin

### 🔍 典型场景

```
场景 1: 反射 Origin 头
请求: Origin: https://evil.com
响应: Access-Control-Allow-Origin: https://evil.com
       Access-Control-Allow-Credentials: true
结果: evil.com 可读取用户敏感数据

场景 2: null Origin 允许
请求: Origin: null (来自 data URL 或本地文件)
响应: Access-Control-Allow-Origin: null
       Access-Control-Allow-Credentials: true
结果: 本地 HTML 文件可跨域访问

场景 3: 正则匹配错误
配置: 允许 *.example.com
实际匹配: evil.com.example.com
结果: 子域名被绕过
```

---

## 一句话防御

**严格限制 `Access-Control-Allow-Origin` 白名单、禁止反射 Origin 头、避免 `Access-Control-Allow-Credentials` 与通配符共用、实施 Vary: Origin 缓存控制。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **CORScanner** | CORS 漏洞扫描 | https://github.com/chenjj/CORScanner |
| **Burp Suite** | CORS 测试 | https://portswigger.net/burp |
| **OWASP CORS Test** | 在线测试工具 | https://www.test-cors.org/ |
| **CORS Misconfig Scanner** | 自动化检测 | https://github.com/s0md3v/Corsy |

---

## 快速缓解措施

### 1. 白名单配置
```javascript
// Node.js + Express 示例
const allowedOrigins = [
  'https://example.com',
  'https://app.example.com',
  'https://admin.example.com'
];

app.use((req, res, next) => {
  const origin = req.headers.origin;

  // 仅允许白名单域名
  if (allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
  }

  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Vary', 'Origin');  // 防止缓存问题

  next();
});
```

### 2. Nginx CORS 配置
```nginx
# Nginx 配置：安全的 CORS 设置
map $http_origin $cors_origin {
    default "";
    "~^https://(www\.)?example\.com$" $http_origin;
    "~^https://app\.example\.com$" $http_origin;
}

server {
    location /api {
        if ($cors_origin != "") {
            add_header 'Access-Control-Allow-Origin' $cors_origin always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE' always;
            add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type' always;
            add_header 'Access-Control-Allow-Credentials' 'true' always;
            add_header 'Vary' 'Origin' always;
        }

        # 处理预检请求
        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }
}
```

### 3. 正确处理 null Origin
```python
# Python + Flask 示例
from flask import Flask, request, Response

app = Flask(__name__)

ALLOWED_ORIGINS = {'https://example.com', 'https://app.example.com'}

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')

    # 拒绝 null Origin
    if origin and origin != 'null' and origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Vary'] = 'Origin'

    return response
```

---

## 相关案例

- [CASE-EXT-DATA-001 缓存污染](./cache-poisoning.md)
- [CASE-EXT-DATA-003 CDN 配置错误](./cdn-misconfig.md)

---

## 参考标准

- OWASP ASVS v4.0 - V13: API and Web Service
- CWE-942: Permissive Cross-domain Policy with Untrusted Domains
- MDN - CORS (Cross-Origin Resource Sharing)
- RFC 6454 - The Web Origin Concept
