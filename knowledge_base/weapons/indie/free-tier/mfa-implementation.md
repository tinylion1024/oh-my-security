# MFA 实现指南 (多因素认证)

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费（TOTP） / $0-15/月（短信/邮件）
- **实施时间**: 2-4小时
- **维护成本**: 1小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
解决账户被盗、密码泄露、身份冒用等安全问题，为用户账户提供第二层安全防护，适用于所有需要增强身份验证的场景。

## 认证方式对比

### 快速选型表

| 认证方式 | 实现复杂度 | 安全性评级 | 用户体验 | 成本 | 独立开发者推荐度 |
|---------|-----------|-----------|---------|------|----------------|
| **TOTP** | ⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐ 好 | ✅ 免费 | ⭐⭐⭐⭐⭐ |
| **短信 OTP** | ⭐ 简单 | ⭐⭐⭐ 中高 | ⭐⭐⭐⭐⭐ 最好 | 💰 按量付费 | ⭐⭐⭐ |
| **邮件 OTP** | ⭐ 简单 | ⭐⭐⭐ 中 | ⭐⭐⭐ 一般 | ✅ 免费 | ⭐⭐⭐⭐ |
| **WebAuthn** | ⭐⭐⭐⭐ 复杂 | ⭐⭐⭐⭐⭐ 最高 | ⭐⭐⭐⭐ 好 | ✅ 免费 | ⭐⭐⭐ |
| **备用恢复码** | ⭐ 简单 | ⭐⭐⭐⭐ 高 | ⭐⭐ 一般 | ✅ 免费 | ⭐⭐⭐⭐⭐ |

### 详细对比

#### 1. TOTP (Time-based One-Time Password)

**优点**：
- 完全免费，无第三方依赖
- 离线可用，无需网络
- 业界标准，兼容 Google Authenticator、Authy、1Password 等
- 安全性高，每 30 秒更换一次

**缺点**：
- 需要用户安装认证器 App
- 手机丢失时需要备用恢复码
- 时间同步问题可能导致验证失败

**适用场景**：
- 所有 Web 应用
- 企业内部系统
- 高安全性要求的场景

---

#### 2. 短信 OTP

**优点**：
- 用户无需安装额外 App
- 覆盖所有手机用户
- 实现简单

**缺点**：
- 有成本（按条计费）
- SIM 卡劫持风险
- 依赖网络信号
- 国际短信成本高

**适用场景**：
- 大众用户应用
- 金融类应用
- 用户群体手机普及率高的地区

---

#### 3. 邮件 OTP

**优点**：
- 免费（利用现有邮件服务）
- 无需额外硬件
- 用户已有邮箱

**缺点**：
- 实时性差
- 邮件可能进入垃圾箱
- 邮箱账户本身的安全性

**适用场景**：
- 作为备用验证方式
- 低频操作验证
- 企业内部系统

---

## 快速上手（5分钟）

### TOTP 快速实现（Python）

```python
# totp_quick_start.py
import pyotp
import qrcode
import io
import base64

# 1. 生成用户密钥（每个用户唯一）
def generate_totp_secret():
    """生成 TOTP 密钥"""
    return pyotp.random_base32()

# 2. 生成二维码 URI
def get_totp_uri(secret, email, issuer="MyApp"):
    """生成 otpauth:// URI"""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)

# 3. 生成二维码图片
def generate_qr_code(uri):
    """生成二维码（返回 base64）"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    
    return base64.b64encode(buffer.getvalue()).decode()

# 4. 验证 TOTP 码
def verify_totp(secret, code):
    """验证 TOTP 代码"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # 允许前后1个窗口

# 使用示例
if __name__ == "__main__":
    # 生成密钥
    secret = generate_totp_secret()
    print(f"用户密钥: {secret}")
    
    # 生成二维码
    uri = get_totp_uri(secret, "user@example.com")
    qr_base64 = generate_qr_code(uri)
    print(f"二维码已生成（Base64长度: {len(qr_base64)}）")
    
    # 验证测试
    # 用户用 Google Authenticator 扫描二维码后输入6位数字
    test_code = input("请输入认证器显示的6位数字: ")
    if verify_totp(secret, test_code):
        print("✅ 验证成功！")
    else:
        print("❌ 验证失败！")
```

### TOTP 快速实现（Node.js）

```javascript
// totp_quick_start.js
const otplib = require('otplib');
const QRCode = require('qrcode');

// 1. 生成用户密钥
function generateTOTPSecret() {
  return otplib.authenticator.generateSecret();
}

// 2. 生成二维码 URI
function getTOTPUri(secret, email, issuer = 'MyApp') {
  return otplib.authenticator.keyuri(email, issuer, secret);
}

// 3. 生成二维码（返回 Data URL）
async function generateQRCode(uri) {
  return await QRCode.toDataURL(uri);
}

// 4. 验证 TOTP 码
function verifyTOTP(secret, code) {
  return otplib.authenticator.check(code, secret);
}

// 使用示例
async function main() {
  // 生成密钥
  const secret = generateTOTPSecret();
  console.log('用户密钥:', secret);

  // 生成二维码
  const uri = getTOTPUri(secret, 'user@example.com');
  const qrDataUrl = await generateQRCode(uri);
  console.log('二维码已生成');

  // 验证测试
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });

  readline.question('请输入认证器显示的6位数字: ', (code) => {
    if (verifyTOTP(secret, code)) {
      console.log('✅ 验证成功！');
    } else {
      console.log('❌ 验证失败！');
    }
    readline.close();
  });
}

main();
```

---

## 详细方案

### 方案架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    MFA 认证流程架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户登录                                                         │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────┐                                                │
│  │ 用户名密码   │  ← 第一因素：知识因素                           │
│  └─────────────┘                                                │
│      │                                                          │
│      ▼ 验证通过                                                  │
│  ┌─────────────┐                                                │
│  │ 检查MFA状态 │                                                │
│  └─────────────┘                                                │
│      │                                                          │
│      ├── 未启用 → 登录成功                                       │
│      │                                                          │
│      └── 已启用                                                  │
│           │                                                     │
│           ▼                                                     │
│      ┌─────────────────────────────────────┐                    │
│      │         第二因素验证选择              │                   │
│      ├─────────┬─────────┬────────────────┤                    │
│      │  TOTP   │ 短信OTP │   邮件OTP      │                    │
│      └─────────┴─────────┴────────────────┘                    │
│           │                                                     │
│           ▼ 验证通过                                             │
│      ┌─────────────┐                                            │
│      │  登录成功   │                                            │
│      └─────────────┘                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 数据库设计

