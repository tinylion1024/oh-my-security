# 独立开发者安全基线武器

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防 + 检测
- **实现成本**: 免费
- **实施时间**: 30分钟（核心项）- 2小时（完整版）
- **维护成本**: 1小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
独立开发者发布产品前的安全基线检查清单，覆盖最常见的10+项安全风险，每项30分钟内可实施，$0成本。

---

## 快速上手（5分钟）

### 核心检查命令

```bash
# 一键检查脚本
curl -sSL https://raw.githubusercontent.com/your-repo/security-baseline/main/check.sh | bash
```

### 最小防御配置

```bash
# 1. 环境变量检查（防止泄露）
grep -r "API_KEY\|SECRET\|PASSWORD" . --include="*.js" --include="*.py" --include="*.ts"

# 2. 依赖安全检查
npm audit # Node.js
pip-audit # Python
trivy fs . # 通用

# 3. HTTPS强制检查
curl -I https://yourdomain.com | grep -i "strict-transport-security"
```

---

## 详细方案

### 检查项总览

| # | 检查项 | 风险等级 | 实施时间 | 免费工具 |
|---|--------|---------|---------|---------|
| 1 | 环境变量安全 | Critical | 10分钟 | dotenv-linter |
| 2 | 依赖安全扫描 | Critical | 5分钟 | npm audit / pip-audit |
| 3 | 数据库连接安全 | Critical | 15分钟 | 配置模板 |
| 4 | API密钥管理 | Critical | 10分钟 | 环境变量 |
| 5 | HTTPS强制配置 | High | 5分钟 | Let's Encrypt |
| 6 | 认证安全加固 | High | 20分钟 | bcrypt / argon2 |
| 7 | 日志安全脱敏 | High | 10分钟 | 自定义过滤器 |
| 8 | 备份策略 | High | 15分钟 | 免费云存储 |
| 9 | 监控告警 | Medium | 10分钟 | UptimeRobot |
| 10 | 速率限制 | Medium | 10分钟 | express-rate-limit |
| 11 | 输入验证 | High | 15分钟 | zod / pydantic |
| 12 | 错误信息安全 | Medium | 5分钟 | 配置模板 |

---

## L1 独立开发者版（速查版）

### 检查项 1: 环境变量安全

#### 一句话风险
你的 `.env` 文件被提交到 Git，API密钥、数据库密码泄露，攻击者获得你所有服务的完全控制权。

#### 一分钟识别
- [ ] 项目根目录存在 `.env` 文件
- [ ] `.gitignore` 中未包含 `.env*`
- [ ] 代码中存在硬编码的 API Key、密码、Token
- [ ] 曾在代码中 `console.log(process.env)` 或类似输出
→ 勾选≥1项，即需关注此风险

#### 一句话防御
`.env` 文件永远不提交到 Git，所有密钥通过环境变量注入，生产环境使用密钥管理服务。

#### 快速行动清单
1. [ ] 立即检查 `.gitignore` 是否包含 `.env*`（1分钟）
2. [ ] 检查历史提交是否泄露密钥，如有则立即轮换（5分钟）
3. [ ] 使用 `git-secrets` 防止未来泄露（5分钟）

#### 推荐工具
- 免费：`dotenv-linter` - 检查 `.env` 文件规范
- 免费：`git-secrets` - 防止密钥提交到 Git
- 免费：`trufflehog` - 扫描历史提交中的密钥

#### 代码示例

```bash
# 1. 添加到 .gitignore
echo ".env*" >> .gitignore
echo "!.env.example" >> .gitignore

# 2. 创建示例文件
cp .env .env.example
# 手动清空 .env.example 中的实际值，保留变量名

# 3. 安装 git-secrets 防止泄露
brew install git-secrets  # macOS
git secrets --install
git secrets --register-aws  # AWS 密钥检测
git secrets --add 'API_KEY.*=.*'  # 自定义检测规则

# 4. 扫描历史提交
trufflehog git file://. --only-verified
```

```python
# Python: 安全加载环境变量
import os
from dotenv import load_dotenv

# 加载环境变量（开发环境）
load_dotenv()

# 必需变量检查
REQUIRED_ENV_VARS = [
    'DATABASE_URL',
    'SECRET_KEY',
    'API_KEY',
]

def validate_env():
    """验证必需的环境变量"""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"缺少必需的环境变量: {missing}")

validate_env()

# 永远不要这样做
# API_KEY = "sk-xxxxxx"  # ❌ 硬编码密钥

# 正确做法
API_KEY = os.getenv('API_KEY')  # ✅ 从环境变量读取
```

```typescript
// Node.js: 安全加载环境变量
import 'dotenv/config';
import { z } from 'zod';

// 环境变量 Schema 验证
const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  SECRET_KEY: z.string().min(32),
  API_KEY: z.string().startsWith('sk-'),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
});

export const env = envSchema.parse(process.env);

// 使用
console.log(env.DATABASE_URL);  // 类型安全
```

#### 验证方法
```bash
# 1. 尝试提交包含密钥的文件
echo "API_KEY=sk-test123" > test.env
git add test.env
git commit -m "test"  # 应该被 git-secrets 阻止

# 2. 检查 GitHub 仓库
# 确认 .env 文件不存在于远程仓库

# 3. 使用 trufflehog 扫描
trufflehog git file://. --only-verified
# 应该无输出（或只有已知的误报）
```

---

### 检查项 2: 依赖安全扫描

#### 一句话风险
你使用的第三方库存在已知漏洞（Log4j级别），攻击者无需账号即可远程执行任意代码。

#### 一分钟识别
- [ ] 从未运行过 `npm audit` 或 `pip-audit`
- [ ] `package.json` / `requirements.txt` 中存在过时依赖
- [ ] 使用了未经维护的包（>1年无更新）
- [ ] 直接使用 `latest` 版本号
→ 勾选≥1项，即需关注此风险

#### 一句话防御
每次部署前运行依赖安全扫描，定期更新依赖，锁定版本号。

#### 快速行动清单
1. [ ] 立即运行 `npm audit fix` 或 `pip-audit -u`（5分钟）
2. [ ] 设置 CI/CD 自动扫描（10分钟）
3. [ ] 订阅安全公告（GitHub Dependabot）（5分钟）

#### 推荐工具
- 免费：`npm audit` - Node.js 内置
- 免费：`pip-audit` - Python 依赖扫描
- 免费：`trivy` - 通用漏洞扫描
- 免费：GitHub Dependabot - 自动 PR 更新

#### 代码示例

```bash
# Node.js: 依赖安全检查
npm audit              # 检查漏洞
npm audit fix          # 自动修复
npm audit fix --force  # 强制修复（可能有破坏性变更）

# Python: 依赖安全检查
pip install pip-audit
pip-audit              # 检查漏洞
pip-audit -u           # 查看可更新版本

# 通用: Trivy 扫描
brew install trivy
trivy fs .             # 扫描整个项目
trivy fs --severity HIGH,CRITICAL .  # 只显示高危
```

```yaml
# GitHub Actions: 自动依赖扫描
name: Security Audit
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * *'  # 每天运行

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Node.js Audit
        run: |
          npm audit --audit-level=high
          
      - name: Python Audit
        run: |
          pip install pip-audit
          pip-audit --skip-editable
          
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          severity: 'HIGH,CRITICAL'
```

```json
// package.json: 锁定版本 + Dependabot 配置
{
  "dependencies": {
    "express": "4.18.2",      // ✅ 锁定版本
    "lodash": "^4.17.21"       // ⚠️ 允许小版本更新
  },
  "scripts": {
    "audit": "npm audit --audit-level=high",
    "audit:fix": "npm audit fix"
  }
}
```

```toml
# pyproject.toml: Dependabot 配置
[tool.dependabot]
update_schedule = "weekly"

# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

#### 验证方法
```bash
# 1. 检查是否存在高危漏洞
npm audit --json | jq '.metadata.vulnerabilities.high, .metadata.vulnerabilities.critical'
# 输出应该为 0

# 2. 运行 Trivy 扫描
trivy fs --severity HIGH,CRITICAL .
# 应该无输出（或只有已知的误报）

# 3. 检查 Dependabot 是否启用
# GitHub → Insights → Dependency graph → Dependabot
```

---

### 检查项 3: 数据库连接安全

#### 一句话风险
数据库使用默认端口、弱密码、公网暴露，攻击者暴力破解后拖库，用户数据全部泄露。

#### 一分钟识别
- [ ] 数据库端口直接暴露在公网（如 3306、5432、27017）
- [ ] 使用默认用户名（root、admin）或弱密码
- [ ] 数据库连接字符串包含明文密码
- [ ] 未使用 SSL/TLS 加密连接
→ 勾选≥1项，即需关注此风险

#### 一句话防御
数据库禁止公网访问，使用强密码 + SSL 连接，连接字符串通过环境变量注入。

#### 快速行动清单
1. [ ] 检查云服务商安全组设置，关闭公网访问（5分钟）
2. [ ] 修改默认密码为强密码（5分钟）
3. [ ] 启用 SSL 连接（5分钟）

#### 推荐工具
- 免费：云服务商安全组配置
- 免费：`sslmode=require`（PostgreSQL）
- 免费：`requireSSL=true`（MySQL）

#### 代码示例

```bash
# 安全组配置示例（AWS EC2）
# 只允许应用服务器 IP 访问数据库端口
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 5432 \
  --source-group sg-app-server  # 只允许应用服务器访问

