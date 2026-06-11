# 免费安全告警配置

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测 + 响应
- **实现成本**: 免费
- **实施时间**: 2小时
- **维护成本**: 30分钟/月
- **最后验证日期**: 2026-06-11

## 适用场景
配置安全事件告警系统,及时发现登录异常、API滥用等安全威胁,并通过邮件、Slack或短信快速通知。

---

## 快速上手（5分钟）

### 基础告警配置
```javascript
// security-alerts.js
const alertRules = {
  // 登录失败告警
  loginFailure: {
    threshold: 5, // 失败次数
    window: 300000, // 时间窗口（5分钟）
    notify: ['email', 'slack']
  },

  // API 速率限制告警
  rateLimit: {
    threshold: 100, // 请求次数
    window: 60000, // 1分钟
    notify: ['slack']
  }
};

// 发送告警
async function sendAlert(type, data) {
  const message = formatAlert(type, data);

  // 并行发送多种通知
  await Promise.all([
    sendEmail(message),
    sendSlack(message),
    sendWebhook(message)
  ]);
}
```

---

## 详细方案

### 方案架构
```
应用日志
    ↓
规则引擎 (匹配告警规则)
    ↓
告警通知
    ├── Email (免费)
    ├── Slack (免费)
    ├── Webhook (免费)
    └── SMS (付费,建议仅关键告警)
```

### 方案对比

| 方案 | 成本 | 延迟 | 可靠性 | 适合场景 |
|------|------|------|--------|---------|
| **Email** | 免费 | 秒级 | 高 | 所有告警 |
| **Slack** | 免费 | 实时 | 高 | 团队协作 |
| **Webhook** | 免费 | 实时 | 中 | 自定义集成 |
| **SMS** | $0.05-0.10/条 | 秒级 | 高 | 关键告警 |
| **Push通知** | 免费 | 实时 | 中 | 移动端 |

---

## 登录异常告警

### 异常检测规则