```sql
-- 用户 MFA 配置表
CREATE TABLE user_mfa (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    
    -- TOTP 配置
    totp_secret VARCHAR(32),          -- Base32 编码的密钥
    totp_enabled BOOLEAN DEFAULT FALSE,
    
    -- 短信验证配置
    phone_number VARCHAR(20),
    sms_enabled BOOLEAN DEFAULT FALSE,
    
    -- 邮件验证配置
    email_verified BOOLEAN DEFAULT FALSE,
    email_enabled BOOLEAN DEFAULT FALSE,
    
    -- 备用恢复码
    recovery_codes JSONB,             -- ["code1", "code2", ...]（哈希后存储）
    
    -- 元数据
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP,
    
    -- 主验证方式
    primary_method VARCHAR(20) DEFAULT 'totp'  -- totp, sms, email
);

-- MFA 使用日志
CREATE TABLE mfa_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    method VARCHAR(20),               -- totp, sms, email, recovery
    success BOOLEAN,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_mfa_user ON user_mfa(user_id);
CREATE INDEX idx_mfa_logs_user ON mfa_logs(user_id, created_at);
```

### Python 完整实现

#### 1. TOTP 服务类

```python
# mfa_service.py
import pyotp
import qrcode
import io
import base64
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from dataclasses import dataclass

@dataclass
class MFAConfig:
    """MFA 配置"""
    totp_enabled: bool = False
    sms_enabled: bool = False
    email_enabled: bool = False
    primary_method: str = 'totp'

class TOTPService:
    """TOTP 认证服务"""
    
    def __init__(self, issuer: str = "MyApp"):
        self.issuer = issuer
    
    def generate_secret(self) -> str:
        """生成新的 TOTP 密钥"""
        return pyotp.random_base32()
    
    def get_provisioning_uri(self, secret: str, email: str) -> str:
        """生成 otpauth:// URI"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name=self.issuer)
    
    def generate_qr_code(self, secret: str, email: str) -> str:
        """生成二维码（Base64 编码）"""
        uri = self.get_provisioning_uri(secret, email)
        
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=5,
            error_correction=qrcode.constants.ERROR_CORRECT_L
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify(self, secret: str, code: str, valid_window: int = 1) -> bool:
        """
        验证 TOTP 代码
        
        Args:
            secret: 用户密钥
            code: 用户输入的6位数字
            valid_window: 允许的时间窗口（前后多少个30秒周期）
        """
        if not code or len(code) != 6 or not code.isdigit():
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=valid_window)
    
    def get_current_code(self, secret: str) -> str:
        """获取当前 TOTP 码（仅用于测试）"""
        totp = pyotp.TOTP(secret)
        return totp.now()
```

#### 2. 备用恢复码服务

```python
# recovery_codes.py
import secrets
import hashlib
from typing import List, Tuple
import json

class RecoveryCodesService:
    """备用恢复码服务"""
    
    @staticmethod
    def generate_codes(count: int = 10) -> Tuple[List[str], List[str]]:
        """
        生成备用恢复码
        
        Returns:
            (原始码列表, 哈希后码列表)
        """
        codes = []
        hashed_codes = []
        
        for _ in range(count):
            # 生成 8 位字母数字码
            code = secrets.token_hex(4).upper()  # 8字符，如 "A1B2C3D4"
            codes.append(code)
            # 存储 SHA256 哈希
            hashed_codes.append(hashlib.sha256(code.encode()).hexdigest())
        
        return codes, hashed_codes
    
    @staticmethod
    def verify_code(code: str, hashed_codes: List[str]) -> Tuple[bool, List[str]]:
        """
        验证恢复码
        
        Returns:
            (是否验证成功, 更新后的哈希列表)
        """
        code_hash = hashlib.sha256(code.upper().encode()).hexdigest()
        
        if code_hash in hashed_codes:
            # 使用后移除
            hashed_codes.remove(code_hash)
            return True, hashed_codes
        
        return False, hashed_codes
    
    @staticmethod
    def format_for_display(codes: List[str]) -> str:
        """格式化恢复码供用户保存"""
        formatted = "备用恢复码（请安全保存）：\n\n"
        for i, code in enumerate(codes, 1):
            formatted += f"{i:2d}. {code[:4]}-{code[4:]}\n"
        formatted += "\n⚠️ 每个码只能使用一次，请妥善保管！"
        return formatted
```

#### 3. 短信 OTP 服务（Twilio 免费层）

```python
# sms_otp_service.py
import random
import string
from datetime import datetime, timedelta
from typing import Optional
import os

# Twilio SDK
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

class SMSOTPService:
    """短信 OTP 服务"""
    
    def __init__(self):
        # Twilio 配置
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        # 初始化客户端
        if self.account_sid and self.auth_token:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
    
    def generate_otp(self, length: int = 6) -> str:
        """生成 OTP 码"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, phone_number: str, otp: str) -> dict:
        """
        发送 OTP 短信
        
        Returns:
            {'success': bool, 'message_id': str, 'error': str}
        """
        if not self.client:
            # 开发环境：打印到控制台
            print(f"[DEV] OTP for {phone_number}: {otp}")
            return {'success': True, 'message_id': 'dev_mode'}
        
        try:
            message = self.client.messages.create(
                body=f"您的验证码是 {otp}，有效期5分钟。如非本人操作请忽略。",
                from_=self.from_number,
                to=phone_number
            )
            
            return {
                'success': True,
                'message_id': message.sid
            }
            
        except TwilioRestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def format_phone_number(self, phone: str) -> str:
        """格式化手机号"""
        # 移除空格和特殊字符
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        
        # 中国手机号格式化
        if cleaned.startswith('1') and len(cleaned) == 11:
            return f'+86{cleaned}'
        
        # 已有国家码
        if cleaned.startswith('+'):
            return cleaned
        
        # 默认添加中国区号
        return f'+86{cleaned}'
```

#### 4. 邮件 OTP 服务（SendGrid 免费层）

```python
# email_otp_service.py
import random
import string
from datetime import datetime, timedelta
from typing import Optional
import os

# SendGrid SDK
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class EmailOTPService:
    """邮件 OTP 服务"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@example.com')
        
        # 初始化客户端
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
        else:
            self.client = None
    
    def generate_otp(self, length: int = 6) -> str:
        """生成 OTP 码"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp(self, email: str, otp: str, username: str = None) -> dict:
        """
        发送 OTP 邮件
        
        Returns:
            {'success': bool, 'message_id': str, 'error': str}
        """
        subject = "您的验证码"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">身份验证</h2>
            <p>尊敬的 {username or '用户'}，</p>
            <p>您的验证码是：</p>
            <div style="background: #f5f5f5; padding: 20px; text-align: center; 
                        font-size: 32px; font-weight: bold; letter-spacing: 5px; 
                        border-radius: 8px; margin: 20px 0;">
                {otp}
            </div>
            <p style="color: #666; font-size: 14px;">
                此验证码将在 <strong>5分钟</strong> 后失效。<br>
                如非本人操作，请忽略此邮件。
            </p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="color: #999; font-size: 12px;">
                此邮件由系统自动发送，请勿回复。
            </p>
        </div>
        """
        
        if not self.client:
            # 开发环境：打印到控制台
            print(f"[DEV] OTP for {email}: {otp}")
            return {'success': True, 'message_id': 'dev_mode'}
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.client.send(message)
            
            return {
                'success': True,
                'message_id': response.headers.get('X-Message-Id', 'unknown')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

#### 5. 完整 MFA 管理器

```python
# mfa_manager.py
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import json

