# GDPR 违规风险（GDPR Violation）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $500-5000 | L3: 合规咨询 + 罚款
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
违反 GDPR 规定，面临高额罚款（最高年营收 4%）和法律诉讼。

### 一分钟识别
你的产品是否有以下风险：
- [ ] 未告知数据收集目的
- [ ] 无合法基础处理数据
- [ ] 未提供隐私政策
- [ ] 收集超过必要数据
- [ ] 未响应用户数据请求
→ 勾选≥2项，即需立即关注

### 一句话防御
制定隐私政策，获取有效同意，支持用户权利请求。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 发布隐私政策
   - [ ] 审查数据收集范围
   - [ ] 确定处理合法性基础

2. **短期行动**（本周可完成，免费）
   - [ ] 实现同意机制
   - [ ] 建立数据请求响应流程
   - [ ] 记录数据处理活动

3. **长期行动**（规划中）
   - [ ] 定期合规审查
   - [ ] 员工培训

---

## L2 小团队版（理解版）

### GDPR 核心要求

| 要求 | 说明 | 合规措施 |
|------|------|---------|
| 合法性 | 必须有合法基础 | 确定处理基础 |
| 目的限制 | 只为特定目的收集 | 明确告知目的 |
| 数据最小化 | 只收集必要数据 | 评估数据必要性 |
| 准确性 | 保持数据准确 | 提供更正机制 |
| 存储限制 | 不超期保留 | 制定保留策略 |
| 安全性 | 保护数据安全 | 实施安全措施 |

### 合规配置

```javascript
// GDPR 合规框架
const gdprCompliance = {
  // 数据处理记录
  processingRecords: {
    purposes: [],                 // 处理目的
    categories: [],               // 数据类别
    recipients: [],               // 接收方
    transfers: [],                // 跨境传输
    retention: [],                // 保留期限
    securityMeasures: []          // 安全措施
  },

  // 合法基础
  legalBasis: {
    consent: {                    // 同意
      freelyGiven: true,
      specific: true,
      informed: true,
      unambiguous: true
    },
    contract: [],                 // 合同
    legalObligation: [],          // 法定义务
    vitalInterests: [],           // 重要利益
    publicTask: [],               // 公共任务
    legitimateInterests: []       // 合法利益
  }
};
```

### 检测清单

- [ ] 有隐私政策
- [ ] 确定了合法基础
- [ ] 实现了同意机制
- [ ] 支持用户权利
- [ ] 记录了处理活动
- [ ] 实施了安全措施

---

## 参考资料

### 官方资源
- [GDPR 官方文本](https://gdpr.eu/)
- [ICO 指南](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/)
