# S3 存储桶公开访问风险

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
你的 AWS S3/阿里云 OSS 存储桶配置为公开访问，攻击者可以遍历下载桶内所有文件，包括用户上传的身份证照片、合同文档、数据库备份等敏感数据。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用 AWS S3/阿里云 OSS/腾讯云 COS 等云存储
- [ ] 存储用户上传的文件（图片、文档、视频等）
- [ ] **从未检查过存储桶的访问权限设置**
- [ ] **为了方便开发，将存储桶设置为"公开读"**
- [ ] 存储桶 URL 格式为 `https://bucket-name.s3.amazonaws.com/`
- [ ] 使用了"任何人可读"或"公开访问"权限
→ 勾选≥2项，尤其是后两项，**立即行动**

### 一句话防御
在云服务商控制台禁用存储桶的公开访问，配置存储桶策略仅允许特定 IP 或经过认证的用户访问，启用 MFA 删除保护。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查存储桶权限**：
   ```bash
   # AWS S3 检查
   aws s3api get-bucket-acl --bucket your-bucket-name

   # 检查是否公开访问
   aws s3api get-public-access-block --bucket your-bucket-name

   # 列出所有存储桶
   aws s3 ls
   ```

2. [ ] **立即禁用公开访问**：
   ```bash
   # AWS S3 - 启用"阻止公开访问"设置
   aws s3api put-public-access-block \
     --bucket your-bucket-name \
     --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

   # 验证
   aws s3api get-public-access-block --bucket your-bucket-name
   ```

3. [ ] **检查文件是否已被访问**：
   ```bash
   # 启用服务器访问日志（如果没有）
   aws s3api put-bucket-logging \
     --bucket your-bucket-name \
     --bucket-logging-status '{
       "LoggingEnabled": {
         "TargetBucket": "log-bucket-name",
         "TargetPrefix": "s3-access-logs/"
       }
     }'

   # 检查最近的访问日志
   aws s3 ls s3://log-bucket-name/s3-access-logs/ --recursive | tail -20
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **配置存储桶策略**：仅允许特定 IP 或经过认证的用户访问
2. [ ] **启用加密**：启用服务器端加密（SSE-S3 或 SSE-KMS）
3. [ ] **启用版本控制**：防止文件被意外删除或覆盖
4. [ ] **检查已泄露文件**：使用 Google 搜索 `site:s3.amazonaws.com "your-bucket-name"`

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用 CloudFront CDN**：通过 CDN 访问，隐藏存储桶 URL
2. [ ] **启用 MFA 删除**：防止恶意删除文件
3. [ ] **定期安全审计**：每月检查存储桶权限

### 推荐工具
- **免费**：
  - [AWS S3 控制台](https://console.aws.amazon.com/s3/) - 免费，图形化配置
  - [AWS CLI](https://aws.amazon.com/cli/) - 免费，命令行工具
  - [S3 Inspector](https://github.com/kromtech/s3-inspector) - 开源，自动检查 S3 权限

- **低成本**：
  - [Trend Micro Cloud One](https://www.trendmicro.com/cloud-one/) - $50/月起，云存储安全监控
  - [Duo Security](https://duo.com/) - $3/用户/月，MFA 保护

### 验证方法
- [ ] **权限验证**：执行 `aws s3api get-public-access-block`，所有选项应为 `true`
- [ ] **访问测试**：匿名访问 `https://your-bucket-name.s3.amazonaws.com/` 应该返回 `AccessDenied`
- [ ] **文件列表测试**：匿名执行 `aws s3 ls s3://your-bucket-name --no-sign-request` 应该失败
- [ ] **应用验证**：你的应用仍然可以正常上传和下载文件（说明权限配置正确）

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2020年，一个在线教育平台使用 AWS S3 存储用户上传的课程视频和学习资料。为了方便前端直接访问文件，开发者将存储桶设置为"公开读"（Public Read）。

