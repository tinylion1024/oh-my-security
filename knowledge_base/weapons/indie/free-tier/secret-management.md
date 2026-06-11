# 密钥管理方案

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费 - $10/月
- **实施时间**: 2-4小时
- **维护成本**: 1小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
安全管理 API Key、数据库密码、加密密钥等敏感凭证，防止密钥硬编码、泄露和滥用。适用于所有需要管理外部服务凭证的独立开发者项目。

---

## 核心原则

### 密钥安全生命周期

```
密钥生命周期管理
┌─────────────────────────────────────────────────────┐
│                    生成阶段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │强随机生成│  │最小权限  │  │命名规范  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    存储阶段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │环境变量  │  │密钥管理器│  │加密存储  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    使用阶段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │运行时加载│  │内存保护  │  │审计日志  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    轮换阶段                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │定期轮换  │  │无停机替换│  │历史追溯  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

### 密钥管理策略矩阵

| 方案 | 成本 | 安全性 | 适用场景 |
|-----|------|--------|---------|
| 环境变量 | 免费 | 中 | L1 独立开发者 |
| .env 文件 | 免费 | 中低 | 开发环境 |
| HashiCorp Vault | 免费 | 高 | L2+ 有自托管能力 |
| 云服务密钥管理 | $1-10/月 | 高 | L2+ 云原生项目 |

---

## 快速上手（5分钟）

### Python 环境变量方案

```python
# config.py
import os
from typing import Optional
from dataclasses import dataclass

@dataclass
class Config:
    """应用配置 - 从环境变量加载"""
    
    # 必需密钥
    DATABASE_URL: str
    SECRET_KEY: str
    API_KEY: str
    
    # 可选密钥
    REDIS_URL: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量加载配置"""
        
        # 验证必需密钥
        required = ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
        missing = [k for k in required if not os.getenv(k)]
        
        if missing:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing)}")
        
        return cls(
            DATABASE_URL=os.getenv('DATABASE_URL'),
            SECRET_KEY=os.getenv('SECRET_KEY'),
            API_KEY=os.getenv('API_KEY'),
            REDIS_URL=os.getenv('REDIS_URL'),
            SMTP_PASSWORD=os.getenv('SMTP_PASSWORD'),
        )
    
    def validate(self) -> bool:
        """验证密钥安全性"""
        issues = []
        
        # 检查密钥强度
        if len(self.SECRET_KEY) < 32:
            issues.append("SECRET_KEY 长度应至少 32 字符")
        
        if self.SECRET_KEY in ['dev', 'test', 'secret', 'password']:
            issues.append("SECRET_KEY 不能使用弱密码")
        
        if issues:
            raise ValueError(f"密钥安全问题: {'; '.join(issues)}")
        
        return True


# 使用示例
config = Config.from_env()
config.validate()

# .env 文件示例（开发环境）
"""
# .env - 不要提交到 Git！

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# 应用密钥（生成方式：openssl rand -hex 32）
SECRET_KEY=a1b2c3d4e5f6...

# API 密钥
API_KEY=sk_live_xxxxx

