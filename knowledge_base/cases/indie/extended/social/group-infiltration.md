# 群组渗透风险（Group Infiltration）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: social（社媒账号安全）
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业群组管理
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
陌生人加入你的私密群组，窃取信息或进行社会工程攻击。

### 一分钟识别
你的群组是否有以下特征：
- [ ] 入群无需审核
- [ ] 管理员权限分散
- [ ] 历史消息公开
- [ ] 未定期清理成员
- [ ] 敏感信息讨论
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
设置入群审核，定期清理成员，不在群组讨论敏感信息。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 开启入群审核
   - [ ] 检查群成员列表
   - [ ] 设置群组隐私

2. **短期行动**（本周可完成，免费）
   - [ ] 清理不活跃成员
   - [ ] 制定群规
   - [ ] 限制管理员权限

3. **长期行动**（规划中）
   - [ ] 定期成员审查
   - [ ] 建立群组管理制度

---

## L2 小团队版（理解版）

### 群组风险分析

| 风险类型 | 说明 | 影响 |
|---------|------|------|
| 信息泄露 | 敏感讨论被窃取 | 商业损失 |
| 社会工程 | 收集信息进行诈骗 | 员工受害 |
| 恶意灌水 | 广告垃圾信息 | 效率降低 |
| 竞争对手 | 获取商业情报 | 竞争劣势 |

### 安全配置

```javascript
// 群组安全策略
const groupSecurity = {
  // 准入控制
  accessControl: {
    joinApproval: true,           // 入群审核
    inviteOnly: true,             // 仅邀请加入
    verifyMembers: true,          // 验证成员身份
    maxMembers: 200               // 成员上限
  },

  // 权限管理
  permissions: {
    adminCount: 3,                // 管理员数量
    messageDelete: 'admin',       // 仅管理员删消息
    memberRemove: 'admin',        // 仅管理员移除成员
    invitePermission: 'admin'     // 仅管理员邀请
  },

  // 内容控制
  contentControl: {
    historyVisibility: 'limited', // 限制历史可见
    messageRetention: 30,         // 消息保留天数
    linkBlocking: true            // 阻止链接
  }
};
```

### 检测清单

- [ ] 入群需要审核
- [ ] 管理员权限明确
- [ ] 历史消息受限
- [ ] 定期清理成员
- [ ] 不讨论敏感信息

---

## 参考资料

### 平台资源
- [Telegram 群组管理](https://telegram.org/blog#groups)
- [WhatsApp 群组设置](https://faq.whatsapp.com/general/chats/about-group-chat/)
