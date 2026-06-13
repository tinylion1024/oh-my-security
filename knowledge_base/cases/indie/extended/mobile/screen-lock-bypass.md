# 锁屏绕过风险（Screen Lock Bypass）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业安全策略
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过技术手段或物理方式绕过锁屏保护，直接访问设备数据。

### 一分钟识别
你的锁屏是否有以下特征：
- [ ] 使用简单图案或4位密码
- [ ] 智能解锁功能开启过多
- [ ] 锁屏显示通知内容
- [ ] USB 调试常开
- [ ] 设备未更新系统
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
使用强密码锁屏，关闭不必要的智能解锁，隐藏锁屏通知内容。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 设置6位以上复杂密码
   - [ ] 关闭锁屏通知内容显示
   - [ ] 检查智能解锁设置

2. **短期行动**（本周可完成，免费）
   - [ ] 关闭不必要的信任设备
   - [ ] 更新系统到最新版本
   - [ ] 审查辅助功能设置

3. **长期行动**（规划中）
   - [ ] 定期检查锁屏安全
   - [ ] 了解新的绕过技术

---

## L2 小团队版（理解版）

### 常见绕过方式

| 方式 | 适用条件 | 防护措施 |
|------|---------|---------|
| 指纹痕迹 | 图案密码 | 使用复杂密码 |
| ADB 绕过 | USB调试开启 | 关闭USB调试 |
| 辅助功能 | 无障碍被滥用 | 审查无障碍权限 |
| 紧急呼叫漏洞 | 旧版系统 | 更新系统 |
| 智能解锁 | 信任设备被利用 | 审查信任设备 |
| 物理提取 | 设备未加密 | 启用加密 |

### 安全配置

```javascript
// 锁屏安全策略
const lockScreenPolicy = {
  lockType: 'password',  // 优先密码
  passwordComplexity: {
    minLength: 8,
    requireComplexity: true
  },
  autoLockTimeout: 1,  // 1分钟
  failedAttempts: {
    maxAttempts: 5,
    wipeAfter: 10  // 10次失败后擦除
  },
  smartLock: {
    trustedDevices: [],
    trustedPlaces: false,
    onBodyDetection: false
  },
  notifications: {
    showContent: false,  // 不显示内容
    hideSensitive: true
  }
};
```

### 检测清单

- [ ] 使用强密码锁屏
- [ ] 自动锁屏时间合理
- [ ] 锁屏通知内容隐藏
- [ ] USB 调试已关闭
- [ ] 智能解锁设备已审查
- [ ] 系统已更新

---

## 参考资料

### 技术文档
- [Android 锁屏安全](https://source.android.com/docs/security/features/lockscreen)
- [iOS 安全功能](https://www.apple.com/privacy/government-requests/)
