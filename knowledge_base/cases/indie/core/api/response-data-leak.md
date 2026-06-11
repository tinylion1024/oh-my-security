# 响应数据泄露

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
API 返回了完整的用户对象（包括密码哈希、手机号、身份证号），攻击者调用接口就能获取所有敏感数据，而你只是想显示用户昵称和头像。

### 一分钟识别
你的产品是否有以下特征：
- [ ] API 直接返回数据库对象
- [ ] 响应中包含敏感字段（密码、密钥、手机号）
- [ ] 不同接口返回相同的数据结构
- [ ] 未使用 DTO（数据传输对象）
- [ ] 前端需要的数据比返回的少很多
→ 勾选≥1项，即需关注此风险

### 一句话防御
使用 DTO 模式：定义专门的响应对象，只包含需要暴露的字段，1小时内可实施。

### 快速行动清单
1. [ ] **立即行动项（今天可完成，免费）**：
   - 审查所有 API 响应，识别敏感字段
   - 创建响应 DTO 类，过滤敏感字段
   - 使用 ORM 的字段选择功能

2. [ ] **短期行动项（本周可完成，免费）**：
   - 实现统一的响应过滤器
   - 为不同场景创建不同的 DTO
   - 添加响应日志审计

3. [ ] **长期行动项（规划中，免费）**：
   - 建立字段分类标准（公开/私密/敏感）
   - 实现基于权限的字段过滤
   - 集成 API 文档自动生成

### 推荐工具
- **免费**：
  - class-transformer - [GitHub](https://github.com/typestack/class-transformer) - 对象转换
  - GraphQL 字段级权限 - 原生支持
  - JPA Projection - Spring 原生支持

### 验证方法
- [ ] 调用 API，检查响应中无敏感字段
- [ ] 使用不同权限用户调用，验证字段过滤
- [ ] 检查日志是否记录响应内容（不应记录敏感字段）
- [ ] 使用 API 测试工具扫描敏感数据

---

## L2 小团队版（理解版）

### 场景还原
某独立开发者的用户资料 API 返回了完整的 User 对象：

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.d",
  "phone": "13800138000",
  "id_card": "110101199001011234",
  "api_key": "sk-1234567890abcdef",
  "created_at": "2024-01-01T00:00:00Z"
}
```

攻击者调用 `/api/users/1` 就获取了密码哈希、手机号、身份证号、API密钥等所有敏感信息，导致：
- 密码哈希可被离线破解
- 个人隐私信息泄露
- API 密钥被盗用

### 攻击路径（3-5步）
1. **信息收集**：攻击者发现 API 返回过多数据
2. **数据提取**：调用 API 获取完整对象
3. **敏感信息收集**：提取密码哈希、密钥、隐私信息
4. **进一步攻击**：使用泄露的信息进行撞库、身份盗用
5. **造成损失**：用户隐私泄露、账号被盗、API 滥用

### 防御实施（低成本方案）

#### 方案A：免费方案（DTO 模式）

**工具/服务**：数据传输对象 + 字段过滤

**配置步骤**：

1. **定义 DTO 类**
```typescript
// TypeScript + NestJS
// user.entity.ts
@Entity('users')
export class User {
  @PrimaryGeneratedColumn()
  id: number;

  @Column()
  username: string;

  @Column()
  email: string;

  @Column()
  passwordHash: string; // 敏感字段

  @Column({ nullable: true })
  phone: string; // 敏感字段

  @Column({ nullable: true })
  idCard: string; // 敏感字段

  @Column({ nullable: true })
  apiKey: string; // 敏感字段

  @Column()
  avatar: string;

  @CreateDateColumn()
  createdAt: Date;
}

// user.dto.ts - 公开 DTO
export class UserPublicDto {
  id: number;
  username: string;
  avatar: string;
}

// user.dto.ts - 完整 DTO（需要权限）
export class UserDetailDto {
  id: number;
  username: string;
  email: string;
  avatar: string;
  createdAt: Date;
}

// user.dto.ts - 自己可看到的完整信息
export class UserSelfDto {
  id: number;
  username: string;
  email: string;
  phone: string;
  avatar: string;
  createdAt: Date;
  // 注意：仍然不暴露 passwordHash、apiKey 等
}
```

2. **使用 DTO 过滤响应**
```typescript
// user.service.ts
import { classToPlain, Expose, Exclude } from 'class-transformer';

@Entity('users')
export class User {
  // ... 字段定义

  @Exclude() // 排除敏感字段
  passwordHash: string;

  @Exclude()
  apiKey: string;

  @Exclude()
  idCard: string;

  // 需要权限才能看
  @Expose({ groups: ['owner'] })
  phone: string;

