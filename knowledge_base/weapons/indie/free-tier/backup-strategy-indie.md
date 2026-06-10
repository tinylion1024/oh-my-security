# 独立开发者备份策略武器

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 响应 + 恢复
- **实现成本**: 免费
- **实施时间**: 2-4小时（一次性配置）
- **维护成本**: 30分钟/月
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## 适用场景
独立开发者需要建立可靠的数据备份体系，防御数据丢失风险（硬件故障、攻击、误操作），确保业务连续性。本文提供 $0 成本的完整备份方案，遵循 3-2-1 备份原则。

---

## 核心原则：3-2-1 备份法则

```
3-2-1 备份法则
├── 3 份副本：原始数据 + 2份备份
├── 2 种介质：本地磁盘 + 云存储
└── 1 个异地：云端备份（异地机房）
```

**为什么重要？**
- 单点故障：本地磁盘损坏 → 数据全丢
- 双重风险：本地+同一云区故障 → 仍可能丢失
- 3-2-1 原则确保任意单点故障都不影响数据安全

---

## 快速上手（5分钟最小方案）

```bash
# 最小可行备份方案（本地 + 云存储）
# 适合刚上线的项目

# 1. 安装备份工具
sudo apt install -y mysqldump postgresql-client mongodb-tools

# 2. 创建备份目录
mkdir -p ~/backups/{db,files}

# 3. 快速数据库备份
mysqldump -u root -p your_db | gzip > ~/backups/db/backup_$(date +%Y%m%d).sql.gz

# 4. 使用 rclone 上传到云端（免费额度）
# 安装: curl https://rclone.org/install.sh | sudo bash
rclone copy ~/backups remote:your-backup-bucket

# 5. 添加到 crontab（每天凌晨3点）
(crontab -l 2>/dev/null; echo "0 3 * * * ~/backup.sh") | crontab -
```

---

## 详细方案

### 1. 数据库备份策略

#### 1.1 全量备份 + 增量备份

```
备份策略时间线
├── 周一 00:00 - 全量备份（完整数据库导出）
├── 周二 00:00 - 增量备份（binlog/wal归档）
├── 周三 00:00 - 增量备份
├── 周四 00:00 - 增量备份
├── 周五 00:00 - 增量备份
├── 周六 00:00 - 增量备份
└── 周日 00:00 - 全量备份 + 增量清理
```

**全量备份特点**：
- 完整数据库快照
- 恢复简单直接
- 占用空间大
- 适合每周一次

**增量备份特点**：
- 只备份变化部分
- 占用空间小
- 恢复需全量+增量
- 适合每日多次

---

### 2. MySQL 自动备份脚本

```bash
#!/bin/bash
# mysql-backup.sh - MySQL 自动备份脚本
# 功能：全量备份 + 自动清理 + 云端上传

set -e

# ============ 配置区域 ============
DB_HOST="localhost"
DB_USER="backup_user"
DB_PASS="your_secure_password"
DB_NAMES=("app_db" "user_db" "log_db")  # 多数据库

BACKUP_DIR="/var/backups/mysql"
RETENTION_DAYS=30  # 本地保留30天
RETENTION_CLOUD=90  # 云端保留90天

# 云存储配置（rclone）
RCLONE_REMOTE="aws-s3"  # rclone配置的远程名称
RCLONE_BUCKET="your-backup-bucket/mysql"

# 加密配置
ENABLE_ENCRYPTION=true
ENCRYPTION_KEY="/root/.backup_key"

# 告警配置
ALERT_EMAIL="your@email.com"
ENABLE_EMAIL_ALERT=true

# ============ 函数定义 ============

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

send_alert() {
    local subject="$1"
    local body="$2"
    
    if [ "$ENABLE_EMAIL_ALERT" = true ]; then
        echo "$body" | mail -s "$subject" "$ALERT_EMAIL"
    fi
    log "ALERT: $subject"
}

# 加密备份文件
encrypt_file() {
    local file="$1"
    local encrypted_file="${file}.enc"
    
    if [ "$ENABLE_ENCRYPTION" = true ]; then
        openssl enc -aes-256-cbc \
            -salt -pbkdf2 \
            -in "$file" \
            -out "$encrypted_file" \
            -pass file:"$ENCRYPTION_KEY"
        echo "$encrypted_file"
    else
        echo "$file"
    fi
}

# 上传到云端
upload_to_cloud() {
    local file="$1"
    local remote_path="$RCLONE_BUCKET/$(basename $file)"
    
    if rclone copy "$file" "$RCLONE_REMOTE:$remote_path" --progress; then
        log "✓ Uploaded to cloud: $remote_path"
        return 0
    else
        send_alert "Backup Upload Failed" "Failed to upload: $file"
        return 1
    fi
}

# 清理过期备份
cleanup_old_backups() {
    log "Cleaning backups older than $RETENTION_DAYS days..."
    
    # 清理本地备份
    find "$BACKUP_DIR" -name "*.sql.gz*" -type f -mtime +$RETENTION_DAYS -delete
    
    # 清理云端备份
    if [ -n "$RCLONE_REMOTE" ]; then
        rclone delete "$RCLONE_REMOTE:$RCLONE_BUCKET" \
            --min-age ${RETENTION_CLOUD}d \
            --rmdirs
    fi
    
    log "✓ Cleanup completed"
}

# 检查备份完整性
verify_backup() {
    local backup_file="$1"
    
    # 检查文件是否完整（gzip测试）
    if gzip -t "$backup_file" 2>/dev/null; then
        log "✓ Backup integrity verified: $backup_file"
        return 0
    else
        send_alert "Backup Integrity Failed" "Corrupted backup: $backup_file"
        return 1
    fi
}

# ============ 主备份流程 ============

main() {
    local TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    local DATE=$(date '+%Y%m%d')
    
    log "========== MySQL Backup Started =========="
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    # 备份每个数据库
    for DB_NAME in "${DB_NAMES[@]}"; do
        log "Backing up database: $DB_NAME"
        
        local BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"
        
        # 执行备份
        if mysqldump \
            -h "$DB_HOST" \
            -u "$DB_USER" \
            -p"$DB_PASS" \
            --single-transaction \
            --routines \
            --triggers \
            --events \
            "$DB_NAME" | gzip > "$BACKUP_FILE"; then
            
            log "✓ Database dumped: $BACKUP_FILE"
            
            # 验证备份
            if verify_backup "$BACKUP_FILE"; then
                # 加密
                local FINAL_FILE=$(encrypt_file "$BACKUP_FILE")
                
                # 上传云端
                upload_to_cloud "$FINAL_FILE"
                
                # 删除加密文件（保留原文件）
                if [ "$ENABLE_ENCRYPTION" = true ]; then
                    rm -f "$FINAL_FILE"
                fi
            fi
        else
            send_alert "MySQL Backup Failed" "Failed to backup database: $DB_NAME"
            continue
        fi
    done
    
    # 全库备份（可选）
    local ALL_DB_FILE="${BACKUP_DIR}/all_databases_${TIMESTAMP}.sql.gz"
    mysqldump \
        -h "$DB_HOST" \
        -u "$DB_USER" \
        -p"$DB_PASS" \
        --single-transaction \
        --all-databases | gzip > "$ALL_DB_FILE"
    
    # 清理过期备份
    cleanup_old_backups
    
    # 备份统计
    local BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
    local BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.sql.gz 2>/dev/null | wc -l)
    
    log "========== Backup Summary =========="
    log "Total backups: $BACKUP_COUNT"
    log "Total size: $BACKUP_SIZE"
    log "Backup directory: $BACKUP_DIR"
    log "========== MySQL Backup Completed =========="
}

# ============ 执行 ============

main "$@"
```

