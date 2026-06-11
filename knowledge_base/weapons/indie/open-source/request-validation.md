# 请求验证库

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 1-2小时
- **维护成本**: 0.5小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
统一 API 请求参数验证，防止无效数据、SQL 注入、XSS 攻击，适用于所有接收用户输入的 API 端点。

## 验证库对比

### 快速选型表

| 库名 | 语言 | 实现复杂度 | 性能 | 类型安全 | 适用场景 | 独立开发者推荐度 |
|------|------|-----------|------|---------|---------|----------------|
| **Pydantic** | Python | ⭐ 简单 | ⭐⭐⭐⭐ 高 | ✅ 是 | FastAPI/Flask/Django | ⭐⭐⭐⭐⭐ |
| **Zod** | TypeScript | ⭐ 简单 | ⭐⭐⭐⭐ 高 | ✅ 是 | 前后端通用 | ⭐⭐⭐⭐⭐ |
| **Joi** | JavaScript | ⭐ 简单 | ⭐⭐⭐ 中等 | ❌ 否 | Express/Node.js | ⭐⭐⭐⭐ |
| **JSON Schema** | 通用 | ⭐⭐ 中等 | ⭐⭐⭐ 中等 | ❌ 否 | 跨语言验证 | ⭐⭐⭐ |
| **Validator.js** | JavaScript | ⭐ 简单 | ⭐⭐⭐⭐⭐ 极高 | ❌ 否 | 字符串验证 | ⭐⭐⭐⭐ |

### 详细对比

#### 1. Pydantic（Python 推荐）

**优点**：
- 与 FastAPI 深度集成，零配置
- 运行时类型检查 + IDE 类型提示
- 自动生成 OpenAPI 文档
- 支持复杂验证规则

**缺点**：
- 性能略低于原生 Python（但可接受）
- 学习自定义验证器语法

**适用场景**：
- FastAPI 项目（默认集成）
- Flask + Pydantic 插件
- Django API 层

---

#### 2. Zod（TypeScript 推荐）

**优点**：
- TypeScript 原生支持，类型推断完美
- 链式调用，API 优雅
- 支持异步验证
- 可生成 TypeScript 类型

**缺点**：
- 包体积较大（压缩后 ~50KB）
- 学习曲线略陡

**适用场景**：
- 前端表单验证
- Node.js API 验证
- tRPC 类型安全 API

---

#### 3. Joi（Node.js 经典）

**优点**：
- API 成熟稳定
- 生态丰富
- 支持复杂验证规则

**缺点**：
- 无 TypeScript 类型推断
- 性能略低于 Zod

**适用场景**：
- Express 项目
- 传统 Node.js API
- 不需要类型安全的项目

---

## 快速上手（5分钟）

### 方案一：Pydantic（Python + FastAPI）

```python
# models.py
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    banned = "banned"

class UserCreate(BaseModel):
    """用户创建请求模型"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        regex="^[a-zA-Z0-9_]+$",
        description="用户名，仅允许字母数字下划线"
    )
    email: EmailStr
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密码，至少8位"
    )
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    status: UserStatus = UserStatus.active
    tags: List[str] = Field(default_factory=list, max_items=10)

    @validator('password')
    def password_strength(cls, v):
        """密码强度验证"""
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    @validator('username')
    def username_not_reserved(cls, v):
        """用户名保留字检查"""
        reserved = ['admin', 'root', 'system', 'api']
        if v.lower() in reserved:
            raise ValueError(f'用户名 {v} 是保留字')
        return v

    class Config:
        # 示例数据（用于 OpenAPI 文档）
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "age": 25,
                "status": "active",
                "tags": ["developer", "python"]
            }
        }

class UserUpdate(BaseModel):
    """用户更新请求模型"""
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    status: Optional[UserStatus] = None
    tags: Optional[List[str]] = None

    class Config:
        extra = "forbid"  # 禁止额外字段

class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    age: Optional[int]
    status: UserStatus
    created_at: datetime

    class Config:
        orm_mode = True  # 支持从 ORM 对象创建
```

