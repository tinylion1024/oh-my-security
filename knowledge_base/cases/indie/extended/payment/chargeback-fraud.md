# 拒付欺诈

## 元数据

| 字段 | 值 |
|------|-----|
| 编号 | PAY-006 |
| 领域 | 支付安全 |
| 适用层级 | L1 ✅ |
| 创建日期 | 2026-06-11 |

---

## 一句话风险

消费者在收到商品后恶意发起拒付（Chargeback），导致商家货物与款项双重损失。

---

## 一分钟识别清单

- [ ] **交易证据链**：是否保存完整的交易日志、发货记录和签收证明？
- [ ] **高风险订单标记**：是否对新地址、大额订单或高风险地区订单增加验证？
- [ ] **拒付率监控**：商户拒付率是否超过 1% 的银行卡网络警戒线？

---

## 一句话防御

建立完整的交易证据链（IP、设备指纹、签收记录），对高风险订单实施地址验证（AVS）和 3D Secure 认证。

---

## 推荐工具链接

| 工具 | 用途 | 链接 |
|------|------|------|
| Stripe Chargeback Protection | 拒付保护服务 | https://stripe.com/docs/radar/chargeback-protection |
| 3D Secure | 身份验证协议 | https://www.emvco.com/emv-technologies/3d-secure/ |
| Visa AVS | 地址验证服务 | https://usa.visa.com/ |

---

## 相关案例

- [礼品卡欺诈](./gift-card-fraud.md)
- [收据篡改](./receipt-manipulation.md)
