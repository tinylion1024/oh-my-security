# PII 数据暴露风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $20-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的应用存储或传输用户身份证号、手机号、银行卡号等 PII（个人身份信息）时未加密，导致数据泄露后违反 GDPR/网络安全法，面临高额罚款和用户信任危机。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 收集用户真实姓名、身份证号、手机号
- [ ] 收集用户银行卡号、支付信息
- [ ] 收集用户地址、出生日期等敏感信息
- [ ] **数据库中存储明文身份证号、手机号**
- [ ] **API 返回完整 PII 数据，未脱敏**
- [ ] **使用 HTTP 传输 PII 数据（未加密）**
→ 勾选≥2项，尤其是后三项，**立即行动**

### 一句话防御
在数据库中对 PII 字段进行加密或脱敏存储，使用 HTTPS 传输数据，API 返回时只返回必要的脱敏信息，最小化 PII 数据收集范围。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **盘点 PII 数据**：
   ```sql
   -- 检查数据库中是否存储明文 PII
   SELECT COUNT(*) as total,
          COUNT(DISTINCT id_card) as id_cards,
          COUNT(DISTINCT phone) as phones,
          COUNT(DISTINCT bank_card) as bank_cards
   FROM users;

   -- 检查是否有明文身份证号
   SELECT id, id_card FROM users LIMIT 5;
   ```

2. [ ] **立即启用 HTTPS**：
   ```bash
   # 使用 Let's Encrypt 免费证书
   sudo apt-get install certbot
   sudo certbot --nginx -d yourdomain.com

   # 或使用 Cloudflare 免费 SSL
   # 在 Cloudflare 控制台启用 "Always Use HTTPS"
   ```

3. [ ] **API 返回脱敏数据**：
   ```javascript
   // ❌ 错误示例：返回完整身份证号
   // return { idCard: "110101199001011234" };

   // ✅ 正确示例：返回脱敏身份证号
   return { idCard: "110***********1234" };
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **实现数据脱敏函数**：对 PII 字段进行脱敏显示
2. [ ] **加密存储 PII**：使用 AES 加密敏感字段
3. [ ] **最小化数据收集**：只收集业务必需的 PII
4. [ ] **更新隐私政策**：明确告知用户数据收集和使用方式

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用数据库字段加密**：如 MySQL 透明数据加密（TDE）
2. [ ] **实施数据访问审计**：记录谁访问了 PII 数据
3. [ ] **定期安全评估**：每年进行一次安全审计

### 推荐工具
- **免费**：
  - [Let's Encrypt](https://letsencrypt.org/) - 免费 SSL 证书
  - [OpenSSL](https://www.openssl.org/) - 免费加密库
  - [CryptoJS](https://github.com/brix/crypto-js) - JavaScript 加密库

- **低成本**：
  - [AWS KMS](https://aws.amazon.com/kms/) - $1/密钥/月，密钥管理服务
  - [HashiCorp Vault](https://www.vaultproject.io/) - 开源，密钥管理和加密

### 验证方法
- [ ] **HTTPS 验证**：访问 `https://yourdomain.com`，浏览器显示安全锁
- [ ] **数据脱敏验证**：API 返回的用户数据中，身份证、手机号等已脱敏
- [ ] **加密验证**：数据库中的 PII 字段是加密后的乱码
- [ ] **合规检查**：隐私政策已更新，明确告知用户数据使用方式

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2021年，一个在线医疗问诊平台收集了 50 万用户的姓名、身份证号、手机号、病历信息。数据库中这些 PII 数据明文存储，API 接口返回完整信息。

攻击者通过 SQL 注入漏洞获取了数据库访问权限，导出了所有用户数据。由于数据未加密，攻击者可以直接读取所有 PII。该平台违反《网络安全法》和《个人信息保护法》，被罚款 100 万元，并永久停止服务。

**类似案例**：
- 2020年，某电商平台泄露 1 亿用户手机号和地址，被罚 50 万元
- 2022年，某教育 App 泄露 300 万学生身份证号，被罚 200 万元
- 2023年，某金融平台泄露用户银行卡号，面临集体诉讼

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── 通过漏洞扫描发现 SQL 注入点
   ├── 或通过社工获取内部访问权限
   └── 或通过数据库暴露获取访问

