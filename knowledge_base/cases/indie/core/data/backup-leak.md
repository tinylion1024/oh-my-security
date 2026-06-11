# 备份泄露风险

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
你的数据库备份文件放在公开目录或未加密存储，攻击者可以直接下载备份文件获取全部用户数据，这比直接攻击数据库更简单更隐蔽。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用数据库备份功能（mysqldump/pg_dump/mongodump）
- [ ] 备份文件存储在服务器本地目录（如 /var/backups/）
- [ ] 备份文件存储在云存储（如 AWS S3/阿里云 OSS）但未加密
- [ ] 备份文件命名包含日期或固定名称（如 backup-2026-06-11.sql）
- [ ] **备份文件存储在 Web 根目录或子目录下**
- [ ] **从未给备份文件设置访问权限或加密**
→ 勾选≥2项，尤其是后两项，**立即行动**

### 一句话防御
备份文件存储到非公开目录，使用加密备份，并设置严格的文件访问权限（chmod 600），在云存储上启用加密和访问控制。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查现有备份位置**：
   ```bash
   # 检查是否有备份文件在 Web 目录
   find /var/www -name "*.sql" -o -name "*.dump" -o -name "*.backup"

   # 检查公开可访问的备份文件
   curl -I https://你的域名/backup.sql
   curl -I https://你的域名/backups/backup-2026-06-11.sql
   ```

2. [ ] **立即移动备份文件**：
   ```bash
   # 移动到非公开目录
   sudo mv /var/www/backups /var/backups/db-backups

   # 设置权限（只有 root 可访问）
   sudo chmod 700 /var/backups/db-backups
   sudo chmod 600 /var/backups/db-backups/*.sql
   ```

3. [ ] **创建加密备份脚本**：
   ```bash
   # 使用 OpenSSL 加密备份
   mysqldump -u root -p mydb | openssl enc -aes-256-cbc -salt -out /var/backups/db-backups/mydb-$(date +%Y%m%d).sql.enc
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **配置自动加密备份**：创建定时任务自动加密备份
2. [ ] **设置备份文件自动清理**：保留最近 7 天备份，自动删除旧备份
3. [ ] **云存储加密**：如果使用 AWS S3，启用服务器端加密（SSE-S3）
4. [ ] **访问日志审计**：检查是否已有备份文件被下载

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用托管备份服务**：如 AWS RDS 自动备份，默认加密
2. [ ] **异地备份**：将备份存储到不同区域或云服务商
3. [ ] **备份恢复测试**：每月测试备份文件是否可以正常恢复

### 推荐工具
- **免费**：
  - [OpenSSL](https://www.openssl.org/) - 免费加密工具，系统自带
  - [GPG](https://gnupg.org/) - 开源加密工具，支持非对称加密
  - [Restic](https://restic.net/) - 开源备份工具，支持加密和去重

- **低成本**：
  - [AWS S3](https://aws.amazon.com/s3/) - $0.023/GB/月，支持自动加密
  - [Backblaze B2](https://www.backblaze.com/b2/cloud-storage.html) - $0.005/GB/月，比 S3 便宜 4 倍

### 验证方法
- [ ] **文件权限验证**：执行 `ls -la /var/backups/db-backups/`，文件权限应为 `-rw-------`
- [ ] **加密验证**：尝试打开备份文件，应该是乱码或提示需要密码
- [ ] **Web 访问验证**：访问 `https://你的域名/backups/` 应该返回 404 或 403
- [ ] **恢复测试**：使用加密备份文件成功恢复数据库
  ```bash
  # 解密并恢复
  openssl enc -aes-256-cbc -d -in backup.sql.enc | mysql -u root -p mydb
  ```

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2020年，一个 SaaS 创业团队每天使用脚本自动备份 PostgreSQL 数据库，备份文件保存在 `/var/www/html/backups/` 目录（Web 根目录下），文件名为 `db-backup-YYYYMMDD.sql`。