**安装与配置**：

```bash
# 1. 创建备份专用MySQL用户
mysql -u root -p << 'EOF'
CREATE USER 'backup_user'@'localhost' IDENTIFIED BY '你的强密码';
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER ON *.* TO 'backup_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# 2. 生成加密密钥
openssl rand -base64 32 > /root/.backup_key
chmod 400 /root/.backup_key

# 3. 保存脚本
chmod +x /usr/local/bin/mysql-backup.sh

# 4. 配置rclone（首次）
rclone config
# 选择云存储类型（AWS S3 / Cloudflare R2 / Backblaze B2）

# 5. 测试执行
/usr/local/bin/mysql-backup.sh

# 6. 添加到crontab
cat >> /etc/cron.d/mysql-backup << 'EOF'
# MySQL daily backup at 3:00 AM
0 3 * * * root /usr/local/bin/mysql-backup.sh >> /var/log/mysql-backup.log 2>&1
EOF
```

---

### 3. PostgreSQL 自动备份脚本

```bash
#!/bin/bash
# pgsql-backup.sh - PostgreSQL 自动备份脚本
# 功能：全量备份 + WAL归档 + PITR支持

set -e

# ============ 配置区域 ============
PG_HOST="localhost"
PG_PORT="5432"
PG_USER="backup_user"
PG_PASS="your_secure_password"
PG_DATABASES=("app_db" "user_db")

BACKUP_DIR="/var/backups/postgresql"
WAL_ARCHIVE_DIR="/var/backups/postgresql/wal_archive"
RETENTION_DAYS=30

# 云存储配置
RCLONE_REMOTE="aws-s3"
RCLONE_BUCKET="your-backup-bucket/postgresql"

# ============ 函数定义 ============

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 设置密码环境变量
export PGPASSWORD="$PG_PASS"

# PostgreSQL全量备份
pg_full_backup() {
    local db="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_DIR}/${db}_${timestamp}.sql.gz"
    
    log "Starting full backup for database: $db"
    
    # 使用pg_dump进行备份
    pg_dump \
        -h "$PG_HOST" \
        -p "$PG_PORT" \
        -U "$PG_USER" \
        -d "$db" \
        --format=custom \
        --no-owner \
        --no-privileges \
        | gzip > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log "✓ Backup created: $backup_file"
        
        # 上传云端
        rclone copy "$backup_file" "$RCLONE_REMOTE:$RCLONE_BUCKET/full/"
        
        # 本地清理
        find "$BACKUP_DIR" -name "${db}_*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
    else
        log "✗ Backup failed for database: $db"
        return 1
    fi
}

# WAL归档备份（用于PITR - Point-in-Time Recovery）
pg_wal_archive() {
    local wal_file="$1"
    local archive_path="${WAL_ARCHIVE_DIR}/$(basename $wal_file)"
    
    # 复制WAL文件到归档目录
    cp "$wal_file" "$archive_path"
    
    # 上传到云端
    rclone copy "$archive_path" "$RCLONE_REMOTE:$RCLONE_BUCKET/wal/"
    
    log "✓ WAL archived: $(basename $wal_file)"
}

# PITR恢复脚本
pg_pitr_restore() {
    local target_time="$1"  # 格式: '2026-06-11 14:30:00'
    local restore_dir="$2"
    
    log "Starting PITR restore to: $target_time"
    
    # 1. 停止PostgreSQL服务
    systemctl stop postgresql
    
    # 2. 清空数据目录
    rm -rf /var/lib/postgresql/14/main/*
    
    # 3. 恢复基础备份
    # (需要先从云端下载基础备份)
    
    # 4. 配置recovery
    cat > /var/lib/postgresql/14/main/recovery.signal << EOF
restore_command = 'rclone cat $RCLONE_REMOTE:$RCLONE_BUCKET/wal/%f > %p'
recovery_target_time = '$target_time'
recovery_target_action = 'promote'
EOF
    
    # 5. 启动PostgreSQL
    systemctl start postgresql
    
    log "✓ PITR restore completed"
}

# ============ 主流程 ============

main() {
    log "========== PostgreSQL Backup Started =========="
    
    mkdir -p "$BACKUP_DIR" "$WAL_ARCHIVE_DIR"
    
    # 全量备份每个数据库
    for db in "${PG_DATABASES[@]}"; do
        pg_full_backup "$db"
    done
    
    # 全库备份
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    pg_dumpall \
        -h "$PG_HOST" \
        -p "$PG_PORT" \
        -U "$PG_USER" \
        | gzip > "${BACKUP_DIR}/all_databases_${timestamp}.sql.gz"
    
    log "========== PostgreSQL Backup Completed =========="
}

# 根据参数执行不同操作
case "$1" in
    "archive")
        pg_wal_archive "$2"
        ;;
    "restore")
        pg_pitr_restore "$2" "$3"
        ;;
    *)
        main
        ;;
esac
```

**PostgreSQL WAL归档配置**（启用PITR）：

```bash
# 编辑 postgresql.conf
sudo tee -a /etc/postgresql/14/main/postgresql.conf << 'EOF'
# WAL配置（用于增量备份和PITR）
wal_level = replica
archive_mode = on
archive_command = '/usr/local/bin/pgsql-backup.sh archive %p'
max_wal_senders = 3
wal_keep_segments = 64
EOF

# 重启PostgreSQL
sudo systemctl restart postgresql
```

