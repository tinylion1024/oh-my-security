# 零信任 (Zero Trust) 架构

## 1. 核心设计哲学
“永不信任，始终验证 (Never Trust, Always Verify)”。

## 2. 三大核心原则
1. **持续验证**: 基于身份、位置、设备健康状况、服务或资产的多维度实时验证，而不仅仅是网络位置。
2. **最小权限 (Least Privilege)**: 仅在需要时授予刚好足够的权限，并尽可能缩短权限生命周期。
3. **假定已失陷 (Assume Breach)**: 最小化受影响范围（爆炸半径），对流量进行加密，确保持续的监控和检测。

## 3. 落地技术架构 (PEA)
- **策略引擎 (Policy Engine)**: 负责决定是否授权。
- **策略管理器 (Policy Administrator)**: 负责建立或断开通信连接。
- **策略执行点 (Policy Enforcement Point)**: 拦截并检查访问。
