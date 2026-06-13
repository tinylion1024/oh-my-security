# 剪贴板泄露风险（Clipboard Leak）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: 免费 | L3: 企业剪贴板管理
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
复制到剪贴板的密码、验证码、钱包地址等敏感信息被恶意 App 读取。

### 一分钟识别
你的剪贴板使用习惯是否有以下特征：
- [ ] 复制密码后不清理
- [ ] 使用普通输入法复制敏感信息
- [ ] 未设置剪贴板自动清理
- [ ] 多应用间频繁复制粘贴
- [ ] 复制钱包地址直接转账
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
敏感信息不通过剪贴板，使用密码管理器自动填充，定期清理剪贴板。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查哪些 App 能读取剪贴板
   - [ ] 安装剪贴板管理工具
   - [ ] 使用密码管理器

2. **短期行动**（本周可完成，免费）
   - [ ] 设置剪贴板自动清理
   - [ ] 减少剪贴板使用频率
   - [ ] 使用隐私输入法

3. **长期行动**（规划中）
   - [ ] 养成安全的剪贴板使用习惯

### 推荐工具
- **免费**：
  - iOS 14+ 剪贴板读取提示
  - Android 剪贴板管理器
  - 密码管理器自动填充

---

## L2 小团队版（理解版）

### 剪贴板风险场景

```
风险数据类型:
1. 密码 - 从密码管理器复制
2. 验证码 - 短信验证码复制
3. 钱包地址 - 加密货币转账
4. 私钥/助记词 - 钱包备份
5. 身份证号 - 表单填写
6. 银行卡号 - 支付信息
```

### 防护措施

```javascript
// 应用层剪贴板保护
class ClipboardSecurity {
  // 敏感内容检测
  isSensitiveContent(content) {
    const patterns = [
      /\b\d{16,19}\b/,  // 银行卡号
      /\b\d{15,18}\b/,  // 身份证号
      /^(0x)?[a-fA-F0-9]{40}$/,  // 以太坊地址
      /^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$/,  // 比特币地址
      /\b\d{6}\b/,  // 6位验证码
    ];
    return patterns.some(p => p.test(content));
  }

  // 安全复制
  async secureCopy(content, options = {}) {
    if (this.isSensitiveContent(content)) {
      // 使用安全剪贴板
      await this.copyToSecureClipboard(content);
      // 设置自动清理
      setTimeout(() => this.clearClipboard(), options.timeout || 30000);
    } else {
      await this.copyToClipboard(content);
    }
  }

  // 清理剪贴板
  clearClipboard() {
    navigator.clipboard.writeText('');
  }
}
```

### 检测清单

- [ ] 了解哪些 App 能读取剪贴板
- [ ] 使用密码管理器自动填充
- [ ] 设置剪贴板自动清理
- [ ] 不复制敏感信息
- [ ] 钱包地址验证后转账

---

## 参考资料

### 技术文档
- [iOS 14 剪贴板隐私功能](https://developer.apple.com/documentation/uikit/uipasteboard)
- [Android 剪贴板 API](https://developer.android.com/reference/android/content/ClipboardManager)
