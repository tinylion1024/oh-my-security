# 输入验证武器库

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 2-4小时
- **维护成本**: 1-2小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
为独立开发者提供全面的输入验证解决方案，防止SQL注入、XSS、CSRF等常见攻击，覆盖前端到后端的全链路验证。

---

## 核心原则

### 黄金法则：白名单优于黑名单

```
❌ 黑名单思维（不安全）
"禁止这些危险字符：<script>、SELECT、DROP..."
问题：攻击者总能找到绕过方法

✅ 白名单思维（安全）
"只允许这些安全字符：字母、数字、下划线..."
优势：不在白名单内的全部拒绝
```

### 验证层次架构

```
输入验证多层防御
┌─────────────────────────────────────────────────────┐
│                    前端验证                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │格式检查  │  │类型检查  │  │长度限制  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    后端验证                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Schema验证│  │业务逻辑  │  │安全过滤  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    数据库层                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │参数化查询│  │类型约束  │  │存储加密  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

---

## 快速上手（5分钟）

### Python + Pydantic 最小示例

```python
# requirements.txt
# pydantic>=2.0

from pydantic import BaseModel, EmailStr, HttpUrl, validator, constr
from typing import Optional
from datetime import datetime
import re

class UserInput(BaseModel):
    """用户输入验证模型"""
    
    # 邮箱验证
    email: EmailStr
    
    # 用户名：3-20字符，仅允许字母数字下划线
    username: constr(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
    
    # 密码：至少8位，包含大小写和数字
    password: constr(min_length=8)
    
    # 手机号：中国大陆格式
    phone: Optional[str] = None
    
    # 年龄：18-120岁
    age: int
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码必须包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码必须包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码必须包含数字')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 120:
            raise ValueError('年龄必须在18-120岁之间')
        return v

# 使用
try:
    user = UserInput(
        email='test@example.com',
        username='john_doe',
        password='SecurePass123',
        phone='13800138000',
        age=25
    )
    print(user.json())
except ValueError as e:
    print(f'验证失败: {e}')
```

### Node.js + Zod 最小示例

```javascript
// package.json
// "zod": "^3.22.0"

const { z } = require('zod');

// 用户输入Schema
const UserSchema = z.object({
  // 邮箱验证
  email: z.string().email('邮箱格式不正确'),
  
  // 用户名：3-20字符，仅字母数字下划线
  username: z.string()
    .min(3, '用户名至少3个字符')
    .max(20, '用户名最多20个字符')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母、数字和下划线'),
  
  // 密码：至少8位，包含大小写和数字
  password: z.string()
    .min(8, '密码至少8个字符')
    .regex(/[A-Z]/, '密码必须包含大写字母')
    .regex(/[a-z]/, '密码必须包含小写字母')
    .regex(/\d/, '密码必须包含数字'),
  
  // 手机号：可选，中国大陆格式
  phone: z.string()
    .regex(/^1[3-9]\d{9}$/, '手机号格式不正确')
    .optional()
    .or(z.undefined()),
  
  // 年龄：18-120岁
  age: z.number()
    .int('年龄必须是整数')
    .min(18, '年龄必须大于等于18岁')
    .max(120, '年龄必须小于等于120岁'),
  
  // URL验证
  website: z.string().url('URL格式不正确').optional(),
  
  // 日期验证
  birthDate: z.string().datetime('日期格式不正确').optional()
});

// 使用验证
function validateUser(data) {
  try {
    const user = UserSchema.parse(data);
    console.log('验证通过:', user);
    return { success: true, data: user };
  } catch (error) {
    console.error('验证失败:', error.errors);
    return { success: false, errors: error.errors };
  }
}

// 测试
validateUser({
  email: 'test@example.com',
  username: 'john_doe',
  password: 'SecurePass123',
  phone: '13800138000',
  age: 25
});
```

---

## 详细方案

### 1. 常见验证类型

#### 1.1 邮箱验证

```python
# Python - 邮箱验证
import re
from email.utils import parseaddr

def validate_email(email: str) -> bool:
    """严格的邮箱验证"""
    
    # 1. 基本格式检查
    if not email or len(email) > 254:
        return False
    
    # 2. 解析邮箱地址
    _, addr = parseaddr(email)
    if not addr:
        return False
    
    # 3. 正则验证（RFC 5322简化版）
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, addr):
        return False
    
    # 4. 危险字符检查
    dangerous = ['<', '>', '"', "'", ';', '\\', '\n', '\r']
    if any(char in email for char in dangerous):
        return False
    
    return True

# 使用
emails = [
    'test@example.com',
    'user+tag@subdomain.example.co.uk',
    'invalid-email',
    'test@.com',
    'test@example'
]

for email in emails:
    print(f'{email}: {validate_email(email)}')
```

```javascript
// Node.js - 邮箱验证
const validator = require('validator');

