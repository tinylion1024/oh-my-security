# 弱密码风险（Weak Password）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0-20/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户使用 admin/123456 等弱密码注册账号，黑客轻松猜解密码登录，导致账号被盗、数据泄露甚至资金损失。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 允许用户设置任意密码（无强度检查）
- [ ] 允许常见弱密码（如 123456、password、qwerty）
- [ ] 允许与用户名/邮箱相同的密码
- [ ] 密码长度无最低要求（或低于8位）
- [ ] 未检测密码是否在泄露数据库中
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
注册/修改密码时强制密码强度检查：最少8位 + 包含数字和字母 + 禁用常见弱密码列表。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 添加密码强度检查函数：最少8位，包含数字和字母
   - [ ] 禁用 Top 100 常见弱密码（见L2代码示例）
   - [ ] 禁止密码与用户名/邮箱相同
   - [ ] 前端实时显示密码强度提示

2. **短期行动**（本周可完成，免费）
   - [ ] 集成 Have I Been Pwned API 检测泄露密码
   - [ ] 添加密码强度可视化指示器（弱/中/强）
   - [ ] 引导用户使用密码管理器生成密码

3. **长期行动**（规划中，低成本）
   - [ ] 强制新用户满足密码强度要求
   - [ ] 渐进式要求老用户更新弱密码
   - [ ] 引导用户开启双因素认证（2FA）

