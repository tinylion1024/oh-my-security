# 数据泄露通知违规（Breach Notification）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $500-2000 | L3: 应急响应团队
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
数据泄露后未在 72 小时内通知监管机构，面临额外罚款。

### 一分钟识别
你的应急准备是否有以下问题：
- [ ] 无泄露响应计划
- [ ] 无通知模板
- [ ] 未指定联系人
- [ ] 无泄露记录机制
- [ ] 未进行演练
→ 勾选≥2项，即需立即准备

### 一句话防御
制定泄露响应计划，准备通知模板，确保 72 小时内通知。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 制定泄露响应计划
   - [ ] 指定 DPO/联系人
   - [ ] 确定监管机构联系方式

2. **短期行动**（本周可完成，免费）
   - [ ] 准备通知模板
   - [ ] 建立泄露记录机制
   - [ ] 团队培训

3. **长期行动**（规划中）
   - [ ] 定期演练
   - [ ] 完善响应流程

---

## L2 小团队版（理解版）

### 泄露通知要求

```
监管机构通知（72小时内）:
- 泄露性质和类别
- 受影响数据主体数量
- DPO 联系方式
- 泄露可能后果
- 已采取的措施

数据主体通知（无不当延迟）:
- 泄露性质
- DPO 联系方式
- 可能后果
- 用户可采取的措施
```

### 泄露响应流程

```javascript
// 数据泄露响应计划
const breachResponse = {
  // 发现与记录
  detection: {
    logDiscovery: true,           // 记录发现时间
    initialAssessment: true,      // 初步评估
    classifySeverity: true        // 分类严重性
  },

  // 遏制与分析
  containment: {
    stopBreach: true,             // 止损
    preserveEvidence: true,       // 保全证据
    assessScope: true             // 评估范围
  },

  // 通知决策
  notification: {
    notifyAuthority: {
      within: '72_hours',         // 72小时内
      threshold: 'risk_to_rights' // 风险阈值
    },
    notifySubjects: {
      threshold: 'high_risk'      // 高风险阈值
    }
  },

  // 记录与改进
  documentation: {
    logAllActions: true,          // 记录所有行动
    rootCauseAnalysis: true,      // 根因分析
    improvementPlan: true         // 改进计划
  }
};
```

### 检测清单

- [ ] 有泄露响应计划
- [ ] 有通知模板
- [ ] 指定了联系人
- [ ] 有记录机制
- [ ] 进行过演练

---

## 参考资料

### 指南
- [ICO 泄露报告指南](https://ico.org.uk/for-organisations/report-a-breach/)
- [EDPB 泄露通知指南](https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-012021-examples-regarding-data-breach-notification_en)
