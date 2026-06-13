# 包名仿冒 (Typosquatting)

## 一句话风险
攻击者注册与流行包名称相似的恶意包，利用开发者拼写错误安装恶意代码。

## 风险等级
- 严重程度: 🟠高
- 影响范围: 所有开发者
- 发生概率: 高

## 场景描述

独立开发者小陈在赶项目进度时，需要安装一个常用的日期处理库 `moment`。匆忙中，他不小心输入了 `npm install momnet`（字母顺序颠倒）。

恰好有一个恶意包 `momnet` 在 npm 仓库中，它模仿 `moment` 的 API，但在内部植入了恶意代码。安装过程中，该包的 postinstall 脚本收集了开发者的环境变量和浏览器 Cookie，并发送到攻击者的服务器。

两周后，小陈发现自己的 AWS 密钥被盗用，云账户产生了异常费用。经过排查才发现是当初的拼写错误导致了这次安全事故。

## 攻击方式
1. 攻击者识别流行的 npm/PyPI 包
2. 注册拼写相似的包名（如：`lodash` → `lodahs`、`react` → `reactt`）
3. 在恶意包中实现相似 API 或导出原包，隐藏恶意行为
4. 等待开发者拼写错误安装
5. 恶意代码在安装或运行时执行攻击

## 真实案例
- **cross-env 事件 (2017)**：攻击者注册 `crossenv` 模仿 `cross-env`，影响数千项目
- **Electron 恶意包 (2020)**：`electron-validator` 模仿合法包窃取数据
- **Python typosquatting (2023)**：PyPI 发现大量模仿 `requests`、`urllib` 的恶意包

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查 package.json 中的包名是否正确
- [ ] 验证所有依赖是否来自官方来源
- [ ] 使用 `npm view <package>` 确认包的下载量和维护者

### 短期加固 (1小时)
- [ ] 安装 typosquatting 检测工具
- [ ] 配置 IDE 自动补全，减少手动输入错误
- [ ] 复制粘贴包名而非手动输入
- [ ] 审查 package-lock.json 中的包来源

### 长期建设
- [ ] 使用依赖审核工具持续监控
- [ ] 建立依赖白名单机制
- [ ] 定期审查和清理依赖
- [ ] 培训团队成员正确安装依赖的方式

## 检测方法

```bash
# 1. 检查可疑包
npm view <package-name> --json | jq '{name, version, maintainers, downloads}'

# 2. 对比流行包
npm view <package-name> --json | jq '.name' | grep -E "react|lodash|moment|express"

# 3. 使用 typosquatting 检测工具
npx meow

# 4. 检查包的 GitHub 仓库
npm view <package-name> repository.url

# 5. 批量检查
npm ls --json | jq '.. | .name? | select(. != null)' | sort | uniq
```

```javascript
// typosquatting 检测脚本
const POPULAR_PACKAGES = [
  'react', 'lodash', 'moment', 'express', 'axios',
  'webpack', 'typescript', 'jest', 'eslint', 'prettier',
  'redux', 'vue', 'angular', 'next', 'gatsby'
];

function levenshteinDistance(a, b) {
  const matrix = Array(b.length + 1).fill(null).map(() =>
    Array(a.length + 1).fill(null)
  );

  for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
  for (let j = 0; j <= b.length; j++) matrix[j][0] = j;

  for (let j = 1; j <= b.length; j++) {
    for (let i = 1; i <= a.length; i++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      matrix[j][i] = Math.min(
        matrix[j][i - 1] + 1,
        matrix[j - 1][i] + 1,
        matrix[j - 1][i - 1] + cost
      );
    }
  }

  return matrix[b.length][a.length];
}

function checkTyposquatting(packageName) {
  const warnings = [];

  for (const popular of POPULAR_PACKAGES) {
    const distance = levenshteinDistance(packageName.toLowerCase(), popular);

    // 编辑距离 <= 2 可能是 typosquatting
    if (distance > 0 && distance <= 2) {
      warnings.push({
        package: packageName,
        similar_to: popular,
        distance: distance,
        severity: distance === 1 ? 'HIGH' : 'MEDIUM'
      });
    }
  }

  return warnings;
}

// 检查当前项目的所有依赖
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
const allDeps = {
  ...pkg.dependencies,
  ...pkg.devDependencies
};

for (const dep of Object.keys(allDeps)) {
  const warnings = checkTyposquatting(dep);
  if (warnings.length > 0) {
    console.error(`[WARN] "${dep}" 可能是 typosquatting:`);
    warnings.forEach(w => console.error(`  → 类似 "${w.similar_to}" (距离: ${w.distance})`));
  }
}
```

## 代码示例

```javascript
// package.json - 安全配置
{
  "scripts": {
    "preinstall": "node scripts/check-typosquatting.js",
    "postinstall": "npm audit"
  }
}

// scripts/check-typosquatting.js
const { execSync } = require('child_process');

const POPULAR_PACKAGES = new Set([
  'react', 'react-dom', 'lodash', 'moment', 'express',
  'axios', 'webpack', 'typescript', 'jest', 'eslint'
]);

function getInstallPackage() {
  // 获取 npm install 的参数
  const args = process.env.npm_config_argv;
  if (!args) return [];

  const parsed = JSON.parse(args);
  const packages = parsed.original.slice(1); // 跳过 'install'

  return packages;
}

function checkPackage(name) {
  // 提取包名（去掉版本号）
  const pkgName = name.split('@')[0];

  for (const popular of POPULAR_PACKAGES) {
    if (isSimilar(pkgName, popular)) {
      console.error(`
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  TYPOSQUATTING WARNING                                    ║
║                                                              ║
║  你正在安装 "${pkgName}"                                      ║
║  这看起来像是流行包 "${popular}" 的拼写错误                    ║
║                                                              ║
║  请确认是否要继续安装                                         ║
╚══════════════════════════════════════════════════════════════╝
      `);
      process.exit(1);
    }
  }
}

function isSimilar(a, b) {
  if (a === b) return false;

  // 编辑距离 <= 2
  const distance = levenshteinDistance(a.toLowerCase(), b.toLowerCase());
  return distance > 0 && distance <= 2;
}
```

```yaml
# GitHub Actions - CI 中检测 typosquatting
name: Check Typosquatting

on:
  pull_request:
    paths:
      - 'package.json'
      - 'package-lock.json'

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for typosquatting
        run: |
          # 提取所有依赖名
          deps=$(cat package.json | jq -r '.dependencies, .devDependencies' | jq -r 'keys[]' | sort | uniq)

          # 流行包列表
          popular="react lodash moment express axios webpack typescript jest eslint"

          for dep in $deps; do
            for pop in $popular; do
              if [[ "${#dep}" -gt 2 ]] && [[ "$dep" != "$pop" ]]; then
                # 简单的相似度检查
                if echo "$dep" | grep -qE "^${pop:0:3}.*${pop: -3}$"; then
                  echo "::warning::依赖 '$dep' 与流行包 '$pop' 相似，请确认是否正确"
                fi
              fi
            done
          done
```

## 参考资料
- [npm Typosquatting Detection](https://blog.npmjs.org/post/162798807125/detecting-typosquatting-attempts)
- [Snyk: Typosquatting Attacks](https://snyk.io/blog/typosquatting-attacks/)
- [Sonatype: Typosquatting Research](https://blog.sonatype.com/typosquatting-attacks-on-the-rise)
- [PyPI Typosquatting Detection](https://github.com/pypa/bandersnatch)
