# API 监控服务

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测
- **实现成本**: 免费（有额度限制）
- **实施时间**: 1-2小时
- **维护成本**: 0.5小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
监控 API 性能指标（响应时间、错误率、吞吐量），追踪异常错误，分析用户体验，适用于所有生产环境的 API 服务。

## 监控服务对比

### 快速选型表

| 服务 | 免费额度 | 主要功能 | 集成难度 | 适用场景 | 独立开发者推荐度 |
|------|---------|---------|---------|---------|----------------|
| **Sentry** | 5K errors/月 | 错误追踪、性能监控 | ⭐ 简单 | 错误监控首选 | ⭐⭐⭐⭐⭐ |
| **LogRocket** | 1K sessions/月 | 会话回放、性能监控 | ⭐ 简单 | 前端用户体验 | ⭐⭐⭐⭐ |
| **Datadog** | 1 host/5 metrics | 全栈监控 | ⭐⭐⭐ 复杂 | 企业级监控 | ⭐⭐⭐ |
| **New Relic** | 100GB/月 | APM、基础设施 | ⭐⭐ 中等 | 全栈可观测 | ⭐⭐⭐⭐ |
| **Grafana Cloud** | 10K metrics | 开源可视化 | ⭐⭐ 中等 | 自定义监控 | ⭐⭐⭐⭐ |

### 详细对比

#### 1. Sentry（推荐错误监控）

**优点**：
- 错误聚合和去重
- 源码映射（Source Map）
- 性能监控（APM）
- 发布跟踪
- 告警规则灵活

**免费额度**：
- 5,000 错误事件/月
- 10,000 性能事件/月
- 1 个项目

**适用场景**：
- 错误追踪（首选）
- 性能监控
- 前后端通用

**价格**：
- Team: $26/月（50K errors）
- Business: $80/月（200K errors）

---

#### 2. LogRocket（推荐前端监控）

**优点**：
- 会话回放（录像）
- 控制台日志记录
- 网络请求监控
- 性能指标
- 用户行为分析

**免费额度**：
- 1,000 会话/月
- 10,000 页面浏览/月

**适用场景**：
- 前端用户体验监控
- Bug 复现
- 转化率分析

**价格**：
- Starter: $75/月（10K sessions）
- Growth: $200/月（25K sessions）

---

#### 3. Datadog（推荐企业级）

**优点**：
- 全栈监控（APM + 日志 + 指标）
- 基础设施监控
- 自动仪表板
- 丰富的集成
- AI 异常检测

**免费额度**：
- 1 host（APM + Infrastructure）
- 5 自定义指标
- 1 天日志保留

**适用场景**：
- 企业级监控
- 微服务架构
- 复杂系统

**价格**：
- Pro: $31/host/月
- Enterprise: 定制

---

## 快速上手（5分钟）

### 方案一：Sentry（错误监控）

#### Python 集成

```bash
# 安装 SDK
pip install sentry-sdk fastapi
```

```python
# main.py
import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration

# 初始化 Sentry
sentry_sdk.init(
    dsn="https://examplePublicKey@o0.ingest.sentry.io/0",
    # 设置采样率
    traces_sample_rate=1.0,  # 100% 采样（生产环境建议降低）
    # 设置环境
    environment="production",
    # 发布版本
    release="my-api@1.0.0",
    # 集成
    integrations=[
        FastApiIntegration(),
    ],
    # 过滤敏感信息
    before_send=lambda event, hint: event,
)

app = FastAPI()

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    try:
        # 业务逻辑
        if user_id == 999:
            raise ValueError("User not found")
        return {"id": user_id, "name": "John Doe"}
    except Exception as e:
        # 手动捕获异常
        sentry_sdk.capture_exception(e)
        raise

@app.get("/api/error")
async def trigger_error():
    # 触发错误（测试 Sentry）
    division_by_zero = 1 / 0
    return {"status": "ok"}

# 性能监控
@app.get("/api/slow")
async def slow_endpoint():
    import time
    time.sleep(2)  # 模拟慢请求
    return {"status": "slow"}
```

#### Node.js 集成

```bash
# 安装 SDK
npm install @sentry/node @sentry/tracing
```

