# Webhook 攻击

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0-20/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者伪造支付平台的 Webhook 通知，你的系统信以为真并自动处理了"付款成功"消息，实际上一分钱都没收到。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 接收第三方服务的 Webhook（如支付、通知、同步）
- [ ] Webhook 端点未验证请求来源
- [ ] Webhook 处理敏感操作（创建订单、激活会员、发送通知）
- [ ] Webhook URL 可被猜测或公开
- [ ] 未使用签名验证机制
→ 勾选≥1项，即需关注此风险

### 一句话防御
双重验证：签名验证（必须）+ IP 白名单（推荐），30分钟内可实施基础防护。

### 快速行动清单
1. [ ] **立即行动项（今天可完成，免费）**：
   - 检查所有 Webhook 端点是否启用签名验证
   - 为每个 Webhook 生成独立的密钥
   - 记录所有 Webhook 请求日志

2. [ ] **短期行动项（本周可完成，免费）**：
   - 实现签名验证逻辑（HMAC-SHA256）
   - 配置 IP 白名单（如果第三方提供）
   - 添加 Webhook 重放攻击防护（时间戳验证）

3. [ ] **长期行动项（规划中，低成本）**：
   - 部署 Webhook 监控告警
   - 实现异步处理和幂等性检查
   - 建立异常 Webhook 响应机制

