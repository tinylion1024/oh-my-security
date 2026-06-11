# 社交登录风险（Social Login Risk）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
第三方登录实现不当，导致账号关联错误、账号劫持、或用户无法正常使用，甚至造成用户数据泄露。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 提供第三方登录（Google、GitHub、微信等）
- [ ] 未验证OAuth回调URL
- [ ] 同一邮箱对应多个社交账号时未处理合并逻辑
- [ ] 未验证OAuth state参数
- [ ] 存储OAuth access token到数据库
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
严格验证OAuth回调URL和state参数 + 正确处理账号关联逻辑 + 不存储access token。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查OAuth回调：确保redirect_uri完全匹配
   - [ ] 验证state参数：防止CSRF攻击
   - [ ] 检查账号关联：同一邮箱多个社交账号的处理逻辑
   - [ ] 测试登录流程：使用不同社交账号登录

2. **短期行动**（本周可完成，免费）
   - [ ] 实现账号绑定流程：允许用户绑定/解绑社交账号
   - [ ] 添加登录确认：首次使用社交账号登录时要求确认
   - [ ] 实现账号合并功能：允许用户合并重复账号
   - [ ] 记录社交登录日志：provider、email、时间

3. **长期行动**（规划中，免费）
   - [ ] 实现多重身份验证
   - [ ] 添加社交账号管理页面
   - [ ] 建立异常登录检测机制