from .totp_service import TOTPService
from .recovery_codes import RecoveryCodesService
from .sms_otp_service import SMSOTPService
from .email_otp_service import EmailOTPService

@dataclass
class MFAStatus:
    """MFA 状态"""
    enabled: bool
    method: str
    backup_codes_remaining: int
    last_used: Optional[datetime]

class MFAManager:
    """MFA 综合管理器"""
    
    # OTP 有效期配置
    OTP_EXPIRY_MINUTES = 5
    MAX_OTP_ATTEMPTS = 5
    
    def __init__(
        self,
        db_connection,
        issuer: str = "MyApp",
        redis_client = None
    ):
        self.db = db_connection
        self.redis = redis_client
        
        self.totp = TOTPService(issuer)
        self.recovery = RecoveryCodesService()
        self.sms = SMSOTPService()
        self.email = EmailOTPService()
    
    # ========== TOTP 管理 ==========
    
    def setup_totp(self, user_id: int, email: str) -> Dict[str, Any]:
        """
        设置 TOTP
        
        Returns:
            {
                'secret': str,          # 密钥（需要用户确认后存储）
                'qr_code': str,         # Base64 二维码
                'manual_code': str,     # 手动输入码
            }
        """
        secret = self.totp.generate_secret()
        qr_code = self.totp.generate_qr_code(secret, email)
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'manual_code': secret,  # 供无法扫描二维码的用户手动输入
        }
    
    def enable_totp(self, user_id: int, secret: str, verify_code: str) -> Dict[str, Any]:
        """
        启用 TOTP（需要验证）
        
        Returns:
            {'success': bool, 'recovery_codes': list, 'error': str}
        """
        # 验证 TOTP 码
        if not self.totp.verify(secret, verify_code):
            return {'success': False, 'error': '验证码错误'}
        
        # 生成备用恢复码
        codes, hashed_codes = self.recovery.generate_codes()
        
        # 存储到数据库
        self.db.execute("""
            INSERT INTO user_mfa (user_id, totp_secret, totp_enabled, recovery_codes, primary_method)
            VALUES (%s, %s, TRUE, %s, 'totp')
            ON CONFLICT (user_id) 
            DO UPDATE SET totp_secret = %s, totp_enabled = TRUE, recovery_codes = %s, updated_at = NOW()
        """, (user_id, secret, json.dumps(hashed_codes), secret, json.dumps(hashed_codes)))
        
        return {
            'success': True,
            'recovery_codes': codes  # 返回原始码供用户保存
        }
    
    # ========== 短信 OTP 管理 ==========
    
    def send_sms_otp(self, user_id: int, phone_number: str) -> Dict[str, Any]:
        """发送短信 OTP"""
        # 检查发送频率限制
        rate_key = f"sms_otp_limit:{user_id}"
        if self.redis:
            count = self.redis.incr(rate_key)
            if count == 1:
                self.redis.expire(rate_key, 60)  # 每分钟限制
            if count > 3:
                return {'success': False, 'error': '发送过于频繁，请稍后再试'}
        
        # 生成并存储 OTP
        otp = self.sms.generate_otp()
        expiry = datetime.utcnow() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
        
        if self.redis:
            self.redis.setex(
                f"sms_otp:{user_id}",
                self.OTP_EXPIRY_MINUTES * 60,
                json.dumps({'otp': otp, 'expires_at': expiry.isoformat()})
            )
        
        # 发送短信
        formatted_phone = self.sms.format_phone_number(phone_number)
        result = self.sms.send_otp(formatted_phone, otp)
        
        return result
    
    def verify_sms_otp(self, user_id: int, code: str) -> bool:
        """验证短信 OTP"""
        if self.redis:
            stored = self.redis.get(f"sms_otp:{user_id}")
            if not stored:
                return False
            
            data = json.loads(stored)
            if data['otp'] == code:
                self.redis.delete(f"sms_otp:{user_id}")
                return True
        
        return False
    
    # ========== 邮件 OTP 管理 ==========
    
    def send_email_otp(self, user_id: int, email: str, username: str = None) -> Dict[str, Any]:
        """发送邮件 OTP"""
        # 检查发送频率限制
        rate_key = f"email_otp_limit:{user_id}"
        if self.redis:
            count = self.redis.incr(rate_key)
            if count == 1:
                self.redis.expire(rate_key, 60)
            if count > 5:
                return {'success': False, 'error': '发送过于频繁，请稍后再试'}
        
        # 生成并存储 OTP
        otp = self.email.generate_otp()
        
        if self.redis:
            self.redis.setex(
                f"email_otp:{user_id}",
                self.OTP_EXPIRY_MINUTES * 60,
                json.dumps({'otp': otp})
            )
        
        # 发送邮件
        result = self.email.send_otp(email, otp, username)
        
        return result
    
    def verify_email_otp(self, user_id: int, code: str) -> bool:
        """验证邮件 OTP"""
        if self.redis:
            stored = self.redis.get(f"email_otp:{user_id}")
            if not stored:
                return False
            
            data = json.loads(stored)
            if data['otp'] == code:
                self.redis.delete(f"email_otp:{user_id}")
                return True
        
        return False
    
    # ========== 通用验证 ==========
    
    def verify(self, user_id: int, code: str, method: str = None) -> Dict[str, Any]:
        """
        综合验证入口
        
        Args:
            user_id: 用户ID
            code: 验证码
            method: 验证方式（totp/sms/email/recovery），为空则自动检测
        
        Returns:
            {'success': bool, 'method': str, 'error': str}
        """
        # 获取用户 MFA 配置
        mfa_config = self.db.fetch_one("""
            SELECT totp_secret, totp_enabled, recovery_codes, primary_method
            FROM user_mfa WHERE user_id = %s
        """, (user_id,))
        
        if not mfa_config:
            return {'success': False, 'error': 'MFA 未配置'}
        
        # 检查尝试次数
        attempt_key = f"mfa_attempts:{user_id}"
        if self.redis:
            attempts = self.redis.get(attempt_key)
            if attempts and int(attempts) >= self.MAX_OTP_ATTEMPTS:
                return {'success': False, 'error': '尝试次数过多，请稍后再试'}
        
        # 自动检测验证方式
        if method is None:
            if len(code) == 6 and code.isdigit():
                method = mfa_config['primary_method']
            elif len(code) == 8 and code.isalnum():
                method = 'recovery'
            else:
                method = mfa_config['primary_method']
        
        # 验证
        success = False
        
        if method == 'totp' and mfa_config['totp_enabled']:
            success = self.totp.verify(mfa_config['totp_secret'], code)
        
        elif method == 'sms':
            success = self.verify_sms_otp(user_id, code)
        
        elif method == 'email':
            success = self.verify_email_otp(user_id, code)
        
        elif method == 'recovery':
            hashed_codes = json.loads(mfa_config['recovery_codes'] or '[]')
            success, new_codes = self.recovery.verify_code(code, hashed_codes)
            if success:
                # 更新剩余恢复码
                self.db.execute("""
                    UPDATE user_mfa SET recovery_codes = %s, updated_at = NOW()
                    WHERE user_id = %s
                """, (json.dumps(new_codes), user_id))
        
        # 记录尝试
        if self.redis:
            if success:
                self.redis.delete(attempt_key)
                self.db.execute("""
                    UPDATE user_mfa SET last_used_at = NOW() WHERE user_id = %s
                """, (user_id,))
            else:
                self.redis.incr(attempt_key)
                self.redis.expire(attempt_key, 300)  # 5分钟过期
        
        # 记录日志
        self._log_verification(user_id, method, success)
        
        return {
            'success': success,
            'method': method,
            'error': None if success else '验证失败'
        }
    
    def _log_verification(self, user_id: int, method: str, success: bool):
        """记录验证日志"""
        # 实现日志记录
        pass
    
    # ========== 状态查询 ==========
    
    def get_status(self, user_id: int) -> Optional[MFAStatus]:
        """获取用户 MFA 状态"""
        result = self.db.fetch_one("""
            SELECT totp_enabled, sms_enabled, email_enabled, 
                   recovery_codes, primary_method, last_used_at
            FROM user_mfa WHERE user_id = %s
        """, (user_id,))
        
        if not result:
            return None
        
        recovery_codes = json.loads(result['recovery_codes'] or '[]')
        
        return MFAStatus(
            enabled=result['totp_enabled'] or result['sms_enabled'] or result['email_enabled'],
            method=result['primary_method'],
            backup_codes_remaining=len(recovery_codes),
            last_used=result['last_used_at']
        )
    
    def disable_mfa(self, user_id: int, verify_code: str) -> bool:
        """禁用 MFA（需要验证）"""
        result = self.verify(user_id, verify_code)
        
        if result['success']:
            self.db.execute("""
                UPDATE user_mfa 
                SET totp_enabled = FALSE, sms_enabled = FALSE, email_enabled = FALSE,
                    updated_at = NOW()
                WHERE user_id = %s
            """, (user_id,))
            return True
        
        return False
    
    def regenerate_recovery_codes(self, user_id: int, verify_code: str) -> Optional[List[str]]:
        """重新生成备用恢复码"""
        result = self.verify(user_id, verify_code)
        
        if result['success']:
            codes, hashed_codes = self.recovery.generate_codes()
            
            self.db.execute("""
                UPDATE user_mfa SET recovery_codes = %s, updated_at = NOW()
                WHERE user_id = %s
            """, (json.dumps(hashed_codes), user_id))
            
            return codes
        
        return None