---

### 4. MongoDB 备份脚本

```bash
#!/bin/bash
# mongo-backup.sh - MongoDB 自动备份脚本
# 功能：全量备份 + Oplog归档

set -e

# ============ 配置区域 ============
MONGO_URI="mongodb://localhost:27017"
MONGO_USER="backup_user"
MONGO_PASS="your_secure_password"
MONGO_AUTH_DB="admin"

BACKUP_DIR="/var/backups/mongodb"
RETENTION_DAYS=30

RCLONE_REMOTE="aws-s3"
RCLONE_BUCKET="your-backup-bucket/mongodb"

# ============ 主流程 ============

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# MongoDB备份
mongo_backup() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_path="${BACKUP_DIR}/mongo_${timestamp}"
    
    log "Starting MongoDB backup..."
    
    mkdir -p "$backup_path"
    
    # 使用mongodump备份
    mongodump \
        --uri="$MONGO_URI" \
        --username="$MONGO_USER" \
        --password="$MONGO_PASS" \
        --authenticationDatabase="$MONGO_AUTH_DB" \
        --out="$backup_path" \
        --gzip \
        --oplog  # 包含oplog用于时间点恢复
    
    if [ $? -eq 0 ]; then
        log "✓ MongoDB dump completed: $backup_path"
        
        # 打包压缩
        tar -czf "${backup_path}.tar.gz" -C "$BACKUP_DIR" "mongo_${timestamp}"
        rm -rf "$backup_path"
        
        # 上传云端
        rclone copy "${backup_path}.tar.gz" "$RCLONE_REMOTE:$RCLONE_BUCKET/"
        
        # 本地清理
        find "$BACKUP_DIR" -name "mongo_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
        
        log "✓ Backup uploaded and cleaned"
    else
        log "✗ MongoDB backup failed"
        return 1
    fi
}

# MongoDB恢复
mongo_restore() {
    local backup_file="$1"
    local target_db="$2"  # 可选，恢复到特定数据库
    
    log "Starting MongoDB restore from: $backup_file"
    
    # 解压
    local temp_dir=$(mktemp -d)
    tar -xzf "$backup_file" -C "$temp_dir"
    
    # 恢复
    if [ -n "$target_db" ]; then
        mongorestore \
            --uri="$MONGO_URI" \
            --username="$MONGO_USER" \
            --password="$MONGO_PASS" \
            --authenticationDatabase="$MONGO_AUTH_DB" \
            --db="$target_db" \
            --drop \
            --gzip \
            "$temp_dir/$target_db"
    else
        mongorestore \
            --uri="$MONGO_URI" \
            --username="$MONGO_USER" \
            --password="$MONGO_PASS" \
            --authenticationDatabase="$MONGO_AUTH_DB" \
            --drop \
            --gzip \
            "$temp_dir"
    fi
    
    rm -rf "$temp_dir"
    log "✓ MongoDB restore completed"
}

# 执行
case "$1" in
    "restore")
        mongo_restore "$2" "$3"
        ;;
    *)
        mongo_backup
        ;;
esac
```

---

### 5. 云存储备份方案对比

#### 免费云存储对比表

| 云存储服务 | 免费额度 | 特点 | 适合场景 |
|-----------|---------|------|---------|
| **AWS S3** | 5GB (12个月) | 业界标准、生态完善 | AWS生态用户 |
| **Cloudflare R2** | 10GB | 无出口流量费、S3兼容 | 高频访问备份 |
| **Backblaze B2** | 10GB | 价格透明、S3兼容 | 长期冷备份 |
| **Google Cloud Storage** | 5GB (90天) | 集成Google生态 | GCP用户 |
| **Wasabi** | 无免费层 | 但价格极低$6.99/TB | 大量冷备份 |
| **MinIO自建** | 无限制 | 需自维护、完全控制 | 隐私敏感场景 |

#### AWS S3 免费层配置

```bash
# 安装AWS CLI
pip install awscli

# 配置凭证
aws configure
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region: us-east-1

# 创建S3桶（免费层12个月内5GB存储）
aws s3 mb s3://your-unique-backup-bucket

# 启用版本控制（防止误删）
aws s3api put-bucket-versioning \
    --bucket your-unique-backup-bucket \
    --versioning-configuration Status=Enabled

# 设置生命周期策略（自动清理旧版本）
cat > lifecycle.json << 'EOF'
{
    "Rules": [
        {
            "ID": "DeleteOldVersions",
            "Status": "Enabled",
            "NoncurrentVersionExpiration": {
                "NoncurrentDays": 90
            }
        },
        {
            "ID": "MoveToGlacier",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "archive/"
            },
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "GLACIER"
                }
            ]
        }
    ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket your-unique-backup-bucket \
    --lifecycle-configuration file://lifecycle.json
```

#### Cloudflare R2 配置（推荐）

```bash
# 优势：10GB免费，无出口流量费，S3兼容API

# 1. 在Cloudflare Dashboard创建R2桶
# https://dash.cloudflare.com/

# 2. 获取API Token
# R2 -> Manage R2 API Tokens -> Create API Token

# 3. 配置rclone
rclone config
# 选择 "s3" 类型
# provider: Cloudflare R2
# access_key_id: [your-key]
# secret_access_key: [your-secret]
# endpoint: https://<account-id>.r2.cloudflarestorage.com

# 4. 测试上传
rclone copy /backup/test.sql.gz r2:your-bucket-name/

# 5. 自动同步脚本
cat > /usr/local/bin/r2-sync.sh << 'EOF'
#!/bin/bash
SOURCE_DIR="/var/backups"
R2_BUCKET="r2:your-backup-bucket"

# 同步到R2（只上传新文件）
rclone sync "$SOURCE_DIR" "$R2_BUCKET" \
    --progress \
    --transfers 4 \
    --checkers 8 \
    --log-file /var/log/rclone.log
EOF

chmod +x /usr/local/bin/r2-sync.sh
```

---

### 6. 文件备份策略

#### 应用文件备份脚本

