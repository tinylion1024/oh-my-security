# 订阅绕过攻击 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: payment（支付安全）
- **严重程度**: high（高危）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户绕过订阅验证逻辑，免费使用付费功能，你的损失：订阅费用全额 + 服务器资源消耗。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 订阅状态仅在前端验证
- [ ] 后端 API 未验证订阅状态
- [ ] 缺少订阅有效期检查
- [ ] 订阅状态更新有延迟
→ 勾选≥1项，即需关注此风险

### 一句话防御
**每次 API 请求都必须验证订阅状态**，订阅状态必须由后端实时查询数据库，不信任前端传递的任何订阅参数。

### 快速行动清单
1. [ ] 立即行动项：检查所有付费 API，确认是否验证订阅状态（今天可完成，免费）
2. [ ] 短期行动项：添加订阅状态中间件，所有付费接口自动验证（本周可完成，免费）
3. [ ] 长期行动项：实现定期订阅检查机制，自动过期未续费订阅（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用订阅管理服务（Stripe Billing）

### 验证方法
- [ ] 在前端修改订阅状态为 "active"
- [ ] 调用付费功能 API
- [ ] 确认系统拒绝访问，返回 403 错误

---

## L2 小团队版（理解版）

### 场景还原
你开发了一个 SaaS 产品，提供基础版（免费）和专业版（$29/月）。用户订阅专业版后，可以访问高级分析功能、导出数据和 API 调用额度。攻击者发现你的系统在前端 JavaScript 中判断订阅状态，于是修改了浏览器中的订阅状态变量，绕过了前端验证。虽然攻击者没有付款，但仍然可以调用所有专业版 API，你的服务器资源被消耗，真实付费用户无法正常使用。

### 攻击路径（简化版）
1. **发现漏洞**：攻击者检查前端代码，发现订阅状态仅在前端验证
2. **修改状态**：通过浏览器开发者工具修改订阅状态变量或 localStorage
3. **绕过前端**：前端显示为"专业版用户"，界面正常访问
4. **调用 API**：由于后端未验证，API 直接返回付费数据
5. **长期免费使用**：攻击者持续使用付费功能，无需付款

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：订阅状态必须由后端实时验证，不信任前端传递的任何订阅参数。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：仅在前端验证
# 前端 JavaScript
function checkSubscription() {
    const user = JSON.parse(localStorage.getItem('user'));
    if (user.subscription === 'pro') {
        showProFeatures();  // 仅前端判断！
    }
}

// 后端 API
@app.route('/api/export-data')
def export_data():
    # 未验证订阅状态，直接返回数据！
    data = get_user_data(current_user.id)
    return jsonify(data)
```

2. **修复代码 - 订阅验证中间件**：
```python
from functools import wraps
from flask import request, jsonify, g
from datetime import datetime

