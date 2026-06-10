# 撞库攻击（Credential Stuffing）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $10-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
黑客用网上泄露的账号密码尝试登录你的SaaS产品，成功登录的用户账号会被盗用，可能导致用户数据泄露、恶意操作甚至经济损失。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 有用户登录功能（邮箱/用户名 + 密码）
- [ ] 登录失败没有次数限制或限制宽松（如允许连续失败10次以上）
- [ ] 没有图形验证码或行为验证
- [ ] 登录成功后没有异地登录提醒
- [ ] 用户可能在不同网站使用相同密码
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
给登录接口加登录失败次数限制（5次失败锁定15分钟）+ 图形验证码。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 给登录接口添加失败次数限制：同一账号连续失败5次，锁定15分钟
   - [ ] 记录登录失败的IP地址和时间（简单日志即可）
   - [ ] 测试：用错误密码连续尝试登录，确认锁定机制生效

2. **短期行动**（本周可完成，免费）
   - [ ] 添加图形验证码（推荐开源方案：hCaptcha 免费版 / reCAPTCHA v3）
   - [ ] 实现异地登录邮件提醒（检测IP地理位置变化）
   - [ ] 查看日志：统计最近是否有异常高频登录失败

3. **长期行动**（规划中，低成本）
   - [ ] 引导用户开启双因素认证（2FA）
   - [ ] 集成威胁情报API检测泄露密码
   - [ ] 建立自动化告警机制

