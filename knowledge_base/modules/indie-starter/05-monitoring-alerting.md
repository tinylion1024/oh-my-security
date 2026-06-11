# 第 5 周：监控告警

## 概述

本周部署监控告警系统，建立持续安全运营能力。

**预计时间**: 2 小时
**难度**: 简单
**成本**: $0

---

## 监控指标选择

### 核心监控指标

| 指标类型 | 指标名称 | 告警阈值 |
|---------|---------|---------|
| **可用性** | 服务在线率 | < 99% |
| **性能** | 响应时间 | > 2s |
| **安全** | 失败登录次数 | > 10次/分钟 |
| **安全** | API 错误率 | > 5% |
| **资源** | CPU 使用率 | > 80% |
| **资源** | 内存使用率 | > 85% |
| **资源** | 磁盘使用率 | > 90% |

---

## 免费监控工具配置

### UptimeRobot（服务可用性）

```bash
# API 创建监控
curl -X POST "https://api.uptimerobot.com/v2/newMonitor" \
  -d "api_key=YOUR_API_KEY" \
  -d "friendly_name=My Website" \
  -d "url=https://yourdomain.com" \
  -d "type=1" \
  -d "interval=300"
```

**配置步骤**:
1. 注册 https://uptimerobot.com
2. 添加监控站点（免费 50 个）
3. 配置告警通知（邮件免费，短信付费）
4. 设置检查间隔（免费版最短 5 分钟）

### Sentry（错误监控）

**Python 集成**:
```python
import sentry_sdk

sentry_sdk.init(
    dsn="https://xxx@sentry.io/xxx",
    traces_sample_rate=0.1,  # 10% 性能追踪
    environment="production"
)

# 自动捕获异常
try:
    1 / 0
except Exception:
    pass  # Sentry 自动上报
```

**Node.js 集成**:
```javascript
const Sentry = require('@sentry/node');

Sentry.init({
    dsn: 'https://xxx@sentry.io/xxx',
    tracesSampleRate: 0.1
});

// 自动捕获
app.use(Sentry.Handlers.errorHandler());
```

### Grafana Cloud（指标监控）

**Prometheus 指标暴露**:
```python
from prometheus_client import Counter, Histogram, generate_latest

# 定义指标
REQUEST_COUNT = Counter('request_count', 'Total requests')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')
LOGIN_FAILURES = Counter('login_failures', 'Failed login attempts')

# 使用
@app.before_request
def before_request():
    REQUEST_COUNT.inc()

@app.after_request
def after_request(response):
    REQUEST_LATENCY.observe(response.response_time)
    return response

@app.route('/metrics')
def metrics():
    return generate_latest()
```

---

## 告警规则设置

### 安全告警规则

```yaml
# 告警规则配置示例
alerts:
  # 1. 登录暴力破解
  - name: login_brute_force
    condition: "login_failures > 10 in 1m"
    severity: high
    message: "检测到登录暴力破解尝试"
    action:
      - block_ip
      - notify_admin

  # 2. API 异常请求
  - name: api_error_spike
    condition: "api_error_rate > 5% in 5m"
    severity: medium
    message: "API 错误率异常"
    action:
      - notify_admin

  # 3. 数据库连接异常
  - name: db_connection_failed
    condition: "db_connections_failed > 3 in 1m"
    severity: critical
    message: "数据库连接失败"
    action:
      - notify_admin
      - auto_restart

  # 4. 磁盘空间不足
  - name: disk_space_low
    condition: "disk_usage > 90%"
    severity: high
    message: "磁盘空间不足"
    action:
      - notify_admin
      - cleanup_logs
```

### 告警通知配置

```python
# 告警通知函数
import requests

def send_alert(message: str, severity: str = 'info'):
    """发送告警通知"""

    # 1. 发送邮件
    send_email(
        to='admin@example.com',
        subject=f'[{severity.upper()}] 安全告警',
        body=message
    )

    # 2. Slack 通知
    if severity in ['high', 'critical']:
        slack_webhook = os.getenv('SLACK_WEBHOOK')
        requests.post(slack_webhook, json={
            'text': f':warning: {message}'
        })

    # 3. 短信通知（仅关键告警）
    if severity == 'critical':
        send_sms(
            phone=os.getenv('ADMIN_PHONE'),
            message=message
        )
```

---

## 应急响应流程

### 简化应急流程

```
发现问题 → 评估严重性 → 采取行动 → 恢复服务 → 复盘改进
    ↓            ↓            ↓           ↓           ↓
  监控告警    P0-P3分级    遏制/修复    验证恢复    记录归档
```

### 严重等级定义

| 等级 | 定义 | 响应时间 | 示例 |
|------|------|---------|------|
| **P0** | 服务完全不可用 | 15 分钟 | 数据库宕机、支付失败 |
| **P1** | 核心功能受损 | 1 小时 | 登录失败、API 异常 |
| **P2** | 部分功能异常 | 4 小时 | 性能下降、告警噪声 |
| **P3** | 轻微问题 | 24 小时 | UI 错位、文案错误 |

### 快速响应清单

```markdown
## 发现问题

- [ ] 确认问题是否真实
- [ ] 记录问题发生时间
- [ ] 检查监控面板

## 评估严重性

- [ ] 影响范围（全部用户 / 部分用户）
- [ ] 影响功能（核心 / 非核心）
- [ ] 确定严重等级

## 采取行动

- [ ] P0: 立即修复或回滚
- [ ] P1: 快速修复
- [ ] P2: 计划修复
- [ ] 通知相关方

## 恢复服务

- [ ] 验证修复效果
- [ ] 确认服务恢复
- [ ] 解除告警

## 复盘改进

- [ ] 记录问题原因
- [ ] 制定预防措施
- [ ] 更新监控规则
```

---

## 持续维护计划

### 日常检查（每天）

- [ ] 查看告警日志
- [ ] 确认服务正常
- [ ] 检查备份状态

### 周度检查（每周）

- [ ] 审查安全日志
- [ ] 检查依赖更新
- [ ] 验证告警规则

### 月度检查（每月）

- [ ] 安全基线审查
- [ ] 备份恢复测试
- [ ] 权限审计
- [ ] 成本优化

---

## 本周实施计划

| 天 | 任务 | 时间 |
|----|------|------|
| Day 1 | UptimeRobot 配置 | 20 分钟 |
| Day 2 | Sentry 集成 | 30 分钟 |
| Day 3 | 告警规则配置 | 20 分钟 |
| Day 4 | 通知渠道配置 | 20 分钟 |
| Day 5 | 应急流程演练 | 30 分钟 |

---

## 验证清单

- [ ] UptimeRobot 已配置
- [ ] Sentry 已集成
- [ ] 核心指标监控已配置
- [ ] 告警规则已设置
- [ ] 通知渠道已配置
- [ ] 应急响应流程已准备
- [ ] 团队已知晓流程

---

## 🎉 恭喜完成！

完成 5 周学习后，你已经建立了基础安全防护体系：

- ✅ 安全基线已建立
- ✅ 账号安全已实施
- ✅ API 安全已配置
- ✅ 数据保护已实施
- ✅ 监控告警已部署

### 下一步建议

1. **定期检查**: 每周审查安全日志
2. **持续学习**: 阅读核心案例库
3. **社区交流**: 加入安全社区学习
4. **工具升级**: 根据需要升级付费工具

### 相关资源

- [MVP 发布检查清单](../mvp-checklist/README.md)
- [应急响应剧本](../incident-playbook/README.md)
- [核心武器库](../../weapons/indie/free-tier/)
- [核心案例库](../../cases/indie/core/)
