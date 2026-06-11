# 暴力破解（Brute Force）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0-20/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过自动化脚本无限次尝试密码组合，最终破解用户账号，导致账号被盗、数据泄露。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 登录接口无失败次数限制
- [ ] 登录失败响应时间一致（未使用延时策略）
- [ ] 没有验证码保护
- [ ] 登录错误提示具体（如"密码错误"而非"用户名或密码错误"）
- [ ] 没有登录失败日志记录
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
登录失败5次锁定账号15分钟 + 验证码保护 + 模糊错误提示。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 实现账号级别限流：同一账号失败5次，锁定15分钟
   - [ ] 实现IP级别限流：同一IP每分钟最多10次尝试
   - [ ] 修改错误提示：统一返回"用户名或密码错误"

2. **短期行动**（本周可完成，免费）
   - [ ] 添加验证码（hCaptcha/Cloudflare Turnstile免费）
   - [ ] 实现指数退避：失败次数越多，等待时间越长
   - [ ] 记录登录失败日志（IP、时间、用户名）

3. **长期行动**（规划中，低成本）
   - [ ] 集成威胁情报API
   - [ ] 添加异常登录告警
   - [ ] 引导用户开启双因素认证（2FA）

### 推荐工具
- **免费**：
  - [hCaptcha](https://www.hcaptcha.com/) - 免费无限制验证码
  - [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/) - 免费智能验证
  - [Arcjet](https://arcjet.com/) - 免费限流+防护，100万请求/月

- **低成本**：
  - [Auth0](https://auth0.com/) - 内置暴力破解防护，免费7000用户/月
  - [Supabase Auth](https://supabase.com/auth) - 自动防护，免费50000用户/月

### 验证方法
- [ ] 测试步骤1：用错误密码连续登录同一账号5次，第6次应被拒绝
- [ ] 测试步骤2：错误提示应为"用户名或密码错误"，而非"密码错误"
- [ ] 测试步骤3：同一IP快速尝试多次登录，应触发限流
- [ ] 测试步骤4：添加验证码后，自动化脚本应被阻止

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有8000个用户，登录接口没有任何保护。某天服务器负载突然飙升，调查发现：

**攻击特征**：
```
# 服务器日志片段
[2026-06-10 03:12:15] POST /api/login - admin@yoursite.com - FAIL (IP: 45.33.*.*)
[2026-06-10 03:12:15] POST /api/login - admin@yoursite.com - FAIL (IP: 45.33.*.*)
[2026-06-10 03:12:15] POST /api/login - admin@yoursite.com - FAIL (IP: 45.33.*.*)
... 每秒50次请求 ...
[2026-06-10 03:15:42] POST /api/login - admin@yoursite.com - SUCCESS
```

**攻击过程**：
1. 攻击者针对管理员账号 `admin@yoursite.com`
2. 使用字典攻击：Top 10000 常见密码
3. 服务器无限制，每秒尝试50次
4. 3分钟后破解成功，密码是 `admin2024`

**真实损失**：
- 管理员账号被接管
- 所有用户数据被导出
- 服务器资源耗尽，影响正常用户

### 攻击路径（简化版）

**攻击方式1：在线暴力破解**

**简单暴力破解**：
```
尝试所有可能的密码组合
- 6位纯数字：100万次尝试
- 8位字母数字：2.8万亿种组合（不现实）
```

**字典攻击**：
```
使用常见密码列表尝试
- Top 100密码：覆盖约15%用户
- Top 1000密码：覆盖约25%用户
- Top 10000密码：覆盖约35%用户
```

**账号枚举 + 定向攻击**：
```
1. 枚举有效用户名（通过注册/忘记密码接口）
2. 针对特定账号进行字典攻击
3. 成功率显著提高
```

**攻击方式2：分布式暴力破解**

```
攻击者控制1000个代理IP
每个IP每分钟尝试5次（绕过单IP限流）
总速度：5000次/分钟
目标：特定用户账号
耗时：约10分钟破解常见密码
```

**攻击方式3：撞库攻击（Credential Stuffing）**

```
使用已知泄露的账号密码组合
成功率：1-5%
不需要暴力破解，而是"试运气"
详见：credential-stuffing.md
```

### 防御实施（低成本方案）

#### 方案A：免费方案（多层限流）

**1. 账号级别限流**

```python
from redis import Redis
from datetime import datetime, timedelta
import json

redis = Redis(host='localhost', port=6379, db=0)

def check_account_lock(email: str) -> tuple[bool, str]:
    """
    检查账号是否被锁定
    
    返回: (是否允许登录, 错误消息)
    """
    # 检查锁定状态
    lock_key = f"account_lock:{email}"
    lock_data = redis.get(lock_key)
    
    if lock_data:
        data = json.loads(lock_data)
        lock_until = datetime.fromisoformat(data['lock_until'])
        
        if datetime.now() < lock_until:
            remaining = (lock_until - datetime.now()).seconds // 60
            return False, f"账号已被锁定，请在{remaining}分钟后重试"
        else:
            # 锁定已过期，清除
            redis.delete(lock_key)
    
    return True, ""

def record_failed_login(email: str, ip: str):
    """记录登录失败"""
    attempts_key = f"login_attempts:{email}"
    lock_key = f"account_lock:{email}"
    
    # 增加失败次数
    attempts = redis.incr(attempts_key)
    redis.expire(attempts_key, 900)  # 15分钟过期
    
    if attempts >= 5:
        # 锁定账号
        lock_until = datetime.now() + timedelta(minutes=15)
        redis.set(
            lock_key,
            json.dumps({
                'attempts': attempts,
                'lock_until': lock_until.isoformat(),
                'last_ip': ip,
            }),
            ex=900
        )
        
        # 清除失败计数
        redis.delete(attempts_key)

def clear_failed_attempts(email: str):
    """登录成功后清除失败记录"""
    redis.delete(f"login_attempts:{email}")
    redis.delete(f"account_lock:{email}")
```

**2. IP级别限流**

```python
def check_ip_rate_limit(ip: str) -> tuple[bool, str]:
    """
    检查IP级别限流
    
    规则：同一IP每分钟最多10次登录尝试
    """
    key = f"ip_login:{ip}"
    
    # 获取当前计数
    count = redis.get(key)
    
    if count and int(count) >= 10:
        ttl = redis.ttl(key)
        return False, f"请求过于频繁，请在{ttl}秒后重试"
    
    return True, ""

def record_ip_attempt(ip: str):
    """记录IP登录尝试"""
    key = f"ip_login:{ip}"
    count = redis.incr(key)
    
    # 第一次设置过期时间
    if count == 1:
        redis.expire(key, 60)  # 1分钟窗口
```

**3. 指数退避策略**

```python
def calculate_delay(attempts: int) -> int:
    """
    计算指数退避延迟（秒）
    
    第1次失败：0秒
    第2次失败：1秒
    第3次失败：2秒
    第4次失败：4秒
    第5次失败：8秒
    ...
    """
    if attempts <= 1:
        return 0
    
    return 2 ** (attempts - 2)

async def login_with_backoff(email: str, password: str, ip: str):
    """带退避的登录处理"""
    # 获取失败次数
    attempts_key = f"login_attempts:{email}"
    attempts = int(redis.get(attempts_key) or 0)
    
    # 计算延迟
    delay = calculate_delay(attempts)
    
    if delay > 0:
        # 延迟响应（增加攻击成本）
        await asyncio.sleep(delay)
    
    # 执行登录验证
    user = authenticate_user(email, password)
    
    if user:
        clear_failed_attempts(email)
        return {'success': True, 'user': user}
    else:
        record_failed_login(email, ip)
        return {'error': '用户名或密码错误'}, 401
```

**4. 模糊错误提示**

```python
# 错误做法 ❌
def login_wrong(email, password):
    user = find_user_by_email(email)
    
    if not user:
        return {'error': '用户不存在'}, 404
    
    if not verify_password(password, user.password):
        return {'error': '密码错误'}, 401
    
    return {'success': True}

# 正确做法 ✅
def login_correct(email, password):
    user = find_user_by_email(email)
    
    # 统一错误消息，避免账号枚举
    generic_error = '用户名或密码错误'
    
    if not user or not verify_password(password, user.password):
        # 记录失败但返回相同错误
        record_failed_login(email, get_ip())
        return {'error': generic_error}, 401
    
    # 登录成功
    return {'success': True, 'user': user}
```

**5. 验证码保护**

```typescript
// 前端：Cloudflare Turnstile 集成
import { Turnstile } from '@marsidev/react-turnstile';

function LoginForm() {
  const [token, setToken] = useState<string>();
  
  return (
    <form onSubmit={handleSubmit}>
      <input type="email" name="email" />
      <input type="password" name="password" />
      
      {/* Cloudflare Turnstile（免费） */}
      <Turnstile
        siteKey={process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY!}
        onSuccess={(token) => setToken(token)}
        options={{
          theme: 'light',
          size: 'normal',
        }}
      />
      
      <button type="submit" disabled={!token}>
        登录
      </button>
    </form>
  );
}

// 后端：验证 Turnstile Token
async function verifyTurnstile(token: string, ip: string): Promise<boolean> {
  const response = await fetch(
    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        secret: process.env.TURNSTILE_SECRET_KEY!,
        response: token,
        remoteip: ip,
      }),
    }
  );
  
  const data = await response.json();
  return data.success;
}

// 登录API
app.post('/api/login', async (req, res) => {
  const { email, password, turnstileToken } = req.body;
  const ip = req.ip;
  
  // 1. 验证 Turnstile
  if (!await verifyTurnstile(turnstileToken, ip)) {
    return res.status(400).json({ error: '验证码验证失败' });
  }
  
  // 2. 检查账号锁定
  const [allowed, message] = check_account_lock(email);
  if (!allowed) {
    return res.status(429).json({ error: message });
  }
  
  // 3. 检查IP限流
  const [ipAllowed, ipMessage] = check_ip_rate_limit(ip);
  if (!ipAllowed) {
    return res.status(429).json({ error: ipMessage });
  }
  
  // 4. 记录IP尝试
  record_ip_attempt(ip);
  
  // 5. 执行登录
  // ...
});
```

**局限性**：
- 需要维护Redis
- 分布式攻击可能绕过IP限流
- 需要手动实现所有逻辑

---

#### 方案B：使用防护服务（推荐）

**使用 Arcjet 智能防护**

```typescript
import arcjet, { shield, detectBot, tokenBucket } from "@arcjet/next";

const aj = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    // 防护盾：检测攻击模式
    shield({
      mode: "LIVE",
    }),
    
    // 机器人检测
    detectBot({
      mode: "LIVE",
      block: ["AUTOMATION_TOOLS"],  // 阻止自动化工具
    }),
    
    // 限流：基于IP
    tokenBucket({
      mode: "LIVE",
      characteristics: ["ip.src"],
      refillRate: 5,    // 每分钟补充5个令牌
      interval: 60,
      capacity: 10,     // 最大10个令牌
    }),
  ],
});

export async function POST(req: Request) {
  // Arcjet 防护检查
  const decision = await aj.protect(req);
  
  if (decision.isDenied()) {
    if (decision.reason.isRateLimit()) {
      return Response.json(
        { error: "请求过于频繁，请稍后重试" },
        { status: 429 }
      );
    }
    
    if (decision.reason.isBot()) {
      return Response.json(
        { error: "检测到自动化工具，访问被拒绝" },
        { status: 403 }
      );
    }
    
    return Response.json(
      { error: "访问被拒绝" },
      { status: 403 }
    );
  }
  
  // 继续登录流程
  return handleLogin(req);
}
```

**使用 Auth0 内置防护**

```javascript
import { Auth0Client } from '@auth0/auth0-spa-js';

// Auth0 自动提供：
// - 暴力破解检测
// - 异常IP识别
// - 自动账号锁定
// - 可疑登录告警

// 在 Auth0 Dashboard 中配置：
// Authentication > Database > Attack Protection
// - Brute Force Protection: 启用
// - Suspicious IP Throttling: 启用
// - Breached Password Detection: 启用

const auth0 = new Auth0Client({
  domain: 'your-domain.auth0.com',
  client_id: 'your-client-id',
});

// 登录
try {
  await auth0.login({
    username: email,
    password: password,
  });
} catch (error) {
  // Auth0 自动处理暴力破解
  // 返回错误：too-many_attempts
  console.error(error);
}
```

**优势**：
- 开箱即用的防护
- 自动检测分布式攻击
- 无需维护基础设施
- 可视化仪表盘
- 免费额度充足

---

#### 方案C：增强方案（+$10-20/月）

在方案B基础上添加：

**1. 威胁情报集成**

```typescript
// 检查IP是否在黑名单中
async function checkIPReputation(ip: string): Promise<{
  risk: 'low' | 'medium' | 'high';
  reasons: string[];
}> {
  // 使用免费/低成本的威胁情报API
  // 如：AbuseIPDB, IPQualityScore
  
  const response = await fetch(
    `https://api.abuseipdb.com/api/v2/check?ipAddress=${ip}`,
    {
      headers: {
        'Key': process.env.ABUSEIPDB_KEY!,
        'Accept': 'application/json',
      },
    }
  );
  
  const data = await response.json();
  
  if (data.data.abuseConfidenceScore > 50) {
    return { risk: 'high', reasons: ['IP在黑名单中'] };
  }
  
  if (data.data.abuseConfidenceScore > 25) {
    return { risk: 'medium', reasons: ['IP有可疑活动'] };
  }
  
  return { risk: 'low', reasons: [] };
}

// 登录前检查
app.post('/api/login', async (req, res) => {
  const ip = req.ip;
  
  // 检查IP信誉
  const reputation = await checkIPReputation(ip);
  
  if (reputation.risk === 'high') {
    // 要求验证码或直接拒绝
    return res.status(403).json({
      error: '检测到可疑IP，请联系客服',
      requireCaptcha: true,
    });
  }
  
  if (reputation.risk === 'medium') {
    // 强制验证码
    return res.status(200).json({
      requireCaptcha: true,
    });
  }
  
  // 正常登录流程
  // ...
});
```

**2. 设备指纹识别**

```typescript
// 前端：收集设备指纹
import FingerprintJS from '@fingerprintjs/fingerprintjs';

async function getDeviceFingerprint(): Promise<string> {
  const fp = await FingerprintJS.load();
  const result = await fp.detect();
  return result.visitorId;
}

// 后端：验证设备指纹
async function checkDeviceFingerprint(
  userId: string,
  fingerprint: string
): Promise<{ trusted: boolean; newDevice: boolean }> {
  // 查询历史指纹
  const knownFingerprints = await getKnownFingerprints(userId);
  
  if (knownFingerprints.includes(fingerprint)) {
    return { trusted: true, newDevice: false };
  }
  
  // 新设备
  return { trusted: false, newDevice: true };
}

// 新设备登录时发送告警
if (deviceCheck.newDevice) {
  await sendNewDeviceAlert(user.email, {
    ip: req.ip,
    userAgent: req.headers['user-agent'],
    timestamp: new Date(),
  });
}
```

---

### 决策树

```
你的登录接口是否有失败次数限制？
├── 否 → 立即添加（方案A基础版）
└── 是 →
    是否有验证码保护？
    ├── 否 → 添加验证码（免费）
    └── 是 →
        是否处理敏感数据？
        ├── 是 → 添加设备指纹 + 威胁情报（方案C）
        └── 否 → 基础防护足够
        
        你使用什么认证方案？
        ├── 自建认证 → 使用 Arcjet（免费）
        ├── Auth0 → 自动防护（配置Dashboard）
        ├── Supabase Auth → 自动防护
        └── 其他 → 检查是否内置防护
```

### 完整代码示例

**Next.js + Arcjet 完整防护方案**

```typescript
// app/api/auth/login/route.ts
import arcjet, { shield, detectBot, tokenBucket } from "@arcjet/next";
import { NextResponse } from "next/server";
import { verifyPassword } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { sign } from "jsonwebtoken";

const aj = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    shield({ mode: "LIVE" }),
    detectBot({
      mode: "LIVE",
      block: ["AUTOMATION_TOOLS"],
    }),
    tokenBucket({
      mode: "LIVE",
      characteristics: ["ip.src"],
      refillRate: 5,
      interval: 60,
      capacity: 10,
    }),
  ],
});

