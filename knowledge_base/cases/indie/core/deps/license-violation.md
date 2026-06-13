# License 违规 (License Violation)

## 一句话风险
项目使用了与自身许可证不兼容的开源依赖，可能面临法律诉讼、赔偿或被迫开源代码的风险。

## 风险等级
- 严重程度: 🟡中
- 影响范围: 所有商业项目
- 发生概率: 高

## 场景描述

独立开发者小张开发了一款商业 SaaS 产品，计划通过订阅收费盈利。在开发过程中，他使用了多个开源库来加速开发，包括一个功能强大的数据处理库。

产品上线半年后，小张收到了律师函，指控他的产品违反了某依赖库的 GPL 许可证。该库要求使用它的项目必须开源，但小张的产品是闭源商业软件。

经过调查，这个库是通过间接依赖引入的，小张并未注意到它的许可证类型。最终，小张面临两个选择：将整个产品开源，或者支付高额许可费用。这对一个独立开发者来说是毁灭性的打击。

## 攻击方式（风险场景）
1. 开发者未检查依赖的许可证类型
2. 通过间接依赖引入不兼容许可证的库
3. 在商业产品中使用 GPL/AGPL 许可的代码
4. 原作者或组织发起法律诉讼
5. 面临代码强制开源或经济赔偿

## 真实案例
- **VMware vs Christoph Hellwig (2015)**：因 Linux 内核 GPL 违规被起诉
- **Jitsi (2020)**：多家公司因 AGPL 违规收到律师函
- **MongoDB (2018)**：修改许可证为 SSPL 防止云厂商白嫖
- **React 专利条款争议 (2017)**：Facebook 的 BSD+Patents 引发争议

## 防御建议

### 立即行动 (5分钟)
- [ ] 运行 `npx license-checker` 检查所有依赖许可证
- [ ] 列出项目中所有使用的依赖
- [ ] 确认产品是否为商业/闭源项目

### 短期加固 (1小时)
- [ ] 建立允许使用的许可证白名单
- [ ] 检查并替换不兼容许可证的依赖
- [ ] 审查间接依赖的许可证
- [ ] 创建 LICENSE 文件和第三方许可声明

### 长期建设
- [ ] 在 CI/CD 中集成许可证检查
- [ ] 建立依赖审核流程
- [ ] 定期审查依赖许可证变化
- [ ] 使用企业级工具持续监控（如 FOSSA、Snyk）
- [ ] 咨询律师，制定合规策略

## 检测方法

```bash
# 1. 使用 license-checker 检查许可证
npx license-checker --json
npx license-checker --onlyAllow 'MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause'

# 2. 使用 npm license
npm license

# 3. 检查单个包的许可证
npm view <package> license
npm view <package> --json | jq '.license'

# 4. 使用 SPDX 检查
npx spdx-satisfies

# 5. 检查间接依赖
npm ls --all --json | jq '.. | .license? | select(. != null)'
```

```javascript
// 许可证检查脚本
const ALLOWED_LICENSES = [
  'MIT',
  'ISC',
  'Apache-2.0',
  'BSD-2-Clause',
  'BSD-3-Clause',
  '0BSD',
  'Unlicense'
];

const COPYLEFT_LICENSES = [
  'GPL-2.0',
  'GPL-3.0',
  'AGPL-3.0',
  'LGPL-2.1',
  'LGPL-3.0',
  'MPL-2.0',
  'CDDL-1.0',
  'EPL-1.0'
];

const PROPRIETARY_LICENSES = [
  'SEE LICENSE IN LICENSE',
  'UNLICENSED',
  'PROPRIETARY'
];

function checkLicenses() {
  const { execSync } = require('child_process');
  const licenses = JSON.parse(execSync('npx license-checker --json', { encoding: 'utf8' }));

  const issues = [];
  const warnings = [];

  for (const [path, info] of Object.entries(licenses)) {
    const pkgName = info.name || path;
    const licenses = Array.isArray(info.licenses) ? info.licenses : [info.licenses];

    for (const license of licenses) {
      // 检查 copyleft 许可证
      if (COPYLEFT_LICENSES.some(l => license.includes(l))) {
        issues.push({
          package: pkgName,
          license: license,
          issue: 'COPYLEFT',
          severity: 'HIGH',
          message: `使用 copyleft 许可证 ${license}，可能需要开源您的代码`
        });
      }

      // 检查专有许可证
      if (PROPRIETARY_LICENSES.includes(license)) {
        issues.push({
          package: pkgName,
          license: license,
          issue: 'PROPRIETARY',
          severity: 'CRITICAL',
          message: `使用专有许可证，可能存在法律风险`
        });
      }

      // 检查未知许可证
      if (!ALLOWED_LICENSES.includes(license) && !COPYLEFT_LICENSES.includes(license)) {
        warnings.push({
          package: pkgName,
          license: license,
          issue: 'UNKNOWN',
          severity: 'MEDIUM',
          message: `许可证 ${license} 未在白名单中`
        });
      }
    }
  }

  return { issues, warnings };
}

const result = checkLicenses();

if (result.issues.length > 0) {
  console.error('\n❌ 严重许可证问题:');
  result.issues.forEach(i => {
    console.error(`  ${i.package}: ${i.message}`);
  });
  process.exit(1);
}

if (result.warnings.length > 0) {
  console.warn('\n⚠️  许可证警告:');
  result.warnings.forEach(w => {
    console.warn(`  ${w.package}: ${w.message}`);
  });
}

console.log('\n✅ 许可证检查通过');
```

