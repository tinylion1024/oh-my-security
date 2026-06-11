# 开源日志聚合方案

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测
- **实现成本**: 免费（Grafana Cloud免费层）或自托管
- **实施时间**: 2小时
- **维护成本**: 30分钟/月
- **最后验证日期**: 2026-06-11

## 适用场景
集中管理应用日志,快速搜索和分析,定位问题根源,了解系统运行状态。

---

## 快速上手（5分钟）

### Loki 快速配置
```yaml
# docker-compose.yml (最简配置)
version: '3'
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
```

```bash
# 启动
docker-compose up -d

# 访问 Grafana
# http://localhost:3000
# 添加 Loki 数据源: http://loki:3100
```

---

## 详细方案

### 方案架构
```
应用日志
    ↓
Promtail / Loki Client (采集)
    ↓
Loki (存储 + 索引)
    ↓
Grafana (可视化 + 查询)
```

### 方案对比

| 方案 | 存储成本 | 查询性能 | 部署复杂度 | 资源占用 | 免费额度 |
|------|---------|---------|-----------|---------|---------|
| **Grafana Loki** | 低 | 快 | 低 | 低 | 50GB/月（云版） |
| **ELK Stack** | 高 | 很快 | 高 | 高 | 自托管无限制 |
| **Fluentd** | 中 | 快 | 中 | 中 | 自托管无限制 |
| **Graylog** | 中 | 快 | 中 | 中 | 自托管无限制 |

---

## Loki 详细配置

### 完整 Loki 配置

```yaml
# loki-config.yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

limits_config:
  # 日志保留策略
  reject_old_samples: true
  reject_old_samples_max_age: 168h  # 7天

  # 摄入限制
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20
  per_stream_rate_limit: 5MB

  # 查询限制
  max_query_length: 721h
  max_query_parallelism: 32

  # 缓存配置
  max_cache_freshness_per_query: 10m

ruler:
  alertmanager_url: http://localhost:9093
  storage:
    type: local
    local:
      directory: /loki/rules
  rule_path: /loki/rules-temp
  enable_api: true

# 压缩配置
compactor:
  working_directory: /loki/compactor
  shared_store: filesystem
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150
```

