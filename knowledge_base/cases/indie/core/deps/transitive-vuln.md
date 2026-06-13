# 传递性漏洞 (Transitive Vulnerability)

## 一句话风险
你的直接依赖没有漏洞，但它依赖的其他包存在安全漏洞，攻击者可间接利用这些漏洞攻击你的项目。

## 风险等级
- 严重程度: 🟠高
- 影响范围: 几乎所有项目（平均每个项目有 80% 的间接依赖）
- 发生概率: 高

## 场景描述

独立开发者小李在开发一个 API 服务时，只使用了几个主流的、经过审查的 npm 包。他运行 `npm audit` 检查依赖，没有发现任何漏洞，于是放心地将项目上线。

三个月后，小李收到安全团队的通知，项目存在严重安全漏洞。经过排查，漏洞来自一个名为 `kind-of` 的间接依赖。这个包被小李使用的某个工具库依赖，而这个工具库又被另一个库依赖，形成了三层依赖链。

`kind-of` 的漏洞允许原型污染，攻击者可以通过构造特定的 API 请求触发漏洞，最终在服务器上执行任意代码。由于是间接依赖，小李从未关注过这个包，安全审计时也容易被忽略。

## 攻击方式
1. 攻击者发现深层依赖中的漏洞
2. 分析哪些热门包使用了这个有漏洞的依赖
3. 针对性地攻击使用热门包的项目
4. 开发者只审查直接依赖，忽视间接依赖
5. 漏洞通过依赖链传播到最终项目

## 真实案例
- **event-stream 事件 (2018)**：通过 `ps-tree` 间接依赖影响 `event-stream`
- **serialize-to-js 漏洞 (2021)**：影响多个流行的模版引擎
- **kind-of 漏洞 (2020)**：影响数百万个项目，包括间接依赖
- **Lodash 依赖链漏洞**：间接依赖影响大量工具

## 防御建议

### 立即行动 (5分钟)
- [ ] 运行 `npm audit` 检查所有依赖（包括间接依赖）
- [ ] 查看完整的依赖树：`npm ls --all`
- [ ] 确认是否存在已知 CVE 漏洞

### 短期加固 (1小时)
- [ ] 使用 `npm audit fix` 自动修复
- [ ] 检查是否需要手动更新间接依赖
- [ ] 使用 `npm overrides` 强制使用安全版本
- [ ] 运行完整测试确保修复不破坏功能

### 长期建设
- [ ] 定期运行依赖安全扫描
- [ ] 在 CI/CD 中集成传递性漏洞检测
- [ ] 使用 `npm overrides` 控制间接依赖版本
- [ ] 评估依赖树深度，减少间接依赖
- [ ] 使用锁文件确保依赖版本一致

## 检测方法

```bash
# 1. 查看完整依赖树
npm ls --all
npm ls <package-name>  # 查看特定包的依赖路径

# 2. 安全审计（包括间接依赖）
npm audit
npm audit --json

# 3. 查看依赖关系图
npx dep-tree
npx npm-dependency-tree

# 4. 查找特定包的来源
npm why <package-name>

# 5. 使用 Snyk 深度扫描
npx snyk test

# 6. 检查依赖树深度
npm ls --all --json | jq 'recurse(.dependencies) | depth'
```

```javascript
// 传递性漏洞检测脚本
const { execSync } = require('child_process');

function analyzeDependencyTree() {
  console.log('=== 传递性依赖分析 ===\n');

  // 获取完整依赖树
  const tree = JSON.parse(execSync('npm ls --all --json', { encoding: 'utf8' }));

  // 分析间接依赖
  const directDeps = Object.keys(tree.dependencies || {});
  const allDeps = new Set();
  const transitiveDeps = new Map(); // 包名 -> 引入路径

  function traverseDeps(deps, path = []) {
    for (const [name, info] of Object.entries(deps)) {
      const currentPath = [...path, name];

      if (!allDeps.has(name)) {
        allDeps.add(name);

        if (path.length > 0) {
          transitiveDeps.set(name, currentPath);
        }
      }

      if (info.dependencies) {
        traverseDeps(info.dependencies, currentPath);
      }
    }
  }

  traverseDeps(tree.dependencies || {});

  console.log(`📦 直接依赖: ${directDeps.length} 个`);
  console.log(`📦 总依赖数: ${allDeps.size} 个`);
  console.log(`📦 间接依赖: ${allDeps.size - directDeps.length} 个`);
  console.log(`📊 间接依赖占比: ${((allDeps.size - directDeps.length) / allDeps.size * 100).toFixed(1)}%\n`);

  // 检查安全漏洞
  console.log('🔒 安全漏洞检查:');
  try {
    const audit = JSON.parse(execSync('npm audit --json', { encoding: 'utf8' }));

    for (const [name, info] of Object.entries(audit.vulnerabilities || {})) {
      const isDirect = directDeps.includes(name);
      const paths = transitiveDeps.get(name) || [];

      console.log(`\n  ${isDirect ? '📌' : '🔗'} ${name} (${info.severity})`);
      if (!isDirect && paths.length > 0) {
        console.log(`     引入路径: ${paths.join(' → ')}`);
      }
      console.log(`     漏洞来源: ${info.via}`);
    }
  } catch (e) {
    console.log('  ✅ 未发现已知漏洞');
  }

  // 分析依赖树深度
  console.log('\n🌳 依赖树深度分析:');
  let maxDepth = 0;

  function getDepth(deps, currentDepth = 0) {
    maxDepth = Math.max(maxDepth, currentDepth);
    for (const info of Object.values(deps)) {
      if (info.dependencies) {
        getDepth(info.dependencies, currentDepth + 1);
      }
    }
  }

  getDepth(tree.dependencies || {});
  console.log(`  最大深度: ${maxDepth} 层`);

  if (maxDepth > 5) {
    console.log('  ⚠️  依赖树过深，建议减少间接依赖');
  }
}

analyzeDependencyTree();
```

