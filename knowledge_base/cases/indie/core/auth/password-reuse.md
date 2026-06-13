# 密码复用风险（Password Reuse）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户在其他网站泄露的密码被用于撞库攻击，因为用户习惯在多个网站使用相同密码，导致你的产品账号被批量接管。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 未检测密码是否在已知泄露数据库中
- [ ] 未强制用户定期更换密码
- [ ] 用户可以使用任意密码注册（无泄露检测）
- [ ] 登录时无异常检测（异地、新设备等）
- [ ] 未提供双因素认证（2FA）作为备用防线
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
注册和登录时检测密码是否在泄露数据库中，强制用户更换已泄露密码，并推荐开启2FA作为第二道防线。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 集成 Have I Been Pwned API 检测泄露密码
   - [ ] 注册时拒绝已知泄露密码
   - [ ] 登录时提示密码已泄露，建议修改
   - [ ] 添加"密码已出现在泄露数据库"的友好提示

2. **短期行动**（本周可完成，低成本）
   - [ ] 实现密码强度可视化指示器
   - [ ] 引导用户开启双因素认证（2FA）
   - [ ] 添加异地登录提醒功能
   - [ ] 实现新设备登录邮件通知

3. **长期行动**（规划中）
   - [ ] 建立异常登录检测系统
   - [ ] 实现风险自适应认证
   - [ ] 定期扫描用户密码泄露状态

