# 开源错误追踪

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测
- **实现成本**: 免费（Sentry免费层）或自托管
- **实施时间**: 30分钟
- **维护成本**: 20分钟/月
- **最后验证日期**: 2026-06-11

## 适用场景
实时追踪应用中的错误和异常,自动聚合相似错误,快速定位问题根源,提升用户体验。

---

## 快速上手（5分钟）

### Sentry 快速配置
```bash
# 1. 注册 Sentry 免费账号
# https://sentry.io/signup/

# 2. 创建项目
# - 选择平台: Node.js / Python / JavaScript
# - 获取 DSN

# 3. 安装 SDK
npm install @sentry/node

# 4. 初始化（Node.js）
# sentry.js
const Sentry = require("@sentry/node");
Sentry.init({
  dsn: "https://xxx@xxx.ingest.sentry.io/xxx",
  environment: process.env.NODE_ENV
});
```

---

## 详细方案

### 方案架构
```
应用代码
    ↓
Sentry SDK (捕获异常)
    ↓
Sentry Server (聚合分析)
    ↓
告警规则 → Email / Slack / Webhook
    ↓
错误详情 → SourceMap还原 → 快速定位
```

### 方案对比

| 方案 | 免费额度 | 类型 | SourceMap | 性能监控 | 集成 |
|------|---------|------|-----------|---------|------|
| **Sentry** | 5,000错误/月 | SaaS | ✅ | ✅ | 丰富 |
| **GlitchTip** | 无限制 | 自托管 | ✅ | ❌ | Sentry兼容 |
| **Bugsnag** | 7,500错误/月 | SaaS | ✅ | ❌ | 中等 |
| **Rollbar** | 5,000错误/月 | SaaS | ✅ | ❌ | 中等 |

---

### Sentry 详细配置

#### Node.js 集成
```javascript
// sentry-setup.js
const Sentry = require("@sentry/node");
const { ProfilingIntegration } = require("@sentry/profiling-node");

Sentry.init({
  dsn: process.env.SENTRY_DSN,

  // 环境标识
  environment: process.env.NODE_ENV,
  release: process.env.npm_package_version,

  // 性能监控
  integrations: [
    new ProfilingIntegration(),
  ],

  // 采样率
  tracesSampleRate: 0.1, // 10% 性能追踪
  profilesSampleRate: 0.1, // 10% 性能分析

  // 错误过滤
  beforeSend(event, hint) {
    // 过滤敏感信息
    if (event.request?.headers) {
      delete event.request.headers.authorization;
      delete event.request.headers.cookie;
    }

    // 过滤特定错误
    if (event.exception?.values?.[0]?.type === 'NetworkError') {
      return null; // 不上报网络错误
    }

    return event;
  },

  // 忽略特定错误
  ignoreErrors: [
    'NetworkError',
    'TopLevelFrameError',
    /ResizeObserver loop/,
  ],
});

// Express 中间件
const express = require('express');
const app = express();

// 请求处理中间件
app.use(Sentry.Handlers.requestHandler());

// 路由处理中间件（必须在所有路由之前）
app.use(Sentry.Handlers.tracingHandler());

// 你的路由
app.get('/api/users', (req, res) => {
  // 手动捕获异常
  try {
    // 业务逻辑
  } catch (error) {
    Sentry.captureException(error);
    throw error;
  }
});

// 错误处理中间件（必须在所有路由之后）
app.use(Sentry.Handlers.errorHandler());
```

#### React 集成
```javascript
// sentry-react.js
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  integrations: [
    new BrowserTracing(),
  ],

  // 性能监控
  tracesSampleRate: 0.1,

  // 会话重放（付费功能）
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,

  // React 错误边界
  beforeSend(event) {
    // 过滤开发环境错误
    if (process.env.NODE_ENV === 'development') {
      return null;
    }
    return event;
  },
});

// 错误边界组件
const SentryErrorBoundary = Sentry.ErrorBoundary;

function App() {
  return (
    <SentryErrorBoundary fallback={<ErrorFallback />}>
      <YourApp />
    </SentryErrorBoundary>
  );
}

// 手动捕获
function handleClick() {
  try {
    // 业务逻辑
  } catch (error) {
    Sentry.captureException(error);
  }
}

// 添加用户上下文
function setUserContext(user) {
  Sentry.setUser({
    id: user.id,
    email: user.email,
    username: user.username,
  });
}

// 添加面包屑（追踪用户行为）
function trackUserAction(action) {
  Sentry.addBreadcrumb({
    category: 'user',
    message: action,
    level: 'info',
  });
}
```

