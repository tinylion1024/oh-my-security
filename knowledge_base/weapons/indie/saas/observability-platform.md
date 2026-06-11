# 可观测平台对比

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测
- **实现成本**: 免费（免费层）到 $100+/月
- **实施时间**: 2小时 - 1天
- **维护成本**: 1小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
选择适合团队规模和预算的可观测平台,整合日志、指标、链路追踪,实现全栈监控能力。

---

## 快速上手（5分钟）

### 平台选择决策树
```
你的团队规模?
├── 1人 → Grafana Cloud Free
├── 2-10人 → Grafana Cloud Pro ($49/月)
└── 10+人 → Datadog / New Relic

你的预算?
├── $0 → Grafana Cloud Free
├── $50-100/月 → Grafana Cloud Pro / New Relic
└── 无上限 → Datadog / Dynatrace

你的技术栈?
├── Kubernetes → Datadog / Grafana Cloud
├── Serverless → New Relic / AWS X-Ray
└── 传统部署 → Grafana Cloud / Prometheus
```

---

## 详细方案

### 平台功能对比矩阵

| 功能 | Grafana Cloud | Datadog | New Relic | Dynatrace |
|------|--------------|---------|-----------|-----------|
| **日志管理** | ✅ Loki | ✅ | ✅ | ✅ |
| **指标监控** | ✅ Prometheus | ✅ | ✅ | ✅ |
| **链路追踪** | ✅ Tempo | ✅ APM | ✅ APM | ✅ APM |
| **性能分析** | ✅ Pyroscope | ✅ | ✅ | ✅ |
| **告警系统** | ✅ AlertManager | ✅ | ✅ | ✅ |
| **Dashboard** | ✅ Grafana | ✅ | ✅ | ✅ |
| **AI分析** | ❌ | ✅ | ✅ | ✅ |
| **自动发现** | ❌ | ✅ | ✅ | ✅ |

---

## Grafana Cloud

### 免费层详情

```
Grafana Cloud Free:
├── 用户: 3个
├── 日志: 50GB/月 (Loki)
├── 指标: 10K series (Prometheus)
├── 追踪: 50GB/月 (Tempo)
├── 保留: 14天
└── 成本: $0/月
```

### 付费层对比

| 计划 | 用户 | 日志 | 指标 | 价格 |
|------|------|------|------|------|
| **Free** | 3 | 50GB | 10K series | $0 |
| **Pro** | 10 | 100GB | 50K series | $49 |
| **Advanced** | 无限 | 自定义 | 自定义 | 自定义 |

### 快速配置

```bash
# 1. 注册 Grafana Cloud
# https://grafana.com/signup

# 2. 安装 Grafana Agent
curl -fsSL https://apt.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://apt.grafana.com stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt-get update && sudo apt-get install grafana-agent

# 3. 配置 Agent
# /etc/grafana-agent.yaml
server:
  log_level: info

metrics:
  wal_directory: /tmp/agent/wal
  global:
    scrape_interval: 15s
  configs:
    - name: default
      remote_write:
        - url: https://<your-grafana-cloud-id>.grafana.net/api/prom/push
          basic_auth:
            username: <your-user-id>
            password: <your-api-key>
      scrape_configs:
        - job_name: node
          static_configs:
            - targets: ['localhost:9100']

logs:
  configs:
    - name: default
      clients:
        - url: https://<your-user-id>:<your-api-key>@<your-grafana-cloud-id>.grafana.net/loki/api/v1/push
      positions:
        filename: /tmp/positions.yaml
      scrape_configs:
        - job_name: app
          static_configs:
            - targets: ['localhost']
              labels:
                job: app
                __path__: /var/log/app/*.log
```

### 优势与劣势

```
优势:
✅ 开源生态,无锁定
✅ 免费层慷慨(50GB日志)
✅ 社区支持强大
✅ Dashboard功能最强
✅ 多数据源整合

劣势:
❌ 配置复杂度高
❌ 无AI分析
❌ 自动发现较弱
❌ 学习曲线陡峭
```

---

## Datadog

### 免费试用与定价

```
Datadog Free Trial:
├── 时长: 14天
├── 功能: 完整功能
├── 用户: 5个
└── 成本: $0

付费计划:
├── Pro: $15/host/月
├── Enterprise: $27/host/月
└── 最低消费: $31/月
```

### 快速配置

```bash
# 1. 注册 Datadog
# https://www.datadoghq.com/free-datadog-trial/

# 2. 安装 Agent (Linux)
DD_API_KEY=<your-api-key> DD_SITE="datadoghq.com" bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# 3. 应用集成
npm install dd-trace

# Node.js 应用
const tracer = require('dd-trace').init({
  service: 'my-app',
  env: 'production'
});
```

### 主要功能