2. 导出 PII 数据
   ├── 使用 SQL 注入导出数据
   │   ' UNION SELECT id_card, phone, bank_card FROM users--
   ├── 或直接访问数据库
   │   mysqldump -h target -u root -p users > users.sql
   └── 获取明文 PII 数据

3. 分析数据价值
   ├── 身份证号：可用于注册账号、办理信用卡
   ├── 手机号：可用于诈骗、垃圾短信
   ├── 银行卡号：可用于盗刷
   └── 病历信息：可用于勒索

4. 利用或出售数据
   ├── 在暗网出售数据（$1-10/条）
   ├── 用于精准诈骗
   ├── 用于身份盗用
   └── 用于勒索（如病历信息）

5. 导致合规风险
   ├── 监管机构调查
   ├── 高额罚款（GDPR 最高 2000 万欧元或 4% 年营收）
   ├── 用户集体诉讼
   └── 品牌信誉丧失
```

**关键点**：
- PII 数据是 **黑客的高价值目标**
- 明文存储 PII 违反 **多项法律法规**
- 数据泄露后的 **合规风险远高于技术风险**
- **一旦泄露，无法挽回**（数据已被复制传播）

### 防御实施（低成本方案）

#### 方案A：免费方案（应用层加密 + 脱敏）

**工具/服务**：OpenSSL/CryptoJS + 数据脱敏函数

**配置步骤**：

**第一步：实现数据脱敏工具**
```javascript
// utils/pii-sanitizer.js
// PII 数据脱敏工具

class PIISanitizer {
  // 脱敏手机号：138****1234
  static maskPhone(phone) {
    if (!phone || phone.length !== 11) return phone;
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  }

  // 脱敏身份证号：110***********1234
  static maskIdCard(idCard) {
    if (!idCard || idCard.length !== 18) return idCard;
    return idCard.replace(/(\d{3})\d{11}(\d{4})/, '$1***********$2');
  }

  // 脱敏银行卡号：6222****1234
  static maskBankCard(cardNumber) {
    if (!cardNumber || cardNumber.length < 8) return cardNumber;
    const start = cardNumber.substring(0, 4);
    const end = cardNumber.substring(cardNumber.length - 4);
    const middle = '*'.repeat(cardNumber.length - 8);
    return `${start}${middle}${end}`;
  }

  // 脱敏邮箱：a***@example.com
  static maskEmail(email) {
    if (!email || !email.includes('@')) return email;
    const [local, domain] = email.split('@');
    const maskedLocal = local.substring(0, 1) + '***';
    return `${maskedLocal}@${domain}`;
  }

  // 脱敏姓名：张*
  static maskName(name) {
    if (!name) return name;
    return name.substring(0, 1) + '*'.repeat(name.length - 1);
  }

  // 脱敏地址：北京市****
  static maskAddress(address) {
    if (!address || address.length < 10) return address;
    return address.substring(0, 6) + '****';
  }

  // 脱敏对象中的所有 PII 字段
  static sanitize(obj, fields = ['phone', 'idCard', 'bankCard', 'email', 'name', 'address']) {
    if (!obj || typeof obj !== 'object') return obj;

    const sanitized = Array.isArray(obj) ? [] : {};

    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'object') {
        sanitized[key] = this.sanitize(value, fields);
      } else {
        switch (key.toLowerCase()) {
          case 'phone':
          case 'mobile':
            sanitized[key] = this.maskPhone(value);
            break;
          case 'idcard':
          case 'id_card':
          case 'identity':
            sanitized[key] = this.maskIdCard(value);
            break;
          case 'bankcard':
          case 'bank_card':
          case 'cardnumber':
            sanitized[key] = this.maskBankCard(value);
            break;
          case 'email':
            sanitized[key] = this.maskEmail(value);
            break;
          case 'name':
          case 'realname':
          case 'real_name':
            sanitized[key] = this.maskName(value);
            break;
          case 'address':
            sanitized[key] = this.maskAddress(value);
            break;
          default:
            sanitized[key] = value;
        }
      }
    }

    return sanitized;
  }
}

