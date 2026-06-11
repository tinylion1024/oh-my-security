# 认证服务对比 (Auth Service Comparison)

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 基础设施选型
- **实现成本**: 视选择的服务而定（$0-100/月）
- **实施时间**: 1-3天（集成）/ 1-2周（迁移）
- **维护成本**: 1-2小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
为独立开发者提供第三方认证服务的选型参考，帮助选择最适合项目需求的认证解决方案，避免重复造轮子并确保安全合规。

## 服务总览

### 快速选型表

| 服务 | 免费额度 | 学习曲线 | 功能完整度 | 可定制性 | 迁出难度 | 独立开发者推荐度 |
|------|---------|---------|-----------|---------|---------|----------------|
| **Auth0** | 7k MAU | ⭐⭐⭐ 中 | ⭐⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ |
| **Supabase Auth** | 50k MAU | ⭐⭐ 低 | ⭐⭐⭐⭐ 中高 | ⭐⭐⭐⭐ 高 | ⭐⭐ 低 | ⭐⭐⭐⭐⭐ |
| **Clerk** | 5k MAU | ⭐ 最简单 | ⭐⭐⭐⭐ 中高 | ⭐⭐⭐ 中 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐⭐ |
| **Firebase Auth** | 无限 MAU | ⭐⭐ 低 | ⭐⭐⭐⭐ 中高 | ⭐⭐⭐ 中 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ |
| **NextAuth.js** | 免费（自托管）| ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 中高 | ⭐⭐⭐⭐⭐ 最高 | ⭐ 最低 | ⭐⭐⭐⭐ |
| **AWS Cognito** | 50k MAU | ⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐⭐ 最高 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ |

### 详细对比

---

## 1. Auth0

### 概述
企业级身份认证平台，功能最全面，安全性最高，但价格较贵。

### 免费额度
| 资源 | 免费限制 |
|------|---------|
| 月活用户 (MAU) | 7,000 |
| 社交登录提供商 | 2个 |
| 自定义域名 | ❌ 不支持 |
| 无密码登录 | ✅ 支持 |
| MFA | ✅ 支持 |
| 规则 (Rules) | ✅ 支持 |

### 付费计划
| 计划 | 月费 | MAU | 特性 |
|------|------|-----|------|
| Free | $0 | 7,000 | 基础功能 |
| Developer | $35 | 10,000 | + 自定义域名 |
| Developer Pro | $240 | 10,000 | + 无密码 + 企业连接器 |
| Enterprise | 定制 | 无限 | + SLA + 专属支持 |

### 核心特性

```javascript
// Auth0 快速集成 (React)
import { Auth0Provider, useAuth0 } from '@auth0/auth0-react';

// 1. 配置 Provider
function App() {
  return (
    <Auth0Provider
      domain="your-domain.auth0.com"
      clientId="your-client-id"
      authorizationParams={{
        redirect_uri: window.location.origin
      }}
    >
      <YourApp />
    </Auth0Provider>
  );
}

// 2. 使用认证
function LoginButton() {
  const { loginWithRedirect, logout, user, isAuthenticated } = useAuth0();

  if (isAuthenticated) {
    return (
      <div>
        <img src={user.picture} alt={user.name} />
        <span>{user.email}</span>
        <button onClick={() => logout()}>Logout</button>
      </div>
    );
  }

  return <button onClick={() => loginWithRedirect()}>Login</button>;
}
```

### 优势
- ✅ 功能最全面，企业级安全
- ✅ 支持 50+ 社交登录提供商
- ✅ 强大的规则引擎（自定义认证流程）
- ✅ 完善的文档和 SDK
- ✅ 合规性好（SOC2, ISO27001, GDPR）

### 劣势
- ❌ 免费额度相对较小
- ❌ 价格增长快（MAU 计费）
- ❌ 配置复杂度较高
- ❌ 中国大陆访问可能受限

### 适用场景
- 企业级应用
- 需要高级安全合规的项目
- 复杂的认证需求（SSO, 企业目录集成）

---

## 2. Supabase Auth

### 概述
开源 Firebase 替代品，提供完整的后端服务，认证是其核心功能之一。

