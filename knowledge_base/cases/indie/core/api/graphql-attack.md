# GraphQL 攻击

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过深度嵌套的 GraphQL 查询，让你的服务器在单次请求中执行数百万次数据库查询，导致服务器资源耗尽或数据泄露。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用 GraphQL API
- [ ] 未配置查询深度限制
- [ ] 未配置查询复杂度限制
- [ ] 类型之间有循环引用关系（如 User → Posts → Comments → User）
- [ ] 未实施字段级权限控制
→ 勾选≥1项，即需关注此风险

### 一句话防御
三层防护：深度限制（必须）+ 复杂度限制（推荐）+ 字段级权限（进阶），1小时内可实施基础防护。

### 快速行动清单
1. [ ] **立即行动项（今天可完成，免费）**：
   - 添加查询深度限制（最大深度：5-10层）
   - 禁用 GraphQL Introspection 查询（生产环境）
   - 添加查询超时设置（如 5-10秒）

2. [ ] **短期行动项（本周可完成，免费）**：
   - 实现查询复杂度分析和限制
   - 配置查询持久化白名单
   - 添加字段级权限控制

3. [ ] **长期行动项（规划中，低成本）**：
   - 部署 GraphQL 安全网关
   - 实现查询缓存机制
   - 建立查询审计日志

### 推荐工具
- **免费**：
  - graphql-depth-limit - [npm](https://www.npmjs.com/package/graphql-depth-limit) - 深度限制中间件
  - graphql-cost-analysis - [GitHub](https://github.com/pa-bru/graphql-cost-analysis) - 复杂度分析
  - Apollo Server 内置限制 - [文档](https://www.apollographql.com/docs/apollo-server/security/authentication/) - 原生支持

- **低成本**：
  - Stellate - $49/月起 - GraphQL CDN + 安全防护
  - GraphQL Shield - [GitHub](https://github.com/maticzav/graphql-shield) - 权限中间件

### 验证方法
- [ ] 构造深度嵌套查询，验证深度限制生效
- [ ] 尝试 Introspection 查询，确认已禁用
- [ ] 构造复杂查询，验证复杂度限制
- [ ] 测试未授权字段访问，验证权限控制

---

## L2 小团队版（理解版）

### 场景还原
某独立开发者的博客平台使用 GraphQL API，攻击者构造了一个深度为20层的嵌套查询：

```graphql
query {
  user(id: 1) {
    posts {
      comments {
        user {
          posts {
            comments {
              # 继续嵌套...20层
            }
          }
        }
      }
    }
  }
}
```

这个查询触发了数百万次数据库查询，服务器 CPU 飙升至 100%，数据库连接池耗尽，所有用户无法访问，持续了3小时。

### 攻击路径（3-5步）
1. **信息收集**：攻击者通过 Introspection 查询获取完整 Schema
2. **发现循环引用**：发现 User → Posts → Comments → User 的循环关系
3. **构造恶意查询**：构建深度嵌套查询，利用循环引用
4. **触发资源耗尽**：单次请求触发指数级数据库查询
5. **数据泄露**：某些情况下可访问未授权字段（如嵌套查询到其他用户的私密信息）

### 防御实施（低成本方案）

#### 方案A：免费方案（基础防护）

**工具/服务**：Apollo Server + 开源中间件

**配置步骤**：

1. **深度限制（必须）**
```javascript
// 使用 Apollo Server
import { ApolloServer } from 'apollo-server';
import depthLimit from 'graphql-depth-limit';

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(7)], // 限制最大深度为7层
});
```

```python
# Python GraphQL (Strawberry)
import strawberry
from strawberry.extensions import DepthLimit

schema = strawberry.Schema(
    query=Query,
    extensions=[DepthLimit(max_depth=7)]
)
```

2. **禁用 Introspection（生产环境）**
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV !== 'production',
  // 或者使用插件完全禁用
  plugins: [
    {
      requestDidStart() {
        return {
          didResolveOperation({ request, operation }) {
            if (operation?.operation === 'query' && !request.query) {
              throw new Error('Only persisted queries are allowed');
            }
          }
        };
      }
    }
  ]
});
```

```python
# Python GraphQL
schema = strawberry.Schema(
    query=Query,
    extensions=[DepthLimit(max_depth=7)],
    # 禁用 introspection
    config=strawberry.Config(
        disable_introspection=True
    )
)
```

3. **查询复杂度限制**
```javascript
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const complexityLimit = createComplexityLimitRule(1000, {
  onCost: (cost) => console.log('query cost:', cost),
  formatErrorMessage: (cost) =>
    `Query with cost ${cost} exceeds maximum allowed complexity`,
});

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(7), complexityLimit],
});
```

```python
# Python 复杂度分析
from graphql_complexity import ComplexityLimitExtension

