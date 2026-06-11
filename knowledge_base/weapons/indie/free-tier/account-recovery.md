# 账号恢复机制 (Account Recovery)

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防 + 响应
- **实现成本**: 免费（自建）/ $0-20/月（邮件服务）
- **实施时间**: 3-5小时
- **维护成本**: 2小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
解决用户忘记密码、账号被盗、设备丢失等场景下的安全恢复问题，确保用户能在保护账户安全的前提下找回账号控制权。

## 恢复方式对比

### 快速选型表

| 恢复方式 | 实现复杂度 | 安全性评级 | 用户体验 | 成本 | 独立开发者推荐度 |
|---------|-----------|-----------|---------|------|----------------|
| **邮件验证** | ⭐ 简单 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 好 | ✅ 免费 | ⭐⭐⭐⭐⭐ |
| **恢复码** | ⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | ⭐⭐ 一般 | ✅ 免费 | ⭐⭐⭐⭐⭐ |
| **安全问题** | ⭐ 简单 | ⭐⭐ 低 | ⭐⭐⭐ 一般 | ✅ 免费 | ⭐⭐ |
| **身份验证** | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ 最高 | ⭐ 差 | 💰 人工成本 | ⭐⭐ |
| **社交验证** | ⭐⭐⭐ 复杂 | ⭐⭐⭐ 中高 | ⭐⭐⭐ 一般 | ✅ 免费 | ⭐⭐⭐ |

### 详细对比

#### 1. 邮件验证重置

**优点**：
- 实现简单，几乎所有邮箱服务都支持
- 用户熟悉，无需额外学习成本
- 免费或低成本

**缺点**：
- 邮箱本身可能被盗
- 邮件可能进入垃圾箱
- 需要用户记住注册邮箱

**适用场景**：
- 大多数 Web 应用
- 作为主要或备用恢复方式

---

#### 2. 恢复码 (Recovery Codes)

**优点**：
- 完全离线可用
- 安全性高，预先生成
- 不依赖第三方服务
- 可撤销和重新生成

**缺点**：
- 用户需要安全保存
- 容易丢失
- 需要在账号正常时生成

**适用场景**：
- 开启 MFA 后的备用方案
- 高安全性应用
- 企业内部系统

---

#### 3. 安全问题

**优点**：
- 实现简单
- 无需第三方服务

**缺点**：
- 答案可能被猜到或社会工程攻击
- 用户可能忘记答案
- 安全性较低

**适用场景**：
- 作为多层验证的一环
- 低安全性应用

---

## 快速上手（5分钟）

### 密码重置流程（Python + Flask）

```python
# password_reset.py
import secrets
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

# 模拟数据库
reset_tokens = {}  # {token: {"email": str, "expires": datetime}}
users_db = {}  # {email: {"password_hash": str, "recovery_codes": []}}

# 1. 请求重置密码
@app.route("/auth/reset-request", methods=["POST"])
def request_reset():
    """发送密码重置邮件"""
    email = request.json.get("email")

    if email not in users_db:
        # 安全考虑：不暴露用户是否存在
        return jsonify({"message": "如果邮箱存在，重置邮件已发送"}), 200

    # 生成安全令牌
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=1)

    reset_tokens[token] = {
        "email": email,
        "expires": expires
    }

    # 发送邮件（实际项目中）
    reset_link = f"https://yourapp.com/reset?token={token}"
    # send_email(email, "密码重置", f"点击链接重置密码: {reset_link}")
    print(f"[DEBUG] 重置链接: {reset_link}")

    return jsonify({"message": "如果邮箱存在，重置邮件已发送"}), 200

# 2. 验证重置令牌
@app.route("/auth/reset-verify/<token>", methods=["GET"])
def verify_reset_token(token):
    """验证重置令牌是否有效"""
    if token not in reset_tokens:
        return jsonify({"error": "无效的重置链接"}), 400

    token_data = reset_tokens[token]
    if datetime.utcnow() > token_data["expires"]:
        del reset_tokens[token]
        return jsonify({"error": "重置链接已过期"}), 400

    return jsonify({"email": token_data["email"], "valid": True}), 200

# 3. 重置密码
@app.route("/auth/reset-confirm", methods=["POST"])
def confirm_reset():
    """确认密码重置"""
    token = request.json.get("token")
    new_password = request.json.get("password")

    if token not in reset_tokens:
        return jsonify({"error": "无效的重置链接"}), 400

    token_data = reset_tokens[token]
    if datetime.utcnow() > token_data["expires"]:
        del reset_tokens[token]
        return jsonify({"error": "重置链接已过期"}), 400

    # 更新密码
    email = token_data["email"]
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    users_db[email]["password_hash"] = password_hash

    # 删除已使用的令牌
    del reset_tokens[token]

    # 撤销所有会话（可选）
    # revoke_all_sessions(email)

    # 发送安全通知
    # send_email(email, "密码已修改", "您的密码已成功修改，如非本人操作请立即联系客服")

    return jsonify({"message": "密码重置成功"}), 200

if __name__ == "__main__":
    app.run(debug=True)
```

