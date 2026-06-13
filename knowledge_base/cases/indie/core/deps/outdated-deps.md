# 过时依赖 (Outdated Dependencies)

## 一句话风险
项目依赖长期未更新，包含已知安全漏洞，容易被攻击者利用。

## 风险等级
- 严重程度: 🟠高
- 影响范围: 所有使用过时依赖的项目
- 发生概率: 高

## 场景描述

独立开发者小王两年前开发了一个在线商城项目，当时使用了最新版本的依赖。项目上线后运行稳定，小王就没有再关注依赖更新。

两年后，小王收到了云服务商的安全警告，提示服务器存在异常出站连接。经过排查，发现攻击者利用了项目中 `lodash` 的一个已知漏洞（CVE-2020-8203），该漏洞允许原型污染，攻击者利用此漏洞注入了恶意代码。

小王检查后发现，项目中的 47 个依赖中有 32 个存在已知安全漏洞，其中 8 个是严重漏洞。这些漏洞在两年间已经被公开，攻击者可以轻易找到利用方法。更糟糕的是，一些依赖的 API 已经发生变化，升级可能导致代码不兼容，小王不得不花费大量时间修复。

## 攻击方式
1. 攻击者扫描公开的漏洞数据库（NVD、CVE）
2. 自动化工具扫描互联网上使用过时依赖的网站
3. 匹配已知漏洞与目标项目
4. 利用漏洞获取服务器权限或窃取数据
5. 植入后门或进行其他恶意操作

## 真实案例
- **Equifax 数据泄露 (2017)**：Apache Struts 过时版本导致 1.43 亿用户数据泄露
- **Log4j 漏洞 (2021)**：大量项目使用过时 Log4j 版本，遭受大规模攻击
- **SolarWinds 供应链攻击 (2020)**：过时依赖成为攻击入口之一
- **npm 生态系统研究**：平均每个项目有 79% 的依赖过时

## 防御建议

### 立即行动 (5分钟)
- [ ] 运行 `npm outdated` 查看过时依赖
- [ ] 运行 `npm audit` 检查已知漏洞
- [ ] 确认当前依赖版本和最新版本差距

### 短期加固 (1小时)
- [ ] 升级所有严重和高危漏洞的依赖
- [ ] 检查升级后的破坏性变更
- [ ] 运行测试确保升级不破坏功能
- [ ] 使用 `npm update` 升级兼容版本

### 长期建设
- [ ] 建立定期依赖更新流程（每周/每月）
- [ ] 使用 Dependabot 或 Renovate 自动化更新
- [ ] 在 CI/CD 中集成漏洞扫描
- [ ] 订阅安全公告和更新通知
- [ ] 使用 `npm ci` 确保一致安装

## 检测方法

```bash
# 1. 检查过时依赖
npm outdated
npm outdated --json

# 2. 安全审计
npm audit
npm audit --json
npm audit fix  # 自动修复

# 3. 检查特定包的版本
npm view <package> versions
npm view <package> time.modified

# 4. 使用第三方工具
npx npm-check-updates
npx depcheck  # 检查未使用的依赖

# 5. 检查直接和间接依赖
npm ls --all
npm ls <package>
```

```javascript
// 过时依赖检测脚本
const { execSync } = require('child_process');

function checkDependencies() {
  console.log('=== 依赖状态检查 ===\n');

  // 检查过时依赖
  console.log('📦 过时依赖:');
  try {
    const outdated = JSON.parse(execSync('npm outdated --json', { encoding: 'utf8' }));
    for (const [name, info] of Object.entries(outdated)) {
      console.log(`  ${name}: ${info.current} → ${info.latest}`);
    }
  } catch (e) {
    // npm outdated 返回非零码如果没有过时包
    console.log('  ✅ 所有依赖都是最新的');
  }

  // 检查漏洞
  console.log('\n🔒 安全漏洞:');
  try {
    const audit = JSON.parse(execSync('npm audit --json', { encoding: 'utf8' }));
    const vulnerabilities = audit.vulnerabilities || {};

    const critical = Object.values(vulnerabilities).filter(v => v.severity === 'critical');
    const high = Object.values(vulnerabilities).filter(v => v.severity === 'high');
    const moderate = Object.values(vulnerabilities).filter(v => v.severity === 'moderate');

    if (critical.length > 0) {
      console.log(`  🔴 严重: ${critical.length} 个`);
      critical.forEach(v => console.log(`     - ${v.name}`));
    }
    if (high.length > 0) {
      console.log(`  🟠 高危: ${high.length} 个`);
    }
    if (moderate.length > 0) {
      console.log(`  🟡 中危: ${moderate.length} 个`);
    }

    if (critical.length > 0 || high.length > 0) {
      console.log('\n  ⚠️  建议运行: npm audit fix');
      process.exit(1);
    }
  } catch (e) {
    console.log('  ✅ 未发现安全漏洞');
  }

  // 检查依赖年龄
  console.log('\n📅 依赖更新时间:');
  const pkg = require('./package.json');
  for (const dep of Object.keys(pkg.dependencies || {}).slice(0, 10)) {
    try {
      const info = JSON.parse(execSync(`npm view ${dep} --json`, { encoding: 'utf8' }));
      const lastUpdate = new Date(info.time.modified);
      const daysSince = Math.floor((Date.now() - lastUpdate) / (1000 * 60 * 60 * 24));

      if (daysSince > 365) {
        console.log(`  ⚠️  ${dep}: ${daysSince} 天未更新`);
      }
    } catch (e) {}
  }
}

checkDependencies();
```

