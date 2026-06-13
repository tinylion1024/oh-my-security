# 账号安全检查清单

> 10分钟快速检查你的账号系统是否存在致命漏洞

---

## 🔴 必须检查 (Critical)

### 密码安全
- [ ] **密码强度**: 是否强制要求密码长度 >= 8 位？
- [ ] **密码复杂度**: 是否要求包含大小写字母、数字、特殊字符？
- [ ] **弱密码检测**: 是否检测常见弱密码（123456, password 等）？
- [ ] **密码存储**: 是否使用 bcrypt/Argon2 等安全哈希？

### 认证安全
- [ ] **MFA/2FA**: 是否支持多因素认证？
- [ ] **登录频率限制**: 是否限制登录尝试次数？
- [ ] **验证码保护**: 是否在登录失败后显示验证码？
- [ ] **异常登录检测**: 是否检测异常登录行为？

### Session 安全
- [ ] **Cookie HttpOnly**: Cookie 是否设置 HttpOnly？
- [ ] **Cookie Secure**: Cookie 是否设置 Secure（仅 HTTPS）？
- [ ] **Session 过期**: Session 是否有合理的过期时间？
- [ ] **Session 固定**: 是否防止 Session 固定攻击？

---

## 🟠 重要检查 (High)

### 密码恢复
- [ ] **恢复链接**: 密码恢复链接是否一次性使用？
- [ ] **恢复过期**: 恢复链接是否有过期时间？
- [ ] **身份验证**: 恢复前是否验证用户身份？
- [ ] **通知机制**: 密码修改是否通知用户？

### OAuth 安全
- [ ] **State 参数**: OAuth 是否验证 state 参数？
- [ ] **Redirect URI**: 是否验证 redirect_uri 白名单？
- [ ] **Token 存储**: OAuth token 是否安全存储？
- [ ] **Scope 限制**: 是否限制最小必要 scope？

---

## 🟡 建议检查 (Medium)

### 登录体验
- [ ] **登录提示**: 是否提供清晰的错误提示？
- [ ] **记住设备**: 是否支持可信设备记住？
- [ ] **多设备管理**: 是否支持查看/踢出其他设备？
- [ ] **登录历史**: 是否记录登录历史？

### API 安全
- [ ] **API Key 轮换**: API Key 是否支持轮换？
- [ ] **Token 过期**: Access token 是否有过期时间？
- [ ] **Refresh token**: Refresh token 是否安全存储？
- [ ] **权限最小化**: 是否遵循最小权限原则？

---

## 📋 快速自测命令

```bash
# 审计账号安全配置
oms account check ./src

# 检测密码强度
oms account password-strength "your-password"

# 查看 2FA 配置指南
oms account 2fa-guide

# 查看账号安全最佳实践
oms account guide
```

---

## 🆘 发现问题怎么办？

1. **立即修复**: Critical 级别问题必须立即修复
2. **短期加固**: High 级别问题建议一周内修复
3. **持续改进**: Medium 级别问题纳入迭代计划

---

## 📞 相关资源

- [撞库攻击](../cases/indie/core/auth/credential-stuffing.md)
- [弱密码风险](../cases/indie/core/auth/weak-password.md)
- [Session劫持](../cases/indie/core/auth/session-hijacking.md)
- [账号接管](../cases/indie/core/auth/account-takeover.md)

---

> 记住：**账号安全是用户信任的基石，一次泄露可能毁掉你的产品。**
