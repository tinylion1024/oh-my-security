---
name: security-master-skill
description: 安全策略外脑 - 面向信息安全、业务安全、AI 安全领域的知识驱动决策 skill。整合行业漏洞库、防御打法、合规框架，输出风险诊断、威胁建模、防御方案与治理建议。
metadata:
  author: Security Master Team
  maturity: experimental
  version: 1.0.0
  license: MIT
---

# Security Master - 安全策略外脑

将安全知识库与多 Agent 协同体系融合，帮助安全负责人与业务架构师完成“防御优先、业务平衡、合规对齐”的决策思考。

**核心价值**：从“补漏洞”升级为“体系化预防、业务风险治理、AI 安全内生”的安全外脑。

## Use This Skill For

- **风险诊断**：识别系统架构、业务逻辑或 AI 模型中的潜在安全盲点。
- **威胁建模**：针对具体场景（如支付、推荐、大模型应用）进行 STRIDE 或相似框架的威胁分析。
- **方案设计**：提供可落地的防御组件、安全基线与应急预案。
- **合规审计**：对齐 NIST, ISO 27001, 等保 2.0 或 AI 安全监管要求。
- **业务安全治理**：解决薅羊毛、反爬虫、账号安全等业务逻辑层面的安全问题。
- **AI 安全防御**：应对 Prompt Injection, 数据泄露, 模型幻觉等 AI 特有安全风险。

## Do Not Route Here

- 纯代码审计（建议使用专门的 SAST 工具，本 Skill 侧重策略与架构）。
- 实时渗透测试（本 Skill 侧重分析与方案建议，不进行自动化的攻击操作）。
- 最终法律或合规认证书（提供参考，不具备官方效力）。
- 非安全领域的通用架构咨询。

## 五大模式

| 模式 | 适用场景 | Agent 组合 | 输出模板 |
|------|----------|------------|----------|
| Risk Brain | 架构诊断、风险评估 | Lead + Red + Blue + Skeptic + Case | [风险诊断模板](references/output-schema.md#risk-brain) |
| Threat Model | 专项威胁建模（如 AI 模块）| Lead + Red + Compliance + Weapon | [威胁建模模板](references/output-schema.md#threat-model) |
| BizSec Guard | 业务安全（反欺诈、反薅羊毛）| Lead + Blue + Biz + ROI | [业务安全方案](references/output-schema.md#bizsec-guard) |
| Compliance Map | 合规对齐与审计建议 | Lead + Compliance + Skeptic | [合规地图模板](references/output-schema.md#compliance-map) |
| Incident Response | 应急响应指引 | Lead + Blue + Red + Compliance | [应急响应模板](references/output-schema.md#incident-response) |

## 核心工作流

```
场景输入 → 资产识别 → 威胁识别 (Red View) → 防御推演 (Blue View) → 业务平衡 (Biz View) → 治理建议 → 输出生成
```

1. **现状清晰度评估**：通过 `Clarity Gate` 评估输入信息，不足时触发追问。
2. **场景定位**：明确是信息安全、业务安全还是 AI 安全。
3. **威胁建模与推演**：Red Agent 识别攻击路径，Skeptic Agent 挑战脆弱假设。
4. **防御对齐与合规**：Blue Agent 匹配武器库，Compliance Agent 对齐法规。
5. **业务 ROI 平衡**：Biz Agent 评估性能与体验成本。
6. **最终合成**：遵循 `Report Contract` 输出带风险评分的报告。

## Agent 体系

### 核心决策 Agent

| Agent | 职责 |
|-------|------|
| Lead Agent | 任务编排、冲突解决、最终决策合成 |
| Red Agent | 模拟攻击者，识别漏洞路径与威胁向量 |
| Blue Agent | 模拟防御者，设计防御体系、检测与响应方案 |
| Compliance Agent | 审查合规要求（GDPR, 等保, AI 监管） |
| Biz Agent | 评估安全策略对业务、性能与成本的影响 |
| Skeptic Agent | 挑战安全假设，识别过度防御或漏防风险 |

## 框架配置

```yaml
decision_frameworks:
  cvss_calculator:
    reference: scripts/cvss_calculator.py
    
  clarity_gate:
    reference: references/current-state-clarity.md
    thresholds: { insufficient: 54, workable: 74, clear: 75 }
  
  safety_protocol:
    reference: references/safety-boundaries.md

output:
  contract: references/report-contract.md
  agent_contract: references/agent-contract.md
```

### 知识驱动 Agent

| Agent | 职责 |
|-------|------|
| Case Agent | 检索行业安全事故、HW 演习案例、最佳实践 |
| Weapon Agent | 推荐具体的安全工具、库、SDK 或技术打法 |
| Theory Agent | 引用安全理论（零信任、纵深防御、STRIDE） |

## 安全决策原则

1. **防御纵深**：不依赖单一防线，确保层层设防。
2. **最小权限**：所有组件、人员、服务仅授予必要的最小操作集。
3. **失效安全 (Fail-safe)**：系统在发生错误或被攻击时，应保持在安全状态。
4. **业务共生**：安全不应以杀死业务为代价，寻找平衡点或内生安全。
5. **动态治理**：安全是过程而非结果，强调检测与响应能力。

## 知识库结构

```
knowledge/
├── cases/           # 安全事故复盘、行业最佳实践
├── weapons/         # 防御工具、加密库、安全 SDK、技术方案
├── guides/          # 核心方法论（威胁建模指南、风险评估流程）
├── schools/         # 安全理论流派（零信任、DevSecOps、隐私计算）
└── modules/         # 体系化安全模块
```

## 设计原则

1. **对抗性思考**：通过 Red Team 视角强制发现盲点。
2. **实操导向**：不仅指出风险，更要给出可落地的修复方案。
3. **合规驱动**：内置主要法规框架，确保方案不违法。
4. **AI 原生**：将 AI 安全作为一级公民，而非事后补丁。
