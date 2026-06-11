# 日志敏感信息泄露

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $10-30/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的应用日志中记录了用户密码、API 密钥、身份证号等敏感信息，攻击者获取日志文件后可直接提取这些明文数据，无需任何破解。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 日志中记录了用户登录密码（明文或哈希）
- [ ] 日志中记录了 API 密钥、Token、JWT
- [ ] 日志中记录了用户身份证、手机号、银行卡号
- [ ] 日志文件存储在服务器上，且未设置访问权限
- [ ] 使用 `console.log()` 或 `print()` 输出完整请求体
- [ ] **从未检查过日志内容是否包含敏感信息**
→ 勾选≥2项，尤其是后两项，**立即行动**

### 一句话防御
在日志输出前增加敏感信息脱敏过滤器，使用环境变量存储密钥，设置日志文件访问权限（chmod 600），定期审计日志内容。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查现有日志**：
   ```bash
   # 搜索日志中的敏感信息
   grep -r "password" /var/log/your-app/
   grep -r "token" /var/log/your-app/
   grep -r "apiKey" /var/log/your-app/

   # 检查是否有完整请求体被记录
   grep -r "request body" /var/log/your-app/ | head -20
   ```

2. [ ] **立即清理敏感日志**：
   ```bash
   # 清空包含敏感信息的日志文件
   sudo truncate -s 0 /var/log/your-app/app.log

   # 或使用 sed 删除敏感行
   sudo sed -i '/password/d' /var/log/your-app/app.log
   ```