export async function POST(req: Request) {
  try {
    // 1. Arcjet 防护
    const decision = await aj.protect(req);
    
    if (decision.isDenied()) {
      if (decision.reason.isRateLimit()) {
        return NextResponse.json(
          { error: "请求过于频繁，请15分钟后重试" },
          { status: 429 }
        );
      }
      
      if (decision.reason.isBot()) {
        return NextResponse.json(
          { error: "检测到自动化工具" },
          { status: 403 }
        );
      }
      
      return NextResponse.json(
        { error: "访问被拒绝" },
        { status: 403 }
      );
    }
    
    // 2. 解析请求
    const { email, password } = await req.json();
    
    if (!email || !password) {
      return NextResponse.json(
        { error: "请输入邮箱和密码" },
        { status: 400 }
      );
    }
    
    // 3. 查找用户
    const user = await prisma.user.findUnique({
      where: { email },
    });
    
    // 统一错误消息（避免账号枚举）
    const genericError = "邮箱或密码错误";
    
    if (!user) {
      return NextResponse.json(
        { error: genericError },
        { status: 401 }
      );
    }
    
    // 4. 验证密码
    const valid = await verifyPassword(password, user.password);
    
    if (!valid) {
      // 记录失败
      await prisma.loginAttempt.create({
        data: {
          userId: user.id,
          success: false,
          ip: req.headers.get("x-forwarded-for") || "unknown",
          userAgent: req.headers.get("user-agent") || "",
        },
      });
      
      return NextResponse.json(
        { error: genericError },
        { status: 401 }
      );
    }
    
    // 5. 创建Session
    const token = sign(
      { userId: user.id, email: user.email },
      process.env.JWT_SECRET!,
      { expiresIn: "7d" }
    );
    
    // 记录成功登录
    await prisma.loginAttempt.create({
      data: {
        userId: user.id,
        success: true,
        ip: req.headers.get("x-forwarded-for") || "unknown",
        userAgent: req.headers.get("user-agent") || "",
      },
    });
    
    // 设置安全Cookie
    const response = NextResponse.json({
      success: true,
      user: { id: user.id, email: user.email, name: user.name },
    });
    
    response.cookies.set("session", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      maxAge: 7 * 24 * 60 * 60, // 7天
      path: "/",
    });
    
    return response;
    
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json(
      { error: "服务器错误，请稍后重试" },
      { status: 500 }
    );
  }
}
```

---

## L3 企业版（深耕版）

企业级暴力破解防护需要更完善的体系：

**1. 高级威胁检测**
- 机器学习模型识别异常模式
- 用户行为分析
- 设备信任评分

**2. 自适应认证**
- 风险自适应MFA
- 步进式认证
- 无感知验证

**3. 完整监控体系**
- SIEM集成
- 实时威胁大屏
- 自动化响应

**详细内容请参考企业级案例**：
- [企业级认证安全](../../enterprise/bizsec/auth/authentication-enterprise.md)
- [威胁检测系统](../../enterprise/infosec/threat-detection.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基础限流 | $0 | 2小时 | 1小时/月 | MVP阶段 |
| L2-方案A（自建） | $0 | 4小时 | 2小时/月 | 技术团队 |
| L2-方案B（SaaS） | $0 | 1小时 | 0小时/月 | 推荐 |
| L2-方案C（增强） | $10-20 | 3小时 | 1小时/月 | 处理敏感数据 |
| L3-企业级 | $200+ | 需评估 | 专职团队 | 企业级应用 |

---

## 常见问题

**Q: 账号锁定会不会影响正常用户？**
A: 合理设置阈值（5次失败锁定15分钟）很少误伤。极端情况下，用户可以通过邮箱验证码解锁。

**Q: IP限流会不会误伤共享网络用户？**
A: 可能会。建议：
- IP限流作为补充，账号限流为主
- 结合验证码减少误伤
- 对可信IP放宽限制

**Q: 验证码会不会影响用户体验？**
A: 使用无感知验证（如Turnstile）可以做到用户无感。只在检测到可疑行为时弹出。

**Q: 分布式攻击如何防护？**
A: 
- 使用账号级别限流（不受IP数量影响）
- 使用智能防护服务（如Arcjet、Auth0）
- 添加设备指纹验证

**Q: 如何平衡安全性和用户体验？**
A: 推荐方案：
- 基础限流：5次失败锁定15分钟
- 指数退避：增加攻击成本，不明显影响用户
- 智能验证：只在可疑时要求验证码
- 异常告警：新设备/异地登录通知

---

## 相关资源

**工具**
- [Arcjet](https://arcjet.com/) - 免费智能防护
- [hCaptcha](https://www.hcaptcha.com/) - 免费验证码
- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/) - 免费智能验证
- [Auth0](https://auth0.com/) - 认证服务

**学习资源**
- [OWASP Brute Force Attack](https://owasp.org/www-community/attacks/Brute_force_attack)
- [NIST Authentication Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)

**相关案例**
- [撞库攻击](./credential-stuffing.md)
- [弱密码风险](./weak-password.md)
- [Session劫持](./session-hijacking.md)