```javascript
// login-anomaly-detection.js
const redis = require('redis');
const client = redis.createClient();

class LoginAnomalyDetector {
  constructor() {
    this.rules = {
      // 规则1: 单IP多次失败
      ipFailureThreshold: 5,
      ipFailureWindow: 300, // 秒

      // 规则2: 单账号多处登录
      multiLocationThreshold: 3,

      // 规则3: 异常时间登录
      abnormalHours: [0, 1, 2, 3, 4, 5], // 凌晨

      // 规则4: 新设备登录
      newDeviceCheck: true,

      // 规则5: 异常地理位置
      geoCheck: true,
    };
  }

  // 检测登录失败
  async checkLoginFailure(ip, email) {
    const key = `login_failure:${ip}:${email}`;
    const failures = await client.incr(key);

    if (failures === 1) {
      await client.expire(key, this.rules.ipFailureWindow);
    }

    if (failures >= this.rules.ipFailureThreshold) {
      await this.sendAlert('login_failure', {
        ip,
        email,
        failures,
        window: `${this.rules.ipFailureWindow}秒`
      });
      return true; // 可疑行为
    }

    return false;
  }

  // 检测多地点登录
  async checkMultiLocation(userId, location) {
    const key = `user_sessions:${userId}`;
    const sessions = await client.lrange(key, 0, -1);

    const uniqueLocations = new Set(
      sessions.map(s => JSON.parse(s).location)
    );

    if (uniqueLocations.size >= this.rules.multiLocationThreshold) {
      await this.sendAlert('multi_location_login', {
        userId,
        locations: Array.from(uniqueLocations),
        newLocation: location
      });
      return true;
    }

    // 记录新会话
    await client.lpush(key, JSON.stringify({
      location,
      timestamp: Date.now()
    }));
    await client.ltrim(key, 0, 9); // 保留最近10个会话

    return false;
  }

  // 检测新设备
  async checkNewDevice(userId, deviceFingerprint) {
    const key = `user_devices:${userId}`;
    const devices = await client.smembers(key);

    if (!devices.includes(deviceFingerprint)) {
      await this.sendAlert('new_device_login', {
        userId,
        device: deviceFingerprint
      });

      // 记录新设备
      await client.sadd(key, deviceFingerprint);
      return true;
    }

    return false;
  }

  // 检测异常时间登录
  checkAbnormalTime() {
    const hour = new Date().getHours();
    return this.rules.abnormalHours.includes(hour);
  }

  // 检测异常地理位置
  async checkAbnormalLocation(userId, currentLocation) {
    const key = `user_locations:${userId}`;
    const locations = await client.lrange(key, 0, -1);

    if (locations.length === 0) {
      // 第一次登录,记录位置
      await client.lpush(key, currentLocation);
      return false;
    }

    // 计算距离（使用 Haversine 公式）
    const lastLocation = JSON.parse(locations[0]);
    const distance = this.calculateDistance(
      lastLocation.lat, lastLocation.lng,
      currentLocation.lat, currentLocation.lng
    );

    // 如果距离超过 1000km,可能异常
    if (distance > 1000) {
      await this.sendAlert('abnormal_location', {
        userId,
        lastLocation,
        currentLocation,
        distance
      });
      return true;
    }

    return false;
  }

  // 计算两点距离（km）
  calculateDistance(lat1, lng1, lat2, lng2) {
    const R = 6371; // 地球半径
    const dLat = this.toRad(lat2 - lat1);
    const dLng = this.toRad(lng2 - lng1);
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(this.toRad(lat1)) * Math.cos(this.toRad(lat2)) *
              Math.sin(dLng/2) * Math.sin(dLng/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
  }

  toRad(deg) {
    return deg * Math.PI / 180;
  }

  // 发送告警
  async sendAlert(type, data) {
    const alert = {
      type,
      data,
      timestamp: new Date().toISOString()
    };

    // 并行发送多种通知
    await Promise.all([
      this.sendSlack(alert),
      this.sendEmail(alert),
      this.logAlert(alert)
    ]);
  }
}
```

### Express 中间件实现

```javascript
// login-security-middleware.js
const detector = new LoginAnomalyDetector();

// 登录失败监控
app.post('/auth/login', async (req, res, next) => {
  const { email, password } = req.body;
  const ip = req.ip;
  const userAgent = req.headers['user-agent'];

  try {
    const user = await authenticateUser(email, password);

    if (user) {
      // 登录成功 - 检查异常
      const deviceFingerprint = generateDeviceFingerprint(userAgent, ip);
      const location = await getLocationFromIP(ip);

      // 并行检测多种异常
      const anomalies = await Promise.all([
        detector.checkMultiLocation(user.id, location),
        detector.checkNewDevice(user.id, deviceFingerprint),
        detector.checkAbnormalLocation(user.id, location)
      ]);

      if (detector.checkAbnormalTime()) {
        await detector.sendAlert('abnormal_time_login', {
          userId: user.id,
          email,
          ip,
          time: new Date().toISOString()
        });
      }

      // 生成 JWT
      const token = generateJWT(user);
      res.json({ token });
    } else {
      // 登录失败 - 记录并检测
      const isSuspicious = await detector.checkLoginFailure(ip, email);

      if (isSuspicious) {
        // 可选: 封禁 IP
        await blockIP(ip, 3600); // 封禁1小时
      }

      res.status(401).json({ error: 'Invalid credentials' });
    }
  } catch (error) {
    next(error);
  }
});
```

---

## API 滥用检测

### 检测规则