### 推荐工具
- **免费**：
  - [NextAuth.js](https://next-auth.js.org/) - Next.js完整认证方案
  - [Passport.js](http://www.passportjs.org/) - Node.js认证中间件
  - [Auth.js](https://authjs.dev/) - 现代Web应用认证

- **低成本**：
  - [Auth0](https://auth0.com/) - 免费额度7000活跃用户/月
  - [Supabase Auth](https://supabase.com/auth) - 免费50000活跃用户/月

### 验证方法
- [ ] 测试步骤1：使用同一邮箱的Google和GitHub登录，确认账号关联正确
- [ ] 测试步骤2：尝试修改redirect_uri，确认被拒绝
- [ ] 测试步骤3：不使用state参数尝试登录，确认被拒绝
- [ ] 测试步骤4：检查数据库，确认未存储access token

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品提供Google和GitHub社交登录，某天收到多个用户投诉：

**案例1：账号劫持**
- 用户A使用Google登录注册账号
- 攻击者创建一个与用户A相同邮箱的GitHub账号
- 使用GitHub登录你的产品，系统自动关联到用户A的账号
- 攻击者成功接管用户A的账号

**案例2：账号重复**
- 用户B先用邮箱注册，未验证邮箱
- 后使用Google登录（相同邮箱）
- 系统创建了两个独立账号
- 用户困惑，数据分散在两个账号中

**案例3：OAuth回调劫持**
- 攻击者修改OAuth回调URL
- 将authorization code重定向到攻击者服务器
- 使用窃取的code访问用户账号

你的数据库显示：
```
用户ID | 邮箱 | 注册方式
001   | user@example.com | email_password
002   | user@example.com | google
→ 同一邮箱，两个账号，数据混乱
```

### 攻击路径（简化版）

**路径1：账号劫持**
1. 攻击者发现目标用户邮箱（如LinkedIn、GitHub）
2. 在社交平台创建相同邮箱的账号（某些平台不验证邮箱）
3. 使用该社交账号登录你的产品
4. 系统根据邮箱自动关联，或创建新账号
5. 如果自动关联，攻击者获得目标用户账号访问权

**路径2：OAuth回调劫持**
1. 攻击者构造恶意链接：修改redirect_uri参数
2. 诱导用户点击恶意登录链接
3. OAuth provider将authorization code发送到攻击者服务器
4. 攻击者使用code换取access token
5. 使用token访问用户账号

**路径3：State参数CSRF**
1. 攻击者生成自己的OAuth state
2. 诱导用户点击包含攻击者state的登录链接
3. 用户授权后，系统使用攻击者的state验证
4. 攻击者的账号与用户的OAuth关联
5. 攻击者可以使用自己的OAuth登录用户账号

### 防御实施（免费方案）

#### OAuth安全实现

```typescript
// lib/oauth-security.ts
import { NextApiRequest, NextApiResponse } from 'next'
import { randomBytes } from 'crypto'

/**
 * OAuth安全配置
 */
export class OAuthSecurity {
  /**
   * 生成state参数（防止CSRF）
   */
  static generateState(): string {
    // 生成随机state
    const state = randomBytes(32).toString('hex')

    // 存储state到session（用于后续验证）
    // 实际应使用Redis或Session存储
    return state
  }

  /**
   * 验证state参数
   */
  static verifyState(state: string, storedState: string): boolean {
    // 使用常量时间比较，防止时序攻击
    return this.constantTimeCompare(state, storedState)
  }

  /**
   * 验证redirect_uri
   */
  static validateRedirectUri(redirectUri: string): boolean {
    // 白名单验证
    const allowedUris = [
      'https://yourapp.com/api/auth/callback/google',
      'https://yourapp.com/api/auth/callback/github',
      'http://localhost:3000/api/auth/callback/google', // 开发环境
    ]

    return allowedUris.includes(redirectUri)
  }

  /**
   * 常量时间比较
   */
  private static constantTimeCompare(a: string, b: string): boolean {
    if (a.length !== b.length) {
      return false
    }

    let result = 0
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i)
    }

    return result === 0
  }
}
```

#### 完整OAuth流程

```typescript
// app/api/auth/oauth/[provider]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { OAuthSecurity } from '@/lib/oauth-security'

const OAUTH_PROVIDERS = {
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    clientId: process.env.GOOGLE_CLIENT_ID!,
    scope: 'openid email profile',
  },
  github: {
    authUrl: 'https://github.com/login/oauth/authorize',
    clientId: process.env.GITHUB_CLIENT_ID!,
    scope: 'user:email',
  },
}

/**
 * 发起OAuth登录
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { provider: string } }
) {
  const provider = params.provider
  const config = OAUTH_PROVIDERS[provider]

  if (!config) {
    return NextResponse.json({ error: '不支持的登录方式' }, { status: 400 })
  }

  // ✅ 1. 生成并存储state
  const state = OAuthSecurity.generateState()
  // 存储到session或cookie
  const stateCookie = `oauth_state_${provider}=${state}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=600`

  // ✅ 2. 构造授权URL
  const redirectUri = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/callback/${provider}`

  const authUrl = new URL(config.authUrl)
  authUrl.searchParams.set('client_id', config.clientId)
  authUrl.searchParams.set('redirect_uri', redirectUri)
  authUrl.searchParams.set('response_type', 'code')
  authUrl.searchParams.set('scope', config.scope)
  authUrl.searchParams.set('state', state)

  // ✅ 3. 重定向到OAuth provider
  return NextResponse.redirect(authUrl.toString(), {
    headers: { 'Set-Cookie': stateCookie }
  })
}
```

#### OAuth回调处理

```typescript
// app/api/auth/callback/[provider]/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { OAuthSecurity } from '@/lib/oauth-security'
import { AccountService } from '@/lib/account-service'

/**
 * OAuth回调处理
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { provider: string } }
) {
  const provider = params.provider
  const { searchParams } = new URL(request.url)

  const code = searchParams.get('code')
  const state = searchParams.get('state')
  const error = searchParams.get('error')

  // 检查错误
  if (error) {
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/login?error=${error}`
    )
  }

  // ✅ 1. 验证state（防止CSRF）
  const storedState = request.cookies.get(`oauth_state_${provider}`)?.value

  if (!state || !storedState || !OAuthSecurity.verifyState(state, storedState)) {
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/login?error=invalid_state`
    )
  }

  // 清除state cookie
  const clearStateCookie = `oauth_state_${provider}=; Path=/; HttpOnly; Secure; Max-Age=0`

  // ✅ 2. 使用code换取access token
  const redirectUri = `${process.env.NEXT_PUBLIC_APP_URL}/api/auth/callback/${provider}`
  const tokenData = await exchangeCodeForToken(provider, code, redirectUri)

  if (!tokenData) {
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/login?error=token_exchange_failed`
    )
  }

  // ✅ 3. 获取用户信息
  const userInfo = await getUserInfo(provider, tokenData.access_token)

  if (!userInfo || !userInfo.email) {
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/login?error=no_email`
    )
  }

  // ✅ 4. 检查邮箱是否已验证
  if (!userInfo.email_verified) {
    return NextResponse.redirect(
      `${process.env.NEXT_PUBLIC_APP_URL}/login?error=email_not_verified`
    )
  }

  // ✅ 5. 账号关联逻辑
  const accountResult = await AccountService.handleOAuthLogin({
    provider,
    providerUserId: userInfo.id,
    email: userInfo.email,
    name: userInfo.name,
    avatar: userInfo.picture,
  })

  // ✅ 6. 创建session（不要存储access token）
  const sessionToken = await createSession(accountResult.userId)

  // 重定向到应用
  return NextResponse.redirect(
    `${process.env.NEXT_PUBLIC_APP_URL}/dashboard`,
    {
      headers: {
        'Set-Cookie': [
          clearStateCookie,
          `session_token=${sessionToken}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800`
        ].join(', ')
      }
    }
  )
}

/**
 * 使用authorization code换取access token
 */
async function exchangeCodeForToken(
  provider: string,
  code: string,
  redirectUri: string
): Promise<any> {
  const endpoints = {
    google: 'https://oauth2.googleapis.com/token',
    github: 'https://github.com/login/oauth/access_token',
  }

  const endpoint = endpoints[provider]
  if (!endpoint) return null

  const tokenParams = new URLSearchParams({
    client_id: process.env[`${provider.toUpperCase()}_CLIENT_ID`]!,
    client_secret: process.env[`${provider.toUpperCase()}_CLIENT_SECRET`]!,
    code,
    redirect_uri: redirectUri,
    grant_type: 'authorization_code',
  })

  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
    },
    body: tokenParams.toString(),
  })

  return await response.json()
}

/**
 * 获取用户信息
 */
async function getUserInfo(provider: string, accessToken: string): Promise<any> {
  const endpoints = {
    google: 'https://www.googleapis.com/oauth2/v2/userinfo',
    github: 'https://api.github.com/user',
  }

  const endpoint = endpoints[provider]
  if (!endpoint) return null

  const response = await fetch(endpoint, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Accept': 'application/json',
    },
  })

  return await response.json()
}
```

#### 账号关联与绑定

```typescript
// lib/account-service.ts
import { db } from '@/lib/database'

