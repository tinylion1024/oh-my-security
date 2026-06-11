# 文件上传攻击

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $0-30/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户上传了一个"图片"，实际是 PHP WebShell，访问这个文件就获得服务器控制权，攻击者可以读取数据库密码、发送垃圾邮件、甚至勒索你的用户。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 允许用户上传文件（头像、附件、文档）
- [ ] 上传文件名未重命名
- [ ] 上传目录可执行脚本（如 PHP、JSP）
- [ ] 文件类型仅依赖扩展名判断
- [ ] 上传文件可被直接访问（URL 可访问）
→ 勾选≥1项，即需关注此风险

### 一句话防御
三层防护：类型验证（必须）+ 安全存储（必须）+ 访问控制（推荐），1小时内可实施基础防护。

### 快速行动清单
1. [ ] **立即行动项（今天可完成，免费）**：
   - 检查上传目录是否可执行脚本，禁止执行权限
   - 为上传文件生成随机文件名，不使用用户提供的文件名
   - 添加文件类型白名单验证（扩展名 + MIME 类型）

2. [ ] **短期行动项（本周可完成，免费）**：
   - 实现文件内容检测（Magic Number）
   - 将上传目录移到 Web 根目录外
   - 添加文件大小限制

3. [ ] **长期行动项（规划中，低成本）**：
   - 接入云存储服务（S3、OSS）
   - 实现病毒扫描
   - 建立上传审计日志