```python
# main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

app = FastAPI()

# 统一错误响应格式
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """自定义验证错误响应"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Failed",
            "details": errors
        }
    )

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    创建用户
    
    Pydantic 会自动验证：
    - username: 3-20字符，仅字母数字下划线
    - email: 邮箱格式
    - password: 至少8位，包含大小写字母和数字
    - age: 0-150 之间
    """
    # 验证通过后的业务逻辑
    return {
        "id": 1,
        "username": user.username,
        "email": user.email,
        "age": user.age,
        "status": user.status,
        "created_at": datetime.utcnow()
    }

@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """更新用户（部分更新）"""
    # 验证至少有一个字段被更新
    if not user.dict(exclude_unset=True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要更新一个字段"
        )
    
    # 更新逻辑
    return {"id": user_id, **user.dict(exclude_unset=True)}
```

### 方案二：Zod（TypeScript/Node.js）

```typescript
// schemas/user.schema.ts
import { z } from 'zod';

// 用户状态枚举
const UserStatusEnum = z.enum(['active', 'inactive', 'banned']);

// 用户创建 Schema
export const UserCreateSchema = z.object({
  username: z.string()
    .min(3, '用户名至少3个字符')
    .max(20, '用户名最多20个字符')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名仅允许字母数字下划线')
    .refine(
      (val) => !['admin', 'root', 'system', 'api'].includes(val.toLowerCase()),
      { message: '该用户名是保留字' }
    ),
  
  email: z.string()
    .email('邮箱格式不正确')
    .max(100, '邮箱最多100个字符'),
  
  password: z.string()
    .min(8, '密码至少8个字符')
    .max(100, '密码最多100个字符')
    .refine(
      (val) => /[A-Z]/.test(val),
      { message: '密码必须包含至少一个大写字母' }
    )
    .refine(
      (val) => /[a-z]/.test(val),
      { message: '密码必须包含至少一个小写字母' }
    )
    .refine(
      (val) => /[0-9]/.test(val),
      { message: '密码必须包含至少一个数字' }
    ),
  
  age: z.number()
    .int('年龄必须是整数')
    .min(0, '年龄不能小于0')
    .max(150, '年龄不能大于150')
    .optional(),
  
  status: UserStatusEnum.default('active'),
  
  tags: z.array(z.string())
    .max(10, '标签最多10个')
    .default([]),
});

// 用户更新 Schema（部分字段可选）
export const UserUpdateSchema = UserCreateSchema.partial();

// 从 Schema 推断 TypeScript 类型
export type UserCreate = z.infer<typeof UserCreateSchema>;
export type UserUpdate = z.infer<typeof UserUpdateSchema>;

// 响应 Schema
export const UserResponseSchema = z.object({
  id: z.number().int().positive(),
  username: z.string(),
  email: z.string().email(),
  age: z.number().optional(),
  status: UserStatusEnum,
  createdAt: z.date(),
});

export type UserResponse = z.infer<typeof UserResponseSchema>;
```

```typescript
// middleware/validate.ts
import { Request, Response, NextFunction } from 'express';
import { AnyZodObject, ZodError } from 'zod';

export const validate = (schema: AnyZodObject) => {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      // 验证请求体、查询参数、路径参数
      await schema.parseAsync({
        body: req.body,
        query: req.query,
        params: req.params,
      });
      
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        // 格式化错误响应
        const errors = error.errors.map((err) => ({
          field: err.path.join('.'),
          message: err.message,
          code: err.code,
        }));
        
        res.status(422).json({
          error: 'Validation Failed',
          details: errors,
        });
      } else {
        next(error);
      }
    }
  };
};
```