3. [ ] **设置日志文件权限**：
   ```bash
   sudo chmod 600 /var/log/your-app/*.log
   sudo chown root:root /var/log/your-app/*.log
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **实现日志脱敏中间件**：在应用层过滤敏感字段
2. [ ] **配置日志轮转**：自动删除或归档旧日志
3. [ ] **审查日志输出代码**：移除调试日志
4. [ ] **使用环境变量**：密钥不再硬编码在代码中

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用日志管理服务**：如 LogDNA、Papertrail（支持敏感信息检测）
2. [ ] **实施日志审计**：定期自动扫描日志内容
3. [ ] **启用日志加密**：加密存储日志文件

### 推荐工具
- **免费**：
  - [winston](https://github.com/winstonjs/winston) - Node.js 日志库，支持自定义格式化和脱敏
  - [loguru](https://github.com/Delgan/loguru) - Python 日志库，支持过滤器
  - [logback](https://logback.qos.ch/) - Java 日志框架，支持脱敏配置

- **低成本**：
  - [LogDNA](https://logdna.com/) - 免费 1GB/月，支持敏感信息检测
  - [Papertrail](https://papertrailapp.com/) - 免费 50MB/月，支持搜索告警

### 验证方法
- [ ] **敏感信息检测**：运行 `grep -E "password|token|apiKey|idCard" /var/log/your-app/*.log` 应该无结果
- [ ] **权限验证**：执行 `ls -la /var/log/your-app/`，文件权限应为 `-rw-------`
- [ ] **功能测试**：登录功能正常，日志中不应该出现密码
- [ ] **模拟攻击测试**：尝试从日志中提取敏感信息，应该无法提取

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2021年，一个电商平台的应用日志中记录了所有 HTTP 请求体，包括用户的登录密码、支付密码、身份证号。日志文件存储在 `/var/log/ec-shop/` 目录，权限为 644（所有用户可读）。

攻击者通过文件遍历漏洞获取了日志文件，提取了 10 万用户的明文密码和身份证号。由于许多用户在不同平台使用相同密码，攻击者成功入侵了大量用户的邮箱和社交账号。

**类似案例**：
- 2020年，某金融 App 的日志记录了用户银行卡号和 CVV，日志泄露后导致大规模盗刷
- 2022年，某 SaaS 产品的日志记录了 API 密钥，被用于免费调用付费 API
- 2023年，某社交平台日志记录了用户私信内容，泄露隐私信息

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── 通过文件遍历漏洞读取日志文件
   ├── 或通过服务器权限提升获取日志访问权
   └── 或通过日志管理服务的公开端点访问

2. 获取日志文件
   ├── wget http://target.com/logs/app.log
   ├── 或直接 cat /var/log/target/app.log
   └── 日志大小：500MB，包含数月数据

3. 提取敏感信息
   ├── 使用正则表达式提取密码
   │   grep -oE "password=[^&\s]+" app.log
   ├── 提取 Token 和 API 密钥
   │   grep -oE "Bearer [A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*" app.log
   └── 提取身份证、手机号
       grep -oE "[0-9]{17}[0-9Xx]|[0-9]{11}" app.log

4. 利用敏感信息
   ├── 使用密码尝试登录其他平台（撞库）
   ├── 使用 API 密钥调用付费服务
   └── 出售身份证和手机号数据

5. 持续监控
   └── 定期获取新日志，持续窃取新数据
```

**关键点**：
- 攻击者 **无需破解密码**，直接获取明文
- 日志包含 **历史数据**，影响范围远超实时数据库
- 攻击 **隐蔽性高**：日志泄露往往在很久后才被发现

### 防御实施（低成本方案）

#### 方案A：免费方案（应用层脱敏）

**工具/服务**：日志库 + 自定义过滤器

**配置步骤**：

**第一步：实现敏感信息过滤器（Node.js 示例）**
```javascript
// utils/logger-sanitizer.js
// 日志脱敏工具

class LogSanitizer {
  constructor() {
    // 需要脱敏的字段列表
    this.sensitiveFields = [
      'password',
      'passwd',
      'pwd',
      'token',
      'accessToken',
      'refreshToken',
      'apiKey',
      'apiSecret',
      'secret',
      'privateKey',
      'creditCard',
      'cvv',
      'idCard',
      'ssn'
    ];

    // 正则表达式匹配模式
    this.patterns = {
      // 邮箱：a***@example.com
      email: /([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g,

      // 手机号：138****1234
      phone: /(\d{3})\d{4}(\d{4})/g,

      // 身份证：110***********1234
      idCard: /(\d{3})\d{11}(\d{4})/g,

      // 银行卡：6222****1234
      creditCard: /(\d{4})\d{8,11}(\d{4})/g,

      // JWT Token：只保留前后各 10 个字符
      jwt: /Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*/g,

      // API Key：只保留前 8 个字符
      apiKey: /[a-zA-Z0-9]{32,}/g
    };
  }

  // 脱敏对象
  sanitize(obj) {
    if (typeof obj !== 'object' || obj === null) {
      return this.sanitizeValue(obj);
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.sanitize(item));
    }

    const sanitized = {};
    for (const [key, value] of Object.entries(obj)) {
      if (this.isSensitiveField(key)) {
        sanitized[key] = this.maskValue(value);
      } else if (typeof value === 'object') {
        sanitized[key] = this.sanitize(value);
      } else {
        sanitized[key] = this.sanitizeValue(value);
      }
    }
    return sanitized;
  }

  // 脱敏字符串值
  sanitizeValue(value) {
    if (typeof value !== 'string') {
      return value;
    }

    let sanitized = value;

    // 脱敏邮箱
    sanitized = sanitized.replace(this.patterns.email, (match, local, domain) => {
      const masked = local.substring(0, 1) + '***';
      return `${masked}@${domain}`;
    });

    // 脱敏手机号
    sanitized = sanitized.replace(this.patterns.phone, '$1****$2');

    // 脱敏身份证
    sanitized = sanitized.replace(this.patterns.idCard, '$1***********$2');

    // 脱敏银行卡
    sanitized = sanitized.replace(this.patterns.creditCard, '$1****$2');

    // 脱敏 JWT
    sanitized = sanitized.replace(this.patterns.jwt, (match) => {
      const token = match.replace('Bearer ', '');
      return `Bearer ${token.substring(0, 10)}...${token.substring(token.length - 10)}`;
    });

    // 脱敏 API Key
    sanitized = sanitized.replace(this.patterns.apiKey, (match) => {
      return match.substring(0, 8) + '****';
    });

    return sanitized;
  }

  // 判断是否为敏感字段
  isSensitiveField(fieldName) {
    const lowerField = fieldName.toLowerCase();
    return this.sensitiveFields.some(sensitive =>
      lowerField.includes(sensitive.toLowerCase())
    );
  }

  // 遮罩敏感值
  maskValue(value) {
    if (typeof value !== 'string') {
      return '******';
    }

    if (value.length <= 4) {
      return '****';
    }

    // 显示前 2 和后 2 个字符
    return value.substring(0, 2) + '****' + value.substring(value.length - 2);
  }
}

module.exports = new LogSanitizer();
```

**第二步：集成到日志库（Winston 示例）**
```javascript
// config/logger.js
const winston = require('winston');
const sanitizer = require('../utils/logger-sanitizer');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json(),
    // 自定义格式化器：脱敏敏感信息
    winston.format.printf((info) => {
      // 脱敏整个 info 对象
      const sanitized = sanitizer.sanitize(info);
      return JSON.stringify(sanitized);
    })
  ),
  transports: [
    new winston.transports.File({ filename: '/var/log/app/error.log', level: 'error' }),
    new winston.transports.File({ filename: '/var/log/app/combined.log' })
  ]
});

