# 安装脚本攻击 (Install Script Attack)

## 一句话风险
恶意包利用 npm 生命周期钩子（preinstall/postinstall）在安装时执行任意代码，绕过开发者的安全审查。

## 风险等级
- 严重程度: 🔴严重
- 影响范围: 所有使用 npm/yarn 的项目
- 发生概率: 高

## 场景描述

独立开发者小李在使用一个流行的 UI 组件库时，注意到这个库最近发布了新版本。他运行 `npm update` 来更新依赖，没有注意到这个包的 `package.json` 中包含了 `postinstall` 脚本。

安装过程中，postinstall 脚本静默执行了以下操作：
1. 收集系统信息（用户名、主机名、环境变量）
2. 扫描 `.ssh`、`.aws`、`.env` 等敏感文件
3. 将收集的数据加密后发送到攻击者的服务器

由于安装过程通常不会显示详细的执行日志，小李完全没有察觉到异常。几周后，小李发现自己的 AWS 账户被异常使用，多个 S3 存储桶的数据被下载，损失了重要的客户数据。

## 攻击方式
1. 攻击者在恶意包的 package.json 中添加生命周期脚本
2. 常用钩子：`preinstall`、`install`、`postinstall`
3. 脚本执行恶意行为：数据窃取、后门植入、挖矿等
4. 用户运行 `npm install` 时自动触发
5. 攻击者获得敏感数据或系统控制权

## 真实案例
- **ua-parser-js (2021)**：postinstall 脚本部署挖矿和窃密程序
- **coa/rc (2021)**：被劫持后通过 preinstall 脚本植入恶意代码
- **Nativefier (2022)**：依赖包通过 postinstall 窃取浏览器数据
- **上千个恶意 npm 包**：利用生命周期钩子进行攻击

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查项目中是否有包使用安装脚本：`grep -r "preinstall\|postinstall" node_modules/*/package.json`
- [ ] 检查最近安装的包是否可信
- [ ] 审查 package-lock.json 中的包来源

### 短期加固 (1小时)
- [ ] 配置 `.npmrc` 禁用生命周期脚本：`ignore-scripts=true`
- [ ] 使用 `npm install --ignore-scripts` 安装依赖
- [ ] 审查关键依赖的 package.json 中的 scripts 字段
- [ ] 使用 `npx @npmcli/install-man-scripts` 控制脚本执行

### 长期建设
- [ ] 在 CI/CD 中默认禁用安装脚本
- [ ] 建立依赖审核流程，检查所有新增依赖的脚本
- [ ] 使用沙箱环境测试新依赖
- [ ] 使用企业级代理过滤恶意包
- [ ] 监控安装过程中的异常行为

## 检测方法

```bash
# 1. 查找所有包含安装脚本的包
grep -r '"preinstall\|"postinstall\|"install"' node_modules/*/package.json

# 2. 列出包含脚本的包
npm ls --json | jq '.. | objects | select(.scripts != null) | select(.scripts.preinstall or .scripts.postinstall) | .name'

# 3. 检查特定包的脚本
npm view <package-name> scripts

# 4. 查看安装过程详细输出
npm install --verbose

# 5. 使用安全工具扫描
npx @npmcli/install-man-scripts --list

# 6. 检查最近修改的包
find node_modules -name "package.json" -mtime -7 -exec grep -l "postinstall" {} \;
```

