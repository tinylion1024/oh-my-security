# SIM 卡调换攻击风险（SIM Swap）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业级身份验证
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者冒充你向运营商申请补办 SIM 卡，接管你的手机号和所有短信验证码，盗取账号。

### 一分钟识别
你是否存在以下风险：
- [ ] 手机号关联重要账号
- [ ] 运营商账户无额外密码
- [ ] 未设置 SIM 卡 PIN
- [ ] 社交媒体公开个人信息
- [ ] 使用短信验证码作为唯一认证
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
设置 SIM 卡 PIN 码，联系运营商设置账户密码，启用非短信二次认证。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 设置 SIM 卡 PIN 码
   - [ ] 联系运营商设置账户密码
   - [ ] 检查哪些账号使用短信验证

2. **短期行动**（本周可完成，免费）
   - [ ] 为重要账号启用 TOTP 验证器
   - [ ] 减少社交媒体个人信息公开
   - [ ] 了解运营商安全措施

3. **长期行动**（规划中）
   - [ ] 迁移到非短信认证方式
   - [ ] 考虑硬件安全密钥

### 推荐工具
- **免费**：
  - SIM 卡 PIN 设置（手机内置）
  - Google Authenticator / Authy
  - 运营商账户安全设置

### 验证方法
- [ ] 测试步骤1：验证 SIM PIN 已设置
- [ ] 测试步骤2：确认运营商账户有密码保护
- [ ] 测试步骤3：检查重要账号是否支持非短信 MFA

---

## L2 小团队版（理解版）

### 攻击流程

```
SIM 调换攻击步骤:
1. 信息收集: 攻击者收集目标个人信息（社交媒体、数据泄露）
2. 社会工程: 攻击者冒充目标联系运营商客服
3. 说服客服: 使用收集的信息通过身份验证
4. 办理补卡: 攻击者获得新 SIM 卡
5. 接管账号: 接收所有短信验证码，重置目标账号密码
```

### 防御措施

**1. SIM 卡保护**
```yaml
SIM_PIN:
  enabled: true
  default: "修改默认 PIN"
  pin_length: 4-8
  max_attempts: 3  # 3次错误后锁定

运营商账户:
  extra_password: "设置独立密码"
  security_questions: "设置安全问题"
  in_person_verification: "要求线下验证"
  notification: "办理业务时短信通知"
```

**2. 账号保护**
```javascript
// 账号安全配置
const accountSecurity = {
  authentication: {
    primary: 'password',
    mfa: {
      preferred: 'totp',           // 优先 TOTP
      fallback: 'backup_codes',    // 备用码
      sms_allowed: false           // 不允许短信 MFA
    }
  },

  // 监控告警
  monitoring: {
    new_device_login: true,
    password_change: true,
    phone_number_change: true,
    email_notification: true
  }
};
```

### 检测清单

- [ ] SIM 卡 PIN 已设置
- [ ] 运营商账户有密码保护
- [ ] 重要账号使用非短信 MFA
- [ ] 社交媒体个人信息已保护
- [ ] 设置账号登录通知
- [ ] 了解 SIM 调换攻击特征

---

## 参考资料

### 真实案例
- [2023 年 SIM 调换攻击案例](https://www.fbi.gov/how-we-can-help-you/safety-resources/scams-and-safety/common-scams-and-crimes/sim-swapping)

### 技术文档
- [NIST 数字身份指南 - 认证方式](https://pages.nist.gov/800-63-3/)
