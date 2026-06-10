# API 认证指南

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 2-4小时
- **维护成本**: 1小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
解决 API 接口未授权访问、身份伪造、请求篡改等安全问题，适用于所有对外暴露的 API 服务。

## 认证方式对比

### 快速选型表

| 认证方式 | 实现复杂度 | 安全性评级 | 适用场景 | 免费方案 | 独立开发者推荐度 |
|---------|-----------|-----------|---------|---------|----------------|
| **API Key** | ⭐ 简单 | ⭐⭐ 中等 | 内部服务、微服务间调用 | ✅ 自实现 | ⭐⭐⭐⭐⭐ |
| **JWT** | ⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | 无状态认证、微服务架构 | ✅ PyJWT/jsonwebtoken | ⭐⭐⭐⭐⭐ |
| **OAuth2** | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ 最高 | 第三方登录、公开API | ✅ Authlib/node-oidc-provider | ⭐⭐⭐ |
| **Basic Auth** | ⭐ 最简单 | ⭐ 低 | 仅测试环境、内部工具 | ✅ 自实现 | ⭐⭐ |
| **HMAC签名** | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 最高 | 支付接口、敏感操作 | ✅ 自实现 | ⭐⭐⭐⭐ |

### 详细对比

#### 1. API Key 认证

**优点**：
- 实现简单，5分钟可上线
- 性能开销极低
- 易于撤销和轮换

**缺点**：
- 无法防止重放攻击（需配合时间戳）
- Key 泄露风险高
- 无法做细粒度权限控制

**适用场景**：
- 内部微服务间调用
- 合作伙伴 API 对接
- 低敏感数据接口

**免费方案**：
```python
# 生成 API Key
import secrets

def generate_api_key():
    return f"sk_live_{secrets.token_urlsafe(32)}"

# 存储：key_hash = hashlib.sha256(key.encode()).hexdigest()
# 验证时对比 hash
```

---

#### 2. JWT (JSON Web Token)

**优点**：
- 无状态，服务端不存储 session
- 自包含用户信息和权限
- 支持过期时间和刷新机制
- 跨服务共享认证

**缺点**：
- Token 泄露后难以撤销（需黑名单机制）
- Payload 默认不加密（敏感信息需额外加密）
- Token 较大，每次请求都传输

**适用场景**：
- 前后端分离应用
- 微服务架构
- 移动 App 认证

**免费方案**：
- Python: `PyJWT` 库
- Node.js: `jsonwebtoken` 库
- Go: `golang-jwt/jwt` 库

---

#### 3. OAuth2

**优点**：
- 行业标准协议
- 支持授权码、客户端凭证等多种模式
- 细粒度权限控制（Scope）
- 用户无需共享密码给第三方

**缺点**：
- 实现复杂，需要授权服务器
- 多次网络往返，性能开销
- 需要维护 refresh token

**适用场景**：
- 第三方登录（微信、GitHub 登录）
- 开放 API 平台
- SaaS 产品集成

**免费方案**：
- 自建：Keycloak（开源）、Authlib（Python）
- 云服务：Supabase Auth（免费额度大）、Clerk（免费 5000 MAU）

---

#### 4. Basic Auth

**优点**：
- 实现最简单
- 所有 HTTP 客户端原生支持
- 调试方便

**缺点**：
- 每次请求都传输密码（需 HTTPS）
- 无法做细粒度权限
- 密码泄露风险高
- 无过期机制

**适用场景**：
- 仅限测试环境
- 内部管理工具
- 快速原型验证

**免费方案**：
```python
# FastAPI 示例
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

async def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    # 验证用户名密码
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Basic"})
    return credentials.username
```

---

#### 5. HMAC 签名认证

**优点**：
- 防篡改、防重放
- 密钥不传输，安全性高
- 可验证请求完整性

**缺点**：
- 实现较复杂
- 时间戳同步要求
- 调试不便

**适用场景**：
- 支付接口
- 敏感操作验证
- API 网关鉴权

**免费方案**：
- 完全自实现，无依赖

---

## 快速上手（5分钟）

### 方案一：API Key 中间件（Node.js）

