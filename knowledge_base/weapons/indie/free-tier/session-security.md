# Session 安全武器文档

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防 + 检测
- **实现成本**: 免费
- **实施时间**: 2-4小时
- **维护成本**: 30分钟/月
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## 适用场景
为独立开发者提供完整的 Session 安全方案，涵盖配置安全、存储方案、防劫持、多设备管理、安全登出等核心场景。适用于 Web 应用、API 服务、SPA 单页应用等多种架构。

---

## 快速上手（总览）

```
Session 安全架构
├── Session 配置安全
│   ├── 安全 Cookie 设置
│   ├── Session ID 强度
│   └── 过期策略
├── 存储方案选择
│   ├── 内存存储（开发）
│   ├── Redis 存储（生产推荐）
│   └── 数据库存储（持久化）
├── 攻击防护
│   ├── Session 固定攻击
│   ├── Session 劫持
│   └── CSRF 防护
└── 会话管理
    ├── 多设备管理
    ├── 安全登出
    └── 异常检测
```

---

## 详细方案

### 1. Session vs JWT 对比

#### 架构对比

```
Session 方案：
客户端 ←→ 服务端（存储 Session）
         ↓
    Session Store（内存/Redis/DB）

JWT 方案：
客户端 ←→ 服务端（无状态验证）
   ↓
  Token（自包含）
```

#### 详细对比表

| 特性 | Session | JWT |
|------|---------|-----|
| **存储位置** | 服务端 | 客户端 |
| **状态** | 有状态 | 无状态 |
| **扩展性** | 需共享存储 | 天然分布式 |
| **安全性** | 可即时撤销 | 难以撤销 |
| **带宽消耗** | 低（仅 Session ID） | 高（完整 Token） |
| **实现复杂度** | 中等 | 简单 |
| **适用场景** | 传统 Web、敏感操作 | API、微服务、SSO |
| **续期机制** | 自动续期 | 需 Refresh Token |

#### 选择建议

```
选择 Session 的场景：
├── 需要即时撤销会话（支付、管理后台）
├── 敏感操作频繁（银行、医疗）
├── 需要服务端会话状态跟踪
├── 传统多页应用
└── 需要防止 Token 泄露后的长期风险

选择 JWT 的场景：
├── 无状态 API 服务
├── 微服务架构
├── 移动应用
├── 第三方授权（SSO）
└── 对服务端存储敏感
```

---

### 2. Session 配置安全

#### Flask Session 安全配置

```python
# flask_session_config.py
from flask import Flask, session
from flask_session import Session  # 需要安装: pip install Flask-Session
import secrets
from datetime import timedelta

app = Flask(__name__)

# ===== 核心 Session 安全配置 =====
app.config.update(
    # Session 密钥（必须是强随机值）
    SECRET_KEY=secrets.token_hex(32),  # 或从环境变量加载
    
    # Cookie 安全设置
    SESSION_COOKIE_SECURE=True,      # 仅 HTTPS 传输
    SESSION_COOKIE_HTTPONLY=True,    # 防止 JavaScript 访问
    SESSION_COOKIE_SAMESITE='Lax',   # 防止 CSRF（推荐 Lax 或 Strict）
    
    # Session 生命周期
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1),  # 默认1小时
    SESSION_REFRESH_EACH_REQUEST=True,  # 每次请求刷新过期时间
    
    # Session 存储类型（开发用 filesystem，生产用 redis）
    SESSION_TYPE='filesystem',  # 'redis' | 'memcached' | 'sqlalchemy'
    SESSION_FILE_DIR='./flask_session/',
    SESSION_PERMANENT=False,    # 默认非永久会话
)

# 初始化 Session 扩展
Session(app)

# ===== 安全 Session 中间件 =====
@app.before_request
def session_security_check():
    """每次请求检查 Session 安全"""
    from flask import request, abort
    import time
    
    # 1. 检查 Session 是否过期
    if 'user_id' in session:
        last_activity = session.get('last_activity', time.time())
        if time.time() - last_activity > 3600:  # 1小时超时
            session.clear()
            return abort(401, 'Session expired')
        session['last_activity'] = time.time()
    
    # 2. 检查 IP 变化（可选，防止 Session 劫持）
    if 'user_id' in session:
        current_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        session_ip = session.get('ip_address')
        if session_ip and session_ip != current_ip:
            # IP 变化，可能是劫持，强制登出
            session.clear()
            return abort(401, 'Session invalidated due to IP change')
    
    # 3. 检查 User-Agent 变化（防止 Session 劫持）
    if 'user_id' in session:
        current_ua = request.headers.get('User-Agent', '')
        session_ua = session.get('user_agent')
        if session_ua and session_ua != current_ua:
            session.clear()
            return abort(401, 'Session invalidated')

# ===== 安全登录示例 =====
@app.route('/api/login', methods=['POST'])
def login():
    from flask import request, jsonify
    import bcrypt
    import time
    
    email = request.json.get('email')
    password = request.json.get('password')
    
    # 验证用户（示例）
    user = get_user_by_email(email)
    if not user or not bcrypt.checkpw(password.encode(), user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # 重新生成 Session ID（防止 Session 固定攻击）
    session.clear()
    session.regenerate() if hasattr(session, 'regenerate') else None
    
    # 设置 Session 数据
    session['user_id'] = user.id
    session['email'] = user.email
    session['login_time'] = time.time()
    session['last_activity'] = time.time()
    session['ip_address'] = request.headers.get('X-Forwarded-For', request.remote_addr)
    session['user_agent'] = request.headers.get('User-Agent', '')
    
    return jsonify({'message': 'Login successful', 'user_id': user.id})

# ===== 安全登出示例 =====
@app.route('/api/logout', methods=['POST'])
def logout():
    """安全登出：完全清除 Session"""
    # 记录登出日志（可选）
    if 'user_id' in session:
        log_logout_event(session['user_id'])
    
    # 清除 Session 数据
    session.clear()
    
    # 返回响应（让客户端也清除 Cookie）
    response = jsonify({'message': 'Logout successful'})
    response.delete_cookie('session')  # 清除 Cookie
    
    return response

# ===== 登出所有设备 =====
@app.route('/api/logout-all', methods=['POST'])
def logout_all_devices():
    """登出所有设备（需要 Redis 或数据库支持）"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # 标记用户所有 Session 无效（Redis 方案）
    # 详见 Redis Session 存储章节
    
    session.clear()
    return jsonify({'message': 'All sessions terminated'})
```

#### Express Session 安全配置

