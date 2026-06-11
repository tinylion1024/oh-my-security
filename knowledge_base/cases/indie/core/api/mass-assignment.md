# 批量赋值漏洞

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
API 接受用户修改任意字段，攻击者可修改角色、权限、余额等敏感字段，实现权限提升。

### 一分钟识别
你的产品是否有以下特征：
- [ ] API 直接使用 `Object.assign()` 或 `{...user, ...req.body}` 更新数据
- [ ] ORM 的 `update()` 方法直接接受用户提交的完整对象
- [ ] 数据库字段包含 `role`、`isAdmin`、`balance`、`verified` 等敏感字段
- [ ] 没有定义允许用户修改的字段白名单
→ 勾选≥1项，即需关注此风险

### 一句话防御
定义字段白名单，只允许用户修改特定字段，完全免费，代码改动小。

### 快速行动清单
1. [ ] **立即（今天）**：审查所有更新 API，标记是否有批量赋值风险
2. [ ] **短期（本周）**：为每个更新操作创建字段白名单或 DTO
3. [ ] **长期（规划中）**：使用验证库（如 Zod、Joi）定义输入 Schema

### 推荐工具
- **免费**：
  - [Zod](https://zod.dev/) - TypeScript 优先的 Schema 验证
  - [Joi](https://joi.dev/) - JavaScript 对象验证
  - [class-validator](https://github.com/typestack/class-validator) - TypeScript 装饰器验证
- **低成本**：
  - [tRPC](https://trpc.io/) - 端到端类型安全，内置验证
  - [NestJS](https://nestjs.com/) - 内置 DTO 和验证管道

### 验证方法
- [ ] 在更新请求中添加 `role: "admin"` 字段，应返回 400 或被忽略
- [ ] 在更新请求中添加 `balance: 1000000` 字段，余额应不变
- [ ] 使用 API 测试工具尝试修改敏感字段，确认被拒绝

---

## L2 小团队版（理解版）

### 场景还原
你的产品是一个 SaaS 平台，用户可以更新自己的个人信息。API 实现如下：

```javascript
// ❌ 危险的实现
app.put('/api/users/:id', async (req, res) => {
  const user = await User.findByIdAndUpdate(
    req.params.id,
    { $set: req.body }, // 直接使用用户提交的所有字段
    { new: true }
  );
  res.json(user);
});
```

攻击者发现这个漏洞后，在更新个人信息的请求中添加：

```json
{
  "name": "Attacker",
  "email": "attacker@evil.com",
  "role": "admin",
  "subscription": "enterprise",
  "balance": 999999
}
```

服务器直接接受并更新了所有字段，攻击者成功将自己提升为管理员，获得企业订阅，还篡改了余额。

### 攻击路径（简化版）
1. **发现目标**：攻击者查看 API 文档或代理抓包，发现更新用户信息的接口
2. **探测漏洞**：在请求中添加 `role: "admin"` 字段，观察是否生效
3. **权限提升**：成功将普通用户权限提升为管理员
4. **资源窃取**：修改订阅类型、余额等字段，获取免费资源
5. **持久化**：创建后门账号，长期潜伏

### 防御实施（低成本方案）

#### 方案A：免费方案（字段白名单）

**工具/服务**: 白名单过滤

**配置步骤**:

```javascript
// ❌ 危险：直接使用用户输入
const updateUser = async (userId, updates) => {
  return await User.findByIdAndUpdate(userId, { $set: updates }, { new: true });
};

// ✅ 安全：字段白名单
const updateUserSafe = async (userId, updates) => {
  // 定义允许用户修改的字段
  const ALLOWED_FIELDS = ['name', 'email', 'avatar', 'bio'];

  const safeUpdates = {};
  for (const field of ALLOWED_FIELDS) {
    if (updates[field] !== undefined) {
      safeUpdates[field] = updates[field];
    }
  }

  return await User.findByIdAndUpdate(userId, { $set: safeUpdates }, { new: true });
};

// ✅ 更好的方式：使用 Object.pick 工具函数
const pick = (obj, keys) => {
  return keys.reduce((acc, key) => {
    if (obj[key] !== undefined) {
      acc[key] = obj[key];
    }
    return acc;
  }, {});
};

const updateUserWithPick = async (userId, updates) => {
  const ALLOWED_FIELDS = ['name', 'email', 'avatar', 'bio'];
  const safeUpdates = pick(updates, ALLOWED_FIELDS);
  return await User.findByIdAndUpdate(userId, { $set: safeUpdates }, { new: true });
};
```

**Prisma 示例**:

```typescript
// ❌ 危险：直接使用用户输入
async function updateUser(userId: string, data: any) {
  return await prisma.user.update({
    where: { id: userId },
    data, // 直接接受用户数据
  });
}

// ✅ 安全：字段白名单
async function updateUserSafe(userId: string, data: unknown) {
  // 定义允许的字段
  const ALLOWED_FIELDS = ['name', 'email', 'avatar', 'bio'] as const;

  // 类型安全的输入
  type UpdateInput = Pick<User, typeof ALLOWED_FIELDS[number]>;

  // 过滤字段
  const safeData: Partial<UpdateInput> = {};
  for (const field of ALLOWED_FIELDS) {
    if (data[field] !== undefined) {
      safeData[field] = data[field];
    }
  }

  return await prisma.user.update({
    where: { id: userId },
    data: safeData,
  });
}
```

#### 方案B：免费方案（DTO 模式）

**工具/服务**: Data Transfer Object + Zod 验证

**配置步骤**:

```typescript
// 使用 Zod 定义输入 Schema
import { z } from 'zod';

// 定义用户更新 DTO
const UpdateUserDto = z.object({
  name: z.string().min(1).max(100).optional(),
  email: z.string().email().optional(),
  avatar: z.string().url().optional(),
  bio: z.string().max(500).optional(),
});

// 类型推导
type UpdateUserInput = z.infer<typeof UpdateUserDto>;

// Express 路由
app.put('/api/users/:id', async (req, res) => {
  try {
    // 1. 验证并过滤输入
    const safeData = UpdateUserDto.parse(req.body);

    // 2. 执行更新（只有 Zod Schema 中定义的字段会被接受）
    const user = await User.findByIdAndUpdate(
      req.params.id,
      { $set: safeData },
      { new: true }
    );

    res.json(user);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({
        error: 'Validation failed',
        details: error.errors,
      });
    }
    res.status(500).json({ error: 'Internal server error' });
  }
});
```

**class-validator 示例（NestJS 风格）**:

```typescript
import { IsString, IsEmail, IsOptional, MaxLength, IsUrl } from 'class-validator';

// 定义 DTO 类
export class UpdateUserDto {
  @IsOptional()
  @IsString()
  @MaxLength(100)
  name?: string;

  @IsOptional()
  @IsEmail()
  email?: string;

  @IsOptional()
  @IsUrl()
  avatar?: string;

  @IsOptional()
  @IsString()
  @MaxLength(500)
  bio?: string;

  // 注意：没有 role、balance、subscription 等敏感字段
}

// Express 使用
import { validate } from 'class-validator';
import { plainToClass } from 'class-transformer';

app.put('/api/users/:id', async (req, res) => {
  // 将普通对象转换为 DTO 类实例
  const dto = plainToClass(UpdateUserDto, req.body);

  // 验证
  const errors = await validate(dto);
  if (errors.length > 0) {
    return res.status(400).json({
      error: 'Validation failed',
      details: errors.map(e => ({
        property: e.property,
        constraints: e.constraints,
      })),
    });
  }

  // 安全更新
  const user = await User.findByIdAndUpdate(
    req.params.id,
    { $set: dto },
    { new: true }
  );

  res.json(user);
});
```

### 决策树

```
你的更新 API 是否直接使用用户输入？
├── 是 → 立即添加字段白名单或 DTO
└── 否
    ├── 是否有敏感字段（role、balance、admin）？
    │   ├── 是 → 确保这些字段不在白名单中
    │   └── 否 → 检查其他潜在风险
    └── 是否使用了 ORM？
        ├── 是 → 检查 ORM 是否有批量赋值保护
        └── 否 → 确保手动过滤正确
```

### 完整代码示例

以下是一个完整的 Next.js API Route 示例，使用 Zod 实现安全的批量赋值防护：

```typescript
// lib/validations/user.ts
import { z } from 'zod';

// 用户更新 DTO
export const UpdateUserSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100).optional(),
  email: z.string().email('Invalid email format').optional(),
  avatar: z.string().url('Invalid avatar URL').optional(),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
  // 只允许这些字段，其他字段将被忽略
});

export type UpdateUserInput = z.infer<typeof UpdateUserSchema>;

// 密码更新 DTO（单独的接口）
export const UpdatePasswordSchema = z.object({
  currentPassword: z.string().min(8, 'Current password is required'),
  newPassword: z.string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
});

export type UpdatePasswordInput = z.infer<typeof UpdatePasswordSchema>;
```

```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { UpdateUserSchema } from '@/lib/validations/user';

// GET /api/users/[id] - 获取用户信息
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const user = await prisma.user.findUnique({
    where: { id: params.id },
    select: {
      id: true,
      name: true,
      email: true,
      avatar: true,
      bio: true,
      createdAt: true,
      // 不返回 password、role 等敏感字段
    },
  });

  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  return NextResponse.json({ data: user });
}

// PUT /api/users/[id] - 更新用户信息
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    // 1. 解析和验证输入
    const body = await request.json();
    const safeData = UpdateUserSchema.parse(body);

    // 2. 检查用户是否存在
    const existingUser = await prisma.user.findUnique({
      where: { id: params.id },
    });

    if (!existingUser) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // 3. 执行更新（只有白名单字段会被更新）
    const updatedUser = await prisma.user.update({
      where: { id: params.id },
      data: safeData,
      select: {
        id: true,
        name: true,
        email: true,
        avatar: true,
        bio: true,
        updatedAt: true,
      },
    });

    return NextResponse.json({ data: updatedUser });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          details: error.errors.map((e) => ({
            field: e.path.join('.'),
            message: e.message,
          })),
        },
        { status: 400 }
      );
    }

    console.error('Update user error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

```typescript
// app/api/users/[id]/password/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { UpdatePasswordSchema } from '@/lib/validations/user';
import bcrypt from 'bcryptjs';

// PUT /api/users/[id]/password - 更新密码（单独接口）
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const { currentPassword, newPassword } = UpdatePasswordSchema.parse(body);

    // 获取用户
    const user = await prisma.user.findUnique({
      where: { id: params.id },
      select: { id: true, password: true },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // 验证当前密码
    const isValid = await bcrypt.compare(currentPassword, user.password);
    if (!isValid) {
      return NextResponse.json(
        { error: 'Current password is incorrect' },
        { status: 400 }
      );
    }

    // 更新密码
    const hashedPassword = await bcrypt.hash(newPassword, 10);
    await prisma.user.update({
      where: { id: params.id },
      data: { password: hashedPassword },
    });

    return NextResponse.json({ success: true, message: 'Password updated' });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          details: error.errors.map((e) => ({
            field: e.path.join('.'),
            message: e.message,
          })),
        },
        { status: 400 }
      );
    }

    console.error('Update password error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

### 常见敏感字段清单

以下字段应**禁止**用户直接修改：

| 字段 | 说明 |
|------|------|
| `role` / `isAdmin` | 权限字段，可导致权限提升 |
| `balance` / `credits` | 余额字段，可导致财务损失 |
| `subscription` / `plan` | 订阅类型，可导致服务滥用 |
| `verified` / `emailVerified` | 验证状态，可绕过验证流程 |
| `createdAt` / `updatedAt` | 时间戳，可篡改记录 |
| `password` | 密码，应单独接口处理 |
| `stripeCustomerId` | 支付信息，可导致支付漏洞 |
| `apiKey` / `secretKey` | 密钥字段，可导致数据泄露 |

---

## L3 企业版（深耕版）

本案例的企业级扩展内容，请参考企业版案例库：

- **详细攻击技术**：参见 [enterprise/infosec/api/mass-assignment.md](../../../enterprise/infosec/api/mass-assignment.md)
- **企业防御架构**：API Gateway 字段过滤、微服务权限隔离
- **合规要求**：OWASP API Security Top 10、SOC 2 访问控制、GDPR 数据最小化
- **监控告警**：异常字段修改检测、权限变更告警
- **渗透测试**：批量赋值漏洞扫描、权限提升测试

企业版核心补充：
1. **嵌套对象攻击**：通过嵌套对象修改关联实体
2. **ORM 特定风险**：各 ORM 框架的批量赋值风险点
3. **GraphQL 批量赋值**：GraphQL Input Type 安全
4. **应急响应**：批量赋值漏洞利用检测、权限回滚