#### Python 集成
```python
# sentry_python.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlAlchemyIntegration

sentry_sdk.init(
    dsn="https://xxx@xxx.ingest.sentry.io/xxx",
    integrations=[
        FlaskIntegration(),
        SqlAlchemyIntegration(),
    ],
    environment="production",
    traces_sample_rate=0.1,

    # 过滤敏感数据
    before_send=lambda event, hint: event,
)

# Flask 应用
from flask import Flask
app = Flask(__name__)

@app.route('/api/users')
def get_users():
    try:
        # 业务逻辑
        pass
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise

# 添加上下文
with sentry_sdk.configure_scope() as scope:
    scope.set_user({"id": user.id, "email": user.email})
    scope.set_tag("page", "dashboard")
    scope.set_extra("data", {"key": "value"})
```

---

### 错误聚合配置

#### 聚合规则
```yaml
# Sentry 项目设置 → Issue Settings → Grouping

# 相同错误自动聚合
# - 相同异常类型和消息
# - 相同堆栈跟踪
# - 相同文件和行号

# 自定义指纹（高级）
# 在 beforeSend 中设置
beforeSend(event) {
  // 自定义聚合规则
  if (event.exception?.values?.[0]?.type === 'DatabaseError') {
    event.fingerprint = ['database-error', event.request?.url];
  }
  return event;
}
```

#### 忽略规则
```javascript
// sentry-ignore.js
Sentry.init({
  // 忽略特定错误类型
  ignoreErrors: [
    // 网络错误
    'NetworkError',
    'Network request failed',

    // 浏览器扩展错误
    'Non-Error promise rejection captured',

    // ResizeObserver 错误
    /ResizeObserver loop limit exceeded/,

    // 第三方脚本错误
    /script error/i,
  ],

  // 忽略特定URL的错误
  denyUrls: [
    /chrome-extension/i,
    /moz-extension/i,
    /safari-extension/i,
  ],

  // 只捕获特定URL的错误
  allowUrls: [
    /https:\/\/yourdomain\.com/,
    /https:\/\/api\.yourdomain\.com/,
  ],
});
```

---

### 告警规则配置

#### Sentry 告警规则
```yaml
# Sentry 项目设置 → Alerts → Create Alert

# 规则1: 新错误告警
条件: An issue is first seen
动作: Send email to team@example.com
频率: 每次触发

# 规则2: 错误频率告警
条件: The issue happens more than 10 times in 1 hour
动作: Send Slack notification
频率: 每10分钟最多一次

# 规则3: 未处理错误告警
条件: An issue is unresolved for more than 24 hours
动作: Send email to lead@example.com
频率: 每天一次

# 规则4: 性能问题告警
条件: Transaction duration > 5s
动作: Send Slack notification
频率: 每小时最多一次
```

#### Slack 集成
```bash
# 1. Sentry 项目设置 → Integrations → Slack
# 2. 授权 Slack 工作区
# 3. 选择通知频道

# 自定义通知规则
# - 新错误 → #engineering-alerts
# - 高频错误 → #oncall
# - 性能问题 → #performance
```

---

### SourceMap 配置

#### 为什么需要 SourceMap?
```
生产代码（压缩后）:
  at Object.a (main.123abc.js:1:2345)
  at Object.b (main.123abc.js:1:3456)

还原后（可读）:
  at handleClick (src/components/Button.tsx:15:5)
  at onSubmit (src/pages/Form.tsx:42:10)
```

#### Webpack 配置
```javascript
// webpack.config.js
module.exports = {
  mode: 'production',

  // 生成 SourceMap
  devtool: 'hidden-source-map', // 或 'source-map'

  output: {
    filename: '[name].[contenthash].js',
    sourceMapFilename: '[name].[contenthash].js.map',
  },

  plugins: [
    // 上传 SourceMap 到 Sentry
    new SentryWebpackPlugin({
      org: 'your-org',
      project: 'your-project',
      authToken: process.env.SENTRY_AUTH_TOKEN,

      // 包含的 SourceMap
      include: './dist',
      ignore: ['node_modules'],

      // 发布版本
      release: process.env.npm_package_version,
    }),
  ],
};
```

#### Vite 配置
```javascript
// vite.config.js
import { defineConfig } from 'vite';
import sentryVitePlugin from '@sentry/vite-plugin';

export default defineConfig({
  build: {
    sourcemap: 'hidden',
  },

  plugins: [
    sentryVitePlugin({
      org: 'your-org',
      project: 'your-project',
      authToken: process.env.SENTRY_AUTH_TOKEN,
      release: {
        name: process.env.npm_package_version,
      },
    }),
  ],
});
```

#### 手动上传 SourceMap
```bash
# 安装 Sentry CLI
npm install -g @sentry/cli

# 上传 SourceMap
sentry-cli releases new <version>
sentry-cli releases files <version> upload-sourcemaps ./dist \
  --url-prefix ~/static/js/ \
  --rewrite
sentry-cli releases finalize <version>
```

---

### GlitchTip 自托管方案

#### 为什么自托管?
```
✅ 无错误数量限制
✅ 完全控制数据
✅ Sentry SDK 兼容
✅ 无隐私担忧
✅ 可自定义功能
```

