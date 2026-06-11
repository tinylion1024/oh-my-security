# 免费可用性监控

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测
- **实现成本**: 免费
- **实施时间**: 30分钟
- **维护成本**: 10分钟/月
- **最后验证日期**: 2026-06-11

## 适用场景
监控你的网站或API是否在线,当服务宕机时第一时间收到告警通知,保证业务可用性。

---

## 快速上手（5分钟）

### UptimeRobot 快速配置
```bash
# 1. 注册 UptimeRobot 免费账号
# https://uptimerobot.com/sign-up

# 2. 添加监控（Web界面）
# - 点击 "+ Add New Monitor"
# - Monitor Type: HTTP(s)
# - Friendly Name: "My API"
# - URL: https://api.example.com/health
# - Monitoring Interval: 5 minutes

# 3. 健康检查端点示例
# health.js (Node.js)
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});
```

---

## 详细方案

### 方案架构
```
UptimeRobot (监控)
    ↓
  [HTTP请求] → 你的服务 /health
    ↓
  [失败检测]
    ↓
  告警通知 → Email / Slack / Webhook
```

### 方案对比

| 服务 | 免费额度 | 检查频率 | 告警方式 | 状态页面 |
|------|---------|---------|---------|---------|
| **UptimeRobot** | 50监控项 | 5分钟 | Email, Slack, Webhook | ✅ 自定义 |
| **Better Stack** | 10监控项 | 3分钟 | Email, Slack, SMS | ✅ 公开页面 |
| **Uptime Kuma** | 无限制 | 自定义 | 多种通知方式 | ✅ 可自托管 |
| **Pingdom** | 1监控项 | 1分钟 | Email | ❌ 无 |

---

### UptimeRobot 详细配置

#### 基础监控配置
```bash
# 创建HTTP监控（API方式）
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d "api_key=your-api-key" \
  -d "friendly_name=My Production API" \
  -d "url=https://api.example.com/health" \
  -d "type=1" \
  -d "interval=300"  # 5分钟

# 创建HTTPS监控（SSL证书检测）
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d "api_key=your-api-key" \
  -d "friendly_name=SSL Certificate Check" \
  -d "url=https://example.com" \
  -d "type=2"  # HTTPS监控

# 创建端口监控
curl -X POST https://api.uptimerobot.com/v2/newMonitor \
  -d "api_key=your-api-key" \
  -d "friendly_name=Database Port" \
  -d "url=your-server-ip" \
  -d "type=4" \
  -d "port=5432"  # PostgreSQL端口
```

#### 告警联系人配置
```bash
# 添加Email告警
curl -X POST https://api.uptimerobot.com/v2/newAlertContact \
  -d "api_key=your-api-key" \
  -d "friendly_name=Dev Team" \
  -d "value=team@example.com" \
  -d "type=2"  # Email类型

# 添加Webhook告警
curl -X POST https://api.uptimerobot.com/v2/newAlertContact \
  -d "api_key=your-api-key" \
  -d "friendly_name=Slack Webhook" \
  -d "value=https://hooks.slack.com/services/YOUR/WEBHOOK/URL" \
  -d "type=11"  # Webhook类型
```

#### Webhook 告警配置

**Slack 集成**:
```javascript
// 1. 在 Slack 创建 Incoming Webhook
// https://my.slack.com/services/new/incoming-webhook

// 2. UptimeRobot 配置 Webhook URL
// Alert Contact → Add → Webhook → 粘贴 Slack Webhook URL

// 3. 自定义告警消息（使用 UptimeRobot 模板变量）
{
  "attachments": [{
    "color": "danger",
    "title": "🚨 {monitor_friendly_name} is DOWN",
    "text": "URL: {monitor_url}\nTime: {alert_time}\nReason: {alert_reason}",
    "footer": "UptimeRobot Monitor"
  }]
}

// 4. 恢复通知
{
  "attachments": [{
    "color": "good",
    "title": "✅ {monitor_friendly_name} is UP",
    "text": "URL: {monitor_url}\nTime: {alert_time}\nDuration: {alert_duration}",
    "footer": "UptimeRobot Monitor"
  }]
}
```