```typescript
// routes/users.ts
import { Router } from 'express';
import { UserCreateSchema, UserUpdateSchema } from '../schemas/user.schema';
import { validate } from '../middleware/validate';

const router = Router();

// 创建用户
router.post(
  '/',
  validate(
    UserCreateSchema.omit({ status: true, tags: true }).extend({
      body: UserCreateSchema,
    })
  ),
  async (req, res) => {
    // 类型安全：req.body 已被验证
    const user: UserCreate = req.body;
    
    // 业务逻辑
    res.status(201).json({
      id: 1,
      ...user,
      createdAt: new Date(),
    });
  }
);

// 更新用户
router.patch(
  '/:id',
  validate(UserUpdateSchema),
  async (req, res) => {
    const { id } = req.params;
    const updates: UserUpdate = req.body;
    
    // 验证至少有一个字段被更新
    if (Object.keys(updates).length === 0) {
      return res.status(400).json({
        error: '至少需要更新一个字段',
      });
    }
    
    // 更新逻辑
    res.json({
      id: parseInt(id),
      ...updates,
    });
  }
);

export default router;
```

### 方案三：Joi（Node.js/Express）

```javascript
// validators/user.validator.js
const Joi = require('joi');

// 用户创建验证 Schema
const userCreateSchema = Joi.object({
  username: Joi.string()
    .alphanum()
    .min(3)
    .max(20)
    .required()
    .messages({
      'string.base': '用户名必须是字符串',
      'string.empty': '用户名不能为空',
      'string.min': '用户名至少{#limit}个字符',
      'string.max': '用户名最多{#limit}个字符',
      'any.required': '用户名是必填项',
    })
    .custom((value, helpers) => {
      const reserved = ['admin', 'root', 'system', 'api'];
      if (reserved.includes(value.toLowerCase())) {
        return helpers.error('any.invalid');
      }
      return value;
    }, '保留字检查'),

  email: Joi.string()
    .email()
    .max(100)
    .required()
    .messages({
      'string.email': '邮箱格式不正确',
    }),

  password: Joi.string()
    .min(8)
    .max(100)
    .required()
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$/, '密码强度')
    .messages({
      'string.pattern.name': '密码必须包含大小写字母和数字',
    }),

  age: Joi.number()
    .integer()
    .min(0)
    .max(150)
    .optional(),

  status: Joi.string()
    .valid('active', 'inactive', 'banned')
    .default('active'),

  tags: Joi.array()
    .items(Joi.string())
    .max(10)
    .default([]),
});

// 用户更新验证 Schema
const userUpdateSchema = userCreateSchema.fork(
  ['username', 'email', 'password', 'age', 'status', 'tags'],
  (schema) => schema.optional()
);

// 验证中间件
const validate = (schema, property = 'body') => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[property], {
      abortEarly: false,  // 返回所有错误
      stripUnknown: true, // 移除未知字段
      convert: true,      // 类型转换
    });

    if (error) {
      const errors = error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message,
        type: detail.type,
      }));

      return res.status(422).json({
        error: 'Validation Failed',
        details: errors,
      });
    }

    // 替换请求体为验证后的值
    req[property] = value;
    next();
  };
};

module.exports = {
  userCreateSchema,
  userUpdateSchema,
  validate,
};
```

```javascript
// routes/users.js
const express = require('express');
const { userCreateSchema, userUpdateSchema, validate } = require('../validators/user.validator');

const router = express.Router();

// 创建用户
router.post(
  '/',
  validate(userCreateSchema),
  async (req, res) => {
    // req.body 已被验证和清理
    const user = req.body;
    
    // 业务逻辑
    res.status(201).json({
      id: 1,
      ...user,
      createdAt: new Date(),
    });
  }
);

// 更新用户
router.patch(
  '/:id',
  validate(userUpdateSchema),
  async (req, res) => {
    const { id } = req.params;
    const updates = req.body;
    
    if (Object.keys(updates).length === 0) {
      return res.status(400).json({
        error: '至少需要更新一个字段',
      });
    }
    
    res.json({
      id: parseInt(id),
      ...updates,
    });
  }
);

module.exports = router;
```

---

## 详细方案

### 方案架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端请求                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      验证中间件层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   类型验证    │  │   格式验证   │  │   业务验证   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                            │                                     │
│                    通过 → 转发控制器                              │
│                    失败 → 422 错误响应                           │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务控制器层                                 │
│  - 使用验证后的类型安全数据                                       │
│  - 执行业务逻辑                                                   │
│  - 返回响应                                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 高级验证规则

