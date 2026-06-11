# 登录异常检测 (Login Anomaly Detection)

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 检测 + 响应
- **实现成本**: 免费（自建）/ $0-30/月（IP地理位置服务）
- **实施时间**: 4-6小时
- **维护成本**: 2-3小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
检测异常登录行为，识别账号被盗、凭证填充、暴力破解等攻击，在账号被入侵前发出告警并采取防护措施。

## 检测维度

### 异常类型分类

| 检测维度 | 异常信号 | 风险等级 | 检测难度 |
|---------|---------|---------|---------|
| **IP 地址** | 新IP/代理/VPN/高风险地区 | ⭐⭐⭐⭐ 高 | ⭐⭐ 中 |
| **设备指纹** | 新设备/模拟器/多设备 | ⭐⭐⭐⭐ 高 | ⭐⭐⭐ 中高 |
| **地理位置** | 位置突变/不可能旅行 | ⭐⭐⭐⭐⭐ 最高 | ⭐⭐ 中 |
| **行为模式** | 时间/频率/操作异常 | ⭐⭐⭐ 中 | ⭐⭐⭐⭐ 高 |
| **账号特征** | 新注册/休眠/高权限 | ⭐⭐⭐ 中 | ⭐ 简单 |
| **登录凭证** | 泄露密码/弱密码 | ⭐⭐⭐⭐ 高 | ⭐⭐ 中 |

### 详细说明

#### 1. IP 地址检测

**检测内容**：
- IP 是否在黑名单中（已知恶意IP）
- 是否为代理/VPN/数据中心IP
- IP 信誉评分
- IP 所属 ASN 是否可疑

**实现方式**：
```python
# IP 风险检测
ip_risk = {
    "is_proxy": True,           # 是否代理
    "is_vpn": False,            # 是否VPN
    "is_tor": False,            # 是否Tor出口
    "is_datacenter": True,      # 是否数据中心IP
    "threat_level": "medium",   # 威胁等级
    "abuse_score": 65,          # 滥用评分 0-100
}
```

---

#### 2. 设备指纹检测

**检测内容**：
- 设备是否为用户常用设备
- 设备类型变化（PC→手机）
- 操作系统变化
- 浏览器指纹变化

**采集特征**：
```javascript
// 设备指纹采集
const deviceFingerprint = {
  // 基础信息
  userAgent: navigator.userAgent,
  platform: navigator.platform,
  language: navigator.language,

  // 屏幕信息
  screenResolution: `${screen.width}x${screen.height}`,
  colorDepth: screen.colorDepth,

  // 浏览器特征
  cookiesEnabled: navigator.cookieEnabled,
  doNotTrack: navigator.doNotTrack,

  // Canvas 指纹
  canvasFingerprint: getCanvasFingerprint(),

  // WebGL 指纹
  webglRenderer: getWebGLRenderer(),
  webglVendor: getWebGLVendor(),

  // 时区
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  timezoneOffset: new Date().getTimezoneOffset(),

  // 插件
  plugins: getPluginList(),
};
```

---

#### 3. 地理位置异常

**检测内容**：
- 登录位置距离上次位置的物理距离
- 两次登录的时间间隔是否允许这种移动
- 是否来自高风险国家/地区

**不可能旅行检测**：
```
上次登录：北京，2024-06-11 10:00
本次登录：纽约，2024-06-11 12:00

距离：~11,000 km
时间间隔：2小时
理论飞行时间：~14小时

结论：不可能旅行 → 高风险
```

---

## 快速上手（5分钟）

### 登录异常检测核心（Python）

