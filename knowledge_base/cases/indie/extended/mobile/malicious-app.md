# 恶意 App 风险（Malicious App）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $50-200/年 | L3: 企业安全方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
下载了伪装成正常应用的恶意 App，导致隐私数据被窃取、设备被控制或财务损失。

### 一分钟识别
App 是否有以下特征：
- [ ] 非官方商店下载
- [ ] 评分低或评论异常
- [ ] 请求过多敏感权限
- [ ] 界面粗糙或抄袭
- [ ] 频繁弹窗广告
→ 勾选≥2项，即为可疑恶意 App

### 一句话防御
只从官方应用商店下载，检查开发者信息和评价，拒绝权限要求过度的应用。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查已安装应用的来源
   - [ ] 卸载可疑应用
   - [ ] 开启应用安全扫描

2. **短期行动**（本周可完成，免费）
   - [ ] 检查所有应用的开发者信息
   - [ ] 清理长期未使用的应用
   - [ ] 安装安全防护软件

3. **长期行动**（规划中）
   - [ ] 建立应用白名单制度
   - [ ] 定期安全审查

### 推荐工具
- **免费**：
  - Google Play Protect (Android 内置)
  - iOS App Store 审核
  - VirusTotal (在线扫描)

### 验证方法
- [ ] 测试步骤1：验证应用来源是否为官方商店
- [ ] 测试步骤2：检查应用评分和评论
- [ ] 测试步骤3：审查应用权限请求

---

## L2 小团队版（理解版）

### 恶意 App 类型

| 类型 | 行为 | 危害等级 |
|------|------|---------|
| 间谍软件 | 窃取数据、监控行为 | 高 |
| 勒索软件 | 加密数据、勒索赎金 | 极高 |
| 广告软件 | 强制弹窗、消耗流量 | 中 |
| 木马 | 远程控制、后门 | 高 |
| 银行木马 | 窃取金融信息 | 极高 |
| 挖矿软件 | 消耗资源挖矿 | 中 |

### 检测特征

```javascript
// 恶意 App 检测指标
const maliciousIndicators = {
  // 安装来源
  source: {
    trusted: ['google_play', 'app_store', 'official_website'],
    suspicious: ['third_party_store', 'unknown_apk', 'direct_download']
  },

  // 行为特征
  behavior: {
    high_risk: [
      'request_device_admin',      // 请求设备管理员
      'accessibility_service',     // 无障碍服务
      'overlay_attack',            // 覆盖攻击
      'sms_intercept',             // 短信拦截
      'notification_listener'      // 通知监听
    ],
    medium_risk: [
      'excessive_permissions',     // 过多权限
      'hidden_icon',               // 隐藏图标
      'auto_start',                // 自启动
      'background_high_traffic'    // 后台高流量
    ]
  },

  // 开发者特征
  developer: {
    suspicious: [
      'new_account',               // 新注册账号
      'multiple_similar_apps',     // 多个相似应用
      'fake_reviews',              // 虚假评论
      'no_website'                 // 无官方网站
    ]
  }
};
```

### 防御措施

1. **下载前检查**
   - 验证开发者信息
   - 检查评分和评论
   - 查看下载量
   - 搜索应用名 + "恶意"

2. **安装后监控**
   - 观察权限请求
   - 监控电池消耗
   - 检查网络流量
   - 注意异常行为

### 检测清单

- [ ] 所有应用来自官方商店
- [ ] 已检查开发者信息
- [ ] 应用权限合理
- [ ] 无异常电池消耗
- [ ] 无异常网络流量
- [ ] 定期清理不常用应用

---

## 参考资料

### 技术文档
- [Android 应用安全最佳实践](https://developer.android.com/topic/security/best-practices)
- [iOS 应用安全指南](https://developer.apple.com/documentation/security)