### 免费额度
| 资源 | 免费限制 |
|------|---------|
| 月活用户 (MAU) | 50,000 |
| 数据库存储 | 500 MB |
| 文件存储 | 1 GB |
| 社交登录提供商 | 无限 |
| 自定义域名 | ❌ 不支持 |
| 行级安全 (RLS) | ✅ 支持 |

### 付费计划
| 计划 | 月费 | MAU | 存储 | 特性 |
|------|------|-----|------|------|
| Free | $0 | 50k | 500MB | 基础功能 |
| Pro | $25 | 100k | 8GB | + 日常备份 + 优先支持 |
| Team | $599 | 无限 | 无限 | + SSO + SOC2 |
| Enterprise | 定制 | 无限 | 无限 | + SLA + 专属部署 |

### 核心特性

```javascript
// Supabase Auth 快速集成
import { createClient } from '@supabase/supabase-js';

// 1. 初始化客户端
const supabase = createClient(
  'https://your-project.supabase.co',
  'your-anon-key'
);

// 2. 邮箱密码注册
async function signUp(email, password) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
    options: {
      emailRedirectTo: 'https://your-app.com/confirm'
    }
  });
  return { data, error };
}

// 3. 登录
async function signIn(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  });
  return { data, error };
}

// 4. 社交登录
async function signInWithGoogle() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: {
      redirectTo: 'https://your-app.com/auth/callback'
    }
  });
  return { data, error };
}

// 5. 魔法链接（无密码登录）
async function sendMagicLink(email) {
  const { data, error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: 'https://your-app.com/auth/callback'
    }
  });
  return { data, error };
}

// 6. 监听认证状态变化
supabase.auth.onAuthStateChange((event, session) => {
  console.log(event, session);
});

// 7. 获取当前用户
async function getCurrentUser() {
  const { data: { user } } = await supabase.auth.getUser();
  return user;
}
```

### 行级安全 (RLS) 示例

```sql
-- 启用 RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 用户只能看到自己的文章
CREATE POLICY "Users can view own posts"
ON posts FOR SELECT
USING (auth.uid() = user_id);

-- 用户只能创建自己的文章
CREATE POLICY "Users can create own posts"
ON posts FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- 用户只能更新自己的文章
CREATE POLICY "Users can update own posts"
ON posts FOR UPDATE
USING (auth.uid() = user_id);
```

### 优势
- ✅ 免费额度大（50k MAU）
- ✅ 开源，可自托管
- ✅ 与数据库深度集成（RLS）
- ✅ 社交登录提供商无限制
- ✅ 文档清晰，上手简单

### 劣势
- ❌ 功能相对 Auth0 较少
- ❌ 企业 SSO 需要付费计划
- ❌ 自定义邮件模板有限制

### 适用场景
- 全栈应用（需要数据库 + 认证）
- 需要行级安全控制的应用
- 预算有限的独立开发者
- 开源爱好者

---

## 3. Clerk

### 概述
专注于开发者体验的现代认证服务，提供精美的 UI 组件，集成最简单。

### 免费额度
| 资源 | 免费限制 |
|------|---------|
| 月活用户 (MAU) | 5,000 |
| 社交登录提供商 | 无限 |
| 自定义域名 | ✅ 支持 |
| 组织功能 | ✅ 支持 |
| Webhook | ✅ 支持 |

### 付费计划
| 计划 | 月费 | MAU | 特性 |
|------|------|-----|------|
| Free | $0 | 5,000 | 基础功能 + 组织 |
| Pro | $25 | 超出部分 $0.02/MAU | + SAML SSO |
| Enterprise | 定制 | 无限 | + SLA + 专属支持 |

### 核心特性