```python
# login_anomaly_detection.py
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class LoginContext:
    """登录上下文信息"""
    user_id: str
    ip_address: str
    user_agent: str
    device_fingerprint: str
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    country: Optional[str] = None

@dataclass
class AnomalyScore:
    """异常评分"""
    total_score: float          # 总分 0-100
    risk_level: str             # low/medium/high/critical
    factors: List[dict]         # 风险因素列表
    recommendation: str         # 建议操作

class LoginAnomalyDetector:
    """登录异常检测器"""

    # 风险阈值
    LOW_RISK_THRESHOLD = 20
    MEDIUM_RISK_THRESHOLD = 50
    HIGH_RISK_THRESHOLD = 75

    # 地理阈值
    IMPOSSIBLE_TRAVEL_SPEED = 900  # km/h（飞机速度）

    def __init__(self, db, ip_service=None):
        self.db = db
        self.ip_service = ip_service  # IP地理位置服务

    async def analyze_login(
        self,
        context: LoginContext
    ) -> AnomalyScore:
        """分析登录异常"""
        factors = []
        total_score = 0

        # 1. 获取用户登录历史
        history = await self._get_login_history(context.user_id, limit=10)
        last_login = history[0] if history else None

        # 2. IP 风险检测
        ip_score, ip_factors = await self._check_ip_risk(context)
        factors.extend(ip_factors)
        total_score += ip_score

        # 3. 设备检测
        device_score, device_factors = await self._check_device(context, history)
        factors.extend(device_factors)
        total_score += device_score

        # 4. 地理位置检测
        if last_login and context.latitude:
            geo_score, geo_factors = await self._check_geography(
                context, last_login
            )
            factors.extend(geo_factors)
            total_score += geo_score

        # 5. 行为模式检测
        behavior_score, behavior_factors = await self._check_behavior(
            context, history
        )
        factors.extend(behavior_factors)
        total_score += behavior_score

        # 6. 时间模式检测
        time_score, time_factors = await self._check_time_pattern(
            context, history
        )
        factors.extend(time_factors)
        total_score += time_score

        # 计算风险等级
        risk_level = self._calculate_risk_level(total_score)
        recommendation = self._get_recommendation(risk_level, factors)

        return AnomalyScore(
            total_score=min(total_score, 100),
            risk_level=risk_level,
            factors=factors,
            recommendation=recommendation
        )

    async def _check_ip_risk(
        self,
        context: LoginContext
    ) -> tuple:
        """检查 IP 风险"""
        score = 0
        factors = []

        if not self.ip_service:
            return score, factors

        # 获取 IP 信息
        ip_info = await self.ip_service.lookup(context.ip_address)

        # 检查是否为代理/VPN
        if ip_info.get('is_proxy'):
            score += 15
            factors.append({
                "type": "ip_proxy",
                "score": 15,
                "detail": "IP 地址为已知代理"
            })

        if ip_info.get('is_vpn'):
            score += 10
            factors.append({
                "type": "ip_vpn",
                "score": 10,
                "detail": "IP 地址为 VPN 出口"
            })

        if ip_info.get('is_tor'):
            score += 25
            factors.append({
                "type": "ip_tor",
                "score": 25,
                "detail": "IP 地址为 Tor 出口节点"
            })

        # 检查是否为数据中心 IP
        if ip_info.get('is_datacenter'):
            score += 10
            factors.append({
                "type": "ip_datacenter",
                "score": 10,
                "detail": "IP 地址来自数据中心"
            })

        # 检查滥用评分
        abuse_score = ip_info.get('abuse_score', 0)
        if abuse_score > 50:
            score += min(abuse_score // 5, 20)
            factors.append({
                "type": "ip_abuse",
                "score": min(abuse_score // 5, 20),
                "detail": f"IP 滥用评分: {abuse_score}"
            })

        # 检查高风险国家
        high_risk_countries = ['CN', 'RU', 'KP', 'IR']  # 示例，实际根据业务调整
        if ip_info.get('country_code') in high_risk_countries:
            score += 10
            factors.append({
                "type": "ip_high_risk_country",
                "score": 10,
                "detail": f"来自高风险国家: {ip_info.get('country')}"
            })

        return score, factors

    async def _check_device(
        self,
        context: LoginContext,
        history: List[dict]
    ) -> tuple:
        """检查设备风险"""
        score = 0
        factors = []

        if not history:
            # 新用户，不扣分
            return score, factors

        # 检查是否为新设备
        known_devices = {
            self._hash_device(h.get('device_fingerprint', ''))
            for h in history
        }
        current_device_hash = self._hash_device(context.device_fingerprint)

        if current_device_hash not in known_devices:
            score += 20
            factors.append({
                "type": "new_device",
                "score": 20,
                "detail": "检测到新设备登录"
            })

        # 检查 User-Agent 变化
        last_ua = history[0].get('user_agent', '')
        if last_ua and context.user_agent != last_ua:
            # UA 变化可能是设备或浏览器变更
            score += 5
            factors.append({
                "type": "ua_change",
                "score": 5,
                "detail": "浏览器信息发生变化"
            })

        # 检查是否为模拟器/自动化工具
        suspicious_keywords = [
            'headless', 'selenium', 'phantomjs',
            'webdriver', 'bot', 'crawler', 'spider'
        ]
        ua_lower = context.user_agent.lower()
        for keyword in suspicious_keywords:
            if keyword in ua_lower:
                score += 30
                factors.append({
                    "type": "automation",
                    "score": 30,
                    "detail": f"检测到自动化工具特征: {keyword}"
                })
                break

        return score, factors

    async def _check_geography(
        self,
        context: LoginContext,
        last_login: dict
    ) -> tuple:
        """检查地理位置异常"""
        score = 0
        factors = []

        if not context.latitude or not last_login.get('latitude'):
            return score, factors

        # 计算距离
        distance = self._haversine_distance(
            context.latitude, context.longitude,
            last_login['latitude'], last_login['longitude']
        )

        # 计算时间间隔（小时）
        time_diff = (context.timestamp - last_login['timestamp']).total_seconds() / 3600

        if time_diff <= 0:
            return score, factors

        # 计算移动速度
        speed = distance / time_diff if time_diff > 0 else 0

        # 不可能旅行检测
        if speed > self.IMPOSSIBLE_TRAVEL_SPEED:
            score += 40
            factors.append({
                "type": "impossible_travel",
                "score": 40,
                "detail": f"不可能旅行检测: {distance:.0f}km/{time_diff:.1f}h = {speed:.0f}km/h"
            })
        elif distance > 500:  # 大于500km的跳跃
            score += 15
            factors.append({
                "type": "location_jump",
                "score": 15,
                "detail": f"位置大幅变化: {distance:.0f}km"
            })

        # 检查是否跨国登录
        if context.country and last_login.get('country'):
            if context.country != last_login['country']:
                score += 10
                factors.append({
                    "type": "country_change",
                    "score": 10,
                    "detail": f"国家变化: {last_login['country']} → {context.country}"
                })

        return score, factors

    async def _check_behavior(
        self,
        context: LoginContext,
        history: List[dict]
    ) -> tuple:
        """检查行为模式"""
        score = 0
        factors = []

        if len(history) < 3:
            return score, factors

        # 检查失败登录次数
        recent_failures = await self._get_recent_failed_logins(
            context.user_id,
            hours=1
        )
        if recent_failures >= 5:
            score += 25
            factors.append({
                "type": "brute_force",
                "score": 25,
                "detail": f"1小时内失败登录{recent_failures}次"
            })
        elif recent_failures >= 3:
            score += 10
            factors.append({
                "type": "multiple_failures",
                "score": 10,
                "detail": f"1小时内失败登录{recent_failures}次"
            })

        # 检查多设备同时登录
        active_sessions = await self._get_active_sessions(context.user_id)
        if len(active_sessions) > 5:
            score += 15
            factors.append({
                "type": "multiple_sessions",
                "score": 15,
                "detail": f"同时活跃会话数: {len(active_sessions)}"
            })

        return score, factors

    async def _check_time_pattern(
        self,
        context: LoginContext,
        history: List[dict]
    ) -> tuple:
        """检查时间模式"""
        score = 0
        factors = []

        if len(history) < 5:
            return score, factors

        # 分析用户常用登录时间段
        login_hours = [h['timestamp'].hour for h in history]
        avg_hour = sum(login_hours) / len(login_hours)

        # 标准差
        variance = sum((h - avg_hour) ** 2 for h in login_hours) / len(login_hours)
        std_dev = math.sqrt(variance)

        current_hour = context.timestamp.hour

        # 如果当前时间超出正常范围（3个标准差）
        if std_dev > 0 and abs(current_hour - avg_hour) > 3 * std_dev:
            score += 10
            factors.append({
                "type": "unusual_time",
                "score": 10,
                "detail": f"非常规时间登录: {current_hour}:00（通常在 {avg_hour:.0f}:00 附近）"
            })

        return score, factors

    def _calculate_risk_level(self, score: float) -> str:
        """计算风险等级"""
        if score >= self.HIGH_RISK_THRESHOLD:
            return "critical"
        elif score >= self.MEDIUM_RISK_THRESHOLD:
            return "high"
        elif score >= self.LOW_RISK_THRESHOLD:
            return "medium"
        return "low"

    def _get_recommendation(
        self,
        risk_level: str,
        factors: List[dict]
    ) -> str:
        """获取建议操作"""
        recommendations = {
            "low": "允许登录，记录日志",
            "medium": "允许登录，发送通知，监控后续行为",
            "high": "要求 MFA 验证，发送告警",
            "critical": "阻止登录，强制验证身份，人工审核"
        }
        return recommendations.get(risk_level, "未知风险等级")

    # ============== 辅助方法 ==============

    def _hash_device(self, fingerprint: str) -> str:
        """哈希设备指纹"""
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:16]

    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """计算两点间的球面距离（公里）"""
        R = 6371  # 地球半径（公里）

        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    async def _get_login_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[dict]:
        """获取登录历史"""
        # 实际项目中从数据库查询
        return []

    async def _get_recent_failed_logins(
        self,
        user_id: str,
        hours: int = 1
    ) -> int:
        """获取最近失败登录次数"""
        return 0

    async def _get_active_sessions(self, user_id: str) -> List[dict]:
        """获取活跃会话"""
        return []


# 使用示例
async def main():
    # 初始化检测器
    detector = LoginAnomalyDetector(db=None, ip_service=None)

    # 构造登录上下文
    context = LoginContext(
        user_id="user_123",
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        device_fingerprint="abc123",
        timestamp=datetime.utcnow(),
        latitude=39.9042,
        longitude=116.4074,
        city="Beijing",
        country="CN"
    )

    # 分析
    result = await detector.analyze_login(context)

    print(f"风险评分: {result.total_score}")
    print(f"风险等级: {result.risk_level}")
    print(f"建议操作: {result.recommendation}")
    print("\n风险因素:")
    for factor in result.factors:
        print(f"  - [{factor['type']}] {factor['detail']} (+{factor['score']})")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 详细方案

### 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     登录异常检测架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  用户登录请求                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐                                                │
│  │ 请求预处理  │ ◄─── IP 解析 / 设备指纹 / 地理位置              │
│  └──────┬──────┘                                                │
│         │                                                       │
│         ▼                                                       │
│  ┌─────────────────────────────────────────┐                    │
│  │           多维度风险分析引擎             │                    │
│  ├─────────────────────────────────────────┤                    │
│  │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐│                    │
│  │  │ IP    │ │ 设备  │ │ 地理  │ │ 行为  ││                    │
│  │  │ 风险  │ │ 风险  │ │ 风险  │ │ 风险  ││                    │
│  │  └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘│                    │
│  │      └─────────┴─────────┴─────────┘    │                    │
│  │                  │                      │                    │
│  └──────────────────┼──────────────────────┘                    │
│                     ▼                                           │
│              ┌──────────┐                                       │
│              │ 风险评分 │ ◄─── 0-100 分                         │
│              └────┬─────┘                                       │
│                   │                                             │
│         ┌────────┼────────┬────────────┐                        │
│         ▼        ▼        ▼            ▼                        │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                  │
│    │ 低风险 │ │中风险  │ │ 高风险 │ │ 极高危 │                  │
│    │ 0-20   │ │ 21-50  │ │ 51-75  │ │ 76-100 │                  │
│    └────┬───┘ └────┬───┘ └────┬───┘ └────┬───┘                  │
│         │          │          │          │                      │
│         ▼          ▼          ▼          ▼                      │
│    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                  │
│    │ 正常   │ │ 记录+  │ │ MFA+   │ │ 阻止+  │                  │
│    │ 登录   │ │ 通知   │ │ 告警   │ │ 审核   │                  │
│    └────────┘ └────────┘ └────────┘ └────────┘                  │
│                                                                 │
│  ┌─────────────────────────────────────────┐                    │
│  │              告警 & 响应                 │                    │
│  ├─────────────────────────────────────────┤                    │
│  │  • 邮件/短信通知                         │                    │
│  │  • 安全事件记录                          │                    │
│  │  • 自动响应（锁定/验证）                 │                    │
│  │  • 人工审核队列                          │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 核心实现步骤

#### 步骤1：数据库设计

```sql
-- 登录日志表
CREATE TABLE login_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT,
    device_fingerprint VARCHAR(64),
    login_status VARCHAR(20) NOT NULL, -- success/failed/blocked
    failure_reason TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    city VARCHAR(100),
    country VARCHAR(50),
    asn INTEGER,
    isp VARCHAR(100),
    is_proxy BOOLEAN DEFAULT FALSE,
    is_vpn BOOLEAN DEFAULT FALSE,
    risk_score INTEGER DEFAULT 0,
    risk_factors JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_login_logs_user ON login_logs(user_id);
