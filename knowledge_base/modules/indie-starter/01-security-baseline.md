# 第 1 周：安全基线

## 概述

本周建立最基础的安全防护，这些是每个独立开发者**必须完成**的配置。

**预计时间**: 2 小时
**难度**: 简单
**成本**: $0

---

## 核心安全原则

### 1. 最小权限原则
只给用户和系统所需的最低权限，不多给。

### 2. 纵深防御原则
不依赖单一防护，多层防护更安全。

### 3. 安全默认原则
默认配置应该是最安全的，需要显式开放权限。

### 4. 快速响应原则
能快速发现问题并响应，比完美防护更重要。

### 5. 成本效益原则
安全投入要与风险匹配，独立开发者要务实。

---

## 必做安全配置清单

### 🔴 关键项（必须立即完成）

#### 1. 环境变量管理

**风险**: API Key、数据库密码等敏感信息硬编码在代码中，泄露到 Git 仓库。

**操作步骤**:

```bash
# 1. 创建 .env 文件
touch .env

# 2. 添加到 .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo ".env.*.local" >> .gitignore

# 3. 使用环境变量
```

```python
# Python 示例
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
API_KEY = os.getenv('API_KEY')
```

```javascript
// Node.js 示例
require('dotenv').config();

const databaseUrl = process.env.DATABASE_URL;
const apiKey = process.env.API_KEY;
```

**验证方法**:
```bash
# 确认 .env 不在 git 追踪中
git status | grep .env
# 应该没有输出
```

---

#### 2. 数据库密码修改

**风险**: 使用默认密码或空密码，数据库被入侵。

**操作步骤**:

```bash
# PostgreSQL
psql -U postgres
ALTER USER postgres WITH PASSWORD '新的强密码';

# MySQL
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY '新的强密码';

# MongoDB
mongo
use admin
db.changeUserPassword("admin", "新的强密码")

# Redis
# 编辑 redis.conf
requirepass 你的强密码
```

**强密码要求**:
- 至少 16 位
- 包含大小写字母、数字、特殊字符
- 不使用常见单词

---

#### 3. HTTPS 强制启用

**风险**: HTTP 明文传输，数据被窃听。

**操作步骤**:

```bash
# 使用 Let's Encrypt 免费证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

**Nginx 配置**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000" always;
}
```

---

### 🟠 高优先项（本周完成）

#### 4. 依赖安全检查

```bash
# Node.js
npm audit
npm audit fix

# Python
pip install safety
safety check

# 或使用 pip-audit
pip install pip-audit
pip-audit
```

---

#### 5. 敏感端口不暴露

```bash
# 检查开放端口
sudo netstat -tlnp

# 使用防火墙限制访问
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 数据库端口仅允许本地访问
# PostgreSQL: 修改 pg_hba.conf
# MySQL: 修改 bind-address = 127.0.0.1
# MongoDB: 修改 bindIp: 127.0.0.1
# Redis: bind 127.0.0.1
```

---

#### 6. 错误信息不泄露

**Python Flask**:
```python
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.errorhandler(500)
def internal_error(error):
    return "服务器错误", 500
```

**Node.js Express**:
```javascript
app.set('env', 'production');

app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).send('服务器错误');
});
```

---

### 🟡 中优先项（本月完成）

#### 7. 日志记录配置

```python
# Python 日志配置
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("应用启动")
```

---

#### 8. 定期备份

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# PostgreSQL 备份
pg_dump -U postgres mydb > $BACKUP_DIR/mydb_$DATE.sql

# 保留最近 7 天
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete

# 上传到云存储（可选）
# aws s3 cp $BACKUP_DIR/mydb_$DATE.sql s3://my-bucket/backups/
```

```bash
# 添加到 crontab
crontab -e
# 每天凌晨 3 点备份
0 3 * * * /path/to/backup.sh
```

---

#### 9. 基础监控

**免费方案推荐**:
- UptimeRobot: 免费监控 50 个站点，5 分钟检查
- Sentry: 免费错误监控，5K 错误/月
- Grafana Cloud: 免费指标监控

```bash
# UptimeRobot API 检查
curl "https://api.uptimerobot.com/v2/getMonitors" \
  -d "api_key=YOUR_API_KEY"
```

---

#### 10. 安全头配置

```nginx
# Nginx 安全头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

## 自动化检查脚本

保存为 `security-check.sh`:

```bash
#!/bin/bash

echo "=== 安全基线检查 ==="

# 1. 检查 .env 是否在 .gitignore
if grep -q ".env" .gitignore; then
    echo "✅ .env 已在 .gitignore"
else
    echo "❌ .env 未在 .gitignore"
fi

# 2. 检查 HTTPS
if curl -sI https://localhost 2>/dev/null | grep -q "200"; then
    echo "✅ HTTPS 已启用"
else
    echo "❌ HTTPS 未启用"
fi

# 3. 检查依赖漏洞
if command -v npm &> /dev/null; then
    npm audit --audit-level=high
fi

# 4. 检查开放端口
echo "开放端口:"
sudo netstat -tlnp | grep LISTEN

# 5. 检查防火墙
if command -v ufw &> /dev/null; then
    sudo ufw status
fi

echo "=== 检查完成 ==="
```

---

## 本周实施计划

| 天 | 任务 | 时间 |
|----|------|------|
| Day 1 | 环境变量配置、数据库密码修改 | 30 分钟 |
| Day 2 | HTTPS 配置 | 30 分钟 |
| Day 3 | 依赖检查、端口检查 | 20 分钟 |
| Day 4 | 错误处理、日志配置 | 20 分钟 |
| Day 5 | 备份配置、监控部署 | 20 分钟 |

---

## 验证清单

- [ ] .env 文件已创建且在 .gitignore 中
- [ ] 数据库密码已修改为强密码
- [ ] HTTPS 已强制启用
- [ ] 依赖安全检查通过
- [ ] 敏感端口仅本地访问
- [ ] 错误信息不泄露敏感数据
- [ ] 日志记录已配置
- [ ] 定期备份已设置
- [ ] 基础监控已部署
- [ ] 安全头已配置

---

## 下一步

完成本周任务后，继续 [第 2 周：账号安全](./02-account-security.md)
