# 邮箱泄露风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $10-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的用户邮箱列表因为 API 未做权限校验或导出功能无限制，被攻击者批量爬取后用于钓鱼攻击，用户投诉激增、品牌信誉受损。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 用户系统存储邮箱地址
- [ ] 有用户列表或通讯录功能
- [ ] **API 接口返回完整邮箱地址**
- [ ] **数据导出功能无权限限制**
- [ ] 前端直接显示完整邮箱
- [ ] 搜索/筛选功能可枚举用户
→ 勾选≥2项，尤其是中间两项，**立即行动**

### 一句话防御
在所有对外接口中脱敏显示邮箱（如 `z***@gmail.com`），并限制用户列表 API 的访问频率和返回字段，导出功能需二次验证。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查 API 返回字段**：
   ```bash
   # 测试你的用户 API
   curl https://your-api.com/api/users
   
   # 如果返回完整邮箱 = 有风险
   # {"email": "user@gmail.com"}  # 危险
   # {"email": "u***@gmail.com"}  # 安全
   ```

2. [ ] **实现邮箱脱敏显示**：
   ```javascript
   // 后端脱敏函数
   function maskEmail(email) {
     const [local, domain] = email.split('@')
     const maskedLocal = local[0] + '***' + local.slice(-1)
     return `${maskedLocal}@${domain}`
   }
   
   // 示例
   maskEmail('zhangsan@gmail.com')  // 'z***n@gmail.com'
   maskEmail('a@qq.com')            // 'a***@qq.com'
   ```

3. [ ] **限制用户列表 API**：
   ```javascript
   // 只返回必要字段
   app.get('/api/users', auth, async (req, res) => {
     const users = await User.find()
       .select('id name avatar')  // 不返回 email
       .limit(20)
     
     res.json(users)
   })
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **添加访问频率限制**：
   ```javascript
   // 使用 rate-limit
   const rateLimit = require('express-rate-limit')
   
   const userApiLimiter = rateLimit({
     windowMs: 15 * 60 * 1000,  // 15 分钟
     max: 100,  // 每 15 分钟最多 100 次请求
     message: '请求过于频繁，请稍后再试'
   })
   
   app.use('/api/users', userApiLimiter)
   ```

2. [ ] **导出功能二次验证**：
   ```javascript
   // 导出前要求输入密码或邮箱验证码
   app.post('/api/users/export', 
     auth, 
     requireReauth,  // 二次验证中间件
     async (req, res) => {
       // 生成导出任务，后台处理
       // 发送邮件通知下载链接
     }
   )
   ```

3. [ ] **添加操作日志**：
   ```javascript
   // 记录所有数据访问
   const logAccess = (action) => {
     return async (req, res, next) => {
       await AccessLog.create({
         userId: req.user.id,
         action,
         ip: req.ip,
         userAgent: req.headers['user-agent'],
         timestamp: new Date()
       })
       next()
     }
   }
   
   app.get('/api/users', auth, logAccess('list_users'), userController.list)
   ```

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用数据脱敏库**：集成专业脱敏工具
2. [ ] **添加异常检测**：监控异常爬取行为
3. [ ] **实施数据最小化原则**：只收集必要数据

### 邮箱脱敏显示实现

**多场景脱敏方案**：

```javascript
// utils/email-mask.js

/**
 * 邮箱脱敏显示
 * @param {string} email - 原始邮箱
 * @param {string} level - 脱敏级别: 'light' | 'medium' | 'heavy'
 * @returns {string} 脱敏后的邮箱
 */
function maskEmail(email, level = 'medium') {
  if (!email || !email.includes('@')) {
    return email
  }

  const [local, domain] = email.split('@')
  const domainParts = domain.split('.')
  const tld = domainParts.pop()
  const domainName = domainParts.join('.')

  switch (level) {
    case 'light':
      // 轻度脱敏: zhang***@gmail.com
      return `${local.slice(0, 4)}***@${domain}`
    
    case 'medium':
      // 中度脱敏: z***n@gmail.com（默认）
      if (local.length <= 2) {
        return `${local[0]}***@${domain}`
      }
      return `${local[0]}***${local.slice(-1)}@${domain}`
    
    case 'heavy':
      // 重度脱敏: z***@g***.com
      const maskedDomain = domainName[0] + '***'
      return `${local[0]}***@${maskedDomain}.${tld}`
    
    case 'hash':
      // 哈希显示: 用户ID或哈希值
      const hash = require('crypto')
        .createHash('sha256')
        .update(email)
        .digest('hex')
        .slice(0, 8)
      return `user_${hash}@***`
    
    default:
      return maskEmail(email, 'medium')
  }
}