# 或只允许特定 IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 5432 \
  --cidr 10.0.1.0/24  # 内网 IP 段
```

```python
# Python: 安全数据库连接
import os
from sqlalchemy import create_engine

# ✅ 从环境变量读取连接字符串
DATABASE_URL = os.getenv('DATABASE_URL')

# ✅ 强制 SSL 连接
if DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql://', 1)
    if '?' in DATABASE_URL:
        DATABASE_URL += '&sslmode=require'
    else:
        DATABASE_URL += '?sslmode=require'

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # 连接健康检查
    pool_recycle=3600,       # 连接回收时间
)

# ✅ 密码复杂度检查
def check_password_strength(password: str) -> bool:
    """检查密码强度"""
    import re
    if len(password) < 16:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*]', password):
        return False
    return True

# 生成强密码
import secrets
import string
def generate_db_password(length=32):
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(secrets.choice(chars) for _ in range(length))
```

```typescript
// Node.js: 安全数据库连接
import { Pool } from 'pg';
import 'dotenv/config';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.NODE_ENV === 'production' 
    ? { rejectUnauthorized: true }  // 生产环境强制 SSL
    : false,
  // 连接池配置
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// 健康检查
pool.on('error', (err) => {
  console.error('数据库连接错误:', err);
});

// 查询超时保护
async function query(text: string, params: any[], timeout = 5000) {
  const result = await pool.query({
    text,
    values: params,
    timeout,  // 查询超时
  });
  return result.rows;
}
```

```bash
# PostgreSQL: 安全配置
# postgresql.conf
listen_addresses = 'localhost'  # 只监听本地
ssl = on                        # 启用 SSL
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'

# pg_hba.conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     scram-sha-256
host    all             all             127.0.0.1/32            scram-sha-256
hostssl all             all             10.0.0.0/8              scram-sha-256  # 内网 SSL
# 拒绝所有其他连接
host    all             all             0.0.0.0/0               reject
```

#### 验证方法
```bash
# 1. 测试公网是否可访问
# 从外部网络执行：
nc -zv your-db-public-ip 5432
# 应该超时或拒绝连接

# 2. 测试 SSL 连接
psql "postgresql://user:pass@host:5432/db?sslmode=require"
# 应该成功连接

# 3. 检查密码强度
# 手动检查密码长度 >= 16，包含大小写数字特殊字符
```

---

### 检查项 4: API密钥管理

#### 一句话风险
你的 OpenAI API Key 硬编码在前端代码中，被恶意用户获取后滥用，一个月产生 $10,000+ 账单。

#### 一分钟识别
- [ ] API Key 出现在前端代码（JS、React、Vue）
- [ ] API Key 出现在移动应用代码中
- [ ] API Key 出现在公开的 GitHub 仓库
- [ ] 未对 API Key 设置使用限制（IP、域名、额度）
→ 勾选≥1项，即需关注此风险

#### 一句话防御
所有 API Key 只在后端使用，前端通过后端代理调用，为每个 API Key 设置限额和域名限制。

#### 快速行动清单
1. [ ] 立即撤销所有泄露的 API Key（2分钟）
2. [ ] 创建新的 API Key 并设置限制（5分钟）
3. [ ] 搭建后端代理层（10分钟）

#### 推荐工具
- 免费：各服务商的密钥管理面板
- 免费额度：Vercel / Netlify 环境变量

#### 代码示例

```javascript
// ❌ 错误做法：前端直接使用 API Key
const openai = new OpenAI({
  apiKey: 'sk-xxxxxx',  // 暴露在前端代码中
});

// ✅ 正确做法：前端调用后端代理
async function callOpenAI(prompt) {
  const response = await fetch('/api/openai', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });
  return response.json();
}
```

```typescript
// Next.js API Route: 后端代理
import OpenAI from 'openai';
import { NextRequest, NextResponse } from 'next/server';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,  // 只在后端使用
});

export async function POST(request: NextRequest) {
  // 1. 用户认证检查
  const userId = request.headers.get('x-user-id');
  if (!userId) {
    return NextResponse.json({ error: '未授权' }, { status: 401 });
  }

  // 2. 速率限制
  const rateLimitKey = `openai:${userId}`;
  const requests = await redis.incr(rateLimitKey);
  if (requests === 1) {
    await redis.expire(rateLimitKey, 60);  // 1分钟窗口
  }
  if (requests > 10) {
    return NextResponse.json({ error: '请求过于频繁' }, { status: 429 });
  }

  // 3. 调用 OpenAI
  const { prompt } = await request.json();
  
  // 输入验证
  if (!prompt || prompt.length > 1000) {
    return NextResponse.json({ error: '无效输入' }, { status: 400 });
  }

  try {
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [{ role: 'user', content: prompt }],
      max_tokens: 500,  // 限制输出长度
    });

    // 4. 记录使用量
    await logAPIUsage(userId, completion.usage);

    return NextResponse.json({
      result: completion.choices[0].message.content,
    });
  } catch (error) {
    console.error('OpenAI API 错误:', error);
    return NextResponse.json({ error: '服务暂时不可用' }, { status: 500 });
  }
}
```

```bash
# 各服务商 API Key 限制配置

# OpenAI: 设置使用限制
# Dashboard → API Keys → Create new secret key
# 勾选 "Restrict to specific domains" 或设置月度限额

# Stripe: 设置密钥权限
# Dashboard → Developers → API Keys
# 创建受限密钥，只授予必要权限（如只读、只创建支付）

# AWS IAM: 最小权限原则
aws iam create-user --user-name my-app
aws iam attach-user-policy --user-name my-app \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess  # 只授予 S3 只读
```

#### 验证方法
```bash
# 1. 检查前端代码是否包含 API Key
grep -r "sk-\|AIza\|ghp_\|AKIA" ./public ./src --include="*.js" --include="*.ts"
# 应该无输出

# 2. 检查 API Key 限制是否生效
# 尝试从不同域名或 IP 调用 API
curl -H "Authorization: Bearer sk-xxx" https://api.openai.com/v1/models
# 应该返回 401 或 403

# 3. 检查账单告警
# 确认服务商账单告警已启用
```

---

### 检查项 5: HTTPS强制配置

#### 一句话风险
你的网站只支持 HTTP，用户登录密码被中间人攻击者截获，账号被盗。

#### 一分钟识别
- [ ] 访问 `http://yourdomain.com` 未自动跳转到 HTTPS
- [ ] 未配置 HSTS 头
- [ ] 混合内容警告（HTTPS 页面加载 HTTP 资源）
- [ ] SSL 证书已过期或即将过期
→ 勾选≥1项，即需关注此风险

#### 一句话防御
使用 Let's Encrypt 免费证书，配置 HSTS 强制 HTTPS，设置自动续期。

#### 快速行动清单
1. [ ] 申请 Let's Encrypt 免费证书（5分钟）
2. [ ] 配置 Nginx 强制 HTTPS（5分钟）
3. [ ] 设置自动续期（5分钟）

#### 推荐工具
- 免费：Let's Encrypt
- 免费：Certbot
- 免费额度：Vercel / Netlify / Cloudflare（自动 HTTPS）

#### 代码示例

```bash
# 使用 Certbot 申请 Let's Encrypt 证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期测试
sudo certbot renew --dry-run

# Certbot 会自动配置 Nginx，但也可以手动配置
```

```nginx
# Nginx: 强制 HTTPS 配置
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 强制跳转 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    
    # HSTS: 强制浏览器使用 HTTPS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    
    # 防止点击劫持
    add_header X-Frame-Options "SAMEORIGIN" always;
    
    # 防止 MIME 类型嗅探
    add_header X-Content-Type-Options "nosniff" always;
    
    # 其他安全头
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # 内容安全策略（根据实际情况调整）
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```javascript
// Express: 强制 HTTPS
app.use((req, res, next) => {
  if (req.headers['x-forwarded-proto'] !== 'https' && process.env.NODE_ENV === 'production') {
    return res.redirect(301, `https://${req.headers.host}${req.url}`);
  }
  next();
});

// 或使用 helmet 添加安全头
import helmet from 'helmet';
app.use(helmet());