```javascript
// express-session-config.js
const express = require('express');
const session = require('express-session');
const RedisStore = require('connect-redis').default;
const crypto = require('crypto');
const Redis = require('ioredis');

const app = express();

// ===== Redis 客户端配置 =====
const redisClient = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  db: 0,
});

redisClient.on('error', (err) => {
  console.error('Redis connection error:', err);
});

// ===== Session 中间件配置 =====
app.use(session({
  // Session 存储
  store: new RedisStore({
    client: redisClient,
    prefix: 'sess:',           // Redis key 前缀
    ttl: 3600,                 // Session 过期时间（秒）
    disableTouch: false,       // 允许刷新 TTL
  }),
  
  // Session 密钥（必须使用强随机值）
  secret: process.env.SESSION_SECRET || crypto.randomBytes(32).toString('hex'),
  
  // Session 名称（自定义，不要使用默认的 connect.sid）
  name: '__host-session',     // 不暴露技术栈信息
  
  // Cookie 配置
  cookie: {
    secure: process.env.NODE_ENV === 'production',  // 仅 HTTPS
    httpOnly: true,            // 防止 JavaScript 访问
    maxAge: 3600000,           // 1小时（毫秒）
    sameSite: 'strict',        // 严格 SameSite
    path: '/',                 // Cookie 路径
    domain: process.env.COOKIE_DOMAIN, // Cookie 域名
  },
  
  // 其他配置
  resave: false,               // 不强制保存未修改的 Session
  saveUninitialized: false,    // 不保存未初始化的 Session
  rolling: true,               // 每次请求刷新 Cookie 过期时间
  unset: 'destroy',            // Session 置空时销毁
}));

// ===== Session 安全中间件 =====
function sessionSecurityMiddleware(req, res, next) {
  if (!req.session) {
    return next();
  }
  
  // 1. 检查 Session 过期
  if (req.session.userId) {
    const lastActivity = req.session.lastActivity || Date.now();
    if (Date.now() - lastActivity > 3600000) { // 1小时
      req.session.destroy();
      return res.status(401).json({ error: 'Session expired' });
    }
    req.session.lastActivity = Date.now();
  }
  
  // 2. IP 绑定检查（可选）
  if (req.session.userId && req.session.ipAddress) {
    const currentIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
    if (req.session.ipAddress !== currentIp) {
      // 记录异常
      console.warn(`IP change detected for user ${req.session.userId}: ${req.session.ipAddress} -> ${currentIp}`);
      // 可选：强制登出或记录审计日志
      // req.session.destroy();
      // return res.status(401).json({ error: 'Session invalidated' });
    }
  }
  
  // 3. User-Agent 检查
  if (req.session.userId && req.session.userAgent) {
    const currentUa = req.headers['user-agent'];
    if (req.session.userAgent !== currentUa) {
      console.warn(`UA change detected for user ${req.session.userId}`);
      req.session.destroy();
      return res.status(401).json({ error: 'Session invalidated' });
    }
  }
  
  next();
}

app.use(sessionSecurityMiddleware);

// ===== 安全登录 =====
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  
  try {
    // 验证用户
    const user = await getUserByEmail(email);
    if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // 重新生成 Session ID（防止 Session 固定攻击）
    req.session.regenerate((err) => {
      if (err) {
        return res.status(500).json({ error: 'Session regeneration failed' });
      }
      
      // 设置 Session 数据
      req.session.userId = user.id;
      req.session.email = user.email;
      req.session.loginTime = Date.now();
      req.session.lastActivity = Date.now();
      req.session.ipAddress = req.headers['x-forwarded-for'] || req.socket.remoteAddress;
      req.session.userAgent = req.headers['user-agent'];
      
      res.json({ message: 'Login successful', userId: user.id });
    });
  } catch (error) {
    res.status(500).json({ error: 'Login failed' });
  }
});

// ===== 安全登出 =====
app.post('/api/logout', (req, res) => {
  const userId = req.session?.userId;
  
  // 记录登出日志
  if (userId) {
    logLogoutEvent(userId);
  }
  
  // 销毁 Session
  req.session.destroy((err) => {
    if (err) {
      return res.status(500).json({ error: 'Logout failed' });
    }
    
    // 清除 Cookie
    res.clearCookie('__host-session');
    res.json({ message: 'Logout successful' });
  });
});

// ===== 登出所有设备 =====
app.post('/api/logout-all', async (req, res) => {
  const userId = req.session?.userId;
  if (!userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  
  // 删除用户所有 Session（Redis 模式）
  const pattern = `sess:*:${userId}`;
  const keys = await redisClient.keys(pattern);
  
  if (keys.length > 0) {
    await redisClient.del(...keys);
  }
  
  // 销毁当前 Session
  req.session.destroy((err) => {
    res.clearCookie('__host-session');
    res.json({ message: 'All sessions terminated', count: keys.length });
  });
});

module.exports = app;
```

---

### 3. Session 存储方案

#### 存储方案对比

| 方案 | 性能 | 持久化 | 扩展性 | 适用场景 | 成本 |
|------|------|--------|--------|---------|------|
| **内存存储** | 极高 | 否 | 差 | 开发/测试 | 免费 |
| **Redis** | 高 | 是 | 优 | 生产环境 | 免费自托管 |
| **Memcached** | 高 | 否 | 优 | 高频读取 | 免费自托管 |
| **PostgreSQL** | 中 | 是 | 良 | 需持久化 | 免费自托管 |
| **MongoDB** | 中 | 是 | 良 | 文档存储 | 免费自托管 |

#### Redis Session 存储实现（推荐）

