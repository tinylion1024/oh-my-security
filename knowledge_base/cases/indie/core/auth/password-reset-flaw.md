# 密码重置漏洞（Password Reset Flaw）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
密码重置流程设计不当，攻击者无需密码即可重置任意用户密码，导致账号被劫持。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 重置链接/令牌长期有效（如永不过期）
- [ ] 重置令牌可预测或可重复使用
- [ ] 重置页面泄露用户信息（如"用户xxx您好"）
- [ ] 重置后不通知用户
- [ ] 重置令牌通过不安全方式发送（如URL参数）
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
重置令牌随机+单次使用+短时有效（15分钟）+ 用户通知。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查重置令牌是否使用加密随机值
   - [ ] 设置令牌过期时间（推荐15分钟）
   - [ ] 实现令牌单次使用（用后即焚）

2. **短期行动**（本周可完成，免费）
   - [ ] 重置成功后发送邮件通知
   - [ ] 记录重置操作日志（IP、时间）
   - [ ] 隐藏重置页面用户信息

3. **长期行动**（规划中，免费）
   - [ ] 添加异地重置检测
   - [ ] 可疑重置要求二次验证
   - [ ] 用户可查看重置历史

### 推荐工具
- **免费**：
  - [nodemailer](https://nodemailer.com/) - Node.js邮件发送
  - [SendGrid](https://sendgrid.com/) - 免费100封/天
  - [Resend](https://resend.com/) - 免费3000封/月

- **低成本**：
  - [Auth0](https://auth0.com/) - 完整密码重置流程，免费7000用户/月
  - [Supabase Auth](https://supabase.com/auth) - 安全重置，免费50000用户/月

### 验证方法
- [ ] 测试步骤1：请求重置后，令牌应在15分钟内过期
- [ ] 测试步骤2：使用令牌重置后，再次使用应失败
- [ ] 测试步骤3：重置成功应收到邮件通知
- [ ] 测试步骤4：重置页面不应显示用户邮箱/用户名

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有5000个用户，密码重置功能存在设计缺陷。某天收到用户反馈"我的密码被改了，不是我操作的"。调查发现：

**攻击场景1：令牌预测**
```
攻击者发现重置令牌格式：reset_12345（自增ID）
攻击者计算下一个令牌：reset_12346
使用该令牌重置目标用户密码
```

**攻击场景2：令牌泄露**
```
用户点击重置链接：https://yoursite.com/reset?token=abc123
重置页面包含第三方资源（如分析脚本、头像）
Referer头泄露：Referer: https://yoursite.com/reset?token=abc123
第三方获取令牌，重置用户密码
```

**攻击场景3：参数污染**
```
攻击者构造请求：
POST /api/reset-password
{
  "email": "victim@example.com",
  "token": "attacker_token",
  "newPassword": "hacked123"
}

后端逻辑错误：检查token有效性，但更新victim邮箱对应的密码
```

**真实案例（2024）**：
某独立开发者的产品重置令牌永不过期，且通过URL参数传递。攻击者：
1. 注册账号获取重置令牌格式
2. 分析发现令牌为时间戳+用户ID的Base64编码
3. 构造管理员账号的重置令牌
4. 成功重置管理员密码，接管系统

### 攻击路径（简化版）

**攻击方式1：令牌预测/暴力破解**

**前提条件**：
- 令牌可预测（如时间戳、自增ID、简单编码）
- 或令牌过短（可暴力破解）

**攻击步骤**：
1. 攻击者请求自己账号的重置链接
2. 分析令牌格式和生成规律
3. 计算或暴力破解目标用户的令牌
4. 使用令牌重置目标用户密码

**攻击方式2：令牌泄露**

**前提条件**：
- 令牌在URL中传递
- 重置页面包含第三方资源
- 或用户分享重置链接

**攻击步骤**：
1. 用户点击重置链接
2. 浏览器发送请求，Referer头包含完整URL（含token）
3. 第三方资源（脚本、图片）获取Referer
4. 攻击者从第三方日志或恶意脚本中获取令牌
5. 使用令牌重置密码

**攻击方式3：逻辑漏洞**

**前提条件**：
- 重置接口参数验证不严格
- 或业务逻辑存在缺陷

**攻击步骤**：
1. 攻击者请求自己账号的重置令牌
2. 构造恶意请求：
   ```
   POST /api/reset-password
   {
     "token": "attacker_token",  // 攻击者的令牌
     "email": "victim@example.com",  // 受害者的邮箱
     "newPassword": "hacked123"
   }
   ```
3. 后端验证令牌有效，但更新了victim的密码
4. 攻击者成功劫持账号

**攻击方式4：Host头注入**

**前提条件**：
- 重置链接基于Host头生成
- 未验证Host头

**攻击步骤**：
1. 攻击者发送请求：
   ```
   POST /api/forgot-password
   Host: evil.com
   {
     "email": "victim@example.com"
   }
   ```
2. 服务器生成重置链接：`https://evil.com/reset?token=xxx`
3. 受害者收到邮件并点击链接
4. 令牌发送到攻击者服务器
5. 攻击者使用令牌重置密码

### 防御实施（低成本方案）

#### 方案A：免费方案（安全实现）

**1. 安全的令牌生成**

```typescript
import { randomBytes, createHash } from 'crypto';

interface ResetToken {
  token: string;          // 发送给用户的令牌
  tokenHash: string;      // 存储在数据库的哈希
  expiresAt: Date;
  used: boolean;
}

function generateResetToken(): ResetToken {
  // 1. 生成加密安全的随机令牌
  const token = randomBytes(32).toString('hex');  // 64字符
  
  // 2. 存储哈希值（不存储明文）
  const tokenHash = createHash('sha256')
    .update(token)
    .digest('hex');
  
  // 3. 设置过期时间（15分钟）
  const expiresAt = new Date(Date.now() + 15 * 60 * 1000);
  
  return {
    token,        // 发送给用户
    tokenHash,    // 存储在数据库
    expiresAt,
    used: false,
  };
}

// 请求重置
async function requestPasswordReset(email: string): Promise<boolean> {
  // 1. 查找用户（不暴露用户是否存在）
  const user = await findUserByEmail(email);
  
  if (!user) {
    // 静默返回，避免账号枚举
    return true;
  }
  
  // 2. 使旧令牌失效
  await invalidateOldTokens(user.id);
  
  // 3. 生成新令牌
  const { token, tokenHash, expiresAt } = generateResetToken();
  
  // 4. 存储令牌哈希
  await saveResetToken({
    userId: user.id,
    tokenHash,
    expiresAt,
    used: false,
  });
  
  // 5. 发送重置邮件
  const resetUrl = `https://yoursite.com/reset-password?token=${token}`;
  await sendResetEmail(user.email, resetUrl);
  
  return true;
}
```

**2. 安全的令牌验证**

```typescript
async function verifyResetToken(token: string): Promise<{
  valid: boolean;
  userId?: string;
  error?: string;
}> {
  // 1. 计算令牌哈希
  const tokenHash = createHash('sha256')
    .update(token)
    .digest('hex');
  
  // 2. 查找令牌记录
  const tokenRecord = await findResetTokenByHash(tokenHash);
  
  if (!tokenRecord) {
    return { valid: false, error: '无效的重置链接' };
  }
  
  // 3. 检查是否已使用
  if (tokenRecord.used) {
    return { valid: false, error: '重置链接已使用' };
  }
  
  // 4. 检查是否过期
  if (new Date() > tokenRecord.expiresAt) {
    return { valid: false, error: '重置链接已过期' };
  }
  
  // 5. 检查令牌长度（防止暴力破解短令牌）
  if (token.length !== 64) {
    return { valid: false, error: '无效的重置链接' };
  }
  
  return { valid: true, userId: tokenRecord.userId };
}
```

**3. 安全的重置流程**

```typescript
async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ success: boolean; error?: string }> {
  // 1. 验证令牌
  const { valid, userId, error } = await verifyResetToken(token);
  
  if (!valid) {
    return { success: false, error };
  }
  
  // 2. 验证密码强度
  const passwordCheck = validatePasswordStrength(newPassword);
  if (!passwordCheck.valid) {
    return { success: false, error: passwordCheck.message };
  }
  
  // 3. 检查新密码是否与旧密码相同
  const user = await findUserById(userId!);
  const samePassword = await verifyPassword(newPassword, user.password);
  
  if (samePassword) {
    return { success: false, error: '新密码不能与旧密码相同' };
  }
  
  // 4. 更新密码
  const hashedPassword = await hashPassword(newPassword);
  await updateUserPassword(userId!, hashedPassword);
  
  // 5. 标记令牌已使用
  await markTokenAsUsed(token);
  
  // 6. 使该用户所有其他会话失效
  await invalidateAllSessions(userId!);
  
  // 7. 发送通知邮件
  await sendPasswordChangedNotification(user.email);
  
  // 8. 记录日志
  await logPasswordReset(userId!, {
    ip: getCurrentIp(),
    userAgent: getCurrentUserAgent(),
    timestamp: new Date(),
  });
  
  return { success: true };
}
```

**4. 防止Host头注入**

```typescript
async function sendResetEmail(email: string, host: string): Promise<void> {
  // 验证Host头
  const allowedHosts = [
    'yoursite.com',
    'www.yoursite.com',
  ];
  
  if (!allowedHosts.includes(host)) {
    throw new Error('Invalid host');
  }
  
  // 生成令牌
  const { token, tokenHash, expiresAt } = generateResetToken();
  
  // 使用硬编码的基础URL
  const baseUrl = process.env.BASE_URL || 'https://yoursite.com';
  const resetUrl = `${baseUrl}/reset-password?token=${token}`;
  
  // 存储和发送
  // ...
}
```

**5. 防止参数污染**

```typescript
// 错误做法 ❌
async function resetPasswordWrong(body: { token?: string; email?: string; newPassword: string }) {
  const { token, email, newPassword } = body;
  
  // 危险：同时接受token和email
  if (token) {
    const userId = await verifyToken(token);
    await updatePassword(email!, newPassword);  // 可能不匹配！
  }
}

// 正确做法 ✅
interface ResetPasswordRequest {
  token: string;      // 只接受token
  newPassword: string;
  // 不接受email参数
}

async function resetPasswordCorrect(body: ResetPasswordRequest) {
  const { token, newPassword } = body;
  
  // 从令牌中获取userId
  const { valid, userId } = await verifyResetToken(token);
  
  if (!valid) {
    throw new Error('Invalid token');
  }
  
  // 使用userId更新密码（不信任用户输入的email）
  await updatePasswordByUserId(userId!, newPassword);
}
```

**6. 数据库设计**

```sql
-- 密码重置令牌表
CREATE TABLE password_reset_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash VARCHAR(64) NOT NULL,  -- SHA256哈希，不存储明文
  expires_at TIMESTAMP NOT NULL,
  used BOOLEAN DEFAULT FALSE,
  used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- 索引
  INDEX idx_token_hash (token_hash),
  INDEX idx_user_id (user_id),
  INDEX idx_expires_at (expires_at)
);

-- 定期清理过期令牌
CREATE OR REPLACE FUNCTION cleanup_expired_tokens() RETURNS void AS $$
BEGIN
  DELETE FROM password_reset_tokens 
  WHERE expires_at < NOW() - INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;
```

**局限性**：
- 需要自己实现所有安全逻辑
- 需要维护邮件发送服务
- 需要定期清理过期令牌

---

#### 方案B：使用认证服务（推荐）

**使用 Auth0 密码重置**

```javascript
import { Auth0Client } from '@auth0/auth0-spa-js';

// Auth0 自动提供安全的密码重置
const auth0 = new Auth0Client({
  domain: 'your-domain.auth0.com',
  client_id: 'your-client-id',
});

// 请求重置
await auth0.changePassword({
  email: 'user@example.com',
  connection: 'Username-Password-Authentication',
});

// Auth0 自动：
// - 生成安全令牌
// - 设置过期时间
// - 发送重置邮件
// - 验证令牌
// - 通知用户

// 自定义邮件模板
// Auth0 Dashboard > Emails > Templates > Change Password
```

**使用 Supabase Auth**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// 请求重置
const { error } = await supabase.auth.resetPasswordForEmail(
  'user@example.com',
  {
    redirectTo: 'https://yoursite.com/reset-password',
  }
)

// 用户点击邮件链接后
const { data, error } = await supabase.auth.updateUser({
  password: 'newPassword123',
})

// Supabase 自动提供：
// - 安全令牌（JWT）
// - 短过期时间
// - 单次使用
// - 邮件通知
// - 会话管理
```

**优势**：
- 开箱即用的安全实现
- 自动令牌管理
- 邮件模板可定制
- 完整审计日志
- 免费额度充足

---

#### 方案C：增强方案（+$10-20/月）

在方案B基础上添加：

**1. 异地重置检测**

```typescript
async function detectAnomalousReset(userId: string, currentIp: string): Promise<{
  suspicious: boolean;
  reason?: string;
}> {
  // 获取用户常用IP
  const recentLogins = await getRecentLogins(userId, 30);  // 最近30天
  
  const commonIPs = recentLogins.map(l => l.ip);
  
  if (!commonIPs.includes(currentIp)) {
    // 异地重置
    const location = await getIPLocation(currentIp);
    
    // 发送额外验证邮件
    await sendVerificationEmail(userId, {
      type: 'suspicious_reset',
      location,
    });
    
    return {
      suspicious: true,
      reason: `检测到异地重置请求：${location.city}, ${location.country}`,
    };
  }
  
  return { suspicious: false };
}

// 处理重置请求
if (resetRequest.suspicious) {
  // 要求额外的邮箱验证
  await sendVerificationCode(userId);
  // 用户需输入验证码才能继续
}
```

**2. 重置冷却期**

```typescript
async function checkResetCooldown(userId: string): Promise<{
  allowed: boolean;
  remainingTime?: number;
}> {
  const lastReset = await getLastPasswordReset(userId);
  
  if (lastReset) {
    const cooldownPeriod = 24 * 60 * 60 * 1000;  // 24小时
    const elapsed = Date.now() - lastReset.getTime();
    
    if (elapsed < cooldownPeriod) {
      return {
        allowed: false,
        remainingTime: cooldownPeriod - elapsed,
      };
    }
  }
  
  return { allowed: true };
}

// 防止频繁重置
const { allowed, remainingTime } = await checkResetCooldown(userId);
if (!allowed) {
  throw new Error(`请在 ${formatTime(remainingTime)} 后再尝试`);
}
```

**3. 可疑行为监控**

```typescript
// 监控异常重置模式
async function monitorResetPatterns(): Promise<void> {
  // 1. 同一IP大量重置请求
  const ipStats = await getResetStatsByIP();
  
  for (const stat of ipStats) {
    if (stat.count > 10) {  // 同一IP超过10次请求
      await alertSuspiciousActivity({
        type: 'mass_reset_from_single_ip',
        ip: stat.ip,
        count: stat.count,
      });
    }
  }
  
  // 2. 同一邮箱频繁请求
  const emailStats = await getResetStatsByEmail();
  
  for (const stat of emailStats) {
    if (stat.count > 5) {  // 同一邮箱超过5次请求
      await alertSuspiciousActivity({
        type: 'frequent_reset_requests',
        email: stat.email,
        count: stat.count,
      });
      
      // 临时禁止该邮箱的重置请求
      await blockResetRequests(stat.email, 60);  // 60分钟
    }
  }
}
```

---

### 决策树

```
你的密码重置功能是否存在？
├── 否 → 无需关注
└── 是 →
    重置令牌是否随机且长度足够（≥64字符）？
    ├── 否 → 立即修改（方案A）
    └── 是 →
        令牌是否有过期时间（≤15分钟）？
        ├── 否 → 添加过期时间
        └── 是 →
            令牌是否单次使用？
            ├── 否 → 实现单次使用
            └── 是 →
                重置后是否通知用户？
                ├── 否 → 添加邮件通知
                └── 是 → 基础防护完成
                
                是否处理敏感数据？
                ├── 是 → 添加异地检测 + 可疑监控（方案C）
                └── 否 → 基础防护足够
```

### 完整代码示例

**Next.js 完整密码重置实现**

```typescript
// app/api/auth/forgot-password/route.ts
import { NextResponse } from 'next/server';
import { randomBytes, createHash } from 'crypto';
import { prisma } from '@/lib/prisma';
import { sendEmail } from '@/lib/email';

export async function POST(req: Request) {
  try {
    const { email } = await req.json();
    
    if (!email) {
      return NextResponse.json(
        { error: '请输入邮箱地址' },
        { status: 400 }
      );
    }
    
    // 查找用户（不暴露是否存在）
    const user = await prisma.user.findUnique({
      where: { email: email.toLowerCase() },
    });
    
    // 即使不存在也返回成功（防止账号枚举）
    if (!user) {
      return NextResponse.json({ success: true });
    }
    
    // 检查冷却期
    const lastRequest = await prisma.passwordResetToken.findFirst({
      where: {
        userId: user.id,
        createdAt: {
          gte: new Date(Date.now() - 60 * 1000),  // 1分钟内
        },
      },
    });
    
    if (lastRequest) {
      return NextResponse.json(
        { error: '请求过于频繁，请稍后再试' },
        { status: 429 }
      );
    }
    
    // 使旧令牌失效
    await prisma.passwordResetToken.updateMany({
      where: { userId: user.id, used: false },
      data: { expiresAt: new Date() },  // 立即过期
    });
    
    // 生成新令牌
    const token = randomBytes(32).toString('hex');
    const tokenHash = createHash('sha256').update(token).digest('hex');
    
    // 存储令牌
    await prisma.passwordResetToken.create({
      data: {
        userId: user.id,
        tokenHash,
        expiresAt: new Date(Date.now() + 15 * 60 * 1000),  // 15分钟
      },
    });
    
    // 发送邮件
    const resetUrl = `${process.env.NEXT_PUBLIC_BASE_URL}/reset-password?token=${token}`;
    
    await sendEmail({
      to: user.email,
      subject: '重置您的密码',
      html: `
        <h1>密码重置</h1>
        <p>您收到这封邮件是因为有人请求重置您的密码。</p>
        <p>点击下面的链接重置密码：</p>
        <a href="${resetUrl}">${resetUrl}</a>
        <p>此链接将在15分钟后过期。</p>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
      `,
    });
    
    return NextResponse.json({ success: true });
    
  } catch (error) {
    console.error('Forgot password error:', error);
    return NextResponse.json(
      { error: '服务器错误，请稍后重试' },
      { status: 500 }
    );
  }
}
```

```typescript
// app/api/auth/reset-password/route.ts
import { NextResponse } from 'next/server';
import { createHash } from 'crypto';
import { prisma } from '@/lib/prisma';
import { hashPassword, verifyPassword } from '@/lib/auth';
import { sendEmail } from '@/lib/email';

export async function POST(req: Request) {
  try {
    const { token, newPassword } = await req.json();
    
    if (!token || !newPassword) {
      return NextResponse.json(
        { error: '缺少必要参数' },
        { status: 400 }
      );
    }
    
    // 验证令牌
    const tokenHash = createHash('sha256').update(token).digest('hex');
    
    const tokenRecord = await prisma.passwordResetToken.findUnique({
      where: { tokenHash },
      include: { user: true },
    });
    
    if (!tokenRecord) {
      return NextResponse.json(
        { error: '无效的重置链接' },
        { status: 400 }
      );
    }
    
    if (tokenRecord.used) {
      return NextResponse.json(
        { error: '重置链接已使用' },
        { status: 400 }
      );
    }
    
    if (new Date() > tokenRecord.expiresAt) {
      return NextResponse.json(
        { error: '重置链接已过期' },
        { status: 400 }
      );
    }
    
    // 验证密码强度
    if (newPassword.length < 8) {
      return NextResponse.json(
        { error: '密码长度至少8位' },
        { status: 400 }
      );
    }
    
    // 检查是否与旧密码相同
    const samePassword = await verifyPassword(
      newPassword,
      tokenRecord.user.password
    );
    
    if (samePassword) {
      return NextResponse.json(
        { error: '新密码不能与旧密码相同' },
        { status: 400 }
      );
    }
    
    // 更新密码
    const hashedPassword = await hashPassword(newPassword);
    
    await prisma.$transaction([
      prisma.user.update({
        where: { id: tokenRecord.userId },
        data: { password: hashedPassword },
      }),
      prisma.passwordResetToken.update({
        where: { id: tokenRecord.id },
        data: { used: true, usedAt: new Date() },
      }),
      // 使所有会话失效
      prisma.session.deleteMany({
        where: { userId: tokenRecord.userId },
      }),
    ]);
    
    // 发送通知邮件
    await sendEmail({
      to: tokenRecord.user.email,
      subject: '密码已更改',
      html: `
        <h1>密码更改通知</h1>
        <p>您的密码已成功更改。</p>
        <p>如果您没有进行此操作，请立即联系客服。</p>
      `,
    });
    
    return NextResponse.json({ success: true });
    
  } catch (error) {
    console.error('Reset password error:', error);
    return NextResponse.json(
      { error: '服务器错误，请稍后重试' },
      { status: 500 }
    );
  }
}
```

---

## L3 企业版（深耕版）

企业级密码重置安全需要更完善的体系：

**1. 多因素验证**
- 短信/邮件验证码
- 安全问题
- 人工客服验证

**2. 风险评估**
- 用户行为分析
- 设备信任评分
- 地理位置验证

**3. 完整审计**
- 所有重置操作日志
- 异常行为告警
- 取证分析支持

**详细内容请参考企业级案例**：
- [企业级密码管理](../../enterprise/bizsec/auth/password-management-enterprise.md)
- [身份验证系统](../../enterprise/infosec/identity-verification.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基本实现 | $0 | 2小时 | 1小时/月 | MVP阶段 |
| L2-方案A（自建） | $0 | 4小时 | 2小时/月 | 技术团队 |
| L2-方案B（SaaS） | $0 | 1小时 | 0小时/月 | 推荐 |
| L2-方案C（增强） | $10-20 | 3小时 | 1小时/月 | 处理敏感数据 |
| L3-企业级 | $200+ | 需评估 | 专职团队 | 企业级应用 |

---

## 常见问题

**Q: 令牌过期时间应该设置为多长？**
A: 推荐设置为15-30分钟。过短影响用户体验，过长增加安全风险。

**Q: 如何防止账号枚举？**
A: 
- 不返回"用户不存在"错误，统一返回"如果邮箱存在，将收到重置邮件"
- 避免重置页面显示用户信息
- 使用相同的响应时间

**Q: 令牌应该存储明文还是哈希？**
A: 必须存储哈希值。如果数据库泄露，攻击者无法直接使用令牌。

**Q: 如何处理用户声称"我没有请求重置"？**
A: 
- 记录每次重置请求的IP和时间
- 如果是异常IP，发送安全提醒
- 提供"撤销重置请求"的功能

**Q: 重置后是否应该强制所有设备登出？**
A: 是的。重置密码后，应使所有会话失效，要求重新登录。

---

## 相关资源

**工具**
- [SendGrid](https://sendgrid.com/) - 邮件发送服务
- [Resend](https://resend.com/) - 开发者邮件服务
- [Auth0](https://auth0.com/) - 认证服务
- [Supabase Auth](https://supabase.com/auth) - 开源认证服务

**学习资源**
- [OWASP Password Reset Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Password Reset Best Practices](https://www.troyhunt.com/password-reset-best-practices/)

**相关案例**
- [弱密码风险](./weak-password.md)
- [暴力破解](./brute-force.md)
- [Session劫持](./session-hijacking.md)
