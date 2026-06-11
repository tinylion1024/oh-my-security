# 部分支付欺诈

## 元数据

| 字段 | 值 |
|------|-----|
| 编号 | PAY-008 |
| 领域 | 支付安全 |
| 适用层级 | L1 ✅ |
| 创建日期 | 2026-06-11 |

---

## 一句话风险

攻击者利用部分支付或分期支付的逻辑漏洞，支付部分款项后取消或修改订单，导致商家损失。

---

## 一分钟识别清单

- [ ] **支付完整性校验**：订单是否在全部款项到账后才标记为可发货？
- [ ] **部分退款逻辑**：部分退款后是否会同步更新订单状态和库存？
- [ ] **支付状态一致性**：是否存在订单金额与实际支付金额不一致的记录？

---

## 一句话防御

实施严格的支付完整性校验，订单仅在全部款项确认到账后方可履行，部分退款需同步更新订单状态。

---

## 推荐工具链接

| 工具 | 用途 | 链接 |
|------|------|------|
| Stripe Partial Capture | 部分捕获逻辑 | https://stripe.com/docs/payments/capture-later |
| Order State Machine | 订单状态机设计 | https://statecharts.dev/ |
| OWASP Business Logic | 业务逻辑漏洞 | https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerabilities |

---

## 相关案例

- [订单篡改](./order-manipulation.md)
- [结算欺诈](./settlement-fraud.md)