// HSTS 配置
app.use(
  helmet.hsts({
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  })
);
```

```yaml
# Vercel: 自动 HTTPS + 安全头配置
# vercel.json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
      ]
    }
  ]
}
```

#### 验证方法
```bash
# 1. 测试 HTTP 跳转
curl -I http://yourdomain.com
# 应该返回 301 或 302 跳转到 HTTPS

# 2. 测试 HSTS 头
curl -I https://yourdomain.com | grep -i "strict-transport-security"
# 应该输出: strict-transport-security: max-age=31536000; includeSubDomains; preload

# 3. SSL 实验室测试
# 访问: https://www.ssllabs.com/ssltest/analyze.html?d=yourdomain.com
# 应该获得 A 或 A+ 评级

# 4. 检查证书有效期
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

### 检查项 6: 认证安全加固

#### 一句话风险
用户密码使用明文存储或弱哈希（MD5），数据库泄露后所有用户密码被破解，攻击者尝试撞库其他网站。

#### 一分钟识别
- [ ] 密码使用 MD5、SHA1 哈希
- [ ] 密码使用可逆加密（AES）存储
- [ ] 密码未加盐（salt）
- [ ] 允许弱密码（<8位、纯数字、常见密码）
→ 勾选≥1项，即需关注此风险

#### 一句话防御
使用 bcrypt 或 argon2 哈希密码，强制最小12位密码，启用双因素认证。

#### 快速行动清单
1. [ ] 检查当前密码存储方式（5分钟）
2. [ ] 升级到 bcrypt/argon2（15分钟）
3. [ ] 添加密码强度验证（5分钟）

#### 推荐工具
- 免费：`bcrypt`（所有语言都有实现）
- 免费：`argon2`（更安全，但需要系统依赖）
- 免费：`zxcvbn`（密码强度检测）

#### 代码示例

```python
# Python: bcrypt 密码哈希
import bcrypt
from password_strength import PasswordPolicy

# 密码强度策略
policy = PasswordPolicy.from_names(
    length=12,        # 最小长度 12
    uppercase=1,      # 至少 1 个大写字母
    numbers=1,        # 至少 1 个数字
    special=1,        # 至少 1 个特殊字符
    strength=0.66,    # 综合强度分数
)

def validate_password(password: str) -> tuple[bool, str]:
    """验证密码强度"""
    result = policy.test(password)
    if result:
        return False, f"密码强度不足: {result}"
    return True, "密码强度合格"

def hash_password(password: str) -> str:
    """哈希密码"""
    # bcrypt 自动加盐，cost factor 12（推荐 10-12）
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# 使用示例
password = "MySecurePassword123!"
valid, msg = validate_password(password)
if valid:
    hashed = hash_password(password)
    print(f"哈希后: {hashed}")
    
    # 验证
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)
```

```typescript
// Node.js: bcrypt 密码哈希
import bcrypt from 'bcrypt';
import { z } from 'zod';

const SALT_ROUNDS = 12;  // 推荐 10-12

// 密码验证 Schema
const passwordSchema = z.string()
  .min(12, '密码至少 12 位')
  .regex(/[A-Z]/, '密码必须包含大写字母')
  .regex(/[a-z]/, '密码必须包含小写字母')
  .regex(/[0-9]/, '密码必须包含数字')
  .regex(/[!@#$%^&*]/, '密码必须包含特殊字符');

export async function validatePassword(password: string): Promise<string | null> {
  try {
    passwordSchema.parse(password);
    return null;  // 验证通过
  } catch (e) {
    return e.errors?.[0]?.message || '密码格式错误';
  }
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

export async function verifyPassword(
  password: string,
  hashedPassword: string
): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword);
}

// 使用示例
async function register(email: string, password: string) {
  // 1. 验证密码强度
  const error = await validatePassword(password);
  if (error) {
    throw new Error(error);
  }
  
  // 2. 哈希密码
  const hashedPassword = await hashPassword(password);
  
  // 3. 存储到数据库
  await db.insertUser({
    email,
    password: hashedPassword,  // 存储哈希值
    created_at: new Date(),
  });
}

async function login(email: string, password: string) {
  const user = await db.findUserByEmail(email);
  if (!user) {
    throw new Error('邮箱或密码错误');
  }
  
  const valid = await verifyPassword(password, user.password);
  if (!valid) {
    // 记录失败尝试
    await db.recordFailedLogin(user.id);
    throw new Error('邮箱或密码错误');
  }
  
  // 检查是否需要重置密码（如果从旧哈希升级）
  if (user.password.startsWith('$2a$') && user.password.startsWith('$2b$')) {
    // 重新哈希（升级 cost factor）
    const newHash = await hashPassword(password);
    await db.updateUserPassword(user.id, newHash);
  }
  
  return generateToken(user);
}
```

```typescript
// Express: 认证中间件
import { Request, Response, NextFunction } from 'express';

declare global {
  namespace Express {
    interface Request {
      userId?: string;
    }
  }
}

// 登录限流
const loginAttempts = new Map<string, { count: number; lockUntil: number }>();

function checkLoginLimit(email: string): { allowed: boolean; waitTime?: number } {
  const attempt = loginAttempts.get(email);
  if (!attempt) {
    return { allowed: true };
  }
  
  if (attempt.lockUntil > Date.now()) {
    return { 
      allowed: false, 
      waitTime: Math.ceil((attempt.lockUntil - Date.now()) / 1000) 
    };
  }
  
  return { allowed: true };
}

function recordLoginFailure(email: string) {
  const attempt = loginAttempts.get(email) || { count: 0, lockUntil: 0 };
  attempt.count++;
  
  // 5 次失败后锁定 15 分钟
  if (attempt.count >= 5) {
    attempt.lockUntil = Date.now() + 15 * 60 * 1000;
    attempt.count = 0;
  }
  
  loginAttempts.set(email, attempt);
}

// 认证中间件
export function authMiddleware(req: Request, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    return res.status(401).json({ error: '未提供认证令牌' });
  }
  
  try {
    const decoded = verifyToken(token);
    req.userId = decoded.userId;
    next();
  } catch (error) {
    return res.status(401).json({ error: '令牌无效或已过期' });
  }
}
```

#### 验证方法
```python
# Python: 验证密码哈希是否安全
import bcrypt

# 测试哈希格式
sample_hash = "$2b$12$N9qo8uLOickgx2ZMRZoMy.Mrq7j7QZ7QZ7j7j7j7j7j7j7j7j7j7j7"
# bcrypt 哈希格式: $2b$<cost>$<22字符salt><31字符hash>
assert sample_hash.startswith('$2b$') or sample_hash.startswith('$2a$')

# 测试 cost factor
cost = int(sample_hash.split('$')[2])
assert cost >= 10, f"Cost factor {cost} 太低，建议 >= 10"
```

```bash
# 使用 hashcat 测试密码哈希强度（仅用于教育目的）
# 如果短时间内能破解，说明 cost factor 太低或密码太弱

# Node.js: 检查所有用户密码哈希格式
node -e "
const db = require('./db');
(async () => {
  const users = await db.query('SELECT id, password FROM users');
  for (const user of users) {
    if (!user.password.startsWith('\$2b\$') && !user.password.startsWith('\$2a\$')) {
      console.log(\`用户 \${user.id} 使用不安全的密码哈希格式\`);
    }
  }
})();
"
```

---

### 检查项 7: 日志安全脱敏

#### 一句话风险
你的错误日志包含完整的用户手机号、密码、信用卡号，日志文件泄露后违反 GDPR，面临巨额罚款。

#### 一分钟识别
- [ ] 日志中包含用户密码、密钥、Token
- [ ] 日志中包含完整手机号、身份证号、银行卡号
- [ ] 日志文件权限过于宽松（chmod 644）
- [ ] 日志无保留期限，无限增长
→ 勾选≥1项，即需关注此风险

#### 一句话防御
日志输出前自动脱敏敏感字段，设置日志保留期限和访问权限。

#### 快速行动清单
1. [ ] 审查现有日志内容，找出敏感数据（5分钟）
2. [ ] 实现日志脱敏中间件（10分钟）
3. [ ] 配置日志轮转和保留策略（5分钟）

#### 推荐工具
- 免费：自定义脱敏函数
- 免费：`winston`（Node.js）+ 自定义 format
- 免费：`logrotate`（系统级日志轮转）

#### 代码示例