/**
 * 账号服务 - 处理账号关联
 */
export class AccountService {
  /**
   * 处理OAuth登录
   */
  static async handleOAuthLogin(data: {
    provider: string
    providerUserId: string
    email: string
    name?: string
    avatar?: string
  }) {
    // 1. 检查是否已存在OAuth账号关联
    const existingOAuth = await db.account.findFirst({
      where: {
        provider: data.provider,
        providerUserId: data.providerUserId,
      },
      include: { user: true },
    })

    if (existingOAuth) {
      // 已关联，直接登录
      return {
        userId: existingOAuth.userId,
        isNewUser: false,
        action: 'login',
      }
    }

    // 2. 检查邮箱是否已存在
    const existingUser = await db.user.findUnique({
      where: { email: data.email },
      include: { accounts: true },
    })

    if (existingUser) {
      // ✅ 关键：正确处理账号关联
      // 检查该邮箱是否已有其他OAuth provider
      const hasOtherProvider = existingUser.accounts.some(
        acc => acc.provider !== data.provider
      )

      if (hasOtherProvider) {
        // 已有其他provider，自动关联
        await db.account.create({
          data: {
            userId: existingUser.id,
            provider: data.provider,
            providerUserId: data.providerUserId,
          },
        })

        return {
          userId: existingUser.id,
          isNewUser: false,
          action: 'linked',
        }
      } else {
        // 只有邮箱密码账号，需要用户确认关联
        return {
          userId: existingUser.id,
          isNewUser: false,
          action: 'confirm_link',
          message: '该邮箱已注册，是否关联社交账号？',
        }
      }
    }

    // 3. 新用户，创建账号
    const newUser = await db.user.create({
      data: {
        email: data.email,
        name: data.name,
        image: data.avatar,
        emailVerified: new Date(), // OAuth邮箱已验证
        accounts: {
          create: {
            provider: data.provider,
            providerUserId: data.providerUserId,
          },
        },
      },
    })

    return {
      userId: newUser.id,
      isNewUser: true,
      action: 'created',
    }
  }

