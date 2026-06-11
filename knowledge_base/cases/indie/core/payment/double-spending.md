# 双花攻击 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: payment（支付安全）
- **严重程度**: critical（严重）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户完成一次支付后，重复提交支付回调或重放支付请求，多次获取商品或服务，你的损失：商品价值 × 重复次数。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 支付回调接口未检查订单是否已处理
- [ ] 支付成功后未更新订单状态
- [ ] 使用支付 ID 而非订单 ID 作为唯一标识
- [ ] 未实现支付回调的幂等性
→ 勾选≥1项，即需关注此风险

### 一句话防御
**支付回调必须实现幂等性**：处理前检查订单状态，已支付的订单直接返回成功，不再重复发放商品。

### 快速行动清单
1. [ ] 立即行动项：检查支付回调接口，添加订单状态检查（今天可完成，免费）
2. [ ] 短期行动项：使用数据库事务确保状态更新和商品发放的原子性（本周可完成，免费）
3. [ ] 长期行动项：添加支付 ID 唯一索引，防止重复处理（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用支付平台的 webhook 签名验证

### 验证方法
- [ ] 完成一次支付
- [ ] 复制支付回调请求数据
- [ ] 多次发送相同请求
- [ ] 确认系统只处理一次，后续返回成功但不重复发放商品

---

## L2 小团队版（理解版）

### 场景还原
你的在线课程平台用户完成了一次 ¥999 的支付购买课程。攻击者使用抓包工具（如 Charles）捕获了支付成功的回调请求，然后多次重放这个请求。由于你的系统没有检查订单是否已处理，每次回调都给用户发放了课程访问权限。攻击者通过重放攻击，用一个订单 ID 获取了多次积分或服务。

另一种场景：用户支付成功后，因为网络延迟多次点击"完成支付"按钮，你的系统创建了多个订单，用户只支付了一个，但系统认为多个订单都支付成功了。

### 攻击路径（简化版）
1. **正常支付**：用户完成一次支付，收到支付成功的回调
2. **捕获请求**：攻击者使用抓包工具或浏览器开发者工具记录回调请求
3. **重放请求**：攻击者多次发送相同的回调请求
4. **重复获益**：系统每次都处理回调，用户多次获取商品或服务

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：支付回调必须幂等，同一个支付只能处理一次。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：未检查订单状态
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    
    # 验证支付
    payment = payment_gateway.verify(payment_id)
    
    # 查询订单
    order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
    
    # 直接发放商品（危险！每次调用都会发放）
    grant_product(order.user_id, order.product_id)
    
    # 更新订单状态
    db.execute("UPDATE orders SET status = 'paid' WHERE id = ?", order.id)
    
    return 'success'
```

2. **修复代码**：
```python
# ✅ 正确做法：实现幂等性
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    
    # 1. 验证签名
    if not payment_gateway.verify_signature(request):
        logger.warning(f"签名验证失败: payment_id={payment_id}")
        return '签名验证失败', 400
    
    # 2. 查询订单（使用数据库行锁）
    order = db.query("""
        SELECT id, user_id, product_id, amount, status
        FROM orders
        WHERE payment_id = ?
        FOR UPDATE  -- 加锁，防止并发
    """, payment_id)
    
    if not order:
        logger.warning(f"订单不存在: payment_id={payment_id}")
        return '订单不存在', 404
    
    # 3. 幂等性检查：订单已支付则直接返回成功
    if order.status == 'paid':
        logger.info(f"订单已处理（幂等）: order_id={order.id}")
        return 'success'  # 返回成功，但不重复处理
    
    # 4. 查询支付状态
    payment = payment_gateway.get_payment(payment_id)
    
    # 5. 验证支付成功
    if payment.status != 'success':
        logger.warning(f"支付未成功: payment_id={payment_id}, status={payment.status}")
        return '支付未成功', 400
    
    # 6. 验证金额
    if payment.amount != order.amount:
        logger.error(f"金额不一致: order={order.id}, expected={order.amount}, actual={payment.amount}")
        return '金额验证失败', 400
    
    # 7. 使用事务更新订单状态和发放商品
    with db.transaction():
        # 更新订单状态
        db.execute("""
            UPDATE orders
            SET status = 'paid', paid_at = NOW()
            WHERE id = ? AND status = 'pending'
        """, order.id)
        
        # 发放商品
        grant_product(order.user_id, order.product_id)
    
    logger.info(f"支付成功: order_id={order.id}, user_id={order.user_id}")
    return 'success'