### 推荐工具
- **免费**：
  - [Have I Been Pwned API](https://haveibeenpwned.com/API/v3) - 密码泄露检测
  - [Pwned Passwords](https://haveibeenpwned.com/Passwords) - 离线密码库查询

- **低成本**：
  - [Auth0 Breached Password Detection](https://auth0.com/) - 自动泄露检测
  - [Stripe Radar](https://stripe.com/radar) - 可借鉴的风控思路

### 验证方法
- [ ] 测试步骤1：使用已知泄露密码注册，应被拒绝或警告
- [ ] 测试步骤2：使用泄露密码登录，应收到修改密码提示
- [ ] 测试步骤3：验证 Have I Been Pwned API 集成正常工作
- [ ] 测试步骤4：测试2FA开启后的登录流程

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有10000个用户，没有密码泄露检测机制。某天发生以下情况：

**攻击时间线**：
1. **Day 0**：某大型网站（如LinkedIn、Adobe）发生数据泄露
2. **Day 1**：泄露数据流入黑市，攻击者获取1000万邮箱+密码组合
3. **Day 2**：攻击者使用自动化脚本撞库
4. **Day 3**：约8%的用户（800个）使用了与泄露相同的密码
5. **Day 4**：攻击者成功接管200+账号，开始数据窃取

**真实损失案例**：
- 2012年 LinkedIn 泄露1.17亿用户数据
- 2013年 Adobe 泄露1.5亿用户数据
- 这些泄露的密码至今仍在被用于撞库攻击

### 攻击路径详解

**第一阶段：数据获取**
```
# 攻击者从暗网获取泄露数据
泄露数据库:
- LinkedIn_2012.txt (117M records)
- Adobe_2013.txt (150M records)
- Collection_1-5.txt (2.2B records)
```

**第二阶段：撞库攻击**
```python
# 撞库攻击伪代码
import requests

def credential_stuffing(target_url, leaked_data):
    success_list = []
    for email, password in leaked_data:
        try:
            response = requests.post(target_url, json={
                'email': email,
                'password': password
            })
            if response.status_code == 200:
                success_list.append((email, password))
                print(f"[SUCCESS] {email}")
        except:
            continue
    return success_list

# 攻击者使用代理池绕过IP限制
# 攻击者控制请求频率绕过频率限制
```

**第三阶段：账号接管**
- 修改密码和绑定邮箱
- 窃取敏感数据
- 利用账号进行钓鱼或诈骗
- 获取付费服务权限

### 防御体系

**第一层：密码泄露检测**
```javascript
// 使用 Have I Been Pwned API
const crypto = require('crypto');

async function checkPasswordLeaked(password) {
  const hash = crypto.createHash('sha1').update(password).digest('hex').toUpperCase();
  const prefix = hash.substring(0, 5);
  const suffix = hash.substring(5);
  
  const response = await fetch(`https://api.pwnedpasswords.com/range/${prefix}`);
  const hashes = await response.text();
  
  // 检查后缀是否在返回的列表中
  const regex = new RegExp(`^${suffix}:(\\d+)$`, 'm');
  const match = hashes.match(regex);
  
  if (match) {
    return { leaked: true, count: parseInt(match[1]) };
  }
  return { leaked: false, count: 0 };
}

// 使用示例
const result = await checkPasswordLeaked('password123');
if (result.leaked) {
  console.log(`密码已在 ${result.count} 次数据泄露中出现！`);
}
```

**第二层：异常登录检测**
```javascript
// 异常登录检测逻辑
async function detectAnomalousLogin(userId, loginContext) {
  const userHistory = await getUserLoginHistory(userId);
  
  const anomalies = [];
  
  // 1. 新设备检测
  if (!userHistory.devices.includes(loginContext.deviceId)) {
    anomalies.push('new_device');
  }
  
  // 2. 异地登录检测
  const lastLocation = userHistory.lastLocation;
  const distance = calculateDistance(lastLocation, loginContext.location);
  if (distance > 500) { // 超过500公里
    anomalies.push('unusual_location');
  }
  
  // 3. 快速异地登录检测
  const timeSinceLastLogin = Date.now() - userHistory.lastLoginTime;
  if (timeSinceLastLogin < 3600000 && distance > 100) {
    anomalies.push('impossible_travel');
  }
  
  return anomalies;
}
```

**第三层：多因素认证（MFA）**
```javascript
// TOTP 双因素认证实现
const speakeasy = require('speakeasy');

// 生成密钥
function generateMFASecret(userEmail) {
  return speakeasy.generateSecret({
    name: `YourApp (${userEmail})`,
    length: 20
  });
}

// 验证 TOTP
function verifyMFAToken(secret, token) {
  return speakeasy.totp.verify({
    secret: secret,
    encoding: 'base32',
    token: token,
    window: 1 // 允许前后1个时间窗口
  });
}
```

### 监控指标

**关键指标**：
- 泄露密码拦截率
- 密码修改完成率
- MFA 开启率
- 异常登录告警数量

**监控代码示例**：
```javascript
// 登录安全监控
async function logSecurityEvent(event) {
  await db.securityLogs.insert({
    type: event.type,
    userId: event.userId,
    ip: event.ip,
    userAgent: event.userAgent,
    timestamp: new Date(),
    metadata: event.metadata
  });
}

// 事件类型
const SECURITY_EVENTS = {
  LEAKED_PASSWORD_ATTEMPT: 'leaked_password_attempt',
  LEAKED_PASSWORD_LOGIN: 'leaked_password_login',
  NEW_DEVICE_LOGIN: 'new_device_login',
  IMPOSSIBLE_TRAVEL: 'impossible_travel',
  MFA_ENABLED: 'mfa_enabled',
  MFA_BYPASS_ATTEMPT: 'mfa_bypass_attempt'
};
```

---

## L3 企业版（深度版）

### 完整架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     密码安全防护架构                           │
├─────────────────────────────────────────────────────────────┤
│  用户层   │  注册/登录 → 密码强度检测 → 泄露检测 → MFA       │
├─────────────────────────────────────────────────────────────┤
│  应用层   │  异常检测 → 风险评分 → 自适应认证 → 告警         │
├─────────────────────────────────────────────────────────────┤
│  数据层   │  泄露数据库 → 用户行为基线 → 设备指纹库          │
├─────────────────────────────────────────────────────────────┤
│  监控层   │  实时监控 → 日志审计 → 安全事件响应              │
└─────────────────────────────────────────────────────────────┘
```

### 风险自适应认证

```javascript
// 风险评分系统
class RiskBasedAuth {
  calculateRiskScore(context) {
    let score = 0;
    
    // 设备风险 (0-30)
    if (!context.knownDevice) score += 20;
    if (context.deviceAge < 7) score += 10;
    
    // 位置风险 (0-30)
    if (!context.knownLocation) score += 15;
    if (context.distanceFromLast > 1000) score += 15;
    
    // 时间风险 (0-20)
    if (!this.isUsualTime(context.time, context.userPattern)) score += 10;
    if (context.timeSinceLastLogin < 300 && context.distanceFromLast > 100) {
      score += 10; // 不可能旅行
    }
    
    // 密码风险 (0-20)
    if (context.passwordLeaked) score += 20;
    if (context.passwordAge > 365) score += 10;
    
    return Math.min(score, 100);
  }
  
  getAuthRequirement(riskScore) {
    if (riskScore < 30) return 'password';
    if (riskScore < 60) return 'password + mfa';
    if (riskScore < 80) return 'password + mfa + email';
    return 'password + mfa + email + admin_approval';
  }
}
```

### 与其他案例的关联

| 关联案例 | 关系说明 | 防御协同 |
|---------|---------|---------|
| credential-stuffing | 密码复用是撞库成功的前提 | 泄露检测 + 异常检测 |
| weak-password | 弱密码更容易被破解和泄露 | 强度检测 + 泄露检测 |
| mfa-bypass | MFA是密码复用的备用防线 | 多层防御 |
| account-takeover | 密码复用导致账号接管 | 泄露检测 + MFA |

### 检测清单

- [ ] 注册时检测密码是否泄露
- [ ] 登录时检测密码是否泄露并提示修改
- [ ] 实现异常登录检测（新设备、异地、不可能旅行）
- [ ] 提供 MFA 选项
- [ ] 定期扫描用户密码泄露状态
- [ ] 实现风险自适应认证
- [ ] 建立安全事件监控和告警
- [ ] 制定密码安全策略文档

---

## 参考资料

### 真实案例
- [LinkedIn 2012 数据泄露](https://en.wikipedia.org/wiki/LinkedIn_data_breach)
- [Adobe 2013 数据泄露](https://en.wikipedia.org/wiki/Adobe_Systems#2013_security_breach)
- [Collection #1 数据泄露](https://www.troyhunt.com/the-773-million-record-collection-1-data-reach/)

### 技术文档
- [Have I Been Pwned API 文档](https://haveibeenpwned.com/API/v3)
- [NIST 密码指南](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)

### 工具
- [zxcvbn - 密码强度检测](https://github.com/dropbox/zxcvbn)
- [speakeasy - TOTP 实现](https://github.com/speakeasyjs/speakeasy)
- [Auth0 - 身份认证服务](https://auth0.com/)