```javascript
// redis-session-store.js
const Redis = require('ioredis');
const crypto = require('crypto');

class RedisSessionStore {
  constructor(options = {}) {
    this.redis = new Redis({
      host: options.host || 'localhost',
      port: options.port || 6379,
      password: options.password,
      db: options.db || 0,
    });
    
    this.prefix = options.prefix || 'session:';
    this.ttl = options.ttl || 3600; // 默认1小时
  }
  
  // 生成 Session ID
  generateSessionId() {
    return crypto.randomBytes(32).toString('hex');
  }
  
  // 创建 Session
  async create(userId, data = {}) {
    const sessionId = this.generateSessionId();
    const sessionKey = `${this.prefix}${sessionId}`;
    const userSessionKey = `${this.prefix}user:${userId}`;
    
    const sessionData = {
      userId,
      createdAt: Date.now(),
      lastActivity: Date.now(),
      ...data,
    };
    
    // 存储 Session 数据
    await this.redis.hset(sessionKey, 
      'data', JSON.stringify(sessionData),
      'userId', userId
    );
    await this.redis.expire(sessionKey, this.ttl);
    
    // 添加到用户 Session 列表（用于多设备管理）
    await this.redis.sadd(userSessionKey, sessionId);
    await this.redis.expire(userSessionKey, this.ttl * 24); // 保留24小时
    
    return sessionId;
  }
  
  // 获取 Session
  async get(sessionId) {
    const sessionKey = `${this.prefix}${sessionId}`;
    const data = await this.redis.hget(sessionKey, 'data');
    
    if (!data) {
      return null;
    }
    
    // 刷新 TTL（滑动过期）
    await this.redis.expire(sessionKey, this.ttl);
    
    return JSON.parse(data);
  }
  
  // 更新 Session
  async update(sessionId, updates) {
    const sessionKey = `${this.prefix}${sessionId}`;
    const existing = await this.get(sessionId);
    
    if (!existing) {
      return false;
    }
    
    const updated = {
      ...existing,
      ...updates,
      lastActivity: Date.now(),
    };
    
    await this.redis.hset(sessionKey, 'data', JSON.stringify(updated));
    return true;
  }
  
  // 销毁 Session
  async destroy(sessionId) {
    const sessionKey = `${this.prefix}${sessionId}`;
    const session = await this.get(sessionId);
    
    if (session?.userId) {
      // 从用户 Session 列表移除
      const userSessionKey = `${this.prefix}user:${session.userId}`;
      await this.redis.srem(userSessionKey, sessionId);
    }
    
    await this.redis.del(sessionKey);
    return true;
  }
  
  // 获取用户所有 Session
  async getUserSessions(userId) {
    const userSessionKey = `${this.prefix}user:${userId}`;
    const sessionIds = await this.redis.smembers(userSessionKey);
    
    const sessions = [];
    for (const sid of sessionIds) {
      const data = await this.get(sid);
      if (data) {
        sessions.push({
          sessionId: sid.substring(0, 8) + '...', // 脱敏
          createdAt: data.createdAt,
          lastActivity: data.lastActivity,
          ipAddress: data.ipAddress,
          userAgent: data.userAgent?.substring(0, 50),
        });
      } else {
        // 清理无效 Session
        await this.redis.srem(userSessionKey, sid);
      }
    }
    
    return sessions.sort((a, b) => b.lastActivity - a.lastActivity);
  }
  
  // 销毁用户所有 Session
  async destroyUserSessions(userId, exceptSessionId = null) {
    const userSessionKey = `${this.prefix}user:${userId}`;
    const sessionIds = await this.redis.smembers(userSessionKey);
    
    let count = 0;
    for (const sid of sessionIds) {
      if (sid !== exceptSessionId) {
        await this.destroy(sid);
        count++;
      }
    }
    
    return count;
  }
  
  // 清理过期 Session（定时任务）
  async cleanup() {
    const pattern = `${this.prefix}*`;
    const keys = await this.redis.keys(pattern);
    let cleaned = 0;
    
    for (const key of keys) {
      const ttl = await this.redis.ttl(key);
      if (ttl === -1) { // 无过期时间
        await this.redis.expire(key, this.ttl);
        cleaned++;
      }
    }
    
    console.log(`Cleanup completed: ${cleaned} sessions set to expire`);
    return cleaned;
  }
}

module.exports = RedisSessionStore;

// ===== 使用示例 =====
const sessionStore = new RedisSessionStore({
  host: 'localhost',
  port: 6379,
  ttl: 3600,
});

// 登录
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await authenticateUser(email, password);
  
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  // 检查设备数量限制
  const sessions = await sessionStore.getUserSessions(user.id);
  if (sessions.length >= 5) { // 最多5个设备
    // 踢掉最旧的设备
    await sessionStore.destroyUserSessions(user.id);
  }
  
  const sessionId = await sessionStore.create(user.id, {
    email: user.email,
    ipAddress: req.ip,
    userAgent: req.headers['user-agent'],
  });
  
  res.cookie('sessionId', sessionId, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    maxAge: 3600000,
  });
  
  res.json({ message: 'Login successful' });
});

// 获取登录设备列表
app.get('/api/sessions', async (req, res) => {
  const userId = req.session?.userId;
  if (!userId) {
    return res.status(401).json({ error: 'Not authenticated' });
  }
  
  const sessions = await sessionStore.getUserSessions(userId);
  res.json({ sessions });
});

// 踢出指定设备
app.delete('/api/sessions/:sessionId', async (req, res) => {
  const userId = req.session?.userId;
  const { sessionId } = req.params;
  
  // 验证 Session 属于当前用户
  const session = await sessionStore.get(sessionId);
  if (!session || session.userId !== userId) {
    return res.status(404).json({ error: 'Session not found' });
  }
  
  await sessionStore.destroy(sessionId);
  res.json({ message: 'Session terminated' });
});
```

#### PostgreSQL Session 存储

```sql
-- session-schema.sql
-- Session 表结构
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    session_token VARCHAR(128) NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- 索引
    INDEX idx_sessions_user_id (user_id),
    INDEX idx_sessions_token (session_token),
    INDEX idx_sessions_expires (expires_at)
);

-- 用户设备信息表
CREATE TABLE user_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    device_id VARCHAR(128) NOT NULL,
    device_name VARCHAR(255),
    device_type VARCHAR(50), -- 'mobile', 'desktop', 'tablet'
    last_used TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, device_id)
);

-- Session 审计日志
CREATE TABLE session_audit_log (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES sessions(id),
    user_id INTEGER,
    action VARCHAR(50) NOT NULL, -- 'create', 'destroy', 'refresh', 'hijack_detected'
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 自动清理过期 Session
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    -- 归档到审计日志
    INSERT INTO session_audit_log (session_id, user_id, action, ip_address, user_agent, details)
    SELECT id, user_id, 'expire', ip_address, user_agent, 
           jsonb_build_object('reason', 'expired')
    FROM sessions
    WHERE expires_at < NOW() AND is_active = TRUE;
    
    -- 删除过期 Session
    DELETE FROM sessions
    WHERE expires_at < NOW() - INTERVAL '7 days';
    
    -- 更新活跃状态
    UPDATE sessions
    SET is_active = FALSE
    WHERE expires_at < NOW() AND is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

-- 定时任务（需要 pg_cron 扩展）
-- SELECT cron.schedule('cleanup_sessions', '0 * * * *', 'SELECT cleanup_expired_sessions()');
```

```python
# postgres_session_store.py
import uuid
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import asyncpg

class PostgresSessionStore:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
        self.session_lifetime = timedelta(hours=1)
    
    async def create(self, user_id: int, ip_address: str = None, 
                     user_agent: str = None) -> str:
        """创建新 Session"""
        session_token = secrets.token_urlsafe(64)
        expires_at = datetime.utcnow() + self.session_lifetime
        
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO sessions (user_id, session_token, ip_address, 
                                     user_agent, expires_at)
                VALUES ($1, $2, $3, $4, $5)
            ''', user_id, session_token, ip_address, user_agent, expires_at)
            
            # 记录审计日志
            await self._log_audit(conn, None, user_id, 'create', 
                                  ip_address, user_agent)
        
        return session_token
    
    async def get(self, session_token: str) -> Optional[Dict]:
        """获取 Session"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                UPDATE sessions
                SET last_activity = NOW()
                WHERE session_token = $1 
                  AND expires_at > NOW() 
                  AND is_active = TRUE
                RETURNING id, user_id, ip_address, user_agent, 
                           created_at, last_activity
            ''', session_token)
            
            if not row:
                return None
            
            return dict(row)
    
    async def destroy(self, session_token: str) -> bool:
        """销毁 Session"""
        async with self.pool.acquire() as conn:
            session = await conn.fetchrow(
                'SELECT id, user_id FROM sessions WHERE session_token = $1',
                session_token
            )
            
            if not session:
                return False
            
            await conn.execute('''
                UPDATE sessions SET is_active = FALSE
                WHERE session_token = $1
            ''', session_token)
            
            await self._log_audit(conn, session['id'], session['user_id'], 
                                  'destroy')
            
            return True
    
    async def get_user_sessions(self, user_id: int) -> List[Dict]:
        """获取用户所有活跃 Session"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT id, ip_address, user_agent, created_at, last_activity
                FROM sessions
                WHERE user_id = $1 AND is_active = TRUE AND expires_at > NOW()
                ORDER BY last_activity DESC
            ''', user_id)
            
            return [dict(row) for row in rows]
    
    async def destroy_user_sessions(self, user_id: int, 
                                    except_token: str = None) -> int:
        """销毁用户所有 Session"""
        async with self.pool.acquire() as conn:
            query = '''
                UPDATE sessions SET is_active = FALSE
                WHERE user_id = $1 AND is_active = TRUE
            '''
            params = [user_id]
            
            if except_token:
                query += ' AND session_token != $2'
                params.append(except_token)
            
            result = await conn.execute(query, *params)
            
            # 返回受影响的行数
            return int(result.split()[-1])
    
    async def _log_audit(self, conn, session_id, user_id, action, 
                         ip_address=None, user_agent=None, details=None):
        """记录审计日志"""
        await conn.execute('''
            INSERT INTO session_audit_log 
            (session_id, user_id, action, ip_address, user_agent, details)
            VALUES ($1, $2, $3, $4, $5, $6)
        ''', session_id, user_id, action, ip_address, user_agent, details)
```