```javascript
// Clerk 快速集成 (Next.js)
import {
  ClerkProvider,
  SignIn,
  SignUp,
  SignedIn,
  SignedOut,
  UserButton
} from '@clerk/nextjs';

// 1. 配置 Provider (app/layout.js)
export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html>
        <body>
          <header>
            <SignedIn>
              <UserButton />
            </SignedIn>
            <SignedOut>
              <a href="/sign-in">Sign In</a>
            </SignedOut>
          </header>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}

// 2. 登录页面 (app/sign-in/[[...index]]/page.js)
import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return <SignIn routing="path" path="/sign-in" />;
}

// 3. 注册页面 (app/sign-up/[[...index]]/page.js)
import { SignUp } from '@clerk/nextjs';

export default function SignUpPage() {
  return <SignUp routing="path" path="/sign-up" />;
}

// 4. 保护 API 路由
import { getAuth } from '@clerk/nextjs/server';

export default function handler(req, res) {
  const { userId } = getAuth(req);

  if (!userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  res.status(200).json({ userId });
}

// 5. 组织功能
import { OrganizationList, OrganizationSwitcher } from '@clerk/nextjs';

function OrganizationPage() {
  return (
    <div>
      <OrganizationSwitcher />
      <OrganizationList
        hidePersonal
        skipInvitationScreen
      />
    </div>
  );
}
```

### 优势
- ✅ 集成最简单，开箱即用
- ✅ 精美的 UI 组件
- ✅ 自定义域名免费支持
- ✅ 内置组织/团队功能
- ✅ 支持无密码登录

### 劣势
- ❌ 免费额度相对较小
- ❌ 部分高级功能需要付费
- ❌ 与 Next.js 绑定较紧

### 适用场景
- Next.js 应用
- 需要精美登录 UI 的项目
- 需要组织/团队功能的应用
- 快速原型开发

---

## 4. Firebase Authentication

### 概述
Google 提供的认证服务，与 Firebase 生态系统深度集成，免费额度慷慨。

### 免费额度
| 资源 | 免费限制 |
|------|---------|
| 月活用户 (MAU) | 无限制 |
| 电话认证 | 3,000次/月 |
| 社交登录提供商 | 无限 |
| 匿名登录 | ✅ 支持 |

### 付费计划
| 计划 | 月费 | 说明 |
|------|------|------|
| Spark (Free) | $0 | 无限 MAU，有限电话认证 |
| Blaze | 按量付费 | 电话认证 $0.006/次起 |

### 核心特性

```javascript
// Firebase Auth 快速集成
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signInWithPhoneNumber,
  RecaptchaVerifier,
  signOut,
  onAuthStateChanged
} from 'firebase/auth';

// 1. 初始化
const app = initializeApp({
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id"
});

const auth = getAuth(app);

// 2. 邮箱密码注册
async function signUp(email, password) {
  const userCredential = await createUserWithEmailAndPassword(
    auth, email, password
  );
  return userCredential.user;
}

// 3. 邮箱密码登录
async function signIn(email, password) {
  const userCredential = await signInWithEmailAndPassword(
    auth, email, password
  );
  return userCredential.user;
}

// 4. Google 登录
async function signInWithGoogle() {
  const provider = new GoogleAuthProvider();
  const result = await signInWithPopup(auth, provider);
  return result.user;
}

// 5. 手机号登录
async function signInWithPhone(phoneNumber, buttonId) {
  const recaptchaVerifier = new RecaptchaVerifier(
    buttonId,
    { size: 'invisible' },
    auth
  );

  const confirmationResult = await signInWithPhoneNumber(
    auth,
    phoneNumber,
    recaptchaVerifier
  );

  // 用户输入验证码
  const code = await getUserInputCode();
  const result = await confirmationResult.confirm(code);
  return result.user;
}

// 6. 监听认证状态
onAuthStateChanged(auth, (user) => {
  if (user) {
    console.log('User signed in:', user.uid);
  } else {
    console.log('User signed out');
  }
});

// 7. 登出
async function logout() {
  await signOut(auth);
}
```

### 优势
- ✅ 免费额度最慷慨（无限 MAU）
- ✅ 与 Firebase 生态深度集成
- ✅ 支持 20+ 社交登录
- ✅ 文档和社区资源丰富
- ✅ Google 支持稳定可靠

### 劣势
- ❌ 电话认证有限制（后付费）
- ❌ 中国大陆访问可能受限
- ❌ 数据存储在 Google 服务器
- ❌ 迁出需要处理数据格式

### 适用场景
- 移动应用
- 与 Firebase 一起使用
- 需要无限免费 MAU 的项目
- Google 生态用户

---

## 5. NextAuth.js (Auth.js)

### 概述
开源认证库，自托管，完全免费，支持多种认证方式，与 Next.js 深度集成。

