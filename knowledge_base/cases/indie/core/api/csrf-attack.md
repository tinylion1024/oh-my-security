# CSRF 攻击

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者诱导用户点击恶意链接，以用户身份执行操作（转账、改密码、发帖），用户毫不知情。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 状态变更操作（转账、修改密码、删除数据）只用 Cookie 认证
- [ ] 没有验证请求来源（Referer/Origin Header）
- [ ] GET 请求可以执行状态变更操作
- [ ] 没有使用 CSRF Token 或 SameSite Cookie
→ 勾选≥1项，即需关注此风险

### 一句话防御
给每个表单添加 CSRF Token + 配置 SameSite Cookie 属性，完全免费，防护效果显著。

### 快速行动清单
1. [ ] **立即（今天）**：配置 Cookie SameSite=Strict 或 Lax 属性
2. [ ] **短期（本周）**：为状态变更操作添加 CSRF Token 验证
3. [ ] **长期（规划中）**：检查所有敏感操作，确保使用 POST/PUT/DELETE 方法

### 推荐工具
- **免费**：
  - [csurf](https://github.com/expressjs/csurf) - Express CSRF 中间件
  - [csrf](https://github.com/pillarjs/csrf) - Node.js CSRF Token 生成
  - [NextAuth.js](https://next-auth.js.org/) - 内置 CSRF 防护
- **低成本**：
  - [Clerk](https://clerk.com/) - 认证服务，内置 CSRF 防护
  - [Auth0](https://auth0.com/) - 企业认证，免费 7000 MAU

### 验证方法
- [ ] 在浏览器开发者工具中检查 Cookie 有 SameSite 属性
- [ ] 创建一个外部 HTML 页面，模拟表单提交到你的站点，应返回 403 Forbidden
- [ ] 检查表单中有隐藏的 CSRF Token 字段

---

## L2 小团队版（理解版）

### 场景还原
你的产品是一个在线支付平台。某天，大量用户投诉账户余额异常减少。调查发现，攻击者在一个热门论坛发布了如下帖子：

```html
<!-- 攻击者在其他网站植入的恶意代码 -->
<img src="https://yourbank.com/api/transfer?to=attacker&amount=1000" style="display:none">
```

或更隐蔽的表单提交：

```html
<form action="https://yourbank.com/api/transfer" method="POST" id="steal">
  <input type="hidden" name="to" value="attacker_account">
  <input type="hidden" name="amount" value="1000">
</form>
<script>document.getElementById('steal').submit();</script>
```

当已登录用户浏览这个帖子时，浏览器自动携带 Cookie 发起转账请求。用户完全不知情，钱已经被转走。

### 攻击路径（简化版）
1. **发现目标**：攻击者发现转账 API 只用 Cookie 认证，无额外验证
2. **构造攻击**：创建恶意页面，自动发起跨站请求
3. **诱导用户**：通过钓鱼邮件、社交媒体、热门论坛传播恶意链接
4. **自动执行**：用户点击后，浏览器自动携带 Cookie 完成请求
5. **资金转移**：用户资金被转移到攻击者账户

### 防御实施（低成本方案）

#### 方案A：免费方案（SameSite Cookie）

**工具/服务**: SameSite Cookie 属性

**配置步骤**:

```javascript
// Express 配置 SameSite Cookie
const express = require('express');
const cookieParser = require('cookie-parser');

const app = express();
app.use(cookieParser());

// 登录时设置 SameSite Cookie
app.post('/api/login', (req, res) => {
  // 验证用户凭证...

  // 设置 SameSite Cookie
  res.cookie('session_id', generateSessionId(), {
    httpOnly: true,      // 防止 JavaScript 访问
    secure: true,        // 仅 HTTPS
    sameSite: 'strict',  // 严格模式：完全禁止跨站请求携带
    maxAge: 24 * 60 * 60 * 1000, // 24 小时
  });

  res.json({ success: true });
});

// 或使用 'lax' 模式（允许顶级导航的 GET 请求）
app.post('/api/login-lax', (req, res) => {
  res.cookie('session_id', generateSessionId(), {
    httpOnly: true,
    secure: true,
    sameSite: 'lax', // 宽松模式：允许从外部链接跳转的 GET 请求
    maxAge: 24 * 60 * 60 * 1000,
  });

  res.json({ success: true });
});
```

**SameSite 模式对比**:

| 模式 | 行为 | 适用场景 |
|------|------|----------|
| `Strict` | 完全禁止跨站请求携带 Cookie | 敏感操作：银行、支付 |
| `Lax` | 允许顶级导航 GET 请求携带 | 大多数网站：需要 SEO、外链跳转 |
| `None` | 允许跨站请求（需配合 Secure） | 第三方集成、嵌入式 Widget |

#### 方案B：免费方案（CSRF Token）

**工具/服务**: CSRF Token 中间件

**配置步骤**:

```javascript
// Express + csurf 实现 CSRF Token
const express = require('express');
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

const app = express();
app.use(cookieParser());

// CSRF 保护中间件
const csrfProtection = csrf({ cookie: true });

// 获取 CSRF Token（供前端使用）
app.get('/api/csrf-token', csrfProtection, (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

// 保护路由：所有状态变更操作
app.post('/api/transfer', csrfProtection, async (req, res) => {
  // req.csrfToken() 已验证
  const { to, amount } = req.body;

  // 执行转账逻辑...
  await transferMoney(req.session.userId, to, amount);

  res.json({ success: true });
});

app.put('/api/password', csrfProtection, async (req, res) => {
  // 修改密码
  await updatePassword(req.session.userId, req.body.newPassword);
  res.json({ success: true });
});
```

**前端集成（Fetch API）**:

```typescript
// 获取 CSRF Token
let csrfToken = '';

async function initCsrf() {
  const res = await fetch('/api/csrf-token');
  const data = await res.json();
  csrfToken = data.csrfToken;
}

// 发起受保护的请求
async function transferMoney(to: string, amount: number) {
  const res = await fetch('/api/transfer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken, // 在 Header 中携带 Token
    },
    body: JSON.stringify({ to, amount }),
    credentials: 'include', // 携带 Cookie
  });

  return res.json();
}

// 页面加载时初始化
initCsrf();
```

**前端集成（表单提交）**:

```tsx
// React 表单示例
import { useEffect, useState } from 'react';

function TransferForm() {
  const [csrfToken, setCsrfToken] = useState('');

  useEffect(() => {
    fetch('/api/csrf-token')
      .then((res) => res.json())
      .then((data) => setCsrfToken(data.csrfToken));
  }, []);

  return (
    <form action="/api/transfer" method="POST">
      {/* 隐藏字段携带 CSRF Token */}
      <input type="hidden" name="_csrf" value={csrfToken} />

      <input name="to" placeholder="收款人" />
      <input name="amount" type="number" placeholder="金额" />
      <button type="submit">转账</button>
    </form>
  );
}
```

#### 方案C：组合方案（SameSite + CSRF Token）

```typescript
// Next.js API Route 完整示例
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';

// 内存存储 CSRF Token（生产环境用 Redis）
const csrfTokens = new Map<string, { token: string; expiresAt: number }>();

// 生成 CSRF Token
function generateCsrfToken(sessionId: string): string {
  const token = randomBytes(32).toString('hex');
  csrfTokens.set(sessionId, {
    token,
    expiresAt: Date.now() + 60 * 60 * 1000, // 1 小时过期
  });
  return token;
}

// 验证 CSRF Token
function validateCsrfToken(sessionId: string, token: string): boolean {
  const stored = csrfTokens.get(sessionId);
  if (!stored) return false;
  if (Date.now() > stored.expiresAt) {
    csrfTokens.delete(sessionId);
    return false;
  }
  return stored.token === token;
}

// GET /api/csrf-token - 获取 Token
export async function GET(request: NextRequest) {
  const sessionId = request.cookies.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const token = generateCsrfToken(sessionId);

  return NextResponse.json({ csrfToken: token });
}

// POST /api/transfer - 受保护的转账操作
export async function POST(request: NextRequest) {
  const sessionId = request.cookies.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 验证 CSRF Token（从 Header 或 Body 获取）
  const csrfToken = request.headers.get('X-CSRF-Token');
  const body = await request.json();
  const tokenFromBody = body._csrf;

  if (!validateCsrfToken(sessionId, csrfToken || tokenFromBody)) {
    return NextResponse.json(
      { error: 'Invalid CSRF token' },
      { status: 403 }
    );
  }

  // 执行转账逻辑
  const { to, amount } = body;
  // await transferMoney(userId, to, amount);

  return NextResponse.json({ success: true, to, amount });
}
```

### 决策树

```
你的应用是否有状态变更操作？
├── 否（纯只读）→ CSRF 风险较低，但仍建议配置 SameSite Cookie
└── 是
    ├── 是否使用 Cookie 认证？
    │   ├── 否（仅用 Token in Header）→ 风险较低，检查是否有遗漏
    │   └── 是 → 必须配置 SameSite + CSRF Token
    └── 敏感操作是否需要二次验证？
        ├── 是 → 添加短信/邮箱验证码
        └── 否 → 确保 CSRF 防护完整
```

### 完整代码示例

以下是一个完整的 Next.js 应用示例，包含 SameSite Cookie 和 CSRF Token 防护：

```typescript
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';

// 模拟用户数据库
const users = new Map([
  ['user@example.com', { id: '1', password: 'hashed_password', name: 'Test User' }],
]);

// 会话存储（生产环境用 Redis）
const sessions = new Map<string, { userId: string; expiresAt: number }>();

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();

  // 验证用户
  const user = users.get(email);
  if (!user || user.password !== password) {
    return NextResponse.json(
      { error: 'Invalid credentials' },
      { status: 401 }
    );
  }

  // 创建会话
  const sessionId = randomBytes(32).toString('hex');
  sessions.set(sessionId, {
    userId: user.id,
    expiresAt: Date.now() + 24 * 60 * 60 * 1000, // 24 小时
  });

  // 设置 SameSite Cookie
  const response = NextResponse.json({ success: true, user: { id: user.id, name: user.name } });
  response.cookies.set('session_id', sessionId, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict', // 关键：Strict 模式
    maxAge: 24 * 60 * 60,
    path: '/',
  });

  return response;
}
```

```typescript
// app/api/csrf/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';

// CSRF Token 存储
const csrfTokens = new Map<string, { token: string; expiresAt: number }>();

export async function GET(request: NextRequest) {
  const sessionId = request.cookies.get('session_id')?.value;

  if (!sessionId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 生成新 Token
  const token = randomBytes(32).toString('hex');
  csrfTokens.set(sessionId, {
    token,
    expiresAt: Date.now() + 60 * 60 * 1000,
  });

  return NextResponse.json({ csrfToken: token });
}

// 验证中间件
export function validateCsrf(request: NextRequest, token: string | null): boolean {
  const sessionId = request.cookies.get('session_id')?.value;
  if (!sessionId || !token) return false;

  const stored = csrfTokens.get(sessionId);
  if (!stored || Date.now() > stored.expiresAt) {
    csrfTokens.delete(sessionId);
    return false;
  }

  return stored.token === token;
}
```

```typescript
// app/api/transfer/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { validateCsrf } from '../csrf/route';

export async function POST(request: NextRequest) {
  // 1. 验证 CSRF Token
  const csrfToken = request.headers.get('X-CSRF-Token');
  if (!validateCsrf(request, csrfToken)) {
    return NextResponse.json(
      { error: 'Invalid CSRF token' },
      { status: 403 }
    );
  }

  // 2. 验证会话
  const sessionId = request.cookies.get('session_id')?.value;
  if (!sessionId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  // 3. 执行转账
  const { to, amount } = await request.json();

  // 业务逻辑...
  console.log(`Transfer ${amount} to ${to}`);

  return NextResponse.json({ success: true, message: 'Transfer completed' });
}
```

```tsx
// app/transfer/page.tsx
'use client';

import { useEffect, useState } from 'react';

export default function TransferPage() {
  const [csrfToken, setCsrfToken] = useState('');
  const [to, setTo] = useState('');
  const [amount, setAmount] = useState('');
  const [message, setMessage] = useState('');

  // 获取 CSRF Token
  useEffect(() => {
    fetch('/api/csrf')
      .then((res) => res.json())
      .then((data) => setCsrfToken(data.csrfToken))
      .catch(() => setMessage('Failed to get CSRF token'));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch('/api/transfer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken,
      },
      body: JSON.stringify({ to, amount: parseFloat(amount) }),
      credentials: 'include',
    });

    const data = await res.json();
    setMessage(data.success ? 'Transfer successful!' : `Error: ${data.error}`);
  };

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">转账</h1>

      {message && (
        <div className={`p-2 mb-4 rounded ${message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="hidden" name="_csrf" value={csrfToken}
        />
        <div>
          <label className="block mb-1">收款人</label>
          <input
            type="text"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
        <div>
          <label className="block mb-1">金额</label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="w-full p-2 border rounded"
            min="0.01"
            step="0.01"
            required
          />
        </div>
        <button
          type="submit"
          className="w-full p-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          确认转账
        </button>
      </form>
    </div>
  );
}
```

---

## L3 企业版（深耕版）

本案例的企业级扩展内容，请参考企业版案例库：

- **详细攻击技术**：参见 [enterprise/infosec/api/csrf-attack.md](../../../enterprise/infosec/api/csrf-attack.md)
- **企业防御架构**：API Gateway CSRF 防护、微服务间通信安全
- **合规要求**：OWASP Top 10 #A01:2021、PCI DSS 安全要求、SOC 2 访问控制
- **监控告警**：跨站请求检测、异常操作告警、用户行为分析
- **渗透测试**：CSRF 漏洞扫描、自动化攻击测试、安全评估

企业版核心补充：
1. **高级 CSRF 技术**：JSON CSRF、Flash CSRF、点击劫持组合攻击
2. **双重 Cookie 验证**：Cookie + Header 双重校验
3. **微服务 CSRF**：服务间调用、分布式 Session
4. **应急响应**：CSRF 攻击溯源、用户通知、安全加固
