# 锁文件篡改 (Lockfile Tampering)

## 一句话风险
攻击者修改锁文件中的包哈希或版本号，绕过依赖验证，使项目安装被篡改的恶意包。

## 风险等级
- 严重程度: 🟠高
- 影响范围: 所有使用锁文件的项目
- 发生概率: 中

## 场景描述

独立开发者小张的项目使用 Git 进行版本控制，`package-lock.json` 文件被提交到仓库。某天，攻击者通过钓鱼攻击获取了小张的 GitHub 凭证，并悄悄修改了 `package-lock.json` 文件。

攻击者将其中几个常用包的版本号修改为包含后门的恶意版本，同时更新了 integrity 哈希值。这些修改隐藏在一次看似普通的提交中（如 "update dependencies"）。

小张和团队成员在拉取代码后运行 `npm ci` 安装依赖，由于 integrity 字段已经被篡改，npm 没有报错，正常安装了恶意包。几周后，团队发现生产环境的敏感数据被泄露到外部服务器。

## 攻击方式
1. 攻击者获取代码仓库的写入权限
2. 修改 `package-lock.json` 中的版本号和 integrity 哈希
3. 提交修改到仓库，伪装成依赖更新
4. 开发者/CI 系统拉取代码并安装依赖
5. npm 验证通过，安装了被篡改的包

## 真实案例
- **CodeCov Bash Uploader 攻击 (2021)**：攻击者修改了脚本哈希验证逻辑
- **SolarWinds 供应链攻击 (2020)**：攻击者在构建过程中注入恶意代码
- **PHP Composer 锁文件篡改**：多个项目报告锁文件被恶意修改
- **事件流攻击**：通过修改依赖配置注入恶意代码

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查 `package-lock.json` 的最近提交历史
- [ ] 验证锁文件中的 integrity 哈希是否正确
- [ ] 确认是否有异常的版本变更

### 短期加固 (1小时)
- [ ] 使用 `npm ci` 而非 `npm install` 进行安装
- [ ] 配置 CODEOWNERS 文件保护锁文件
- [ ] 启用 Git 签名验证提交
- [ ] 审查所有对锁文件的修改

### 长期建设
- [ ] 在 CI/CD 中验证锁文件完整性
- [ ] 使用 Sigstore 签名验证
- [ ] 启用分支保护和必经审核
- [ ] 定期审计锁文件变更
- [ ] 使用依赖锁定和固定版本策略

## 检测方法

```bash
# 1. 检查锁文件完整性
npm ci --dry-run

# 2. 验证哈希值
npx package-lock-validator

# 3. 检查最近的锁文件变更
git log --oneline -10 -- package-lock.json

# 4. 对比差异
git diff HEAD~1 -- package-lock.json

# 5. 检查特定包的哈希
cat package-lock.json | jq '.packages["node_modules/lodash"].integrity'

# 6. 使用 npm cache verify
npm cache verify
```

```javascript
// 锁文件完整性验证脚本
const fs = require('fs');
const crypto = require('crypto');
const https = require('https');

async function verifyLockfileIntegrity() {
  console.log('=== 锁文件完整性验证 ===\n');

  const lockfile = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));
  const issues = [];

  // 检查 lockfileVersion
  if (lockfile.lockfileVersion < 2) {
    console.warn('⚠️  建议升级 lockfileVersion 到 2 或更高');
  }

  // 验证每个包的 integrity
  for (const [path, info] of Object.entries(lockfile.packages || {})) {
    if (path === '') continue; // 根目录
    if (!info.resolved || !info.integrity) continue;

    const pkgName = path.replace('node_modules/', '');

    try {
      // 从 npm registry 获取包信息
      const registryData = await fetchPackageInfo(info.resolved);

      // 验证 integrity
      if (info.integrity !== registryData.integrity) {
        issues.push({
          package: pkgName,
          issue: 'INTEGRITY_MISMATCH',
          expected: registryData.integrity,
          actual: info.integrity,
          severity: 'CRITICAL'
        });
      }

      // 验证版本是否仍可从 registry 获取
      if (!registryData.exists) {
        issues.push({
          package: pkgName,
          issue: 'VERSION_NOT_FOUND',
          version: info.version,
          severity: 'HIGH'
        });
      }
    } catch (e) {
      console.warn(`无法验证 ${pkgName}: ${e.message}`);
    }
  }

  // 报告结果
  if (issues.length > 0) {
    console.error('\n❌ 发现锁文件问题:\n');
    for (const issue of issues) {
      console.error(`${issue.severity}: ${issue.package}`);
      console.error(`  问题: ${issue.issue}`);
      if (issue.expected) {
        console.error(`  预期: ${issue.expected}`);
        console.error(`  实际: ${issue.actual}`);
      }
    }
    process.exit(1);
  }

  console.log('✅ 锁文件完整性验证通过');
}

async function fetchPackageInfo(resolvedUrl) {
  return new Promise((resolve, reject) => {
    const req = https.get(resolvedUrl, {
      headers: { 'Accept': 'application/json' }
    }, (res) => {
      if (res.statusCode === 404) {
        resolve({ exists: false });
        return;
      }

      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ exists: true, data: JSON.parse(data) });
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
  });
}

verifyLockfileIntegrity();
```

## 代码示例

```jsonc
// package.json - 锁文件保护配置
{
  "scripts": {
    "preinstall": "node scripts/verify-lockfile.js",
    "verify-lockfile": "node scripts/verify-lockfile.js",
    "postinstall": "npm run verify-lockfile"
  }
}
```