  @Expose({ groups: ['owner', 'admin'] })
  email: string;

  @Expose() // 公开字段
  username: string;

  @Expose()
  avatar: string;
}

// user.controller.ts
@Controller('users')
export class UserController {
  constructor(private userService: UserService) {}

  @Get(':id')
  async getUser(@Param('id') id: number, @CurrentUser() currentUser) {
    const user = await this.userService.findById(id);

    // 根据权限选择暴露组
    const groups = currentUser?.id === id ? ['owner'] : [];
    return classToPlain(user, { groups });
  }

  @Get('me')
  @UseGuards(AuthGuard)
  async getCurrentUser(@CurrentUser() currentUser) {
    const user = await this.userService.findById(currentUser.id);
    return classToPlain(user, { groups: ['owner'] });
  }
}
```

```python
# Python + Pydantic
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 数据库模型
class User:
    id: int
    username: str
    email: str
    password_hash: str
    phone: Optional[str]
    id_card: Optional[str]
    api_key: Optional[str]
    avatar: str
    created_at: datetime

# 公开 DTO
class UserPublicDTO(BaseModel):
    id: int
    username: str
    avatar: str

    class Config:
        from_attributes = True

# 详情 DTO（需要权限）
class UserDetailDTO(BaseModel):
    id: int
    username: str
    email: str
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True

# 自己的信息 DTO
class UserSelfDTO(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str]
    avatar: str
    created_at: datetime

    class Config:
        from_attributes = True

# 使用
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/users/{user_id}", response_model=UserPublicDTO)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/me", response_model=UserSelfDTO)
async def get_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

3. **ORM 字段选择**
```typescript
// TypeORM 字段选择
async findById(id: number, fields?: string[]) {
  const select = fields || ['id', 'username', 'avatar'];

  return this.userRepository.findOne({
    where: { id },
    select,
  });
}

// 使用
@Get(':id')
async getUser(@Param('id') id: number) {
  // 只选择需要的字段
  return this.userService.findById(id, ['id', 'username', 'avatar']);
}
```

```python
# SQLAlchemy 字段选择
from sqlalchemy.orm import load_only

def get_user_public(db: Session, user_id: int):
    return db.query(User).options(
        load_only(User.id, User.username, User.avatar)
    ).filter(User.id == user_id).first()

def get_user_detail(db: Session, user_id: int):
    return db.query(User).options(
        load_only(
            User.id, User.username, User.email,
            User.avatar, User.created_at
        )
    ).filter(User.id == user_id).first()
```

**局限性**：
- 需要手动定义每个 DTO
- 不同权限场景需要不同的 DTO
- 字段新增时容易遗漏

#### 方案B：自动化方案（响应过滤器）

**工具/服务**：自动化字段过滤

**配置步骤**：

1. **全局响应过滤器**
```typescript
// response-filter.interceptor.ts
import {
  Injectable,
  NestInterceptor,
  ExecutionContext,
  CallHandler,
} from '@nestjs/common';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

// 敏感字段配置
const SENSITIVE_FIELDS = [
  'passwordHash',
  'password_hash',
  'apiKey',
  'api_key',
  'idCard',
  'id_card',
  'secret',
  'token',
  'refreshToken',
];

const PERMISSION_BASED_FIELDS = {
  phone: ['owner', 'admin'],
  email: ['owner', 'admin'],
  phoneVerified: ['owner'],
};

@Injectable()
export class ResponseFilterInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const currentUser = request.user;

    return next.handle().pipe(
      map(data => this.filterSensitiveData(data, currentUser))
    );
  }

  private filterSensitiveData(data: any, currentUser: any): any {
    if (!data) return data;

    // 数组处理
    if (Array.isArray(data)) {
      return data.map(item => this.filterSensitiveData(item, currentUser));
    }

    // 对象处理
    if (typeof data === 'object') {
      const filtered = {};

      for (const [key, value] of Object.entries(data)) {
        // 跳过敏感字段
        if (SENSITIVE_FIELDS.includes(key)) {
          continue;
        }

        // 检查权限字段
        const allowedRoles = PERMISSION_BASED_FIELDS[key];
        if (allowedRoles) {
          const userRole = this.getUserRole(currentUser, data);
          if (!allowedRoles.includes(userRole)) {
            continue;
          }
        }

        // 递归处理嵌套对象
        filtered[key] = this.filterSensitiveData(value, currentUser);
      }

      return filtered;
    }

    return data;
  }

  private getUserRole(currentUser: any, data: any): string {
    if (!currentUser) return 'anonymous';
    if (currentUser.id === data?.id) return 'owner';
    if (currentUser.role === 'admin') return 'admin';
    return 'user';
  }
}

// 全局应用
@Module({
  providers: [
    {
      provide: APP_INTERCEPTOR,
      useClass: ResponseFilterInterceptor,
    },
  ],
})
export class AppModule {}
```