function validateEmail(email) {
  // 1. 基本检查
  if (!email || email.length > 254) return false;
  
  // 2. 格式验证
  if (!validator.isEmail(email)) return false;
  
  // 3. 危险字符检查
  const dangerous = /['"<>\n\r\\;]/;
  if (dangerous.test(email)) return false;
  
  // 4. 域名验证（可选）
  const domain = email.split('@')[1];
  // 可以添加DNS记录验证
  
  return true;
}

// 使用 validator.js 的额外功能
const email = 'test@example.com';
console.log('邮箱格式:', validator.isEmail(email));
console.log('规范化:', validator.normalizeEmail(email));
```

#### 1.2 URL验证

```python
# Python - URL验证
from urllib.parse import urlparse
import re

def validate_url(url: str, allowed_schemes: list = None) -> bool:
    """安全的URL验证"""
    
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
    
    # 1. 长度检查
    if not url or len(url) > 2048:
        return False
    
    # 2. 解析URL
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    
    # 3. 协议检查（白名单）
    if parsed.scheme.lower() not in allowed_schemes:
        return False
    
    # 4. 域名检查
    if not parsed.netloc:
        return False
    
    # 5. 危险协议阻止（SSRF防护）
    blocked_schemes = ['file', 'javascript', 'data', 'vbscript']
    if parsed.scheme.lower() in blocked_schemes:
        return False
    
    # 6. 内网IP检查（SSRF防护）
    hostname = parsed.hostname
    if hostname:
        # 阻止私有IP
        private_ips = [
            r'^127\.',           # 127.0.0.0/8
            r'^10\.',            # 10.0.0.0/8
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # 172.16.0.0/12
            r'^192\.168\.',      # 192.168.0.0/16
            r'^localhost$',      # localhost
            r'^0\.0\.0\.0$'      # 0.0.0.0
        ]
        for pattern in private_ips:
            if re.match(pattern, hostname):
                return False
    
    return True

# 使用
urls = [
    'https://example.com/path?query=value',
    'http://localhost:8080/admin',  # 阻止内网访问
    'file:///etc/passwd',           # 阻止危险协议
    'javascript:alert(1)',          # 阻止XSS
    'https://192.168.1.1/secret'    # 阻止私有IP
]

for url in urls:
    print(f'{url}: {validate_url(url)}')
```

```javascript
// Node.js - URL验证
const { URL } = require('url');

function validateUrl(url, allowedSchemes = ['http', 'https']) {
  try {
    // 1. 长度检查
    if (!url || url.length > 2048) return { valid: false, reason: 'URL太长' };
    
    // 2. 解析URL
    const parsed = new URL(url);
    
    // 3. 协议检查
    const scheme = parsed.protocol.replace(':', '').toLowerCase();
    if (!allowedSchemes.includes(scheme)) {
      return { valid: false, reason: '不支持的协议' };
    }
    
    // 4. 危险协议阻止
    const blockedSchemes = ['file', 'javascript', 'data', 'vbscript'];
    if (blockedSchemes.includes(scheme)) {
      return { valid: false, reason: '危险协议' };
    }
    
    // 5. SSRF防护 - 内网IP检查
    const hostname = parsed.hostname;
    const privateIpPatterns = [
      /^127\./,
      /^10\./,
      /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
      /^192\.168\./,
      /^localhost$/i,
      /^0\.0\.0\.0$/
    ];
    
    if (privateIpPatterns.some(p => p.test(hostname))) {
      return { valid: false, reason: '禁止访问内网' };
    }
    
    return { valid: true, parsed };
  } catch (error) {
    return { valid: false, reason: 'URL格式错误' };
  }
}

// 使用
const urls = [
  'https://example.com',
  'http://localhost/admin',
  'file:///etc/passwd',
  'https://192.168.1.1/secret'
];

urls.forEach(url => {
  console.log(url, validateUrl(url));
});
```

#### 1.3 手机号验证

```python
# Python - 国际手机号验证
import re

class PhoneValidator:
    """多国手机号验证器"""
    
    # 各国手机号正则（白名单模式）
    PATTERNS = {
        'CN': r'^1[3-9]\d{9}$',                    # 中国大陆
        'US': r'^\+1[2-9]\d{2}[2-9]\d{6}$',       # 美国/加拿大
        'UK': r'^\+44[1-9]\d{8,9}$',              # 英国
        'JP': r'^\+81[1-9]\d{8,9}$',              # 日本
        'KR': r'^\+82[1-9]\d{7,8}$',              # 韩国
        'TW': r'^\+886[1-9]\d{7,8}$',             # 台湾
        'HK': r'^\+852[5-9]\d{7}$',               # 香港
    }
    
    @classmethod
    def validate(cls, phone: str, country: str = 'CN') -> bool:
        """验证手机号"""
        
        # 1. 清理输入
        phone = re.sub(r'[\s\-()]', '', phone)
        
        # 2. 长度检查
        if len(phone) < 10 or len(phone) > 15:
            return False
        
        # 3. 国家格式验证
        pattern = cls.PATTERNS.get(country.upper())
        if pattern:
            if not re.match(pattern, phone):
                return False
        
        # 4. 通用安全检查
        if not re.match(r'^\+?[0-9]+$', phone):
            return False
        
        return True
    
    @classmethod
    def normalize(cls, phone: str, country: str = 'CN') -> str:
        """规范化手机号"""
        phone = re.sub(r'[\s\-()]', '', phone)
        
        # 添加国际区号
        prefixes = {
            'CN': '+86',
            'US': '+1',
            'UK': '+44',
            'JP': '+81',
            'KR': '+82',
            'TW': '+886',
            'HK': '+852'
        }
        
        prefix = prefixes.get(country.upper(), '')
        if not phone.startswith('+'):
            phone = prefix + phone.lstrip('0')
        
        return phone

# 使用
validator = PhoneValidator()
print(validator.validate('13800138000', 'CN'))      # True
print(validator.validate('13800138000', 'US'))      # False
print(validator.normalize('013800138000', 'CN'))    # +8613800138000
```

#### 1.4 日期验证

```python
# Python - 日期验证
from datetime import datetime, date
from typing import Optional

class DateValidator:
    """安全的日期验证器"""
    
    @staticmethod
    def validate(
        date_str: str,
        format: str = '%Y-%m-%d',
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ) -> bool:
        """验证日期格式和范围"""
        
        # 1. 长度检查
        if len(date_str) > 20:
            return False
        
        # 2. 危险字符检查
        if not re.match(r'^[\d\-/:\s]+$', date_str):
            return False
        
        # 3. 格式验证
        try:
            parsed = datetime.strptime(date_str, format).date()
        except ValueError:
            return False
        
        # 4. 范围验证
        if min_date and parsed < min_date:
            return False
        if max_date and parsed > max_date:
            return False
        
        return True
    
    @staticmethod
    def validate_iso(date_str: str) -> bool:
        """ISO 8601 格式验证"""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except ValueError:
            return False

# 使用
validator = DateValidator()

# 基本验证
print(validator.validate('2024-06-15'))  # True
print(validator.validate('2024-13-01'))  # False

# 范围验证
min_date = date(2024, 1, 1)
max_date = date(2024, 12, 31)
print(validator.validate('2024-06-15', min_date=min_date, max_date=max_date))

# ISO格式
print(validator.validate_iso('2024-06-15T10:30:00Z'))
```

---

### 2. SQL注入防护

#### 2.1 参数化查询（核心防御）

```python
# Python - 参数化查询
import sqlite3
from typing import List, Optional

class SafeDatabase:
    """安全的数据库操作类"""
    
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    # ✅ 正确：参数化查询
    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """安全的查询方式"""
        cursor = self.conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)  # 参数作为元组传入
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_users_by_emails(self, emails: List[str]) -> List[dict]:
        """批量查询（IN语句）"""
        placeholders = ','.join('?' * len(emails))
        cursor = self.conn.execute(
            f'SELECT * FROM users WHERE email IN ({placeholders})',
            tuple(emails)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def search_users(self, username: str, limit: int = 10) -> List[dict]:
        """模糊搜索"""
        cursor = self.conn.execute(
            "SELECT * FROM users WHERE username LIKE ? LIMIT ?",
            (f'%{username}%', limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def safe_insert(self, table: str, data: dict) -> int:
        """安全插入"""
        # 白名单验证表名
        allowed_tables = ['users', 'posts', 'comments']
        if table not in allowed_tables:
            raise ValueError(f'Invalid table: {table}')
        
        # 白名单验证列名
        columns = list(data.keys())
        placeholders = ','.join('?' * len(columns))
        sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
        
        cursor = self.conn.execute(sql, tuple(data.values()))
        self.conn.commit()
        return cursor.lastrowid
    
    # ❌ 错误：字符串拼接（危险！）
    def UNSAFE_get_user(self, username: str):
        """不安全的查询方式 - 仅作反面教材"""
        # 危险：username 可能是 "admin' OR '1'='1"
        sql = f"SELECT * FROM users WHERE username = '{username}'"
        # 永远不要这样做！
        pass

# 使用
db = SafeDatabase('app.db')

# 安全查询
user = db.get_user_by_id(1)
users = db.search_users('john')

# 安全插入
user_id = db.safe_insert('users', {
    'username': 'john_doe',
    'email': 'john@example.com'
})
```

```python
# Python - SQLAlchemy ORM（更安全）
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(100))

# 创建引擎和会话
engine = create_engine('sqlite:///app.db')
Session = sessionmaker(bind=engine)
session = Session()

# ✅ 安全：ORM查询
user = session.query(User).filter(User.id == 1).first()
users = session.query(User).filter(User.username.like('%john%')).all()

# ✅ 安全：原生SQL + 参数化
result = session.execute(
    text('SELECT * FROM users WHERE id = :id'),
    {'id': 1}
)
```

```javascript
// Node.js - 参数化查询（Sequelize）
const { Sequelize, DataTypes } = require('sequelize');

const sequelize = new Sequelize('sqlite::memory:');

// 定义模型
const User = sequelize.define('User', {
  username: DataTypes.STRING,
  email: DataTypes.STRING
});

// ✅ 安全：ORM查询
async function getUserById(id) {
  return await User.findByPk(id);
}

async function searchUsers(username) {
  return await User.findAll({
    where: {
      username: {
        [Sequelize.Op.like]: `%${username}%`
      }
    }
  });
}

// ✅ 安全：原生SQL参数化
async function rawQuery(id) {
  const [results] = await sequelize.query(
    'SELECT * FROM Users WHERE id = ?',
    {
      replacements: [id],
      type: Sequelize.QueryTypes.SELECT
    }
  );
  return results;
}

// ❌ 错误：字符串拼接
function unsafeQuery(username) {
  // 危险！不要这样做
  return sequelize.query(
    `SELECT * FROM Users WHERE username = '${username}'`
  );
}
```

#### 2.2 输入过滤（辅助防御）

```python
# Python - SQL注入过滤
import re

class SQLInjectionFilter:
    """SQL注入过滤器（辅助防御，不能替代参数化查询）"""
    
    # 危险关键词（仅供参考，不推荐黑名单模式）
    DANGEROUS_KEYWORDS = [
        'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP',
        'UNION', 'OR', 'AND', '--', '/*', '*/', ';',
        'EXEC', 'EXECUTE', 'XP_', 'SP_'
    ]
    
    @classmethod
    def detect(cls, input_str: str) -> bool:
        """检测潜在的SQL注入"""
        upper_input = input_str.upper()
        
        # 检查危险关键词
        for keyword in cls.DANGEROUS_KEYWORDS:
            if keyword in upper_input:
                return True
        
        # 检查特殊字符组合
        patterns = [
            r"['\"].*['\"].*[=]",  # 引号+等号
            r"\d+\s*=\s*\d+",      # 数字比较
            r"--.*$",               # SQL注释
            r"/\*.*\*/",           # 块注释
        ]
        
        for pattern in patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def sanitize_identifier(cls, identifier: str) -> str:
        """清理标识符（表名、列名）"""
        # 只允许字母、数字、下划线
        return re.sub(r'[^a-zA-Z0-9_]', '', identifier)

# 使用
filter = SQLInjectionFilter()

# 检测
print(filter.detect("admin' OR '1'='1"))  # True
print(filter.detect("normal input"))       # False

# 清理标识符
print(filter.sanitize_identifier("users; DROP TABLE users--"))
# 输出: usersDROPTABLEusers
```

---

### 3. XSS防护

#### 3.1 HTML转义

```python
# Python - HTML转义
import html
import re
from typing import Optional

class XSSProtector:
    """XSS防护工具"""
    
    # HTML实体编码
    @staticmethod
    def escape_html(text: str) -> str:
        """基础HTML转义"""
        return html.escape(text, quote=True)
    
    # 白名单式HTML清理
    @staticmethod
    def sanitize_html(
        text: str,
        allowed_tags: list = None,
        allowed_attrs: dict = None
    ) -> str:
        """允许部分HTML标签（白名单模式）"""
        
        if allowed_tags is None:
            allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'img']
        
        if allowed_attrs is None:
            allowed_attrs = {
                'a': ['href', 'title'],
                'img': ['src', 'alt', 'width', 'height']
            }
        
        # 完全转义
        escaped = html.escape(text)
        
        # 这里应该使用专门的库如 bleach 或 lxml
        # 以下为简化示例
        # 实际使用推荐: pip install bleach
        
        return escaped
    
    # URL安全的XSS防护
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """清理URL，防止javascript:协议XSS"""
        
        url = url.strip().lower()
        
        # 危险协议黑名单
        dangerous_protocols = [
            'javascript:', 'vbscript:', 'data:text/html',
            'data:application', 'data:image/svg+xml'
        ]
        
        for protocol in dangerous_protocols:
            if url.startswith(protocol):
                return None
        
        return url
    
    # CSS清理
    @staticmethod
    def sanitize_css(css: str) -> str:
        """清理CSS，防止expression()等XSS"""
        
        # 移除危险CSS
        patterns = [
            r'expression\s*\([^)]*\)',
            r'javascript\s*:',
            r'behavior\s*:',
            r'-moz-binding\s*:',
            r'@import',
            r'url\s*\(["\']?javascript:',
        ]
        
        result = css
        for pattern in patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        
        return result

# 使用
protector = XSSProtector()

# HTML转义
print(protector.escape_html('<script>alert(1)</script>'))
# 输出: &lt;script&gt;alert(1)&lt;/script&gt;

# URL清理
print(protector.sanitize_url('javascript:alert(1)'))  # None
print(protector.sanitize_url('https://example.com'))  # https://example.com
```

```python
# Python - 使用Bleach库（推荐）
# pip install bleach

import bleach

class HTMLSanitizer:
    """使用Bleach的HTML清理器"""
    
    # 允许的标签白名单
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'i', 'b',
        'a', 'img', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'pre', 'code'
    ]
    
    # 允许的属性白名单
    ALLOWED_ATTRS = {
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'width', 'height'],
        '*': ['class', 'id']
    }
    
    # 允许的协议白名单
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    @classmethod
    def clean(cls, html: str) -> str:
        """清理HTML内容"""
        return bleach.clean(
            html,
            tags=cls.ALLOWED_TAGS,
            attributes=cls.ALLOWED_ATTRS,
            protocols=cls.ALLOWED_PROTOCOLS,
            strip=True
        )
    
    @classmethod
    def clean_and_linkify(cls, text: str) -> str:
        """清理并自动转换URL为链接"""
        return bleach.linkify(
            bleach.clean(text, tags=cls.ALLOWED_TAGS),
            protocols=cls.ALLOWED_PROTOCOLS
        )

