# 儿童数据处理违规（Children Data）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $500-2000 | L3: 合规专家
- **独立开发者适用度**: ⭐⭐⭐ (3/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
未经监护人同意处理儿童数据，违反儿童保护法规。

### 一分钟识别
你的产品是否有以下风险：
- [ ] 无年龄验证机制
- [ ] 未获取监护人同意
- [ ] 未提供适龄隐私政策
- [ ] 默认设置不够隐私
- [ ] 向儿童推送广告
→ 勾选≥2项，即需立即关注

### 一句话防御
验证用户年龄，获取监护人同意，设置高隐私默认。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 评估是否可能有儿童用户
   - [ ] 实施年龄验证
   - [ ] 审查隐私设置默认值

2. **短期行动**（本周可完成，中成本）
   - [ ] 制定监护人同意流程
   - [ ] 创建适龄隐私政策
   - [ ] 禁止向儿童推送广告

3. **长期行动**（规划中）
   - [ ] 定期审查儿童保护措施
   - [ ] 员工培训

---

## L2 小团队版（理解版）

### 儿童数据处理要求

```
GDPR 要求:
1. 年龄验证
   - 13-16岁以下需监护人同意（各国不同）
   - 必须进行合理年龄验证

2. 监护人同意
   - 必须获得监护人同意
   - 必须验证监护人身份

3. 适龄信息
   - 使用儿童能理解的语言
   - 提供适龄的隐私政策

4. 特殊保护
   - 默认最高隐私设置
   - 禁止定向广告
   - 不出售儿童数据

5. 权利保障
   - 监护人可代为行使权利
   - 可要求删除儿童数据
```

### 儿童保护配置

```javascript
// 儿童数据保护策略
const childrenDataProtection = {
  // 年龄验证
  ageVerification: {
    method: 'self_declaration',   // 自声明
    additionalChecks: true,       // 额外检查
    logAttempts: true             // 记录尝试
  },

  // 监护人同意
  parentalConsent: {
    required: true,               // 必须获得
    verificationMethod: 'email',  // 验证方式
    recordConsent: true           // 记录同意
  },

  // 隐私设置
  privacyDefaults: {
    profileVisibility: 'private', // 私密
    dataCollection: 'minimal',    // 最小化
    thirdPartySharing: false      // 不共享
  },

  // 广告限制
  advertising: {
    targetedAds: false,           // 禁止定向广告
    contextualOnly: true          // 仅上下文广告
  }
};
```

### 检测清单

- [ ] 有年龄验证机制
- [ ] 有监护人同意流程
- [ ] 有适龄隐私政策
- [ ] 默认高隐私设置
- [ ] 禁止定向广告

---

## 参考资料

### 法规
- [COPPA (美国)](https://www.ftc.gov/enforcement/rules/rulemaking-regulatory-reform-proceedings/childrens-online-privacy-protection-rule)
- [GDPR 儿童数据](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/children/)
- [中国未成年人保护法](http://www.npc.gov.cn/npc/c30834/202010/acd8684a0c1b4a0b9c6b9f0e6d45e44c.shtml)
