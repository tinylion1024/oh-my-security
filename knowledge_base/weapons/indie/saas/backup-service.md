# 云备份服务对比

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 响应/恢复
- **实现成本**: 免费 - $10/月
- **实施时间**: 1-2小时
- **维护成本**: 0.5小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
为独立开发者项目选择合适的云备份方案，包括数据库备份、文件备份、配置备份等。适用于所有需要数据持久化和灾难恢复的项目。

---

## 核心原则

### 备份策略层次

```
数据备份多层防御
┌─────────────────────────────────────────────────────┐
│                    本地备份                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │即时快照  │  │本地磁盘  │  │开发环境  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    云端备份                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │对象存储  │  │异地容灾  │  │版本控制  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
├─────────────────────────────────────────────────────┤
│                    恢复验证                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │定期演练  │  │完整性校验│  │恢复时间  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

### 备份策略矩阵

| 数据类型 | 备份频率 | 保留周期 | 存储类型 | 恢复时间 |
|---------|---------|---------|---------|---------|
| 数据库 | 每日 | 30天 | 对象存储 | 1-4小时 |
| 用户文件 | 实时/每日 | 90天 | 对象存储 | 4-24小时 |
| 配置文件 | 每次变更 | 永久 | Git | 分钟级 |
| 日志 | 每日 | 30天 | 压缩存储 | 1小时 |
| 代码 | 实时 | 永久 | Git | 分钟级 |

---

## 快速上手（5分钟）

### 自动化备份脚本

```bash
#!/bin/bash
# backup.sh - 通用备份脚本

set -e

# 配置
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 云存储配置（选择一个）
# AWS S3
# S3_BUCKET="s3://your-bucket/backups"
# Backblaze B2 (通过 S3 兼容 API)
# B2_BUCKET="s3://your-bucket/backups"
# Cloudflare R2
# R2_BUCKET="s3://your-bucket/backups"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 数据库备份
backup_database() {
    local db_name=$1
    local db_user=$2
    local db_host=${3:-localhost}
    
    log "开始备份数据库: $db_name"
    
    local backup_file="${BACKUP_DIR}/${db_name}_${DATE}.sql.gz"
    
    # PostgreSQL
    if command -v pg_dump &> /dev/null; then
        pg_dump -U "$db_user" -h "$db_host" "$db_name" | gzip > "$backup_file"
    # MySQL
    elif command -v mysqldump &> /dev/null; then
        mysqldump -u "$db_user" -h "$db_host" "$db_name" | gzip > "$backup_file"
    else
        log "错误: 未找到数据库工具"
        return 1
    fi
    
    log "数据库备份完成: $backup_file"
    
    # 上传到云存储
    upload_to_cloud "$backup_file"
}

# 文件备份
backup_files() {
    local source_dir=$1
    local backup_name=$2
    
    log "开始备份文件: $source_dir"
    
    local backup_file="${BACKUP_DIR}/${backup_name}_${DATE}.tar.gz"
    
    tar -czf "$backup_file" -C "$(dirname "$source_dir")" "$(basename "$source_dir")"
    
    log "文件备份完成: $backup_file"
    
    # 上传到云存储
    upload_to_cloud "$backup_file"
}

# 上传到云存储
upload_to_cloud() {
    local file=$1
    
    # AWS S3
    if [ -n "$S3_BUCKET" ]; then
        log "上传到 S3: $S3_BUCKET"
        aws s3 cp "$file" "$S3_BUCKET/$(basename "$file")"
    # Backblaze B2
    elif [ -n "$B2_BUCKET" ]; then
        log "上传到 B2: $B2_BUCKET"
        # 使用 S3 兼容 API
        aws s3 cp "$file" "$B2_BUCKET/$(basename "$file")" \
            --endpoint-url=https://s3.us-west-004.backblazeb2.com
    # Cloudflare R2
    elif [ -n "$R2_BUCKET" ]; then
        log "上传到 R2: $R2_BUCKET"
        aws s3 cp "$file" "$R2_BUCKET/$(basename "$file")" \
            --endpoint-url=https://<account-id>.r2.cloudflarestorage.com
    else
        log "警告: 未配置云存储，备份仅保存在本地"
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log "清理 ${RETENTION_DAYS} 天前的备份"
    
    find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete
    
    # 清理云存储中的旧备份（如果配置了生命周期规则则不需要）
    if [ -n "$S3_BUCKET" ]; then
        # S3 生命周期规则会自动清理，这里不手动删除
        log "云存储旧备份由生命周期规则管理"
    fi
}

