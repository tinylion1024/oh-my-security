# GitHub 密钥泄露风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $10-30/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你将 AWS API Key、数据库密码、JWT 密钥等敏感信息硬编码在代码中，提交到 GitHub 后，自动化扫描工具在几分钟内发现并利用这些密钥，导致你的云服务被滥用、数据库被入侵。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 代码中包含 `API_KEY = "sk-..."` 或 `PASSWORD = "..."` 等硬编码密钥
- [ ] 配置文件（如 `config.js`, `.env`）被提交到 Git 仓库
- [ ] 使用 GitHub 公开仓库或私有仓库
- [ ] **从未检查过 Git 提交历史是否包含敏感信息**
- [ ] **使用真实密钥进行测试，忘记删除就提交了代码**
- [ ] `.gitignore` 文件未包含 `.env`、`config.local.js` 等
→ 勾选≥2项，尤其是后两项，**立即行动**

### 一句话防御
使用环境变量存储敏感信息，配置 `.gitignore` 排除敏感文件，使用 git-secrets 工具防止提交密钥，定期轮换所有已泄露的密钥。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查 GitHub 仓库是否泄露密钥**：
   ```bash
   # 使用 gitleaks 扫描本地仓库
   brew install gitleaks  # macOS
   gitleaks --path=/path/to/your/repo --branch=all

   # 或使用 truffleHog 扫描 GitHub 仓库
   pip install trufflehog
   trufflehog https://github.com/your-username/your-repo
   ```

2. [ ] **立即轮换已泄露的密钥**：
   ```bash
   # AWS API Key
   # 1. 登录 AWS IAM 控制台
   # 2. 找到泄露的 Access Key
   # 3. 先禁用，然后删除
   # 4. 创建新的 Access Key
   # 5. 更新环境变量

   # 数据库密码
   mysql -u root -p
   ALTER USER 'app_user'@'%' IDENTIFIED BY '新的强密码';

   # JWT 密钥
   # 生成新的 JWT 密钥
   openssl rand -base64 32
   # 更新环境变量
   ```

3. [ ] **从 Git 历史中移除敏感信息**：
   ```bash
   # 使用 BFG Repo-Cleaner 删除敏感文件
   brew install bfg
   git clone --mirror https://github.com/your-username/your-repo.git
   bfg --delete-files .env your-repo.git
   cd your-repo.git
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   git push

   # 或使用 git filter-branch（较慢）
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **配置 `.gitignore`**：
   ```gitignore
   # 环境变量文件
   .env
   .env.local
   .env.*.local

   # 配置文件
   config.local.js
   config.production.js
   settings.py

   # 密钥文件
   *.pem
   *.key
   id_rsa*
   ```

2. [ ] **安装 git-secrets**：
   ```bash
   # macOS
   brew install git-secrets

   # 在项目中配置
   cd /path/to/your/repo
   git secrets --install
   git secrets --register-aws
   git secrets --add 'password\s*=\s*["\'].*["\']'
   ```

3. [ ] **迁移到环境变量**：
   ```javascript
   // ❌ 错误示例
   const API_KEY = "sk-1234567890abcdef";

   // ✅ 正确示例
   const API_KEY = process.env.API_KEY;
   ```

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用密钥管理服务**：如 AWS Secrets Manager、HashiCorp Vault
2. [ ] **启用 GitHub Secret Scanning**：GitHub 免费为公开仓库提供
3. [ ] **实施密钥轮换策略**：每 90 天轮换一次密钥

### 推荐工具
- **免费**：
  - [git-secrets](https://github.com/awslabs/git-secrets) - 防止提交密钥到 Git
  - [gitleaks](https://github.com/gitleaks/gitleaks) - 扫描 Git 历史中的密钥
  - [truffleHog](https://github.com/trufflesecurity/trufflehog) - 扫描 GitHub 仓库

- **低成本**：
  - [GitHub Advanced Security](https://github.com/features/security) - $4/用户/月，私有仓库密钥扫描
  - [GitGuardian](https://www.gitguardian.com/) - 免费 1 个仓库，私有仓库密钥监控

### 验证方法
- [ ] **扫描验证**：运行 `gitleaks` 应该无密钥泄露警告
- [ ] **Git 历史验证**：运行 `git log -p | grep -i "password\|api_key\|secret"` 应该无结果
- [ ] **功能测试**：应用使用环境变量后仍然可以正常运行
- [ ] **密钥状态验证**：旧的密钥已被禁用，新的密钥正常工作

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2021年，一位独立开发者在使用 GitHub Actions 进行自动部署时，不小心将 AWS Access Key 硬编码在 `.github/workflows/deploy.yml` 文件中，并提交到公开仓库。

6 分钟后，自动化扫描工具发现了这个 AWS Access Key，并在 2 小时内使用该密钥创建了价值 $5,000 的 EC2 实例进行加密货币挖矿。开发者在 4 小时后收到 AWS 账单告警才发现，但已经产生了 $5,000 的费用。

**类似案例**：
- 2020年，某创业公司员工将 Slack Webhook URL 提交到 GitHub，被用于发送垃圾消息
- 2021年，某开发者的 Stripe API Key 泄露，被用于创建测试交易
- 2022年，某 SaaS 产品的数据库密码泄露，导致 100 万用户数据泄露

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── 使用自动化工具扫描 GitHub 公开仓库
   ├── 工具：git-all-secrets, truffleHog, GitRob
   ├── 目标：包含 AWS, Google, Stripe, Slack 等关键词的文件
   └── 扫描速度：每分钟可扫描数千个仓库

2. 提取密钥
   ├── 使用正则表达式匹配密钥模式
   │   AWS Access Key: AKIA[0-9A-Z]{16}
   │   AWS Secret Key: [A-Za-z0-9/+=]{40}
   │   Google API Key: AIza[0-9A-Za-z_-]{35}
   │   Stripe API Key: sk_live_[0-9a-zA-Z]{24}
   └── 从 Git 历史中挖掘已删除的密钥

3. 验证密钥有效性
   ├── 尝试使用密钥调用 API
   │   aws sts get-caller-identity --access-key-id AKIA...
   ├── 验证权限范围
   │   aws iam get-user --access-key-id AKIA...
   └── 筛选有效且有价值的密钥

4. 利用密钥
   ├── 场景A：AWS 密钥
   │   ├── 创建 EC2 实例进行挖矿
   │   ├── 创建 S3 存储桶用于数据窃取
   │   └── 创建 IAM 用户进行长期访问
   ├── 场景B：Stripe 密钥
   │   ├── 查询交易记录
   │   ├── 创建退款
   │   └── 创建测试交易
   └── 场景C：数据库密码
       ├── 直接连接数据库
       ├── 导出数据
       └── 删除或加密数据（勒索）

5. 持续监控
   └── 监控仓库更新，获取新泄露的密钥
```

