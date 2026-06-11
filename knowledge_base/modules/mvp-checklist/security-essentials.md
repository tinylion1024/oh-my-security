# 安全必备项

> 文档路径：`/modules/mvp-checklist/security-essentials.md`  
> 最后更新：2025-06-11  
> 预计阅读时间：15 分钟

---

## 概述

本文档列出 MVP 上线前**必须实现**的 Top 10 安全措施，以及常见遗漏项和快速修复指南。如果时间紧迫，至少要确保这 10 项全部通过。

---

## 一、必须实现的安全措施（Top 10）

### 🔴 1. 密码安全存储

**风险等级**：🔴 关键  
**修复难度**：低  
**影响范围**：所有使用密码认证的系统

#### 为什么必须？

密码泄露是账户劫持的主要途径。一旦数据库泄露，弱哈希或明文存储的密码将直接暴露用户账户。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 算法选择 | 使用 `bcrypt`、`Argon2` 或 `scrypt` |
| 禁止使用 | MD5、SHA1、SHA256（单独使用） |
| 最小强度 | bcrypt cost ≥ 10，Argon2 迭代 ≥ 2 |
| 加盐 | 算法内置盐值，无需额外存储 |

#### 代码示例

```javascript
// Node.js - bcrypt
const bcrypt = require('bcrypt');
const saltRounds = 12; // 推荐 10-12

// 加密
const hashedPassword = await bcrypt.hash(plainPassword, saltRounds);

// 验证
const isMatch = await bcrypt.compare(inputPassword, hashedPassword);
```

```python
# Python - bcrypt
import bcrypt

# 加密
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))

# 验证
is_match = bcrypt.checkpw(password.encode('utf-8'), hashed)
```

#### 快速检查

```bash
# 检查密码哈希格式（bcrypt 以 $2b$ 或 $2a$ 开头）
grep -r "password.*:" database_dump.txt | head -5
# 正确格式示例：$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYA/7.J5DdOq
```

---

### 🔴 2. 全站 HTTPS

**风险等级**：🔴 关键  
**修复难度**：低  
**影响范围**：所有 Web 应用

#### 为什么必须？

HTTP 明文传输，数据在传输过程中可被监听、篡改。HTTPS 是现代 Web 安全的基础。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 强制 HTTPS | 所有 HTTP 请求重定向到 HTTPS |
| 证书有效 | 使用可信 CA 签发的证书 |
| HSTS | 启用 HTTP Strict Transport Security |
| 证书续期 | 自动续期，避免过期 |

#### 配置示例

```nginx
# Nginx - 强制 HTTPS
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name example.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

#### 快速检查

```bash
# 检查 HTTPS 和证书
curl -sI https://your-domain.com | grep -E "HTTP|Strict-Transport-Security"

# 使用 SSL Labs 测试
# 访问: https://www.ssllabs.com/ssltest/
```

---

### 🔴 3. 敏感数据加密存储

**风险等级**：🔴 关键  
**修复难度**：中  
**影响范围**：存储敏感数据的所有系统

#### 为什么必须？

数据库泄露时有发生。敏感数据加密存储可确保即使数据库泄露，数据也无法被直接读取。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 算法选择 | AES-256-GCM（推荐）或 ChaCha20-Poly1305 |
| 密钥管理 | 使用 KMS 或密钥管理服务，密钥与数据分离 |
| 加密范围 | 个人身份信息、支付信息、敏感业务数据 |
| 密钥轮换 | 定期轮换加密密钥 |

#### 代码示例

```javascript
// Node.js - AES-256-GCM 加密
const crypto = require('crypto');

const algorithm = 'aes-256-gcm';
const key = Buffer.from(process.env.ENCRYPTION_KEY, 'hex'); // 32 bytes

function encrypt(text) {
    const iv = crypto.randomBytes(12); // GCM 推荐 12 bytes
    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();
    return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
}