攻击者通过 Google 搜索 `site:s3.amazonaws.com "course-videos"` 发现了该存储桶，使用 AWS CLI 工具遍历下载了整个存储桶，获取了价值 50 万美元的付费课程视频，并在盗版网站免费分享，导致平台用户流失严重。

**类似案例**：
- 2019年，某医疗 App 的 S3 存储桶公开，泄露 150 万用户病历和身份证照片
- 2021年，某企业将数据库备份存储在公开 S3，泄露 1TB 商业机密
- 2022年，某社交平台的用户头像和私信附件存储在公开 S3，被批量下载

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── Google 搜索：site:s3.amazonaws.com "关键词"
   ├── Shodan 搜索：port:443 "AmazonS3"
   ├── 使用工具：S3Scanner、Bucket Finder
   └── 猜测常见桶名：company-name-backups, company-name-uploads

2. 验证可访问性
   ├── 访问 https://bucket-name.s3.amazonaws.com/
   ├── 或使用 AWS CLI（匿名访问）
   │   aws s3 ls s3://bucket-name --no-sign-request
   └── 返回文件列表或 XML 错误信息

3. 遍历文件列表
   ├── aws s3 ls s3://bucket-name --recursive --no-sign-request
   ├── 或访问 https://bucket-name.s3.amazonaws.com/?list-type=2&max-keys=1000
   └── 获取完整的文件列表（文件名、大小、修改时间）

4. 批量下载文件
   ├── aws s3 sync s3://bucket-name ./stolen-data --no-sign-request
   ├── 使用多线程工具加速下载
   └── 整个过程可能 < 1 小时（取决于数据量）

5. 利用数据
   ├── 分析文件内容（数据库备份、身份证照片、合同等）
   ├── 在暗网出售或公开发布
   └── 持续监控新文件（定期同步）
```

**关键点**：
- 攻击者 **无需任何凭据**，仅需知道存储桶名称
- Google 和 Shodan **已经索引了大量公开 S3 桶**
- 批量下载工具使窃取数据 **极其简单快速**
- 存储桶 URL **难以更改**，一旦泄露就永久暴露

### 防御实施（低成本方案）

#### 方案A：免费方案（AWS IAM + 存储桶策略）

**工具/服务**：AWS IAM + S3 Bucket Policy

**配置步骤**：

**第一步：禁用公开访问**
```bash
# 使用 AWS CLI
aws s3api put-public-access-block \
  --bucket your-bucket-name \
  --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'
```

**第二步：配置存储桶策略（仅允许特定 IP 访问）**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificIPOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ],
      "Condition": {
        "NotIpAddress": {
          "aws:SourceIp": [
            "192.0.2.0/24",  // 你的办公室 IP 段
            "203.0.113.0/24"  // 你的应用服务器 IP 段
          ]
        }
      }
    }
  ]
}
```

**第三步：使用预签名 URL（临时访问）**
```javascript
// Node.js 示例：生成临时访问 URL（1 小时有效）
const AWS = require('aws-sdk');
const s3 = new AWS.S3();

app.get('/download/:filename', (req, res) => {
  const params = {
    Bucket: 'your-bucket-name',
    Key: req.params.filename,
    Expires: 3600  // 1 小时
  };

  const url = s3.getSignedUrl('getObject', params);
  res.json({ downloadUrl: url });
});
```

**第四步：启用加密和版本控制**
```bash
# 启用服务器端加密
aws s3api put-bucket-encryption \
  --bucket your-bucket-name \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'

# 启用版本控制
aws s3api put-bucket-versioning \
  --bucket your-bucket-name \
  --versioning-configuration Status=Enabled
```

**局限性**：
- 需要维护 IP 白名单（团队 IP 变化时需手动更新）
- 无法限制单个文件的访问权限
- 预签名 URL 可能被分享（但会过期）

#### 方案B：低成本方案（CloudFront CDN + 签名 URL）

**工具/服务**：AWS CloudFront + Signed URLs

**配置步骤**：

