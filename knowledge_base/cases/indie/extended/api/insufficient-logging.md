# 日志不足 (Insufficient Logging)

> **Tier 适用**: L1 ✅

## 一句话风险

关键操作未记录日志或日志级别不当，导致无法检测攻击、追踪溯源和应急响应。

## 一分钟识别清单

- [ ] 认证成功/失败未记录日志
- [ ] 敏感操作（增删改）无审计日志
- [ ] 日志中缺少关键信息（用户、IP、时间、操作）

## 一句话防御

记录所有认证、授权、敏感操作日志，并集中存储和监控告警。

## 推荐工具链接

- [ELK Stack](https://www.elastic.co/elastic-stack/) - 日志分析平台
- [Wazuh](https://wazuh.com/) - 安全监控和日志分析
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 暴力破解 | 无登录失败日志，无法发现攻击 |
| 越权操作 | 无操作审计，无法追溯责任 |
| 数据泄露 | 无访问日志，无法确定泄露范围 |
| 内部威胁 | 缺少操作日志，无法审计员工行为 |

## 必须记录的事件

| 类别 | 事件 |
|------|------|
| 认证 | 登录成功/失败、登出、密码修改 |
| 授权 | 权限变更、角色分配 |
| 敏感操作 | 数据创建/修改/删除 |
| 系统操作 | 配置变更、服务启停 |
| 异常行为 | 频繁失败、异常请求 |

## 日志规范示例

```python
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

def log_security_event(event_type, user_id, ip_address, details):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "ip_address": ip_address,
        "details": details,
        "request_id": request.id if hasattr(request, 'id') else None
    }
    logger.warning(json.dumps(log_entry))

# 使用示例
log_security_event(
    event_type="LOGIN_FAILED",
    user_id="user@example.com",
    ip_address="192.168.1.100",
    details={"reason": "invalid_password", "attempt": 3}
)
```

## 日志配置

```python
# Python logging 配置
LOGGING = {
    'version': 1,
    'formatters': {
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}'
        }
    },
    'handlers': {
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/app/security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'json'
        }
    },
    'loggers': {
        'security': {
            'handlers': ['security_file'],
            'level': 'INFO'
        }
    }
}
```

## 日志脱敏

```python
def sanitize_log_data(data):
    """脱敏敏感字段"""
    SENSITIVE_FIELDS = ['password', 'token', 'credit_card', 'ssn']
    if isinstance(data, dict):
        return {k: '***' if k in SENSITIVE_FIELDS else sanitize_log_data(v)
                for k, v in data.items()}
    return data
```

## 监控告警示例

```yaml
# 阈值告警规则
alerts:
  - name: login_failure_spike
    condition: "login_failed > 10 in 5m"
    severity: warning

  - name: unusual_access_pattern
    condition: "distinct(ip) > 5 per user in 1h"
    severity: critical
```

## 参考

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [PCI DSS Logging Requirements](https://www.pcisecuritystandards.org/)
