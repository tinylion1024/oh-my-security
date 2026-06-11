# 第 2 周：账号安全

## 概述

本周实施账号安全措施，保护用户账户不被盗用。

**预计时间**: 2 小时
**难度**: 中等
**成本**: $0

---

## 核心知识

### 账号安全三大支柱

1. **认证安全**: 确认用户是谁
2. **授权安全**: 确认用户能做什么
3. **会话安全**: 确保会话不被劫持

---

## 密码策略实施

### 密码哈希（必须）

**❌ 错误做法**:
```python
# 不要明文存储
password = request.form['password']
db.execute("INSERT INTO users (password) VALUES (?)", password)
```

**✅ 正确做法**:

```python
# Python bcrypt
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

# 使用
hashed = hash_password("user_password")
is_valid = verify_password("user_password", hashed)
```

```javascript
// Node.js bcrypt
const bcrypt = require('bcrypt');

async function hashPassword(password) {
    return await bcrypt.hash(password, 12);
}

async function verifyPassword(password, hashed) {
    return await bcrypt.compare(password, hashed);
}

// 使用
const hashed = await hashPassword('user_password');
const isValid = await verifyPassword('user_password', hashed);
```

### 密码强度验证

```python
import re

def check_password_strength(password: str) -> tuple[bool, list]:
    """检查密码强度"""
    issues = []

    if len(password) < 8:
        issues.append("密码至少 8 位")

    if len(password) > 128:
        issues.append("密码不能超过 128 位")

    if not re.search(r'[a-z]', password):
        issues.append("建议包含小写字母")

    if not re.search(r'[A-Z]', password):
        issues.append("建议包含大写字母")

    if not re.search(r'\d', password):
        issues.append("建议包含数字")

    # 常见密码黑名单
    common = ['password', '123456', 'qwerty', 'admin']
    if password.lower() in common:
        issues.append("密码过于常见")

    return len(issues) == 0, issues
```

---

## 登录安全配置

### 登录限流（必须）

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # 登录接口更严格
def login():
    # 登录逻辑
    pass
```

```javascript
// Express 限流
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 分钟
    max: 5, // 最多 5 次尝试
    message: '登录尝试过多，请稍后再试'
});

app.post('/login', loginLimiter, (req, res) => {
    // 登录逻辑
});
```

### 登录失败记录

```python
# 记录失败登录
def log_failed_login(email: str, ip: str):
    db.execute("""
        INSERT INTO failed_logins (email, ip, created_at)
        VALUES (?, ?, NOW())
    """, email, ip)

    # 检查是否需要锁定
    count = db.query("""
        SELECT COUNT(*) as cnt FROM failed_logins
        WHERE email = ? AND created_at > NOW() - INTERVAL 15 MINUTE
    """, email)

    if count['cnt'] >= 5:
        # 锁定账户 15 分钟
        lock_account(email, minutes=15)
        send_alert_email(email)
```

---

## MFA 配置步骤

### TOTP 实现（推荐）

```python
import pyotp
import qrcode

# 1. 生成密钥
secret = pyotp.random_base32()

# 2. 生成二维码
def get_mfa_qr(email: str, secret: str):
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=email, issuer_name="MyApp")

    qr = qrcode.make(uri)
    return qr

# 3. 验证码验证
def verify_mfa_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)

# 使用
is_valid = verify_mfa_code(user.mfa_secret, request.form['code'])
```

### 备用恢复码

```python
import secrets

def generate_backup_codes(count: int = 10) -> list:
    """生成备用恢复码"""
    return [secrets.token_hex(4).upper() for _ in range(count)]

# 存储（哈希后）
codes = generate_backup_codes()
hashed_codes = [hash_password(code) for code in codes]

# 给用户展示一次
print("请保存这些恢复码:", codes)

# 验证恢复码
def verify_backup_code(code: str, user_id: str) -> bool:
    user_codes = db.query("SELECT backup_codes FROM users WHERE id = ?", user_id)
    for hashed in user_codes:
        if verify_password(code, hashed):
            # 移除已使用的码
            remove_backup_code(user_id, hashed)
            return True
    return False
```

---

## Session 安全

### 安全配置

```python
# Flask Session 配置
app.config.update(
    SESSION_COOKIE_SECURE=True,      # 仅 HTTPS
    SESSION_COOKIE_HTTPONLY=True,    # JavaScript 无法访问
    SESSION_COOKIE_SAMESITE='Lax',   # CSRF 防护
    PERMANENT_SESSION_LIFETIME=3600  # 1 小时过期
)
```

```javascript
// Express Session 配置
app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: true,        // 仅 HTTPS
        httpOnly: true,      // JavaScript 无法访问
        sameSite: 'strict',  // CSRF 防护
        maxAge: 3600000      // 1 小时
    }
}));
```

### Session 重生成

```python
@app.route('/login', methods=['POST'])
def login():
    # 验证用户
    if verify_user(email, password):
        # 重生成 Session（防止 Session 固定攻击）
        session.regenerate()

        # 设置用户信息
        session['user_id'] = user.id
        session['login_time'] = datetime.now()

        return redirect('/dashboard')
```

---

## 异常登录检测

```python
def detect_anomaly_login(user_id: str, request) -> dict:
    """检测异常登录"""
    user = get_user(user_id)
    anomalies = []

    # 1. 检查 IP
    current_ip = request.remote_addr
    if user.last_login_ip != current_ip:
        anomalies.append(f"IP 变化: {user.last_login_ip} -> {current_ip}")

    # 2. 检查设备
    user_agent = request.headers.get('User-Agent')
    if user.last_user_agent != user_agent:
        anomalies.append(f"设备变化")

    # 3. 检查地理位置（可选）
    # 需要地理位置服务

    # 4. 检查登录时间
    if user.last_login_time:
        if datetime.now() - user.last_login_time < timedelta(seconds=10):
            anomalies.append("登录间隔过短")

    return {
        'is_anomaly': len(anomalies) > 0,
        'anomalies': anomalies
    }

# 使用
result = detect_anomaly_login(user.id, request)
if result['is_anomaly']:
    send_security_alert_email(user.email, result['anomalies'])
```

---

## 本周实施计划

| 天 | 任务 | 时间 |
|----|------|------|
| Day 1 | 密码哈希实施 | 30 分钟 |
| Day 2 | 登录限流配置 | 20 分钟 |
| Day 3 | Session 安全配置 | 20 分钟 |
| Day 4 | MFA 实施准备 | 30 分钟 |
| Day 5 | 异常检测实施 | 20 分钟 |

---

## 验证清单

- [ ] 密码使用 bcrypt 哈希存储
- [ ] 密码强度验证已实施
- [ ] 登录限流已配置
- [ ] Session 安全配置完成
- [ ] Session 重生成已实施
- [ ] MFA 可选功能已准备
- [ ] 异常登录检测已实施

---

## 下一步

完成本周任务后，继续 [第 3 周：API 安全](./03-api-security.md)
