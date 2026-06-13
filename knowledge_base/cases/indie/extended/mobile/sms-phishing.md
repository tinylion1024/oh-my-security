# 短信钓鱼风险（SMS Phishing）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: mobile（移动设备安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $10-50/月 | L3: 企业短信安全网关
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
收到伪装成银行、快递、官方机构的钓鱼短信，点击链接后账号被盗或手机感染木马。

### 一分钟识别
短信是否有以下特征：
- [ ] 包含短链接（bit.ly、t.cn等）
- [ ] 紧急催促语气（"立即验证"、"账户冻结"）
- [ ] 非官方号码发送
- [ ] 链接域名与官方不符
- [ ] 要求提供验证码/密码
→ 勾选≥2项，即为可疑钓鱼短信

### 一句话防御
不点击短信中的链接，通过官方渠道核实信息，使用短信过滤功能。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 开启手机短信过滤功能
   - [ ] 记住官方客服号码
   - [ ] 了解常见钓鱼手法

2. **短期行动**（本周可完成，免费）
   - [ ] 安装短信安全应用
   - [ ] 设置未知号码拦截
   - [ ] 向运营商举报钓鱼短信

3. **长期行动**（规划中）
   - [ ] 使用虚拟号码注册非重要服务
   - [ ] 定期安全教育

### 验证方法
- [ ] 测试步骤1：检查短信过滤是否生效
- [ ] 测试步骤2：验证官方号码保存是否完整
- [ ] 测试步骤3：测试举报渠道是否可用

---

## L2 小团队版（理解版）

### 场景还原
你的产品通过短信发送验证码和通知，但用户报告收到伪装成你公司的钓鱼短信：

**攻击流程**：
1. 攻击者收集用户手机号
2. 伪造官方短信模板
3. 使用伪基站或短信平台发送
4. 用户点击链接进入钓鱼网站
5. 用户输入账号密码
6. 攻击者实时使用凭据登录

### 钓鱼短信特征分析

**1. 内容特征**
```
常见话术:
- "您的账户异常，请立即验证"
- "您的快递无法投递，请确认地址"
- "您的积分即将过期，点击兑换"
- "银行系统升级，需重新验证"
- "中奖通知，点击领取"
```

**2. 链接特征**
```python
def analyze_sms_link(url):
    """分析短信链接风险"""
    risk_factors = []

    # 检查短链接
    short_domains = ['bit.ly', 't.cn', 'goo.gl', 'tinyurl']
    if any(d in url for d in short_domains):
        risk_factors.append('短链接隐藏真实目标')

    # 检查域名相似度
    if is_typosquatting(url, official_domain):
        risk_factors.append('域名与官方相似')

    # 检查 HTTPS
    if not url.startswith('https'):
        risk_factors.append('非安全连接')

    return risk_factors
```

### 防御实现

**1. 官方短信规范**
```javascript
// 安全的短信模板
const smsTemplate = {
  verification: {
    content: '【官方App】您的验证码是123456，5分钟内有效。请勿告知他人。',
    features: [
      '使用官方签名【xxx】',
      '不包含任何链接',
      '强调保密要求',
      '说明有效期'
    ]
  },

  notification: {
    content: '【官方App】您的订单已发货。查看详情请登录官方App或访问 www.official.com',
    features: [
      '完整显示官方域名',
      '建议通过App访问',
      '不使用短链接'
    ]
  }
};
```

**2. 钓鱼检测服务**
```javascript
// 集成钓鱼检测 API
class PhishingDetector {
  async checkUrl(url) {
    const result = await this.api.check({
      url,
      features: {
        domain_age: await this.getDomainAge(url),
        ssl_cert: await this.checkSSLCert(url),
        content_similarity: await this.compareWithOfficial(url)
      }
    });

    return {
      risk: result.risk_score,
      category: result.category,
      recommendation: result.recommendation
    };
  }
}
```

### 检测清单

- [ ] 官方短信使用规范签名
- [ ] 短信不包含可疑链接
- [ ] 用户可通过官方渠道验证
- [ ] 建立钓鱼短信举报机制
- [ ] 监控非官方短信发送
- [ ] 用户安全教育到位

---

## 参考资料

### 真实案例
- [2023 年短信钓鱼攻击报告](https://www.example.com/report)

### 技术文档
- [短信安全最佳实践](https://www.example.com/sms-security)
- [反钓鱼工作组成果](https://apwg.org/)