```

### Node.js 完整实现

#### 1. TOTP 服务

```javascript
// services/totp.service.js
const otplib = require('otplib');
const QRCode = require('qrcode');

class TOTPService {
  constructor(issuer = 'MyApp') {
    this.issuer = issuer;
  }

  /**
   * 生成新的 TOTP 密钥
   */
  generateSecret() {
    return otplib.authenticator.generateSecret();
  }

  /**
   * 生成二维码
   */
  async generateQRCode(secret, email) {
    const uri = otplib.authenticator.keyuri(email, this.issuer, secret);
    return await QRCode.toDataURL(uri);
  }

  /**
   * 验证 TOTP 码
   */
  verify(secret, code, window = 1) {
    if (!code || code.length !== 6 || !/^\d{6}$/.test(code)) {
      return false;
    }
    return otplib.authenticator.check(code, secret, { window });
  }

  /**
   * 获取当前 TOTP 码（仅用于测试）
   */
  getCurrentCode(secret) {
    return otplib.authenticator.generate(secret);
  }
}

module.exports = TOTPService;
```

#### 2. 备用恢复码服务

```javascript
// services/recovery.service.js
const crypto = require('crypto');

class RecoveryCodesService {
  /**
   * 生成备用恢复码
   */
  generateCodes(count = 10) {
    const codes = [];
    const hashedCodes = [];

    for (let i = 0; i < count; i++) {
      // 生成 8 位字母数字码
      const code = crypto.randomBytes(4).toString('hex').toUpperCase();
      codes.push(code);
      
      // 存储 SHA256 哈希
      const hash = crypto.createHash('sha256').update(code).digest('hex');
      hashedCodes.push(hash);
    }

    return { codes, hashedCodes };
  }

  /**
   * 验证恢复码
   */
  verifyCode(code, hashedCodes) {
    const codeHash = crypto.createHash('sha256').update(code.toUpperCase()).digest('hex');
    
    const index = hashedCodes.indexOf(codeHash);
    if (index !== -1) {
      // 使用后移除
      hashedCodes.splice(index, 1);
      return { valid: true, remaining: hashedCodes };
    }

    return { valid: false, remaining: hashedCodes };
  }

  /**
   * 格式化恢复码供用户保存
   */
  formatForDisplay(codes) {
    let formatted = '备用恢复码（请安全保存）：\n\n';
    codes.forEach((code, i) => {
      formatted += `${(i + 1).toString().padStart(2, ' ')}. ${code.slice(0, 4)}-${code.slice(4)}\n`;
    });
    formatted += '\n⚠️ 每个码只能使用一次，请妥善保管！';
    return formatted;
  }
}

module.exports = RecoveryCodesService;
```

#### 3. 短信 OTP 服务（Twilio）

```javascript
// services/sms.service.js
const twilio = require('twilio');

class SMSOTPService {
  constructor() {
    this.accountSid = process.env.TWILIO_ACCOUNT_SID;
    this.authToken = process.env.TWILIO_AUTH_TOKEN;
    this.fromNumber = process.env.TWILIO_PHONE_NUMBER;
    
    this.client = (this.accountSid && this.authToken) 
      ? twilio(this.accountSid, this.authToken) 
      : null;
  }

  /**
   * 生成 OTP 码
   */
  generateOTP(length = 6) {
    return Array.from({ length }, () => Math.floor(Math.random() * 10)).join('');
  }

