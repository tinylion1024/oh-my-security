# 供应链投毒 (Supply Chain Poisoning)

## 一句话风险
攻击者通过污染软件供应链中的某个环节，向下游项目注入恶意代码，影响所有依赖该组件的项目。

## 风险等级
- 严重程度: 🔴严重
- 影响范围: 所有使用受污染依赖的项目
- 发生概率: 中

## 场景描述

独立开发者小李正在开发一个 SaaS 产品，项目依赖了约 50 个 npm 包。某天，其中一个常用的工具库被攻击者接管，攻击者在发布新版本时注入了恶意代码，该代码会在构建时窃取环境变量中的敏感信息（如 AWS 密钥、数据库密码等）。

小李运行 `npm update` 后，恶意代码随之进入项目。在 CI/CD 构建过程中，恶意代码将环境变量发送到攻击者的服务器。攻击者获得了小李的 AWS 凭证，随后在云上创建了恶意资源，导致账户被扣款数千美元。由于供应链攻击具有传导性，所有使用该库的项目都面临相同风险。

## 攻击方式
1. 攻击者通过社会工程、凭证泄露或维护者权限漏洞获取包的发布权限
2. 在新版本中注入恶意代码，通常隐藏在构建脚本或混淆代码中
3. 恶意代码执行敏感数据窃取、后门植入或挖矿等行为
4. 发布新版本并自动传播到所有下游项目
5. 用户运行 `npm install` 或 `npm update` 时触发攻击

## 真实案例
- **event-stream 事件 (2018)**：攻击者接管流行的 npm 包 event-stream，注入窃取加密货币钱包的恶意代码
- **ua-parser-js 事件 (2021)**：包被劫持，添加了挖矿和窃取数据的恶意代码
- **colors.js / faker.js 事件 (2022)**：维护者故意破坏自己的包以抗议商业使用

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查项目依赖是否有已知漏洞：`npm audit` / `yarn audit`
- [ ] 审查 package.json 中的依赖来源是否可信
- [ ] 确认是否使用了 package-lock.json 并提交到版本控制

### 短期加固 (1小时)
- [ ] 启用 npm 两步验证 (2FA)
- [ ] 使用 `npm ci` 代替 `npm install` 确保锁定版本
- [ ] 检查依赖的维护者数量和活跃度
- [ ] 移除不必要的依赖，减少攻击面

### 长期建设
- [ ] 实施依赖固定策略，锁定所有依赖版本
- [ ] 建立私有 npm 缓存/代理，审核所有新增依赖
- [ ] 使用 SCA (Software Composition Analysis) 工具持续监控
- [ ] 配置 CI/CD 检查依赖变化告警
- [ ] 使用 Sigstore 等工具验证包签名

## 检测方法

```bash
# 1. 检查依赖树中是否有可疑包
npm ls --all

# 2. 查看包的详细信息
npm view <package-name> --json

# 3. 检查包的维护者和发布历史
npm view <package-name> maintainers
npm view <package-name> time

# 4. 使用安全工具扫描
npm audit --json | jq

# 5. 检查安装脚本
cat node_modules/<package>/package.json | grep -E "preinstall|postinstall|install"
```

## 代码示例

```javascript
// package.json - 固定版本，避免自动升级
{
  "dependencies": {
    "lodash": "4.17.21",  // 精确版本，而非 ^4.17.21
    "express": "4.18.2"
  },
  "scripts": {
    // 验证依赖完整性
    "preinstall": "npx npm-force-resolutions",
    "audit": "npm audit --audit-level=moderate",
    "check-licenses": "npx license-checker --production --onlyAllow 'MIT;ISC;Apache-2.0'"
  }
}

// .npmrc - 安全配置
// 禁止执行生命周期脚本（谨慎使用，可能影响某些包）
ignore-scripts=true

// 或只允许特定包执行脚本
ignore-scripts=false
enable-pre-post-scripts=false
```

```yaml
# GitHub Actions - 依赖安全检查
name: Dependency Security

on:
  pull_request:
    paths:
      - 'package-lock.json'
      - 'package.json'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - name: Security Audit
        run: npm audit --audit-level=moderate
      - name: Check for new dependencies
        run: |
          if git diff --name-only origin/main | grep -q "package.json"; then
            echo "New dependencies added, please review carefully"
            git diff origin/main package.json
          fi
```

## 参考资料
- [npm Documentation: Security Best Practices](https://docs.npmjs.com/packages-and-modules/securing-your-code)
- [OWASP: Dependency Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Dependency_Management_Cheat_Sheet.html)
- [Snyk: State of Open Source Security](https://snyk.io/state-of-open-source-security/)
- [Node.js Security Best Practices](https://nodejs.org/en/docs/guides/security/)
