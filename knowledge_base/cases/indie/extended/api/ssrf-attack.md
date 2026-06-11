# SSRF 攻击 (Server-Side Request Forgery)

> **Tier 适用**: L1 ✅

## 一句话风险

攻击者利用服务端发起请求的能力，访问内网资源或云元数据，导致数据泄露或内网渗透。

## 一分钟识别清单

- [ ] 用户输入被直接拼接到 URL 参数中发起服务端请求
- [ ] 未限制请求协议（file://、gopher://、dict:// 等）
- [ ] 可访问云元数据端点（如 `169.254.169.254`）或内网服务

## 一句话防御

对用户输入的 URL 进行严格的白名单校验，禁止访问内网 IP 和敏感协议。

## 推荐工具链接

- [SSRFmap](https://github.com/swisskyrepo/SSRFmap) - SSRF 漏洞利用工具
- [Gopherus](https://github.com/tarunkant/Gopherus) - 生成 SSRF Payload
- [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 云元数据获取 | 访问 AWS/GCP 元数据获取临时凭证 |
| 内网端口扫描 | 探测内网开放服务 |
| 文件读取 | 使用 file:// 协议读取本地文件 |
| Redis 未授权 | 通过 gopher:// 攻击内网 Redis |

## 修复代码示例

```python
# 错误：直接使用用户输入
import requests
url = request.args.get('url')
response = requests.get(url)

# 正确：URL 白名单校验
ALLOWED_DOMAINS = ['api.example.com', 'cdn.example.com']

def safe_request(user_url):
    parsed = urlparse(user_url)
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError("域名不在白名单中")
    if parsed.scheme not in ['http', 'https']:
        raise ValueError("仅允许 HTTP/HTTPS")
    return requests.get(user_url, timeout=5)
```

## 检测命令

```bash
# 测试云元数据访问
curl "https://target.com/fetch?url=http://169.254.169.254/latest/meta-data/"

# 测试内网访问
curl "https://target.com/fetch?url=http://127.0.0.1:6379/"
```

## 参考

- [PortSwigger SSRF](https://portswigger.net/web-security/ssrf)
- [HackerOne SSRF Reports](https://hackerone.com/hacktivity?querystring=ssrf&filter=type%3Ahacktivity&page=1)