### 恢复码生成与使用（Node.js）

```javascript
// recoveryCodes.js
const crypto = require('crypto');

/**
 * 恢复码管理类
 */
class RecoveryCodesManager {
  constructor() {
    this.codes = new Map(); // userId -> { codes: [], createdAt: Date }
  }

  /**
   * 生成恢复码
   * @param {string} userId - 用户ID
   * @param {number} count - 生成数量（默认10个）
   * @returns {string[]} 恢复码列表
   */
  generateCodes(userId, count = 10) {
    const codes = [];
    for (let i = 0; i < count; i++) {
      // 生成格式: XXXX-XXXX-XXXX
      const code = this._generateSingleCode();
      // 存储哈希值而非明文
      codes.push({
        codeHash: this._hashCode(code),
        used: false,
        usedAt: null
      });
      codes.push(code); // 返回明文给用户保存
    }

    // 存储到数据库
    this.codes.set(userId, {
      codes: codes.filter((_, i) => i % 2 === 1), // 只存奇数索引的哈希对象
      createdAt: new Date()
    });

    // 返回明文码
    return codes.filter((_, i) => i % 2 === 0);
  }

  /**
   * 生成单个恢复码
   */
  _generateSingleCode() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // 排除易混淆字符
    let code = '';
    for (let i = 0; i < 12; i++) {
      if (i > 0 && i % 4 === 0) code += '-';
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  }

  /**
   * 哈希恢复码
   */
  _hashCode(code) {
    return crypto.createHash('sha256').update(code).digest('hex');
  }

  /**
   * 验证恢复码
   * @param {string} userId - 用户ID
   * @param {string} code - 用户输入的恢复码
   * @returns {boolean} 是否验证成功
   */
  verifyCode(userId, code) {
    const userData = this.codes.get(userId);
    if (!userData) return false;

    const codeHash = this._hashCode(code.toUpperCase().replace(/-/g, ''));
    const codeEntry = userData.codes.find(
      c => c.codeHash === codeHash && !c.used
    );

    if (codeEntry) {
      codeEntry.used = true;
      codeEntry.usedAt = new Date();
      return true;
    }

    return false;
  }

  /**
   * 获取剩余恢复码数量
   */
  getRemainingCount(userId) {
    const userData = this.codes.get(userId);
    if (!userData) return 0;
    return userData.codes.filter(c => !c.used).length;
  }

  /**
   * 撤销所有恢复码并重新生成
   */
  regenerateCodes(userId) {
    return this.generateCodes(userId);
  }
}

// 使用示例
const manager = new RecoveryCodesManager();

// 生成恢复码
const userId = 'user_123';
const codes = manager.generateCodes(userId);
console.log('生成的恢复码（请安全保存）:');
codes.forEach((code, i) => console.log(`${i + 1}. ${code}`));

// 验证恢复码
const testCode = codes[0];
console.log(`\n验证恢复码 "${testCode}":`, manager.verifyCode(userId, testCode));
console.log('剩余恢复码数量:', manager.getRemainingCount(userId));

// 再次使用同一个码应该失败
console.log(`\n再次验证 "${testCode}":`, manager.verifyCode(userId, testCode));
```

