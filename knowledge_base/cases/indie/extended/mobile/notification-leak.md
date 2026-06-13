# 通知泄露风险（Notification Leak）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业通知管理
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
锁屏通知显示验证码、聊天内容等敏感信息，被他人看到导致隐私泄露或账号被盗。

### 一分钟识别
你的通知设置是否有以下特征：
- [ ] 锁屏显示通知内容
- [ ] 所有应用都显示详细通知
- [ ] 验证码短信直接显示
- [ ] 邮件预览显示正文
- [ ] 通知不自动隐藏
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
设置解锁后才显示通知内容，敏感应用隐藏通知详情。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 设置锁屏隐藏通知内容
   - [ ] 检查各应用通知权限
   - [ ] 关闭敏感应用锁屏通知

2. **短期行动**（本周可完成，免费）
   - [ ] 配置每个应用的通知显示方式
   - [ ] 测试通知隐私设置
   - [ ] 审查通知历史记录

3. **长期行动**（规划中）
   - [ ] 定期检查通知设置
   - [ ] 更新应用通知权限

### 推荐工具
- **免费**：
  - iOS 设置 > 通知 > 显示预览 > 解锁时
  - Android 设置 > 应用 > 通知

---

## L2 小团队版（理解版）

### 通知泄露场景

| 场景 | 泄露内容 | 风险等级 |
|------|---------|---------|
| 验证码短信 | 登录验证码 | 高 |
| 银行通知 | 交易金额、余额 | 高 |
| 邮件预览 | 邮件标题、内容 | 中 |
| 聊天消息 | 对话内容 | 中 |
| 日程提醒 | 行程信息 | 中 |
| 社交媒体 | 私信内容 | 中 |

### 安全配置

```javascript
// 通知安全策略
const notificationPolicy = {
  // 默认设置
  default: {
    showOnLockScreen: false,    // 锁屏不显示
    showContent: false,         // 不显示内容
    showPreview: 'when_unlocked'  // 解锁后显示预览
  },

  // 敏感应用
  sensitiveApps: ['banking', 'authenticator', 'email', 'messaging'],
  sensitiveConfig: {
    showOnLockScreen: false,
    showContent: false,
    hideSenderName: true,
    hideTitle: true
  },

  // 验证码处理
  otpHandling: {
    autoCopy: false,            // 不自动复制
    hideInNotification: true,   // 不显示
    requireUnlockToView: true   // 需解锁查看
  }
};
```

### 检测清单

- [ ] 锁屏不显示通知内容
- [ ] 敏感应用隐藏通知
- [ ] 验证码不显示在通知
- [ ] 通知预览设置为解锁时
- [ ] 定期审查应用通知权限

---

## 参考资料

### 技术文档
- [iOS 通知隐私设置](https://support.apple.com/en-us/HT202955)
- [Android 通知最佳实践](https://developer.android.com/develop/ui/views/notifications)
