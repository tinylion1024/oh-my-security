# OAuth 配置错误（OAuth Misconfiguration）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
OAuth回调URL配置不当，攻击者构造恶意链接窃取授权码，导致账号被劫持、用户数据泄露。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用第三方登录（Google/GitHub/微信等）
- [ ] OAuth回调URL使用通配符（如 *.example.com）
- [ ] OAuth回调URL未严格限制（包含localhost或多个域名）
- [ ] state参数未验证或可预测
- [ ] 未绑定OAuth用户唯一标识（sub）到本地账号
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
OAuth回调URL严格白名单 + 验证state参数 + 绑定唯一标识符（sub）到账号。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查所有OAuth配置，回调URL只保留生产域名
   - [ ] 移除localhost、通配符等不安全配置
   - [ ] 实现并验证state参数（随机值+Session绑定）

2. **短期行动**（本周可完成，免费）
   - [ ] 绑定OAuth唯一标识（sub）到本地账号，而非邮箱
   - [ ] 添加回调URL来源验证
   - [ ] 记录OAuth登录日志（IP、时间、Provider）

3. **长期行动**（规划中，免费）
   - [ ] 定期审查OAuth配置
   - [ ] 添加异常登录检测（OAuth登录+新设备）
   - [ ] 用户可查看和管理第三方授权

