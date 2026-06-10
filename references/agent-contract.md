# Agent 协作契约

## 1. 交互规范
所有 Agent 之间的信息传递必须遵循结构化数据格式，确保可解析性。

## 2. 核心链路数据结构

### Red -> Blue: 威胁向量 (Threat Vector)
- `attack_path`: 完整的利用链描述。
- `cwe_id`: 对应的 CWE 分类。
- `preconditions`: 攻击成功的先决条件。
- `impact_cia`: 机密性、完整性、可用性的损耗评级。

### Blue -> Biz: 防御开销 (Defense Overhead)
- `latency_impact`: 预计增加的毫秒数。
- `ux_friction`: 用户交互干扰评级 (1-10)。
- `ops_cost`: 维护与部署成本预估。

### Compliance -> Lead: 合规约束 (Compliance Constraints)
- `mandatory_controls`: 必须实现的控制项。
- `legal_risk`: 违反后可能面临的法律后果。

## 3. 冲突解决协议
1. **硬冲突**：如果安全要求与法律合规冲突，合规权重大于安全。
2. **软冲突**：如果安全要求与业务性能冲突，由 Lead Agent 引入 Skeptic Agent 进行第三方评估，输出 2-3 种不同强度的方案供用户选择。
