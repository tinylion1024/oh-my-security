# 10分钟快速防御清单

## 元数据
- **tier适用**: L1 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 10分钟
- **维护成本**: 30分钟/月
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## 适用场景
独立开发者在产品上线前或日常维护时，快速完成基础安全加固。每项措施都可以在1分钟内完成，全部完成可防御80%的常见攻击。

---

## 快速上手（总览）

```
10分钟防御清单
├── 1分钟：修改默认密码
├── 1分钟：启用HTTPS
├── 1分钟：关闭不必要端口
├── 1分钟：设置强密码策略
├── 1分钟：启用日志记录
├── 1分钟：配置基础限流
├── 1分钟：检查公开访问权限
├── 1分钟：设置自动备份
├── 1分钟：更新依赖
└── 1分钟：启用基础监控
```

---

## 详细方案

### 1. 立即修改默认密码

**风险**：默认密码是黑客的首选攻击路径，Shodan上大量暴露的服务器仍使用 `admin/admin123`。

**免费方案**：

```bash
# 1分钟操作：检查并修改关键服务密码
# 数据库密码
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY '新强密码';
FLUSH PRIVILEGES;

# Redis密码（编辑 redis.conf）
echo "requirepass 你的强密码" >> /etc/redis/redis.conf
systemctl restart redis

# 服务器登录密码
passwd your_username
```

**验证方法**：
```bash
# 尝试用空密码或默认密码登录，应失败
mysql -u root -p"" -e "SELECT 1" && echo "警告：空密码可登录！"
redis-cli -a "" ping && echo "警告：Redis无密码！"
```

---

### 2. 启用HTTPS

**风险**：HTTP传输明文可被中间人窃听，包括用户密码、Cookie、API密钥。

**免费方案**：

```bash
# 使用 Let's Encrypt 免费证书（有效期90天，自动续期）
# 安装 certbot
sudo apt install certbot python3-certbot-nginx  # Ubuntu/Debian
# 或
sudo yum install certbot python3-certbot-nginx  # CentOS/RHEL

# 1分钟获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期（添加到crontab）
echo "0 3 * * * certbot renew --quiet" | crontab -
```

**Nginx配置强制HTTPS**：
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
    
    # 安全headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

**验证方法**：
```bash
# 检查HTTPS是否生效
curl -I https://yourdomain.com
# 应看到：HTTP/2 200

# 检查HTTP是否跳转
curl -I http://yourdomain.com
# 应看到：HTTP/1.1 301 Moved Permanently

# 在线测试
# https://www.ssllabs.com/ssltest/
```

---

### 3. 关闭不必要端口

**风险**：开放端口越多，攻击面越大。未使用的服务可能存在未知漏洞。

**免费方案**：

```bash
# 1分钟检查当前开放端口
sudo netstat -tlnp
# 或
sudo ss -tlnp

# 只保留必要端口（示例：SSH 22, HTTP 80, HTTPS 443）
# 使用ufw防火墙（Ubuntu）
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'
sudo ufw enable

# 使用firewalld（CentOS）
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

**验证方法**：
```bash
# 从外部扫描端口
nmap -p- your_server_ip

# 应只显示：
# PORT    STATE SERVICE
# 22/tcp  open  ssh
# 80/tcp  open  http
# 443/tcp open  https

# 检查防火墙状态
sudo ufw status verbose
```

---

### 4. 设置强密码策略

**风险**：弱密码是暴力破解的主要目标，"123456"、"password"仍是最常见密码。

**免费方案**：

```python
# 后端密码强度验证（Python示例）
import re

def validate_password(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    if len(password) < 12:
        return False, "密码至少12位"
    if not re.search(r'[A-Z]', password):
        return False, "需要包含大写字母"
    if not re.search(r'[a-z]', password):
        return False, "需要包含小写字母"
    if not re.search(r'[0-9]', password):
        return False, "需要包含数字"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "需要包含特殊字符"
    
    # 检查常见弱密码
    weak_passwords = ['password123', 'qwerty123', 'admin123']
    if password.lower() in weak_passwords:
        return False, "密码过于常见"
    
    return True, "密码强度符合要求"

# 注册时使用
valid, message = validate_password(user_password)
if not valid:
    raise ValueError(message)
```

**前端配合验证**：
```typescript
// 密码强度实时提示
function checkPasswordStrength(password: string): string {
  let strength = 0;
  if (password.length >= 12) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^A-Za-z0-9]/.test(password)) strength++;
  
  const levels = ['极弱', '弱', '一般', '强', '极强'];
  return levels[strength] || '极弱';
}
```

**验证方法**：
```bash
# 测试弱密码是否被拒绝
curl -X POST https://yourdomain.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"123456"}'

