# 生物识别绕过 (Biometric Bypass)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-006 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

攻击者使用伪造的生物特征（指纹膜、深度伪造视频等）或利用实现漏洞绕过生物识别认证。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **缺乏活性检测**
  生物识别系统可被静态照片、录音或指纹膜欺骗

- [ ] **客户端验证**
  生物识别验证仅在客户端进行，服务端无二次校验

- [ ] **降级攻击**
  系统允许从生物识别降级到弱认证（如 PIN 码）且无额外保护

---

## 一句话防御

**服务端验证生物识别结果，结合活性检测与设备信任链，禁止无保护的认证降级。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 活性检测 | [Apple Face ID Liveness](https://developer.apple.com/documentation/localauthentication) |
| WebAuthn | [webauthn.io](https://webauthn.io/) |
| 深度伪造检测 | [DeepFaceLab Detection](https://github.com/iperov/DeepFaceLab) |
| 学习资源 | [NIST SP 800-63B Biometrics](https://pages.nist.gov/800-63-3/sp800-63b.html#sec5) |

---

## 相关案例

- `sms-hijacking.md` - 短信劫持
- `remember-me-attack.md` - 记住我功能攻击

---

## 参考资料

- [NIST: Biometric Authentication Requirements](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP: Mobile Biometric Authentication](https://owasp.org/www-project-mobile-security/)
