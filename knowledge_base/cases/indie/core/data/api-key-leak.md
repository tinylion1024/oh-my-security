# API Key 泄露风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $10-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的内部 API Key（如 OpenAI、AWS、Stripe）被意外提交到前端代码或 GitHub，攻击者获取后恶意消费你的配额，甚至窃取你的用户数据。

### 一分钟识别
你的项目是否有以下特征：
- [ ] 使用第三方 API（OpenAI、AWS、Stripe、SendGrid 等）
- [ ] API Key 存储在 `.env` 或配置文件中
- [ ] **前端代码中直接调用这些 API**
- [ ] **曾经提交过 `.env` 文件到 Git**
- [ ] GitHub 仓库是公开的
- [ ] 没有设置 API Key 的使用配额限制
→ 勾选≥2项，尤其是中间两项，**立即行动**

### 一句话防御
所有敏感 API Key 必须存储在后端环境变量中，通过后端代理转发请求，并立即轮换所有疑似泄露的密钥。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查代码仓库**：
   ```bash
   # 搜索代码中的 API Key
   git grep -i "api_key\|apikey\|secret\|token" -- '*.js' '*.ts' '*.jsx' '*.tsx' '*.env*'
   
   # 检查 GitHub 历史（即使是私有仓库也要检查）
   git log --all --full-history -- "*.env*" ".env"
   ```

2. [ ] **检查前端代码**：
   ```bash
   # 搜索前端代码中的硬编码 Key
   grep -r "sk-\|pk-\|AIza\|AKIA\|SG\." public/ src/
   
   # 常见 API Key 前缀
   # OpenAI: sk-
   # Stripe: sk_live_, pk_live_
   # AWS: AKIA
   # SendGrid: SG.
   # Google: AIza
   # Firebase: AAAA
   ```

3. [ ] **立即轮换泄露的密钥**：
   - OpenAI: https://platform.openai.com/api-keys → Revoke → Create new
   - AWS: IAM → Users → Security credentials → Create access key
   - Stripe: Dashboard → Developers → API keys → Roll key
   - SendGrid: Settings → API Keys → Delete & Recreate

4. [ ] **从 Git 历史中删除**（如果已提交）：
   ```bash
   # 使用 BFG Repo-Cleaner（推荐）
   # 1. 下载 https://rtyley.github.io/bfg-repo-cleaner/
   
   # 2. 创建密码文件 secrets.txt，每行一个要删除的模式
   echo "sk-xxxxx" >> secrets.txt
   echo "AKIAxxxxx" >> secrets.txt
   
   # 3. 清理历史
   java -jar bfg.jar --replace-text secrets.txt
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # 4. 强制推送
   git push --force
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **配置环境变量管理**：
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   
   # 添加到 .gitignore
   echo ".env" >> .gitignore
   echo ".env.local" >> .gitignore
   echo ".env.*.local" >> .gitignore
   
   # 验证 .gitignore 生效
   git check-ignore .env
   ```

2. [ ] **创建后端 API 代理**：
   ```javascript
   // 后端代理示例（Node.js）
   // routes/api-proxy.ts
   
   import { Router } from 'express'
   import fetch from 'node-fetch'
   
   const router = Router()
   
   // OpenAI API 代理
   router.post('/openai/chat', async (req, res) => {
     const response = await fetch('https://api.openai.com/v1/chat/completions', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
       },
       body: JSON.stringify(req.body)
     })
     
     const data = await response.json()
     res.json(data)
   })
   
   export default router
   ```

3. [ ] **设置配额和监控**：
   - OpenAI: Usage limits → Set monthly budget
   - AWS: Budgets → Create budget alert
   - Stripe: Dashboard → Developers → Webhooks → Add webhook for usage events

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用密钥管理服务**：AWS Secrets Manager、HashiCorp Vault
2. [ ] **实施密钥轮换策略**：定期（如每 90 天）轮换
3. [ ] **启用密钥扫描工具**：GitGuardian、TruffleHog

### API Key 管理方案

**环境变量管理（推荐）**：

