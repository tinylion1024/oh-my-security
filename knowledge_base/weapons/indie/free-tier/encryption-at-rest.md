# 静态数据加密

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 2-4小时
- **维护成本**: 1小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
对数据库中的敏感字段进行加密存储，如用户密码、支付信息、身份证号等。防止数据库泄露导致敏感信息直接暴露。适用于所有存储用户敏感信息的独立开发者项目。

---

## 核心原则

### 加密层次架构

```
数据加密多层防御
┌─────────────────────────────────────────────────────┐
│                    应用层加密                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │字段加密  │  │传输加密  │  │内存保护  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    数据库层加密                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │透明加密  │  │列级加密  │  │备份加密  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    存储层加密                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │磁盘加密  │  │对象存储  │  │文件系统  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

### 加密策略矩阵

| 数据类型 | 加密方式 | 存储格式 | 示例 |
|---------|---------|---------|------|
| 密码 | bcrypt/argon2 | 哈希 | `$2b$12$...` |
| 身份证 | AES-256-GCM | Base64 | `enc:v1:aes256:...` |
| 银行卡 | AES-256-GCM | Base64 | `enc:v1:aes256:...` |
| 地址 | AES-256-CBC | Base64 | `enc:v1:aes256:...` |
| 备注信息 | AES-256-GCM | Base64 | `enc:v1:aes256:...` |

---

## 快速上手（5分钟）

### Python AES 加密实现

```python
# requirements.txt
# cryptography>=41.0.0

import os
import base64
import json
from datetime import datetime
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


class AES256Encryptor:
    """AES-256-GCM 加密器"""
    
    VERSION = 'v1'
    ALGORITHM = 'aes256'
    NONCE_SIZE = 12  # GCM 推荐 12 字节
    KEY_SIZE = 32    # AES-256 需要 32 字节密钥
    SALT_SIZE = 16
    
    def __init__(self, master_key: str):
        """
        初始化加密器
        
        Args:
            master_key: 主密钥（建议 >= 32 字符）
        """
        self.master_key = master_key.encode()
        self._derived_keys: dict = {}
    
    def _derive_key(self, salt: bytes, context: str = '') -> bytes:
        """
        从主密钥派生加密密钥
        
        Args:
            salt: 盐值
            context: 上下文信息（用于密钥分离）
        
        Returns:
            派生密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt + context.encode(),
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(self.master_key)
    
    def encrypt(self, plaintext: str, context: str = '') -> str:
        """
        加密字符串
        
        Args:
            plaintext: 明文
            context: 加密上下文（如字段名），用于密钥分离
        
        Returns:
            加密字符串（格式：enc:v1:aes256:base64(salt+nonce+ciphertext)）
        """
        if not plaintext:
            return plaintext
        
        # 生成随机盐和 nonce
        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)
        
        # 派生密钥
        key = self._derive_key(salt, context)
        
        # 加密
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        
        # 组合：salt + nonce + ciphertext
        combined = salt + nonce + ciphertext
        
        # 编码
        encoded = base64.b64encode(combined).decode()
        
        return f'enc:{self.VERSION}:{self.ALGORITHM}:{encoded}'
    
    def decrypt(self, encrypted: str, context: str = '') -> str:
        """
        解密字符串
        
        Args:
            encrypted: 加密字符串
            context: 加密上下文（必须与加密时一致）
        
        Returns:
            明文
        """
        if not encrypted or not encrypted.startswith('enc:'):
            return encrypted
        
        # 解析格式
        parts = encrypted.split(':')
        if len(parts) != 4 or parts[0] != 'enc':
            raise ValueError(f"无效的加密格式: {encrypted[:20]}...")
        
        version, algorithm = parts[1], parts[2]
        if version != self.VERSION or algorithm != self.ALGORITHM:
            raise ValueError(f"不支持的加密版本或算法: {version}/{algorithm}")
        
        # 解码
        combined = base64.b64decode(parts[3])
        
        # 分离
        salt = combined[:self.SALT_SIZE]
        nonce = combined[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
        ciphertext = combined[self.SALT_SIZE + self.NONCE_SIZE:]
        
        # 派生密钥
        key = self._derive_key(salt, context)
        
        # 解密
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        return plaintext.decode()
    
    def encrypt_dict(
        self, 
        data: dict, 
        fields: list, 
        context_prefix: str = ''
    ) -> dict:
        """
        加密字典中的指定字段
        
        Args:
            data: 原始数据
            fields: 需要加密的字段列表
            context_prefix: 上下文前缀
        
        Returns:
            加密后的数据
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                context = f"{context_prefix}.{field}" if context_prefix else field
                result[field] = self.encrypt(str(result[field]), context)
        return result
    
    def decrypt_dict(
        self, 
        data: dict, 
        fields: list, 
        context_prefix: str = ''
    ) -> dict:
        """
        解密字典中的指定字段
        
        Args:
            data: 加密数据
            fields: 需要解密的字段列表
            context_prefix: 上下文前缀
        
        Returns:
            解密后的数据
        """
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                context = f"{context_prefix}.{field}" if context_prefix else field
                try:
                    result[field] = self.decrypt(result[field], context)
                except Exception:
                    pass  # 解密失败，保留原值
        return result


