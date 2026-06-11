# AI 输出清洗

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 响应
- **实现成本**: 免费
- **实施时间**: 1-2小时
- **维护成本**: 2-3小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
清洗 AI 输出内容，防止泄露敏感信息（PII、API 密钥、内部路径等），过滤有害内容和敏感词。

## 快速上手（5分钟）

```python
# output_sanitizer.py - 最小可运行示例
import re
from typing import Tuple, List

class SimpleOutputSanitizer:
    """5分钟版输出清洗器"""

    # PII 检测模式
    PII_PATTERNS = {
        "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        "phone": r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}",
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "api_key": r"(?i)(api[_-]?key|apikey|token|secret)['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{20,}",
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "private_key": r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----",
    }

    # 敏感路径模式
    PATH_PATTERNS = [
        r"/home/[a-zA-Z0-9_-]+",
        r"/Users/[a-zA-Z0-9_-]+",
        r"C:\\Users\\[a-zA-Z0-9_-]+",
        r"/var/log/[a-zA-Z0-9_\-/]+",
    ]

    def sanitize(self, text: str) -> Tuple[str, List[dict]]:
        """
        清洗输出内容
        返回: (清洗后的文本, 检测到的敏感信息列表)
        """
        detected = []
        sanitized = text

        # 1. PII 检测和替换
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, sanitized)
            if matches:
                detected.append({
                    "type": pii_type,
                    "count": len(matches),
                    "samples": matches[:2]  # 只保留前2个样本
                })
                # 替换为占位符
                sanitized = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", sanitized)

        # 2. 敏感路径替换
        for pattern in self.PATH_PATTERNS:
            sanitized = re.sub(pattern, "[PATH_REDACTED]", sanitized)

        # 3. IP 地址替换 (可选)
        ip_pattern = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        if re.search(ip_pattern, sanitized):
            sanitized = re.sub(ip_pattern, "[IP_REDACTED]", sanitized)

        return sanitized, detected

# 使用示例
if __name__ == "__main__":
    sanitizer = SimpleOutputSanitizer()

    test_outputs = [
        "联系邮箱: user@example.com",
        "API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz",
        "用户电话: 555-123-4567",
        "文件路径: /home/john/.ssh/id_rsa",
        "正常内容: 这是一段正常的文本",
    ]

    for output in test_outputs:
        clean, detected = sanitizer.sanitize(output)
        status = "🔍 检测" if detected else "✅ 安全"
        print(f"{status}: {output}")
        print(f"  → {clean}")
        if detected:
            print(f"  检测到: {detected}")
        print()
```

## 详细方案

### 方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI 原始输出                               │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: PII 检测                                          │
│  - 正则模式匹配                                             │
│  - 命名实体识别 (NER)                                       │
│  - 自定义敏感词库                                           │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 敏感信息检测                                      │
│  - API 密钥检测                                             │
│  - 内部路径检测                                             │
│  - 数据库连接字符串                                         │
│  - 私钥/证书检测                                            │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 内容审核 (可选)                                   │
│  - 有害内容检测                                             │
│  - 仇恨言论检测                                             │
│  - 成人内容过滤                                             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: 替换 & 日志                                        │
│  - 占位符替换                                               │
│  - 审计日志记录                                             │
│  - 告警通知                                                 │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  清洗后输出                                  │
└─────────────────────────────────────────────────────────────┘
```

### 实现步骤

#### 步骤1: PII 检测实现 (30分钟)

```python
# pii_detector.py
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class PIIType(Enum):
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    PASSWORD = "password"
    NAME = "name"
    ADDRESS = "address"
    DATE = "date"

@dataclass
class PIIMatch:
    """PII 匹配结果"""
    type: PIIType
    value: str
    start: int
    end: int
    confidence: float
    context: str  # 匹配周围的文本