### 推荐工具
- **免费**：
  - [zxcvbn](https://github.com/dropbox/zxcvbn) - Dropbox开源密码强度检测库
  - [Have I Been Pwned API](https://haveibeenpwned.com/API/v3) - 免费密码泄露检测
  - [password-validator](https://www.npmjs.com/package/password-validator) - npm密码验证库

- **低成本**：
  - [Auth0](https://auth0.com/) - 内置密码强度策略，免费7000用户/月
  - [Supabase Auth](https://supabase.com/auth) - 密码策略可配置，免费50000用户/月

### 验证方法
- [ ] 测试步骤1：尝试注册密码 "123456"，应被拒绝
- [ ] 测试步骤2：尝试注册密码 "password"，应被拒绝
- [ ] 测试步骤3：尝试注册与用户名相同的密码，应被拒绝
- [ ] 测试步骤4：尝试注册8位以下密码，应被拒绝
- [ ] 测试步骤5：尝试注册 "Abc12345"，应通过

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有5000个用户，没有密码强度要求。某天你发现：
- 约15%的用户使用 Top 100 弱密码（如 123456、password、qwerty）
- 约8%的用户密码与邮箱前缀相同
- 约5%的用户密码在已知泄露数据库中

攻击者只需尝试常见弱密码，就能以约20%的成功率登录用户账号：
```
# 攻击脚本伪代码
for user in user_list:
    for weak_password in top_100_weak_passwords:
        if try_login(user.email, weak_password):
            print(f"成功: {user.email}:{weak_password}")
```

**真实损失案例**：
- 某独立开发者的SaaS产品，管理员账号使用 "admin123"
- 攻击者猜解成功后，获取所有用户数据
- 最终损失：用户流失、法律诉讼、产品下线

### 攻击路径（简化版）

**第一阶段：信息收集**
1. 攻击者收集目标用户名/邮箱（公开信息、社工库、爬虫）
2. 识别目标网站是否有密码强度要求

**第二阶段：弱密码猜解**
3. 使用 Top 100/1000 弱密码列表尝试登录
4. 尝试密码与用户名相同的组合
5. 尝试常见模式：用户名+123、用户名+年份

**第三阶段：账号接管**
6. 成功登录后修改密码和邮箱
7. 窃取数据或发起进一步攻击
8. 利用信任关系进行钓鱼

### 防御实施（低成本方案）

#### 方案A：免费方案（纯自建）

**1. 密码强度检测函数**

```python
# Python 密码强度检测
import re

# Top 100 常见弱密码（实际应从文件加载更大列表）
TOP_100_WEAK_PASSWORDS = {
    '123456', 'password', '12345678', 'qwerty', '123456789',
    '12345', '1234', '111111', '1234567', 'dragon',
    '123123', 'baseball', 'abc123', 'football', 'monkey',
    'letmein', 'shadow', 'master', '666666', 'qwertyuiop',
    '123321', 'mustang', '1234567890', 'michael', '654321',
    'superman', '1qaz2wsx', '7777777', 'fuckyou', '121212',
    '000000', 'qazwsx', '123qwe', 'killer', 'trustno1',
    'jordan', 'jennifer', 'zxcvbnm', 'asdfgh', 'hunter',
    'buster', 'soccer', 'harley', 'batman', 'andrew',
    'tigger', 'sunshine', 'iloveyou', '2000', 'charlie',
    'robert', 'thomas', 'hockey', 'ranger', 'daniel',
    'starwars', 'klaster', '112233', 'george', 'computer',
    'michelle', 'jessica', 'pepper', '1111', 'zxcvbn',
    '555555', '11111111', '131313', 'freedom', '777777',
    'pass', 'maggie', '159753', 'aaaaaa', 'ginger',
    'princess', 'joshua', 'cheese', 'amanda', 'summer',
    'love', 'ashley', 'nicole', 'chelsea', 'biteme',
    'matthew', 'access', 'yankees', '987654321', 'dallas',
    'austin', 'thunder', 'taylor', 'matrix', 'william'
}

def validate_password(password: str, username: str = None, email: str = None) -> tuple[bool, str]:
    """
    验证密码强度
    
    返回: (是否通过, 错误消息)
    """
    # 1. 基本长度检查
    if len(password) < 8:
        return False, "密码长度至少8位"
    
    if len(password) > 128:
        return False, "密码长度不能超过128位"
    
    # 2. 检查是否在常见弱密码列表
    if password.lower() in TOP_100_WEAK_PASSWORDS:
        return False, "该密码过于常见，请更换"
    
    # 3. 检查是否包含用户名或邮箱
    if username and username.lower() in password.lower():
        return False, "密码不能包含用户名"
    
    if email:
        email_prefix = email.split('@')[0].lower()
        if email_prefix in password.lower():
            return False, "密码不能包含邮箱前缀"
    
    # 4. 字符类型检查
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not has_letter or not has_digit:
        return False, "密码必须包含字母和数字"
    
    # 5. 键盘模式检查（可选增强）
    keyboard_patterns = [
        'qwerty', 'asdfgh', 'zxcvbn', 'qwertyuiop',
        '1234567890', '0987654321'
    ]
    password_lower = password.lower()
    for pattern in keyboard_patterns:
        if pattern in password_lower:
            return False, "密码包含常见键盘模式，请更换"
    
    return True, "密码强度合格"


def calculate_password_strength(password: str) -> dict:
    """
    计算密码强度分数（0-100）
    
    返回: {
        'score': 0-100,
        'level': 'weak' | 'medium' | 'strong',
        'feedback': list[str]
    }
    """
    score = 0
    feedback = []
    
    # 长度评分
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    
    # 字符多样性评分
    if re.search(r'[a-z]', password):
        score += 10
    if re.search(r'[A-Z]', password):
        score += 10
    if re.search(r'\d', password):
        score += 10
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 20
    
    # 扣分项
    if password.lower() in TOP_100_WEAK_PASSWORDS:
        score -= 50
        feedback.append("该密码在常见弱密码列表中")
    
    if re.search(r'(.)\1{2,}', password):  # 连续相同字符
        score -= 10
        feedback.append("避免连续相同字符")
    
    # 键盘模式
    keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '1234567890']
    for pattern in keyboard_patterns:
        if pattern in password.lower():
            score -= 15
            feedback.append("避免键盘顺序字符")
            break
    
    # 限制分数范围
    score = max(0, min(100, score))
    
    # 强度等级
    if score < 40:
        level = 'weak'
    elif score < 70:
        level = 'medium'
    else:
        level = 'strong'
    
    return {
        'score': score,
        'level': level,
        'feedback': feedback
    }
```

**2. 泄露密码检测**

```python
import hashlib
import requests

async def check_password_breach(password: str) -> int:
    """
    检查密码是否在已知泄露数据库中
    
    使用 k-anonymity 协议，只发送密码哈希前5位
    
    返回: 泄露次数（0表示未泄露）
    """
    # SHA-1 哈希
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]
    
    try:
        # 调用 Have I Been Pwned API
        response = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=5
        )
        response.raise_for_status()
        
        # 检查完整哈希是否在结果中
        for line in response.text.splitlines():
            hash_suffix, count = line.split(':')
            if hash_suffix == suffix:
                return int(count)
        
        return 0  # 未泄露
        
    except Exception as e:
        # API 失败时不阻止注册，记录日志
        print(f"泄露检测失败: {e}")
        return 0


# 使用示例
async def register_user(email: str, username: str, password: str):
    # 1. 基本强度检查
    valid, msg = validate_password(password, username, email)
    if not valid:
        return {'error': msg}
    
    # 2. 泄露检查
    breach_count = await check_password_breach(password)
    if breach_count > 0:
        return {
            'error': f'该密码已在数据泄露中出现 {breed_count} 次，请更换密码'
        }
    
    # 3. 创建用户（实际应使用 bcrypt/argon2 哈希）
    # ...
    
    return {'success': True}
```

**3. 前端实时反馈**

```typescript
// React 组件示例
import { useState, useMemo } from 'react';

interface PasswordStrength {
  score: number;
  level: 'weak' | 'medium' | 'strong';
  feedback: string[];
}

function PasswordInput() {
  const [password, setPassword] = useState('');
  
  const strength = useMemo<PasswordStrength>(() => {
    if (!password) {
      return { score: 0, level: 'weak', feedback: [] };
    }
    
    // 调用后端 API 或前端计算
    const score = calculateStrength(password);
    return score;
  }, [password]);
  
  return (
    <div className="space-y-2">
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        className="w-full p-2 border rounded"
        placeholder="至少8位，包含字母和数字"
      />
      
      {/* 强度指示器 */}
      <div className="space-y-1">
        <div className="flex gap-1">
          <div className={`h-2 flex-1 rounded ${
            strength.score > 30 ? 'bg-red-400' : 'bg-gray-200'
          }`} />
          <div className={`h-2 flex-1 rounded ${
            strength.score > 60 ? 'bg-yellow-400' : 'bg-gray-200'
          }`} />
          <div className={`h-2 flex-1 rounded ${
            strength.score > 80 ? 'bg-green-400' : 'bg-gray-200'
          }`} />
        </div>
        
        <p className="text-sm text-gray-600">
          密码强度: {strength.level === 'weak' ? '弱' : 
                     strength.level === 'medium' ? '中' : '强'}
        </p>
        
        {strength.feedback.map((msg, i) => (
          <p key={i} className="text-sm text-red-600">• {msg}</p>
        ))}
      </div>
    </div>
  );
}
```

**局限性**：
- 需要维护弱密码列表
- 泄露检测依赖第三方API
- 无统一管理界面

---

#### 方案B：低成本方案（使用认证服务）

**使用 Auth0 密码策略**

Auth0 内置强大的密码策略配置：

```javascript
// Auth0 配置（在 Dashboard 中设置）
{
  "password_policy": "excellent",  // good | fair | excellent | low
  "password_complexity_options": {
    "min_length": 8,
    "min_uppercase": 1,
    "min_lowercase": 1,
    "min_number": 1,
    "min_symbol": 0
  },
  "password_history": {
    "enable": true,
    "size": 5  // 禁止最近5次使用的密码
  },
  "password_no_personal_info": {
    "enable": true  // 禁止包含用户个人信息
  },
  "password_dictionary": {
    "enable": true,
    "dictionary": ["password", "qwerty", "123456"]  // 自定义禁用词
  }
}
```

**使用 Supabase Auth**

```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Supabase 支持密码强度验证
// 在 Dashboard > Authentication > Policies 中配置

// 注册时自动验证密码强度
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'userPassword123',
  options: {
    data: {
      // 额外用户信息
    }
  }
})

// Supabase 自动拒绝不符合策略的密码
if (error) {
  console.error(error.message)  // "Password is too weak"
}
```

**优势**：
- 开箱即用的密码策略
- 自动检测泄露密码
- 无需维护弱密码列表
- 提供管理界面
- 免费额度充足

---

#### 方案C：增强方案（+$10-20/月）

在方案B基础上添加：

**1. 使用 zxcvbn 进行智能检测**

```javascript
import zxcvbn from 'zxcvbn';

function checkPasswordStrength(password: string, userInputs: string[] = []) {
  const result = zxcvbn(password, userInputs);
  
  // result.score: 0-4 (0=weak, 4=strong)
  // result.feedback: 改进建议
  // result.crack_times_display: 破解时间估算
  
  if (result.score < 3) {
    return {
      valid: false,
      message: result.feedback.warning || '密码强度不足',
      suggestions: result.feedback.suggestions
    };
  }
  
  return { valid: true };
}

// 使用示例
const result = checkPasswordStrength(
  'MyP@ssw0rd!',
  ['john', 'john@example.com']  // 用户相关信息，用于检测
);

// zxcvbn 会检测:
// - 常见密码模式
// - 键盘序列
// - 日期格式
// - 重复字符
// - 包含用户信息
```

**2. 密码生成器集成**

```typescript
// 引导用户使用密码管理器生成的密码
function generateSecurePassword(): string {
  const length = 16;
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
  
  // 使用 crypto.getRandomValues 生成安全的随机密码
  const array = new Uint32Array(length);
  crypto.getRandomValues(array);
  
  let password = '';
  for (let i = 0; i < length; i++) {
    password += charset[array[i] % charset.length];
  }
  
  return password;
}

// 前端生成按钮
<button onClick={() => {
  const password = generateSecurePassword();
  setPasswordField(password);
}}>
  生成安全密码
</button>
```

---

### 决策树

```
你的产品是否有用户注册功能？
├── 否 → 无需防护
└── 是 →
    你使用的是什么认证方案？
    ├── 自建认证 → 使用方案A（免费，需自行实现）
    ├── Auth0 → 使用方案B（免费7000用户/月）
    ├── Supabase Auth → 使用方案B（免费50000用户/月）
    └── 其他SaaS → 检查是否支持密码策略配置

    你的用户数据是否敏感？
    ├── 是 → 添加泄露检测 + zxcvbn（方案C）
    └── 否 → 基础密码强度检查足够
```

### 完整代码示例

**Next.js API 完整实现**

```typescript
// app/api/auth/register/route.ts
import { NextResponse } from 'next/server';
import { hash } from 'bcryptjs';
import { zxcvbn } from 'zxcvbn';

// 常见弱密码列表
const WEAK_PASSWORDS = new Set([
  '123456', 'password', '12345678', 'qwerty', '123456789',
  // ... 更多
]);

export async function POST(req: Request) {
  try {
    const { email, username, password } = await req.json();
    
    // 1. 基本验证
    if (!email || !username || !password) {
      return NextResponse.json(
        { error: '请填写所有必填项' },
        { status: 400 }
      );
    }
    
    // 2. 密码强度检查
    const passwordCheck = validatePasswordStrength(
      password,
      username,
      email
    );
    
    if (!passwordCheck.valid) {
      return NextResponse.json(
        { error: passwordCheck.message },
        { status: 400 }
      );
    }
    
    // 3. 泄露检测
    const breachCount = await checkPasswordBreach(password);
    if (breachCount > 100) {  // 超过100次泄露则拒绝
      return NextResponse.json(
        { error: '该密码极不安全，请更换' },
        { status: 400 }
      );
    }
    
    // 4. 哈希密码
    const hashedPassword = await hash(password, 12);
    
    // 5. 创建用户（示例）
    const user = await createUser({
      email,
      username,
      password: hashedPassword,
    });
    
    return NextResponse.json({
      success: true,
      user: { id: user.id, email: user.email }
    });
    
  } catch (error) {
    console.error('Registration error:', error);
    return NextResponse.json(
      { error: '注册失败，请稍后重试' },
      { status: 500 }
    );
  }
}

function validatePasswordStrength(
  password: string,
  username: string,
  email: string
): { valid: boolean; message: string } {
  // 长度检查
  if (password.length < 8) {
    return { valid: false, message: '密码长度至少8位' };
  }
  
  // 弱密码列表
  if (WEAK_PASSWORDS.has(password.toLowerCase())) {
    return { valid: false, message: '该密码过于常见，请更换' };
  }
  
  // 包含用户名或邮箱
  if (password.toLowerCase().includes(username.toLowerCase())) {
    return { valid: false, message: '密码不能包含用户名' };
  }
  
  const emailPrefix = email.split('@')[0];
  if (password.toLowerCase().includes(emailPrefix.toLowerCase())) {
    return { valid: false, message: '密码不能包含邮箱前缀' };
  }
  
  // 使用 zxcvbn 进行深度检测
  const result = zxcvbn(password, [username, email]);
  if (result.score < 2) {
    return {
      valid: false,
      message: result.feedback.warning || '密码强度不足'
    };
  }
  
  return { valid: true, message: '' };
}

async function checkPasswordBreach(password: string): Promise<number> {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hashBuffer = await crypto.subtle.digest('SHA-1', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray
    .map(b => b.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase();
  
  const prefix = hashHex.substring(0, 5);
  const suffix = hashHex.substring(5);
  
  try {
    const response = await fetch(
      `https://api.pwnedpasswords.com/range/${prefix}`
    );
    const text = await response.text();
    
    for (const line of text.split('\n')) {
      const [hashSuffix, count] = line.split(':');
      if (hashSuffix === suffix) {
        return parseInt(count, 10);
      }
    }
    
    return 0;
  } catch {
    return 0;  // API 失败时不阻止
  }
}
```

---

## L3 企业版（深耕版）

企业级弱密码防护需要更完善的策略体系，包括：

**1. 密码策略管理**
- 自适应密码策略
- 密码生命周期管理
- 多因素认证强制
- 密码泄露监控告警

**2. 高级检测能力**
- 深度密码分析
- 用户行为分析
- 威胁情报集成
- 暗网监控

**3. 用户教育体系**
- 密码安全培训
- 密码管理器推广
- 安全意识测试

**详细内容请参考企业级案例**：
- [企业级密码策略](../../enterprise/bizsec/auth/password-policy-enterprise.md)
- [身份安全管理](../../enterprise/infosec/identity-management.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基本检查 | $0 | 1小时 | 0.5小时/月 | MVP阶段 |
| L2-方案A（自建） | $0 | 3小时 | 1小时/月 | 技术团队，需定制化 |
| L2-方案B（SaaS） | $0 | 0.5小时 | 0小时/月 | 快速上线，无运维 |
| L2-方案C（增强） | $10-20 | 2小时 | 0.5小时/月 | 处理敏感数据 |
| L3-企业级 | $100+ | 需评估 | 专职团队 | 企业级应用 |

---

## 常见问题

**Q: 强密码要求会不会降低注册转化率？**
A: 短期可能略有影响，但长期来看，安全的产品更容易获得用户信任。可以通过密码生成器、实时强度反馈来改善体验。

**Q: 泄露检测会不会泄露我的密码？**
A: 不会。k-anonymity协议只发送密码哈希的前5位，完整密码永远不会发送给第三方。

**Q: 如果用户坚持使用弱密码怎么办？**
A: 对于非关键业务，可以允许但发送安全提醒；对于关键业务（支付、隐私数据），应强制要求强密码或开启2FA。

**Q: 密码策略如何平衡安全性和用户体验？**
A: 推荐方案：
- 长度优先：鼓励使用更长的密码（12位以上）
- 实时反馈：显示密码强度和改进建议
- 密码生成器：提供一键生成安全密码的选项
- 渐进式要求：新用户强制要求，老用户逐步引导

---

## 相关资源

**工具**
- [zxcvbn](https://github.com/dropbox/zxcvbn) - 智能密码强度检测
- [Have I Been Pwned](https://haveibeenpwned.com/) - 密码泄露检测
- [Auth0](https://auth0.com/) - 身份认证服务
- [Supabase Auth](https://supabase.com/auth) - 开源认证服务

**学习资源**
- [NIST密码指南](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP密码存储速查表](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Dropbox密码强度分析](https://dropbox.tech/security/zxcvbn-realistic-password-strength-estimation)

**相关案例**
- [撞库攻击](./credential-stuffing.md)
- [暴力破解](./brute-force.md)
- [密码重置漏洞](./password-reset-flaw.md)