```javascript
// api-key-middleware.js
const crypto = require('crypto');

// 模拟数据库存储
const apiKeys = new Map([
  ['sk_live_abc123', { userId: 'user_001', scopes: ['read', 'write'] }],
  ['sk_live_xyz789', { userId: 'user_002', scopes: ['read'] }],
]);

function apiKeyMiddleware(req, res, next) {
  const apiKey = req.headers['x-api-key'];

  if (!apiKey) {
    return res.status(401).json({ error: 'API Key required' });
  }

  const keyData = apiKeys.get(apiKey);
  if (!keyData) {
    return res.status(401).json({ error: 'Invalid API Key' });
  }

  // 权限检查
  const requiredScope = req.method === 'GET' ? 'read' : 'write';
  if (!keyData.scopes.includes(requiredScope)) {
    return res.status(403).json({ error: 'Insufficient permissions' });
  }

  req.user = keyData;
  next();
}

// 使用示例
// app.use('/api', apiKeyMiddleware);

module.exports = { apiKeyMiddleware, generateApiKey };

function generateApiKey() {
  const key = crypto.randomBytes(32).toString('base64url');
  return `sk_live_${key}`;
}
```

### 方案二：JWT 生成和验证（Python）

```python
# jwt_auth.py
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "your-secret-key-change-in-production"  # 环境变量中配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_id: str, scopes: list = None) -> str:
    """生成 JWT Token"""
    payload = {
        "sub": user_id,
        "scopes": scopes or [],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """验证并解码 JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def jwt_required(f):
    """JWT 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header required"}), 401

        token = auth_header.split(' ')[1]
        try:
            user_data = decode_token(token)
            request.user = user_data
        except ValueError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)
    return decorated

# 使用示例
# @app.route('/api/protected')
# @jwt_required
# def protected():
#     return jsonify({"user": request.user})
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
│                    API 网关 / 中间件                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ API Key 检查  │  │ JWT 验证     │  │ HMAC 签名验证 │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                            │                                     │
│                    通过 → 转发请求                                │
│                    失败 → 401/403                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      业务服务层                                   │
│  - 获取用户身份信息                                               │
│  - 执行权限检查                                                   │
│  - 处理业务逻辑                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### HMAC 签名实现

```python
# hmac_auth.py
import hmac
import hashlib
import time
from urllib.parse import urlparse