# 使用
sanitizer = HTMLSanitizer()

# 清理危险HTML
dirty = '<script>alert(1)</script><p onclick="evil()">Hello</p>'
clean = sanitizer.clean(dirty)
print(clean)
# 输出: &lt;script&gt;alert(1)&lt;/script&gt;<p>Hello</p>
```

```javascript
// Node.js - XSS防护
const validator = require('validator');
const DOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');

// 创建DOMPurify实例
const window = new JSDOM('').window;
const dompurify = DOMPurify(window);

class XSSProtector {
  // 基础转义
  static escapeHtml(text) {
    return validator.escape(text);
  }
  
  // HTML清理（白名单模式）
  static sanitizeHtml(html, options = {}) {
    const defaultOptions = {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a', 'img'],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title'],
      ALLOW_DATA_ATTR: false
    };
    
    return dompurify.sanitize(html, { ...defaultOptions, ...options });
  }
  
  // URL清理
  static sanitizeUrl(url) {
    // 检查危险协议
    const dangerous = /^(javascript|vbscript|data:text\/html)/i;
    if (dangerous.test(url)) return null;
    
    return url;
  }
  
  // 属性清理
  static sanitizeAttribute(attr, value) {
    const allowedAttrs = {
      a: ['href', 'title', 'target', 'rel'],
      img: ['src', 'alt', 'width', 'height']
    };
    
    const [tag, name] = attr.split('.');
    if (allowedAttrs[tag]?.includes(name)) {
      return value;
    }
    return null;
  }
}