## 代码示例

```jsonc
// package.json - 许可证配置
{
  "name": "my-commercial-app",
  "license": "UNLICENSED",  // 商业软件，不使用开源许可证
  "private": true,
  "scripts": {
    "license-check": "license-checker --onlyAllow 'MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause'",
    "license-report": "license-checker --json --out license-report.json",
    "license-summary": "license-checker --summary"
  },
  "dependencies": {
    "express": "^4.18.2",     // MIT ✓
    "lodash": "^4.17.21",     // MIT ✓
    "moment": "^2.29.4"       // MIT ✓
  }
}
```

```javascript
// .license-checker.json - 许可证检查配置
{
  "license": "MIT",
  "licenses": {
    "MIT": {
      "color": "green",
      "label": "MIT License"
    },
    "ISC": {
      "color": "green",
      "label": "ISC License"
    },
    "Apache-2.0": {
      "color": "green",
      "label": "Apache 2.0"
    },
    "GPL-3.0": {
      "color": "red",
      "label": "GPL 3.0 - 商业项目慎用!"
    },
    "AGPL-3.0": {
      "color": "red",
      "label": "AGPL 3.0 - 网络服务也需要开源!"
    }
  }
}
```

```yaml
# GitHub Actions - 许可证检查
name: License Check

on:
  push:
    branches: [main]
  pull_request:

jobs:
  license-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: npm ci

      - name: Check licenses
        run: |
          npx license-checker --summary
          npx license-checker --onlyAllow 'MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause;0BSD' --excludePrivatePackages

      - name: Generate license report
        run: npx license-checker --json --out license-report.json

      - name: Upload license report
        uses: actions/upload-artifact@v4
        with:
          name: license-report
          path: license-report.json

      - name: Check for copyleft
        run: |
          if npx license-checker --json | jq -e 'to_entries[] | select(.value.licenses | test("GPL|AGPL|LGPL"))' > /dev/null; then
            echo "::error::发现 copyleft 许可证，商业项目可能不兼容"
            exit 1
          fi
```

```markdown
# THIRD-PARTY-NOTICES.md - 第三方许可声明模板

# Third-Party Notices

This project uses the following third-party packages:

## MIT License

The following packages are licensed under the MIT License:

### express (v4.18.2)
Copyright (c) 2009-2014 TJ Holowaychuk <tj@vision-media.ca>

Permission is hereby granted, free of charge, to any person obtaining a copy...
[Full MIT License text]

### lodash (v4.17.21)
Copyright OpenJS Foundation and other contributors <https://openjsf.org/>

Permission is hereby granted, free of charge, to any person obtaining a copy...
[Full MIT License text]

## Apache License 2.0

### axios (v1.6.0)
Copyright (c) 2014-present Matt Zabriskie

Licensed under the Apache License, Version 2.0...
[Full Apache 2.0 License text]
```

## 常见许可证兼容性表

| 许可证 | 可用于闭源商业 | 要求开源 | 备注 |
|--------|----------------|----------|------|
| MIT | ✅ | ❌ | 最宽松 |
| ISC | ✅ | ❌ | 类似 MIT |
| Apache-2.0 | ✅ | ❌ | 有专利授权 |
| BSD-2/3-Clause | ✅ | ❌ | 宽松 |
| GPL-2.0/3.0 | ❌ | ✅ | 衍生作品必须开源 |
| AGPL-3.0 | ❌ | ✅ | 网络服务也需要开源 |
| LGPL | ⚠️ | 部分 | 链接库可闭源 |
| MPL-2.0 | ⚠️ | 部分 | 文件级别 copyleft |
| SSPL | ❌ | ✅ | MongoDB 专用 |
| UNLICENSED | ❌ | ❌ | 专有，不可商用 |

## 参考资料
- [choosealicense.com](https://choosealicense.com/)
- [SPDX License List](https://spdx.org/licenses/)
- [TLDRLegal](https://www.tldrlegal.com/)
- [npm license-checker](https://github.com/davglass/license-checker)
- [FOSSA License Management](https://fossa.com/)
- [Snyk License Compliance](https://snyk.io/features/open-source-security-license-compliance/)