```javascript
// APM 自动追踪
const tracer = require('dd-trace').init();

// 自定义追踪
const span = tracer.startSpan('custom.operation');
// ... 业务逻辑
span.finish();

// 自定义指标
const dogstatsd = require('datadog-metrics');
dogstatsd.increment('myapp.requests', 1, ['endpoint:users']);

// 日志集成
const winston = require('winston');
const { DatadogTransport } = require('winston-datadog');

const logger = winston.createLogger({
  transports: [
    new DatadogTransport({
      apiKey: process.env.DD_API_KEY,
      hostname: 'my-app'
    })
  ]
});
```

### 优势与劣势

```
优势:
✅ 功能最全面
✅ AI异常检测
✅ 自动服务发现
✅ 用户体验优秀
✅ 集成生态丰富(600+)

劣势:
❌ 价格昂贵
❌ 存在锁定风险
❌ 数据出境合规问题
❌ 学习成本较高
```

---

## New Relic

### 免费层详情

```
New Relic Free:
├── 用户: 无限
├── 数据摄入: 100GB/月
├── 用户数: 无限
├── 保留: 3天(免费层)
└── 成本: $0/月

付费层:
├── Pro: $0.30/GB
├── Enterprise: 自定义
└── 保留: 可延长至13个月
```

### 快速配置

```bash
# 1. 注册 New Relic
# https://newrelic.com/signup

# 2. 安装 Infrastructure Agent
curl -Ls https://download.newrelic.com/infrastructure_agent/gpg/newrelic-infra.gpg | sudo apt-key add -
echo "deb https://download.newrelic.com/infrastructure_agent/linux/apt/ main" | sudo tee /etc/apt/sources.list.d/newrelic-infra.list
sudo apt-get update && sudo apt-get install newrelic-infra

# 3. Node.js APM
npm install newrelic

# newrelic.js
exports.config = {
  app_name: ['My App'],
  license_key: 'your-license-key',
  logging: {
    level: 'info'
  }
}
```

### NRQL 查询示例

```sql
-- 1. 查询错误率
SELECT percentage(count(*), WHERE error is true)
FROM Transaction
WHERE appName = 'My App'
SINCE 1 hour ago

-- 2. 查询响应时间分布
SELECT histogram(duration)
FROM Transaction
WHERE appName = 'My App'
FACET name

-- 3. Top 10 慢查询
SELECT average(duration)
FROM Transaction
WHERE appName = 'My App'
FACET name
ORDER BY average(duration) DESC
LIMIT 10

-- 4. 错误趋势
SELECT count(*)
FROM Transaction
WHERE error is true
FACET appName
TIMESERIES auto

-- 5. 用户地理位置分布
SELECT uniqueCount(session)
FROM PageView
FACET countryCode
SINCE 1 day ago
```

### 优势与劣势

```
优势:
✅ 免费层最慷慨(100GB/月)
✅ 用户数不限
✅ NRQL查询强大
✅ UI现代化
✅ Full-Stack可观测

劣势:
❌ AI功能较弱
❌ 集成生态少于Datadog
❌ Dashboard灵活性不如Grafana
❌ 部分高级功能付费
```

---

## Dynatrace

### 定价模型

```
Dynatrace 定价:
├── 计费单位: Davis Units (DUs)
├── 价格: $0.014/DU
├── 典型主机: 100-500 DUs/月
└── 最低消费: 自定义

试用:
├── 时长: 15天
├── 功能: 完整功能
└── 成本: $0
```

### 快速配置

```bash
# 1. 注册 Dynatrace
# https://www.dynatrace.com/trial/

# 2. 下载 OneAgent
# Dashboard → Deploy Dynatrace → Download OneAgent

# 3. 安装
/bin/sh /path/to/Dynatrace-OneAgent-Linux.sh

# 自动发现和监控无需额外配置
```

### 主要功能

```
Dynatrace 特点:
├── Davis AI (自动化根因分析)
├── 全栈自动发现
├── Smartscape (拓扑图)
├── 自动基线检测
├── 实时应用拓扑
└── 无需手动配置

AI 功能:
├── 异常自动检测
├── 根因自动定位
├── 影响范围分析
├── 性能预测
└── 自动告警降噪
```

### 优势与劣势

```
优势:
✅ AI能力最强(Davis)
✅ 自动化程度最高
✅ 零配置监控
✅ 企业级功能
✅ 性能分析深度

劣势:
❌ 价格最贵
❌ 学习曲线陡峭
❌ 中小团队过度
❌ 灵活性较低
```

---

## 成本对比

### 小型团队（5人以下）

| 平台 | 月成本 | 数据量 | 优势 |
|------|--------|--------|------|
| **Grafana Cloud Free** | $0 | 50GB | 开源生态 |
| **New Relic Free** | $0 | 100GB | 最慷慨 |
| **Datadog Pro** | $31 | ~2主机 | 功能全面 |

### 中型团队（10-20人）

| 平台 | 月成本 | 数据量 | 适用场景 |
|------|--------|--------|---------|
| **Grafana Cloud Pro** | $49 | 100GB | Kubernetes |
| **New Relic Pro** | $100 | ~300GB | 全栈监控 |
| **Datadog Pro** | $150 | ~10主机 | 复杂架构 |