### 推荐工具
- **免费**：
  - [hCaptcha](https://www.hcaptcha.com/) - 免费无限制验证码
  - [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/) - 免费智能验证
  - 开源限流库（见L2代码示例）

- **低成本**：
  - [Auth0](https://auth0.com/) - 免费额度7000活跃用户/月
  - [Supabase Auth](https://supabase.com/auth) - 免费50000活跃用户/月
  - [Arcjet](https://arcjet.com/) - 免费100万请求/月限流+防护

### 验证方法
- [ ] 测试步骤1：用错误密码连续登录5次，第6次应被拒绝
- [ ] 测试步骤2：等待15分钟后，应能继续尝试登录
- [ ] 测试步骤3：检查日志是否记录了失败IP和时间
- [ ] 测试步骤4：添加验证码后，自动化脚本应无法绕过

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有2000个用户，其中30%的用户习惯在不同网站使用相同密码。某天，黑客获取了一个包含100万条账号密码的泄露数据库，使用自动化脚本对你的登录接口发起撞库攻击：

- **攻击速度**：每秒尝试50次登录
- **成功率**：约2%（行业标准，撞库成功率通常1-5%）
- **受影响用户**：约400个账号可能被成功登录
- **潜在损失**：用户数据泄露、恶意订单、资金盗用、品牌信任崩塌

你的服务器日志显示：
```
[2026-06-10 03:22:15] POST /api/login - user@example.com - FAIL (IP: 45.33.*.*)
[2026-06-10 03:22:15] POST /api/login - user2@example.com - FAIL (IP: 45.33.*.*)
[2026-06-10 03:22:16] POST /api/login - user3@example.com - FAIL (IP: 45.33.*.*)
... 连续数万次请求 ...
```

### 攻击路径（简化版）

**第一阶段：数据获取**
1. 黑客从暗网或公开泄露数据库获取账号密码列表（如LinkedIn 2012泄露、Collection #1-5等）
2. 数据格式通常为：`邮箱/用户名:密码` 明文或简单哈希

**第二阶段：自动化攻击**
3. 使用工具（如Sentry MBA、SNIPR）配置目标网站的登录接口
4. 编写脚本批量尝试登录，自动识别成功/失败响应
5. 绕过简单防护：轮换代理IP、随机延时、伪装User-Agent

**第三阶段：利益变现**
6. 成功登录的账号被收集出售或直接利用
7. 窃取账户余额、读取敏感数据、发起欺诈交易
8. 利用信任关系进行钓鱼（如向账号好友发送诈骗信息）

### 防御实施（低成本方案）

#### 方案A：免费方案（纯自建）

**1. IP级别限流**
```python
# Flask 示例：使用 Redis 实现IP限流
from flask import Flask, request, jsonify
from redis import Redis
import time

app = Flask(__name__)
redis = Redis(host='localhost', port=6379, db=0)

def check_rate_limit(ip):
    """检查IP是否被限流"""
    key = f"login_attempts:{ip}"
    attempts = redis.get(key)

    if attempts and int(attempts) >= 10:  # IP级别：10次失败后限流
        ttl = redis.ttl(key)
        return False, ttl

    return True, 0

def record_failed_attempt(ip):
    """记录登录失败"""
    key = f"login_attempts:{ip}"
    redis.incr(key)
    redis.expire(key, 900)  # 15分钟过期

@app.route('/api/login', methods=['POST'])
def login():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)

    # 检查IP限流
    allowed, ttl = check_rate_limit(ip)
    if not allowed:
        return jsonify({
            'error': f'Too many attempts. Try again in {ttl} seconds.'
        }), 429

    # 模拟登录验证
    email = request.json.get('email')
    password = request.json.get('password')

    if authenticate_user(email, password):  # 你的认证逻辑
        redis.delete(f"login_attempts:{ip}")
        return jsonify({'success': True})
    else:
        record_failed_attempt(ip)
        return jsonify({'error': 'Invalid credentials'}), 401
```

**2. 账号级别锁定**
```python
def check_account_lock(email):
    """检查账号是否被锁定"""
    key = f"account_lock:{email}"
    lock_info = redis.get(key)

    if lock_info:
        attempts, lock_time = json.loads(lock_info)
        if attempts >= 5:  # 5次失败后锁定
            return False, lock_time

    return True, 0

def record_account_failed(email):
    """记录账号失败尝试"""
    key = f"account_lock:{email}"
    lock_info = redis.get(key)

    if lock_info:
        attempts, _ = json.loads(lock_info)
        attempts += 1
    else:
        attempts = 1

    redis.set(key, json.dumps([attempts, time.time()]), ex=900)  # 15分钟
```

**局限性**：
- 需要自己维护Redis服务
- IP限流可能误伤共享IP用户（如公司网络、咖啡厅WiFi）
- 无法识别分布式攻击（大量不同IP）

---

#### 方案B：低成本方案（$10-50/月）

**使用 Arcjet 实现智能防护**

Arcjet 提供免费额度（100万请求/月），集成简单：

```javascript
// Next.js 示例
import arcjet, { detectBot, shield, tokenBucket } from "@arcjet/next";

const aj = arcjet({
  key: process.env.ARCJET_KEY, // 免费获取
  rules: [
    // 防护盾：检测常见攻击模式
    shield({ mode: "LIVE" }),

    // 机器人检测
    detectBot({
      mode: "LIVE",
      allow: [], // 拒绝所有自动化工具
    }),

    // 限流：同一IP每分钟最多10次登录
    tokenBucket({
      mode: "LIVE",
      refillRate: 5, // 每分钟补充5个令牌
      interval: 60,
      capacity: 10, // 最大10个令牌
    }),
  ],
});

export async function POST(req) {
  const decision = await aj.protect(req);

  if (decision.isDenied()) {
    return Response.json(
      { error: "Access denied" },
      { status: 403 }
    );
  }

  // 你的登录逻辑
  return handleLogin(req);
}
```

**使用 Supabase Auth（免费50000活跃用户/月）**

Supabase 内置了撞库防护：

```javascript
// 注册/登录自动获得防护
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// 登录
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123',
})

// Supabase 自动提供：
// - 登录失败限流
// - 异常行为检测
// - IP信誉评分
// - 可疑登录告警
```

**优势**：
- 无需维护Redis
- 自动识别分布式攻击
- 提供可视化仪表盘
- 内置异地登录检测
- 免费额度足够小型SaaS使用

---

#### 方案C：增强方案（+$20-30/月）

在方案B基础上添加：

**1. 密码泄露检测**

使用 Have I Been Pwned API 检测用户密码是否在已知泄露中：

```python
import hashlib
import requests

def check_password_breach(password):
    """检查密码是否在泄露数据库中"""
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    # k-anonymity API：只发送前5位
    response = requests.get(
        f'https://api.pwnedpasswords.com/range/{prefix}'
    )

    # 检查完整哈希是否在结果中
    for line in response.text.splitlines():
        hash_suffix, count = line.split(':')
        if hash_suffix == suffix:
            return int(count)  # 泄露次数

    return 0  # 未泄露

# 注册时检查
breach_count = check_password_breach(password)
if breach_count > 0:
    return "此密码已在数据泄露中出现，请更换密码"
```

**2. 异地登录告警**

```python
import geoip2.database

def check_geo_change(email, current_ip):
    """检测异地登录"""
    reader = geoip2.database.Reader('GeoLite2-City.mmdb')

    # 获取当前位置
    current_location = reader.city(current_ip)

    # 获取上次登录位置（从数据库读取）
    last_location = get_last_login_location(email)

    if last_location:
        distance = calculate_distance(
            current_location.location.latitude,
            current_location.location.longitude,
            last_location['lat'],
            last_location['lon']
        )

        # 距离超过500km且时间间隔<24小时
        if distance > 500:
            send_email_alert(
                email,
                f"检测到异地登录，位置：{current_location.city.name}"
            )
```

---

### 决策树

```
你的产品是否有用户登录功能？
├── 否 → 无需防护
└── 是 →
    你的技术栈是什么？
    ├── Node.js/Next.js → 使用 Arcjet（免费100万请求/月）
    ├── 任意框架 → 使用 Supabase Auth（免费50000用户/月）
    └── 自建后端 → 使用 Redis 实现限流（见方案A）

    是否处理敏感数据（支付、个人隐私）？
    ├── 是 → 添加密码泄露检测 + 异地登录告警（+$20/月）
    └── 否 → 基础防护足够

    你的用户是否可能使用弱密码？
    ├── 是 → 强制密码强度检查 + 引导开启2FA
    └── 否 → 基础防护足够
```

### 完整代码示例

**Next.js + Arcjet 完整防护方案**

```typescript
// app/api/auth/login/route.ts
import arcjet, { detectBot, shield, tokenBucket } from "@arcjet/next";
import { NextResponse } from "next/server";
import { signIn } from "@/lib/auth";

const aj = arcjet({
  key: process.env.ARCJET_KEY!,
  rules: [
    shield({ mode: "LIVE" }),
    detectBot({ mode: "LIVE", allow: [] }),
    tokenBucket({
      mode: "LIVE",
      refillRate: 5,
      interval: 60,
      capacity: 10,
    }),
  ],
});

export async function POST(req: Request) {
  try {
    // Arcjet 防护检查
    const decision = await aj.protect(req);

    if (decision.isDenied()) {
      if (decision.reason.isRateLimit()) {
        return NextResponse.json(
          { error: "登录尝试过于频繁，请15分钟后再试" },
          { status: 429 }
        );
      }

      if (decision.reason.isBot()) {
        return NextResponse.json(
          { error: "检测到自动化工具，访问被拒绝" },
          { status: 403 }
        );
      }

      return NextResponse.json(
        { error: "访问被拒绝" },
        { status: 403 }
      );
    }

    // 解析请求
    const { email, password } = await req.json();

    // 验证输入
    if (!email || !password) {
      return NextResponse.json(
        { error: "邮箱和密码不能为空" },
        { status: 400 }
      );
    }

    // 检查密码是否在泄露数据库中（可选）
    const breachCount = await checkPasswordBreach(password);
    if (breachCount > 0) {
      // 允许登录但发送警告
      await sendBreachWarningEmail(email, breachCount);
    }

    // 执行登录
    const result = await signIn(email, password);

    if (!result.success) {
      return NextResponse.json(
        { error: "邮箱或密码错误" },
        { status: 401 }
      );
    }

    // 检测异地登录（可选）
    const ip = req.headers.get("x-forwarded-for") || "unknown";
    await checkAndAlertGeoChange(email, ip);

    return NextResponse.json({
      success: true,
      user: result.user,
    });
  } catch (error) {
    console.error("Login error:", error);
    return NextResponse.json(
      { error: "服务器错误" },
      { status: 500 }
    );
  }
}

// 辅助函数
async function checkPasswordBreach(password: string): Promise<number> {
  const sha1 = Array.from(
    new Uint8Array(
      await crypto.subtle.digest("SHA-1", new TextEncoder().encode(password))
    )
  )
    .map(b => b.toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();

  const prefix = sha1.substring(0, 5);
  const suffix = sha1.substring(5);

  const response = await fetch(
    `https://api.pwnedpasswords.com/range/${prefix}`
  );
  const text = await response.text();

  for (const line of text.split("\n")) {
    const [hashSuffix, count] = line.split(":");
    if (hashSuffix === suffix) {
      return parseInt(count, 10);
    }
  }

  return 0;
}

async function checkAndAlertGeoChange(email: string, ip: string) {
  // 实现异地登录检测
  // 可以使用 MaxMind GeoIP 数据库
}
```

**前端登录表单配合**

```typescript
// components/LoginForm.tsx
"use client";

import { useState } from "react";

export function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || "登录失败");
        return;
      }

      // 登录成功
      window.location.href = "/dashboard";
    } catch (err) {
      setError("网络错误，请重试");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="email">邮箱</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full p-2 border rounded"
        />
      </div>

      <div>
        <label htmlFor="password">密码</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full p-2 border rounded"
        />
      </div>

      {error && (
        <div className="p-3 bg-red-50 text-red-700 rounded">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full p-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {loading ? "登录中..." : "登录"}
      </button>
    </form>
  );
}
```

---

## L3 企业版（深耕版）

企业级撞库防护需要更完善的体系化方案，包括：

**1. 多维度威胁检测**
- 设备指纹识别
- 行为生物特征分析
- IP信誉评分系统
- 威胁情报集成

**2. 高级验证机制**
- 风险自适应认证
- 无感知验证（行为验证码）
- 多因素认证强制策略

**3. 完整监控体系**
- SIEM系统集成
- 实时威胁大屏
- 自动化应急响应
- 取证分析能力

**详细内容请参考企业级案例**：
- [企业级撞库防护方案](../../enterprise/bizsec/auth/credential-stuffing-enterprise.md)
- [威胁情报集成指南](../../enterprise/infosec/threat-intelligence.md)
- [应急响应剧本](../../modules/incident-playbook/credential-stuffing-response.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基础限流 | $0 | 2小时 | 1小时/月 | MVP阶段，用户<1000 |
| L2-方案A（自建） | $0 | 4小时 | 2小时/月 | 技术团队，有Redis经验 |
| L2-方案B（SaaS） | $0-10 | 1小时 | 0.5小时/月 | 快速上线，无运维压力 |
| L2-方案C（增强） | $20-30 | 3小时 | 1小时/月 | 处理敏感数据 |
| L3-企业级 | $200+ | 需评估 | 专职团队 | 金融、医疗、政务 |

---

## 常见问题

**Q: 我的用户很少，真的需要防护吗？**
A: 需要。自动化攻击不会因为你的用户少就放过你，反而小网站更容易成为目标（因为防护更弱）。

**Q: 限流会不会影响正常用户？**
A: 合理设置阈值（如5次失败锁定15分钟）不会影响正常用户。极少数误伤可以通过邮箱验证码解锁。

**Q: 验证码会不会降低用户体验？**
A: 使用无感知验证（如Arcjet、reCAPTCHA v3）可以做到用户无感。只有在检测到可疑行为时才需要验证。

**Q: 密码泄露检测会不会泄露我的密码？**
A: 不会。k-anonymity协议只发送密码哈希的前5位，完整密码不会发送给第三方。

**Q: 如果我已经被攻击了怎么办？**
A: 参考[应急响应剧本](../../modules/incident-playbook/credential-stuffing-response.md)：
1. 立即启用严格限流（1次失败即锁定）
2. 强制所有用户重置密码
3. 分析日志定位受影响账号
4. 通知用户并提供补偿

---

## 相关资源

**工具**
- [Arcjet](https://arcjet.com/) - 免费智能防护
- [Supabase Auth](https://supabase.com/auth) - 免费认证服务
- [hCaptcha](https://www.hcaptcha.com/) - 免费验证码
- [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/) - 免费智能验证

**学习资源**
- [OWASP Credential Stuffing Prevention](https://owasp.org/www-community/attacks/Credential_stuffing)
- [Have I Been Pwned API](https://haveibeenpwned.com/API/v3)
- [NIST密码指南](https://pages.nist.gov/800-63-3/sp800-63b.html)

**相关案例**
- [弱密码攻击](./weak-password.md)
- [Session劫持](./session-hijacking.md)
- [暴力破解](./brute-force.md)