CREATE INDEX idx_login_logs_ip ON login_logs(ip_address);
CREATE INDEX idx_login_logs_created ON login_logs(created_at);
CREATE INDEX idx_login_logs_risk ON login_logs(risk_score);

-- 用户设备白名单
CREATE TABLE user_devices (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    device_fingerprint VARCHAR(64) NOT NULL,
    device_name VARCHAR(100),
    user_agent TEXT,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_trusted BOOLEAN DEFAULT FALSE,
    login_count INTEGER DEFAULT 0
);

CREATE INDEX idx_user_devices_user ON user_devices(user_id);
CREATE UNIQUE INDEX idx_user_devices_unique ON user_devices(user_id, device_fingerprint);

-- 异常事件表
CREATE TABLE anomaly_events (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_score INTEGER,
    factors JSONB,
    ip_address VARCHAR(45),
    device_fingerprint VARCHAR(64),
    action_taken VARCHAR(50), -- allowed/mfa_required/blocked
    resolved_at TIMESTAMP,
    resolved_by INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_anomaly_events_user ON anomaly_events(user_id);
CREATE INDEX idx_anomaly_events_type ON anomaly_events(event_type);
CREATE INDEX idx_anomaly_events_created ON anomaly_events(created_at);
```

#### 步骤2：完整检测服务

```python
# login_anomaly_service.py
import asyncio
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class IPInfo:
    """IP 信息"""
    ip: str
    country: str
    country_code: str
    city: str
    latitude: float
    longitude: float
    asn: int
    isp: str
    is_proxy: bool
    is_vpn: bool
    is_tor: bool
    is_datacenter: bool
    threat_level: str
    abuse_score: int

@dataclass
class AnomalyEvent:
    """异常事件"""
    event_type: str
    risk_level: str
    risk_score: int
    factors: List[Dict]
    action_taken: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None

class LoginAnomalyService:
    """登录异常检测服务"""

    def __init__(
        self,
        db,
        ip_lookup_service,
        notification_service,
        config: Dict
    ):
        self.db = db
        self.ip_service = ip_lookup_service
        self.notification = notification_service
        self.config = config

        # 检测配置
        self.thresholds = {
            'low': config.get('low_threshold', 20),
            'medium': config.get('medium_threshold', 50),
            'high': config.get('high_threshold', 75),
        }

        # 响应配置
        self.responses = {
            'low': self._allow_login,
            'medium': self._allow_with_notification,
            'high': self._require_mfa,
            'critical': self._block_and_alert,
        }

    async def process_login(
        self,
        user_id: str,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str
    ) -> Dict:
        """
        处理登录请求，返回处理结果

        Returns:
            {
                "allowed": bool,
                "action": str,
                "risk_score": int,
                "risk_level": str,
                "requires_mfa": bool,
                "message": str
            }
        """
        # 1. 获取 IP 信息
        ip_info = await self._get_ip_info(ip_address)

        # 2. 构造上下文
        context = {
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'device_fingerprint': device_fingerprint,
            'timestamp': datetime.utcnow(),
            'ip_info': asdict(ip_info) if ip_info else {},
        }

        # 3. 执行分析
        result = await self._analyze(context)

        # 4. 执行响应
        response = await self._execute_response(
            risk_level=result['risk_level'],
            context=context,
            result=result
        )

        # 5. 记录日志
        await self._log_login_attempt(
            context=context,
            result=result,
            action=response['action']
        )

        return response

    async def _analyze(self, context: Dict) -> Dict:
        """执行多维分析"""
        factors = []
        total_score = 0

        # 获取历史数据
        history = await self._get_login_history(context['user_id'])
        known_devices = await self._get_known_devices(context['user_id'])

        # IP 风险分析
        ip_score, ip_factors = await self._analyze_ip(context)
        factors.extend(ip_factors)
        total_score += ip_score

        # 设备风险分析
        device_score, device_factors = await self._analyze_device(
            context, known_devices
        )
        factors.extend(device_factors)
        total_score += device_score

        # 地理风险分析
        geo_score, geo_factors = await self._analyze_geography(
            context, history
        )
        factors.extend(geo_factors)
        total_score += geo_score

        # 行为风险分析
        behavior_score, behavior_factors = await self._analyze_behavior(
            context
        )
        factors.extend(behavior_factors)
        total_score += behavior_score

        # 计算最终风险等级
        risk_level = self._calculate_risk_level(total_score)

        return {
            'risk_score': min(total_score, 100),
            'risk_level': risk_level,
            'factors': factors,
        }

    async def _analyze_ip(self, context: Dict) -> tuple:
        """IP 风险分析"""
        score = 0
        factors = []
        ip_info = context.get('ip_info', {})

        if not ip_info:
            return score, factors

        # 检查代理/VPN
        if ip_info.get('is_tor'):
            score += 30
            factors.append({
                'type': 'tor_exit_node',
                'score': 30,
                'detail': '登录来自 Tor 出口节点'
            })

        if ip_info.get('is_proxy'):
            score += 15
            factors.append({
                'type': 'proxy_ip',
                'score': 15,
                'detail': '登录来自代理服务器'
            })

        if ip_info.get('is_vpn'):
            score += 10
            factors.append({
                'type': 'vpn_ip',
                'score': 10,
                'detail': '登录来自 VPN 出口'
            })

        if ip_info.get('is_datacenter'):
            score += 10
            factors.append({
                'type': 'datacenter_ip',
                'score': 10,
                'detail': '登录来自数据中心 IP'
            })

        # 检查滥用评分
        abuse_score = ip_info.get('abuse_score', 0)
        if abuse_score > 70:
            score += 20
            factors.append({
                'type': 'high_abuse_score',
                'score': 20,
                'detail': f'IP 滥用评分过高: {abuse_score}'
            })
        elif abuse_score > 40:
            score += 10
            factors.append({
                'type': 'elevated_abuse_score',
                'score': 10,
                'detail': f'IP 滥用评分偏高: {abuse_score}'
            })

        return score, factors

    async def _analyze_device(
        self,
        context: Dict,
        known_devices: List[Dict]
    ) -> tuple:
        """设备风险分析"""
        score = 0
        factors = []
        fingerprint = context['device_fingerprint']
        user_agent = context['user_agent']

        # 检查是否为新设备
        known_fps = {d['device_fingerprint'] for d in known_devices}
        if fingerprint not in known_fps:
            score += 20
            factors.append({
                'type': 'new_device',
                'score': 20,
                'detail': '检测到新设备登录'
            })

        # 检查自动化工具
        automation_keywords = [
            'headless', 'selenium', 'webdriver',
            'phantomjs', 'puppeteer', 'playwright'
        ]
        ua_lower = user_agent.lower()
        for keyword in automation_keywords:
            if keyword in ua_lower:
                score += 35
                factors.append({
                    'type': 'automation_detected',
                    'score': 35,
                    'detail': f'检测到自动化工具: {keyword}'
                })
                break

        # 检查异常 User-Agent
        if not user_agent or len(user_agent) < 20:
            score += 15
            factors.append({
                'type': 'suspicious_ua',
                'score': 15,
                'detail': 'User-Agent 异常'
            })

        return score, factors

    async def _analyze_geography(
        self,
        context: Dict,
        history: List[Dict]
    ) -> tuple:
        """地理风险分析"""
        score = 0
        factors = []
        ip_info = context.get('ip_info', {})

        if not history or not ip_info.get('latitude'):
            return score, factors

        last_login = history[0]
        if not last_login.get('latitude'):
            return score, factors

        # 计算距离
        distance = self._calculate_distance(
            ip_info['latitude'], ip_info['longitude'],
            last_login['latitude'], last_login['longitude']
        )

        # 计算时间间隔
        time_diff = (
            context['timestamp'] - last_login['created_at']
        ).total_seconds() / 3600

        if time_diff <= 0:
            return score, factors

        # 不可能旅行检测
        speed = distance / time_diff
        if speed > 900:  # 超过飞机速度
            score += 40
            factors.append({
                'type': 'impossible_travel',
                'score': 40,
                'detail': f'不可能旅行: {distance:.0f}km/{time_diff:.1f}h'
            })
        elif distance > 1000 and time_diff < 12:
            score += 20
            factors.append({
                'type': 'suspicious_distance',
                'score': 20,
                'detail': f'短时间内大范围移动: {distance:.0f}km'
            })

        # 跨国登录
        if ip_info.get('country_code') and last_login.get('country_code'):
            if ip_info['country_code'] != last_login['country_code']:
                score += 10
                factors.append({
                    'type': 'country_change',
                    'score': 10,
                    'detail': f'跨国登录: {last_login["country_code"]} → {ip_info["country_code"]}'
                })

        return score, factors

    async def _analyze_behavior(self, context: Dict) -> tuple:
        """行为风险分析"""
        score = 0
        factors = []

        # 检查最近失败登录
        recent_failures = await self._get_recent_failures(
            context['user_id'],
            hours=1
        )

        if recent_failures >= 5:
            score += 30
            factors.append({
                'type': 'brute_force_attempt',
                'score': 30,
                'detail': f'1小时内失败登录{recent_failures}次'
            })
        elif recent_failures >= 3:
            score += 15
            factors.append({
                'type': 'multiple_failures',
                'score': 15,
                'detail': f'1小时内失败登录{recent_failures}次'
            })

        # 检查活跃会话数
        active_sessions = await self._get_active_sessions(context['user_id'])
        if len(active_sessions) > 10:
            score += 20
            factors.append({
                'type': 'excessive_sessions',
                'score': 20,
                'detail': f'活跃会话数过多: {len(active_sessions)}'
            })
        elif len(active_sessions) > 5:
            score += 10
            factors.append({
                'type': 'multiple_sessions',
                'score': 10,
                'detail': f'多个活跃会话: {len(active_sessions)}'
            })

        return score, factors

    # ============== 响应动作 ==============

    async def _allow_login(self, context: Dict, result: Dict) -> Dict:
        """允许登录"""
        return {
            'allowed': True,
            'action': 'allowed',
            'risk_score': result['risk_score'],
            'risk_level': result['risk_level'],
            'requires_mfa': False,
            'message': '登录成功'
        }

    async def _allow_with_notification(
        self,
        context: Dict,
        result: Dict
    ) -> Dict:
        """允许登录并发送通知"""
        # 发送安全通知
        await self._send_security_notification(
            user_id=context['user_id'],
            event='suspicious_login',
            details={
                'ip': context['ip_address'],
                'location': context.get('ip_info', {}).get('city', 'Unknown'),
                'factors': result['factors']
            }
        )

        return {
            'allowed': True,
            'action': 'allowed_with_notification',
            'risk_score': result['risk_score'],
            'risk_level': result['risk_level'],
            'requires_mfa': False,
            'message': '登录成功，已发送安全通知'
        }

    async def _require_mfa(self, context: Dict, result: Dict) -> Dict:
        """要求 MFA 验证"""
        return {
            'allowed': False,
            'action': 'mfa_required',
            'risk_score': result['risk_score'],
            'risk_level': result['risk_level'],
            'requires_mfa': True,
            'message': '检测到异常登录，请进行二次验证'
        }

    async def _block_and_alert(self, context: Dict, result: Dict) -> Dict:
        """阻止登录并告警"""
        # 记录异常事件
        await self._create_anomaly_event(
            user_id=context['user_id'],
            event_type='blocked_login',
            risk_level='critical',
            risk_score=result['risk_score'],
            factors=result['factors'],
            context=context
        )

        # 发送告警
        await self._send_security_alert(
            user_id=context['user_id'],
            event='blocked_login',
            details={
                'ip': context['ip_address'],
                'factors': result['factors']
            }
        )

        return {
            'allowed': False,
            'action': 'blocked',
            'risk_score': result['risk_score'],
            'risk_level': result['risk_level'],
            'requires_mfa': False,
            'message': '登录已被阻止，请联系客服'
        }

    # ============== 辅助方法 ==============

    def _calculate_risk_level(self, score: int) -> str:
        """计算风险等级"""
        if score >= self.thresholds['high']:
            return 'critical'
        elif score >= self.thresholds['medium']:
            return 'high'
        elif score >= self.thresholds['low']:
            return 'medium'
        return 'low'

    def _calculate_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """计算球面距离（公里）"""
        import math
        R = 6371

        lat1, lon1, lat2, lon2 = map(
            math.radians, [lat1, lon1, lat2, lon2]
        )
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = math.sin(dlat/2)**2 + \
            math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    async def _get_ip_info(self, ip: str) -> Optional[IPInfo]:
        """获取 IP 信息"""
        if not self.ip_service:
            return None
        return await self.ip_service.lookup(ip)

    async def _get_login_history(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """获取登录历史"""
        return await self.db.fetch_all("""
            SELECT * FROM login_logs
            WHERE user_id = $1 AND login_status = 'success'
            ORDER BY created_at DESC
            LIMIT $2
        """, user_id, limit)

    async def _get_known_devices(self, user_id: str) -> List[Dict]:
        """获取已知设备"""
        return await self.db.fetch_all("""
            SELECT * FROM user_devices
            WHERE user_id = $1
        """, user_id)

    async def _get_recent_failures(
        self,
        user_id: str,
        hours: int = 1
    ) -> int:
        """获取最近失败次数"""
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self.db.fetch_one("""
            SELECT COUNT(*) as count FROM login_logs
            WHERE user_id = $1
              AND login_status = 'failed'
              AND created_at > $2
        """, user_id, since)
        return result['count']

    async def _get_active_sessions(self, user_id: str) -> List[Dict]:
        """获取活跃会话"""
        return await self.db.fetch_all("""
            SELECT * FROM user_sessions
            WHERE user_id = $1 AND expires_at > NOW()
        """, user_id)
```

### 告警配置

```python
# alert_config.py
ALERT_CONFIG = {
    # 告警渠道
    'channels': {
        'email': {
            'enabled': True,
            'template': 'security_alert_email.html'
        },
        'sms': {
            'enabled': False,  # 付费服务
        },
        'webhook': {
            'enabled': True,
            'url': 'https://your-webhook.com/security-alerts'
        }
    },

    # 告警规则
    'rules': {
        'new_device_login': {
            'risk_levels': ['medium', 'high', 'critical'],
            'notify_user': True,
            'notify_admin': False,
        },
        'impossible_travel': {
            'risk_levels': ['high', 'critical'],
            'notify_user': True,
            'notify_admin': True,
        },
        'blocked_login': {
            'risk_levels': ['critical'],
            'notify_user': True,
            'notify_admin': True,
        },
        'brute_force_detected': {
            'risk_levels': ['high', 'critical'],
            'notify_user': True,
            'notify_admin': True,
        }
    },

    # 告警频率限制
    'rate_limits': {
        'per_user_per_hour': 5,
        'per_ip_per_hour': 10,
    }
}
```

## 成本估算

### 免费方案

| 项目 | 说明 | 成本 |
|------|------|------|
| IP 地理位置查询 | ip-api.com 免费版 | $0（45次/分钟限制） |
| 代理检测 | 免费数据库（IP2Proxy LITE） | $0 |
| 数据库存储 | 检测日志存储 | 视数据量 |
| **总计** | **基础功能** | **$0/月** |

### 付费方案

| 项目 | 月成本 | 说明 |
|------|--------|------|
| IP 地理位置API | $20 | MaxMind GeoIP2（100k次/月） |
| 代理/VPN检测 | $30 | IPHub/IPQualityScore |
| 邮件通知 | $15 | SendGrid Essential |
| **总计** | **$65/月** | 中等用户量 |

## 迁出成本

### 从自建迁移到第三方

| 项目 | 难度 | 时间 |
|------|------|------|
| 集成 SDK | 低 | 2-4小时 |
| 数据迁移 | 中 | 1天 |
| 规则调整 | 中 | 1-2天 |

### 从第三方迁移到自建

| 项目 | 难度 | 时间 |
|------|------|------|
| 规则迁移 | 高 | 3-5天 |
| 数据库建设 | 中 | 1-2天 |
| 测试验证 | 中 | 2-3天 |

## 与其他武器配合

### 上游武器

| 武器 | 配合方式 |
|------|----------|
| **输入验证** | 登录前验证输入格式 |
| **密码策略** | 检测弱密码登录尝试 |

### 下游武器

| 武器 | 配合方式 |
|------|----------|
| **MFA 实现** | 高风险登录触发 MFA |
| **账号恢复** | 账号被盗后的恢复入口 |
| **会话安全** | 异常登录后撤销会话 |

### 配合示例

```python
# 完整登录流程
async def login_handler(request):
    # 1. 输入验证
    if not validate_login_input(request):
        return error("无效的输入")

    # 2. 密码验证
    user = await verify_password(request.email, request.password)
    if not user:
        await record_failed_attempt(request.email, request.ip)
        return error("邮箱或密码错误")

    # 3. 异常检测
    anomaly_result = await anomaly_service.process_login(
        user_id=user.id,
        ip_address=request.ip,
        user_agent=request.user_agent,
        device_fingerprint=request.device_fingerprint
    )

    # 4. 根据检测结果处理
    if anomaly_result['action'] == 'blocked':
        return error("登录已被阻止，请联系客服")

    if anomaly_result['requires_mfa']:
        # 重定向到 MFA 验证
        return redirect("/auth/mfa")

    # 5. 创建会话
    session = await create_session(user.id)

    # 6. 记录设备
    await record_device(user.id, request.device_fingerprint)

    return success(session)
```

## 常见问题

### Q1: 误判率如何控制？

**A:** 通过调整阈值和白名单机制：

```python
# 设备白名单
async def is_trusted_device(user_id: str, fingerprint: str) -> bool:
    device = await db.fetch_one("""
        SELECT is_trusted FROM user_devices
        WHERE user_id = $1 AND device_fingerprint = $2
    """, user_id, fingerprint)
    return device and device['is_trusted']

# 在分析时跳过可信设备
if await is_trusted_device(user_id, fingerprint):
    return {'risk_score': 0, 'risk_level': 'low', 'factors': []}
```

### Q2: 如何处理 VPN 用户？

**A:** 区分用户主动使用 VPN 和可疑代理：

```python
# 检查用户是否已声明使用 VPN
async def check_vpn_user_preference(user_id: str, ip_info: Dict) -> bool:
    preference = await get_user_security_preference(user_id)
    if preference.get('uses_vpn'):
        # 用户已声明使用 VPN，降低评分
        return True
    return False
```

### Q3: 如何避免影响正常用户旅行？

**A:** 提供"我在旅行"声明：

```python
# 用户可以提前声明旅行计划
async def declare_travel(user_id: str, destination: str, dates: tuple):
    await db.execute("""
        INSERT INTO travel_declarations
        (user_id, destination, start_date, end_date)
        VALUES ($1, $2, $3, $4)
    """, user_id, destination, dates[0], dates[1])

# 检测时检查是否有有效声明
async def has_valid_travel_declaration(user_id: str, country: str) -> bool:
    return await db.fetch_one("""
        SELECT 1 FROM travel_declarations
        WHERE user_id = $1
          AND destination = $2
          AND start_date <= CURRENT_DATE
          AND end_date >= CURRENT_DATE
    """, user_id, country)
```

### Q4: 如何处理分布式攻击？

**A:** 全局 IP 信誉评分：

```python
# 跨用户的 IP 信誉系统
async def get_ip_reputation(ip: str) -> Dict:
    """获取 IP 的全局信誉"""
    stats = await db.fetch_one("""
        SELECT
            COUNT(DISTINCT user_id) as affected_users,
            COUNT(*) FILTER (WHERE login_status = 'failed') as failed_attempts,
            COUNT(*) FILTER (WHERE risk_score > 50) as high_risk_logins
        FROM login_logs
        WHERE ip_address = $1
          AND created_at > NOW() - INTERVAL '24 hours'
    """, ip)

    return {
        'affected_users': stats['affected_users'],
        'failed_attempts': stats['failed_attempts'],
        'is_suspicious': stats['affected_users'] > 10 or stats['failed_attempts'] > 50
    }
```

### Q5: 检测结果如何用于后续风控？

**A:** 建立用户风险档案：

```python
# 用户风险档案
async def update_user_risk_profile(user_id: str, event: Dict):
    """更新用户风险档案"""
    await db.execute("""
        INSERT INTO user_risk_profiles (user_id, risk_events, last_updated)
        VALUES ($1, jsonb_build_array($2), NOW())
        ON CONFLICT (user_id) DO UPDATE SET
            risk_events = user_risk_profiles.risk_events || $2,
            risk_score = user_risk_profiles.risk_score + $3,
            last_updated = NOW()
    """, user_id, json.dumps(event), event.get('risk_score', 0))
```

## 安全清单

- [ ] 记录所有登录尝试（成功和失败）
- [ ] 使用加密安全的随机数生成令牌
- [ ] 不在日志中存储敏感信息
- [ ] 实现合理的告警频率限制
- [ ] 定期审计异常事件记录
- [ ] 提供 IP 白名单功能
- [ ] 支持设备信任管理
- [ ] 实现不可能旅行检测
- [ ] 检测自动化工具
- [ ] 建立用户风险档案