  /**
   * 发送 OTP 短信
   */
  async sendOTP(phoneNumber, otp) {
    if (!this.client) {
      // 开发环境
      console.log(`[DEV] OTP for ${phoneNumber}: ${otp}`);
      return { success: true, messageId: 'dev_mode' };
    }

    try {
      const message = await this.client.messages.create({
        body: `您的验证码是 ${otp}，有效期5分钟。如非本人操作请忽略。`,
        from: this.fromNumber,
        to: this.formatPhoneNumber(phoneNumber)
      });

      return { success: true, messageId: message.sid };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * 格式化手机号
   */
  formatPhoneNumber(phone) {
    const cleaned = phone.replace(/[^\d+]/g, '');
    
    // 中国手机号
    if (cleaned.startsWith('1') && cleaned.length === 11) {
      return `+86${cleaned}`;
    }
    
    return cleaned.startsWith('+') ? cleaned : `+86${cleaned}`;
  }
}

module.exports = SMSOTPService;
```

#### 4. 完整 MFA 中间件（Express）

```javascript
// middleware/mfa.middleware.js
const TOTPService = require('../services/totp.service');
const RecoveryCodesService = require('../services/recovery.service');
const SMSOTPService = require('../services/sms.service');

class MFAMiddleware {
  constructor(db, redis, issuer = 'MyApp') {
    this.db = db;
    this.redis = redis;
    this.totp = new TOTPService(issuer);
    this.recovery = new RecoveryCodesService();
    this.sms = new SMSOTPService();
    
    this.OTP_EXPIRY_MINUTES = 5;
    this.MAX_ATTEMPTS = 5;
  }

  /**
   * 检查 MFA 状态
   */
  async checkMFAStatus(req, res, next) {
    const userId = req.user?.id;
    
    if (!userId) {
      return res.status(401).json({ error: '未认证' });
    }

    const result = await this.db.query(
      'SELECT totp_enabled, primary_method, recovery_codes FROM user_mfa WHERE user_id = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      req.mfaRequired = false;
      return next();
    }

    const mfa = result.rows[0];
    req.mfaRequired = mfa.totp_enabled;
    req.mfaMethod = mfa.primary_method;

    next();
  }

  /**
   * MFA 验证中间件
   */
  requireMFA() {
    return async (req, res, next) => {
      const userId = req.user?.id;
      
      if (!userId) {
        return res.status(401).json({ error: '未认证' });
      }

      // 检查是否已通过 MFA 验证
      const mfaVerified = await this.redis.get(`mfa_verified:${userId}`);
      
      if (mfaVerified) {
        return next();
      }

      // 检查 MFA 状态
      const result = await this.db.query(
        'SELECT totp_enabled, totp_secret, recovery_codes FROM user_mfa WHERE user_id = $1',
        [userId]
      );

      if (result.rows.length === 0 || !result.rows[0].totp_enabled) {
        return next();
      }

      return res.status(403).json({ 
        error: '需要 MFA 验证',
        mfaRequired: true
      });
    };
  }

  /**
   * 验证 MFA 代码
   */
  async verifyMFA(req, res) {
    const userId = req.user.id;
    const { code, method } = req.body;

    if (!code) {
      return res.status(400).json({ error: '验证码不能为空' });
    }

    // 检查尝试次数
    const attempts = await this.redis.get(`mfa_attempts:${userId}`);
    if (attempts && parseInt(attempts) >= this.MAX_ATTEMPTS) {
      return res.status(429).json({ error: '尝试次数过多，请稍后再试' });
    }

    // 获取用户 MFA 配置
    const result = await this.db.query(
      'SELECT totp_secret, recovery_codes FROM user_mfa WHERE user_id = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(400).json({ error: 'MFA 未配置' });
    }

    const { totp_secret, recovery_codes } = result.rows[0];
    let success = false;
    let usedMethod = method;

    // 自动检测验证方式
    if (!method) {
      if (/^\d{6}$/.test(code)) {
        usedMethod = 'totp';
      } else if (/^[A-Z0-9]{8}$/i.test(code)) {
        usedMethod = 'recovery';
      } else {
        usedMethod = 'totp';
      }
    }

    // 验证
    if (usedMethod === 'totp') {
      success = this.totp.verify(totp_secret, code);
    } else if (usedMethod === 'recovery') {
      const hashedCodes = recovery_codes || [];
      const result = this.recovery.verifyCode(code, hashedCodes);
      success = result.valid;
      
      if (success) {
        // 更新剩余恢复码
        await this.db.query(
          'UPDATE user_mfa SET recovery_codes = $1 WHERE user_id = $2',
          [JSON.stringify(result.remaining), userId]
        );
      }
    }

    if (success) {
      // 清除尝试计数
      await this.redis.del(`mfa_attempts:${userId}`);
      
      // 设置 MFA 验证通过状态（有效期与 session 一致）
      await this.redis.setex(`mfa_verified:${userId}`, 3600, '1');
      
      // 更新最后使用时间
      await this.db.query(
        'UPDATE user_mfa SET last_used_at = NOW() WHERE user_id = $1',
        [userId]
      );

      // 记录日志
      await this.logVerification(userId, usedMethod, true, req.ip);

      return res.json({ success: true, method: usedMethod });
    } else {
      // 增加尝试计数
      await this.redis.incr(`mfa_attempts:${userId}`);
      await this.redis.expire(`mfa_attempts:${userId}`, 300);

      // 记录日志
      await this.logVerification(userId, usedMethod, false, req.ip);

      return res.status(400).json({ success: false, error: '验证码错误' });
    }
  }

  /**
   * 设置 TOTP
   */
  async setupTOTP(req, res) {
    const userId = req.user.id;
    const email = req.user.email;

    const secret = this.totp.generateSecret();
    const qrCode = await this.totp.generateQRCode(secret, email);

    // 临时存储密钥，等待确认
    await this.redis.setex(`totp_setup:${userId}`, 300, secret);

    return res.json({
      secret,
      qrCode,
      manualCode: secret
    });
  }

  /**
   * 确认并启用 TOTP
   */
  async enableTOTP(req, res) {
    const userId = req.user.id;
    const { code } = req.body;

    // 获取临时存储的密钥
    const secret = await this.redis.get(`totp_setup:${userId}`);
    
    if (!secret) {
      return res.status(400).json({ error: '设置已过期，请重新开始' });
    }

    // 验证 TOTP 码
    if (!this.totp.verify(secret, code)) {
      return res.status(400).json({ error: '验证码错误' });
    }

    // 生成备用恢复码
    const { codes, hashedCodes } = this.recovery.generateCodes();

    // 存储到数据库
    await this.db.query(`
      INSERT INTO user_mfa (user_id, totp_secret, totp_enabled, recovery_codes, primary_method)
      VALUES ($1, $2, TRUE, $3, 'totp')
      ON CONFLICT (user_id) 
      DO UPDATE SET totp_secret = $2, totp_enabled = TRUE, recovery_codes = $3, updated_at = NOW()
    `, [userId, secret, JSON.stringify(hashedCodes)]);

    // 清除临时数据
    await this.redis.del(`totp_setup:${userId}`);

    return res.json({
      success: true,
      recoveryCodes: codes
    });
  }

  /**
   * 禁用 MFA
   */
  async disableMFA(req, res) {
    const userId = req.user.id;
    const { code } = req.body;

    // 验证
    const result = await this.verifyMFAInternal(userId, code);
    
    if (!result.success) {
      return res.status(400).json({ error: '验证码错误' });
    }

    await this.db.query(`
      UPDATE user_mfa 
      SET totp_enabled = FALSE, sms_enabled = FALSE, email_enabled = FALSE, updated_at = NOW()
      WHERE user_id = $1
    `, [userId]);

    return res.json({ success: true });
  }

  /**
   * 内部验证方法
   */
  async verifyMFAInternal(userId, code) {
    const result = await this.db.query(
      'SELECT totp_secret, recovery_codes FROM user_mfa WHERE user_id = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      return { success: false };
    }

    const { totp_secret, recovery_codes } = result.rows[0];

    // 尝试 TOTP
    if (this.totp.verify(totp_secret, code)) {
      return { success: true, method: 'totp' };
    }

    // 尝试恢复码
    const hashedCodes = recovery_codes || [];
    const recoveryResult = this.recovery.verifyCode(code, hashedCodes);
    
    if (recoveryResult.valid) {
      await this.db.query(
        'UPDATE user_mfa SET recovery_codes = $1 WHERE user_id = $2',
        [JSON.stringify(recoveryResult.remaining), userId]
      );
      return { success: true, method: 'recovery' };
    }

    return { success: false };
  }

  /**
   * 记录验证日志
   */
  async logVerification(userId, method, success, ipAddress) {
    await this.db.query(`
      INSERT INTO mfa_logs (user_id, method, success, ip_address)
      VALUES ($1, $2, $3, $4)
    `, [userId, method, success, ipAddress]);
  }
}

module.exports = MFAMiddleware;
```

### 前端集成示例

#### React 组件

```jsx
// components/MFASetup.jsx
import React, { useState, useEffect } from 'react';
import QRCode from 'react-qr-code';

function MFASetup({ userId, email }) {
  const [step, setStep] = useState('intro'); // intro, setup, verify, success
  const [secret, setSecret] = useState('');
  const [qrCode, setQrCode] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [recoveryCodes, setRecoveryCodes] = useState([]);
  const [error, setError] = useState('');

  // 开始设置
  const startSetup = async () => {
    try {
      const response = await fetch('/api/mfa/totp/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });
      
      const data = await response.json();
      
      setSecret(data.secret);
      setQrCode(data.qrCode);
      setStep('setup');
    } catch (err) {
      setError('设置失败，请稍后重试');
    }
  };

  // 验证并启用
  const verifyAndEnable = async () => {
    try {
      const response = await fetch('/api/mfa/totp/enable', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ code: verificationCode })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setRecoveryCodes(data.recoveryCodes);
        setStep('success');
      } else {
        setError(data.error || '验证码错误');
      }
    } catch (err) {
      setError('验证失败，请稍后重试');
    }
  };

  // 渲染不同步骤
  if (step === 'intro') {
    return (
      <div className="mfa-setup">
        <h2>启用两步验证</h2>
        <p>使用验证器应用（如 Google Authenticator）增强账户安全</p>
        <button onClick={startSetup} className="btn btn-primary">
          开始设置
        </button>
      </div>
    );
  }

  if (step === 'setup') {
    return (
      <div className="mfa-setup">
        <h2>扫描二维码</h2>
        <p>使用验证器应用扫描下方二维码：</p>
        
        <div className="qr-container" style={{ padding: '20px', background: '#fff' }}>
          <QRCode value={qrCode} size={200} />
        </div>
        
        <p style={{ marginTop: '20px' }}>或手动输入密钥：</p>
        <code style={{ 
          display: 'block', 
          padding: '10px', 
          background: '#f5f5f5',
          wordBreak: 'break-all'
        }}>
          {secret}
        </code>
        
        <div style={{ marginTop: '20px' }}>
          <label>输入验证器显示的6位数字：</label>
          <input
            type="text"
            maxLength={6}
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value)}
            placeholder="000000"
            style={{ 
              fontSize: '24px', 
              letterSpacing: '8px',
              textAlign: 'center',
              padding: '10px',
              width: '200px',
              marginRight: '10px'
            }}
          />
          <button 
            onClick={verifyAndEnable} 
            className="btn btn-primary"
            disabled={verificationCode.length !== 6}
          >
            验证并启用
          </button>
        </div>
        
        {error && <p className="error">{error}</p>}
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="mfa-setup">
        <h2>✅ 两步验证已启用</h2>
        
        <div style={{ 
          background: '#fff3cd', 
          padding: '20px', 
          borderRadius: '8px',
          marginTop: '20px'
        }}>
          <h3>⚠️ 请保存备用恢复码</h3>
          <p>如果丢失验证器，可使用以下恢复码登录：</p>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '10px',
            marginTop: '10px'
          }}>
            {recoveryCodes.map((code, i) => (
              <div key={i} style={{ 
                fontFamily: 'monospace',
                fontSize: '18px',
                padding: '5px',
                background: '#fff'
              }}>
                {code.slice(0, 4)}-{code.slice(4)}
              </div>
            ))}
          </div>
          
          <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
            每个恢复码只能使用一次
          </p>
        </div>
        
        <button 
          onClick={() => window.print()} 
          className="btn btn-secondary"
          style={{ marginTop: '20px' }}
        >
          打印恢复码
        </button>
      </div>
    );
  }
}