# 使用示例
if __name__ == '__main__':
    # 从环境变量获取主密钥
    master_key = os.getenv('ENCRYPTION_KEY', 'your-secret-key-at-least-32-chars')
    
    encryptor = AES256Encryptor(master_key)
    
    # 加密单个字段
    id_card = "110101199001011234"
    encrypted = encryptor.encrypt(id_card, context='user.id_card')
    print(f"加密后: {encrypted}")
    
    # 解密
    decrypted = encryptor.decrypt(encrypted, context='user.id_card')
    print(f"解密后: {decrypted}")
    
    # 加密字典
    user = {
        'name': '张三',
        'id_card': '110101199001011234',
        'phone': '13812345678',
        'bank_card': '6222021234567890123'
    }
    
    encrypted_user = encryptor.encrypt_dict(
        user, 
        fields=['id_card', 'bank_card'],
        context_prefix='user'
    )
    print(f"加密后用户: {encrypted_user}")
```

---

## 详细方案

### 方案架构

```
┌────────────────────────────────────────────────────────┐
│                    加密数据流                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  用户输入              应用处理            数据库存储   │
│  ┌──────────┐        ┌──────────┐       ┌──────────┐  │
│  │ 明文数据 │───────▶│ 加密模块 │──────▶│ 密文存储 │  │
│  │身份证号  │        │ AES-256  │       │ enc:...  │  │
│  └──────────┘        └──────────┘       └──────────┘  │
│                           │                            │
│                           ▼                            │
│                    ┌──────────┐                       │
│                    │ 密钥管理 │                       │
│                    │ KMS/Env  │                       │
│                    └──────────┘                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 实现步骤

#### 步骤1：数据库集成

**SQLAlchemy 模型集成**

