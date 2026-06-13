# 原型污染 (Prototype Pollution)

## 一句话风险
攻击者通过修改 JavaScript 对象的原型链，向所有对象注入恶意属性，导致程序行为异常或执行任意代码。

## 风险等级
- 严重程度: 🟠高
- 影响范围: JavaScript/Node.js 项目
- 发生概率: 中

## 场景描述

独立开发者小李开发了一个电商平台，其中包含一个用于合并用户配置的工具函数。该函数使用递归方式深度合并对象，但未对键名进行过滤。

攻击者发现这个漏洞后，在商品评论的 JSON 数据中注入了 `__proto__` 属性。当服务端解析并合并这个 JSON 时，所有新创建的对象都被污染，添加了攻击者控制的属性。

攻击者进一步利用这个漏洞，在 `__proto__` 中注入了恶意方法。当管理员访问后台时，污染的属性触发了远程代码执行，攻击者成功获取了服务器权限。

## 攻击方式
1. 识别存在深度合并/克隆功能且未过滤的代码
2. 构造包含 `__proto__`、`constructor`、`prototype` 的恶意输入
3. 递归合并时，恶意属性被注入到 Object.prototype
4. 所有后续创建的对象都继承污染的属性
5. 触发条件执行恶意代码（如模板引擎、沙箱逃逸）

## 真实案例
- **jQuery < 3.4.0 (2019)**：`$.extend` 存在原型污染漏洞，影响数百万网站
- **lodash < 4.17.12 (2019)**：`_.merge`、`_.defaultsDeep` 存在原型污染
- **minimist (2020)**：命令行参数解析存在原型污染，影响大量工具
- **axios (2021)**：特定场景下存在原型污染风险

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查依赖版本，升级已知漏洞版本
- [ ] 运行 `npm audit` 检查原型污染漏洞
- [ ] 审查项目中使用 `Object.assign`、`...spread` 的代码

### 短期加固 (1小时)
- [ ] 审查所有深度合并/克隆函数的实现
- [ ] 使用 `Object.create(null)` 创建纯净对象
- [ ] 添加键名过滤逻辑，拒绝 `__proto__` 等特殊键
- [ ] 升级 lodash、axios 等高风险依赖

### 长期建设
- [ ] 使用 TypeScript 配置 `{ "noImplicitAny": true }` 增强类型检查
- [ ] 实施输入验证，使用 JSON Schema 验证外部数据
- [ ] 集成 SAST 工具检测原型污染
- [ ] 使用 `Object.freeze(Object.prototype)` 冻结原型
- [ ] 代码审查关注对象操作安全性

## 检测方法

```javascript
// 1. 检测原型污染的简单测试
const test = {};
if (test.__proto__.polluted === 'yes') {
  console.error('检测到原型污染!');
}

// 2. 运行时检测
Object.defineProperty(Object.prototype, '__proto__', {
  set: function(value) {
    console.error('[ALERT] 尝试修改 __proto__');
    console.trace();
  }
});

// 3. 使用安全工具检测
// npm install -g snyk
// snyk test

// 4. 代码审计关键词
// 搜索: __proto__, constructor.prototype, Object.prototype
// grep -r "__proto__\|constructor\.prototype" src/
```

```javascript
// 单元测试：检测原型污染
function testPrototypePollution(mergeFunction) {
  const originalProto = Object.prototype.test;

  try {
    // 尝试污染原型
    mergeFunction({}, JSON.parse('{"__proto__":{"test":"polluted"}}'));

    // 检查是否被污染
    const testObj = {};
    if (testObj.test === 'polluted') {
      throw new Error('函数存在原型污染漏洞!');
    }
  } finally {
    // 清理
    if (originalProto === undefined) {
      delete Object.prototype.test;
    } else {
      Object.prototype.test = originalProto;
    }
  }
}

// 测试你的合并函数
testPrototypePollution(yourMergeFunction);
```

## 代码示例

