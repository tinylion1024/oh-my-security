# [利用WMI与PowerShell的隐蔽无文件恶意软件执行]
- **所属领域**: 信息安全 - 端点安全
- **威胁类型**: 无文件攻击 (Fileless Malware) / 内存驻留
- **事件回顾**: 某电力基础设施管理中心遭到网络攻击。安全分析师排查终端卡顿问题时发现CPU占用率极高，但磁盘上未找到任何可疑可执行文件。溯源表明，攻击者利用Windows Management Instrumentation (WMI) 和PowerShell实现隐蔽的无文件攻击。恶意代码作为WMI类属性有效载荷存储在WMI存储库中，通过WMI事件订阅（Event Subscription）实现持久化，无需在硬盘写入任何传统恶意文件，避开了基于签名的反病毒扫描。
- **Red View (利用路径)**: 攻击者获取低权限后，利用系统自带的WMI命令行工具（wmic.exe）创建恶意的 `__EventFilter` 和 `__EventConsumer`。当特定系统事件触发时，绑定的PowerShell脚本被唤醒。该脚本从WMI存储库读取Base64编码的shellcode，并利用反射式DLL注入技术直接在内存中执行，整个生命周期不接触磁盘。
- **Blue View (防御缺失)**: 蓝队缺乏对无文件攻击特征的监控能力。虽然部署了反病毒软件，但对系统原生进程（LoLBin，如 wmiprvse.exe、powershell.exe）的异常调用链没有建立基线监测。同时未能启用PowerShell的脚本块日志记录和系统转录，导致事后取证无法还原攻击者执行的真实命令。
- **策略借鉴**: 针对无文件攻击需提升终端可见性体系：1）全面开启PowerShell脚本块日志和AMSI（反恶意软件扫描接口）集成；2）使用Sysmon监控WMI异常事件订阅和高危进程注入行为；3）采用内存扫描技术和基于行为的异常分析，替代仅依赖文件哈希的静态防御。