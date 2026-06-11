# 积分欺诈

## 元数据

| 字段 | 值 |
|------|-----|
| 编号 | PAY-004 |
| 领域 | 支付安全 |
| 适用层级 | L1 ✅ |
| 创建日期 | 2026-06-11 |

---

## 一句话风险

攻击者通过虚假交易、批量注册账户或利用积分规则漏洞非法获取或消耗积分。

---

## 一分钟识别清单

- [ ] **积分来源追踪**：是否记录每笔积分的来源（消费、活动、赠送）并可审计？
- [ ] **账户关联检测**：是否识别同一设备/IP 注册的多账户积分转移行为？
- [ ] **异常积分变动**：是否存在短时间内大量积分获取或消耗的异常模式？

---

## 一句话防御

建立积分生命周期追踪系统，实施账户关联检测和异常行为风控，对高风险积分操作增加延时确认机制。

---

## 推荐工具链接

| 工具 | 用途 | 链接 |
|------|------|------|
| FraudLabs Pro | 欺诈检测服务 | https://www.fraudlabspro.com/ |
| Redis Rate Limiting | 积分操作限频 | https://redis.io/glossary/rate-limiting/ |
| OWASP Session Management | 会话管理 | https://owasp.org/www-community/vulnerabilities/Broken_Authentication |

---

## 相关案例

- [折扣滥用](./discount-abuse.md)
- [礼品卡欺诈](./gift-card-fraud.md)
