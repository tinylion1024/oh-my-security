# 案例：Kubernetes Dashboard 未授权访问导致的集群接管

## 事件回顾
随着微服务架构的普及，某大型电商平台将其核心业务完全迁移至自建的 Kubernetes 集群。然而，在一次例行维护中，工程师为了方便监控，错误地将 Kubernetes Dashboard 服务暴露在了公网上，并且绑定了具有最高权限的 ServiceAccount。这一致命配置失误被自动化漏洞扫描脚本迅速发现，攻击者无需提供任何身份凭证即可直接访问 Dashboard。这导致攻击者在几分钟内接管了整个 K8s 集群，不仅部署了恶意挖矿容器消耗算力，还利用容器逃逸技术获取了宿主机的底层控制权。

## Red View (利用路径)
1. **端口扫描与暴露服务发现**：攻击者通过 Shodan/Censys 等搜索引擎或大规模端口扫描，发现了开放的 Kubernetes Dashboard 默认端口，且该页面允许直接跳过登录验证。
2. **高权限滥用与后门部署**：进入 Dashboard 后，攻击者发现其绑定的默认 ServiceAccount 拥有 `cluster-admin` 角色。攻击者随即通过界面或 API 创建了一个特权容器（Privileged Pod），挂载了宿主机的根目录 `/` 到容器内部。
3. **容器逃逸与持久化控制**：通过该特权容器，攻击者使用 `chroot` 进入宿主机文件系统，添加 SSH 公钥并修改 crontab 定时任务，植入了加密货币挖矿木马，同时窃取了集群内的敏感 Secrets（如数据库密码、云厂商 API Key）。

## Blue View (防御缺失)
- **管理接口违规暴露**：K8s Dashboard 作为高敏感的内部管理工具，未经任何访问控制（如 VPN、IP 白名单、Ingress OIDC 认证）直接暴露在公网，违反了基本的网络隔离边界原则。
- **RBAC 配置严重失效**：未能遵循最小权限原则，Dashboard 被赋予了集群管理员（ClusterAdmin）的超级权限。即使暴露，若仅为只读权限，破坏力也会大大受限。
- **缺乏容器运行时安全防护**：集群未实施 Pod 安全策略（如 PSP/OPA Gatekeeper/Kyverno），允许随意创建带有 `privileged: true` 及 `hostPath` 挂载属性的高危 Pod，导致从容器到宿主机的逃逸轻而易举。

## 策略借鉴
1. **强化管理面接口的访问控制**：永远不要将 K8s Dashboard 或 API Server 直接暴露在公网。必须通过强认证机制（如 OIDC、SAML 结合双因素认证）并在 VPN 或内网零信任网关（如 Cloudflare Access, Teleport）的保护下进行访问。
2. **严格实施 RBAC 与最小权限**：审查并重构 K8s 的 Role-Based Access Control 策略。为 Dashboard 以及任何服务账号分配最低限度的权限（如仅授予 `view` 权限），严禁轻易使用 `cluster-admin` 角色绑定。
3. **实施运行时的 Pod 安全准入控制**：全面部署 Kyverno 或 OPA Gatekeeper 准入控制器，制定严格的安全策略：强制禁止特权容器运行，限制 `hostPID`、`hostNetwork` 及敏感目录的 `hostPath` 挂载，并结合 Falco 或 Tetragon 进行运行时的异常行为监控（如意外的 Shell 执行）。