```bash
# .env.example（提交到 Git）
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_ORG_ID=org-xxxx

# AWS
AWS_ACCESS_KEY_ID=AKIAxxxxx
AWS_SECRET_ACCESS_KEY=xxxxx
AWS_REGION=us-east-1

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# SendGrid
SENDGRID_API_KEY=SG.xxxxx

# Database
DATABASE_URL=postgresql://user:password@host:5432/db

# JWT
JWT_SECRET=your-jwt-secret-at-least-32-chars
```

```javascript
// config/env.ts
import dotenv from 'dotenv'
import path from 'path'

// 加载环境变量
dotenv.config({ path: path.resolve(__dirname, '../.env') })

// 验证必需的环境变量
const requiredEnvVars = [
  'OPENAI_API_KEY',
  'DATABASE_URL',
  'JWT_SECRET'
]

const missing = requiredEnvVars.filter(key => !process.env[key])

if (missing.length > 0) {
  throw new Error(`缺少必需的环境变量: ${missing.join(', ')}`)
}

// 导出配置
export const config = {
  openai: {
    apiKey: process.env.OPENAI_API_KEY!,
    orgId: process.env.OPENAI_ORG_ID
  },
  database: {
    url: process.env.DATABASE_URL!
  },
  jwt: {
    secret: process.env.JWT_SECRET!
  },
  stripe: {
    secretKey: process.env.STRIPE_SECRET_KEY!,
    publishableKey: process.env.STRIPE_PUBLISHABLE_KEY!,
    webhookSecret: process.env.STRIPE_WEBHOOK_SECRET!
  }
}

export default config
```

**前端安全调用模式**：

```typescript
// ❌ 错误：前端直接调用
const response = await fetch('https://api.openai.com/v1/chat/completions', {
  headers: {
    'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`  // 危险！
  }
})

// ✅ 正确：前端调用后端代理
const response = await fetch('/api/openai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`  // 用户认证 token
  },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Hello' }]
  })
})
```

### 密钥轮换流程

**标准轮换流程**：

```
1. 准备阶段
   ├── 创建新密钥
   ├── 在密钥管理系统中记录
   └── 设置双重运行期（新旧密钥同时有效）
   
2. 切换阶段
   ├── 更新应用配置（使用新密钥）
   ├── 部署到生产环境
   ├── 监控错误日志（确保新密钥工作正常）
   └── 保留旧密钥 24-48 小时（回滚用）
   
3. 清理阶段
   ├── 确认新密钥稳定运行
   ├── 撤销旧密钥
   └── 更新文档和密码管理器
   
4. 审计阶段
   ├── 记录轮换时间和原因
   ├── 检查旧密钥使用日志（是否有异常）
   └── 更新密钥清单
```

**轮换脚本示例**：

```bash
#!/bin/bash
# rotate-api-keys.sh
# 用途：自动化密钥轮换流程

set -e

KEY_TYPE="${1:-openai}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== 密钥轮换开始 ==="
echo "类型: $KEY_TYPE"
echo "时间: $TIMESTAMP"

case $KEY_TYPE in
  openai)
    echo "轮换 OpenAI API Key..."
    
    # 1. 备份当前配置
    cp .env ".env.backup.$TIMESTAMP"
    
    # 2. 提示创建新密钥
    echo "请在 OpenAI 平台创建新 API Key:"
    echo "https://platform.openai.com/api-keys"
    read -p "输入新的 API Key: " NEW_KEY
    
    # 3. 更新 .env
    sed -i "s/^OPENAI_API_KEY=.*/OPENAI_API_KEY=$NEW_KEY/" .env
    
    # 4. 重启服务
    echo "重启应用..."
    # pm2 restart app
    
    echo "✓ OpenAI API Key 已更新"
    echo "⚠️  请在 48 小时后撤销旧密钥"
    ;;
    
  aws)
    echo "轮换 AWS Access Key..."
    
    # AWS CLI 自动创建新密钥
    NEW_KEYS=$(aws iam create-access-key --output json)
    NEW_ACCESS_KEY=$(echo $NEW_KEYS | jq -r '.AccessKey.AccessKeyId')
    NEW_SECRET_KEY=$(echo $NEW_KEYS | jq -r '.AccessKey.SecretAccessKey')
    
    # 更新配置
    sed -i "s/^AWS_ACCESS_KEY_ID=.*/AWS_ACCESS_KEY_ID=$NEW_ACCESS_KEY/" .env
    sed -i "s/^AWS_SECRET_ACCESS_KEY=.*/AWS_SECRET_ACCESS_KEY=$NEW_SECRET_KEY/" .env
    
    echo "✓ AWS Access Key 已更新"
    echo "新 Access Key ID: $NEW_ACCESS_KEY"
    echo "⚠️  请保存 Secret Access Key: $NEW_SECRET_KEY"
    echo "⚠️  请在 48 小时后删除旧密钥"
    ;;
    
  stripe)
    echo "Stripe API Key 需要在 Dashboard 手动轮换:"
    echo "https://dashboard.stripe.com/test/apikeys"
    ;;
    
  *)
    echo "不支持的密钥类型: $KEY_TYPE"
    echo "支持: openai, aws, stripe"
    exit 1
    ;;
