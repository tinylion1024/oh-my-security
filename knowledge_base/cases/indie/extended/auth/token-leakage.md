# 令牌泄露 (Token Leakage)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-003 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

认证令牌通过 URL 参数、日志文件、Referer 头或错误信息意外泄露，导致攻击者劫持用户会话。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **令牌出现在 URL 中**
  访问日志、浏览器历史记录、第三方统计工具中可见明文令牌

- [ ] **Referer 头泄露**
  外部链接请求的 `Referer` 头中携带认证令牌

- [ ] **错误信息暴露**
  服务器错误页面、调试信息或 API 响应中包含令牌值

---

## 一句话防御

**令牌仅通过 HttpOnly+Secure Cookie 或 Authorization 头传递，永不在 URL、日志、错误信息中出现。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 日志脱敏 | [log4j Pattern Layout](https://logging.apache.org/log4j/2.x/manual/layouts.html) |
| Cookie 安全 | [OWASP Cookie Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| 日志扫描 | [gitleaks](https://github.com/gitleaks/gitleaks) |
| 学习资源 | [JWT Best Practices](https://auth0.com/blog/jwt-authentication-best-practices/) |

---

## 相关案例

- `email-verification-bypass.md` - 邮箱验证绕过
- `magic-link-abuse.md` - 魔法链接滥用

---

## 参考资料

- [OWASP: Sensitive Data Exposure](https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure)
- [RFC 6750: Bearer Token Usage](https://datatracker.ietf.org/doc/html/rfc6750)
