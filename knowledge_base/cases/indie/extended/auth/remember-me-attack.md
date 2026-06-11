# 记住我功能攻击 (Remember Me Attack)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-008 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

"记住我"令牌设计不当，导致令牌可预测、长期有效或可重放，攻击者窃取后持久化访问受害账户。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **令牌可预测**
  记住我令牌基于用户 ID、时间戳等可预测值生成

- [ ] **令牌永不过期**
  "记住我"令牌无过期时间，或过期时间过长（>30 天）

- [ ] **令牌窃取风险**
  令牌存储在非 HttpOnly Cookie，易被 XSS 窃取

---

## 一句话防御

**记住我令牌使用加密安全随机值，存储于 HttpOnly+Secure Cookie，绑定设备指纹，有效期不超过 30 天。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 安全 Cookie | [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| 设备指纹 | [FingerprintJS](https://github.com/fingerprintjs/fingerprintjs) |
| 令牌管理 | [Authlib](https://authlib.org/) |
| 学习资源 | [PortSwigger: Session Management](https://portswigger.net/web-security/authentication) |

---

## 相关案例

- `token-leakage.md` - 令牌泄露
- `biometric-bypass.md` - 生物识别绕过

---

## 参考资料

- [OWASP: Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [RFC 6819: Remember Me Security](https://datatracker.ietf.org/doc/html/rfc6819)
