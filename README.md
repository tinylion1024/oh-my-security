# 🛡️ Oh-My-Security (OMS)

> 你的终端安全瑞士军刀。

**Oh-My-Security** 是一款专为安全工程师和极客开发者打造的命令行工具与知识引擎。它完成了从“被动知识库”到“主动安全终端”的蜕变，提供开箱即用的命令行体验、自动化安全审计脚本，以及基于 **300+ 真实硬核案例** 的 AI 辅助决策能力。

---

## ✨ 核心特性

- **💻 极致的 CLI 体验**: 输入 `oms` 即可在终端唤起安全引擎，支持颜色高亮与结构化表格输出。
- **📚 海量实战记忆**: 内置 **304 个**高度专业化的案例（覆盖 Infosec、Bizsec、AIsec），作为大模型决策的上下文基石。
- **🧮 终端安全算力**: 内置 CVSS 3.1 漏洞评估计算器，后续支持一键 JWT 解析、编码转换等。
- **🧩 强可扩展架构**: 插件化的目录设计（`plugins/`），极易接入诸如 Semgrep 审计、Nmap 扫描等外部能力。

---

## 🚀 快速开始

### 1. 安装
克隆本仓库，并将 `bin` 目录添加到您的环境变量中，同时设置 `PYTHONPATH`：

```bash
git clone https://github.com/tinylion1024/oh-my-security.git
cd oh-my-security
pip install -r requirements.txt

# 将 oms 加入全局命令 (建议写入 ~/.zshrc 或 ~/.bashrc)
export PYTHONPATH=$(pwd)
export PATH="$PATH:$(pwd)/bin"
```

### 2. 使用演示

在终端中输入 `oms`，您将看到极客风格的启动界面：

```text
  ____  _       __  __          ____                       _ _         
 / __ \| |     |  \/  |        / ___|                     (_) |        
| |  | | |__   | \  / |_   _  | |___  ___  ___ _   _ _ __  _| |_ _   _ 
| |  | | '_ \  | |\/| | | | |  \___ \/ _ \/ __| | | | '__| | | __| | | |
| |__| | | | | | |  | | |_| |  ____) |  __/ (__| |_| | |  | | | |_| |_| |
 \____/|_| |_| |_|  |_|\__, | |_____/ \___|\___|\__,_|_|  |_|_|\__|\__, |
```

#### 🔍 在终端中检索案例 (OMS Case)
快速从 300+ 个专家级案例中寻找对应的安全事件：

```bash
oms case "薅羊毛"
```

#### 🧮 终端漏洞定级 (OMS CVSS)
无需打开网页，在命令行直接计算漏洞的 CVSS 3.1 基础得分：

```bash
oms cvss -av N -ac L -pr N -ui N -c H -i H -a H
```

---

## 📂 项目架构

为了支持工具化与极客生态，项目结构设计如下：

```text
oh-my-security/
├── bin/
│   └── oms                 # 命令行可执行入口 (基于 Argparse & Rich)
├── oms_core/               # 核心 Python 引擎
│   ├── retriever.py        # 检索 300+ 案例的引擎
│   ├── cvss_calc.py        # 终端计算器逻辑
│   └── generate_indexes.py # 知识库自动索引生成脚本
├── plugins/                # [建设中] 第三方安全插件生态
├── knowledge_base/         # 您的核心安全资产
│   ├── cases/              # 304 个专家级案例 (Infosec, Bizsec, AIsec)
│   ├── weapons/            # 具体的防御武器技术栈
│   └── schools/            # 顶级安全理论流派
└── requirements.txt
```

---

## 🤖 背后的大脑：多 Agent 协同体系

OMS 不仅是一个静态工具，配合大模型智能体（如 Gemini CLI），它充当了一个高级安全委员会：

- **Red Agent**：推演攻击面的 `Red View`。
- **Blue Agent**：匹配防御武器库的 `Blue View`。
- **Biz Agent**：评估安全对业务性能与体验损耗的平衡官。
- **Compliance**：对齐 GDPR、等保 2.0 等法规的审计官。

*(详细指令规范请参考 `SKILL.md` 和 `references/output-schema.md`)*

---

## 🤝 参与贡献
我们欢迎您通过提交 PR 来扩展 `knowledge_base` 中的案例库，或者在 `plugins` 目录下开发令人惊叹的安全小工具！

## ⚖️ 免责声明
*Oh-My-Security 提供的所有案例及建议均为决策参考，严禁将其用于未经授权的非法攻击目的。*