module.exports = PIISanitizer;

// 使用示例
const sanitizer = require('./utils/pii-sanitizer');

// 脱敏单个字段
console.log(sanitizer.maskPhone('13812345678'));  // 138****5678
console.log(sanitizer.maskIdCard('110101199001011234'));  // 110***********1234

// 脱敏整个对象
const user = {
  id: 1,
  name: '张三',
  phone: '13812345678',
  idCard: '110101199001011234',
  email: 'zhangsan@example.com'
};

const sanitizedUser = sanitizer.sanitize(user);
console.log(sanitizedUser);
// { id: 1, name: '张*', phone: '138****5678', idCard: '110***********1234', email: 'z***@example.com' }
```

**第二步：实现 PII 加密存储**
```javascript
// utils/pii-encryption.js
// PII 数据加密工具

const crypto = require('crypto');

class PIIEncryption {
  constructor(encryptionKey) {
    this.algorithm = 'aes-256-gcm';
    this.key = Buffer.from(encryptionKey, 'base64');
  }

  // 加密
  encrypt(text) {
    if (!text) return text;

    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(this.algorithm, this.key, iv);

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const authTag = cipher.getAuthTag();

    // 返回格式：iv:authTag:encrypted
    return `${iv.toString('hex')}:${authTag.toString('hex')}:${encrypted}`;
  }

  // 解密
  decrypt(encryptedData) {
    if (!encryptedData) return encryptedData;

    const [ivHex, authTagHex, encrypted] = encryptedData.split(':');

    const iv = Buffer.from(ivHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');

    const decipher = crypto.createDecipheriv(this.algorithm, this.key, iv);
    decipher.setAuthTag(authTag);

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  // 哈希（不可逆，用于需要验证的场景）
  hash(text) {
    if (!text) return text;

    return crypto.createHash('sha256').update(text).digest('hex');
  }

  // 验证哈希
  verifyHash(text, hash) {
    return this.hash(text) === hash;
  }
}

// 从环境变量读取加密密钥
const encryptionKey = process.env.PII_ENCRYPTION_KEY;
if (!encryptionKey) {
  throw new Error('缺少环境变量: PII_ENCRYPTION_KEY');
}

module.exports = new PIIEncryption(encryptionKey);

// 生成加密密钥（仅第一次运行）
// console.log(crypto.randomBytes(32).toString('base64'));
```

**第三步：在数据模型中使用加密**
```javascript
// models/user.js
const piiEncryption = require('../utils/pii-encryption');
const piiSanitizer = require('../utils/pii-sanitizer');

class User {
  constructor(data) {
    this.id = data.id;
    this.username = data.username;

    // 加密存储 PII
    this.phone = data.phone ? piiEncryption.encrypt(data.phone) : null;
    this.idCard = data.idCard ? piiEncryption.encrypt(data.idCard) : null;
    this.bankCard = data.bankCard ? piiEncryption.encrypt(data.bankCard) : null;
    this.email = data.email;
  }

  // 解密 PII 数据（仅在需要时调用）
  decryptPII() {
    return {
      phone: this.phone ? piiEncryption.decrypt(this.phone) : null,
      idCard: this.idCard ? piiEncryption.decrypt(this.idCard) : null,
      bankCard: this.bankCard ? piiEncryption.decrypt(this.bankCard) : null
    };
  }

  // 返回脱敏数据（用于 API 响应）
  toSanitizedJSON() {
    const decryptedPII = this.decryptPII();

    return {
      id: this.id,
      username: this.username,
      phone: piiSanitizer.maskPhone(decryptedPII.phone),
      idCard: piiSanitizer.maskIdCard(decryptedPII.idCard),
      bankCard: piiSanitizer.maskBankCard(decryptedPII.bankCard),
      email: piiSanitizer.maskEmail(this.email)
    };
  }
}

module.exports = User;

// 使用示例
const user = new User({
  id: 1,
  username: 'zhangsan',
  phone: '13812345678',
  idCard: '110101199001011234',
  bankCard: '6222021234567890123',
  email: 'zhangsan@example.com'
});

// 保存到数据库（PII 已加密）
// db.query('INSERT INTO users SET ?', user);

// API 返回脱敏数据
app.get('/user/:id', (req, res) => {
  const user = getUserFromDB(req.params.id);
  res.json(user.toSanitizedJSON());
});
```

**第四步：数据库表设计**
```sql
-- 用户表（PII 字段加密存储）
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,

  -- PII 字段（加密存储）
  phone VARCHAR(255),  -- 加密后的手机号
  id_card VARCHAR(255),  -- 加密后的身份证号
  bank_card VARCHAR(255),  -- 加密后的银行卡号
  email VARCHAR(100),

  -- 访问审计字段
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_accessed_at TIMESTAMP,  -- 最后访问 PII 的时间
  accessed_by INT,  -- 谁访问了 PII

  INDEX idx_username (username),
  INDEX idx_email (email)
);

-- PII 访问日志表
CREATE TABLE pii_access_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  field_name VARCHAR(50) NOT NULL,  -- phone, id_card, bank_card
  accessed_by INT NOT NULL,  -- 访问者 ID
  access_reason VARCHAR(255),  -- 访问原因
  ip_address VARCHAR(50),
  user_agent VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_user_id (user_id),
  INDEX idx_accessed_by (accessed_by),
  INDEX idx_created_at (created_at)
);
```

**局限性**：
- 需要在应用层处理加密解密
- 性能开销（每次查询需要解密）
- 密钥管理复杂（密钥丢失则数据无法恢复）

#### 方案B：低成本方案（数据库字段加密）

**工具/服务**：MySQL 透明数据加密（TDE）/ PostgreSQL pgcrypto

**配置步骤**：

**第一步：MySQL 加密函数**
```sql
-- 使用 MySQL 内置加密函数
INSERT INTO users (username, phone, id_card)
VALUES (
  'zhangsan',
  AES_ENCRYPT('13812345678', 'encryption_key'),
  AES_ENCRYPT('110101199001011234', 'encryption_key')
);