# 应返回错误：密码强度不符合要求
```

---

### 5. 启用日志记录

**风险**：没有日志就无法发现攻击、溯源取证、分析安全事件。

**免费方案**：

```python
# Python日志配置（1分钟添加）
import logging
from logging.handlers import RotatingFileHandler
import os

# 创建日志目录
os.makedirs('logs', exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        RotatingFileHandler(
            'logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
    ],
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 关键操作记录
@app.route('/api/login', methods=['POST'])
def login():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    email = request.json.get('email')
    
    logger.info(f"LOGIN_ATTEMPT - IP: {ip} - Email: {email}")
    
    if authenticate_user(email, password):
        logger.info(f"LOGIN_SUCCESS - IP: {ip} - Email: {email}")
    else:
        logger.warning(f"LOGIN_FAILED - IP: {ip} - Email: {email}")
```

**日志内容应包含**：
- 时间戳（ISO 8601格式）
- 事件类型（登录/注册/支付/删除等）
- 来源IP
- 用户标识
- 操作结果

**验证方法**：
```bash
# 检查日志文件是否生成
ls -la logs/app.log

# 实时查看日志
tail -f logs/app.log

# 搜索异常事件
grep -i "failed\|error\|warning" logs/app.log | tail -20
```

---

### 6. 配置基础限流

**风险**：无限制的API调用会导致DDoS攻击、暴力破解、资源耗尽。

**免费方案**：

```javascript
// Node.js/Express 内存限流（1分钟添加）
const rateLimit = require('express-rate-limit');

// 通用限流：每IP每分钟100次请求
const generalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1分钟
  max: 100, // 限制100次
  message: { error: '请求过于频繁，请稍后再试' },
  standardHeaders: true,
  legacyHeaders: false,
});

// 登录严格限流：每IP每分钟5次
const loginLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5,
  message: { error: '登录尝试过多，请15分钟后再试' },
  skipSuccessfulRequests: true, // 成功请求不计数
});

app.use('/api/', generalLimiter);
app.use('/api/login', loginLimiter);
app.use('/api/register', loginLimiter);
```

**Python/Flask版本**：
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # 登录逻辑
    pass
```

**验证方法**：
```bash
# 快速发送多次请求测试限流
for i in {1..10}; do
  curl -X POST https://yourdomain.com/api/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}'
  echo ""
done

# 第6次应返回429 Too Many Requests
```

---

### 7. 检查公开访问权限

**风险**：云存储、数据库、管理后台意外暴露在公网。

**免费方案**：

```bash
# 1分钟检查清单

# 1. 检查云存储权限（AWS S3示例）
aws s3api get-bucket-acl --bucket your-bucket-name
# 确保没有 "URI": "http://acs.amazonaws.com/groups/global/AllUsers"

# 2. 检查数据库外网访问
# MySQL
mysql -u root -e "SELECT user, host FROM mysql.user WHERE host = '%' OR host LIKE '%.%'"
# Redis
redis-cli CONFIG GET bind
# 应该是 bind 127.0.0.1 或内网IP

# 3. 检查管理后台是否有认证
curl -I https://yourdomain.com/admin
# 不应返回200，应返回302跳转登录或401/403

# 4. 检查敏感文件是否可访问
curl -I https://yourdomain.com/.env
curl -I https://yourdomain.com/.git/config
curl -I https://yourdomain.com/config.php
# 都应返回404或403
```

**Nginx禁止敏感文件访问**：
```nginx
# 在server块中添加
location ~ /\.(env|git|htaccess|htpasswd) {
    deny all;
    return 404;
}

location ~ \.(log|sql|bak|backup|old)$ {
    deny all;
    return 404;
}
```