## 代码示例

```jsonc
// package.json - 版本管理最佳实践
{
  "name": "my-project",
  "scripts": {
    "check:outdated": "npm outdated",
    "check:audit": "npm audit --audit-level=moderate",
    "check:deps": "npm run check:outdated && npm run check:audit",
    "update:safe": "npm update && npm audit fix",
    "update:major": "npx npm-check-updates -u"
  },
  "dependencies": {
    // 使用精确版本或补丁范围
    "express": "4.18.2",      // 精确版本
    "lodash": "~4.17.21",     // 允许补丁更新
    "axios": "^1.6.0"         // 允许次版本更新
  },
  "devDependencies": {
    "@types/node": "^20.0.0"
  }
}
```

```yaml
# GitHub Actions - 定期检查过时依赖
name: Dependency Check

on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一检查
  pull_request:
  push:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Check for outdated dependencies
        run: npm outdated || true

      - name: Security audit
        run: npm audit --audit-level=moderate
        continue-on-error: true

      - name: Generate audit report
        run: npm audit --json > audit-report.json
        continue-on-error: true

      - name: Upload audit report
        uses: actions/upload-artifact@v4
        with:
          name: audit-report
          path: audit-report.json

      - name: Create issue if vulnerabilities found
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const audit = JSON.parse(fs.readFileSync('audit-report.json'));
            const vulns = Object.values(audit.vulnerabilities || {});

            if (vulns.length > 0) {
              const critical = vulns.filter(v => v.severity === 'critical');
              const high = vulns.filter(v => v.severity === 'high');

              const body = `## 🔒 安全漏洞报告

              发现以下安全漏洞需要修复：

              - 🔴 严重: ${critical.length} 个
              - 🟠 高危: ${high.length} 个

              ### 详细信息

              ${vulns.map(v => `- **${v.name}**: ${v.severity} - ${v.via}`).join('\n')}

              ### 修复建议

              \`\`\`bash
              npm audit fix
              \`\`\`
              `;

              github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: '⚠️ 发现安全漏洞',
                body: body,
                labels: ['security', 'dependencies']
              });
            }
```

```yaml
# Dependabot 配置 - .github/dependabot.yml
version: 2
updates:
  # 启用 npm 依赖更新
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'  # 每周检查
      day: 'monday'
      time: '09:00'
    open-pull-requests-limit: 10
    # 自动合并补丁更新
    automerged-updates:
      - dependency-type: 'dev-dependencies'
        update-types: ['version-update:semver-patch']
      - dependency-type: 'dependencies'
        update-types: ['version-update:semver-patch']
    # 提交消息格式
    commit-message:
      prefix: 'chore'
      include: 'scope'
    # 标签
    labels:
      - 'dependencies'
      - 'security'

  # 启用 GitHub Actions 更新
  - package-ecosystem: 'github-actions'
    directory: '/'
    schedule:
      interval: 'monthly'
```

```javascript
// Renovate 配置 - renovate.json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:base"
  ],
  "schedule": ["every weekend"],
  "automerge": true,
  "automergeType": "pr",
  "automergeStrategy": "merge-commit",
  "major": {
    "automerge": false
  },
  "minor": {
    "automerge": true,
    "groupName": "minor dependencies"
  },
  "patch": {
    "automerge": true,
    "groupName": "patch dependencies"
  },
  "vulnerabilityAlerts": {
    "enabled": true,
    "automerge": true
  },
  "packageRules": [
    {
      "matchPackagePatterns": ["eslint", "prettier"],
      "automerge": true,
      "groupName": "linting tools"
    },
    {
      "matchUpdateTypes": ["major"],
      "addLabels": ["breaking-change"]
    }
  ]
}
```

## 参考资料
- [npm Documentation: npm-outdated](https://docs.npmjs.com/cli/v9/commands/npm-outdated)
- [npm Documentation: npm-audit](https://docs.npmjs.com/cli/v9/commands/npm-audit)
- [GitHub Dependabot](https://docs.github.com/en/code-security/dependabot)
- [Renovate Bot](https://github.com/renovatebot/renovate)
- [Snyk Vulnerability DB](https://security.snyk.io/)
- [Node.js Security Best Practices](https://github.com/goldbergyoni/nodebestpractices#6-security-best-practices)