```python
# models.py
from sqlalchemy import Column, Integer, String, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from .encryption import AES256Encryptor
import os
import json

Base = declarative_base()

class EncryptedString(TypeDecorator):
    """
    SQLAlchemy 加密字符串类型
    
    使用方法：
        class User(Base):
            id_card = Column(EncryptedString(100))
    """
    
    impl = String
    cache_ok = True
    
    def __init__(self, length=None, context='', **kwargs):
        self.length = length
        self.context = context
        self._encryptor = None
        super().__init__(**kwargs)
    
    @property
    def encryptor(self):
        if self._encryptor is None:
            master_key = os.getenv('ENCRYPTION_KEY')
            if not master_key:
                raise ValueError("缺少 ENCRYPTION_KEY 环境变量")
            self._encryptor = AES256Encryptor(master_key)
        return self._encryptor
    
    def process_bind_param(self, value, dialect):
        """存储前加密"""
        if value is None:
            return None
        return self.encryptor.encrypt(value, self.context)
    
    def process_result_value(self, value, dialect):
        """读取后解密"""
        if value is None:
            return None
        return self.encryptor.decrypt(value, self.context)


class EncryptedJSON(TypeDecorator):
    """
    SQLAlchemy 加密 JSON 类型
    
    使用方法：
        class User(Base):
            metadata = Column(EncryptedJSON(context='user.metadata'))
    """
    
    impl = String
    cache_ok = True
    
    def __init__(self, context='', **kwargs):
        self.context = context
        self._encryptor = None
        super().__init__(**kwargs)
    
    @property
    def encryptor(self):
        if self._encryptor is None:
            master_key = os.getenv('ENCRYPTION_KEY')
            if not master_key:
                raise ValueError("缺少 ENCRYPTION_KEY 环境变量")
            self._encryptor = AES256Encryptor(master_key)
        return self._encryptor
    
    def process_bind_param(self, value, dialect):
        """存储前加密"""
        if value is None:
            return None
        json_str = json.dumps(value, ensure_ascii=False)
        return self.encryptor.encrypt(json_str, self.context)
    
    def process_result_value(self, value, dialect):
        """读取后解密"""
        if value is None:
            return None
        json_str = self.encryptor.decrypt(value, self.context)
        return json.loads(json_str)


# 使用示例
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    
    # 加密字段
    id_card = Column(EncryptedString(200, context='user.id_card'))
    bank_card = Column(EncryptedString(200, context='user.bank_card'))
    
    # 加密 JSON
    sensitive_metadata = Column(EncryptedJSON(context='user.metadata'))
```

#### 步骤2：PostgreSQL pgcrypto 使用

```sql
-- 启用 pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 创建加密函数
CREATE OR REPLACE FUNCTION encrypt_field(
    plaintext TEXT,
    key TEXT
) RETURNS TEXT AS $$
BEGIN
    RETURN encode(
        pgp_sym_encrypt(plaintext, key, 'cipher-algo=aes256'),
        'base64'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建解密函数
CREATE OR REPLACE FUNCTION decrypt_field(
    ciphertext TEXT,
    key TEXT
) RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(
        decode(ciphertext, 'base64'),
        key
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建加密列
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    id_card_encrypted TEXT,
    bank_card_encrypted TEXT
);

-- 插入加密数据
INSERT INTO users (username, id_card_encrypted, bank_card_encrypted)
VALUES (
    'zhangsan',
    encrypt_field('110101199001011234', current_setting('app.encryption_key')),
    encrypt_field('6222021234567890123', current_setting('app.encryption_key'))
);

-- 查询解密数据
SELECT 
    id,
    username,
    decrypt_field(id_card_encrypted, current_setting('app.encryption_key')) as id_card,
    decrypt_field(bank_card_encrypted, current_setting('app.encryption_key')) as bank_card
FROM users;

-- 创建视图（自动解密）
CREATE VIEW users_decrypted AS
SELECT 
    id,
    username,
    decrypt_field(id_card_encrypted, current_setting('app.encryption_key')) as id_card,
    decrypt_field(bank_card_encrypted, current_setting('app.encryption_key')) as bank_card
FROM users;

-- 设置会话级加密密钥
SET app.encryption_key = 'your-encryption-key-at-least-32-chars';
```

**Python PostgreSQL 集成**