### 推荐工具
- **免费**：
  - [OAuth 2.0 Security Best Practices](https://oauth.net/2/oauth-best-practice/) - 官方最佳实践
  - [Auth0](https://auth0.com/) - 自动安全配置，免费7000用户/月
  - [NextAuth.js](https://next-auth.js.org/) - 开源OAuth实现

- **低成本**：
  - [Supabase Auth](https://supabase.com/auth) - OAuth集成，免费50000用户/月
  - [Clerk](https://clerk.com/) - OAuth + 用户管理，免费5000 MAU

### 验证方法
- [ ] 测试步骤1：检查OAuth配置，回调URL应只有生产域名
- [ ] 测试步骤2：尝试使用修改后的state参数，应被拒绝
- [ ] 测试步骤3：尝试使用未注册的回调URL，应被拒绝
- [ ] 测试步骤4：同一OAuth账号用不同邮箱登录，应关联到同一本地账号

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品支持Google和GitHub登录，某天用户反馈"我的账号被别人登录了"。调查发现：

**攻击场景**：
1. 攻击者发现你的OAuth回调URL配置为 `*.example.com`
2. 攻击者构造恶意链接：`https://evil.com/callback?code=xxx`
3. 诱骗用户点击，授权码被发送到攻击者服务器
4. 攻击者使用授权码换取access_token
5. 攻击者获取用户身份，登录你的产品

**真实案例（2024）**：
某独立开发者的产品使用GitHub登录，回调URL配置了 `http://localhost:3000/callback` 用于开发调试。攻击者注册域名 `localhost.com`，诱导用户访问：
```
https://github.com/login/oauth/authorize?
  client_id=YOUR_CLIENT_ID&
  redirect_uri=http://localhost.com/callback&
  state=attacker_controlled
```
用户授权后，授权码发送到攻击者控制的服务器，导致账号劫持。

### 攻击路径（简化版）

**攻击方式1：开放重定向URI**

**前提条件**：
- OAuth回调URL配置宽松（通配符、localhost等）

**攻击步骤**：
1. 攻击者发现回调URL配置：`*.example.com`
2. 注册恶意域名：`attacker.example.com.evil.com`（如果配置错误可能匹配）
3. 构造钓鱼链接，诱导用户授权
4. 授权码被发送到攻击者服务器
5. 攻击者用授权码换取token，登录受害者账号

**攻击方式2：State参数攻击**

**前提条件**：
- state参数未验证或可预测

**攻击步骤**：
1. 攻击者发起OAuth流程，获取合法state
2. 诱骗受害者点击包含攻击者state的链接
3. 受害者授权后，token关联到攻击者的Session
4. 攻击者使用受害者的OAuth身份登录

**攻击方式3：账号劫持（邮箱不一致）**

**前提条件**：
- OAuth登录仅通过邮箱绑定账号
- 用户OAuth邮箱可修改

**攻击步骤**：
1. 攻击者注册账号：attacker@evil.com
2. 攻击者在OAuth Provider（如GitHub）修改邮箱为victim@example.com
3. 攻击者用GitHub登录你的产品
4. 系统匹配邮箱，关联到受害者账号
5. 攻击者成功劫持账号

### 防御实施（低成本方案）

#### 方案A：免费方案（正确配置OAuth）

**1. OAuth安全配置清单**

```yaml
# OAuth 安全配置检查清单

✅ 回调URL配置：
  - 只使用生产域名（https://yoursite.com/callback）
  - 禁止通配符（*.example.com）
  - 禁止localhost（除非开发环境专用OAuth应用）
  - 禁止HTTP（除非本地开发）
  - 精确匹配，不依赖后缀匹配

✅ State参数：
  - 使用加密安全的随机值
  - 绑定到用户Session
  - 验证返回的state与发起时一致
  - 单次使用，用后即弃

✅ 用户标识：
  - 绑定OAuth唯一标识（sub）到本地账号
  - 不要仅依赖邮箱（邮箱可修改）
  - 记录Provider + sub的组合

✅ Token处理：
  - 不要在URL中传递token
  - 使用PKCE（针对公开客户端）
  - Token存储在服务端Session或安全Cookie
```

**2. State参数安全实现**

```typescript
// 生成和验证state参数
import { randomBytes, createHash } from 'crypto';

// 生成state
function generateState(sessionId: string): string {
  // 1. 随机值
  const random = randomBytes(16).toString('hex');
  
  // 2. 绑定Session（可选，用于验证）
  const sessionHash = createHash('sha256')
    .update(sessionId + process.env.STATE_SECRET)
    .digest('hex')
    .substring(0, 16);
  
  // 3. 组合：随机值 + Session哈希
  return `${random}.${sessionHash}`;
}

// 验证state
function verifyState(state: string, sessionId: string): boolean {
  try {
    const [random, sessionHash] = state.split('.');
    
    // 重新计算Session哈希
    const expectedHash = createHash('sha256')
      .update(sessionId + process.env.STATE_SECRET)
      .digest('hex')
      .substring(0, 16);
    
    return sessionHash === expectedHash;
  } catch {
    return false;
  }
}

// 使用示例
app.get('/auth/google', (req, res) => {
  const state = generateState(req.session.id);
  
  // 保存state到Session
  req.session.oauthState = state;
  
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  authUrl.searchParams.set('client_id', process.env.GOOGLE_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', 'https://yoursite.com/auth/google/callback');
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('state', state);  // 关键：传递state
  authUrl.searchParams.set('scope', 'openid email profile');
  
  res.redirect(authUrl.toString());
});

app.get('/auth/google/callback', async (req, res) => {
  const { code, state } = req.query;
  
  // 关键：验证state
  if (!verifyState(state as string, req.session.id)) {
    return res.status(400).json({ error: 'Invalid state parameter' });
  }
  
  // 检查是否已使用（防止重放）
  if (req.session.oauthState !== state) {
    return res.status(400).json({ error: 'State mismatch' });
  }
  
  // 清除已使用的state
  delete req.session.oauthState;
  
  // 继续OAuth流程...
});
```

**3. 绑定OAuth唯一标识（sub）**

```typescript
// 正确的OAuth用户绑定
interface OAuthUser {
  provider: string;  // 'google' | 'github' | 'twitter'
  sub: string;       // OAuth Provider的唯一标识
  email: string;
  name: string;
  picture?: string;
}

async function handleOAuthLogin(oauthUser: OAuthUser) {
  // 错误做法：仅通过邮箱查找
  // let user = await findUserByEmail(oauthUser.email);
  
  // 正确做法：通过 Provider + sub 查找
  let user = await findUserByOAuthId(oauthUser.provider, oauthUser.sub);
  
  if (!user) {
    // 检查邮箱是否已注册（可选：自动关联）
    const existingUser = await findUserByEmail(oauthUser.email);
    
    if (existingUser) {
      // 关联OAuth账号到现有用户
      await linkOAuthAccount(existingUser.id, oauthUser);
      user = existingUser;
    } else {
      // 创建新用户
      user = await createUser({
        email: oauthUser.email,
        name: oauthUser.name,
        picture: oauthUser.picture,
      });
      
      // 保存OAuth绑定
      await linkOAuthAccount(user.id, oauthUser);
    }
  }
  
  // 更新用户信息（可选）
  await updateUserProfile(user.id, {
    email: oauthUser.email,  // 邮箱可能在Provider中已修改
    name: oauthUser.name,
    picture: oauthUser.picture,
  });
  
  return user;
}

// 数据库设计
// users 表:
// - id, email, name, created_at, ...
//
// oauth_accounts 表:
// - id
// - user_id (外键到users)
// - provider ('google', 'github', etc.)
// - provider_user_id (sub)
// - created_at
//
// 唯一约束: (provider, provider_user_id)
```

**4. 回调URL严格验证**

```typescript
// OAuth Provider配置（示例：Google）

// 错误配置 ❌
const wrongConfig = {
  redirect_uris: [
    'http://localhost:3000/callback',  // 不应在生产配置中
    'https://*.yoursite.com/callback', // 通配符危险
    'https://yoursite.com',            // 不精确
  ]
};

// 正确配置 ✅
const correctConfig = {
  redirect_uris: [
    'https://yoursite.com/auth/google/callback',  // 精确路径
    'https://www.yoursite.com/auth/google/callback',
  ],
  
  // 如果需要多个环境，创建不同的OAuth应用
  // 生产环境: 使用生产专用配置
  // 开发环境: 使用开发专用配置（不同的client_id）
};

// 运行时验证
function validateRedirectUri(redirectUri: string): boolean {
  const allowedUris = [
    'https://yoursite.com/auth/google/callback',
    'https://www.yoursite.com/auth/google/callback',
  ];
  
  // 精确匹配，不使用正则或通配符
  return allowedUris.includes(redirectUri);
}
```

**5. PKCE保护（增强安全）**

```typescript
// PKCE (Proof Key for Code Exchange) for OAuth 2.0
import { randomBytes, createHash } from 'crypto';

function base64URLEncode(buffer: Buffer): string {
  return buffer
    .toString('base64')
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

function generatePKCE(): { verifier: string; challenge: string } {
  // 1. 生成code_verifier（43-128字符）
  const verifier = base64URLEncode(randomBytes(32));
  
  // 2. 生成code_challenge（SHA256哈希）
  const challenge = base64URLEncode(
    createHash('sha256').update(verifier).digest()
  );
  
  return { verifier, challenge };
}

// 发起OAuth请求时
app.get('/auth/google', (req, res) => {
  const { verifier, challenge } = generatePKCE();
  
  // 保存verifier到Session
  req.session.codeVerifier = verifier;
  
  const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
  authUrl.searchParams.set('client_id', process.env.GOOGLE_CLIENT_ID);
  authUrl.searchParams.set('redirect_uri', 'https://yoursite.com/auth/google/callback');
  authUrl.searchParams.set('response_type', 'code');
  authUrl.searchParams.set('state', generateState(req.session.id));
  authUrl.searchParams.set('code_challenge', challenge);
  authUrl.searchParams.set('code_challenge_method', 'S256');
  
  res.redirect(authUrl.toString());
});

// 接收回调时
app.get('/auth/google/callback', async (req, res) => {
  const { code, state } = req.query;
  
  // 验证state...
  
  // 使用code + code_verifier换取token
  const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      client_id: process.env.GOOGLE_CLIENT_ID,
      client_secret: process.env.GOOGLE_CLIENT_SECRET,
      code: code as string,
      code_verifier: req.session.codeVerifier,  // 关键
      grant_type: 'authorization_code',
      redirect_uri: 'https://yoursite.com/auth/google/callback',
    }),
  });
  
  // 清除verifier
  delete req.session.codeVerifier;
  
  // 处理token...
});
```

**局限性**：
- 需要自己实现所有安全逻辑
- 需要维护多个环境配置
- 需要定期审查配置

---

#### 方案B：使用成熟框架（推荐）

**使用 NextAuth.js**

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      // NextAuth自动处理state、PKCE等
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],
  
  callbacks: {
    async signIn({ user, account, profile }) {
      // 关键：绑定Provider + sub到本地账号
      const existingUser = await db.user.findFirst({
        where: {
          accounts: {
            some: {
              provider: account.provider,
              providerAccountId: account.providerAccountId, // sub
            }
          }
        }
      });
      
      if (existingUser) {
        return true;  // 允许登录
      }
      
      // 检查邮箱是否已存在
      const emailUser = await db.user.findUnique({
        where: { email: user.email! }
      });
      
      if (emailUser) {
        // 关联OAuth账号
        await db.account.create({
          data: {
            userId: emailUser.id,
            type: account.type,
            provider: account.provider,
            providerAccountId: account.providerAccountId,
            access_token: account.access_token,
          }
        });
        return true;
      }
      
      // 创建新用户
      return true;
    },
    
    async session({ session, user }) {
      // 自定义Session
      session.user.id = user.id;
      return session;
    },
  },
  
  // 安全配置（NextAuth默认启用）
  useSecureCookies: process.env.NODE_ENV === 'production',
  cookies: {
    sessionToken: {
      name: `__Secure-next-auth.session-token`,
      options: {
        httpOnly: true,
        sameSite: 'lax',
        path: '/',
        secure: true,
      },
    },
  },
});

export { handler as GET, handler as POST };
```

**使用 Supabase Auth**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// 发起OAuth登录
async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: 'https://yoursite.com/auth/callback',
      // Supabase自动处理state验证
      queryParams: {
        access_type: 'offline',
        prompt: 'consent',
      }
    }
  })
  
  if (error) throw error
  // 重定向到OAuth Provider
  window.location.href = data.url
}

// 处理回调（Supabase自动验证state）
async function handleCallback() {
  const { data: { session }, error } = await supabase.auth.getSession()
  
  if (error) throw error
  
  // Supabase自动绑定：
  // - Provider
  // - Provider Account ID (sub)
  // 到auth.users表
}
```

**优势**：
- 自动处理state验证
- 自动PKCE保护
- 自动Session管理
- 内置安全配置
- 开箱即用

---

### 常见配置错误示例

| 错误配置 | 风险 | 正确配置 |
|---------|------|---------|
| `redirect_uri: *.example.com` | 通配符匹配恶意域名 | 精确指定完整URL |
| `redirect_uri: http://localhost:3000`（生产） | 开发环境泄露到生产 | 生产环境删除此配置 |
| 不验证state参数 | CSRF攻击 | 生成、绑定、验证state |
| 仅绑定邮箱 | 邮箱修改导致劫持 | 绑定Provider+sub |
| state使用可预测值 | 可被猜测绕过 | 使用加密随机值 |
| 不使用PKCE | 授权码拦截 | 启用PKCE（S256） |

---

### 决策树

```
你使用OAuth登录吗？
├── 否 → 无需关注
└── 是 →
    回调URL是否使用通配符？
    ├── 是 → 立即修改为精确URL
    └── 否 →
        是否验证state参数？
        ├── 否 → 立即实现state验证
        └── 是 →
            是否绑定OAuth唯一标识（sub）？
            ├── 否 → 修改为绑定Provider+sub
            └── 是 → 基础防护完成
            
            是否使用PKCE？
            ├── 否 → 建议启用（增强保护）
            └── 是 → 防护完善
```

### 完整代码示例

**Next.js + NextAuth 完整OAuth实现**

```typescript
// lib/auth.ts
import { NextAuthOptions } from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import { PrismaAdapter } from '@next-auth/prisma-adapter';
import { prisma } from './prisma';

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      authorization: {
        params: {
          prompt: 'consent',
          access_type: 'offline',
          scope: 'openid email profile',
        },
      },
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
      authorization: {
        params: {
          scope: 'read:user user:email',
        },
      },
    }),
  ],
  
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30天
  },
  
  pages: {
    signIn: '/login',
    error: '/auth/error',
  },
  
  callbacks: {
    async signIn({ user, account, profile }) {
      // 记录OAuth登录日志
      await prisma.loginLog.create({
        data: {
          userId: user.id,
          provider: account.provider,
          providerAccountId: account.providerAccountId,
          ip: '...', // 从请求中获取
          userAgent: '...',
          timestamp: new Date(),
        }
      });
      
      return true;
    },
    
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string;
      }
      return session;
    },
  },
  
  events: {
    async signIn({ user, account }) {
      console.log(`OAuth login: ${account.provider} - ${user.email}`);
    },
  },
  
  debug: process.env.NODE_ENV === 'development',
};
```

---

## L3 企业版（深耕版）

企业级OAuth安全需要更完善的体系：

**1. 多Provider统一管理**
- 统一身份映射
- 多因素认证集成
- 风险自适应登录

**2. 高级监控**
- OAuth登录审计
- 异常行为检测
- Provider可用性监控

**3. 合规要求**
- GDPR数据处理
- SOC 2审计日志
- 隐私政策集成

**详细内容请参考企业级案例**：
- [企业级OAuth实施](../../enterprise/bizsec/auth/oauth-enterprise.md)
- [身份联合](../../enterprise/infosec/identity-federation.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基本配置 | $0 | 1小时 | 0.5小时/月 | MVP阶段 |
| L2-方案A（自建） | $0 | 4小时 | 1小时/月 | 技术团队 |
| L2-方案B（框架） | $0 | 2小时 | 0小时/月 | 推荐 |
| L3-企业级 | $200+ | 需评估 | 专职团队 | 企业级应用 |

---

## 常见问题

**Q: 为什么不能只用邮箱绑定OAuth账号？**
A: 用户可以在OAuth Provider中修改邮箱，如果只用邮箱绑定，攻击者修改邮箱后可能劫持其他用户的账号。sub是OAuth Provider保证的唯一标识。

**Q: 开发环境如何配置OAuth？**
A: 创建单独的OAuth应用用于开发环境：
- 使用不同的client_id/client_secret
- 配置localhost回调URL
- 绝不要在生产的OAuth应用中配置localhost

**Q: state参数为什么要绑定Session？**
A: 防止CSRF攻击。如果不绑定Session，攻击者可以构造一个合法的state，诱导受害者完成OAuth流程，受害者登录到攻击者的Session。

**Q: PKCE是必须的吗？**
A: 对于公开客户端（如SPA、移动应用），强烈推荐使用PKCE。对于服务端应用，client_secret已提供保护，但PKCE仍可增强安全性。

**Q: 如何处理OAuth Provider的用户信息变更？**
A: 每次登录时同步用户信息，但核心绑定关系（Provider+sub）不变。如果邮箱变更，可发送通知邮件。

---

## 相关资源

**工具**
- [NextAuth.js](https://next-auth.js.org/) - Next.js OAuth解决方案
- [Auth0](https://auth0.com/) - 企业级认证服务
- [Supabase Auth](https://supabase.com/auth) - 开源认证服务

**学习资源**
- [OAuth 2.0 Security Best Practices](https://oauth.net/2/oauth-best-practice/)
- [OAuth 2.0 Threat Model](https://datatracker.ietf.org/doc/html/rfc6819)
- [OWASP OAuth Security](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Authentication_Testing/09-Testing_for_OAuth_Authentication_Vulnerabilities)

**相关案例**
- [Session劫持](./session-hijacking.md)
- [CSRF攻击](../api/csrf.md)
- [账号劫持](./account-takeover.md)
