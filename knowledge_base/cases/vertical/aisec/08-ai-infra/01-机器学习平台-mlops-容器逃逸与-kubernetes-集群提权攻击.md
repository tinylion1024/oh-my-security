# 机器学习平台 (MLOps) 容器逃逸与 Kubernetes 集群提权攻击
- **所属领域**: AI 安全
- **威胁类型**: 基础设施安全 / 容器逃逸 / 权限提升
- **事件回顾**: 某科技公司自研的 MLOps 平台遭到黑客入侵。攻击者首先注册了该平台的普通开发者账号，并利用平台提供的 Jupyter Notebook 实例作为入口。随后，攻击者通过在 Notebook 中执行恶意代码，成功利用底层 Docker 容器的配置缺陷（特权模式运行或挂载了敏感的主机目录）实现了容器逃逸，获取了宿主机的 root 权限。进一步，攻击者窃取了 Kubernetes 集群的 ServiceAccount Token，从而横向移动并控制了整个 AI 算力集群。
- **Red View (利用路径)**: 攻击者利用 Python 的 `os.system` 或类似机制在 Jupyter 环境中执行 Shell 命令进行信息收集。发现容器是以 `--privileged` 模式启动后，利用 `mount` 命令将宿主机的根目录挂载到容器内部，或者利用挂载的 docker.sock 与宿主机 Docker 守护进程通信，启动一个新的挂载宿主机根目录的容器。逃逸后，读取 `/var/run/secrets/kubernetes.io/serviceaccount/token` 并利用 kubectl 命令提权，接管集群 API Server。
- **Blue View (防御缺失)**: MLOps 平台为了方便用户调试和挂载各种加速硬件（如 GPU），默认给予了用户工作负载过高的权限（特权容器或不当挂载）。安全团队未实施严格的 Pod 安全策略（Pod Security Policies / Pod Security Admission），未能隔离开发环境容器的网络与内网核心网络。此外，缺乏针对容器内异常行为（如敏感目录挂载、特权系统调用）的运行时监控。
- **策略借鉴**: 遵循最小权限原则，严禁以特权模式运行用户提交的代码和 Notebook 容器；使用 Seccomp、AppArmor 和 SELinux 限制容器内的系统调用；配置严格的 RBAC 策略和网络策略，实现多租户之间的网络与资源隔离；部署如 Falco/Tetragon 等容器运行时安全工具，实时监控并阻断容器逃逸行为。