#### 1. 自定义验证器

**Pydantic**：
```python
from pydantic import BaseModel, validator

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    card_number: str
    cvv: str

    @validator('amount')
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError('金额必须大于0')
        if v > 1000000:
            raise ValueError('单笔金额不能超过100万')
        return round(v, 2)  # 保留两位小数

    @validator('card_number')
    def luhn_check(cls, v):
        """Luhn 算法验证信用卡号"""
        v = v.replace(' ', '')
        if not v.isdigit():
            raise ValueError('卡号必须为数字')
        
        # Luhn 算法
        digits = [int(d) for d in v]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(divmod(d * 2, 10))
        
        if checksum % 10 != 0:
            raise ValueError('无效的卡号')
        
        return v

    @validator('cvv')
    def cvv_format(cls, v):
        if not v.isdigit() or len(v) not in [3, 4]:
            raise ValueError('CVV 必须是3-4位数字')
        return v
```

**Zod**：
```typescript
// 自定义 Luhn 验证
const luhnCheck = (cardNumber: string): boolean => {
  const digits = cardNumber.replace(/\s/g, '').split('').map(Number);
  const oddDigits = digits.slice(-1, -digits.length - 1, -2);
  const evenDigits = digits.slice(-2, -digits.length - 1, -2);
  
  let checksum = oddDigits.reduce((sum, d) => sum + d, 0);
  for (const d of evenDigits) {
    checksum += Math.floor((d * 2) / 10) + ((d * 2) % 10);
  }
  
  return checksum % 10 === 0;
};

// 支付请求 Schema
const PaymentRequestSchema = z.object({
  amount: z.number()
    .positive('金额必须大于0')
    .max(1000000, '单笔金额不能超过100万')
    .transform((val) => Math.round(val * 100) / 100), // 保留两位小数
  
  currency: z.string()
    .length(3, '货币代码必须是3位')
    .regex(/^[A-Z]{3}$/, '货币代码格式不正确'),
  
  cardNumber: z.string()
    .regex(/^[\d\s]+$/, '卡号必须为数字')
    .transform((val) => val.replace(/\s/g, ''))
    .refine(luhnCheck, { message: '无效的卡号' }),
  
  cvv: z.string()
    .regex(/^\d{3,4}$/, 'CVV 必须是3-4位数字'),
});
```

#### 2. 跨字段验证

**Pydantic**：
```python
from pydantic import BaseModel, root_validator

class DateRange(BaseModel):
    start_date: date
    end_date: date

    @root_validator
    def validate_date_range(cls, values):
        start = values.get('start_date')
        end = values.get('end_date')
        
        if start and end:
            if start > end:
                raise ValueError('开始日期不能晚于结束日期')
            
            delta = (end - start).days
            if delta > 365:
                raise ValueError('日期范围不能超过1年')
        
        return values

class PasswordChange(BaseModel):
    password: str
    confirm_password: str

    @root_validator
    def passwords_match(cls, values):
        pw1 = values.get('password')
        pw2 = values.get('confirm_password')
        
        if pw1 and pw2 and pw1 != pw2:
            raise ValueError('两次密码输入不一致')
        
        return values
```

**Zod**：
```typescript
// 日期范围验证
const DateRangeSchema = z.object({
  startDate: z.date(),
  endDate: z.date(),
}).refine(
  (data) => data.startDate <= data.endDate,
  { message: '开始日期不能晚于结束日期', path: ['endDate'] }
).refine(
  (data) => {
    const delta = (data.endDate.getTime() - data.startDate.getTime()) / (1000 * 60 * 60 * 24);
    return delta <= 365;
  },
  { message: '日期范围不能超过1年', path: ['endDate'] }
);

// 密码确认验证
const PasswordChangeSchema = z.object({
  password: z.string().min(8),
  confirmPassword: z.string(),
}).refine(
  (data) => data.password === data.confirmPassword,
  { message: '两次密码输入不一致', path: ['confirmPassword'] }
);
```

#### 3. 条件验证