// 使用
const dirty = '<script>alert(1)</script><p>Hello</p>';
console.log(XSSProtector.sanitizeHtml(dirty));
// 输出: <p>Hello</p>

console.log(XSSProtector.escapeHtml('<script>'));
// 输出: &lt;script&gt;
```

---

### 4. CSRF防护

#### 4.1 Token验证

```python
# Python - CSRF防护（Flask示例）
from flask import Flask, request, session, jsonify
import secrets
import hmac
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

class CSRFProtector:
    """CSRF Token管理"""
    
    TOKEN_LENGTH = 32
    
    @classmethod
    def generate_token(cls) -> str:
        """生成CSRF Token"""
        return secrets.token_hex(cls.TOKEN_LENGTH)
    
    @classmethod
    def get_session_token(cls) -> str:
        """获取或创建Session中的Token"""
        if 'csrf_token' not in session:
            session['csrf_token'] = cls.generate_token()
        return session['csrf_token']
    
    @classmethod
    def validate_token(cls, token: str) -> bool:
        """验证Token"""
        session_token = session.get('csrf_token')
        
        if not session_token or not token:
            return False
        
        # 使用恒定时间比较（防止时序攻击）
        return hmac.compare_digest(session_token, token)
    
    @classmethod
    def rotate_token(cls):
        """轮换Token（使用后更换）"""
        session['csrf_token'] = cls.generate_token()

# CSRF装饰器
def csrf_protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取Token（支持Header和表单）
        token = request.headers.get('X-CSRF-Token') or \
                request.form.get('csrf_token')
        
        if not CSRFProtector.validate_token(token):
            return jsonify({'error': 'Invalid CSRF token'}), 403
        
        # 轮换Token
        CSRFProtector.rotate_token()
        
        return f(*args, **kwargs)
    return decorated_function

# 路由
@app.route('/api/csrf-token', methods=['GET'])
def get_csrf_token():
    """获取CSRF Token"""
    return jsonify({'csrf_token': CSRFProtector.get_session_token()})