### 推荐工具
- **免费**：
  - Stripe CLI - [文档](https://stripe.com/docs/stripe-cli) - 本地测试 Webhook
  - svix-webhooks - [GitHub](https://github.com/svix/svix-webhooks) - 开源 Webhook 服务

- **低成本**：
  - Svix - $25/月起 - 托管 Webhook 服务
  - Hookdeck - $19/月起 - Webhook 可靠性平台

### 验证方法
- [ ] 使用官方测试工具发送 Webhook，验证签名校验生效
- [ ] 发送伪造的 Webhook 请求，验证被拒绝
- [ ] 发送过期的 Webhook 请求，验证时间戳校验生效
- [ ] 检查日志是否记录验证失败的请求

---

## L2 小团队版（理解版）

### 场景还原
某独立开发者的订阅制 SaaS 产品使用 Stripe 处理支付。攻击者发现了 Webhook 端点（`/api/webhooks/stripe`），但没有验证签名。攻击者伪造了一个"支付成功"的 Webhook 请求，系统自动将用户升级为年度会员（价值$299），攻击者分文未付。

更糟糕的是，攻击者批量注册了100个账户，重复此攻击，累计损失$29,900。

### 攻击路径（3-5步）
1. **信息收集**：攻击者发现你的 Webhook 端点（通过源码、文档或猜测）
2. **构造伪造请求**：根据第三方 API 文档构造合法格式的 Webhook
3. **发送恶意请求**：向你的 Webhook 端点发送伪造请求
4. **系统自动处理**：系统未验证来源，自动执行敏感操作
5. **造成损失**：非法激活服务、绕过支付、获取未授权数据

### 防御实施（低成本方案）

#### 方案A：免费方案（签名验证）

**工具/服务**：HMAC-SHA256 签名验证

**配置步骤**：

1. **Stripe Webhook 签名验证**
```javascript
// Node.js + Express
const crypto = require('crypto');
const express = require('express');
const app = express();

// Stripe Webhook 密钥（从 Dashboard 获取）
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET;

app.post('/api/webhooks/stripe', express.raw({ type: 'application/json' }), (req, res) => {
  const sig = req.headers['stripe-signature'];
  const payload = req.body;

  // 1. 验证签名
  let event;
  try {
    event = stripe.webhooks.constructEvent(payload, sig, STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // 2. 处理事件
  switch (event.type) {
    case 'checkout.session.completed':
      const session = event.data.object;
      // 处理支付成功
      handlePaymentSuccess(session);
      break;
    case 'customer.subscription.deleted':
      const subscription = event.data.object;
      // 处理订阅取消
      handleSubscriptionCancelled(subscription);
      break;
    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  res.json({ received: true });
});
```

```python
# Python + Flask
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')

@app.route('/api/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return jsonify({'error': 'Invalid signature'}), 400

    # 处理事件
    if event.type == 'checkout.session.completed':
        session = event.data.object
        handle_payment_success(session)

    return jsonify({'received': True})
```

2. **通用 HMAC 签名验证**
```javascript
// 通用 Webhook 签名验证中间件
function verifyWebhookSignature(secret, headerName = 'x-webhook-signature') {
  return (req, res, next) => {
    const signature = req.headers[headerName];
    const payload = JSON.stringify(req.body);

    // 计算预期的签名
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');

    // 使用时间安全比较（防止时序攻击）
    const isValid = crypto.timingSafeEqual(
      Buffer.from(signature, 'hex'),
      Buffer.from(expectedSignature, 'hex')
    );

    if (!isValid) {
      console.error('Invalid webhook signature');
      return res.status(401).json({ error: 'Invalid signature' });
    }

    next();
  };
}

// 使用
app.post('/api/webhooks/custom',
  express.json(),
  verifyWebhookSignature(process.env.WEBHOOK_SECRET),
  (req, res) => {
    // 处理 Webhook
    res.json({ received: true });
  }
);
```

```python
# Python 通用签名验证
import hmac
import hashlib
from functools import wraps
from flask import request, jsonify

def verify_webhook_signature(secret, header_name='X-Webhook-Signature'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            signature = request.headers.get(header_name)
            if not signature:
                return jsonify({'error': 'Missing signature'}), 401

            payload = request.get_data()

            # 计算预期签名
            expected_signature = hmac.new(
                secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            # 时间安全比较
            if not hmac.compare_digest(signature, expected_signature):
                return jsonify({'error': 'Invalid signature'}), 401

            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 使用
@app.route('/api/webhooks/custom', methods=['POST'])
@verify_webhook_signature(os.environ.get('WEBHOOK_SECRET'))
def custom_webhook():
    data = request.json
    # 处理 Webhook
    return jsonify({'received': True})
```

3. **时间戳验证（防重放攻击）**
```javascript
function verifyWebhookWithTimestamp(secret, maxAge = 300) {
  return (req, res, next) => {
    const signature = req.headers['x-webhook-signature'];
    const timestamp = req.headers['x-webhook-timestamp'];

    if (!signature || !timestamp) {
      return res.status(401).json({ error: 'Missing signature or timestamp' });
    }

    // 检查时间戳是否过期
    const now = Math.floor(Date.now() / 1000);
    if (now - parseInt(timestamp) > maxAge) {
      return res.status(401).json({ error: 'Webhook expired' });
    }

    // 验证签名（包含时间戳）
    const payload = `${timestamp}.${JSON.stringify(req.body)}`;
    const expectedSignature = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');

    const isValid = crypto.timingSafeEqual(
      Buffer.from(signature, 'hex'),
      Buffer.from(expectedSignature, 'hex')
    );

    if (!isValid) {
      return res.status(401).json({ error: 'Invalid signature' });
    }

    next();
  };
}
```

**局限性**：
- 需要为每个第三方服务配置不同的验证逻辑
- IP 白名单需要额外配置
- 缺少统一的监控告警

#### 方案B：低成本方案（<$50/月）

**工具/服务**：IP 白名单 + Webhook 服务

**配置步骤**：

1. **IP 白名单配置**
```javascript
// IP 白名单中间件
const WEBHOOK_IP_WHITELIST = {
  stripe: [
    '3.18.12.63',
    '3.130.192.231',
    '13.235.14.247',
    // ... 更多 IP
  ],
  github: [
    '192.30.252.0/22',
    '185.199.108.0/22',
  ],
  slack: [
    '34.211.165.0/24',
    '54.187.204.0/24',
  ]
};

function ipWhitelist(services) {
  return (req, res, next) => {
    const clientIp = req.ip || req.connection.remoteAddress;

    // 检查 IP 是否在白名单中
    const allowed = services.some(service => {
      const whitelist = WEBHOOK_IP_WHITELIST[service];
      return whitelist.some(ip => isIpInCidr(clientIp, ip));
    });

    if (!allowed) {
      console.error(`Webhook from unauthorized IP: ${clientIp}`);
      return res.status(403).json({ error: 'IP not whitelisted' });
    }

    next();
  };
}

// 使用（结合签名验证）
app.post('/api/webhooks/stripe',
  ipWhitelist(['stripe']),
  express.raw({ type: 'application/json' }),
  verifyStripeSignature,
  handleStripeWebhook
);
```

```python
# Python IP 白名单
import ipaddress
from functools import wraps

WEBHOOK_IP_WHITELIST = {
    'stripe': ['3.18.12.63', '3.130.192.231', '13.235.14.247'],
    'github': ['192.30.252.0/22', '185.199.108.0/22'],
}

def is_ip_in_whitelist(ip, service):
    whitelist = WEBHOOK_IP_WHITELIST.get(service, [])
    for allowed in whitelist:
        if '/' in allowed:
            # CIDR 表示法
            if ipaddress.ip_address(ip) in ipaddress.ip_network(allowed):
                return True
        else:
            if ip == allowed:
                return True
    return False

def ip_whitelist(service):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            if not is_ip_in_whitelist(client_ip, service):
                return jsonify({'error': 'IP not whitelisted'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

2. **Svix 托管服务（简化 Webhook 管理）**
```javascript
const svix = new Svix('your-api-key');

// 接收 Webhook
app.post('/api/webhooks/svix', express.raw({ type: 'application/json' }), async (req, res) => {
  const payload = req.body;
  const headers = req.headers;

  try {
    const event = await svix.webhooks.verify(payload, headers);
    // event 已验证，处理业务逻辑
    console.log('Received event:', event);
    res.json({ received: true });
  } catch (err) {
    console.error('Webhook verification failed:', err);
    res.status(400).json({ error: 'Verification failed' });
  }
});
```

**优势**：
- 双重验证（签名 + IP）更安全
- 托管服务减少维护成本
- 提供重试和监控功能

### 决策树
```
你的 Webhook 是否处理敏感操作（支付、激活、权限）？
├── 是 → 必须启用签名验证
│   ├── 第三方是否提供 IP 白名单？→ 启用 IP 白名单（双重验证）
│   └── 否 → 仅签名验证 + 时间戳验证
└── 否 → 是否处理用户数据？
    ├── 是 → 至少需要签名验证
    └── 否 → 记录日志即可
```

### 代码示例

**完整的 Webhook 安全处理类**
```javascript
class WebhookHandler {
  constructor(config) {
    this.secrets = config.secrets;
    this.ipWhitelists = config.ipWhitelists || {};
    this.maxAge = config.maxAge || 300; // 5分钟
  }

  // 验证签名
  verifySignature(payload, signature, secret) {
    const expected = crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex');

    return crypto.timingSafeEqual(
      Buffer.from(signature, 'hex'),
      Buffer.from(expected, 'hex')
    );
  }

  // 验证时间戳
  verifyTimestamp(timestamp) {
    const now = Math.floor(Date.now() / 1000);
    return (now - parseInt(timestamp)) <= this.maxAge;
  }

  // 验证 IP
  verifyIP(clientIp, service) {
    const whitelist = this.ipWhitelists[service];
    if (!whitelist) return true; // 无白名单配置则跳过

    return whitelist.some(ip => {
      if (ip.includes('/')) {
        return this.isIpInCidr(clientIp, ip);
      }
      return clientIp === ip;
    });
  }

  // 验证 CIDR
  isIpInCidr(ip, cidr) {
    const [range, bits] = cidr.split('/');
    const mask = ~(2 ** (32 - bits) - 1);
    const ipNum = this.ipToNumber(ip);
    const rangeNum = this.ipToNumber(range);
    return (ipNum & mask) === (rangeNum & mask);
  }

  ipToNumber(ip) {
    return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet), 0) >>> 0;
  }

  // 创建中间件
  middleware(service) {
    return (req, res, next) => {
      const clientIp = req.ip || req.connection.remoteAddress;
      const signature = req.headers['x-webhook-signature'];
      const timestamp = req.headers['x-webhook-timestamp'];
      const payload = req.body;

      // 1. IP 白名单验证
      if (!this.verifyIP(clientIp, service)) {
        this.log('warn', 'IP not whitelisted', { clientIp, service });
        return res.status(403).json({ error: 'IP not whitelisted' });
      }

      // 2. 时间戳验证
      if (timestamp && !this.verifyTimestamp(timestamp)) {
        this.log('warn', 'Webhook expired', { timestamp });
        return res.status(401).json({ error: 'Webhook expired' });
      }

      // 3. 签名验证
      const secret = this.secrets[service];
      if (!secret || !this.verifySignature(
        timestamp ? `${timestamp}.${payload}` : payload,
        signature,
        secret
      )) {
        this.log('warn', 'Invalid signature', { service });
        return res.status(401).json({ error: 'Invalid signature' });
      }

      // 验证通过
      this.log('info', 'Webhook verified', { service, clientIp });
      next();
    };
  }

  log(level, message, data) {
    console.log(JSON.stringify({
      level,
      message,
      timestamp: new Date().toISOString(),
      ...data
    }));
  }
}