esac

echo "=== 轮换完成 ==="
echo "备份文件: .env.backup.$TIMESTAMP"
```

### 推荐工具
- **免费**：
  - [GitGuardian Free](https://www.gitguardian.com/) - 公开仓库扫描
  - [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Git 历史扫描
  - [gitleaks](https://github.com/gitleaks/gitleaks) - CI/CD 集成扫描

- **低成本**：
  - [GitGuardian Pro](https://www.gitguardian.com/pricing) - $399/年起，私有仓库
  - [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) - $0.40/密钥/月
  - [Doppler](https://www.doppler.com/) - $7/月起，密钥管理

### 验证方法
- [ ] **代码扫描**：`gitleaks detect --source .` 无泄露
- [ ] **GitHub 检查**：搜索仓库历史，无敏感文件
- [ ] **前端检查**：浏览器开发者工具 → Sources → 搜索 `sk-` 等
- [ ] **环境验证**：`.env` 在 `.gitignore` 中

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2023年，一位独立开发者将 OpenAI API Key 硬编码在前端 JavaScript 文件中。攻击者通过查看网页源码获取了 Key，在 24 小时内消费了 $5000+ 的 API 配额。

**后果**：
- OpenAI 账单 $5000+
- API 配额耗尽，服务中断
- 需要申请新的 API Key
- 代码需要重构

**类似案例**：
- 2022年，某 SaaS 产品 AWS Key 泄露，被用于挖矿，账单 $10000+
- 2021年，某应用 Stripe Key 泄露，攻击者恶意创建订单
- 2020年，GitHub 扫描发现 600 万+ 泄露的密钥

### 攻击路径（简化版）

```
1. 发现泄露源
   ├── GitHub 公开仓库搜索
   │   git clone https://github.com/user/repo
   │   grep -r "sk-\|AKIA\|SG\." .
   │
   ├── 前端代码检查
   │   浏览器 → F12 → Sources → 搜索 "api_key"
   │
   ├── NPM 包供应链
   │   发布包含密钥的 npm 包
   │   攻击者下载包，扫描源码
   │
   └── Docker Hub
       公开镜像中包含密钥
   
2. 验证密钥有效性
   ├── curl https://api.openai.com/v1/models \
   │     -H "Authorization: Bearer sk-xxxxx"
   ├── 返回 200 = 有效
   └── 返回 401 = 已失效
   
3. 评估价值
   ├── OpenAI: API 配额可用于生成内容
   ├── AWS: 计算资源（挖矿、DDoS）
   ├── Stripe: 支付欺诈
   └── SendGrid: 发送垃圾邮件
   
4. 恶意利用
   ├── 方式A: 消费配额（OpenAI）
   ├── 方式B: 挖矿（AWS）
   ├── 方式C: 发送垃圾邮件（SendGrid）
   └── 方式D: 出售密钥（暗网 $10-100/个）
   
5. 持续监控
   ├── 自动化脚本监控密钥状态
   ├── 密钥失效后寻找新泄露
   └── 批量收集和分类
