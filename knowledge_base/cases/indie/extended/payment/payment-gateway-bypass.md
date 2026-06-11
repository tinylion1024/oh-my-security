# 支付网关绕过

## 元数据

| 字段 | 值 |
|------|-----|
| 编号 | PAY-007 |
| 领域 | 支付安全 |
| 适用层级 | L1 ✅ |
| 创建日期 | 2026-06-11 |

---

## 一句话风险

攻击者绕过正常支付流程，直接调用后端接口或篡改支付状态参数，实现"零元购"。

---

## 一分钟识别清单

- [ ] **支付状态验证**：订单状态是否依赖支付网关的 Webhook 回调而非客户端参数？
- [ ] **接口访问控制**：支付回调接口是否验证来源签名？
- [ ] **订单状态一致性**：是否存在订单状态为"已支付"但支付网关无对应成功记录？

---

## 一句话防御

支付成功状态必须以支付网关的服务端回调为准，所有支付状态变更需签名验证并记录审计日志。

---

## 推荐工具链接

| 工具 | 用途 | 链接 |
|------|------|------|
| Stripe Webhooks | 支付回调验证 | https://stripe.com/docs/webhooks |
| PayPal IPN | 即时支付通知 | https://developer.paypal.com/api/nvp-soap/ipn/ |
| OWASP Broken Access Control | 访问控制漏洞 | https://owasp.org/Top10/A01_2021-Broken_Access_Control/ |

---

## 相关案例

- [支付重放攻击](./payment-replay.md)
- [订单篡改](./order-manipulation.md)