### 免费额度
| 资源 | 限制 |
|------|------|
| 月活用户 (MAU) | 无限制（自托管） |
| 社交登录提供商 | 无限 |
| 自定义域名 | ✅ 自己控制 |
| 数据库 | 需要自己提供 |

### 成本构成
| 项目 | 月成本 |
|------|--------|
| 数据库 | $5-15 (如 PostgreSQL) |
| 托管 | $0-10 (Vercel 免费版) |
| **总计** | **$5-25/月** |

### 核心特性

```javascript
// NextAuth.js 快速集成 (Next.js App Router)
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';
import GithubProvider from 'next-auth/providers/github';
import CredentialsProvider from 'next-auth/providers/credentials';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { prisma } from '@/lib/prisma';

// 1. 配置 (app/api/auth/[...nextauth]/route.js)
const handler = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    GithubProvider({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),
    CredentialsProvider({
      name: 'Email',
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials) {
        // 自定义验证逻辑
        const user = await verifyUser(
          credentials.email,
          credentials.password
        );
        if (user) return user;
        return null;
      }
    })
  ],
  session: { strategy: 'jwt' },
  pages: {
    signIn: '/login',
    newUser: '/signup',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.id;
      }
      return session;
    }
  }
});

export { handler as GET, handler as POST };

// 2. 使用 Session Provider (app/layout.js)
import { SessionProvider } from 'next-auth/react';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <SessionProvider>
          {children}
        </SessionProvider>
      </body>
    </html>
  );
}

// 3. 获取当前用户 (app/components/UserInfo.js)
'use client';
import { useSession, signIn, signOut } from 'next-auth/react';

export default function UserInfo() {
  const { data: session, status } = useSession();

  if (status === 'loading') return <p>Loading...</p>;

  if (status === 'unauthenticated') {
    return <button onClick={() => signIn()}>Sign In</button>;
  }

  return (
    <div>
      <p>Welcome, {session.user.email}</p>
      <button onClick={() => signOut()}>Sign Out</button>
    </div>
  );
}

// 4. 保护服务端页面 (app/dashboard/page.js)
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await getServerSession();

  if (!session) {
    redirect('/login');
  }

  return <div>Dashboard for {session.user.email}</div>;
}

// 5. 保护 API 路由 (app/api/protected/route.js)
import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';

export async function GET(request) {
  const session = await getServerSession();

  if (!session) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  return NextResponse.json({ user: session.user });
}
```

### 优势
- ✅ 完全免费，自托管
- ✅ 完全控制数据和代码
- ✅ 迁出成本最低
- ✅ 支持多种数据库
- ✅ 社区活跃，文档丰富

### 劣势
- ❌ 需要自己维护和托管
- ❌ 需要自己处理安全更新
- ❌ 没有管理后台 UI
- ❌ 企业级功能需要自己实现

### 适用场景
- 注重数据主权的企业
- 需要完全控制的场景
- 预算有限的项目
- 开源爱好者

---

## 6. AWS Cognito

### 概述
AWS 提供的企业级认证服务，与 AWS 生态系统深度集成，适合已有 AWS 基础设施的项目。

### 免费额度
| 资源 | 免费限制 |
|------|---------|
| 月活用户 (MAU) | 50,000 |
| 社交登录提供商 | 无限 |
| 自定义域名 | ✅ 支持 |
| MFA | ✅ 支持 |
| SAML/OIDC | ✅ 支持 |

### 付费计划
| 计划 | 月费 | 说明 |
|------|------|------|
| Free Tier | $0 | 50k MAU（永久免费） |
| 按量付费 | $0.0055/MAU | 超出免费额度后 |

### 核心特性