/**
 * 根据用户权限决定脱敏级别
 */
function maskEmailByRole(email, viewerRole) {
  const levels = {
    'admin': null,        // 不脱敏
    'manager': 'light',   // 轻度
    'support': 'medium',  // 中度
    'user': 'heavy',      // 重度
    'public': 'hash'      // 哈希
  }
  
  const level = levels[viewerRole] || 'heavy'
  return level ? maskEmail(email, level) : email
}

// 示例
console.log(maskEmail('zhangsan@gmail.com'))
// z***n@gmail.com

console.log(maskEmail('zhangsan@gmail.com', 'light'))
// zhang***@gmail.com

console.log(maskEmail('zhangsan@gmail.com', 'heavy'))
// z***@g***.com
```

**前端展示组件（React）**：

```tsx
// components/MaskedEmail.tsx
import { useState } from 'react'
import { maskEmail, maskEmailByRole } from '@/utils/email-mask'

interface Props {
  email: string
  role?: string
  showReveal?: boolean
  onReveal?: () => Promise<boolean>
}

export function MaskedEmail({ 
  email, 
  role = 'user', 
  showReveal = false,
  onReveal 
}: Props) {
  const [revealed, setRevealed] = useState(false)

  const handleReveal = async () => {
    if (onReveal) {
      const allowed = await onReveal()
      if (allowed) {
        setRevealed(true)
        // 记录查看行为
        logEmailReveal(email)
      }
    }
  }

  const displayEmail = revealed 
    ? email 
    : maskEmailByRole(email, role)

  return (
    <span className="masked-email">
      {displayEmail}
      {showReveal && !revealed && (
        <button 
          onClick={handleReveal}
          className="reveal-btn text-blue-500 text-xs ml-2"
        >
          显示完整
        </button>
      )}
    </span>
  )
}

// 使用示例
<MaskedEmail 
  email="user@example.com" 
  role={currentUser.role}
  showReveal={currentUser.role === 'admin'}
  onReveal={async () => {
    // 验证权限或记录日志
    return true
  }}
/>
```

### 导出限制机制

**完整导出安全方案**：

```javascript
// middleware/export-control.js

const { RateLimiter } = require('limiter')
const crypto = require('crypto')

// 导出频率限制器（每个用户）
const exportLimiters = new Map()

/**
 * 获取用户的导出限制器
 */
function getUserLimiter(userId) {
  if (!exportLimiters.has(userId)) {
    exportLimiters.set(userId, new RateLimiter({
      tokensPerInterval: 3,  // 每天最多 3 次
      interval: 'day'
    }))
  }
  return exportLimiters.get(userId)
}

/**
 * 导出权限中间件
 */
async function exportControl(req, res, next) {
  const userId = req.user.id
  
  // 1. 频率限制
  const limiter = getUserLimiter(userId)
  const canExport = await limiter.removeTokens(1)
  
  if (!canExport) {
    return res.status(429).json({
      error: '导出次数已达上限，请明天再试'
    })
  }

  // 2. 二次验证检查
  const { reauthToken } = req.body
  const validReauth = await verifyReauthToken(userId, reauthToken)
  
  if (!validReauth) {
    return res.status(401).json({
      error: '请重新验证身份',
      requireReauth: true
    })
  }

  // 3. 记录导出请求
  await ExportLog.create({
    userId,
    ip: req.ip,
    userAgent: req.headers['user-agent'],
    timestamp: new Date(),
    dataTypes: req.body.dataTypes
  })

  next()
}

/**
 * 生成导出任务
 */
async function createExportTask(userId, options) {
  const taskId = crypto.randomUUID()
  
  // 创建后台任务
  await ExportTask.create({
    id: taskId,
    userId,
    status: 'pending',
    options,
    createdAt: new Date(),
    expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24小时有效
  })
  
  // 添加到队列
  await exportQueue.add('process', { taskId, userId, options })
  
  return taskId
}

/**
 * 处理导出任务（后台 Worker）
 */