```javascript
// 安装脚本检测工具
const fs = require('fs');
const path = require('path');

const DANGEROUS_SCRIPTS = [
  'preinstall',
  'install',
  'postinstall',
  'preuninstall',
  'postuninstall'
];

const SUSPICIOUS_PATTERNS = [
  /curl\s+http/i,
  /wget\s+http/i,
  /eval\s*\(/i,
  /Function\s*\(/i,
  /base64/i,
  /process\.env/i,
  /\.ssh/i,
  /\.aws/i,
  /child_process/i,
  /exec\s*\(/i,
  /spawn\s*\(/i
];

function scanForInstallScripts() {
  console.log('=== 安装脚本扫描 ===\n');

  const nodeModulesPath = path.join(process.cwd(), 'node_modules');
  if (!fs.existsSync(nodeModulesPath)) {
    console.error('node_modules 目录不存在');
    return;
  }

  const findings = [];

  function scanPackage(pkgPath) {
    const pkgJsonPath = path.join(pkgPath, 'package.json');
    if (!fs.existsSync(pkgJsonPath)) return;

    try {
      const pkg = JSON.parse(fs.readFileSync(pkgJsonPath, 'utf8'));
      const scripts = pkg.scripts || {};

      for (const scriptName of DANGEROUS_SCRIPTS) {
        const scriptContent = scripts[scriptName];
        if (!scriptContent) continue;

        const finding = {
          package: pkg.name,
          version: pkg.version,
          script: scriptName,
          content: scriptContent,
          issues: []
        };

        // 检查可疑模式
        for (const pattern of SUSPICIOUS_PATTERNS) {
          if (pattern.test(scriptContent)) {
            finding.issues.push(`检测到可疑模式: ${pattern}`);
          }
        }

        findings.push(finding);
      }
    } catch (e) {}
  }

  function scanDirectory(dirPath) {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dirPath, entry.name);

      if (entry.isDirectory()) {
        if (entry.name.startsWith('@')) {
          // 作用域包
          scanDirectory(fullPath);
        } else if (entry.name !== '.bin' && !entry.name.startsWith('.')) {
          scanPackage(fullPath);
        }
      }
    }
  }

  scanDirectory(nodeModulesPath);

  // 报告结果
  if (findings.length === 0) {
    console.log('✅ 未发现安装脚本');
    return;
  }

  console.log(`发现 ${findings.length} 个包包含安装脚本:\n`);

  for (const finding of findings) {
    const hasIssues = finding.issues.length > 0;
    console.log(`${hasIssues ? '⚠️' : 'ℹ️'} ${finding.package}@${finding.version}`);
    console.log(`   ${finding.script}: ${finding.content}`);

    if (hasIssues) {
      for (const issue of finding.issues) {
        console.log(`   ❌ ${issue}`);
      }
    }
    console.log('');
  }

  // 如果有高风险发现，退出码为 1
  const hasHighRisk = findings.some(f => f.issues.length > 0);
  if (hasHighRisk) {
    console.log('⚠️  发现可疑安装脚本，建议人工审查');
    process.exit(1);
  }
}

scanForInstallScripts();
```

## 代码示例

```
# .npmrc - 禁用安装脚本（推荐配置）
# 全局禁用所有生命周期脚本
ignore-scripts=true

# 或者只禁用特定阶段
ignore-scripts=false
enable-pre-post-scripts=false

# 使用 allow-scripts 精确控制
# 需要安装: npm install -g @npmcli/install-man-scripts
```

```jsonc
// package.json - 安全配置
{
  "scripts": {
    "preinstall": "npx npm-force-resolutions",
    "postinstall": "node scripts/audit-deps.js",
    "audit:scripts": "node scripts/scan-install-scripts.js"
  }
}
```