// 使用示例
const webhookHandler = new WebhookHandler({
  secrets: {
    stripe: process.env.STRIPE_WEBHOOK_SECRET,
    github: process.env.GITHUB_WEBHOOK_SECRET,
    slack: process.env.SLACK_WEBHOOK_SECRET,
  },
  ipWhitelists: {
    stripe: ['3.18.12.63', '3.130.192.231'],
    github: ['192.30.252.0/22'],
  },
  maxAge: 300
});

app.post('/api/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  webhookHandler.middleware('stripe'),
  handleStripeWebhook
);
```

---

## L3 企业版（深耕版）

参见企业级案例：[Webhook 安全最佳实践](../../enterprise/infosec/webhook-security.md)

### 高级防护策略

1. **Webhook 网关**
   - 统一入口管理
   - 自动签名验证
   - 速率限制

2. **重试与幂等性**
   - 自动重试机制
   - 幂等性保证
   - 死信队列

3. **监控与告警**
   - 实时监控
   - 异常检测
   - 自动响应

### 推荐企业方案
- Svix Enterprise - 按需定价
- Hookdeck Pro - $99/月起
- AWS API Gateway + Lambda - 按使用量计费

---

## 相关案例
- [API 未授权访问](./unauthorized-access.md)
- [支付参数篡改](../payment/payment-tampering.md)

## 推荐武器
- [Webhook 签名验证库](../../../weapons/indie/open-source/webhook-signature.md)
- [Svix 配置模板](../../../weapons/indie/saas/svix-webhook.md)
