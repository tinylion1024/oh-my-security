# JWT 攻击（JWT Attack）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
JWT配置不当（如允许 `alg=none`、密钥过弱、未验证签名），攻击者可伪造令牌绕过认证，完全接管任意用户账号。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用JWT进行认证（Authorization: Bearer xxx）
- [ ] 未设置JWT签名密钥或使用弱密钥（如"secret"、"123456"）
- [ ] 未验证JWT签名算法（可能被改为 `none`）
- [ ] JWT未设置有效期（exp字段）或有效期过长（超过24小时）
- [ ] 敏感信息存储在JWT payload中（如密码、权限）
→ 勾选≥1项，即需立即关注此风险

### 一句话防御
使用强密钥（256位以上）+ 强制验证签名算法 + 设置合理有效期（15分钟-2小时）+ 不存储敏感信息。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查JWT配置：密钥长度≥32字节，算法固定为RS256或HS256
   - [ ] 禁用 `alg=none`：在验证时拒绝无签名Token
   - [ ] 设置有效期：access token 15分钟-2小时，refresh token 7天
   - [ ] 验证签名：确保verify()时强制检查算法

2. **短期行动**（本周可完成，免费）
   - [ ] 实现刷新令牌机制：access token短期 + refresh token长期
   - [ ] 添加JWT黑名单：用于登出和令牌撤销
   - [ ] 检查payload：移除敏感信息（密码、权限改为从数据库查询）
   - [ ] 测试：尝试使用无签名Token访问接口

3. **长期行动**（规划中，免费）
   - [ ] 升级到非对称加密（RS256/ES256）
   - [ ] 实现密钥轮换机制
   - [ ] 集成JWT监控和告警