def require_subscription(min_plan='basic'):
    """
    订阅验证装饰器
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.user_id
            
            # 查询用户订阅状态
            subscription = db.query("""
                SELECT plan, status, expires_at
                FROM subscriptions
                WHERE user_id = ? AND status = 'active'
                ORDER BY expires_at DESC
                LIMIT 1
            """, user_id)
            
            # 验证订阅是否存在
            if not subscription:
                return jsonify({
                    'error': '需要订阅',
                    'code': 'SUBSCRIPTION_REQUIRED'
                }), 403
            
            # 验证订阅状态
            if subscription.status != 'active':
                return jsonify({
                    'error': '订阅未激活',
                    'code': 'SUBSCRIPTION_INACTIVE'
                }), 403
            
            # 验证订阅是否过期
            if subscription.expires_at < datetime.now():
                # 自动更新订阅状态
                db.execute("""
                    UPDATE subscriptions
                    SET status = 'expired'
                    WHERE user_id = ? AND id = ?
                """, user_id, subscription.id)
                
                return jsonify({
                    'error': '订阅已过期',
                    'code': 'SUBSCRIPTION_EXPIRED'
                }), 403
            
            # 验证订阅等级
            plan_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
            user_plan_level = plan_hierarchy.get(subscription.plan, 0)
            required_plan_level = plan_hierarchy.get(min_plan, 1)
            
            if user_plan_level < required_plan_level:
                return jsonify({
                    'error': f'需要 {min_plan} 或更高等级订阅',
                    'code': 'SUBSCRIPTION_UPGRADE_REQUIRED',
                    'current_plan': subscription.plan,
                    'required_plan': min_plan
                }), 403
            
            # 将订阅信息存储到请求上下文
            g.subscription = subscription
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 使用示例
@app.route('/api/export-data')
@require_subscription(min_plan='pro')
def export_data():
    """导出数据 - 需要专业版订阅"""
    data = get_user_data(g.user_id)
    return jsonify(data)

@app.route('/api/analytics')
@require_subscription(min_plan='basic')
def analytics():
    """高级分析 - 需要基础版及以上订阅"""
    analytics_data = get_analytics(g.user_id)
    return jsonify(analytics_data)
```

3. **订阅状态检查服务**：
```python
class SubscriptionService:
    @staticmethod
    def get_active_subscription(user_id):
        """
        获取用户有效订阅
        """
        subscription = db.query("""
            SELECT id, plan, status, expires_at, created_at
            FROM subscriptions
            WHERE user_id = ? AND status = 'active' AND expires_at > NOW()
            ORDER BY expires_at DESC
            LIMIT 1
        """, user_id)
        
        return subscription
    
    @staticmethod
    def check_subscription_access(user_id, required_plan):
        """
        检查用户订阅是否满足要求
        """
        subscription = SubscriptionService.get_active_subscription(user_id)
        
        if not subscription:
            return False, 'NO_SUBSCRIPTION'
        
        plan_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
        user_plan_level = plan_hierarchy.get(subscription.plan, 0)
        required_plan_level = plan_hierarchy.get(required_plan, 1)
        
        if user_plan_level < required_plan_level:
            return False, 'UPGRADE_REQUIRED'
        
        return True, subscription
    
    @staticmethod
    def refresh_subscription_status(user_id):
        """
        刷新订阅状态（定期任务）
        """
        # 查询所有过期但状态仍为 active 的订阅
        expired_subs = db.query_all("""
            SELECT id, user_id, expires_at
            FROM subscriptions
            WHERE user_id = ? AND status = 'active' AND expires_at < NOW()
        """, user_id)
        
        if expired_subs:
            for sub in expired_subs:
                # 更新订阅状态
                db.execute("""
                    UPDATE subscriptions
                    SET status = 'expired', updated_at = NOW()
                    WHERE id = ?
                """, sub.id)
                
                logger.info(f"订阅已过期: user_id={sub.user_id}, subscription_id={sub.id}")
            
            return len(expired_subs)
        
        return 0

# 定期检查任务（使用 Celery 或 APScheduler）
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', hours=1)
def check_all_subscriptions():
    """
    每小时检查所有订阅状态
    """
    # 查询所有需要检查的用户
    users = db.query_all("""
        SELECT DISTINCT user_id
        FROM subscriptions
        WHERE status = 'active'
    """)
    
    for user in users:
        SubscriptionService.refresh_subscription_status(user.user_id)

scheduler.start()
```

4. **订阅状态缓存优化**：
```python
import redis
import json
from datetime import datetime, timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

class SubscriptionCache:
    @staticmethod
    def get_subscription(user_id):
        """
        获取订阅信息（带缓存）
        """
        cache_key = f"subscription:{user_id}"
        
        # 尝试从缓存获取
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 从数据库获取
        subscription = SubscriptionService.get_active_subscription(user_id)
        
        if subscription:
            # 缓存 5 分钟
            cache_data = {
                'id': subscription.id,
                'plan': subscription.plan,
                'status': subscription.status,
                'expires_at': subscription.expires_at.isoformat(),
            }
            redis_client.setex(
                cache_key,
                timedelta(minutes=5),
                json.dumps(cache_data)
            )
        
        return subscription
    
    @staticmethod
    def invalidate_cache(user_id):
        """
        清除订阅缓存（订阅变更时调用）
        """
        cache_key = f"subscription:{user_id}"
        redis_client.delete(cache_key)

# 使用缓存的验证中间件
def require_subscription_cached(min_plan='basic'):
    """
    订阅验证装饰器（带缓存）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = g.user_id
            
            # 从缓存获取订阅信息
            subscription = SubscriptionCache.get_subscription(user_id)
            
            if not subscription:
                return jsonify({
                    'error': '需要订阅',
                    'code': 'SUBSCRIPTION_REQUIRED'
                }), 403
            
            # 验证订阅状态
            if subscription['status'] != 'active':
                return jsonify({
                    'error': '订阅未激活',
                    'code': 'SUBSCRIPTION_INACTIVE'
                }), 403
            
            # 验证订阅等级
            plan_hierarchy = {'free': 0, 'basic': 1, 'pro': 2, 'enterprise': 3}
            user_plan_level = plan_hierarchy.get(subscription['plan'], 0)
            required_plan_level = plan_hierarchy.get(min_plan, 1)
            
            if user_plan_level < required_plan_level:
                return jsonify({
                    'error': f'需要 {min_plan} 或更高等级订阅',
                    'code': 'SUBSCRIPTION_UPGRADE_REQUIRED'
                }), 403
            
            g.subscription = subscription
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