**第一步：创建 CloudFront 分发**
```bash
# 使用 AWS 控制台创建 CloudFront 分发
# 1. 进入 CloudFront 控制台
# 2. 创建分发
# 3. 源：选择你的 S3 存储桶
# 4. 限制存储桶访问：Yes
# 5. 创建新的 Origin Access Identity
# 6. 授予存储桶读取权限：Yes, Update Bucket Policy
# 7. 查看器协议策略：Redirect HTTP to HTTPS
# 8. 限制查看器访问：Yes
# 9. 可信签署者：Self
# 10. 创建分发
```

**第二步：生成 CloudFront 签名 URL**
```javascript
// Node.js 示例：生成 CloudFront 签名 URL
const AWS = require('aws-sdk');
const cloudfront = new AWS.CloudFront.Signer('KEY_PAIR_ID', 'PRIVATE_KEY');

app.get('/download/:filename', (req, res) => {
  const url = `https://d111111abcdef8.cloudfront.net/${req.params.filename}`;

  const signedUrl = cloudfront.getSignedUrl({
    url: url,
    expires: Math.floor(Date.now() / 1000) + 3600  // 1 小时后过期
  });

  res.json({ downloadUrl: signedUrl });
});
```

**第三步：配置存储桶策略（仅允许 CloudFront 访问）**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity YOUR_OAI_ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::your-bucket-name/*"
    }
  ]
}
```

**优势**：
- **隐藏存储桶 URL**：用户只能看到 CloudFront URL
- **CDN 加速**：文件下载速度更快
- **细粒度控制**：每个文件可以单独设置访问权限
- **防盗链**：可以设置 Referer 白名单
- **成本较低**：CloudFront 流量费用 $0.085/GB（比 S3 略贵）

**成本对比**：

| 指标 | 方案A (IAM+策略) | 方案B (CloudFront) |
|------|-----------------|-------------------|
| 月成本 | $0 | $5-20/月 |
| 访问控制 | IP 白名单 | 签名 URL（更灵活） |
| 下载速度 | 直连 S3 | CDN 加速 |
| URL 安全 | 暴露 S3 URL | 隐藏 S3 URL |
| 维护成本 | 中（维护 IP） | 低（自动管理） |
| 适用场景 | 内部使用 | 公开访问文件 |

### 决策树

```
你的产品如何使用存储桶？
├── 仅内部使用（如备份、日志）
│   └── 方案A（禁用公开访问 + IP 白名单）
│
├── 用户上传但不公开访问
│   ├── 使用预签名 URL → 方案A（预签名 URL）
│   └── 需要长期访问权限 → 方案A（IAM 用户）
│
└── 用户上传且公开访问（如头像、图片）
    ├── 需要防盗链 → 方案B（CloudFront）
    └── 不需要防盗链 → 方案A（选择部分文件公开）
```

### 代码示例

#### 完整的 S3 安全配置脚本

