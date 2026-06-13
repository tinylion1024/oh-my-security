# 假钱包风险（Fake Wallet）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: crypto（加密资产安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $50-200 | L3: 企业钱包安全
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
下载了假冒的钱包软件，私钥被窃取，资产被盗。

### 一分钟识别
你的钱包是否有以下风险：
- [ ] 非官方渠道下载
- [ ] 界面粗糙
- [ ] 要求输入助记词
- [ ] 评分低或评论异常
- [ ] 无官方认证
→ 勾选≥2项，可能为假钱包

### 一句话防御
只从官方网站下载钱包，验证签名，检查评价。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查钱包下载来源
   - [ ] 验证钱包签名
   - [ ] 检查版本是否最新

2. **短期行动**（本周可完成，免费）
   - [ ] 转移资产到安全钱包
   - [ ] 清理可疑钱包
   - [ ] 建立下载验证习惯

3. **长期行动**（规划中）
   - [ ] 只使用知名钱包
   - [ ] 定期检查钱包安全

### 推荐钱包
- **硬件钱包**：
  - Ledger (ledger.com)
  - Trezor (trezor.io)

- **软件钱包**：
  - MetaMask (metamask.io)
  - Rabby (rabby.io)

---

## L2 小团队版（理解版）

### 假钱包类型

| 类型 | 说明 | 危害 |
|------|------|------|
| 应用商店假货 | 仿冒官方应用 | 私钥被窃 |
| 钓鱼网站 | 模仿官网 | 助记词泄露 |
| 破解版钱包 | 带后门的钱包 | 资产被盗 |
| 仿冒硬件 | 假硬件钱包 | 预设助记词 |

### 验证方法

```javascript
// 钱包验证清单
const walletVerification = {
  // 下载验证
  download: {
    source: 'official_website',   // 官方网站
    domain: 'metamask.io',        // 验证域名
    https: true,                  // HTTPS
    signature: true               // 验证签名
  },

  // 应用验证
  application: {
    developer: 'verified',        // 验证开发者
    rating: '>4.5',               // 高评分
    downloads: '>1M',             // 高下载量
    reviews: 'legitimate'         // 真实评论
  },

  // 运行验证
  runtime: {
    noUnusualRequests: true,      // 无异常请求
    noSeedPhraseInput: true,      // 不要求输入助记词
    openSource: true              // 开源（可选）
  }
};
```

### 检测清单

- [ ] 从官方网站下载
- [ ] 验证开发者信息
- [ ] 检查评分和评论
- [ ] 验证应用签名
- [ ] 不输入已有助记词

---

## 参考资料

### 官方钱包
- [MetaMask](https://metamask.io/)
- [Ledger](https://www.ledger.com/)
- [Trezor](https://trezor.io/)
- [Rabby](https://rabby.io/)