**Telegram 集成**:
```javascript
// 1. 创建 Telegram Bot
// 与 @BotFather 对话: /newbot → 获取 API Token

// 2. 获取 Chat ID
// 发送消息给 bot,访问: https://api.telegram.org/bot<token>/getUpdates

// 3. 配置 Webhook
const TELEGRAM_BOT_TOKEN = 'your-bot-token';
const CHAT_ID = 'your-chat-id';

// UptimeRobot Webhook URL:
`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage?chat_id=${CHAT_ID}&text={monitor_friendly_name}+is+{alert_type_friendly}`
```

**Discord 集成**:
```javascript
// 1. Discord 服务器设置 → 整合 → Webhook → 创建 Webhook

// 2. UptimeRobot 配置 Discord Webhook URL
{
  "content": "🚨 **{monitor_friendly_name}** is {alert_type_friendly}!\nURL: {monitor_url}\nTime: {alert_time}"
}
```

---

### 状态页面配置

#### UptimeRobot 状态页面
```bash
# 创建公开状态页面
# 1. UptimeRobot Dashboard → Status Pages → Create
# 2. 选择要显示的监控项
# 3. 自定义域名（可选）: status.example.com

# 状态页面内容示例
# - 整体状态指示器
# - 各服务状态列表
# - 过去30天可用性统计
# - 事件历史记录
```

#### 状态页面嵌入代码
```html
<!-- 嵌入到你的网站 -->
<iframe
  src="https://stats.uptimerobot.com/YOUR_STATUS_PAGE_ID"
  width="100%"
  height="600px"
  frameborder="0">
</iframe>

<!-- 或使用徽章 -->
<a href="https://status.example.com">
  <img src="https://img.shields.io/uptimerobot/ratio/YOUR_MONITOR_ID" alt="Uptime">
</a>
```

---

### Better Stack 配置

#### Better Stack 免费层优势
```
✅ 更快的检查频率（3分钟 vs UptimeRobot 5分钟）
✅ 更好的UI/UX
✅ 内置事件时间线
✅ 自动状态页面
✅ Slack/Email/SMS 告警
```

#### 快速配置
```bash
# 1. 注册 Better Stack
# https://betterstack.com/sign-up

# 2. 创建监控
# - Monitors → Add Monitor
# - URL: https://api.example.com/health
# - Check Frequency: 3 minutes
# - Regions: 选择多个地区

# 3. 配置告警
# - On-call Schedules → Create Schedule
# - Integrations → Add Integration (Slack/Email)

# 4. 启用状态页面
# - Status Pages → Create Status Page
# - 自定义域名: status.yourcompany.com
```

---

### Uptime Kuma 自托管方案

#### 为什么选择自托管?
```
✅ 无监控数量限制
✅ 完全控制数据
✅ 更灵活的通知方式
✅ 自定义检查频率
✅ 无隐私担忧
```

#### Docker 部署
```yaml
# docker-compose.yml
version: '3'
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    volumes:
      - ./uptime-kuma-data:/app/data
    ports:
      - 3001:3001
    restart: always

# 启动
docker-compose up -d

# 访问
# http://localhost:3001
```

#### Nginx 反向代理 + HTTPS
```nginx
# /etc/nginx/sites-available/uptime.yourcompany.com
server {
    listen 443 ssl http2;
    server_name uptime.yourcompany.com;

    ssl_certificate /etc/letsencrypt/live/uptime.yourcompany.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/uptime.yourcompany.com/privkey.pem;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

### 健康检查端点最佳实践

#### 基础健康检查
```javascript
// health-basic.js
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});
```

#### 详细健康检查
```javascript
// health-detailed.js
const healthCheck = {
  status: 'ok',
  timestamp: new Date().toISOString(),
  uptime: process.uptime(),
  version: process.env.npm_package_version,
  checks: {
    database: await checkDatabase(),
    redis: await checkRedis(),
    external_api: await checkExternalAPI()
  }
};