```javascript
// api-abuse-detection.js
class APIAbuseDetector {
  constructor() {
    this.rules = {
      // 全局速率限制
      globalRateLimit: {
        window: 60000, // 1分钟
        max: 1000
      },

      // 敏感接口限制
      sensitiveEndpoints: {
        '/api/auth/login': { window: 3600000, max: 5 },
        '/api/auth/register': { window: 3600000, max: 3 },
        '/api/payment': { window: 60000, max: 10 },
        '/api/password/reset': { window: 3600000, max: 3 }
      },

      // 异常检测阈值
      anomalyThreshold: 3, // 标准差倍数
    };
  }

  // 实时检测
  async detectAbuse(req) {
    const ip = req.ip;
    const userId = req.user?.id;
    const endpoint = req.path;

    const checks = [];

    // 检查全局速率
    checks.push(this.checkGlobalRate(ip));

    // 检查敏感接口速率
    if (this.rules.sensitiveEndpoints[endpoint]) {
      checks.push(this.checkSensitiveRate(ip, endpoint));
    }

    // 检查异常行为模式
    if (userId) {
      checks.push(this.checkAnomalousBehavior(userId, endpoint));
    }

    const results = await Promise.all(checks);
    const abuseDetected = results.some(r => r.abuse);

    if (abuseDetected) {
      await this.sendAlert('api_abuse', {
        ip,
        userId,
        endpoint,
        violations: results.filter(r => r.abuse)
      });
    }

    return abuseDetected;
  }

  // 检查全局速率
  async checkGlobalRate(ip) {
    const key = `global_rate:${ip}`;
    const count = await client.incr(key);

    if (count === 1) {
      await client.pexpire(key, this.rules.globalRateLimit.window);
    }

    if (count > this.rules.globalRateLimit.max) {
      return {
        abuse: true,
        type: 'global_rate_exceeded',
        count,
        limit: this.rules.globalRateLimit.max
      };
    }

    return { abuse: false };
  }

  // 检查敏感接口速率
  async checkSensitiveRate(ip, endpoint) {
    const rule = this.rules.sensitiveEndpoints[endpoint];
    const key = `sensitive:${endpoint}:${ip}`;
    const count = await client.incr(key);

    if (count === 1) {
      await client.pexpire(key, rule.window);
    }

    if (count > rule.max) {
      return {
        abuse: true,
        type: 'sensitive_rate_exceeded',
        endpoint,
        count,
        limit: rule.max
      };
    }

    return { abuse: false };
  }

  // 检查异常行为模式
  async checkAnomalousBehavior(userId, endpoint) {
    const key = `user_behavior:${userId}`;
    const history = await client.lrange(key, 0, 99);

    if (history.length < 10) {
      // 数据不足,记录行为
      await this.recordBehavior(userId, endpoint);
      return { abuse: false };
    }

    // 计算正常行为模式
    const counts = history.map(h => JSON.parse(h).count);
    const mean = counts.reduce((a, b) => a + b) / counts.length;
    const stdDev = Math.sqrt(
      counts.reduce((sum, c) => sum + Math.pow(c - mean, 2), 0) / counts.length
    );

    // 获取当前请求频率
    const currentCount = await this.getCurrentCount(userId);

    // 如果超出正常范围（均值 + 3倍标准差）
    if (currentCount > mean + this.rules.anomalyThreshold * stdDev) {
      return {
        abuse: true,
        type: 'anomalous_behavior',
        current: currentCount,
        mean,
        stdDev
      };
    }

    return { abuse: false };
  }

  // 记录用户行为
  async recordBehavior(userId, endpoint) {
    const key = `user_behavior:${userId}`;
    const minute = new Date().toISOString().slice(0, 16);

    await client.lpush(key, JSON.stringify({
      endpoint,
      count: await this.getCurrentCount(userId),
      timestamp: Date.now()
    }));
    await client.ltrim(key, 0, 99); // 保留最近100条
  }
}
```

### Express 中间件

```javascript
// api-security-middleware.js
const abuseDetector = new APIAbuseDetector();

app.use(async (req, res, next) => {
  const abuse = await abuseDetector.detectAbuse(req);

  if (abuse) {
    return res.status(429).json({
      error: 'Too many requests',
      message: 'Abnormal behavior detected'
    });
  }

  next();
});
```

---