**关键点**：
- 攻击者使用 **自动化工具**，**几分钟内** 就能发现泄露的密钥
- Git 历史中的密钥 **即使删除也会保留**，直到强制清理
- 密钥泄露的 **发现时间 < 利用时间**，开发者往往来不及反应

### 防御实施（低成本方案）

#### 方案A：免费方案（环境变量 + git-secrets）

**工具/服务**：环境变量 + `.gitignore` + git-secrets

**配置步骤**：

**第一步：配置 `.gitignore`**
```gitignore
# 环境变量文件
.env
.env.local
.env.production
.env.*.local

# 配置文件（包含敏感信息）
config/local.js
config/production.js
settings/local.py
*.local.json

# 密钥和证书文件
*.pem
*.key
*.crt
id_rsa*
*.p12
*.pfx

# 云服务配置
.aws/credentials
.gcp/keyfile.json
.azure/credentials

# IDE 和编辑器
.vscode/settings.json
.idea/workspace.xml
```

**第二步：迁移到环境变量**
```javascript
// config/database.js
// ❌ 错误示例：硬编码密钥
// const DB_PASSWORD = "MyPassword123";

// ✅ 正确示例：使用环境变量
const DB_PASSWORD = process.env.DB_PASSWORD;

if (!DB_PASSWORD) {
  throw new Error('缺少环境变量: DB_PASSWORD');
}

module.exports = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 3306,
  user: process.env.DB_USER || 'root',
  password: DB_PASSWORD,
  database: process.env.DB_NAME || 'myapp'
};
```

**第三步：创建 `.env` 文件模板**
```bash
# .env.example（提交到 Git）
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=myapp

# AWS 配置
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# JWT 配置
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRES_IN=7d

# 第三方 API
STRIPE_API_KEY=your_stripe_key_here
SENDGRID_API_KEY=your_sendgrid_key_here
```

```bash
# .env（不提交到 Git，包含真实密钥）
DB_HOST=prod-db.example.com
DB_PASSWORD=MyRealPassword123!
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
JWT_SECRET=$(openssl rand -base64 32)
```

