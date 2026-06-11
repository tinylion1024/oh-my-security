# 临时文件暴露 (Temporary File Exposure)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-005 |
| 分类 | 数据安全 / 文件安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

临时文件包含敏感数据且权限配置不当或存储位置可预测，导致未经授权访问、数据泄露或竞争条件攻击。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **可预测的文件名** - 临时文件名可被猜测（如 `temp.tmp`、`upload_123.tmp`）
- [ ] **不安全的权限** - 临时文件权限设置为全局可读（如 `chmod 644`）
- [ ] **Web 可访问** - 临时文件存储在 Web 根目录或可通过 URL 访问

### 🔍 典型场景

```
场景 1: 文档转换服务
上传 PDF → 转换为图片 → 存储在 /tmp/convert_12345.png
攻击者遍历数字访问其他用户的转换文件
结果:     其他用户的文档被窃取

场景 2: 数据导出
导出用户数据 → 写入 /var/www/html/export_user_123.csv
直接访问 https://example.com/export_user_123.csv
结果:     用户敏感数据泄露

场景 3: 竞争条件
文件上传 → 重命名到最终位置
攻击者在重命名前访问临时文件
结果:     文件内容被读取或替换
```

---

## 一句话防御

**使用随机不可预测的文件名、设置严格的文件权限、将临时文件存储在 Web 根目录外、及时清理过期文件、使用安全临时文件 API。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **mktemp** | 安全临时文件创建 | https://man7.org/linux/man-pages/man1/mktemp.1.html |
| **Lynis** | 系统安全审计 | https://cisofy.com/lynis/ |
| **File Permissions Scanner** | 权限扫描工具 | https://github.com/Anon-Exploiter/file-permission-scanner |

---

## 快速缓解措施

### 1. 安全创建临时文件
```python
# Python 示例
import tempfile
import os

# 使用安全临时文件 API
with tempfile.NamedTemporaryFile(
    mode='w',
    suffix='.csv',
    prefix='export_',
    dir='/secure/tmp',  # 非 Web 目录
    delete=True  # 自动删除
) as temp_file:
    temp_file.write(sensitive_data)
    # 文件会在 with 块结束时自动删除
```

### 2. 随机文件名与权限
```javascript
// Node.js 示例
const fs = require('fs');
const crypto = require('crypto');

const tempDir = '/secure/tmp';  // 非 Web 目录
const randomName = crypto.randomBytes(32).toString('hex');
const tempPath = path.join(tempDir, `export_${randomName}.csv`);

// 写入文件并设置严格权限（仅所有者可读写）
fs.writeFileSync(tempPath, sensitiveData, { mode: 0o600 });

// 使用后立即删除
fs.unlinkSync(tempPath);
```

### 3. 定期清理临时文件
```bash
# cron 任务：每小时清理超过 1 小时的临时文件
0 * * * * find /tmp -type f -name "export_*.csv" -mmin +60 -delete

# 或使用 systemd timer
[Unit]
Description=Clean temporary files

[Timer]
OnCalendar=hourly

[Service]
Type=oneshot
ExecStart=/usr/bin/find /tmp -type f -name "export_*.csv" -mmin +60 -delete
```

---

## 相关案例

- [CASE-EXT-DATA-004 日志注入](./log-injection.md)
- [CASE-EXT-DATA-006 配置文件暴露](./config-exposure.md)

---

## 参考标准

- CWE-379: Creation of Temporary File in Directory with Insecure Permissions
- OWASP ASVS v4.0 - V12: Files and Resources
- NIST SP 800-53 - SI-7: Software, Firmware, and Information Integrity
- POSIX.1-2008 - Temporary Files
