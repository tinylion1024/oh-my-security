# 授权攻击风险（Approval Attack）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: crypto（加密资产安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业授权审计
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
曾授权的恶意合约随时可以转移你的代币或 NFT，即使授权已过去很久。

### 一分钟识别
你的授权是否有以下风险：
- [ ] 存在无限授权
- [ ] 授权过可疑合约
- [ ] 长期未检查授权
- [ ] 不记得授权来源
- [ ] 多链都有授权
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
立即检查并撤销所有授权，以后只授权精确金额。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查 Ethereum 链授权
   - [ ] 撤销所有无限授权
   - [ ] 撤销可疑合约授权

2. **短期行动**（本周可完成，免费）
   - [ ] 检查所有链的授权
   - [ ] 清理旧授权
   - [ ] 建立授权检查习惯

3. **长期行动**（规划中）
   - [ ] 每周检查授权
   - [ ] 使用授权管理工具

### 推荐工具
- **免费**：
  - Revoke.cash
  - Etherscan Token Approvals
  - 各链区块浏览器

### 验证方法
- [ ] 测试步骤1：检查所有链授权
- [ ] 测试步骤2：撤销测试
- [ ] 测试步骤3：确认授权列表清洁

---

## L2 小团队版（理解版）

### 授权攻击原理

```
攻击流程:
1. 用户授权恶意合约
2. 合约获得转账权限
3. 攻击者随时可调用
4. 用户资产被转移
5. 无需私钥签名
```

### 安全配置

```javascript
// 授权安全策略
const approvalSecurity = {
  // 授权原则
  principles: {
    minApproval: true,            // 最小授权
    exactAmount: true,            // 精确金额
    revokeAfterUse: true,         // 用后撤销
    verifyContract: true          // 验证合约
  },

  // 检查频率
  monitoring: {
    checkFrequency: 'weekly',     // 每周检查
    alertOnInfinite: true,        // 无限授权警告
    alertOnNew: true              // 新授权警告
  },

  // 撤销工具
  revokeTools: [
    'https://revoke.cash',
    'https://etherscan.io/tokenapprovalchecker'
  ]
};
```

### 检测清单

- [ ] 定期检查所有链授权
- [ ] 无无限授权存在
- [ ] 不明合约已撤销
- [ ] 新授权后立即检查
- [ ] 使用精确金额授权

---

## 参考资料

### 工具
- [Revoke.cash](https://revoke.cash/)
- [Etherscan Approvals](https://etherscan.io/tokenapprovalchecker)
- [Allowance Checker](https://celsius.network/)