class HMACAuth:
    """
    HMAC 签名认证实现

    签名流程：
    1. 拼接签名字符串：METHOD + URL + TIMESTAMP + BODY
    2. 使用 HMAC-SHA256 计算签名
    3. 将签名放入 Header
    """

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode('utf-8')

    def sign_request(
        self,
        method: str,
        url: str,
        body: str = "",
        timestamp: int = None
    ) -> dict:
        """生成请求签名"""
        timestamp = timestamp or int(time.time())

        # 拼接签名字符串
        string_to_sign = f"{method.upper()}\n{url}\n{timestamp}\n{body}"

        # 计算签名
        signature = hmac.new(
            self.secret_key,
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return {
            "X-Timestamp": str(timestamp),
            "X-Signature": signature,
        }

    def verify_request(
        self,
        method: str,
        url: str,
        timestamp: int,
        signature: str,
        body: str = "",
        tolerance_seconds: int = 300
    ) -> bool:
        """验证请求签名"""

        # 1. 时间戳检查（防重放）
        current_time = int(time.time())
        if abs(current_time - timestamp) > tolerance_seconds:
            raise ValueError("Request expired")

        # 2. 签名验证
        expected = self.sign_request(method, url, body, timestamp)
        expected_sig = expected["X-Signature"]

        if not hmac.compare_digest(signature, expected_sig):
            raise ValueError("Invalid signature")

        return True

# 使用示例
"""
# 客户端
auth = HMACAuth("your-secret-key")
headers = auth.sign_request("POST", "/api/payment", '{"amount": 100}')
# 发送请求时带上 headers['X-Timestamp'] 和 headers['X-Signature']

# 服务端
@verify_hmac
def handle_payment():
    # 签名验证通过后执行业务逻辑
    pass
"""
```

### OAuth2 集成示例

```python
# oauth2_provider.py
from authlib.integrations.flask_oauth2 import AuthorizationServer
from authlib.integrations.sqla_oauth2 import (
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
    OAuth2ClientMixin,
)
from flask import Flask
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# OAuth2 数据模型
class OAuth2Client(Base, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)

class OAuth2AuthorizationCode(Base, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)

class OAuth2Token(Base, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)

# Flask OAuth2 服务器配置
app = Flask(__name__)

def query_client(client_id):
    return OAuth2Client.query.filter_by(client_id=client_id).first()

def save_token(token_data, request):
    token = OAuth2Token(
        client_id=request.client.client_id,
        user_id=request.user.id,
        **token_data
    )
    db.session.add(token)
    db.session.commit()

authorization = AuthorizationServer(
    app,
    query_client=query_client,
    save_token=save_token,
)

# 授权端点
@app.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    # 用户授权确认
    pass

@app.route('/oauth/token', methods=['POST'])
def issue_token():
    return authorization.create_token_response()

# 资源保护
from authlib.integrations.flask_oauth2 import ResourceProtector
require_oauth = ResourceProtector()

@app.route('/api/user')
@require_oauth('profile')
def user_profile():
    user = current_token.user
    return jsonify(user.to_dict())
```

---

## 安全最佳实践

### 1. 通用原则

- ✅ **始终使用 HTTPS**：所有认证信息传输必须加密
- ✅ **密钥安全存储**：使用环境变量或密钥管理服务
- ✅ **最小权限原则**：仅授予必需的 scope
- ✅ **定期轮换密钥**：建议每 90 天轮换一次 API Key
- ✅ **日志审计**：记录所有认证失败事件

### 2. JWT 安全

```python
# ✅ 正确做法
payload = {
    "sub": user_id,
    "exp": datetime.utcnow() + timedelta(minutes=15),  # 短有效期
    "iat": datetime.utcnow(),
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# ❌ 错误做法
payload = {
    "sub": user_id,
    "exp": datetime.utcnow() + timedelta(days=365),  # 过长
}
token = jwt.encode(payload, "password123", algorithm="none")  # 无签名
```

### 3. 防重放攻击

```python
# 使用 nonce 和时间戳
def verify_request_with_nonce(nonce: str, timestamp: int, max_age: int = 300):
    # 1. 检查时间戳
    if abs(time.time() - timestamp) > max_age:
        raise ValueError("Request expired")

    # 2. 检查 nonce 是否已使用（Redis）
    if redis_client.exists(f"nonce:{nonce}"):
        raise ValueError("Duplicate request")

    # 3. 记录 nonce（5分钟过期）
    redis_client.setex(f"nonce:{nonce}", max_age, "1")
```

### 4. API Key 安全

```python
# ✅ 正确：存储 hash，验证时对比
import hashlib

def store_api_key(key: str) -> str:
    """存储 API Key 的 hash 值"""
    return hashlib.sha256(key.encode()).hexdigest()

def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """验证 API Key"""
    return hmac.compare_digest(
        hashlib.sha256(provided_key.encode()).hexdigest(),
        stored_hash
    )

# ❌ 错误：明文存储
# database.save(api_key)  # 危险！
```

---

## 成本估算

| 指标 | 自建方案 | 云服务方案 |
|------|---------|----------|
| **月成本** | $0（服务器费用除外） | $0-100/月 |
| **性能** | 1000+ req/s | 取决于套餐 |
| **功能** | 基础认证 | 完整身份管理 |
| **维护时间** | 2-4小时/月 | 0小时 |
| **可靠性** | 需自建高可用 | SLA 保证 |

### 免费方案推荐

| 服务 | 免费额度 | 特点 |
|------|---------|------|
| **Supabase Auth** | 50,000 MAU | JWT + OAuth + Row Level Security |
| **Clerk** | 5,000 MAU | 完整用户管理 + UI 组件 |
| **Auth0** | 7,000 MAU | 企业级，功能最全 |
| **Firebase Auth** | 无限制 | Google 生态集成 |

---

## 迁出成本

### 从 Basic Auth 迁出

- **迁出难度**：低
- **迁出步骤**：
  1. 新增 JWT/OAuth2 端点
  2. 前端同时支持两种认证
  3. 逐步迁移用户
  4. 下线 Basic Auth

### 从 API Key 迁出

- **迁出难度**：中
- **迁出步骤**：
  1. 为现有用户生成 JWT refresh token
  2. 客户端换取 access token
  3. 设置过渡期（30天）
  4. 强制切换

### 从自建 OAuth2 迁出

- **迁出难度**：高
- **迁出步骤**：
  1. 导出现有 token 和 client 数据
  2. 配置新服务商
  3. 数据迁移和验证
  4. 更新回调 URL
  5. 用户重新授权

---

## 与其他武器配合

- **前置**：HTTPS（必需）、API 网关（可选）
- **后置**：Rate Limiting（限流）、Audit Logging（审计日志）
- **替代**：无（认证是必需的）
- **互补**：
  - [API Rate Limiting](./api-rate-limit.md) - 防滥用
  - [Security Headers](./security-headers.md) - 防护层
  - [Secrets Management](./secrets-management.md) - 密钥管理

---

## 常见问题

**Q: API Key vs JWT，怎么选？**

A:
- 内部服务、微服务 → API Key
- 用户认证、跨服务 → JWT
- 第三方登录 → OAuth2

**Q: JWT 泄露了怎么办？**

A:
1. 短有效期（15分钟）+ Refresh Token
2. 维护黑名单（Redis）
3. 紧急情况：更换 SECRET_KEY，所有用户重新登录

**Q: 如何处理多设备登录？**

A:
```python
# 方案1：JWT payload 包含 device_id
payload = {"sub": user_id, "device_id": device_id, ...}

# 方案2：服务端维护 session 表
# session_id, user_id, device_info, last_active, is_active
```

**Q: 移动端如何安全存储 Token？**

A:
- iOS: Keychain Services
- Android: EncryptedSharedPreferences (Jetpack Security)
- 勿存：SharedPreferences、UserDefaults、LocalStorage

---

## 推荐实现

### 完整方案（Python）

```bash
# 安装依赖
pip install pyjwt passlib python-multipart
```

```python
# auth_system.py - 完整示例
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# 配置
SECRET_KEY = "change-this-to-a-random-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# 模拟用户数据库
fake_users_db = {
    "alice": {
        "username": "alice",
        "hashed_password": pwd_context.hash("password123"),
        "scopes": ["read", "write"],
    },
    "bob": {
        "username": "bob",
        "hashed_password": pwd_context.hash("password456"),
        "scopes": ["read"],
    },
}

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    scopes: list[str] = []

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception
    return User(username=username, scopes=user["scopes"])

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or not pwd_context.verify(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user["username"], "scopes": user["scopes"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}

@app.get("/api/protected")
async def protected_endpoint(user: User = Depends(get_current_user)):
    return {"message": f"Hello {user.username}", "scopes": user.scopes}

@app.get("/api/admin")
async def admin_endpoint(user: User = Depends(get_current_user)):
    if "write" not in user.scopes:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return {"message": "Admin access granted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 完整方案（Node.js）

```javascript
// server.js - Express + JWT 完整示例
const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { body, validationResult } = require('express-validator');

const app = express();
app.use(express.json());

// 配置
const JWT_SECRET = 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = '30m';

// 模拟用户数据库
const users = new Map([
  ['alice', { password: bcrypt.hashSync('password123', 10), scopes: ['read', 'write'] }],
  ['bob', { password: bcrypt.hashSync('password456', 10), scopes: ['read'] }],
]);

// 认证中间件
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader?.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'Token required' });
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid or expired token' });
    }
    req.user = user;
    next();
  });
}

// 权限中间件
function requireScope(scope) {
  return (req, res, next) => {
    if (!req.user.scopes.includes(scope)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
}

// 路由
app.post('/auth/login',
  body('username').notEmpty(),
  body('password').notEmpty(),
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const { username, password } = req.body;
    const user = users.get(username);

    if (!user || !bcrypt.compareSync(password, user.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
      { sub: username, scopes: user.scopes },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );

    res.json({ access_token: token, token_type: 'bearer' });
  }
);

app.get('/api/public', (req, res) => {
  res.json({ message: 'This is a public endpoint' });
});

app.get('/api/protected', authenticateToken, (req, res) => {
  res.json({ message: `Hello ${req.user.sub}`, scopes: req.user.scopes });
});

app.get('/api/admin', authenticateToken, requireScope('write'), (req, res) => {
  res.json({ message: 'Admin access granted' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

---

## 测试验证

### API Key 测试

```bash
# 正确请求
curl -H "X-API-Key: sk_live_abc123" http://localhost:3000/api/data

# 无 Key
curl http://localhost:3000/api/data  # 期望 401

# 错误 Key
curl -H "X-API-Key: invalid" http://localhost:3000/api/data  # 期望 401
```

### JWT 测试

```bash
# 登录获取 token
TOKEN=$(curl -s -X POST http://localhost:8000/token \
  -d "username=alice&password=password123" | jq -r .access_token)

# 使用 token 访问
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/protected

# 过期 token
curl -H "Authorization: Bearer expired.token.here" http://localhost:8000/api/protected  # 期望 401
```

---

## 参考资料

- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 7519 - JSON Web Token](https://datatracker.ietf.org/doc/html/rfc7519)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [jsonwebtoken (Node.js)](https://github.com/auth0/node-jsonwebtoken)