```python
# Python 响应过滤中间件
from functools import wraps
from typing import Any, Dict, List, Optional

SENSITIVE_FIELDS = [
    'password_hash', 'api_key', 'id_card',
    'secret', 'token', 'refresh_token'
]

PERMISSION_BASED_FIELDS = {
    'phone': ['owner', 'admin'],
    'email': ['owner', 'admin'],
}

def filter_response(data: Any, current_user: Optional[Dict] = None) -> Any:
    """过滤响应数据"""
    if data is None:
        return None

    if isinstance(data, list):
        return [filter_response(item, current_user) for item in data]

    if isinstance(data, dict):
        filtered = {}
        for key, value in data.items():
            # 跳过敏感字段
            if key in SENSITIVE_FIELDS:
                continue

            # 检查权限字段
            if key in PERMISSION_BASED_FIELDS:
                user_role = get_user_role(current_user, data)
                if user_role not in PERMISSION_BASED_FIELDS[key]:
                    continue

            # 递归处理
            filtered[key] = filter_response(value, current_user)

        return filtered

    return data

def get_user_role(current_user: Optional[Dict], data: Dict) -> str:
    if not current_user:
        return 'anonymous'
    if current_user.get('id') == data.get('id'):
        return 'owner'
    if current_user.get('role') == 'admin':
        return 'admin'
    return 'user'

# 使用装饰器
def filter_sensitive_data(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        result = f(*args, **kwargs)
        current_user = getattr(request, 'user', None)
        return filter_response(result, current_user)
    return decorated_function

# 应用
@app.get("/users/<int:user_id>")
@filter_sensitive_data
def get_user(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    return user.to_dict()
```

2. **API 文档集成**
```typescript
// Swagger 自动文档 + 响应示例
@ApiTags('users')
@Controller('users')
export class UserController {
  @Get(':id')
  @ApiOperation({ summary: '获取用户信息' })
  @ApiOkResponse({
    description: '用户公开信息',
    type: UserPublicDto,
    example: {
      id: 1,
      username: 'john_doe',
      avatar: 'https://example.com/avatar.jpg',
    }
  })
  async getUser(@Param('id') id: number) {
    // ...
  }

  @Get('me')
  @UseGuards(AuthGuard)
  @ApiOperation({ summary: '获取当前用户信息' })
  @ApiOkResponse({
    description: '当前用户详细信息',
    type: UserSelfDto,
    example: {
      id: 1,
      username: 'john_doe',
      email: 'john@example.com',
      phone: '138****8000',
      avatar: 'https://example.com/avatar.jpg',
    }
  })
  async getCurrentUser(@CurrentUser() currentUser) {
    // ...
  }
}
```

**优势**：
- 自动过滤，无需手动定义每个 DTO
- 统一管理敏感字段
- 支持权限控制

### 决策树
```
你的 API 是否返回敏感数据？
├── 是 → 必须使用 DTO 过滤
│   ├── 是否有多种权限场景？→ 使用权限组 + 响应过滤器
│   └── 场景单一？→ 使用固定 DTO
└── 否 → 是否可能新增敏感字段？
    ├── 是 → 使用响应过滤器预防
    └── 否 → 直接返回即可
```

### 代码示例