async function processExportTask(task) {
  const { taskId, userId, options } = task
  
  try {
    // 1. 获取数据（根据权限过滤）
    let data = await getExportData(userId, options)
    
    // 2. 敏感字段脱敏
    data = sanitizeExportData(data, options.sensitivity)
    
    // 3. 生成文件
    const filePath = await generateExportFile(data, options.format)
    
    // 4. 上传到临时存储
    const downloadUrl = await uploadToTempStorage(filePath, taskId)
    
    // 5. 发送邮件通知
    await sendExportNotification(userId, downloadUrl)
    
    // 6. 更新任务状态
    await ExportTask.update(taskId, {
      status: 'completed',
      downloadUrl,
      completedAt: new Date()
    })
    
    // 7. 删除本地临时文件
    await fs.unlink(filePath)
    
  } catch (error) {
    await ExportTask.update(taskId, {
      status: 'failed',
      error: error.message
    })
    throw error
  }
}

/**
 * 敏感数据处理
 */
function sanitizeExportData(data, sensitivity = 'medium') {
  const fields = {
    email: sensitivity === 'low' ? 'full' : 'mask',
    phone: 'mask',
    address: sensitivity === 'high' ? 'remove' : 'mask',
    idCard: 'remove',
    password: 'remove'
  }
  
  return data.map(item => {
    const sanitized = { ...item }
    
    if (fields.email === 'mask' && sanitized.email) {
      sanitized.email = maskEmail(sanitized.email, 'heavy')
    }
    
    if (fields.phone === 'mask' && sanitized.phone) {
      sanitized.phone = maskPhone(sanitized.phone)
    }
    
    if (fields.address === 'remove') {
      delete sanitized.address
    }
    
    delete sanitized.password
    delete sanitized.idCard
    
    return sanitized
  })
}

module.exports = {
  exportControl,
  createExportTask,
  processExportTask,
  sanitizeExportData
}
```

### 推荐工具
- **免费**：
  - 自建脱敏函数（上文代码示例）
  - [express-rate-limit](https://github.com/nfriedly/express-rate-limit) - API 限流
  - [morgan](https://github.com/expressjs/morgan) - 访问日志

- **低成本**：
  - [DataDome](https://datadome.co/) - $90/月起，爬虫防护
  - [Imperva](https://www.imperva.com/) - 数据保护
  - [Akamai Bot Manager](https://www.akamai.com/) - 机器人管理

### 验证方法
- [ ] **API 测试**：用户列表 API 不应返回完整邮箱
- [ ] **前端测试**：页面显示邮箱应被脱敏
- [ ] **爬取测试**：模拟批量请求，验证限流生效
- [ ] **导出测试**：验证导出需要二次认证

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2020年，某社交平台因 API 设计缺陷，攻击者通过遍历用户 ID，在 2 小时内爬取了 500 万用户邮箱。攻击者随后：
1. 使用这些邮箱进行钓鱼攻击
2. 在暗网以 $1000 出售邮箱列表
3. 发送大量垃圾邮件

**后果**：
- 500 万用户收到钓鱼邮件
- 平台收到大量用户投诉
- 被 Google 邮件服务列入黑名单
- 品牌信誉严重受损
- 处理成本超过 $50,000

**类似案例**：
- 2021年，某招聘网站用户列表 API 无鉴权，泄露 200 万用户信息
- 2022年，某电商平台通讯录功能可枚举用户，导致钓鱼诈骗

### 攻击路径（简化版）

```
1. 发现目标
   ├── 注册账号，熟悉产品功能
   ├── 发现用户列表/通讯录/搜索功能
   └── 分析 API 请求/响应结构
   
2. 分析 API 漏洞
   ├── GET /api/users?page=1&limit=20
   ├── 响应包含完整邮箱: {"email": "user@gmail.com"}
   ├── 无访问频率限制
   └── 无权限校验（或弱校验）
   
3. 编写爬取脚本
   ├── for page in range(1, 100000):
   │     response = requests.get(f'/api/users?page={page}')
   │     emails.extend(extract_emails(response))
   ├── 或通过用户 ID 遍历
   │     for id in range(1, 1000000):
   │       response = requests.get(f'/api/users/{id}')
   └── 多线程并发爬取
   
4. 批量爬取数据
   ├── 使用代理池避免 IP 封禁
   ├── 分布式爬取（多账号 + 多 IP）
   └── 2-4 小时内爬取数百万条
   
5. 利用数据
   ├── 方式A: 钓鱼攻击
   ├── 方式B: 出售给黑产
   └── 方式C: 垃圾邮件营销
