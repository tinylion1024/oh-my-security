# 账号接管（Account Takeover）

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: auth（认证安全）
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $20-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过撞库、密码重置漏洞、Session劫持等多种手段完全控制用户账号，可能导致用户数据泄露、资金损失、恶意操作等严重后果。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 有密码重置功能（邮箱验证码/链接）
- [ ] 有用户登录功能且未启用多因素认证
- [ ] Session有效期较长（如超过7天）
- [ ] 没有异常登录检测机制
- [ ] 允许同一账号多设备同时登录
→ 勾选≥2项，即需立即关注此风险

### 一句话防御
实施账号安全检查清单：启用多因素认证 + 异常登录检测 + Session有效期控制 + 密码重置流程加固。

### 快速行动清单
1. **立即行动**（今天可完成，免费）
   - [ ] 检查密码重置流程：重置链接是否一次性、是否有时效限制
   - [ ] 缩短Session有效期：建议7天内强制重新登录
   - [ ] 添加异常登录检测：IP地理位置变化、新设备识别
   - [ ] 记录所有关键操作日志：登录、密码修改、邮箱更改

2. **短期行动**（本周可完成，免费）
   - [ ] 实现多因素认证（邮箱验证码即可）
   - [ ] 添加账号活动页面：显示最近登录记录
   - [ ] 实现异地登录邮件提醒
   - [ ] 添加账号锁定机制：连续失败5次锁定15分钟

3. **长期行动**（规划中，低成本）
   - [ ] 集成威胁情报API检测泄露密码
   - [ ] 实现设备指纹识别
   - [ ] 建立自动化风控系统