class PIIDetector:
    """PII 检测器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> Dict[PIIType, List[re.Pattern]]:
        """加载检测模式"""
        patterns = {
            PIIType.EMAIL: [
                re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
            ],
            PIIType.PHONE: [
                re.compile(r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}"),  # US
                re.compile(r"\+?86[-.\s]?1[3-9]\d{9}"),  # China mobile
            ],
            PIIType.SSN: [
                re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
            ],
            PIIType.CREDIT_CARD: [
                re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),  # 通用格式
                re.compile(r"\b(?:3[47]\d{2}[\s\-]?\d{6}[\s\-]?\d{5})\b"),  # Amex
            ],
            PIIType.IP_ADDRESS: [
                re.compile(r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b")
            ],
            PIIType.API_KEY: [
                re.compile(r"(?i)(?:api[_-]?key|apikey|secret|token|auth)\s*[:=]\s*['\"]?[a-zA-Z0-9_\-]{20,}['\"]?"),
                re.compile(r"sk-[a-zA-Z0-9]{48}"),  # OpenAI
                re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS
                re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub
            ],
            PIIType.PASSWORD: [
                re.compile(r"(?i)(?:password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s]{8,}['\"]?"),
            ],
            PIIType.DATE: [
                re.compile(r"\b\d{4}[-/]\d{2}[-/]\d{2}\b"),  # YYYY-MM-DD
                re.compile(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b"),  # MM-DD-YYYY
            ],
        }
        return patterns

    def detect(self, text: str) -> List[PIIMatch]:
        """检测 PII"""
        matches = []

        for pii_type, patterns in self.patterns.items():
            for pattern in patterns:
                for match in pattern.finditer(text):
                    # 获取上下文
                    context_start = max(0, match.start() - 20)
                    context_end = min(len(text), match.end() + 20)
                    context = text[context_start:context_end]

                    matches.append(PIIMatch(
                        type=pii_type,
                        value=match.group(),
                        start=match.start(),
                        end=match.end(),
                        confidence=0.9,  # 正则匹配通常高置信度
                        context=context
                    ))

        # 按位置排序
        matches.sort(key=lambda x: x.start)

        return matches

    def detect_with_ner(self, text: str) -> List[PIIMatch]:
        """使用 NER 检测 (需要额外依赖)"""
        try:
            import spacy

            # 加载模型
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(text)

            matches = []

            # 映射 spaCy 实体类型到我们的类型
            entity_mapping = {
                "PERSON": PIIType.NAME,
                "ORG": None,  # 组织通常不是 PII
                "GPE": None,  # 地点通常不是 PII
                "DATE": PIIType.DATE,
            }

            for ent in doc.ents:
                if ent.label_ in entity_mapping and entity_mapping[ent.label_]:
                    matches.append(PIIMatch(
                        type=entity_mapping[ent.label_],
                        value=ent.text,
                        start=ent.start_char,
                        end=ent.end_char,
                        confidence=0.7,  # NER 置信度略低
                        context=text[max(0, ent.start_char - 20):min(len(text), ent.end_char + 20)]
                    ))

            return matches

        except ImportError:
            # spaCy 未安装，回退到纯正则
            return self.detect(text)

# 使用示例
if __name__ == "__main__":
    detector = PIIDetector()

    test_text = """
    用户信息：
    姓名: John Smith
    邮箱: john.smith@example.com
    电话: 555-123-4567
    SSN: 123-45-6789
    API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890
    IP: 192.168.1.1
    """

    matches = detector.detect(test_text)

    print("检测到的 PII:")
    for match in matches:
        print(f"  {match.type.value}: {match.value[:20]}... (置信度: {match.confidence})")
```

#### 步骤2: 敏感词过滤 (30分钟)

```python
# sensitive_filter.py
import re
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
import json

@dataclass
class FilterRule:
    """过滤规则"""
    pattern: str
    category: str
    action: str  # "redact", "block", "warn"
    replacement: str = "[REDACTED]"

class SensitiveFilter:
    """敏感词过滤器"""

    def __init__(self, custom_words: Optional[Dict[str, List[str]]] = None):
        # 默认敏感词库
        self.word_lists = {
            "profanity": [],  # 需要填充实际词库
            "internal": [],   # 内部术语
            "competitors": [], # 竞争对手
        }

        # 合并自定义词库
        if custom_words:
            self.word_lists.update(custom_words)

        # 编译正则
        self.compiled_rules: List[FilterRule] = []
        self._compile_rules()

        # 白名单
        self.whitelist: Set[str] = set()

    def _compile_rules(self):
        """编译过滤规则"""
        # 内部路径
        self.compiled_rules.extend([
            FilterRule(
                pattern=r"/home/[a-zA-Z0-9_-]+(/[a-zA-Z0-9_-]+)*",
                category="internal_path",
                action="redact",
                replacement="[INTERNAL_PATH]"
            ),
            FilterRule(
                pattern=r"/Users/[a-zA-Z0-9_-]+(/[a-zA-Z0-9_-]+)*",
                category="internal_path",
                action="redact",
                replacement="[INTERNAL_PATH]"
            ),
            FilterRule(
                pattern=r"C:\\Users\\[a-zA-Z0-9_-]+(?:\\[a-zA-Z0-9_-]+)*",
                category="internal_path",
                action="redact",
                replacement="[INTERNAL_PATH]"
            ),
        ])

        # 数据库连接字符串
        self.compiled_rules.extend([
            FilterRule(
                pattern=r"(?i)(?:mysql|postgres|mongodb)://[^\s]+",
                category="connection_string",
                action="redact",
                replacement="[DATABASE_URL_REDACTED]"
            ),
        ])

        # 内部域名
        self.compiled_rules.extend([
            FilterRule(
                pattern=r"(?i)[a-zA-Z0-9-]+\.(?:internal|local|corp|lan)(?:\.[a-zA-Z]{2,})?",
                category="internal_domain",
                action="redact",
                replacement="[INTERNAL_DOMAIN]"
            ),
        ])

    def add_word_list(self, category: str, words: List[str]):
        """添加自定义词库"""
        self.word_lists[category] = words

    def add_to_whitelist(self, word: str):
        """添加到白名单"""
        self.whitelist.add(word.lower())

    def filter(self, text: str) -> tuple[str, List[dict]]:
        """
        过滤敏感内容
        返回: (过滤后的文本, 检测结果列表)
        """
        filtered = text
        detections = []

        # 1. 正则规则过滤
        for rule in self.compiled_rules:
            matches = list(re.finditer(rule.pattern, filtered))
            if matches:
                detections.append({
                    "category": rule.category,
                    "action": rule.action,
                    "count": len(matches),
                    "samples": [m.group()[:50] for m in matches[:3]]
                })
                filtered = re.sub(rule.pattern, rule.replacement, filtered)

        # 2. 词库过滤
        for category, words in self.word_lists.items():
            for word in words:
                if word.lower() in self.whitelist:
                    continue

                # 不区分大小写查找
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                matches = list(pattern.finditer(filtered))
                if matches:
                    detections.append({
                        "category": category,
                        "action": "redact",
                        "word": word,
                        "count": len(matches)
                    })
                    filtered = pattern.sub("[REDACTED]", filtered)

        return filtered, detections

    def load_from_file(self, filepath: str):
        """从文件加载词库"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for category, words in data.items():
                self.word_lists[category] = words

