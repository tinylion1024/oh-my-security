# 管理员默认凭据 (Admin Default Credentials)

## 元数据

| 字段 | 值 |
|------|-----|
| **案例 ID** | AUTH-004 |
| **分类** | 认证安全 |
| **适用层级** | L1 ✅ |
| **创建时间** | 2026-06-11 |
| **更新时间** | 2026-06-11 |

---

## 一句话风险

系统部署后未修改默认管理员账号密码，攻击者使用已知凭据列表直接登录获取管理员权限。

---

## 一分钟识别清单

### 2-3 项核心指标

- [ ] **默认凭据未变更**
  安装向导跳过密码设置，或文档中可查到默认账号密码

- [ ] **弱密码策略**
  管理员密码为 `admin`、`123456`、`password` 等常见弱密码

- [ ] **首次登录无强制修改**
  首次使用默认凭据登录后，系统未强制要求修改密码

---

## 一句话防御

**部署时强制设置唯一管理员密码，禁止使用默认凭据，首次登录强制修改密码。**

---

## 推荐工具链接

| 类型 | 工具/资源 |
|------|----------|
| 默认密码库 | [DefaultCreds-cheat-sheet](https://github.com/ihebski/DefaultCreds-cheat-sheet) |
| 密码审计 | [Hydra](https://github.com/vanhauser-thc/thc-hydra) |
| 弱密码检测 | [SecLists Passwords](https://github.com/danielmiessler/SecLists/tree/master/Passwords) |
| 学习资源 | [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) |

---

## 相关案例

- `captcha-bypass.md` - 验证码绕过
- `account-enumeration.md` - 账号枚举

---

## 参考资料

- [OWASP: Default Passwords](https://owasp.org/www-community/vulnerabilities/Use_of_default_password)
- [CIS Benchmark: Authentication](https://www.cisecurity.org/cis-benchmarks)