```javascript
// app.js
const express = require('express');
const Sentry = require('@sentry/node');
const { ProfilingIntegration } = require('@sentry/profiling-node');

const app = express();

// 初始化 Sentry
Sentry.init({
  dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0',
  integrations: [
    // Express 集成
    new Sentry.Integrations.Http({ tracing: true }),
    new Sentry.Integrations.Express({ app }),
    new ProfilingIntegration(),
  ],
  tracesSampleRate: 1.0,
  profilesSampleRate: 1.0,
  environment: 'production',
  release: 'my-api@1.0.0',
});

// 请求处理器（必须在其他中间件之前）
app.use(Sentry.Handlers.requestHandler());
// 追踪中间件
app.use(Sentry.Handlers.tracingHandler());

// 路由
app.get('/api/users/:userId', async (req, res) => {
  const { userId } = req.params;
  
  try {
    if (userId === '999') {
      throw new Error('User not found');
    }
    res.json({ id: userId, name: 'John Doe' });
  } catch (error) {
    // 手动捕获异常
    Sentry.captureException(error);
    res.status(500).json({ error: error.message });
  }
});

// 触发错误测试
app.get('/api/error', (req, res) => {
  throw new Error('Test error');
});

// 错误处理器（必须在其他中间件之后）
app.use(Sentry.Handlers.errorHandler());

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

#### 前端集成（React）

```bash
# 安装 SDK
npm install @sentry/react
```

```javascript
// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';
import App from './App';

Sentry.init({
  dsn: 'https://examplePublicKey@o0.ingest.sentry.io/0',
  integrations: [
    new BrowserTracing(),
    new Sentry.Replay(),
  ],
  tracesSampleRate: 1.0,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  environment: process.env.NODE_ENV,
});

// 错误边界
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<p>出错了，请刷新页面</p>}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>
);
```

### 方案二：LogRocket（前端监控）

```bash
# 安装 SDK
npm install logrocket
```

```javascript
// src/index.js
import LogRocket from 'logrocket';

// 初始化
LogRocket.init('your-app-id');

// 与 Redux 集成（可选）
import { createStore, applyMiddleware } from 'redux';
import thunk from 'redux-thunk';
import rootReducer from './reducers';

const store = createStore(
  rootReducer,
  applyMiddleware(thunk, LogRocket.reduxMiddleware())
);

// 与 Sentry 集成
import * as Sentry from '@sentry/react';

LogRocket.getSessionURL(function (sessionURL) {
  Sentry.setTag('sessionURL', sessionURL);
});
```

```javascript
// 与 React 组件集成
import React from 'react';
import LogRocket from 'logrocket';

function LoginButton() {
  const handleLogin = async () => {
    const user = await login();
    
    // 识别用户
    LogRocket.identify(user.id, {
      name: user.name,
      email: user.email,
      plan: user.plan,
    });
  };
  
  return <button onClick={handleLogin}>登录</button>;
}
```

### 方案三：自定义监控（Prometheus + Grafana）

```yaml
# docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api'
    static_configs:
      - targets: ['app:8000']
```

```python
# Python API 暴露指标
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI, Response
import time

# 定义指标
REQUEST_COUNT = Counter(
    'api_request_count',
    'API Request Count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API Request Latency',
    ['method', 'endpoint']
)

app = FastAPI()

