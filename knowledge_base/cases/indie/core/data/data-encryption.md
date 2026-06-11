# 数据加密缺失风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $50-200/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的敏感数据（密码、身份证、银行卡号）以明文存储在数据库中，一旦数据库泄露或被拖库，攻击者可以直接获取所有用户隐私信息。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 存储用户密码、身份证、银行卡等敏感信息
- [ ] 数据库字段直接存储原始值
- [ ] **密码使用可逆加密而非哈希**
- [ ] **身份证、手机号明文存储**
- [ ] 日志中打印敏感数据
- [ ] 备份文件未加密
→ 勾选≥2项，尤其是中间两项，**立即行动**

### 一句话防御
密码必须使用 bcrypt/argon2 单向哈希，其他敏感字段（身份证、银行卡）使用 AES 加密存储，密钥通过环境变量或密钥管理服务管理。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查现有数据存储**：
   ```sql
   -- 检查密码字段
   SELECT id, password FROM users LIMIT 5;
   -- 如果看到明文密码 = 危险！
   -- 如果看到 $2b$ 开头 = bcrypt 哈希（安全）
   
   -- 检查敏感字段
   SELECT id, id_card, phone, bank_card FROM users LIMIT 5;
   -- 如果看到明文 = 需要加密
   ```

2. [ ] **密码哈希处理**：
   ```javascript
   // 使用 bcrypt
   const bcrypt = require('bcryptjs')
   
   // 哈希密码
   const hashedPassword = await bcrypt.hash(plainPassword, 12)
   // 存储到数据库: $2b$12$xxxxx
   
   // 验证密码
   const isValid = await bcrypt.compare(inputPassword, hashedPassword)
   ```

3. [ ] **敏感字段加密**：
   ```javascript
   // 使用 AES-256-GCM 加密
   const crypto = require('crypto')
   
   const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY  // 32字节
   
   function encrypt(text) {
     const iv = crypto.randomBytes(16)
     const cipher = crypto.createCipheriv('aes-256-gcm', ENCRYPTION_KEY, iv)
     
     let encrypted = cipher.update(text, 'utf8', 'hex')
     encrypted += cipher.final('hex')
     
     const authTag = cipher.getAuthTag()
     
     return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted
   }
   
   function decrypt(encrypted) {
     const [ivHex, authTagHex, data] = encrypted.split(':')
     const iv = Buffer.from(ivHex, 'hex')
     const authTag = Buffer.from(authTagHex, 'hex')
     
     const decipher = crypto.createDecipheriv('aes-256-gcm', ENCRYPTION_KEY, iv)
     decipher.setAuthTag(authTag)
     
     let decrypted = decipher.update(data, 'hex', 'utf8')
     decrypted += decipher.final('utf8')
     
     return decrypted
   }
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **迁移现有数据**：
   ```javascript
   // 数据迁移脚本
   async function migratePasswords() {
     const users = await User.find({})
     
     for (const user of users) {
       // 检查是否已哈希
       if (!user.password.startsWith('$2b$')) {
         // 哈希明文密码
         const hashed = await bcrypt.hash(user.password, 12)
         await User.updateOne({ _id: user._id }, { password: hashed })
         console.log(`用户 ${user.email} 密码已哈希`)
       }
     }
   }
   ```

2. [ ] **生成加密密钥**：
   ```bash
   # 生成 32 字节密钥
   node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
   
   # 添加到 .env
   echo "ENCRYPTION_KEY=生成的密钥" >> .env
   ```

3. [ ] **禁用敏感日志**：
   ```javascript
   // 使用日志脱敏
   const safeLog = (data) => {
     const sensitiveFields = ['password', 'idCard', 'bankCard', 'phone']
     const masked = { ...data }
     
     sensitiveFields.forEach(field => {
       if (masked[field]) {
         masked[field] = '***'
       }
     })
     
     console.log(masked)
   }
   ```

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用数据库加密扩展**：PostgreSQL pgcrypto、MySQL AES 函数
2. [ ] **启用备份加密**：云服务商提供的加密备份
3. [ ] **使用密钥管理服务**：AWS KMS、HashiCorp Vault

### 字段级加密实现

**完整的加密工具类**：

```typescript
// utils/encryption.ts
import crypto from 'crypto'

interface EncryptedData {
  iv: string
  authTag: string
  data: string
}

class FieldEncryption {
  private algorithm = 'aes-256-gcm'
  private key: Buffer