// 如果是开发环境，输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

module.exports = logger;
```

**第三步：在应用中使用**
```javascript
// 使用示例
const logger = require('./config/logger');

// ❌ 错误示例：直接记录敏感信息
// logger.info('User login', { email: 'user@example.com', password: '123456' });

// ✅ 正确示例：使用脱敏日志
logger.info('User login', {
  email: 'user@example.com',
  password: '123456'  // 自动脱敏为 '12****56'
});

// 记录 HTTP 请求体
app.use((req, res, next) => {
  // 自动脱敏请求体中的敏感字段
  logger.info('HTTP Request', {
    method: req.method,
    path: req.path,
    body: req.body  // 自动脱敏
  });
  next();
});
```

**第四步：配置日志轮转**
```bash
# /etc/logrotate.d/your-app
/var/log/your-app/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
```

**局限性**：
- 需要在每个日志输出点手动集成
- 可能遗漏某些敏感字段
- 性能开销（每次日志输出都需要脱敏处理）

#### 方案B：低成本方案（日志管理服务）

**工具/服务**：LogDNA / Papertrail（支持敏感信息检测和脱敏）

**配置步骤**：

**第一步：注册 LogDNA（免费 1GB/月）**
```bash
# 安装 LogDNA agent
curl -sLO https://repo.logdna.com/logdna.gpg
sudo apt-key add logdna.gpg
echo "deb https://repo.logdna.com stable main" | sudo tee /etc/apt/sources.list.d/logdna.list
sudo apt-get update
sudo apt-get install logdna-agent

# 配置 LogDNA
sudo logdna-agent -k YOUR_INGESTION_KEY

# 添加日志目录
sudo logdna-agent -d /var/log/your-app/

# 启动服务
sudo systemctl start logdna-agent
```

**第二步：配置敏感信息检测规则**
```yaml
# 在 LogDNA 控制台配置
# Settings → Alerts → Create Alert

Alert Name: Sensitive Information Detected
Search Query: password OR token OR apiKey OR idCard OR creditCard
Alert Type: Real-time
Notification: Email / Slack / Webhook
```

**第三步：启用自动脱敏（LogDNA 企业版）**
```yaml
# logdna-config.yaml
scrubbing:
  enabled: true
  rules:
    - pattern: "password"
      replacement: "******"
    - pattern: "token"
      replacement: "[REDACTED]"
    - pattern: "\\d{17}[0-9Xx]"  # 身份证
      replacement: "[ID_CARD_REDACTED]"
    - pattern: "\\d{16,19}"  # 银行卡
      replacement: "[CARD_REDACTED]"
```

**优势**：
- **自动检测**：自动发现日志中的敏感信息
- **实时告警**：发现敏感信息立即通知
- **搜索分析**：强大的日志搜索和分析能力
- **团队协作**：多人可同时查看和分析日志

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (LogDNA) |
|------|------------|----------------|
| 月成本 | $0 | $0-50/月 |
| 存储空间 | 受限于服务器 | 1GB 免费 |
| 敏感信息检测 | 手动配置 | 自动检测 |
| 告警通知 | 无 | 实时告警 |
| 团队协作 | 无 | 支持 |
| 维护成本 | 高 | 低 |

### 决策树

```
你的产品处于什么阶段？
├── MVP/原型阶段
│   ├── 日志量 < 100MB/月 → 方案A（DIY）
│   └── 日志量 > 100MB/月 → 方案B（LogDNA 免费层）
│
├── 已有付费用户
│   ├── 需要合规审计 → 方案B（LogDNA 付费层）
│   └── 仅需基础防护 → 方案A（DIY）
│
└── 团队规模
    ├── 1 人 → 方案A 或 方案B 免费层
    └── 2+ 人 → 方案B（方便团队协作）
```

### 代码示例

#### Python 日志脱敏示例

```python
# utils/logger_sanitizer.py
import re
import logging
from typing import Any, Dict

