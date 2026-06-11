# API 版本控制缺陷

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
旧版本 API 存在漏洞但未下线，攻击者绕过新版本直接调用旧版本，利用已修复的漏洞。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 多个 API 版本同时运行（/v1/、/v2/）
- [ ] 旧版本 API 没有明确的下线计划
- [ ] 不同版本使用相同认证但权限不同
- [ ] 用户可以自由选择 API 版本调用
→ 勾选≥1项，即需关注此风险

### 一句话防御
建立 API 版本生命周期管理，旧版本漏洞修复后强制升级或下线，完全免费。

### 快速行动清单
1. [ ] **立即（今天）**：盘点所有正在运行的 API 版本
2. [ ] **短期（本周）**：为每个版本设置明确的废弃日期
3. [ ] **长期（规划中）**：建立版本迁移机制和用户通知流程

### 推荐工具
- **免费**：
  - [Postman](https://www.postman.com/) - API 版本管理
  - [Stoplight](https://stoplight.io/) - API 设计和文档平台
  - [Swagger/OpenAPI](https://swagger.io/) - API 规范和版本声明
- **低成本**：
  - [Kong Gateway](https://konghq.com/) - API 网关，版本路由
  - [Vercel](https://vercel.com/) - 部署平台，支持版本别名

### 验证方法
- [ ] 尝试调用 `/v1/` 版本 API，确认是否有漏洞已在新版本修复
- [ ] 检查旧版本 API 是否仍在运行
- [ ] 验证是否可以通过修改 URL 路径访问旧版本

---

## L2 小团队版（理解版）

### 场景还原
你的产品是一个支付 API 服务。去年你在 `/v2/` 版本修复了一个严重的越权访问漏洞，但 `/v1/` 版本因为"兼容性原因"一直保留。

攻击者通过分析历史文档发现了这个漏洞，直接调用：

```bash
# 新版本已修复，返回 403
curl https://api.yourapp.com/v2/users/123/balance

# 旧版本仍有漏洞，返回敏感数据
curl https://api.yourapp.com/v1/users/123/balance
```

攻击者利用旧版本 API 批量获取了数万用户的余额信息，还绕过了新版本的安全限制执行了越权操作。

### 攻击路径（简化版）
1. **信息收集**：攻击者查阅历史文档、GitHub 提交记录，发现 API 版本历史
2. **漏洞关联**：通过 Changelog 发现 v1 版本存在已知漏洞
3. **版本探测**：验证 `/v1/` 端点是否仍然可用
4. **漏洞利用**：使用旧版本 API 执行已修复的攻击
5. **持续滥用**：长期利用旧版本 API 直到被发现

### 防御实施（低成本方案）

#### 方案A：免费方案（版本生命周期管理）

**工具/服务**: 规范化版本管理

**版本策略选择**:

| 策略 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| URL 路径版本 | `/v1/users` | 简单直观 | URL 污染 |
| Header 版本 | `Accept: application/vnd.api+json;version=1` | URL 干净 | 客户端复杂 |
| 查询参数 | `/users?version=1` | 灵活 | 容易混淆 |
| 时间戳版本 | `/2024-01-01/users` | 清晰时间线 | 维护困难 |

**推荐：URL 路径版本 + 生命周期管理**

```typescript
// 版本配置
interface ApiVersion {
  version: string;
  path: string;
  status: 'active' | 'deprecated' | 'sunset';
  deprecatedAt?: Date;
  sunsetAt?: Date;
  migrationGuide?: string;
}

const API_VERSIONS: ApiVersion[] = [
  {
    version: '1.0.0',
    path: '/v1',
    status: 'sunset',
    deprecatedAt: new Date('2025-01-01'),
    sunsetAt: new Date('2026-01-01'),
    migrationGuide: '/docs/migration/v1-to-v2',
  },
  {
    version: '2.0.0',
    path: '/v2',
    status: 'active',
  },
  {
    version: '3.0.0-beta',
    path: '/v3',
    status: 'active',
  },
];
```

**Express 版本路由中间件**:

```typescript
import express, { Request, Response, NextFunction } from 'express';

const app = express();

// 版本状态中间件
const versionStatusMiddleware = (versionConfig: ApiVersion) => {
  return (req: Request, res: Response, next: NextFunction) => {
    // 设置版本信息 Header
    res.setHeader('X-API-Version', versionConfig.version);

    if (versionConfig.status === 'deprecated') {
      res.setHeader('Deprecation', 'true');
      res.setHeader('Sunset', versionConfig.sunsetAt?.toUTCString() || '');
      res.setHeader('Link', `<${versionConfig.migrationGuide}>; rel="sunset"`);
    }

    if (versionConfig.status === 'sunset') {
      // 已下线版本返回 410 Gone
      return res.status(410).json({
        error: 'API version has been sunset',
        message: `This API version was sunset on ${versionConfig.sunsetAt?.toDateString()}`,
        migrationGuide: versionConfig.migrationGuide,
        currentVersion: '/v2',
      });
    }

    next();
  };
};

// v1 版本路由（已下线）
app.use('/v1', versionStatusMiddleware(API_VERSIONS[0]));

// v2 版本路由（当前活跃）
app.use('/v2', versionStatusMiddleware(API_VERSIONS[1]), v2Routes);

// v3 版本路由（Beta）
app.use('/v3', versionStatusMiddleware(API_VERSIONS[2]), v3Routes);

// 默认路由（指向最新稳定版本）
app.use('/', (req, res, next) => {
  req.url = '/v2' + req.url;
  next('route');
});
```

#### 方案B：版本废弃流程

**工具/服务**: 版本迁移通知系统

**废弃流程时间线**:

```
Day 0:   发布新版本，标记旧版本为 deprecated
         └── 邮件通知所有 API 用户
         └── 响应 Header 添加 Deprecation: true

Day 30:  第一次提醒
         └── 邮件提醒 + Dashboard 提醒
         └── 旧版本 API 响应添加警告信息

Day 60:  第二次提醒
         └── 最后提醒邮件
         └── 旧版本 API 添加限速（降低 50%）

Day 90:  旧版本下线（Sunset）
         └── 返回 410 Gone
         └── 提供迁移文档链接
```

**版本废弃通知中间件**:

```typescript
// 废弃警告中间件
const deprecationWarningMiddleware = (config: {
  sunsetDate: Date;
  migrationGuide: string;
  newVersion: string;
}) => {
  const daysUntilSunset = Math.ceil(
    (config.sunsetDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  return (req: Request, res: Response, next: NextFunction) => {
    // 设置标准废弃 Headers
    res.setHeader('Deprecation', 'true');
    res.setHeader('Sunset', config.sunsetDate.toUTCString());
    res.setHeader(
      'Link',
      `<${config.migrationGuide}>; rel="sunset"; type="text/html"`
    );

    // 自定义警告 Header
    res.setHeader(
      'X-API-Warning',
      `This API version will be sunset in ${daysUntilSunset} days. ` +
      `Migrate to ${config.newVersion}. See ${config.migrationGuide}`
    );

    // 响应体添加警告（可选）
    const originalJson = res.json.bind(res);
    res.json = (body: any) => {
      if (body && typeof body === 'object') {
        body._warnings = body._warnings || [];
        body._warnings.push({
          type: 'deprecation',
          message: `API v1 will be sunset on ${config.sunsetDate.toDateString()}`,
          migrationGuide: config.migrationGuide,
        });
      }
      return originalJson(body);
    };

    next();
  };
};

// 应用到 v1 版本
app.use('/v1', deprecationWarningMiddleware({
  sunsetDate: new Date('2026-01-01'),
  migrationGuide: 'https://docs.yourapp.com/migration/v1-to-v2',
  newVersion: '/v2',
}), v1Routes);
```

### 决策树

```
你是否有多个 API 版本同时运行？
├── 否 → 确保新版本发布后旧版本被正确下线
└── 是
    ├── 旧版本是否有已知漏洞？
    │   ├── 是 → 立即下线或修复
    │   └── 否 → 设置废弃计划
    └── 是否有版本迁移文档？
        ├── 是 → 通知用户迁移
        └── 否 → 创建迁移文档后通知
```

### 完整代码示例

以下是一个完整的 Next.js API 版本管理示例：

```typescript
// lib/api-version.ts
export interface ApiVersionConfig {
  version: string;
  path: string;
  status: 'active' | 'deprecated' | 'sunset';
  deprecatedAt?: Date;
  sunsetAt?: Date;
  releaseNotes?: string;
  migrationGuide?: string;
}

export const API_VERSIONS: ApiVersionConfig[] = [
  {
    version: '1.0.0',
    path: '/api/v1',
    status: 'sunset',
    deprecatedAt: new Date('2025-01-01'),
    sunsetAt: new Date('2026-01-01'),
    migrationGuide: '/docs/api/migration/v1-to-v2',
  },
  {
    version: '2.0.0',
    path: '/api/v2',
    status: 'active',
    releaseNotes: '/docs/api/v2/release-notes',
  },
];

// 获取当前活跃版本
export function getActiveVersion(): ApiVersionConfig {
  return API_VERSIONS.find((v) => v.status === 'active')!;
}

// 获取版本配置
export function getVersionConfig(path: string): ApiVersionConfig | undefined {
  return API_VERSIONS.find((v) => v.path === path);
}
```

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { API_VERSIONS, getVersionConfig } from './lib/api-version';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 匹配 API 版本路径
  const versionMatch = pathname.match(/^\/api\/(v\d+)/);

  if (versionMatch) {
    const versionPath = `/api/${versionMatch[1]}`;
    const config = getVersionConfig(versionPath);

    if (!config) {
      return NextResponse.json(
        { error: 'Invalid API version' },
        { status: 404 }
      );
    }

    // 处理已下线版本
    if (config.status === 'sunset') {
      const activeVersion = API_VERSIONS.find((v) => v.status === 'active');
      return NextResponse.json(
        {
          error: 'API version has been sunset',
          sunsetAt: config.sunsetAt,
          migrationGuide: config.migrationGuide,
          currentVersion: activeVersion?.path,
        },
        { status: 410 }
      );
    }

    // 处理已废弃版本
    if (config.status === 'deprecated') {
      const response = NextResponse.next();

      // 设置废弃 Headers
      response.headers.set('Deprecation', 'true');
      if (config.sunsetAt) {
        response.headers.set('Sunset', config.sunsetAt.toUTCString());
      }
      if (config.migrationGuide) {
        response.headers.set(
          'Link',
          `<${config.migrationGuide}>; rel="sunset"`
        );
      }

      // 计算剩余天数
      const daysUntilSunset = config.sunsetAt
        ? Math.ceil(
            (config.sunsetAt.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
          )
        : 0;

      response.headers.set(
        'X-API-Warning',
        `This API version is deprecated and will be sunset in ${daysUntilSunset} days. ` +
          `Please migrate to the latest version.`
      );

      return response;
    }

    // 活跃版本，添加版本号 Header
    const response = NextResponse.next();
    response.headers.set('X-API-Version', config.version);
    return response;
  }

  // 默认路由到最新版本
  if (pathname.startsWith('/api/') && !versionMatch) {
    const activeVersion = API_VERSIONS.find((v) => v.status === 'active');
    if (activeVersion) {
      const url = request.nextUrl.clone();
      url.pathname = pathname.replace('/api/', `${activeVersion.path}/`);
      return NextResponse.redirect(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/api/:path*',
};
```

```typescript
// app/api/v2/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

// GET /api/v2/users - v2 版本用户列表（安全）
export async function GET(request: NextRequest) {
  // v2 版本有完善的认证和权限检查
  const authHeader = request.headers.get('authorization');

  if (!authHeader) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  // 返回用户列表（已修复越权漏洞）
  const users = [
    { id: 1, name: 'User 1', email: 'user1@example.com' },
    { id: 2, name: 'User 2', email: 'user2@example.com' },
  ];

  return NextResponse.json({
    data: users,
    meta: {
      version: '2.0.0',
      timestamp: new Date().toISOString(),
    },
  });
}
```

```typescript
// app/api/v1/users/route.ts - v1 版本（已下线，此文件可删除或仅作存档）
// 此版本已被标记为 sunset，请求会在 middleware 中被拦截返回 410 Gone
// 历史代码仅供参考：

/*
// ❌ v1 版本存在越权漏洞
export async function GET(request: NextRequest) {
  // 没有认证检查！
  const users = await db.user.findMany();
  return NextResponse.json({ data: users });
}
*/
```

### 版本迁移文档模板

```markdown
# API v1 到 v2 迁移指南

## 重要时间节点
- **2025-01-01**: v1 标记为 deprecated
- **2026-01-01**: v1 正式下线

## 主要变更

### 认证方式变更
- v1: 无认证
- v2: 需要 Bearer Token 认证

```diff
- GET /api/v1/users
+ GET /api/v2/users
+ Authorization: Bearer <your_token>
```

### 响应格式变更
- v1: 直接返回数组
- v2: 包装在 `data` 字段中

```diff
- [ { "id": 1, "name": "User" } ]
+ { "data": [ { "id": 1, "name": "User" } ], "meta": { "version": "2.0.0" } }
```

### 端点变更
| v1 端点 | v2 端点 | 变更说明 |
|---------|---------|----------|
| GET /users | GET /users | 添加认证 |
| GET /users/:id | GET /users/:id | 添加权限检查 |
| POST /users | POST /users | 添加验证 |

## 迁移步骤
1. 获取 API Token
2. 更新所有 API 调用路径
3. 添加 Authorization Header
4. 测试验证
```

---

## L3 企业版（深耕版）

本案例的企业级扩展内容，请参考企业版案例库：

- **详细攻击技术**：参见 [enterprise/infosec/api/versioning-flaw.md](../../../enterprise/infosec/api/versioning-flaw.md)
- **企业防御架构**：API Gateway 版本控制、服务网格版本路由
- **合规要求**：OWASP API Security Top 10 #API8:2019、SOC 2 变更管理
- **监控告警**：旧版本调用监控、版本分布分析、迁移进度跟踪
- **渗透测试**：版本漏洞关联分析、历史漏洞回归测试

企业版核心补充：
1. **版本指纹识别**：自动识别所有 API 版本和漏洞关联
2. **灰度发布安全**：金丝雀部署中的安全风险
3. **BFF 版本管理**：Backend For Frontend 版本策略
4. **应急响应**：紧急版本回滚、漏洞热修复