```

**关键数据**：
- 爬取速度：无限制时可达 1000-5000 条/秒
- 成本：攻击者成本 < $100（代理 + VPS）
- 收益：暗网售价 $0.001-0.01/条邮箱
- 影响：用户投诉率通常增加 5-10 倍

### 防御实施（低成本方案）

#### 方案A：免费方案（代码层面防护）

**第一步：API 响应脱敏**

```typescript
// middleware/response-filter.ts
import { Response, NextFunction } from 'express'

interface FieldRule {
  action: 'remove' | 'mask' | 'truncate'
  maskType?: 'email' | 'phone' | 'idCard'
  truncateLength?: number
}

// 字段过滤规则
const fieldRules: Record<string, FieldRule> = {
  'email': { action: 'mask', maskType: 'email' },
  'phone': { action: 'mask', maskType: 'phone' },
  'password': { action: 'remove' },
  'passwordHash': { action: 'remove' },
  'idCard': { action: 'remove' },
  'address': { action: 'truncate', truncateLength: 20 },
  'realName': { action: 'mask', maskType: 'name' }
}

// 脱敏函数
const maskers = {
  email: (value: string) => {
    const [local, domain] = value.split('@')
    return `${local[0]}***${local.slice(-1)}@${domain}`
  },
  phone: (value: string) => {
    return value.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
  },
  name: (value: string) => {
    return value[0] + '*'.repeat(value.length - 1)
  }
}

// 递归过滤对象
function filterObject(obj: any, rules: Record<string, FieldRule>): any {
  if (!obj || typeof obj !== 'object') {
    return obj
  }

  if (Array.isArray(obj)) {
    return obj.map(item => filterObject(item, rules))
  }

  const filtered: any = {}
  for (const [key, value] of Object.entries(obj)) {
    const rule = rules[key]
    
    if (!rule) {
      filtered[key] = filterObject(value, rules)
      continue
    }

    switch (rule.action) {
      case 'remove':
        // 不包含该字段
        break
      
      case 'mask':
        if (rule.maskType && maskers[rule.maskType]) {
          filtered[key] = maskers[rule.maskType](value)
        } else {
          filtered[key] = '***'
        }
        break
      
      case 'truncate':
        filtered[key] = typeof value === 'string' 
          ? value.slice(0, rule.truncateLength) + '...'
          : value
        break
    }
  }

  return filtered
}

// Express 中间件
export function responseFilter(sensitiveFields: Record<string, FieldRule> = fieldRules) {
  return (req: any, res: Response, next: NextFunction) => {
    const originalJson = res.json.bind(res)

    res.json = (data: any) => {
      const filteredData = filterObject(data, sensitiveFields)
      return originalJson(filteredData)
    }

    next()
  }
}

// 使用
app.use('/api', responseFilter())
```

**第二步：访问频率限制**

```typescript
// middleware/rate-limiter.ts
import rateLimit from 'express-rate-limit'
import RedisStore from 'rate-limit-redis'
import Redis from 'ioredis'

const redis = new Redis(process.env.REDIS_URL)

// 通用 API 限流
export const generalLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args)
  }),
  windowMs: 15 * 60 * 1000,  // 15 分钟
  max: 200,  // 每 15 分钟最多 200 次请求
  message: {
    error: '请求过于频繁，请稍后再试',
    retryAfter: '15 minutes'
  },
  standardHeaders: true,
  legacyHeaders: false
})

// 敏感接口严格限流
export const sensitiveLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args)
  }),
  windowMs: 60 * 60 * 1000,  // 1 小时
  max: 20,  // 每小时最多 20 次
  skipSuccessfulRequests: false,
  keyGenerator: (req) => {
    // 基于用户 ID + IP 组合限流
    return `${req.user?.id || req.ip}:sensitive`
  }
})

// 用户列表专用限流
export const userListLimiter = rateLimit({
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args)
  }),
  windowMs: 60 * 60 * 1000,  // 1 小时
  max: 30,  // 每小时最多 30 次列表请求
  keyGenerator: (req) => `user:${req.user?.id}:list`
})

// 应用限流
app.use('/api/', generalLimiter)
app.use('/api/users', userListLimiter)
app.use('/api/users/export', sensitiveLimiter)
```

**第三步：异常行为检测**

```typescript
// services/anomaly-detection.ts

interface AccessPattern {
  userId: string
  endpoint: string
  requestCount: number
  timeWindow: number  // 分钟
  threshold: number
}

// 异常检测规则
const rules: AccessPattern[] = [
  {
    userId: '*',
    endpoint: '/api/users',
    requestCount: 50,
    timeWindow: 5,
    threshold: 50  // 5 分钟内请求用户列表 50 次
  },
  {
    userId: '*',
    endpoint: '/api/users/*',
    requestCount: 100,
    timeWindow: 10,
    threshold: 100  // 10 分钟内查看 100 个用户详情
  }
]