```python
# Python: 日志脱敏
import re
import logging
from typing import Any

# 敏感字段正则
SENSITIVE_PATTERNS = {
    'phone': re.compile(r'1[3-9]\d{9}'),
    'id_card': re.compile(r'\d{17}[\dXx]'),
    'bank_card': re.compile(r'\d{15,19}'),
    'email': re.compile(r'[\w.-]+@[\w.-]+\.\w+'),
}

# 敏感字段名（需要脱敏的字段）
SENSITIVE_FIELDS = {
    'password', 'passwd', 'pwd',
    'token', 'access_token', 'refresh_token',
    'secret', 'api_key', 'apikey',
    'credit_card', 'card_number',
    'ssn', 'id_number',
}

def mask_phone(phone: str) -> str:
    """手机号脱敏: 138****8888"""
    return phone[:3] + '****' + phone[7:] if len(phone) == 11 else '***'

def mask_id_card(id_card: str) -> str:
    """身份证号脱敏: 110***********1234"""
    return id_card[:3] + '*' * 11 + id_card[14:] if len(id_card) == 18 else '***'

def mask_bank_card(card: str) -> str:
    """银行卡脱敏: **** **** **** 1234"""
    return '**** **** **** ' + card[-4:] if len(card) >= 4 else '***'

def mask_email(email: str) -> str:
    """邮箱脱敏: a***@example.com"""
    parts = email.split('@')
    if len(parts) == 2:
        return parts[0][0] + '***@' + parts[1]
    return '***'

def mask_sensitive_data(data: Any) -> Any:
    """递归脱敏敏感数据"""
    if isinstance(data, dict):
        return {
            k: '***' if k.lower() in SENSITIVE_FIELDS else mask_sensitive_data(v)
            for k, v in data.items()
        }
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    elif isinstance(data, str):
        # 脱敏手机号
        data = SENSITIVE_PATTERNS['phone'].sub(mask_phone, data)
        # 脱敏身份证
        data = SENSITIVE_PATTERNS['id_card'].sub(mask_id_card, data)
        # 脱敏银行卡
        data = SENSITIVE_PATTERNS['bank_card'].sub(mask_bank_card, data)
        # 脱敏邮箱
        data = SENSITIVE_PATTERNS['email'].sub(mask_email, data)
        return data
    else:
        return data

class SensitiveDataFilter(logging.Filter):
    """日志敏感数据过滤器"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        # 脱敏日志消息
        if isinstance(record.msg, str):
            record.msg = mask_sensitive_data(record.msg)
        elif isinstance(record.msg, dict):
            record.msg = mask_sensitive_data(record.msg)
        return True

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(),
    ],
)

# 添加脱敏过滤器
for handler in logging.root.handlers:
    handler.addFilter(SensitiveDataFilter())

# 使用示例
logger = logging.getLogger(__name__)

# 自动脱敏
logger.info(f"用户登录: 手机号=13812345678")
# 输出: 用户登录: 手机号=138****5678

logger.info({
    "user": "张三",
    "phone": "13812345678",
    "password": "MySecretPassword123",  # 敏感字段自动替换为 ***
    "id_card": "110101199001011234",
})
# 输出: {'user': '张三', 'phone': '138****5678', 'password': '***', 'id_card': '110***********1234'}
```

```typescript
// Node.js: Winston 日志脱敏
import winston from 'winston';
import { format } from 'winston';

// 敏感字段正则
const SENSITIVE_PATTERNS = {
  phone: /1[3-9]\d{9}/g,
  idCard: /\d{17}[\dXx]/g,
  bankCard: /\d{15,19}/g,
  email: /[\w.-]+@[\w.-]+\.\w+/g,
};

// 敏感字段名
const SENSITIVE_FIELDS = new Set([
  'password', 'passwd', 'pwd',
  'token', 'accessToken', 'refreshToken',
  'secret', 'apiKey', 'apikey',
  'creditCard', 'cardNumber',
  'ssn', 'idNumber',
]);

// 脱敏函数
function maskValue(value: string): string {
  // 手机号: 138****5678
  value = value.replace(SENSITIVE_PATTERNS.phone, (m) => 
    m.slice(0, 3) + '****' + m.slice(7)
  );
  // 身份证: 110***********1234
  value = value.replace(SENSITIVE_PATTERNS.idCard, (m) => 
    m.slice(0, 3) + '*'.repeat(11) + m.slice(14)
  );
  // 银行卡: **** **** **** 1234
  value = value.replace(SENSITIVE_PATTERNS.bankCard, (m) => 
    '**** **** **** ' + m.slice(-4)
  );
  // 邮箱: a***@example.com
  value = value.replace(SENSITIVE_PATTERNS.email, (m) => {
    const [local, domain] = m.split('@');
    return local[0] + '***@' + domain;
  });
  return value;
}

function maskObject(obj: any): any {
  if (obj === null || obj === undefined) return obj;
  
  if (typeof obj === 'string') {
    return maskValue(obj);
  }
  
  if (Array.isArray(obj)) {
    return obj.map(maskObject);
  }
  
  if (typeof obj === 'object') {
    const masked: any = {};
    for (const [key, value] of Object.entries(obj)) {
      if (SENSITIVE_FIELDS.has(key.toLowerCase())) {
        masked[key] = '***';
      } else {
        masked[key] = maskObject(value);
      }
    }
    return masked;
  }
  
  return obj;
}

// 自定义格式
const sensitiveDataFormat = format((info) => {
  info.message = maskObject(info.message);
  return info;
});

// 创建 logger
const logger = winston.createLogger({
  level: 'info',
  format: format.combine(
    format.timestamp(),
    sensitiveDataFormat(),
    format.json(),
  ),
  transports: [
    new winston.transports.File({ 
      filename: 'error.log', 
      level: 'error',
      maxsize: 5242880,  // 5MB
      maxFiles: 5,
    }),
    new winston.transports.File({ 
      filename: 'combined.log',
      maxsize: 5242880,
      maxFiles: 10,
    }),
  ],
});

// 开发环境输出到控制台
if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: format.combine(
      format.colorize(),
      format.simple(),
    ),
  }));
}

export { logger };

// 使用示例
logger.info('用户登录', { 
  userId: '123',
  phone: '13812345678',
  password: 'secret123',  // 自动脱敏为 ***
});
```

```bash
# logrotate 配置: 日志轮转
# /etc/logrotate.d/your-app

/var/log/your-app/*.log {
    daily                    # 每天轮转
    rotate 30                # 保留 30 天
    compress                 # 压缩旧日志
    delaycompress            # 延迟压缩
    missingok                # 文件不存在不报错
    notifempty               # 空文件不轮转
    create 0640 app app     # 新文件权限
    sharedscripts
    postrotate
        # 轮转后执行（如通知应用重新打开日志文件）
        systemctl reload your-app
    endscript
}

# 测试配置
logrotate -d /etc/logrotate.d/your-app

# 手动执行
logrotate -f /etc/logrotate.d/your-app
```

#### 验证方法
```bash
# 1. 检查日志是否包含敏感数据
grep -r "password\|token\|secret" /var/log/your-app/
# 应该只看到脱敏后的 ***

# 2. 检查日志文件权限
ls -la /var/log/your-app/
# 应该是 640 或更严格

# 3. 测试脱敏效果
# Python
python -c "
from logging_utils import mask_sensitive_data
print(mask_sensitive_data({'phone': '13812345678', 'password': 'secret'}))
# 应该输出: {'phone': '138****5678', 'password': '***'}
"

# 4. 检查日志保留策略
logrotate -d /etc/logrotate.d/your-app | grep rotate
# 应该显示保留天数
```

---

### 检查项 8: 备份策略

#### 一句话风险
数据库服务器磁盘故障，无备份可恢复，所有用户数据永久丢失，业务倒闭。

#### 一分钟识别
- [ ] 数据库从未备份
- [ ] 备份文件存储在同一服务器
- [ ] 备份未加密
- [ ] 从未测试过恢复流程
→ 勾选≥1项，即需关注此风险

#### 一句话防御
每日自动备份到云存储，保留30天，加密存储，每周测试恢复。

#### 快速行动清单
1. [ ] 配置数据库自动备份（10分钟）
2. [ ] 设置备份上传到云存储（5分钟）
3. [ ] 编写恢复脚本并测试（10分钟）

#### 推荐工具
- 免费：PostgreSQL `pg_dump` + cron
- 免费额度：AWS S3（5GB）、Google Cloud Storage（5GB）
- 免费：Backblaze B2（10GB）

#### 代码示例

