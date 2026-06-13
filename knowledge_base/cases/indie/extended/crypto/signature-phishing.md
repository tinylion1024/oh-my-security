# 签名钓鱼风险（Signature Phishing）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: crypto（加密资产安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业安全培训
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
被诱导签署恶意消息，授权攻击者转移你的代币或 NFT。

### 一分钟识别
签名请求是否有以下特征：
- [ ] 来源不明的网站
- [ ] 承诺免费空投
- [ ] 内容难以理解
- [ ] 钱包弹窗警告
- [ ] 要求多次签名
→ 勾选≥2项，可能为签名钓鱼

### 一句话防御
只在可信网站签名，使用钱包安全扫描，定期撤销授权。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 了解签名钓鱼原理
   - [ ] 检查现有授权
   - [ ] 撤销可疑授权

2. **短期行动**（本周可完成，免费）
   - [ ] 安装钱包安全插件
   - [ ] 建立签名习惯
   - [ ] 学习识别恶意签名

3. **长期行动**（规划中）
   - [ ] 定期撤销授权
   - [ ] 只使用可信 DApp

### 推荐工具
- **免费**：
  - Revoke.cash（撤销授权）
  - Rabby 钱包（安全扫描）
  - Wallet Guard

### 验证方法
- [ ] 测试步骤1：检查所有链的授权
- [ ] 测试步骤2：撤销测试授权
- [ ] 测试步骤3：验证钱包安全提示

---

## L2 小团队版（理解版）

### 恶意签名类型

| 类型 | 说明 | 危害 |
|------|------|------|
| Permit | 无 gas 授权 | 代币被转 |
| Seaport | NFT 授权 | NFT 被转 |
| EIP-2612 | 代币授权 | 代币被转 |
| setApprovalForAll | 全部授权 | 所有 NFT |
| 签名中继 | 免 gas 签名 | 资产被转 |

### 防护措施

```javascript
// 签名安全检查
const signatureSecurity = {
  // 签名前检查
  beforeSign: {
    verifyDomain: true,           // 验证域名
    checkContract: true,          // 检查合约
    scanContent: true,            // 扫描内容
    useHardwareWallet: true       // 使用硬件钱包
  },

  // 危险签名模式
  dangerousPatterns: [
    'permit',                     // Permit 签名
    'setApprovalForAll',          // 全部授权
    'safeTransferFrom',           // 转移签名
    'signTransaction'             // 交易签名
  ],

  // 授权管理
  approvalManagement: {
    defaultApproval: 0,           // 默认不授权
    maxApproval: 'exact',         // 精确金额
    regularRevoke: true           // 定期撤销
  }
};
```

### 检测清单

- [ ] 只在可信网站签名
- [ ] 使用钱包安全扫描
- [ ] 定期撤销授权
- [ ] 使用硬件钱包确认
- [ ] 理解签名内容

---

## 参考资料

### 工具
- [Revoke.cash](https://revoke.cash/)
- [Rabby Wallet](https://rabby.io/)
- [Unrekt](https://app.unrekt.net/)