@app.middleware("http")
async def add_metrics(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    
    # 记录指标
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## 详细方案

### 方案架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        应用程序                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   错误捕获    │  │   性能追踪   │  │   用户追踪   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      监控平台层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Sentry      │  │  LogRocket   │  │  Grafana     │          │
│  │  错误追踪     │  │  会话回放    │  │  指标可视化   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      告警通知层                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   邮件告警    │  │   Slack      │  │   Webhook    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 核心监控指标

#### 1. 错误监控

**关键指标**：
- 错误率（Errors/Minute）
- 错误类型分布
- 影响用户数
- 首次出现时间
- 错误趋势

**Sentry 配置**：
```python
import sentry_sdk

def before_send(event, hint):
    """过滤敏感信息"""
    # 移除敏感 Header
    if 'request' in event and 'headers' in event['request']:
        headers = event['request']['headers']
        for key in ['authorization', 'cookie', 'x-api-key']:
            if key in headers:
                headers[key] = '[Filtered]'
    
    return event

sentry_sdk.init(
    dsn="YOUR_DSN",
    before_send=before_send,
    # 错误采样
    sample_rate=1.0,
    # 忽略特定错误
    ignore_errors=[
        KeyboardInterrupt,
        SystemExit,
    ],
)
```

#### 2. 性能监控

**关键指标**：
- 平均响应时间（P50, P95, P99）
- 吞吐量（Requests/Second）
- 错误率（Error Rate %）
- Apdex 分数

**Sentry 性能监控**：
```python
from sentry_sdk import start_transaction

@app.get("/api/users")
async def get_users():
    # 创建事务
    with start_transaction(op="http.server", name="GET /api/users") as transaction:
        # 数据库查询
        with transaction.start_child(op="db.query", description="SELECT users"):
            users = await db.fetch_all("SELECT * FROM users")
        
        # 缓存操作
        with transaction.start_child(op="cache", description="Redis get"):
            cached = await redis.get("users:count")
        
        return {"users": users, "count": cached}
```

#### 3. 自定义指标

**业务指标**：
```python
from prometheus_client import Counter, Gauge, Histogram

# 注册用户数
SIGNUP_COUNT = Counter(
    'user_signup_total',
    'Total user signups',
    ['source']  # 渠道来源
)

# 活跃用户数
ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

# 支付金额
PAYMENT_AMOUNT = Histogram(
    'payment_amount_dollars',
    'Payment amount in dollars',
    buckets=[1, 5, 10, 25, 50, 100, 250, 500, 1000]
)

# 使用示例
@app.post("/api/users")
async def create_user(user: UserCreate):
    # 业务逻辑
    SIGNUP_COUNT.labels(source=user.source).inc()
    return {"id": 1, "name": user.username}

@app.post("/api/payments")
async def process_payment(payment: PaymentRequest):
    # 业务逻辑
    PAYMENT_AMOUNT.observe(payment.amount)
    return {"status": "success"}
```

### 告警配置

#### Sentry 告警规则

```yaml
# 推荐告警规则
rules:
  # 错误率告警
  - name: "High Error Rate"
    conditions:
      - type: "error_rate"
        threshold: 10  # 每分钟10个错误
        window: 5m
    actions:
      - type: "email"
        targets: ["dev@example.com"]
      - type: "slack"
        channel: "#alerts"
  
  # 首次出现错误
  - name: "New Error Type"
    conditions:
      - type: "first_seen"
    actions:
      - type: "email"
        targets: ["dev@example.com"]
  
  # 性能告警
  - name: "Slow API Response"
    conditions:
      - type: "transaction_duration"
        threshold: 5000  # 5秒
        percentile: 95
    actions:
      - type: "slack"
        channel: "#alerts"
```

#### 自定义 Webhook

```python
# 自定义告警处理器
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

@app.post("/webhook/sentry")
async def sentry_webhook(request: Request):
    """Sentry Webhook 处理"""
    data = await request.json()
    
    # 解析告警数据
    error = {
        "project": data.get("project"),
        "error": data.get("event", {}).get("message"),
        "url": data.get("url"),
        "timestamp": data.get("event", {}).get("datetime"),
    }
    
    # 发送到 Slack
    slack_message = {
        "text": f"🚨 新错误: {error['error']}",
        "attachments": [{
            "color": "danger",
            "fields": [
                {"title": "项目", "value": error["project"], "short": True},
                {"title": "时间", "value": error["timestamp"], "short": True},
                {"title": "链接", "value": error["url"], "short": False},
            ]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            json=slack_message
        )
    
    return {"status": "ok"}
```

---

## 免费额度对比

| 服务 | 免费额度 | 超额后 | 适用规模 |
|------|---------|-------|---------|
| **Sentry** | 5K errors/月<br>10K transactions/月 | $26/月（50K） | 1-5K DAU |
| **LogRocket** | 1K sessions/月<br>10K pageviews/月 | $75/月（10K） | 1-3K DAU |
| **Datadog** | 1 host<br>5 custom metrics | $31/host/月 | 10+ hosts |
| **New Relic** | 100GB/month<br>1 user | $99/月 | 中小型 |
| **Grafana Cloud** | 10K metrics<br>50GB logs | $49/月 | 自建监控 |

### 省钱技巧

1. **采样策略**：
```python
# Sentry 性能采样
sentry_sdk.init(
    dsn="YOUR_DSN",
    traces_sample_rate=0.1,  # 10% 采样
)
```

2. **过滤无用错误**：
```python
def before_send(event, hint):
    # 忽略健康检查错误
    if event.get('request', {}).get('url', '').endswith('/health'):
        return None
    return event
```

3. **数据保留策略**：
- Sentry: 免费版保留90天
- Grafana Cloud: 免费版保留14天

---

## 成本估算

| 指标 | 免费方案 | 付费方案（$50-100/月） |
|------|---------|---------------------|
| **错误监控** | 5K errors/月 | 100K+ errors/月 |
| **性能监控** | 10K transactions/月 | 无限制 |
| **数据保留** | 14-90天 | 1年+ |
| **团队协作** | 1人 | 无限团队成员 |
| **高级功能** | 基础 | 会话回放、AI分析 |

---

## 迁出成本

### 从 Sentry 迁出

- **迁出难度**：中
- **迁出步骤**：
  1. 导出错误数据（Sentry API）
  2. 配置新监控系统
  3. 更新应用 SDK
  4. 验证数据采集
  5. 关闭 Sentry

### 从自建监控迁出

- **迁出难度**：高
- **迁出步骤**：
  1. 导出 Prometheus 指标
  2. 配置 Grafana Dashboard 导出
  3. 迁移告警规则
  4. 更新应用指标采集

---

## 与其他武器配合

- **前置**：
  - [API 网关](./api-gateway-simple.md) - 统一入口
  - [日志收集](../saas/log-aggregation.md) - 日志聚合

- **后置**：
  - [应急响应](../../guides/indie-incident-response.md) - 错误处理
  - [性能优化](../free-tier/performance-optimization.md) - 性能调优

- **替代**：无（监控是必需的）

- **互补**：
  - [API 认证](./api-auth-guide.md) - 错误追踪
  - [限流](./rate-limiting-simple.md) - 流量监控

---

## 常见问题

**Q: Sentry vs LogRocket，怎么选？**

A:
- 后端错误 → Sentry
- 前端用户体验 → LogRocket
- 预算有限 → Sentry（免费额度更大）

**Q: 如何降低监控成本？**

A:
1. 降低采样率（10-20%）
2. 过滤无用错误（健康检查、404）
3. 缩短数据保留时间
4. 使用 Grafana Cloud 自建监控

**Q: 如何避免告警风暴？**

A:
```python
# Sentry 告警配置
rules:
  - name: "Error Spike"
    conditions:
      - type: "error_rate"
        threshold: 10
        window: 5m
    # 避免重复告警
    frequency: 1h  # 每小时最多告警一次
    # 分组告警
    group_by: "error.type"
```

**Q: 如何保护用户隐私？**

A:
```python
def before_send(event, hint):
    # 移除 PII 信息
    if 'request' in event:
        request = event['request']
        
        # 移除敏感 Header
        for key in ['authorization', 'cookie', 'x-api-key']:
            request['headers'].pop(key, None)
        
        # 移除敏感查询参数
        if 'query_string' in request:
            params = parse_qs(request['query_string'])
            for key in ['token', 'password', 'api_key']:
                params.pop(key, None)
            request['query_string'] = urlencode(params, doseq=True)
        
        # 移除敏感请求体
        if 'data' in request:
            try:
                body = json.loads(request['data'])
                for key in ['password', 'token', 'credit_card']:
                    body.pop(key, None)
                request['data'] = json.dumps(body)
            except:
                pass
    
    return event
```

---

## 推荐实现

### 完整方案（Sentry + Prometheus + Grafana）

```bash
# 目录结构
mkdir -p monitoring/{prometheus,grafana/provisioning}
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SENTRY_DSN=${SENTRY_DSN}
      - ENVIRONMENT=production
    depends_on:
      - prometheus

  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3001:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false

volumes:
  prometheus-data:
  grafana-data:
```

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - /etc/prometheus/rules.yml

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api'
    static_configs:
      - targets: ['app:8000']
    metrics_path: '/metrics'
```

```yaml
# monitoring/prometheus/rules.yml
groups:
  - name: api_rules
    rules:
      # 错误率告警
      - alert: HighErrorRate
        expr: rate(api_request_count{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      # 响应时间告警
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(api_request_latency_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API response time"
          description: "P95 latency is {{ $value }}s"
```

```python
# app/main.py - 完整示例
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import time
import os

# Sentry 初始化
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development"),
    traces_sample_rate=0.1,
    integrations=[FastApiIntegration()],
)

# Prometheus 指标
REQUEST_COUNT = Counter(
    'api_request_count',
    'API Request Count',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_latency_seconds',
    'API Request Latency',
    ['method', 'endpoint']
)

app = FastAPI(title="Monitored API")

# 中间件：记录指标
@app.middleware("http")
async def add_metrics(request: Request, call_next):
    # 排除 metrics 端点
    if request.url.path == "/metrics":
        return await call_next(request)
    
    start_time = time.time()
    response = await call_next(request)
    
    # 记录请求计数
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    # 记录延迟
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response

# Metrics 端点
@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain"
    )

# 业务路由
@app.get("/api/users")
async def get_users():
    return {"users": ["Alice", "Bob"]}

@app.get("/api/error")
async def trigger_error():
    # 测试错误追踪
    division_by_zero = 1 / 0
    return {"status": "error"}

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 参考资料

- [Sentry 官方文档](https://docs.sentry.io/)
- [LogRocket 官方文档](https://docs.logrocket.com/)
- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [OpenTelemetry 官方文档](https://opentelemetry.io/docs/)
- [SRE 监控最佳实践](https://sre.google/sre-book/monitoring-distributed-systems/)
