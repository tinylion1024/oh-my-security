# 依赖混淆 (Dependency Confusion)

## 一句话风险
攻击者利用私有包名在公共仓库中注册同名恶意包，诱使包管理器从公共仓库安装恶意版本而非私有版本。

## 风险等级
- 严重程度: 🔴严重
- 影响范围: 使用私有包的企业和团队
- 发生概率: 高

## 场景描述

某独立开发者小王的团队开发了一个内部工具包 `@mycompany/internal-utils`，托管在公司内部的私有 npm 仓库。团队的所有项目都依赖这个包，包含核心业务逻辑和敏感配置。

攻击者通过公开的 package.json 文件或招聘信息发现了这个私有包名。攻击者在 npm 公共仓库注册了同名包 `@mycompany/internal-utils`，并在其中植入了数据窃取代码。

某天，一位新入职的开发者在配置开发环境时，npm 配置有误，导致包管理器优先从公共仓库查找包。于是，恶意包被安装到项目中。在构建过程中，恶意代码窃取了公司的 AWS 密钥和数据库密码，并发送给攻击者。

## 攻击方式
1. 攻击者发现目标组织使用的私有包名（通过 GitHub、招聘信息、泄露的配置等）
2. 在公共仓库注册同名包，版本号设置得比私有包更高
3. 包管理器默认优先从公共仓库下载，忽略私有仓库
4. 开发者运行 `npm install` 时安装了恶意公共包
5. 恶意代码在安装或运行时执行攻击行为

## 真实案例
- **Alex Birsan 研究 (2021)**：成功攻击 Microsoft、Apple、PayPal 等 35 家公司，获得 130,000 美元赏金
- **Stripe 事件**：私有包名被抢注，导致供应链风险
- **中国多家企业**：2022 年发现大量私有包名在 npm 公共仓库被抢注

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查所有私有包名是否在公共仓库被抢注
- [ ] 验证 `.npmrc` 配置是否正确指向私有仓库
- [ ] 确认 package-lock.json 中的包来源

### 短期加固 (1小时)
- [ ] 在公共仓库抢注所有私有包名（占位保护）
- [ ] 配置 `.npmrc` 确保作用域包指向私有仓库
- [ ] 启用私有仓库的认证机制
- [ ] 审查 CI/CD 中的 npm 配置

### 长期建设
- [ ] 使用作用域包名（如 `@company/package`）
- [ ] 配置企业级 npm 代理，白名单机制
- [ ] 实施包完整性验证（checksum/signature）
- [ ] 建立包命名规范和注册保护机制
- [ ] 定期审计依赖来源

## 检测方法

```bash
# 1. 检查私有包是否在公共仓库存在
npm view @mycompany/internal-utils --registry https://registry.npmjs.org

# 2. 检查包的实际来源
npm ls @mycompany/internal-utils
npm view @mycompany/internal-utils dist.tarball

# 3. 验证 lock 文件中的来源
cat package-lock.json | jq '.packages | to_entries[] | select(.key | contains("@mycompany")) | .value.resolved'

# 4. 检查 npm 配置
npm config list
cat ~/.npmrc

# 5. 使用安全工具
npx npm-audit-resolver
```

```javascript
// 检测脚本：验证所有依赖来源
const fs = require('fs');
const path = require('path');

function checkDependencySources() {
  const lockFile = JSON.parse(fs.readFileSync('package-lock.json', 'utf8'));
  const packages = lockFile.packages || {};

  const ALLOWED_REGISTRIES = [
    'https://npm.mycompany.com',
    'https://registry.npmjs.org' // 仅允许特定公共包
  ];

  const PRIVATE_SCOPES = ['@mycompany', '@internal'];

  const issues = [];

  for (const [name, info] of Object.entries(packages)) {
    if (name === '') continue; // 根目录

    const resolved = info.resolved || '';

    // 检查私有包来源
    for (const scope of PRIVATE_SCOPES) {
      if (name.startsWith(scope) && !resolved.includes('npm.mycompany.com')) {
        issues.push({
          package: name,
          issue: 'PRIVATE_PACKAGE_PUBLIC_SOURCE',
          source: resolved
        });
      }
    }

    // 检查是否来自未知源
    const isAllowedSource = ALLOWED_REGISTRIES.some(reg => resolved.includes(reg));
    if (resolved && !isAllowedSource) {
      issues.push({
        package: name,
        issue: 'UNKNOWN_REGISTRY',
        source: resolved
      });
    }
  }

  return issues;
}

const issues = checkDependencySources();
if (issues.length > 0) {
  console.error('发现依赖来源问题:');
  issues.forEach(i => console.error(`  - ${i.package}: ${i.issue} (${i.source})`));
  process.exit(1);
}
```

## 代码示例

```
# .npmrc - 正确配置防止依赖混淆

# 公司私有仓库
@mycompany:registry=https://npm.mycompany.com
//npm.mycompany.com/:_authToken=${NPM_TOKEN}

# 默认公共仓库
registry=https://registry.npmjs.org

# 禁止从其他源安装
# strict-ssl=true

# 锁定特定包的来源
lodash:registry=https://registry.npmjs.org
```

```yaml
# GitHub Actions - 验证依赖来源
name: Verify Dependencies

on:
  push:
    branches: [main]
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://npm.mycompany.com'
          scope: '@mycompany'

      - name: Install dependencies
        run: npm ci
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}

      - name: Verify private packages source
        run: |
          # 检查所有 @mycompany 包来自私有仓库
          packages=$(cat package-lock.json | jq -r '.packages | keys[]' | grep '@mycompany' || true)
          for pkg in $packages; do
            source=$(cat package-lock.json | jq -r ".packages[\"$pkg\"].resolved")
            if [[ ! "$source" =~ "npm.mycompany.com" ]]; then
              echo "::error::私有包 $pkg 来自非预期源: $source"
              exit 1
            fi
          done

      - name: Check for confusion attack
        run: |
          # 检查私有包是否在公共仓库存在
          scopes=("@mycompany" "@internal")
          for scope in "${scopes[@]}"; do
            packages=$(cat package.json | jq -r ".dependencies, .devDependencies" | jq -r "keys[]" | grep "$scope" || true)
            for pkg in $packages; do
              if npm view $pkg --registry https://registry.npmjs.org 2>/dev/null; then
                echo "::warning::私有包 $pkg 在公共仓库存在同名包"
              fi
            done
          done
```

```jsonc
// package.json - 私有包声明
{
  "name": "@mycompany/my-app",
  "dependencies": {
    // 明确指定来源
    "@mycompany/internal-utils": "1.2.3",
    "@mycompany/logger": "^2.0.0"
  },
  "publishConfig": {
    // 确保发布到正确的仓库
    "registry": "https://npm.mycompany.com",
    "access": "restricted"
  }
}
```

## 参考资料
- [Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of Other Companies](https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610)
- [npm Scope Configuration](https://docs.npmjs.com/cli/v9/using-npm/scope)
- [Protecting Against Dependency Confusion](https://github.blog/2021-02-12-avoiding-npm-substitution-attacks/)
- [OWASP: Dependency Confusion](https://owasp.org/www-community/attacks/Dependency_Confusion)