### 推荐工具
- **免费**：
  - Multer (Node.js) - [GitHub](https://github.com/expressjs/multer) - 文件上传中间件
  - filetype.py - [GitHub](https://github.com/h2non/filetype.py) - Python 文件类型检测

- **低成本**：
  - AWS S3 - $0.023/GB/月 - 安全对象存储
  - Cloudinary - $89/月起 - 图片处理 + 安全上传
  - ClamAV - 开源病毒扫描

### 验证方法
- [ ] 上传合法文件，验证功能正常
- [ ] 上传恶意文件（如 .php），验证被拒绝
- [ ] 上传伪装文件（如 .jpg 实际是 .exe），验证内容检测生效
- [ ] 访问上传的文件，验证无执行权限

---

## L2 小团队版（理解版）

### 场景还原
某独立开发者允许用户上传头像，文件保存在 `/uploads/avatars/` 目录。攻击者上传了一个名为 `avatar.php` 的 WebShell 文件：

```php
<?php system($_GET['cmd']); ?>
```

访问 `https://example.com/uploads/avatars/avatar.php?cmd=cat /etc/passwd` 就能读取服务器文件，攻击者进一步读取了数据库配置文件，获取了数据库密码，导出了所有用户数据。

### 攻击路径（3-5步）
1. **构造恶意文件**：攻击者创建包含恶意代码的文件（WebShell、病毒、钓鱼页面）
2. **绕过验证**：通过修改扩展名、Content-Type、添加图片头等方式绕过验证
3. **上传文件**：将恶意文件上传到服务器
4. **访问执行**：直接访问上传的文件，触发代码执行
5. **控制服务器**：通过 WebShell 执行任意命令，获取服务器控制权

### 防御实施（低成本方案）

#### 方案A：免费方案（本地安全存储）

**工具/服务**：文件验证 + 安全存储配置

**配置步骤**：

1. **文件类型验证（多层）**
```javascript
// Node.js 文件上传验证
const multer = require('multer');
const path = require('path');
const fs = require('fs');

// 允许的文件类型
const ALLOWED_TYPES = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/gif': ['.gif'],
  'application/pdf': ['.pdf'],
};

// Magic Number 验证
const FILE_SIGNATURES = {
  'image/jpeg': [Buffer.from([0xFF, 0xD8, 0xFF])],
  'image/png': [Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])],
  'image/gif': [Buffer.from([0x47, 0x49, 0x46, 0x38])],
  'application/pdf': [Buffer.from([0x25, 0x50, 0x44, 0x46])],
};

// 验证文件类型
function validateFileType(file) {
  // 1. 检查扩展名
  const ext = path.extname(file.originalname).toLowerCase();
  const allowedExts = Object.values(ALLOWED_TYPES).flat();
  if (!allowedExts.includes(ext)) {
    throw new Error(`Invalid file extension: ${ext}`);
  }

  // 2. 检查 MIME 类型
  if (!ALLOWED_TYPES[file.mimetype]) {
    throw new Error(`Invalid MIME type: ${file.mimetype}`);
  }

  // 3. 检查扩展名与 MIME 类型是否匹配
  if (!ALLOWED_TYPES[file.mimetype].includes(ext)) {
    throw new Error(`Extension ${ext} does not match MIME type ${file.mimetype}`);
  }

  // 4. 检查文件头（Magic Number）
  const signatures = FILE_SIGNATURES[file.mimetype];
  if (signatures) {
    const fileBuffer = fs.readFileSync(file.path);
    const isValid = signatures.some(sig =>
      fileBuffer.slice(0, sig.length).equals(sig)
    );
    if (!isValid) {
      throw new Error('File signature does not match declared type');
    }
  }

  return true;
}

// 生成安全文件名
function generateSafeFilename(originalName) {
  const ext = path.extname(originalName).toLowerCase();
  const randomName = crypto.randomBytes(16).toString('hex');
  return `${randomName}${ext}`;
}

// Multer 配置
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    // 上传到 Web 根目录外
    cb(null, '/var/uploads/tmp/');
  },
  filename: (req, file, cb) => {
    cb(null, generateSafeFilename(file.originalname));
  }
});

const upload = multer({
  storage,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
    files: 1,
  },
  fileFilter: (req, file, cb) => {
    try {
      validateFileType(file);
      cb(null, true);
    } catch (err) {
      cb(err);
    }
  }
});

// 使用
app.post('/upload', upload.single('file'), (req, res) => {
  // 文件已验证，移动到最终位置
  const finalPath = `/var/uploads/final/${req.file.filename}`;
  fs.renameSync(req.file.path, finalPath);

  res.json({
    success: true,
    filename: req.file.filename
  });
});
```

```python
# Python 文件上传验证
import os
import magic
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

ALLOWED_TYPES = {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
    'image/gif': ['.gif'],
    'application/pdf': ['.pdf'],
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def validate_file(file):
    """验证上传文件"""
    # 1. 检查文件大小
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValueError(f'File too large: {size} bytes')

    # 2. 检查扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    allowed_exts = [ext for exts in ALLOWED_TYPES.values() for ext in exts]
    if ext not in allowed_exts:
        raise ValueError(f'Invalid extension: {ext}')

    # 3. 检查 MIME 类型（通过文件内容）
    mime = magic.Magic(mime=True)
    file_type = mime.from_buffer(file.read(1024))
    file.seek(0)

    if file_type not in ALLOWED_TYPES:
        raise ValueError(f'Invalid file type: {file_type}')

    # 4. 检查扩展名与 MIME 类型匹配
    if ext not in ALLOWED_TYPES[file_type]:
        raise ValueError(f'Extension {ext} does not match type {file_type}')

    return file_type

def generate_safe_filename(original_filename):
    """生成安全文件名"""
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4().hex}{ext}"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['file']

    try:
        file_type = validate_file(file)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    # 生成安全文件名
    safe_filename = generate_safe_filename(file.filename)

    # 保存到安全目录（Web 根目录外）
    upload_dir = '/var/uploads/final/'
    os.makedirs(upload_dir, exist_ok=True)
    file.save(os.path.join(upload_dir, safe_filename))

    return jsonify({
        'success': True,
        'filename': safe_filename
    })
```

2. **安全存储配置**
```bash
# Nginx 配置：禁止上传目录执行脚本
location /uploads/ {
    # 禁止执行任何脚本
    location ~* /uploads/.*\.(php|jsp|asp|aspx|cgi|pl|py|sh)$ {
        deny all;
    }

    # 设置正确的 Content-Type
    types {
        image/jpeg jpg jpeg;
        image/png png;
        image/gif gif;
    }

    # 禁止目录列表
    autoindex off;

    # 只读访问
    add_header Content-Disposition "attachment";
}
```

```bash
# Apache 配置：禁止脚本执行
<Directory "/var/www/html/uploads">
    Options -ExecCGI -Indexes
    AllowOverride None
    <FilesMatch "\.(php|jsp|asp|aspx|cgi|pl|py|sh)$">
        Order Allow,Deny
        Deny from all
    </FilesMatch>
</Directory>
```

3. **文件访问控制**
```javascript
// 通过 API 访问文件（而非直接 URL）
app.get('/files/:filename', authenticateUser, (req, res) => {
  const filename = req.params.filename;
  const filePath = path.join('/var/uploads/final/', filename);

  // 验证文件存在
  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'File not found' });
  }

  // 权限检查（可选）
  if (!canAccessFile(req.user, filename)) {
    return res.status(403).json({ error: 'Access denied' });
  }

  // 设置正确的 Content-Type
  const ext = path.extname(filename).toLowerCase();
  const contentTypes = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.pdf': 'application/pdf',
  };

  res.setHeader('Content-Type', contentTypes[ext] || 'application/octet-stream');
  res.setHeader('Content-Disposition', `inline; filename="${filename}"`);

  // 流式传输文件
  const fileStream = fs.createReadStream(filePath);
  fileStream.pipe(res);
});
```

**局限性**：
- 需要手动配置各种验证规则
- 本地存储扩展性有限
- 缺少病毒扫描能力

#### 方案B：低成本方案（<$50/月）

**工具/服务**：云存储 + 病毒扫描

**配置步骤**：

1. **AWS S3 安全上传**
```javascript
const AWS = require('aws-sdk');
const s3 = new AWS.S3();

async function uploadToS3(file, userId) {
  // 验证文件类型
  validateFileType(file);

  // 生成安全文件名
  const safeFilename = generateSafeFilename(file.originalname);
  const key = `uploads/${userId}/${safeFilename}`;

  // 上传到 S3
  const result = await s3.upload({
    Bucket: process.env.S3_BUCKET,
    Key: key,
    Body: fs.createReadStream(file.path),
    ContentType: file.mimetype,
    // 私有访问
    ACL: 'private',
    // 添加元数据
    Metadata: {
      'user-id': userId,
      'original-name': file.originalname,
    },
    // 服务端加密
    ServerSideEncryption: 'AES256',
  }).promise();

  // 删除临时文件
  fs.unlinkSync(file.path);

  return {
    key: result.Key,
    url: `https://${process.env.S3_BUCKET}.s3.amazonaws.com/${key}`,
  };
}