-- 查询时解密
SELECT
  id,
  username,
  CAST(AES_DECRYPT(phone, 'encryption_key') AS CHAR) as phone,
  CAST(AES_DECRYPT(id_card, 'encryption_key') AS CHAR) as id_card
FROM users
WHERE id = 1;
```

**第二步：PostgreSQL pgcrypto 扩展**
```sql
-- 启用 pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 插入加密数据
INSERT INTO users (username, phone, id_card)
VALUES (
  'zhangsan',
  pgp_sym_encrypt('13812345678', 'encryption_key'),
  pgp_sym_encrypt('110101199001011234', 'encryption_key')
);

-- 查询时解密
SELECT
  id,
  username,
  pgp_sym_decrypt(phone::bytea, 'encryption_key') as phone,
  pgp_sym_decrypt(id_card::bytea, 'encryption_key') as id_card
FROM users
WHERE id = 1;
```

**第三步：创建视图（自动脱敏）**
```sql
-- 创建脱敏视图
CREATE VIEW users_sanitized AS
SELECT
  id,
  username,
  CONCAT(
    SUBSTRING(CAST(AES_DECRYPT(phone, 'encryption_key') AS CHAR), 1, 3),
    '****',
    SUBSTRING(CAST(AES_DECRYPT(phone, 'encryption_key') AS CHAR), 8, 4)
  ) as phone,
  CONCAT(
    SUBSTRING(CAST(AES_DECRYPT(id_card, 'encryption_key') AS CHAR), 1, 3),
    '***********',
    SUBSTRING(CAST(AES_DECRYPT(id_card, 'encryption_key') AS CHAR), 15, 4)
  ) as id_card,
  email
FROM users;

