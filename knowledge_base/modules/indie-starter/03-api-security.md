# 第 3 周：API 安全

## 概述

本周实施 API 安全措施，保护接口不被滥用。

**预计时间**: 2 小时
**难度**: 中等
**成本**: $0

---

## 核心原则

### API 安全三大原则

1. **认证**: 谁在调用 API
2. **授权**: 能调用什么 API
3. **限流**: 能调用多少次

---

## 认证方式选择

### 认证方式对比

| 方式 | 复杂度 | 安全性 | 适用场景 |
|------|-------|--------|---------|
| API Key | 简单 | 中等 | 内部服务 |
| JWT | 中等 | 高 | 微服务 |
| OAuth2 | 复杂 | 最高 | 第三方授权 |
| Session | 简单 | 中等 | 传统 Web |

### JWT 实现（推荐）

```python
# Python JWT 实现
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv('JWT_SECRET')

def create_token(user_id: str) -> str:
    """创建 JWT"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token: str) -> dict:
    """验证 JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return {'valid': True, 'user_id': payload['user_id']}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}

# 中间件
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        result = verify_token(token)
        if not result['valid']:
            return jsonify({'error': result['error']}), 401
        g.user_id = result['user_id']
        return f(*args, **kwargs)
    return decorated
```

```javascript
// Node.js JWT 实现
const jwt = require('jsonwebtoken');

const SECRET_KEY = process.env.JWT_SECRET;

function createToken(userId) {
    return jwt.sign(
        { userId },
        SECRET_KEY,
        { expiresIn: '1h' }
    );
}

function verifyToken(token) {
    try {
        return jwt.verify(token, SECRET_KEY);
    } catch (error) {
        return null;
    }
}

// 中间件
function authRequired(req, res, next) {
    const auth = req.headers.authorization;
    if (!auth) {
        return res.status(401).json({ error: 'No token provided' });
    }

    const token = auth.replace('Bearer ', '');
    const decoded = verifyToken(token);

    if (!decoded) {
        return res.status(401).json({ error: 'Invalid token' });
    }

    req.userId = decoded.userId;
    next();
}
```

---

## 限流配置

### 分层限流策略

```
用户请求 → CDN 限流 → Nginx 限流 → 应用层限流 → 数据库
```

### 应用层限流

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(app, key_func=get_remote_address)

# 不同接口不同限制
@app.route('/api/public')
@limiter.limit("100/hour")
def public_api():
    pass

@app.route('/api/auth')
@limiter.limit("10/minute")
def auth_api():
    pass

@app.route('/api/admin')
@limiter.limit("30/minute")
def admin_api():
    pass
```

### Redis 分布式限流

```python
import redis
import time

r = redis.Redis()

def rate_limit(key: str, limit: int, window: int) -> bool:
    """
    滑动窗口限流
    key: 限流键
    limit: 限制次数
    window: 时间窗口（秒）
    """
    now = time.time()
    window_start = now - window

    # 使用事务保证原子性
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, window)

    result = pipe.execute()
    count = result[2]

    return count <= limit

# 使用
if not rate_limit(f"rate:{user_id}", 100, 3600):
    return "请求过于频繁", 429
```

---

## 输入验证

### 数据验证库

**Python Pydantic**:
```python
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('密码至少 8 位')
        return v

    @validator('name')
    def name_length(cls, v):
        if len(v) > 50:
            raise ValueError('名称不能超过 50 字符')
        return v

# 使用
@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = UserCreate(**request.json)
        # data.email 已验证为有效邮箱
        # data.password 已验证长度
    except ValidationError as e:
        return jsonify({'errors': e.errors()}), 400
```

**Node.js Zod**:
```javascript
const { z } = require('zod');

const UserCreateSchema = z.object({
    email: z.string().email(),
    password: z.string().min(8).max(128),
    name: z.string().min(1).max(50)
});

// 使用
app.post('/api/users', (req, res) => {
    try {
        const data = UserCreateSchema.parse(req.body);
        // data 已验证
    } catch (error) {
        res.status(400).json({ errors: error.errors });
    }
});
```

### SQL 注入防护

```python
# ❌ 错误做法
sql = f"SELECT * FROM users WHERE id = {user_input}"

# ✅ 正确做法
sql = "SELECT * FROM users WHERE id = ?"
db.execute(sql, user_input)

# 使用 ORM
user = User.query.filter_by(id=user_input).first()
```

---

## 响应过滤

### 字段白名单

```python
# ❌ 直接返回用户对象
@app.route('/api/users/<id>')
def get_user(id):
    user = User.query.get(id)
    return jsonify(user.to_dict())  # 可能包含敏感字段

# ✅ 字段过滤
def user_to_api(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': mask_email(user.email),  # 脱敏
        'created_at': user.created_at.isoformat()
    }

@app.route('/api/users/<id>')
def get_user(id):
    user = User.query.get(id)
    return jsonify(user_to_api(user))
```

---

## 本周实施计划

| 天 | 任务 | 时间 |
|----|------|------|
| Day 1 | JWT 认证实施 | 30 分钟 |
| Day 2 | 应用层限流配置 | 20 分钟 |
| Day 3 | 输入验证实施 | 30 分钟 |
| Day 4 | 响应过滤实施 | 20 分钟 |
| Day 5 | API 安全测试 | 20 分钟 |

---

## 验证清单

- [ ] JWT 认证已实施
- [ ] 应用层限流已配置
- [ ] 输入验证已添加
- [ ] SQL 注入防护已实施
- [ ] 响应字段已过滤
- [ ] API 安全测试通过

---

## 下一步

完成本周任务后，继续 [第 4 周：数据保护](./04-data-protection.md)