```javascript
// AWS Cognito 快速集成
import { CognitoIdentityProviderClient } from '@aws-sdk/client-cognito-identity-provider';
import {
  InitiateAuthCommand,
  SignUpCommand,
  ConfirmSignUpCommand
} from '@aws-sdk/client-cognito-identity-provider';

const client = new CognitoIdentityProviderClient({
  region: 'us-east-1'
});

const CLIENT_ID = 'your-client-id';
const USER_POOL_ID = 'your-user-pool-id';

// 1. 注册
async function signUp(email, password) {
  const command = new SignUpCommand({
    ClientId: CLIENT_ID,
    Username: email,
    Password: password,
    UserAttributes: [
      { Name: 'email', Value: email }
    ]
  });

  const response = await client.send(command);
  return response;
}

// 2. 确认注册
async function confirmSignUp(email, code) {
  const command = new ConfirmSignUpCommand({
    ClientId: CLIENT_ID,
    Username: email,
    ConfirmationCode: code
  });

  return await client.send(command);
}

// 3. 登录
async function signIn(email, password) {
  const command = new InitiateAuthCommand({
    ClientId: CLIENT_ID,
    AuthFlow: 'USER_PASSWORD_AUTH',
    AuthParameters: {
      USERNAME: email,
      PASSWORD: password
    }
  });

  const response = await client.send(command);
  return {
    accessToken: response.AuthenticationResult.AccessToken,
    idToken: response.AuthenticationResult.IdToken,
    refreshToken: response.AuthenticationResult.RefreshToken
  };
}
```

### 优势
- ✅ 免费额度大（50k MAU）
- ✅ 企业级功能全面
- ✅ 与 AWS 生态深度集成
- ✅ 支持企业 SSO
- ✅ 高可用性和扩展性

### 劣势
- ❌ 学习曲线陡峭
- ❌ 配置复杂
- ❌ SDK 相对落后
- ❌ 迁出成本高

### 适用场景
- 已使用 AWS 的项目
- 需要企业级 SSO
- 需要高可用性和合规性
- AWS 生态用户

---

## 详细对比表

### 功能对比

| 功能 | Auth0 | Supabase | Clerk | Firebase | NextAuth | Cognito |
|------|-------|----------|-------|----------|----------|---------|
| 邮箱密码 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 魔法链接 | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| 社交登录 | ✅ 50+ | ✅ 无限 | ✅ 无限 | ✅ 20+ | ✅ 无限 | ✅ 无限 |
| 手机登录 | ✅ | ✅ | ✅ | ✅ 有限 | ✅ | ✅ |
| 企业 SSO | ✅ 付费 | ✅ 付费 | ✅ 付费 | ❌ | ✅ | ✅ |
| MFA | ✅ | ✅ | ✅ | ✅ | 手动 | ✅ |
| 组织/团队 | ✅ 付费 | ✅ | ✅ 免费 | ❌ | 手动 | ✅ |
| 自定义域名 | ✅ 付费 | ❌ | ✅ 免费 | ❌ | ✅ 自控 | ✅ |
| Webhooks | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 用户管理 UI | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| 审计日志 | ✅ | ✅ | ✅ | ✅ | 手动 | ✅ |
| 密码重置 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 邮箱验证 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 用户元数据 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 匿名登录 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 价格对比（月费）

| MAU | Auth0 | Supabase | Clerk | Firebase | NextAuth | Cognito |
|-----|-------|----------|-------|----------|----------|---------|
| 5k | $0 | $0 | $0 | $0 | ~$10* | $0 |
| 10k | $35 | $0 | $100 | $0 | ~$10* | $0 |
| 25k | $240 | $0 | $400 | $0 | ~$15* | $0 |
| 50k | $240 | $0 | $900 | $0 | ~$20* | $0 |
| 100k | $955 | $25 | $1,900 | $0 | ~$30* | $275 |

*NextAuth 成本为自托管数据库费用估算

---

## 选型决策树

```
需要认证服务
    │
    ├─ 预算极有限？
    │   ├─ 是 → Firebase Auth (无限 MAU)
    │   │      或 NextAuth.js (自托管)
    │   │
    │   └─ 否 → 继续判断
    │
    ├─ 需要完全控制数据？
    │   ├─ 是 → NextAuth.js (自托管)
    │   │      或 Supabase (可自托管)
    │   │
    │   └─ 否 → 继续判断
    │
    ├─ 使用 Next.js 且需要快速开发？
    │   ├─ 是 → Clerk (最简单)
    │   │
    │   └─ 否 → 继续判断
    │
    ├─ 需要数据库 + 认证？
    │   ├─ 是 → Supabase
    │   │
    │   └─ 否 → 继续判断
    │
    ├─ 已使用 AWS？
    │   ├─ 是 → Cognito
    │   │
    │   └─ 否 → 继续判断
    │
    ├─ 需要企业级功能？
    │   ├─ 是 → Auth0
    │   │
    │   └─ 否 → Firebase Auth / Clerk
```