**第四步：安装和配置 git-secrets**
```bash
# 安装 git-secrets
# macOS
brew install git-secrets

# Ubuntu/Debian
sudo apt-get install git-secrets

# 或从源码安装
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets
sudo make install

# 在项目中配置
cd /path/to/your/repo
git secrets --install

# 添加 AWS 密钥检测规则（内置）
git secrets --register-aws

# 添加自定义规则
# 检测密码字段
git secrets --add 'password\s*=\s*["\'].*["\']'

# 检测 API Key 字段
git secrets --add 'api[_-]?key\s*=\s*["\'].*["\']'

# 检测密钥字段
git secrets --add 'secret[_-]?key\s*=\s*["\'].*["\']'

# 添加白名单（允许的字段）
git secrets --add --allowed 'password\s*=\s*process\.env\.PASSWORD'

# 测试配置
echo 'password = "test123"' | git secrets --scan
# 应该输出：[ERROR] Matched prohibited pattern
```

**第五步：配置 pre-commit hook**
```bash
# git-secrets 会自动配置 pre-commit hook
# 手动测试
git commit -m "test commit"
# 如果包含密钥，会阻止提交

# 也可以配置 commit-msg hook
git secrets --install --commit-msg-hook
```

**局限性**：
- 需要在每个开发者的机器上安装 git-secrets
- 可能误报（需要配置白名单）
- 只能防止未来的泄露，无法修复历史泄露

#### 方案B：低成本方案（密钥管理服务）

**工具/服务**：AWS Secrets Manager / HashiCorp Vault / Doppler

**配置步骤**：

**第一步：使用 AWS Secrets Manager（示例）**
```bash
# 创建密钥
aws secretsmanager create-secret \
  --name myapp/database/password \
  --secret-string "MyRealPassword123!"

aws secretsmanager create-secret \
  --name myapp/aws/access-key \
  --secret-string '{"access_key_id":"AKIA...","secret_access_key":"wJal..."}'

# 在应用中读取密钥
```

```javascript
// Node.js 示例
const AWS = require('aws-sdk');
const secretsManager = new AWS.SecretsManager();

async function getSecret(secretName) {
  const data = await secretsManager.getSecretValue({ SecretId: secretName }).promise();
  return JSON.parse(data.SecretString);
}

// 使用密钥
const dbConfig = await getSecret('myapp/database/password');
const awsConfig = await getSecret('myapp/aws/access-key');
```

**第二步：使用 Doppler（推荐给独立开发者）**
```bash
# 安装 Doppler CLI
brew install dopplerhq/cli/doppler

# 登录
doppler login

# 创建项目
doppler projects create my-app

# 设置密钥
doppler secrets set DB_PASSWORD MyRealPassword123!
doppler secrets set AWS_ACCESS_KEY_ID AKIA...
doppler secrets set AWS_SECRET_ACCESS_KEY wJal...

# 在本地开发中使用
doppler run -- npm start

# 在 CI/CD 中使用
doppler run --secrets-file .env -- ./deploy.sh
```

**优势**：
- **集中管理**：所有密钥在一个地方管理
- **自动轮换**：支持自动轮换密钥
- **访问控制**：细粒度的访问权限控制
- **审计日志**：记录所有密钥访问
- **易于使用**：开发者无需手动管理 `.env` 文件

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (Secrets Manager) |
|------|------------|------------------------|
| 月成本 | $0 | $0.40/密钥/月 + $0.05/万次调用 |
| 密钥轮换 | 手动 | 自动 |
| 访问控制 | 无 | RBAC |
| 审计日志 | 无 | 有 |
| 维护成本 | 高 | 低 |

### 决策树

```
你的产品处于什么阶段？
├── MVP/原型阶段
│   ├── 1 人开发 → 方案A（环境变量 + git-secrets）
│   └── 2+ 人开发 → 方案B（Doppler 免费层）
│
├── 已有付费用户
│   ├── 密钥数量 < 10 → 方案A
│   └── 密钥数量 > 10 → 方案B
│
└── 合规要求
    ├── 无特殊要求 → 方案A 或 方案B
    └── SOC2/GDPR → 方案B（AWS Secrets Manager）
```

### 代码示例

#### 完整的密钥管理配置脚本

