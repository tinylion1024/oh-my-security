# 同意绕过风险（Consent Bypass）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $100-500 | L3: 合规整改
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
同意机制设计不当，被认定为无效同意，数据处理违法。

### 一分钟识别
你的同意机制是否有以下问题：
- [ ] 预先勾选同意框
- [ ] 捆绑同意多个目的
- [ ] 拒绝后无法使用
- [ ] 撤回比给予困难
- [ ] 同意前已收集数据
→ 勾选≥2项，即需立即整改

### 一句话防御
设计有效同意机制：自愿、具体、知情、明确、可撤回。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 取消预先勾选
   - [ ] 分离不同目的同意
   - [ ] 提供拒绝选项

2. **短期行动**（本周可完成，免费）
   - [ ] 实现同意撤回功能
   - [ ] 记录同意历史
   - [ ] 用户友好设计

3. **长期行动**（规划中）
   - [ ] 定期审查同意机制
   - [ ] 员工培训

---

## L2 小团队版（理解版）

### 有效同意要素

| 要素 | 要求 | 常见问题 |
|------|------|---------|
| 自愿性 | 拒绝不影响服务 | 绑定核心服务 |
| 具体性 | 每个目的单独同意 | 捆绑同意 |
| 知情性 | 用户理解同意内容 | 信息不充分 |
| 明确性 | 主动行为表达 | 预勾选 |
| 可撤回性 | 可随时撤回 | 撤回困难 |

### 同意机制实现

```javascript
// 合规同意管理
const consentManagement = {
  // 同意请求
  request: {
    separateByPurpose: true,      // 按目的分离
    clearLanguage: true,          // 清晰语言
    noPreChecked: true,           // 不预勾选
    equalProminence: true         // 同等突出拒绝
  },

  // 同意记录
  records: {
    timestamp: true,              // 时间戳
    purposes: true,               // 目的
    version: true,                // 政策版本
    source: true                  // 来源
  },

  // 撤回机制
  withdrawal: {
    easyAccess: true,             // 易于访问
    sameChannel: true,            // 同等渠道
    immediateEffect: true         // 立即生效
  }
};
```

### 检测清单

- [ ] 无预先勾选
- [ ] 各目的独立同意
- [ ] 拒绝不影响核心服务
- [ ] 撤回机制完善
- [ ] 记录同意历史

---

## 参考资料

### 指南
- [ICO 同意指南](https://ico.org.uk/for-organisations/guide-to-pecr/guidance-on-the-use-of-cookies-and-similar-technologies/)
- [EDPB 同意指南](https://edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-052020-consent-under-regulation-2016679_en)
