# 数据主体权利违规（Subject Right Violation）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $200-1000 | L3: 法律合规
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
未响应用户数据请求，违反 GDPR 赋予的权利，面临罚款。

### 一分钟识别
你的产品是否支持：
- [ ] 用户请求数据副本
- [ ] 用户更正数据
- [ ] 用户删除数据
- [ ] 用户导出数据
- [ ] 用户反对处理
→ 勾选<3项，即需立即关注

### 一句话防御
建立用户数据请求响应机制，30天内响应，支持所有权利。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 设置数据请求接收渠道
   - [ ] 制定响应流程
   - [ ] 确定负责人

2. **短期行动**（本周可完成，免费）
   - [ ] 实现数据导出功能
   - [ ] 实现数据删除功能
   - [ ] 建立请求记录

3. **长期行动**（规划中）
   - [ ] 定期演练响应流程
   - [ ] 员工培训

---

## L2 小团队版（理解版）

### 用户权利清单

| 权利 | 说明 | 响应要求 |
|------|------|---------|
| 知情权 | 了解数据处理情况 | 隐私政策 |
| 访问权 | 获取数据副本 | 30天响应 |
| 更正权 | 修正不准确数据 | 及时响应 |
| 删除权 | 要求删除数据 | 30天响应 |
| 限制处理权 | 限制数据处理 | 30天响应 |
| 可携带权 | 结构化格式获取数据 | 30天响应 |
| 反对权 | 反对特定处理 | 及时响应 |

### 请求处理流程

```javascript
// 数据主体请求处理
const dsrHandling = {
  // 接收请求
  receipt: {
    channels: ['email', 'web_form'],
    verifyIdentity: true,         // 身份验证
    logRequest: true              // 记录请求
  },

  // 处理流程
  process: {
    acknowledge: '3_days',        // 3天内确认
    deadline: '30_days',          // 30天响应
    extension: '60_days',         // 复杂可延长
    notifyExtension: true         // 通知延长
  },

  // 响应类型
  responses: {
    access: 'provide_copy',       // 提供副本
    rectification: 'correct_data', // 更正数据
    erasure: 'delete_data',       // 删除数据
    portability: 'structured_format', // 结构化格式
    restriction: 'limit_processing',  // 限制处理
    objection: 'stop_processing'  // 停止处理
  }
};
```

### 检测清单

- [ ] 有请求接收渠道
- [ ] 有身份验证机制
- [ ] 30天内响应
- [ ] 支持所有权利
- [ ] 记录处理过程

---

## 参考资料

### 指南
- [ICO 数据主体权利](https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/)
