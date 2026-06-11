# 限流绕过攻击

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $50-100/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过代理池或 IP 轮换绕过你的限流保护，像一群人排队领免费咖啡，每个人都换一套衣服重新排队。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 限流仅基于 IP 地址
- [ ] 提供公开 API 或有免费额度
- [ ] 涉及抢购、抽奖、优惠券等利益场景
- [ ] 未设置用户级别限流
- [ ] 限流阈值宽松（>100次/分钟）
→ 勾选≥1项，即需关注此风险

### 一句话防御
三层限流：IP限流（基础）+ 用户限流（核心）+ 行为限流（进阶），30分钟内可实施。

### 快速行动清单
1. [ ] **立即行动项（今天可完成，免费）**：
   - 为关键 API 添加用户级限流（如 60次/分钟/用户）
   - 记录并监控异常高频访问日志
   - 在 Nginx/应用层添加 IP 限流作为第一道防线

2. [ ] **短期行动项（本周可完成，免费）**：
   - 实现滑动窗口限流算法替代固定窗口
   - 添加限流触发后的告警通知
   - 配置日志记录限流事件

3. [ ] **长期行动项（规划中，低成本）**：
   - 接入行为分析服务检测异常模式
   - 考虑部署分布式限流方案（如 Redis + Lua）
   - 建立自动化封禁机制

### 推荐工具
- **免费**：
  - Nginx limit_req 模块 - [文档](https://nginx.org/en/docs/http/ngx_http_limit_req_module.html) - 原生支持，无需额外成本
  - Redis + Lua 脚本 - [GitHub](https://github.com/antirez/redisclock) - 自托管限流

- **低成本**：
  - Cloudflare Rate Limiting - $5/月起 - 边缘限流，减轻服务器压力
  - Upstash Rate Limiting - $0.2/100K 请求 - Serverless 友好

### 验证方法
- [ ] 使用不同 IP 模拟高频访问，验证限流生效
- [ ] 使用同一账户不同 IP 访问，验证用户级限流生效
- [ ] 检查日志是否记录限流事件
- [ ] 模拟正常用户行为，确认无误拦截

---

## L2 小团队版（理解版）

### 场景还原
某独立开发者的 API 服务提供免费套餐（1000次/天），攻击者使用代理池（1000个IP）在10分钟内消耗了你100万次调用额度，相当于正常用户3年的使用量，而你的账单增加了$500。

### 攻击路径（3-5步）
1. **信息收集**：攻击者发现限流仅基于 IP（如 X-Forwarded-For 头）
2. **工具准备**：使用免费代理池（如 ProxyScrape）或购买住宅代理服务
3. **绕过实施**：每个请求使用不同代理 IP，每次都能通过限流检查
4. **持续攻击**：自动化脚本持续调用，消耗 API 配额或服务器资源
5. **后果显现**：正常用户无法访问、API 成本激增、服务降级

### 防御实施（低成本方案）

#### 方案A：免费方案（三层限流）

**工具/服务**：Nginx + 应用层限流 + Redis

**配置步骤**：

1. **IP 限流（Nginx 层）**
```nginx
# /etc/nginx/conf.d/rate-limit.conf
limit_req_zone $binary_remote_addr zone=ip_limit:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=ip_limit burst=20 nodelay;
        limit_req_status 429;
        # ...
    }
}
```

2. **用户限流（应用层）**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)

# 用户级限流（需要认证）
@app.route("/api/premium")
@limiter.limit("100 per minute", key_func=lambda: current_user.id)
def premium_endpoint():
    return {"data": "..."}
```

3. **滑动窗口限流（Redis）**
```python
import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

def sliding_window_rate_limit(user_id, limit=60, window=60):
    """滑动窗口限流算法"""
    now = time.time()
    key = f"rate_limit:{user_id}"

    # 移除窗口外的记录
    r.zremrangebyscore(key, 0, now - window)

    # 获取当前窗口内的请求数
    current = r.zcard(key)

    if current < limit:
        # 添加新请求
        r.zadd(key, {str(now): now})
        r.expire(key, window)
        return True

    return False
```

**局限性**：
- 单机部署时 Redis 可能成为瓶颈
- 需要维护限流配置
- 行为检测能力有限

#### 方案B：低成本方案（<$50/月）

**工具/服务**：Cloudflare Rate Limiting + 行为分析

**配置步骤**：

1. **Cloudflare 边缘限流**
```yaml
# Cloudflare 规则配置
# 在 Cloudflare Dashboard → Security → WAF
- 表达式: (http.request.uri.path contains "/api/")
- 速率: 100 请求/分钟/IP
- 动作: Block
- 超时: 10分钟
```

2. **行为检测（简单版）**
```python
from collections import defaultdict
from datetime import datetime, timedelta

# 内存中的行为追踪（生产环境建议用 Redis）
behavior_tracker = defaultdict(list)

def detect_abnormal_behavior(user_id, action):
    """检测异常行为模式"""
    now = datetime.now()
    behavior_tracker[user_id].append(now)

    # 只保留最近10分钟记录
    behavior_tracker[user_id] = [
        t for t in behavior_tracker[user_id]
        if now - t < timedelta(minutes=10)
    ]

    # 检测异常模式
    recent_actions = len(behavior_tracker[user_id])

    # 规则1：高频访问
    if recent_actions > 500:  # 10分钟内超过500次
        return "high_frequency"

    # 规则2：规律性访问（机器人特征）
    if recent_actions > 50:
        timestamps = behavior_tracker[user_id][-20:]
        intervals = [(timestamps[i+1] - timestamps[i]).total_seconds()
                     for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval)**2 for x in intervals) / len(intervals)

        if variance < 0.1:  # 间隔时间过于规律
            return "bot_pattern"

    return None