## 告警通知配置

### Email 告警

```javascript
// email-alerts.js
const nodemailer = require('nodemailer');

// 使用免费的邮件服务
// 选项1: Gmail (需要应用专用密码)
// 选项2: SendGrid Free (100封/天)
// 选项3: AWS SES (62000封/月免费)

const transporter = nodemailer.createTransport({
  host: 'smtp.sendgrid.net',
  port: 587,
  auth: {
    user: 'apikey',
    pass: process.env.SENDGRID_API_KEY
  }
});

async function sendEmailAlert(alert) {
  const { type, data } = alert;

  const templates = {
    login_failure: {
      subject: '🚨 登录失败告警',
      html: `
        <h2>登录失败告警</h2>
        <p><strong>IP:</strong> ${data.ip}</p>
        <p><strong>邮箱:</strong> ${data.email}</p>
        <p><strong>失败次数:</strong> ${data.failures}</p>
        <p><strong>时间窗口:</strong> ${data.window}</p>
        <p><strong>时间:</strong> ${alert.timestamp}</p>
      `
    },
    api_abuse: {
      subject: '🚨 API滥用告警',
      html: `
        <h2>API滥用告警</h2>
        <p><strong>IP:</strong> ${data.ip}</p>
        <p><strong>用户:</strong> ${data.userId || '匿名'}</p>
        <p><strong>端点:</strong> ${data.endpoint}</p>
        <p><strong>违规类型:</strong> ${data.violations.map(v => v.type).join(', ')}</p>
      `
    }
  };

  const template = templates[type] || templates.default;

  await transporter.sendMail({
    from: 'alerts@yourcompany.com',
    to: 'security@yourcompany.com',
    subject: template.subject,
    html: template.html
  });
}
```

### Slack 告警

```javascript
// slack-alerts.js
const axios = require('axios');

const SLACK_WEBHOOK_URL = process.env.SLACK_WEBHOOK_URL;

async function sendSlackAlert(alert) {
  const { type, data } = alert;

  const colors = {
    login_failure: 'danger',
    api_abuse: 'warning',
    new_device_login: '#36a64f'
  };

  const message = {
    attachments: [{
      color: colors[type] || 'good',
      title: `🚨 ${formatAlertType(type)}`,
      fields: formatFields(data),
      footer: 'Security Alert System',
      ts: Math.floor(Date.now() / 1000)
    }]
  };

  await axios.post(SLACK_WEBHOOK_URL, message);
}

function formatAlertType(type) {
  const types = {
    login_failure: '登录失败告警',
    api_abuse: 'API滥用告警',
    new_device_login: '新设备登录',
    multi_location_login: '多地点登录',
    abnormal_location: '异常地理位置'
  };
  return types[type] || type;
}

function formatFields(data) {
  return Object.entries(data).map(([key, value]) => ({
    title: key,
    value: typeof value === 'object' ? JSON.stringify(value) : String(value),
    short: true
  }));
}
```

### Webhook 告警

```javascript
// webhook-alerts.js
const crypto = require('crypto');

async function sendWebhookAlert(alert, webhookUrl, secret) {
  const payload = JSON.stringify(alert);
  const signature = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  await axios.post(webhookUrl, {
    payload: alert,
    signature: `sha256=${signature}`,
    timestamp: Date.now()
  }, {
    headers: {
      'X-Alert-Signature': signature,
      'Content-Type': 'application/json'
    }
  });
}
```

### SMS 告警（关键告警）

```javascript
// sms-alerts.js
const twilio = require('twilio');

const client = twilio(
  process.env.TWILIO_ACCOUNT_SID,
  process.env.TWILIO_AUTH_TOKEN
);

// 仅用于关键告警
async function sendSMSAlert(alert, phoneNumber) {
  const criticalTypes = ['security_breach', 'massive_ddos'];

  if (!criticalTypes.includes(alert.type)) {
    return; // 非关键告警不发短信
  }

  const message = `🚨 安全告警: ${alert.type}
