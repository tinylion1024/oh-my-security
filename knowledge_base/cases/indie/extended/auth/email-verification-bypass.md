# 邮箱验证绕过 (Email Verification Bypass)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-002 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

攻击者通过逻辑漏洞、响应篡改或协议缺陷绕过邮箱验证流程，使用虚假邮箱注册账户或接管他人账户。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **验证状态不一致**
  后端数据库显示 `verified=false`，但前端显示已验证状态

- [ ] **绕过验证参数**
  请求中包含 `verified=true`、`bypass=1` 等可疑参数

- [ ] **验证码复用**
  同一验证链接/令牌可多次使用，或验证后未失效

---

## 一句话防御

**验证令牌使用加密安全的随机值（≥128 位），单次使用后立即失效，后端强制验证状态检查。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 安全令牌生成 | [secrets.token_urlsafe](https://docs.python.org/3/library/secrets.html) |
| 邮件测试 | [MailHog](https://github.com/mailhog/MailHog) |
| 协议分析 | [Burp Suite](https://portswigger.net/burp) |
| 学习资源 | [OWASP Auth Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) |

---

## 相关案例

- `magic-link-abuse.md` - 魔法链接滥用
- `token-leakage.md` - 令牌泄露

---

## 参考资料

- [OWASP: Broken Authentication](https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication)
- [PortSwigger: Email Verification Bypass](https://portswigger.net/web-security/authentication)