---

### 4. JWT 实现方案

#### 完整 JWT 安全实现

```javascript
// jwt-auth.js
const jwt = require('jsonwebtoken');
const crypto = require('crypto');

class JWTAuth {
  constructor(options = {}) {
    this.accessTokenSecret = options.accessTokenSecret || process.env.JWT_ACCESS_SECRET;
    this.refreshTokenSecret = options.refreshTokenSecret || process.env.JWT_REFRESH_SECRET;
    this.accessTokenExpiry = options.accessTokenExpiry || '15m';  // 短期
    this.refreshTokenExpiry = options.refreshTokenExpiry || '7d'; // 长期
    this.issuer = options.issuer || 'your-app';
    this.audience = options.audience || 'your-app-users';
  }
  
  // ===== 生成 Token 对 =====
  generateTokens(userId, payload = {}) {
    const accessToken = jwt.sign(
      {
        sub: userId,
        type: 'access',
        iat: Math.floor(Date.now() / 1000),
        ...payload,
      },
      this.accessTokenSecret,
      {
        expiresIn: this.accessTokenExpiry,
        issuer: this.issuer,
        audience: this.audience,
        jwtid: crypto.randomBytes(16).toString('hex'), // JWT ID
      }
    );
    
    const refreshToken = jwt.sign(
      {
        sub: userId,
        type: 'refresh',
        iat: Math.floor(Date.now() / 1000),
      },
      this.refreshTokenSecret,
      {
        expiresIn: this.refreshTokenExpiry,
        issuer: this.issuer,
        audience: this.audience,
        jwtid: crypto.randomBytes(16).toString('hex'),
      }
    );
    
    return { accessToken, refreshToken };
  }
  
  // ===== 验证 Access Token =====
  verifyAccessToken(token) {
    try {
      const decoded = jwt.verify(token, this.accessTokenSecret, {
        issuer: this.issuer,
        audience: this.audience,
      });
      
      if (decoded.type !== 'access') {
        throw new Error('Invalid token type');
      }
      
      return { valid: true, payload: decoded };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  }
  
  // ===== 验证 Refresh Token =====
  verifyRefreshToken(token) {
    try {
      const decoded = jwt.verify(token, this.refreshTokenSecret, {
        issuer: this.issuer,
        audience: this.audience,
      });
      
      if (decoded.type !== 'refresh') {
        throw new Error('Invalid token type');
      }
      
      return { valid: true, payload: decoded };
    } catch (error) {
      return { valid: false, error: error.message };
    }
  }
  
  // ===== 刷新 Token =====
  async refreshTokens(refreshToken, tokenStore) {
    // 验证 Refresh Token
    const { valid, payload } = this.verifyRefreshToken(refreshToken);
    
    if (!valid) {
      return { error: 'Invalid refresh token' };
    }
    
    // 检查 Token 是否在黑名单中
    const isBlacklisted = await tokenStore.isBlacklisted(refreshToken);
    if (isBlacklisted) {
      return { error: 'Token has been revoked' };
    }
    
    // 检查 Token 是否有效（在存储中）
    const storedToken = await tokenStore.getRefreshToken(payload.sub, refreshToken);
    if (!storedToken) {
      return { error: 'Refresh token not found' };
    }
    
    // 将旧的 Refresh Token 加入黑名单
    await tokenStore.blacklistToken(refreshToken, payload.exp);
    
    // 生成新的 Token 对
    const newTokens = this.generateTokens(payload.sub);
    
    // 存储新的 Refresh Token
    await tokenStore.saveRefreshToken(payload.sub, newTokens.refreshToken);
    
    return newTokens;
  }
}

// ===== Token 存储（使用 Redis）=====
class RedisTokenStore {
  constructor(redisClient) {
    this.redis = redisClient;
    this.refreshPrefix = 'refresh:';
    this.blacklistPrefix = 'blacklist:';
  }
  
  async saveRefreshToken(userId, token) {
    const decoded = jwt.decode(token);
    const key = `${this.refreshPrefix}${userId}:${decoded.jti}`;
    const ttl = decoded.exp - Math.floor(Date.now() / 1000);
    
    await this.redis.setex(key, ttl, '1');
  }
  
  async getRefreshToken(userId, token) {
    const decoded = jwt.decode(token);
    const key = `${this.refreshPrefix}${userId}:${decoded.jti}`;
    
    return await this.redis.get(key);
  }
  
  async blacklistToken(token, exp) {
    const key = `${this.blacklistPrefix}${token}`;
    const ttl = exp - Math.floor(Date.now() / 1000);
    
    if (ttl > 0) {
      await this.redis.setex(key, ttl, '1');
    }
  }
  
  async isBlacklisted(token) {
    const key = `${this.blacklistPrefix}${token}`;
    return await this.redis.exists(key);
  }
  
  async revokeAllUserTokens(userId) {
    const pattern = `${this.refreshPrefix}${userId}:*`;
    const keys = await this.redis.keys(pattern);
    
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
    
    return keys.length;
  }
}

// ===== Express 中间件 =====
function authMiddleware(jwtAuth, tokenStore) {
  return async (req, res, next) => {
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    const token = authHeader.substring(7);
    
    // 检查黑名单
    const isBlacklisted = await tokenStore.isBlacklisted(token);
    if (isBlacklisted) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }
    
    // 验证 Token
    const { valid, payload, error } = jwtAuth.verifyAccessToken(token);
    
    if (!valid) {
      return res.status(401).json({ error: error || 'Invalid token' });
    }
    
    req.user = payload;
    next();
  };
}

// ===== 使用示例 =====
const jwtAuth = new JWTAuth();
const tokenStore = new RedisTokenStore(redisClient);

// 登录
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  
  const user = await authenticateUser(email, password);
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  const tokens = jwtAuth.generateTokens(user.id, { email: user.email });
  
  // 存储 Refresh Token
  await tokenStore.saveRefreshToken(user.id, tokens.refreshToken);
  
  res.json({
    accessToken: tokens.accessToken,
    refreshToken: tokens.refreshToken,
    expiresIn: 900, // 15分钟
  });
});

// 刷新 Token
app.post('/api/refresh', async (req, res) => {
  const { refreshToken } = req.body;
  
  if (!refreshToken) {
    return res.status(400).json({ error: 'Refresh token required' });
  }
  
  const tokens = await jwtAuth.refreshTokens(refreshToken, tokenStore);
  
  if (tokens.error) {
    return res.status(401).json({ error: tokens.error });
  }
  
  res.json(tokens);
});

// 登出
app.post('/api/logout', authMiddleware(jwtAuth, tokenStore), async (req, res) => {
  const { refreshToken } = req.body;
  
  if (refreshToken) {
    const decoded = jwt.decode(refreshToken);
    await tokenStore.blacklistToken(refreshToken, decoded.exp);
  }
  
  // 也可以撤销 Access Token（存储到黑名单）
  const authHeader = req.headers.authorization;
  const accessToken = authHeader.substring(7);
  const decoded = jwt.decode(accessToken);
  await tokenStore.blacklistToken(accessToken, decoded.exp);
  
  res.json({ message: 'Logged out successfully' });
});

// 登出所有设备
app.post('/api/logout-all', authMiddleware(jwtAuth, tokenStore), async (req, res) => {
  const count = await tokenStore.revokeAllUserTokens(req.user.sub);
  res.json({ message: 'All sessions terminated', count });
});

module.exports = { JWTAuth, RedisTokenStore, authMiddleware };
```