```

**关键数据**：
- GitHub 每天新增 6000+ 泄露密钥
- 平均发现到利用时间：< 1 小时
- 暗网密钥售价：$10-100/个
- 平均单次泄露损失：$500-10000

### 防御实施（低成本方案）

#### 方案A：免费方案（流程 + 工具）

**第一步：Git Hook 防护**

```bash
# .git/hooks/pre-commit
#!/bin/bash

# 检查是否包含敏感信息
if git diff --cached --name-only | xargs grep -l "sk-\|AKIA\|SG\."; then
  echo "❌ 检测到可能的 API Key！"
  echo "请确保不要提交敏感信息。"
  exit 1
fi
```

**使用 gitleaks（推荐）**：

```bash
# 安装
brew install gitleaks  # macOS
# 或
sudo apt install gitleaks  # Ubuntu

# 配置 .gitleaks.toml
title = "Gitleaks Configuration"

[[rules]]
id = "openai-api-key"
description = "OpenAI API Key"
regex = '''sk-[a-zA-Z0-9]{20}T3BlbkFJ[a-zA-Z0-9]{20}'''
tags = ["key", "openai"]

[[rules]]
id = "aws-access-key"
description = "AWS Access Key"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["key", "aws"]

[[rules]]
id = "generic-api-key"
description = "Generic API Key"
regex = '''(?i)(api_key|apikey|api_secret|secret_key)\s*[:=]\s*['"]?[a-zA-Z0-9_-]{20,}['"]?'''
tags = ["key", "generic"]

# 扫描
gitleaks detect --source . --config .gitleaks.toml

# CI/CD 集成（GitHub Actions）
# .github/workflows/gitleaks.yml
name: Gitleaks
on: [push, pull_request]
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

**第二步：环境变量管理**

```typescript
// config/secrets.ts
import { config } from 'dotenv'
import { expand } from 'dotenv-expand'
import { z } from 'zod'

// 加载环境变量
config()
expand(config())

// 环境变量 Schema
const EnvSchema = z.object({
  // API Keys
  OPENAI_API_KEY: z.string().startsWith('sk-'),
  STRIPE_SECRET_KEY: z.string().startsWith('sk_'),
  STRIPE_PUBLISHABLE_KEY: z.string().startsWith('pk_'),
  AWS_ACCESS_KEY_ID: z.string().startsWith('AKIA'),
  AWS_SECRET_ACCESS_KEY: z.string().min(40),
  
  // Database
  DATABASE_URL: z.string().url(),
  
  // Security
  JWT_SECRET: z.string().min(32),
  
  // Optional
  OPENAI_ORG_ID: z.string().optional(),
  SENTRY_DSN: z.string().url().optional()
})

// 验证并导出
export const env = EnvSchema.parse(process.env)

// 类型安全的访问
export type Env = z.infer<typeof EnvSchema>
```

**第三步：API 代理层**

```typescript
// routes/api-proxy.ts
import { Router, Request, Response } from 'express'
import { z } from 'zod'
import rateLimit from 'express-rate-limit'
import { env } from '@/config/secrets'

const router = Router()

// OpenAI API 代理配置
const openaiProxy = {
  baseUrl: 'https://api.openai.com/v1',
  timeout: 30000,
  maxTokens: 4096
}

// 频率限制
const openaiLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 分钟
  max: 20,  // 每分钟最多 20 次
  message: { error: '请求过于频繁' }
})

// 请求验证 Schema
const ChatCompletionSchema = z.object({
  model: z.enum(['gpt-3.5-turbo', 'gpt-4', 'gpt-4-turbo']),
  messages: z.array(z.object({
    role: z.enum(['system', 'user', 'assistant']),
    content: z.string().max(4000)
  })),
  temperature: z.number().min(0).max(2).optional(),
  max_tokens: z.number().max(openaiProxy.maxTokens).optional()
})

/**
 * OpenAI Chat Completions 代理
 */
router.post('/openai/chat',
  openaiLimiter,
  async (req: Request, res: Response) => {
    try {
      // 验证请求
      const body = ChatCompletionSchema.parse(req.body)
      
      // 限制 token 数量
      const requestBody = {
        ...body,
        max_tokens: Math.min(body.max_tokens || 1000, openaiProxy.maxTokens)
      }
      
      // 调用 OpenAI API
      const response = await fetch(`${openaiProxy.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
          ...(env.OPENAI_ORG_ID && { 'OpenAI-Organization': env.OPENAI_ORG_ID })
        },
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(openaiProxy.timeout)
      })
      
      if (!response.ok) {
        const error = await response.json()
        return res.status(response.status).json(error)
      }
      
      const data = await response.json()
      
      // 记录使用量（可用于计费）
      await logUsage(req.user!.id, {
        model: body.model,
        tokens: data.usage?.total_tokens || 0,
        cost: calculateCost(body.model, data.usage)
      })
      
      res.json(data)
      
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ error: '请求参数无效', details: error.errors })
      }
      
      console.error('OpenAI API Error:', error)
      res.status(500).json({ error: 'API 调用失败' })
    }
  }
)