```

3. **数据库优化**：
```sql
-- 添加唯一索引，防止同一个支付 ID 对应多个订单
ALTER TABLE orders ADD UNIQUE INDEX idx_payment_id (payment_id);

-- 添加状态索引，加快查询
ALTER TABLE orders ADD INDEX idx_status (status);
```

**局限性**：
- 需要数据库支持事务和行锁
- 需要修改现有代码

#### 方案B：使用分布式锁（中等成本）

**工具/服务**：Redis

**优势**：
- 防止分布式环境下的并发问题
- 性能更好

**配置示例**：
```python
import redis
from contextlib import contextmanager

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@contextmanager
def distributed_lock(lock_key, timeout=10):
    """
    分布式锁
    """
    lock = redis_client.lock(lock_key, timeout=timeout)
    acquired = lock.acquire(blocking=True, blocking_timeout=5)
    
    try:
        if acquired:
            yield True
        else:
            yield False
    finally:
        if acquired:
            lock.release()

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    
    # 使用分布式锁
    with distributed_lock(f"payment:lock:{payment_id}") as acquired:
        if not acquired:
            logger.warning(f"获取锁失败: payment_id={payment_id}")
            return '处理中', 429
        
        # 查询订单
        order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
        
        # 幂等性检查
        if order.status == 'paid':
            return 'success'
        
        # 处理支付...
        process_payment(order, payment_id)
        
        return 'success'
```

**成本**：Redis 云服务 $5-15/月

### 决策树
```
支付回调是否检查订单状态？
├── 否 → 立即添加状态检查（方案A）
└── 是 → 是否使用数据库事务？
    ├── 否 → 添加事务保证原子性（方案A）
    └── 是 → 是否有分布式环境？
        ├── 是 → 考虑使用分布式锁（方案B）
        └── 否 → 当前后端方案足够（方案A）
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify
from database import db
from payment_gateway import payment_gateway
import logging
from datetime import datetime

app = Flask(__name__)
logger = logging.getLogger(__name__)