---

### 5. Session 固定攻击防护

#### 攻击原理

```
Session 固定攻击流程：
1. 攻击者获取有效的 Session ID
   ↓
2. 诱骗受害者使用该 Session ID（通过链接、注入等）
   ↓
3. 受害者登录成功，Session 获得授权
   ↓
4. 攻击者使用已知的 Session ID 访问受害者账户
```

#### 防护实现

```python
# session_fixation_protection.py
from flask import Flask, session, request, redirect, url_for
import secrets
import time

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# ===== 核心防护：登录时重新生成 Session ID =====
def prevent_session_fixation():
    """Session 固定攻击防护装饰器"""
    def decorator(f):
        def wrapped(*args, **kwargs):
            # 登录前保存必要数据
            pre_login_data = dict(session)
            
            # 清除旧 Session
            session.clear()
            
            # 生成新的 Session ID（Flask 内置支持）
            session.modified = True
            session.new = True
            
            # 恢复必要数据（不包括敏感的认证信息）
            for key in ['csrf_token', 'language']:
                if key in pre_login_data:
                    session[key] = pre_login_data[key]
            
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ===== 更完整的实现 =====
@app.route('/api/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    
    # 验证用户
    user = authenticate_user(email, password)
    if not user:
        return {'error': 'Invalid credentials'}, 401
    
    # ===== 关键：登录成功后重新生成 Session =====
    # 1. 保存登录前的非认证数据
    temp_data = {
        'cart_items': session.get('cart_items', []),
        'redirect_url': session.get('redirect_url'),
    }
    
    # 2. 完全清除旧 Session
    session.clear()
    
    # 3. 强制生成新 Session ID
    # Flask-Session 会自动处理，或使用：
    if hasattr(session, 'regenerate'):
        session.regenerate()
    
    # 4. 设置新的认证数据
    session['user_id'] = user.id
    session['authenticated'] = True
    session['login_time'] = time.time()
    session['auth_method'] = 'password'
    
    # 5. 恢复非认证数据
    session['cart_items'] = temp_data['cart_items']
    
    # 6. 记录审计日志
    log_login_event(user.id, {
        'ip': request.remote_addr,
        'ua': request.headers.get('User-Agent'),
        'session_created': True,
    })
    
    return {'message': 'Login successful', 'user_id': user.id}

# ===== 检测 Session 固定攻击 =====
@app.before_request
def detect_session_fixation():
    """检测可能的 Session 固定攻击"""
    if 'user_id' not in session:
        return
    
    # 1. 检查登录时间与 Session 创建时间
    login_time = session.get('login_time', 0)
    session_created = session.get('_creation_time', time.time())
    
    # 如果 Session 创建时间早于登录时间，可能是攻击
    if session_created < login_time - 60:  # 允许60秒偏差
        log_security_event('session_fixation_suspected', {
            'user_id': session.get('user_id'),
            'login_time': login_time,
            'session_created': session_created,
        })
        session.clear()
        return redirect(url_for('login'))
    
    # 2. 检查 Session ID 来源
    session_source = session.get('_source', 'unknown')
    if session_source not in ['login', 'refresh']:
        log_security_event('unknown_session_source', {
            'source': session_source,
            'user_id': session.get('user_id'),
        })
```

```javascript
// Express Session 固定攻击防护
function preventSessionFixation(req, res, next) {
  const originalSessionId = req.sessionID;
  
  // 标记原始 Session ID
  req.session._originalId = originalSessionId;
  
  next();
}

// 登录处理
app.post('/api/login', preventSessionFixation, async (req, res) => {
  const { email, password } = req.body;
  
  const user = await authenticateUser(email, password);
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }
  
  // ===== 关键：重新生成 Session =====
  req.session.regenerate((err) => {
    if (err) {
      return res.status(500).json({ error: 'Session error' });
    }
    
    // 设置新的 Session 数据
    req.session.userId = user.id;
    req.session.email = user.email;
    req.session.loginTime = Date.now();
    req.session.authenticated = true;
    
    // 记录 Session ID 变化
    logSecurityEvent('session_regenerated', {
      userId: user.id,
      oldSessionId: req.session._originalId,
      newSessionId: req.sessionID,
    });
    
    res.json({ message: 'Login successful' });
  });
});
```

---

### 6. Session 劫持防护

#### 多层防护实现

```python
# session_hijacking_protection.py
from flask import request, session, abort
from functools import wraps
import hashlib
import time

class SessionHijackingProtection:
    def __init__(self, strict_mode=False):
        self.strict_mode = strict_mode
        self.allowed_ip_change = False  # 是否允许 IP 变化
        self.allowed_ua_change = False  # 是否允许 UA 变化
    
    def _get_client_fingerprint(self):
        """生成客户端指纹"""
        components = [
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            request.headers.get('Accept-Encoding', ''),
            # 不包含 IP，因为 IP 可能正常变化（移动网络）
        ]
        fingerprint = '|'.join(components)
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:32]
    
    def _get_ip_address(self):
        """获取真实 IP"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr
    
    def middleware(self):
        """Session 劫持检测中间件"""
        @wraps
        def wrapper(f):
            def decorated_function(*args, **kwargs):
                if 'user_id' not in session:
                    return f(*args, **kwargs)
                
                current_fingerprint = self._get_client_fingerprint()
                current_ip = self._get_ip_address()
                
                stored_fingerprint = session.get('client_fingerprint')
                stored_ip = session.get('ip_address')
                
                # 1. 检查指纹变化
                if stored_fingerprint and stored_fingerprint != current_fingerprint:
                    self._handle_hijacking_attempt('fingerprint_mismatch', {
                        'stored': stored_fingerprint,
                        'current': current_fingerprint,
                    })
                    session.clear()
                    abort(401, 'Session invalidated due to security concerns')
                
                # 2. 检查 IP 变化（可选，可能误报）
                if not self.allowed_ip_change and stored_ip and stored_ip != current_ip:
                    if self.strict_mode:
                        self._handle_hijacking_attempt('ip_change', {
                            'stored': stored_ip,
                            'current': current_ip,
                        })
                        session.clear()
                        abort(401, 'Session invalidated due to IP change')
                    else:
                        # 非严格模式：记录但不强制登出
                        log_suspicious_activity('ip_change', {
                            'user_id': session.get('user_id'),
                            'stored_ip': stored_ip,
                            'current_ip': current_ip,
                        })
                
                return f(*args, **kwargs)
            return decorated_function
        return wrapper
    
    def _handle_hijacking_attempt(self, reason, details):
        """处理劫持尝试"""
        log_security_event('session_hijacking_detected', {
            'reason': reason,
            'details': details,
            'user_id': session.get('user_id'),
            'ip': self._get_ip_address(),
            'user_agent': request.headers.get('User-Agent'),
            'timestamp': time.time(),
        })
        
        # 可选：发送告警邮件
        send_security_alert(session.get('user_id'), 'session_hijacking', details)
    
    def initialize_session(self, user_id):
        """初始化安全 Session"""
        session['user_id'] = user_id
        session['client_fingerprint'] = self._get_client_fingerprint()
        session['ip_address'] = self._get_ip_address()
        session['session_start'] = time.time()
        session['last_activity'] = time.time()

# ===== 使用 =====
protection = SessionHijackingProtection(strict_mode=False)

@app.before_request
def check_session_hijacking():
    if 'user_id' in session:
        # 更新最后活动时间
        session['last_activity'] = time.time()
        
        # 检查指纹
        current_fp = protection._get_client_fingerprint()
        stored_fp = session.get('client_fingerprint')
        
        if stored_fp and stored_fp != current_fp:
            log_security_event('session_fingerprint_mismatch', {
                'user_id': session.get('user_id'),
                'stored_fp': stored_fp,
                'current_fp': current_fp,
            })
            session.clear()
            return redirect('/login')
```