**验证方法**：
```bash
# 使用在线工具扫描
# https://securityheaders.com/
# https://observatory.mozilla.org/

# 或使用nuclei快速扫描
# nuclei -u https://yourdomain.com -t exposures/
```

---

### 8. 设置自动备份

**风险**：数据丢失（攻击、误删、硬件故障）无恢复手段，业务直接终止。

**免费方案**：

```bash
# 1分钟设置数据库自动备份

# 创建备份脚本
cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"
mkdir -p $BACKUP_DIR

# MySQL备份
mysqldump -u root -p'你的密码' --all-databases | gzip > $BACKUP_DIR/mysql_$DATE.sql.gz

# 文件备份（如用户上传的文件）
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/uploads

# 保留最近7天的备份
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed at $DATE"
EOF

chmod +x /root/backup.sh

# 添加到crontab（每天凌晨3点执行）
echo "0 3 * * * /root/backup.sh >> /var/log/backup.log 2>&1" | crontab -
```

**云存储异地备份**：
```bash
# 使用rclone同步到云存储（免费额度通常够用）
# 安装rclone
curl https://rclone.org/install.sh | sudo bash

# 配置（交互式，只需一次）
rclone config

# 添加到备份脚本
rclone sync /backup remote:backup-bucket --progress
```

**验证方法**：
```bash
# 手动执行备份测试
/root/backup.sh

# 检查备份文件
ls -lh /backup/

# 模拟恢复
gunzip < /backup/mysql_latest.sql.gz | mysql -u root -p test_restore
```

---

### 9. 更新依赖

**风险**：过时的依赖包含已知漏洞，是自动化攻击的首选目标。

**免费方案**：

```bash
# 1分钟检查并更新

# Node.js项目
npm audit
npm audit fix

# Python项目
pip list --outdated
pip install --upgrade pip
pip-audit  # 需要安装: pip install pip-audit

# 系统包更新
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
sudo yum update -y  # CentOS/RHEL
```

**自动化依赖检查（GitHub Actions）**：
```yaml
# .github/workflows/security.yml
name: Security Check

on:
  schedule:
    - cron: '0 6 * * 1'  # 每周一早上6点

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run npm audit
        run: npm audit --audit-level=high
      
      - name: Run pip-audit
        run: |
          pip install pip-audit
          pip-audit
```

**验证方法**：
```bash
# 检查是否有已知漏洞
npm audit
# 应无high/critical漏洞

# 查看过时依赖
npm outdated
# 主要依赖应保持最新
```

---

### 10. 启用基础监控

**风险**：服务器宕机、异常访问、资源耗尽却不知道，用户先发现就晚了。

**免费方案**：

**方案A：Uptime监控（UptimeRobot免费版）**
```
1. 访问 https://uptimerobot.com/
2. 免费注册账号
3. 添加监控：
   - Monitor Type: HTTPS
   - URL: https://yourdomain.com
   - Monitoring Interval: 5分钟（免费版）
4. 设置告警邮箱

免费额度：
- 50个监控点
- 5分钟检查间隔
- 邮件告警
```

**方案B：服务器监控（自建）**
```bash
# 1分钟安装netdata（开源监控）
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# 访问 http://your-server:19999 查看监控面板

# 或使用Prometheus + Grafana（更强大但需要配置）
```

**简单存活检查脚本**：
```bash
cat > /root/monitor.sh << 'EOF'
#!/bin/bash

# 检查关键服务
services=("nginx" "mysql" "redis")
for service in "${services[@]}"; do
    if ! systemctl is-active --quiet $service; then
        echo "ALERT: $service is down!" | mail -s "Service Alert" your@email.com
        systemctl restart $service
    fi
done

# 检查磁盘空间
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Disk usage is ${DISK_USAGE}%" | mail -s "Disk Alert" your@email.com
fi
EOF

chmod +x /root/monitor.sh
echo "*/5 * * * * /root/monitor.sh" | crontab -
```

