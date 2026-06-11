# 数据脱敏工具

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 1-2小时
- **维护成本**: 0.5小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
在日志、API响应、调试输出中自动脱敏敏感数据，防止邮箱、手机号、身份证等敏感信息泄露。适用于需要记录日志但又不能暴露用户隐私的场景。

---

## 核心原则

### 脱敏层次架构

```
数据脱敏多层防御
┌─────────────────────────────────────────────────────┐
│                    应用层脱敏                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │日志框架  │  │响应过滤器│  │序列化器  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    中间件层脱敏                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │API网关   │  │日志收集器│  │AOP切面   │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    存储层脱敏                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │数据库视图│  │数据导出  │  │备份文件  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

### 脱敏策略矩阵

| 数据类型 | 脱敏方式 | 示例 |
|---------|---------|------|
| 邮箱 | 保留首字符和域名 | `z***@example.com` |
| 手机号 | 保留前3后4 | `138****1234` |
| 身份证 | 保留前3后4 | `110***********1234` |
| 银行卡 | 保留后4位 | `**** **** **** 1234` |
| 姓名 | 保留姓氏 | `张**` |
| 地址 | 仅保留省市 | `北京市朝阳区***` |
| 密码 | 完全隐藏 | `******` |

---

## 快速上手（5分钟）

### Python 最小示例

```python
import re
from typing import Any, Dict, List, Union

