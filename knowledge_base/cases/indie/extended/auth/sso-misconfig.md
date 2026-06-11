# SSO 配置错误 (SSO Misconfiguration)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-005 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

SAML/OAuth/OIDC 配置错误导致身份验证可被绕过，攻击者伪造身份或冒充任意用户登录系统。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **签名验证缺失**
  SAML 断言未验证签名，或接受自签名证书

- [ ] **回调 URL 未限制**
  OAuth `redirect_uri` 可被修改为攻击者控制的域名

- [ ] **邮箱映射漏洞**
  用户身份仅通过邮箱字段识别，允许 `email` 声明伪造

---

## 一句话防御

**严格验证 SAML 签名、限制 OAuth 回调域名白名单、使用唯一标识符（sub）而非邮箱识别用户。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| SAML 测试 | [SAMLtractor](https://github.com/actuator-saml/SAMLtractor) |
| OAuth 安全 | [OAuth 2.0 Security BCP](https://oauth.net/2/oauth-best-practice/) |
| OIDC 调试 | [OIDC Debugger](https://oidcdebugger.com/) |
| 学习资源 | [OWASP SAML Security](https://github.com/OWASP/www-project-saml-security) |

---

## 相关案例

- `email-verification-bypass.md` - 邮箱验证绕过
- `token-leakage.md` - 令牌泄露

---

## 参考资料

- [RFC 6819: OAuth 2.0 Threat Model](https://datatracker.ietf.org/doc/html/rfc6819)
- [SAML Security Cheat Sheet](https://github.com/OWASP/www-project-saml-security)
