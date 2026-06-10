# Kubernetes API Server裸奔引发的K8s集群全面接管攻击
- **所属领域**: 信息安全
- **威胁类型**: K8s配置漏洞 / 集群接管
- **事件回顾**: 某电商平台的Kubernetes集群因网络管理员的一次错误路由配置，使得原本只在内网通信的K8s API Server（通常为6443端口）意外暴露于公网，且未配置匿名请求拦截。黑客通过扫描发现后，无需任何凭据即可向API Server下发指令。攻击者创建了一个绑定ClusterRoleBinding最高特权的恶意DaemonSet，导致K8s集群中所有的物理节点都被下发了挖矿和后门容器，造成严重的计算资源被盗和业务瘫痪。
- **Red View (利用路径)**: 全网扫描暴露的6443端口并探测K8s API接口响应 -> 发现允许匿名访问或存在旧版未修补漏洞 -> 利用`kubectl`或直接发送REST API请求列出集群资源 -> 提交恶意DaemonSet或Pod定义文件，配置特权模式或挂载宿主机目录 -> 启动挖矿程序并在宿主机留存持久化后门。
- **Blue View (防御缺失)**: Kubernetes安全基线严重缺失，API Server未关闭匿名访问（`--anonymous-auth=false`）且对外网直接开放；RBAC权限控制形同虚设，未对Pod运行的Security Context进行限制；缺乏集群级别的审计日志与异常API调用告警。
- **策略借鉴**: 严格收敛公网暴露面，K8s API Server仅限可信内网访问；强制执行细粒度的RBAC控制策略，并禁用匿名访问；部署Pod安全准入（Pod Security Admission）控制策略，阻止特权容器与危险挂载的创建；实施全量审计日志（Audit Log）分析和威胁告警。