**Pydantic**：
```python
from pydantic import BaseModel, validator, root_validator
from typing import Optional, Literal

class PaymentRequest(BaseModel):
    payment_method: Literal['credit_card', 'bank_transfer', 'paypal']
    
    # 信用卡字段
    card_number: Optional[str] = None
    cvv: Optional[str] = None
    
    # 银行转账字段
    bank_account: Optional[str] = None
    routing_number: Optional[str] = None
    
    # PayPal 字段
    paypal_email: Optional[str] = None

    @root_validator
    def validate_payment_method(cls, values):
        method = values.get('payment_method')
        
        if method == 'credit_card':
            if not values.get('card_number') or not values.get('cvv'):
                raise ValueError('信用卡支付需要提供卡号和CVV')
        
        elif method == 'bank_transfer':
            if not values.get('bank_account') or not values.get('routing_number'):
                raise ValueError('银行转账需要提供账号和路由号')
        
        elif method == 'paypal':
            if not values.get('paypal_email'):
                raise ValueError('PayPal 支付需要提供邮箱')
        
        return values
```

**Zod**：
```typescript
const PaymentRequestSchema = z.discriminatedUnion('paymentMethod', [
  // 信用卡支付
  z.object({
    paymentMethod: z.literal('credit_card'),
    cardNumber: z.string(),
    cvv: z.string(),
  }),
  
  // 银行转账
  z.object({
    paymentMethod: z.literal('bank_transfer'),
    bankAccount: z.string(),
    routingNumber: z.string(),
  }),
  
  // PayPal 支付
  z.object({
    paymentMethod: z.literal('paypal'),
    paypalEmail: z.string().email(),
  }),
]);
```

### 错误响应格式

#### 统一错误格式

```json
{
  "error": "Validation Failed",
  "details": [
    {
      "field": "username",
      "message": "用户名至少3个字符",
      "code": "string_min"
    },
    {
      "field": "email",
      "message": "邮箱格式不正确",
      "code": "string_email"
    }
  ],
  "timestamp": "2026-06-11T10:30:00Z",
  "path": "/api/users"
}
```

#### 实现示例

**FastAPI**：
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from datetime import datetime

app = FastAPI()

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "code": error["type"],
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Failed",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        }
    )
```

**Express**：
```typescript
// middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';

export const errorHandler = (
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  if (error instanceof ZodError) {
    const errors = error.errors.map((err) => ({
      field: err.path.join('.'),
      message: err.message,
      code: err.code,
    }));

    return res.status(422).json({
      error: 'Validation Failed',
      details: errors,
      timestamp: new Date().toISOString(),
      path: req.path,
    });
  }

  // 其他错误
  console.error(error);
  res.status(500).json({
    error: 'Internal Server Error',
    message: process.env.NODE_ENV === 'production' ? '服务器错误' : error.message,
  });
};
```

---

## 成本估算

| 指标 | Pydantic | Zod | Joi |
|------|----------|-----|-----|
| **月成本** | $0 | $0 | $0 |
| **包体积** | 内置（FastAPI） | ~50KB | ~30KB |
| **性能** | 10000+ req/s | 15000+ req/s | 8000+ req/s |
| **学习时间** | 1小时 | 2小时 | 1小时 |
| **维护成本** | 低 | 低 | 低 |

---

## 迁出成本

### 从 Joi 迁出

- **迁出难度**：中
- **迁出步骤**：
  1. 将 Joi Schema 转换为 Zod Schema
  2. 更新验证中间件
  3. 添加 TypeScript 类型定义
  4. 测试所有验证规则

### 从手动验证迁出

- **迁出难度**：低
- **迁出步骤**：
  1. 定义 Schema
  2. 替换手动 if-else 验证
  3. 统一错误响应格式
  4. 添加单元测试

---

## 与其他武器配合

- **前置**：
  - [API 网关](./api-gateway-simple.md) - 统一入口
  - [API 认证](./api-auth-guide.md) - 身份验证

- **后置**：
  - [SQL 注入防护](../free-tier/sql-injection-prevention.md) - 数据库安全
  - [XSS 防护](../free-tier/xss-prevention.md) - 跨站脚本防护

- **替代**：手动验证（不推荐）

- **互补**：
  - [限流](./rate-limiting-simple.md) - 防滥用
  - [API 监控](../saas/api-monitoring.md) - 错误监控

---

## 常见问题

**Q: Pydantic vs Zod vs Joi，怎么选？**

A:
- Python 项目 → Pydantic（FastAPI 默认集成）
- TypeScript 项目 → Zod（类型安全）
- JavaScript 项目 → Joi（经典稳定）

**Q: 验证性能会影响 API 响应时间吗？**

A: 影响极小（<1ms），但建议：
- 简单验证优先
- 复杂验证（如数据库查重）放在业务层
- 使用缓存减少重复验证

**Q: 如何验证文件上传？**

A:
```python
# Pydantic
from pydantic import BaseModel, validator
from fastapi import UploadFile

