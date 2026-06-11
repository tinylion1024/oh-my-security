# 日志安全配置

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测/响应
- **实现成本**: 免费
- **实施时间**: 1-2小时
- **维护成本**: 0.5小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
安全记录应用日志，避免敏感信息泄露，建立日志审计机制。适用于所有需要记录日志的独立开发者项目，特别是处理用户敏感数据的应用。

---

## 核心原则

### 日志安全层次架构

```
日志安全多层防御
┌─────────────────────────────────────────────────────┐
│                    输入层过滤                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │敏感信息  │  │结构验证  │  │级别控制  │         │
│  │脱敏      │  │          │  │          │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    输出层控制                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │访问控制  │  │格式标准化│  │审计追踪  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    存储层保护                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │日志轮转  │  │完整性校验│  │备份加密  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

### 日志安全策略矩阵

| 日志类型 | 敏感信息 | 访问级别 | 保留周期 | 审计要求 |
|---------|---------|---------|---------|---------|
| 访问日志 | 脱敏 | 团队 | 90天 | 是 |
| 错误日志 | 脱敏 | 开发 | 30天 | 是 |
| 调试日志 | 完全脱敏 | 仅开发 | 7天 | 否 |
| 审计日志 | 加密存储 | 管理员 | 365天 | 是 |
| 性能日志 | 无敏感 | 团队 | 30天 | 否 |

---

## 快速上手（5分钟）

### Python 安全日志配置

```python
# requirements.txt
# python-json-logger>=2.0.0

import logging
import sys
import os
from datetime import datetime
from typing import Any, Dict
from pythonjsonlogger import jsonlogger
import re