## 详细方案

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     账号恢复流程架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户请求恢复                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                                │
│  │ 身份确认 │ ◄─── 邮箱验证 / 手机验证 / 恢复码              │
│  └────┬────┘                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────┐                                                │
│  │ 风险评估 │ ◄─── 检查异常行为 / 设备变化                   │
│  └────┬────┘                                                │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────┐                                            │
│  │ 验证方式选择 │ ◄─── 多种方式可选                          │
│  └──────┬──────┘                                            │
│         │                                                   │
│    ┌────┴────┬─────────┐                                    │
│    ▼         ▼         ▼                                    │
│ ┌──────┐ ┌──────┐ ┌──────┐                                  │
│ │邮件OTP│ │恢复码 │ │人工审核│                               │
│ └───┬──┘ └───┬──┘ └───┬──┘                                  │
│     └────┬───┴───────┘                                      │
│          ▼                                                  │
│     ┌──────────┐                                            │
│     │ 重置凭证  │ ◄─── 生成一次性令牌                        │
│     └─────┬────┘                                            │
│           ▼                                                 │
│     ┌──────────┐                                            │
│     │ 设置新密码│ ◄─── 强制密码复杂度                        │
│     └─────┬────┘                                            │
│           ▼                                                 │
│     ┌──────────┐                                            │
│     │ 安全审计  │ ◄─── 记录恢复事件 / 通知用户              │
│     └──────────┘                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心实现步骤

#### 步骤1：数据库设计

```sql
-- 密码重置令牌表
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    token_hash VARCHAR(64) NOT NULL,  -- SHA-256 哈希
    email VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);

-- 恢复码表
CREATE TABLE recovery_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    code_hash VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP,
    used_ip VARCHAR(45),
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_recovery_codes_user ON recovery_codes(user_id);

-- 账号恢复事件日志
CREATE TABLE account_recovery_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    recovery_type VARCHAR(50) NOT NULL, -- 'email', 'recovery_code', 'manual'
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_fingerprint VARCHAR(64),
    success BOOLEAN DEFAULT FALSE,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recovery_logs_user ON account_recovery_logs(user_id);
CREATE INDEX idx_recovery_logs_created ON account_recovery_logs(created_at);
```

#### 步骤2：完整恢复服务实现