class FileUpload(BaseModel):
    file: UploadFile

    @validator('file')
    def validate_file(cls, v):
        # 文件类型检查
        allowed_types = ['image/jpeg', 'image/png', 'image/gif']
        if v.content_type not in allowed_types:
            raise ValueError('仅支持 JPG/PNG/GIF 格式')
        
        # 文件大小检查（需要在路由中处理）
        return v
```

```typescript
// Zod
import { z } from 'zod';

const FileUploadSchema = z.object({
  mimetype: z.enum(['image/jpeg', 'image/png', 'image/gif']),
  size: z.number().max(5 * 1024 * 1024, '文件大小不能超过5MB'),
});
```

**Q: 如何处理嵌套对象验证？**

A:
```python
# Pydantic
class Address(BaseModel):
    street: str
    city: str
    zip_code: str

class UserCreate(BaseModel):
    username: str
    address: Address  # 嵌套对象自动验证
```

```typescript
// Zod
const AddressSchema = z.object({
  street: z.string(),
  city: z.string(),
  zipCode: z.string(),
});

const UserCreateSchema = z.object({
  username: z.string(),
  address: AddressSchema, // 嵌套对象自动验证
});
```

---

## 推荐实现

### 完整方案（FastAPI + Pydantic）

```bash
# 安装依赖
pip install fastapi uvicorn pydantic[email]
```

```python
# main.py - 完整示例
from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr, validator, root_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

app = FastAPI(
    title="用户管理 API",
    description="完整的请求验证示例",
    version="1.0.0"
)

# 统一错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "code": error["type"],
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Failed",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path,
        }
    )

# 数据模型
class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class Address(BaseModel):
    street: str = Field(..., min_length=5, max_length=200)
    city: str = Field(..., min_length=2, max_length=100)
    zip_code: str = Field(..., regex=r'^\d{5}(-\d{4})?$')

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        regex="^[a-zA-Z0-9_]+$"
    )
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    age: Optional[int] = Field(None, ge=0, le=150)
    status: UserStatus = UserStatus.active
    address: Optional[Address] = None
    tags: List[str] = Field(default_factory=list, max_items=10)

    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('密码必须包含至少一个大写字母')
        if not any(c.islower() for c in v):
            raise ValueError('密码必须包含至少一个小写字母')
        if not any(c.isdigit() for c in v):
            raise ValueError('密码必须包含至少一个数字')
        return v

    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123",
                "age": 25,
                "status": "active",
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "zip_code": "10001"
                },
                "tags": ["developer", "python"]
            }
        }

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    age: Optional[int]
    status: UserStatus
    address: Optional[Address]
    created_at: datetime

    class Config:
        orm_mode = True

# API 路由
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """创建用户（完整验证）"""
    # 这里模拟数据库操作
    return {
        "id": 1,
        **user.dict(),
        "created_at": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 参考资料

- [Pydantic 官方文档](https://pydantic-docs.helpmanual.io/)
- [Zod 官方文档](https://zod.dev/)
- [Joi 官方文档](https://joi.dev/api/)
- [FastAPI 请求验证](https://fastapi.tiangolo.com/tutorial/body/)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