// 生成临时访问 URL（带过期时间）
function getSignedUrl(key, expiresIn = 3600) {
  return s3.getSignedUrl('getObject', {
    Bucket: process.env.S3_BUCKET,
    Key: key,
    Expires: expiresIn,
  });
}
```

2. **ClamAV 病毒扫描**
```javascript
const NodeClam = require('clamscan');

const clamscan = new NodeClam().init({
  clamscan: {
    path: '/usr/bin/clamscan',
    db: '/var/lib/clamav',
    scan_recursively: false,
  },
});

async function scanFile(filePath) {
  const { is_infected, viruses } = await clamscan.is_infected(filePath);

  if (is_infected) {
    // 删除感染文件
    fs.unlinkSync(filePath);
    throw new Error(`Virus detected: ${viruses.join(', ')}`);
  }

  return true;
}

// 在上传流程中集成
app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    // 病毒扫描
    await scanFile(req.file.path);

    // 上传到 S3
    const result = await uploadToS3(req.file, req.user.id);

    res.json({ success: true, ...result });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});
```

**优势**：
- 云存储安全性更高
- 自动扩展，无需担心磁盘空间
- 提供访问控制和加密
- 病毒扫描提供额外保护

### 决策树
```
你的应用是否允许用户上传文件？
├── 是 → 必须实施文件验证
│   ├── 文件是否包含敏感信息？→ 启用病毒扫描
│   ├── 预算充足？→ 使用云存储（S3）
│   └── 预算有限？→ 本地安全存储
└── 否 → 无需处理
```

### 代码示例

**完整的文件上传安全处理类**
```javascript
class SecureFileUploader {
  constructor(config) {
    this.allowedTypes = config.allowedTypes || {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/gif': ['.gif'],
      'application/pdf': ['.pdf'],
    };
    this.maxSize = config.maxSize || 5 * 1024 * 1024;
    this.uploadDir = config.uploadDir || '/var/uploads';
    this.s3Config = config.s3;
    this.clamscan = config.clamscan;
  }

  // 验证文件类型
  validateType(file) {
    const ext = path.extname(file.originalname).toLowerCase();
    const mime = file.mimetype;

    // 检查 MIME 类型
    if (!this.allowedTypes[mime]) {
      throw new Error(`Invalid MIME type: ${mime}`);
    }

    // 检查扩展名
    if (!this.allowedTypes[mime].includes(ext)) {
      throw new Error(`Extension ${ext} not allowed for ${mime}`);
    }

    // 检查文件头
    this.validateSignature(file);
  }