```python
# account_recovery_service.py
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RecoveryType(Enum):
    EMAIL = "email"
    RECOVERY_CODE = "recovery_code"
    MANUAL = "manual"

@dataclass
class RecoveryRequest:
    user_id: str
    email: str
    ip_address: str
    user_agent: str
    device_fingerprint: Optional[str] = None

@dataclass
class RecoveryResult:
    success: bool
    message: str
    requires_manual_review: bool = False
    recovery_token: Optional[str] = None

class AccountRecoveryService:
    """账号恢复服务"""

    def __init__(self, db, email_service, config):
        self.db = db
        self.email_service = email_service
        self.config = config

        # 配置
        self.token_expiry_hours = config.get('token_expiry_hours', 1)
        self.max_attempts_per_hour = config.get('max_attempts_per_hour', 3)
        self.recovery_code_count = config.get('recovery_code_count', 10)

    async def initiate_recovery(
        self,
        email: str,
        ip_address: str,
        user_agent: str
    ) -> Dict:
        """
        发起账号恢复流程

        Returns:
            {
                "success": bool,
                "message": str,
                "recovery_options": List[str],  # 可用的恢复方式
                "token": Optional[str]  # 用于后续验证的临时令牌
            }
        """
        # 1. 检查请求频率
        recent_attempts = await self._get_recent_attempts(email, hours=1)
        if recent_attempts >= self.max_attempts_per_hour:
            logger.warning(f"Too many recovery attempts for {email}")
            return {
                "success": False,
                "message": "请求过于频繁，请稍后再试",
                "recovery_options": []
            }

        # 2. 查找用户（不暴露是否存在）
        user = await self._find_user_by_email(email)
        if not user:
            # 记录失败尝试（安全考虑）
            await self._log_recovery_attempt(
                email=email,
                ip_address=ip_address,
                success=False,
                reason="user_not_found"
            )
            # 返回模糊消息，不暴露用户是否存在
            return {
                "success": True,
                "message": "如果邮箱已注册，您将收到恢复指引",
                "recovery_options": []
            }

        # 3. 检查是否有恢复码
        has_recovery_codes = await self._has_recovery_codes(user['id'])

        # 4. 生成临时令牌
        temp_token = secrets.token_urlsafe(32)

        # 5. 记录恢复会话
        await self._create_recovery_session(
            user_id=user['id'],
            temp_token=temp_token,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # 6. 发送邮件验证
        reset_token = await self._create_reset_token(user['id'], ip_address)
        await self._send_recovery_email(
            email=email,
            reset_token=reset_token,
            has_recovery_codes=has_recovery_codes
        )

        # 7. 记录成功
        await self._log_recovery_attempt(
            email=email,
            ip_address=ip_address,
            user_id=user['id'],
            success=True
        )

        recovery_options = ["email"]
        if has_recovery_codes:
            recovery_options.append("recovery_code")

        return {
            "success": True,
            "message": "恢复邮件已发送",
            "recovery_options": recovery_options,
            "temp_token": temp_token
        }

    async def verify_with_recovery_code(
        self,
        temp_token: str,
        recovery_code: str,
        ip_address: str
    ) -> RecoveryResult:
        """使用恢复码验证身份"""

        # 1. 验证临时令牌
        session = await self._get_recovery_session(temp_token)
        if not session:
            return RecoveryResult(
                success=False,
                message="无效的恢复会话"
            )

        # 2. 验证恢复码
        code_valid = await self._verify_recovery_code(
            user_id=session['user_id'],
            code=recovery_code
        )

        if not code_valid:
            await self._log_recovery_attempt(
                user_id=session['user_id'],
                ip_address=ip_address,
                success=False,
                reason="invalid_recovery_code"
            )
            return RecoveryResult(
                success=False,
                message="恢复码无效或已使用"
            )

        # 3. 生成重置令牌
        reset_token = await self._create_reset_token(
            user_id=session['user_id'],
            ip_address=ip_address,
            verified_by="recovery_code"
        )

        # 4. 记录成功
        await self._log_recovery_attempt(
            user_id=session['user_id'],
            ip_address=ip_address,
            success=True,
            reason="recovery_code_verified"
        )

        return RecoveryResult(
            success=True,
            message="身份验证成功",
            recovery_token=reset_token
        )

    async def reset_password(
        self,
        reset_token: str,
        new_password: str,
        ip_address: str
    ) -> RecoveryResult:
        """重置密码"""

        # 1. 验证令牌
        token_data = await self._get_reset_token(reset_token)
        if not token_data:
            return RecoveryResult(
                success=False,
                message="无效的重置链接"
            )

        if datetime.utcnow() > token_data['expires_at']:
            return RecoveryResult(
                success=False,
                message="重置链接已过期"
            )

        if token_data['used_at']:
            return RecoveryResult(
                success=False,
                message="重置链接已使用"
            )

        # 2. 验证密码强度
        password_valid, password_msg = self._validate_password(new_password)
        if not password_valid:
            return RecoveryResult(success=False, message=password_msg)

        # 3. 检查密码是否与历史密码相同
        if await self._is_password_reused(
            token_data['user_id'],
            new_password
        ):
            return RecoveryResult(
                success=False,
                message="不能使用最近使用过的密码"
            )

        # 4. 更新密码
        await self._update_password(
            user_id=token_data['user_id'],
            new_password=new_password
        )

        # 5. 标记令牌已使用
        await self._mark_token_used(reset_token)

        # 6. 撤销所有会话
        await self._revoke_all_sessions(token_data['user_id'])

        # 7. 生成新的恢复码
        new_codes = await self._regenerate_recovery_codes(
            token_data['user_id']
        )

        # 8. 发送安全通知
        user = await self._get_user(token_data['user_id'])
        await self._send_password_changed_notification(
            email=user['email'],
            ip_address=ip_address
        )

        # 9. 记录审计日志
        await self._log_recovery_attempt(
            user_id=token_data['user_id'],
            ip_address=ip_address,
            success=True,
            reason="password_reset_completed"
        )

        return RecoveryResult(
            success=True,
            message="密码重置成功，请使用新密码登录"
        )

    # ============== 恢复码管理 ==============

    async def generate_recovery_codes(
        self,
        user_id: str
    ) -> List[str]:
        """生成新的恢复码"""
        codes = []

        for _ in range(self.recovery_code_count):
            code = self._generate_single_code()
            code_hash = self._hash_code(code)

            await self.db.execute("""
                INSERT INTO recovery_codes (user_id, code_hash)
                VALUES ($1, $2)
            """, user_id, code_hash)

            codes.append(code)

        return codes

    def _generate_single_code(self) -> str:
        """生成单个恢复码"""
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        parts = []
        for _ in range(3):
            part = ''.join(
                secrets.choice(chars) for _ in range(4)
            )
            parts.append(part)
        return '-'.join(parts)

    def _hash_code(self, code: str) -> str:
        """哈希恢复码"""
        normalized = code.upper().replace('-', '')
        return hashlib.sha256(normalized.encode()).hexdigest()

    async def _verify_recovery_code(
        self,
        user_id: str,
        code: str
    ) -> bool:
        """验证恢复码"""
        code_hash = self._hash_code(code)

        result = await self.db.fetch_one("""
            UPDATE recovery_codes
            SET used_at = CURRENT_TIMESTAMP,
                used_ip = $3
            WHERE user_id = $1
              AND code_hash = $2
              AND used_at IS NULL
              AND revoked = FALSE
            RETURNING id
        """, user_id, code_hash, "request.ip")

        return result is not None

    async def get_remaining_codes_count(
        self,
        user_id: str
    ) -> int:
        """获取剩余恢复码数量"""
        result = await self.db.fetch_one("""
            SELECT COUNT(*) as count
            FROM recovery_codes
            WHERE user_id = $1
              AND used_at IS NULL
              AND revoked = FALSE
        """, user_id)
        return result['count']

    # ============== 辅助方法 ==============

    def _validate_password(self, password: str) -> tuple:
        """验证密码强度"""
        if len(password) < 12:
            return False, "密码至少需要12个字符"

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

        if not (has_upper and has_lower and has_digit and has_special):
            return False, "密码需要包含大小写字母、数字和特殊字符"

        # 检查常见弱密码
        common_passwords = [
            "password", "123456", "qwerty", "admin",
            "letmein", "welcome", "monkey", "dragon"
        ]
        if password.lower() in common_passwords:
            return False, "密码过于常见，请选择更强的密码"

        return True, "密码强度符合要求"

    async def _log_recovery_attempt(
        self,
        email: Optional[str] = None,
        user_id: Optional[str] = None,
        ip_address: str = "",
        success: bool = False,
        reason: str = ""
    ):
        """记录恢复尝试"""
        await self.db.execute("""
            INSERT INTO account_recovery_logs
            (user_id, email, recovery_type, ip_address, success, failure_reason)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, user_id, email, "email", ip_address, success, reason if not success else None)
```

