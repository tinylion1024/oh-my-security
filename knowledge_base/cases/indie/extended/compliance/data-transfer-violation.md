# 数据跨境传输违规（Data Transfer Violation）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $500-2000 | L3: 法律合规
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
向非欧盟认可国家传输数据缺乏保护措施，违反 GDPR 规定。

### 一分钟识别
你的服务是否有以下特征：
- [ ] 使用海外云服务
- [ ] 数据存储在国外
- [ ] 未告知用户跨境传输
- [ ] 未签署保护协议
- [ ] 未评估传输风险
→ 勾选≥2项，即需立即关注

### 一句话防御
使用合规云服务，签署标准合同条款，告知用户跨境传输。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 确认数据存储位置
   - [ ] 检查云服务商合规性
   - [ ] 更新隐私政策

2. **短期行动**（本周可完成，中成本）
   - [ ] 签署标准合同条款
   - [ ] 进行传输影响评估
   - [ ] 选择合规服务商

3. **长期行动**（规划中）
   - [ ] 定期评估传输风险
   - [ ] 关注法规变化

---

## L2 小团队版（理解版）

### 合法传输机制

| 机制 | 适用场景 | 要求 |
|------|---------|------|
| 充分性决定 | 传输到认可国家 | 无需额外措施 |
| 标准合同条款 | 常规传输 | 签署 SCC |
| 约束性企业规则 | 集团内部 | BCR 认证 |
| 用户同意 | 特定情况 | 明确告知同意 |
| 履行合同必要 | 合同履行 | 用户请求 |

### 认可国家列表

```
欧盟认可数据保护充分国家:
- 英国 (UK)
- 日本 (JP)
- 韩国 (KR)
- 加拿大 (CA)
- 阿根廷 (AR)
- 以色列 (IL)
- 新西兰 (NZ)
- 瑞士 (CH)
- 安道尔 (AD)
- 乌拉圭 (UY)
```

### 传输合规配置

```javascript
// 跨境传输合规
const transferCompliance = {
  // 传输评估
  assessment: {
    destinationCountry: '',       // 目的地国家
    adequacyDecision: false,      // 充分性认定
    protectionMeasures: [],       // 保护措施
    risks: []                     // 风险评估
  },

  // 保护措施
  safeguards: {
    scc: true,                    // 标准合同条款
    additionalMeasures: [],       // 额外措施
    transparency: true            // 透明度
  },

  // 用户告知
  disclosure: {
    inPrivacyPolicy: true,        // 隐私政策中说明
    purposes: [],                 // 传输目的
    safeguards: [],               // 保护措施
    rights: []                    // 用户权利
  }
};
```

### 检测清单

- [ ] 知晓数据存储位置
- [ ] 使用合规传输机制
- [ ] 告知用户跨境传输
- [ ] 签署必要协议
- [ ] 进行风险评估

---

## 参考资料

### 官方资源
- [欧盟委员会 SCC](https://ec.europa.eu/info/law/law-topic/data-protection/international-dimension-data-protection/standard-contractual-clauses-scc_en)
- [传输影响评估指南](https://edpb.europa.eu/our-work-tools/our-documents/recommendations/recommendations-012020-measures-supplement-transfer_en)