攻击者通过目录扫描工具发现该目录可访问，直接下载了过去 30 天的所有备份文件，获取了 50 万用户的邮箱、密码哈希、手机号。由于备份文件未加密，攻击者无需任何破解直接读取了所有数据。

**类似案例**：
- 2019年，某电商网站的 MySQL 备份文件在 `/backup/` 目录可下载，泄露 100 万用户数据
- 2021年，某 SaaS 产品的 AWS S3 备份桶公开访问，导致 5TB 数据泄露
- 2022年，某医疗 App 的备份文件命名规律，攻击者遍历下载了所有历史备份

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── 使用目录扫描工具（DirBuster/gobuster）
   ├── 扫描常见备份目录：/backup/, /backups/, /db/, /sql/
   └── 尝试常见备份文件名：backup.sql, db.sql, dump.sql

2. 探测备份文件
   ├── 发现 https://example.com/backups/ 目录存在
   ├── 列出目录内容（Index of /backups/）
   └── 发现多个备份文件：backup-2026-06-01.sql, backup-2026-06-02.sql, ...

3. 下载备份文件
   ├── wget https://example.com/backups/backup-2026-06-11.sql
   ├── 文件大小：500MB（包含大量用户数据）
   └── 整个过程 < 10 分钟

4. 提取敏感数据
   ├── grep "INSERT INTO users" backup.sql
   ├── 提取邮箱、密码、手机号
   └── 导出为 CSV 文件，流入暗网

5. 清除痕迹
   └── 攻击者无需访问数据库，备份文件删除后无痕迹
```

**关键点**：
- 攻击者 **无需任何数据库权限**，仅通过 Web 访问备份文件
- 备份文件包含 **完整的历史数据**，比实时数据库数据更丰富
- 攻击 **难以检测**：Web 服务器访问日志可能被忽视

### 防御实施（低成本方案）

#### 方案A：免费方案（DIY 配置）

**工具/服务**：本地加密 + 云存储

**配置步骤**：

**第一步：创建安全的备份目录**
```bash
# 创建非公开目录
sudo mkdir -p /var/backups/db-backups
sudo chown root:root /var/backups/db-backups
sudo chmod 700 /var/backups/db-backups
```

**第二步：创建加密备份脚本**
```bash
#!/bin/bash
# backup-mysql-encrypted.sh
# 用途：加密备份 MySQL 数据库

set -e

# 配置参数
DB_NAME="${DB_NAME:-mydb}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"
BACKUP_DIR="/var/backups/db-backups"
ENCRYPTION_KEY="${ENCRYPTION_KEY:-$(openssl rand -base64 32)}"
RETENTION_DAYS=7

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份文件名（带时间戳）
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}-$(date +%Y%m%d-%H%M%S).sql.enc"

# 执行备份并加密
echo "开始备份数据库: $DB_NAME"
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" | \
  openssl enc -aes-256-cbc -salt -pass pass:"$ENCRYPTION_KEY" -out "$BACKUP_FILE"

# 设置权限
chmod 600 "$BACKUP_FILE"

echo "✓ 备份完成: $BACKUP_FILE"

# 删除旧备份（保留最近 N 天）
find "$BACKUP_DIR" -name "*.sql.enc" -type f -mtime +$RETENTION_DAYS -delete
echo "✓ 已清理 $RETENTION_DAYS 天前的旧备份"

# 保存加密密钥（仅第一次运行时）
KEY_FILE="$BACKUP_DIR/.encryption-key"
if [ ! -f "$KEY_FILE" ]; then
  echo "$ENCRYPTION_KEY" > "$KEY_FILE"
  chmod 600 "$KEY_FILE"
  echo "⚠️  加密密钥已保存到: $KEY_FILE"
  echo "   请妥善保管此密钥，丢失将无法恢复备份！"
fi
```

**第三步：配置定时任务**
```bash
# 编辑 crontab
crontab -e