详情: ${JSON.stringify(alert.data).slice(0, 100)}
时间: ${alert.timestamp}`;

  await client.messages.create({
    body: message,
    to: phoneNumber,
    from: process.env.TWILIO_PHONE_NUMBER
  });
}

// 成本控制
const smsBudget = {
  dailyLimit: 10, // 每天最多10条
  currentCount: 0
};

async function checkSMSBudget() {
  const today = new Date().toISOString().slice(0, 10);
  const key = `sms_count:${today}`;
  const count = await client.incr(key);

  if (count === 1) {
    await client.expire(key, 86400); // 24小时过期
  }

  if (count > smsBudget.dailyLimit) {
    await sendSlackAlert({
      type: 'sms_budget_exceeded',
      data: { count, limit: smsBudget.dailyLimit }
    });
    return false;
  }

  return true;
}
```

---

## 成本估算

### 免费方案

| 通知方式 | 成本 | 限制 | 适用场景 |
|---------|------|------|---------|
| **Email** | 免费 | 无限制 | 所有告警 |
| **Slack** | 免费 | 无限制 | 团队协作 |
| **Webhook** | 免费 | 无限制 | 自定义集成 |
| **Pushover** | $5一次性 | 无限制 | 个人项目 |

### 付费方案（仅关键告警）

| 服务 | 价格 | 免费额度 | 适用场景 |
|------|------|---------|---------|
| **Twilio SMS** | $0.05-0.10/条 | 无 | 关键告警 |
| **AWS SNS** | $0.00645/通知 | 100万/月 | 大规模通知 |
| **PagerDuty** | $7/用户/月 | 无 | 企业级 |

### 成本控制建议
```
告警分级:
├── P0 (严重): SMS + Email + Slack
├── P1 (重要): Email + Slack
├── P2 (一般): Slack
└── P3 (信息): 日志记录

估算月成本:
- Email: $0
- Slack: $0
- SMS: $10-20/月 (仅P0告警)
```

---

## 迁出成本

### 告警系统迁出
- **迁出难度**: 低
- **时间估算**: 1-2小时
- **步骤**:
  1. 导出告警规则配置
  2. 修改 Webhook URL
  3. 更新邮件服务配置
  4. 测试新告警渠道

---

## 与其他武器配合

### 推荐组合
```
安全告警体系:
├── 登录异常检测 → Email + Slack
├── API滥用检测 → Slack
├── 错误监控 → Sentry
├── 可用性监控 → UptimeRobot
└── 日志分析 → Grafana Loki
```

### 前置武器
- **日志系统**: 提供告警数据源
- **监控系统**: 发现异常事件

### 后置武器
- **事故响应**: 处理告警事件
- **审计日志**: 记录告警历史

---

## 常见问题

### Q: 如何避免告警疲劳?
A:
1. 合理设置阈值,避免误报
2. 告警分级,区分严重程度
3. 相同告警合并,减少重复
4. 定期审查和优化规则

### Q: SMS告警成本如何控制?
A:
1. 仅用于P0级关键告警
2. 设置每日发送上限
3. 使用免费替代方案（Slack/Email）
4. 按需开启,定期审查

### Q: 如何处理告警延迟?
A:
1. 使用实时推送（Slack Webhook）
2. 减少中间处理环节
3. 优化告警规则执行效率
4. 监控告警系统自身健康

---

## 推荐实现

### 小型项目（推荐）
- **Email** - Nodemailer + Gmail/SendGrid
- **Slack** - Incoming Webhook
- **总成本**: $0

### 中型项目
- **Email** - SendGrid Pro ($15/月)
- **Slack** - 自定义应用集成
- **SMS** - Twilio 按需使用
- **总成本**: $15-30/月

### 企业级
- **PagerDuty** - $7-15/用户/月
- **Opsgenie** - $7-15/用户/月
- **集成**: 多渠道、值班表、升级策略

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
