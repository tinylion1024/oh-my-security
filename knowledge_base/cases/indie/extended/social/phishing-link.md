# 钓鱼链接风险（Phishing Link）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: social（社媒账号安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $50-200 | L3: 安全培训方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
社媒上的钓鱼链接诱导你输入账号密码，导致账号被盗。

### 一分钟识别
链接是否有以下特征：
- [ ] 短链接无法看到真实地址
- [ ] 域名与官方相似但不完全相同
- [ ] 要求登录才能查看内容
- [ ] 承诺免费赠品或抽奖
- [ ] 紧急催促点击
→ 勾选≥2项，即为可疑钓鱼链接

### 一句话防御
不点击不明链接，检查域名真伪，通过官方渠道访问服务。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 了解常见钓鱼手法
   - [ ] 安装链接安全检测工具
   - [ ] 养成检查域名习惯

2. **短期行动**（本周可完成，免费）
   - [ ] 教育团队成员识别钓鱼
   - [ ] 设置登录通知
   - [ ] 启用二次认证

3. **长期行动**（规划中）
   - [ ] 定期安全培训
   - [ ] 建立可疑链接报告机制

---

## L2 小团队版（理解版）

### 常见钓鱼手法

```
社媒钓鱼形式:
1. "查看谁看了你的主页"
2. "你被 @提及了"
3. "账号被举报，点击申诉"
4. "免费获得认证"
5. "中奖通知"
6. "内容被删除，点击申诉"
```

### 防护实现

```javascript
// 链接安全检测
class LinkSecurityChecker {
  async checkLink(url) {
    const result = {
      safe: true,
      risks: []
    };

    // 检查短链接
    if (this.isShortUrl(url)) {
      const expanded = await this.expandShortUrl(url);
      url = expanded;
      result.risks.push('短链接已展开');
    }

    // 检查域名
    const domain = new URL(url).hostname;
    if (!this.isOfficialDomain(domain)) {
      result.safe = false;
      result.risks.push('非官方域名');
    }

    // 检查钓鱼数据库
    if (await this.isInPhishingDatabase(url)) {
      result.safe = false;
      result.risks.push('已被标记为钓鱼网站');
    }

    return result;
  }

  isOfficialDomain(domain) {
    const officialDomains = [
      'instagram.com',
      'twitter.com',
      'x.com',
      'facebook.com',
      'tiktok.com'
    ];
    return officialDomains.some(d => domain === d || domain.endsWith('.' + d));
  }
}
```

### 检测清单

- [ ] 不点击可疑短链接
- [ ] 检查域名是否为官方
- [ ] 启用二次认证
- [ ] 设置登录通知
- [ ] 定期检查授权应用

---

## 参考资料

### 工具
- [VirusTotal](https://www.virustotal.com/)
- [URLVoid](https://www.urlvoid.com/)
- [Google 安全浏览](https://safebrowsing.google.com/)
