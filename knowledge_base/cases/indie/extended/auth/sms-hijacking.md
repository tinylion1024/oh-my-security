# 短信劫持 (SMS Hijacking)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-001 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

攻击者通过 SIM 卡交换、短信拦截或 SS7 漏洞劫持短信验证码，绕过双因素认证完全接管账户。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **异常 SIM 卡活动**
  运营商通知 SIM 卡已更换，用户本人未操作

- [ ] **验证码延迟或未收到**
  正常请求验证码后长时间未收到，或收到多条未请求的验证码

- [ ] **账户异常登录**
  收到异地/异常设备登录通知，但本人未操作

---

## 一句话防御

**弃用短信作为唯一双因素认证，优先使用 TOTP/FIDO2 等不依赖运营商通道的认证方式。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 认证方案 | [FIDO2/WebAuthn](https://fidoalliance.org/fido2/) |
| TOTP 实现 | [Authlib TOTP](https://authlib.org/) |
| 检测工具 | [Twilio SIM Swap API](https://www.twilio.com/docs/verify/sim-swap) |
| 学习资源 | [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) |

---

## 相关案例

- `token-leakage.md` - 令牌泄露
- `account-enumeration.md` - 账号枚举

---

## 参考资料

- [NIST: Deprecating SMS for OTP](https://pages.nist.gov/800-63-3/sp800-63b.html#sec5)
- [FIDO Alliance Whitepaper](https://fidoalliance.org/white-paper-multi-device-fido-credentials/)
