# 报告输出契约 (Report Contract)

## 1. 强制性字段
所有正式输出的策略报告必须包含以下字段：

- **风险等级 (Risk Rating)**: [Critical/High/Medium/Low]
- **核心风险点 (Core Findings)**: 简明扼要的 1-3 点风险。
- **治理建议 (Recommendations)**: 分为 `Immediate` (立即修复), `Strategic` (架构优化), `Monitoring` (持续监测)。
- **合规结论 (Compliance Status)**: 是否符合特定的法规标准。
- **证据支撑 (Evidence)**: 引用 `knowledge/cases/` 或 `knowledge/weapons/`。

## 2. 报告质量标准
1. **可执行性**: 必须包含具体的修复步骤或推荐的工具。
2. **逻辑一致性**: 红队的攻击路径必须被蓝队的防御方案覆盖，且被怀疑论者挑战过。
3. **数据支撑**: 如果包含风险评分，必须附带评分逻辑说明。
