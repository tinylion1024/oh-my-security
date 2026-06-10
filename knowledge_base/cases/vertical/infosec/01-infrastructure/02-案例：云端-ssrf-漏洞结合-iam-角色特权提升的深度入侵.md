# 案例：云端 SSRF 漏洞结合 IAM 角色特权提升的深度入侵

## 事件回顾
某知名金融机构遭受了一次极其严重的网络攻击，导致超过 1 亿用户的信用卡申请数据、社会安全号码（SSN）以及银行账户信息被窃取。该事件的核心起因是其部署在 AWS 云上的 Web 应用防火墙（WAF）存在服务器端请求伪造（SSRF）漏洞。由于这台 WAF 所在的 EC2 实例被过度赋予了高级别的 IAM 角色权限，攻击者不仅突破了边界，更利用云原生元数据服务，将权限横向扩展到了敏感的后端存储层，最终实现了灾难级别的数据拖库。

## Red View (利用路径)
1. **SSRF 漏洞探测与利用**：攻击者通过发送特制的 HTTP 请求，发现目标公司的 WAF（或反向代理）对内部地址的请求缺乏严格过滤，成功实现了 SSRF 攻击。
2. **元数据服务凭证窃取**：利用 SSRF，攻击者指示服务器请求 AWS 实例元数据服务（IMDSv1）端点 `http://169.254.169.254/latest/meta-data/iam/security-credentials/`，成功窃取到了分配给该 EC2 实例的临时安全凭证（Access Key, Secret Key, Session Token）。
3. **权限滥用与数据外泄**：由于该 EC2 角色拥有过高的 `s3:List*` 和 `s3:Get*` 权限，攻击者在本地配置了这些临时凭证，并伪装成合法服务，列出了 700 多个 S3 存储桶，随后同步命令并窃取了包含敏感金融数据的文件。

## Blue View (防御缺失)
- **过度宽松的 IAM 权限 (Over-permissive Roles)**：分配给 WAF 实例的 IAM 角色远超其执行网络流量过滤所需的最小权限，它无需访问后端核心数据存储桶却拥有全量 S3 读取权限。
- **落后的元数据服务版本**：系统仍然在使用未要求增强验证的 IMDSv1。IMDSv1 对 SSRF 攻击毫无抵抗力，而若强制要求使用需要 PUT 请求获取 Token 的 IMDSv2，攻击难度将大幅增加。
- **内外网边界与网络异常流量监控缺失**：对于云资源向外部未知 IP 进行的大量数据传输，缺乏 VPC 流日志（VPC Flow Logs）的深度监控，未能触发针对大流量外发（Data Exfiltration）的告警。

## 策略借鉴
1. **强制升级并实施 IMDSv2**：在云基础设施中，彻底淘汰 IMDSv1，强制所有 EC2 实例使用 IMDSv2（Instance Metadata Service Version 2）。由于 IMDSv2 强制要求在获取凭证前发起特定的 PUT 请求以获取 Token，这极大地缓解了绝大多数基于 GET 的 SSRF 漏洞攻击。
2. **细粒度的最小权限原则 (Least Privilege)**：对所有云上计算节点（EC2, Lambda, ECS）严格实施按需授权。对于 WAF 等边界网关，绝对禁止赋予其访问后端核心数据（如 S3, RDS）的权限；利用 IAM Access Analyzer 定期清理未使用的权限。
3. **深度防御与 Zero Trust 网络边界**：配置 WAF 和网络防火墙以阻断所有不必要的出站请求；通过 VPC Endpoint (PrivateLink) 实现服务间的私有通信，并辅以严格的 S3 Bucket Policy，仅允许来自特定 VPC 端点且具备合法角色身份的访问。