---

### 7. 多设备登录管理

#### 完整实现

```javascript
// multi-device-manager.js
const Redis = require('ioredis');

class MultiDeviceSessionManager {
  constructor(redisClient, options = {}) {
    this.redis = redisClient;
    this.maxDevices = options.maxDevices || 5; // 最多设备数
    this.sessionPrefix = 'device_session:';
    this.userDevicesPrefix = 'user_devices:';
  }
  
  // ===== 注册新设备 =====
  async registerDevice(userId, deviceInfo) {
    const deviceId = this._generateDeviceId(deviceInfo);
    const deviceKey = `${this.userDevicesPrefix}${userId}`;
    
    // 获取当前设备列表
    let devices = await this._getUserDevices(userId);
    
    // 检查设备数量限制
    const existingIndex = devices.findIndex(d => d.deviceId === deviceId);
    if (existingIndex === -1) {
      // 新设备
      if (devices.length >= this.maxDevices) {
        // 踢掉最旧的设备
        const oldest = devices.sort((a, b) => a.lastUsed - b.lastUsed)[0];
        await this._revokeDevice(userId, oldest.deviceId);
        devices = devices.filter(d => d.deviceId !== oldest.deviceId);
      }
    }
    
    // 更新或添加设备
    const device = {
      deviceId,
      deviceName: this._getDeviceName(deviceInfo),
      deviceType: this._getDeviceType(deviceInfo),
      ipAddress: deviceInfo.ipAddress,
      location: deviceInfo.location,
      userAgent: deviceInfo.userAgent,
      lastUsed: Date.now(),
      createdAt: existingIndex === -1 ? Date.now() : devices[existingIndex].createdAt,
    };
    
    // 移除旧记录并添加新记录
    devices = devices.filter(d => d.deviceId !== deviceId);
    devices.push(device);
    
    // 保存到 Redis
    await this.redis.set(
      deviceKey,
      JSON.stringify(devices),
      'EX',
      30 * 24 * 3600 // 30天过期
    );
    
    return device;
  }
  
  // ===== 获取用户设备列表 =====
  async getUserDevices(userId) {
    const devices = await this._getUserDevices(userId);
    
    return devices.map(device => ({
      deviceId: device.deviceId,
      deviceName: device.deviceName,
      deviceType: device.deviceType,
      ipAddress: device.ipAddress,
      location: device.location,
      lastUsed: new Date(device.lastUsed).toISOString(),
      createdAt: new Date(device.createdAt).toISOString(),
      isCurrent: device.isCurrent || false,
    }));
  }
  
  // ===== 撤销指定设备 =====
  async revokeDevice(userId, deviceId) {
    await this._revokeDevice(userId, deviceId);
    return { success: true, deviceId };
  }
  
  // ===== 撤销所有其他设备 =====
  async revokeOtherDevices(userId, currentDeviceId) {
    const devices = await this._getUserDevices(userId);
    let revokedCount = 0;
    
    for (const device of devices) {
      if (device.deviceId !== currentDeviceId) {
        await this._revokeDevice(userId, device.deviceId);
        revokedCount++;
      }
    }
    
    return { success: true, revokedCount };
  }
  
  // ===== 内部方法 =====
  async _getUserDevices(userId) {
    const deviceKey = `${this.userDevicesPrefix}${userId}`;
    const data = await this.redis.get(deviceKey);
    return data ? JSON.parse(data) : [];
  }
  
  async _revokeDevice(userId, deviceId) {
    // 1. 从设备列表移除
    const deviceKey = `${this.userDevicesPrefix}${userId}`;
    let devices = await this._getUserDevices(userId);
    devices = devices.filter(d => d.deviceId !== deviceId);
    await this.redis.set(deviceKey, JSON.stringify(devices), 'EX', 30 * 24 * 3600);
    
    // 2. 删除该设备的所有 Session
    const sessionPattern = `${this.sessionPrefix}${userId}:${deviceId}:*`;
    const keys = await this.redis.keys(sessionPattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
    
    // 3. 记录审计日志
    await this._logDeviceRevocation(userId, deviceId);
  }
  
  _generateDeviceId(deviceInfo) {
    const crypto = require('crypto');
    const fingerprint = [
      deviceInfo.userAgent || '',
      deviceInfo.screenResolution || '',
      deviceInfo.timezone || '',
      deviceInfo.language || '',
    ].join('|');
    
    return crypto.createHash('sha256').update(fingerprint).digest('hex').substring(0, 16);
  }
  
  _getDeviceName(deviceInfo) {
    const ua = deviceInfo.userAgent || '';
    
    if (/iPhone/.test(ua)) return 'iPhone';
    if (/iPad/.test(ua)) return 'iPad';
    if (/Android/.test(ua)) {
      if (/Mobile/.test(ua)) return 'Android Phone';
      return 'Android Tablet';
    }
    if (/Windows/.test(ua)) return 'Windows PC';
    if (/Mac/.test(ua)) return 'Mac';
    if (/Linux/.test(ua)) return 'Linux PC';
    
    return 'Unknown Device';
  }
  
  _getDeviceType(deviceInfo) {
    const ua = deviceInfo.userAgent || '';
    
    if (/Mobile|Android|iPhone/.test(ua)) return 'mobile';
    if (/Tablet|iPad/.test(ua)) return 'tablet';
    return 'desktop';
  }
  
  async _logDeviceRevocation(userId, deviceId) {
    // 实现审计日志记录
    console.log(`Device revoked: userId=${userId}, deviceId=${deviceId}`);
  }
}

// ===== API 路由 =====
const deviceManager = new MultiDeviceSessionManager(redisClient, { maxDevices: 5 });

// 获取设备列表
app.get('/api/devices', requireAuth, async (req, res) => {
  const devices = await deviceManager.getUserDevices(req.user.id);
  res.json({ devices });
});

// 撤销指定设备
app.delete('/api/devices/:deviceId', requireAuth, async (req, res) => {
  const { deviceId } = req.params;
  const result = await deviceManager.revokeDevice(req.user.id, deviceId);
  res.json(result);
});

// 撤销所有其他设备
app.post('/api/devices/revoke-others', requireAuth, async (req, res) => {
  const currentDeviceId = req.session.deviceId;
  const result = await deviceManager.revokeOtherDevices(req.user.id, currentDeviceId);
  res.json(result);
});

module.exports = MultiDeviceSessionManager;
```

---

### 8. Session 过期策略

#### 策略设计

```
Session 过期策略矩阵
├── 绝对过期
│   └── 到达指定时间后强制过期
├── 滑动过期
│   └── 每次活动后延长过期时间
├── 空闲过期
│   └── 无活动一段时间后过期
└── 强制过期
    └── 管理员或用户主动触发
```

#### 实现代码