# 使用示例
if __name__ == "__main__":
    filter = SensitiveFilter()

    # 添加自定义词库
    filter.add_word_list("internal", [
        "ProjectX",  # 内部项目代号
        "SecretSauce",  # 内部技术名称
    ])

    test_outputs = [
        "文件位于 /home/john/projects/secret",
        "数据库连接: mysql://user:pass@internal.corp.company.com/db",
        "正在开发 ProjectX 项目",
        "正常内容，没有敏感信息",
    ]

    for output in test_outputs:
        clean, detected = filter.filter(output)
        status = "🔍" if detected else "✅"
        print(f"{status} 原文: {output}")
        print(f"   清洗: {clean}")
        if detected:
            print(f"   检测: {detected}")
        print()
```

#### 步骤3: 完整集成示例 (1小时)

```python
# integrated_sanitizer.py
from pii_detector import PIIDetector, PIIMatch, PIIType
from sensitive_filter import SensitiveFilter
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class SanitizationResult:
    """清洗结果"""
    original: str
    sanitized: str
    pii_detected: List[PIIMatch]
    sensitive_detected: List[dict]
    is_safe: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "original": self.original[:100] + "..." if len(self.original) > 100 else self.original,
            "sanitized": self.sanitized,
            "pii_count": len(self.pii_detected),
            "sensitive_count": len(self.sensitive_detected),
            "is_safe": self.is_safe,
            "timestamp": self.timestamp
        }