```bash
#!/bin/bash
# secrets-management-setup.sh
# 用途：配置密钥管理最佳实践
# 适用：独立开发者、小团队

set -e

echo "=== 密钥管理配置脚本 ==="

# 步骤 1: 安装 git-secrets
echo "步骤 1/5: 安装 git-secrets..."
if command -v git-secrets &> /dev/null; then
  echo "✓ git-secrets 已安装"
else
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install git-secrets
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    git clone https://github.com/awslabs/git-secrets.git /tmp/git-secrets
    cd /tmp/git-secrets
    sudo make install
    cd -
    rm -rf /tmp/git-secrets
  fi
  echo "✓ git-secrets 已安装"
fi

# 步骤 2: 配置 .gitignore
echo "步骤 2/5: 配置 .gitignore..."
GITIGNORE_FILE=".gitignore"

if [ ! -f "$GITIGNORE_FILE" ]; then
  touch "$GITIGNORE_FILE"
fi

# 添加敏感文件模式（如果不存在）
patterns=(
  ".env"
  ".env.local"
  ".env.*.local"
  "*.pem"
  "*.key"
  "id_rsa*"
  "config/local.*"
  "config/production.*"
  "*.local.json"
)

for pattern in "${patterns[@]}"; do
  if ! grep -q "^$pattern$" "$GITIGNORE_FILE"; then
    echo "$pattern" >> "$GITIGNORE_FILE"
  fi
done

echo "✓ .gitignore 已配置"

# 步骤 3: 创建 .env.example
echo "步骤 3/5: 创建 .env.example..."
cat > .env.example <<'EOF'
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=myapp

# AWS 配置
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# JWT 配置
JWT_SECRET=your_jwt_secret_here
JWT_EXPIRES_IN=7d

# 第三方 API
STRIPE_API_KEY=your_stripe_key_here
SENDGRID_API_KEY=your_sendgrid_key_here
EOF

echo "✓ .env.example 已创建"

# 步骤 4: 配置 git-secrets
echo "步骤 4/5: 配置 git-secrets..."
git secrets --install

# 注册 AWS 密钥检测规则
git secrets --register-aws

# 添加自定义规则
git secrets --add 'password\s*=\s*["\'][^"\']{8,}["\']'
git secrets --add 'api[_-]?key\s*=\s*["\'][^"\']{16,}["\']'
git secrets --add 'secret[_-]?key\s*=\s*["\'][^"\']{16,}["\']'
git secrets --add 'token\s*=\s*["\'][^"\']{16,}["\']'

# 添加白名单
git secrets --add --allowed 'password\s*=\s*process\.env\.'
git secrets --add --allowed 'api[_-]?key\s*=\s*process\.env\.'
git secrets --add --allowed 'secret[_-]?key\s*=\s*process\.env\.'

echo "✓ git-secrets 已配置"

# 步骤 5: 扫描现有代码
echo "步骤 5/5: 扫描现有代码..."
if git secrets --scan-history 2>&1 | grep -q "ERROR"; then
  echo "⚠️  发现潜在密钥泄露！"
  echo "请执行以下步骤："
  echo "1. 检查泄露的密钥"
  echo "2. 立即轮换泄露的密钥"
  echo "3. 从 Git 历史中删除敏感信息"
  echo "   使用 BFG Repo-Cleaner: bfg --delete-files .env"
else
  echo "✓ 未发现密钥泄露"
fi

echo ""
echo "=== 配置完成 ==="
echo "后续步骤："
echo "1. 复制 .env.example 为 .env，填入真实密钥"
echo "   cp .env.example .env"
echo "2. 更新应用代码，使用环境变量"
echo "   const API_KEY = process.env.API_KEY;"
echo "3. 定期轮换密钥（建议每 90 天）"
echo "4. 定期运行 git secrets --scan-history"
```

#### 应用代码示例（Node.js）

