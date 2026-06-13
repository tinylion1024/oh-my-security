# 支付重定向攻击

## 一句话风险
攻击者通过篡改支付成功后的跳转URL或回调地址，将用户引导至钓鱼网站窃取信息或绕过支付验证。

## 风险等级
- 严重程度: 🟠高
- 影响范围: 所有使用支付跳转/回调的Web应用
- 发生概率: 中

## 场景描述
独立开发者小王的在线商城使用第三方支付，用户支付成功后，支付网关会跳转回商城的"支付成功"页面。为了让多个页面都能发起支付，小王在前端传递了一个returnUrl参数，支付完成后跳转到这个URL。某安全研究员发现，可以通过修改returnUrl参数将用户跳转到任意网站。攻击者构造了一个钓鱼链接：将returnUrl指向与商城页面相似的钓鱼网站，诱骗用户点击。用户支付后，被自动跳转到钓鱼网站，钓鱼网站显示"支付失败，请重新输入卡号"，用户误以为是真实页面，输入了银行卡信息导致财产损失。另一种攻击方式是利用开放重定向漏洞进行钓鱼攻击，攻击者在邮件或社交媒体中散布带有恶意returnUrl的支付链接，由于链接域名是真实的商城域名，用户更容易信任。支付重定向攻击不仅危害用户，还可能导致平台承担责任。

## 攻击方式
1. 分析支付跳转逻辑，找到returnUrl/redirectUrl参数
2. 构造恶意重定向URL（钓鱼网站或恶意页面）
3. 通过邮件/社交媒体传播带有恶意重定向的支付链接
4. 用户支付后被重定向到钓鱼网站
5. 钓鱼网站窃取用户敏感信息
6. 或利用重定向绕过某些安全检查

## 真实案例
- 2019年某知名电商支付重定向漏洞，可用于钓鱼攻击
- 2020年某支付平台回调地址可被篡改
- PayPal曾多次出现开放重定向漏洞被用于钓鱼

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查支付跳转URL是否可被外部控制
- [ ] 检查回调地址是否有白名单限制
- [ ] 测试是否可以跳转到外部域名

### 短期加固 (1小时)
- [ ] 实现重定向URL白名单
- [ ] 使用相对路径或固定路径跳转
- [ ] 添加重定向确认页面

### 长期建设
- [ ] 实现统一的URL跳转安全中间件
- [ ] 使用签名校验跳转参数
- [ ] 建立钓鱼域名监控
- [ ] 用户安全意识教育

## 检测方法
```javascript
// 检测开放重定向漏洞的脚本
const testUrls = [
  'https://evil.com',
  '//evil.com',
  'https://yoursite.com@evil.com',
  'https://yoursite.com%2F%2Fevil.com',
  'javascript:alert(1)',
  'data:text/html,<script>alert(1)</script>'
];

async function testRedirect(baseUrl, returnUrlParam) {
  for (const url of testUrls) {
    const testUrl = `${baseUrl}?${returnUrlParam}=${encodeURIComponent(url)}`;
    console.log(`Testing: ${testUrl}`);

    // 检查是否被重定向到外部URL
    // ...
  }
}
```

