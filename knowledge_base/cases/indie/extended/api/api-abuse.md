# API 滥用 (API Abuse)

> **Tier 适用**: L1 ✅

## 一句话风险

攻击者通过自动化工具滥用 API 接口，进行数据爬取、暴力破解或资源耗尽。

## 一分钟识别清单

- [ ] API 无速率限制或限制过宽松
- [ ] 缺少有效的认证和授权机制
- [ ] 未对异常请求模式进行监控和阻断

## 一句话防御

实施多层次的速率限制、认证机制和异常行为检测。

## 推荐工具链接

- [API Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
- [Rate Limiter](https://github.com/animir/node-rate-limiter) - Node.js 速率限制
- [API Gateway](https://www.nginx.com/learn/api-gateway/) - API 网关安全

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 数据爬取 | 自动化获取敏感业务数据 |
| 暴力破解 | 枚举用户名/密码/验证码 |
| 资源滥用 | 消耗服务器资源导致拒绝服务 |
| API 发现 | 自动化探测隐藏接口 |

## 防护代码示例

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # 验证逻辑
    pass
```

## 检测命令

```bash
# 快速请求测试
for i in {1..100}; do
  curl -s "https://api.target.com/endpoint" &
done

# 检查是否返回 429 Too Many Requests
```

## 防护措施

| 层级 | 措施 |
|------|------|
| 网络层 | IP 黑名单、GeoIP 限制 |
| 应用层 | 速率限制、CAPTCHA |
| 业务层 | 用户配额、异常检测 |

## 参考

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
