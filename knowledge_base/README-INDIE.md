# 🛡️ Oh-My-Security 独立开发者快速入门

> 专为独立开发者设计的安全知识库，5分钟上手，30分钟核心防护。

---

## 🎯 你是谁？

如果你符合以下特征，这个知识库就是为你准备的：

- ✅ 独立开发者 / Indie Hacker / 自媒体创作者
- ✅ 1人维护的全栈项目
- ✅ 安全预算接近零
- ✅ 安全投入 < 总开发时间 5%
- ✅ 希望快速获得可落地的防御方案

---

## 🚀 5分钟快速开始

### 场景 1: 我要上线 MVP

👉 直接查看 **[MVP 发布检查清单](./modules/mvp-checklist/README.md)**

```
10 分钟检查 40+ 安全项
确保上线前不遗漏关键防护
```

### 场景 2: 我遇到了安全问题

👉 在 **[核心案例库](./cases/indie/core/)** 中搜索你的问题

```
常见问题：
- 账号被盗 → auth/credential-stuffing.md
- 支付漏洞 → payment/parameter-tampering.md
- 数据泄露 → data/database-exposure.md
- API 被攻击 → api/sql-injection.md
- AI 安全 → ai/prompt-injection.md
```

### 场景 3: 我想系统学习安全

👉 跟随 **[独立开发者起步套件](./modules/indie-starter/README.md)**

```
5 周渐进式学习路径
每周 1-2 小时
建立完整安全防护体系
```

---

## 📚 知识库结构

```
knowledge_base/
├── cases/indie/           # 案例库
│   ├── core/              # 核心案例 (50个 L1+L2)
│   │   ├── auth/         # 认证安全
│   │   ├── data/         # 数据安全
│   │   ├── api/          # API安全
│   │   ├── payment/      # 支付安全
│   │   └── ai/           # AI安全
│   └── extended/          # 扩展案例 (L1骨架版)
│
├── weapons/indie/         # 武器库 (30个)
│   ├── free-tier/        # 免费层服务
│   ├── open-source/      # 开源工具
│   └── saas/             # 低成本SaaS
│
├── modules/               # 模块化路径
│   ├── indie-starter/    # 5周起步套件
│   ├── mvp-checklist/    # MVP检查清单
│   └── incident-playbook/ # 应急响应剧本
│
└── tools/                 # 辅助工具
    ├── case-coverage-checker.py
    ├── weapon-validator.py
    └── quality-linter.py
```

---

## 🔥 核心案例速查

### 认证安全 (11个)

| 案例 | 一句话风险 | 严重程度 |
|------|-----------|---------|
| [撞库攻击](./cases/indie/core/auth/credential-stuffing.md) | 用户密码泄露后被批量尝试登录 | 🔴 严重 |
| [弱密码](./cases/indie/core/auth/weak-password.md) | 用户使用简单密码导致账号被盗 | 🔴 严重 |
| [Session劫持](./cases/indie/core/auth/session-hijacking.md) | 攻击者窃取用户会话冒充操作 | 🔴 严重 |
| [暴力破解](./cases/indie/core/auth/brute-force.md) | 攻击者通过大量尝试破解密码 | 🟠 高 |
| [账号接管](./cases/indie/core/auth/account-takeover.md) | 攻击者完全控制用户账号 | 🔴 严重 |

### 支付安全 (11个)

| 案例 | 一句话风险 | 严重程度 |
|------|-----------|---------|
| [参数篡改](./cases/indie/core/payment/parameter-tampering.md) | 前端价格被修改导致财务损失 | 🔴 严重 |
| [零元订单](./cases/indie/core/payment/zero-order-attack.md) | 支付金额为0免费获取商品 | 🔴 严重 |
| [双花攻击](./cases/indie/core/payment/double-spending.md) | 同一笔支付被重复使用 | 🔴 严重 |
| [退款欺诈](./cases/indie/core/payment/refund-fraud.md) | 用户购买后恶意申请退款 | 🟠 高 |
| [回调伪造](./cases/indie/core/payment/callback-fraud.md) | 伪造支付成功回调绕过支付 | 🔴 严重 |

### 数据安全 (11个)

| 案例 | 一句话风险 | 严重程度 |
|------|-----------|---------|
| [数据库暴露](./cases/indie/core/data/database-exposure.md) | 云数据库无认证暴露在公网 | 🔴 严重 |
| [GitHub密钥泄露](./cases/indie/core/data/github-secret-leak.md) | 代码提交包含API Key | 🔴 严重 |
| [备份泄露](./cases/indie/core/data/backup-leak.md) | 数据库备份文件放在公开目录 | 🔴 严重 |
| [Redis未授权](./cases/indie/core/data/redis-exposure.md) | Redis无密码暴露公网 | 🔴 严重 |
| [日志敏感信息](./cases/indie/core/data/log-sensitive.md) | 日志记录密码/令牌等 | 🟠 高 |