## 代码示例
```javascript
// ❌ 错误做法：允许任意重定向
app.get('/payment/return', (req, res) => {
  const { returnUrl, orderId } = req.query;

  // 危险：直接重定向到用户指定的URL
  res.redirect(returnUrl);
});

// ❌ 错误做法：仅检查是否以http开头
app.get('/payment/return', (req, res) => {
  const { returnUrl } = req.query;

  // 危险：可以被 https://evil.com 绕过
  if (returnUrl.startsWith('https://')) {
    res.redirect(returnUrl);
  }
});

// ❌ 错误做法：简单的域名检查
app.get('/payment/return', (req, res) => {
  const { returnUrl } = req.query;

  // 危险：可以被 https://yoursite.com@evil.com 绕过
  if (returnUrl.includes('yoursite.com')) {
    res.redirect(returnUrl);
  }
});

// ✅ 正确做法：白名单 + 签名校验
const ALLOWED_DOMAINS = [
  'yoursite.com',
  'www.yoursite.com',
  'app.yoursite.com'
];

const crypto = require('crypto');

class RedirectService {
  constructor(secret) {
    this.secret = secret;
    this.allowedDomains = new Set(ALLOWED_DOMAINS);
  }

  // 生成签名重定向URL
  signRedirectUrl(url, expiry = 3600) {
    const timestamp = Math.floor(Date.now() / 1000) + expiry;
    const data = `${url}:${timestamp}`;
    const signature = crypto
      .createHmac('sha256', this.secret)
      .update(data)
      .digest('hex');

    return { url, timestamp, signature };
  }

  // 验证重定向URL
  validateRedirectUrl(url, timestamp, signature) {
    // 1. 检查时间戳
    const now = Math.floor(Date.now() / 1000);
    if (timestamp < now) {
      return { valid: false, error: '链接已过期' };
    }

    // 2. 验证签名
    const data = `${url}:${timestamp}`;
    const expectedSignature = crypto
      .createHmac('sha256', this.secret)
      .update(data)
      .digest('hex');

    if (signature !== expectedSignature) {
      return { valid: false, error: '签名无效' };
    }

    // 3. 解析并验证域名
    try {
      const parsedUrl = new URL(url);

      if (!this.allowedDomains.has(parsedUrl.hostname)) {
        return { valid: false, error: '不允许的域名' };
      }

      // 4. 确保是https协议
      if (parsedUrl.protocol !== 'https:') {
        return { valid: false, error: '仅允许HTTPS协议' };
      }

      return { valid: true, url };
    } catch (error) {
      return { valid: false, error: '无效的URL' };
    }
  }

  // 安全重定向
  safeRedirect(res, url, timestamp, signature) {
    const result = this.validateRedirectUrl(url, timestamp, signature);

    if (!result.valid) {
      // 记录异常重定向尝试
      securityLog.record({
        type: 'invalid_redirect',
        url,
        timestamp,
        signature,
        error: result.error
      });

      // 重定向到安全页面
      return res.redirect('/payment/error?code=invalid_redirect');
    }

    return res.redirect(result.url);
  }
}

const redirectService = new RedirectService(process.env.REDIRECT_SECRET);

// 支付成功回调
app.get('/payment/return', (req, res) => {
  const { returnUrl, timestamp, signature, orderId } = req.query;

  redirectService.safeRedirect(res, returnUrl, timestamp, signature);
});

// 发起支付时生成签名URL
app.post('/api/payment/create', async (req, res) => {
  const { orderId, customReturnUrl } = req.body;

  // 使用默认回调URL或用户指定的URL
  const returnUrl = customReturnUrl || '/payment/success';

  // 生成签名
  const signedUrl = redirectService.signRedirectUrl(returnUrl);

  // 创建支付订单
  const paymentUrl = await paymentGateway.createPayment({
    orderId,
    returnUrl: `${baseUrl}/payment/return?returnUrl=${encodeURIComponent(signedUrl.url)}&timestamp=${signedUrl.timestamp}&signature=${signedUrl.signature}`
  });

  res.json({ paymentUrl });
});

// ✅ 更安全的做法：完全避免客户端指定重定向URL
app.get('/payment/return', async (req, res) => {
  const { orderId, status } = req.query;

  // 验证订单状态
  const order = await db.getOrderById(orderId);

  if (!order) {
    return res.redirect('/payment/error?code=order_not_found');
  }

  // 根据订单类型/来源决定跳转页面（服务端控制）
  const redirectMap = {
    'product': '/orders/success',
    'subscription': '/subscription/success',
    'credit': '/credits/success'
  };

  const redirectPath = redirectMap[order.type] || '/payment/success';

  res.redirect(`${redirectPath}?orderId=${orderId}`);
});

// ✅ 中间件：统一处理开放重定向
function validateRedirect(req, res, next) {
  const { redirect, next: nextUrl, returnUrl, callback } = req.query;

  const redirectUrl = redirect || nextUrl || returnUrl || callback;

  if (redirectUrl) {
    try {
      const parsed = new URL(redirectUrl, `${req.protocol}://${req.get('host')}`);

      // 检查是否为内部URL
      const allowedHosts = ['yoursite.com', 'www.yoursite.com'];
      if (!allowedHosts.includes(parsed.hostname)) {
        // 显示警告页面而非直接重定向
        return res.render('redirect-warning', {
          targetUrl: redirectUrl,
          isExternal: true
        });
      }
    } catch (error) {
      return res.status(400).json({ error: '无效的重定向URL' });
    }
  }

  next();
}

// 应用于所有可能涉及重定向的路由
app.use(validateRedirect);

// ✅ 用户安全确认页面
app.get('/redirect', (req, res) => {
  const { url } = req.query;

  res.render('redirect-confirm', {
    targetUrl: url,
    domain: new URL(url).hostname
  });
});
```

## 参考资料
- [OWASP - Unvalidated Redirects and Forwards](https://owasp.org/www-community/vulnerabilities/Unvalidated_Redirects_and_Forwards)
- [开放重定向漏洞检测与防护](https://portswigger.net/web-security/dom-based/open-redirection)
- [支付安全最佳实践](https://stripe.com/docs/security)
