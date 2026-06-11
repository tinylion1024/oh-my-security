# 折扣滥用

## 元数据

| 字段 | 值 |
|------|-----|
| 编号 | PAY-003 |
| 领域 | 支付安全 |
| 适用层级 | L1 ✅ |
| 创建日期 | 2026-06-11 |

---

## 一句话风险

攻击者通过重复使用优惠券、叠加折扣或利用逻辑漏洞获取不当优惠。

---

## 一分钟识别清单

- [ ] **优惠券使用限制**：是否限制每个用户/设备/IP 使用优惠券的次数？
- [ ] **折扣叠加规则**：是否禁止或严格控制多折扣叠加使用？
- [ ] **异常折扣率**：是否存在订单折扣率异常高（如超过 50%）的集中使用？

---

## 一句话防御

实施优惠券单次使用限制、设备指纹识别和折扣叠加规则校验，对异常高折扣订单进行人工审核。

---

## 推荐工具链接

| 工具 | 用途 | 链接 |
|------|------|------|
| FingerprintJS | 设备指纹识别 | https://github.com/fingerprintjs/fingerprintjs |
| Coupon Fraud Prevention | 折扣滥用防护 | https://stripe.com/docs/radar |
| OWASP Business Logic | 业务逻辑漏洞 | https://owasp.org/www-community/vulnerabilities/Business_logic_vulnerabilities |

---

## 相关案例

- [订单篡改](./order-manipulation.md)
- [礼品卡欺诈](./gift-card-fraud.md)