/**
 * AWS S3 签名 URL 代理
 */
router.get('/aws/presigned-url',
  async (req: Request, res: Response) => {
    const { key, type } = req.query
    
    if (!key || !type) {
      return res.status(400).json({ error: '缺少参数' })
    }
    
    // 生成预签名 URL
    const url = await generatePresignedUrl(key as string, type as string)
    
    res.json({ url })
  }
)

export default router
```

#### 方案B：低成本方案（专业工具）

**Doppler 密钥管理**：

```bash
# 安装 Doppler CLI
brew install dopplerhq/cli/doppler

# 登录
doppler login

# 创建项目
doppler setup

# 配置密钥
doppler secrets set OPENAI_API_KEY sk-xxxxx
doppler secrets set STRIPE_SECRET_KEY sk_live_xxxxx

# 本地开发时运行
doppler run -- npm run dev

# CI/CD 中使用
doppler run --secrets-file .doppler/secrets.json -- ./deploy.sh
```

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (Doppler) |
|------|------------|-----------------|
| 月成本 | $0 | $7+ |
| 配置时间 | 4-8 小时 | 1 小时 |
| 维护时间 | 2 小时/月 | 0 |
| 安全等级 | 依赖配置 | 企业级 |
| 团队协作 | 手动同步 | 自动同步 |
| 审计日志 | 需自建 | 内置 |

### 决策树

```
你的团队规模？
├── 1 人
│   └── 方案A (DIY) 足够
│
├── 2-5 人
│   ├── 预算有限 → 方案A
│   └── 预算充足 → 方案B ($7-21/月)
│
└── 5+ 人
    └── 方案B ($21-49/月)
```

### 代码示例

#### 完整的密钥管理方案

```typescript
// lib/secrets-manager.ts
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm'
import { KV } from 'cloudflare-workers-kv'

interface SecretConfig {
  key: string
  version?: string
  cacheTTL?: number  // 秒
}

class SecretsManager {
  private cache: Map<string, { value: string; expires: number }> = new Map()
  private ssmClient?: SSMClient
  private kv?: KV

  constructor() {
    // 根据环境选择密钥存储
    if (process.env.AWS_REGION) {
      this.ssmClient = new SSMClient({ region: process.env.AWS_REGION })
    }
  }

  /**
   * 获取密钥
   */
  async get(config: SecretConfig): Promise<string> {
    const cacheKey = `${config.key}:${config.version || 'latest'}`
    
    // 检查缓存
    const cached = this.cache.get(cacheKey)
    if (cached && cached.expires > Date.now()) {
      return cached.value
    }

    // 从存储中获取
    let value: string

    if (this.ssmClient) {
      value = await this.getFromSSM(config)
    } else {
      value = await this.getFromEnv(config)
    }

    // 更新缓存
    this.cache.set(cacheKey, {
      value,
      expires: Date.now() + (config.cacheTTL || 300) * 1000
    })

    return value
  }

  /**
   * 从 AWS SSM 获取
   */
  private async getFromSSM(config: SecretConfig): Promise<string> {
    if (!this.ssmClient) {
      throw new Error('AWS SSM client not initialized')
    }

    const command = new GetParameterCommand({
      Name: config.key,
      WithDecryption: true
    })

    const response = await this.ssmClient.send(command)
    
    if (!response.Parameter?.Value) {
      throw new Error(`Secret not found: ${config.key}`)
    }

    return response.Parameter.Value
  }

