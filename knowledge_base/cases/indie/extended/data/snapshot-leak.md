# 快照泄露 (Snapshot Leak)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-007 |
| 分类 | 数据安全 / 云安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

云服务器快照或备份包含敏感数据且权限配置不当，导致快照被公开访问或被攻击者获取，造成大规模数据泄露。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **公开访问的快照** - AMI、EBS 快照、RDS 快照设置为公开
- [ ] **快照权限不当** - 快照共享给错误的账户或组织
- [ ] **未加密的快照** - 快照数据未加密且包含敏感信息

### 🔍 典型场景

```
场景 1: AWS AMI 公开泄露
AMI 设置为 public
任何 AWS 用户都可基于该 AMI 启动实例
结果:     AMI 中包含的数据库、配置、用户数据泄露

场景 2: EBS 快照共享错误
快照共享给测试账户而非生产账户
测试账户权限较弱或已被入侵
结果:     快照中的敏感数据被访问

场景 3: RDS 快照未加密
数据库快照包含 PII 数据
快照未启用加密
结果:     符合性违规，数据泄露风险
```

---

## 一句话防御

**实施快照加密、定期审计快照权限、使用 AWS Backup 自动化管理、限制快照公开访问、监控快照创建与共享事件。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **AWS Config** | 配置合规监控 | https://aws.amazon.com/config/ |
| **Prowler** | AWS 安全审计 | https://github.com/toniblyx/prowler |
| **ScoutSuite** | 云安全审计 | https://github.com/nccgroup/ScoutSuite |
| **CloudSploit** | 云安全扫描 | https://cloudsploit.com/ |

---

## 快速缓解措施

### 1. 审计快照权限
```bash
# AWS CLI：列出公开的 EBS 快照
aws ec2 describe-snapshots \
  --owner-ids self \
  --query 'Snapshots[?!contains(Permissions, `private`)]' \
  --output json

# AWS CLI：列出公开的 AMI
aws ec2 describe-images \
  --owners self \
  --query 'Images[?Public==`true`]' \
  --output json
```

### 2. 启用快照加密
```bash
# AWS CLI：创建加密快照
aws ec2 create-snapshot \
  --volume-id vol-12345678 \
  --encrypted \
  --kms-key-id alias/my-key \
  --description "Encrypted snapshot"

# AWS CLI：复制并加密现有快照
aws ec2 copy-snapshot \
  --source-region us-east-1 \
  --source-snapshot-id snap-12345678 \
  --encrypted \
  --kms-key-id alias/my-key
```

### 3. 监控快照事件
```python
# Python + boto3：监控快照公开访问
import boto3
import json

def check_public_snapshots():
    ec2 = boto3.client('ec2')

    # 检查 EBS 快照
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])
    for snap in snapshots['Snapshots']:
        attrs = ec2.describe_snapshot_attribute(
            SnapshotId=snap['SnapshotId'],
            Attribute='createVolumePermission'
        )
        if 'Groups' in attrs and 'all' in attrs['Groups']:
            print(f"PUBLIC SNAPSHOT FOUND: {snap['SnapshotId']}")

        # 检查 AMI
        images = ec2.describe_images(Owners=['self'])
        for img in images['Images']:
            if img['Public']:
                print(f"PUBLIC AMI FOUND: {img['ImageId']}")
```

---

## 相关案例

- [CASE-EXT-DATA-006 配置文件暴露](./config-exposure.md)
- [CASE-EXT-DATA-008 调试端点暴露](./debug-endpoint-exposure.md)

---

## 参考标准

- AWS Well-Architected Framework - Security Pillar
- CIS AWS Foundations Benchmark
- NIST SP 800-53 - SC-28: Protection of Information at Rest
- GDPR Article 32 - Security of Processing