class SensitiveDataFilter(logging.Filter):
    """敏感数据脱敏过滤器"""
    
    SENSITIVE_PATTERNS = [
        # 密码类
        (r'(password|passwd|pwd)["\']?\s*[:=]\s*["\']?[^\s"\']+', 
         r'\g<0>[:value]******'),
        # API 密钥
        (r'(api[_-]?key|token|secret)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9_-]{16,}',
         r'\g<0>[:value]******'),
        # 邮箱
        (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
         lambda m: f'{m.group(0)[0]}***@{m.group(0).split("@")[1]}'),
        # 手机号
        (r'1[3-9]\d{9}',
         lambda m: f'{m.group(0)[:3]}****{m.group(0)[-4:]}'),
        # 身份证
        (r'[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]',
         lambda m: f'{m.group(0)[:3]}***********{m.group(0)[-4:]}'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """过滤并脱敏日志记录"""
        if record.msg:
            record.msg = self._mask_text(str(record.msg))
        
        if record.args:
            if isinstance(record.args, dict):
                record.args = self._mask_dict(record.args)
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    self._mask_text(arg) if isinstance(arg, str)
                    else self._mask_dict(arg) if isinstance(arg, dict)
                    else arg
                    for arg in record.args
                )
        
        return True
    
    def _mask_text(self, text: str) -> str:
        """脱敏文本"""
        result = text
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            if callable(replacement):
                result = re.sub(pattern, replacement, result)
            else:
                result = re.sub(pattern, replacement, result)
        return result
    
    def _mask_dict(self, data: dict) -> dict:
        """脱敏字典"""
        sensitive_keys = [
            'password', 'passwd', 'pwd', 'secret', 'token',
            'api_key', 'apikey', 'private_key', 'access_token'
        ]
        
        result = {}
        for key, value in data.items():
            key_lower = key.lower()
            if any(s in key_lower for s in sensitive_keys):
                result[key] = '******'
            elif isinstance(value, str):
                result[key] = self._mask_text(value)
            elif isinstance(value, dict):
                result[key] = self._mask_dict(value)
            else:
                result[key] = value
        
        return result


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """自定义 JSON 格式化器"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """添加自定义字段"""
        super().add_fields(log_record, record, message_dict)
        
        # 添加时间戳
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # 添加环境信息
        log_record['env'] = os.getenv('ENV', 'development')
        
        # 添加服务信息
        log_record['service'] = os.getenv('SERVICE_NAME', 'app')
        
        # 添加主机信息
        import socket
        log_record['hostname'] = socket.gethostname()
        
        # 添加请求 ID（如果有）
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        # 添加用户 ID（如果有）
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id


def setup_secure_logging(
    log_level: str = 'INFO',
    log_file: str = None,
    enable_json: bool = True
) -> logging.Logger:
    """
    配置安全日志
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径
        enable_json: 是否使用 JSON 格式
    
    Returns:
        配置好的日志器
    """
    # 创建根日志器
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    logger.handlers = []
    
    # 添加脱敏过滤器
    logger.addFilter(SensitiveDataFilter())
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    
    if enable_json:
        # JSON 格式
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            rename_fields={'levelname': 'level', 'name': 'logger'}
        )
    else:
        # 文本格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定）
    if log_file:
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# 使用示例
if __name__ == '__main__':
    logger = setup_secure_logging(log_level='DEBUG', enable_json=True)
    
    # 测试敏感信息脱敏
    logger.info("用户登录: email=zhangsan@example.com, password=secret123")
    logger.info(f"API 调用: api_key=sk_live_1234567890")
    logger.info(f"用户数据: phone=13812345678, id_card=110101199001011234")
    
    # 测试字典脱敏
    logger.info("用户信息", extra={
        'user': {
            'name': '张三',
            'password': 'secret123',
            'api_key': 'sk_live_xxxxx'
        }
    })
```

---

## 详细方案

### 方案架构

```
┌────────────────────────────────────────────────────────┐
│                    日志安全流程                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  应用代码              日志框架            输出        │
│  ┌──────────┐        ┌──────────┐       ┌──────────┐  │
│  │ logger   │───────▶│ 脱敏过滤 │──────▶│ 控制台   │  │
│  │.info()   │        │ 格式化   │       └──────────┘  │
│  └──────────┘        └──────────┘       ┌──────────┐  │
│                           │            │ 文件     │  │
│                           ▼            └──────────┘  │
│                    ┌──────────┐       ┌──────────┐  │
│                    │ 级别控制 │──────▶│ 远程收集 │  │
│                    │ 审计日志 │       └──────────┘  │
│                    └──────────┘                      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 实现步骤

#### 步骤1：日志级别最佳实践

```python
import logging
from enum import Enum
from typing import Callable, Any
import functools


class LogLevel(Enum):
    """日志级别定义"""
    DEBUG = 'DEBUG'      # 开发调试信息
    INFO = 'INFO'        # 一般信息
    WARNING = 'WARNING'  # 警告信息
    ERROR = 'ERROR'      # 错误信息
    CRITICAL = 'CRITICAL'  # 严重错误


class SecureLogger:
    """安全日志器"""
    
    # 不同环境的日志级别配置
    ENV_LEVELS = {
        'development': LogLevel.DEBUG,
        'staging': LogLevel.INFO,
        'production': LogLevel.WARNING,
    }
    
    # 敏感操作审计日志
    AUDIT_OPERATIONS = [
        'user_login',
        'user_logout',
        'password_change',
        'data_export',
        'permission_change',
        'config_change',
    ]
    
    def __init__(self, name: str, env: str = None):
        self.logger = logging.getLogger(name)
        self.env = env or os.getenv('ENV', 'development')
        self._setup_level()
    
    def _setup_level(self):
        """根据环境设置日志级别"""
        level = self.ENV_LEVELS.get(self.env, LogLevel.INFO)
        self.logger.setLevel(level.value)
    
    def _should_audit(self, operation: str) -> bool:
        """判断是否需要审计"""
        return operation in self.AUDIT_OPERATIONS
    
    def audit(
        self, 
        operation: str, 
        user_id: str = None,
        details: dict = None,
        success: bool = True
    ):
        """
        记录审计日志
        
        Args:
            operation: 操作名称
            user_id: 用户 ID
            details: 操作详情
            success: 是否成功
        """
        if not self._should_audit(operation):
            return
        
        audit_record = {
            'audit': True,
            'operation': operation,
            'user_id': user_id,
            'success': success,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        
        self.logger.info(f"AUDIT: {operation}", extra=audit_record)
    
    def log_performance(
        self, 
        operation: str, 
        duration_ms: float,
        metadata: dict = None
    ):
        """
        记录性能日志
        
        Args:
            operation: 操作名称
            duration_ms: 耗时（毫秒）
            metadata: 元数据
        """
        perf_record = {
            'performance': True,
            'operation': operation,
            'duration_ms': duration_ms,
            **(metadata or {})
        }
        
        # 慢操作告警
        if duration_ms > 1000:
            self.logger.warning(f"SLOW: {operation} took {duration_ms:.2f}ms", extra=perf_record)
        else:
            self.logger.debug(f"PERF: {operation} took {duration_ms:.2f}ms", extra=perf_record)


def log_performance(operation: str):
    """
    性能日志装饰器
    
    Args:
        operation: 操作名称
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            logger = SecureLogger(func.__module__)
            
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start) * 1000
                logger.log_performance(operation, duration, {'status': 'success'})
                return result
            except Exception as e:
                duration = (time.time() - start) * 1000
                logger.log_performance(operation, duration, {'status': 'error', 'error': str(e)})
                raise
        return wrapper
    return decorator