  // 验证文件签名
  validateSignature(file) {
    const signatures = {
      'image/jpeg': [[0xFF, 0xD8, 0xFF]],
      'image/png': [[0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]],
      'image/gif': [[0x47, 0x49, 0x46, 0x38]],
      'application/pdf': [[0x25, 0x50, 0x44, 0x46]],
    };

    const sigs = signatures[file.mimetype];
    if (!sigs) return;

    const buffer = fs.readFileSync(file.path);
    const valid = sigs.some(sig =>
      buffer.slice(0, sig.length).equals(Buffer.from(sig))
    );

    if (!valid) {
      throw new Error('File signature mismatch');
    }
  }

  // 验证文件大小
  validateSize(file) {
    const stats = fs.statSync(file.path);
    if (stats.size > this.maxSize) {
      throw new Error(`File too large: ${stats.size} bytes`);
    }
  }

  // 病毒扫描
  async scanForVirus(filePath) {
    if (!this.clamscan) return;

    const { is_infected, viruses } = await this.clamscan.is_infected(filePath);
    if (is_infected) {
      throw new Error(`Virus detected: ${viruses.join(', ')}`);
    }
  }

  // 生成安全文件名
  generateFilename(originalName) {
    const ext = path.extname(originalName).toLowerCase();
    const hash = crypto.randomBytes(16).toString('hex');
    const timestamp = Date.now();
    return `${timestamp}-${hash}${ext}`;
  }

  // 上传到本地
  async uploadLocal(file, userId) {
    const safeFilename = this.generateFilename(file.originalname);
    const userDir = path.join(this.uploadDir, userId.toString());
    const finalPath = path.join(userDir, safeFilename);

    // 确保目录存在
    fs.mkdirSync(userDir, { recursive: true, mode: 0o750 });

    // 移动文件
    fs.renameSync(file.path, finalPath);
    fs.chmodSync(finalPath, 0o640); // 只读权限

    return {
      filename: safeFilename,
      path: finalPath,
      url: `/files/${userId}/${safeFilename}`,
    };
  }

  // 上传到 S3
  async uploadS3(file, userId) {
    if (!this.s3Config) {
      throw new Error('S3 not configured');
    }

    const s3 = new AWS.S3(this.s3Config);
    const safeFilename = this.generateFilename(file.originalname);
    const key = `uploads/${userId}/${safeFilename}`;

    const result = await s3.upload({
      Bucket: this.s3Config.bucket,
      Key: key,
      Body: fs.createReadStream(file.path),
      ContentType: file.mimetype,
      ACL: 'private',
      ServerSideEncryption: 'AES256',
      Metadata: {
        'user-id': userId.toString(),
        'original-name': file.originalname,
      },
    }).promise();

    fs.unlinkSync(file.path);

    return {
      filename: safeFilename,
      key: result.Key,
      url: result.Location,
    };
  }

  // 处理上传
  async handleUpload(file, userId) {
    // 1. 验证文件大小
    this.validateSize(file);

    // 2. 验证文件类型
    this.validateType(file);

    // 3. 病毒扫描
    await this.scanForVirus(file.path);

    // 4. 上传到存储
    const result = this.s3Config
      ? await this.uploadS3(file, userId)
      : await this.uploadLocal(file, userId);

    return result;
  }
}

// 使用示例
const uploader = new SecureFileUploader({
  allowedTypes: {
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
  },
  maxSize: 10 * 1024 * 1024, // 10MB
  uploadDir: '/var/uploads',
  s3Config: {
    bucket: process.env.S3_BUCKET,
    region: process.env.AWS_REGION,
  },
});

app.post('/upload', upload.single('file'), async (req, res) => {
  try {
    const result = await uploader.handleUpload(req.file, req.user.id);
    res.json({ success: true, ...result });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});
```

---

## L3 企业版（深耕版）

参见企业级案例：[文件上传安全](../../enterprise/infosec/file-upload-security.md)

### 高级防护策略

1. **内容安全策略**
   - 图片去 EXIF 信息
   - 图片重编码
   - 内容审核

2. **高级威胁检测**
   - 沙箱分析
   - 行为检测
   - AI 内容识别

3. **合规性检查**
   - GDPR 数据处理
   - 数据分类标记
   - 审计日志

### 推荐企业方案
- AWS S3 + Lambda - 按使用量计费
- Cloudinary Pro - $89/月起
- Microsoft Defender for Cloud - 企业定价

---

## 相关案例
- [SQL 注入攻击](./sql-injection.md)
- [XSS 攻击](./xss-attack.md)

## 推荐武器
- [文件上传验证库](../../../weapons/indie/open-source/file-upload-validator.md)
- [S3 安全配置模板](../../../weapons/indie/saas/s3-secure-upload.md)