function decrypt(encrypted) {
    const [ivHex, authTagHex, data] = encrypted.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');
    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    decipher.setAuthTag(authTag);
    let decrypted = decipher.update(data, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}
```

#### 快速检查

```bash
# 检查数据库中是否有明文敏感数据
# 假设用户表中有 phone 字段
mysql> SELECT phone FROM users LIMIT 5;
# 如果显示真实手机号而非加密字符串，则未加密
```

---

### 🔴 4. SQL 注入防护

**风险等级**：🔴 关键  
**修复难度**：低  
**影响范围**：所有使用数据库的系统

#### 为什么必须？

SQL 注入可导致数据泄露、数据篡改、甚至服务器被控制。这是最常见的 Web 漏洞之一。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 参数化查询 | 使用参数化查询或 ORM |
| 禁止拼接 | 禁止直接拼接用户输入到 SQL |
| 输入验证 | 验证输入类型和格式 |
| 最小权限 | 数据库账户仅授予必要权限 |

#### 代码示例

```javascript
// 错误示例 - SQL 拼接
const query = `SELECT * FROM users WHERE id = '${userId}'`; // 危险！

// 正确示例 - 参数化查询
const query = 'SELECT * FROM users WHERE id = ?';
connection.query(query, [userId], (err, results) => {
    // 安全
});

// 使用 ORM（如 Sequelize）
const user = await User.findOne({ where: { id: userId } });
```

#### 快速检查

```bash
# 搜索代码中可能的 SQL 注入点
grep -rn "SELECT.*\${\|SELECT.*+\s*\"" --include="*.js" --include="*.py" .
grep -rn "WHERE.*\${\|WHERE.*+\s*\"" --include="*.js" --include="*.py" .
```

---

### 🔴 5. XSS 防护

**风险等级**：🔴 关键  
**修复难度**：中  
**影响范围**：所有 Web 应用

#### 为什么必须？

XSS 攻击可窃取用户 Cookie、Session、执行恶意操作，是 Web 安全的重灾区。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 输出编码 | 所有动态内容输出前进行 HTML 编码 |
| CSP | 配置 Content-Security-Policy |
| 输入验证 | 白名单验证用户输入 |
| Cookie 保护 | 设置 HttpOnly 属性 |

#### 代码示例

```javascript
// React 自动转义
<div>{userInput}</div> // 安全，React 会自动转义

// 危险！
<div dangerouslySetInnerHTML={{__html: userInput}} />

// 使用 DOMPurify 清理 HTML
import DOMPurify from 'dompurify';
<div dangerouslySetInnerHTML={{__html: DOMPurify.sanitize(userInput)}} />
```

```http
# CSP 配置
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-xxx'; style-src 'self' 'unsafe-inline';
```

#### 快速检查

```bash
# 测试 XSS 漏洞
# 在输入框或 URL 参数中输入：
<script>alert('XSS')</script>
<img src=x onerror=alert('XSS')>
"><script>alert('XSS')</script>
```

---

### 🔴 6. 支付数据不落本地

**风险等级**：🔴 关键  
**修复难度**：中  
**影响范围**：所有涉及支付的 Web 应用

#### 为什么必须？

自行存储支付卡信息面临极高的安全风险和合规成本。使用支付网关托管可大幅降低风险。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 支付网关 | 使用 PCI DSS 认证的支付服务商（如 Stripe、支付宝、微信支付） |
| 托管页面 | 用户在支付网关页面完成支付 |
| Token 化 | 使用支付网关返回的 Token 标识支付方式 |
| 不存储卡号 | 禁止存储卡号、CVV、有效期 |

#### 架构示意

```
用户 → 你的网站 → 支付网关托管页面 → 支付完成回调
                    ↑
               卡信息在这里处理
               你的服务器不接触卡信息
```

#### 快速检查

```bash
# 检查数据库是否存储了支付卡信息
mysql> SHOW COLUMNS FROM payments LIKE '%card%';
mysql> SHOW COLUMNS FROM payments LIKE '%cvv%';
# 如果有 card_number、cvv 等字段，则存在风险
```

---

### 🔴 7. 隐私政策已上线并获用户同意

**风险等级**：🔴 关键  
**修复难度**：低  
**影响范围**：所有收集用户数据的 Web 应用

#### 为什么必须？

GDPR、网络安全法等法规要求必须告知用户数据收集和使用方式，并获得用户同意。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 隐私政策 | 上线前必须发布隐私政策 |
| 用户同意 | 首次使用时获取用户同意 |
| 可撤回 | 用户可随时撤回同意 |
| 儿童保护 | 如涉及儿童，需监护人同意 |

#### 实现要点

```html
<!-- Cookie 同意横幅 -->
<div id="cookie-banner" class="cookie-banner">
    <p>我们使用 Cookie 改善您的体验。继续使用即表示同意我们的
        <a href="/privacy">隐私政策</a>。
    </p>
    <button onclick="acceptCookies()">同意</button>
    <button onclick="rejectCookies()">拒绝</button>
</div>
```

#### 快速检查

- [ ] 隐私政策页面可访问（/privacy）
- [ ] 首次访问显示 Cookie 同意提示
- [ ] 用户同意记录可查询
- [ ] 用户可删除账户和数据

---

### 🔴 8. 第三方 SDK 安全

**风险等级**：🔴 关键  
**修复难度**：中  
**影响范围**：所有使用第三方库/SDK 的项目

#### 为什么必须？

第三方依赖可能包含已知漏洞或恶意代码，是供应链攻击的主要途径。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 来源可信 | 仅从官方源安装依赖 |
| 版本锁定 | 锁定依赖版本，避免自动更新 |
| 漏洞扫描 | 定期扫描依赖漏洞 |
| 最小依赖 | 仅安装必要的依赖 |

#### 代码示例

```bash
# 检查依赖漏洞
npm audit

# 自动修复
npm audit fix

# 使用 Snyk 检查
npx snyk test

# 检查过时依赖
npm outdated
```

#### 快速检查

```bash
# 检查 package-lock.json 或 yarn.lock 是否存在
ls package-lock.json yarn.lock

# 运行漏洞扫描
npm audit --audit-level=high
```

---

### 🟠 9. 错误信息不泄露敏感信息

**风险等级**：🟠 高  
**修复难度**：低  
**影响范围**：所有 Web 应用

#### 为什么必须？

详细的错误信息可能泄露系统内部结构、数据库信息、文件路径等，为攻击者提供线索。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 统一错误响应 | 对外返回统一格式的错误信息 |
| 隐藏技术细节 | 不返回堆栈跟踪、SQL 语句、文件路径 |
| 记录详细日志 | 服务器端记录详细错误信息供排查 |
| 错误码设计 | 使用错误码而非描述性错误信息 |

#### 代码示例

```javascript
// 错误处理中间件
app.use((err, req, res, next) => {
    // 记录详细错误到日志
    console.error(err);
    
    // 返回统一格式的错误响应
    res.status(500).json({
        error: {
            code: 'INTERNAL_ERROR',
            message: '服务器内部错误，请稍后重试'
        }
    });
});
```

#### 快速检查

```bash
# 触发一个错误，检查响应
curl -X POST https://your-domain.com/api/invalid-endpoint

# 不应返回类似以下信息：
# - 堆栈跟踪
# - SQL 语句
# - 文件路径
# - 数据库连接字符串
```

---

### 🟠 10. 日志不记录敏感数据

**风险等级**：🟠 高  
**修复难度**：低  
**影响范围**：所有记录日志的系统

#### 为什么必须？

日志文件可能被攻击者获取，其中包含的敏感数据会导致信息泄露。

#### 实现要求

| 要求 | 说明 |
|------|------|
| 脱敏处理 | 日志记录前对敏感数据脱敏 |
| 过滤字段 | 配置敏感字段过滤列表 |
| 日志访问控制 | 限制日志文件访问权限 |
| 日志保留 | 设置合理的日志保留周期 |

#### 代码示例

```javascript
// 日志脱敏函数
function maskSensitive(data) {
    const sensitiveFields = ['password', 'token', 'cardNumber', 'cvv', 'ssn'];
    const masked = { ...data };
    
    for (const field of sensitiveFields) {
        if (masked[field]) {
            masked[field] = '***REDACTED***';
        }
    }
    
    // 手机号脱敏
    if (masked.phone) {
        masked.phone = masked.phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
    }
    
    return masked;
}

// 使用
logger.info('User login', maskSensitive({ userId: 123, phone: '13812345678', password: 'secret' }));
// 输出: User login { userId: 123, phone: '138****5678', password: '***REDACTED***' }
```

#### 快速检查

```bash
# 搜索日志中的敏感数据
grep -rn "password\|token\|secret\|card" /var/log/your-app/ --include="*.log"

# 检查日志配置
cat /etc/your-app/logging.conf
```

---

## 二、常见遗漏项提醒

### 易被忽视的安全问题

| # | 遗漏项 | 风险 | 快速检查方法 |
|---|--------|------|-------------|
| 1 | 测试/调试接口未关闭 | 攻击者利用测试接口 | 检查 `/test`、`/debug`、`/swagger` 等路径 |
| 2 | 默认账户未修改 | 攻击者使用默认密码登录 | 检查 `admin/admin`、`root/root` 等默认账户 |
| 3 | 文件上传目录可执行 | 上传恶意脚本执行 | 检查上传目录权限，禁止执行 |
| 4 | API 无速率限制 | 暴力破解、DDoS | 测试连续请求是否被限制 |
| 5 | 敏感信息在 URL 中 | 日志、Referer 泄露 | 检查 URL 是否包含 token、password |
| 6 | 弱随机数生成器 | 可预测的 Token、密码 | 检查是否使用 `Math.random()` |
| 7 | 开发环境信息泄露 | 版本信息辅助攻击 | 检查响应头是否暴露框架版本 |
| 8 | 未设置安全响应头 | XSS、点击劫持 | 检查 CSP、X-Frame-Options 等 |
| 9 | 备份文件可访问 | 源码泄露 | 检查 `.bak`、`.zip`、`.tar.gz` 文件 |
| 10 | 错误页面信息泄露 | 技术栈泄露 | 触发 404、500 错误检查响应 |

---

## 三、快速修复指南

### 按优先级排序的修复清单

#### 🔴 P0 - 上线前必须修复

| 问题 | 修复方法 | 预计时间 |
|------|----------|----------|
| 密码明文存储 | 改用 bcrypt/Argon2 | 2-4 小时 |
| 无 HTTPS | 配置 SSL 证书，强制 HTTPS | 1-2 小时 |
| SQL 注入 | 改用参数化查询/ORM | 2-4 小时 |
| XSS 漏洞 | 输出编码，配置 CSP | 2-4 小时 |
| 支付数据落本地 | 接入支付网关托管 | 4-8 小时 |

#### 🟠 P1 - 上线后一周内修复

| 问题 | 修复方法 | 预计时间 |
|------|----------|----------|
| 无 API 速率限制 | 实现速率限制中间件 | 1-2 小时 |
| 日志记录敏感数据 | 实现日志脱敏 | 1-2 小时 |
| 安全响应头缺失 | 配置安全响应头 | 0.5 小时 |
| 错误信息泄露 | 统一错误处理 | 1-2 小时 |

#### 🟡 P2 - 上线后一月内修复

| 问题 | 修复方法 | 预计时间 |
|------|----------|----------|
| 无 MFA | 实现 TOTP/短信验证 | 4-8 小时 |
| Session 管理不当 | 优化 Session 配置 | 2-4 小时 |
| 数据分类分级 | 制定数据分类标准 | 4-8 小时 |

---

## 四、风险评估表

### 按业务场景的风险评估

| 业务场景 | 关键风险 | 必备安全措施 | 检查频率 |
|----------|----------|--------------|----------|
| 用户注册登录 | 密码泄露、账户劫持 | 密码加密、MFA、登录限制 | 上线前 |
| 用户数据存储 | 数据泄露 | 数据加密、访问控制 | 上线前 |
| 在线支付 | 支付数据泄露、欺诈 | 支付网关托管、防重放 | 上线前 |
| 文件上传 | 恶意文件上传 | 类型验证、大小限制、目录隔离 | 上线前 |
| API 接口 | 注入、越权、滥用 | 输入验证、权限检查、速率限制 | 上线前 |
| 第三方集成 | 数据泄露、供应链攻击 | 来源验证、权限最小化 | 上线前 |
| 后台管理 | 越权、误操作 | MFA、操作日志、权限分离 | 上线前 |
| 数据导出 | 批量数据泄露 | 权限控制、脱敏、审批流程 | 上线前 |

### 风险等级判定

| 等级 | 判定标准 | 响应要求 |
|------|----------|----------|
| 🔴 严重 | 可能导致大规模数据泄露、资金损失、系统被控 | 立即停止上线，修复后复查 |
| 🟠 高 | 可能导致部分数据泄露、账户被盗、业务中断 | 上线前必须修复或豁免审批 |
| 🟡 中 | 可能导致信息泄露、用户体验受损 | 上线后 7 天内修复 |
| 🟢 低 | 最佳实践建议，影响较小 | 上线后 30 天内优化 |

---

## 五、安全检查快速清单

### 一键自检

```bash
# 复制以下命令执行
echo "=== MVP 安全必备项自检 ==="

# 1. 检查 HTTPS
echo -e "\n[1] HTTPS 检查"
curl -sI https://$DOMAIN 2>/dev/null | head -5

# 2. 检查安全响应头
echo -e "\n[2] 安全响应头检查"
curl -sI https://$DOMAIN 2>/dev/null | grep -iE "strict-transport|x-frame-options|content-security-policy|x-content-type"

# 3. 检查依赖漏洞
echo -e "\n[3] 依赖漏洞检查"
npm audit --audit-level=high 2>/dev/null || echo "无 package.json 或无高危漏洞"

# 4. 检查硬编码敏感信息
echo -e "\n[4] 敏感信息泄露检查"
grep -rn "password\s*=\s*['\"]" --include="*.js" --include="*.py" . 2>/dev/null | head -5 || echo "未发现明文密码"

echo -e "\n=== 检查完成 ==="
```

---

> ⚠️ **提醒**：本清单为基线要求，根据业务特性可能需要补充额外安全措施。建议结合 [pre-launch-checklist.md](./pre-launch-checklist.md) 进行全面检查。
