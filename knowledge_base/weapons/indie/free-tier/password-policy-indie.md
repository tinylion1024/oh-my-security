# 密码策略 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 30分钟
- **维护成本**: 10分钟/月
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## 适用场景
独立开发者在产品中实现用户认证时，需要一套实用的密码安全策略。本文档提供从密码复杂度验证、安全存储到重置流程的完整解决方案，所有方案均为免费且可在30分钟内实施。

---

## 快速上手（总览）

```
密码策略实施清单
├── 5分钟：实现密码强度验证
├── 10分钟：配置密码安全存储
├── 5分钟：添加常见密码黑名单
├── 5分钟：实现密码重置流程
└── 5分钟：添加多因素认证推荐
```

---

## 详细方案

### 1. 密码复杂度要求

**原则**：实用而非过度。过严的密码要求会导致用户写在便利贴上，反而降低安全性。

#### 推荐策略

| 要求 | 最小标准 | 增强标准 | 说明 |
|------|---------|---------|------|
| 最小长度 | 12位 | 16位 | 长度比复杂度更重要 |
| 大写字母 | 可选 | 建议 | 增加熵值 |
| 小写字母 | 必须 | 必须 | 基础要求 |
| 数字 | 可选 | 建议 | 增加熵值 |
| 特殊字符 | 可选 | 建议 | 增加熵值 |
| 最大长度 | 128位 | 128位 | 防止DoS攻击 |
| 禁止空格 | 否 | 否 | 允许密码短语 |

#### 密码强度验证（Python实现）

```python
# password_validator.py
import re
from typing import Tuple
import hashlib

class PasswordValidator:
    """密码强度验证器"""
    
    # 常见弱密码黑名单（基于 RockYou 泄露数据 Top 1000）
    WEAK_PASSWORDS = {
        '123456', 'password', '12345678', 'qwerty', '123456789',
        '12345', '1234', '111111', '1234567', 'dragon',
        '123123', 'baseball', 'abc123', 'football', 'monkey',
        'letmein', '696969', 'shadow', 'master', '666666',
        'qwertyuiop', '123321', 'mustang', '1234567890', 'michael',
        '654321', 'pussy', 'superman', '1qaz2wsx', '7777777',
        'admin', 'administrator', 'welcome', 'login', 'passw0rd',
        'password1', 'password123', 'admin123', 'root', 'toor',
        'iloveyou', 'sunshine', 'princess', 'starwars', 'batman',
        'trustno1', 'ashley', 'bailey', 'passw0rd', 'shadow1'
    }
    
    def __init__(
        self,
        min_length: int = 12,
        max_length: int = 128,
        require_upper: bool = False,
        require_lower: bool = True,
        require_digit: bool = False,
        require_special: bool = False,
        check_common: bool = True
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.require_upper = require_upper
        self.require_lower = require_lower
        self.require_digit = require_digit
        self.require_special = require_special
        self.check_common = check_common
    
    def validate(self, password: str) -> Tuple[bool, str, int]:
        """
        验证密码强度
        
        Returns:
            (是否有效, 错误消息, 强度评分 0-100)
        """
        if not password:
            return False, "密码不能为空", 0
        
        # 长度检查
        if len(password) < self.min_length:
            return False, f"密码至少需要 {self.min_length} 位", 0
        
        if len(password) > self.max_length:
            return False, f"密码不能超过 {self.max_length} 位", 0
        
        # 字符类型检查
        if self.require_upper and not re.search(r'[A-Z]', password):
            return False, "密码需要包含大写字母", 0
        
        if self.require_lower and not re.search(r'[a-z]', password):
            return False, "密码需要包含小写字母", 0
        
        if self.require_digit and not re.search(r'[0-9]', password):
            return False, "密码需要包含数字", 0
        
        if self.require_special and not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            return False, "密码需要包含特殊字符", 0
        
        # 常见密码检查
        if self.check_common:
            normalized = password.lower()
            if normalized in self.WEAK_PASSWORDS:
                return False, "密码过于常见，请选择更独特的密码", 0
            
            # 检查是否包含常见密码
            for weak in self.WEAK_PASSWORDS:
                if weak in normalized and len(weak) >= 6:
                    return False, "密码包含常见弱密码模式", 0
        
        # 计算强度评分
        score = self._calculate_strength(password)
        
        return True, "密码强度符合要求", score
    
    def _calculate_strength(self, password: str) -> int:
        """计算密码强度评分 (0-100)"""
        score = 0
        
        # 长度评分（最高 40 分）
        length = len(password)
        if length >= 16:
            score += 40
        elif length >= 14:
            score += 32
        elif length >= 12:
            score += 24
        else:
            score += 16
        
        # 字符多样性评分（最高 40 分）
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password))
        
        diversity = sum([has_upper, has_lower, has_digit, has_special])
        score += diversity * 10
        
        # 字符均匀分布（最高 20 分）
        if has_upper and has_lower:
            upper_ratio = len(re.findall(r'[A-Z]', password)) / length
            lower_ratio = len(re.findall(r'[a-z]', password)) / length
            if 0.2 <= upper_ratio <= 0.8 and 0.2 <= lower_ratio <= 0.8:
                score += 10
        
        if has_digit:
            digit_ratio = len(re.findall(r'[0-9]', password)) / length
            if 0.1 <= digit_ratio <= 0.4:
                score += 5
        
        if has_special:
            special_ratio = len(re.findall(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password)) / length
            if 0.05 <= special_ratio <= 0.3:
                score += 5
        
        return min(score, 100)
    
    def get_strength_label(self, score: int) -> str:
        """获取强度标签"""
        if score >= 80:
            return "强"
        elif score >= 60:
            return "中"
        elif score >= 40:
            return "弱"
        else:
            return "极弱"


# 使用示例
if __name__ == "__main__":
    validator = PasswordValidator(
        min_length=12,
        require_upper=True,
        require_lower=True,
        require_digit=True
    )
    
    test_passwords = [
        "password123",
        "MySecureP@ss2024!",
        "correct-horse-battery-staple",
        "Short1!",
        "ThisIsAVeryLongPasswordThatIsActuallySecure123!@#"
    ]
    
    for pwd in test_passwords:
        valid, message, score = validator.validate(pwd)
        label = validator.get_strength_label(score)
        print(f"密码: {pwd[:20]}... -> 有效: {valid}, 消息: {message}, 强度: {score} ({label})")
```