# 每天凌晨 2 点执行备份
0 2 * * * /usr/local/bin/backup-mysql-encrypted.sh >> /var/log/db-backup.log 2>&1
```

**第四步：测试恢复**
```bash
# 解密备份文件
openssl enc -aes-256-cbc -d -pass pass:"$(cat /var/backups/db-backups/.encryption-key)" \
  -in /var/backups/db-backups/mydb-20260611-020000.sql.enc | mysql -u root -p mydb_restored
```

**局限性**：
- 需要手动管理加密密钥
- 本地备份文件可能丢失（服务器故障）
- 无异地备份

#### 方案B：低成本方案（<$50/月）

**工具/服务**：Restic + AWS S3（或 Backblaze B2）

**配置步骤**：

**第一步：安装 Restic**
```bash
# macOS
brew install restic

# Ubuntu/Debian
sudo apt-get install restic

# 或下载二进制文件
wget https://github.com/restic/restic/releases/download/v0.15.1/restic_0.15.1_linux_amd64.bz2
bunzip2 restic_0.15.1_linux_amd64.bz2
sudo mv restic_0.15.1_linux_amd64 /usr/local/bin/restic
sudo chmod +x /usr/local/bin/restic
```

**第二步：创建 S3 存储桶**
```bash
# 使用 AWS CLI 创建存储桶
aws s3 mb s3://my-app-backups-unique-name

# 启用版本控制（防止意外删除）
aws s3api put-bucket-versioning \
  --bucket my-app-backups-unique-name \
  --versioning-configuration Status=Enabled

# 启用默认加密
aws s3api put-bucket-encryption \
  --bucket my-app-backups-unique-name \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
```

**第三步：创建备份脚本**
```bash
#!/bin/bash
# backup-with-restic.sh
# 用途：使用 Restic 备份到 S3，自动加密

set -e

# 配置参数
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"
export RESTIC_REPOSITORY="s3:s3.amazonaws.com/my-app-backups-unique-name"
export RESTIC_PASSWORD="${RESTIC_PASSWORD}"  # 加密密码

DB_NAME="${DB_NAME:-mydb}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"

# 初始化仓库（仅第一次运行）
restic snapshots &>/dev/null || restic init

# 创建临时备份文件
TEMP_BACKUP="/tmp/db-backup-$(date +%Y%m%d-%H%M%S).sql"
mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" > "$TEMP_BACKUP"

# 上传到 S3（自动加密）
restic backup "$TEMP_BACKUP" --tag "db-backup" --tag "$DB_NAME"

# 删除临时文件
rm -f "$TEMP_BACKUP"

# 清理旧备份（保留最近 30 天）
restic forget --keep-daily 30 --prune

echo "✓ 备份完成"
```

**第四步：测试恢复**
```bash
# 列出所有备份
restic snapshots

# 恢复最新备份
restic restore latest --target /tmp/restore

# 恢复数据库
mysql -u root -p mydb < /tmp/restore/tmp/db-backup-*.sql
```

**优势**：
- **自动加密**：Restic 默认加密所有数据
- **去重压缩**：节省存储空间和带宽
- **版本控制**：可恢复任意历史版本
- **异地备份**：数据存储在 AWS S3
- **成本低**：$5-10/月（10GB 数据）

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (Restic+S3) |
|------|------------|-------------------|
| 月成本 | $0 | $5-10/月 |
| 存储空间 | 受限于服务器 | 无限 |
| 加密 | 手动 | 自动 |
| 异地备份 | 无 | 有 |
| 版本控制 | 手动 | 自动 |
| 恢复难度 | 中等 | 简单 |

### 决策树

```
你的产品处于什么阶段？
├── MVP/原型阶段
│   ├── 数据量 < 1GB → 方案A（DIY）
│   └── 数据量 > 1GB → 方案B（Restic+S3）
│
├── 已有付费用户
│   ├── 数据量 < 10GB → 方案B（Restic+S3, $5-10/月）
│   └── 数据量 > 10GB → 方案B（Restic+S3, $10-50/月）
│
└── 团队规模
    ├── 1 人 → 方案A 或 方案B
    └── 2+ 人 → 方案B（方便团队协作和恢复）