```bash
#!/bin/bash
# file-backup.sh - 应用文件自动备份

set -e

# ============ 配置区域 ============
BACKUP_DIRS=(
    "/var/www/html"
    "/var/www/uploads"
    "/etc/nginx"
    "/etc/letsencrypt"
    "/home/deploy/.ssh"
)

BACKUP_DIR="/var/backups/files"
RETENTION_DAYS=30

RCLONE_REMOTE="aws-s3"
RCLONE_BUCKET="your-backup-bucket/files"

# 排除模式
EXCLUDE_PATTERNS=(
    "*.log"
    "*.tmp"
    "node_modules"
    ".git"
    "cache/*"
)

# ============ 函数定义 ============

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 创建排除参数
build_exclude_args() {
    local args=""
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        args="$args --exclude=$pattern"
    done
    echo "$args"
}

# 备份单个目录
backup_directory() {
    local source_dir="$1"
    local dir_name=$(basename "$source_dir")
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="${BACKUP_DIR}/${dir_name}_${timestamp}.tar.gz"
    
    log "Backing up: $source_dir"
    
    # 获取排除参数
    local exclude_args=$(build_exclude_args)
    
    # 增量备份（使用tar的--newer参数）
    local snapshot_file="${BACKUP_DIR}/.snapshot_${dir_name}"
    
    if [ -f "$snapshot_file" ]; then
        # 增量备份
        tar -czf "$backup_file" \
            $exclude_args \
            --listed-incremental="$snapshot_file" \
            -C "$(dirname $source_dir)" \
            "$dir_name"
        log "✓ Incremental backup: $backup_file"
    else
        # 首次全量备份
        tar -czf "$backup_file" \
            $exclude_args \
            --listed-incremental="$snapshot_file" \
            -C "$(dirname $source_dir)" \
            "$dir_name"
        log "✓ Full backup: $backup_file"
    fi
    
    # 上传云端
    rclone copy "$backup_file" "$RCLONE_REMOTE:$RCLONE_BUCKET/"
    
    # 计算备份大小
    local size=$(du -sh "$backup_file" | cut -f1)
    log "  Size: $size"
}

# ============ 主流程 ============

main() {
    log "========== File Backup Started =========="
    
    mkdir -p "$BACKUP_DIR"
    
    # 备份每个目录
    for dir in "${BACKUP_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            backup_directory "$dir"
        else
            log "✗ Directory not found: $dir"
        fi
    done
    
    # 清理过期备份
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # 备份统计
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    local file_count=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
    
    log "========== Backup Summary =========="
    log "Total files: $file_count"
    log "Total size: $total_size"
    log "========== File Backup Completed =========="
}

main "$@"
```

---

### 7. 备份加密实现

```bash
#!/bin/bash
# backup-encryption.sh - 备份加密工具

# ============ 加密配置 ============

# 生成加密密钥（一次性）
generate_encryption_key() {
    local key_file="$1"
    openssl rand -base64 32 > "$key_file"
    chmod 400 "$key_file"
    echo "Encryption key saved to: $key_file"
    echo "⚠️  请妥善保管此密钥！丢失将无法恢复备份！"
}

# 使用公钥加密（无需管理密码）
setup_gpg_encryption() {
    # 生成GPG密钥对
    gpg --full-generate-key
    # 选择: (1) RSA and RSA
    # 密钥长度: 4096
    # 有效期: 0 (永不过期)
    
    # 导出公钥（用于备份服务器）
    gpg --armor --export your@email.com > public_key.asc
    
    # 导出私钥（离线保管）
    gpg --armor --export-secret-keys your@email.com > private_key.asc
    # ⚠️ 将私钥保存到安全位置后删除
    # rm private_key.asc
}

# 加密文件（对称加密）
encrypt_file_symmetric() {
    local input_file="$1"
    local key_file="$2"
    local output_file="${input_file}.enc"
    
    openssl enc -aes-256-cbc \
        -salt -pbkdf2 \
        -in "$input_file" \
        -out "$output_file" \
        -pass file:"$key_file"
    
    echo "Encrypted: $output_file"
}

# 解密文件
decrypt_file_symmetric() {
    local input_file="$1"
    local key_file="$2"
    local output_file="${input_file%.enc}"
    
    openssl enc -aes-256-cbc \
        -d -pbkdf2 \
        -in "$input_file" \
        -out "$output_file" \
        -pass file:"$key_file"
    
    echo "Decrypted: $output_file"
}

# 加密文件（GPG非对称加密，更安全）
encrypt_file_gpg() {
    local input_file="$1"
    local recipient="$2"  # GPG密钥邮箱
    local output_file="${input_file}.gpg"
    
    gpg --encrypt \
        --recipient "$recipient" \
        --output "$output_file" \
        "$input_file"
    
    echo "Encrypted with GPG: $output_file"
}

# 解密文件（GPG）
decrypt_file_gpg() {
    local input_file="$1"
    local output_file="${input_file%.gpg}"
    
    gpg --decrypt \
        --output "$output_file" \
        "$input_file"
    
    echo "Decrypted: $output_file"
}

# 示例使用
case "$1" in
    "generate-key")
        generate_encryption_key "$2"
        ;;
    "setup-gpg")
        setup_gpg_encryption
        ;;
    "encrypt")
        encrypt_file_symmetric "$2" "$3"
        ;;
    "decrypt")
        decrypt_file_symmetric "$2" "$3"
        ;;
    "encrypt-gpg")
        encrypt_file_gpg "$2" "$3"
        ;;
    "decrypt-gpg")
        decrypt_file_gpg "$2"
        ;;
    *)
        echo "Usage: $0 {generate-key|setup-gpg|encrypt|decrypt|encrypt-gpg|decrypt-gpg}"
        ;;
esac
```

**最佳实践**：

```bash
# 1. 生成加密密钥
/usr/local/bin/backup-encryption.sh generate-key /root/.backup_key

# 2. 备份密钥到安全位置（离线保存）
# - 复制到USB驱动器
# - 打印为纸质备份
# - 使用密码管理器存储

# 3. 在备份脚本中启用加密
# 修改 mysql-backup.sh:
ENABLE_ENCRYPTION=true
ENCRYPTION_KEY="/root/.backup_key"
```

---

### 8. 备份恢复脚本