```python
# session_expiry.py
from datetime import datetime, timedelta
from typing import Optional

class SessionExpiryPolicy:
    def __init__(self, 
                 absolute_timeout: int = 86400,     # 绝对过期：24小时
                 idle_timeout: int = 1800,          # 空闲过期：30分钟
                 sliding_window: bool = True,       # 启用滑动窗口
                 remember_me_timeout: int = 604800, # 记住我：7天
                 ):
        self.absolute_timeout = absolute_timeout
        self.idle_timeout = idle_timeout
        self.sliding_window = sliding_window
        self.remember_me_timeout = remember_me_timeout
    
    def check_expiry(self, session_data: dict) -> tuple[bool, str]:
        """检查 Session 是否过期"""
        now = datetime.utcnow()
        
        # 获取关键时间戳
        created_at = session_data.get('_created_at')
        last_activity = session_data.get('_last_activity', created_at)
        remember_me = session_data.get('_remember_me', False)
        
        if not created_at:
            return True, 'missing_creation_time'
        
        # 1. 检查绝对过期
        timeout = self.remember_me_timeout if remember_me else self.absolute_timeout
        if (now - created_at).total_seconds() > timeout:
            return True, 'absolute_timeout'
        
        # 2. 检查空闲过期
        if (now - last_activity).total_seconds() > self.idle_timeout:
            return True, 'idle_timeout'
        
        return False, 'active'
    
    def update_activity(self, session_data: dict) -> dict:
        """更新活动时间（滑动窗口）"""
        if self.sliding_window:
            session_data['_last_activity'] = datetime.utcnow()
            session_data['_activity_count'] = session_data.get('_activity_count', 0) + 1
        return session_data
    
    def create_session(self, user_id: int, remember_me: bool = False) -> dict:
        """创建新 Session"""
        now = datetime.utcnow()
        return {
            'user_id': user_id,
            '_created_at': now,
            '_last_activity': now,
            '_remember_me': remember_me,
            '_activity_count': 0,
        }

# ===== Flask 集成 =====
from flask import session, redirect, url_for

expiry_policy = SessionExpiryPolicy()

@app.before_request
def check_session_expiry():
    """检查 Session 过期"""
    if 'user_id' not in session:
        return
    
    # 检查过期
    is_expired, reason = expiry_policy.check_expiry(dict(session))
    
    if is_expired:
        # 记录过期事件
        log_session_event('expired', {
            'user_id': session.get('user_id'),
            'reason': reason,
        })
        
        # 清除 Session
        session.clear()
        
        # 重定向到登录页
        return redirect(url_for('login', expired='true'))
    
    # 更新活动时间
    expiry_policy.update_activity(session)
```

---

## 成本估算

### 各方案成本对比

| 方案 | 实现成本 | 运行成本 | 适用规模 |
|------|---------|---------|---------|
| **内存存储** | $0 | $0 | 开发/测试 |
| **Redis 自托管** | $0 | 服务器资源 | 小型应用 |
| **Redis 托管** | $0 | $5-30/月 | 中型应用 |
| **PostgreSQL** | $0 | 数据库资源 | 需持久化 |
| **JWT 无状态** | $0 | $0 | API 服务 |
| **Auth0 Free** | $0 | $0 | <7k MAU |
| **Clerk Free** | $0 | $0 | <5k MAU |

### 详细成本分析

```
免费方案成本估算（月度）

自托管 Redis（推荐）:
├── 服务器成本: $0（使用现有服务器）
├── 内存占用: 64-256MB（1万 Session）
├── 带宽成本: 忽略不计
└── 总成本: $0

托管 Redis（Upstash Free）:
├── 免费额度: 10,000 请求/天
├── 存储: 256MB
├── 超出后: $0.2/100k 请求
└── 适合: <5k MAU

JWT 无状态:
├── 无服务端存储成本
├── 带宽增加: ~1KB/请求
├── Token 撤销需要存储
└── 总成本: $0

第三方认证:
├── Auth0 Free: 7,000 MAU
├── Clerk Free: 5,000 MAU
├── Supabase Auth: 50,000 MAU
└── 超出后: $35-50/月
```

---

## 迁出成本

### 迁出难度评估

| 来源 | 目标 | 难度 | 时间 | 关键步骤 |
|------|------|------|------|---------|
| 内存存储 | Redis | 低 | 2小时 | 更新配置、迁移数据 |
| Redis | PostgreSQL | 中 | 1天 | 创建表、编写迁移脚本 |
| JWT | Session | 中 | 1天 | 修改认证逻辑、添加存储 |
| Auth0 | 自建 | 高 | 2-3天 | 导出用户、重写认证 |

### 迁出最佳实践

```
降低迁出成本的策略:

1. 抽象认证层
   ├── 创建统一的认证接口
   ├── 业务代码依赖接口而非实现
   └── 可随时替换底层实现

2. 数据可导出
   ├── 定期导出 Session 数据
   ├── 用户数据保持独立
   └── 避免依赖特定存储格式

3. 协议标准化
   ├── 使用 OAuth 2.0 / OIDC
   ├── 避免厂商特定 API
   └── 便于切换 Provider
```

---

## 验证方法

### 安全测试清单

```bash
# ===== 1. Session 配置检查 =====

# 检查 Cookie 安全属性
curl -I https://yourdomain.com/api/login
# 应包含：
# Set-Cookie: session=...; Secure; HttpOnly; SameSite=Strict

# 检查 Session ID 强度
# Session ID 应该至少 128 位随机数
python3 -c "
import secrets
session_id = secrets.token_hex(32)  # 256 位
print(f'Session ID length: {len(session_id) * 4} bits')
print(f'Example: {session_id}')
"

# ===== 2. Session 固定攻击测试 =====

# 步骤1: 获取未认证的 Session ID
SESSION_ID=$(curl -c - https://yourdomain.com 2>&1 | grep session | awk '{print $NF}')
echo "Session ID: $SESSION_ID"

# 步骤2: 使用该 Session ID 登录
curl -b "session=$SESSION_ID" -X POST https://yourdomain.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# 步骤3: 检查 Session ID 是否变化
NEW_SESSION_ID=$(curl -c - -b "session=$SESSION_ID" https://yourdomain.com/api/me 2>&1 | grep session | awk '{print $NF}')
echo "New Session ID: $NEW_SESSION_ID"

# 如果 SESSION_ID == NEW_SESSION_ID，存在漏洞！

# ===== 3. Session 劫持测试 =====

# 正常登录
TOKEN=$(curl -X POST https://yourdomain.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}' | jq -r '.token')

# 修改 User-Agent 后访问
curl -H "Authorization: Bearer $TOKEN" \
  -H "User-Agent: Different-Agent" \
  https://yourdomain.com/api/me

# 如果返回 401，说明劫持防护有效

# ===== 4. 过期策略测试 =====

# 登录并记录时间
START_TIME=$(date +%s)
curl -X POST https://yourdomain.com/api/login -c cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# 等待超过空闲时间（例如 35 分钟）
sleep 2100

# 尝试访问
curl -b cookies.txt https://yourdomain.com/api/me
# 应返回 401 Unauthorized

# ===== 5. 多设备测试 =====

# 设备1 登录
curl -X POST https://yourdomain.com/api/login -c device1.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# 设备2 登录
curl -X POST https://yourdomain.com/api/login -c device2.txt \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password"}'

# 获取设备列表
curl -b device1.txt https://yourdomain.com/api/devices

# 设备1 登出所有其他设备
curl -b device1.txt -X POST https://yourdomain.com/api/logout-all

# 设备2 应该被登出
curl -b device2.txt https://yourdomain.com/api/me
# 应返回 401
```

### 自动化测试脚本