**局限性**：
- 需要维护订阅状态同步
- 缓存可能导致订阅状态延迟更新

#### 方案B：使用 Stripe Billing（低成本）

**工具/服务**：Stripe Billing / Paddle

**优势**：
- Stripe 自动管理订阅状态
- Webhook 实时通知订阅变更
- 自动处理订阅过期和续费

**配置示例**：
```python
import stripe

# Webhook 处理订阅变更
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # 处理订阅事件
    if event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        handle_subscription_created(subscription)
    
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    return 'success', 200

def handle_subscription_created(subscription):
    """处理订阅创建"""
    customer_id = subscription['customer']
    user = db.query("SELECT id FROM users WHERE stripe_customer_id = ?", customer_id)
    
    if user:
        # 创建订阅记录
        db.execute("""
            INSERT INTO subscriptions
                (user_id, plan, status, expires_at, stripe_subscription_id, created_at)
            VALUES (?, ?, ?, ?, ?, NOW())
        """, user.id, subscription['plan']['id'], subscription['status'],
            datetime.fromtimestamp(subscription['current_period_end']),
            subscription['id'])
        
        # 清除缓存
        SubscriptionCache.invalidate_cache(user.id)

def handle_subscription_deleted(subscription):
    """处理订阅取消"""
    stripe_subscription_id = subscription['id']
    
    # 更新订阅状态
    db.execute("""
        UPDATE subscriptions
        SET status = 'cancelled', updated_at = NOW()
        WHERE stripe_subscription_id = ?
    """, stripe_subscription_id)
    
    # 清除缓存
    user = db.query("""
        SELECT user_id FROM subscriptions WHERE stripe_subscription_id = ?
    """, stripe_subscription_id)
    
    if user:
        SubscriptionCache.invalidate_cache(user.user_id)
```

**成本**：Stripe Billing 手续费 0.5% + 2.9% + $0.30/笔

