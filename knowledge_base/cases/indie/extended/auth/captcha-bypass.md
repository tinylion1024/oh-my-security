# 验证码绕过 (CAPTCHA Bypass)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-010 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

验证码实现存在逻辑漏洞或可被自动化工具破解，攻击者绕过保护进行暴力破解、账号枚举或自动化注册。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **验证码可重用**
  同一验证码可多次提交，或验证后未失效

- [ ] **客户端验证**
  验证码验证仅在前端进行，后端未校验

- [ ] **验证码易破解**
  图形验证码字符简单、扭曲不足，可被 OCR 轻松识别

---

## 一句话防御

**后端强制验证码校验，单次使用后失效，优先使用行为验证或第三方验证服务（reCAPTCHA/hCaptcha）。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 验证码服务 | [hCaptcha](https://www.hcaptcha.com/) |
| 验证码服务 | [Google reCAPTCHA](https://www.google.com/recaptcha/) |
| OCR 破解测试 | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) |
| 学习资源 | [OWASP CAPTCHA Guide](https://owasp.org/www-community/controls/CAPTCHA) |

---

## 相关案例

- `account-enumeration.md` - 账号枚举
- `admin-default-credentials.md` - 管理员默认凭据

---

## 参考资料

- [OWASP: CAPTCHA Security](https://owasp.org/www-community/controls/CAPTCHA)
- [Google reCAPTCHA Best Practices](https://developers.google.com/recaptcha/docs/best_practices)