**完整的响应过滤方案**
```typescript
// field-filter.service.ts
import { Injectable } from '@nestjs/common';

interface FieldPolicy {
  exclude?: string[];
  include?: string[];
  groups?: { [field: string]: string[] };
}

@Injectable()
export class FieldFilterService {
  // 默认敏感字段
  private defaultSensitiveFields = [
    'passwordHash', 'password_hash',
    'apiKey', 'api_key',
    'idCard', 'id_card',
    'secret', 'token', 'refreshToken',
    'creditCard', 'credit_card',
    'ssn',
  ];

  // 字段脱敏规则
  private maskingRules = {
    email: (value: string) => value?.replace(/(.{2}).*(@.*)/, '$1***$2'),
    phone: (value: string) => value?.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2'),
    idCard: (value: string) => value?.replace(/(.{6}).*(.{4})/, '$1********$2'),
    creditCard: (value: string) => value?.replace(/(\d{4})\d{8}(\d{4})/, '$1********$2'),
  };

  /**
   * 过滤对象字段
   */
  filter<T>(data: T, policy: FieldPolicy, userGroups: string[] = []): Partial<T> {
    if (!data || typeof data !== 'object') {
      return data;
    }

    if (Array.isArray(data)) {
      return data.map(item => this.filter(item, policy, userGroups)) as any;
    }

    const result: any = {};

    for (const [key, value] of Object.entries(data)) {
      // 检查排除字段
      if (policy.exclude?.includes(key)) {
        continue;
      }

      // 检查默认敏感字段
      if (this.defaultSensitiveFields.includes(key)) {
        continue;
      }

      // 检查包含字段（白名单模式）
      if (policy.include && !policy.include.includes(key)) {
        continue;
      }

      // 检查权限组
      if (policy.groups && policy.groups[key]) {
        const allowedGroups = policy.groups[key];
        const hasPermission = userGroups.some(g => allowedGroups.includes(g));
        if (!hasPermission) {
          continue;
        }
      }

      // 应用脱敏规则
      let filteredValue = value;
      if (typeof value === 'string' && this.maskingRules[key]) {
        filteredValue = this.maskingRules[key](value);
      }

      // 递归处理嵌套对象
      if (filteredValue && typeof filteredValue === 'object') {
        filteredValue = this.filter(filteredValue, policy, userGroups);
      }

      result[key] = filteredValue;
    }

    return result;
  }

  /**
   * 创建策略构建器
   */
  createPolicy(): PolicyBuilder {
    return new PolicyBuilder(this.defaultSensitiveFields);
  }
}

class PolicyBuilder {
  private policy: FieldPolicy = {};

  constructor(private defaultSensitiveFields: string[]) {}

  exclude(...fields: string[]): this {
    this.policy.exclude = [...(this.policy.exclude || []), ...fields];
    return this;
  }

  include(...fields: string[]): this {
    this.policy.include = [...(this.policy.include || []), ...fields];
    return this;
  }

  requireGroup(field: string, groups: string[]): this {
    if (!this.policy.groups) this.policy.groups = {};
    this.policy.groups[field] = groups;
    return this;
  }

  build(): FieldPolicy {
    return this.policy;
  }
}

// 使用示例
@Controller('users')
export class UserController {
  constructor(
    private userService: UserService,
    private fieldFilter: FieldFilterService,
  ) {}

  @Get(':id')
  async getUser(@Param('id') id: number) {
    const user = await this.userService.findById(id);

    // 公开信息：只包含基本字段
    const policy = this.fieldFilter.createPolicy()
      .include('id', 'username', 'avatar')
      .build();

    return this.fieldFilter.filter(user, policy);
  }

  @Get(':id/detail')
  @UseGuards(AuthGuard)
  async getUserDetail(
    @Param('id') id: number,
    @CurrentUser() currentUser,
  ) {
    const user = await this.userService.findById(id);

    // 判断权限
    const groups = [];
    if (currentUser.id === id) groups.push('owner');
    if (currentUser.role === 'admin') groups.push('admin');

    // 详情信息：email 需要权限，phone 需脱敏
    const policy = this.fieldFilter.createPolicy()
      .include('id', 'username', 'email', 'phone', 'avatar', 'createdAt')
      .requireGroup('email', ['owner', 'admin'])
      .build();

    return this.fieldFilter.filter(user, policy, groups);
  }

  @Get('me')
  @UseGuards(AuthGuard)
  async getCurrentUser(@CurrentUser() currentUser) {
    const user = await this.userService.findById(currentUser.id);

    // 自己的信息：可以看大部分字段，但仍需脱敏
    const policy = this.fieldFilter.createPolicy()
      .include('id', 'username', 'email', 'phone', 'avatar', 'createdAt')
      .build();

    return this.fieldFilter.filter(user, policy, ['owner']);
  }
}
```

---

## L3 企业版（深耕版）

参见企业级案例：[API 数据安全](../../enterprise/infosec/api-data-security.md)

### 高级防护策略

1. **动态字段控制**
   - 基于用户属性的实时权限
   - 字段级加密
   - 数据脱敏策略

2. **数据分类与标记**
   - 自动敏感数据识别
   - 数据分类标签
   - 合规性检查

3. **审计与监控**
   - 敏感数据访问审计
   - 异常访问检测
   - 合规报告生成

### 推荐企业方案
- Apache Shiro - 字段级权限
- Spring Security - 方法级安全
- API Gateway - 响应过滤

---

## 相关案例
- [API 未授权访问](./unauthorized-access.md)
- [日志敏感数据泄露](../data/log-leak.md)

## 推荐武器
- [响应过滤器模板](../../../weapons/indie/open-source/response-filter.md)
- [DTO 生成器](../../../weapons/indie/open-source/dto-generator.md)