```bash
#!/bin/bash
# PostgreSQL 自动备份脚本
# 文件: /usr/local/bin/backup-postgres.sh

set -e

# 配置
DB_NAME="myapp"
DB_USER="postgres"
BACKUP_DIR="/var/backups/postgres"
S3_BUCKET="s3://my-backups/postgres"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份文件名（带时间戳）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# 执行备份
echo "开始备份数据库: $DB_NAME"
pg_dump -U "$DB_USER" -d "$DB_NAME" | gzip > "$BACKUP_FILE"

# 加密备份（使用 GPG）
echo "加密备份文件"
gpg --batch --yes --passphrase "$BACKUP_ENCRYPTION_KEY" \
    --symmetric --cipher-algo AES256 "$BACKUP_FILE"
rm "$BACKUP_FILE"  # 删除未加密文件

# 上传到 S3
echo "上传到云存储: $S3_BUCKET"
aws s3 cp "${BACKUP_FILE}.gpg" "$S3_BUCKET/" \
    --storage-class STANDARD_IA  # 低频访问存储，节省成本

# 清理本地旧备份
find "$BACKUP_DIR" -name "*.sql.gz.gpg" -mtime +$RETENTION_DAYS -delete

# 清理 S3 旧备份
aws s3 ls "$S3_BUCKET/" | while read -r line; do
    file_date=$(echo "$line" | awk '{print $1" "$2}')
    file_name=$(echo "$line" | awk '{print $4}')
    
    if [[ $(date -d "$file_date" +%s) -lt $(date -d "-$RETENTION_DAYS days" +%s) ]]; then
        aws s3 rm "$S3_BUCKET/$file_name"
    fi
done

echo "备份完成: ${BACKUP_FILE}.gpg"

# 验证备份完整性
echo "验证备份..."
gunzip -c "${BACKUP_FILE}.gpg" | head -n 1 > /dev/null && echo "备份文件有效"
```

```bash
# 恢复脚本
#!/bin/bash
# 文件: /usr/local/bin/restore-postgres.sh

set -e

BACKUP_FILE="$1"
DB_NAME="myapp"
DB_USER="postgres"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file.gpg>"
    echo "可用的备份文件:"
    aws s3 ls s3://my-backups/postgres/
    exit 1
fi

# 从 S3 下载（如果是远程文件）
if [[ "$BACKUP_FILE" == s3://* ]]; then
    echo "从 S3 下载备份..."
    aws s3 cp "$BACKUP_FILE" /tmp/restore.sql.gz.gpg
    BACKUP_FILE="/tmp/restore.sql.gz.gpg"
fi

# 解密
echo "解密备份文件..."
gpg --batch --yes --passphrase "$BACKUP_ENCRYPTION_KEY" \
    --decrypt "$BACKUP_FILE" | gunzip > /tmp/restore.sql

# 确认恢复
read -p "这将覆盖数据库 $DB_NAME，确认吗？(yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "取消恢复"
    exit 1
fi

# 恢复数据库
echo "恢复数据库..."
psql -U "$DB_USER" -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME};"
psql -U "$DB_USER" -d postgres -c "CREATE DATABASE ${DB_NAME};"
psql -U "$DB_USER" -d "$DB_NAME" -f /tmp/restore.sql

# 清理
rm /tmp/restore.sql /tmp/restore.sql.gz.gpg 2>/dev/null || true

echo "恢复完成"
```

```bash
# cron 配置: 每天凌晨 2 点备份
# crontab -e
0 2 * * * /usr/local/bin/backup-postgres.sh >> /var/log/backup.log 2>&1

# 每周日凌晨 3 点测试恢复（可选）
0 3 * * 0 /usr/local/bin/test-restore.sh >> /var/log/backup-test.log 2>&1
```

```yaml
# GitHub Actions: 自动备份到云存储
name: Database Backup
on:
  schedule:
    - cron: '0 2 * * *'  # 每天 UTC 2:00
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - name: Install PostgreSQL client
        run: sudo apt-get install -y postgresql-client
        
      - name: Backup database
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          S3_BUCKET: s3://my-backups/postgres
        run: |
          TIMESTAMP=$(date +%Y%m%d_%H%M%S)
          pg_dump "$DATABASE_URL" | gzip > backup.sql.gz
          
          # 加密
          gpg --batch --yes --passphrase "${{ secrets.BACKUP_ENCRYPTION_KEY }}" \
              --symmetric --cipher-algo AES256 backup.sql.gz
          
          # 上传
          aws s3 cp backup.sql.gz.gpg "$S3_BUCKET/backup_${TIMESTAMP}.sql.gz.gpg"
          
      - name: Cleanup old backups
        run: |
          # 清理 30 天前的备份
          aws s3 ls s3://my-backups/postgres/ | while read -r line; do
            file_date=$(echo "$line" | awk '{print $1}')
            file_name=$(echo "$line" | awk '{print $4}')
            
            if [[ $(date -d "$file_date" +%s) -lt $(date -d "-30 days" +%s) ]]; then
              aws s3 rm "s3://my-backups/postgres/$file_name"
            fi
          done
```

#### 验证方法
```bash
# 1. 验证备份文件存在
ls -lh /var/backups/postgres/
aws s3 ls s3://my-backups/postgres/

# 2. 验证备份文件可恢复
# 创建测试数据库
psql -c "CREATE DATABASE test_restore;"
# 恢复
gunzip -c /var/backups/postgres/latest.sql.gz | psql test_restore
# 验证数据
psql test_restore -c "SELECT COUNT(*) FROM users;"

# 3. 验证加密
file /var/backups/postgres/latest.sql.gz.gpg
# 应该显示: GPG symmetrically encrypted data

# 4. 模拟灾难恢复
# 在测试环境中完整执行恢复流程
/usr/local/bin/restore-postgres.sh s3://my-backups/postgres/latest.sql.gz.gpg
```

---

### 检查项 9: 监控告警

#### 一句话风险
你的网站宕机 4 小时，你却还在睡觉，用户流失，收入损失。

#### 一分钟识别
- [ ] 无任何监控工具
- [ ] 依赖用户反馈发现问题
- [ ] 无告警通知渠道
- [ ] 服务器资源（CPU、内存、磁盘）无监控
→ 勾选≥1项，即需关注此风险

#### 一句话防御
使用免费监控服务（UptimeRobot），设置5分钟检查间隔，邮件/Slack通知。

#### 快速行动清单
1. [ ] 注册 UptimeRobot 免费版（5分钟）
2. [ ] 添加网站监控（5分钟）
3. [ ] 配置告警通知（5分钟）

#### 推荐工具
- 免费：UptimeRobot（50个监控，5分钟间隔）
- 免费：Better Uptime（10个监控）
- 免费额度：Sentry（5K错误/月）

#### 代码示例

```yaml
# UptimeRobot 监控配置
# 通过 Web UI 配置，但也可以用 API 自动化

# 监控项清单：
# 1. 首页可访问性 (HTTP 200)
# 2. API 健康检查 (/health)
# 3. 登录功能 (/login)
# 4. 支付页面 (/checkout)
```

```python
# Python: 健康检查端点
from fastapi import FastAPI, Response
import psutil
import asyncio

app = FastAPI()

@app.get("/health")
async def health_check():
    """基础健康检查"""
    return {"status": "ok"}

@app.get("/health/detailed")
async def detailed_health():
    """详细健康检查"""
    # CPU 使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    
    # 内存使用率
    memory = psutil.virtual_memory()
    
    # 磁盘使用率
    disk = psutil.disk_usage('/')
    
    # 检查阈值
    warnings = []
    if cpu_percent > 80:
        warnings.append(f"CPU 使用率过高: {cpu_percent}%")
    if memory.percent > 80:
        warnings.append(f"内存使用率过高: {memory.percent}%")
    if disk.percent > 80:
        warnings.append(f"磁盘使用率过高: {disk.percent}%")
    
    return {
        "status": "ok" if not warnings else "warning",
        "cpu": cpu_percent,
        "memory": {
            "total": memory.total,
            "used": memory.used,
            "percent": memory.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent,
        },
        "warnings": warnings,
    }

@app.get("/health/database")
async def database_health():
    """数据库连接检查"""
    try:
        # 执行简单查询
        result = await db.execute("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return Response(
            content={"status": "error", "message": str(e)},
            status_code=503,
        )
```

```typescript
// Node.js: 健康检查端点
import express from 'express';
import os from 'os';

const app = express();

// 基础健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 详细健康检查
app.get('/health/detailed', async (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: {
      total: os.totalmem(),
      free: os.freemem(),
      used: os.totalmem() - os.freemem(),
      percent: ((os.totalmem() - os.freemem()) / os.totalmem() * 100).toFixed(2),
    },
    cpu: {
      loadavg: os.loadavg(),
      cores: os.cpus().length,
    },
  };

  // 检查内存阈值
  if (health.memory.percent > 80) {
    health.status = 'warning';
    health.warnings = health.warnings || [];
    health.warnings.push(`内存使用率过高: ${health.memory.percent}%`);
  }

  res.json(health);
});

// 数据库健康检查
app.get('/health/database', async (req, res) => {
  try {
    await db.query('SELECT 1');
    res.json({ status: 'ok', database: 'connected' });
  } catch (error) {
    res.status(503).json({ status: 'error', message: error.message });
  }
});

// 依赖服务健康检查
app.get('/health/dependencies', async (req, res) => {
  const checks = {
    database: false,
    redis: false,
    external_api: false,
  };

  try {
    await db.query('SELECT 1');
    checks.database = true;
  } catch (e) {}

  try {
    await redis.ping();
    checks.redis = true;
  } catch (e) {}

  try {
    await fetch('https://api.example.com/health');
    checks.external_api = true;
  } catch (e) {}

  const allHealthy = Object.values(checks).every(Boolean);
  
  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ok' : 'degraded',
    checks,
  });
});

export { app };
```

