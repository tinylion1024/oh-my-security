# 魔法链接滥用 (Magic Link Abuse)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-007 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

魔法链接令牌可预测、可重放或未及时失效，攻击者截获链接后无限次登录受害账户。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **令牌可预测**
  魔法链接令牌使用时间戳、自增 ID 等可预测值生成

- [ ] **令牌永不过期**
  魔法链接生成后无过期时间，可被长期滥用

- [ ] **令牌可重放**
  同一魔法链接可多次使用，使用后未立即失效

---

## 一句话防御

**魔法链接令牌使用加密安全随机值（≥128 位），单次使用后失效，有效期不超过 15 分钟。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 安全令牌 | [secrets.token_urlsafe](https://docs.python.org/3/library/secrets.html) |
| 魔法链接服务 | [Magic.link](https://magic.link/) |
| 安全审计 | [Burp Suite](https://portswigger.net/burp) |
| 学习资源 | [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) |

---

## 相关案例

- `email-verification-bypass.md` - 邮箱验证绕过
- `token-leakage.md` - 令牌泄露

---

## 参考资料

- [OWASP: Passwordless Authentication](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html#authentication-and-passwordless)
- [Magic Link Security Best Practices](https://magic.link/blog/magic-links-security)