```javascript
// ❌ 不安全的深度合并
function unsafeMerge(target, source) {
  for (const key in source) {
    if (typeof source[key] === 'object' && source[key] !== null) {
      target[key] = target[key] || {};
      unsafeMerge(target[key], source[key]);  // 未过滤 key
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// ✅ 安全的深度合并
function safeMerge(target, source) {
  const FORBIDDEN_KEYS = ['__proto__', 'constructor', 'prototype'];

  for (const key in source) {
    // 过滤危险键
    if (FORBIDDEN_KEYS.includes(key)) {
      console.warn(`拒绝危险键: ${key}`);
      continue;
    }

    if (typeof source[key] === 'object' && source[key] !== null) {
      target[key] = target[key] || {};
      safeMerge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}

// ✅ 使用 Map 代替普通对象
function safeMergeWithMap(target, source) {
  const result = new Map(target);

  for (const [key, value] of source) {
    // Map 不存在原型链污染问题
    if (value instanceof Map) {
      result.set(key, safeMergeWithMap(result.get(key) || new Map(), value));
    } else {
      result.set(key, value);
    }
  }

  return result;
}

// ✅ 使用 Object.create(null) 创建纯净对象
function createSafeObject() {
  return Object.create(null);  // 无原型链
}

// ✅ 冻结原型（应用启动时执行一次）
function freezePrototype() {
  Object.freeze(Object.prototype);
  Object.freeze(Object);
  console.log('原型链已冻结');
}
```

```javascript
// Express 中间件：防护原型污染
function prototypePollutionGuard(req, res, next) {
  const FORBIDDEN_KEYS = ['__proto__', 'constructor', 'prototype'];

  function sanitize(obj) {
    if (typeof obj !== 'object' || obj === null) return obj;

    for (const key of Object.keys(obj)) {
      if (FORBIDDEN_KEYS.includes(key)) {
        delete obj[key];
        console.warn(`已移除危险属性: ${key}`);
        continue;
      }

      if (typeof obj[key] === 'object') {
        sanitize(obj[key]);
      }
    }

    return obj;
  }

  // 清理请求体
  if (req.body) {
    req.body = sanitize(req.body);
  }

  // 清理查询参数
  if (req.query) {
    req.query = sanitize(req.query);
  }

  next();
}

// 使用
app.use(express.json());
app.use(prototypePollutionGuard);
```

```typescript
// TypeScript 类型安全的配置合并
interface SafeConfig {
  [key: string]: string | number | boolean | SafeConfig;
}

function mergeConfig<T extends SafeConfig>(
  target: T,
  source: Partial<T>
): T {
  const FORBIDDEN_KEYS = new Set(['__proto__', 'constructor', 'prototype']);

  const result = { ...target };

  for (const key in source) {
    if (FORBIDDEN_KEYS.has(key)) {
      throw new Error(`禁止使用保留键: ${key}`);
    }

    const value = source[key];
    if (value !== undefined) {
      if (typeof value === 'object' && value !== null) {
        result[key] = mergeConfig(result[key], value) as T[Extract<keyof T, string>];
      } else {
        result[key] = value as T[Extract<keyof T, string>];
      }
    }
  }

  return result;
}
```

```yaml
# GitHub Actions - 原型污染检测
name: Security Check

on: [push, pull_request]

jobs:
  prototype-pollution:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Check for dangerous patterns
        run: |
          echo "检查危险模式..."
          grep -rn "__proto__" src/ && echo "发现 __proto__ 使用" && exit 1
          grep -rn "constructor\.prototype" src/ && echo "发现 constructor.prototype 使用" && exit 1
          echo "检查通过"
```

## 参考资料
- [Prototype Pollution in Node.js](https://nodejs.org/en/docs/guides/security/)
- [OWASP: Prototype Pollution](https://owasp.org/www-community/attacks/Prototype_Pollution)
- [Snyk: Prototype Pollution Guide](https://snyk.io/blog/prototype-pollution-javascript/)
- [PortSwigger: Prototype Pollution](https://portswigger.net/web-security/prototype-pollution)
- [npm Advisory List](https://www.npmjs.com/advisories?search=prototype%20pollution)