### API安全 (11个)

| 案例 | 一句话风险 | 严重程度 |
|------|-----------|---------|
| [SQL注入](./cases/indie/core/api/sql-injection.md) | 用户输入导致数据库被篡改 | 🔴 严重 |
| [XSS攻击](./cases/indie/core/api/xss-attack.md) | 恶意脚本在其他用户浏览器执行 | 🔴 严重 |
| [CSRF攻击](./cases/indie/core/api/csrf-attack.md) | 诱导用户执行非预期操作 | 🟠 高 |
| [API未授权](./cases/indie/core/api/unauthorized-access.md) | API无需认证即可访问 | 🔴 严重 |
| [文件上传攻击](./cases/indie/core/api/file-upload-attack.md) | 上传恶意文件获取服务器权限 | 🔴 严重 |

### AI安全 (6个)

| 案例 | 一句话风险 | 严重程度 |
|------|-----------|---------|
| [Prompt注入](./cases/indie/core/ai/prompt-injection.md) | 用户输入覆盖系统指令 | 🔴 严重 |
| [数据窃取](./cases/indie/core/ai/data-exfiltration.md) | 诱导AI泄露训练数据 | 🔴 严重 |
| [成本滥用](./cases/indie/core/ai/cost-abuse.md) | 大量调用AI API导致巨额账单 | 🟠 高 |
| [越狱攻击](./cases/indie/core/ai/jailbreak-attack.md) | 绕过AI安全限制 | 🟠 高 |
| [幻觉风险](./cases/indie/core/ai/hallucination-risk.md) | AI生成虚假信息误导用户 | 🟡 中 |

---

## ⚔️ 核心武器推荐

### 必备武器 (Top 5)

| 武器 | 用途 | 成本 |
|------|------|------|
| [安全基线](./weapons/indie/free-tier/indie-security-baseline.md) | 13项必做安全配置 | 免费 |
| [快速防御清单](./weapons/indie/free-tier/quick-defense-checklist.md) | 10分钟防御清单 | 免费 |
| [免费技术栈](./weapons/indie/free-tier/free-security-stack.md) | 免费安全技术栈图谱 | 免费 |
| [限流方案](./weapons/indie/open-source/rate-limiting-simple.md) | 防止API被滥用 | 免费 |
| [API认证指南](./weapons/indie/open-source/api-auth-guide.md) | 5种认证方式对比 | 免费 |

### 免费工具推荐

| 类别 | 工具 | 免费额度 |
|------|------|---------|
| 认证 | Auth0 | 7,000 MAU/月 |
| 认证 | Supabase Auth | 50,000 MAU/月 |
| 监控 | Sentry | 5,000 错误/月 |
| 监控 | UptimeRobot | 50 监控/5分钟检查 |
| CDN | Cloudflare | 无限流量 |
| 备份 | AWS S3 | 5GB 存储/月 |

---

## 📋 学习路径

### 路径 1: 快速上线 (1小时)

```
1. 阅读 MVP 发布检查清单 (10分钟)
2. 完成前 10 项必做配置 (30分钟)
3. 运行安全检查脚本 (10分钟)
4. 部署基础监控 (10分钟)
```

### 路径 2: 系统学习 (5周)

```
Week 1: 安全基线 → 10项必做配置
Week 2: 账号安全 → 密码策略 + MFA
Week 3: API安全 → 认证 + 限流
Week 4: 数据保护 → 加密 + 备份
Week 5: 监控告警 → 持续运营
```

### 路径 3: 应急响应 (随时)

```
出事了？直接看应急响应剧本
→ 评估严重性
→ 采取行动
→ 恢复服务
→ 复盘改进
```

---

## 🆘 常见问题

### Q: 我没有安全经验，能用吗？

A: 可以！所有内容都设计为独立开发者友好，包含：
- 一分钟识别清单
- 一句话防御建议
- 可直接运行的代码示例

### Q: 真的免费吗？

A: 是的！所有推荐方案都有免费选项，总成本 $0。

### Q: 实施需要多久？

A: 核心防护措施 30 分钟内可实施。完整安全体系约 5 周（每周 1-2 小时）。

### Q: 出了安全问题怎么办？

A: 查看 [应急响应剧本](./modules/incident-playbook/README.md)，按流程处理。

---

## 📞 获取帮助

- **查阅案例库**: [cases/indie/core/](./cases/indie/core/)
- **查阅武器库**: [weapons/indie/](./weapons/indie/)
- **运行检查工具**: `python tools/case-coverage-checker.py`

---

## 🎉 开始你的安全之旅

**立即开始**: [MVP 发布检查清单](./modules/mvp-checklist/README.md) ← 10分钟完成上线前检查

**系统学习**: [独立开发者起步套件](./modules/indie-starter/README.md) ← 5周建立完整防护

---

> 记住：**安全不需要完美，但需要行动**。从今天开始，完成第一项配置！