class IntegratedOutputSanitizer:
    """集成版输出清洗器"""

    def __init__(
        self,
        enable_ner: bool = False,
        custom_word_lists: Optional[Dict[str, List[str]]] = None,
        enable_logging: bool = True
    ):
        self.pii_detector = PIIDetector()
        self.sensitive_filter = SensitiveFilter(custom_word_lists)
        self.enable_ner = enable_ner
        self.enable_logging = enable_logging

        # 审计日志
        self.audit_log: List[SanitizationResult] = []

        # 配置
        self.config = {
            "block_on_pii": False,  # 检测到 PII 是否阻止输出
            "block_on_sensitive": False,  # 检测到敏感词是否阻止输出
            "redact_all": True,  # 是否全部替换
            "log_retention_days": 30,
        }

    def sanitize(self, text: str) -> SanitizationResult:
        """
        主清洗方法
        """
        # 1. PII 检测
        pii_matches = self.pii_detector.detect(text)

        # 2. 敏感内容检测
        sensitive_filtered, sensitive_detected = self.sensitive_filter.filter(text)

        # 3. 构建结果
        sanitized = sensitive_filtered

        # 4. 判断是否安全
        is_safe = len(pii_matches) == 0 and len(sensitive_detected) == 0

        result = SanitizationResult(
            original=text,
            sanitized=sanitized,
            pii_detected=pii_matches,
            sensitive_detected=sensitive_detected,
            is_safe=is_safe
        )

        # 5. 记录审计日志
        if self.enable_logging:
            self.audit_log.append(result)

        return result

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """获取审计日志"""
        return [r.to_dict() for r in self.audit_log[-limit:]]

    def export_audit_log(self, filepath: str):
        """导出审计日志"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self.audit_log], f, indent=2, ensure_ascii=False)

    def clear_old_logs(self, days: int = 30):
        """清理旧日志"""
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=days)
        self.audit_log = [
            r for r in self.audit_log
            if datetime.fromisoformat(r.timestamp) > cutoff
        ]

# 完整使用示例
async def ai_call_with_sanitization():
    """带输出清洗的 AI 调用示例"""
    sanitizer = IntegratedOutputSanitizer(enable_logging=True)

    # 模拟 AI 输出
    ai_outputs = [
        "用户 john@example.com 的订单已处理",
        "API 密钥 sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890 已创建",
        "文件保存到 /home/john/.ssh/id_rsa",
        "这是一条正常的 AI 回复",
    ]

    for output in ai_outputs:
        result = sanitizer.sanitize(output)

        print(f"原始: {output[:50]}...")
        print(f"清洗: {result.sanitized[:50]}...")
        print(f"安全: {'✅' if result.is_safe else '❌'}")
        print(f"PII: {len(result.pii_detected)} | 敏感: {len(result.sensitive_detected)}")
        print("-" * 60)

    # 查看审计日志
    print("\n审计日志:")
    print(json.dumps(sanitizer.get_audit_log(3), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import asyncio
    asyncio.run(ai_call_with_sanitization())
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| enable_ner | False | 是否启用命名实体识别 |
| block_on_pii | False | 检测到 PII 是否阻止输出 |
| block_on_sensitive | False | 检测到敏感词是否阻止输出 |
| redact_all | True | 是否全部替换敏感内容 |
| log_retention_days | 30 | 日志保留天数 |

### 输出清洗示例

| 场景 | 原始输出 | 清洗后 | 检测类型 |
|-----|---------|--------|---------|
| 用户邮箱 | "user@example.com" | "[EMAIL_REDACTED]" | PII |
| API 密钥 | "sk-1234..." | "[API_KEY_REDACTED]" | 敏感信息 |
| 内部路径 | "/home/john/file" | "[INTERNAL_PATH]" | 敏感路径 |
| 电话号码 | "555-123-4567" | "[PHONE_REDACTED]" | PII |
| 正常内容 | "Hello world" | "Hello world" | 无 |

## 成本估算

| 指标 | 免费方案 | 付费方案 |
|------|---------|----------|
| 月成本 | $0 | $20-50 (托管 NER) |
| 性能 | 5000+ req/s (规则) | 100 req/s (API) |
| 准确率 | 85% (规则) | 95% (NER) |
| 延迟 | < 1ms (规则) | 50-100ms (NER) |

### 免费方案
- 纯规则检测: $0
- spaCy NER (离线): $0
- 自托管小模型: GPU 成本

### 付费方案
- Google DLP API: $1/1000 次
- AWS Comprehend: $0.0001/单位
- Azure Content Safety: 免费层 + 按量付费

## 迁出成本

- **迁出难度**: 低
- **迁出步骤**:
  1. 导出敏感词库 (JSON)
  2. 导出正则规则配置
  3. 迁移审计日志
  4. 更新 API 调用接口

## 与其他武器配合

- **前置**:
  - [Prompt 过滤](../open-source/prompt-filter.md) - 先过滤输入，减少输出风险
  - [AI 成本控制](../free-tier/ai-cost-control.md) - 控制清洗 API 成本
- **后置**: 无
- **替代**: [AI 安全服务](../saas/ai-security-service.md) - 托管清洗服务

## 常见问题

**Q: 如何处理误报？**

A: 使用白名单：
```python
sanitizer.sensitive_filter.add_to_whitelist("example.com")
sanitizer.sensitive_filter.add_to_whitelist("localhost")
```

**Q: 检测延迟会影响用户体验吗？**

A: 规则检测很快 (<1ms)，NER 会增加延迟 (10-50ms)。建议：
- 同步使用规则检测
- 异步使用 NER 进行二次验证

**Q: 如何处理多语言？**

A:
```python
# 不同语言使用不同模式
class MultilingualSanitizer:
    def __init__(self):
        self.patterns = {
            "en": {...},
            "zh": {
                "phone": r"1[3-9]\d{9}",  # 中国手机号
                "id_card": r"\d{17}[\dXx]",  # 身份证号
            }
        }
```

**Q: 如何平衡安全性和可用性？**

A:
```python
# 分级处理
if len(pii_matches) > 3:  # 大量 PII
    return "[OUTPUT_BLOCKED: Too much PII]"
elif pii_matches:  # 少量 PII
    return sanitized  # 替换后返回
else:
    return original  # 原文返回
```

## 推荐实现

### 免费
- **自建方案**: 本模板代码 - $0
- **spaCy NER**: https://spacy.io - 开源免费
- **presidio**: https://github.com/microsoft/presidio - 微软开源 PII 检测

### 低成本
- **Google DLP**: https://cloud.google.com/dlp - 免费层
- **AWS Comprehend**: https://aws.amazon.com/comprehend - 免费层

### 企业级
- **Microsoft Presidio**: 开源自托管
- **AWS Macie**: https://aws.amazon.com/macie - 数据发现和保护
- **Azure Content Safety**: https://azure.microsoft.com/products/cognitive-services/content-safety

## 审计与合规

```python
# compliance.py
class ComplianceReporter:
    """合规报告生成器"""

    def __init__(self, sanitizer: IntegratedOutputSanitizer):
        self.sanitizer = sanitizer

    def generate_report(self, start_date: str, end_date: str) -> Dict:
        """生成合规报告"""
        # 筛选时间范围
        logs = [
            log for log in self.sanitizer.audit_log
            if start_date <= log.timestamp <= end_date
        ]

        return {
            "period": f"{start_date} to {end_date}",
            "total_outputs": len(logs),
            "safe_outputs": sum(1 for log in logs if log.is_safe),
            "pii_detected": sum(len(log.pii_detected) for log in logs),
            "sensitive_detected": sum(len(log.sensitive_detected) for log in logs),
            "pii_types": self._count_pii_types(logs),
            "recommendations": self._generate_recommendations(logs)
        }

    def _count_pii_types(self, logs) -> Dict:
        """统计 PII 类型"""
        counts = {}
        for log in logs:
            for match in log.pii_detected:
                pii_type = match.type.value
                counts[pii_type] = counts.get(pii_type, 0) + 1
        return counts

    def _generate_recommendations(self, logs) -> List[str]:
        """生成建议"""
        recommendations = []

        pii_count = sum(len(log.pii_detected) for log in logs)
        if pii_count > 100:
            recommendations.append("检测到大量 PII 泄露，建议审查 AI 模型训练数据")

        return recommendations
```

## 性能优化

```python
# performance.py
import re
from functools import lru_cache

class CachedSanitizer:
    """带缓存的清洗器"""

    def __init__(self, sanitizer):
        self.sanitizer = sanitizer
        self._cache = {}
        self._max_cache = 10000

    @lru_cache(maxsize=1000)
    def sanitize(self, text: str):
        """缓存相同文本的清洗结果"""
        return self.sanitizer.sanitize(text)

    def batch_sanitize(self, texts: List[str]) -> List[str]:
        """批量处理"""
        return [self.sanitize(text) for text in texts]
```

## 维护建议

1. **每周**: 检查审计日志，调整误报规则
2. **每月**: 更新敏感词库，添加新的 PII 类型
3. **每季度**: 评估检测准确率，优化规则
4. **持续**: 关注新型隐私泄露方式