```yaml
# Prometheus + Grafana 监控（可选，适合技术型开发者）
# docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:

# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['host.docker.internal:3000']
```

```bash
# 告警脚本: 发送 Slack 通知
#!/bin/bash
# 文件: /usr/local/bin/send-alert.sh

SLACK_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"
ALERT_TITLE="$1"
ALERT_MESSAGE="$2"

curl -X POST "$SLACK_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d "{
    \"text\": \"🚨 $ALERT_TITLE\",
    \"attachments\": [{
      \"color\": \"danger\",
      \"text\": \"$ALERT_MESSAGE\",
      \"footer\": \"$(hostname)\",
      \"ts\": $(date +%s)
    }]
  }"

# 使用示例
# ./send-alert.sh "服务器宕机" "API 服务无响应，请立即检查"
```

#### 验证方法
```bash
# 1. 验证健康检查端点
curl https://yourdomain.com/health
# 应该返回: {"status":"ok"}

curl https://yourdomain.com/health/detailed
# 应该返回详细状态，无 warning

# 2. 验证告警通知
# UptimeRobot: 暂时停止服务，确认收到邮件/Slack通知
# 或手动触发测试告警

# 3. 检查监控面板
# 登录 UptimeRobot 确认监控状态为绿色
# 检查响应时间趋势

# 4. 模拟故障
# 停止服务 5 分钟
sudo systemctl stop your-app
# 等待告警通知
# 恢复服务
sudo systemctl start your-app
# 确认收到恢复通知
```

---

### 检查项 10: 速率限制

#### 一句话风险
攻击者每秒发送 1000 次登录请求，暴力破解用户密码，你的服务器 CPU 飙升，正常用户无法访问。

#### 一分钟识别
- [ ] 登录接口无速率限制
- [ ] API 接口无速率限制
- [ ] 未区分 IP 和用户级别的限制
- [ ] 无验证码等防自动化措施
→ 勾选≥1项，即需关注此风险

#### 一句话防御
所有敏感接口添加速率限制，IP 级别 100请求/分钟，用户级别 10请求/分钟。

#### 快速行动清单
1. [ ] 为登录接口添加速率限制（10分钟）
2. [ ] 为 API 接口添加全局限制（5分钟）
3. [ ] 配置 Nginx 限流（可选，5分钟）

#### 推荐工具
- 免费：`express-rate-limit`（Node.js）
- 免费：`slowapi`（Python FastAPI）
- 免费：Nginx `limit_req`

#### 代码示例

```typescript
// Node.js: Express 速率限制
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redis } from './redis';

// 全局 API 限制
export const apiLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 分钟
  max: 100,             // 每个 IP 最多 100 请求
  message: { error: '请求过于频繁，请稍后再试' },
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args),
  }),
});

// 登录限制（更严格）
export const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 分钟
  max: 5,                     // 每个 IP 最多 5 次登录尝试
  message: { error: '登录尝试次数过多，请 15 分钟后再试' },
  skipSuccessfulRequests: true,  // 成功的请求不计入限制
});

// 注册限制
export const registerLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,  // 1 小时
  max: 3,                     // 每个 IP 最多 3 次注册
  message: { error: '注册请求过多，请 1 小时后再试' },
});

// 密码重置限制
export const passwordResetLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,  // 1 小时
  max: 3,                     // 每个 IP 最多 3 次
  message: { error: '密码重置请求过多，请 1 小时后再试' },
});

// 用户级别限制（针对已登录用户）
export const userLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 分钟
  max: 30,              // 每个用户最多 30 请求
  keyGenerator: (req) => req.userId || req.ip,  // 使用用户 ID 或 IP
  message: { error: '请求过于频繁' },
});

// 应用中间件
app.use('/api/', apiLimiter);          // 全局 API 限制
app.post('/login', loginLimiter, loginHandler);  // 登录限制
app.post('/register', registerLimiter, registerHandler);  // 注册限制
app.post('/password/reset', passwordResetLimiter, resetHandler);  // 密码重置限制
```

```python
# Python: FastAPI 速率限制
from fastapi import FastAPI, Request, HTTPException, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()

# 创建限制器
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 登录限制
@app.post("/login")
@limiter.limit("5/15minute")  # 15 分钟内最多 5 次
async def login(request: Request, credentials: LoginCredentials):
    # 登录逻辑
    pass

# 全局 API 限制
@app.get("/api/data")
@limiter.limit("100/minute")  # 每分钟最多 100 次
async def get_data(request: Request):
    # 业务逻辑
    pass

# 用户级别限制（需要认证）
async def get_current_user(request: Request) -> User:
    # 从 token 获取用户
    pass

@app.get("/api/user/resource")
@limiter.limit("30/minute", key_func=lambda: get_current_user)
async def get_user_resource(request: Request, user: User = Depends(get_current_user)):
    # 业务逻辑
    pass

# 自定义限流响应
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(
        status_code=429,
        detail="请求过于频繁，请稍后再试",
        headers={"Retry-After": exc.detail},
    )
```

```nginx
# Nginx: 请求速率限制
# 在 http 块中定义限制区域
http {
    # 基于 IP 的请求限制
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/m;
    
    # 登录限制
    server {
        location /login {
            limit_req zone=login_limit burst=5 nodelay;
            limit_req_status 429;
            
            proxy_pass http://localhost:3000;
        }
        
        # API 限制
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            limit_req_status 429;
            
            proxy_pass http://localhost:3000;
        }
    }
    
    # 自定义 429 响应
    error_page 429 = @too_many_requests;
    
    location @too_many_requests {
        default_type application/json;
        return 429 '{"error": "请求过于频繁，请稍后再试"}';
    }
}
```

```typescript
// 验证码集成（防止自动化攻击）
import svgCaptcha from 'svg-captcha';

// 生成验证码
app.get('/captcha', (req, res) => {
  const captcha = svgCaptcha.create({
    size: 4,
    noise: 2,
    color: true,
  });
  
  // 存储验证码到 session 或 Redis
  req.session.captcha = captcha.text;
  
  res.type('svg');
  res.status(200).send(captcha.data);
});

// 验证验证码
app.post('/login', loginLimiter, async (req, res) => {
  const { captcha, ...credentials } = req.body;
  
  // 验证码校验
  if (!captcha || captcha.toLowerCase() !== req.session.captcha?.toLowerCase()) {
    return res.status(400).json({ error: '验证码错误' });
  }
  
  // 清除验证码
  delete req.session.captcha;
  
  // 登录逻辑
  // ...
});
```

#### 验证方法
```bash
# 1. 测试 API 速率限制
for i in {1..110}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" https://yourdomain.com/api/data)
  echo "请求 $i: $response"
done
# 应该在第 101 个请求开始返回 429

# 2. 测试登录限制
for i in {1..10}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST https://yourdomain.com/login \
    -H "Content-Type: application/json" \
    -d '{"email":"test@test.com","password":"wrong"}')
  echo "登录尝试 $i: $response"
done
# 应该在第 6 次开始返回 429

# 3. 测试 Nginx 限制
ab -n 200 -c 10 https://yourdomain.com/api/data
# 查看失败请求数

# 4. 检查 Redis 中的限流键
redis-cli keys "*rate-limit*"
redis-cli get "rate-limit:127.0.0.1"
```

---

### 检查项 11: 输入验证

#### 一句话风险
用户在搜索框输入 `<script>alert('XSS')</script>`，你的页面弹出警告，存储型 XSS 可窃取所有用户 Cookie。

#### 一分钟识别
- [ ] 用户输入未做任何过滤直接输出
- [ ] SQL 查询使用字符串拼接
- [ ] 文件上传未验证类型和大小
- [ ] 用户输入未做长度限制
→ 勾选≥1项，即需关注此风险

#### 一句话防御
所有用户输入进行类型验证、长度限制、特殊字符转义，使用参数化查询防止 SQL 注入。

#### 快速行动清单
1. [ ] 为所有 API 添加输入验证（15分钟）
2. [ ] 使用 ORM/参数化查询（10分钟）
3. [ ] 添加 XSS 过滤（5分钟）

#### 推荐工具
- 免费：`zod`（TypeScript/Node.js）
- 免费：`pydantic`（Python）
- 免费：`DOMPurify`（前端 XSS 过滤）

#### 代码示例

