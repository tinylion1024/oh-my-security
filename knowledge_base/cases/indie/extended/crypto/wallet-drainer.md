# 钱包抽干攻击（Wallet Drainer）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: crypto（加密资产安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业安全方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
恶意合约一键转走你钱包中所有代币、NFT 和其他资产。

### 一分钟识别
你是否经历过：
- [ ] 点击了可疑链接
- [ ] 授权过不明合约
- [ ] 钱包资产突然消失
- [ ] 有不明转账记录
- [ ] 收到异常通知
→ 勾选≥2项，可能已被攻击

### 一句话防御
不点击可疑链接，使用钱包安全工具，硬件钱包确认。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查钱包授权
   - [ ] 撤销所有可疑授权
   - [ ] 检查交易记录

2. **短期行动**（本周可完成，免费）
   - [ ] 转移资产到新钱包
   - [ ] 安装安全插件
   - [ ] 学习防护知识

3. **长期行动**（规划中）
   - [ ] 使用硬件钱包
   - [ ] 建立安全习惯

### 推荐工具
- **免费**：
  - Revoke.cash
  - Rabby 钱包
  - Wallet Guard

### 验证方法
- [ ] 测试步骤1：检查授权列表
- [ ] 测试步骤2：检查交易历史
- [ ] 测试步骤3：验证钱包余额

---

## L2 小团队版（理解版）

### 钱包抽干原理

```
攻击流程:
1. 用户访问恶意网站
2. 连接钱包
3. 请求签名授权
4. 用户确认签名
5. 合约获得转账权限
6. 攻击者调用批量转账
7. 所有资产被转走
```

### 防护措施

```javascript
// 钱包防护策略
const walletProtection = {
  // 连接前检查
  beforeConnect: {
    verifyDomain: true,           // 验证域名
    checkContract: true,          // 检查合约
    useExtension: true            // 使用安全插件
  },

  // 签名检查
  beforeSign: {
    readContent: true,            // 阅读内容
    checkWarning: true,           // 检查警告
    useHardware: true             // 使用硬件钱包
  },

  // 定期检查
  monitoring: {
    checkApprovals: 'daily',      // 每日检查
    checkTransactions: 'daily',   // 每日检查
    alertOnSuspicious: true       // 异常告警
  }
};
```

### 检测清单

- [ ] 不连接可疑网站
- [ ] 使用安全插件
- [ ] 仔细阅读签名内容
- [ ] 使用硬件钱包
- [ ] 定期检查授权

---

## 参考资料

### 工具
- [Revoke.cash](https://revoke.cash/)
- [Rabby Wallet](https://rabby.io/)
- [Wallet Guard](https://walletguard.app/)