```

### 代码示例

#### 完整的备份安全配置脚本

```bash
#!/bin/bash
# secure-backup-setup.sh
# 用途：一键配置安全的数据库备份方案
# 适用：独立开发者、小团队

set -e

echo "=== 数据库备份安全配置脚本 ==="

# 配置参数
DB_TYPE="${DB_TYPE:-mysql}"  # mysql 或 postgresql
DB_NAME="${DB_NAME:-mydb}"
DB_USER="${DB_USER:-root}"
DB_PASS="${DB_PASS:-}"
BACKUP_DIR="/var/backups/db-backups"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
USE_S3="${USE_S3:-false}"
S3_BUCKET="${S3_BUCKET:-}"

# 检查备份目录
echo "步骤 1/5: 创建备份目录..."
if [ -d "/var/www/html/backups" ]; then
  echo "⚠️  检测到备份文件在 Web 根目录！"
  read -p "是否立即移动到安全目录？(y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo mv /var/www/html/backups "$BACKUP_DIR"
    echo "✓ 备份文件已移动到: $BACKUP_DIR"
  fi
fi

mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
echo "✓ 备份目录已创建: $BACKUP_DIR"

# 生成加密密钥
echo "步骤 2/5: 生成加密密钥..."
ENCRYPTION_KEY=$(openssl rand -base64 32)
KEY_FILE="$BACKUP_DIR/.encryption-key"
echo "$ENCRYPTION_KEY" > "$KEY_FILE"
chmod 600 "$KEY_FILE"
echo "✓ 加密密钥已生成: $KEY_FILE"
echo "  ⚠️  请妥善保管此密钥！"

# 创建备份脚本
echo "步骤 3/5: 创建备份脚本..."
BACKUP_SCRIPT="/usr/local/bin/backup-db-secure.sh"
cat > "$BACKUP_SCRIPT" <<'EOF'
#!/bin/bash
set -e

DB_TYPE="${DB_TYPE}"
DB_NAME="${DB_NAME}"
DB_USER="${DB_USER}"
DB_PASS="${DB_PASS}"
BACKUP_DIR="${BACKUP_DIR}"
ENCRYPTION_KEY=$(cat "${BACKUP_DIR}/.encryption-key")
RETENTION_DAYS="${RETENTION_DAYS}"

# 备份文件名
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}-${TIMESTAMP}.sql.enc"

# 执行备份
case "$DB_TYPE" in
  mysql)
    mysqldump -u "$DB_USER" -p"$DB_PASS" "$DB_NAME" | \
      openssl enc -aes-256-cbc -salt -pass pass:"$ENCRYPTION_KEY" -out "$BACKUP_FILE"
    ;;
  postgresql)
    PGPASSWORD="$DB_PASS" pg_dump -U "$DB_USER" "$DB_NAME" | \
      openssl enc -aes-256-cbc -salt -pass pass:"$ENCRYPTION_KEY" -out "$BACKUP_FILE"
    ;;
esac

chmod 600 "$BACKUP_FILE"
echo "✓ 备份完成: $BACKUP_FILE"

# 清理旧备份
find "$BACKUP_DIR" -name "*.sql.enc" -type f -mtime +$RETENTION_DAYS -delete

# S3 上传（如果启用）
if [ "$USE_S3" = "true" ]; then
  aws s3 cp "$BACKUP_FILE" "s3://$S3_BUCKET/"
  echo "✓ 已上传到 S3: s3://$S3_BUCKET/"
fi
EOF