### 决策树
```
后端是否验证订阅状态？
├── 否 → 立即添加订阅验证中间件（方案A）
└── 是 → 是否实时查询数据库？
    ├── 否 → 修改为实时查询（方案A）
    └── 是 → 是否有定期检查机制？
        ├── 否 → 添加定期检查任务（方案A）
        └── 是 → 当前方案基本完善
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify, g
from functools import wraps
from datetime import datetime, timedelta
import redis
import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
logger = logging.getLogger(__name__)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 订阅等级定义
PLAN_HIERARCHY = {
    'free': 0,
    'basic': 1,
    'pro': 2,
    'enterprise': 3
}

# 订阅状态定义
SUBSCRIPTION_STATUS = {
    'active': '有效',
    'expired': '已过期',
    'cancelled': '已取消',
    'past_due': '逾期'
}

class SubscriptionService:
    @staticmethod
    def get_active_subscription(user_id):
        """
        获取用户有效订阅（从数据库）
        """
        return db.query("""
            SELECT id, user_id, plan, status, expires_at,
                   stripe_subscription_id, created_at, updated_at
            FROM subscriptions
            WHERE user_id = ? AND status = 'active' AND expires_at > NOW()
            ORDER BY expires_at DESC
            LIMIT 1
        """, user_id)
    
    @staticmethod
    def check_access(user_id, required_plan):
        """
        检查用户订阅是否满足要求
        """
        subscription = SubscriptionService.get_active_subscription(user_id)
        
        if not subscription:
            return False, {
                'error': '需要订阅',
                'code': 'SUBSCRIPTION_REQUIRED'
            }
        
        user_plan_level = PLAN_HIERARCHY.get(subscription.plan, 0)
        required_plan_level = PLAN_HIERARCHY.get(required_plan, 1)
        
        if user_plan_level < required_plan_level:
            return False, {
                'error': f'需要 {required_plan} 或更高等级订阅',
                'code': 'SUBSCRIPTION_UPGRADE_REQUIRED',
                'current_plan': subscription.plan,
                'required_plan': required_plan
            }
        
        return True, subscription

class SubscriptionCache:
    @staticmethod
    def get(user_id):
        """
        获取订阅信息（带缓存）
        """
        cache_key = f"subscription:{user_id}"
        
        # 尝试从缓存获取
        cached = redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            # 检查缓存是否过期
            expires_at = datetime.fromisoformat(data['expires_at'])
            if expires_at > datetime.now():
                return data
            else:
                # 缓存过期，清除缓存
                redis_client.delete(cache_key)
        
        # 从数据库获取
        subscription = SubscriptionService.get_active_subscription(user_id)
        
        if subscription:
            cache_data = {
                'id': subscription.id,
                'plan': subscription.plan,
                'status': subscription.status,
                'expires_at': subscription.expires_at.isoformat(),
            }
            
            # 计算缓存时间：距离过期时间和 5 分钟中的较小值
            ttl = min(
                (subscription.expires_at - datetime.now()).total_seconds(),
                300
            )
            
            if ttl > 0:
                redis_client.setex(cache_key, ttl, json.dumps(cache_data))
            
            return cache_data
        
        return None
    
    @staticmethod
    def invalidate(user_id):
        """
        清除订阅缓存
        """
        cache_key = f"subscription:{user_id}"
        redis_client.delete(cache_key)
        logger.info(f"订阅缓存已清除: user_id={user_id}")

def require_subscription(min_plan='basic'):
    """
    订阅验证装饰器
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 从请求上下文获取用户 ID
            user_id = getattr(g, 'user_id', None)
            
            if not user_id:
                return jsonify({
                    'error': '未授权访问',
                    'code': 'UNAUTHORIZED'
                }), 401
            
            # 从缓存获取订阅信息
            subscription = SubscriptionCache.get(user_id)
            
            if not subscription:
                return jsonify({
                    'error': '需要订阅',
                    'code': 'SUBSCRIPTION_REQUIRED'
                }), 403
            
            # 验证订阅状态
            if subscription['status'] != 'active':
                return jsonify({
                    'error': '订阅未激活',
                    'code': 'SUBSCRIPTION_INACTIVE'
                }), 403
            
            # 验证订阅等级
            user_plan_level = PLAN_HIERARCHY.get(subscription['plan'], 0)
            required_plan_level = PLAN_HIERARCHY.get(min_plan, 1)
            
            if user_plan_level < required_plan_level:
                return jsonify({
                    'error': f'需要 {min_plan} 或更高等级订阅',
                    'code': 'SUBSCRIPTION_UPGRADE_REQUIRED',
                    'current_plan': subscription['plan'],
                    'required_plan': min_plan
                }), 403
            
            # 存储订阅信息到请求上下文
            g.subscription = subscription
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# 定期任务：检查过期订阅
scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', hours=1)
def check_expired_subscriptions():
    """
    每小时检查所有过期订阅
    """
    try:
        # 查询所有过期但状态仍为 active 的订阅
        expired_subs = db.query_all("""
            SELECT id, user_id, expires_at
            FROM subscriptions
            WHERE status = 'active' AND expires_at < NOW()
        """)
        
        if expired_subs:
            for sub in expired_subs:
                # 更新订阅状态
                db.execute("""
                    UPDATE subscriptions
                    SET status = 'expired', updated_at = NOW()
                    WHERE id = ?
                """, sub.id)
                
                # 清除缓存
                SubscriptionCache.invalidate(sub.user_id)
                
                logger.info(f"订阅已过期: user_id={sub.user_id}, subscription_id={sub.id}")
            
            logger.info(f"已处理 {len(expired_subs)} 个过期订阅")
    
    except Exception as e:
        logger.error(f"检查过期订阅失败: {e}")

scheduler.start()

# API 示例
@app.route('/api/export-data', methods=['POST'])
@require_subscription(min_plan='pro')
def export_data():
    """导出数据 - 需要专业版订阅"""
    user_id = g.user_id
    subscription = g.subscription
    
    # 执行导出操作
    data = export_user_data(user_id)
    
    logger.info(f"用户导出数据: user_id={user_id}, plan={subscription['plan']}")
    
    return jsonify({
        'data': data,
        'subscription': subscription['plan']
    })

@app.route('/api/analytics', methods=['GET'])
@require_subscription(min_plan='basic')
def analytics():
    """高级分析 - 需要基础版及以上订阅"""
    user_id = g.user_id
    subscription = g.subscription
    
    # 获取分析数据
    analytics_data = get_analytics(user_id)
    
    return jsonify({
        'analytics': analytics_data,
        'subscription': subscription['plan']
    })

@app.route('/api/subscription/status', methods=['GET'])
def subscription_status():
    """获取订阅状态"""
    user_id = g.user_id
    
    subscription = SubscriptionCache.get(user_id)
    
    if subscription:
        return jsonify({
            'has_subscription': True,
            'plan': subscription['plan'],
            'status': subscription['status'],
            'expires_at': subscription['expires_at']
        })
    else:
        return jsonify({
            'has_subscription': False,
            'plan': 'free',
            'status': None
        })

# 订阅更新接口（清除缓存）
@app.route('/api/subscription/update', methods=['POST'])
def update_subscription():
    """更新订阅（来自 Stripe Webhook）"""
    user_id = request.json.get('user_id')
    
    # 更新数据库订阅信息
    # ...
    
    # 清除缓存
    SubscriptionCache.invalidate(user_id)
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **订阅管理**：
   - 多层级订阅体系
   - 订阅降级保护期
   - 订阅继承和转让

2. **验证机制**：
   - 多节点订阅状态同步
   - 订阅状态一致性检查
   - 订阅欺诈检测

3. **风控规则**：
   - 异常订阅行为检测
   - 订阅共享检测
   - 订阅状态异常监控

4. **监控告警**：
   - 订阅绕过告警
   - 订阅异常告警
   - 订阅使用量监控

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [Stripe Billing 文档](https://stripe.com/docs/billing)
- [订阅管理最佳实践](https://www.paddle.com/blog/subscription-management)
- [订阅欺诈防范](https://stripe.com/docs/billing/subscriptions/overview)