```bash
#!/bin/bash
# s3-security-setup.sh
# 用途：一键配置 AWS S3 存储桶安全措施
# 适用：独立开发者、小团队

set -e

echo "=== S3 存储桶安全配置脚本 ==="

# 配置参数
BUCKET_NAME="${BUCKET_NAME:-my-app-uploads}"
REGION="${REGION:-us-east-1}"
ALLOWED_IPS="${ALLOWED_IPS:-}"  # IP 白名单，逗号分隔

# 检查存储桶是否存在
echo "步骤 1/6: 检查存储桶..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
  echo "✓ 存储桶存在: $BUCKET_NAME"
else
  echo "✗ 存储桶不存在，正在创建..."
  aws s3 mb s3://$BUCKET_NAME --region $REGION
  echo "✓ 存储桶已创建: $BUCKET_NAME"
fi

# 禁用公开访问
echo "步骤 2/6: 禁用公开访问..."
aws s3api put-public-access-block \
  --bucket "$BUCKET_NAME" \
  --public-access-block-configuration '{
    "BlockPublicAcls": true,
    "IgnorePublicAcls": true,
    "BlockPublicPolicy": true,
    "RestrictPublicBuckets": true
  }'
echo "✓ 公开访问已禁用"

# 启用加密
echo "步骤 3/6: 启用服务器端加密..."
aws s3api put-bucket-encryption \
  --bucket "$BUCKET_NAME" \
  --server-side-encryption-configuration '{
    "Rules": [
      {
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "AES256"
        }
      }
    ]
  }'
echo "✓ 服务器端加密已启用"

# 启用版本控制
echo "步骤 4/6: 启用版本控制..."
aws s3api put-bucket-versioning \
  --bucket "$BUCKET_NAME" \
  --versioning-configuration Status=Enabled
echo "✓ 版本控制已启用"

# 配置存储桶策略
echo "步骤 5/6: 配置存储桶策略..."
if [ -n "$ALLOWED_IPS" ]; then
  # 如果提供了 IP 白名单，创建 IP 限制策略
  IFS=',' read -ra IP_ARRAY <<< "$ALLOWED_IPS"
  IP_LIST=$(printf '"%s",' "${IP_ARRAY[@]}" | sed 's/,$//')

  cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowSpecificIPOnly",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME",
        "arn:aws:s3:::$BUCKET_NAME/*"
      ],
      "Condition": {
        "NotIpAddress": {
          "aws:SourceIp": [$IP_LIST]
        }
      }
    }
  ]
}
EOF

  aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file:///tmp/bucket-policy.json
  echo "✓ 存储桶策略已配置（IP 白名单）"
else
  echo "⚠️  未提供 IP 白名单，跳过存储桶策略配置"
fi

# 启用访问日志
echo "步骤 6/6: 启用访问日志..."
LOG_BUCKET="${BUCKET_NAME}-logs"

# 创建日志存储桶
if ! aws s3api head-bucket --bucket "$LOG_BUCKET" 2>/dev/null; then
  aws s3 mb s3://$LOG_BUCKET --region $REGION
  echo "✓ 日志存储桶已创建: $LOG_BUCKET"
fi

# 配置访问日志
aws s3api put-bucket-logging \
  --bucket "$BUCKET_NAME" \
  --bucket-logging-status "{
    \"LoggingEnabled\": {
      \"TargetBucket\": \"$LOG_BUCKET\",
      \"TargetPrefix\": \"s3-access-logs/\"
    }
  }"
echo "✓ 访问日志已启用"

echo ""
echo "=== 配置完成 ==="
echo "存储桶名称: $BUCKET_NAME"
echo "公开访问: 已禁用"
echo "加密: 已启用（AES-256）"
echo "版本控制: 已启用"
echo "访问日志: s3://$LOG_BUCKET/s3-access-logs/"
echo ""
echo "后续步骤："
echo "1. 测试上传文件："
echo "   echo 'test' > test.txt"
echo "   aws s3 cp test.txt s3://$BUCKET_NAME/"
echo "2. 测试匿名访问（应该失败）："
echo "   aws s3 ls s3://$BUCKET_NAME --no-sign-request"
echo "3. 定期检查访问日志，确认无异常访问"
```

#### 应用代码示例（Node.js）

