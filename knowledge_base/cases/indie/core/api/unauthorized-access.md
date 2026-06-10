# API 未授权访问

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的公开API没有身份验证，任何人都可以无限调用，服务器资源被滥用、账单爆炸、服务瘫痪。

### 一分钟识别
你的产品是否有以下特征：
- [ ] API端点没有要求任何认证信息（API Key / Token / Session）
- [ ] 任何人知道URL就能直接访问数据或功能
- [ ] 没有对单个IP或用户的调用频率做限制
- [ ] 敏感操作（查询、修改、删除数据）没有权限校验
→ 勾选≥1项，即需关注此风险

### 一句话防御
给每个API加一个简单的 API Key 验证 + 基础速率限制，30分钟内可实施，完全免费。

### 快速行动清单
1. [ ] **立即（今天）**：在API网关或应用层添加 API Key 认证中间件
2. [ ] **短期（本周）**：为每个用户/应用分配独立的 API Key，添加速率限制（如 100次/分钟/IP）
3. [ ] **长期（规划中）**：接入免费监控告警，监控异常调用模式

### 推荐工具
- **免费**：
  - [Cloudflare Workers](https://workers.cloudflare.com/) - 免费额度10万次/天，自带速率限制
  - [Upstash Rate Limit](https://upstash.com/) - 免费10K请求/天，Redis速率限制
  - [Express Rate Limit](https://github.com/nfriedly/express-rate-limit) - Node.js内存限流，零成本
- **低成本**：
  - [Vercel Edge Functions](https://vercel.com/) - $20/月起，内置安全中间件
  - [Supabase Auth](https://supabase.com/) - 免费50K活跃用户，自带API Key管理

### 验证方法
- [ ] 用 Postman 或 curl 不带任何认证信息调用 API，应返回 401 Unauthorized
- [ ] 用正确的 API Key 调用，应正常返回数据
- [ ] 连续快速调用超过限制次数，应返回 429 Too Many Requests

---

## L2 小团队版（理解版）

### 场景还原
你的产品是一个图片处理 API 服务。某天凌晨，你的服务器CPU飙升到100%，数据库连接池耗尽，用户投诉服务不可用。查看日志发现，某个IP在过去1小时内调用了你的 API **120万次**——消耗了$300的云服务费用，而你当月总收入才$500。更糟糕的是，攻击者通过你的API爬取了所有用户数据。

### 攻击路径（简化版）
1. **发现目标**：攻击者通过搜索引擎或端口扫描发现你的公开API端点 `api.yourapp.com/v1/images`
2. **验证漏洞**：用 curl 测试发现无需任何认证即可调用，返回完整数据
3. **资源滥用**：编写脚本每秒发起100次请求，持续消耗你的服务器资源和带宽
4. **数据爬取**：遍历API参数，批量获取所有用户数据（如果API返回敏感信息）
5. **持续攻击**：即使你重启服务，攻击者脚本自动恢复，持续数天

### 防御实施（低成本方案）

#### 方案A：免费方案（纯代码实现）

**工具/服务**: 应用层中间件 + 内存限流

**配置步骤**:

```javascript
// Node.js + Express 示例
const express = require('express');
const rateLimit = require('express-rate-limit');
const app = express();

// 1. API Key 认证中间件
const VALID_API_KEYS = new Set([
  process.env.API_KEY_USER_1,
  process.env.API_KEY_USER_2,
  // 从数据库或环境变量加载
]);

function apiKeyAuth(req, res, next) {
  const apiKey = req.headers['x-api-key'] || req.query.api_key;
  
  if (!apiKey || !VALID_API_KEYS.has(apiKey)) {
    return res.status(401).json({ error: 'Unauthorized: Invalid or missing API key' });
  }
  
  // 可选：记录API Key对应的用户信息到 req.user
  req.apiKey = apiKey;
  next();
}

// 2. 速率限制中间件
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1分钟窗口
  max: 100, // 每分钟最多100次
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later.' },
  // 基于IP + API Key组合限流
  keyGenerator: (req) => `${req.ip}-${req.headers['x-api-key']}`,
});

// 3. 应用到所有API路由
app.use('/api/', apiKeyAuth, limiter);

// 你的业务路由
app.get('/api/v1/images', (req, res) => {
  // 正常业务逻辑
  res.json({ images: [...] });
});

app.listen(3000);
```

**局限性**:
- 内存限流在多实例部署时不共享状态
- API Key 管理需要手动维护
- 无持久化的调用日志和审计

#### 方案B：低成本方案（<$50/月）

**工具/服务**: Upstash Redis + Clerk/Auth0 身份认证

**配置步骤**:

```javascript
// 使用 Upstash Redis 实现分布式限流
import { Redis } from '@upstash/redis';
import { Ratelimit } from '@upstash/ratelimit';
import { ClerkExpressWithAuth } from '@clerk/clerk-sdk-node';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
});

// 分布式速率限制器
const ratelimit = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(100, '1 m'), // 100次/分钟
  analytics: true, // 启用分析
  prefix: 'ratelimit',
});

// Clerk 认证中间件
const requireAuth = ClerkExpressWithAuth({});

app.use('/api/', requireAuth);

app.use('/api/', async (req, res, next) => {
  // 检查认证
  if (!req.auth?.userId) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  // 速率限制
  const { success, limit, reset, remaining } = await ratelimit.limit(
    `api-${req.auth.userId}`
  );
  
  res.setHeader('X-RateLimit-Limit', limit);
  res.setHeader('X-RateLimit-Remaining', remaining);
  res.setHeader('X-RateLimit-Reset', reset);
  
  if (!success) {
    return res.status(429).json({ 
      error: 'Rate limit exceeded',
      resetAt: new Date(reset).toISOString()
    });
  }
  
  req.userId = req.auth.userId;
  next();
});

// 业务路由
app.get('/api/v1/images', async (req, res) => {
  // req.userId 已通过认证
  const images = await getImagesForUser(req.userId);
  res.json({ images });
});
```

**成本估算**:
- Upstash Redis 免费层: 10K 请求/天
- 超出后: $0.2/100K 请求
- Clerk 免费层: 5K MAU
- 超出后: $25/月（10K MAU）

**优势**:
- 分布式限流，多实例共享状态
- 完整的用户认证和API Key管理
- 自带分析面板，可查看调用趋势
- 支持多种认证方式（OAuth、Email、手机号）

### 决策树

```
你的API是否对外公开？
├── 否（仅内部服务调用）→ 考虑网络层隔离（VPC/防火墙），可简化认证
└── 是（公开API）
    ├── 是否处理敏感数据？
    │   ├── 是 → 方案B（完整认证 + 分布式限流 + 审计日志）
    │   └── 否 → 方案A（简单认证 + 内存限流）
    └── 是否需要多实例部署？
        ├── 是 → 方案B（Upstash Redis 分布式限流）
        └── 否 → 方案A足够
```

### 完整代码示例

以下是一个完整的 Next.js API Route 示例，包含认证和限流：

```typescript
// app/api/v1/images/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

// 初始化 Redis 限流器（单例模式）
const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(100, '1 m'),
  analytics: true,
  prefix: 'api-ratelimit',
});

// API Key 验证
function validateApiKey(authHeader: string | null): { valid: boolean; userId?: string } {
  if (!authHeader?.startsWith('Bearer ')) {
    return { valid: false };
  }
  
  const token = authHeader.slice(7);
  
  // 从数据库验证 API Key（示例：使用环境变量模拟）
  // 生产环境应使用数据库或认证服务
  const apiKeys: Record<string, string> = {
    [process.env.API_KEY_ADMIN!]: 'admin',
    [process.env.API_KEY_USER_1!]: 'user_1',
    [process.env.API_KEY_USER_2!]: 'user_2',
  };
  
  const userId = apiKeys[token];
  return userId ? { valid: true, userId } : { valid: false };
}

export async function GET(request: NextRequest) {
  // 1. 认证检查
  const authHeader = request.headers.get('authorization');
  const { valid, userId } = validateApiKey(authHeader);
  
  if (!valid) {
    return NextResponse.json(
      { error: 'Unauthorized', message: 'Invalid or missing API key' },
      { status: 401 }
    );
  }
  
  // 2. 速率限制
  const ip = request.ip || 'unknown';
  const identifier = `${userId}-${ip}`;
  
  const { success, limit, reset, remaining } = await ratelimit.limit(identifier);
  
  // 3. 返回限流头信息
  const headers = {
    'X-RateLimit-Limit': limit.toString(),
    'X-RateLimit-Remaining': remaining.toString(),
    'X-RateLimit-Reset': new Date(reset).toISOString(),
  };
  
  if (!success) {
    return NextResponse.json(
      { 
        error: 'Rate limit exceeded', 
        message: `Try again at ${new Date(reset).toISOString()}` 
      },
      { status: 429, headers }
    );
  }
  
  // 4. 业务逻辑（示例）
  try {
    // 根据 userId 获取数据
    const images = await getImagesForUser(userId!);
    
    return NextResponse.json(
      { data: images, meta: { userId } },
      { headers }
    );
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// 示例数据获取函数
async function getImagesForUser(userId: string) {
  // 实际实现从数据库获取
  return [
    { id: 1, url: 'https://example.com/image1.jpg', userId },
    { id: 2, url: 'https://example.com/image2.jpg', userId },
  ];
}
```

**环境变量配置** (`.env.local`):
```bash
# Upstash Redis
UPSTASH_REDIS_REST_URL=https://your-redis.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token_here

# API Keys（生产环境应存储在数据库）
API_KEY_ADMIN=sk_live_admin_xxxxx
API_KEY_USER_1=sk_live_user1_xxxxx
API_KEY_USER_2=sk_live_user2_xxxxx
```

---

## L3 企业版（深耕版）

本案例的企业级扩展内容，请参考企业版案例库：

- **详细攻击技术**：参见 [enterprise/infosec/api/broken-authentication.md](../../../enterprise/infosec/api/broken-authentication.md)
- **企业防御架构**：WAF策略、API网关安全、零信任架构
- **合规要求**：OWASP API Security Top 10、SOC 2 API控制、GDPR数据处理
- **监控告警**：SIEM集成、异常检测算法、自动化响应
- **渗透测试**：API安全测试清单、自动化扫描工具、红队演练

企业版核心补充：
1. **API生命周期安全**：设计、开发、测试、部署、运维、下线全流程
2. **多租户隔离**：租户级认证、数据隔离、资源配额
3. **审计与合规**：完整的调用链追踪、合规报告生成
4. **高级威胁防护**：API滥用检测、爬虫识别、Bot管理