schema = strawberry.Schema(
    query=Query,
    extensions=[
        DepthLimit(max_depth=7),
        ComplexityLimitExtension(max_complexity=1000)
    ]
)
```

4. **超时设置**
```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: ({ req }) => {
    // 设置查询超时
    return {
      timeout: 5000 // 5秒超时
    };
  },
  plugins: [
    {
      requestDidStart() {
        return {
          willSendResponse(requestContext) {
            // 清理超时资源
          }
        };
      }
    }
  ]
});
```

**局限性**：
- 需要手动配置每个限制
- 字段级权限需要额外实现
- 性能监控能力有限

#### 方案B：低成本方案（<$50/月）

**工具/服务**：GraphQL Shield + Stellate

**配置步骤**：

1. **字段级权限控制（GraphQL Shield）**
```javascript
import { shield, rule, and, or, not } from 'graphql-shield';
import { applyMiddleware } from 'graphql-middleware';

// 定义规则
const isAuthenticated = rule({ cache: 'contextual' })(
  async (parent, args, ctx, info) => {
    return ctx.user !== null;
  }
);

const isAdmin = rule({ cache: 'contextual' })(
  async (parent, args, ctx, info) => {
    return ctx.user?.role === 'ADMIN';
  }
);

const isOwner = rule({ cache: 'contextual' })(
  async (parent, args, ctx, info) => {
    return ctx.user?.id === parent.userId;
  }
);

// 权限配置
const permissions = shield({
  Query: {
    // 所有人可访问
    publicPosts: allow,
    // 需要登录
    myPosts: isAuthenticated,
    // 需要管理员
    allUsers: isAdmin,
  },
  Mutation: {
    createPost: isAuthenticated,
    deletePost: and(isAuthenticated, or(isAdmin, isOwner)),
  },
  User: {
    // 敏感字段需要权限
    email: isOwner,
    paymentInfo: and(isOwner, isAuthenticated),
    // 公开字段
    name: allow,
    posts: allow,
  },
  Post: {
    // 作者才能查看私密帖子
    secretContent: or(isAdmin, isOwner),
  }
});

// 应用中间件
const server = new ApolloServer({
  typeDefs,
  resolvers,
  middleware: applyMiddleware(permissions),
});
```

2. **Stellate 安全配置（云端防护）**
```yaml
# stellate.config.ts
import { Config } from 'stellate'

const config: Config = {
  serviceName: 'my-graphql-api',

  // 查询限制
  security: {
    // 深度限制
    maxDepth: 10,

    // 复杂度限制
    maxComplexity: 5000,

    // 查询超时
    requestTimeout: 10000, // 10秒

    // 禁用 introspection
    disableIntrospection: true,

    // 持久化查询白名单
    persistedQueries: {
      enabled: true,
      mode: 'whitelist',
    },
  },

  // 缓存配置
  caching: {
    rules: [
      {
        types: ['Query'],
        maxAge: 60,
        staleWhileRevalidate: 300,
      }
    ]
  },

  // 速率限制
  rateLimiting: {
    rules: [
      {
        name: 'global',
        limit: 100,
        window: 60,
      },
      {
        name: 'mutations',
        match: { operationType: 'mutation' },
        limit: 20,
        window: 60,
      }
    ]
  }
}

export default config
```

3. **查询持久化（白名单模式）**
```javascript
// 只允许预定义的查询
const persistedQueries = {
  'getUserPosts': `
    query GetUserPosts($userId: ID!) {
      user(id: $userId) {
        posts {
          id
          title
          createdAt
        }
      }
    }
  `,
  // ...其他预定义查询
};

const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [
    {
      requestDidStart() {
        return {
          didResolveOperation({ request, operation }) {
            // 如果不是预定义查询，拒绝执行
            if (request.query && !Object.values(persistedQueries).includes(request.query)) {
              throw new Error('Query not in whitelist');
            }
          }
        };
      }
    }
  ]
});
```

**优势**：
- 字段级权限精细控制
- 云端防护减少服务器压力
- 提供监控和分析面板
- 查询缓存提升性能

### 决策树
```
你的 GraphQL API 是否对外公开？
├── 是 → 必须启用所有防护措施
│   ├── 预算充足 → 方案B（Stellate + Shield）
│   └── 预算有限 → 方案A（开源方案）
└── 否 → 是否有敏感数据？
    ├── 是 → 至少需要深度限制 + 字段级权限
    └── 否 → 深度限制 + 超时设置即可
