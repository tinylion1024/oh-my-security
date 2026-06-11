# JWT 弱密钥 (JWT Weak Secret)

> **Tier 适用**: L1 ✅

## 一句话风险

JWT 签名使用弱密钥或默认密钥，攻击者可伪造合法 Token 提升权限。

## 一分钟识别清单

- [ ] JWT 使用弱密钥（如 "secret"、"123456"）
- [ ] 使用默认密钥或公开的测试密钥
- [ ] 签名算法设置为 "none" 或接受算法切换

## 一句话防御

使用强随机密钥（256 位以上），禁止 "none" 算法，验证算法一致性。

## 推荐工具链接

- [jwt_tool](https://github.com/ticarpi/jwt_tool) - JWT 渗透测试工具
- [jwt-cracker](https://github.com/brendan-rius/c-jwt-cracker) - JWT 密钥爆破
- [JWT.io](https://jwt.io/) - JWT 在线调试

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 弱密钥爆破 | 暴力破解简单密钥 |
| None 算法攻击 | 修改 alg 为 none 绕过验证 |
| 算法切换 | RS256 改为 HS256 用公钥签名 |
| 密钥泄露 | 从配置文件或代码库获取密钥 |

## 攻击示例

```bash
# 使用 jwt_tool 测试
python3 jwt_tool.py <token> -C -d wordlist.txt

# None 算法攻击
python3 jwt_tool.py <token> -X n

# 算法混淆攻击
python3 jwt_tool.py <token> -X k -pk public.pem
```

## 修复代码示例

```python
# 错误：使用弱密钥
import jwt
token = jwt.encode(payload, "secret", algorithm="HS256")

# 正确：使用强密钥
import secrets
import jwt

SECRET_KEY = secrets.token_urlsafe(32)  # 生成 256 位密钥
token = jwt.encode(
    payload,
    SECRET_KEY,
    algorithm="HS256",
    headers={"typ": "JWT", "alg": "HS256"}
)

# 验证时指定算法
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

## 检测方法

```bash
# 解码 JWT
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." | cut -d'.' -f2 | base64 -d

# 使用常见密钥尝试
for secret in "secret" "123456" "admin" "password"; do
  python3 -c "import jwt; jwt.decode('$TOKEN', '$secret', algorithms=['HS256'])" 2>/dev/null && echo "Found: $secret"
done
```

## 安全配置

```python
JWT_CONFIG = {
    "algorithm": "HS256",
    "secret": os.environ.get("JWT_SECRET"),  # 从环境变量读取
    "expires_in": 3600,  # 1 小时过期
    "issuer": "your-app",
    "audience": "your-users"
}
```

## 参考

- [JWT Security Best Practices](https://auth0.com/blog/jwt-security-best-practices/)
- [Attacking JWT Authentication](https://portswigger.net/web-security/jwt)