```typescript
// TypeScript: Zod 输入验证
import { z } from 'zod';

// 用户注册 Schema
const registerSchema = z.object({
  email: z.string()
    .email('邮箱格式错误')
    .max(100, '邮箱过长'),
  
  password: z.string()
    .min(12, '密码至少 12 位')
    .max(100, '密码过长')
    .regex(/[A-Z]/, '密码必须包含大写字母')
    .regex(/[a-z]/, '密码必须包含小写字母')
    .regex(/[0-9]/, '密码必须包含数字')
    .regex(/[!@#$%^&*]/, '密码必须包含特殊字符'),
  
  username: z.string()
    .min(3, '用户名至少 3 位')
    .max(20, '用户名最多 20 位')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母数字下划线'),
  
  age: z.number()
    .int('年龄必须是整数')
    .min(0, '年龄不能为负')
    .max(150, '年龄不合理')
    .optional(),
  
  website: z.string()
    .url('网址格式错误')
    .optional()
    .or(z.undefined()),
});

// 使用验证中间件
import { Request, Response, NextFunction } from 'express';

function validateBody(schema: z.ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({
          error: '输入验证失败',
          details: error.errors.map(e => ({
            field: e.path.join('.'),
            message: e.message,
          })),
        });
      }
      next(error);
    }
  };
}

// 应用到路由
app.post('/register', 
  validateBody(registerSchema),
  async (req: Request, res: Response) => {
    // req.body 已经通过验证
    const { email, password, username } = req.body;
    
    // 业务逻辑...
  }
);
```

```python
# Python: Pydantic 输入验证
from pydantic import BaseModel, EmailStr, validator, Field, HttpUrl
from typing import Optional
import re

class UserRegister(BaseModel):
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=12, max_length=100)
    username: str = Field(..., min_length=3, max_length=20)
    age: Optional[int] = Field(None, ge=0, le=150)
    website: Optional[HttpUrl] = None
    
    @validator('password')
    def password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'[0-9]', v):
            raise ValueError('密码必须包含数字')
        if not re.search(r'[!@#$%^&*]', v):
            raise ValueError('密码必须包含特殊字符')
        return v
    
    @validator('username')
    def username_format(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母数字下划线')
        return v

# FastAPI 使用
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/register")
async def register(user: UserRegister):
    # user 已经通过验证
    # 类型安全访问
    email = user.email
    password = user.password
    
    # 业务逻辑...
    return {"message": "注册成功"}
```

```typescript
// SQL 注入防护：参数化查询
import { Pool } from 'pg';

const pool = new Pool();

// ❌ 错误做法：字符串拼接
async function getUserWrong(username: string) {
  const query = `SELECT * FROM users WHERE username = '${username}'`;
  // 输入: ' OR '1'='1
  // 实际执行: SELECT * FROM users WHERE username = '' OR '1'='1'
  // 返回所有用户！
  return pool.query(query);
}

// ✅ 正确做法：参数化查询
async function getUserCorrect(username: string) {
  const query = 'SELECT * FROM users WHERE username = $1';
  const result = await pool.query(query, [username]);
  return result.rows[0];
}

// ✅ 使用 ORM（Prisma）
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function getUserORM(username: string) {
  return prisma.user.findFirst({
    where: { username },
  });
}

// 批量插入也需要参数化
async function createUsers(users: Array<{ name: string; email: string }>) {
  const values = users.map((u, i) => `($${i * 2 + 1}, $${i * 2 + 2})`).join(',');
  const params = users.flatMap(u => [u.name, u.email]);
  
  const query = `
    INSERT INTO users (name, email)
    VALUES ${values}
    RETURNING id
  `;
  
  return pool.query(query, params);
}
```

```typescript
// XSS 防护：输出转义
import DOMPurify from 'dompurify';
import { JSDOM } from 'jsdom';

const window = new JSDOM('').window;
const purify = DOMPurify(window);

// 用户输入清洗
function sanitizeHtml(dirty: string): string {
  return purify.sanitize(dirty, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href'],
  });
}

// API 响应示例
app.get('/user/:id/profile', async (req, res) => {
  const user = await db.getUser(req.params.id);
  
  // 清洗用户生成的内容
  res.json({
    ...user,
    bio: sanitizeHtml(user.bio),  // 清洗 HTML
  });
});

// 前端 React 自动转义
function UserProfile({ user }) {
  return (
    <div>
      {/* React 默认转义 */}
      <p>{user.bio}</p>
      
      {/* 如需渲染 HTML，使用 dangerouslySetInnerHTML 前先清洗 */}
      <div dangerouslySetInnerHTML={{ 
        __html: DOMPurify.sanitize(user.bio) 
      }} />
    </div>
  );
}
```

```typescript
// 文件上传验证
import multer from 'multer';
import path from 'path';

// 允许的文件类型
const ALLOWED_MIME_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
];

const MAX_FILE_SIZE = 5 * 1024 * 1024;  // 5MB

const storage = multer.diskStorage({
  destination: './uploads/',
  filename: (req, file, cb) => {
    // 生成安全的文件名
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, `file-${uniqueSuffix}${ext}`);
  },
});

const upload = multer({
  storage,
  limits: {
    fileSize: MAX_FILE_SIZE,
    files: 1,
  },
  fileFilter: (req, file, cb) => {
    // 验证 MIME 类型
    if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
      return cb(new Error('不支持的文件类型'));
    }
    
    // 验证扩展名（防止伪造）
    const ext = path.extname(file.originalname).toLowerCase();
    const extMap = {
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.png': 'image/png',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
    };
    
    if (extMap[ext] !== file.mimetype) {
      return cb(new Error('文件扩展名与内容不匹配'));
    }
    
    cb(null, true);
  },
});

// 使用
app.post('/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: '未上传文件' });
  }
  
  res.json({
    filename: req.file.filename,
    size: req.file.size,
    mimetype: req.file.mimetype,
  });
});

// 错误处理
app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({ error: '文件大小超过限制 (5MB)' });
    }
    return res.status(400).json({ error: err.message });
  }
  next(err);
});
```

#### 验证方法
```bash
# 1. 测试输入验证
curl -X POST https://yourdomain.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid","password":"123"}'
# 应该返回 400 + 验证错误详情

# 2. 测试 SQL 注入防护
curl -X GET "https://yourdomain.com/api/user?username=admin' OR '1'='1"
# 应该返回空结果或错误，不应返回所有用户

# 3. 测试 XSS 防护
curl -X POST https://yourdomain.com/api/profile \
  -H "Content-Type: application/json" \
  -d '{"bio":"<script>alert(1)</script>"}'
# 返回的 bio 应该被转义或移除 script 标签

# 4. 测试文件上传
curl -X POST https://yourdomain.com/upload \
  -F "file=@malicious.exe"
# 应该返回 400 错误

curl -X POST https://yourdomain.com/upload \
  -F "file=@large.jpg"  # 大于 5MB
# 应该返回 400 错误
```

---

### 检查项 12: 错误信息安全

#### 一句话风险
生产环境错误返回完整堆栈信息，包含数据库连接字符串、文件路径、内部实现细节，攻击者利用这些信息发起精准攻击。

#### 一分钟识别
- [ ] 生产环境返回详细错误堆栈
- [ ] 错误信息包含数据库连接字符串
- [ ] 错误信息包含文件路径
- [ ] 未区分开发和生产环境的错误展示
→ 勾选≥1项，即需关注此风险

#### 一句话防御
生产环境只返回通用错误信息，详细错误记录到日志，使用环境变量控制错误展示。

#### 快速行动清单
1. [ ] 检查生产环境错误响应（2分钟）
2. [ ] 配置错误处理中间件（5分钟）
3. [ ] 分离开发和生产环境配置（3分钟）

#### 推荐工具
- 免费：框架内置错误处理
- 免费：`morgan`（日志）
- 免费：`sentry`（错误追踪）

#### 代码示例

```typescript
// Node.js: Express 全局错误处理
import express, { Request, Response, NextFunction } from 'express';

const app = express();

// 自定义错误类
class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {
    super(message);
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

// 404 错误
app.use((req: Request, res: Response, next: NextFunction) => {
  next(new AppError(`找不到路径: ${req.originalUrl}`, 404));
});

// 全局错误处理中间件
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  // 如果是自定义错误
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      status: 'error',
      message: err.message,
      ...(process.env.NODE_ENV === 'development' && {
        stack: err.stack,
      }),
    });
  }
  
  // 未知错误
  console.error('未处理的错误:', err);
  
  // 生产环境：隐藏详细错误信息
  if (process.env.NODE_ENV === 'production') {
    return res.status(500).json({
      status: 'error',
      message: '服务器内部错误，请稍后再试',
    });
  }
  
  // 开发环境：返回详细错误
  return res.status(500).json({
    status: 'error',
    message: err.message,
    stack: err.stack,
  });
});

// 异步错误处理包装器
function asyncHandler(fn: Function) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// 使用
app.get('/api/user/:id', asyncHandler(async (req, res) => {
  const user = await db.getUser(req.params.id);
  if (!user) {
    throw new AppError('用户不存在', 404);
  }
  res.json(user);
}));
```