```python
# test_session_security.py
import pytest
import requests
import time

BASE_URL = 'https://yourdomain.com'

class TestSessionSecurity:
    
    def test_session_cookie_attributes(self):
        """测试 Cookie 安全属性"""
        response = requests.post(f'{BASE_URL}/api/login', json={
            'email': 'test@test.com',
            'password': 'testpassword',
        })
        
        cookie = response.cookies.get('session')
        assert cookie is not None, 'Session cookie not set'
        
        # 检查 Cookie 属性（需要检查 Set-Cookie header）
        set_cookie = response.headers.get('Set-Cookie', '')
        assert 'HttpOnly' in set_cookie, 'HttpOnly not set'
        assert 'Secure' in set_cookie, 'Secure not set'
        assert 'SameSite' in set_cookie, 'SameSite not set'
    
    def test_session_fixation_protection(self):
        """测试 Session 固定攻击防护"""
        # 获取未认证 Session
        session = requests.Session()
        session.get(f'{BASE_URL}/')
        old_session_id = session.cookies.get('session')
        
        # 登录
        session.post(f'{BASE_URL}/api/login', json={
            'email': 'test@test.com',
            'password': 'testpassword',
        })
        
        new_session_id = session.cookies.get('session')
        
        # Session ID 应该变化
        assert old_session_id != new_session_id, \
            'Session ID not regenerated after login (Session Fixation vulnerability)'
    
    def test_session_hijacking_protection(self):
        """测试 Session 劫持防护"""
        # 正常登录
        session = requests.Session()
        session.post(f'{BASE_URL}/api/login', json={
            'email': 'test@test.com',
            'password': 'testpassword',
        })
        
        # 修改 User-Agent
        response = session.get(f'{BASE_URL}/api/me', headers={
            'User-Agent': 'Hacker/1.0'
        })
        
        # 应该被拒绝或强制登出
        assert response.status_code == 401, \
            'Session hijacking protection not working'
    
    def test_session_expiry(self):
        """测试 Session 过期"""
        session = requests.Session()
        session.post(f'{BASE_URL}/api/login', json={
            'email': 'test@test.com',
            'password': 'testpassword',
        })
        
        # 等待超过空闲时间（假设测试环境设置较短）
        time.sleep(1900)  # 约 31 分钟
        
        response = session.get(f'{BASE_URL}/api/me')
        assert response.status_code == 401, 'Session not expired after idle timeout'
    
    def test_concurrent_sessions_limit(self):
        """测试并发 Session 限制"""
        sessions = []
        
        # 创建超过限制的 Session
        for i in range(6):  # 假设限制为 5
            session = requests.Session()
            session.post(f'{BASE_URL}/api/login', json={
                'email': 'test@test.com',
                'password': 'testpassword',
            })
            sessions.append(session)
        
        # 第一个 Session 应该被踢出
        response = sessions[0].get(f'{BASE_URL}/api/me')
        assert response.status_code == 401, 'Oldest session not revoked'
    
    def test_logout_all_devices(self):
        """测试登出所有设备"""
        # 创建多个 Session
        sessions = []
        for i in range(3):
            session = requests.Session()
            session.post(f'{BASE_URL}/api/login', json={
                'email': 'test@test.com',
                'password': 'testpassword',
            })
            sessions.append(session)
        
        # 从第一个 Session 登出所有设备
        sessions[0].post(f'{BASE_URL}/api/logout-all')
        
        # 其他 Session 应该无效
        for i in range(1, 3):
            response = sessions[i].get(f'{BASE_URL}/api/me')
            assert response.status_code == 401, f'Session {i} still valid after logout-all'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## 与其他武器配合

```
Session 安全配合图谱

前置配合:
├── [HTTPS 加密](./https-setup.md) - Cookie 安全传输基础
├── [密码安全](./password-security.md) - 登录入口防护
└── [输入验证](./input-validation.md) - 防止注入攻击

并行配合:
├── [CSRF 防护](./csrf-protection.md) - 配合 SameSite
├── [Rate Limiting](./rate-limiting.md) - 防止暴力破解
└── [日志审计](./audit-logging.md) - 记录异常行为

后置配合:
├── [入侵检测](../open-source/intrusion-detection.md) - 检测异常 Session
└── [安全监控](./security-monitoring.md) - 实时告警
```

---

## 常见问题

### Q: Session 和 JWT 如何选择？
A: 
- **需要即时撤销** → Session（支付、管理后台）
- **无状态 API** → JWT
- **移动应用** → JWT + Refresh Token
- **传统 Web** → Session
- **混合场景** → Session（Web）+ JWT（API）

### Q: Session 存储选哪个？
A:
- **开发环境** → 内存存储
- **生产环境（小规模）** → Redis
- **需要持久化** → PostgreSQL
- **需要高可用** → Redis Cluster

### Q: 如何防止 Session 劫持？
A:
1. Cookie 设置 Secure、HttpOnly、SameSite
2. 绑定 IP 和 User-Agent（注意误报）
3. 使用 HTTPS 全站加密
4. 登录时重新生成 Session ID
5. 监控异常活动

### Q: 如何处理多设备登录？
A:
1. 设置最大设备数限制（如 5 个）
2. 提供设备管理界面
3. 允许用户查看和撤销设备
4. 异地登录发送通知
5. 可疑活动强制登出

### Q: Refresh Token 存哪里？
A:
- **最安全** → HttpOnly Cookie
- **移动应用** → 安全存储（Keychain/Keystore）
- **SPA** → 内存 + HttpOnly Cookie
- **不要** → LocalStorage（XSS 风险）

### Q: 如何实现"记住我"功能？
A:
```python
# 安全的记住我实现
@app.route('/api/login', methods=['POST'])
def login():
    remember_me = request.json.get('remember_me', False)
    
    if remember_me:
        # 延长 Session 过期时间
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=30)
        
        # 设置持久化 Refresh Token
        refresh_token = generate_refresh_token()
        set_cookie('refresh_token', refresh_token, 
                   max_age=30*24*3600, 
                   httponly=True, 
                   secure=True)
    else:
        session.permanent = False
        app.permanent_session_lifetime = timedelta(hours=1)
```

---

## 推荐实现

### 完整免费方案
- **存储**: Redis（自托管或 Upstash Free）
- **配置**: Secure + HttpOnly + SameSite=Strict
- **过期**: 滑动过期 30 分钟 + 绝对过期 24 小时
- **防护**: Session 固定 + 劫持检测 + 多设备管理

### 推荐服务

**认证服务（免费层）**
- Auth0 Free: https://auth0.com/pricing - 7,000 MAU
- Clerk Free: https://clerk.com/pricing - 5,000 MAU
- Supabase Auth: https://supabase.com/auth - 50,000 MAU

**Redis 托管（免费层）**
- Upstash Free: https://upstash.com/pricing - 10k 请求/天
- Redis Cloud Free: https://redis.com/pricing - 30MB

**监控告警**
- Sentry Free: https://sentry.io - 错误追踪
- Grafana Cloud Free: https://grafana.com - 日志分析

---

## 相关资源

### 官方文档
- OWASP Session Management: https://owasp.org/www-community/vulnerabilities/Session_fixation
- MDN HTTP Cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
- Redis Documentation: https://redis.io/docs/

### 开源项目
- express-session: https://github.com/expressjs/session
- Flask-Session: https://github.com/pallets-eco/flask-session
- node-redis-session: https://github.com/tj/connect-redis

### 安全测试
- OWASP ZAP: https://www.zaproxy.org/
- Burp Suite: https://portswigger.net/burp
- Session Cookie Checker: https://securityheaders.com/

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