```

3. **组合防御**
```python
@app.route("/api/resource")
def protected_resource():
    user_id = get_current_user_id()

    # 第一层：基础限流
    if not sliding_window_rate_limit(user_id, limit=100):
        return {"error": "Rate limit exceeded"}, 429

    # 第二层：行为检测
    behavior = detect_abnormal_behavior(user_id, "api_call")
    if behavior:
        log_suspicious_activity(user_id, behavior)
        if behavior == "bot_pattern":
            # 触发验证码或临时封禁
            return {"error": "Suspicious activity", "require_captcha": True}, 403

    return {"data": "..."}
```

**优势**：
- 边缘节点分担限流压力
- Cloudflare 提供基础的机器人检测
- 降低服务器负载
- 有 Dashboard 可视化监控

### 决策树
```
你的 API 是否涉及利益场景（抢购/优惠券/免费额度）？
├── 是 → 必须采用三层限流 + 行为检测
│   ├── 预算充足 → 方案B（Cloudflare）
│   └── 预算有限 → 方案A（自建）
└── 否 → 是否提供公开 API？
    ├── 是 → 采用用户级限流 + IP限流
    └── 否 → 仅需 IP 限流
```

### 代码示例

**完整限流中间件（Flask 示例）**
```python
from functools import wraps
from flask import request, jsonify, g
import redis
import time
import hashlib

# Redis 连接（生产环境使用连接池）
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class RateLimiter:
    """多层限流器"""

    def __init__(self, redis_client):
        self.redis = redis_client

    def check_ip_limit(self, ip, limit=1000, window=60):
        """IP 级别限流"""
        key = f"ip_limit:{ip}"
        return self._sliding_window(key, limit, window)

    def check_user_limit(self, user_id, limit=100, window=60):
        """用户级别限流"""
        key = f"user_limit:{user_id}"
        return self._sliding_window(key, limit, window)

    def check_endpoint_limit(self, endpoint, user_id, limit=10, window=60):
        """端点级别限流（防止某个接口被滥用）"""
        key = f"endpoint_limit:{endpoint}:{user_id}"
        return self._sliding_window(key, limit, window)

    def _sliding_window(self, key, limit, window):
        """滑动窗口算法"""
        now = time.time()

        # Lua 脚本保证原子性
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])

        -- 移除窗口外的记录
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

        -- 获取当前计数
        local current = redis.call('ZCARD', key)

        if current < limit then
            -- 添加新请求
            redis.call('ZADD', key, now, now .. '-' .. math.random())
            redis.call('EXPIRE', key, window)
            return 1
        else
            return 0
        end
        """

        result = self.redis.eval(lua_script, 1, key, limit, window, now)
        return result == 1

    def get_remaining(self, key):
        """获取剩余配额"""
        now = time.time()
        return limit - self.redis.zcard(key)


# 使用示例
limiter = RateLimiter(redis_client)

def rate_limit(ip_limit=1000, user_limit=100, endpoint_limit=None):
    """限流装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if ',' in ip:
                ip = ip.split(',')[0].strip()

            # IP 限流
            if not limiter.check_ip_limit(ip, ip_limit):
                return jsonify({
                    "error": "IP rate limit exceeded",
                    "retry_after": 60
                }), 429

            # 用户限流（需要认证）
            if hasattr(g, 'current_user') and g.current_user:
                if not limiter.check_user_limit(g.current_user.id, user_limit):
                    return jsonify({
                        "error": "User rate limit exceeded",
                        "retry_after": 60
                    }), 429

                # 端点限流
                if endpoint_limit:
                    if not limiter.check_endpoint_limit(
                        request.endpoint,
                        g.current_user.id,
                        endpoint_limit
                    ):
                        return jsonify({
                            "error": "Endpoint rate limit exceeded",
                            "retry_after": 60
                        }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


# 应用到路由
@app.route("/api/data")
@rate_limit(ip_limit=1000, user_limit=100)
def get_data():
    return {"data": "..."}


@app.route("/api/premium-action")
@rate_limit(ip_limit=100, user_limit=10, endpoint_limit=5)
def premium_action():
    return {"result": "success"}
```

---

## L3 企业版（深耕版）

参见企业级案例：[限流与流量控制](../../enterprise/infosec/rate-limiting.md)

### 高级限流策略

1. **自适应限流**
   - 基于系统负载动态调整阈值
   - 服务降级时自动收紧限流

2. **分布式限流**
   - 使用 Redis Cluster 或 etcd
   - 一致性哈希减少锁竞争

3. **机器学习行为检测**
   - 训练用户行为模型
   - 实时异常检测

### 推荐企业方案
- Kong Enterprise - $650/月起
- AWS WAF + Shield - 按使用量计费
- Akamai Bot Manager - 企业定价

---

## 相关案例
- [API 未授权访问](./unauthorized-access.md)
- [分布式拒绝服务攻击](../../enterprise/infosec/ddos.md)

## 推荐武器
- [Redis 限流器](../../../weapons/indie/open-source/redis-limiter.md)
- [Cloudflare WAF 配置](../../../weapons/indie/saas/cloudflare-waf.md)