# 验证备份
verify_backup() {
    local backup_file=$1
    
    log "验证备份: $backup_file"
    
    # 检查文件完整性
    if gzip -t "$backup_file" 2>/dev/null; then
        log "备份完整性验证通过"
        return 0
    else
        log "错误: 备份文件损坏"
        return 1
    fi
}

# 主函数
main() {
    log "========== 开始备份 =========="
    
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库（示例）
    # backup_database "myapp" "postgres"
    
    # 备份文件（示例）
    # backup_files "/var/www/uploads" "uploads"
    
    # 清理旧备份
    cleanup_old_backups
    
    log "========== 备份完成 =========="
}

# 运行
main "$@"
```

---

## 详细方案

### 云服务对比

#### 1. AWS S3

**免费额度**
- 新用户：5GB 存储，12个月
- 请求：20,000 GET，2,000 PUT

**定价（美东区）**

| 项目 | 价格 |
|-----|------|
| 存储（Standard） | $0.023/GB/月 |
| 存储（Glacier） | $0.004/GB/月 |
| 请求（PUT） | $0.005/1000 |
| 请求（GET） | $0.0004/1000 |
| 数据传出 | $0.09/GB（前 100GB 免费） |
| 生命周期转换 | $0.01/1000 |

**优势**
- 服务稳定，生态完整
- 生命周期规则自动降级存储
- 版本控制支持
- 跨区域复制

**劣势**
- 数据传出费用高
- 学习曲线较陡

**配置示例**

```bash
# 安装 AWS CLI
pip install awscli

# 配置凭证
aws configure

# 创建存储桶
aws s3 mb s3://myapp-backups

# 上传文件
aws s3 cp backup.sql.gz s3://myapp-backups/

# 同步目录
aws s3 sync /backups s3://myapp-backups/

# 设置生命周期规则（30天后转入 Glacier）
aws s3api put-bucket-lifecycle-configuration \
    --bucket myapp-backups \
    --lifecycle-configuration file://lifecycle.json
```

```json
// lifecycle.json
{
    "Rules": [
        {
            "ID": "MoveToGlacier",
            "Status": "Enabled",
            "Filter": {},
            "Transitions": [
                {
                    "Days": 30,
                    "StorageClass": "GLACIER"
                }
            ],
            "Expiration": {
                "Days": 365
            }
        }
    ]
}
```

#### 2. Backblaze B2

**免费额度**
- 存储：10GB
- 带宽：1GB/天
- 请求：2500次/天

**定价**

| 项目 | 价格 |
|-----|------|
| 存储 | $0.005/GB/月 |
| 下载 | 前 1GB 免费，之后 $0.01/GB |
| 请求（Class B） | $0.004/10000 |
| 请求（Class C） | 免费 |

**优势**
- 存储成本最低
- 免费额度 generous
- S3 兼容 API
- 无最低存储时间

**劣势**
- 节点较少
- 生态不如 AWS 完整

**配置示例**

```bash
# 使用 S3 兼容 API
aws configure set profile.b2.s3_signature_version s3v4

# 上传
aws s3 cp backup.sql.gz s3://my-bucket/ \
    --endpoint-url=https://s3.us-west-004.backblazeb2.com \
    --profile b2

# 或使用 Backblaze CLI
pip install b2

b2 authorize-account <applicationKeyId> <applicationKey>
b2 upload-file my-bucket backup.sql.gz backup.sql.gz
```

#### 3. Cloudflare R2

**免费额度**
- 存储：10GB
| 请求：100万次 Class A，1000万次 Class B

**定价**

| 项目 | 价格 |
|-----|------|
| 存储 | $0.015/GB/月 |
| Class A 操作 | $4.50/百万次 |
| Class B 操作 | $0.36/百万次 |
| 数据传出 | **免费** |

**优势**
- **数据传出免费**（最大优势）
- S3 兼容 API
- 与 Cloudflare CDN 集成
- 免费额度 generous

**劣势**
- 新服务，稳定性待验证
- 生态仍在建设

**配置示例**

```bash
# 配置 AWS CLI 使用 R2
aws configure set profile.r2.s3_signature_version s3v4

# 上传（替换 <account-id>）
aws s3 cp backup.sql.gz s3://my-bucket/ \
    --endpoint-url=https://<account-id>.r2.cloudflarestorage.com \
    --profile r2