### 配置选项

```python
# config.py
RECOVERY_CONFIG = {
    # 令牌配置
    'token_expiry_hours': 1,          # 重置令牌有效期（小时）
    'max_attempts_per_hour': 3,       # 每小时最大尝试次数

    # 恢复码配置
    'recovery_code_count': 10,        # 生成恢复码数量
    'recovery_code_format': 'XXXX-XXXX-XXXX',

    # 密码配置
    'min_password_length': 12,
    'require_special_chars': True,
    'password_history_count': 5,      # 检查最近N个密码

    # 安全配置
    'require_email_verification': True,
    'notify_on_password_change': True,
    'revoke_all_sessions_on_reset': True,
    'require_new_recovery_codes_on_reset': True,
}
```

## 成本估算

### 免费方案（自建）

| 项目 | 说明 |
|------|------|
| 邮件发送 | 使用免费额度（SendGrid 100封/天，AWS SES 62,000封/月） |
| 存储 | 恢复码和令牌占用空间极小（<1KB/用户） |
| 计算 | 本地加密验证，无额外成本 |
| **总计** | **$0/月** |

### 付费方案

| 项目 | 月成本 | 说明 |
|------|--------|------|
| 邮件服务 | $15 | SendGrid Essential（40k封/月） |
| 短信备用 | $1-50 | 按实际使用量计费 |
| **总计** | **$15-65/月** | 视用户量和短信使用而定 |

## 迁出成本

### 从自建迁移到第三方服务

| 项目 | 难度 | 时间 |
|------|------|------|
| 用户数据导出 | 低 | 1-2小时 |
| 恢复码迁移 | 低 | 不需要（重新生成） |
| 代码重构 | 中 | 1-3天 |

### 从第三方迁移到自建

| 项目 | 难度 | 时间 |
|------|------|------|
| API 改造 | 中 | 2-3天 |
| 邮件模板迁移 | 低 | 2-4小时 |
| 恢复流程重写 | 中 | 1-2天 |