```javascript
// scripts/verify-lockfile.js - 安装前验证
const fs = require('fs');
const { execSync } = require('child_process');

function verifyLockfile() {
  // 检查锁文件是否存在
  if (!fs.existsSync('package-lock.json')) {
    console.error('❌ package-lock.json 不存在');
    process.exit(1);
  }

  // 检查 package.json 和 lock 文件是否同步
  const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
  const lock = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));

  const pkgDeps = { ...pkg.dependencies, ...pkg.devDependencies };
  const lockDeps = lock.packages['']?.dependencies || {};

  for (const [name, version] of Object.entries(pkgDeps)) {
    if (!lockDeps[name]) {
      console.error(`❌ ${name} 在 package.json 中存在但在 lock 文件中不存在`);
      process.exit(1);
    }
  }

  // 检查可疑的 integrity 格式
  for (const [path, info] of Object.entries(lock.packages)) {
    if (!info.integrity) continue;

    // integrity 应该是 sha512- 或 sha256- 开头
    if (!info.integrity.match(/^(sha512|sha256)-/)) {
      console.error(`❌ ${path} 的 integrity 格式可疑: ${info.integrity}`);
      process.exit(1);
    }
  }

  console.log('✅ 锁文件验证通过');
}

verifyLockfile();
```

```yaml
# GitHub Actions - 锁文件完整性检查
name: Lockfile Integrity Check

on:
  push:
    paths:
      - 'package-lock.json'
      - 'package.json'
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2  # 获取最近两个提交以对比

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Check lockfile changes
        run: |
          if git diff --name-only HEAD~1 HEAD | grep -q "package-lock.json"; then
            echo "### 📦 锁文件变更检测" >> $GITHUB_STEP_SUMMARY

            # 显示变更统计
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
            git diff HEAD~1 HEAD -- package-lock.json --stat >> $GITHUB_STEP_SUMMARY
            echo "\`\`\`" >> $GITHUB_STEP_SUMMARY

            # 检查 integrity 变更
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "### 🔍 Integrity 变更" >> $GITHUB_STEP_SUMMARY
            echo "" >> $GITHUB_STEP_SUMMARY
            echo "\`\`\`diff" >> $GITHUB_STEP_SUMMARY
            git diff HEAD~1 HEAD -- package-lock.json | grep -A2 -B2 "integrity" >> $GITHUB_STEP_SUMMARY || echo "无 integrity 变更" >> $GITHUB_STEP_SUMMARY
            echo "\`\`\`" >> $GITHUB_STEP_SUMMARY
          fi

      - name: Verify lockfile integrity
        run: |
          node -e "
            const fs = require('fs');
            const lock = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));

            // 检查 integrity 格式
            const issues = [];
            for (const [path, info] of Object.entries(lock.packages)) {
              if (info.integrity && !info.integrity.match(/^(sha512|sha256)-/)) {
                issues.push(path + ': ' + info.integrity);
              }
            }

            if (issues.length > 0) {
              console.error('发现可疑 integrity:');
              issues.forEach(i => console.error('  - ' + i));
              process.exit(1);
            }
            console.log('Integrity 格式验证通过');
          "

      - name: Install and verify
        run: |
          npm ci
          npm ls --depth=0

      - name: Security audit
        run: npm audit --audit-level=moderate
```

```
# .github/CODEOWNERS - 保护锁文件
# 锁文件需要安全团队审核
/package-lock.json @security-team @lead-dev
/yarn.lock @security-team @lead-dev
/pnpm-lock.yaml @security-team @lead-dev

# 依赖配置文件也需要审核
/package.json @lead-dev
/.npmrc @security-team
```

```yaml
# .github/workflows/branch-protection.yml
# 分支保护规则（通过 GitHub API 配置）
name: Configure Branch Protection

on:
  workflow_dispatch:

jobs:
  configure:
    runs-on: ubuntu-latest
    steps:
      - name: Configure main branch protection
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.repos.updateBranchProtection({
              owner: context.repo.owner,
              repo: context.repo.repo,
              branch: 'main',
              required_pull_request_reviews: {
                required_approving_review_count: 1,
                require_code_owner_reviews: true
              },
              restrictions: null,
              enforce_admins: true,
              required_status_checks: {
                strict: true,
                contexts: ['Lockfile Integrity Check']
              }
            });
```

```javascript
// Git pre-commit hook - 验证锁文件变更
// .husky/pre-commit
const { execSync } = require('child_process');

// 检查是否修改了 lock 文件
const changedFiles = execSync('git diff --cached --name-only', { encoding: 'utf8' })
  .trim()
  .split('\n');

if (changedFiles.includes('package-lock.json')) {
  console.log('📦 检测到 package-lock.json 变更...');

  // 运行完整性检查
  try {
    execSync('npm run verify-lockfile', { stdio: 'inherit' });
  } catch (e) {
    console.error('❌ 锁文件验证失败，请检查变更');
    process.exit(1);
  }

  console.log('✅ 锁文件验证通过');
}
```

## 参考资料
- [npm Documentation: package-lock.json](https://docs.npmjs.com/cli/v9/configuring-npm/package-lock-json)
- [GitHub: Securing your supply chain](https://docs.github.com/en/code-security/supply-chain-security)
- [Sigstore: Software Supply Chain Security](https://www.sigstore.dev/)
- [Snyk: Lockfile Security](https://snyk.io/blog/lockfile-security/)
- [npm ci vs npm install](https://docs.npmjs.com/cli/v9/commands/npm-ci)