chmod +x "$BACKUP_SCRIPT"
# 替换变量
sed -i "s|\${DB_TYPE}|$DB_TYPE|g" "$BACKUP_SCRIPT"
sed -i "s|\${DB_NAME}|$DB_NAME|g" "$BACKUP_SCRIPT"
sed -i "s|\${DB_USER}|$DB_USER|g" "$BACKUP_SCRIPT"
sed -i "s|\${DB_PASS}|$DB_PASS|g" "$BACKUP_SCRIPT"
sed -i "s|\${BACKUP_DIR}|$BACKUP_DIR|g" "$BACKUP_SCRIPT"
sed -i "s|\${RETENTION_DAYS}|$RETENTION_DAYS|g" "$BACKUP_SCRIPT"
sed -i "s|\${USE_S3}|$USE_S3|g" "$BACKUP_SCRIPT"
sed -i "s|\${S3_BUCKET}|$S3_BUCKET|g" "$BACKUP_SCRIPT"

echo "✓ 备份脚本已创建: $BACKUP_SCRIPT"

# 配置定时任务
echo "步骤 4/5: 配置定时任务..."
(crontab -l 2>/dev/null; echo "0 2 * * * $BACKUP_SCRIPT >> /var/log/db-backup.log 2>&1") | crontab -
echo "✓ 定时任务已配置：每天凌晨 2 点执行备份"

# 测试备份
echo "步骤 5/5: 测试备份..."
"$BACKUP_SCRIPT"
echo "✓ 测试备份成功"

echo ""
echo "=== 配置完成 ==="
echo "备份目录: $BACKUP_DIR"
echo "备份脚本: $BACKUP_SCRIPT"
echo "加密密钥: $KEY_FILE"
echo ""
echo "后续步骤："
echo "1. 测试恢复："
echo "   openssl enc -aes-256-cbc -d -pass pass:\$(cat $KEY_FILE) -in <备份文件> | mysql -u root -p $DB_NAME"
echo "2. 定期检查备份文件："
echo "   ls -la $BACKUP_DIR"
echo "3. 将加密密钥保存到安全的地方（如密码管理器）"
```

#### 应用代码示例（Node.js）

```javascript
// lib/backup-manager.js
// 安全的数据库备份管理器

const { exec } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

class BackupManager {
  constructor(config) {
    this.dbConfig = config.database;
    this.backupConfig = config.backup;
    this.encryptionKey = config.encryptionKey;
  }

  async createBackup() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupFile = path.join(
      this.backupConfig.directory,
      `${this.dbConfig.database}-${timestamp}.sql.enc`
    );

    // 创建备份
    const dumpCommand = this.buildDumpCommand();
    const encryptedBackup = await this.encryptBackup(dumpCommand);

    await fs.writeFile(backupFile, encryptedBackup, { mode: 0o600 });

