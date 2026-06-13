# 恶意包 (Malicious Package)

## 一句话风险
攻击者发布伪装成合法库的恶意包，一旦安装便会执行恶意行为，如窃取数据、植入后门或进行挖矿。

## 风险等级
- 严重程度: 🔴严重
- 影响范围: 安装该包的所有项目和环境
- 发生概率: 中

## 场景描述

独立开发者小张在开发一个电商网站，需要实现图片处理功能。他在网上搜索到一篇教程，推荐了一个名为 `image-processor-pro` 的包。小张没有仔细核实，直接运行了 `npm install image-processor-pro`。

实际上，这是一个恶意包。该包在安装时会执行 preinstall 脚本，收集开发者机器上的敏感信息：SSH 密钥、AWS 凭证、浏览器中保存的 Cookie 等。收集完成后，数据被发送到攻击者控制的服务器。

几周后，小张发现自己的 AWS 账户异常，多个 EC2 实例被创建用于挖矿。更糟糕的是，攻击者使用窃取的 SSH 密钥访问了小张的其他服务器，导致更多资产受损。

## 攻击方式
1. 攻击者创建恶意包，模仿合法库的功能和命名
2. 编写安装钩子脚本（preinstall/postinstall），执行恶意行为
3. 将包发布到 npm/PyPI 等公共仓库
4. 通过 SEO 优化、虚假教程、社交媒体推广等方式传播
5. 开发者安装包后，恶意代码立即执行

## 真实案例
- **electron-native-notify (2018)**：恶意包伪装成合法通知库，窃取 Ethereum 钱包文件
- **Python 恶意包浪潮 (2023)**：PyPI 上发现数千个恶意包，伪装成流行库
- **ua-parser-js (2021)**：被劫持后添加恶意代码，影响数百万下载

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查项目中所有依赖的来源是否为官方仓库
- [ ] 验证包名拼写是否正确，警惕拼写相似包
- [ ] 审查 node_modules 中可疑包的 package.json

### 短期加固 (1小时)
- [ ] 使用 `npm view <package>` 检查包的下载量、维护者、更新历史
- [ ] 检查包的 GitHub 仓库是否真实存在且活跃
- [ ] 审查所有依赖的安装脚本（preinstall/postinstall）
- [ ] 使用 `npm audit` 扫描已知恶意包

### 长期建设
- [ ] 建立依赖审核流程，新依赖需人工审查
- [ ] 使用企业级 npm 代理（如 Verdaccio）过滤可疑包
- [ ] 配置 `.npmrc` 禁止执行安装脚本
- [ ] 使用沙箱环境测试新依赖
- [ ] 订阅安全公告，及时了解恶意包情报

## 检测方法

```bash
# 1. 检查包的基本信息
npm view <package-name>
npm view <package-name> --json | jq '{name, version, maintainers, repository}'

# 2. 检查下载量（低下载量需警惕）
npm view <package-name> --json | jq '.time | keys | length'

# 3. 查看包内容
npm pack <package-name> --dry-run

# 4. 检查安装脚本
npm view <package-name> --json | jq '.scripts'
grep -r "preinstall\|postinstall" node_modules/*/package.json

# 5. 使用安全工具
npx npm-check-audit
pip install safety && safety check
```

```python
# Python: 检测可疑包
import subprocess
import json

def check_package_safety(package_name):
    """检查 PyPI 包的基本信息"""
    import requests
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        info = data['info']

        # 检查关键信息
        warnings = []
        if not info.get('home_page'):
            warnings.append("缺少项目主页")
        if not info.get('author'):
            warnings.append("缺少作者信息")
        if not info.get('classifiers'):
            warnings.append("缺少分类信息")

        return {
            'name': info['name'],
            'version': info['version'],
            'author': info.get('author'),
            'warnings': warnings
        }
    except Exception as e:
        return {'error': str(e)}
```

## 代码示例

```javascript
// package.json - 安全配置示例
{
  "name": "my-project",
  "scripts": {
    "postinstall": "node scripts/check-deps.js"
  }
}

// scripts/check-deps.js - 依赖安全检查脚本
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const SUSPICIOUS_SCRIPTS = [
  /curl\s+http/i,
  /wget\s+http/i,
  /eval\s*\(/i,
  /Function\s*\(/i,
  /base64/i,
  /process\.env/i,
];

function checkPackage(pkgPath) {
  const pkgJson = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));

  // 检查脚本
  const scripts = pkgJson.scripts || {};
  for (const [name, script] of Object.entries(scripts)) {
    for (const pattern of SUSPICIOUS_SCRIPTS) {
      if (pattern.test(script)) {
        console.error(`[ALERT] 可疑脚本 ${name}: ${script}`);
      }
    }
  }

  // 检查依赖
  if (pkgJson.dependencies) {
    const deps = Object.keys(pkgJson.dependencies);
    if (deps.length > 50) {
      console.warn(`[WARN] 依赖数量过多: ${deps.length}`);
    }
  }
}

// 遍历所有依赖
const nodeModules = path.join(__dirname, '..', 'node_modules');
if (fs.existsSync(nodeModules)) {
  const pkgs = fs.readdirSync(nodeModules);
  pkgs.forEach(pkg => {
    const pkgPath = path.join(nodeModules, pkg, 'package.json');
    if (fs.existsSync(pkgPath)) {
      checkPackage(pkgPath);
    }
  });
}
```

```
# .npmrc - 禁止执行脚本配置
# 生产环境推荐配置
ignore-scripts=true

# 或者使用 allow-scripts 精确控制
# npm install -g @npmcli/install-man-scripts
```

## 参考资料
- [npm Malicious Packages Advisory](https://www.npmjs.com/advisories)
- [PyPI Malware Checks](https://github.com/pypa/bandit)
- [Snyk Vulnerability DB](https://security.snyk.io/)
- [Sonatype Malicious Package Detection](https://blog.sonatype.com/)
