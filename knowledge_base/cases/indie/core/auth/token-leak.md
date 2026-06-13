# 令牌泄露风险（Token Leak）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
JWT、Session Token、API Key 等认证令牌因配置错误、代码泄露或传输不安全被攻击者获取，导致任意用户账号接管或 API 滥用。

### 一分钟识别
你的产品是否有以下特征：
- [ ] JWT 存储在 localStorage 中
- [ ] API Key 硬编码在前端代码中
- [ ] Token 没有过期时间或过期时间过长
- [ ] Token 通过非 HTTPS 传输
- [ ] 敏感 Token 出现在日志或错误信息中
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
JWT 存储 HttpOnly Cookie 中，API Key 只存后端，设置合理的 Token 过期时间，强制 HTTPS 传输，日志脱敏处理。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查 JWT 是否存储在 localStorage，改为 HttpOnly Cookie
   - [ ] 检查前端代码是否有硬编码的 API Key
   - [ ] 设置 JWT 过期时间（建议 15-60 分钟）
   - [ ] 检查日志是否记录了 Token 信息

2. **短期行动**（本周可完成，免费）
   - [ ] 实现 Refresh Token 机制
   - [ ] 添加 Token 撤销机制（黑名单）
   - [ ] 实现 Token 泄露检测
   - [ ] 日志脱敏处理

3. **长期行动**（规划中，低成本）
   - [ ] 实现异常 Token 使用检测
   - [ ] 建立密钥轮换机制
   - [ ] 实现多设备 Token 管理