### 推荐工具
- **免费**：
  - [Auth0](https://auth0.com/) - 免费额度7000活跃用户/月，内置异常检测
  - [Supabase Auth](https://supabase.com/auth) - 免费50000活跃用户/月
  - [Arcjet](https://arcjet.com/) - 免费100万请求/月，机器人检测

- **低成本**：
  - [Clerk](https://clerk.com/) - 免费5000活跃用户/月，完整认证方案
  - [Osano](https://www.osano.com/) - 免费版含合规检测

### 验证方法
- [ ] 测试步骤1：尝试重置密码，确认链接是否一次性
- [ ] 测试步骤2：从不同IP登录，检查是否收到告警邮件
- [ ] 测试步骤3：查看账号活动页面，确认登录记录准确
- [ ] 测试步骤4：连续失败登录5次，确认账号被锁定

---

## L2 小团队版（理解版）

### 场景还原
你的SaaS产品有5000个用户，某天收到多个用户投诉"账号被盗"：

**案例1：撞库攻击**
- 用户A在不同网站使用相同密码
- 黑客获取泄露数据库后尝试登录你的产品
- 成功登录后修改绑定的手机号和邮箱
- 盗取账户余额2000元

**案例2：密码重置漏洞**
- 用户B的邮箱被黑客入侵
- 黑客利用"忘记密码"功能发送重置链接到邮箱
- 重置密码后完全接管账号
- 删除用户数据并勒索

**案例3：Session劫持**
- 用户C在公共WiFi下登录
- 黑客通过中间人攻击窃取Session Token
- 使用Token访问用户账户
- 窃取敏感商业数据

你的服务器日志显示：
```
[2026-06-10 02:15:33] POST /api/auth/reset-password - user@example.com - SUCCESS
[2026-06-10 02:16:12] POST /api/auth/change-email - user@example.com - SUCCESS (new: hacker@evil.com)
[2026-06-10 02:17:05] POST /api/payment/withdraw - user@example.com - $2000
```

### 攻击路径（简化版）

**路径1：撞库攻击**
1. 黑客从暗网获取泄露的账号密码数据库（如Collection #1-5）
2. 使用自动化工具批量尝试登录你的产品
3. 成功登录后立即修改账号绑定信息（邮箱、手机号）
4. 窃取账户余额或敏感数据
5. 利用信任关系进行钓鱼（向账号好友发送诈骗信息）

**路径2：密码重置接管**
1. 黑客先入侵用户邮箱（通过钓鱼或暴力破解）
2. 使用"忘记密码"功能发送重置链接
3. 从邮箱中获取重置链接并修改密码
4. 登录后修改备用邮箱和手机号
5. 用户失去账号控制权

**路径3：Session劫持**
1. 用户在不安全网络环境（公共WiFi）登录
2. 黑客通过中间人攻击窃取Session Token
3. 使用Token直接访问用户账户，无需密码
4. 进行恶意操作（转账、修改信息、删除数据）
5. 用户无感知，直到发现异常

### 防御实施（低成本方案）

#### 方案A：免费方案（纯自建）

**1. 账号安全检查清单**

```python
# 账号安全评分系统
class AccountSecurityChecker:
    """账号安全检查清单"""

    @staticmethod
    def check_password_strength(password):
        """检查密码强度"""
        checks = {
            'length': len(password) >= 12,
            'uppercase': any(c.isupper() for c in password),
            'lowercase': any(c.islower() for c in password),
            'digit': any(c.isdigit() for c in password),
            'special': any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        }

        score = sum(checks.values())
        return {
            'score': score,
            'checks': checks,
            'is_strong': score >= 4
        }

    @staticmethod
    def check_account_security(user):
        """账号安全检查"""
        risks = []

        # 检查密码强度
        password_check = AccountSecurityChecker.check_password_strength(user.password)
        if not password_check['is_strong']:
            risks.append('密码强度不足')

        # 检查是否启用2FA
        if not user.two_factor_enabled:
            risks.append('未启用双因素认证')

        # 检查最近登录异常
        recent_logins = get_recent_logins(user.id, days=30)
        if has_geo_anomaly(recent_logins):
            risks.append('检测到异地登录')

        # 检查密码是否泄露
        if check_password_breach(user.password) > 0:
            risks.append('密码已在数据泄露中出现')

        return {
            'secure': len(risks) == 0,
            'risks': risks,
            'score': 100 - len(risks) * 20
        }
```

**2. 异常登录检测**

```python
# 异常登录检测系统
import geoip2.database
from datetime import datetime, timedelta
from collections import defaultdict

class AnomalyLoginDetector:
    """异常登录检测器"""

    def __init__(self):
        self.reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        self.login_history = defaultdict(list)  # {user_id: [login_records]}

    def detect_anomaly(self, user_id, current_ip, user_agent):
        """检测异常登录"""
        # 获取当前位置
        try:
            location = self.reader.city(current_ip)
            current_geo = {
                'country': location.country.iso_code,
                'city': location.city.name,
                'lat': location.location.latitude,
                'lon': location.location.longitude,
                'ip': current_ip
            }
        except:
            current_geo = {'country': 'Unknown', 'ip': current_ip}

        # 获取历史登录记录
        history = self.login_history[user_id][-10:]  # 最近10次

        anomalies = []

        # 1. 新设备检测
        known_devices = {h['device_fingerprint'] for h in history}
        current_device = self._generate_device_fingerprint(user_agent)
        if current_device not in known_devices:
            anomalies.append({
                'type': 'new_device',
                'message': '检测到新设备登录',
                'severity': 'medium'
            })

        # 2. 异地登录检测
        if history:
            last_login = history[-1]
            distance = self._calculate_distance(
                current_geo.get('lat', 0),
                current_geo.get('lon', 0),
                last_login['geo'].get('lat', 0),
                last_login['geo'].get('lon', 0)
            )

            time_diff = datetime.now() - last_login['timestamp']

            # 24小时内距离超过500km
            if distance > 500 and time_diff < timedelta(hours=24):
                anomalies.append({
                    'type': 'geo_anomaly',
                    'message': f"检测到异地登录，距离上次登录{distance:.0f}km",
                    'severity': 'high',
                    'last_location': last_login['geo']['city'],
                    'current_location': current_geo.get('city', 'Unknown')
                })

        # 3. 高频登录检测
        recent_failures = self._get_recent_failures(user_id, minutes=15)
        if recent_failures >= 5:
            anomalies.append({
                'type': 'brute_force',
                'message': f'15分钟内登录失败{recent_failures}次',
                'severity': 'critical'
            })

        # 记录本次登录
        self.login_history[user_id].append({
            'timestamp': datetime.now(),
            'geo': current_geo,
            'device_fingerprint': current_device,
            'ip': current_ip
        })

        return {
            'anomalies': anomalies,
            'risk_level': self._calculate_risk_level(anomalies),
            'geo': current_geo
        }

    def _generate_device_fingerprint(self, user_agent):
        """生成设备指纹"""
        import hashlib
        return hashlib.md5(user_agent.encode()).hexdigest()

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """计算两点间距离（km）"""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # 地球半径

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def _calculate_risk_level(self, anomalies):
        """计算风险等级"""
        if not anomalies:
            return 'low'

        severities = [a['severity'] for a in anomalies]
        if 'critical' in severities:
            return 'critical'
        elif 'high' in severities:
            return 'high'
        else:
            return 'medium'

    def _get_recent_failures(self, user_id, minutes=15):
        """获取最近失败次数"""
        # 实现从Redis或数据库获取
        pass
```

**3. 密码重置流程加固**

```python
# 安全的密码重置流程
import secrets
from datetime import datetime, timedelta

class SecurePasswordReset:
    """安全的密码重置"""

    def __init__(self):
        self.reset_tokens = {}  # 生产环境应使用Redis

    def initiate_reset(self, email):
        """发起密码重置"""
        # 生成安全随机Token
        token = secrets.token_urlsafe(32)

        # 设置有效期（15分钟）
        expires_at = datetime.now() + timedelta(minutes=15)

        # 存储Token（一次性使用）
        self.reset_tokens[token] = {
            'email': email,
            'expires_at': expires_at,
            'used': False,
            'created_at': datetime.now()
        }

        # 发送重置链接
        reset_link = f"https://yoursite.com/reset-password?token={token}"
        self._send_reset_email(email, reset_link)

        return {
            'success': True,
            'message': '重置邮件已发送',
            'expires_in': 900  # 秒
        }

    def verify_and_reset(self, token, new_password):
        """验证并重置密码"""
        # 检查Token是否存在
        if token not in self.reset_tokens:
            return {'success': False, 'error': '无效的重置链接'}

        token_data = self.reset_tokens[token]

        # 检查是否已使用
        if token_data['used']:
            return {'success': False, 'error': '重置链接已使用'}

        # 检查是否过期
        if datetime.now() > token_data['expires_at']:
            return {'success': False, 'error': '重置链接已过期'}

        # 标记Token为已使用
        token_data['used'] = True

        # 更新密码
        email = token_data['email']
        update_user_password(email, new_password)

        # 发送通知邮件
        send_password_changed_notification(email)

        return {'success': True, 'message': '密码重置成功'}

    def _send_reset_email(self, email, reset_link):
        """发送重置邮件"""
        # 使用你的邮件服务
        pass
```

**局限性**：
- 需要自己维护检测逻辑和数据库
- 异常检测规则需要不断优化
- 缺少专业的威胁情报

---

#### 方案B：低成本方案（$20-50/月）

**使用 Auth0 完整防护方案**

```javascript
// Auth0 配置 - 内置账号接管防护
// auth0-config.js

export const auth0Config = {
  domain: process.env.AUTH0_DOMAIN,
  clientId: process.env.AUTH0_CLIENT_ID,
  clientSecret: process.env.AUTH0_CLIENT_SECRET,

  // 异常检测配置
  anomalyDetection: {
    enableIpAnomalyDetection: true,
    // 检测到异常时的行为
    actions: {
      suspiciousLogin: 'block', // 或 'mfa', 'notification'
      bruteForceProtection: 'block'
    }
  },

  // 暴力破解防护
  bruteForceProtection: {
    enabled: true,
    maxAttempts: 5,
    lockoutDuration: 15 // 分钟
  },

  // 密码策略
  passwordPolicy: {
    minLength: 12,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSymbols: true,
    // 检查密码泄露
    enablePasswordHibpCheck: true
  },

  // 多因素认证
  mfa: {
    enabled: true,
    // 高风险场景强制MFA
    challengeWhen: {
      suspiciousLogin: true,
      newDevice: true,
      geoAnomaly: true
    }
  }
}

// 登录流程 - 自动包含风险检测
import { Auth0Client } from '@auth0/auth0-react'

const auth0Client = new Auth0Client(auth0Config)

// 登录时自动进行异常检测
async function login(email, password) {
  try {
    const result = await auth0Client.loginWithCredentials({
      username: email,
      password: password
    })

    // Auth0 自动处理：
    // - 异常登录检测
    // - 暴力破解防护
    // - 密码泄露检查
    // - 高风险时要求MFA

    return result
  } catch (error) {
    // 处理安全错误
    if (error.code === 'too_many_attempts') {
      return { error: '登录尝试过多，账号已锁定' }
    }
    if (error.code === 'suspicious_login') {
      return { error: '检测到异常登录，请验证身份' }
    }
    throw error
  }
}
```

**使用 Supabase Auth（免费50000活跃用户/月）**

```javascript
// Supabase Auth 完整防护方案
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_ANON_KEY
)

// 登录流程 - 自动防护
async function secureLogin(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })

  // Supabase 自动提供：
  // - 暴力破解防护
  // - 异常登录检测
  // - 密码泄露检查
  // - Session管理

  if (error) {
    // 处理错误
    if (error.message.includes('Invalid login credentials')) {
      // 记录失败尝试
      await logFailedAttempt(email)
    }
    throw error
  }

  // 检查是否需要MFA
  if (data.user.factors && data.user.factors.length > 0) {
    // 要求用户完成MFA
    await supabase.auth.mfa.challenge({
      factorId: data.user.factors[0].id
    })
  }

  return data
}

// 监听登录事件
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    // 检查登录风险
    checkLoginRisk(session.user)
  }
})

// 异常登录检测
async function checkLoginRisk(user) {
  // 获取用户登录历史
  const { data: logins } = await supabase
    .from('login_history')
    .select('*')
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .limit(10)

  // 检测异常
  const anomalies = detectAnomalies(logins)

  if (anomalies.length > 0) {
    // 发送告警邮件
    await sendSecurityAlert(user.email, anomalies)
  }
}
```

**优势**：
- 无需自建检测系统
- 自动更新威胁情报
- 专业的安全团队维护
- 免费额度足够中小型SaaS使用

---

### 决策树

```
你的产品是否处理用户资金或敏感数据？
├── 是 → 必须启用多因素认证 + 异常登录检测
└── 否 →
    是否有密码重置功能？
    ├── 是 → 加固密码重置流程（一次性Token + 时效限制）
    └── 否 → 基础防护足够

你的技术栈是什么？
├── React/Vue/Next.js → 使用 Auth0 或 Supabase Auth
└── 自建后端 → 使用自建方案A

你的预算如何？
├── $0 → 使用 Supabase Auth（免费50000用户/月）
├── $20-50/月 → 使用 Auth0（增强安全功能）
└── 自建 → 使用方案A + Redis
```

---

### 完整代码示例

**Next.js + Supabase 完整防护方案**

```typescript
// lib/auth-security.ts
import { createClient } from '@supabase/supabase-js'
import { NextApiRequest } from 'next'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
)

export class AccountSecurityService {
  /**
   * 账号安全检查
   */
  static async checkAccountSecurity(userId: string) {
    // 获取用户信息
    const { data: user } = await supabase.auth.admin.getUserById(userId)

    if (!user) {
      return { secure: false, risks: ['用户不存在'] }
    }

    const risks: string[] = []

    // 1. 检查是否启用2FA
    const { data: factors } = await supabase.auth.mfa.listFactors(userId)
    if (!factors || factors.length === 0) {
      risks.push('未启用双因素认证')
    }

    // 2. 检查最近登录异常
    const { data: recentLogins } = await supabase
      .from('login_history')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(10)

    if (recentLogins && this.hasGeoAnomaly(recentLogins)) {
      risks.push('检测到异地登录')
    }

    // 3. 检查密码泄露
    const isBreached = await this.checkPasswordBreached(user.email!)
    if (isBreached) {
      risks.push('密码可能在数据泄露中出现')
    }

    // 4. 检查Session有效性
    const { data: sessions } = await supabase.auth.admin.listUserSessions(userId)
    const activeSessions = sessions?.filter(s => !s.expired_at) || []

    if (activeSessions.length > 5) {
      risks.push('活跃Session过多，建议检查')
    }

    return {
      secure: risks.length === 0,
      risks,
      score: 100 - risks.length * 20,
      sessions: activeSessions.length
    }
  }

  /**
   * 异常登录检测
   */
  static async detectAnomalyLogin(
    userId: string,
    ip: string,
    userAgent: string
  ) {
    const anomalies: Array<{
      type: string
      message: string
      severity: 'low' | 'medium' | 'high' | 'critical'
    }> = []

    // 获取地理位置
    const geo = await this.getGeoLocation(ip)

    // 获取历史登录记录
    const { data: history } = await supabase
      .from('login_history')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(10)

    if (history && history.length > 0) {
      const lastLogin = history[0]

      // 检测新设备
      if (lastLogin.user_agent !== userAgent) {
        anomalies.push({
          type: 'new_device',
          message: '检测到新设备登录',
          severity: 'medium'
        })
      }

      // 检测异地登录
      const distance = this.calculateDistance(
        geo.lat, geo.lon,
        lastLogin.lat, lastLogin.lon
      )

      const hoursSinceLastLogin =
        (Date.now() - new Date(lastLogin.created_at).getTime()) / (1000 * 60 * 60)

      if (distance > 500 && hoursSinceLastLogin < 24) {
        anomalies.push({
          type: 'geo_anomaly',
          message: `检测到异地登录，距离${distance.toFixed(0)}km`,
          severity: 'high'
        })
      }
    }

    // 记录本次登录
    await supabase.from('login_history').insert({
      user_id: userId,
      ip_address: ip,
      user_agent: userAgent,
      geo_country: geo.country,
      geo_city: geo.city,
      lat: geo.lat,
      lon: geo.lon,
      created_at: new Date().toISOString()
    })

    // 如果检测到异常，发送告警
    if (anomalies.length > 0) {
      await this.sendSecurityAlert(userId, anomalies)
    }

    return {
      anomalies,
      riskLevel: this.calculateRiskLevel(anomalies),
      geo
    }
  }

  /**
   * Session管理
   */
  static async manageSessions(userId: string) {
    // 获取所有Session
    const { data: sessions } = await supabase.auth.admin.listUserSessions(userId)

    // 按设备分组
    const deviceMap = new Map<string, typeof sessions>()
    sessions?.forEach(session => {
      const device = this.getDeviceInfo(session.user_agent)
      if (!deviceMap.has(device)) {
        deviceMap.set(device, [])
      }
      deviceMap.get(device)!.push(session)
    })

    // 检查异常Session
    const activeSessions = sessions?.filter(s => !s.expired_at) || []
    const anomalies = []

    // 同一设备多个Session
    deviceMap.forEach((sessions, device) => {
      if (sessions.length > 2) {
        anomalies.push({
          type: 'multiple_sessions',
          device,
          count: sessions.length
        })
      }
    })

    // Session过多
    if (activeSessions.length > 5) {
      anomalies.push({
        type: 'too_many_sessions',
        count: activeSessions.length
      })
    }

    return {
      total: sessions?.length || 0,
      active: activeSessions.length,
      devices: Array.from(deviceMap.keys()),
      anomalies
    }
  }

  /**
   * 强制登出其他设备
   */
  static async logoutOtherDevices(userId: string, currentSessionId: string) {
    const { data: sessions } = await supabase.auth.admin.listUserSessions(userId)

    const otherSessions = sessions
      ?.filter(s => s.id !== currentSessionId)
      .map(s => s.id) || []

    // 撤销其他Session
    for (const sessionId of otherSessions) {
      await supabase.auth.admin.signOut(userId, sessionId)
    }

    return {
      revoked: otherSessions.length,
      message: `已登出${otherSessions.length}个其他设备`
    }
  }

  // 辅助方法
  private static hasGeoAnomaly(logins: any[]): boolean {
    if (logins.length < 2) return false

    const last = logins[0]
    const previous = logins[1]

    const distance = this.calculateDistance(
      last.lat, last.lon,
      previous.lat, previous.lon
    )

    const hoursDiff =
      (new Date(last.created_at).getTime() - new Date(previous.created_at).getTime())
      / (1000 * 60 * 60)

    return distance > 500 && hoursDiff < 24
  }

  private static calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371
    const dLat = (lat2 - lat1) * Math.PI / 180
    const dLon = (lon2 - lon1) * Math.PI / 180
    const a =
      Math.sin(dLat/2) * Math.sin(dLat/2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon/2) * Math.sin(dLon/2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
    return R * c
  }

  private static async getGeoLocation(ip: string) {
    // 使用GeoIP服务
    // 这里可以集成MaxMind GeoIP2
    return {
      country: 'CN',
      city: 'Beijing',
      lat: 39.9042,
      lon: 116.4074
    }
  }

  private static calculateRiskLevel(anomalies: any[]): string {
    if (anomalies.some(a => a.severity === 'critical')) return 'critical'
    if (anomalies.some(a => a.severity === 'high')) return 'high'
    if (anomalies.some(a => a.severity === 'medium')) return 'medium'
    return 'low'
  }

  private static async checkPasswordBreached(email: string): Promise<boolean> {
    // 检查密码是否泄露
    // 可以集成Have I Been Pwned API
    return false
  }

  private static async sendSecurityAlert(userId: string, anomalies: any[]) {
    // 发送安全告警邮件
    const { data: user } = await supabase.auth.admin.getUserById(userId)
    if (!user) return

    // 发送邮件逻辑
    console.log(`发送安全告警到 ${user.email}:`, anomalies)
  }

  private static getDeviceInfo(userAgent: string): string {
    if (userAgent.includes('Mobile')) return 'Mobile'
    if (userAgent.includes('Tablet')) return 'Tablet'
    return 'Desktop'
  }
}
```

**API路由示例**

```typescript
// app/api/auth/check-security/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { AccountSecurityService } from '@/lib/auth-security'
import { getCurrentUser } from '@/lib/auth'

export async function GET(request: NextRequest) {
  try {
    const user = await getCurrentUser(request)
    if (!user) {
      return NextResponse.json({ error: '未授权' }, { status: 401 })
    }

    const security = await AccountSecurityService.checkAccountSecurity(user.id)

    return NextResponse.json(security)
  } catch (error) {
    console.error('Security check error:', error)
    return NextResponse.json(
      { error: '检查失败' },
      { status: 500 }
    )
  }
}

// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server'
import { AccountSecurityService } from '@/lib/auth-security'

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // 执行登录逻辑...

    // 登录成功后检测异常
    const ip = request.headers.get('x-forwarded-for') || 'unknown'
    const userAgent = request.headers.get('user-agent') || 'unknown'

    const anomalyResult = await AccountSecurityService.detectAnomalyLogin(
      user.id,
      ip,
      userAgent
    )

    // 如果风险高，要求MFA
    if (anomalyResult.riskLevel === 'high' || anomalyResult.riskLevel === 'critical') {
      return NextResponse.json({
        requiresMFA: true,
        anomalies: anomalyResult.anomalies,
        message: '检测到异常登录，请验证身份'
      })
    }

    return NextResponse.json({
      success: true,
      user,
      warnings: anomalyResult.anomalies
    })
  } catch (error) {
    console.error('Login error:', error)
    return NextResponse.json(
      { error: '登录失败' },
      { status: 500 }
    )
  }
}
```

---

## L3 企业版（深耕版）

企业级账号接管防护需要完整的身份安全管理平台，包括：

**1. 高级威胁检测**
- 行为生物特征分析
- 设备指纹识别
- 机器学习风险模型
- 实时威胁情报集成

**2. 零信任架构**
- 持续身份验证
- 最小权限原则
- 微隔离网络

**3. 完整审计系统**
- SIEM集成
- 取证分析能力
- 合规报告

**详细内容请参考企业级案例**：
- [企业级账号安全方案](../../enterprise/bizsec/auth/account-security-enterprise.md)
- [零信任架构实践](../../enterprise/infosec/zero-trust.md)

---

## 成本估算总结

| 防护层级 | 月成本 | 实施时间 | 维护成本 | 适用场景 |
|---------|--------|---------|---------|---------|
| L1-基础检查 | $0 | 2小时 | 1小时/月 | MVP阶段 |
| L2-方案A（自建） | $0 | 8小时 | 4小时/月 | 技术团队，需完全控制 |
| L2-方案B（SaaS） | $0-20 | 2小时 | 1小时/月 | 快速上线，无运维压力 |
| L3-企业级 | $200+ | 需评估 | 专职团队 | 金融、医疗、政务 |

---

## 常见问题

**Q: 多因素认证会不会影响用户体验？**
A: 使用风险自适应认证，只在检测到异常时要求MFA，正常登录无需额外验证。

**Q: 异常登录检测会不会误报？**
A: 合理设置阈值（如距离500km），提供白名单机制，允许用户标记常用设备。

**Q: 如何防止密码重置流程被滥用？**
A: 使用一次性Token + 15分钟有效期 + 邮件通知，并记录所有重置尝试。

**Q: 用户账号已被接管怎么办？**
A: 参考[应急响应剧本](../../modules/incident-playbook/account-takeover-response.md)：
1. 立即冻结账号
2. 联系用户验证身份
3. 回滚恶意操作
4. 加固账号安全

---

## 相关资源

**工具**
- [Auth0](https://auth0.com/) - 免费额度7000活跃用户/月
- [Supabase Auth](https://supabase.com/auth) - 免费50000活跃用户/月
- [Clerk](https://clerk.com/) - 免费5000活跃用户/月
- [Arcjet](https://arcjet.com/) - 免费100万请求/月

**学习资源**
- [OWASP Account Lockout](https://owasp.org/www-community/controls/Account_lockout_policy)
- [NIST Digital Identity Guidelines](https://pages.nist.gov/800-63-3/)
- [Have I Been Pwned](https://haveibeenpwned.com/)

**相关案例**
- [撞库攻击](./credential-stuffing.md)
- [Session劫持](./session-hijacking.md)
- [密码重置漏洞](./password-reset-vulnerability.md)