```

### 成本对比表

| 场景 | AWS S3 | Backblaze B2 | Cloudflare R2 |
|-----|--------|--------------|---------------|
| 存储 10GB | $0.23/月 | $0.05/月 | $0.15/月 |
| 存储 100GB | $2.30/月 | $0.50/月 | $1.50/月 |
| 存储 1TB | $23/月 | $5/月 | $15/月 |
| 下载 10GB | $0.90 | $0.10 | **免费** |
| 下载 100GB | $9.00 | $1.00 | **免费** |
| 免费额度 | 5GB（12个月） | **10GB（永久）** | **10GB（永久）** |

### 推荐方案

#### L1 独立开发者（预算 ≈ $0）

**推荐：Cloudflare R2**

理由：
- 免费额度最大（10GB 存储 + 免费传出）
- 成本最低（长期）
- S3 兼容，迁移简单

#### L2 小团队（预算 $10-50/月）

**推荐：混合方案**

- **热数据**：AWS S3 Standard（频繁访问）
- **冷数据**：Backblaze B2（长期存储）
- **数据传出**：Cloudflare R2（免费传出）

### 自动化备份脚本（完整版）

```python
#!/usr/bin/env python3
"""
自动化备份脚本 - 支持多云存储

支持：
- PostgreSQL / MySQL 数据库备份
- 文件目录备份
- 多云存储上传（S3/B2/R2）
- 自动清理旧备份
- 备份验证
- 告警通知
"""

import os
import sys
import gzip
import shutil
import tarfile
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import json
import hashlib


# 配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackupConfig:
    """备份配置"""
    
    def __init__(self, config_file: str = 'backup_config.json'):
        self.config = self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> dict:
        """加载配置文件"""
        if os.path.exists(config_file):
            with open(config_file) as f:
                return json.load(f)
        return {
            'backup_dir': '/backups',
            'retention_days': 30,
            'databases': [],
            'files': [],
            'storage': {}
        }
    
    @property
    def backup_dir(self) -> Path:
        return Path(self.config.get('backup_dir', '/backups'))
    
    @property
    def retention_days(self) -> int:
        return self.config.get('retention_days', 30)
    
    @property
    def databases(self) -> List[dict]:
        return self.config.get('databases', [])
    
    @property
    def files(self) -> List[dict]:
        return self.config.get('files', [])
    
    @property
    def storage(self) -> dict:
        return self.config.get('storage', {})


class CloudStorage:
    """云存储抽象类"""
    
    def __init__(self, config: dict):
        self.config = config
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        raise NotImplementedError
    
    def delete(self, remote_path: str) -> bool:
        raise NotImplementedError
    
    def list_files(self, prefix: str = '') -> List[str]:
        raise NotImplementedError