```javascript
// lib/s3-manager.js
// 安全的 S3 存储管理器

const AWS = require('aws-sdk');
const s3 = new AWS.S3();

class S3Manager {
  constructor(bucketName) {
    this.bucketName = bucketName;
  }

  // 上传文件（私有）
  async uploadPrivateFile(key, body, contentType) {
    const params = {
      Bucket: this.bucketName,
      Key: key,
      Body: body,
      ContentType: contentType,
      ACL: 'private'  // 明确设置为私有
    };

    const result = await s3.upload(params).promise();
    console.log(`✓ 文件已上传（私有）: ${result.Key}`);
    return result;
  }

  // 生成预签名 URL（临时访问）
  async getSignedUrl(key, expiresIn = 3600) {
    const params = {
      Bucket: this.bucketName,
      Key: key,
      Expires: expiresIn
    };

    const url = s3.getSignedUrl('getObject', params);
    console.log(`✓ 预签名 URL 已生成（${expiresIn}秒有效）: ${url}`);
    return url;
  }

  // 生成上传预签名 URL（允许用户直接上传）
  async getUploadSignedUrl(key, contentType, expiresIn = 3600) {
    const params = {
      Bucket: this.bucketName,
      Key: key,
      ContentType: contentType,
      Expires: expiresIn
    };

    const url = s3.getSignedUrl('putObject', params);
    console.log(`✓ 上传预签名 URL 已生成: ${url}`);
    return url;
  }

  // 列出文件（需要认证）
  async listFiles(prefix = '') {
    const params = {
      Bucket: this.bucketName,
      Prefix: prefix
    };

    const data = await s3.listObjectsV2(params).promise();
    return data.Contents.map(item => ({
      key: item.Key,
      size: item.Size,
      lastModified: item.LastModified
    }));
  }

  // 删除文件（需要认证）
  async deleteFile(key) {
    const params = {
      Bucket: this.bucketName,
      Key: key
    };

    await s3.deleteObject(params).promise();
    console.log(`✓ 文件已删除: ${key}`);
  }

  // 检查文件是否存在
  async fileExists(key) {
    try {
      await s3.headObject({ Bucket: this.bucketName, Key: key }).promise();
      return true;
    } catch (error) {
      if (error.code === 'NotFound') {
        return false;
      }
      throw error;
    }
  }
}

module.exports = S3Manager;

// 使用示例
const s3Manager = new S3Manager('my-app-uploads');

// 上传文件（私有）
await s3Manager.uploadPrivateFile('user-123/avatar.jpg', fileBuffer, 'image/jpeg');

// 生成临时访问 URL（1 小时有效）
const downloadUrl = await s3Manager.getSignedUrl('user-123/avatar.jpg', 3600);

// 允许用户直接上传（前端）
const uploadUrl = await s3Manager.getUploadSignedUrl('user-123/avatar.jpg', 'image/jpeg', 3600);
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业云存储安全最佳实践](../../enterprise/infosec/cloud-storage-security-enterprise.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 合规要求 | 基础保护 | SOC2/ISO27001/PCI-DSS |
| 访问控制 | IP 白名单 | RBAC + 属性基访问控制（ABAC） |
| 加密 | 服务器端加密 | 客户端加密 + KMS 密钥管理 |
| 监控 | 访问日志 | Macie（敏感数据检测）+ GuardDuty（威胁检测） |
| 防护 | 无 | WAF + Shield（防 DDoS） |
| 审计 | 手动检查 | Config Rules + 自动合规检查 |

---

## 附录：常见问题

**Q: 我使用的是阿里云 OSS/腾讯云 COS，也需要担心吗？**

A: 需要，所有云存储服务都有类似的公开访问风险。请检查：
- 阿里云 OSS：在 Bucket 设置中检查"读写权限"，应该是"私有"
- 腾讯云 COS：在存储桶列表中检查"公有读私有写"，应该是"私有读写"

**Q: 用户上传的头像图片需要公开访问，怎么处理？**

A: 推荐方案：
1. 使用 CloudFront CDN + 签名 URL（方案B）
2. 或生成缩略图公开访问，原图保持私有
3. 或使用专门的图片处理服务（如 Imgix、Cloudinary）

**Q: 存储桶已经有公开访问的文件，怎么办？**

A: 立即执行：
1. 禁用存储桶公开访问（防止新文件公开）
2. 检查已公开文件是否包含敏感信息
3. 如果包含敏感信息，立即修改文件权限为私有
4. 使用 Google Search Console 请求删除 Google 索引

**Q: 如何检查存储桶是否已被 Google 索引？**

A: 在 Google 搜索：
```
site:s3.amazonaws.com "your-bucket-name"
site:s3.amazonaws.com "关键词"
```
如果发现已被索引，使用 Google Search Console 请求删除。

---

## 参考资源

- [AWS S3 Security Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [Amazon S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [S3 Inspector Tool](https://github.com/kromtech/s3-inspector)
- [AWS CloudFront Signed URLs](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-signed-urls.html)