  /**
   * 用户确认关联社交账号
   */
  static async confirmLink(data: {
    userId: string
    provider: string
    providerUserId: string
    password: string // 验证密码
  }) {
    // 验证用户密码
    const user = await db.user.findUnique({
      where: { id: data.userId },
    })

    if (!user || !user.password) {
      throw new Error('用户不存在或未设置密码')
    }

    // 验证密码
    const isValid = await verifyPassword(data.password, user.password)
    if (!isValid) {
      throw new Error('密码错误')
    }

    // 创建关联
    await db.account.create({
      data: {
        userId: data.userId,
        provider: data.provider,
        providerUserId: data.providerUserId,
      },
    })

    return { success: true }
  }

  /**
   * 获取用户的所有社交账号
   */
  static async getLinkedAccounts(userId: string) {
    const accounts = await db.account.findMany({
      where: { userId },
      select: {
        provider: true,
        createdAt: true,
      },
    })

    return accounts
  }

  /**
   * 解绑社交账号
   */
  static async unlinkAccount(userId: string, provider: string) {
    // 检查用户是否还有其他登录方式
    const accounts = await db.account.findMany({
      where: { userId },
    })

    const user = await db.user.findUnique({
      where: { id: userId },
    })

    // 如果只有一个社交账号且没有密码，不允许解绑
    if (accounts.length === 1 && !user?.password) {
      throw new Error('至少保留一种登录方式')
    }

    await db.account.deleteMany({
      where: {
        userId,
        provider,
      },
    })

    return { success: true }
  }
}
```

#### 账号管理页面

```typescript
// app/settings/accounts/page.tsx
'use client'

import { useState, useEffect } from 'react'
import { AccountService } from '@/lib/account-service'

