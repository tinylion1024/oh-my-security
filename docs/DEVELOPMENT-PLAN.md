# Oh-My-Security 开发计划

> 版本: v1.0
> 更新时间: 2024-06-12
> 状态: 规划中

---

## 📋 目录

- [项目概述](#项目概述)
- [场景矩阵](#场景矩阵)
- [开发路线图](#开发路线图)
- [详细规划](#详细规划)
- [技术架构](#技术架构)
- [资源需求](#资源需求)
- [风险评估](#风险评估)

---

## 项目概述

### 背景

Oh-My-Security (OMS) 是专为**独立开发者、Indie Hackers、自媒体创作者**打造的轻量级终端安全工具。

### 核心价值

```
传统安全工具 → 企业级、复杂、昂贵、需要专业背景
OMS → 个人级、简单、免费、零安全基础可上手
```

### 目标用户画像

- 独立开发者 / Indie Hacker
- 1人维护的全栈项目
- 安全预算接近零
- 安全投入 < 总开发时间 5%
- 希望快速获得可落地的防御方案

### 成功指标

| 指标 | 目标 |
|------|------|
| 核心场景覆盖 | 12个场景全覆盖 |
| 案例库规模 | 300+ 实战案例 |
| 上手时间 | < 5分钟 |
| 核心防护实施 | < 30分钟 |
| 用户成本 | $0 (全免费方案) |

---

## 场景矩阵

### 完整场景列表

| 序号 | 场景 | 命令 | 优先级 | 风险等级 | 状态 |
|------|------|------|--------|----------|------|
| 1 | 代码审计 | `oms code` | P0 | 🔴 破产级 | ✅ 已有 |
| 2 | 内容风控 | `oms content` | P0 | 🔴 破产级 | ✅ 已有 |
| 3 | 业务安全 | `oms bizsec` | P0 | 🔴 破产级 | ✅ 已有 |
| 4 | VPS加固 | `oms vps` | P1 | 🟠 高风险 | ✅ 已有 |
| 5 | 支付安全 | `oms payment` | P0 | 🔴 破产级 | 🆕 待开发 |
| 6 | 账号安全 | `oms account` | P0 | 🔴 破产级 | 🆕 待开发 |
| 7 | 依赖安全 | `oms deps` | P0 | 🔴 破产级 | 🆕 待开发 |
| 8 | 域名资产 | `oms domain` | P1 | 🟠 高风险 | 🆕 待开发 |
| 9 | AI安全 | `oms ai` | P1 | 🟠 高风险 | 🆕 待开发 |
| 10 | 应急响应 | `oms incident` | P1 | 🟠 高风险 | 🆕 待开发 |
| 11 | 移动设备 | `oms mobile` | P2 | 🟡 中风险 | 🆕 待开发 |
| 12 | 社媒账号 | `oms social` | P2 | 🟡 中风险 | 🆕 待开发 |
| 13 | 加密资产 | `oms crypto` | P2 | 🟡 中风险 | 🆕 待开发 |
| 14 | 合规自查 | `oms compliance` | P2 | 🟡 中风险 | 🆕 待开发 |

### 优先级定义

| 优先级 | 定义 | 判断标准 |
|--------|------|----------|
| **P0** | 立即需要 | 破产级风险，直接经济损失 |
| **P1** | 近期需要 | 高影响风险，业务中断 |
| **P2** | 锦上添花 | 中等风险，特定人群需要 |

---

## 开发路线图

### Phase 0: 基础完善 (Week 1-2)

**目标**: 完善现有场景，建立开发规范

```
Week 1:
├── 完善现有 4 个场景的文档和案例
├── 建立统一的 CLI 命令规范
├── 创建场景开发模板
└── 编写开发贡献指南

Week 2:
├── 优化 knowledge_base 结构
├── 补充核心案例至 100 个
├── 创建自动化测试框架
└── 发布 v0.2.0
```

**交付物**:
- [ ] 场景开发模板文档
- [ ] CLI 命令规范文档
- [ ] 贡献者指南
- [ ] v0.2.0 版本发布

---

### Phase 1: P0 场景开发 (Week 3-6)

**目标**: 完成破产级风险场景

#### Week 3-4: `oms payment` 支付安全

```
功能设计:
├── 支付参数篡改检测
├── 零元订单漏洞扫描
├── 双花攻击防护检查
├── 退款欺诈模式识别
├── 支付回调验证指南
└── 第三方支付安全配置检查

案例库:
├── parameter-tampering.md (参数篡改)
├── zero-order-attack.md (零元订单)
├── double-spending.md (双花攻击)
├── refund-fraud.md (退款欺诈)
├── callback-fraud.md (回调伪造)
├── price-manipulation.md (价格操纵)
├── currency-attack.md (货币单位攻击)
├── discount-abuse.md (优惠券滥用)
├── subscription-bypass.md (订阅绕过)
└── payment-redirect.md (支付重定向)
```

#### Week 5: `oms account` 账号安全

```
功能设计:
├── 密码强度检测
├── 撞库风险自查
├── 2FA 开启指南
├── Session 安全配置
├── 账号恢复流程检查
└── 敏感操作二次验证

案例库:
├── credential-stuffing.md (撞库攻击)
├── weak-password.md (弱密码)
├── session-hijacking.md (Session劫持)
├── brute-force.md (暴力破解)
├── account-takeover.md (账号接管)
├── password-reuse.md (密码复用)
├── mfa-bypass.md (MFA绕过)
├── recovery-attack.md (恢复流程攻击)
├── oauth-misconfig.md (OAuth配置错误)
└── token-leak.md (令牌泄露)
```

#### Week 6: `oms deps` 依赖安全

```
功能设计:
├── 依赖漏洞扫描 (整合 OSV/CVE)
├── 供应链投毒检测
├── License 合规检查
├── 过时依赖识别
├── 恶意包识别
└── 依赖锁定建议

案例库:
├── supply-chain-poisoning.md (供应链投毒)
├── malicious-package.md (恶意包)
├── dependency-confusion.md (依赖混淆)
├── typosquatting.md (包名仿冒)
├── prototype-pollution.md (原型污染)
├── license-violation.md (License违规)
├── outdated-deps.md (过时依赖)
├── transitive-vuln.md (传递性漏洞)
├── lockfile-tampering.md (锁文件篡改)
└── install-script-attack.md (安装脚本攻击)
```

**Phase 1 交付物**:
- [ ] `oms payment` 完整功能 + 10个案例
- [ ] `oms account` 完整功能 + 10个案例
- [ ] `oms deps` 完整功能 + 10个案例
- [ ] v0.3.0 版本发布

---

### Phase 2: P1 场景开发 (Week 7-10)

**目标**: 完成高风险场景

#### Week 7: `oms domain` 域名资产

```
功能设计:
├── 域名到期提醒
├── DNS 配置检查
├── SSL 证书状态
├── 域名锁定建议
├── WHOIS 隐私检查
└── 子域名泄露检测

案例库:
├── domain-hijacking.md (域名劫持)
├── dns-poisoning.md (DNS污染)
├── ssl-expired.md (SSL过期)
├── whois-exposure.md (WHOIS泄露)
├── subdomain-takeover.md (子域名接管)
├── domain-squatting.md (域名抢注)
├── dns-rebinding.md (DNS重绑定)
├── cert-transparency.md (证书透明度泄露)
├── registrar-attack.md (注册商攻击)
└── domain-lock-bypass.md (域名锁绕过)
```

#### Week 8: `oms ai` AI安全

```
功能设计:
├── Prompt 注入检测
├── API Key 使用审计
├── 模型输出过滤
├── 成本控制建议
├── 数据泄露防护
└── AI 应用安全配置

案例库:
├── prompt-injection.md (Prompt注入)
├── data-exfiltration.md (数据窃取)
├── cost-abuse.md (成本滥用)
├── jailbreak-attack.md (越狱攻击)
├── hallucination-risk.md (幻觉风险)
├── model-poisoning.md (模型投毒)
├── embedding-attack.md (嵌入攻击)
├── rag-leak.md (RAG数据泄露)
├── function-call-abuse.md (函数调用滥用)
└── context-overflow.md (上下文溢出攻击)
```

#### Week 9-10: `oms incident` 应急响应

```
功能设计:
├── 事件分类与定级
├── 应急响应剧本
├── 证据保全指南
├── 恢复操作清单
├── 复盘模板
└── 联系方式清单

剧本库:
├── account-compromised.md (账号被盗)
├── data-breach.md (数据泄露)
├── service-down.md (服务宕机)
├── payment-fraud.md (支付欺诈)
├── malware-detected.md (恶意软件)
├── ddos-attack.md (DDoS攻击)
├── ransomware.md (勒索软件)
├── social-engineering.md (社会工程)
├── insider-threat.md (内部威胁)
└── third-party-breach.md (第三方泄露)
```

**Phase 2 交付物**:
- [ ] `oms domain` 完整功能 + 10个案例
- [ ] `oms ai` 完整功能 + 10个案例
- [ ] `oms incident` 完整功能 + 10个剧本
- [ ] v0.4.0 版本发布

---

### Phase 3: P2 场景开发 (Week 11-14)

**目标**: 完成中等风险场景

#### Week 11: `oms mobile` 移动设备

```
功能设计:
├── 手机安全配置检查
├── App 权限审计
├── 钓鱼短信识别
├── 设备丢失应对
├── 备份加密检查
└── 生物识别安全

案例库:
├── device-lost.md (设备丢失)
├── app-permission-abuse.md (权限滥用)
├── sms-phishing.md (短信钓鱼)
├── malicious-app.md (恶意App)
├── backup-exposure.md (备份泄露)
├── biometric-bypass.md (生物识别绕过)
├── sim-swap.md (SIM卡调换)
├── screen-lock-bypass.md (锁屏绕过)
├── clipboard-leak.md (剪贴板泄露)
└── notification-leak.md (通知泄露)
```

#### Week 12: `oms social` 社媒账号

```
功能设计:
├── 社媒账号安全检查
├── 钓鱼链接识别
├── 账号冒充检测
├── 隐私设置优化
├── 第三方授权审计
└── 内容发布风险提示

案例库:
├── account-impersonation.md (账号冒充)
├── phishing-link.md (钓鱼链接)
├── oauth-abuse.md (OAuth滥用)
├── privacy-leak.md (隐私泄露)
├── content-hijacking.md (内容劫持)
├── verified-badge-fraud.md (认证造假)
├── dm-phishing.md (私信钓鱼)
├── story-attack.md (快拍攻击)
├── group-infiltration.md (群组渗透)
└── cross-post-risk.md (跨平台风险)
```

#### Week 13: `oms crypto` 加密资产

```
功能设计:
├── 钱包安全检查
├── 私钥存储审计
├── 签名钓鱼识别
├── 授权漏洞检测
├── 助记词安全
└── 硬件钱包指南

案例库:
├── private-key-leak.md (私钥泄露)
├── signature-phishing.md (签名钓鱼)
├── approval-attack.md (授权攻击)
├── mnemonic-exposure.md (助记词泄露)
├── wallet-drainer.md (钱包抽干)
├── smart-contract-bug.md (合约漏洞)
├── bridge-attack.md (跨链桥攻击)
├── dusting-attack.md (粉尘攻击)
├── clipboard-hijack.md (剪贴板劫持)
└── fake-wallet.md (假钱包)
```

#### Week 14: `oms compliance` 合规自查

```
功能设计:
├── 隐私政策生成
├── GDPR 合规检查
├── 数据跨境评估
├── 用户同意管理
├── 数据主体权利
└── 保留期限设置

案例库:
├── gdpr-violation.md (GDPR违规)
├── privacy-policy-missing.md (隐私政策缺失)
├── consent-bypass.md (同意绕过)
├── data-transfer-violation.md (数据跨境违规)
├── retention-violation.md (保留期限违规)
├── subject-right-violation.md (主体权利违规)
├── cookie-violation.md (Cookie违规)
├── breach-notification.md (泄露通知)
├── children-data.md (儿童数据处理)
└── employee-data.md (员工数据处理)
```

**Phase 3 交付物**:
- [ ] `oms mobile` 完整功能 + 10个案例
- [ ] `oms social` 完整功能 + 10个案例
- [ ] `oms crypto` 完整功能 + 10个案例
- [ ] `oms compliance` 完整功能 + 10个案例
- [ ] v0.5.0 版本发布

---

### Phase 4: 完善与发布 (Week 15-16)

**目标**: 文档完善、测试覆盖、正式发布

```
Week 15:
├── 完善所有场景文档
├── 补充案例至 300+
├── 编写用户手册
├── 录制演示视频
└── 性能优化

Week 16:
├── 全面测试覆盖
├── 安全审计
├── 发布 v1.0.0
├── 官网建设
└── 社区推广
```

**Phase 4 交付物**:
- [ ] 完整用户手册
- [ ] 300+ 案例库
- [ ] 演示视频
- [ ] v1.0.0 正式发布
- [ ] 官网上线

---

## 详细规划

### 场景开发模板

每个场景必须包含以下内容:

```
scenario-name/
├── README.md              # 场景说明
├── cases/                 # 案例库 (10+)
│   ├── case-1.md
│   └── ...
├── weapons/               # 防御武器
│   ├── tool-1.md
│   └── ...
├── checklists/            # 检查清单
│   └── main-checklist.md
├── cli.py                 # CLI 实现
└── tests/                 # 测试用例
    └── test_scenario.py
```

### 案例模板

```markdown
# 案例名称

## 一句话风险
[风险描述，一句话说明]

## 风险等级
- 严重程度: 🔴严重 / 🟠高 / 🟡中 / 🟢低
- 影响范围: [影响范围]
- 发生概率: [概率评估]

## 场景描述
[详细场景描述]

## 攻击方式
[攻击者如何利用]

## 真实案例
[真实案例链接或描述]

## 防御建议
### 立即行动 (5分钟)
- [ ] [行动1]
- [ ] [行动2]

### 短期加固 (1小时)
- [ ] [行动1]
- [ ] [行动2]

### 长期建设
- [ ] [行动1]
- [ ] [行动2]

## 检测方法
[如何检测此问题]

## 代码示例
[防御代码示例]

## 参考资料
- [参考链接1]
- [参考链接2]
```

---

## 技术架构

### 目录结构

```
oh-my-security/
├── bin/                    # CLI 入口
│   └── oms
├── oms_core/               # 核心框架
│   ├── base.py            # 基类
│   ├── scanner.py         # 扫描器
│   ├── reporter.py        # 报告生成
│   └── utils.py           # 工具函数
├── scenarios/              # 场景模块
│   ├── code/              # 代码审计
│   ├── content/           # 内容风控
│   ├── bizsec/            # 业务安全
│   ├── vps/               # VPS加固
│   ├── payment/           # 支付安全
│   ├── account/           # 账号安全
│   ├── deps/              # 依赖安全
│   ├── domain/            # 域名资产
│   ├── ai/                # AI安全
│   ├── incident/          # 应急响应
│   ├── mobile/            # 移动设备
│   ├── social/            # 社媒账号
│   ├── crypto/            # 加密资产
│   └── compliance/        # 合规自查
├── knowledge_base/         # 知识库
│   ├── cases/             # 案例库
│   ├── weapons/           # 武器库
│   ├── modules/           # 模块
│   └── tools/             # 工具
├── plugins/                # 插件
├── tests/                  # 测试
└── docs/                   # 文档
```

### CLI 命令规范

```bash
# 统一命令格式
oms <scenario> [action] [options]

# 示例
oms code scan ./src              # 扫描代码
oms code check --pre-commit      # 提交前检查
oms content scan article.md      # 扫描内容
oms payment audit                # 支付审计
oms incident playbook breached   # 应急剧本

# 通用选项
--format json/yaml/markdown      # 输出格式
--severity critical/high/medium  # 严重程度过滤
--output report.md               # 输出文件
--quiet                          # 静默模式
--verbose                        # 详细模式
```

### 技术栈

| 类别 | 技术 | 用途 |
|------|------|------|
| 语言 | Python 3.8+ | 核心实现 |
| CLI | Click / Typer | 命令行框架 |
| 配置 | YAML / TOML | 配置文件 |
| 模板 | Jinja2 | 报告生成 |
| HTTP | httpx | API 调用 |
| 解析 | tree-sitter | 代码解析 |
| 漏洞 | OSV / CVE | 漏洞数据 |
| AI | OpenAI / Claude | AI 增强 |

---

## 资源需求

### 人力需求

| 阶段 | 角色 | 工作量 |
|------|------|--------|
| Phase 0-1 | 安全专家 | 40h/周 × 4周 |
| Phase 2 | 安全专家 | 40h/周 × 4周 |
| Phase 3 | 安全专家 | 20h/周 × 4周 |
| Phase 4 | 全栈开发 | 40h/周 × 2周 |

### 外部资源

| 资源 | 用途 | 成本 |
|------|------|------|
| OSV API | 漏洞数据 | 免费 |
| CVE 数据库 | 漏洞数据 | 免费 |
| npm/pypi API | 包信息 | 免费 |
| 域名 WHOIS | 域名信息 | 免费 |
| AI API | AI 增强 | 按用量 |

---

## 风险评估

### 技术风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| AI API 成本过高 | 中 | 高 | 提供离线模式，用户自备 API Key |
| 漏洞数据源不稳定 | 低 | 中 | 多数据源备份，本地缓存 |
| 依赖解析复杂 | 中 | 中 | 使用成熟解析库，限制语言范围 |

### 项目风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 案例质量不均 | 中 | 高 | 建立审核机制，社区贡献 |
| 维护负担重 | 高 | 中 | 自动化测试，社区维护 |
| 用户反馈少 | 中 | 中 | 建立社区渠道，主动收集 |

---

## 里程碑

| 版本 | 时间 | 内容 |
|------|------|------|
| v0.2.0 | Week 2 | 基础完善，开发规范 |
| v0.3.0 | Week 6 | P0 场景完成 |
| v0.4.0 | Week 10 | P1 场景完成 |
| v0.5.0 | Week 14 | P2 场景完成 |
| v1.0.0 | Week 16 | 正式发布 |

---

## 下一步行动

### 本周任务 (Week 1)

- [ ] 完善现有 4 个场景文档
- [ ] 创建场景开发模板
- [ ] 编写 CLI 命令规范
- [ ] 补充核心案例至 100 个
- [ ] 创建贡献者指南

### 即时行动

1. **创建开发分支**: `git checkout -b feature/scenario-expansion`
2. **更新 README**: 添加新场景说明
3. **创建模板**: 编写场景/案例模板
4. **开始第一个场景**: `oms payment`

---

> 🚀 **Let's build the security toolkit for indie developers!**