```javascript
// scripts/scan-install-scripts.js - CI 前扫描
const { execSync } = require('child_process');

function auditInstallScripts() {
  console.log('🔍 扫描安装脚本...\n');

  // 获取所有包含安装脚本的包
  const result = execSync(
    `grep -r '"preinstall\\|"postinstall\\|"install"' node_modules/*/package.json || true`,
    { encoding: 'utf8' }
  );

  if (!result.trim()) {
    console.log('✅ 未发现安装脚本');
    return;
  }

  console.log('发现以下包包含安装脚本:\n');
  console.log(result);

  // 检查可疑内容
  const suspicious = [
    'curl', 'wget', 'eval', 'base64', 'exec', 'spawn',
    'process.env', '.ssh', '.aws', 'token', 'password'
  ];

  const lines = result.split('\n');
  for (const line of lines) {
    for (const pattern of suspicious) {
      if (line.toLowerCase().includes(pattern.toLowerCase())) {
        console.error(`⚠️  可疑模式 "${pattern}" 在: ${line}`);
        process.exit(1);
      }
    }
  }
}

auditInstallScripts();
```

```yaml
# GitHub Actions - 安装脚本安全检查
name: Install Script Security Check

on:
  push:
    branches: [main]
  pull_request:

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Create safe .npmrc
        run: |
          echo "ignore-scripts=true" > .npmrc
          echo "✅ 已禁用安装脚本"

      - name: Install dependencies
        run: npm ci

      - name: Scan for install scripts
        run: |
          echo "### 📋 安装脚本扫描报告" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          scripts=$(grep -r '"preinstall\|"postinstall\|"install"' node_modules/*/package.json || true)

          if [ -z "$scripts" ]; then
            echo "✅ 未发现安装脚本" >> $GITHUB_STEP_SUMMARY
          else
            echo "以下包包含安装脚本:" >> $GITHUB_STEP_SUMMARY
            echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
            echo "$scripts" >> $GITHUB_STEP_SUMMARY
            echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY

            # 检查可疑模式
            if echo "$scripts" | grep -qiE 'curl|wget|eval|base64|exec|spawn|process\.env'; then
              echo "::error::发现可疑安装脚本"
              exit 1
            fi
          fi

      - name: Run with scripts enabled for trusted packages
        run: |
          # 移除 ignore-scripts，只对信任的包启用脚本
          rm .npmrc

          # 使用 allow-scripts 控制哪些包可以运行脚本
          npx @npmcli/install-man-scripts --allow lodash --allow express

          npm rebuild
```

```javascript
// 使用 allow-scripts 精确控制
// .nsprc 文件配置
{
  "allowed": [
    // 只允许这些包运行脚本
    "esbuild",
    "sharp",
    "bcrypt"
  ],
  "blocked": [
    // 明确禁止这些包运行脚本
    "some-suspicious-package"
  ]
}

// 然后使用
// npx @npmcli/install-man-scripts
```

```bash
#!/bin/bash
# scripts/safe-install.sh - 安全安装脚本

echo "🔒 开始安全安装..."

# 1. 先用 ignore-scripts 安装
echo "📦 安装依赖（禁用脚本）..."
npm ci --ignore-scripts

# 2. 扫描安装脚本
echo "🔍 扫描安装脚本..."
npx @npmcli/install-man-scripts --list

# 3. 审查后，只对信任的包启用脚本
echo "✅ 对信任的包启用脚本..."
npx @npmcli/install-man-scripts --allow esbuild --allow sharp

# 4. 验证安装
npm ls --depth=0

echo "✅ 安全安装完成"
```

## 常见包含合法安装脚本的包

| 包名 | 脚本用途 | 安全性 |
|------|----------|--------|
| esbuild | 编译原生二进制 | ✅ 安全 |
| sharp | 图像处理二进制 | ✅ 安全 |
| bcrypt | 加密库原生编译 | ✅ 安全 |
| node-sass | Sass 编译器 | ✅ 安全 |
| puppeteer | 下载 Chromium | ⚠️ 检查下载源 |
| electron | 下载 Electron | ⚠️ 检查下载源 |

## 参考资料
- [npm Documentation: Scripts](https://docs.npmjs.com/cli/v9/using-npm/scripts)
- [npm: ignore-scripts](https://docs.npmjs.com/cli/v9/using-npm/config#ignore-scripts)
- [npm install-man-scripts](https://github.com/npm/install-man-scripts)
- [Snyk: Malicious npm packages](https://snyk.io/blog/peacenotwar-malicious-npm-package-node-ipc/)
- [The npm Blog: Script Security](https://blog.npmjs.org/post/141702881055/package-install-scripts-vulnerability)