```

### 代码示例

**完整的 Apollo Server 安全配置**
```javascript
import { ApolloServer } from 'apollo-server-express';
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';
import { shield, rule, and, or, allow } from 'graphql-shield';
import { applyMiddleware } from 'graphql-middleware';

// 1. 定义权限规则
const isAuthenticated = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => ctx.user !== null
);

const isAdmin = rule({ cache: 'contextual' })(
  async (parent, args, ctx) => ctx.user?.role === 'ADMIN'
);

const permissions = shield({
  Query: {
    '*': isAuthenticated, // 默认需要登录
    publicData: allow,     // 公开数据
  },
  Mutation: {
    '*': isAuthenticated,
    deleteUser: isAdmin,
  },
  User: {
    email: isAuthenticated,
    password: isAdmin, // 只有管理员能看密码哈希
  }
}, {
  fallbackRule: allow, // 默认允许（按需调整）
  debug: false, // 生产环境关闭调试
});

// 2. 创建服务器
const server = new ApolloServer({
  typeDefs,
  resolvers,

  // 查询验证规则
  validationRules: [
    depthLimit(7), // 深度限制
    createComplexityLimitRule(1000, { // 复杂度限制
      scalarCost: 1,
      objectCost: 1,
      listFactor: 10,
      onCost: (cost) => {
        console.log(`Query cost: ${cost}`);
      }
    })
  ],

  // 禁用 introspection
  introspection: process.env.NODE_ENV === 'development',

  // 上下文：用户认证
  context: async ({ req }) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const user = await verifyToken(token);
    return { user };
  },

  // 插件：超时和日志
  plugins: [
    {
      requestDidStart(context) {
        const startTime = Date.now();
        const timeout = setTimeout(() => {
          console.error('Query timeout');
        }, 5000);

        return {
          willSendResponse() {
            clearTimeout(timeout);
            const duration = Date.now() - startTime;
            console.log(`Query completed in ${duration}ms`);
          },
          didEncounterErrors(errs) {
            console.error('GraphQL errors:', errs);
          }
        };
      }
    }
  ],

  // 格式化错误
  formatError: (error) => {
    // 生产环境隐藏详细错误信息
    if (process.env.NODE_ENV === 'production') {
      return {
        message: error.message,
        code: error.extensions?.code,
      };
    }
    return error;
  }
});

// 3. 应用权限中间件
const schema = applyMiddleware(server.schema, permissions);
server.schema = schema;

export default server;
```

**查询复杂度计算示例**
```javascript
// 自定义复杂度计算
const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    posts: [Post!]! @cost(complexity: 10)  # 每个用户帖子成本10
  }

  type Post {
    id: ID!
    title: String!
    comments: [Comment!]! @cost(complexity: 5)  # 每个帖子评论成本5
  }

  type Comment {
    id: ID!
    content: String!
  }

  type Query {
    user(id: ID!): User @cost(complexity: 1)
    searchUsers(query: String!): [User!]! @cost(complexity: 20)
  }
`;

// 复杂度计算示例：
// query { user(id: "1") { posts { comments { content } } } }
// 成本 = 1 (user) + 10 (posts) + 5 (comments) * 平均帖子数 * 平均评论数
// 如果用户有10个帖子，每个帖子有5条评论
// 总成本 = 1 + 10 + (5 * 10 * 5) = 261
```

---

## L3 企业版（深耕版）

参见企业级案例：[GraphQL 安全最佳实践](../../enterprise/infosec/graphql-security.md)

### 高级防护策略

1. **查询分析引擎**
   - 实时查询分析
   - 异常查询检测
   - 自动拦截恶意模式

2. **分布式查询缓存**
   - 多层缓存策略
   - 缓存预热
   - 缓存穿透防护

3. **审计与合规**
   - 查询审计日志
   - 数据访问追踪
   - 合规报告生成

### 推荐企业方案
- Apollo Enterprise - 按需定价
- Hasura Cloud - $99/月起
- AWS AppSync - 按请求计费

---

## 相关案例
- [API 未授权访问](./unauthorized-access.md)
- [限流绕过攻击](./rate-limit-bypass.md)

## 推荐武器
- [GraphQL 安全中间件集](../../../weapons/indie/open-source/graphql-security-middleware.md)
- [Stellate 配置模板](../../../weapons/indie/saas/stellate-config.md)