class SensitiveDataFilter(logging.Filter):
    """日志敏感信息过滤器"""

    def __init__(self):
        super().__init__()
        # 敏感字段列表
        self.sensitive_fields = {
            'password', 'passwd', 'pwd', 'token', 'access_token',
            'api_key', 'secret', 'private_key', 'credit_card',
            'cvv', 'id_card', 'ssn'
        }

        # 正则表达式模式
        self.patterns = [
            # 手机号：138****1234
            (r'(\d{3})\d{4}(\d{4})', r'\1****\2'),
            # 身份证：110***********1234
            (r'(\d{3})\d{11}(\d{4})', r'\1***********\2'),
            # 邮箱：a***@example.com
            (r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', self._mask_email),
            # JWT Token
            (r'Bearer\s+[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.[A-Za-z0-9-_.+/=]*', self._mask_jwt),
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录"""
        # 脱敏日志消息
        record.msg = self._sanitize(str(record.msg))

        # 脱敏参数
        if hasattr(record, 'args') and record.args:
            record.args = self._sanitize_args(record.args)

        return True

    def _sanitize(self, text: str) -> str:
        """脱敏字符串"""
        for pattern, replacement in self.patterns:
            if callable(replacement):
                text = re.sub(pattern, replacement, text)
            else:
                text = re.sub(pattern, replacement, text)
        return text

    def _sanitize_args(self, args: Any) -> Any:
        """脱敏参数"""
        if isinstance(args, dict):
            return self._sanitize_dict(args)
        elif isinstance(args, tuple):
            return tuple(self._sanitize(arg) for arg in args)
        elif isinstance(args, str):
            return self._sanitize(args)
        return args

    def _sanitize_dict(self, data: Dict) -> Dict:
        """脱敏字典"""
        sanitized = {}
        for key, value in data.items():
            if key.lower() in self.sensitive_fields:
                sanitized[key] = self._mask_value(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize(value)
            else:
                sanitized[key] = value
        return sanitized

    def _mask_value(self, value: Any) -> str:
        """遮罩敏感值"""
        if not isinstance(value, str):
            return '******'

        if len(value) <= 4:
            return '****'

        return f'{value[:2]}****{value[-2:]}'

    @staticmethod
    def _mask_email(match: re.Match) -> str:
        """遮罩邮箱"""
        local = match.group(1)
        domain = match.group(2)
        masked = local[0] + '***'
        return f'{masked}@{domain}'

    @staticmethod
    def _mask_jwt(match: re.Match) -> str:
        """遮罩 JWT"""
        token = match.group(0).replace('Bearer ', '')
        return f'Bearer {token[:10]}...{token[-10:]}'


# 使用示例
def setup_logger():
    """配置日志"""
    logger = logging.getLogger('myapp')
    logger.setLevel(logging.INFO)

    # 添加敏感信息过滤器
    logger.addFilter(SensitiveDataFilter())

    # 文件处理器
    file_handler = logging.FileHandler('/var/log/myapp/app.log')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(file_handler)

    return logger


# 使用日志
logger = setup_logger()

# ✅ 日志会自动脱敏
logger.info('User login', extra={
    'email': 'user@example.com',
    'password': '123456'  # 自动脱敏为 '12****56'
})
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业日志安全最佳实践](../../enterprise/infosec/log-security-enterprise.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 合规要求 | 基础保护 | PCI-DSS/GDPR/HIPAA |
| 日志保留 | 7 天 | 1-7 年（可审计） |
| 敏感信息检测 | 正则匹配 | NLP + 机器学习 |
| 访问控制 | 文件权限 | RBAC + 审计日志 |
| 日志存储 | 本地文件 | SIEM 集中管理 |
| 实时监控 | 无 | SIEM 实时告警 |

---

## 附录：常见问题

**Q: 日志脱敏会影响性能吗？**

A: 影响很小：
- 正则匹配开销：每条日志增加 < 1ms
- 可以在异步任务中进行脱敏
- 对于高并发场景，可以采样记录日志（如只记录 10% 的请求）

**Q: 如果必须记录敏感信息怎么办？**

A: 如果业务必须记录（如审计需求），请：
1. 加密存储日志文件
2. 限制访问权限（仅管理员可访问）
3. 设置审计日志（记录谁访问了日志）
4. 定期清理不再需要的敏感日志

**Q: 如何发现已有的日志中是否包含敏感信息？**

A: 定期审计日志：
```bash
# 搜索常见敏感信息
grep -rE "password|token|apiKey|idCard|creditCard" /var/log/your-app/

# 使用工具自动检测
# 安装 gitleaks
brew install gitleaks

# 扫描日志文件
gitleaks --path=/var/log/your-app/ --no-git
```

**Q: 测试环境日志需要脱敏吗？**

A: 需要，原因：
1. 测试环境可能使用真实数据
2. 开发人员不应看到用户密码
3. 测试环境安全意识可能更低，更容易泄露

---

## 参考资源

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [NIST Guide to Computer Security Log Management](https://csrc.nist.gov/publications/detail/sp/800-92/final)
- [Winston Logging Library](https://github.com/winstonjs/winston)
- [Python Logging Best Practices](https://docs.python.org/3/howto/logging.html)
