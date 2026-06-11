# 支付重放攻击

## 元数据

| 字段 | 值 |
|------|-----|
| 编号 | PAY-001 |
| 领域 | 支付安全 |
| 适用层级 | L1 ✅ |
| 创建日期 | 2026-06-11 |

---

## 一句话风险

攻击者截获合法支付请求并重复提交，导致重复扣款或多次发货。

---

## 一分钟识别清单

- [ ] **检查幂等性**：支付接口是否实现了幂等键（Idempotency Key）机制？
- [ ] **验证时间戳**：请求是否包含防重放的时间戳校验（建议 5-15 分钟窗口）？
- [ ] **审计日志异常**：是否存在相同订单号的多次成功支付记录？

---

## 一句话防御

为每笔支付生成唯一幂等键，服务端验证并拒绝重复请求，同时设置合理的请求过期时间。

---

## 推荐工具链接

| 工具 | 用途 | 链接 |
|------|------|------|
| Stripe Idempotency | 支付幂等性最佳实践 | https://stripe.com/docs/api/idempotent_requests |
| OWASP API Security | API 安全 Top 10 | https://owasp.org/www-project-api-security/ |
| JWT.io | Token 时间戳验证 | https://jwt.io/ |

---

## 相关案例

- [订单篡改](./order-manipulation.md)
- [支付网关绕过](./payment-gateway-bypass.md)
