# 员工数据处理违规（Employee Data）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: compliance（合规自查）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $200-1000 | L3: HR 合规系统
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
不当处理员工数据，如过度监控，违反劳动法和个人数据保护法。

### 一分钟识别
你的员工数据处理是否有以下问题：
- [ ] 无员工隐私政策
- [ ] 未告知监控范围
- [ ] 收集非必要数据
- [ ] 监控超出必要范围
- [ ] 员工数据保护不足
→ 勾选≥2项，即需立即关注

### 一句话防御
制定员工隐私政策，告知监控范围，最小化数据收集。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 制定员工隐私政策
   - [ ] 审查监控范围
   - [ ] 告知员工数据处理情况

2. **短期行动**（本周可完成，免费）
   - [ ] 限制数据访问权限
   - [ ] 实施数据保护措施
   - [ ] 员工培训

3. **长期行动**（规划中）
   - [ ] 定期审查员工数据处理
   - [ ] 建立数据治理体系

---

## L2 小团队版（理解版）

### 员工数据处理原则

```
合法性基础:
- 劳动合同履行
- 法定义务
- 合法利益（需评估）

监控限制:
- 必须告知员工
- 必须有必要性
- 不能监控私人通讯
- 数据必须安全存储
```

### 员工数据保护配置

```javascript
// 员工数据处理策略
const employeeDataProtection = {
  // 数据分类
  dataCategories: {
    necessary: ['姓名', '联系方式', '银行账户', '身份证号'],
    optional: ['紧急联系人', '家庭住址'],
    sensitive: ['健康状况', '宗教信仰']  // 需额外保护
  },

  // 监控政策
  monitoring: {
    allowed: {
      workDeviceUsage: true,      // 工作设备使用
      workingTime: true,          // 工作时间
      securityLogs: true          // 安全日志
    },
    prohibited: {
      privateCommunication: true, // 私人通讯
      personalDevices: true,      // 个人设备
      offHoursActivity: true      // 非工作时间活动
    }
  },

  // 告知义务
  disclosure: {
    purpose: true,                // 处理目的
    scope: true,                  // 监控范围
    retention: true,              // 保留期限
    rights: true                  // 员工权利
  },

  // 安全措施
  security: {
    accessControl: true,          // 访问控制
    encryption: true,             // 加密
    auditLog: true                // 审计日志
  }
};
```

### 检测清单

- [ ] 有员工隐私政策
- [ ] 告知了监控范围
- [ ] 数据收集最小化
- [ ] 有访问控制
- [ ] 员工知晓权利

---

## 参考资料

### 指南
- [ICO 员工监控指南](https://ico.org.uk/for-organisations/guide-to-data-protection/employment/)
- [中国劳动合同法](http://www.npc.gov.cn/npc/c2193/200706/0fd7e65b7d8c4dd69b9c540c52b96e5f.shtml)