```python
# Python: FastAPI 错误处理
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback

app = FastAPI()
logger = logging.getLogger(__name__)

# 自定义异常
class AppException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

# 全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )

# 验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "输入验证失败",
            "details": exc.errors(),
        },
    )

# 全局异常处理（捕获所有未处理异常）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # 记录详细错误到日志
    logger.error(f"未处理的异常: {exc}\n{traceback.format_exc()}")
    
    # 生产环境隐藏详细错误
    if os.getenv("ENVIRONMENT") == "production":
        return JSONResponse(
            status_code=500,
            content={"error": "服务器内部错误，请稍后再试"},
        )
    
    # 开发环境返回详细错误
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "type": type(exc).__name__,
            "traceback": traceback.format_exc(),
        },
    )

# 使用
@app.get("/api/user/{user_id}")
async def get_user(user_id: int):
    user = await db.get_user(user_id)
    if not user:
        raise AppException("用户不存在", 404)
    return user
```

```typescript
// 敏感信息脱敏
function sanitizeErrorMessage(message: string): string {
  // 移除数据库连接字符串
  message = message.replace(
    /postgres:\/\/[^\s]+/g,
    'postgres://[REDACTED]'
  );
  
  // 移除文件路径
  message = message.replace(
    /\/[\w\/-]+\.(ts|js|py)/g,
    '[FILE_PATH]'
  );
  
  // 移除 API Key
  message = message.replace(
    /sk-[a-zA-Z0-9]+/g,
    '[API_KEY]'
  );
  
  return message;
}

// 安全日志记录
function logError(error: Error, req: Request) {
  const safeMessage = sanitizeErrorMessage(error.message);
  
  logger.error({
    message: safeMessage,
    stack: process.env.NODE_ENV === 'development' ? error.stack : undefined,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    userId: req.userId,
    timestamp: new Date().toISOString(),
  });
}
```

```typescript
// Sentry 集成（可选）
import * as Sentry from '@sentry/node';

// 初始化 Sentry
Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  // 过滤敏感信息
  beforeSend(event) {
    if (event.request) {
      delete event.request.cookies;
      if (event.request.headers) {
        delete event.request.headers.authorization;
        delete event.request.headers.cookie;
      }
    }
    return event;
  },
});

// Express 集成
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.errorHandler({
  shouldHandleError(error) {
    // 只报告 500 错误
    return error.status >= 500;
  },
}));
```

#### 验证方法
```bash
# 1. 测试生产环境错误响应
NODE_ENV=production npm start

curl https://yourdomain.com/api/nonexistent
# 应该返回: {"error":"找不到路径"} 而非堆栈信息

curl https://yourdomain.com/api/error
# 应该返回: {"error":"服务器内部错误"} 而非详细错误

# 2. 检查错误响应头
curl -I https://yourdomain.com/api/error
# 确认没有 X-Powered-By 等敏感信息

# 3. 测试开发环境
NODE_ENV=development npm start
curl http://localhost:3000/api/error
# 应该返回详细堆栈信息

# 4. 检查日志
# 确认生产环境日志不包含敏感信息
grep -r "password\|secret\|token" /var/log/your-app/
# 应该无输出或已脱敏
```

---

## 成本估算

| 指标 | 免费方案 | 低成本方案 |
|------|---------|----------|
| 总实施成本 | $0 | $0 |
| 实施时间 | 2小时（完整版） | 30分钟（核心项） |
| 维护时间 | 1小时/月 | 30分钟/月 |
| 月运营成本 | $0 | $0-50（可选SaaS） |

### 核心项（30分钟快速版）
1. ✅ 环境变量安全（检查 `.gitignore`）
2. ✅ HTTPS 强制配置（Let's Encrypt）
3. ✅ 密码哈希（bcrypt）
4. ✅ 速率限制（express-rate-limit）
5. ✅ 错误信息安全（关闭详细错误）

---

## 迁出成本

- **迁出难度**: 低
- **迁出步骤**: 
  1. 导出环境变量到新平台
  2. 迁移备份文件
  3. 更新监控配置

---

## 与其他武器配合

- **前置**: 无（安全基线是起点）
- **后置**: 
  - `incident-response-playbook.md`（应急响应）
  - `security-monitoring.md`（深度监控）
- **替代**: 无（必须实施）

---

## 常见问题

**Q: 我是个人开发者，真的需要这么多安全措施吗？**

A: 安全不是可选项。独立开发者更容易成为攻击目标（自动化扫描、低防御）。实施这个基线清单只需要 2 小时，但能防止 80% 的常见攻击。

**Q: 免费方案够用吗？**

A: 对于独立开发者完全够用。本清单中所有工具都有免费层，足以支撑从 0 到 1 万用户。当业务增长后再考虑付费方案。

**Q: 哪些项目最优先？**

A: 按严重程度排序：
1. Critical（今天做）：环境变量、依赖安全、数据库安全、API密钥
2. High（本周做）：HTTPS、认证、日志、备份
3. Medium（本月做）：监控、速率限制、输入验证、错误处理

**Q: 如何验证安全性？**

A: 每个检查项都包含验证方法。此外可以使用：
- `nmap` 扫描开放端口
- `OWASP ZAP` 自动化漏洞扫描
- `SSL Labs` 测试 HTTPS 配置
- `Security Headers` 检查安全头

---

## 推荐实现

### 免费（推荐）
- 所有代码示例均可免费使用
- Let's Encrypt 免费证书
- UptimeRobot 免费监控
- GitHub Dependabot 免费依赖更新

### 低成本（可选升级）
- Sentry Developer Plan - $26/月 - 错误追踪
- Cloudflare Pro - $20/月 - WAF + DDoS防护
- Datadog - $15/月 - 深度监控

### 企业级
- 参考 `cases/enterprise/` 目录中的企业级案例

---

## 附录：一键检查脚本

```bash
#!/bin/bash
# 文件: security-check.sh
# 用法: curl -sSL https://your-repo/security-check.sh | bash

echo "=== 独立开发者安全基线检查 ==="
echo ""

# 1. 环境变量安全
echo "1. 环境变量安全"
if [ -f ".env" ]; then
  if grep -q ".env" .gitignore; then
    echo "  ✅ .env 已在 .gitignore 中"
  else
    echo "  ❌ .env 未添加到 .gitignore"
  fi
else
  echo "  ⚠️  未找到 .env 文件"
fi

# 2. 依赖安全
echo ""
echo "2. 依赖安全"
if [ -f "package.json" ]; then
  vulnerabilities=$(npm audit --json | jq '.metadata.vulnerabilities.total')
  if [ "$vulnerabilities" = "0" ]; then
    echo "  ✅ 无已知漏洞"
  else
    echo "  ❌ 发现 $vulnerabilities 个漏洞"
  fi
elif [ -f "requirements.txt" ]; then
  echo "  运行 pip-audit 检查..."
fi

# 3. HTTPS
echo ""
echo "3. HTTPS 配置"
if [ -n "$DOMAIN" ]; then
  hsts=$(curl -sI "https://$DOMAIN" | grep -i "strict-transport-security")
  if [ -n "$hsts" ]; then
    echo "  ✅ HSTS 已配置"
  else
    echo "  ❌ 未配置 HSTS"
  fi
else
  echo "  ⚠️  未设置 DOMAIN 环境变量"
fi

# 4. 密码强度
echo ""
echo "4. 数据库密码"
if [ -n "$DATABASE_URL" ]; then
  password=$(echo "$DATABASE_URL" | sed -n 's/.*:\([^@]*\)@.*/\1/p')
  if [ ${#password} -lt 16 ]; then
    echo "  ❌ 数据库密码少于 16 位"
  else
    echo "  ✅ 数据库密码长度合格"
  fi
fi

# 5. 备份
echo ""
echo "5. 备份检查"
if [ -d "/var/backups" ]; then
  latest_backup=$(ls -t /var/backups/*.sql.gz 2>/dev/null | head -1)
  if [ -n "$latest_backup" ]; then
    backup_age=$((($(date +%s) - $(stat -c %Y "$latest_backup")) / 86400))
    if [ $backup_age -le 1 ]; then
      echo "  ✅ 备份最新（$backup_age 天前）"
    else
      echo "  ⚠️  备份已过期（$backup_age 天前）"
    fi
  else
    echo "  ❌ 未找到备份文件"
  fi
else
  echo "  ❌ 未配置备份目录"
fi

echo ""
echo "=== 检查完成 ==="
```

---

## 更新日志

- **2026-06-11**: 初始版本，包含 12 项安全基线检查