  constructor(encryptionKey: string) {
    // 密钥必须是 32 字节（256 位）
    this.key = Buffer.from(encryptionKey, 'base64')
    
    if (this.key.length !== 32) {
      throw new Error('加密密钥必须是 32 字节')
    }
  }

  /**
   * 加密文本
   */
  encrypt(plaintext: string): string {
    const iv = crypto.randomBytes(16)
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv)

    let encrypted = cipher.update(plaintext, 'utf8', 'hex')
    encrypted += cipher.final('hex')

    const authTag = cipher.getAuthTag()

    // 格式: iv:authTag:encrypted
    return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`
  }

  /**
   * 解密文本
   */
  decrypt(encrypted: string): string {
    const parts = encrypted.split(':')
    
    if (parts.length !== 3) {
      throw new Error('无效的加密数据格式')
    }

    const [ivHex, authTagHex, data] = parts
    const iv = Buffer.from(ivHex, 'hex')
    const authTag = Buffer.from(authTagHex, 'hex')

    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv)
    decipher.setAuthTag(authTag)

    let decrypted = decipher.update(data, 'hex', 'utf8')
    decrypted += decipher.final('utf8')

    return decrypted
  }

  /**
   * 加密对象（指定字段）
   */
  encryptFields<T extends Record<string, any>>(
    obj: T,
    fields: (keyof T)[]
  ): T {
    const result = { ...obj }

    for (const field of fields) {
      if (result[field] && typeof result[field] === 'string') {
        result[field] = this.encrypt(result[field]) as any
      }
    }

    return result
  }

  /**
   * 解密对象（指定字段）
   */
  decryptFields<T extends Record<string, any>>(
    obj: T,
    fields: (keyof T)[]
  ): T {
    const result = { ...obj }

    for (const field of fields) {
      if (result[field] && typeof result[field] === 'string') {
        try {
          result[field] = this.decrypt(result[field]) as any
        } catch (error) {
          // 解密失败，可能不是加密数据
          console.warn(`字段 ${String(field)} 解密失败`)
        }
      }
    }

    return result
  }

  /**
   * 哈希（单向，用于密码）
   */
  async hashPassword(password: string): Promise<string> {
    const bcrypt = await import('bcryptjs')
    return bcrypt.hash(password, 12)
  }

  /**
   * 验证密码
   */
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    const bcrypt = await import('bcryptjs')
    return bcrypt.compare(password, hash)
  }
}

// 单例
const encryption = new FieldEncryption(process.env.ENCRYPTION_KEY!)

export default encryption
export { FieldEncryption }
```

**Mongoose Schema 集成**：

```typescript
// models/User.ts
import mongoose, { Schema, Document } from 'mongoose'
import encryption from '@/utils/encryption'

interface IUser extends Document {
  email: string
  password: string  // bcrypt 哈希
  phone?: string    // AES 加密
  idCard?: string   // AES 加密
  bankCard?: string // AES 加密
  name: string
  createdAt: Date
  updatedAt: Date
}

const UserSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      index: true
    },
    password: {
      type: String,
      required: true,
      select: false  // 默认不返回
    },
    phone: {
      type: String,
      select: false
    },
    idCard: {
      type: String,
      select: false
    },
    bankCard: {
      type: String,
      select: false
    },
    name: {
      type: String,
      required: true
    }
  },
  {
    timestamps: true
  }
)

// 保存前加密敏感字段
UserSchema.pre('save', async function(next) {
  // 密码哈希
  if (this.isModified('password') && !this.password.startsWith('$2b$')) {
    this.password = await encryption.hashPassword(this.password)
  }

  // 敏感字段加密
  if (this.isModified('phone') && this.phone) {
    this.phone = encryption.encrypt(this.phone)
  }

  if (this.isModified('idCard') && this.idCard) {
    this.idCard = encryption.encrypt(this.idCard)
  }

  if (this.isModified('bankCard') && this.bankCard) {
    this.bankCard = encryption.encrypt(this.bankCard)
  }

  next()
})

// 解密方法
UserSchema.methods.decryptFields = function() {
  const user = this.toObject()
  
  if (user.phone) {
    user.phone = encryption.decrypt(user.phone)
  }
  
  if (user.idCard) {
    user.idCard = encryption.decrypt(user.idCard)
  }
  
  if (user.bankCard) {
    user.bankCard = encryption.decrypt(user.bankCard)
  }
  
  return user
}

// 静态方法：安全创建
UserSchema.statics.createSecure = async function(data: Partial<IUser>) {
  const user = new this(data)
  await user.save()
  return user
}

export const User = mongoose.model<IUser>('User', UserSchema)
```

### 加密库推荐

| 用途 | 推荐库 | 说明 |
|------|--------|------|
| 密码哈希 | bcrypt / argon2 | 单向哈希，防彩虹表 |
| 对称加密 | crypto (Node.js) | AES-256-GCM |
| 非对称加密 | node-rsa | RSA-OAEP |
| 密钥派生 | crypto.pbkdf2 | PBKDF2 / scrypt |
| 数据库加密 | pgcrypto (PostgreSQL) | 数据库层加密 |
| 密钥管理 | AWS KMS / Vault | 企业级密钥管理 |

**各语言实现参考**：

```javascript
// Node.js
const bcrypt = require('bcryptjs')
const crypto = require('crypto')

// Python
import bcrypt
from cryptography.fernet import Fernet

# 密码哈希
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))

# 对称加密
key = Fernet.generate_key()
f = Fernet(key)
encrypted = f.encrypt(data.encode())

# Go
import (
    "golang.org/x/crypto/bcrypt"
    "crypto/aes"
    "crypto/cipher"
)

hashed, _ := bcrypt.GenerateFromPassword([]byte(password), 12)
```

### 推荐工具
- **免费**：
  - [bcrypt.js](https://github.com/dcodeIO/bcrypt.js) - 密码哈希
  - [Node.js crypto](https://nodejs.org/api/crypto.html) - 内置加密模块
  - [argon2](https://github.com/ranisalt/argon2) - 更安全的密码哈希

- **低成本**：
  - [AWS KMS](https://aws.amazon.com/kms/) - $1/月 + $0.03/10000 次请求
  - [HashiCorp Vault](https://www.vaultproject.io/) - 开源免费，托管版 $0.50/小时
  - [Google Cloud KMS](https://cloud.google.com/kms) - 类似 AWS KMS

### 验证方法
- [ ] **密码检查**：数据库中密码字段应为 `$2b$` 或 `$argon2` 开头
- [ ] **加密检查**：敏感字段应为 `iv:authTag:data` 格式
- [ ] **日志检查**：日志中不应出现明文敏感数据
- [ ] **备份检查**：备份文件应为加密格式

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2019年，某社交平台数据库被拖库，由于密码使用 MD5 哈希（弱哈希）且无盐，攻击者使用彩虹表在 24 小时内破解了 80% 的密码。同时，身份证号、手机号明文存储，导致用户隐私大规模泄露。

**后果**：
- 500 万用户密码被破解
- 身份证号泄露，用户遭遇诈骗
- 监管机构介入，罚款 ¥500 万
- 平台被迫关闭

**类似案例**：
- 2020年，某招聘网站明文存储密码，数据库泄露后直接暴露
- 2021年，某电商平台使用可逆加密，攻击者获取密钥后解密所有数据

### 攻击路径（简化版）

```
1. 获取数据库访问
   ├── SQL 注入
   ├── 数据库服务暴露
   ├── 备份文件泄露
   └── 内部人员泄露
   
2. 分析加密方式
   ├── 明文存储 → 直接使用
   ├── 可逆加密（AES-ECB）→ 尝试获取密钥
   ├── 弱哈希（MD5/SHA1）→ 彩虹表破解
   └── 强哈希（bcrypt）→ 难以破解
   
3. 批量解密/破解
   ├── 明文: 无需处理
   ├── 可逆加密: 获取密钥后批量解密
   ├── MD5: 彩虹表/字典攻击
   └── bcrypt: 计算成本极高（放弃或针对性破解）
   
4. 利用数据
   ├── 密码 → 尝试其他平台（撞库）
   ├── 身份证 → 诈骗、注册账号
   ├── 手机号 → 骚扰、钓鱼
   └── 银行卡 → 金融诈骗
```

**关键数据**：
- MD5 破解速度：100 亿次/秒（GPU）
- bcrypt 破解速度：< 10000 次/秒
- 彩虹表覆盖率：常见密码 > 90%
- 撞库成功率：10-20%

### 防御实施（低成本方案）

#### 方案A：免费方案（应用层加密）

**完整的用户模型实现**：

```typescript
// models/User.ts（完整版）
import mongoose, { Schema, Document, Model } from 'mongoose'
import bcrypt from 'bcryptjs'
import crypto from 'crypto'

// 加密配置
const ENCRYPTION_KEY = Buffer.from(process.env.ENCRYPTION_KEY!, 'base64')
const ALGORITHM = 'aes-256-gcm'

// 加密函数
function encrypt(text: string): string {
  const iv = crypto.randomBytes(16)
  const cipher = crypto.createCipheriv(ALGORITHM, ENCRYPTION_KEY, iv)
  
  let encrypted = cipher.update(text, 'utf8', 'hex')
  encrypted += cipher.final('hex')
  
  const authTag = cipher.getAuthTag()
  return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`
}

function decrypt(encrypted: string): string {
  const [ivHex, authTagHex, data] = encrypted.split(':')
  const iv = Buffer.from(ivHex, 'hex')
  const authTag = Buffer.from(authTagHex, 'hex')
  
  const decipher = crypto.createDecipheriv(ALGORITHM, ENCRYPTION_KEY, iv)
  decipher.setAuthTag(authTag)
  
  let decrypted = decipher.update(data, 'hex', 'utf8')
  decrypted += decipher.final('utf8')
  
  return decrypted
}

// 用户接口
interface IUser extends Document {
  email: string
  password: string
  profile: {
    name: string
    phone?: string
    idCard?: string
  }
  payment: {
    bankCard?: string
    bankName?: string
  }
  createdAt: Date
  updatedAt: Date
  comparePassword(password: string): Promise<boolean>
  getDecryptedProfile(): any
}

// Schema
const UserSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      index: true
    },
    password: {
      type: String,
      required: true,
      select: false
    },
    profile: {
      name: { type: String, required: true },
      phone: { type: String, select: false },
      idCard: { type: String, select: false }
    },
    payment: {
      bankCard: { type: String, select: false },
      bankName: { type: String }
    }
  },
  {
    timestamps: true
  }
)

// 保存前处理
UserSchema.pre('save', async function(next) {
  // 密码哈希
  if (this.isModified('password')) {
    if (!this.password.startsWith('$2b$')) {
      this.password = await bcrypt.hash(this.password, 12)
    }
  }

  // 敏感字段加密
  if (this.isModified('profile.phone') && this.profile.phone) {
    this.profile.phone = encrypt(this.profile.phone)
  }

  if (this.isModified('profile.idCard') && this.profile.idCard) {
    this.profile.idCard = encrypt(this.profile.idCard)
  }

  if (this.isModified('payment.bankCard') && this.payment.bankCard) {
    this.payment.bankCard = encrypt(this.payment.bankCard)
  }

  next()
})

// 密码验证方法
UserSchema.methods.comparePassword = async function(password: string): Promise<boolean> {
  return bcrypt.compare(password, this.password)
}

// 解密方法
UserSchema.methods.getDecryptedProfile = function() {
  const profile = this.toObject()
  
  if (profile.profile?.phone) {
    try {
      profile.profile.phone = decrypt(profile.profile.phone)
    } catch {}
  }
  
  if (profile.profile?.idCard) {
    try {
      profile.profile.idCard = decrypt(profile.profile.idCard)
    } catch {}
  }
  
  if (profile.payment?.bankCard) {
    try {
      profile.payment.bankCard = decrypt(profile.payment.bankCard)
    } catch {}
  }
  
  return profile
}

// 静态方法：安全查询
UserSchema.statics.findByEmail = async function(email: string) {
  return this.findOne({ email: email.toLowerCase() })
    .select('+password +profile.phone +profile.idCard +payment.bankCard')
}

// 静态方法：数据迁移
UserSchema.statics.migrateEncryption = async function() {
  const users = await this.find({})
  let migrated = 0

  for (const user of users) {
    let needsSave = false

    // 检查密码是否需要哈希
    if (!user.password.startsWith('$2b$')) {
      user.password = await bcrypt.hash(user.password, 12)
      needsSave = true
    }

    // 检查敏感字段是否需要加密
    // （假设明文数据不包含 ':' 字符）
    if (user.profile.phone && !user.profile.phone.includes(':')) {
      user.profile.phone = encrypt(user.profile.phone)
      needsSave = true
    }

    if (user.profile.idCard && !user.profile.idCard.includes(':')) {
      user.profile.idCard = encrypt(user.profile.idCard)
      needsSave = true
    }

    if (needsSave) {
      await user.save()
      migrated++
      console.log(`用户 ${user.email} 数据已迁移`)
    }
  }

  return { total: users.length, migrated }
}

export const User = mongoose.model<IUser, Model<IUser> & {
  findByEmail(email: string): Promise<IUser | null>
  migrateEncryption(): Promise<{ total: number; migrated: number }>
}>('User', UserSchema)
```

**数据迁移脚本**：

```typescript
// scripts/migrate-encryption.ts
import mongoose from 'mongoose'
import { User } from '@/models/User'
import { config } from '@/config/env'

async function migrate() {
  console.log('连接数据库...')
  await mongoose.connect(config.database.url)

  console.log('开始数据迁移...')
  const result = await User.migrateEncryption()

  console.log(`迁移完成:`)
  console.log(`  总用户数: ${result.total}`)
  console.log(`  已迁移: ${result.migrated}`)

  await mongoose.disconnect()
}

migrate().catch(console.error)
```

#### 方案B：低成本方案（数据库层加密）

**PostgreSQL pgcrypto**：

```sql
-- 启用 pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 创建加密表
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,  -- bcrypt
  phone BYTEA,  -- 加密存储
  id_card BYTEA,  -- 加密存储
  created_at TIMESTAMP DEFAULT NOW()
);

-- 加密插入
INSERT INTO users (email, password_hash, phone, id_card)
VALUES (
  'user@example.com',
  crypt('password', gen_salt('bf', 12)),  -- bcrypt 哈希
  pgp_sym_encrypt('13800138000', 'encryption_key'),  -- 加密
  pgp_sym_encrypt('110101199001011234', 'encryption_key')
);

-- 解密查询
SELECT 
  email,
  pgp_sym_decrypt(phone, 'encryption_key') AS phone,
  pgp_sym_decrypt(id_card, 'encryption_key') AS id_card
FROM users
WHERE email = 'user@example.com';

-- 密码验证
SELECT id FROM users
WHERE email = 'user@example.com'
  AND password_hash = crypt('input_password', password_hash);
```

**成本对比**：

| 指标 | 方案A (应用层) | 方案B (数据库层) |
|------|---------------|-----------------|
| 月成本 | $0 | $0 |
| 配置时间 | 4-8 小时 | 2-4 小时 |
| 性能影响 | 中等 | 较低 |
| 灵活性 | 高 | 中等 |
| 密钥管理 | 应用管理 | 数据库管理 |
| 可移植性 | 高 | 低（依赖数据库） |

### 决策树

```
你的数据敏感程度？
├── 仅密码
│   └── bcrypt 哈希足矣
│
├── 密码 + 少量敏感字段
│   └── 方案A（应用层加密）
│
└── 大量敏感数据
    ├── 使用 PostgreSQL → 方案B（pgcrypto）
    ├── 使用 MySQL → MySQL AES 函数
    └── 多数据库 → 方案A（统一加密）
```

### 代码示例

#### 完整的加密服务

```typescript
// services/encryption-service.ts
import crypto from 'crypto'
import bcrypt from 'bcryptjs'
import { KMSClient, EncryptCommand, DecryptCommand } from '@aws-sdk/client-kms'

interface EncryptionConfig {
  algorithm: string
  keySource: 'local' | 'kms'
  kmsKeyId?: string
}

class EncryptionService {
  private config: EncryptionConfig
  private localKey?: Buffer
  private kmsClient?: KMSClient

  constructor(config: EncryptionConfig) {
    this.config = config

    if (config.keySource === 'local') {
      this.localKey = Buffer.from(process.env.ENCRYPTION_KEY!, 'base64')
    } else if (config.keySource === 'kms') {
      this.kmsClient = new KMSClient({})
    }
  }

  /**
   * 加密数据
   */
  async encrypt(plaintext: string): Promise<string> {
    if (this.config.keySource === 'kms') {
      return this.encryptWithKMS(plaintext)
    }
    return this.encryptWithLocalKey(plaintext)
  }

  /**
   * 解密数据
   */
  async decrypt(encrypted: string): Promise<string> {
    if (this.config.keySource === 'kms') {
      return this.decryptWithKMS(encrypted)
    }
    return this.decryptWithLocalKey(encrypted)
  }

  /**
   * 本地密钥加密
   */
  private encryptWithLocalKey(plaintext: string): string {
    const iv = crypto.randomBytes(16)
    const cipher = crypto.createCipheriv(
      this.config.algorithm,
      this.localKey!,
      iv
    )

    let encrypted = cipher.update(plaintext, 'utf8', 'hex')
    encrypted += cipher.final('hex')

    const authTag = cipher.getAuthTag()
    return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`
  }

  /**
   * 本地密钥解密
   */
  private decryptWithLocalKey(encrypted: string): string {
    const [ivHex, authTagHex, data] = encrypted.split(':')
    const iv = Buffer.from(ivHex, 'hex')
    const authTag = Buffer.from(authTagHex, 'hex')

    const decipher = crypto.createDecipheriv(
      this.config.algorithm,
      this.localKey!,
      iv
    )
    decipher.setAuthTag(authTag)

    let decrypted = decipher.update(data, 'hex', 'utf8')
    decrypted += decipher.final('utf8')

    return decrypted
  }

  /**
   * AWS KMS 加密
   */
  private async encryptWithKMS(plaintext: string): Promise<string> {
    const command = new EncryptCommand({
      KeyId: this.config.kmsKeyId,
      Plaintext: Buffer.from(plaintext, 'utf8')
    })

    const response = await this.kmsClient!.send(command)
    return Buffer.from(response.CiphertextBlob!).toString('base64')
  }

  /**
   * AWS KMS 解密
   */
  private async decryptWithKMS(encrypted: string): Promise<string> {
    const command = new DecryptCommand({
      CiphertextBlob: Buffer.from(encrypted, 'base64')
    })

    const response = await this.kmsClient!.send(command)
    return Buffer.from(response.Plaintext!).toString('utf8')
  }

  /**
   * 密码哈希
   */
  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 12)
  }

  /**
   * 密码验证
   */
  async verifyPassword(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash)
  }

  /**
   * 生成密钥
   */
  static generateKey(): string {
    return crypto.randomBytes(32).toString('base64')
  }
}

// 使用示例
const encryptionService = new EncryptionService({
  algorithm: 'aes-256-gcm',
  keySource: process.env.AWS_REGION ? 'kms' : 'local',
  kmsKeyId: process.env.KMS_KEY_ID
})

export default encryptionService
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业数据加密案例集](../../enterprise/infosec/data-encryption-enterprise.md)
- [HashiCorp Vault 最佳实践](../../enterprise/infosec/vault-best-practices.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 密钥管理 | 环境变量 | HashiCorp Vault / AWS KMS |
| 密钥轮换 | 手动 | 自动轮换（30-90 天） |
| 加密范围 | 敏感字段 | 全链路（传输+存储+备份） |
| 审计 | 无 | 加密操作审计日志 |
| 合规 | 无 | PCI-DSS / HIPAA / GDPR |

---

## 附录：常见问题

**Q: 为什么不能用 MD5/SHA1 存储密码？**

A:
1. **弱哈希**：MD5/SHA1 设计用于快速计算，不抗暴力破解
2. **无盐**：相同密码生成相同哈希，易受彩虹表攻击
3. **破解速度**：MD5 可达 100 亿次/秒（GPU），bcrypt < 10000 次/秒
4. **推荐**：bcrypt（cost=12）或 argon2

**Q: AES-ECB 和 AES-GCM 有什么区别？**

A:
- **ECB 模式**：相同明文生成相同密文，不安全
- **CBC 模式**：需要手动管理 IV 和 Padding
- **GCM 模式**：提供加密 + 认证，推荐使用

**Q: 如何选择加密密钥长度？**

A:
- **AES-128**：128 位密钥，足够安全
- **AES-256**：256 位密钥，更高安全裕度
- **推荐**：AES-256-GCM（256 位密钥 = 32 字节）

**Q: 密钥应该存储在哪里？**

A:
- **开发环境**：环境变量（`.env` 文件，不提交 Git）
- **生产环境**：密钥管理服务（AWS KMS、Vault）
- **禁止**：硬编码、配置文件提交、数据库明文存储

**Q: 如何处理已存储的明文数据？**

A:
1. 创建迁移脚本
2. 批量加密明文数据
3. 验证加密正确性
4. 删除明文备份
5. 更新应用代码

---

## 参考资源

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [NIST Cryptographic Standards](https://csrc.nist.gov/publications/detail/sp/800-175b/final)
- [bcrypt Documentation](https://github.com/kelektiv/node.bcrypt.js)
- [AWS KMS Best Practices](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)
- [PostgreSQL pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html)
