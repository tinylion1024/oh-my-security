# SQL 注入

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
用户输入未过滤，直接拼接到 SQL 查询，攻击者可读取、篡改、删除整个数据库数据。

### 一分钟识别
你的产品是否有以下特征：
- [ ] SQL 查询使用字符串拼接用户输入
- [ ] 使用 `${variable}` 或 `+ variable +` 构造 SQL
- [ ] 直接将 req.body/req.query 参数传入数据库查询
- [ ] 错误信息直接返回 SQL 语句详情
→ 勾选≥1项，即需关注此风险

### 一句话防御
使用参数化查询（Prepared Statement）替代字符串拼接，完全免费，代码改动极小。

### 快速行动清单
1. [ ] **立即（今天）**：审计所有 SQL 查询，标记使用字符串拼接的位置
2. [ ] **短期（本周）**：将所有拼接 SQL 改为参数化查询
3. [ ] **长期（规划中）**：引入 ORM 框架，使用查询构建器自动防护

### 推荐工具
- **免费**：
  - [Prisma](https://www.prisma.io/) - 类型安全的 ORM，自动参数化
  - [Drizzle ORM](https://orm.drizzle.team/) - 轻量级 TypeScript ORM
  - [Knex.js](https://knexjs.org/) - 查询构建器，自动转义
  - [pg-promise](https://github.com/vitaly-t/pg-promise) - PostgreSQL 参数化查询
- **低成本**：
  - [Supabase](https://supabase.com/) - 托管 PostgreSQL + 安全 API
  - [PlanetScale](https://planetscale.com/) - MySQL 兼容，内置安全防护

### 验证方法
- [ ] 在输入框输入 `' OR '1'='1`，应返回正常错误而非异常数据
- [ ] 在输入框输入 `'; DROP TABLE users;--`，数据库表应完好无损
- [ ] 使用 SQLMap 工具扫描，应无注入点报告

---

## L2 小团队版（理解版）

### 场景还原
你的产品是一个电商平台的商品搜索功能。某天，客服接到大量用户投诉账户余额异常。调查发现，攻击者通过搜索框注入了恶意 SQL：

```sql
' UNION SELECT id, username, password, email, balance FROM users--
```

这个注入不仅绕过了商品搜索，还泄露了 **所有用户的账号密码和余额信息**。攻击者随后批量修改用户余额，提现后消失。更糟糕的是，数据库没有备份，恢复需要数周时间。

### 攻击路径（简化版）
1. **发现目标**：攻击者在搜索框输入 `'`，收到数据库错误信息，确认存在注入点
2. **探测结构**：通过 `UNION SELECT` 和 `information_schema` 获取表结构和字段名
3. **提取数据**：构造 UNION 注入，批量导出用户表、订单表等敏感数据
4. **权限提升**：利用数据库配置不当，读取系统文件或执行系统命令
5. **数据篡改**：修改用户余额、删除审计日志、植入后门账户

### 防御实施（低成本方案）

#### 方案A：免费方案（参数化查询）

**工具/服务**: 原生参数化查询

**配置步骤**:

```javascript
// ❌ 危险：字符串拼接
const searchProducts = async (keyword) => {
  const sql = `SELECT * FROM products WHERE name LIKE '%${keyword}%'`;
  // 输入: ' OR '1'='1' --
  // 实际执行: SELECT * FROM products WHERE name LIKE '%' OR '1'='1' --%'
  return await db.query(sql);
};

// ✅ 安全：参数化查询
const searchProductsSafe = async (keyword) => {
  const sql = `SELECT * FROM products WHERE name LIKE ?`;
  // 参数自动转义，输入被当作字面值处理
  return await db.query(sql, [`%${keyword}%`]);
};
```

**Node.js + mysql2 示例**:

```javascript
const mysql = require('mysql2/promise');

// 创建连接池
const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
});

// ✅ 安全的用户查询
async function getUserById(userId) {
  const [rows] = await pool.execute(
    'SELECT id, username, email FROM users WHERE id = ?',
    [userId] // 参数化，自动转义
  );
  return rows[0];
}

// ✅ 安全的搜索查询
async function searchProducts(keyword, category, minPrice, maxPrice) {
  let sql = 'SELECT * FROM products WHERE 1=1';
  const params = [];

  if (keyword) {
    sql += ' AND name LIKE ?';
    params.push(`%${keyword}%`);
  }

  if (category) {
    sql += ' AND category = ?';
    params.push(category);
  }

  if (minPrice !== undefined) {
    sql += ' AND price >= ?';
    params.push(minPrice);
  }

  if (maxPrice !== undefined) {
    sql += ' AND price <= ?';
    params.push(maxPrice);
  }

  const [rows] = await pool.execute(sql, params);
  return rows;
}

// ✅ 安全的插入操作
async function createUser(username, email, hashedPassword) {
  const [result] = await pool.execute(
    'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
    [username, email, hashedPassword]
  );
  return result.insertId;
}
```

**PostgreSQL 示例**:

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// ✅ PostgreSQL 参数化查询（使用 $1, $2 占位符）
async function getUserByEmail(email) {
  const result = await pool.query(
    'SELECT * FROM users WHERE email = $1',
    [email]
  );
  return result.rows[0];
}

// ✅ 使用 pg-promise 更安全的写法
const pgp = require('pg-promise')();

const db = pgp(process.env.DATABASE_URL);

async function updateUserInfo(userId, updates) {
  // 使用 Named Parameters 更清晰
  return await db.oneOrNone(
    `UPDATE users
     SET username = $<username>,
         email = $<email>,
         updated_at = NOW()
     WHERE id = $<userId>
     RETURNING *`,
    { userId, ...updates }
  );
}
```

#### 方案B：低成本方案（ORM）

**工具/服务**: Prisma ORM

**配置步骤**:

```typescript
// schema.prisma
model User {
  id        Int      @id @default(autoincrement())
  username  String   @unique
  email     String   @unique
  password  String
  balance   Decimal  @default(0)
  createdAt DateTime @default(now())
}

model Product {
  id          Int      @id @default(autoincrement())
  name        String
  category    String
  price       Decimal
  description String?
  createdAt   DateTime @default(now())
}
```

```typescript
// ✅ Prisma 自动参数化，完全防注入
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// 安全查询：用户查询
async function getUserById(id: number) {
  return await prisma.user.findUnique({
    where: { id },
    select: {
      id: true,
      username: true,
      email: true,
      // password 字段不返回
    },
  });
}

// 安全查询：产品搜索
async function searchProducts(keyword: string, category?: string) {
  return await prisma.product.findMany({
    where: {
      AND: [
        {
          OR: [
            { name: { contains: keyword, mode: 'insensitive' } },
            { description: { contains: keyword, mode: 'insensitive' } },
          ],
        },
        category ? { category } : {},
      ],
    },
    orderBy: { createdAt: 'desc' },
  });
}

// 安全操作：用户注册
async function createUser(data: { username: string; email: string; password: string }) {
  return await prisma.user.create({
    data,
    select: {
      id: true,
      username: true,
      email: true,
    },
  });
}

// 安全操作：余额更新（使用事务）
async function transferBalance(fromId: number, toId: number, amount: number) {
  return await prisma.$transaction(async (tx) => {
    // 扣款
    await tx.user.update({
      where: { id: fromId },
      data: { balance: { decrement: amount } },
    });

    // 入账
    await tx.user.update({
      where: { id: toId },
      data: { balance: { increment: amount } },
    });

    // 记录日志
    await tx.transactionLog.create({
      data: { fromId, toId, amount, type: 'TRANSFER' },
    });
  });
}
```

**成本估算**:
- Prisma: 完全免费开源
- Supabase 托管: 免费 500MB 数据库，超出后 $25/月起

**优势**:
- 类型安全，编译期检查
- 自动参数化，无需手动处理
- 查询构建器直观易用
- 支持多数据库（PostgreSQL、MySQL、SQLite、MongoDB）

### ORM 安全使用方法

```typescript
// ❌ 危险：Prisma 原始 SQL（仍有注入风险）
const users = await prisma.$queryRaw`
  SELECT * FROM users WHERE name = '${name}'
`;

// ✅ 安全：Prisma 原始 SQL + 参数化
const users = await prisma.$queryRaw<
  User[]
>`SELECT * FROM users WHERE name = ${name}`;

// ✅ 更安全：使用 Prisma 查询 API
const users = await prisma.user.findMany({
  where: { name },
});
```

```javascript
// ❌ 危险：Knex.js 原始 SQL
const users = await knex.raw(
  `SELECT * FROM users WHERE id = ${userId}`
);

// ✅ 安全：Knex.js 参数化
const users = await knex.raw(
  'SELECT * FROM users WHERE id = ?',
  [userId]
);

// ✅ 更安全：Knex.js 查询构建器
const users = await knex('users').where('id', userId);
```

### 决策树

```
你的项目使用什么数据库访问方式？
├── 直接 SQL 查询
│   ├── 有字符串拼接？ → 立即改为参数化查询（方案A）
│   └── 已使用参数化？ → 继续检查是否有遗漏
└── 使用 ORM/查询构建器
    ├── 原始 SQL 查询？ → 检查是否参数化
    └── 仅使用 API？ → 已安全，确认无绕过
```

### 完整代码示例

以下是一个完整的 Next.js API Route 示例，使用 Prisma 实现安全的 CRUD 操作：

```typescript
// app/api/products/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// GET /api/products - 安全的产品搜索
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const keyword = searchParams.get('q') || '';
    const category = searchParams.get('category');
    const minPrice = searchParams.get('minPrice');
    const maxPrice = searchParams.get('maxPrice');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 100);

    // Prisma 自动参数化，完全防注入
    const where = {
      AND: [
        keyword
          ? {
              OR: [
                { name: { contains: keyword, mode: 'insensitive' as const } },
                { description: { contains: keyword, mode: 'insensitive' as const } },
              ],
            }
          : {},
        category ? { category } : {},
        minPrice ? { price: { gte: parseFloat(minPrice) } } : {},
        maxPrice ? { price: { lte: parseFloat(maxPrice) } } : {},
      ],
    };

    const [products, total] = await Promise.all([
      prisma.product.findMany({
        where,
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: 'desc' },
      }),
      prisma.product.count({ where }),
    ]);

    return NextResponse.json({
      data: products,
      meta: { page, limit, total, totalPages: Math.ceil(total / limit) },
    });
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// POST /api/products - 安全的产品创建
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, category, price, description } = body;

    // 输入验证（防注入的第一道防线）
    if (!name || typeof name !== 'string' || name.length > 200) {
      return NextResponse.json(
        { error: 'Invalid product name' },
        { status: 400 }
      );
    }

    if (!category || typeof category !== 'string') {
      return NextResponse.json(
        { error: 'Invalid category' },
        { status: 400 }
      );
    }

    const priceValue = parseFloat(price);
    if (isNaN(priceValue) || priceValue < 0) {
      return NextResponse.json(
        { error: 'Invalid price' },
        { status: 400 }
      );
    }

    // Prisma 自动参数化
    const product = await prisma.product.create({
      data: {
        name,
        category,
        price: priceValue,
        description: description || null,
      },
    });

    return NextResponse.json({ data: product }, { status: 201 });
  } catch (error) {
    console.error('Create error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

---

## L3 企业版（深耕版）

本案例的企业级扩展内容，请参考企业版案例库：

- **详细攻击技术**：参见 [enterprise/infosec/api/sql-injection.md](../../../enterprise/infosec/api/sql-injection.md)
- **企业防御架构**：WAF SQL 注入规则、数据库审计、最小权限原则
- **合规要求**：OWASP Top 10 #A03:2021、PCI DSS 数据安全、SOC 2 访问控制
- **监控告警**：异常 SQL 模式检测、数据库访问审计、实时告警
- **渗透测试**：SQLMap 自动化扫描、盲注测试、二次注入检测

企业版核心补充：
1. **高级注入技术**：盲注、时间盲注、堆叠查询、二次注入
2. **数据库隔离**：读写分离、应用账户最小权限、存储过程安全
3. **WAF 策略**：SQL 注入特征库、语义分析、机器学习检测
4. **应急响应**：注入事件溯源、数据泄露评估、系统加固