## 迁移指南

### 从 Auth0 迁移到 Supabase

```python
# 迁移脚本示例
import asyncio
from supabase import create_client
from auth0.authentication import Users

async def migrate_users(auth0_domain, auth0_token, supabase_url, supabase_key):
    """从 Auth0 迁移用户到 Supabase"""

    # 初始化客户端
    auth0_users = Users(auth0_domain, auth0_token)
    supabase = create_client(supabase_url, supabase_key)

    # 获取 Auth0 用户
    users = auth0_users.all()

    for user in users:
        # 创建 Supabase 用户
        try:
            # 如果用户使用邮箱密码
            if user.get('email'):
                await supabase.auth.admin.create_user({
                    'email': user['email'],
                    'email_confirm': True,
                    'user_metadata': user.get('user_metadata', {}),
                    'app_metadata': user.get('app_metadata', {})
                })
                print(f"迁移成功: {user['email']}")
        except Exception as e:
            print(f"迁移失败: {user.get('email')} - {e}")
```

### 迁移清单

```
迁移检查清单
───────────────────────────────────────────────
[ ] 导出用户数据
[ ] 映射字段差异
[ ] 迁移用户元数据
[ ] 更新社交登录配置
[ ] 更新回调 URL
[ ] 更新客户端 SDK
[ ] 测试认证流程
[ ] 通知用户密码重置（如需要）
[ ] 切换 DNS
[ ] 监控错误日志
```

## 成本估算

### 按用户规模估算（月费）

| 用户规模 | 推荐服务 | 月费估算 | 说明 |
|---------|---------|---------|------|
| < 5k MAU | Clerk | $0 | 免费额度内 |
| 5-10k MAU | Supabase | $0-25 | 视数据库使用 |
| 10-25k MAU | Firebase | $0 | 免费无限 MAU |
| 25-50k MAU | Supabase/Cognito | $0-25 | 在免费额度内 |
| 50-100k MAU | Supabase Pro | $25 | 或 Firebase $0 |
| > 100k MAU | 自建或企业方案 | 定制 | 需评估具体需求 |

## 迁出成本

### 从各服务迁出的难度评估

| 服务 | 数据导出 | 代码改造 | 总时间 | 迁出成本 |
|------|---------|---------|--------|---------|
| **Auth0** | 中等 | 中等 | 3-5天 | ⭐⭐⭐ |
| **Supabase** | 简单 | 低 | 1-2天 | ⭐⭐ |
| **Clerk** | 中等 | 中等 | 2-3天 | ⭐⭐⭐ |
| **Firebase** | 中等 | 中等 | 2-4天 | ⭐⭐⭐ |
| **NextAuth** | 最简单 | 最低 | 1天 | ⭐ |
| **Cognito** | 复杂 | 高 | 5-7天 | ⭐⭐⭐⭐ |

### 降低迁出成本的策略

```javascript
// 使用适配器模式，降低对特定服务的依赖
// auth-adapter.js

class AuthAdapter {
  // 统一接口
  async signUp(email, password) { throw new Error('Not implemented'); }
  async signIn(email, password) { throw new Error('Not implemented'); }
  async signOut() { throw new Error('Not implemented'); }
  async getCurrentUser() { throw new Error('Not implemented'); }
  async resetPassword(email) { throw new Error('Not implemented'); }
}

// Supabase 实现
class SupabaseAuthAdapter extends AuthAdapter {
  constructor(client) {
    super();
    this.client = client;
  }

  async signUp(email, password) {
    const { data, error } = await this.client.auth.signUp({ email, password });
    if (error) throw error;
    return data;
  }

  // ... 其他方法实现
}

// 使用时
const auth = new SupabaseAuthAdapter(supabaseClient);
await auth.signUp('user@example.com', 'password');

// 迁移时只需更换实现
// const auth = new ClerkAuthAdapter(clerkClient);
```

## 与其他武器配合

### 配合登录异常检测