```bash
#!/bin/bash
# backup-restore.sh - 统一备份恢复脚本

set -e

# ============ 配置区域 ============
BACKUP_DIR="/var/backups"
TEMP_DIR="/tmp/restore_$(date +%s)"

# 云存储配置
RCLONE_REMOTE="aws-s3"

# ============ 函数定义 ============

log() {
    echo "[RESTORE] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 列出可用备份
list_available_backups() {
    echo "========== Available Backups =========="
    echo ""
    echo "Local backups:"
    find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.tar.gz" | sort -r | head -20
    
    echo ""
    echo "Cloud backups:"
    rclone ls "$RCLONE_REMOTE:your-backup-bucket" | head -20
}

# 恢复MySQL数据库
restore_mysql() {
    local backup_file="$1"
    local target_db="$2"
    local key_file="${3:-/root/.backup_key}"
    
    log "Starting MySQL restore..."
    log "Backup file: $backup_file"
    log "Target database: $target_db"
    
    # 创建临时目录
    mkdir -p "$TEMP_DIR"
    
    # 如果是加密文件，先解密
    local sql_file="$backup_file"
    if [[ "$backup_file" == *.enc ]]; then
        log "Decrypting backup..."
        openssl enc -aes-256-cbc -d -pbkdf2 \
            -in "$backup_file" \
            -out "${TEMP_DIR}/backup.sql.gz" \
            -pass file:"$key_file"
        sql_file="${TEMP_DIR}/backup.sql.gz"
    fi
    
    # 解压
    gunzip -c "$sql_file" > "${TEMP_DIR}/backup.sql"
    
    # 恢复数据库
    log "Restoring database..."
    mysql -u root -p << EOF
DROP DATABASE IF EXISTS ${target_db}_restore;
CREATE DATABASE ${target_db}_restore;
USE ${target_db}_restore;
SOURCE ${TEMP_DIR}/backup.sql;
EOF
    
    log "✓ Database restored to: ${target_db}_restore"
    log "Please verify and rename: RENAME DATABASE ${target_db}_restore TO $target_db;"
    
    # 清理
    rm -rf "$TEMP_DIR"
}

# 恢复PostgreSQL数据库
restore_postgresql() {
    local backup_file="$1"
    local target_db="$2"
    
    log "Starting PostgreSQL restore..."
    
    mkdir -p "$TEMP_DIR"
    
    # 解压
    gunzip -c "$backup_file" > "${TEMP_DIR}/backup.sql"
    
    # 创建恢复数据库
    sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS ${target_db}_restore;
CREATE DATABASE ${target_db}_restore;
EOF
    
    # 恢复
    sudo -u postgres psql "${target_db}_restore" < "${TEMP_DIR}/backup.sql"
    
    log "✓ Database restored to: ${target_db}_restore"
    rm -rf "$TEMP_DIR"
}

# 恢复文件备份
restore_files() {
    local backup_file="$1"
    local target_dir="$2"
    
    log "Starting file restore..."
    log "Backup file: $backup_file"
    log "Target directory: $target_dir"
    
    # 创建临时目录
    mkdir -p "$TEMP_DIR"
    
    # 解压
    tar -xzf "$backup_file" -C "$TEMP_DIR"
    
    # 确认恢复
    read -p "This will overwrite files in $target_dir. Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        log "Restore cancelled"
        exit 0
    fi
    
    # 恢复文件
    rsync -av "${TEMP_DIR}/" "$target_dir"
    
    log "✓ Files restored to: $target_dir"
    rm -rf "$TEMP_DIR"
}

# 从云端下载备份
download_from_cloud() {
    local cloud_path="$1"
    local local_path="$2"
    
    log "Downloading from cloud: $cloud_path"
    rclone copy "$RCLONE_REMOTE:$cloud_path" "$local_path"
    log "✓ Download completed"
}

# ============ 主流程 ============

case "$1" in
    "list")
        list_available_backups
        ;;
    "mysql")
        restore_mysql "$2" "$3" "$4"
        ;;
    "pgsql")
        restore_postgresql "$2" "$3"
        ;;
    "files")
        restore_files "$2" "$3"
        ;;
    "download")
        download_from_cloud "$2" "$3"
        ;;
    *)
        echo "Usage: $0 {list|mysql|pgsql|files|download}"
        echo ""
        echo "Examples:"
        echo "  $0 list"
        echo "  $0 mysql /backup/db_20260611.sql.gz app_db"
        echo "  $0 pgsql /backup/db_20260611.sql.gz app_db"
        echo "  $0 files /backup/uploads_20260611.tar.gz /var/www/uploads"
        echo "  $0 download bucket/db_20260611.sql.gz /local/backup/"
        ;;
esac
```

---

### 9. 自动化备份调度

#### Cron 定时任务配置

```bash
# /etc/cron.d/backup-schedule

# 环境变量
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=your@email.com

# MySQL 每日备份（凌晨3点）
0 3 * * * root /usr/local/bin/mysql-backup.sh >> /var/log/backup/mysql.log 2>&1

# PostgreSQL 每日备份（凌晨4点）
0 4 * * * root /usr/local/bin/pgsql-backup.sh >> /var/log/backup/pgsql.log 2>&1

# MongoDB 每日备份（凌晨5点）
0 5 * * * root /usr/local/bin/mongo-backup.sh >> /var/log/backup/mongo.log 2>&1

# 应用文件 每日备份（凌晨6点）
0 6 * * * root /usr/local/bin/file-backup.sh >> /var/log/backup/files.log 2>&1

# 云存储同步 每日（凌晨7点）
0 7 * * * root /usr/local/bin/r2-sync.sh >> /var/log/backup/sync.log 2>&1

# 每周备份验证（周日凌晨8点）
0 8 * * 0 root /usr/local/bin/backup-verify.sh >> /var/log/backup/verify.log 2>&1

# 每月恢复测试（每月1号凌晨9点）
0 9 1 * * root /usr/local/bin/backup-recovery-test.sh >> /var/log/backup/test.log 2>&1
```

#### Systemd Timer（替代Cron）

```ini
# /etc/systemd/system/mysql-backup.service
[Unit]
Description=MySQL Database Backup
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/mysql-backup.sh
User=root

# /etc/systemd/system/mysql-backup.timer
[Unit]
Description=Run MySQL backup daily

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# 启用定时器
systemctl enable mysql-backup.timer
systemctl start mysql-backup.timer

# 查看定时器状态
systemctl list-timers
```

---

### 10. 备份验证与恢复测试

#### 自动验证脚本

