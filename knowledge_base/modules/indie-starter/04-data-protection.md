# 第 4 周：数据保护

## 概述

本周实施数据保护措施，确保敏感数据安全存储。

**预计时间**: 2 小时
**难度**: 中等
**成本**: $0

---

## 数据分类指南

### 数据等级划分

| 等级 | 数据类型 | 示例 | 保护措施 |
|------|---------|------|---------|
| **P0 敏感** | 认证凭据 | 密码、API Key | 哈希、加密、绝不记录日志 |
| **P1 机密** | 个人隐私 | 身份证、手机号 | 加密存储、访问控制 |
| **P2 内部** | 业务数据 | 订单、交易记录 | 访问控制、备份 |
| **P3 公开** | 公开信息 | 商品描述 | 无特殊要求 |

---

## 加密存储方案

### 字段级加密

```python
from cryptography.fernet import Fernet

# 生成密钥（一次性）
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_field(value: str) -> str:
    """加密字段"""
    return cipher.encrypt(value.encode()).decode()

def decrypt_field(encrypted: str) -> str:
    """解密字段"""
    return cipher.decrypt(encrypted.encode()).decode()

# 使用
user.phone_encrypted = encrypt_field(phone_number)
original_phone = decrypt_field(user.phone_encrypted)
```

### 数据库加密配置

**PostgreSQL**:
```sql
-- 启用 pgcrypto 扩展
CREATE EXTENSION pgcrypto;

-- 加密列
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    phone BYTEA,  -- 加密存储
    created_at TIMESTAMP
);

-- 插入加密数据
INSERT INTO users (email, phone)
VALUES (
    'user@example.com',
    pgp_sym_encrypt('13800138000', 'encryption_key')
);

-- 查询解密数据
SELECT email, pgp_sym_decrypt(phone, 'encryption_key') as phone
FROM users;
```

---

## 备份策略配置

### 备份三原则

1. **3 份备份**: 原始数据 + 2 份备份
2. **2 种介质**: 本地 + 云端
3. **1 份异地**: 不同地理位置

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"
S3_BUCKET="s3://my-bucket/backups"

# 数据库备份
pg_dump -U postgres mydb | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# 文件备份
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/uploads

# 上传到云存储
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz $S3_BUCKET/
aws s3 cp $BACKUP_DIR/files_$DATE.tar.gz $S3_BUCKET/

# 本地保留最近 7 天
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

# 发送通知
echo "Backup completed: $DATE" | mail -s "Backup Report" admin@example.com
```

### 加密备份

```bash
# 使用 GPG 加密
gpg --symmetric --cipher-algo AES256 $BACKUP_DIR/db_$DATE.sql.gz

# 解密
gpg --decrypt $BACKUP_DIR/db_$DATE.sql.gz.gpg > $BACKUP_DIR/db_$DATE.sql.gz
```

---

## 数据泄露防护

### 日志脱敏

```python
import re

def mask_email(email: str) -> str:
    """邮箱脱敏: t***@example.com"""
    if '@' not in email:
        return email
    name, domain = email.split('@')
    return f"{name[0]}***@{domain}"

def mask_phone(phone: str) -> str:
    """手机号脱敏: 138****8000"""
    if len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[7:]}"

def mask_id_card(id_card: str) -> str:
    """身份证脱敏: 310***********1234"""
    if len(id_card) != 18:
        return id_card
    return f"{id_card[:3]}***********{id_card[14:]}"

# 日志过滤器
class SensitiveFilter:
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'\s]+)', 'password": "***"'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'\s]+)', 'token": "***"'),
        (r'api_key["\']?\s*[:=]\s*["\']?([^"\'\s]+)', 'api_key": "***"'),
    ]

    @classmethod
    def filter(cls, message: str) -> str:
        for pattern, replacement in cls.SENSITIVE_PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        return message
```

### API 响应脱敏

```python
def user_to_response(user):
    """API 响应脱敏"""
    return {
        'id': user.id,
        'name': user.name,
        'email': mask_email(user.email),
        'phone': mask_phone(user.phone) if user.phone else None,
        # 不返回敏感字段
        # 'password_hash': user.password_hash,  # 绝不返回
        # 'api_key': user.api_key,  # 绝不返回
    }
```

---

## 访问控制

### 基于角色的访问控制 (RBAC)

```python
# 角色定义
ROLES = {
    'admin': ['read', 'write', 'delete', 'admin'],
    'editor': ['read', 'write'],
    'viewer': ['read']
}

def check_permission(user_id: str, action: str) -> bool:
    """检查权限"""
    user = get_user(user_id)
    role = user.role

    if role not in ROLES:
        return False

    return action in ROLES[role]

# 装饰器
def require_permission(action: str):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not check_permission(g.user_id, action):
                return jsonify({'error': 'Permission denied'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# 使用
@app.route('/api/admin/users')
@require_permission('admin')
def list_users():
    return jsonify([user_to_response(u) for u in User.query.all()])
```

---

## 本周实施计划

| 天 | 任务 | 时间 |
|----|------|------|
| Day 1 | 数据分类完成 | 20 分钟 |
| Day 2 | 敏感字段加密实施 | 30 分钟 |
| Day 3 | 备份策略配置 | 30 分钟 |
| Day 4 | 日志脱敏实施 | 20 分钟 |
| Day 5 | 访问控制实施 | 20 分钟 |

---

## 验证清单

- [ ] 数据分类已完成
- [ ] 敏感字段已加密存储
- [ ] 自动备份已配置
- [ ] 备份已测试恢复
- [ ] 日志脱敏已实施
- [ ] API 响应脱敏已实施
- [ ] 访问控制已实施

---

## 下一步

完成本周任务后，继续 [第 5 周：监控告警](./05-monitoring-alerting.md)
