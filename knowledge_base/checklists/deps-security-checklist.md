# 依赖安全检查清单

> 10分钟快速检查你的项目依赖是否存在致命风险

---

## 🔴 必须检查 (Critical)

### 依赖来源
- [ ] **官方源**: 所有依赖是否来自官方源？
- [ ] **签名验证**: 是否验证包签名？
- [ ] **锁文件**: 是否提交锁文件（package-lock.json/yarn.lock）？
- [ ] **私有仓库**: 内部包是否使用私有仓库？

### 版本管理
- [ ] **版本固定**: 生产依赖是否锁定具体版本？
- [ ] **版本范围**: 是否避免使用 `*` 或 `latest`？
- [ ] **定期更新**: 是否定期更新依赖？
- [ ] **安全版本**: 是否检查已知 CVE？

### 安装安全
- [ ] **安装脚本**: 是否检查 postinstall/preinstall 脚本？
- [ ] **依赖数量**: 依赖数量是否合理？
- [ ] **间接依赖**: 是否了解间接依赖？
- [ ] **可信来源**: 是否只使用可信来源的包？

---

## 🟠 重要检查 (High)

### License 合规
- [ ] **License 类型**: 是否识别所有依赖的 License？
- [ ] **传染性 License**: 是否避免 GPL/AGPL 依赖（除非开源）？
- [ ] **商业友好**: 是否使用商业友好的 License？
- [ ] **License 冲突**: 是否检查 License 冲突？

### 供应链安全
- [ ] **维护者身份**: 是否检查关键依赖的维护者？
- [ ] **下载量**: 是否检查包的下载量（过低可能有风险）？
- [ ] **Typosquatting**: 是否检查是否有仿冒包？
- [ ] **依赖混淆**: 是否防止依赖混淆攻击？

---

## 🟡 建议检查 (Medium)

### 维护状态
- [ ] **活跃度**: 依赖是否活跃维护？
- [ ] **Issue 响应**: 维护者是否响应 Issue？
- [ ] **安全更新**: 是否及时发布安全更新？
- [ ] **替代方案**: 是否有更好的替代方案？

### 性能影响
- [ ] **包大小**: 依赖大小是否合理？
- [ ] **加载时间**: 是否影响应用启动时间？
- [ ] **Tree-shaking**: 是否支持 Tree-shaking？
- [ ] **重复依赖**: 是否有重复功能的依赖？

---

## 📋 快速自测命令

```bash
# 扫描依赖漏洞
oms deps scan ./package.json

# 检查 License 合规性
oms deps check-licenses ./package.json

# 检测供应链投毒风险
oms deps supply-chain ./

# 查看依赖安全最佳实践
oms deps guide
```

---

## 🆘 发现问题怎么办？

1. **立即修复**: Critical 级别问题必须立即修复
2. **短期加固**: High 级别问题建议一周内修复
3. **持续改进**: Medium 级别问题纳入迭代计划

---

## 📞 相关资源

- [供应链投毒](../cases/indie/core/deps/supply-chain-poisoning.md)
- [恶意包攻击](../cases/indie/core/deps/malicious-package.md)
- [依赖混淆攻击](../cases/indie/core/deps/dependency-confusion.md)
- [包名仿冒](../cases/indie/core/deps/typosquatting.md)

---

> 记住：**一个恶意依赖可以完全控制你的服务器，不要盲目信任任何包。**