### 大型团队（50人+）

| 平台 | 月成本 | 数据量 | 特点 |
|------|--------|--------|------|
| **Grafana Cloud** | 自定义 | 无限 | 灵活 |
| **Datadog Enterprise** | $500+ | 自定义 | 功能全 |
| **Dynatrace** | $500+ | 自定义 | AI强 |

---

## 成本优化建议

### 数据采样策略

```yaml
# Grafana Agent 配置
metrics:
  global:
    scrape_interval: 15s
  configs:
    - name: default
      remote_write:
        - url: https://...
          # 降低高基数指标采样
          write_relabel_configs:
            - source_labels: [__name__]
              regex: 'high_cardinality_metric.*'
              action: drop

logs:
  configs:
    - name: default
      # 过滤调试日志
      scrape_configs:
        - job_name: app
          pipeline_stages:
            - match:
                selector: '{level="debug"}'
                action: drop
```

### 智能过滤

```javascript
// 日志过滤
if (process.env.NODE_ENV === 'production') {
  // 仅上报 warn 及以上级别
  logger.transports.forEach(transport => {
    if (transport.level === 'debug') {
      transport.silent = true;
    }
  });
}

// 指标过滤
const metrics = {
  // 仅保留关键指标
  include: [
    'http_request_duration_seconds',
    'http_requests_total',
    'process_cpu_seconds_total',
    'process_resident_memory_bytes'
  ],

  // 过滤高基数指标
  exclude: [
    'http_request_duration_seconds_bucket',
    'process_open_fds'
  ]
};
```

### 成本监控

```sql
-- New Relic 成本监控
SELECT sum(GigabytesIngested)
FROM NrUsage
FACET ProductLine
SINCE 1 month ago

-- 设置告警
SELECT sum(GigabytesIngested)
FROM NrUsage
WHERE ProductLine = 'Logs'
SINCE 1 day ago
```

---

## 迁出成本

### 各平台迁出对比

| 平台 | 迁出难度 | 时间估算 | 关键步骤 |
|------|---------|---------|---------|
| **Grafana Cloud** | 低 | 1-2天 | 导出Dashboard,数据迁移 |
| **New Relic** | 中 | 2-3天 | NRQL转换,Dashboard重建 |
| **Datadog** | 高 | 3-5天 | 查询转换,集成重写 |
| **Dynatrace** | 高 | 3-5天 | 配置重建,AI规则重写 |

### 避免锁定的最佳实践

```markdown
1. 使用开源标准:
   - 指标: Prometheus格式
   - 日志: JSON格式
   - 追踪: OpenTelemetry

2. 抽象监控层:
   - 封装监控接口
   - 避免平台特定代码
   - 使用中间件模式

3. 定期导出数据:
   - 定期备份Dashboard配置
   - 导出关键指标数据
   - 保留原始日志副本

4. 多平台策略:
   - 核心指标: Prometheus + Grafana
   - 日志: Loki
   - 追踪: Jaeger
   - 避免单一平台依赖
```

---

## 与其他武器配合

### 推荐组合

```
独立开发者（$0）:
├── Grafana Cloud Free (指标+日志+追踪)
├── UptimeRobot (可用性监控)
└── Sentry Free (错误追踪)

小团队（$50-100）:
├── New Relic Pro (全栈监控)
├── UptimeRobot (外部监控)
└── Sentry Team (错误追踪)

中大型团队（$200+）:
├── Datadog Pro (全栈监控+AI)
├── PagerDuty (告警管理)
└── 安全工具集成
```

---

## 常见问题

### Q: 免费层够用吗?
A:
- **Grafana Cloud Free**: 适合小型项目,50GB日志/月
- **New Relic Free**: 最慷慨,100GB/月,适合中型项目
- **超限后**: 考虑自托管或优化数据量

### Q: 如何选择平台?
A:
```
优先考虑:
1. 预算限制
2. 团队规模
3. 技术栈匹配
4. 功能需求

推荐:
- 预算$0 → New Relic Free / Grafana Cloud Free
- 预算$50-100 → Grafana Cloud Pro
- 预算$200+ → Datadog
- 企业级 → Dynatrace
```

### Q: 如何控制成本?
A:
1. 合理设置数据保留
2. 过滤无用日志和指标
3. 降低采样率
4. 使用采样策略
5. 定期审查使用量

---

## 推荐实现

### 独立开发者（推荐）
- **New Relic Free** - https://newrelic.com - 100GB/月
- 或 **Grafana Cloud Free** - https://grafana.com - 50GB/月

### 小团队
- **Grafana Cloud Pro** - $49/月
- 开源生态,灵活可控

### 中大型团队
- **Datadog** - $150-500/月
- 功能全面,AI支持

### 企业级
- **Dynatrace** - 自定义定价
- 最强AI能力

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
