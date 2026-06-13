# 智能合约漏洞风险（Smart Contract Bug）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: crypto（加密资产安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: 免费 | L3: 审计服务
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
与有漏洞的智能合约交互，导致资产被盗或锁定。

### 一分钟识别
合约是否有以下特征：
- [ ] 未经过审计
- [ ] 代码未开源
- [ ] 新部署的合约
- [ ] TVL 高但时间短
- [ ] 社区有负面反馈
→ 勾选≥2项，即需谨慎交互

### 一句话防御
只与经过审计的开源合约交互，检查项目背景。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查常用合约是否审计
   - [ ] 撤销高风险合约授权
   - [ ] 了解审计报告含义

2. **短期行动**（本周可完成，免费）
   - [ ] 学习查看合约代码
   - [ ] 关注安全审计账号
   - [ ] 建立合约检查习惯

3. **长期行动**（规划中）
   - [ ] 定期审查合约交互
   - [ ] 关注安全公告

### 推荐工具
- **免费**：
  - Etherscan 合约验证
  - 审计报告查看

### 验证方法
- [ ] 测试步骤1：检查合约审计状态
- [ ] 测试步骤2：验证合约开源
- [ ] 测试步骤3：查看社区反馈

---

## L2 小团队版（理解版）

### 常见合约漏洞

| 漏洞类型 | 说明 | 影响 |
|---------|------|------|
| 重入攻击 | 函数被重复调用 | 资金被盗 |
| 整数溢出 | 数值计算错误 | 逻辑异常 |
| 权限绕过 | 访问控制缺陷 | 未授权操作 |
| 价格操控 | Oracle 被操纵 | 价格异常 |
| 闪电贷攻击 | 借贷被滥用 | 市场操纵 |

### 安全检查

```javascript
// 合约安全检查清单
const contractSecurity = {
  // 基础检查
  basics: {
    isVerified: true,             // 已验证
    isOpenSource: true,           // 开源
    isAudited: true,              // 已审计
    auditorReputation: 'top'      // 知名审计机构
  },

  // 风险指标
  riskIndicators: {
    contractAge: '>30days',       // 存在时间
    tvl: 'checked',               // TVL 检查
    communityTrust: 'high',       // 社区信任
    securityIncidents: 0          // 无安全事件
  },

  // 审计要点
  auditChecks: {
    auditFirm: ['Trail of Bits', 'OpenZeppelin', 'Consensys'],
    auditDate: '<1year',          // 一年内审计
    findingsResolved: true        // 发现已解决
  }
};
```

### 检测清单

- [ ] 合约已审计
- [ ] 代码已开源
- [ ] 运行时间足够
- [ ] 社区信任度高
- [ ] 无安全事件历史

---

## 参考资料

### 审计机构
- [Trail of Bits](https://www.trailofbits.com/)
- [OpenZeppelin](https://www.openzeppelin.com/)
- [Consensys Diligence](https://consensys.net/diligence/)