```python
# requirements.txt
# psycopg2-binary>=2.9.0
# sqlalchemy>=2.0.0

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

class PostgresEncryptedDB:
    """PostgreSQL 加密数据库操作"""
    
    def __init__(self, database_url: str, encryption_key: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)
        self.encryption_key = encryption_key
    
    def set_session_key(self, session):
        """设置会话加密密钥"""
        session.execute(
            text(f"SET app.encryption_key = '{self.encryption_key}'")
        )
    
    def insert_user(self, username: str, id_card: str, bank_card: str):
        """插入用户（自动加密）"""
        session = self.Session()
        try:
            self.set_session_key(session)
            session.execute(text("""
                INSERT INTO users (username, id_card_encrypted, bank_card_encrypted)
                VALUES (:username, encrypt_field(:id_card, current_setting('app.encryption_key')),
                        encrypt_field(:bank_card, current_setting('app.encryption_key')))
            """), {
                'username': username,
                'id_card': id_card,
                'bank_card': bank_card
            })
            session.commit()
        finally:
            session.close()
    
    def get_user(self, username: str):
        """查询用户（自动解密）"""
        session = self.Session()
        try:
            self.set_session_key(session)
            result = session.execute(text("""
                SELECT id, username,
                       decrypt_field(id_card_encrypted, current_setting('app.encryption_key')) as id_card,
                       decrypt_field(bank_card_encrypted, current_setting('app.encryption_key')) as bank_card
                FROM users WHERE username = :username
            """), {'username': username})
            row = result.fetchone()
            return dict(row._mapping) if row else None
        finally:
            session.close()


# 使用示例
db = PostgresEncryptedDB(
    database_url=os.getenv('DATABASE_URL'),
    encryption_key=os.getenv('ENCRYPTION_KEY')
)

db.insert_user('zhangsan', '110101199001011234', '6222021234567890123')
user = db.get_user('zhangsan')
print(user)
```

#### 步骤3：密钥管理方案