```bash
#!/bin/bash
# backup-verify.sh - 备份完整性验证

set -e

# ============ 配置区域 ============
BACKUP_DIR="/var/backups"
LOG_FILE="/var/log/backup/verify.log"

# ============ 函数定义 ============

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 验证MySQL备份
verify_mysql_backup() {
    local backup_file="$1"
    
    log "Verifying MySQL backup: $backup_file"
    
    # 1. 检查文件完整性（gzip测试）
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log "✗ GZIP integrity check failed: $backup_file"
        return 1
    fi
    log "✓ GZIP integrity OK"
    
    # 2. 检查SQL文件结构
    local sql_content=$(zcat "$backup_file" | head -50)
    if ! echo "$sql_content" | grep -q "MySQL dump"; then
        log "✗ Invalid MySQL dump format"
        return 1
    fi
    log "✓ MySQL dump format OK"
    
    # 3. 检查文件大小（不应为0）
    local size=$(stat -f%z "$backup_file" 2>/dev/null || stat -c%s "$backup_file")
    if [ "$size" -lt 100 ]; then
        log "✗ Backup file too small: $size bytes"
        return 1
    fi
    log "✓ File size OK: $size bytes"
    
    return 0
}

# 验证PostgreSQL备份
verify_pgsql_backup() {
    local backup_file="$1"
    
    log "Verifying PostgreSQL backup: $backup_file"
    
    # 检查gzip完整性
    if ! gzip -t "$backup_file" 2>/dev/null; then
        log "✗ GZIP integrity check failed"
        return 1
    fi
    
    # 检查PG dump格式
    local sql_content=$(zcat "$backup_file" | head -50)
    if ! echo "$sql_content" | grep -q "PostgreSQL"; then
        log "✗ Invalid PostgreSQL dump format"
        return 1
    fi
    
    log "✓ PostgreSQL backup valid"
    return 0
}

# 验证文件备份
verify_file_backup() {
    local backup_file="$1"
    
    log "Verifying file backup: $backup_file"
    
    # 检查tar完整性
    if ! tar -tzf "$backup_file" >/dev/null 2>&1; then
        log "✗ TAR integrity check failed"
        return 1
    fi
    
    log "✓ File backup valid"
    return 0
}

# 验证云存储备份
verify_cloud_backup() {
    log "Verifying cloud backup accessibility..."
    
    # 检查最新备份是否已上传
    local latest_local=$(ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | head -1)
    if [ -n "$latest_local" ]; then
        local filename=$(basename "$latest_local")
        if rclone ls "aws-s3:your-backup-bucket/$filename" >/dev/null 2>&1; then
            log "✓ Latest backup exists in cloud: $filename"
        else
            log "✗ Latest backup NOT in cloud: $filename"
            return 1
        fi
    fi
    
    return 0
}

# ============ 主流程 ============

main() {
    log "========== Backup Verification Started =========="
    
    local errors=0
    
    # 验证MySQL备份
    for backup in "$BACKUP_DIR"/mysql/*.sql.gz; do
        [ -f "$backup" ] || continue
        verify_mysql_backup "$backup" || ((errors++))
    done
    
    # 验证PostgreSQL备份
    for backup in "$BACKUP_DIR"/postgresql/*.sql.gz; do
        [ -f "$backup" ] || continue
        verify_pgsql_backup "$backup" || ((errors++))
    done
    
    # 验证文件备份
    for backup in "$BACKUP_DIR"/files/*.tar.gz; do
        [ -f "$backup" ] || continue
        verify_file_backup "$backup" || ((errors++))
    done
    
    # 验证云存储
    verify_cloud_backup || ((errors++))
    
    log "========== Verification Summary =========="
    if [ $errors -eq 0 ]; then
        log "✓ All backups verified successfully"
        return 0
    else
        log "✗ $errors backup(s) failed verification"
        # 发送告警
        echo "Backup verification failed: $errors error(s)" | mail -s "Backup Alert" your@email.com
        return 1
    fi
}

main "$@"
```

#### 恢复测试脚本

```bash
#!/bin/bash
# backup-recovery-test.sh - 定期恢复测试

set -e

# ============ 配置区域 ============
TEST_DB_PREFIX="restore_test_"
TEST_DIR="/tmp/restore_test"

# ============ 函数定义 ============

log() {
    echo "[RECOVERY TEST] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 测试MySQL恢复
test_mysql_recovery() {
    log "Testing MySQL recovery..."
    
    local latest_backup=$(ls -t /var/backups/mysql/*.sql.gz | head -1)
    local test_db="${TEST_DB_PREFIX}$(date +%s)"
    
    # 恢复到测试数据库
    gunzip -c "$latest_backup" | mysql -u root -p"$MYSQL_PASS" -e "CREATE DATABASE $test_db; USE $test_db; SOURCE /dev/stdin;"
    
    # 验证数据
    local table_count=$(mysql -u root -p"$MYSQL_PASS" -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$test_db'")
    
    if [ "$table_count" -gt 0 ]; then
        log "✓ MySQL recovery test passed: $table_count tables restored"
        # 清理测试数据库
        mysql -u root -p"$MYSQL_PASS" -e "DROP DATABASE $test_db"
        return 0
    else
        log "✗ MySQL recovery test failed: no tables restored"
        return 1
    fi
}

# 测试PostgreSQL恢复
test_pgsql_recovery() {
    log "Testing PostgreSQL recovery..."
    
    local latest_backup=$(ls -t /var/backups/postgresql/*.sql.gz | head -1)
    local test_db="${TEST_DB_PREFIX}$(date +%s)"
    
    # 创建并恢复测试数据库
    sudo -u postgres createdb "$test_db"
    gunzip -c "$latest_backup" | sudo -u postgres psql "$test_db" >/dev/null
    
    # 验证
    local table_count=$(sudo -u postgres psql -t "$test_db" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    
    if [ "$table_count" -gt 0 ]; then
        log "✓ PostgreSQL recovery test passed"
        sudo -u postgres dropdb "$test_db"
        return 0
    else
        log "✗ PostgreSQL recovery test failed"
        return 1
    fi
}

# 测试文件恢复
test_file_recovery() {
    log "Testing file recovery..."
    
    local latest_backup=$(ls -t /var/backups/files/*.tar.gz | head -1)
    local test_dir="${TEST_DIR}/files_$(date +%s)"
    
    mkdir -p "$test_dir"
    tar -xzf "$latest_backup" -C "$test_dir"
    
    # 验证
    local file_count=$(find "$test_dir" -type f | wc -l)
    
    if [ "$file_count" -gt 0 ]; then
        log "✓ File recovery test passed: $file_count files restored"
        rm -rf "$test_dir"
        return 0
    else
        log "✗ File recovery test failed"
        return 1
    fi
}

# 生成测试报告
generate_report() {
    local report_file="/var/log/backup/recovery_test_$(date +%Y%m%d).log"
    
    cat > "$report_file" << EOF
========== Recovery Test Report ==========
Date: $(date)
Hostname: $(hostname)

Test Results:
- MySQL Recovery: ${mysql_result:-FAILED}
- PostgreSQL Recovery: ${pgsql_result:-FAILED}
- File Recovery: ${file_result:-FAILED}

Recommendations:
$(grep -E "✗|failed" "$report_file" && echo "Please investigate failed tests" || echo "All tests passed successfully")

Next scheduled test: $(date -d '+1 month' '+%Y-%m-%d')
EOF
    
    log "Report saved to: $report_file"
}

# ============ 主流程 ============

main() {
    log "========== Recovery Test Started =========="
    
    local failed=0
    
    # 执行测试
    if test_mysql_recovery; then
        mysql_result="PASSED"
    else
        mysql_result="FAILED"
        ((failed++))
    fi
    
    if test_pgsql_recovery; then
        pgsql_result="PASSED"
    else
        pgsql_result="FAILED"
        ((failed++))
    fi
    
    if test_file_recovery; then
        file_result="PASSED"
    else
        file_result="FAILED"
        ((failed++))
    fi
    
    # 生成报告
    generate_report
    
    log "========== Recovery Test Completed =========="
    log "Summary: $((3 - failed))/3 tests passed"
    
    # 发送报告
    if [ $failed -gt 0 ]; then
        mail -s "Recovery Test FAILED" your@email.com < /var/log/backup/recovery_test_$(date +%Y%m%d).log
        return 1
    else
        mail -s "Recovery Test PASSED" your@email.com < /var/log/backup/recovery_test_$(date +%Y%m%d).log
        return 0
    fi
}

main "$@"
```