class DataMasker:
    """数据脱敏工具类"""
    
    # 正则表达式库
    PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone_cn': r'1[3-9]\d{9}',
        'id_card_cn': r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
        'bank_card': r'(?:\d{4}[ -]?){3}\d{4}',
        'password': r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?[^\s"\']{6,}',
        'api_key': r'(?:api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}',
    }
    
    @staticmethod
    def mask_email(email: str) -> str:
        """邮箱脱敏：z***@example.com"""
        if not email or '@' not in email:
            return email
        username, domain = email.split('@', 1)
        if len(username) <= 1:
            return f'*@{domain}'
        return f'{username[0]}***@{domain}'
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """手机号脱敏：138****1234"""
        if not phone or len(phone) < 7:
            return phone
        return f'{phone[:3]}****{phone[-4:]}'
    
    @staticmethod
    def mask_id_card(id_card: str) -> str:
        """身份证脱敏：110***********1234"""
        if not id_card or len(id_card) < 7:
            return id_card
        return f'{id_card[:3]}{"*" * (len(id_card) - 7)}{id_card[-4:]}'
    
    @staticmethod
    def mask_bank_card(card: str) -> str:
        """银行卡脱敏：**** **** **** 1234"""
        if not card:
            return card
        digits = re.sub(r'[^\d]', '', card)
        if len(digits) < 4:
            return card
        return f'**** **** **** {digits[-4:]}'
    
    @staticmethod
    def mask_name(name: str) -> str:
        """姓名脱敏：张**"""
        if not name:
            return name
        return f'{name[0]}{"*" * (len(name) - 1)}'
    
    @staticmethod
    def mask_password(password: str) -> str:
        """密码脱敏：完全隐藏"""
        return '******'
    
    def mask_text(self, text: str, patterns: List[str] = None) -> str:
        """
        自动识别并脱敏文本中的敏感信息
        
        Args:
            text: 待脱敏文本
            patterns: 要脱敏的模式列表，默认全部
        
        Returns:
            脱敏后的文本
        """
        if not text:
            return text
        
        patterns = patterns or list(self.PATTERNS.keys())
        result = text
        
        for pattern_name in patterns:
            if pattern_name not in self.PATTERNS:
                continue
            
            pattern = self.PATTERNS[pattern_name]
            
            def replacer(match):
                matched_text = match.group(0)
                if pattern_name == 'email':
                    return self.mask_email(matched_text)
                elif pattern_name == 'phone_cn':
                    return self.mask_phone(matched_text)
                elif pattern_name == 'id_card_cn':
                    return self.mask_id_card(matched_text)
                elif pattern_name == 'bank_card':
                    return self.mask_bank_card(matched_text)
                elif pattern_name in ('password', 'api_key'):
                    # 替换值为 ******
                    return re.sub(r'([:=]\s*["\']?)[^\s"\']+', r'\g<1>******', matched_text)
                return matched_text
            
            result = re.sub(pattern, replacer, result)
        
        return result
    
    def mask_dict(
        self, 
        data: Dict[str, Any], 
        sensitive_keys: List[str] = None
    ) -> Dict[str, Any]:
        """
        脱敏字典中的敏感字段
        
        Args:
            data: 待脱敏字典
            sensitive_keys: 敏感字段名列表
        
        Returns:
            脱敏后的字典
        """
        default_sensitive = [
            'password', 'passwd', 'pwd',
            'api_key', 'apikey', 'api-key',
            'token', 'secret', 'secret_key',
            'access_token', 'refresh_token',
            'private_key', 'privatekey',
            'credit_card', 'card_number',
        ]
        sensitive_keys = sensitive_keys or default_sensitive
        
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            
            # 检查是否为敏感字段
            is_sensitive = any(s in key_lower for s in sensitive_keys)
            
            if is_sensitive:
                result[key] = '******'
            elif isinstance(value, str):
                result[key] = self.mask_text(value)
            elif isinstance(value, dict):
                result[key] = self.mask_dict(value, sensitive_keys)
            elif isinstance(value, list):
                result[key] = [
                    self.mask_dict(item, sensitive_keys) if isinstance(item, dict)
                    else self.mask_text(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result


# 快速使用示例
if __name__ == '__main__':
    masker = DataMasker()
    
    # 文本脱敏
    text = "用户张三的手机号是13812345678，邮箱是zhangsan@example.com"
    print(masker.mask_text(text))
    # 输出: 用户张三的手机号是138****5678，邮箱是z***@example.com
    
    # 字典脱敏
    data = {
        "username": "zhangsan",
        "password": "MySecret123",
        "email": "zhangsan@example.com",
        "phone": "13812345678",
        "api_key": "sk-1234567890abcdef"
    }
    print(masker.mask_dict(data))
    # 输出: {'username': 'zhangsan', 'password': '******', 'email': 'z***@example.com', 'phone': '138****5678', 'api_key': '******'}
```

---

## 详细方案

### 方案架构

```
┌────────────────────────────────────────────────────────┐
│                    日志脱敏系统                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐        │
│  │ 应用代码 │───▶│ 日志框架 │───▶│ 脱敏过滤器│        │
│  └──────────┘    └──────────┘    └──────────┘        │
│                                         │              │
│                                         ▼              │
│                                  ┌──────────┐         │
│                                  │ 日志输出 │         │
│                                  └──────────┘         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 实现步骤

#### 步骤1：日志框架集成

**Python logging 集成**

```python
import logging
import json
from typing import Any

class SensitiveDataFilter(logging.Filter):
    """日志脱敏过滤器"""
    
    def __init__(self, masker: DataMasker = None):
        super().__init__()
        self.masker = masker or DataMasker()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤并脱敏日志记录"""
        # 脱敏消息
        if record.msg:
            record.msg = self.masker.mask_text(str(record.msg))
        
        # 脱敏参数
        if record.args:
            if isinstance(record.args, dict):
                record.args = self.masker.mask_dict(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self.masker.mask_text(arg) if isinstance(arg, str)
                    else self.masker.mask_dict(arg) if isinstance(arg, dict)
                    else arg
                    for arg in record.args
                )
        
        return True


# 配置日志
def setup_secure_logging():
    """配置安全日志"""
    
    # 创建脱敏过滤器
    mask_filter = SensitiveDataFilter()
    
    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 添加过滤器
    logger.addFilter(mask_filter)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(console_handler)
    
    return logger


# 使用示例
logger = setup_secure_logging()
logger.info("用户登录: email=zhangsan@example.com, password=secret123")
# 输出: 用户登录: email=z***@example.com, password=******
```

**JavaScript/Node.js 集成**

```javascript
// masker.js
class DataMasker {
  static maskEmail(email) {
    if (!email || !email.includes('@')) return email;
    const [username, domain] = email.split('@');
    if (username.length <= 1) return `*@${domain}`;
    return `${username[0]}***@${domain}`;
  }

  static maskPhone(phone) {
    if (!phone || phone.length < 7) return phone;
    return `${phone.slice(0, 3)}****${phone.slice(-4)}`;
  }

  static maskIdCard(idCard) {
    if (!idCard || idCard.length < 7) return idCard;
    return `${idCard.slice(0, 3)}${'*'.repeat(idCard.length - 7)}${idCard.slice(-4)}`;
  }

  static maskPassword() {
    return '******';
  }

  static maskObject(obj, sensitiveKeys = [
    'password', 'passwd', 'pwd',
    'api_key', 'apikey', 'token',
    'secret', 'private_key'
  ]) {
    const result = {};
    
    for (const [key, value] of Object.entries(obj)) {
      const keyLower = key.toLowerCase();
      const isSensitive = sensitiveKeys.some(s => keyLower.includes(s));
      
      if (isSensitive) {
        result[key] = '******';
      } else if (typeof value === 'string') {
        result[key] = this.maskText(value);
      } else if (typeof value === 'object' && value !== null) {
        result[key] = this.maskObject(value, sensitiveKeys);
      } else {
        result[key] = value;
      }
    }
    
    return result;
  }

  static maskText(text) {
    if (!text) return text;
    
    // 邮箱
    text = text.replace(
      /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
      match => this.maskEmail(match)
    );
    
    // 手机号
    text = text.replace(
      /1[3-9]\d{9}/g,
      match => this.maskPhone(match)
    );
    
    // 身份证
    text = text.replace(
      /[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]/g,
      match => this.maskIdCard(match)
    );
    
    return text;
  }
}

// Pino 日志集成
const pino = require('pino');

const masker = DataMasker;

const logger = pino({
  level: 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  hooks: {
    logMethod(inputArgs, method) {
      // 脱敏参数
      const maskedArgs = inputArgs.map(arg => {
        if (typeof arg === 'string') {
          return masker.maskText(arg);
        }
        if (typeof arg === 'object' && arg !== null) {
          return masker.maskObject(arg);
        }
        return arg;
      });
      return method.apply(this, maskedArgs);
    }
  }
});

module.exports = { DataMasker, logger };
```

#### 步骤2：API 响应脱敏

```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json

class ResponseMaskingMiddleware(BaseHTTPMiddleware):
    """API 响应脱敏中间件"""
    
    def __init__(self, app, masker: DataMasker = None):
        super().__init__(app)
        self.masker = masker or DataMasker()
    
    async def dispatch(self, request: Request, call_next):
        # 执行请求
        response = await call_next(request)
        
        # 只处理 JSON 响应
        if response.headers.get('content-type', '').startswith('application/json'):
            # 读取响应体
            body = b''
            async for chunk in response.body_iterator:
                body += chunk
            
            try:
                # 解析 JSON
                data = json.loads(body)
                
                # 脱敏
                masked_data = self.masker.mask_dict(data)
                
                # 返回新响应
                return JSONResponse(
                    content=masked_data,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except Exception:
                # 解析失败，返回原始响应
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        
        return response


# FastAPI 集成
app = FastAPI()
app.add_middleware(ResponseMaskingMiddleware)

@app.get("/user/{user_id}")
async def get_user(user_id: int):
    return {
        "id": user_id,
        "username": "zhangsan",
        "email": "zhangsan@example.com",
        "phone": "13812345678",
        "api_key": "sk-1234567890"
    }
```

#### 步骤3：正则表达式库扩展

```python
class SensitivePatterns:
    """敏感数据正则表达式库"""
    
    # 中国大陆
    PHONE_CN = r'1[3-9]\d{9}'
    ID_CARD_CN = r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]'
    BANK_CARD_CN = r'(?:\d{4}[ -]?){3}\d{4}'
    
    # 国际
    PHONE_INTERNATIONAL = r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'
    
    # 通用
    EMAIL = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    IP_V4 = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    IP_V6 = r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
    
    # 密钥类
    API_KEY = r'(?:api[_-]?key|apikey|token|secret)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}'
    JWT = r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'
    AWS_KEY = r'AKIA[0-9A-Z]{16}'
    GITHUB_TOKEN = r'ghp_[a-zA-Z0-9]{36}'
    STRIPE_KEY = r'sk_live_[0-9a-zA-Z]{24}'
    
    # 数据库连接
    DB_CONNECTION = r'(?:mysql|postgres|mongodb|redis)://[^\s]+'
    
    # 支付信息
    CREDIT_CARD = r'(?:\d{4}[ -]?){3}\d{4}'
    CVV = r'\b\d{3,4}\b'
    
    @classmethod
    def all_patterns(cls) -> dict:
        """返回所有模式"""
        return {
            'phone_cn': cls.PHONE_CN,
            'id_card_cn': cls.ID_CARD_CN,
            'bank_card_cn': cls.BANK_CARD_CN,
            'email': cls.EMAIL,
            'ip_v4': cls.IP_V4,
            'api_key': cls.API_KEY,
            'jwt': cls.JWT,
            'aws_key': cls.AWS_KEY,
        }
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `mask_email` | True | 是否脱敏邮箱 |
| `mask_phone` | True | 是否脱敏手机号 |
| `mask_id_card` | True | 是否脱敏身份证 |
| `mask_password` | True | 是否脱敏密码 |
| `mask_api_key` | True | 是否脱敏API密钥 |
| `sensitive_keys` | 见代码 | 敏感字段名列表 |
| `custom_patterns` | {} | 自定义正则模式 |

---

## 成本估算

| 指标 | 免费方案 | 备注 |
|------|---------|------|
| 月成本 | $0 | 完全免费 |
| 性能影响 | < 5% | 文本处理开销 |
| 实施时间 | 1-2小时 | 包括测试 |
| 维护成本 | 0.5小时/月 | 定期更新规则 |

---

## 迁出成本

- **迁出难度**：低
- **迁出步骤**：
  1. 移除日志过滤器
  2. 移除中间件
  3. 代码变更量小，主要是配置删除
- **数据兼容性**：无影响，脱敏是运行时行为，不影响存储数据

---

## 与其他武器配合

- **前置**：
  - [secret-management.md](../free-tier/secret-management.md) - 确保密钥不被硬编码
  - [input-validation.md](../free-tier/input-validation.md) - 输入验证防止恶意输入

- **后置**：
  - [log-security.md](./log-security.md) - 日志安全配置
  - [encryption-at-rest.md](../free-tier/encryption-at-rest.md) - 存储加密

- **配合**：
  - 与日志审计系统配合，记录脱敏操作
  - 与监控系统配合，检测敏感信息泄露告警

---

## 常见问题

**Q: 脱敏会影响调试吗？**  
A: 可以通过配置开关，在开发环境禁用脱敏，生产环境启用。建议使用不同的日志级别或环境变量控制。

**Q: 正则表达式性能如何？**  
A: 对于单次请求，性能影响 < 5ms。如果有大量文本需要脱敏，建议：
- 使用预编译正则
- 只在关键字段启用脱敏
- 使用缓存减少重复处理

**Q: 如何处理嵌套的JSON？**  
A: 使用递归遍历处理嵌套结构，示例代码已包含递归处理逻辑。

**Q: 脱敏后还能还原吗？**  
A: 不能。脱敏是单向操作，无法还原原始数据。这是安全设计的核心原则。

---

## 推荐实现

### 开源方案

- **Python**: 本文档提供的 `DataMasker` 类
- **Java**: [Logback](https://logback.qos.ch/) + 自定义脱敏转换器
- **Node.js**: [pino](https://github.com/pinojs/pino) + 自定义脱敏钩子
- **Go**: [logrus](https://github.com/sirupsen/logrus) + 自定义钩子

### 商业方案（可选）

- **AWS CloudWatch Logs** - 数据保护策略（$0.50/GB）
- **Datadog Sensitive Data Scanner** - 自动敏感数据检测（$0.10/GB）

---

## 最佳实践清单

- [ ] 所有日志框架已配置脱敏过滤器
- [ ] API 响应已配置脱敏中间件
- [ ] 敏感字段列表已完整定义
- [ ] 开发环境可查看原始数据（使用环境变量控制）
- [ ] 生产环境强制启用脱敏
- [ ] 定期审查脱敏规则（至少每季度）
- [ ] 有敏感信息泄露的监控告警
- [ ] 脱敏功能已纳入代码审查清单

---

## 验证清单

- [ ] 邮箱脱敏测试通过
- [ ] 手机号脱敏测试通过
- [ ] 身份证脱敏测试通过
- [ ] 密码脱敏测试通过
- [ ] API Key 脱敏测试通过
- [ ] 嵌套 JSON 脱敏测试通过
- [ ] 日志输出不包含敏感信息
- [ ] API 响应不包含敏感信息