-- 应用查询脱敏视图
SELECT * FROM users_sanitized WHERE id = 1;
```

**优势**：
- **数据库层加密**：应用代码无需修改
- **自动加密解密**：插入和查询时自动处理
- **透明访问**：可以使用视图实现自动脱敏

**成本对比**：

| 指标 | 方案A (应用层) | 方案B (数据库层) |
|------|--------------|----------------|
| 月成本 | $0 | $0（使用数据库内置功能） |
| 性能开销 | 中（应用层加密） | 低（数据库层优化） |
| 代码改动 | 大（需修改所有 CRUD） | 小（使用视图） |
| 密钥管理 | 应用管理 | 数据库管理 |
| 灵活性 | 高 | 中 |

### 决策树

```
你的产品如何处理 PII？
├── 少量 PII 字段（< 5 个）
│   └── 方案A（应用层加密 + 脱敏）
│
├── 大量 PII 字段（> 5 个）
│   └── 方案B（数据库层加密）
│
├── 需要细粒度访问控制
│   └── 方案A（应用层可以记录访问日志）
│
└── 合规要求（GDPR/等保）
    └── 方案A + 方案B 组合
```

### 代码示例

#### 完整的 PII 保护配置脚本

```bash
#!/bin/bash
# pii-protection-setup.sh
# 用途：配置 PII 数据保护措施
# 适用：独立开发者、小团队

set -e

echo "=== PII 数据保护配置脚本 ==="

# 步骤 1: 生成加密密钥
echo "步骤 1/5: 生成加密密钥..."
PII_KEY=$(openssl rand -base64 32)
echo "PII_ENCRYPTION_KEY=$PII_KEY" >> .env
echo "✓ 加密密钥已生成并保存到 .env"

# 步骤 2: 创建数据库表
echo "步骤 2/5: 创建数据库表..."
mysql -u root -p <<'EOF'
CREATE DATABASE IF NOT EXISTS myapp;
USE myapp;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) NOT NULL,
  phone VARCHAR(255),
  id_card VARCHAR(255),
  bank_card VARCHAR(255),
  email VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  last_accessed_at TIMESTAMP,
  accessed_by INT,
  INDEX idx_username (username),
  INDEX idx_email (email)
);

-- PII 访问日志表
CREATE TABLE IF NOT EXISTS pii_access_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  field_name VARCHAR(50) NOT NULL,
  accessed_by INT NOT NULL,
  access_reason VARCHAR(255),
  ip_address VARCHAR(50),
  user_agent VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_accessed_by (accessed_by),
  INDEX idx_created_at (created_at)
);
EOF

echo "✓ 数据库表已创建"

# 步骤 3: 创建脱敏视图
echo "步骤 3/5: 创建脱敏视图..."
mysql -u root -p myapp <<EOF
CREATE OR REPLACE VIEW users_sanitized AS
SELECT
  id,
  username,
  CONCAT(
    SUBSTRING(CAST(AES_DECRYPT(phone, '$PII_KEY') AS CHAR), 1, 3),
    '****',
    SUBSTRING(CAST(AES_DECRYPT(phone, '$PII_KEY') AS CHAR), 8, 4)
  ) as phone,
  CONCAT(
    SUBSTRING(CAST(AES_DECRYPT(id_card, '$PII_KEY') AS CHAR), 1, 3),
    '***********',
    SUBSTRING(CAST(AES_DECRYPT(id_card, '$PII_KEY') AS CHAR), 15, 4)
  ) as id_card,
  email
FROM users;
EOF

echo "✓ 脱敏视图已创建"

# 步骤 4: 创建工具函数
echo "步骤 4/5: 创建 PII 工具函数..."
cat > utils/pii-sanitizer.js <<'EOF'
// PII 脱敏工具
class PIISanitizer {
  static maskPhone(phone) {
    if (!phone || phone.length !== 11) return phone;
    return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');
  }

  static maskIdCard(idCard) {
    if (!idCard || idCard.length !== 18) return idCard;
    return idCard.replace(/(\d{3})\d{11}(\d{4})/, '$1***********$2');
  }