---

## 恢复测试清单

### 月度恢复测试清单

```markdown
## 月度备份恢复测试清单

**测试日期**: YYYY-MM-DD
**测试人员**: [姓名]
**测试环境**: [生产/预发布]

### 1. 准备阶段
- [ ] 确认测试不会影响生产数据
- [ ] 准备隔离的测试环境
- [ ] 确认有足够的磁盘空间
- [ ] 通知相关人员即将进行恢复测试

### 2. 数据库恢复测试

#### MySQL
- [ ] 选择最新的MySQL备份文件
- [ ] 恢复到测试数据库
- [ ] 验证表数量是否匹配
- [ ] 验证关键数据行数
- [ ] 执行简单查询验证数据完整性
- [ ] 记录恢复耗时: ___ 分钟
- [ ] 清理测试数据库

#### PostgreSQL
- [ ] 选择最新的PostgreSQL备份文件
- [ ] 恢复到测试数据库
- [ ] 验证schema完整性
- [ ] 验证索引、约束是否存在
- [ ] 执行存储过程验证
- [ ] 记录恢复耗时: ___ 分钟
- [ ] 清理测试数据库

#### MongoDB
- [ ] 选择最新的MongoDB备份文件
- [ ] 恢复到测试数据库
- [ ] 验证collection数量
- [ ] 验证文档数量
- [ ] 验证索引是否存在
- [ ] 记录恢复耗时: ___ 分钟
- [ ] 清理测试数据库

### 3. 文件恢复测试

#### 应用文件
- [ ] 选择最新的应用文件备份
- [ ] 恢复到临时目录
- [ ] 验证文件数量
- [ ] 验证关键配置文件
- [ ] 验证文件权限
- [ ] 记录恢复耗时: ___ 分钟
- [ ] 清理临时目录

#### 用户上传文件
- [ ] 选择最新的用户文件备份
- [ ] 恢复到临时目录
- [ ] 随机验证10个文件可访问性
- [ ] 验证文件完整性（MD5校验）
- [ ] 记录恢复耗时: ___ 分钟
- [ ] 清理临时目录

### 4. 云存储恢复测试

#### AWS S3 / Cloudflare R2
- [ ] 从云端下载最新备份
- [ ] 验证下载速度
- [ ] 验证文件完整性
- [ ] 验证版本控制是否正常
- [ ] 记录下载耗时: ___ 分钟

### 5. 加密备份恢复测试
- [ ] 使用加密密钥解密备份
- [ ] 验证解密后数据完整性
- [ ] 确认密钥管理流程正确
- [ ] 记录解密耗时: ___ 分钟

### 6. 时间点恢复测试（PITR）
- [ ] 选择特定时间点
- [ ] 使用全量备份 + 增量备份恢复
- [ ] 验证数据是否恢复到指定时间点
- [ ] 记录恢复耗时: ___ 分钟

### 7. 灾难恢复演练（季度）
- [ ] 模拟完全数据丢失场景
- [ ] 从零开始恢复整个系统
- [ ] 验证所有服务是否正常
- [ ] 记录总恢复时间: ___ 小时
- [ ] 评估是否满足RTO要求

### 8. 问题记录

| 问题描述 | 严重性 | 解决方案 | 状态 |
|---------|--------|---------|------|
|         |        |         |      |
|         |        |         |      |

### 9. 测试结论

**通过项**: ___ / ___
**失败项**: ___ / ___
**整体评估**: [通过/部分通过/失败]

**改进建议**:
1. 
2. 
3. 

**下次测试日期**: YYYY-MM-DD

**签字**: ________________
```

---

## 成本估算

### 免费方案成本分析

| 项目 | 免费额度 | 实际成本 | 备注 |
|------|---------|---------|------|
| 本地存储 | 无限制 | $0 | 使用服务器硬盘 |
| AWS S3 (12个月) | 5GB | $0 | 新账户首年 |
| Cloudflare R2 | 10GB | $0 | 持续免费 |
| Backblaze B2 | 10GB | $0 | 持续免费 |
| rclone工具 | 开源免费 | $0 | 无限制使用 |
| 加密工具 | OpenSSL/GPG | $0 | 系统内置 |
| **总成本** | - | **$0** | 完全免费 |

### 成长阶段成本预测

| 数据量 | 推荐方案 | 月成本 | 年成本 |
|-------|---------|--------|--------|
| 0-10GB | Cloudflare R2 | $0 | $0 |
| 10-100GB | Cloudflare R2 + B2 | $0-5 | $0-60 |
| 100GB-1TB | AWS S3 Glacier | $4-10 | $48-120 |
| 1TB-10TB | AWS S3 + Glacier | $23-230 | $276-2760 |

---

## 本地备份方案

### 本地存储策略