#### 密码强度实时检测（JavaScript/TypeScript实现）

```typescript
// password-strength.ts

interface PasswordStrengthResult {
  valid: boolean;
  message: string;
  score: number;
  label: string;
  suggestions: string[];
}

// 常见弱密码黑名单
const WEAK_PASSWORDS = new Set([
  '123456', 'password', '12345678', 'qwerty', '123456789',
  '12345', '1234', '111111', '1234567', 'dragon',
  '123123', 'baseball', 'abc123', 'football', 'monkey',
  'letmein', 'shadow', 'master', 'qwertyuiop', '123321',
  'admin', 'administrator', 'welcome', 'login', 'passw0rd',
  'password1', 'password123', 'admin123', 'root', 'toor',
  'iloveyou', 'sunshine', 'princess', 'starwars', 'batman'
]);

export function checkPasswordStrength(password: string): PasswordStrengthResult {
  const suggestions: string[] = [];
  let score = 0;
  
  // 基础检查
  if (!password) {
    return {
      valid: false,
      message: '密码不能为空',
      score: 0,
      label: '无',
      suggestions: ['请输入密码']
    };
  }
  
  // 长度检查
  if (password.length < 12) {
    suggestions.push('密码至少需要12位');
    return {
      valid: false,
      message: '密码太短',
      score: 0,
      label: '极弱',
      suggestions
    };
  }
  
  // 长度评分
  if (password.length >= 20) score += 40;
  else if (password.length >= 16) score += 32;
  else if (password.length >= 14) score += 24;
  else score += 16;
  
  // 字符类型检查
  const hasUpper = /[A-Z]/.test(password);
  const hasLower = /[a-z]/.test(password);
  const hasDigit = /[0-9]/.test(password);
  const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  
  if (!hasLower) suggestions.push('添加小写字母');
  if (!hasUpper) suggestions.push('添加大写字母');
  if (!hasDigit) suggestions.push('添加数字');
  if (!hasSpecial) suggestions.push('添加特殊字符');
  
  // 多样性评分
  const diversity = [hasUpper, hasLower, hasDigit, hasSpecial].filter(Boolean).length;
  score += diversity * 10;
  
  // 常见密码检查
  const normalized = password.toLowerCase();
  for (const weak of WEAK_PASSWORDS) {
    if (normalized.includes(weak)) {
      return {
        valid: false,
        message: '密码包含常见弱密码',
        score: 0,
        label: '极弱',
        suggestions: ['请选择更独特的密码']
      };
    }
  }
  
  // 字符分布均匀度
  if (hasUpper && hasLower) {
    const upperCount = (password.match(/[A-Z]/g) || []).length;
    const ratio = upperCount / password.length;
    if (ratio >= 0.2 && ratio <= 0.8) score += 10;
  }
  
  // 连续字符惩罚
  if (/(.)\1{2,}/.test(password)) {
    score -= 10;
    suggestions.push('避免连续重复字符');
  }
  
  // 键盘模式惩罚
  const keyboardPatterns = ['qwerty', 'asdfgh', 'zxcvbn', '1234567890'];
  for (const pattern of keyboardPatterns) {
    if (normalized.includes(pattern)) {
      score -= 15;
      suggestions.push('避免键盘连续模式');
      break;
    }
  }
  
  // 最终评分
  score = Math.max(0, Math.min(100, score));
  
  let label: string;
  if (score >= 80) label = '强';
  else if (score >= 60) label = '中';
  else if (score >= 40) label = '弱';
  else label = '极弱';
  
  return {
    valid: score >= 40,
    message: score >= 60 ? '密码强度符合要求' : '密码强度不足',
    score,
    label,
    suggestions
  };
}

// React 组件示例
export function PasswordStrengthIndicator({ password }: { password: string }) {
  const result = checkPasswordStrength(password);
  
  const getColor = () => {
    if (result.score >= 80) return 'bg-green-500';
    if (result.score >= 60) return 'bg-yellow-500';
    if (result.score >= 40) return 'bg-orange-500';
    return 'bg-red-500';
  };
  
  return (
    <div className="space-y-2">
      {/* 进度条 */}
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full transition-all duration-300 ${getColor()}`}
          style={{ width: `${result.score}%` }}
        />
      </div>
      
      {/* 标签和建议 */}
      <div className="flex justify-between text-sm">
        <span className={result.score >= 60 ? 'text-green-600' : 'text-red-600'}>
          {result.label}
        </span>
        <span className="text-gray-500">{result.score}/100</span>
      </div>
      
      {result.suggestions.length > 0 && (
        <ul className="text-xs text-gray-500 list-disc list-inside">
          {result.suggestions.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

---

### 2. 密码安全存储

**原则**：永远不要存储明文密码，使用现代哈希算法（bcrypt 或 argon2）。

#### 哈希算法对比

| 算法 | 优势 | 劣势 | 推荐场景 |
|------|------|------|---------|
| **bcrypt** | 广泛支持、内置盐值、可调成本 | 内存使用较低 | 通用场景 |
| **argon2** | 抗GPU攻击、内存硬 | 需要更多配置 | 高安全需求 |
| **scrypt** | 内存硬、可配置复杂 | 较argon2旧 | 兼容旧系统 |
| ~~PBKDF2~~ | 广泛支持 | 可被GPU加速 | 不推荐 |
| ~~SHA256~~ | 快速 | 太快、易暴力破解 | 不适用于密码 |

#### Python 密码哈希实现

```python
# password_hasher.py
import bcrypt
import secrets
import base64
from typing import Tuple
from dataclasses import dataclass

@dataclass
class HashedPassword:
    """哈希后的密码对象"""
    hash: str
    algorithm: str = "bcrypt"
    version: int = 1

class PasswordHasher:
    """密码哈希处理器"""
    
    def __init__(self, rounds: int = 12):
        """
        初始化哈希器
        
        Args:
            rounds: bcrypt 成本轮数（推荐12，每增加1，时间翻倍）
        """
        self.rounds = rounds
    
    def hash_password(self, password: str) -> HashedPassword:
        """
        哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            HashedPassword 对象
        """
        # 生成盐值并哈希
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return HashedPassword(
            hash=hashed.decode('utf-8'),
            algorithm="bcrypt",
            version=1
        )
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            hashed: 存储的哈希值
            
        Returns:
            是否匹配
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed.encode('utf-8')
            )
        except Exception:
            return False
    
    def needs_rehash(self, hashed: str, new_rounds: int = None) -> bool:
        """
        检查是否需要重新哈希（成本参数变化时）
        
        Args:
            hashed: 存储的哈希值
            new_rounds: 新的成本参数，默认使用初始化时的值
            
        Returns:
            是否需要重新哈希
        """
        if new_rounds is None:
            new_rounds = self.rounds
            
        try:
            # 提取当前轮数
            current_rounds = bcrypt.gensalt(rounds=new_rounds)
            # 检查哈希是否需要更新
            return not hashed.startswith(f'$2b${new_rounds:02d}$')
        except Exception:
            return True


# 使用示例
if __name__ == "__main__":
    hasher = PasswordHasher(rounds=12)
    
    # 注册时哈希密码
    password = "MySecurePassword123!"
    hashed = hasher.hash_password(password)
    print(f"哈希值: {hashed.hash}")
    print(f"算法: {hashed.algorithm}")
    
    # 登录时验证密码
    is_valid = hasher.verify_password(password, hashed.hash)
    print(f"验证结果: {is_valid}")
    
    # 错误密码验证
    is_valid_wrong = hasher.verify_password("WrongPassword", hashed.hash)
    print(f"错误密码验证: {is_valid_wrong}")
```

#### Argon2 高安全实现

```python
# password_hasher_argon2.py
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError
from typing import Optional

class Argon2PasswordHasher:
    """
    Argon2 密码哈希器（更安全的选择）
    
    Argon2 是密码哈希竞赛的获胜者，专门设计用于抵抗：
    - GPU 暴力破解
    - 侧信道攻击
    - 时间-空间权衡攻击
    """
    
    def __init__(
        self,
        time_cost: int = 3,        # 迭代次数
        memory_cost: int = 65536,  # 内存使用（KB），64MB
        parallelism: int = 4,      # 并行线程数
        hash_len: int = 32,        # 输出长度
        salt_len: int = 16         # 盐值长度
    ):
        self.ph = PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
            type=Type.ID  # Argon2id 混合模式
        )
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        return self.ph.hash(password)
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """验证密码"""
        try:
            self.ph.verify(hashed, password)
            return True
        except (VerifyMismatchError, VerificationError):
            return False
    
    def needs_rehash(self, hashed: str) -> bool:
        """检查是否需要重新哈希"""
        return self.ph.check_needs_rehash(hashed)


# Flask 集成示例
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)
hasher = Argon2PasswordHasher()

# 模拟用户数据库
users_db = {}

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # 验证密码强度
    validator = PasswordValidator(min_length=12, require_upper=True)
    valid, message, score = validator.validate(password)
    
    if not valid:
        return jsonify({'error': message}), 400
    
    # 哈希密码
    hashed = hasher.hash_password(password)
    
    # 存储用户
    users_db[email] = {
        'email': email,
        'password_hash': hashed,
        'created_at': datetime.now().isoformat()
    }
    
    return jsonify({'message': '注册成功', 'strength_score': score})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = users_db.get(email)
    if not user:
        return jsonify({'error': '用户不存在'}), 401
    
    if not hasher.verify_password(password, user['password_hash']):
        return jsonify({'error': '密码错误'}), 401
    
    # 检查是否需要重新哈希
    if hasher.needs_rehash(user['password_hash']):
        user['password_hash'] = hasher.hash_password(password)
        # 保存更新
    
    return jsonify({'message': '登录成功'})
```

#### Node.js 密码验证实现

```javascript
// password-hasher.js
const bcrypt = require('bcrypt');
const argon2 = require('argon2');

class BcryptPasswordHasher {
  constructor(rounds = 12) {
    this.rounds = rounds;
  }

  async hash(password) {
    return bcrypt.hash(password, this.rounds);
  }

  async verify(password, hash) {
    return bcrypt.compare(password, hash);
  }

  needsRehash(hash) {
    // 检查是否使用当前轮数
    const match = hash.match(/^\$2[aby]\$(\d+)\$/);
    if (match) {
      return parseInt(match[1]) !== this.rounds;
    }
    return true;
  }
}

class Argon2PasswordHasher {
  constructor(options = {}) {
    this.options = {
      type: argon2.arggon2id,
      memoryCost: 65536,   // 64MB
      timeCost: 3,
      parallelism: 4,
      hashLength: 32,
      ...options
    };
  }

  async hash(password) {
    return argon2.hash(password, this.options);
  }

  async verify(hash, password) {
    try {
      return await argon2.verify(hash, password);
    } catch {
      return false;
    }
  }

  needsRehash(hash) {
    return argon2.needsRehash(hash, this.options);
  }
}

// Express 集成示例
const express = require('express');
const app = express();
app.use(express.json());

const hasher = new BcryptPasswordHasher(12);
// 或使用 argon2: const hasher = new Argon2PasswordHasher();

// 用户数据库（示例）
const users = new Map();

// 注册
app.post('/register', async (req, res) => {
  const { email, password } = req.body;

  // 验证密码强度
  const strength = checkPasswordStrength(password);
  if (!strength.valid) {
    return res.status(400).json({ 
      error: strength.message,
      suggestions: strength.suggestions 
    });
  }

  // 检查用户是否存在
  if (users.has(email)) {
    return res.status(400).json({ error: '用户已存在' });
  }

  // 哈希密码
  const hash = await hasher.hash(password);

  // 存储用户
  users.set(email, {
    email,
    passwordHash: hash,
    createdAt: new Date().toISOString()
  });

  res.json({ 
    message: '注册成功',
    strength: strength.label 
  });
});

// 登录
app.post('/login', async (req, res) => {
  const { email, password } = req.body;

  const user = users.get(email);
  if (!user) {
    return res.status(401).json({ error: '用户不存在' });
  }

  const valid = await hasher.verify(password, user.passwordHash);
  if (!valid) {
    return res.status(401).json({ error: '密码错误' });
  }

  // 检查是否需要重新哈希
  if (hasher.needsRehash(user.passwordHash)) {
    user.passwordHash = await hasher.hash(password);
    // 保存更新
    console.log('密码哈希已更新');
  }

  res.json({ message: '登录成功' });
});

module.exports = { BcryptPasswordHasher, Argon2PasswordHasher };
```

---

### 3. 密码重置流程

**安全原则**：
1. 重置令牌一次性使用
2. 令牌有效期短（15-60分钟）
3. 不泄露用户存在性
4. 记录所有重置操作

#### 密码重置实现（Python）

```python
# password_reset.py
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict
from dataclasses import dataclass
import hashlib

@dataclass
class ResetToken:
    """重置令牌"""
    token_hash: str       # 令牌哈希（存储用）
    user_id: str          # 用户ID
    created_at: float     # 创建时间戳
    expires_at: float     # 过期时间戳
    used: bool = False    # 是否已使用

class PasswordResetService:
    """密码重置服务"""
    
    def __init__(
        self,
        token_expiry_minutes: int = 30,
        token_length: int = 32
    ):
        self.token_expiry = token_expiry_minutes * 60  # 转换为秒
        self.token_length = token_length
        # 实际项目中应使用 Redis
        self._tokens: Dict[str, ResetToken] = {}
    
    def generate_token(self, user_id: str) -> str:
        """
        生成重置令牌
        
        Returns:
            原始令牌（只返回一次，用于发送邮件）
        """
        # 生成随机令牌
        token = secrets.token_urlsafe(self.token_length)
        
        # 存储哈希值（不存储原始令牌）
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        now = time.time()
        reset_token = ResetToken(
            token_hash=token_hash,
            user_id=user_id,
            created_at=now,
            expires_at=now + self.token_expiry
        )
        
        # 使旧令牌失效
        self._invalidate_user_tokens(user_id)
        
        # 存储新令牌
        self._tokens[token_hash] = reset_token
        
        return token
    
    def validate_token(self, token: str) -> Optional[str]:
        """
        验证重置令牌
        
        Returns:
            用户ID（如果有效），否则返回 None
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        reset_token = self._tokens.get(token_hash)
        if not reset_token:
            return None
        
        # 检查是否过期
        if time.time() > reset_token.expires_at:
            del self._tokens[token_hash]
            return None
        
        # 检查是否已使用
        if reset_token.used:
            return None
        
        return reset_token.user_id
    
    def consume_token(self, token: str) -> Optional[str]:
        """
        消费令牌（一次性使用）
        
        Returns:
            用户ID（如果有效），否则返回 None
        """
        user_id = self.validate_token(token)
        if not user_id:
            return None
        
        # 标记为已使用
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self._tokens[token_hash].used = True
        
        # 记录日志
        self._log_reset_event(user_id, 'token_used')
        
        return user_id
    
    def _invalidate_user_tokens(self, user_id: str):
        """使该用户的所有旧令牌失效"""
        to_delete = [
            h for h, t in self._tokens.items() 
            if t.user_id == user_id
        ]
        for h in to_delete:
            del self._tokens[h]
    
    def _log_reset_event(self, user_id: str, event: str):
        """记录重置事件"""
        # 实际项目中应写入审计日志
        print(f"[RESET] {datetime.now().isoformat()} - User: {user_id} - Event: {event}")


# Flask 集成示例
from flask import Flask, request, jsonify, current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
reset_service = PasswordResetService(token_expiry_minutes=30)

def send_reset_email(email: str, token: str):
    """发送重置邮件"""
    reset_url = f"https://yourdomain.com/reset-password?token={token}"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "密码重置请求"
    msg['From'] = "noreply@yourdomain.com"
    msg['To'] = email
    
    html = f"""
    <html>
      <body>
        <h2>密码重置</h2>
        <p>您收到这封邮件是因为有人请求重置您的密码。</p>
        <p>请点击以下链接重置密码（30分钟内有效）：</p>
        <a href="{reset_url}">{reset_url}</a>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # 发送邮件（实际项目中使用邮件服务）
    # with smtplib.SMTP('smtp.example.com', 587) as server:
    #     server.send_message(msg)
    print(f"发送重置邮件到 {email}: {reset_url}")

@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    """请求密码重置"""
    email = request.json.get('email')
    
    # 查找用户
    user = users_db.get(email)
    
    # 无论用户是否存在，都返回相同响应（防止用户枚举）
    response = {'message': '如果该邮箱已注册，您将收到重置邮件'}
    
    if user:
        # 生成令牌
        token = reset_service.generate_token(user['id'])
        
        # 发送邮件
        send_reset_email(email, token)
        
        # 记录日志
        print(f"[RESET_REQUEST] {email} at {datetime.now()}")
    
    return jsonify(response)

@app.route('/reset-password', methods=['POST'])
def reset_password():
    """执行密码重置"""
    token = request.json.get('token')
    new_password = request.json.get('new_password')
    
    # 验证密码强度
    validator = PasswordValidator(min_length=12)
    valid, message, _ = validator.validate(new_password)
    if not valid:
        return jsonify({'error': message}), 400
    
    # 验证令牌
    user_id = reset_service.consume_token(token)
    if not user_id:
        return jsonify({'error': '无效或已过期的重置链接'}), 400
    
    # 更新密码
    user = users_db.get(user_id)
    if user:
        hasher = PasswordHasher()
        user['password_hash'] = hasher.hash_password(new_password).hash
        user['password_changed_at'] = datetime.now().isoformat()
    
    return jsonify({'message': '密码已重置，请使用新密码登录'})
```

---

### 4. 多因素认证（MFA）推荐

**免费 MFA 方案对比**

| 方案 | 类型 | 免费额度 | 集成难度 | 推荐场景 |
|------|------|---------|---------|---------|
| **TOTP (Google Authenticator)** | 时间令牌 | 无限 | 低 | 通用首选 |
| **WebAuthn (硬件密钥)** | 硬件 | 无限 | 中 | 高安全需求 |
| **短信验证** | 短信 | 收费 | 低 | 备用方案 |
| **邮件验证码** | 邮件 | 免费 | 低 | 低安全场景 |

#### TOTP 实现（Python）

```python
# totp_service.py
import pyotp
import qrcode
import io
import base64
from typing import Tuple

class TOTPService:
    """TOTP 双因素认证服务"""
    
    def __init__(self, issuer: str = "MyApp"):
        self.issuer = issuer
    
    def generate_secret(self) -> str:
        """生成 TOTP 密钥"""
        return pyotp.random_base32()
    
    def get provisioning_uri(self, secret: str, email: str) -> str:
        """生成配对 URI"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=self.issuer
        )
    
    def generate_qr_code(self, secret: str, email: str) -> str:
        """
        生成 QR 码（Base64 编码图片）
        
        Returns:
            Base64 编码的 PNG 图片
        """
        uri = self.get_provisioning_uri(secret, email)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 转换为 Base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_code(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        验证 TOTP 代码
        
        Args:
            secret: TOTP 密钥
            code: 用户输入的 6 位代码
            valid_window: 有效窗口（前后多少个周期）
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)


# Flask MFA 集成示例
@app.route('/mfa/setup', methods=['POST'])
def setup_mfa():
    """设置 MFA"""
    user_id = get_current_user_id()  # 假设已登录
    user = users_db.get(user_id)
    
    totp = TOTPService(issuer="MyApp")
    
    # 生成密钥
    secret = totp.generate_secret()
    
    # 临时存储（需要用户验证后才正式启用）
    user['mfa_secret_pending'] = secret
    
    # 生成 QR 码
    qr_code = totp.generate_qr_code(secret, user['email'])
    
    return jsonify({
        'secret': secret,  # 用于手动输入
        'qr_code': f"data:image/png;base64,{qr_code}"
    })

@app.route('/mfa/verify', methods=['POST'])
def verify_mfa():
    """验证并启用 MFA"""
    user_id = get_current_user_id()
    user = users_db.get(user_id)
    code = request.json.get('code')
    
    secret = user.get('mfa_secret_pending') or user.get('mfa_secret')
    if not secret:
        return jsonify({'error': 'MFA 未设置'}), 400
    
    totp = TOTPService()
    if totp.verify_code(secret, code):
        # 启用 MFA
        if user.get('mfa_secret_pending'):
            user['mfa_secret'] = user.pop('mfa_secret_pending')
            user['mfa_enabled'] = True
        
        return jsonify({'message': 'MFA 验证成功'})
    
    return jsonify({'error': '验证码错误'}), 400
```

---

### 5. 常见密码黑名单

基于 RockYou 和 HIBP 数据的 Top 500 常见密码：

```python
# common_passwords.py

# Top 200 最常见密码（截断版，实际应维护完整列表）
TOP_COMMON_PASSWORDS = {
    '123456', 'password', '12345678', 'qwerty', '123456789',
    '12345', '1234', '111111', '1234567', 'dragon',
    '123123', 'baseball', 'abc123', 'football', 'monkey',
    'letmein', '696969', 'shadow', 'master', '666666',
    'qwertyuiop', '123321', 'mustang', '1234567890', 'michael',
    '654321', 'pussy', 'superman', '1qaz2wsx', '7777777',
    'admin', 'administrator', 'welcome', 'login', 'passw0rd',
    'password1', 'password123', 'admin123', 'root', 'toor',
    'iloveyou', 'sunshine', 'princess', 'starwars', 'batman',
    'trustno1', 'ashley', 'bailey', 'shadow1', 'jesus',
    'ninja', 'mustang', 'password1', 'password123', 'abc123',
    'letmein', 'monkey', 'dragon', '111111', 'baseball',
    'qwerty', 'football', 'master', 'superman', 'access',
    'yankees', 'buster', 'charlie', 'robert', 'thomas',
    'hunter', 'ranger', 'jordan', 'harley', 'hockey',
    'killer', 'george', 'andrew', 'michelle', 'joshua',
    'pepper', 'summer', 'winter', 'spring', 'autumn',
    # ... 完整列表应有 500-1000 个
}

def is_common_password(password: str) -> bool:
    """检查是否为常见密码"""
    normalized = password.lower().strip()
    return normalized in TOP_COMMON_PASSWORDS

def contains_common_pattern(password: str) -> bool:
    """检查是否包含常见密码模式"""
    normalized = password.lower()
    
    # 检查是否包含常见密码
    for common in TOP_COMMON_PASSWORDS:
        if len(common) >= 6 and common in normalized:
            return True
    
    # 检查键盘模式
    keyboard_patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', '123456', '098765',
        'qwertz', 'azerty', '!@#$%^', 'qwertyuiop'
    ]
    for pattern in keyboard_patterns:
        if pattern in normalized:
            return True
    
    return False
```

---

## 验证方法

### 自动化测试脚本

```bash
#!/bin/bash
# test_password_policy.sh

echo "=== 密码策略测试 ==="

# 测试弱密码拒绝
echo -e "\n[测试1] 弱密码应被拒绝"
curl -s -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test1@test.com","password":"123456"}' | jq .

# 测试短密码拒绝
echo -e "\n[测试2] 短密码应被拒绝"
curl -s -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test2@test.com","password":"Short1!"}' | jq .

# 测试强密码接受
echo -e "\n[测试3] 强密码应被接受"
curl -s -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@test.com","password":"MySecureP@ss2024!"}' | jq .

# 测试密码验证
echo -e "\n[测试4] 正确密码应能登录"
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@test.com","password":"MySecureP@ss2024!"}' | jq .

# 测试错误密码拒绝
echo -e "\n[测试5] 错误密码应被拒绝"
curl -s -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@test.com","password":"WrongPassword!"}' | jq .

# 测试密码重置流程
echo -e "\n[测试6] 密码重置请求"
curl -s -X POST http://localhost:5000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email":"test3@test.com"}' | jq .

echo -e "\n=== 测试完成 ==="
```

### 密码哈希验证

```python
# test_hash_verification.py
import time
from password_hasher import PasswordHasher

def test_bcrypt_timing():
    """测试 bcrypt 哈希时间"""
    hasher = PasswordHasher(rounds=12)
    password = "TestPassword123!"
    
    # 哈希时间
    start = time.time()
    hashed = hasher.hash_password(password)
    hash_time = time.time() - start
    print(f"哈希时间: {hash_time:.3f}s")
    
    # 验证时间（正确密码）
    start = time.time()
    valid = hasher.verify_password(password, hashed.hash)
    verify_time = time.time() - start
    print(f"验证时间（正确）: {verify_time:.3f}s")
    
    # 验证时间（错误密码）
    start = time.time()
    valid = hasher.verify_password("WrongPassword", hashed.hash)
    verify_time_wrong = time.time() - start
    print(f"验证时间（错误）: {verify_time_wrong:.3f}s")
    
    # 正确和错误密码验证时间应相近（防止时序攻击）
    assert abs(verify_time - verify_time_wrong) < 0.1, "可能存在时序攻击漏洞"

if __name__ == "__main__":
    test_bcrypt_timing()
```

---

## 成本估算

| 指标 | 免费方案 | 备注 |
|------|---------|------|
| 密码哈希 | $0 | bcrypt/argon2 开源库 |
| 密码验证 | $0 | 无需外部服务 |
| 密码重置 | $0 | 邮件服务通常有免费额度 |
| TOTP MFA | $0 | 开源库，无需服务费 |
| 总成本 | $0 | 完全免费 |

---

## 迁出成本

- **难度**：低
- **时间**：< 1小时
- **步骤**：
  1. 导出用户数据（邮箱、哈希值）
  2. 在新系统配置相同的哈希算法
  3. 验证密码迁移兼容性
  4. 要求用户首次登录时重置密码（可选）

---

## 与其他武器配合

- **前置**：无（认证基础）
- **后置**：
  - [会话管理](./session-management.md)
  - [OAuth 集成](./oauth-integration.md)
  - [权限控制](./access-control.md)
- **配合**：
  - [API 限流](./rate-limiting.md) - 防止暴力破解
  - [日志审计](./audit-logging.md) - 记录认证事件

---

## 常见问题

**Q: bcrypt 和 argon2 应该选哪个？**
A: 
- 通用场景：**bcrypt**（成熟稳定、生态完善）
- 高安全需求：**argon2**（抗 GPU 攻击、内存硬）
- 避免使用：MD5、SHA1、SHA256（不适合密码哈希）

**Q: 密码长度限制多少合适？**
A: 最小 12 位，最大 128 位。最大限制是防止 DoS 攻击（哈希长字符串消耗资源）。

**Q: 如何处理密码重置邮件延迟？**
A: 
1. 设置合理的过期时间（30分钟）
2. 允许用户请求重发
3. 显示"如果邮箱存在，您将收到邮件"避免用户枚举

**Q: MFA 是必须的吗？**
A: 不强制，但强烈建议。对于敏感操作（支付、修改密码）应要求 MFA 验证。

**Q: 如何防止暴力破解？**
A: 
1. 登录限流（5次/分钟/IP）
2. 账户锁定（10次失败后锁定15分钟）
3. 验证码（多次失败后显示）
4. 密码哈希使用足够高的成本参数

---

## 推荐实现

### Python
- **bcrypt**: `pip install bcrypt`
- **argon2**: `pip install argon2-cffi`
- **TOTP**: `pip install pyotp qrcode`

### Node.js
- **bcrypt**: `npm install bcrypt`
- **argon2**: `npm install argon2`
- **TOTP**: `npm install otplib qrcode`

### 前端
- **密码强度检测**: 本文提供的 TypeScript 实现
- **TOTP 输入**: `react-otp-input`

---

## 相关资源

**安全标准**
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Have I Been Pwned API](https://haveibeenpwned.com/API/v3) - 检查密码是否泄露

**开源项目**
- [passlib](https://passlib.readthedocs.io/) - Python 密码哈希库
- [bcrypt](https://github.com/pyca/bcrypt) - bcrypt Python 实现
- [argon2](https://github.com/P-H-C/phc-winner-argon2) - Argon2 官方实现

**测试工具**
- [How Secure Is My Password](https://www.security.org/how-secure-is-my-password/)
- [Kaspersky Password Checker](https://password.kaspersky.com/)

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