**验证方法**：
```bash
# 测试监控告警
sudo systemctl stop nginx  # 暂停nginx
# 等待5分钟，检查是否收到告警邮件

# 访问监控面板
curl http://localhost:19999/api/v1/allmetrics
```

---

## 成本估算

| 指标 | 免费方案 | 备注 |
|------|---------|------|
| 证书费用 | $0 | Let's Encrypt |
| 监控费用 | $0 | UptimeRobot免费版 |
| 备份存储 | $0 | 本地+云存储免费额度 |
| 防火墙 | $0 | 系统内置 |
| 总成本 | $0 | 完全免费 |

---

## 迁出成本

- **难度**：低
- **时间**：< 30分钟
- **步骤**：
  1. 导出日志文件
  2. 备份配置文件（nginx.conf、防火墙规则）
  3. 在新服务器重复上述步骤
  4. 或使用云服务商的安全组替代本地防火墙

---

## 与其他武器配合

- **前置**：无（这是第一道防线）
- **后置**：
  - [入侵检测系统](../open-source/intrusion-detection.md)
  - [Web应用防火墙](../free-tier/waf.md)
  - [日志分析平台](../open-source/log-analysis.md)
- **替代**：云服务商安全套件（如AWS Shield、Cloudflare Pro）

---

## 常见问题

**Q: 10分钟真的够吗？**
A: 每项措施平均1分钟，总共10分钟。第一次可能需要20分钟，熟悉后可以更快。

**Q: 这些措施真的有效吗？**
A: 可以防御80%的自动化攻击和随机扫描。针对性攻击需要更深度的防护。

**Q: 我使用云服务，还需要这些吗？**
A: 云服务只提供基础设施安全，应用层安全（如密码策略、限流）仍需要自己配置。

**Q: 完成这些后还需要什么？**
A: 建议继续学习：
- [L1认证安全案例](../../../cases/indie/core/auth/)
- [L1数据安全案例](../../../cases/indie/core/data/)
- [独立开发者威胁建模](../../../guides/indie-threat-modeling.md)

**Q: 如何记住定期检查？**
A: 设置日历提醒，每月第一个周一检查：
1. 查看监控日志异常
2. 运行依赖更新
3. 验证备份可恢复
4. 检查证书到期时间

---

## 快速检查脚本

将以下脚本保存为 `security-check.sh`，每月运行一次：

```bash
#!/bin/bash
# 安全检查脚本 - 每月运行

echo "=== 安全检查 $(date) ==="

# 1. 检查开放端口
echo -e "\n[端口检查]"
sudo netstat -tlnp | grep LISTEN

# 2. 检查HTTPS证书
echo -e "\n[证书检查]"
certbot certificates

# 3. 检查依赖漏洞
echo -e "\n[依赖检查]"
npm audit --audit-level=high 2>/dev/null || echo "无npm项目"

# 4. 检查备份
echo -e "\n[备份检查]"
ls -lh /backup/ | tail -5

# 5. 检查日志异常
echo -e "\n[日志异常]"
grep -i "failed\|error" logs/app.log 2>/dev/null | tail -10 || echo "无日志文件"

# 6. 检查磁盘空间
echo -e "\n[磁盘空间]"
df -h | grep -E "^/dev"

echo -e "\n=== 检查完成 ==="
```

---

## 推荐实现

- **免费**：本文所有方案均为免费
- **低成本升级**：
  - Cloudflare Pro - $20/月 - 增强DDoS防护
  - UptimeRobot Pro - $7/月 - 1分钟监控间隔
  - Better Uptime - $20/月 - 状态页面 + 团队告警

---

## 相关资源

**工具**
- [Let's Encrypt](https://letsencrypt.org/) - 免费SSL证书
- [UptimeRobot](https://uptimerobot.com/) - 免费网站监控
- [Certbot](https://certbot.eff.org/) - 证书自动管理
- [Netdata](https://www.netdata.cloud/) - 开源服务器监控

**学习资源**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [Mozilla SSL配置生成器](https://ssl-config.mozilla.org/)

**相关案例**
- [数据库暴露案例](../../../cases/indie/core/data/database-exposure.md)
- [弱密码攻击案例](../../../cases/indie/core/auth/weak-password.md)