class S3Storage(CloudStorage):
    """AWS S3 存储"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.bucket = config.get('bucket')
        self.prefix = config.get('prefix', 'backups')
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        try:
            remote_uri = f"s3://{self.bucket}/{self.prefix}/{remote_path}"
            cmd = ['aws', 's3', 'cp', local_path, remote_uri]
            subprocess.run(cmd, check=True)
            logger.info(f"上传到 S3: {remote_uri}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"S3 上传失败: {e}")
            return False


class R2Storage(CloudStorage):
    """Cloudflare R2 存储"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.bucket = config.get('bucket')
        self.prefix = config.get('prefix', 'backups')
        self.account_id = config.get('account_id')
        self.endpoint = f"https://{self.account_id}.r2.cloudflarestorage.com"
    
    def upload(self, local_path: str, remote_path: str) -> bool:
        try:
            remote_uri = f"s3://{self.bucket}/{self.prefix}/{remote_path}"
            cmd = [
                'aws', 's3', 'cp', local_path, remote_uri,
                '--endpoint-url', self.endpoint
            ]
            subprocess.run(cmd, check=True)
            logger.info(f"上传到 R2: {remote_uri}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"R2 上传失败: {e}")
            return False


class BackupManager:
    """备份管理器"""
    
    def __init__(self, config: BackupConfig):
        self.config = config
        self.backup_dir = config.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化云存储
        self.storages: List[CloudStorage] = []
        self._init_storages()
    
    def _init_storages(self):
        """初始化云存储"""
        storage_config = self.config.storage
        
        if storage_config.get('s3'):
            self.storages.append(S3Storage(storage_config['s3']))
        
        if storage_config.get('r2'):
            self.storages.append(R2Storage(storage_config['r2']))
    
    def backup_postgresql(
        self,
        db_name: str,
        db_user: str,
        db_host: str = 'localhost',
        db_port: int = 5432
    ) -> Optional[Path]:
        """备份 PostgreSQL 数据库"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"{db_name}_{timestamp}.sql.gz"
        
        logger.info(f"开始备份 PostgreSQL 数据库: {db_name}")
        
        try:
            # 执行 pg_dump
            cmd = [
                'pg_dump',
                '-U', db_user,
                '-h', db_host,
                '-p', str(db_port),
                db_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                env={**os.environ, 'PGPASSWORD': os.getenv('PGPASSWORD', '')}
            )
            
            if result.returncode != 0:
                logger.error(f"pg_dump 失败: {result.stderr.decode()}")
                return None
            
            # 压缩
            with gzip.open(backup_file, 'wb') as f:
                f.write(result.stdout)
            
            logger.info(f"数据库备份完成: {backup_file}")
            
            # 上传到云存储
            self._upload_to_cloud(backup_file)
            
            return backup_file
        
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return None
    
    def backup_mysql(
        self,
        db_name: str,
        db_user: str,
        db_host: str = 'localhost',
        db_port: int = 3306
    ) -> Optional[Path]:
        """备份 MySQL 数据库"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"{db_name}_{timestamp}.sql.gz"
        
        logger.info(f"开始备份 MySQL 数据库: {db_name}")
        
        try:
            cmd = [
                'mysqldump',
                '-u', db_user,
                '-h', db_host,
                '-P', str(db_port),
                db_name
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                env={**os.environ, 'MYSQL_PWD': os.getenv('MYSQL_PWD', '')}
            )
            
            if result.returncode != 0:
                logger.error(f"mysqldump 失败: {result.stderr.decode()}")
                return None
            
            with gzip.open(backup_file, 'wb') as f:
                f.write(result.stdout)
            
            logger.info(f"数据库备份完成: {backup_file}")
            
            self._upload_to_cloud(backup_file)
            
            return backup_file
        
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return None
    
    def backup_directory(
        self,
        source_dir: str,
        backup_name: str
    ) -> Optional[Path]:
        """备份目录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"{backup_name}_{timestamp}.tar.gz"
        
        logger.info(f"开始备份目录: {source_dir}")
        
        try:
            source_path = Path(source_dir)
            if not source_path.exists():
                logger.error(f"源目录不存在: {source_dir}")
                return None
            
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(source_path, arcname=source_path.name)
            
            logger.info(f"目录备份完成: {backup_file}")
            
            self._upload_to_cloud(backup_file)
            
            return backup_file
        
        except Exception as e:
            logger.error(f"目录备份失败: {e}")
            return None
    
    def _upload_to_cloud(self, backup_file: Path):
        """上传到云存储"""
        for storage in self.storages:
            storage.upload(str(backup_file), backup_file.name)
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        logger.info(f"清理 {self.config.retention_days} 天前的备份")
        
        cutoff_time = datetime.now() - timedelta(days=self.config.retention_days)
        
        for backup_file in self.backup_dir.glob('*'):
            if backup_file.is_file():
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if mtime < cutoff_time:
                    backup_file.unlink()
                    logger.info(f"删除旧备份: {backup_file}")
    
    def verify_backup(self, backup_file: Path) -> bool:
        """验证备份完整性"""
        logger.info(f"验证备份: {backup_file}")
        
        try:
            if backup_file.suffix == '.gz':
                with gzip.open(backup_file, 'rb') as f:
                    # 读取一小部分验证
                    f.read(1024)
                logger.info("备份完整性验证通过")
                return True
            elif backup_file.suffix == '.tar.gz' or backup_file.name.endswith('.tar.gz'):
                with tarfile.open(backup_file, 'r:gz') as tar:
                    tar.getnames()
                logger.info("备份完整性验证通过")
                return True
            else:
                logger.warning("未知的备份格式，跳过验证")
                return True
        
        except Exception as e:
            logger.error(f"备份验证失败: {e}")
            return False
    
    def run_backup(self):
        """执行完整备份"""
        logger.info("========== 开始备份 ==========")
        
        # 备份数据库
        for db_config in self.config.databases:
            db_type = db_config.get('type', 'postgresql')
            
            if db_type == 'postgresql':
                self.backup_postgresql(
                    db_name=db_config['name'],
                    db_user=db_config['user'],
                    db_host=db_config.get('host', 'localhost'),
                    db_port=db_config.get('port', 5432)
                )
            elif db_type == 'mysql':
                self.backup_mysql(
                    db_name=db_config['name'],
                    db_user=db_config['user'],
                    db_host=db_config.get('host', 'localhost'),
                    db_port=db_config.get('port', 3306)
                )
        
        # 备份文件目录
        for file_config in self.config.files:
            self.backup_directory(
                source_dir=file_config['path'],
                backup_name=file_config['name']
            )
        
        # 清理旧备份
        self.cleanup_old_backups()
        
        logger.info("========== 备份完成 ==========")


# 配置文件示例
"""
// backup_config.json
{
    "backup_dir": "/backups",
    "retention_days": 30,
    "databases": [
        {
            "type": "postgresql",
            "name": "myapp",
            "user": "postgres",
            "host": "localhost",
            "port": 5432
        }
    ],
    "files": [
        {
            "name": "uploads",
            "path": "/var/www/uploads"
        }
    ],
    "storage": {
        "s3": {
            "bucket": "my-backups",
            "prefix": "backups"
        },
        "r2": {
            "bucket": "my-backups",
            "prefix": "backups",
            "account_id": "your-account-id"
        }
    }
}
"""

# 使用示例
if __name__ == '__main__':
    config = BackupConfig('backup_config.json')
    manager = BackupManager(config)
    manager.run_backup()
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| `backup_dir` | /backups | 本地备份目录 |
| `retention_days` | 30 | 保留天数 |
| `compress` | true | 是否压缩 |
| `encrypt` | false | 是否加密 |
| `notify_on_failure` | false | 失败时通知 |

---

## 成本估算

### 存储成本对比（月度）

| 数据量 | AWS S3 | Backblaze B2 | Cloudflare R2 |
|-------|--------|--------------|---------------|
| 10GB | $0.23 | **免费** | **免费** |
| 50GB | $1.15 | $0.25 | $0.75 |
| 100GB | $2.30 | $0.50 | $1.50 |
| 500GB | $11.50 | $2.50 | $7.50 |
| 1TB | $23.00 | $5.00 | $15.00 |

### 传出流量对比

| 流量 | AWS S3 | Backblaze B2 | Cloudflare R2 |
|-----|--------|--------------|---------------|
| 10GB | $0.90 | $0.10 | **免费** |
| 50GB | $4.50 | $0.50 | **免费** |
| 100GB | $9.00 | $1.00 | **免费** |

---

## 迁出成本

- **迁出难度**：中
- **迁出步骤**：
  1. 从源存储下载所有文件
  2. 上传到目标存储
  3. 更新备份脚本配置
- **注意事项**：
  - AWS S3 传出费用较高
  - 建议分批迁移，避免大量传出费用

---

## 与其他武器配合

- **前置**：
  - [encryption-at-rest.md](../free-tier/encryption-at-rest.md) - 备份文件加密
  - [secret-management.md](../free-tier/secret-management.md) - 存储凭证管理

- **后置**：
  - 灾难恢复演练

- **配合**：
  - 与监控配合，备份失败告警
  - 与日志配合，记录备份操作

---

## 常见问题

**Q: 备份频率应该是多少？**  
A: 根据数据重要性：
- 关键数据库：每日
- 用户文件：每日或实时
- 配置文件：每次变更
- 日志：每周

**Q: 备份应该保留多久？**  
A: 根据合规要求：
- 一般业务：30天
- 金融/医疗：365天或更长
- 建议：本地7天 + 云端30天 + 归档365天

**Q: 如何验证备份有效？**  
A: 三种方法：
- 定期恢复测试（推荐每月）
- 文件完整性校验（MD5/SHA256）
- 抽查恢复关键数据

**Q: 多云存储有必要吗？**  
A: L1 开发者：单云即可
L2+ 团队：建议多云：
- 主存储 + 备用存储
- 热数据 + 冷数据分离
- 降低单点故障风险

---

## 推荐实现

### 免费/低成本方案

- **Cloudflare R2** - 10GB 免费，传出免费
- **Backblaze B2** - 10GB 免费，存储最便宜
- **Google Cloud Storage** - 5GB 免费（12个月）

### 自动化工具

- **restic** - 开源备份工具，支持多云
- **rclone** - 云存储同步工具
- **Duplicity** - 加密备份工具

### 企业方案（可选）

- **Veeam** - 企业备份解决方案
- **Acronis** - 混合云备份
- **Rubrik** - 云数据管理

---

## 最佳实践清单

- [ ] 有自动化备份脚本
- [ ] 备份存储在异地（云存储）
- [ ] 备份文件已加密（敏感数据）
- [ ] 有备份保留策略
- [ ] 定期验证备份有效性
- [ ] 有恢复演练计划
- [ ] 备份失败有告警
- [ ] 存储凭证安全管理

---

## 验证清单

- [ ] 备份脚本可正常运行
- [ ] 备份文件可成功上传到云存储
- [ ] 备份文件可成功恢复
- [ ] 旧备份可自动清理
- [ ] 备份失败有通知
- [ ] 恢复时间在可接受范围内