export default function AccountSettings() {
  const [accounts, setAccounts] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAccounts()
  }, [])

  async function loadAccounts() {
    try {
      const data = await AccountService.getLinkedAccounts()
      setAccounts(data)
    } catch (error) {
      console.error('加载账号失败:', error)
    } finally {
      setLoading(false)
    }
  }

  async function handleUnlink(provider: string) {
    if (!confirm(`确定要解绑 ${provider} 账号吗？`)) {
      return
    }

    try {
      await AccountService.unlinkAccount(provider)
      await loadAccounts()
    } catch (error) {
      alert(error.message)
    }
  }

  if (loading) return <div>加载中...</div>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">账号管理</h1>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">已关联的社交账号</h2>

        {accounts.map(account => (
          <div
            key={account.provider}
            className="flex items-center justify-between p-4 border rounded"
          >
            <div>
              <p className="font-medium">{account.provider}</p>
              <p className="text-sm text-gray-500">
                关联于 {new Date(account.createdAt).toLocaleDateString()}
              </p>
            </div>

            <button
              onClick={() => handleUnlink(account.provider)}
              className="px-4 py-2 text-red-600 border border-red-600 rounded hover:bg-red-50"
            >
              解绑
            </button>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">添加其他登录方式</h2>

        <div className="flex gap-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            关联 Google
          </button>
          <button className="px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-900">
            关联 GitHub
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

### 决策树

```
你的产品是否提供社交登录？
├── 否 → 无需防护
└── 是 →
    是否验证state参数？
    ├── 否 → 立即添加state验证（防止CSRF）
    └── 是 →
        是否验证redirect_uri？
        ├── 否 → 立即添加白名单验证
        └── 是 →
            同一邮箱多个provider如何处理？
            ├── 未处理 → 实现账号关联逻辑
            └── 已处理 → 基本安全

是否存储access token？
├── 是 → 立即移除（只存储必要的用户信息）
└── 否 → 符合最佳实践
```

---

### 完整代码示例

**使用NextAuth.js（推荐方案）**

```typescript
// pages/api/auth/[...nextauth].ts
import NextAuth from 'next-auth'
import GoogleProvider from 'next-auth/providers/google'
import GitHubProvider from 'next-auth/providers/github'
import { PrismaAdapter } from '@next-auth/prisma-adapter'
import { db } from '@/lib/database'

export default NextAuth({
  adapter: PrismaAdapter(db),

  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
  ],

  callbacks: {
    async signIn({ user, account, profile }) {
      // ✅ 1. 验证邮箱
      if (!user.email) {
        return false
      }

      // ✅ 2. 检查邮箱是否已验证
      if (account.provider === 'google' && !profile.email_verified) {
        return false
      }

      // ✅ 3. 处理账号关联
      const existingUser = await db.user.findUnique({
        where: { email: user.email },
      })

      if (existingUser) {
        // 已存在，允许登录
        return true
      }

      // 新用户，允许注册
      return true
    },

    async session({ session, user }) {
      // 添加用户ID到session
      session.user.id = user.id
      return session
    },
  },

  pages: {
    signIn: '/login',
    error: '/auth/error',
  },

  events: {
    async signIn({ user, account }) {
      // 记录登录日志
      console.log(`用户 ${user.email} 通过 ${account.provider} 登录`)
    },
  },
})
```

**前端使用**

```typescript
// pages/login.tsx
import { signIn } from 'next-auth/react'

export default function LoginPage() {
  return (
    <div className="space-y-4">
      <h1>登录</h1>

      <button
        onClick={() => signIn('google', { callbackUrl: '/dashboard' })}
        className="px-4 py-2 bg-blue-600 text-white rounded"
      >
        使用 Google 登录
      </button>

      <button
        onClick={() => signIn('github', { callbackUrl: '/dashboard' })}
        className="px-4 py-2 bg-gray-800 text-white rounded"
      >
        使用 GitHub 登录
      </button>
    </div>
  )
}
```

---

## L3 企业版（深耕版）

企业级社交登录安全需要更完善的体系：

**1. 高级身份验证**
- 多因素认证集成
- 风险自适应认证
- 实时身份验证

**2. 完整账号生命周期**
- 账号迁移机制
- 账号合并策略
- 企业身份集成

**3. 监控和审计**
- 异常登录检测
- 账号关联分析
- 安全事件审计

**详细内容请参考企业级案例**：
- [企业级OAuth实现](../../enterprise/bizsec/auth/oauth-enterprise.md)
- [身份联邦管理](../../enterprise/infosec/identity-federation.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基础实现 | $0 | 4小时 | 1小时/月 | MVP阶段 |
| L2-完整方案 | $0 | 8小时 | 2小时/月 | 生产环境 |
| L3-企业级 | $50+ | 需评估 | 专职团队 | 企业应用 |

---

## 常见问题

**Q: 同一邮箱多个社交账号如何处理？**
A: 推荐自动关联策略：首次登录创建账号，后续使用相同邮箱的社交账号自动关联。

**Q: 用户忘记密码但有社交账号怎么办？**
A: 引导用户使用社交账号登录，然后设置密码或解绑社交账号。

**Q: 如何防止账号劫持？**
A: 严格验证OAuth流程，不信任未验证的邮箱，实现账号关联确认机制。

**Q: 社交账号被封禁怎么办？**
A: 引导用户绑定多个登录方式，提供密码登录作为备选。

---

## 相关资源

**工具**
- [NextAuth.js](https://next-auth.js.org/) - 完整认证方案
- [Auth.js](https://authjs.dev/) - 现代Web应用认证
- [Passport.js](http://www.passportjs.org/) - Node.js认证中间件

**学习资源**
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [OpenID Connect](https://openid.net/connect/)
- [OWASP OAuth Security](https://owasp.org/www-community/vulnerabilities/OAuth_misconfiguration)

**相关案例**
- [账号接管](./account-takeover.md)
- [CSRF攻击](./csrf-attack.md)
- [Session劫持](./session-hijacking.md)