# 使用示例
logger = SecureLogger('myapp')

# 审计日志
logger.audit('user_login', user_id='user123', details={'ip': '192.168.1.1'})

# 性能日志
@log_performance('database_query')
def query_database():
    import time
    time.sleep(0.1)
    return {'data': 'result'}

query_database()
```

#### 步骤2：日志审计方案

```python
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import hashlib


class AuditLogManager:
    """审计日志管理器"""
    
    def __init__(self, log_dir: str = 'logs/audit'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def write_audit_log(
        self,
        operation: str,
        user_id: str,
        details: dict,
        success: bool = True,
        ip_address: str = None
    ):
        """
        写入审计日志
        
        Args:
            operation: 操作名称
            user_id: 用户 ID
            details: 操作详情
            success: 是否成功
            ip_address: IP 地址
        """
        timestamp = datetime.utcnow()
        
        audit_record = {
            'timestamp': timestamp.isoformat(),
            'operation': operation,
            'user_id': user_id,
            'success': success,
            'ip_address': ip_address,
            'details': details
        }
        
        # 计算日志哈希（用于完整性校验）
        log_str = json.dumps(audit_record, sort_keys=True)
        audit_record['hash'] = hashlib.sha256(log_str.encode()).hexdigest()
        
        # 写入日志文件
        log_file = self.log_dir / f"audit-{timestamp.strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(audit_record, ensure_ascii=False) + '\n')
    
    def query_audit_logs(
        self,
        user_id: str = None,
        operation: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        success: bool = None
    ) -> List[Dict]:
        """
        查询审计日志
        
        Args:
            user_id: 用户 ID 过滤
            operation: 操作过滤
            start_time: 开始时间
            end_time: 结束时间
            success: 成功状态过滤
        
        Returns:
            匹配的审计日志列表
        """
        results = []
        
        # 确定查询的日志文件
        if start_time and end_time:
            date_range = [
                start_time + timedelta(days=i)
                for i in range((end_time - start_time).days + 1)
            ]
        else:
            # 默认查询最近 7 天
            date_range = [
                datetime.utcnow() - timedelta(days=i)
                for i in range(7)
            ]
        
        for date in date_range:
            log_file = self.log_dir / f"audit-{date.strftime('%Y-%m-%d')}.jsonl"
            if not log_file.exists():
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        
                        # 应用过滤条件
                        if user_id and record.get('user_id') != user_id:
                            continue
                        if operation and record.get('operation') != operation:
                            continue
                        if success is not None and record.get('success') != success:
                            continue
                        if start_time:
                            record_time = datetime.fromisoformat(record['timestamp'])
                            if record_time < start_time:
                                continue
                        if end_time:
                            record_time = datetime.fromisoformat(record['timestamp'])
                            if record_time > end_time:
                                continue
                        
                        results.append(record)
                    except json.JSONDecodeError:
                        continue
        
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def verify_integrity(self, date: datetime = None) -> Dict:
        """
        验证日志完整性
        
        Args:
            date: 要验证的日期，默认今天
        
        Returns:
            验证结果
        """
        date = date or datetime.utcnow()
        log_file = self.log_dir / f"audit-{date.strftime('%Y-%m-%d')}.jsonl"
        
        if not log_file.exists():
            return {'valid': False, 'reason': '日志文件不存在'}
        
        corrupted = []
        total = 0
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                total += 1
                try:
                    record = json.loads(line)
                    stored_hash = record.pop('hash', None)
                    
                    # 重新计算哈希
                    log_str = json.dumps(record, sort_keys=True)
                    computed_hash = hashlib.sha256(log_str.encode()).hexdigest()
                    
                    if stored_hash != computed_hash:
                        corrupted.append(i)
                except json.JSONDecodeError:
                    corrupted.append(i)
        
        return {
            'valid': len(corrupted) == 0,
            'total': total,
            'corrupted': corrupted,
            'corruption_rate': len(corrupted) / total if total > 0 else 0
        }


# 使用示例
audit_manager = AuditLogManager()

# 写入审计日志
audit_manager.write_audit_log(
    operation='user_login',
    user_id='user123',
    details={'method': 'password', 'mfa': True},
    success=True,
    ip_address='192.168.1.1'
)

# 查询审计日志
logs = audit_manager.query_audit_logs(
    user_id='user123',
    operation='user_login',
    start_time=datetime.utcnow() - timedelta(days=1)
)

# 验证完整性
integrity = audit_manager.verify_integrity()
print(f"日志完整性: {integrity}")
```

#### 步骤3：日志轮转和归档

```python
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


class LogRotator:
    """日志轮转管理器"""
    
    def __init__(
        self,
        log_dir: str = 'logs',
        max_size_mb: int = 10,
        max_files: int = 5,
        compress_after_days: int = 7,
        delete_after_days: int = 30
    ):
        """
        初始化日志轮转器
        
        Args:
            log_dir: 日志目录
            max_size_mb: 单个日志文件最大大小（MB）
            max_files: 保留的日志文件数量
            compress_after_days: 多少天后压缩
            delete_after_days: 多少天后删除
        """
        self.log_dir = Path(log_dir)
        self.max_size = max_size_mb * 1024 * 1024
        self.max_files = max_files
        self.compress_after_days = compress_after_days
        self.delete_after_days = delete_after_days
    
    def rotate_if_needed(self, log_file: Path):
        """
        如果需要则轮转日志
        
        Args:
            log_file: 日志文件路径
        """
        if not log_file.exists():
            return
        
        # 检查文件大小
        if log_file.stat().st_size >= self.max_size:
            self._rotate(log_file)
    
    def _rotate(self, log_file: Path):
        """执行轮转"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        rotated_name = f"{log_file.stem}.{timestamp}{log_file.suffix}"
        rotated_path = log_file.parent / rotated_name
        
        # 移动当前文件
        shutil.move(str(log_file), str(rotated_path))
        
        # 清理旧文件
        self._cleanup(log_file)
    
    def _cleanup(self, log_file: Path):
        """清理旧日志文件"""
        # 获取所有相关日志文件
        pattern = f"{log_file.stem}.*{log_file.suffix}*"
        log_files = sorted(
            self.log_dir.glob(pattern),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # 删除超出数量的文件
        for old_file in log_files[self.max_files:]:
            old_file.unlink()
    
    def compress_old_logs(self):
        """压缩旧日志"""
        now = datetime.now()
        
        for log_file in self.log_dir.glob('*.log'):
            if log_file.suffix == '.gz':
                continue
            
            # 检查文件年龄
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            age_days = (now - mtime).days
            
            if age_days >= self.compress_after_days:
                # 压缩文件
                compressed_path = log_file.with_suffix('.log.gz')
                with open(log_file, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原文件
                log_file.unlink()
    
    def delete_old_logs(self):
        """删除过期日志"""
        now = datetime.now()
        
        for log_file in self.log_dir.glob('*.log*'):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            age_days = (now - mtime).days
            
            if age_days >= self.delete_after_days:
                log_file.unlink()
    
    def get_log_stats(self) -> List[Dict]:
        """获取日志统计信息"""
        stats = []
        
        for log_file in self.log_dir.glob('*.log*'):
            stat = log_file.stat()
            stats.append({
                'name': log_file.name,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'compressed': log_file.suffix == '.gz'
            })
        
        return sorted(stats, key=lambda x: x['modified'], reverse=True)


# 使用示例
rotator = LogRotator(
    log_dir='logs',
    max_size_mb=10,
    max_files=5,
    compress_after_days=7,
    delete_after_days=30
)

# 检查并轮转
rotator.rotate_if_needed(Path('logs/app.log'))

# 压缩旧日志
rotator.compress_old_logs()

# 删除过期日志
rotator.delete_old_logs()

# 获取统计
stats = rotator.get_log_stats()
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `log_level` | INFO | 日志级别 |
| `log_format` | JSON | 日志格式 |
| `max_file_size_mb` | 10 | 单文件最大大小 |
| `max_files` | 5 | 保留文件数量 |
| `compress_after_days` | 7 | 压缩周期 |
| `delete_after_days` | 30 | 删除周期 |
| `enable_audit` | True | 启用审计日志 |

---

## 成本估算

| 指标 | 本地方案 | 云服务方案 |
|------|---------|-----------|
| 月成本 | $0 | $5-50/月 |
| 存储成本 | 磁盘空间 | $0.1/GB |
| 性能影响 | < 1% | < 5% |
| 实施时间 | 1-2小时 | 2-4小时 |

---

## 迁出成本

- **迁出难度**：低
- **迁出步骤**：
  1. 导出日志文件
  2. 转换格式（如需要）
  3. 导入新系统
- **数据格式**：JSON Lines 格式，易于迁移

---

## 与其他武器配合

- **前置**：
  - [data-masking.md](./data-masking.md) - 日志脱敏
  - [secret-management.md](../free-tier/secret-management.md) - 密钥不记录

- **后置**：
  - [backup-service.md](../saas/backup-service.md) - 日志备份

- **配合**：
  - 与监控系统配合，日志告警
  - 与 SIEM 系统配合，安全分析

---

## 常见问题

**Q: 日志应该保留多久？**  
A: 根据类型不同：
- 访问日志：90天
- 错误日志：30天
- 审计日志：365天（合规要求）
- 调试日志：7天

**Q: JSON vs 文本格式？**  
A: 推荐 JSON：
- 结构化，易于解析
- 支持复杂字段
- 便于日志聚合系统处理

**Q: 如何处理大量日志？**  
A: 三种方案：
- 日志轮转 + 压缩
- 日志聚合系统（如 Loki，免费）
- 云日志服务（如 CloudWatch，按量付费）

**Q: 审计日志需要加密吗？**  
A: 建议：
- 包含敏感信息：加密
- 仅操作记录：不加密
- 合规要求：遵循合规标准

---

## 推荐实现

### 开源方案

- **Python**: `logging` + `python-json-logger`
- **Node.js**: `pino` 或 `winston`
- **Go**: `logrus` 或 `zap`
- **日志聚合**: Grafana Loki（免费）

### 云服务方案（可选）

- **AWS CloudWatch Logs** - $0.50/GB
- **Google Cloud Logging** - $0.50/GB
- **Datadog Logs** - $0.10/GB
- **Logtail** - 免费层 + $5/月

---

## 最佳实践清单

- [ ] 所有日志已配置脱敏过滤器
- [ ] 生产环境日志级别 >= INFO
- [ ] 敏感操作有审计日志
- [ ] 日志有轮转和归档机制
- [ ] 日志格式标准化（JSON）
- [ ] 有日志完整性校验机制
- [ ] 日志文件权限正确（600/640）
- [ ] 有日志监控和告警

---

## 验证清单

- [ ] 敏感信息已脱敏
- [ ] 日志格式正确
- [ ] 日志轮转正常工作
- [ ] 审计日志记录完整
- [ ] 日志完整性验证通过
- [ ] 日志文件权限正确