## 代码示例

```jsonc
// package.json - 使用 overrides 控制间接依赖版本
{
  "name": "my-project",
  "dependencies": {
    "express": "^4.18.2",
    "some-popular-lib": "^2.0.0"
  },
  "overrides": {
    // 强制所有依赖使用安全的 lodash 版本
    "lodash": "4.17.21",

    // 强制特定包使用特定版本
    "kind-of": "6.0.3",

    // 对特定包的依赖进行覆盖
    "some-popular-lib": {
      "vulnerable-dep": "2.0.0"
    }
  },
  "scripts": {
    "audit": "npm audit --audit-level=moderate",
    "ls-deps": "npm ls --all",
    "check-transitive": "node scripts/check-transitive.js"
  }
}
```

```javascript
// scripts/check-transitive.js - 深度检查脚本
const { execSync } = require('child_process');
const fs = require('fs');

// 已知的高危包黑名单
const BLACKLIST = [
  'event-stream',
  'flatmap-stream',
  'serialize-to-js',
  'kind-of@<6.0.3'
];

function checkTransitiveVulnerabilities() {
  const tree = JSON.parse(execSync('npm ls --all --json', { encoding: 'utf8' }));
  const issues = [];

  function scanDeps(deps, path = []) {
    for (const [name, info] of Object.entries(deps)) {
      const currentPath = [...path, name];
      const version = info.version;

      // 检查黑名单
      for (const item of BLACKLIST) {
        const [pkgName, versionRange] = item.split('@');
        if (name === pkgName) {
          if (!versionRange || version === versionRange) {
            issues.push({
              type: 'BLACKLIST',
              package: name,
              version: version,
              path: currentPath
            });
          }
        }
      }

      // 递归扫描
      if (info.dependencies) {
        scanDeps(info.dependencies, currentPath);
      }
    }
  }

  scanDeps(tree.dependencies || {});

  if (issues.length > 0) {
    console.error('❌ 发现安全问题:\n');
    for (const issue of issues) {
      console.error(`${issue.package}@${issue.version}`);
      console.error(`  引入路径: ${issue.path.join(' → ')}`);
    }
    process.exit(1);
  }

  console.log('✅ 间接依赖检查通过');
}

checkTransitiveVulnerabilities();
```

```yaml
# GitHub Actions - 传递性漏洞扫描
name: Transitive Dependency Check

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * *'  # 每天检查

jobs:
  transitive-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Analyze dependency tree
        run: |
          echo "### 📦 依赖分析" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          # 统计依赖
          direct=$(cat package.json | jq '.dependencies, .devDependencies' | jq -s 'add | keys | length')
          total=$(npm ls --all --json | jq 'recurse(.dependencies) | keys' | jq -s 'add | unique | length')

          echo "- 直接依赖: ${direct} 个" >> $GITHUB_STEP_SUMMARY
          echo "- 总依赖数: ${total} 个" >> $GITHUB_STEP_SUMMARY
          echo "- 间接依赖: $((total - direct)) 个" >> $GITHUB_STEP_SUMMARY
          echo "- 间接依赖占比: $(((total - direct) * 100 / total))%" >> $GITHUB_STEP_SUMMARY

      - name: Security audit
        run: npm audit --audit-level=moderate
        continue-on-error: true

      - name: Deep scan with Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high
          command: test
        continue-on-error: true

      - name: Check for critical transitive vulnerabilities
        run: |
          audit=$(npm audit --json)
          critical=$(echo "$audit" | jq '.vulnerabilities | to_entries[] | select(.value.severity == "critical")')

          if [ -n "$critical" ]; then
            echo "::error::发现严重传递性漏洞"
            echo "$critical" | jq -r '.key'
            exit 1
          fi
```

```javascript
// Express 中间件：运行时检测可疑依赖加载
const Module = require('module');
const originalRequire = Module.prototype.require;

const SUSPICIOUS_PACKAGES = new Set([
  'event-stream',
  'flatmap-stream',
  // 添加其他可疑包
]);

const loadedPackages = new Set();

Module.prototype.require = function(id) {
  // 检测可疑包
  const pkgName = id.split('/')[0];
  if (SUSPICIOUS_PACKAGES.has(pkgName)) {
    console.error(`[SECURITY] 检测到可疑包加载: ${id}`);
    console.error(`调用栈:\n${new Error().stack}`);
    process.exit(1);
  }

  // 记录所有加载的包
  loadedPackages.add(pkgName);

  return originalRequire.apply(this, arguments);
};

// 应用启动后报告
process.on('beforeExit', () => {
  console.log('\n已加载的包:');
  console.log([...loadedPackages].sort().join('\n'));
});
```

## 参考资料
- [npm Documentation: npm-ls](https://docs.npmjs.com/cli/v9/commands/npm-ls)
- [npm Documentation: overrides](https://docs.npmjs.com/cli/v9/configuring-npm/package-json#overrides)
- [Snyk: Transitive Dependencies Security](https://snyk.io/learn/transitive-dependencies/)
- [Node.js Security: Dependency Management](https://nodejs.org/en/docs/guides/security/)
- [NPM Audit Documentation](https://docs.npmjs.com/cli/v9/commands/npm-audit)