```python
# 在认证服务登录后触发异常检测
async def login_with_anomaly_check(email, password, context):
    # 1. 认证
    user = await auth_service.signIn(email, password)
    if not user:
        return {"success": False, "error": "Invalid credentials"}

    # 2. 异常检测
    anomaly_result = await anomaly_detector.analyze({
        "user_id": user.id,
        "ip": context.ip,
        "user_agent": context.user_agent,
        "device_fingerprint": context.device_fingerprint
    })

    # 3. 根据风险等级处理
    if anomaly_result.risk_level == "critical":
        await auth_service.signOut(user.session_id)
        return {"success": False, "error": "Suspicious login blocked"}

    if anomaly_result.risk_level == "high":
        # 要求 MFA
        return {"success": True, "requires_mfa": True, "user": user}

    return {"success": True, "user": user}
```

### 配合 MFA 实现

```javascript
// 使用认证服务的 MFA 功能
async function enableMFA(userId) {
  // Supabase 示例
  const { data, error } = await supabase.auth.mfa.enroll({
    factorType: 'totp',
    friendlyName: 'My Authenticator'
  });

  if (error) throw error;

  // 返回 TOTP URI 和 QR 码
  return {
    totpUri: data.totp.uri,
    qrCode: data.totp.qr_code
  };
}

async function verifyMFA(factorId, code) {
  const { data, error } = await supabase.auth.mfa.verify({
    factorId,
    code
  });

  if (error) throw error;
  return data;
}
```

## 常见问题

### Q1: 如何选择社交登录提供商？

**A:** 根据目标用户群体选择：

| 用户群体 | 推荐登录方式 |
|---------|-------------|
| 大众用户 | Google + 微信（中国）+ Apple |
| 开发者 | GitHub + Google |
| 企业用户 | SSO + Microsoft |
| 社交媒体用户 | Facebook + Twitter + Google |

### Q2: 免费额度用完后怎么办？

**A:** 策略性应对：

1. **Firebase Auth**：免费无限 MAU，可长期使用
2. **Supabase**：50k MAU 足够大部分独立项目
3. **自托管 NextAuth**：无用户数限制，只付数据库费用
4. **优化用户结构**：清理不活跃用户，减少 MAU

### Q3: 如何处理中国用户？

**A:** 考虑以下方案：

```javascript
// 根据地区选择认证服务
function getAuthProvider(region) {
  if (region === 'CN') {
    // 中国用户使用国内服务
    return {
      provider: 'wechat',  // 微信登录
      host: 'api.your-cn-server.com'
    };
  }
  return {
    provider: 'google',
    host: 'api.your-global-server.com'
  };
}
```

### Q4: 如何实现多租户？

**A:** 使用支持组织功能的服务：

| 服务 | 多租户支持 |
|------|-----------|
| Clerk | ✅ 内置组织功能 |
| Auth0 | ✅ Organizations（付费） |
| Supabase | ✅ 自建（使用 RLS） |
| NextAuth | ✅ 自建（自定义逻辑） |

```javascript
// Clerk 组织示例
import { OrganizationSwitcher, useOrganization } from '@clerk/nextjs';

function Dashboard() {
  const { organization } = useOrganization();

  return (
    <div>
      <OrganizationSwitcher />
      <p>当前组织: {organization?.name}</p>
    </div>
  );
}
```

### Q5: 如何保证认证服务可用性？

**A:**
1. **多区域部署**：选择有多区域支持的服务
2. **降级方案**：准备备选认证方式
3. **本地缓存**：缓存用户会话，避免频繁验证
4. **监控告警**：设置认证失败率告警

```python
# 认证服务降级示例
async def authenticate(email, password):
    try:
        # 尝试主认证服务
        return await primary_auth.sign_in(email, password)
    except AuthTimeoutError:
        # 降级到备用服务
        log.warning("Primary auth timeout, using fallback")
        return await fallback_auth.sign_in(email, password)
```

## 安全清单

- [ ] 配置正确的回调 URL 白名单
- [ ] 启用 HTTPS
- [ ] 设置合理的会话过期时间
- [ ] 启用邮箱验证
- [ ] 配置密码策略
- [ ] 启用 MFA（高安全场景）
- [ ] 配置 CORS 策略
- [ ] 审计日志开启
- [ ] 定期检查社交登录配置
- [ ] 密钥和凭证安全存储
- [ ] 准备认证服务降级方案