@app.route('/api/submit', methods=['POST'])
@csrf_protected
def submit_form():
    """需要CSRF保护的接口"""
    data = request.json
    return jsonify({'success': True, 'data': data})

# 使用示例
if __name__ == '__main__':
    # 客户端流程：
    # 1. GET /api/csrf-token 获取token
    # 2. POST请求时，在Header中携带 X-CSRF-Token: <token>
    # 或在表单中添加 <input type="hidden" name="csrf_token" value="<token>">
    app.run()
```

```javascript
// Node.js - CSRF防护（Express示例）
const express = require('express');
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

const app = express();

app.use(cookieParser());
app.use(express.json());

// CSRF保护中间件
const csrfProtection = csrf({ cookie: true });

// 获取CSRF Token
app.get('/api/csrf-token', csrfProtection, (req, res) => {
  res.json({ csrfToken: req.csrfToken() });
});

// 需要CSRF保护的路由
app.post('/api/submit', csrfProtection, (req, res) => {
  res.json({ success: true, data: req.body });
});

// 错误处理
app.use((err, req, res, next) => {
  if (err.code === 'EBADCSRFTOKEN') {
    return res.status(403).json({ error: 'Invalid CSRF token' });
  }
  next(err);
});

// 前端集成示例
/*
// 获取Token
const response = await fetch('/api/csrf-token');
const { csrfToken } = await response.json();

// 发送请求时携带Token
await fetch('/api/submit', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': csrfToken
  },
  body: JSON.stringify(data)
});
*/

app.listen(3000);
```

#### 4.2 SameSite Cookie

```python
# Python - Flask Cookie安全配置
from flask import Flask, make_response

app = Flask(__name__)

@app.route('/set-cookie')
def set_secure_cookie():
    """设置安全的Cookie"""
    response = make_response('Cookie set')
    
    # CSRF防护：SameSite属性
    response.set_cookie(
        'session_id',
        value='abc123',
        httponly=True,      # 防止JS读取
        secure=True,        # 仅HTTPS
        samesite='Strict'   # 或 'Lax'
    )
    
    return response

# SameSite属性说明：
# - Strict: 完全禁止跨站发送Cookie（最安全，可能影响用户体验）
# - Lax: 允许GET请求跨站发送（推荐，平衡安全和体验）
# - None: 允许跨站发送（需要secure=True）
```

---

### 5. 文件上传验证

```python
# Python - 安全的文件上传验证
import os
import imghdr
import magic
import hashlib
from pathlib import Path
from typing import Optional, Tuple

class FileUploadValidator:
    """安全的文件上传验证器"""
    
    # 允许的文件类型（白名单）
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt'],
        'data': ['.csv', '.json', '.xml']
    }
    
    # 允许的MIME类型（白名单）
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf',
        'text/plain', 'text/csv',
        'application/json', 'application/xml'
    }
    
    # 最大文件大小（字节）
    MAX_SIZES = {
        'image': 5 * 1024 * 1024,      # 5MB
        'document': 10 * 1024 * 1024,  # 10MB
        'data': 1 * 1024 * 1024        # 1MB
    }
    
    @classmethod
    def validate(
        cls,
        file_content: bytes,
        filename: str,
        category: str = 'image'
    ) -> Tuple[bool, Optional[str]]:
        """
        验证上传文件
        返回: (是否有效, 错误信息)
        """
        
        # 1. 文件名验证
        ext = Path(filename).suffix.lower()
        if ext not in cls.ALLOWED_EXTENSIONS.get(category, []):
            return False, f'不允许的文件扩展名: {ext}'
        
        # 2. 文件大小验证
        max_size = cls.MAX_SIZES.get(category, 5 * 1024 * 1024)
        if len(file_content) > max_size:
            return False, f'文件大小超过限制: {max_size / 1024 / 1024}MB'
        
        # 3. MIME类型验证（通过文件内容）
        mime_type = magic.from_buffer(file_content, mime=True)
        if mime_type not in cls.ALLOWED_MIME_TYPES:
            return False, f'不允许的MIME类型: {mime_type}'
        
        # 4. 扩展名与内容匹配验证
        if not cls._validate_content_match(file_content, ext):
            return False, '文件扩展名与内容不匹配'
        
        # 5. 恶意文件检测
        if cls._detect_malicious(file_content):
            return False, '检测到可疑文件内容'
        
        return True, None
    
    @classmethod
    def _validate_content_match(cls, content: bytes, ext: str) -> bool:
        """验证文件扩展名与实际内容是否匹配"""
        
        # 图片类型验证
        if ext in ['.jpg', '.jpeg']:
            return imghdr.what(None, h=content) == 'jpeg'
        elif ext == '.png':
            return imghdr.what(None, h=content) == 'png'
        elif ext == '.gif':
            return imghdr.what(None, h=content) == 'gif'
        
        # PDF验证
        if ext == '.pdf':
            return content[:4] == b'%PDF'
        
        return True
    
    @classmethod
    def _detect_malicious(cls, content: bytes) -> bool:
        """检测恶意文件特征"""
        
        # 转换为小写字符串检查
        content_lower = content.lower()
        
        # 危险特征检测
        dangerous_patterns = [
            b'<script',
            b'<?php',
            b'<%',
            b'#!/',
            b'eval(',
            b'exec(',
            b'system(',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                return True
        
        return False
    
    @classmethod
    def generate_safe_filename(cls, original: str) -> str:
        """生成安全的文件名"""
        
        # 获取扩展名
        ext = Path(original).suffix.lower()
        
        # 生成随机文件名
        random_name = hashlib.sha256(
            os.urandom(32) + original.encode()
        ).hexdigest()[:16]
        
        return f'{random_name}{ext}'

# Flask使用示例
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    content = file.read()
    
    # 验证文件
    is_valid, error = FileUploadValidator.validate(
        content,
        file.filename,
        category='image'
    )
    
    if not is_valid:
        return jsonify({'error': error}), 400
    
    # 生成安全文件名
    safe_name = FileUploadValidator.generate_safe_filename(file.filename)
    
    # 保存文件（确保保存目录不可执行）
    save_path = os.path.join('/safe/upload/path', safe_name)
    with open(save_path, 'wb') as f:
        f.write(content)
    
    return jsonify({'success': True, 'filename': safe_name})
```

```javascript
// Node.js - 文件上传验证
const path = require('path');
const crypto = require('crypto');
const fileType = require('file-type');
const sharp = require('sharp');

class FileUploadValidator {
  constructor() {
    // 允许的文件类型白名单
    this.allowedExtensions = {
      image: ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
      document: ['.pdf', '.txt'],
      data: ['.csv', '.json']
    };
    
    // 允许的MIME类型白名单
    this.allowedMimeTypes = new Set([
      'image/jpeg', 'image/png', 'image/gif', 'image/webp',
      'application/pdf', 'text/plain', 'text/csv', 'application/json'
    ]);
    
    // 最大文件大小
    this.maxSizes = {
      image: 5 * 1024 * 1024,      // 5MB
      document: 10 * 1024 * 1024,  // 10MB
      data: 1 * 1024 * 1024        // 1MB
    };
  }
  
  async validate(buffer, filename, category = 'image') {
    const ext = path.extname(filename).toLowerCase();
    
    // 1. 扩展名验证
    if (!this.allowedExtensions[category]?.includes(ext)) {
      return { valid: false, error: `不允许的扩展名: ${ext}` };
    }
    
    // 2. 大小验证
    const maxSize = this.maxSizes[category] || 5 * 1024 * 1024;
    if (buffer.length > maxSize) {
      return { valid: false, error: `文件大小超过限制` };
    }
    
    // 3. MIME类型验证（通过文件内容）
    const type = await fileType.fromBuffer(buffer);
    if (!type || !this.allowedMimeTypes.has(type.mime)) {
      return { valid: false, error: `不允许的MIME类型` };
    }
    
    // 4. 扩展名与内容匹配
    const mimeToExt = {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/gif': ['.gif'],
      'image/webp': ['.webp']
    };
    
    const allowedExts = mimeToExt[type.mime];
    if (allowedExts && !allowedExts.includes(ext)) {
      return { valid: false, error: '扩展名与内容不匹配' };
    }
    
    // 5. 恶意内容检测
    if (this.detectMalicious(buffer)) {
      return { valid: false, error: '检测到可疑内容' };
    }
    
    return { valid: true };
  }
  
  detectMalicious(buffer) {
    const content = buffer.toString('utf8').toLowerCase();
    const patterns = [
      '<script', '<?php', '<%', '#!/', 'eval(', 'exec('
    ];
    
    return patterns.some(p => content.includes(p));
  }
  
  generateSafeFilename(original) {
    const ext = path.extname(original).toLowerCase();
    const randomName = crypto.randomBytes(16).toString('hex');
    return `${randomName}${ext}`;
  }
  
  // 图片处理（防止图片马）
  async processImage(buffer) {
    try {
      // 重新编码图片，移除可能的恶意代码
      return await sharp(buffer)
        .toFormat('jpeg', { quality: 90 })
        .toBuffer();
    } catch (error) {
      throw new Error('图片处理失败');
    }
  }
}

// Express使用示例
const express = require('express');
const multer = require('multer');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });
const validator = new FileUploadValidator();

