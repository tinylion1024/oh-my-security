# 元数据泄露 (Metadata Leak)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-009 |
| 分类 | 数据安全 / 信息泄露 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

文件、图片、文档等资源包含敏感元数据（如 EXIF、作者信息、GPS 位置、编辑历史），导致用户隐私泄露或系统信息暴露。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **图片 EXIF 数据未清除** - 上传的图片包含 GPS 坐标、拍摄设备、时间等信息
- [ ] **文档元数据泄露** - PDF、Office 文档包含作者、修订历史、隐藏批注
- [ ] **云服务元数据泄露** - AWS EC2 实例元数据服务（IMDS）可被 SSRF 访问

### 🔍 典型场景

```
场景 1: 图片 GPS 泄露
用户上传自拍照片
照片 EXIF 包含 GPS 坐标: 39.9042° N, 116.4074° E
结果:     用户精确位置泄露，可能被跟踪

场景 2: 文档作者泄露
上传合同 PDF 文件
PDF 属性: 作者="张三"，修订历史显示删除内容
结果:     泄露员工身份、合同历史信息

场景 3: AWS 元数据服务
SSRF 攻击访问: http://169.254.169.254/latest/meta-data/iam/security-credentials/
返回: IAM 临时凭证
结果:     云账户完全被控制
```

---

## 一句话防御

**上传时自动移除敏感元数据、实施文档清洗流程、启用 AWS IMDSv2 防止 SSRF 攻击、限制元数据服务访问。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **ExifTool** | 元数据查看与删除 | https://exiftool.org/ |
| **MAT2** | 元数据清理工具 | https://0xacab.org/jvoisin/mat2 |
| **ExifCleaner** | 图片元数据清理 | https://exifcleaner.com/ |
| **AWS IMDSv2** | 实例元数据保护 | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html |

---

## 快速缓解措施

### 1. 图片元数据清理
```python
# Python + Pillow 示例
from PIL import Image
import piexif

def remove_exif(image_path, output_path):
    img = Image.open(image_path)

    # 方法 1：重新保存不包含 EXIF
    data = list(img.getdata())
    img_no_exif = Image.new(img.mode, img.size)
    img_no_exif.putdata(data)
    img_no_exif.save(output_path)

    # 方法 2：使用 piexif 清理特定字段
    exif_dict = piexif.load(img.info.get('exif', b''))
    # 删除 GPS 信息
    exif_dict['GPS'] = {}
    exif_bytes = piexif.dump(exif_dict)
    img.save(output_path, exif=exif_bytes)
```

### 2. 文档元数据清理
```python
# Python + PyPDF2 示例
from PyPDF2 import PdfReader, PdfWriter

def clean_pdf_metadata(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # 清空元数据
    writer.add_metadata({
        "/Title": "",
        "/Author": "",
        "/Subject": "",
        "/Creator": "",
        "/Producer": "Secure PDF Processor"
    })

    with open(output_path, "wb") as output_file:
        writer.write(output_file)
```

### 3. AWS IMDSv2 启用
```bash
# AWS CLI：在实例上启用 IMDSv2
aws ec2 modify-instance-metadata-options \
  --instance-id i-12345678 \
  --http-tokens required \
  --http-endpoint enabled

# 使用 IMDSv2 获取元数据
TOKEN=$(curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
```

---

## 相关案例

- [CASE-EXT-DATA-006 配置文件暴露](./config-exposure.md)
- [CASE-EXT-DATA-007 快照泄露](./snapshot-leak.md)

---

## 参考标准

- OWASP ASVS v4.0 - V12: Files and Resources
- CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
- NIST SP 800-53 - SI-11: Error Handling
- EXIF 2.3 Specification