class PaymentService:
    @staticmethod
    def process_payment_callback(payment_id, callback_data):
        """
        处理支付回调 - 幂等实现
        
        Returns:
            (success, message)
        """
        # 1. 验证签名
        if not payment_gateway.verify_signature(callback_data):
            logger.warning(f"签名验证失败: payment_id={payment_id}")
            return False, '签名验证失败'
        
        # 2. 使用数据库事务处理
        with db.transaction() as tx:
            # 查询订单并加锁
            order = tx.query("""
                SELECT id, user_id, product_id, amount, status, created_at
                FROM orders
                WHERE payment_id = ?
                FOR UPDATE
            """, payment_id)
            
            if not order:
                logger.warning(f"订单不存在: payment_id={payment_id}")
                return False, '订单不存在'
            
            # 幂等性检查：已支付直接返回成功
            if order.status == 'paid':
                logger.info(f"订单已处理（幂等）: order_id={order.id}")
                return True, 'success'
            
            # 订单状态异常
            if order.status not in ['pending', 'created']:
                logger.warning(f"订单状态异常: order_id={order.id}, status={order.status}")
                return False, '订单状态异常'
            
            # 3. 查询支付状态
            try:
                payment = payment_gateway.get_payment(payment_id)
            except Exception as e:
                logger.error(f"查询支付失败: payment_id={payment_id}, error={e}")
                return False, '查询支付失败'
            
            # 4. 验证支付成功
            if payment.status != 'success':
                logger.warning(f"支付未成功: payment_id={payment_id}, status={payment.status}")
                return False, '支付未成功'
            
            # 5. 验证金额
            if payment.amount != order.amount:
                logger.error(f"""
                    金额不一致告警:
                    order_id={order.id}
                    expected={order.amount}
                    actual={payment.amount}
                    user_id={order.user_id}
                """)
                send_security_alert('amount_mismatch', order, payment)
                return False, '金额验证失败'
            
            # 6. 更新订单状态（条件更新，防止并发）
            rows_updated = tx.execute("""
                UPDATE orders
                SET status = 'paid',
                    paid_at = ?,
                    payment_method = ?,
                    updated_at = ?
                WHERE id = ? AND status = 'pending'
            """, datetime.now(), payment.method, datetime.now(), order.id)
            
            if rows_updated == 0:
                # 并发情况下，其他进程可能已更新
                logger.info(f"订单状态已被更新: order_id={order.id}")
                return True, 'success'
            
            # 7. 发放商品（幂等）
            PaymentService.grant_product(tx, order.user_id, order.product_id)
            
            # 8. 记录成功日志
            logger.info(f"""
                支付成功:
                order_id={order.id}
                user_id={order.user_id}
                product_id={order.product_id}
                amount={order.amount}
                payment_method={payment.method}
            """)
            
            return True, 'success'
    
    @staticmethod
    def grant_product(tx, user_id, product_id):
        """
        发放商品 - 幂等实现
        """
        # 检查是否已发放
        existing = tx.query("""
            SELECT id FROM user_products
            WHERE user_id = ? AND product_id = ?
        """, user_id, product_id)
        
        if existing:
            logger.info(f"商品已发放（幂等）: user_id={user_id}, product_id={product_id}")
            return
        
        # 发放商品
        tx.execute("""
            INSERT INTO user_products (user_id, product_id, granted_at)
            VALUES (?, ?, ?)
        """, user_id, product_id, datetime.now())
        
        logger.info(f"商品发放成功: user_id={user_id}, product_id={product_id}")

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """
    支付回调接口 - 幂等实现
    """
    try:
        payment_id = request.form.get('payment_id')
        
        success, message = PaymentService.process_payment_callback(
            payment_id,
            request.form.to_dict()
        )
        
        if success:
            return message, 200
        else:
            return message, 400
            
    except Exception as e:
        logger.error(f"处理支付回调异常: {e}")
        return '系统错误', 500

@app.route('/api/payment/webhook', methods=['POST'])
def payment_webhook():
    """
    支付 Webhook - 幂等实现
    """
    try:
        # 解析 webhook 数据
        webhook_data = request.json
        event_type = webhook_data.get('type')
        
        if event_type != 'payment.success':
            return 'ignored', 200
        
        payment_id = webhook_data.get('data', {}).get('payment_id')
        
        success, message = PaymentService.process_payment_callback(
            payment_id,
            webhook_data
        )
        
        return message, 200 if success else 400
        
    except Exception as e:
        logger.error(f"处理 webhook 异常: {e}")
        return '系统错误', 500

def send_security_alert(alert_type, order, payment):
    """发送安全告警"""
    # 实现告警逻辑
    pass
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **幂等性保障**：
   - 数据库唯一索引
   - 分布式锁
   - 条件更新

2. **并发控制**：
   - 数据库行锁
   - 乐观锁
   - 分布式锁

3. **监控告警**：
   - 重复回调检测
   - 异常订单监控
   - 商品发放记录

4. **审计日志**：
   - 所有回调记录
   - 幂等性命中统计
   - 异常回调分析

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [幂等性设计模式](https://martinfowler.com/articles/patterns-of-distributed-systems/idempotent-receiver.html)
- [支付系统幂等性最佳实践](https://stripe.com/docs/webhooks/best-practices)
- [分布式锁实现](https://redis.io/topics/distlock)