```python
import os
from typing import Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EncryptionKeyManager:
    """加密密钥管理器"""
    
    def __init__(self):
        self.keys: dict = {}
        self.rotation_period_days = 365
    
    def get_current_key(self) -> str:
        """获取当前加密密钥"""
        key = os.getenv('ENCRYPTION_KEY')
        if not key or len(key) < 32:
            raise ValueError("ENCRYPTION_KEY 必须至少 32 字符")
        return key
    
    def get_previous_key(self) -> Optional[str]:
        """获取上一个密钥（用于密钥轮换）"""
        return os.getenv('ENCRYPTION_KEY_PREVIOUS')
    
    def generate_new_key(self) -> str:
        """生成新密钥"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def rotate_key(self) -> tuple:
        """
        轮换密钥
        
        Returns:
            (新密钥, 旧密钥)
        """
        import secrets
        
        # 生成新密钥
        new_key = secrets.token_urlsafe(32)
        old_key = self.get_current_key()
        
        logger.info("密钥已轮换，请更新环境变量")
        logger.info(f"新密钥: {new_key[:8]}...")
        logger.info(f"旧密钥已备份，请设置为 ENCRYPTION_KEY_PREVIOUS")
        
        return new_key, old_key
    
    def decrypt_with_fallback(self, encryptor: AES256Encryptor, encrypted: str, context: str) -> str:
        """
        使用密钥回退机制解密（支持密钥轮换）
        
        Args:
            encryptor: 加密器实例
            encrypted: 加密字符串
            context: 加密上下文
        
        Returns:
            解密后的明文
        """
        # 尝试当前密钥
        try:
            return encryptor.decrypt(encrypted, context)
        except Exception:
            pass
        
        # 尝试旧密钥
        previous_key = self.get_previous_key()
        if previous_key:
            old_encryptor = AES256Encryptor(previous_key)
            try:
                plaintext = old_encryptor.decrypt(encrypted, context)
                logger.info(f"使用旧密钥解密成功，应重新加密: {context}")
                return plaintext
            except Exception:
                pass
        
        raise ValueError(f"解密失败: {context}")


# 密钥轮换脚本
def rotate_encryption_keys():
    """执行密钥轮换"""
    key_manager = EncryptionKeyManager()
    new_key, old_key = key_manager.rotate_key()
    
    print(f"""
密钥轮换完成！

请执行以下操作：

1. 更新环境变量：
   ENCRYPTION_KEY_PREVIOUS={old_key}
   ENCRYPTION_KEY={new_key}

2. 重启应用

3. 运行数据重新加密脚本（可选，但推荐）

注意：
- 保留旧密钥至少 90 天
- 监控旧密钥使用情况
- 所有旧密钥加密的数据应重新加密
""")


if __name__ == '__main__':
    rotate_encryption_keys()
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `ENCRYPTION_KEY` | 必需 | 主加密密钥（>= 32 字符） |
| `ENCRYPTION_KEY_PREVIOUS` | 可选 | 旧密钥（用于轮换） |
| `ENCRYPTION_ALGORITHM` | AES-256-GCM | 加密算法 |
| `KEY_DERIVATION_ITERATIONS` | 100000 | 密钥派生迭代次数 |

---

## 成本估算

| 指标 | 应用层加密 | 数据库加密 |
|------|-----------|-----------|
| 月成本 | $0 | $0 |
| 性能影响 | 5-10% | 10-15% |
| 存储开销 | 30-50% | 30-50% |
| 实施时间 | 2-4小时 | 4-8小时 |

---

## 迁出成本

- **迁出难度**：中
- **迁出步骤**：
  1. 导出所有加密数据
  2. 使用旧密钥解密
  3. 使用新密钥重新加密
  4. 验证数据完整性
- **数据迁移工具**：需编写迁移脚本

---

## 与其他武器配合

- **前置**：
  - [secret-management.md](../free-tier/secret-management.md) - 管理加密密钥
  - [data-masking.md](./data-masking.md) - 日志脱敏

- **后置**：
  - [backup-service.md](../saas/backup-service.md) - 加密备份

- **配合**：
  - 与数据库备份配合，确保备份数据已加密
  - 与密钥轮换流程配合，平滑过渡

---

## 常见问题

**Q: AES-256-GCM 和 AES-256-CBC 选哪个？**  
A: 推荐 GCM：
- GCM 提供认证加密，防篡改
- GCM 并行性能更好
- CBC 需要额外 HMAC 保证完整性

**Q: 加密对性能影响多大？**  
A: 典型影响：
- 单次加密/解密：< 1ms
- 批量操作：增加 5-10% 时间
- 建议：只加密敏感字段，非敏感字段不加密

**Q: 如何处理加密字段查询？**  
A: 三种方案：
1. 使用盲索引（Blind Index）- 可精确匹配
2. 加密前标准化 - 如身份证号统一格式
3. 不支持加密字段范围查询

**Q: 密钥丢失了怎么办？**  
A: **无法恢复**。这是加密的核心特性：
- 必须有密钥备份机制
- 建议使用密钥管理服务（KMS）
- 定期测试密钥恢复流程

---

## 推荐实现

### 开源方案

- **Python**: `cryptography` 库（本文方案）
- **Node.js**: `crypto` 内置模块
- **Go**: `crypto/aes` 标准库
- **Java**: `javax.crypto` 标准库

### 数据库扩展

- **PostgreSQL**: `pgcrypto` 扩展（免费）
- **MySQL**: `AES_ENCRYPT/AES_DECRYPT` 函数（免费）
- **SQLite**: SEE（SQLite Encryption Extension，付费）

### 云服务方案（可选）

- **AWS KMS** - $1/月 + $0.03/10000次请求
- **Google Cloud KMS** - $0.06/月 + $0.03/10000次请求
- **HashiCorp Vault** - 开源自托管免费

---

## 最佳实践清单

- [ ] 加密密钥 >= 32 字符
- [ ] 密钥存储在环境变量或 KMS
- [ ] 使用 AES-256-GCM 算法
- [ ] 每个字段使用独立的加密上下文
- [ ] 有密钥轮换计划（每年至少一次）
- [ ] 有密钥备份和恢复流程
- [ ] 加密字段有清晰的标识
- [ ] 加密操作有审计日志

---

## 验证清单

- [ ] 加密后数据无法直接读取
- [ ] 解密后数据与原始一致
- [ ] 密钥轮换流程测试通过
- [ ] 性能测试符合预期
- [ ] 数据库备份已加密
- [ ] 密钥丢失恢复测试通过