### Promtail 配置（日志采集）

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  # 应用日志
  - job_name: app-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: app
          env: production
          __path__: /var/log/app/*.log

    # 多行日志处理（Java堆栈跟踪）
    pipeline_stages:
      - multiline:
          firstline: '^\d{4}-\d{2}-\d{2}'
          max_wait_time: 3s

      # 提取字段
      - regex:
          expression: '^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?P<level>\w+) (?P<message>.*)$'

      # 设置日志级别标签
      - labels:
          level:

  # Nginx 访问日志
  - job_name: nginx-logs
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/access.log

    pipeline_stages:
      - regex:
          expression: '^(?P<remote_addr>[\d\.]+) - (?P<remote_user>\S+) \[(?P<time>[^\]]+)\] "(?P<method>\w+) (?P<path>\S+) (?P<protocol>[^"]+)" (?P<status>\d+) (?P<body_bytes_sent>\d+)'

      - labels:
          remote_addr:
          method:
          status:

  # Docker 容器日志
  - job_name: docker-logs
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
```

### Docker Compose 完整部署

```yaml
# docker-compose.yml
version: '3'

volumes:
  loki-data:
  grafana-data:
  promtail-positions:

services:
  loki:
    image: grafana/loki:2.9.0
    container_name: loki
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/config.yaml
      - loki-data:/loki
    command: -config.file=/etc/loki/config.yaml
    restart: unless-stopped

  promtail:
    image: grafana/promtail:2.9.0
    container_name: promtail
    volumes:
      - ./promtail-config.yaml:/etc/promtail/config.yaml
      - /var/log:/var/log:ro
      - promtail-positions:/tmp
    command: -config.file=/etc/promtail/config.yaml
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.0.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana-datasources:/etc/grafana/provisioning/datasources
    restart: unless-stopped
```

---

## 日志查询示例

### LogQL 查询语法

```logql
# 基础查询
{job="app"}                    # 查询 app job 的所有日志
{job="app", level="error"}     # 查询 app 的错误日志

# 文本搜索
{job="app"} |= "error"         # 包含 "error"
{job="app"} != "debug"         # 不包含 "debug"
{job="app"} |~ "error|warn"    # 正则匹配

# 字段提取
{job="app"}
  | regexp `(?P<level>\w+) (?P<message>.*)`
  | level = "error"

# 聚合查询
count_over_time({job="app"}[5m])                    # 5分钟日志计数
rate({job="app", level="error"}[5m])                # 错误率
bytes_over_time({job="app"}[1h])                    # 1小时日志大小

# 分组聚合
sum by (level) (count_over_time({job="app"}[5m]))   # 按级别分组计数

# Top N 查询
topk(10, sum by (path) (count_over_time({job="nginx"}[1h])))  # 访问最多的路径
```

### 常用查询示例

```logql
# 1. 查找特定用户的操作日志
{job="app"} |= "user_id=12345"

# 2. 查找HTTP 500错误
{job="nginx"} | json | status = "500"

# 3. 查找慢请求（>1秒）
{job="app"} | regexp `duration=(?P<duration>\d+)ms` | duration > 1000

# 4. 统计各状态码数量
sum by (status) (count_over_time({job="nginx"}[1h]))

# 5. 查找异常堆栈
{job="app"} |~ "Exception.*\n\s+at\s+"

# 6. 查找特定时间段的错误
{job="app", level="error"} [2024-01-01T00:00:00Z, 2024-01-01T01:00:00Z]

# 7. 计算错误率
rate({job="app", level="error"}[5m]) / rate({job="app"}[5m])

# 8. 查找API调用失败的请求
{job="app"} |= "api_call" |= "failed"
```

---

## 日志保留策略

### Loki 保留策略配置

```yaml
# loki-config.yaml
limits_config:
  # 全局保留时间
  retention_period: 168h  # 7天

  # 按流保留
  per_stream_retention:
    - selector: '{level="error"}'
      retention: 720h  # 错误日志保留30天
    - selector: '{level="debug"}'
      retention: 24h   # 调试日志保留1天

compactor:
  retention_enabled: true
  retention_delete_delay: 2h
  retention_delete_worker_count: 150
```

### 自动清理脚本

```bash
#!/bin/bash
# log-cleanup.sh

# 配置
LOG_DIR="/var/log/app"
RETENTION_DAYS=7
ARCHIVE_DIR="/var/log/archive"

# 1. 归档旧日志
find $LOG_DIR -name "*.log" -mtime +$RETENTION_DAYS -exec gzip {} \;
find $LOG_DIR -name "*.gz" -mtime +$RETENTION_DAYS -exec mv {} $ARCHIVE_DIR \;

# 2. 删除过期归档
find $ARCHIVE_DIR -name "*.gz" -mtime +30 -delete

# 3. 清理 Loki 数据（通过API）
curl -X POST http://localhost:3100/loki/api/v1/delete \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{level=\"debug\"}",
    "start": "'$(date -d "-1 day" +%s)'",
    "end": "'$(date +%s)'"
  }'
```

---

## Grafana 可视化

### 预置 Dashboard

```json
// grafana-dashboards/app-logs.json
{
  "dashboard": {
    "title": "Application Logs",
    "panels": [
      {
        "title": "Log Volume",
        "type": "timeseries",
        "targets": [
          {
            "expr": "sum(rate({job=\"app\"}[5m]))",
            "legendFormat": "Total"
          },
          {
            "expr": "sum(rate({job=\"app\", level=\"error\"}[5m]))",
            "legendFormat": "Errors"
          }
        ]
      },
      {
        "title": "Error Logs",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"app\", level=\"error\"}"
          }
        ]
      },
      {
        "title": "Top Error Types",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (error_type) (count_over_time({job=\"app\", level=\"error\"}[1h]))"
          }
        ]
      }
    ]
  }
}
```

### 告警规则

```yaml
# loki-rules.yaml
groups:
  - name: app_alerts
    rules:
      # 错误率告警
      - alert: HighErrorRate
        expr: rate({job="app", level="error"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/s"

      # 特定错误告警
      - alert: DatabaseError
        expr: count_over_time({job="app"} |= "database error"[5m]) > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database errors detected"
          description: "{{ $value }} database errors in last 5 minutes"
```

---

## 应用集成

### Node.js 集成

```javascript
// winston-loki.js
const winston = require('winston');
const LokiTransport = require('winston-loki');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    // 控制台输出
    new winston.transports.Console(),

    // Loki 输出
    new LokiTransport({
      host: 'http://localhost:3100',
      labels: {
        job: 'app',
        env: process.env.NODE_ENV
      },
      json: true,
      batching: true,
      interval: 5, // 批量发送间隔（秒）
    })
  ]
});

// 使用
logger.info('User logged in', { userId: 123, ip: '1.2.3.4' });
logger.error('Payment failed', { orderId: 456, error: err.message });
```

### Python 集成

```python
# logging_loki.py
import logging
from loki_logger_handler import LokiLoggerHandler

# 创建 Loki handler
loki_handler = LokiLoggerHandler(
    url="http://localhost:3100/loki/api/v1/push",
    labels={
        "job": "app",
        "env": "production"
    }
)

# 配置 logger
logger = logging.getLogger()
logger.addHandler(loki_handler)
logger.setLevel(logging.INFO)

# 使用
logger.info("User logged in", extra={"user_id": 123})
logger.error("Payment failed", extra={"order_id": 456})
```

### Go 集成

```go
// loki.go
package main

import (
    "github.com/grafana/loki-client-go/loki"
)

func main() {
    config := loki.Config{
        URL:      "http://localhost:3100/loki/api/v1/push",
        Labels:   map[string]string{"job": "app", "env": "production"},
        BatchWait: 5 * time.Second,
        BatchSize: 10000,
    }

    client, _ := loki.New(config)
    defer client.Stop()

    // 发送日志
    client.Handle(loki.LabelSet{}, time.Now(), "User logged in")
}
```

---

## 成本估算

### 自托管成本

| 组件 | 内存 | CPU | 存储 | 月成本 |
|------|------|-----|------|--------|
| **Loki** | 1-2GB | 1核 | 根据日志量 | $10-20 |
| **Promtail** | 256MB | 0.5核 | 忽略 | $5 |
| **Grafana** | 512MB | 0.5核 | 1GB | $5 |
| **总计** | 2-3GB | 2核 | 可变 | $20-30 |

### Grafana Cloud 免费层

```
免费额度:
- 50GB 日志/月
- 3个用户
- 30天保留

超出后:
- $0.50/GB
- 或升级付费计划
```

### 存储估算

```
日志量估算:
- 小型应用: 1-5GB/月
- 中型应用: 10-50GB/月
- 大型应用: 100GB+/月

存储成本:
- Loki: 原日志的 10-20% (压缩后)
- ELK: 原日志的 50-100% (索引开销)
```

---

## 迁出成本

### Loki 迁出
- **迁出难度**: 中
- **时间估算**: 1-2天
- **步骤**:
  1. 导出日志数据（API或命令行）
  2. 转换查询语法（如迁到ELK）
  3. 迁移Dashboard配置
  4. 更新应用日志配置

### ELK 迁出
- **迁出难度**: 高
- **时间估算**: 2-3天
- **步骤**:
  1. 重建索引结构
  2. 转换查询DSL
  3. 迁移可视化面板
  4. 调整性能参数

---

## 与其他武器配合

### 推荐组合
```
日志体系:
├── Loki (日志聚合)
├── Sentry (错误追踪)
├── Prometheus (指标监控)
├── Grafana (可视化)
└── AlertManager (告警)
```

### 前置武器
- **应用日志**: 结构化日志输出
- **Prometheus**: 指标数据补充

### 后置武器
- **告警系统**: 基于日志的告警
- **事故响应**: 日志分析定位问题

---

## 常见问题

### Q: Loki vs ELK 如何选择?
A:
- **选 Loki**: 资源有限、成本敏感、日志量大
- **选 ELK**: 需要全文搜索、复杂查询、强大分析

### Q: 如何减少存储成本?
A:
1. 合理设置保留策略
2. 压缩旧日志
3. 过滤无用日志
4. 使用对象存储（S3/GCS）

### Q: 查询慢怎么办?
A:
1. 优化标签设计（避免高基数）
2. 使用查询缓存
3. 限制查询时间范围
4. 增加查询并行度

---

## 推荐实现

### 小型项目（推荐）
- **Grafana Cloud** - https://grafana.com - 50GB/月免费
- 无需运维,快速上手

### 中型项目
- **Loki 自托管** - Docker部署
- 完全控制,成本可控

### 大型项目
- **Loki + S3** - 对象存储后端
- 水平扩展,高性能

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