  static maskBankCard(cardNumber) {
    if (!cardNumber || cardNumber.length < 8) return cardNumber;
    const start = cardNumber.substring(0, 4);
    const end = cardNumber.substring(cardNumber.length - 4);
    const middle = '*'.repeat(cardNumber.length - 8);
    return \`\${start}\${middle}\${end}\`;
  }
}

module.exports = PIISanitizer;
EOF

echo "✓ PII 工具函数已创建"

# 步骤 5: 创建隐私政策模板
echo "步骤 5/5: 创建隐私政策模板..."
cat > privacy-policy-template.md <<'EOF'
# 隐私政策

## 我们收集哪些信息

我们收集以下个人信息：
- 姓名
- 手机号
- 身份证号
- 银行卡号
- 电子邮箱

## 我们如何使用您的信息

我们使用您的信息用于：
- 提供服务
- 身份验证
- 支付处理

## 我们如何保护您的信息

我们采取以下措施保护您的信息：
- 数据加密存储
- HTTPS 安全传输
- 访问权限控制
- 定期安全审计

## 您的权利

根据《个人信息保护法》，您有以下权利：
- 访问您的个人信息
- 更正您的个人信息
- 删除您的个人信息
- 撤回同意

## 联系我们

如有疑问，请联系：privacy@yourapp.com
EOF

echo "✓ 隐私政策模板已创建"

echo ""
echo "=== 配置完成 ==="
echo "加密密钥: .env"
echo "数据库表: users, pii_access_logs"
echo "脱敏视图: users_sanitized"
echo "工具函数: utils/pii-sanitizer.js"
echo "隐私政策: privacy-policy-template.md"
echo ""
echo "后续步骤："
echo "1. 更新应用代码，使用加密存储 PII"
echo "2. 更新 API，返回脱敏数据"
echo "3. 完善隐私政策，明确告知用户"
echo "4. 实施访问审计，记录 PII 访问"
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业 PII 保护最佳实践](../../enterprise/infosec/pii-protection-enterprise.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 合规要求 | 网络安全法/个保法 | GDPR/CCPA/HIPAA/等保三级 |
| 加密标准 | AES-256 | FIPS 140-2 认证加密 |
| 密钥管理 | 环境变量 | HSM/KMS 专业密钥管理 |
| 访问控制 | 基础权限 | RBAC + 属性基访问控制（ABAC） |
| 审计日志 | 手动记录 | SIEM 集中审计 |
| 数据主体权利 | 基础响应 | 自动化 DSR（数据主体请求） |

---

## 附录：常见问题

**Q: 我的数据库已经存储了大量明文 PII，如何迁移到加密存储？**

A: 分步迁移：
1. 添加新的加密字段（如 `phone_encrypted`）
2. 编写脚本批量加密现有数据
   ```sql
   UPDATE users SET phone_encrypted = AES_ENCRYPT(phone, 'key');
   ```
3. 更新应用代码，使用加密字段
4. 删除明文字段

**Q: 加密会影响查询性能吗？**

A: 会有影响，但可以优化：
- 只加密敏感字段，非敏感字段不加密
- 对加密字段建立索引（使用哈希索引）
- 使用数据库层加密（性能优化更好）

**Q: 如果用户要求导出数据，如何处理？**

A: 根据《个人信息保护法》，用户有权获取其个人数据：
1. 验证用户身份（确保是本人）
2. 解密所有 PII 数据
3. 导出为结构化格式（JSON/CSV）
4. 记录导出操作（审计日志）

**Q: 如何最小化 PII 数据收集？**

A: 遵循"最小必要"原则：
- 只收集业务必需的 PII
- 能用邮箱注册的，不要收集手机号
- 能用手机号验证的，不要收集身份证号
- 定期清理不再需要的 PII 数据

---

## 参考资源

- [《中华人民共和国个人信息保护法》](http://www.npc.gov.cn/npc/c30834/202108/a8c4e3677c74491a80b53a172bb753fe.shtml)
- [GDPR 官方网站](https://gdpr.eu/)
- [OWASP Data Protection Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/User_Privacy_Protection_Cheat_Sheet.html)
- [MySQL Encryption Functions](https://dev.mysql.com/doc/refman/8.0/en/encryption-functions.html)
- [PostgreSQL pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html)