export default MFASetup;
```

#### 登录时 MFA 验证

```jsx
// components/MFAVerify.jsx
import React, { useState, useEffect } from 'react';

function MFAVerify({ onVerified }) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [method, setMethod] = useState('totp'); // totp, recovery

  const verify = async () => {
    if (code.length < 6) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('/api/mfa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ code, method })
      });
      
      const data = await response.json();
      
      if (data.success) {
        onVerified();
      } else {
        setError(data.error || '验证失败');
      }
    } catch (err) {
      setError('网络错误，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mfa-verify">
      <h2>两步验证</h2>
      
      <div className="method-tabs">
        <button 
          className={method === 'totp' ? 'active' : ''}
          onClick={() => setMethod('totp')}
        >
          验证器
        </button>
        <button 
          className={method === 'recovery' ? 'active' : ''}
          onClick={() => setMethod('recovery')}
        >
          恢复码
        </button>
      </div>
      
      <p>
        {method === 'totp' 
          ? '请输入验证器显示的6位数字' 
          : '请输入8位备用恢复码'}
      </p>
      
      <input
        type="text"
        maxLength={method === 'totp' ? 6 : 8}
        value={code}
        onChange={(e) => setCode(e.target.value.toUpperCase())}
        placeholder={method === 'totp' ? '000000' : 'XXXXXXXX'}
        style={{ 
          fontSize: '24px', 
          letterSpacing: '4px',
          textAlign: 'center',
          padding: '15px',
          width: '200px'
        }}
        autoFocus
      />
      
      <button 
        onClick={verify} 
        disabled={loading || (method === 'totp' ? code.length !== 6 : code.length !== 8)}
        className="btn btn-primary"
        style={{ display: 'block', margin: '20px auto' }}
      >
        {loading ? '验证中...' : '验证'}
      </button>
      
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default MFAVerify;
```

---

## MFA 强制策略

### 策略配置

```python
# mfa_policy.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta

class MFAPolicyLevel(Enum):
    """MFA 强制级别"""
    DISABLED = "disabled"          # 不强制
    OPTIONAL = "optional"          # 可选启用
    RECOMMENDED = "recommended"    # 推荐启用（显示提示）
    ENFORCED = "enforced"          # 强制启用
    ENFORCED_IMMEDIATE = "enforced_immediate"  # 立即强制

@dataclass
class MFAPolicy:
    """MFA 策略配置"""
    level: MFAPolicyLevel
    grace_period_days: int = 14     # 宽限期（天）
    allowed_methods: list = None   # 允许的验证方式
    exempt_roles: list = None      # 豁免的角色
    
    def __post_init__(self):
        self.allowed_methods = self.allowed_methods or ['totp', 'sms', 'email']
        self.exempt_roles = self.exempt_roles or []

class MFAPolicyManager:
    """MFA 策略管理器"""
    
    def __init__(self, db):
        self.db = db
    
    def get_user_policy(self, user_id: int) -> MFAPolicy:
        """获取用户适用的 MFA 策略"""
        # 查询用户角色和组织设置
        result = self.db.fetch_one("""
            SELECT u.role, o.mfa_policy, o.mfa_grace_period
            FROM users u
            LEFT JOIN organizations o ON u.org_id = o.id
            WHERE u.id = %s
        """, (user_id,))
        
        if not result:
            return MFAPolicy(level=MFAPolicyLevel.OPTIONAL)
        
        # 检查豁免角色
        exempt_roles = ['service_account', 'api_user']
        if result['role'] in exempt_roles:
            return MFAPolicy(level=MFAPolicyLevel.DISABLED)
        
        return MFAPolicy(
            level=MFAPolicyLevel(result['mfa_policy'] or 'optional'),
            grace_period_days=result['mfa_grace_period'] or 14
        )
    
    def check_mfa_requirement(self, user_id: int) -> dict:
        """
        检查用户 MFA 要求
        
        Returns:
            {
                'required': bool,           # 是否需要 MFA
                'immediate': bool,          # 是否立即需要
                'grace_period_ends': date,  # 宽限期结束日期
                'warning': str              # 警告信息
            }
        """
        policy = self.get_user_policy(user_id)
        
        if policy.level == MFAPolicyLevel.DISABLED:
            return {'required': False}
        
        # 检查用户是否已启用 MFA
        mfa_status = self.db.fetch_one("""
            SELECT totp_enabled, sms_enabled, email_enabled, created_at
            FROM user_mfa WHERE user_id = %s
        """, (user_id,))
        
        if mfa_status and (mfa_status['totp_enabled'] or mfa_status['sms_enabled']):
            return {'required': False}  # 已启用
        
        if policy.level == MFAPolicyLevel.OPTIONAL:
            return {
                'required': False,
                'warning': '建议启用两步验证以增强账户安全'
            }
        
        if policy.level == MFAPolicyLevel.RECOMMENDED:
            return {
                'required': False,
                'warning': '强烈建议启用两步验证',
                'recommended': True
            }
        
        if policy.level == MFAPolicyLevel.ENFORCED:
            # 计算宽限期
            user_created = self.db.fetch_one(
                "SELECT created_at FROM users WHERE id = %s", (user_id,)
            )['created_at']
            
            grace_period_ends = user_created + timedelta(days=policy.grace_period_days)
            remaining_days = (grace_period_ends - datetime.utcnow()).days
            
            if remaining_days > 0:
                return {
                    'required': False,
                    'immediate': False,
                    'grace_period_ends': grace_period_ends,
                    'warning': f'请在 {remaining_days} 天内启用两步验证'
                }
        
        # 强制启用
        return {
            'required': True,
            'immediate': True,
            'warning': '请立即启用两步验证以继续使用账户'
        }
```

---

## 成本估算

### 免费方案对比

| 方案 | 月成本 | 用户体验 | 安全性 | 适用场景 |
|------|--------|---------|--------|---------|
| **TOTP** | $0 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 所有应用首选 |
| **邮件 OTP** | $0 | ⭐⭐⭐ | ⭐⭐⭐ | 备用方案 |
| **Redis 存储** | $0（自建） | N/A | N/A | OTP 临时存储 |

### 付费方案对比

| 方案 | 月成本 | 免费额度 | 特点 | 适用场景 |
|------|--------|---------|------|---------|
| **Twilio 短信** | 按量付费 | $0（测试$15.50） | 全球覆盖 | 需要短信验证 |
| **SendGrid 邮件** | $0-15 | 100封/天 | 高送达率 | 需要邮件验证 |
| **Auth0 MFA** | $0-240 | 7,000 MAU | 托管服务 | 快速集成 |

### Twilio 短信成本估算

```
Twilio 短信定价（中国）：
- 发送短信：$0.055/条
- 接收短信：免费

月成本估算：
- 100 用户 × 5 次登录/月 = 500 条
- 500 × $0.055 = $27.50/月

优化建议：
1. 优先使用 TOTP（免费）
2. 短信作为备用方式
3. 设置合理的 OTP 有效期（减少重发）
```

### SendGrid 邮件成本估算

```
SendGrid 定价：
- Free：100 封/天（3,000 封/月）
- Essentials：$14.95/月（40,000 封）
- Pro：$89.95/月（100,000 封）

独立开发者建议：
- Free 层足够小型项目
- 超过 3,000 封/月时升级
```

---

## 迁出成本

### 从 Auth0 MFA 迁出

- **迁出难度**：中
- **迁出步骤**：
  1. 导出用户 MFA 配置（密钥需重新生成）
  2. 实现自托管 TOTP 服务
  3. 用户重新绑定 MFA
  4. 迁移验证流程
- **预计时间**：2-3 天

### 从短信 OTP 迁出

- **迁出难度**：低
- **迁出步骤**：
  1. 实现 TOTP 服务
  2. 引导用户绑定 TOTP
  3. 短信作为备用方式
  4. 逐步降低短信使用率
- **预计时间**：1-2 天

### 从自建方案迁出到托管服务

- **迁出难度**：中
- **迁出步骤**：
  1. 评估托管服务 API
  2. 导出现有配置
  3. 实现迁移脚本
  4. 并行运行验证
  5. 切换流量
- **预计时间**：3-5 天

---

## 与其他武器配合

### 推荐组合

```
基础安全链路：
├── HTTPS（必需）
├── 密码哈希（bcrypt/argon2）
├── MFA（本方案）
├── Rate Limiting（防止暴力破解）
└── Session 管理（安全 Token）

增强安全链路：
├── 设备指纹（检测异常登录）
├── IP 黑名单（阻止已知威胁）
├── 异常检测（AI 驱动）
└── 审计日志（合规需求）
```

### 配合武器

- **前置**：[API 认证指南](./api-auth-guide.md) - 基础认证
- **后置**：[简易限流方案](./rate-limiting-simple.md) - 防暴力破解
- **互补**：[免费安全技术栈图谱](./free-security-stack.md) - 整体安全

---

## 常见问题

**Q: TOTP 和短信 OTP 如何选择？**

A:
- 优先选择 **TOTP**：免费、安全、无需网络
- 短信作为**备用**：覆盖无智能手机用户
- 组合使用：TOTP 主验证 + 短信备用

**Q: 用户丢失认证器怎么办？**

A:
1. 提供**备用恢复码**（必须）
2. 邮箱验证重置 MFA
3. 客服人工验证（高价值账户）

**Q: 时间不同步导致 TOTP 验证失败？**

A:
```python
# 允许更大的时间窗口
totp.verify(code, valid_window=2)  # 前后 2 个窗口（共 90 秒）

# 或使用服务器时间校准
from ntplib import NTPClient
ntp = NTPClient()
response = ntp.request('pool.ntp.org')
server_time = response.tx_time
```

**Q: 如何防止 MFA 疲劳攻击？**

A:
1. 限制 OTP 发送频率
2. 设置每日尝试上限
3. 异常行为检测
4. 发送前确认提示

**Q: 数据库存储 MFA 密钥安全吗？**

A:
- 存储 TOTP 密钥时使用**应用层加密**
- 加密密钥存储在 HSM 或密钥管理服务
- 或使用数据库字段级加密（如 PostgreSQL pgcrypto）

```python
# 加密存储示例
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # 存储在安全位置
fernet = Fernet(key)

encrypted_secret = fernet.encrypt(secret.encode())
# 存储 encrypted_secret 到数据库
```

---

## 安全最佳实践

### 1. 密钥管理

```python
# ✅ 正确：加密存储
import os
from cryptography.fernet import Fernet

# 从环境变量或密钥管理服务获取加密密钥
ENCRYPTION_KEY = os.getenv('MFA_ENCRYPTION_KEY')
fernet = Fernet(ENCRYPTION_KEY)

def store_totp_secret(user_id: int, secret: str):
    encrypted = fernet.encrypt(secret.encode())
    # 存储 encrypted 到数据库

def get_totp_secret(user_id: int) -> str:
    encrypted = db.get_secret(user_id)
    return fernet.decrypt(encrypted).decode()

# ❌ 错误：明文存储
# db.store(user_id, secret)  # 危险！
```

### 2. 防重放攻击

```python
# 使用 nonce 防止重放
import secrets

def verify_with_nonce(user_id: int, code: str) -> bool:
    nonce_key = f"totp_nonce:{user_id}:{code}"
    
    # 检查是否已使用
    if redis.exists(nonce_key):
        return False  # 重放攻击
    
    # 验证 TOTP
    if totp.verify(secret, code):
        # 标记已使用（有效期与 TOTP 窗口一致）
        redis.setex(nonce_key, 90, "1")
        return True
    
    return False
```

### 3. 速率限制

```python
# MFA 验证速率限制
MFA_RATE_LIMITS = {
    'verify': {'max': 10, 'window': 300},    # 5分钟10次
    'sms_send': {'max': 3, 'window': 60},    # 1分钟3次
    'email_send': {'max': 5, 'window': 60},  # 1分钟5次
}

async def check_rate_limit(user_id: int, action: str) -> bool:
    key = f"mfa_ratelimit:{action}:{user_id}"
    limit = MFA_RATE_LIMITS[action]
    
    current = await redis.incr(key)
    if current == 1:
        await redis.expire(key, limit['window'])
    
    return current <= limit['max']
```

### 4. 安全审计

```python
# MFA 安全审计日志
def log_mfa_event(
    user_id: int,
    event: str,  # 'setup', 'verify', 'disable', 'recovery_used'
    success: bool,
    metadata: dict = None
):
    log_entry = {
        'user_id': user_id,
        'event': event,
        'success': success,
        'ip_address': get_client_ip(),
        'user_agent': get_user_agent(),
        'timestamp': datetime.utcnow().isoformat(),
        'metadata': metadata or {}
    }
    
    # 存储到日志系统
    db.insert('mfa_audit_log', log_entry)
    
    # 异常事件告警
    if event in ['recovery_used', 'mfa_disabled']:
        send_security_alert(user_id, event)
```

---

## 测试验证

### 单元测试

```python
# tests/test_mfa.py
import pytest
from mfa_service import TOTPService, RecoveryCodesService

class TestTOTPService:
    def test_generate_secret(self):
        service = TOTPService()
        secret = service.generate_secret()
        
        assert len(secret) == 32  # Base32 编码
        assert secret.isalnum()
    
    def test_verify_success(self):
        service = TOTPService()
        secret = service.generate_secret()
        code = service.get_current_code(secret)
        
        assert service.verify(secret, code) is True
    
    def test_verify_invalid_code(self):
        service = TOTPService()
        secret = service.generate_secret()
        
        assert service.verify(secret, '000000') is False
    
    def test_verify_wrong_secret(self):
        service = TOTPService()
        secret1 = service.generate_secret()
        secret2 = service.generate_secret()
        code = service.get_current_code(secret1)
        
        assert service.verify(secret2, code) is False

class TestRecoveryCodesService:
    def test_generate_codes(self):
        service = RecoveryCodesService()
        codes, hashed = service.generate_codes(10)
        
        assert len(codes) == 10
        assert len(hashed) == 10
        assert all(len(c) == 8 for c in codes)
    
    def test_verify_and_consume(self):
        service = RecoveryCodesService()
        codes, hashed = service.generate_codes(5)
        
        # 验证并消费
        result = service.verify_code(codes[0], hashed)
        assert result['valid'] is True
        assert len(result['remaining']) == 4
        
        # 再次使用同一码应失败
        result2 = service.verify_code(codes[0], result['remaining'])
        assert result2['valid'] is False
```

### 集成测试

```python
# tests/test_mfa_integration.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestMFAIntegration:
    def test_setup_and_verify_flow(self, auth_token):
        # 1. 开始设置
        response = client.post(
            '/api/mfa/totp/setup',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert response.status_code == 200
        data = response.json()
        assert 'secret' in data
        assert 'qrCode' in data
        
        # 2. 使用模拟验证
        from mfa_service import TOTPService
        totp = TOTPService()
        code = totp.get_current_code(data['secret'])
        
        # 3. 启用
        response = client.post(
            '/api/mfa/totp/enable',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'code': code}
        )
        assert response.status_code == 200
        assert 'recoveryCodes' in response.json()
        
        # 4. 验证
        new_code = totp.get_current_code(data['secret'])
        response = client.post(
            '/api/mfa/verify',
            headers={'Authorization': f'Bearer {auth_token}'},
            json={'code': new_code}
        )
        assert response.json()['success'] is True
```

---

## 参考资料

### 标准规范
- [RFC 6238 - TOTP](https://datatracker.ietf.org/doc/html/rfc6238)
- [RFC 4226 - HOTP](https://datatracker.ietf.org/doc/html/rfc4226)
- [RFC 6287 - OCRA](https://datatracker.ietf.org/doc/html/rfc6287)

### 开源库
- [pyotp](https://github.com/pyotp/pyotp) - Python TOTP 库
- [otplib](https://github.com/yeojz/otplib) - Node.js OTP 库
- [speakeasy](https://github.com/speakeasyjs/speakeasy) - Node.js TOTP 库

### 服务商文档
- [Twilio SMS API](https://www.twilio.com/docs/sms)
- [SendGrid Email API](https://docs.sendgrid.com/)
- [Auth0 MFA](https://auth0.com/docs/mfa)

### 安全指南
- [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) - 数字身份指南
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

---

## 更新日志

| 日期 | 变更 |
|------|------|
| 2026-06-11 | 初始版本，包含 TOTP/短信/邮件/恢复码方案 |

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