## 与其他武器配合

### 上游武器

| 武器 | 配合方式 |
|------|----------|
| **MFA 实现** | 恢复码作为 MFA 丢失后的备用方案 |
| **登录异常检测** | 恢复前检查账号是否有异常登录 |
| **会话安全** | 重置密码后撤销所有会话 |

### 下游武器

| 武器 | 配合方式 |
|------|----------|
| **审计日志** | 记录所有恢复事件 |
| **安全告警** | 可疑恢复行为触发告警 |

### 配合示例

```python
# 恢复前检查异常行为
async def initiate_recovery_with_check(self, email: str, ip: str):
    # 先检查是否有异常登录
    anomaly_check = await login_anomaly_service.check_user_risk(email)

    if anomaly_check.risk_score > 70:
        # 高风险账号，要求人工验证
        return await self._initiate_manual_recovery(email, ip)

    # 正常流程
    return await self.initiate_recovery(email, ip)
```

## 常见问题

### Q1: 恢复码被泄露怎么办？

**A:**
1. 用户可以随时重新生成恢复码（旧码自动失效）
2. 每个恢复码只能使用一次
3. 建议开启使用通知，发现异常立即修改

```python
# 恢复码重新生成
@app.post("/recovery-codes/regenerate")
async def regenerate_codes(current_user: User):
    # 撤销所有旧码
    await db.execute(
        "UPDATE recovery_codes SET revoked = TRUE WHERE user_id = $1",
        current_user.id
    )
    # 生成新码
    new_codes = await recovery_service.generate_recovery_codes(current_user.id)
    return {"codes": new_codes, "message": "请安全保存新恢复码"}
```

### Q2: 用户邮箱也丢失了怎么办？

**A:** 提供多因素身份验证流程：

```python
async def manual_recovery_request(self, user_id: str, documents: List):
    """
    人工审核恢复流程
    1. 提交身份证明文件
    2. 客服人工审核
    3. 通过后允许设置新邮箱和密码
    """
    pass
```

### Q3: 如何防止暴力破解恢复码？

**A:**
1. 限制尝试次数
2. 增加尝试间隔
3. 账户锁定机制

```python
async def verify_with_rate_limit(self, temp_token: str, code: str):
    # 检查尝试次数
    attempts = await self._get_failed_attempts(temp_token)
    if attempts >= 5:
        # 锁定15分钟
        await self._lock_session(temp_token, minutes=15)
        raise TooManyAttemptsError("尝试次数过多，请15分钟后再试")

    # 验证
    result = await self._verify_code(temp_token, code)
    if not result:
        await self._record_failed_attempt(temp_token)

    return result
```

### Q4: 重置邮件进入垃圾箱怎么办？

**A:**
1. 配置 SPF/DKIM/DMARC
2. 使用专业邮件服务
3. 提供备用验证方式（恢复码）
4. 显示发送提示

```javascript
// 前端提示
<div className="email-sent-notice">
  <p>邮件已发送至 {maskedEmail}</p>
  <ul>
    <li>请检查垃圾邮件文件夹</li>
    <li>添加 {senderEmail} 到联系人</li>
    <li>如果没有收到，<a onClick={resendEmail}>点击重新发送</a></li>
  </ul>
</div>
```

### Q5: 如何处理批量账号恢复请求？

**A:** 人工介入 + 分批处理

```python
async def batch_recovery_check(self, requests: List):
    """
    批量恢复请求检查
    用于检测可能的攻击
    """
    if len(requests) > 10:  # 同一IP短时间内请求超过10个
        # 触发安全告警
        await security_alert_service.trigger({
            "type": "mass_recovery_attempt",
            "ip": requests[0].ip,
            "count": len(requests)
        })

        # 暂停处理，等待人工审核
        return {"status": "pending_review"}
```

## 安全清单

- [ ] 重置令牌使用加密安全的随机数生成器
- [ ] 令牌存储哈希值而非明文
- [ ] 设置合理的令牌过期时间（推荐1小时）
- [ ] 限制请求频率防止滥用
- [ ] 不暴露用户是否存在的信息
- [ ] 密码重置后撤销所有会话
- [ ] 记录所有恢复事件用于审计
- [ ] 恢复码一次性使用
- [ ] 提供恢复码重新生成功能
- [ ] 发送安全通知告知用户
