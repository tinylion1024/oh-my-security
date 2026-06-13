# 剪贴板劫持风险（Clipboard Hijack）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: crypto（加密资产安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $50-100 | L3: 企业安全方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
复制钱包地址时被恶意软件替换，转账到攻击者地址。

### 一分钟识别
你的设备是否有以下风险：
- [ ] 安装了可疑软件
- [ ] 无杀毒软件
- [ ] 不检查地址完整性
- [ ] 使用公共电脑转账
- [ ] 不验证转账地址
→ 勾选≥2项，即需立即关注

### 一句话防御
转账前检查地址首尾字符，使用硬件钱包确认。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 扫描设备恶意软件
   - [ ] 养成检查地址习惯
   - [ ] 使用二维码转账

2. **短期行动**（本周可完成，免费）
   - [ ] 安装杀毒软件
   - [ ] 使用硬件钱包
   - [ ] 建立安全转账流程

3. **长期行动**（规划中）
   - [ ] 定期安全扫描
   - [ ] 设备安全加固

### 推荐工具
- **免费**：
  - Windows Defender
  - Malwarebytes

- **硬件钱包**：
  - Ledger
  - Trezor

---

## L2 小团队版（理解版）

### 剪贴板劫持原理

```
攻击流程:
1. 恶意软件常驻后台
2. 监控剪贴板内容
3. 识别钱包地址模式
4. 替换为攻击者地址
5. 用户粘贴时使用错误地址
6. 资金转入攻击者账户
```

### 防护措施

```javascript
// 转账安全配置
const transferSecurity = {
  // 地址验证
  addressVerification: {
    checkFirstLast: true,         // 检查首尾
    compareQRCode: true,          // 对比二维码
    useHardwareWallet: true,      // 硬件钱包确认
    verifyOnDevice: true          // 设备上验证
  },

  // 安全措施
  securityMeasures: {
    antivirusInstalled: true,     // 安装杀毒
    noPiratedSoftware: true,      // 无盗版软件
    regularScans: true,           // 定期扫描
    safeComputing: true           // 安全计算习惯
  },

  // 转账流程
  transferProcess: {
    step1: 'copy_address',
    step2: 'check_first_last_4_chars',
    step3: 'verify_on_hardware_wallet',
    step4: 'confirm_transaction'
  }
};
```

### 检测清单

- [ ] 转账前检查地址
- [ ] 使用硬件钱包确认
- [ ] 设备有杀毒软件
- [ ] 无可疑软件
- [ ] 避免公共电脑

---

## 参考资料

### 工具
- [Malwarebytes](https://www.malwarebytes.com/)
- [Ledger](https://www.ledger.com/)