#### Docker 部署
```yaml
# docker-compose.yml
version: '3'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: glitchtip
      POSTGRES_USER: glitchtip
      POSTGRES_PASSWORD: glitchtip
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis-data:/data

  web:
    image: glitchtip/glitchtip:latest
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgres://glitchtip:glitchtip@postgres:5432/glitchtip
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key
      GLITCHTIP_DOMAIN: https://glitchtip.yourdomain.com
    volumes:
      - uploads:/code/uploads

  worker:
    image: glitchtip/glitchtip:latest
    depends_on:
      - postgres
      - redis
    command: ./bin/run-worker
    environment:
      DATABASE_URL: postgres://glitchtip:glitchtip@postgres:5432/glitchtip
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key

  migrate:
    image: glitchtip/glitchtip:latest
    depends_on:
      - postgres
    command: ./bin/run-migrate
    environment:
      DATABASE_URL: postgres://glitchtip:glitchtip@postgres:5432/glitchtip
      SECRET_KEY: your-secret-key

volumes:
  postgres-data:
  redis-data:
  uploads:
```

#### 使用 GlitchTip
```javascript
// 与 Sentry SDK 完全兼容
const Sentry = require("@sentry/node");

Sentry.init({
  // 只需修改 DSN 指向自托管服务
  dsn: "https://xxx@glitchtip.yourdomain.com/xxx",
  // 其他配置与 Sentry 相同
});
```

---

## 成本估算

### 免费方案对比

| 方案 | 错误数量 | 团队成员 | 数据保留 | 性能监控 |
|------|---------|---------|---------|---------|
| **Sentry Free** | 5,000/月 | 1 | 30天 | ✅ |
| **GlitchTip** | 无限制 | 无限制 | 自定义 | ❌ |
| **Bugsnag Free** | 7,500/月 | 1 | 7天 | ❌ |

### 付费升级对比

| 服务 | 价格 | 错误数量 | 团队成员 | 特点 |
|------|------|---------|---------|------|
| Sentry Team | $26/月 | 50,000 | 5 | 会话重放 |
| Sentry Business | $80/月 | 200,000 | 无限 | SSO |
| Bugsnag Pro | $35/月 | 无限制 | 5 | 稳定性评分 |

### 自托管成本
```
GlitchTip 自托管:
- 服务器: $10-20/月（小型云服务器）
- 存储: 根据错误量，约 $5-10/月
- 带宽: 通常可忽略
总计: $15-30/月（无错误数量限制）
```

---

## 迁出成本

### Sentry 迁出
- **迁出难度**: 低
- **时间估算**: 2-4小时
- **步骤**:
  1. 导出错误数据（API）
  2. 导出告警规则配置
  3. 修改 DSN 指向新服务
  4. 重新上传 SourceMap

### GlitchTip 迁出
- **迁出难度**: 中
- **时间估算**: 1天
- **步骤**:
  1. 导出数据库
  2. 迁移到新服务器
  3. 更新 DNS 配置
  4. 重新部署应用

---

## 与其他武器配合

### 推荐组合
```
完整错误处理体系:
├── Sentry (错误追踪)
├── UptimeRobot (可用性监控)
├── Grafana Loki (日志聚合)
└── Prometheus (性能监控)
```

### 前置武器
- **日志系统**: 补充错误上下文
- **性能监控**: 发现性能问题

### 后置武器
- **告警系统**: 及时通知错误
- **事故响应**: 处理严重错误

---

## 常见问题

### Q: 5,000错误/月够用吗?
A: 对于独立开发者通常够用:
- 平均每天约160个错误
- 相同错误会聚合,实际错误类型更少
- 如超限,可考虑自托管 GlitchTip

### Q: SourceMap 必须吗?
A: 强烈建议配置:
- 生产代码压缩后难以定位
- SourceMap 还原真实代码位置
- 节省调试时间,提升效率

### Q: 如何减少噪音?
A:
1. 配置忽略规则过滤无关错误
2. 设置告警阈值避免频繁通知
3. 定期处理已解决错误
4. 使用指纹自定义聚合规则

### Q: Sentry vs 自托管?
A:
- **选 Sentry**: 快速上手,无需运维,功能完整
- **选 GlitchTip**: 无错误限制,数据自主,成本可控

---

## 推荐实现

### 小型项目（推荐）
- **Sentry Free** - https://sentry.io - 5,000错误/月
- 简单易用,功能强大

### 中型项目
- **Sentry Team** - $26/月 - 50,000错误
- 团队协作,会话重放

### 自托管需求
- **GlitchTip** - https://glitchtip.com
- Sentry兼容,无限制

### 其他选择
- **Bugsnag** - https://bugsnag.com - 7,500错误/月
- **Rollbar** - https://rollbar.com - 5,000错误/月

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