# 可选服务
REDIS_URL=redis://localhost:6379
SMTP_PASSWORD=xxxxx
"""

# .gitignore 必须包含
"""
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
"""


# 快速生成密钥
def generate_secret_key(length: int = 32) -> str:
    """生成强随机密钥"""
    import secrets
    return secrets.token_hex(length)


if __name__ == '__main__':
    print(f"生成的新密钥: {generate_secret_key()}")
```

---

## 详细方案

### 方案架构

```
┌────────────────────────────────────────────────────────┐
│                    密钥管理架构                         │
├────────────────────────────────────────────────────────┤
│                                                        │
│  开发环境                 生产环境                      │
│  ┌──────────┐           ┌──────────┐                  │
│  │ .env文件 │           │ 环境变量  │                  │
│  └────┬─────┘           └────┬─────┘                  │
│       │                      │                         │
│       ▼                      ▼                         │
│  ┌─────────────────────────────────┐                  │
│  │         配置加载器              │                  │
│  │  - 验证必需密钥                 │                  │
│  │  - 类型转换                     │                  │
│  │  - 安全检查                     │                  │
│  └─────────────┬───────────────────┘                  │
│                │                                       │
│                ▼                                       │
│  ┌─────────────────────────────────┐                  │
│  │         应用使用                 │                  │
│  │  - 运行时内存                    │                  │
│  │  - 不记录日志                    │                  │
│  │  - 不返回响应                    │                  │
│  └─────────────────────────────────┘                  │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 实现步骤

#### 步骤1：环境变量最佳实践

**Python 完整方案**

```python
# requirements.txt
# python-dotenv>=1.0.0

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


class SecretManager:
    """密钥管理器"""
    
    def __init__(self, env_file: str = '.env', required_keys: List[str] = None):
        """
        初始化密钥管理器
        
        Args:
            env_file: 环境变量文件路径（仅开发环境）
            required_keys: 必需的密钥列表
        """
        self.required_keys = required_keys or []
        self._loaded = False
        self._secrets: Dict[str, str] = {}
        
        # 开发环境加载 .env 文件
        if os.getenv('ENV', 'development') == 'development':
            env_path = Path(env_file)
            if env_path.exists():
                load_dotenv(env_path)
                logger.info(f"已加载环境变量文件: {env_path}")
            else:
                logger.warning(f"环境变量文件不存在: {env_path}")
    
    def get(self, key: str, default: str = None) -> Optional[str]:
        """获取密钥"""
        value = os.getenv(key, default)
        
        if value is None and key in self.required_keys:
            raise ValueError(f"缺少必需的密钥: {key}")
        
        return value
    
    def get_all(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """批量获取密钥"""
        return {key: self.get(key) for key in keys}
    
    def validate(self) -> Dict[str, Any]:
        """验证密钥完整性"""
        issues = []
        
        for key in self.required_keys:
            value = os.getenv(key)
            if not value:
                issues.append(f"缺少: {key}")
            elif len(value) < 8:
                issues.append(f"{key} 长度过短")
            elif value.lower() in ['test', 'dev', 'password', 'secret']:
                issues.append(f"{key} 使用了弱值")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def generate_key(length: int = 32) -> str:
        """生成强随机密钥"""
        import secrets
        return secrets.token_urlsafe(length)
    
    def check_gitignore(self) -> bool:
        """检查 .gitignore 是否包含敏感文件"""
        gitignore_path = Path('.gitignore')
        if not gitignore_path.exists():
            return False
        
        content = gitignore_path.read_text()
        required_patterns = ['.env', '*.key', '*.pem', 'secrets/']
        
        return all(pattern in content for pattern in required_patterns)


# 使用示例
secrets = SecretManager(
    required_keys=['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
)

# 验证
validation = secrets.validate()
if not validation['valid']:
    print(f"密钥问题: {validation['issues']}")
    exit(1)

# 使用
db_url = secrets.get('DATABASE_URL')
api_key = secrets.get('API_KEY')
```

**Node.js 完整方案**

```javascript
// config/secrets.js
require('dotenv').config();

class SecretManager {
  constructor(options = {}) {
    this.requiredKeys = options.requiredKeys || [];
    this.validate();
  }

  get(key, defaultValue = null) {
    const value = process.env[key] || defaultValue;
    
    if (value === null && this.requiredKeys.includes(key)) {
      throw new Error(`缺少必需的密钥: ${key}`);
    }
    
    return value;
  }

  getAll(keys) {
    return keys.reduce((acc, key) => {
      acc[key] = this.get(key);
      return acc;
    }, {});
  }

  validate() {
    const issues = [];
    
    for (const key of this.requiredKeys) {
      const value = process.env[key];
      
      if (!value) {
        issues.push(`缺少: ${key}`);
      } else if (value.length < 8) {
        issues.push(`${key} 长度过短`);
      } else if (['test', 'dev', 'password', 'secret'].includes(value.toLowerCase())) {
        issues.push(`${key} 使用了弱值`);
      }
    }
    
    if (issues.length > 0) {
      console.error('密钥验证失败:', issues.join('; '));
      process.exit(1);
    }
    
    return true;
  }

  static generateKey(length = 32) {
    const crypto = require('crypto');
    return crypto.randomBytes(length).toString('base64url');
  }
}

// 使用示例
const secrets = new SecretManager({
  requiredKeys: ['DATABASE_URL', 'SECRET_KEY', 'API_KEY']
});

module.exports = secrets;
```

#### 步骤2：HashiCorp Vault 开源版配置

```bash
# 安装 Vault (macOS)
brew install vault

# 开发模式启动（仅用于本地测试）
vault server -dev

# 生产模式配置
# config.hcl
```

```hcl
# config.hcl - Vault 生产配置
storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = false
  tls_cert_file = "/opt/vault/tls/tls.crt"
  tls_key_file  = "/opt/vault/tls/tls.key"
}

api_addr = "https://your-domain.com:8200"
disable_mlock = true
ui = true
```

```bash
# 启动 Vault
vault server -config=config.hcl

# 初始化 Vault（仅首次）
vault operator init

# 解封 Vault（每次重启后需要）
vault operator unseal

# 启用密钥引擎
vault secrets enable -path=secret kv-v2

# 存储密钥
vault kv put secret/myapp database_url="postgresql://..." api_key="sk_live_..."

# 读取密钥
vault kv get secret/myapp
```

**Python Vault 客户端**

```python
# requirements.txt
# hvac>=1.0.0

import hvac
from typing import Optional, Dict

class VaultSecretManager:
    """HashiCorp Vault 密钥管理器"""
    
    def __init__(self, url: str, token: str, path: str = 'secret'):
        """
        初始化 Vault 客户端
        
        Args:
            url: Vault 服务器地址
            token: 访问令牌
            path: 密钥路径前缀
        """
        self.client = hvac.Client(url=url, token=token)
        self.path = path
        
        if not self.client.is_authenticated():
            raise ValueError("Vault 认证失败")
    
    def get(self, key: str) -> Optional[str]:
        """获取密钥"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(
                path=f'{self.path}/{key}'
            )
            return response['data']['data'].get('value')
        except hvac.exceptions.InvalidPath:
            return None
    
    def set(self, key: str, value: str, metadata: Dict = None):
        """存储密钥"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=f'{self.path}/{key}',
            secret={'value': value, **(metadata or {})}
        )
    
    def delete(self, key: str):
        """删除密钥"""
        self.client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=f'{self.path}/{key}'
        )
    
    def list(self) -> list:
        """列出所有密钥"""
        try:
            response = self.client.secrets.kv.v2.list_secrets(path=self.path)
            return response['data']['keys']
        except hvac.exceptions.InvalidPath:
            return []


# 使用示例
vault = VaultSecretManager(
    url=os.getenv('VAULT_ADDR'),
    token=os.getenv('VAULT_TOKEN'),
    path='myapp'
)

api_key = vault.get('api_key')
```

#### 步骤3：密钥轮换流程

```python
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class KeyRotationManager:
    """密钥轮换管理器"""
    
    def __init__(self, secrets: SecretManager):
        self.secrets = secrets
        self.rotation_log: List[Dict] = []
    
    def rotate_key(
        self, 
        key_name: str, 
        new_value: str,
        old_key_suffix: str = '_OLD'
    ) -> Tuple[str, str]:
        """
        轮换密钥
        
        Args:
            key_name: 密钥名称
            new_value: 新密钥值
            old_key_suffix: 旧密钥后缀
        
        Returns:
            (旧密钥名, 新密钥名)
        """
        old_key = f"{key_name}{old_key_suffix}"
        old_value = os.getenv(key_name)
        
        # 1. 备份旧密钥
        os.environ[old_key] = old_value
        
        # 2. 设置新密钥
        os.environ[key_name] = new_value
        
        # 3. 记录轮换日志
        log_entry = {
            'key_name': key_name,
            'rotated_at': datetime.now().isoformat(),
            'old_key_backup': old_key,
        }
        self.rotation_log.append(log_entry)
        
        logger.info(f"密钥已轮换: {key_name}")
        
        return old_key, key_name
    
    def get_rotation_schedule(self) -> Dict[str, timedelta]:
        """获取密钥轮换周期建议"""
        return {
            'API_KEY': timedelta(days=90),
            'DATABASE_PASSWORD': timedelta(days=90),
            'SECRET_KEY': timedelta(days=365),
            'JWT_SECRET': timedelta(days=180),
            'ENCRYPTION_KEY': timedelta(days=365),
        }
    
    def check_rotation_needed(self) -> List[Dict]:
        """检查需要轮换的密钥"""
        schedule = self.get_rotation_schedule()
        needed = []
        
        # 检查轮换日志
        last_rotations = {}
        for entry in reversed(self.rotation_log):
            key = entry['key_name']
            if key not in last_rotations:
                last_rotations[key] = datetime.fromisoformat(entry['rotated_at'])
        
        for key, period in schedule.items():
            last_rotation = last_rotations.get(key)
            
            if not last_rotation:
                needed.append({
                    'key': key,
                    'reason': '从未轮换'
                })
            elif datetime.now() - last_rotation > period:
                needed.append({
                    'key': key,
                    'reason': f'超过轮换周期 ({period.days}天)',
                    'last_rotation': last_rotation.isoformat()
                })
        
        return needed


# 轮换脚本示例
def rotate_database_password():
    """轮换数据库密码"""
    import psycopg2
    
    # 1. 生成新密码
    new_password = SecretManager.generate_key(24)
    
    # 2. 连接数据库
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    # 3. 更新密码
    user = 'app_user'  # 应用数据库用户
    cursor.execute(f"ALTER USER {user} WITH PASSWORD '{new_password}';")
    conn.commit()
    
    # 4. 更新环境变量
    # 这里需要更新实际的密钥存储（环境变量/Vault等）
    logger.info("数据库密码已更新，请更新应用配置")
    
    return new_password
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `env_file` | `.env` | 环境变量文件路径 |
| `required_keys` | `[]` | 必需密钥列表 |
| `validation_strict` | `True` | 严格验证模式 |
| `rotation_period_days` | 90 | 默认轮换周期 |

---

## 成本估算

| 方案 | 月成本 | 功能 | 适用场景 |
|------|--------|------|---------|
| 环境变量 | $0 | 基础密钥管理 | L1 独立开发者 |
| HashiCorp Vault 自托管 | $0 | 完整密钥管理 | L2 有运维能力 |
| AWS Secrets Manager | $0.40/密钥/月 | 云原生方案 | AWS 用户 |
| Vercel Env Variables | $0 | 部署平台集成 | Vercel 用户 |
| Doppler | $0-8/月 | 开发者友好 | L2 小团队 |

---

## 迁出成本

### 从环境变量迁出

- **迁出难度**：低
- **迁出步骤**：
  1. 导出所有环境变量
  2. 导入到新密钥管理系统
  3. 更新应用加载逻辑
  4. 测试验证

### 迁出到其他平台

- **迁出难度**：中
- **迁出步骤**：
  1. 从当前系统导出密钥
  2. 批量导入到新系统
  3. 更新应用配置
  4. 轮换所有密钥（安全最佳实践）

---

## 与其他武器配合

- **前置**：
  - [input-validation.md](../free-tier/input-validation.md) - 验证密钥格式

- **后置**：
  - [encryption-at-rest.md](../free-tier/encryption-at-rest.md) - 加密密钥保护
  - [data-masking.md](./data-masking.md) - 日志中隐藏密钥

- **配合**：
  - 与 CI/CD 配合，注入密钥到构建环境
  - 与监控配合，检测密钥泄露告警

---

## 常见问题

**Q: .env 文件安全吗？**  
A: .env 文件仅用于开发环境。生产环境应使用：
- 环境变量（容器化部署）
- 密钥管理服务（云平台）
- HashiCorp Vault（自托管）

**Q: 密钥应该多久轮换一次？**  
A: 建议周期：
- API Key：90天
- 数据库密码：90天
- 加密密钥：365天
- 发生泄露时：立即

**Q: 如何检测密钥是否泄露？**  
A: 使用以下工具：
- GitHub Secret Scanning（免费）
- GitGuardian（有免费额度）
- TruffleHog（开源扫描工具）

**Q: 多环境如何管理？**  
A: 使用环境前缀：
- `DEV_DATABASE_URL`
- `STAGING_DATABASE_URL`
- `PROD_DATABASE_URL`

---

## 推荐实现

### 免费/开源方案

- **环境变量** - 适用于所有平台，免费
- **HashiCorp Vault** - 功能完整，自托管免费
- **Infisical** - 开源密钥管理，开发者友好

### 云服务方案

- **AWS Secrets Manager** - $0.40/密钥/月
- **Google Secret Manager** - $0.06/密钥/月
- **Vercel Environment Variables** - 免费层
- **Doppler** - 免费层 + $8/月

---

## 最佳实践清单

- [ ] 所有密钥通过环境变量加载，无硬编码
- [ ] .env 文件已添加到 .gitignore
- [ ] 密钥长度 >= 32 字符
- [ ] 有密钥轮换计划（至少每90天）
- [ ] 有密钥泄露监控（GitHub Secret Scanning）
- [ ] 开发和生产环境使用不同密钥
- [ ] 密钥权限遵循最小权限原则
- [ ] 有密钥备份和恢复流程

---

## 验证清单

- [ ] 应用启动时验证必需密钥存在
- [ ] 密钥强度检查通过
- [ ] .gitignore 包含敏感文件
- [ ] 无密钥泄露警告（GitHub/GitGuardian）
- [ ] 密钥轮换流程测试通过
- [ ] 生产环境不使用开发密钥