app.post('/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file provided' });
  }
  
  // 验证文件
  const result = await validator.validate(
    req.file.buffer,
    req.file.originalname,
    'image'
  );
  
  if (!result.valid) {
    return res.status(400).json({ error: result.error });
  }
  
  // 生成安全文件名
  const safeName = validator.generateSafeFilename(req.file.originalname);
  
  // 处理图片（可选）
  const processedBuffer = await validator.processImage(req.file.buffer);
  
  // 保存文件...
  
  res.json({ success: true, filename: safeName });
});
```

---

### 6. JSON Schema验证

#### 6.1 Python JSON Schema

```python
# Python - JSON Schema验证
import json
from jsonschema import validate, ValidationError, Draft7Validator
from typing import Dict, Any

class JSONSchemaValidator:
    """JSON Schema验证器"""
    
    # API请求Schema
    API_SCHEMAS = {
        'user_create': {
            'type': 'object',
            'required': ['username', 'email', 'password'],
            'properties': {
                'username': {
                    'type': 'string',
                    'minLength': 3,
                    'maxLength': 20,
                    'pattern': '^[a-zA-Z0-9_]+$'
                },
                'email': {
                    'type': 'string',
                    'format': 'email'
                },
                'password': {
                    'type': 'string',
                    'minLength': 8
                },
                'age': {
                    'type': 'integer',
                    'minimum': 18,
                    'maximum': 120
                },
                'role': {
                    'type': 'string',
                    'enum': ['user', 'admin', 'moderator']
                }
            },
            'additionalProperties': False  # 禁止额外字段
        },
        
        'product_create': {
            'type': 'object',
            'required': ['name', 'price'],
            'properties': {
                'name': {
                    'type': 'string',
                    'minLength': 1,
                    'maxLength': 200
                },
                'price': {
                    'type': 'number',
                    'minimum': 0,
                    'exclusiveMinimum': True
                },
                'description': {
                    'type': 'string',
                    'maxLength': 2000
                },
                'tags': {
                    'type': 'array',
                    'items': {
                        'type': 'string',
                        'minLength': 1,
                        'maxLength': 50
                    },
                    'minItems': 0,
                    'maxItems': 10,
                    'uniqueItems': True
                }
            }
        }
    }
    
    @classmethod
    def validate_data(
        cls,
        data: Dict[str, Any],
        schema_name: str
    ) -> tuple[bool, list]:
        """
        验证JSON数据
        返回: (是否有效, 错误列表)
        """
        
        schema = cls.API_SCHEMAS.get(schema_name)
        if not schema:
            return False, [f'Unknown schema: {schema_name}']
        
        validator = Draft7Validator(schema)
        errors = list(validator.iter_errors(data))
        
        if errors:
            error_messages = [
                f'{error.path}: {error.message}'
                for error in errors
            ]
            return False, error_messages
        
        return True, []
    
    @classmethod
    def validate_custom_schema(
        cls,
        data: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> tuple[bool, list]:
        """使用自定义Schema验证"""
        
        try:
            validate(instance=data, schema=schema)
            return True, []
        except ValidationError as e:
            return False, [str(e)]

# Flask使用示例
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    
    # 验证数据
    is_valid, errors = JSONSchemaValidator.validate_data(data, 'user_create')
    
    if not is_valid:
        return jsonify({'errors': errors}), 400
    
    # 处理有效数据...
    return jsonify({'success': True})

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    
    is_valid, errors = JSONSchemaValidator.validate_data(data, 'product_create')
    
    if not is_valid:
        return jsonify({'errors': errors}), 400
    
    # 处理有效数据...
    return jsonify({'success': True})
```

#### 6.2 Node.js JSON Schema

```javascript
// Node.js - JSON Schema验证（Ajv）
const Ajv = require('ajv');
const addFormats = require('ajv-formats');

const ajv = new Ajv({ allErrors: true });
addFormats(ajv);

class JSONSchemaValidator {
  constructor() {
    // 定义Schema
    this.schemas = {
      userCreate: {
        type: 'object',
        required: ['username', 'email', 'password'],
        properties: {
          username: {
            type: 'string',
            minLength: 3,
            maxLength: 20,
            pattern: '^[a-zA-Z0-9_]+$'
          },
          email: {
            type: 'string',
            format: 'email'
          },
          password: {
            type: 'string',
            minLength: 8
          },
          age: {
            type: 'integer',
            minimum: 18,
            maximum: 120
          },
          role: {
            type: 'string',
            enum: ['user', 'admin', 'moderator']
          }
        },
        additionalProperties: false
      },
      
      productCreate: {
        type: 'object',
        required: ['name', 'price'],
        properties: {
          name: {
            type: 'string',
            minLength: 1,
            maxLength: 200
          },
          price: {
            type: 'number',
            minimum: 0,
            exclusiveMinimum: true
          },
          tags: {
            type: 'array',
            items: {
              type: 'string',
              minLength: 1,
              maxLength: 50
            },
            minItems: 0,
            maxItems: 10,
            uniqueItems: true
          }
        }
      }
    };
    
    // 编译所有Schema
    this.validators = {};
    for (const [name, schema] of Object.entries(this.schemas)) {
      this.validators[name] = ajv.compile(schema);
    }
  }
  
  validate(data, schemaName) {
    const validate = this.validators[schemaName];
    
    if (!validate) {
      return {
        valid: false,
        errors: [`Unknown schema: ${schemaName}`]
      };
    }
    
    const valid = validate(data);
    
    if (!valid) {
      return {
        valid: false,
        errors: validate.errors.map(e => 
          `${e.instancePath} ${e.message}`
        )
      };
    }
    
    return { valid: true };
  }
  
  // 自定义格式验证
  addCustomFormat(name, regex) {
    ajv.addFormat(name, {
      type: 'string',
      validate: (data) => regex.test(data)
    });
  }
}

// 添加自定义格式
const validator = new JSONSchemaValidator();
validator.addCustomFormat('phone-cn', /^1[3-9]\d{9}$/);

// Express使用示例
const express = require('express');
const app = express();

app.use(express.json());

// 验证中间件
function validateSchema(schemaName) {
  return (req, res, next) => {
    const result = validator.validate(req.body, schemaName);
    
    if (!result.valid) {
      return res.status(400).json({ errors: result.errors });
    }
    
    next();
  };
}

app.post('/api/users', validateSchema('userCreate'), (req, res) => {
  // 处理已验证的数据
  res.json({ success: true, data: req.body });
});

app.post('/api/products', validateSchema('productCreate'), (req, res) => {
  res.json({ success: true, data: req.body });
});
```

---

### 7. 正则表达式库

```python
# Python - 常用验证正则
import re

class RegexPatterns:
    """常用验证正则表达式"""
    
    # 身份验证
    EMAIL = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    PASSWORD_STRONG = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    USERNAME = r'^[a-zA-Z0-9_]{3,20}$'
    
    # 电话号码
    PHONE_CN = r'^1[3-9]\d{9}$'
    PHONE_US = r'^\+1[2-9]\d{2}[2-9]\d{6}$'
    PHONE_INTERNATIONAL = r'^\+[1-9]\d{6,14}$'
    
    # 身份证
    ID_CARD_CN = r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$'
    
    # 信用卡
    CREDIT_CARD_VISA = r'^4[0-9]{12}(?:[0-9]{3})?$'
    CREDIT_CARD_MASTERCARD = r'^5[1-5][0-9]{14}$'
    
    # 网络
    URL = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    DOMAIN = r'^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$'
    IPV4 = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    IPV6 = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    
    # 日期
    DATE_ISO = r'^\d{4}-\d{2}-\d{2}$'
    DATETIME_ISO = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
    TIME_24H = r'^([01]?[0-9]|2[0-3]):[0-5][0-9](:[0-5][0-9])?$'
    
    # 其他
    SLUG = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    HEX_COLOR = r'^#?([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$'
    UUID = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    BASE64 = r'^[A-Za-z0-9+/]+={0,2}$'
    
    @classmethod
    def validate(cls, pattern: str, value: str) -> bool:
        """验证值是否匹配模式"""
        return bool(re.match(pattern, value))
    
    @classmethod
    def extract(cls, pattern: str, text: str) -> list:
        """提取所有匹配项"""
        return re.findall(pattern, text)
    
    @classmethod
    def sanitize(cls, pattern: str, text: str, replacement: str = '') -> str:
        """移除所有匹配项"""
        return re.sub(pattern, replacement, text)

# 使用示例
print(RegexPatterns.validate(RegexPatterns.EMAIL, 'test@example.com'))  # True
print(RegexPatterns.validate(RegexPatterns.PHONE_CN, '13800138000'))   # True
print(RegexPatterns.validate(RegexPatterns.UUID, '550e8400-e29b-41d4-a716-446655440000'))  # True
```

---

## 免费验证库对比

### Python库对比

| 库名 | 类型 | 特点 | 免费额度 | 适用场景 |
|------|------|------|---------|---------|
| **Pydantic** | Schema验证 | 类型安全、自动转换、性能优秀 | 完全免费 | API验证、配置管理 |
| **marshmallow** | Schema验证 | 灵活、可定制、ORM集成 | 完全免费 | 复杂数据序列化 |
| **cerberus** | Schema验证 | 轻量、规则可扩展 | 完全免费 | 配置文件验证 |
| **jsonschema** | JSON Schema | 标准实现、全功能 | 完全免费 | JSON API验证 |
| **WTForms** | 表单验证 | Flask集成、CSRF保护 | 完全免费 | Web表单验证 |
| **bleach** | HTML清理 | 白名单式XSS防护 | 完全免费 | 富文本过滤 |
| **email-validator** | 邮箱验证 | DNS验证、规范化 | 完全免费 | 邮箱注册 |

### Node.js库对比

| 库名 | 类型 | 特点 | 免费额度 | 适用场景 |
|------|------|------|---------|---------|
| **Zod** | Schema验证 | TypeScript优先、类型推导 | 完全免费 | 前后端验证 |
| **Joi** | Schema验证 | 功能丰富、生态成熟 | 完全免费 | 企业级验证 |
| **Yup** | Schema验证 | 轻量、Promise支持 | 完全免费 | 表单验证 |
| **Ajv** | JSON Schema | 性能最高、标准兼容 | 完全免费 | API验证 |
| **validator.js** | 字符串验证 | 120+验证器、零依赖 | 完全免费 | 通用验证 |
| **DOMPurify** | HTML清理 | 浏览器/Node双端 | 完全免费 | XSS防护 |
| **express-validator** | Express集成 | 中间件、sanitize | 完全免费 | Express应用 |

---

## 成本估算

### 全栈免费方案

| 验证领域 | 免费方案 | 月成本 | 开发时间 |
|---------|---------|--------|---------|
| Schema验证 | Pydantic/Zod | $0 | 2小时 |
| SQL注入防护 | 参数化查询 | $0 | 1小时 |
| XSS防护 | bleach/DOMPurify | $0 | 2小时 |
| CSRF防护 | 内置Token机制 | $0 | 1小时 |
| 文件验证 | magic/file-type | $0 | 2小时 |
| **总计** | | **$0** | **8小时** |

---

## 与其他武器配合

```
输入验证防御链
┌─────────────────────────────────────────────────────┐
│              前置：认证授权                          │
│  确保只有授权用户能提交数据                          │
├─────────────────────────────────────────────────────┤
│              核心：输入验证                          │
│  Schema验证 → 类型检查 → 格式验证 → 业务规则        │
├─────────────────────────────────────────────────────┤
│              后置：安全输出                          │
│  HTML转义 → JSON编码 → 安全Header                   │
└─────────────────────────────────────────────────────┘

配合关系：
- 前置武器：认证授权（确保用户身份）
- 后置武器：API安全（Rate Limit + 安全Header）
- 协同武器：WAF（ModSecurity规则补充）
- 监控武器：日志审计（记录验证失败）
```

---

## 常见问题

### Q: 白名单和黑名单哪个更好？
A: **白名单优于黑名单**。黑名单总会有遗漏，攻击者会不断发现新的绕过方法。白名单明确只允许已知安全的输入，更安全。

### Q: 前端验证就够了，为什么还需要后端验证？
A: 前端验证可以被绕过（禁用JS、修改代码、直接调用API）。**前端验证提升用户体验，后端验证保障安全**，两者缺一不可。

### Q: 正则表达式能防止SQL注入吗？
A: 不能完全依赖。**参数化查询是SQL注入防护的核心**。正则表达式只能作为辅助手段，验证输入格式。

### Q: 如何处理大量验证错误？
A: 返回所有错误一次性修复，而不是逐个返回。使用Schema验证库的错误收集功能。

### Q: 文件上传验证有什么最佳实践？
A: 
1. 验证文件内容而非仅扩展名
2. 白名单限制MIME类型
3. 重新处理图片（移除EXIF、重编码）
4. 存储到不可执行目录
5. 生成随机文件名

---

## 推荐实现

### Python生态
- Schema验证：**Pydantic** - https://pydantic-docs.helpmanual.io/ - 完全免费
- HTML清理：**Bleach** - https://bleach.readthedocs.io/ - 完全免费
- 表单验证：**WTForms** - https://wtforms.readthedocs.io/ - 完全免费
- JSON Schema：**jsonschema** - https://python-jsonschema.readthedocs.io/ - 完全免费

### Node.js生态
- Schema验证：**Zod** - https://zod.dev/ - 完全免费
- 字符串验证：**validator.js** - https://github.com/validatorjs/validator.js - 完全免费
- HTML清理：**DOMPurify** - https://github.com/cure53/DOMPurify - 完全免费
- Express集成：**express-validator** - https://express-validator.github.io/ - 完全免费

### 多语言工具
- JSON Schema规范：**json-schema.org** - https://json-schema.org/ - 标准规范
- 正则表达式测试：**regex101** - https://regex101.com/ - 在线工具

---

## 下一步行动

### Week 1: 基础验证
- [ ] 引入Pydantic/Zod进行Schema验证
- [ ] 实施参数化查询（替换字符串拼接）
- [ ] 添加基础HTML转义

### Week 2: 深度防护
- [ ] 实施CSRF Token机制
- [ ] 添加文件上传验证
- [ ] 部署Bleach/DOMPurify

### Week 3: 全面加固
- [ ] 配置JSON Schema验证所有API
- [ ] 添加自定义验证器（业务规则）
- [ ] 实施审计日志

### 持续维护
- [ ] 定期审查验证规则
- [ ] 关注新攻击模式
- [ ] 更新依赖库版本

---

**最后更新**: 2026-06-11
**维护状态**: 🟢 活跃维护
**下次验证**: 2026-07-11
