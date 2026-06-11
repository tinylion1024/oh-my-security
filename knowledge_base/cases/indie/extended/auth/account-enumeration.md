# 账号枚举 (Account Enumeration)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-009 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

登录、注册、密码重置等功能返回差异化响应，攻击者枚举出有效账号用于后续定向攻击。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **差异化错误消息**
  登录时返回 "用户不存在" 与 "密码错误" 两种不同提示

- [ ] **响应时间差异**
  存在账号时响应快，不存在时响应慢（或反之）

- [ ] **注册泄露存在性**
  注册已存在邮箱时返回 "邮箱已被注册"

---

## 一句话防御

**统一错误消息（"用户名或密码错误"），统一响应时间，注册流程返回 "如邮箱有效将收到确认邮件"。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 枚举测试 | [Burp Suite Intruder](https://portswigger.net/burp/documentation/desktop/tools/intruder) |
| 响应时间分析 | [OWASP ZAP](https://www.zaproxy.org/) |
| 账号列表 | [SecLists Usernames](https://github.com/danielmiessler/SecLists/tree/master/Usernames) |
| 学习资源 | [PortSwigger: Username Enumeration](https://portswigger.net/web-security/authentication) |

---

## 相关案例

- `admin-default-credentials.md` - 管理员默认凭据
- `captcha-bypass.md` - 验证码绕过

---

## 参考资料

- [OWASP: Testing for Account Enumeration](https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account)
- [PortSwigger: Information Disclosure](https://portswigger.net/web-security/information-disclosure)