```bash
# 本地备份存储结构
/var/backups/
├── mysql/
│   ├── full/          # 全量备份
│   ├── incremental/   # 增量备份
│   └── .snapshots/    # 快照文件
├── postgresql/
│   ├── full/
│   ├── wal_archive/   # WAL归档
│   └── .snapshots/
├── mongodb/
├── files/
│   ├── app/
│   ├── uploads/
│   └── config/
└── logs/
    └── backup.log

# 存储策略
本地存储策略:
├── 热存储 (SSD)
│   ├── 最近7天备份
│   └── 快速恢复用
├── 温存储 (HDD)
│   ├── 最近30天备份
│   └── 常规恢复用
└── 冷存储 (外置硬盘/磁带)
    ├── 最近1年备份
    └── 灾难恢复用
```

### 外置硬盘备份（离线备份）

```bash
#!/bin/bash
# external-backup.sh - 外置硬盘离线备份

# ============ 配置区域 ============
EXTERNAL_DRIVE="/mnt/external-drive"  # 外置硬盘挂载点
BACKUP_SOURCE="/var/backups"
BACKUP_DEST="$EXTERNAL_DRIVE/offline-backups"

# ============ 主流程 ============

# 检查外置硬盘是否挂载
if ! mountpoint -q "$EXTERNAL_DRIVE"; then
    echo "External drive not mounted. Please connect and mount the drive."
    exit 1
fi

# 同步备份
rsync -av --delete \
    "$BACKUP_SOURCE/" \
    "$BACKUP_DEST/"

# 验证
rsync -av --dry-run \
    "$BACKUP_SOURCE/" \
    "$BACKUP_DEST/" \
    | grep -c "sending"

# 完成提示
echo "Offline backup completed at $(date)"
echo "You can now safely disconnect the external drive."
```

---

## 迁出成本

- **难度**：低
- **时间**：< 1小时
- **步骤**：
  1. 导出备份配置文件
  2. 迁移rclone配置
  3. 在新服务器安装脚本
  4. 从云端拉取历史备份
  5. 验证恢复流程

---

## 与其他武器配合

- **前置**：
  - [10分钟快速防御清单](./quick-defense-checklist.md)
  - [免费安全技术栈](./free-security-stack.md)
- **后置**：
  - [入侵检测系统](../open-source/intrusion-detection.md)
  - [日志分析平台](../open-source/log-analysis.md)
- **配合**：
  - [密钥管理方案](../free-tier/secrets-management.md)
  - [监控告警方案](../free-tier/monitoring.md)

---

## 常见问题

**Q: 免费额度真的够用吗？**
A: 对于独立开发者：
- 数据库备份通常 < 1GB（压缩后）
- 应用文件通常 < 5GB
- 10GB 云存储足够 3-6 个月备份
- 定期清理可延长使用时间

**Q: 备份频率应该多高？**
A: 建议频率：
- 数据库：每日全量 + 每小时增量（业务关键）
- 文件：每日一次
- 配置：每次变更后
- 云同步：每日一次

**Q: 如何处理敏感数据备份？**
A: 必须加密：
- 使用 AES-256 加密
- 密钥与备份分开存储
- 加密密钥离线备份
- 定期轮换密钥

**Q: 恢复时间目标（RTO）多少合理？**
A: 建议目标：
- 关键数据库：< 1小时
- 应用文件：< 2小时
- 完整系统：< 4小时
- 根据业务容忍度调整

**Q: 如何验证备份没有损坏？**
A: 多层验证：
- 自动：gzip/tar完整性检查
- 定期：恢复测试脚本
- 月度：完整恢复演练
- 季度：灾难恢复演习

**Q: 备份应该保留多久？**
A: 建议策略：
- 本地：30天（快速恢复）
- 云端：90天（常规恢复）
- 归档：1年（合规要求）
- 永久：关键配置快照

---

## 快速检查脚本

```bash
#!/bin/bash
# backup-health-check.sh - 备份健康检查

echo "=== Backup Health Check $(date) ==="

# 1. 检查最新备份时间
echo -e "\n[Latest Backups]"
for dir in /var/backups/*/; do
    latest=$(ls -t "$dir" 2>/dev/null | head -1)
    if [ -n "$latest" ]; then
        echo "$(basename $dir): $latest"
    else
        echo "$(basename $dir): ⚠️  No backups found!"
    fi
done

# 2. 检查备份大小
echo -e "\n[Backup Sizes]"
du -sh /var/backups/*

# 3. 检查磁盘空间
echo -e "\n[Disk Space]"
df -h /var/backups

# 4. 检查云同步状态
echo -e "\n[Cloud Sync Status]"
rclone ls aws-s3:your-backup-bucket | tail -5

# 5. 检查加密密钥
echo -e "\n[Encryption Key]"
if [ -f /root/.backup_key ]; then
    echo "✓ Encryption key exists"
else
    echo "⚠️  Encryption key not found!"
fi

# 6. 检查定时任务
echo -e "\n[Scheduled Tasks]"
crontab -l | grep backup

echo -e "\n=== Check Complete ==="
```

---

## 推荐实现

### 免费方案（本文所述）
- 完全 $0 成本
- 满足独立开发者需求
- 需要手动配置

### 低成本升级

| 方案 | 月成本 | 优势 |
|------|--------|------|
| Backblaze B2 | $6/TB | 无出口流量费 |
| Wasabi | $6.99/TB | 简单定价 |
| IDrive | $3.71/5TB | 包含备份软件 |
| Restic + B2 | $5-10 | 增量去重 |

### 企业级方案

| 方案 | 月成本 | 优势 |
|------|--------|------|
| Veeam | $100+ | 企业级功能 |
| Commvault | $200+ | 合规支持 |
| AWS Backup | 按量付费 | 云原生集成 |
| Azure Backup | 按量付费 | 企业集成 |

---

## 相关资源

### 工具
- [rclone](https://rclone.org/) - 云存储同步工具
- [restic](https://restic.net/) - 现代化备份工具
- [Borg Backup](https://www.borgbackup.org/) - 去重备份
- [Duplicity](http://duplicity.nongnu.org/) - 加密备份

### 学习资源
- [3-2-1 Backup Rule](https://www.backblaze.com/blog/the-3-2-1-backup-strategy/)
- [PostgreSQL PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [MySQL Binary Logs](https://dev.mysql.com/doc/refman/8.0/en/binary-log.html)

### 相关案例
- [数据库恢复案例](../../../cases/indie/core/data/database-recovery.md)
- [勒索软件应对案例](../../../cases/indie/core/data/ransomware-response.md)

---

## 更新记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-06-11 | 1.0 | 初始版本，包含完整备份策略 |
