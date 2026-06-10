# GitHub Actions工作流滥用引发的大规模挖矿算力盗用事件
- **所属领域**: 信息安全
- **威胁类型**: CI/CD滥用 / 资源消耗
- **事件回顾**: 某知名开源项目利用GitHub Actions进行日常的代码自动化测试。2020年，黑客通过Fork该开源仓库，修改了针对Pull Request触发的GitHub Actions Workflow配置，向其中加入了部署门罗币挖矿程序的指令。随后，黑客向官方仓库提交了伪造的PR（Pull Request）。由于该项目的配置未限制来自外部Fork的自动构建权限，GitHub自动分配了数百台云端Runner实例去运行这个携带挖矿代码的PR测试，大量耗费了云算力，并可能引发项目维护者的云账单爆炸。
- **Red View (利用路径)**: Fork目标的高星开源仓库 -> 篡改`.github/workflows/`下的YAML配置文件，加入下载和执行挖矿程序的Shell指令 -> 向目标项目提交虚假的PR -> 触发目标项目的GitHub Actions CI流程 -> 在GitHub托管的Runner服务器上长时间占用CPU资源挖矿。
- **Blue View (防御缺失)**: CI/CD环境对外部贡献者的触发机制缺乏审核，默认允许任何外部PR自动执行Workflow脚本；缺乏对自动化工作流运行时间和异常CPU占用的监控；未配置工作流只读或有限权限的最小化控制策略。
- **策略借鉴**: 在代码托管平台（如GitHub/GitLab）中配置“要求来自首次贡献者或所有外部贡献者的PR必须经由维护者批准后才能运行CI工作流”；严格限制Workflow的运行超时期时长和环境权限（例如设置`permissions: read-all`）；剥离构建节点与内部核心网络的直接访问权限，防止由挖矿演变为内网渗透。
