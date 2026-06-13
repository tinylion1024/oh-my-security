# 数据保留期限违规（Retention Violation）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: 免费 | L3: 数据治理方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
无限期保留数据，违反存储限制原则，增加数据泄露风险。

### 一分钟识别
你的数据管理是否有以下问题：
- [ ] 无数据保留策略
- [ ] 未定义各类数据期限
- [ ] 超期数据未删除
- [ ] 无自动删除机制
- [ ] 未告知用户保留期限
→ 勾选≥2项，即需立即关注

### 一句话防御
制定数据保留策略，设置自动删除，在隐私政策中说明。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 列出所有数据类型
   - [ ] 确定各类数据保留期限
   - [ ] 更新隐私政策

2. **短期行动**（本周可完成，免费）
   - [ ] 清理超期数据
   - [ ] 实现自动删除机制
   - [ ] 记录删除日志

3. **长期行动**（规划中）
   - [ ] 定期审查保留策略
   - [ ] 完善数据生命周期管理

---

## L2 小团队版（理解版）

### 数据保留原则

```
保留期限设定依据:
1. 法律法规要求
   - 税务数据: 5-10年
   - 医疗数据: 15-30年
   - 员工数据: 劳动法要求

2. 合同义务
   - 保修期相关
   - 争议解决需要

3. 商业需要
   - 客户关系维护
   - 服务改进

4. 最小化原则
   - 超出必要即删除
   - 匿名化处理
```

### 保留策略配置

```javascript
// 数据保留策略
const retentionPolicy = {
  // 用户数据
  userData: {
    accountInfo: {
      retention: 'account_lifetime_plus_30days',
      afterDeletion: 'anonymize'
    },
    usageLogs: {
      retention: '90_days',
      afterDeletion: 'delete'
    },
    marketingData: {
      retention: 'until_consent_withdrawn',
      afterDeletion: 'delete'
    }
  },

  // 业务数据
  businessData: {
    transactionRecords: {
      retention: '7_years',        // 税务要求
      reason: 'tax_regulation'
    },
    supportTickets: {
      retention: '3_years',
      reason: 'dispute_resolution'
    }
  },

  // 自动化
  automation: {
    enabled: true,
    frequency: 'daily',
    notifyBeforeDelete: 7         // 删除前通知天数
  }
};
```

### 检测清单

- [ ] 有数据保留策略
- [ ] 各类数据有期限
- [ ] 有删除机制
- [ ] 告知用户期限
- [ ] 记录删除操作

---

## 参考资料

### 指南
- [ICO 数据保留指南](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/principles/storage-limitation/)