class AnomalyDetector {
  private redis: Redis

  constructor() {
    this.redis = new Redis(process.env.REDIS_URL)
  }

  async checkPattern(req: any): Promise<{ isAnomaly: boolean; reason?: string }> {
    const userId = req.user?.id || 'anonymous'
    const endpoint = this.normalizeEndpoint(req.path)
    
    for (const rule of rules) {
      const key = `anomaly:${userId}:${endpoint}:${rule.timeWindow}m`
      const count = await this.redis.incr(key)
      
      if (count === 1) {
        await this.redis.expire(key, rule.timeWindow * 60)
      }
      
      if (count > rule.threshold) {
        // 记录异常
        await this.logAnomaly(userId, endpoint, count, rule)
        
        return {
          isAnomaly: true,
          reason: `检测到异常访问行为：${rule.timeWindow}分钟内请求${endpoint} ${count}次`
        }
      }
    }
    
    return { isAnomaly: false }
  }

  private normalizeEndpoint(path: string): string {
    // 将 /api/users/123 转换为 /api/users/*
    return path.replace(/\/\d+/g, '/*')
  }

  private async logAnomaly(userId: string, endpoint: string, count: number, rule: AccessPattern) {
    await AnomalyLog.create({
      userId,
      endpoint,
      count,
      threshold: rule.threshold,
      timeWindow: rule.timeWindow,
      timestamp: new Date()
    })
    
    // 发送告警
    await sendAlert({
      level: 'warning',
      message: `异常访问行为检测: 用户 ${userId}`,
      details: {
        endpoint,
        count,
        threshold: rule.threshold
      }
    })
  }
}

// 中间件
export function anomalyDetection() {
  const detector = new AnomalyDetector()
  
  return async (req: any, res: any, next: any) => {
    const result = await detector.checkPattern(req)
    
    if (result.isAnomaly) {
      return res.status(429).json({
        error: '检测到异常行为',
        message: result.reason,
        code: 'ANOMALY_DETECTED'
      })
    }
    
    next()
  }
}
```

#### 方案B：低成本方案（第三方服务）

**DataDome 爬虫防护**：

```javascript
// DataDome 集成
const DataDome = require('@datadome/nodejs')

const dataDome = new DataDome.Client({
  key: process.env.DATADOME_KEY,
  endpoint: 'api.datadome.co'
})

// 中间件
app.use(dataDome.middleware)

// DataDome 会自动检测并阻止：
// - 批量爬虫
// - 机器人流量
// - 异常访问模式
```

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (DataDome) |
|------|------------|------------------|
| 月成本 | $0 | $90+ |
| 配置时间 | 4-8 小时 | 1 小时 |
| 维护时间 | 2 小时/月 | 0 |
| 检测能力 | 基础规则 | AI 驱动 |
| 误报率 | 较高 | 较低 |
| 适应性 | 需手动调整 | 自动学习 |

### 决策树

```
你的产品类型？
├── 面向公众的用户平台
│   ├── 用户 < 10000 → 方案A (DIY)
│   └── 用户 > 10000 → 方案A + 方案B
│
├── 企业内部系统
│   └── 方案A 足够
│
└── 有合规要求（GDPR）
    └── 方案A + 审计日志 + DLP
```

### 代码示例

#### 完整的用户 API 安全实现

```typescript
// routes/users.ts
import { Router } from 'express'
import { auth, requireRole } from '@/middleware/auth'
import { userListLimiter, sensitiveLimiter } from '@/middleware/rate-limiter'
import { anomalyDetection } from '@/middleware/anomaly-detection'
import { responseFilter } from '@/middleware/response-filter'
import { logAccess } from '@/middleware/audit-log'

const router = Router()

// 公开字段（不包含邮箱）
const PUBLIC_FIELDS = 'id name avatar createdAt'
const PROTECTED_FIELDS = 'id name avatar email phone createdAt'

/**
 * 用户列表（脱敏 + 限流）
 */