```javascript
// config/secrets.js
// 安全的密钥管理器

require('dotenv').config();

class SecretsManager {
  constructor() {
    this.requiredSecrets = [
      'DB_HOST',
      'DB_USER',
      'DB_PASSWORD',
      'DB_NAME',
      'JWT_SECRET',
      'AWS_ACCESS_KEY_ID',
      'AWS_SECRET_ACCESS_KEY'
    ];

    this.validateSecrets();
  }

  validateSecrets() {
    const missing = this.requiredSecrets.filter(key => !process.env[key]);

    if (missing.length > 0) {
      throw new Error(`缺少必需的环境变量: ${missing.join(', ')}`);
    }

    // 验证密钥强度
    this.validateStrength('DB_PASSWORD', 12);
    this.validateStrength('JWT_SECRET', 32);
    this.validateStrength('AWS_SECRET_ACCESS_KEY', 40);
  }

  validateStrength(key, minLength) {
    const value = process.env[key];
    if (value && value.length < minLength) {
      console.warn(`⚠️  ${key} 强度不足（最小 ${minLength} 字符）`);
    }
  }

  get(key) {
    const value = process.env[key];
    if (!value) {
      throw new Error(`环境变量 ${key} 未设置`);
    }
    return value;
  }

  getOptional(key, defaultValue) {
    return process.env[key] || defaultValue;
  }

  // 获取数据库配置
  getDatabaseConfig() {
    return {
      host: this.get('DB_HOST'),
      port: parseInt(this.getOptional('DB_PORT', '3306')),
      user: this.get('DB_USER'),
      password: this.get('DB_PASSWORD'),
      database: this.get('DB_NAME')
    };
  }

  // 获取 AWS 配置
  getAWSConfig() {
    return {
      accessKeyId: this.get('AWS_ACCESS_KEY_ID'),
      secretAccessKey: this.get('AWS_SECRET_ACCESS_KEY'),
      region: this.getOptional('AWS_REGION', 'us-east-1')
    };
  }

  // 获取 JWT 配置
  getJWTConfig() {
    return {
      secret: this.get('JWT_SECRET'),
      expiresIn: this.getOptional('JWT_EXPIRES_IN', '7d')
    };
  }

  // 轮换密钥（需要手动调用）
  async rotateSecret(key, newValue) {
    console.log(`开始轮换密钥: ${key}`);

    // 1. 更新环境变量
    process.env[key] = newValue;

    // 2. 更新 .env 文件
    const fs = require('fs').promises;
    const path = require('path');
    const envPath = path.join(process.cwd(), '.env');

    let envContent = await fs.readFile(envPath, 'utf8');
    const regex = new RegExp(`^${key}=.*$`, 'm');
    envContent = envContent.replace(regex, `${key}=${newValue}`);

    await fs.writeFile(envPath, envContent);

    console.log(`✓ 密钥已轮换: ${key}`);
  }
}

module.exports = new SecretsManager();

// 使用示例
const secrets = require('./config/secrets');

// 获取数据库配置
const dbConfig = secrets.getDatabaseConfig();

// 获取 JWT 配置
const jwtConfig = secrets.getJWTConfig();

// 轮换密钥
// await secrets.rotateSecret('JWT_SECRET', newJwtSecret);
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业密钥管理最佳实践](../../enterprise/infosec/secrets-management-enterprise.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 合规要求 | 基础保护 | SOC2/ISO27001/PCI-DSS |
| 密钥存储 | 环境变量 | HSM（硬件安全模块） |
| 密钥轮换 | 手动 | 自动轮换（30-90天） |
| 访问控制 | 无 | RBAC + 审批流程 |
| 审计日志 | 无 | 完整审计追踪 |
| 泄露检测 | 手动扫描 | 实时监控 + 自动响应 |

---

## 附录：常见问题

**Q: 我已经将密钥提交到 GitHub，删除文件后还有风险吗？**

A: **有风险**。Git 历史会保留所有提交记录，攻击者可以从历史记录中提取密钥。必须：
1. 立即轮换密钥（比清理历史更重要）
2. 使用 BFG Repo-Cleaner 或 git filter-branch 清理历史
3. 强制推送到远程仓库（`git push --force`）

**Q: GitHub 私有仓库是否安全？**

A: 私有仓库比公开仓库安全，但仍有风险：
1. 协作者可能泄露仓库内容
2. GitHub 员工理论上可以访问
3. 应该假设"私有仓库也可能泄露"，避免提交密钥

**Q: 使用 git-secrets 后误报怎么办？**

A: 配置白名单：
```bash
# 允许特定模式
git secrets --add --allowed 'password\s*=\s*process\.env\.PASSWORD'
git secrets --add --allowed 'password\s*=\s*YOUR_PASSWORD_HERE'
```

**Q: 如何检测代码中是否已经泄露密钥？**

A: 使用 gitleaks 扫描：
```bash
# 扫描本地仓库
gitleaks --path=/path/to/repo --branch=all

# 扫描远程仓库
gitleaks --repo-url=https://github.com/user/repo
```

---

## 参考资源

- [git-secrets](https://github.com/awslabs/git-secrets)
- [gitleaks](https://github.com/gitleaks/gitleaks)
- [truffleHog](https://github.com/trufflesecurity/trufflehog)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Doppler](https://www.doppler.com/)
