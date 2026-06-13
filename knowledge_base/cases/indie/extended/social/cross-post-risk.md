# 跨平台风险（Cross-Post Risk）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: social（社媒账号安全）
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: 免费 | L3: 跨平台安全审计
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
多个社媒平台使用相同密码或关联账号，一个平台泄露导致所有平台受损。

### 一分钟识别
你的账号是否有以下特征：
- [ ] 多平台使用相同密码
- [ ] 绑定相同邮箱
- [ ] 绑定相同手机号
- [ ] 公开信息交叉关联
- [ ] 未启用各平台 MFA
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
每平台独立密码，关键账号独立邮箱，全面启用 MFA。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查密码复用情况
   - [ ] 为重要账号设置独立密码
   - [ ] 启用所有平台 MFA

2. **短期行动**（本周可完成，免费）
   - [ ] 使用密码管理器
   - [ ] 分离关键账号邮箱
   - [ ] 审查账号关联

3. **长期行动**（规划中）
   - [ ] 定期更换密码
   - [ ] 定期审查关联

---

## L2 小团队版（理解版）

### 跨平台风险分析

| 风险类型 | 说明 | 影响 |
|---------|------|------|
| 密码复用 | 一处泄露多处受害 | 连锁损失 |
| 账号关联 | 通过公开信息关联 | 隐私泄露 |
| 信息聚合 | 多平台信息拼图 | 身份盗用 |
| 权限连锁 | OAuth 连锁授权 | 全面失守 |

### 安全配置

```javascript
// 跨平台安全策略
const crossPlatformSecurity = {
  // 密码策略
  passwords: {
    unique: true,                 // 每平台独立
    complexity: 'high',           // 高复杂度
    manager: 'bitwarden',         // 使用密码管理器
    rotation: 90                  // 90天轮换
  },

  // 身份分离
  identitySeparation: {
    criticalAccounts: {           // 关键账号
      email: 'separate',          // 独立邮箱
      phone: 'separate'           // 独立手机
    },
    financialAccounts: {          // 金融账号
      email: 'separate',
      mfa: 'hardware'             // 硬件 MFA
    }
  },

  // MFA 配置
  mfa: {
    enableAll: true,              // 全面启用
    preferred: 'totp',            // 优先 TOTP
    backup: 'codes'               // 备用码
  }
};
```

### 检测清单

- [ ] 各平台独立密码
- [ ] 关键账号独立邮箱
- [ ] 所有关键账号启用 MFA
- [ ] 公开信息最小化
- [ ] 定期审查账号关联

---

## 参考资料

### 工具
- [Have I Been Pwned](https://haveibeenpwned.com/)
- [Bitwarden 密码管理器](https://bitwarden.com/)
- [Authy 验证器](https://authy.com/)