router.get('/',
  auth,
  userListLimiter,
  anomalyDetection(),
  logAccess('list_users'),
  async (req, res) => {
    const { page = 1, limit = 20, search } = req.query
    
    // 限制每页数量
    const safeLimit = Math.min(Number(limit), 50)
    
    const query = search
      ? { $or: [
          { name: { $regex: search, $options: 'i' } },
          // 不允许通过邮箱搜索
        ]}
      : {}
    
    const users = await User.find(query)
      .select(PUBLIC_FIELDS)  // 不返回邮箱
      .skip((page - 1) * safeLimit)
      .limit(safeLimit)
      .sort({ createdAt: -1 })
    
    const total = await User.countDocuments(query)
    
    res.json({
      users,
      pagination: {
        page: Number(page),
        limit: safeLimit,
        total,
        pages: Math.ceil(total / safeLimit)
      }
    })
  }
)

/**
 * 用户详情（根据权限脱敏）
 */
router.get('/:id',
  auth,
  anomalyDetection(),
  logAccess('view_user'),
  async (req, res) => {
    const user = await User.findById(req.params.id)
      .select(PROTECTED_FIELDS)
    
    if (!user) {
      return res.status(404).json({ error: '用户不存在' })
    }
    
    // 根据权限决定返回字段
    const isSelf = req.user.id === req.params.id
    const isAdmin = req.user.role === 'admin'
    
    let response: any = {
      id: user.id,
      name: user.name,
      avatar: user.avatar,
      createdAt: user.createdAt
    }
    
    // 自己或管理员可以看到邮箱
    if (isSelf || isAdmin) {
      response.email = user.email
      response.phone = user.phone
    } else {
      // 其他人看到脱敏邮箱
      response.email = maskEmail(user.email, 'medium')
    }
    
    res.json(response)
  }
)

/**
 * 数据导出（二次验证 + 严格限流）
 */
router.post('/export',
  auth,
  requireRole('admin'),  // 只有管理员可以导出
  sensitiveLimiter,
  async (req, res) => {
    // 1. 验证二次认证
    const { reauthToken } = req.body
    const valid = await verifyReauthToken(req.user.id, reauthToken)
    
    if (!valid) {
      return res.status(401).json({
        error: '请重新验证身份',
        requireReauth: true
      })
    }
    
    // 2. 创建导出任务
    const taskId = await createExportTask(req.user.id, {
      dataTypes: req.body.dataTypes,
      format: req.body.format || 'csv',
      sensitivity: 'high'  // 高敏感度脱敏
    })
    
    // 3. 记录操作
    await AuditLog.create({
      userId: req.user.id,
      action: 'export_users',
      details: { taskId, dataTypes: req.body.dataTypes },
      ip: req.ip,
      timestamp: new Date()
    })
    
    res.json({
      message: '导出任务已创建',
      taskId,
      statusUrl: `/api/exports/${taskId}`
    })
  }
)

export default router
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业数据泄露防护案例集](../../enterprise/infosec/data-leak-enterprise.md)
- [DLP 最佳实践](../../enterprise/infosec/dlp-best-practices.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 脱敏策略 | 固定规则 | 动态策略 + 上下文感知 |
| 监控 | 基础日志 | SIEM + UEBA 实时检测 |
| 响应 | 手动处理 | SOAR 自动化响应 |
| 合规 | 无 | GDPR/CCPA 数据主体权利 |
| DLP | 代码层面 | 专业 DLP 平台 |

---

## 附录：常见问题

**Q: 什么时候需要显示完整邮箱？**

A: 只有以下场景：
1. 用户查看自己的个人资料
2. 管理员在后台管理用户（需审计）
3. 发送邮件时（后端使用，不显示）

**Q: 用户搜索功能如何防止枚举？**

A: 策略包括：
1. 不支持邮箱搜索（只支持用户名/昵称）
2. 搜索结果限制数量（最多 20 条）
3. 搜索频率限制
4. 搜索结果不返回邮箱字段

**Q: 导出功能必须提供吗？**

A: 取决于：
1. 合规要求（GDPR 数据可携带权）
2. 业务需求
3. 如果提供，必须：
   - 二次验证
   - 频率限制
   - 完整审计日志
   - 敏感数据脱敏

**Q: 如何处理已经被爬取的情况？**

A: 应急响应：
1. 立即关闭漏洞接口
2. 分析日志，确定影响范围
3. 评估泄露数据类型和数量
4. 如涉及敏感信息，依法通知用户
5. 必要时报告监管机构

---

## 参考资源

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [GDPR Data Minimization](https://gdpr-info.eu/art-5-gdpr/)
- [Data Masking Best Practices](https://www.ibm.com/docs/en/iis/11.7?topic=masking-data-best-practices)
- [Rate Limiting Best Practices](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
