# 配置文件暴露 (Configuration File Exposure)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-006 |
| 分类 | 数据安全 / 配置安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

敏感配置文件（如 `.env`、`config.json`、数据库配置）被部署到 Web 根目录或权限设置不当，导致数据库凭证、API 密钥等敏感信息泄露。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **Web 可访问的配置文件** - 配置文件存储在 Web 根目录或可通过 URL 访问
- [ ] **版本控制泄露** - 配置文件被提交到 Git 仓库且未在 `.gitignore` 中排除
- [ ] **默认凭据未更改** - 使用默认用户名、密码或密钥

### 🔍 典型场景

```
场景 1: 直接访问配置文件
访问: https://example.com/.env
文件内容: DB_PASSWORD=SuperSecret123
结果:     数据库被完全控制

场景 2: Git 仓库泄露
访问: https://example.com/.git/config
或:   https://github.com/user/repo/blob/main/.env
结果:     API 密钥、数据库凭据泄露

场景 3: 备份文件暴露
访问: https://example.com/config.php.bak
或:   https://example.com/web.config.old
结果:     配置信息泄露
```

---

## 一句话防御

**将配置文件存储在 Web 根目录外、使用环境变量、实施严格的文件权限、配置 Web 服务器拒绝访问敏感文件、使用密钥管理服务。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **gitleaks** | Git 仓库敏感信息扫描 | https://github.com/gitleaks/gitleaks |
| **truffleHog** | Git 历史敏感信息检测 | https://github.com/trufflesecurity/trufflehog |
| **GitGuardian** | 秘密检测平台 | https://www.gitguardian.com/ |
| **AWS Secrets Manager** | 密钥管理服务 | https://aws.amazon.com/secrets-manager/ |
| **HashiCorp Vault** | 密钥管理工具 | https://www.vaultproject.io/ |

---

## 快速缓解措施

### 1. Web 服务器配置
```nginx
# Nginx 配置：拒绝访问敏感文件
location ~ /\.(env|git|svn|htaccess|htpasswd) {
    deny all;
    return 404;
}

# 拒绝访问常见备份文件
location ~* \.(bak|backup|old|orig|original|save|swp|tmp)$ {
    deny all;
    return 404;
}

# 拒绝访问配置文件
location ~* (config\.php|database\.yml|settings\.py|\.env)$ {
    deny all;
    return 404;
}
```

### 2. 正确的 .gitignore
```gitignore
# 环境配置
.env
.env.local
.env.*.local

# 配置文件
config/secrets.yml
config/database.yml
config/credentials.yml.enc

# 云服务配置
.aws/credentials
.azure/credentials
.gcloud/credentials

# IDE 配置
.idea/
.vscode/
*.swp
*.swo
```

### 3. 使用环境变量
```python
# Python 示例：使用环境变量
import os
from dotenv import load_dotenv

# 从 .env 文件加载（仅在开发环境）
if os.getenv('ENV') == 'development':
    load_dotenv()

# 生产环境应使用系统环境变量
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
API_KEY = os.getenv('API_KEY')

# 永远不要在代码中硬编码敏感信息
# BAD: SECRET_KEY = "my-secret-key-123"
```

---

## 相关案例

- [CASE-EXT-DATA-005 临时文件暴露](./temp-file-exposure.md)
- [CASE-EXT-DATA-007 快照泄露](./snapshot-leak.md)

---

## 参考标准

- CWE-538: Insertion of Sensitive Information into Externally-Accessible File or Directory
- OWASP ASVS v4.0 - V14: Configuration
- NIST SP 800-53 - CM-6: Configuration Settings
- 12-Factor App - Config