    console.log(`✓ 备份完成: ${backupFile}`);
    return backupFile;
  }

  buildDumpCommand() {
    switch (this.dbConfig.type) {
      case 'mysql':
        return `mysqldump -u ${this.dbConfig.user} -p${this.dbConfig.password} ${this.dbConfig.database}`;
      case 'postgresql':
        return `PGPASSWORD=${this.dbConfig.password} pg_dump -U ${this.dbConfig.user} ${this.dbConfig.database}`;
      default:
        throw new Error(`不支持的数据库类型: ${this.dbConfig.type}`);
    }
  }

  async encryptBackup(dumpCommand) {
    return new Promise((resolve, reject) => {
      exec(dumpCommand, (error, stdout, stderr) => {
        if (error) reject(error);

        // 使用 AES-256-CBC 加密
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv(
          'aes-256-cbc',
          Buffer.from(this.encryptionKey, 'base64'),
          iv
        );

        let encrypted = cipher.update(stdout, 'utf8', 'hex');
        encrypted += cipher.final('hex');

        // 将 IV 附加到加密数据前面
        resolve(iv.toString('hex') + ':' + encrypted);
      });
    });
  }

  async restoreBackup(backupFile) {
    const encryptedData = await fs.readFile(backupFile, 'utf8');
    const decryptedSQL = await this.decryptBackup(encryptedData);

    // 恢复数据库
    const restoreCommand = this.buildRestoreCommand();
    return new Promise((resolve, reject) => {
      exec(restoreCommand, (error, stdout, stderr) => {
        if (error) reject(error);
        console.log('✓ 数据库恢复完成');
        resolve();
      }).stdin.end(decryptedSQL);
    });
  }

  async decryptBackup(encryptedData) {
    const [ivHex, encrypted] = encryptedData.split(':');
    const iv = Buffer.from(ivHex, 'hex');

    const decipher = crypto.createDecipheriv(
      'aes-256-cbc',
      Buffer.from(this.encryptionKey, 'base64'),
      iv
    );

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  }

  buildRestoreCommand() {
    switch (this.dbConfig.type) {
      case 'mysql':
        return `mysql -u ${this.dbConfig.user} -p${this.dbConfig.password} ${this.dbConfig.database}`;
      case 'postgresql':
        return `PGPASSWORD=${this.dbConfig.password} psql -U ${this.dbConfig.user} ${this.dbConfig.database}`;
    }
  }

  async cleanupOldBackups() {
    const files = await fs.readdir(this.backupConfig.directory);
    const now = Date.now();
    const retentionMs = this.backupConfig.retentionDays * 24 * 60 * 60 * 1000;

    for (const file of files) {
      const filePath = path.join(this.backupConfig.directory, file);
      const stats = await fs.stat(filePath);

      if (now - stats.mtimeMs > retentionMs) {
        await fs.unlink(filePath);
        console.log(`✓ 已删除旧备份: ${file}`);
      }
    }
  }
}

module.exports = BackupManager;
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业数据备份安全最佳实践](../../enterprise/infosec/backup-security-enterprise.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 合规要求 | 基础保护 | GDPR/SOC2/HIPAA |
| 加密标准 | AES-256 | FIPS 140-2 认证加密 |
| 异地备份 | 单一云区域 | 多区域/多云容灾 |
| 访问控制 | 文件权限 | RBAC + 审计日志 |
| 备份频率 | 每日 | 每小时/实时 |
| 恢复测试 | 手动 | 自动化 RTO/RPO 验证 |

---

## 附录：常见问题

**Q: 我使用的是托管数据库（如 AWS RDS），还需要担心备份泄露吗？**

A: 托管数据库的自动备份默认加密，但你需要：
1. 确认已启用加密（AWS RDS 默认启用）
2. 限制备份快照的访问权限
3. 不要将备份快照公开共享
4. 定期检查备份快照是否被意外公开

**Q: 备份文件加密后，性能会受影响吗？**

A: 影响很小：
- 加密时间：500MB 备份文件加密约 5-10 秒
- CPU 开销：现代 CPU 支持 AES-NI 指令集，加密几乎无感
- 存储：加密后文件大小增加 < 5%

**Q: 加密密钥丢失了怎么办？**

A: **无法恢复**。建议：
1. 使用密码管理器保存加密密钥
2. 多人团队使用密钥管理服务（如 AWS KMS）
3. 定期备份加密密钥到多个安全位置

**Q: 如何验证备份文件是否可恢复？**

A: 定期测试恢复：
```bash
# 每月测试恢复到测试数据库
./restore-backup.sh backup-20260611.sql.enc test_db

# 验证数据完整性
mysql -u root -p test_db -e "SELECT COUNT(*) FROM users;"
```

---

## 参考资源

- [OWASP Backup Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Backup_Cheatsheet.html)
- [AWS S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [Restic Documentation](https://restic.readthedocs.io/)
- [MySQL Backup and Recovery](https://dev.mysql.com/doc/mysql-backup-excerpt/8.0/en/)
