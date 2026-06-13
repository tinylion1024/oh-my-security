# OAuth 滥用风险（OAuth Abuse）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: social（社媒账号安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业 OAuth 审计
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
授权恶意第三方应用访问你的社媒账号，导致数据泄露或账号被滥用。

### 一分钟识别
你的授权是否有以下特征：
- [ ] 授权后忘记撤销
- [ ] 授权来源不明的应用
- [ ] 未审查授权范围
- [ ] 长期未检查已授权应用
- [ ] 授权过多权限
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
定期审查已授权应用，只授权可信应用，及时撤销不需要的授权。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查所有平台的已授权应用
   - [ ] 撤销不再使用的应用授权
   - [ ] 检查可疑应用

2. **短期行动**（本周可完成，免费）
   - [ ] 建立授权审查习惯
   - [ ] 记录授权的应用清单
   - [ ] 设置授权提醒

3. **长期行动**（规划中）
   - [ ] 定期审查（每月）
   - [ ] 只使用官方应用

### 推荐工具
- **免费**：
  - 各平台设置中的已授权应用
  - 第三方权限管理工具

---

## L2 小团队版（理解版）

### OAuth 风险场景

| 风险类型 | 说明 | 影响 |
|---------|------|------|
| 过度授权 | 授权不必要的权限 | 数据泄露 |
| 恶意应用 | 钓鱼应用骗取授权 | 账号滥用 |
| 长期授权 | 忘记撤销旧授权 | 持续风险 |
| 数据收集 | 应用过度收集数据 | 隐私泄露 |

### 安全配置

```javascript
// OAuth 授权管理策略
const oauthPolicy = {
  // 授权前检查
  beforeAuthorize: {
    verifyAppSource: true,      // 验证应用来源
    checkPermissions: true,     // 检查权限范围
    readPrivacyPolicy: true,    // 阅读隐私政策
    limitScope: true            // 限制授权范围
  },

  // 授权管理
  management: {
    reviewFrequency: 'monthly',  // 每月审查
    revokeUnused: true,          // 撤销未使用应用
    logAuthorizations: true      // 记录授权历史
  },

  // 监控告警
  monitoring: {
    alertOnNewAuthorization: true,
    alertOnSensitiveAccess: true,
    alertOnSuspiciousActivity: true
  }
};
```

### 检测清单

- [ ] 已审查所有已授权应用
- [ ] 撤销了不再使用的授权
- [ ] 了解各应用授权范围
- [ ] 建立定期审查习惯
- [ ] 只授权可信应用

---

## 参考资料

### 平台资源
- [Facebook 应用设置](https://www.facebook.com/settings?tab=applications)
- [Twitter 应用设置](https://twitter.com/settings/sessions)
- [Google 账号权限](https://myaccount.google.com/permissions)
