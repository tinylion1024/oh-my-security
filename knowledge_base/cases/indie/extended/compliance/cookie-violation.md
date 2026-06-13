# Cookie 违规风险（Cookie Violation）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $100-500 | L3: Cookie 管理平台
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
未获得同意就设置非必要 Cookie，违反 ePrivacy 和 GDPR。

### 一分钟识别
你的 Cookie 使用是否有以下问题：
- [ ] 无 Cookie 横幅
- [ ] 只有"接受"按钮
- [ ] 同意前已设置非必要 Cookie
- [ ] 无 Cookie 管理页面
- [ ] 预先勾选所有选项
→ 勾选≥2项，即需立即整改

### 一句话防御
先同意后设置 Cookie，提供接受和拒绝两个选项。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 实施 Cookie 横幅
   - [ ] 添加拒绝按钮
   - [ ] 同意前不设置非必要 Cookie

2. **短期行动**（本周可完成，免费）
   - [ ] 创建 Cookie 设置页面
   - [ ] 分类管理 Cookie
   - [ ] 记录用户偏好

3. **长期行动**（规划中）
   - [ ] 定期审查 Cookie 使用
   - [ ] 最小化非必要 Cookie

---

## L2 小团队版（理解版）

### Cookie 分类

| 类型 | 说明 | 同意要求 |
|------|------|---------|
| 必要 Cookie | 服务运行必需 | 无需同意 |
| 功能 Cookie | 记住用户偏好 | 需要同意 |
| 分析 Cookie | 统计用户行为 | 需要同意 |
| 营销 Cookie | 个性化广告 | 需要同意 |

### Cookie 合规实现

```javascript
// Cookie 合规管理
const cookieCompliance = {
  // 横幅设计
  banner: {
    showOnFirstVisit: true,       // 首次访问显示
    acceptButton: true,           // 接受按钮
    rejectButton: true,           // 拒绝按钮（同等突出）
    customizeButton: true,        // 自定义按钮
    noPreChecked: true            // 不预先勾选
  },

  // 同意前行为
  beforeConsent: {
    onlyEssentialCookies: true,   // 仅必要 Cookie
    noThirdPartyTags: true        // 无第三方标签
  },

  // 同意后行为
  afterConsent: {
    respectChoice: true,          // 尊重用户选择
    categories: {
      necessary: true,            // 必要
      functional: false,          // 功能（用户选择）
      analytics: false,           // 分析（用户选择）
      marketing: false            // 营销（用户选择）
    }
  },

  // 管理
  management: {
    settingsPage: true,           // 设置页面
    easyAccess: true,             // 易于访问
    changeAnytime: true           // 随时更改
  }
};
```

### 检测清单

- [ ] 有 Cookie 横幅
- [ ] 有拒绝按钮
- [ ] 同意前无非必要 Cookie
- [ ] 有 Cookie 管理页面
- [ ] 记录用户偏好

---

## 参考资料

### 工具
- [Cookiebot](https://www.cookiebot.com/)
- [OneTrust](https://www.onetrust.com/)
- [Osano](https://www.osano.com/)