  /**
   * 从环境变量获取
   */
  private async getFromEnv(config: SecretConfig): Promise<string> {
    const value = process.env[config.key]
    
    if (!value) {
      throw new Error(`Environment variable not found: ${config.key}`)
    }

    return value
  }

  /**
   * 批量获取
   */
  async getMany(configs: SecretConfig[]): Promise<Record<string, string>> {
    const results: Record<string, string> = {}

    await Promise.all(
      configs.map(async (config) => {
        results[config.key] = await this.get(config)
      })
    )

    return results
  }

  /**
   * 清除缓存
   */
  clearCache(key?: string) {
    if (key) {
      for (const cacheKey of this.cache.keys()) {
        if (cacheKey.startsWith(key)) {
          this.cache.delete(cacheKey)
        }
      }
    } else {
      this.cache.clear()
    }
  }
}

// 单例
export const secretsManager = new SecretsManager()

// 使用示例
async function example() {
  const openaiKey = await secretsManager.get({
    key: 'OPENAI_API_KEY',
    cacheTTL: 600  // 缓存 10 分钟
  })

  const allSecrets = await secretsManager.getMany([
    { key: 'OPENAI_API_KEY' },
    { key: 'STRIPE_SECRET_KEY' },
    { key: 'DATABASE_URL' }
  ])
}
```

#### GitHub Actions 密钥管理

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      # 使用 GitHub Secrets
      - name: Create .env file
        run: |
          echo "OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}" >> .env
          echo "STRIPE_SECRET_KEY=${{ secrets.STRIPE_SECRET_KEY }}" >> .env
          echo "DATABASE_URL=${{ secrets.DATABASE_URL }}" >> .env
      
      # 或使用 Doppler
      - name: Install Doppler
        uses: dopplerhq/cli-action@v1
      
      - name: Deploy with Doppler
        run: doppler run -- firebase deploy
        env:
          DOPPLER_TOKEN: ${{ secrets.DOPPLER_TOKEN }}
      
      # 安全扫描
      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业密钥管理案例集](../../enterprise/infosec/secrets-management-enterprise.md)
- [HashiCorp Vault 最佳实践](../../enterprise/infosec/vault-best-practices.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 密钥存储 | 环境变量 | HashiCorp Vault / AWS Secrets Manager |
| 轮换策略 | 手动 | 自动轮换（30-90 天） |
| 访问控制 | 无 | RBAC + 审计 |
| 监控 | 无 | 实时监控 + 异常检测 |
| 合规 | 无 | SOC2 / PCI-DSS |

---

## 附录：常见问题

**Q: 哪些 Key 可以暴露在前端？**

A: 只有设计为公开的 Key：
- Stripe Publishable Key（`pk_live_`）- 用于前端支付
- Firebase API Key - 设计为公开
- Google Maps API Key - 可设置域名限制
- reCAPTCHA Site Key - 设计为公开

**重要**：即使是公开 Key，也要设置使用限制（域名、配额）。

**Q: Git 历史中已有密钥，怎么彻底删除？**

A:
```bash
# 方法1：BFG Repo-Cleaner（推荐）
java -jar bfg.jar --replace-text passwords.txt
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force

# 方法2：git filter-repo
pip install git-filter-repo
git filter-repo --replace-text passwords.txt
git push --force --all

# 注意：强制推送后，所有协作者需要重新克隆仓库
```

**Q: 如何检测密钥是否已被泄露？**

A:
1. GitGuardian 扫描公开仓库
2. 在服务商控制台检查使用量异常
3. 启用账单告警（AWS Budgets、OpenAI Usage Limits）
4. 检查 API 访问日志

**Q: 泄露后应该做什么？**

A:
1. **立即轮换密钥**（最优先）
2. 检查使用量和账单
3. 从 Git 历史删除
4. 分析泄露原因，修复流程
5. 通知相关方（如涉及用户数据）

---

## 参考资源

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Secrets Security Best Practices](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [GitGuardian State of Secrets Sprawl Report](https://www.gitguardian.com/state-of-secrets-sprawl-report-2023)
- [TruffleHog Documentation](https://github.com/trufflesecurity/trufflehog)