### 推荐工具
- **免费**：
  - [jwt.io](https://jwt.io/) - JWT 调试工具
  - [truffleHog](https://github.com/trufflesecurity/trufflehog) - Git 密钥泄露扫描

- **低成本**：
  - [GitGuardian](https://www.gitguardian.com/) - 密钥泄露监控
  - [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) - 密钥管理

### 验证方法
- [ ] 测试步骤1：检查 DevTools Application，确认 JWT 不在 localStorage
- [ ] 测试步骤2：检查 DevTools Network，确认 Token 通过 HTTPS 传输
- [ ] 测试步骤3：测试 Token 过期后自动刷新
- [ ] 测试步骤4：检查日志文件，确认无 Token 明文

---

## L2 小团队版（理解版）

### 场景还原
你的 SaaS 产品使用 JWT 认证，存储在 localStorage 中。某天发生：

**攻击时间线**：
1. **Day 0**：你的网站存在 XSS 漏洞（可能是第三方库或用户输入未转义）
2. **Day 1**：攻击者发现漏洞，注入恶意脚本
3. **Day 2**：恶意脚本窃取 localStorage 中的 JWT
4. **Day 3**：攻击者使用窃取的 JWT 访问所有用户数据

**真实损失案例**：
- 2021年某金融科技公司，因 JWT 存储在 localStorage 被 XSS 攻击窃取
- 2020年某电商平台，API Key 泄露在 GitHub 导致恶意调用

### 常见 Token 泄露方式

**1. localStorage 存储 JWT**
```javascript
// 错误示例：JWT 存储在 localStorage
// 登录成功后
localStorage.setItem('token', response.data.token);

// 问题：
// 1. 任何 JavaScript 都可以访问 localStorage
// 2. XSS 攻击可以窃取 token
// 3. 浏览器扩展可能读取 token

// 正确示例：使用 HttpOnly Cookie
// 后端设置 Cookie
res.cookie('token', token, {
  httpOnly: true,  // JavaScript 无法访问
  secure: true,    // 仅 HTTPS
  sameSite: 'strict', // CSRF 防护
  maxAge: 3600000  // 1小时过期
});
```

**2. URL 参数传递 Token**
```javascript
// 错误示例：Token 在 URL 中
// 重定向时
window.location.href = `/dashboard?token=${token}`;

// 问题：
// 1. URL 会被记录在浏览器历史
// 2. URL 会被记录在服务器日志
// 3. URL 可能被第三方脚本读取（如分析工具）
// 4. 用户可能分享包含 Token 的链接

// 正确示例：使用 Cookie 或 POST 请求
```

**3. Referer 头泄露**
```javascript
// 场景：你的网站加载了第三方资源
// 用户点击第三方链接时，Referer 头可能包含 Token
<a href="https://external-site.com">External Link</a>

// 如果当前 URL 是 /dashboard?token=xxx
// Referer 头会包含完整 URL，泄露 Token

// 防御：
// 1. 设置 Referrer-Policy 头
res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
// 或
<meta name="referrer" content="strict-origin-when-cross-origin">
```

**4. 日志记录 Token**
```javascript
// 错误示例：日志中记录 Token
app.use((req, res, next) => {
  console.log('Request:', {
    url: req.url,
    headers: req.headers, // 包含 Authorization: Bearer xxx
    body: req.body        // 可能包含 Token
  });
  next();
});

// 正确示例：日志脱敏
function sanitizeHeaders(headers) {
  const sanitized = { ...headers };
  if (sanitized['authorization']) {
    sanitized['authorization'] = '[REDACTED]';
  }
  return sanitized;
}

app.use((req, res, next) => {
  logger.info('Request:', {
    url: req.url,
    headers: sanitizeHeaders(req.headers),
    userId: req.user?.id // 记录用户 ID 而非 Token
  });
  next();
});
```

**5. GitHub 代码泄露**
```javascript
// 错误示例：API Key 硬编码
const API_KEY = 'sk-xxx-xxx-xxx'; // 开发者不小心提交到 GitHub

// 正确示例：使用环境变量
const API_KEY = process.env.API_KEY;

// 防御措施：
// 1. 使用 .gitignore 忽略 .env 文件
// 2. 使用 pre-commit hook 检查敏感信息
// 3. 使用密钥管理服务
```

### 完整的 Token 安全实现

```javascript
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

class TokenService {
  constructor() {
    this.accessTokenSecret = process.env.JWT_ACCESS_SECRET;
    this.refreshTokenSecret = process.env.JWT_REFRESH_SECRET;
    this.accessTokenExpiry = '15m';  // 15分钟
    this.refreshTokenExpiry = '7d';  // 7天
  }
  
  // 生成 Access Token
  generateAccessToken(user) {
    return jwt.sign(
      { 
        userId: user.id,
        email: user.email,
        role: user.role
      },
      this.accessTokenSecret,
      { 
        expiresIn: this.accessTokenExpiry,
        issuer: 'your-app',
        audience: 'your-app-users'
      }
    );
  }
  
  // 生成 Refresh Token
  generateRefreshToken(user) {
    const tokenId = crypto.randomBytes(16).toString('hex');
    
    const token = jwt.sign(
      { 
        userId: user.id,
        tokenId: tokenId
      },
      this.refreshTokenSecret,
      { expiresIn: this.refreshTokenExpiry }
    );
    
    // 存储 Token ID 用于撤销
    this.storeTokenId(user.id, tokenId);
    
    return token;
  }
  
  // 设置 Token Cookie
  setTokenCookies(res, accessToken, refreshToken) {
    // Access Token - HttpOnly Cookie
    res.cookie('accessToken', accessToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 15 * 60 * 1000, // 15分钟
      path: '/'
    });
    
    // Refresh Token - HttpOnly Cookie
    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7天
      path: '/api/auth/refresh' // 只在刷新接口使用
    });
  }
  
  // 刷新 Access Token
  async refreshAccessToken(refreshToken) {
    try {
      const decoded = jwt.verify(refreshToken, this.refreshTokenSecret);
      
      // 检查 Token 是否被撤销
      if (await this.isTokenRevoked(decoded.tokenId)) {
        throw new Error('Token revoked');
      }
      
      const user = await this.getUserById(decoded.userId);
      const newAccessToken = this.generateAccessToken(user);
      
      return { accessToken: newAccessToken };
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }
  
  // 撤销 Token（用于登出）
  async revokeToken(tokenId) {
    await this.addToBlacklist(tokenId);
  }
  
  // Token 黑名单（使用 Redis）
  async addToBlacklist(tokenId) {
    await redis.set(`blacklist:${tokenId}`, '1', 'EX', 7 * 24 * 60 * 60);
  }
  
  async isTokenRevoked(tokenId) {
    const exists = await redis.get(`blacklist:${tokenId}`);
    return !!exists;
  }
}

// 中间件：验证 Access Token
function authenticateToken(req, res, next) {
  const token = req.cookies.accessToken;
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  jwt.verify(token, process.env.JWT_ACCESS_SECRET, (err, user) => {
    if (err) {
      // Token 过期，尝试刷新
      if (err.name === 'TokenExpiredError') {
        return res.status(401).json({ 
          error: 'Token expired',
          shouldRefresh: true 
        });
      }
      return res.status(403).json({ error: 'Invalid token' });
    }
    
    req.user = user;
    next();
  });
}
```

### Token 泄露检测

```javascript
class TokenLeakDetector {
  constructor() {
    this.suspiciousPatterns = [];
  }
  
  // 检测异常 Token 使用
  async detectAnomalousUsage(token, context) {
    const decoded = jwt.decode(token);
    const usage = await this.getTokenUsage(decoded.tokenId);
    
    const anomalies = [];
    
    // 1. 同一 Token 多地点使用
    if (usage.locations.length > 2) {
      const distance = this.calculateDistance(
        usage.locations[0],
        usage.locations[1]
      );
      if (distance > 500) { // 超过500公里
        anomalies.push('multiple_locations');
      }
    }
    
    // 2. 短时间大量请求
    const recentRequests = await this.getRecentRequests(decoded.tokenId, 60000);
    if (recentRequests > 100) { // 1分钟超过100次
      anomalies.push('high_frequency');
    }
    
    // 3. Token 在新设备使用
    if (!usage.knownDevices.includes(context.deviceId)) {
      anomalies.push('new_device');
    }
    
    if (anomalies.length > 0) {
      await this.alertTokenLeak(decoded.userId, anomalies);
      return { leaked: true, anomalies };
    }
    
    return { leaked: false };
  }
  
  // 告警
  async alertTokenLeak(userId, anomalies) {
    logger.security('Token leak detected', { userId, anomalies });
    
    // 发送通知给用户
    await sendSecurityAlert(userId, {
      type: 'TOKEN_LEAK_DETECTED',
      message: '检测到您的账号令牌可能已泄露，请重新登录',
      anomalies
    });
    
    // 可选：自动撤销 Token
    await this.revokeAllUserTokens(userId);
  }
}
```

### API Key 安全最佳实践

```javascript
// API Key 管理服务
class APIKeyService {
  // 生成 API Key
  generateAPIKey(userId, name, permissions) {
    const key = `sk_${crypto.randomBytes(32).toString('hex')}`;
    const hashedKey = this.hashKey(key);
    
    // 存储 hashed key（而非明文）
    await db.apiKeys.create({
      userId,
      name,
      keyHash: hashedKey,
      permissions,
      createdAt: new Date(),
      lastUsed: null,
      expiresAt: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000) // 1年
    });
    
    // 返回明文 key（只在创建时显示一次）
    return key;
  }
  
  // 验证 API Key
  async verifyAPIKey(key) {
    const hashedKey = this.hashKey(key);
    const keyRecord = await db.apiKeys.findByHash(hashedKey);
    
    if (!keyRecord) {
      return { valid: false };
    }
    
    if (keyRecord.expiresAt < new Date()) {
      return { valid: false, reason: 'expired' };
    }
    
    if (keyRecord.revoked) {
      return { valid: false, reason: 'revoked' };
    }
    
    // 更新最后使用时间
    await db.apiKeys.updateLastUsed(keyRecord.id);
    
    return { 
      valid: true, 
      userId: keyRecord.userId,
      permissions: keyRecord.permissions
    };
  }
  
  // 哈希 API Key
  hashKey(key) {
    return crypto.createHash('sha256').update(key).digest('hex');
  }
  
  // 轮换 API Key
  async rotateKey(keyId) {
    const oldKey = await db.apiKeys.findById(keyId);
    
    // 创建新 Key
    const newKey = await this.generateAPIKey(
      oldKey.userId,
      oldKey.name,
      oldKey.permissions
    );
    
    // 标记旧 Key 为待过期
    await db.apiKeys.update(keyId, {
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000), // 24小时后过期
      replacedBy: newKey.id
    });
    
    return newKey;
  }
}
```

---

## L3 企业版（深度版）

### Token 安全架构

```
┌─────────────────────────────────────────────────────────────┐
│                     Token 安全防护架构                        │
├─────────────────────────────────────────────────────────────┤
│  生成层   │  安全随机 → 短过期 → 最小权限 → 加密签名          │
├─────────────────────────────────────────────────────────────┤
│  传输层   │  HTTPS Only → HttpOnly Cookie → SameSite        │
├─────────────────────────────────────────────────────────────┤
│  存储层   │  后端加密 → 密钥管理 → 环境隔离                   │
├─────────────────────────────────────────────────────────────┤
│  监控层   │  异常检测 → 泄露告警 → 自动撤销                   │
└─────────────────────────────────────────────────────────────┘
```

### Token 类型对比

| Token 类型 | 存储位置 | 安全性 | 适用场景 |
|-----------|---------|--------|----------|
| JWT | HttpOnly Cookie | ⭐⭐⭐⭐ | Web 应用 |
| Session Token | 服务端 + Cookie | ⭐⭐⭐⭐⭐ | 传统 Web 应用 |
| API Key | 后端环境变量 | ⭐⭐⭐⭐⭐ | 服务端 API 调用 |
| OAuth Token | 后端存储 | ⭐⭐⭐⭐ | 第三方授权 |

### 检测清单

- [ ] JWT 使用 HttpOnly Cookie 存储
- [ ] Token 设置合理的过期时间
- [ ] 实现 Refresh Token 机制
- [ ] Token 不出现在 URL 参数中
- [ ] 日志对 Token 进行脱敏
- [ ] API Key 存储在后端
- [ ] 实现密钥轮换机制
- [ ] 建立密钥泄露监控
- [ ] 设置安全响应头
- [ ] 实现 Token 撤销机制

---

## 参考资料

### 真实案例
- [GitHub 密钥泄露统计](https://secretscanning.githubusercontent.com/)
- [JWT 安全最佳实践](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/06-Session_Management_Testing/10-Testing_JSON_Web_Tokens)

### 技术文档
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [JWT.io](https://jwt.io/)
- [RFC 7519 - JSON Web Token](https://tools.ietf.org/html/rfc7519)

### 工具
- [truffleHog - 密钥扫描](https://github.com/trufflesecurity/trufflehog)
- [GitGuardian - 泄露监控](https://www.gitguardian.com/)
- [jwt-decode - JWT 解码](https://github.com/auth0/jwt-decode)