app.get('/health', async (req, res) => {
  try {
    // 检查数据库连接
    const dbStart = Date.now();
    await db.query('SELECT 1');
    const dbLatency = Date.now() - dbStart;

    // 检查 Redis 连接
    const redisStart = Date.now();
    await redis.ping();
    const redisLatency = Date.now() - redisStart;

    res.status(200).json({
      status: 'ok',
      checks: {
        database: { status: 'ok', latency: dbLatency },
        redis: { status: 'ok', latency: redisLatency }
      }
    });
  } catch (error) {
    res.status(503).json({
      status: 'error',
      error: error.message
    });
  }
});
```

#### Kubernetes 健康检查
```yaml
# k8s-healthcheck.yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: app
    image: my-app:latest
    livenessProbe:
      httpGet:
        path: /health
        port: 3000
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health
        port: 3000
      initialDelaySeconds: 5
      periodSeconds: 5
```

---

## 成本估算

### 免费方案对比

| 方案 | 监控数量 | 检查频率 | 存储时长 | 状态页面 |
|------|---------|---------|---------|---------|
| **UptimeRobot** | 50 | 5分钟 | 2个月 | ✅ |
| **Better Stack** | 10 | 3分钟 | 30天 | ✅ |
| **Uptime Kuma** | 无限 | 自定义 | 自定义 | ✅ |

### 付费升级对比

| 服务 | 价格 | 监控数量 | 检查频率 | 特点 |
|------|------|---------|---------|------|
| UptimeRobot Pro | $7/月 | 50 | 1分钟 | SMS通知 |
| Better Stack Team | $12/月 | 50 | 1分钟 | 团队协作 |
| Pingdom Pro | $10/月 | 10 | 1分钟 | 性能监控 |

---

## 迁出成本

### UptimeRobot 迁出
- **迁出难度**: 低
- **时间估算**: 1-2小时
- **步骤**:
  1. 导出监控列表（Dashboard → Settings → Export）
  2. 导出联系人信息
  3. 在新服务中批量导入
  4. 更新 Webhook URL

### Better Stack 迁出
- **迁出难度**: 低
- **时间估算**: 1小时
- **步骤**:
  1. Settings → Export Data
  2. 监控配置导出为 JSON
  3. 在新服务中导入

### Uptime Kuma 迁出
- **迁出难度**: 中
- **时间估算**: 2-4小时
- **步骤**:
  1. 导出配置（Settings → Export）
  2. 备份数据目录
  3. 在新服务器部署
  4. 恢复配置和数据

---

## 与其他武器配合

### 推荐组合
```
独立开发者监控体系:
├── UptimeRobot (可用性监控)
├── Sentry (错误追踪)
├── Grafana Loki (日志聚合)
└── Cloudflare Analytics (流量分析)
```

### 前置武器
- **SSL证书**: 确保HTTPS监控正常工作
- **健康检查端点**: 实现详细的健康检查

### 后置武器
- **错误追踪**: 发现问题时快速定位
- **日志聚合**: 查找宕机原因

---

## 常见问题

### Q: 免费监控够用吗?
A: 对于独立开发者完全够用:
- UptimeRobot 50个监控项可覆盖多个服务
- 5分钟检查频率足够及时发现问题
- 如需更快响应,可自托管 Uptime Kuma

### Q: 如何减少误报?
A:
1. 设置合理的超时时间（30秒）
2. 配置重试机制（失败后重试2次再告警）
3. 使用多地监控（Better Stack支持多地区）
4. 健康检查端点增加容错逻辑

### Q: 状态页面有必要吗?
A: 强烈建议配置:
- 增加用户信任度
- 减少客服咨询
- 公开透明地展示服务质量
- 可嵌入官网或文档

### Q: 如何监控定时任务?
A: 使用心跳监控:
```javascript
// 定时任务执行时发送心跳
const cron = require('node-cron');

cron.schedule('0 2 * * *', async () => {
  // 执行任务
  await performBackup();

  // 发送心跳到 UptimeRobot
  await fetch('https://heartbeat.uptimerobot.com/your-heartbeat-url');
});
```

---

## 推荐实现

### 小型项目（推荐）
- **UptimeRobot Free** - https://uptimerobot.com - 50监控项
- 简单易用,5分钟配置完成

### 中型项目
- **Better Stack Free** - https://betterstack.com - 10监控项
- 更好的UI,3分钟检查频率

### 自托管需求
- **Uptime Kuma** - https://github.com/louislam/uptime-kuma
- 无限制,完全控制

### 付费升级
- **UptimeRobot Pro** - $7/月 - 1分钟检查
- **Better Stack Team** - $12/月 - 团队协作

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
