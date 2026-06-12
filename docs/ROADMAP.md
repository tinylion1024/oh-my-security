# Oh-My-Security 开发路线图

> 快速查看版本 - 详细计划见 [DEVELOPMENT-PLAN.md](./DEVELOPMENT-PLAN.md)

---

## 🗓️ 时间线总览

```
Week 1-2   │ Phase 0: 基础完善
Week 3-6   │ Phase 1: P0 场景 (破产级风险)
Week 7-10  │ Phase 2: P1 场景 (高风险)
Week 11-14 │ Phase 3: P2 场景 (中等风险)
Week 15-16 │ Phase 4: 完善发布
```

---

## 📊 场景矩阵

### ✅ 已完成 (4个)

| 场景 | 命令 | 状态 |
|------|------|------|
| 代码审计 | `oms code` | ✅ |
| 内容风控 | `oms content` | ✅ |
| 业务安全 | `oms bizsec` | ✅ |
| VPS加固 | `oms vps` | ✅ |

### 🔴 P0 - 破产级风险 (Week 3-6)

| 场景 | 命令 | 风险 | 开发周 |
|------|------|------|--------|
| 支付安全 | `oms payment` | 直接经济损失 | Week 3-4 |
| 账号安全 | `oms account` | 账号=资产 | Week 5 |
| 依赖安全 | `oms deps` | 供应链攻击 | Week 6 |

### 🟠 P1 - 高风险 (Week 7-10)

| 场景 | 命令 | 风险 | 开发周 |
|------|------|------|--------|
| 域名资产 | `oms domain` | 网站瘫痪 | Week 7 |
| AI安全 | `oms ai` | 新场景风险 | Week 8 |
| 应急响应 | `oms incident` | 危机处理 | Week 9-10 |

### 🟡 P2 - 中等风险 (Week 11-14)

| 场景 | 命令 | 风险 | 开发周 |
|------|------|------|--------|
| 移动设备 | `oms mobile` | 设备安全 | Week 11 |
| 社媒账号 | `oms social` | 品牌受损 | Week 12 |
| 加密资产 | `oms crypto` | Web3风险 | Week 13 |
| 合规自查 | `oms compliance` | 法律风险 | Week 14 |

---

## 🎯 版本里程碑

```
v0.2.0 ─────► v0.3.0 ─────► v0.4.0 ─────► v0.5.0 ─────► v1.0.0
Week 2        Week 6        Week 10       Week 14       Week 16
  │             │             │             │             │
  ▼             ▼             ▼             ▼             ▼
基础完善      P0完成        P1完成        P2完成        正式发布
```

| 版本 | 时间 | 交付物 |
|------|------|--------|
| v0.2.0 | Week 2 | 开发规范、模板、100案例 |
| v0.3.0 | Week 6 | payment + account + deps |
| v0.4.0 | Week 10 | domain + ai + incident |
| v0.5.0 | Week 14 | mobile + social + crypto + compliance |
| v1.0.0 | Week 16 | 300+案例、完整文档、正式发布 |

---

## 📈 案例库增长

```
现有 ──────► Phase 1 ──────► Phase 2 ──────► Phase 3 ──────► 发布
50个          +30个           +30个           +40个          300+
              (P0场景)        (P1场景)        (P2场景)
```

---

## 🚀 下一步

1. **本周**: 完善现有场景文档，创建开发模板
2. **下周**: 开始 `oms payment` 开发
3. **持续**: 每个场景 10+ 案例，配套武器库

---

> 详细计划: [DEVELOPMENT-PLAN.md](./DEVELOPMENT-PLAN.md)