### 推荐工具
- **免费**：
  - [jwt.io](https://jwt.io/) - JWT调试工具（检查payload和签名）
  - [jsonwebtoken](https://github.com/auth0/node-jsonwebtoken) - Node.js JWT库
  - [PyJWT](https://github.com/jpadilla/pyjwt) - Python JWT库

- **低成本**：
  - [Auth0](https://auth0.com/) - 免费额度7000活跃用户/月，托管JWT
  - [Supabase Auth](https://supabase.com/auth) - 免费50000活跃用户/月

### 验证方法
- [ ] 测试步骤1：修改JWT alg为"none"，尝试访问接口（应被拒绝）
- [ ] 测试步骤2：检查JWT有效期，确认exp字段存在且合理
- [ ] 测试步骤3：使用jwt.io解码JWT，确认无敏感信息
- [ ] 测试步骤4：尝试使用过期JWT访问接口（应返回401）

---

## L2 小团队版（理解版）

### 场景还原
你的API使用JWT进行认证，某天发现异常流量：

**案例1：alg=none 攻击**
- 开发时为了方便调试，未严格验证签名算法
- 攻击者修改JWT header：`{"alg":"none"}` 并删除签名
- 服务端接受无签名Token，攻击者伪造管理员身份
- 获取所有用户数据并删除数据库

**案例2：弱密钥破解**
- JWT使用默认密钥"secret123"
- 攻击者使用工具（如hashcat）暴力破解密钥
- 破解成功后伪造任意用户Token
- 修改用户数据、发起恶意交易

**案例3：JWT泄露**
- JWT有效期设置为30天
- 攻击者通过XSS漏洞窃取用户JWT
- 使用JWT长期访问用户账号，即使密码已修改
- 用户修改密码后JWT仍然有效

你的服务器日志显示：
```
[2026-06-10 10:22:15] GET /api/admin/users - Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0...
[2026-06-10 10:22:15] ERROR: Invalid signature (但请求仍然成功)
[2026-06-10 10:23:30] DELETE /api/users/all - 5000 users deleted
```

### 攻击路径（简化版）

**路径1：alg=none 攻击**
1. 攻击者获取合法JWT（通过注册或抓包）
2. 解码JWT，修改payload（如将role改为admin）
3. 修改header：`{"alg":"none","typ":"JWT"}`
4. 删除签名部分，保留header.payload
5. 服务端未严格验证算法，接受无签名Token
6. 攻击者以管理员身份访问系统

**路径2：弱密钥暴力破解**
1. 攻击者获取一个合法JWT
2. 使用字典攻击或暴力破解工具
3. 常见弱密钥：secret、123456、password、admin
4. 破解成功后可签名任意JWT
5. 伪造管理员或任意用户Token

**路径3：JWT长期有效**
1. 攻击者通过XSS或中间人攻击窃取JWT
2. JWT有效期30天，无需重新认证
3. 即使受害者修改密码，JWT仍然有效
4. 攻击者持续访问受害者账号

**路径4：密钥泄露**
1. 开发者将密钥硬编码在代码中
2. 代码上传到GitHub公开仓库
3. 攻击者从代码库中找到密钥
4. 使用密钥签名任意JWT

### 防御实施（免费方案）

#### JWT安全配置清单

```typescript
// lib/jwt-security.ts
import jwt from 'jsonwebtoken'

/**
 * JWT安全配置清单
 */
export const JWTSecurityConfig = {
  // ✅ 1. 使用强密钥（至少256位）
  // 生成强密钥: node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
  secret: process.env.JWT_SECRET, // 必须从环境变量读取

  // ✅ 2. 强制算法
  algorithms: ['RS256', 'HS256'], // 只接受这两种算法

  // ✅ 3. 设置有效期
  accessTokenExpiry: '15m', // access token: 15分钟
  refreshTokenExpiry: '7d',  // refresh token: 7天

  // ✅ 4. 签发者验证
  issuer: 'your-app-name',

  // ✅ 5. 受众验证
  audience: 'your-app-users',

  // ❌ 不存储敏感信息
  // payload中不应包含：密码、权限、敏感数据
}

/**
 * 安全的JWT签名
 */
export class SecureJWT {
  private static secret = process.env.JWT_SECRET!
  private static algorithm = 'HS256'

  /**
   * 生成access token（短期）
   */
  static signAccessToken(payload: object): string {
    return jwt.sign(
      {
        ...payload,
        // 标准字段
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (15 * 60), // 15分钟
        iss: JWTSecurityConfig.issuer,
        aud: JWTSecurityConfig.audience,
      },
      this.secret,
      {
        algorithm: this.algorithm, // 强制算法
      }
    )
  }

  /**
   * 生成refresh token（长期）
   */
  static signRefreshToken(userId: string): string {
    return jwt.sign(
      {
        userId,
        type: 'refresh',
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (7 * 24 * 60 * 60), // 7天
      },
      this.secret,
      {
        algorithm: this.algorithm,
      }
    )
  }

  /**
   * 验证JWT - 关键安全检查
   */
  static verify(token: string): any {
    try {
      // ✅ 关键：强制指定算法，不接受alg=none
      const decoded = jwt.verify(token, this.secret, {
        algorithms: [this.algorithm], // 只接受指定算法
        issuer: JWTSecurityConfig.issuer,
        audience: JWTSecurityConfig.audience,
      })

      return {
        valid: true,
        payload: decoded,
      }
    } catch (error) {
      return {
        valid: false,
        error: error.message,
      }
    }
  }

  /**
   * 解码JWT（不验证签名，仅用于调试）
   */
  static decode(token: string): any {
    return jwt.decode(token, { complete: true })
  }
}
```

#### JWT验证中间件

```typescript
// middleware/jwt-auth.ts
import { NextRequest, NextResponse } from 'next/server'
import { SecureJWT } from '@/lib/jwt-security'

/**
 * JWT认证中间件
 */
export async function jwtAuthMiddleware(request: NextRequest) {
  const authHeader = request.headers.get('authorization')

  // 检查Authorization头
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return NextResponse.json(
      { error: '未提供认证令牌' },
      { status: 401 }
    )
  }

  const token = authHeader.substring(7) // 去掉"Bearer "

  // ✅ 关键：验证JWT
  const result = SecureJWT.verify(token)

  if (!result.valid) {
    return NextResponse.json(
      { error: '令牌无效或已过期', details: result.error },
      { status: 401 }
    )
  }

  // 检查黑名单（用于登出）
  const isBlacklisted = await checkTokenBlacklist(token)
  if (isBlacklisted) {
    return NextResponse.json(
      { error: '令牌已失效' },
      { status: 401 }
    )
  }

  // 将用户信息添加到请求中
  request.headers.set('x-user-id', result.payload.userId)
  request.headers.set('x-user-role', result.payload.role)

  return null // 继续处理请求
}

/**
 * 检查Token黑名单
 */
async function checkTokenBlacklist(token: string): Promise<boolean> {
  // 使用Redis存储黑名单
  // const redis = new Redis(process.env.REDIS_URL)
  // return await redis.sismember('jwt:blacklist', token)
  return false
}
```

#### 完整认证流程

```typescript
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { SecureJWT } from '@/lib/jwt-security'
import { UserDB } from '@/lib/db'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // 验证用户凭据
    const user = await UserDB.findByEmail(email)
    if (!user || !user.verifyPassword(password)) {
      return NextResponse.json(
        { error: '邮箱或密码错误' },
        { status: 401 }
      )
    }

    // ✅ 生成JWT（不存储敏感信息）
    const accessToken = SecureJWT.signAccessToken({
      userId: user.id,
      email: user.email,
      // ❌ 不要存储敏感信息：密码、权限等
    })

    const refreshToken = SecureJWT.signRefreshToken(user.id)

    // 存储refresh token到数据库（用于撤销）
    await UserDB.storeRefreshToken(user.id, refreshToken)

    return NextResponse.json({
      accessToken,
      refreshToken,
      expiresIn: 900, // 秒
      tokenType: 'Bearer',
    })
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: '登录失败' },
      { status: 500 }
    )
  }
}

// app/api/auth/refresh/route.ts
export async function POST(request: NextRequest) {
  try {
    const { refreshToken } = await request.json()

    // 验证refresh token
    const result = SecureJWT.verify(refreshToken)
    if (!result.valid || result.payload.type !== 'refresh') {
      return NextResponse.json(
        { error: '无效的刷新令牌' },
        { status: 401 }
      )
    }

    // 检查refresh token是否在数据库中
    const isValid = await UserDB.verifyRefreshToken(
      result.payload.userId,
      refreshToken
    )
    if (!isValid) {
      return NextResponse.json(
        { error: '刷新令牌已失效' },
        { status: 401 }
      )
    }

    // 生成新的access token
    const accessToken = SecureJWT.signAccessToken({
      userId: result.payload.userId,
    })

    return NextResponse.json({
      accessToken,
      expiresIn: 900,
    })
  } catch (error) {
    console.error('Refresh error:', error)
    return NextResponse.json(
      { error: '刷新失败' },
      { status: 500 }
    )
  }
}

// app/api/auth/logout/route.ts
export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get('authorization')
    const token = authHeader?.substring(7)

    // 将token加入黑名单
    if (token) {
      await addToBlacklist(token)
    }

    // 撤销所有refresh token
    const userId = request.headers.get('x-user-id')
    if (userId) {
      await UserDB.revokeRefreshTokens(userId)
    }

    return NextResponse.json({
      success: true,
      message: '已登出',
    })
  } catch (error) {
    console.error('Logout error:', error)
    return NextResponse.json(
      { error: '登出失败' },
      { status: 500 }
    )
  }
}

async function addToBlacklist(token: string) {
  // 使用Redis存储黑名单，有效期与token一致
  // const redis = new Redis(process.env.REDIS_URL)
  // const decoded = jwt.decode(token)
  // const ttl = decoded.exp - Math.floor(Date.now() / 1000)
  // await redis.setex(`blacklist:${token}`, ttl, '1')
}
```

#### 密钥管理最佳实践

```bash
# .env（不要提交到Git）
JWT_SECRET=your-very-strong-secret-key-at-least-32-characters-long

# 生成强密钥
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
# 输出示例: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

# .gitignore
.env
.env.local
.env.*.local
```

```typescript
// lib/key-rotation.ts
/**
 * JWT密钥轮换
 */
export class KeyRotation {
  private static keys = new Map<string, string>()

  /**
   * 加载密钥（支持多个密钥用于轮换）
   */
  static loadKeys() {
    // 主密钥
    this.keys.set('primary', process.env.JWT_SECRET!)

    // 历史密钥（用于验证旧Token）
    if (process.env.JWT_SECRET_OLD) {
      this.keys.set('old', process.env.JWT_SECRET_OLD)
    }
  }

  /**
   * 验证Token（尝试所有密钥）
   */
  static verify(token: string): any {
    for (const [name, secret] of this.keys.entries()) {
      try {
        const decoded = jwt.verify(token, secret, {
          algorithms: ['HS256'],
        })

        return {
          valid: true,
          payload: decoded,
          keyUsed: name,
        }
      } catch (error) {
        // 继续尝试下一个密钥
        continue
      }
    }

    return {
      valid: false,
      error: '所有密钥验证失败',
    }
  }

  /**
   * 轮换密钥
   */
  static rotate(newSecret: string) {
    // 将当前主密钥降级为历史密钥
    const currentPrimary = this.keys.get('primary')
    if (currentPrimary) {
      this.keys.set('old', currentPrimary)
      process.env.JWT_SECRET_OLD = currentPrimary
    }

    // 设置新主密钥
    this.keys.set('primary', newSecret)
    process.env.JWT_SECRET = newSecret

    console.log('密钥轮换完成')
  }
}
```

---

### 决策树

```
你的JWT是否已经配置？
├── 否 → 立即配置（使用强密钥 + 强制算法 + 有效期）
└── 是 →
    是否验证签名算法？
    ├── 否 → 立即修复：在verify()时指定algorithms
    └── 是 →
        密钥强度是否足够（≥32字节）？
        ├── 否 → 立即更换强密钥
        └── 是 →
            有效期是否合理（≤2小时）？
            ├── 否 → 缩短有效期，实现refresh token
            └── 是 → 基本安全

是否处理敏感数据？
├── 是 → 考虑升级到非对称加密（RS256）
└── 否 → 对称加密（HS256）足够
```

---

### 完整代码示例

**Python实现（Flask）**

```python
# lib/jwt_security.py
import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class JWTSecurity:
    """
    JWT安全配置 - Python实现
    """

    def __init__(self):
        # 从环境变量读取密钥
        self.secret = os.getenv('JWT_SECRET')
        if not self.secret or len(self.secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")

        self.algorithm = 'HS256'
        self.access_token_expiry = 15  # 分钟
        self.refresh_token_expiry = 7  # 天
        self.issuer = 'your-app-name'

    def sign_access_token(self, payload: Dict[str, Any]) -> str:
        """生成access token"""
        now = datetime.utcnow()

        token_payload = {
            **payload,
            'iat': now,
            'exp': now + timedelta(minutes=self.access_token_expiry),
            'iss': self.issuer,
            'type': 'access'
        }

        return jwt.encode(
            token_payload,
            self.secret,
            algorithm=self.algorithm
        )

    def sign_refresh_token(self, user_id: str) -> str:
        """生成refresh token"""
        now = datetime.utcnow()

        token_payload = {
            'userId': user_id,
            'iat': now,
            'exp': now + timedelta(days=self.refresh_token_expiry),
            'type': 'refresh'
        }

        return jwt.encode(
            token_payload,
            self.secret,
            algorithm=self.algorithm
        )

    def verify(self, token: str) -> Dict[str, Any]:
        """
        验证JWT - 关键安全检查
        """
        try:
            # ✅ 关键：强制指定算法
            decoded = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],  # 只接受指定算法
                issuer=self.issuer,
                options={
                    'verify_exp': True,  # 验证过期时间
                    'verify_iat': True,  # 验证签发时间
                    'require': ['exp', 'iat', 'userId']  # 必需字段
                }
            )

            return {
                'valid': True,
                'payload': decoded
            }

        except jwt.ExpiredSignatureError:
            return {
                'valid': False,
                'error': '令牌已过期'
            }
        except jwt.InvalidAlgorithmError:
            return {
                'valid': False,
                'error': '无效的算法'
            }
        except jwt.InvalidSignatureError:
            return {
                'valid': False,
                'error': '无效的签名'
            }
        except jwt.InvalidTokenError as e:
            return {
                'valid': False,
                'error': f'无效的令牌: {str(e)}'
            }

    def decode_without_verify(self, token: str) -> Dict[str, Any]:
        """解码JWT（不验证签名，仅用于调试）"""
        try:
            return jwt.decode(
                token,
                options={'verify_signature': False}
            )
        except:
            return {}


# Flask中间件
from functools import wraps
from flask import request, jsonify

jwt_security = JWTSecurity()

def jwt_required(f):
    """JWT认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'error': '未提供认证令牌'
            }), 401

        token = auth_header.split(' ')[1]
        result = jwt_security.verify(token)

        if not result['valid']:
            return jsonify({
                'error': result['error']
            }), 401

        # 将用户信息传递给路由
        request.current_user = result['payload']

        return f(*args, **kwargs)

    return decorated_function


# Flask路由示例
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/auth/login', methods=['POST'])
def login():
    """登录接口"""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # 验证用户（这里应该查询数据库）
    user = authenticate_user(email, password)

    if not user:
        return jsonify({'error': '邮箱或密码错误'}), 401

    # 生成JWT
    access_token = jwt_security.sign_access_token({
        'userId': user['id'],
        'email': user['email']
    })

    refresh_token = jwt_security.sign_refresh_token(user['id'])

    return jsonify({
        'accessToken': access_token,
        'refreshToken': refresh_token,
        'expiresIn': 900
    })


@app.route('/api/protected', methods=['GET'])
@jwt_required
def protected_route():
    """受保护的路由"""
    return jsonify({
        'message': '访问成功',
        'user': request.current_user
    })


def authenticate_user(email, password):
    """验证用户（示例）"""
    # 实际应查询数据库
    if email == 'test@example.com' and password == 'password':
        return {'id': '1', 'email': email}
    return None
```

---

## L3 企业版（深耕版）

企业级JWT安全需要更完善的体系：

**1. 高级加密方案**
- 非对称加密（RS256/ES256）
- 密钥管理系统（KMS）
- 密钥自动轮换

**2. 完整令牌管理**
- 令牌撤销机制
- 令牌黑名单
- 令牌刷新策略

**3. 监控和告警**
- 异常令牌检测
- 令牌使用分析
- 安全事件审计

**详细内容请参考企业级案例**：
- [企业级JWT安全方案](../../enterprise/bizsec/auth/jwt-security-enterprise.md)
- [密钥管理最佳实践](../../enterprise/infosec/key-management.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基础配置 | $0 | 1小时 | 0.5小时/月 | MVP阶段 |
| L2-完整方案 | $0 | 4小时 | 1小时/月 | 生产环境 |
| L3-企业级 | $50+ | 需评估 | 专职团队 | 金融、医疗 |

---

## 常见问题

**Q: JWT应该存储在localStorage还是Cookie？**
A: 推荐使用HttpOnly Cookie，防止XSS攻击。如果使用localStorage，确保实施严格的CSP策略。

**Q: access token有效期应该多长？**
A: 建议15分钟-2小时。结合refresh token实现无感刷新。

**Q: 如何实现JWT撤销？**
A: 使用黑名单（Redis存储）或维护Token版本号（存储在数据库中）。

**Q: 对称加密还是非对称加密？**
A: 小型项目用HS256（对称）足够。需要第三方验证或高安全场景用RS256（非对称）。

---

## 相关资源

**工具**
- [jwt.io](https://jwt.io/) - JWT调试工具
- [jsonwebtoken](https://github.com/auth0/node-jsonwebtoken) - Node.js库
- [PyJWT](https://github.com/jpadilla/pyjwt) - Python库

**学习资源**
- [JWT.io Introduction](https://jwt.io/introduction)
- [OWASP JWT Security](https://owasp.org/www-community/vulnerabilities/JSON_Web_Token_(JWT)_Cheat_Sheet_for_Java)
- [RFC 7519](https://tools.ietf.org/html/rfc7519)

**相关案例**
- [Session劫持](./session-hijacking.md)
- [账号接管](./account-takeover.md)
- [API认证漏洞](./api-authentication-vulnerability.md)
