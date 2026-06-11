# 支付回调伪造 - 独立开发者版

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
攻击者伪造支付平台的成功回调请求，你的系统未验证签名直接处理，用户未实际支付就获得了商品，你的损失：商品全额价值。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 支付回调接口未验证签名
- [ ] 直接信任回调数据中的支付状态
- [ ] 未主动查询支付平台验证支付结果
- [ ] 回调接口使用 HTTP 而非 HTTPS
→ 勾选≥1项，即需关注此风险

### 一句话防御
**必须验证回调签名并主动查询支付状态**：使用支付平台提供的签名算法验证请求来源，同时主动调用支付平台 API 确认支付结果。

### 快速行动清单
1. [ ] 立即行动项：检查回调接口，确认是否验证签名（今天可完成，免费）
2. [ ] 短期行动项：添加签名验证逻辑（本周可完成，免费）
3. [ ] 长期行动项：实现支付状态主动查询作为二次验证（规划中，免费）

### 推荐工具
- 免费：支付平台提供的签名验证（如 Stripe Webhook Signatures）
- 低成本：使用支付平台 SDK 自动验证

### 验证方法
- [ ] 使用 curl 或 Postman 发送伪造的回调请求
- [ ] 确认系统拒绝未签名的请求
- [ ] 确认系统拒绝签名错误的请求
- [ ] 确认只有真实支付才能触发商品发放

---

## L2 小团队版（理解版）

### 场景还原
你的在线课程平台使用第三方支付网关处理支付。支付成功后，支付网关会向你的服务器发送回调通知。攻击者发现了你的回调接口 URL（`https://yoursite.com/api/payment/callback`），然后伪造了一个支付成功的回调请求：

```bash
curl -X POST https://yoursite.com/api/payment/callback \
  -d "payment_id=PAY123456" \
  -d "status=success" \
  -d "amount=99900"
```

你的系统没有验证这个请求是否真的来自支付网关，直接处理了这个"支付成功"的回调，给攻击者发放了课程访问权限。攻击者没有支付一分钱就获取了价值 ¥999 的课程。

更严重的是，攻击者可以批量构造请求，给任意用户发放任意商品，你的平台完全失控。

### 攻击路径（简化版）
1. **发现接口**：攻击者找到回调接口 URL（通过抓包、代码泄露或猜测）
2. **构造请求**：伪造支付成功的回调请求数据
3. **发送请求**：直接调用回调接口，绕过支付网关
4. **获取商品**：系统未验证签名，直接发放商品

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：验证回调签名 + 主动查询支付状态。

**工具/服务**：支付平台 SDK

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：未验证签名
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    status = request.form.get('status')
    amount = request.form.get('amount')
    
    # 直接信任回调数据！
    if status == 'success':
        # 发放商品
        order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
        grant_product(order.user_id, order.product_id)
        db.execute("UPDATE orders SET status = 'paid' WHERE payment_id = ?", payment_id)
    
    return 'success'
```

2. **修复代码 - 添加签名验证**：
```python
import hmac
import hashlib

# 支付平台配置
PAYMENT_SECRET = 'your_webhook_secret_key'  # 从支付平台获取

def verify_callback_signature(request):
    """
    验证回调签名
    """
    # 获取签名（不同平台字段名可能不同）
    signature = request.headers.get('X-Payment-Signature')
    
    if not signature:
        logger.warning("缺少签名")
        return False
    
    # 计算期望的签名
    payload = request.get_data()  # 原始请求体
    expected_signature = hmac.new(
        PAYMENT_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    # 比较签名（使用恒定时间比较，防止时序攻击）
    if not hmac.compare_digest(signature, expected_signature):
        logger.warning(f"签名验证失败: expected={expected_signature}, actual={signature}")
        return False
    
    return True

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    
    # 1. 验证签名（关键！）
    if not verify_callback_signature(request):
        logger.warning(f"签名验证失败: payment_id={payment_id}")
        return '签名验证失败', 400
    
    # 2. 查询订单
    order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
    
    if not order:
        logger.warning(f"订单不存在: payment_id={payment_id}")
        return '订单不存在', 404
    
    # 3. 幂等性检查
    if order.status == 'paid':
        logger.info(f"订单已处理: order_id={order.id}")
        return 'success'
    
    # 4. 主动查询支付状态（二次验证）
    try:
        payment = payment_gateway.get_payment(payment_id)
    except Exception as e:
        logger.error(f"查询支付失败: payment_id={payment_id}, error={e}")
        return '查询支付失败', 500
    
    # 5. 验证支付状态
    if payment.status != 'success':
        logger.warning(f"支付未成功: payment_id={payment_id}, status={payment.status}")
        return '支付未成功', 400
    
    # 6. 验证金额
    if payment.amount != order.amount:
        logger.error(f"金额不一致: order={order.id}, expected={order.amount}, actual={payment.amount}")
        return '金额验证失败', 400
    
    # 7. 更新订单状态并发放商品
    with db.transaction():
        db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
        grant_product(order.user_id, order.product_id)
    
    logger.info(f"支付成功: order_id={order.id}")
    return 'success'
```

3. **使用 Stripe Webhook 签名验证**：
```python
import stripe

# Stripe Webhook 签名密钥
STRIPE_WEBHOOK_SECRET = 'whsec_xxxxx'

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    # 1. 验证签名（Stripe SDK 自动处理）
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # 无效的 payload
        logger.error(f"Invalid payload: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # 无效的签名
        logger.error(f"Invalid signature: {e}")
        return 'Invalid signature', 400
    
    # 2. 处理事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        payment_intent_id = session.get('payment_intent')
        
        # 3. 主动查询 PaymentIntent 状态
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status != 'succeeded':
            logger.warning(f"PaymentIntent 未成功: {payment_intent_id}")
            return 'Payment not succeeded', 400
        
        # 4. 查询订单
        order = db.query("""
            SELECT * FROM orders WHERE payment_id = ?
        """, payment_intent_id)
        
        if not order:
            logger.warning(f"订单不存在: {payment_intent_id}")
            return 'Order not found', 404
        
        # 5. 幂等性检查
        if order.status == 'paid':
            return 'success', 200
        
        # 6. 更新订单并发放商品
        db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
        grant_product(order.user_id, order.product_id)
        
        logger.info(f"支付成功: order_id={order.id}")
    
    return 'success', 200
```

4. **双重验证模式（最安全）**：
```python
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """
    支付回调 - 双重验证模式
    """
    payment_id = request.form.get('payment_id')
    
    # 第一重验证：签名验证
    if not verify_callback_signature(request):
        logger.warning(f"签名验证失败: payment_id={payment_id}")
        return '签名验证失败', 400
    
    # 查询订单
    order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
    
    if not order:
        return '订单不存在', 404
    
    # 幂等性检查
    if order.status == 'paid':
        return 'success'
    
    # 第二重验证：主动查询支付平台
    try:
        # 调用支付平台 API 查询支付状态
        payment = payment_gateway.get_payment(payment_id)
        
        # 验证支付状态
        if payment.status != 'success':
            return '支付未成功', 400
        
        # 验证金额
        if payment.amount != order.amount:
            send_security_alert('amount_mismatch', order, payment)
            return '金额验证失败', 400
        
    except Exception as e:
        logger.error(f"查询支付平台失败: {e}")
        # 如果查询失败，不要发放商品
        return '验证失败', 500
    
    # 更新订单状态
    db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
    grant_product(order.user_id, order.product_id)
    
    return 'success'
```

**局限性**：
- 需要支付平台支持签名验证
- 需要额外的 API 调用（主动查询）

#### 方案B：使用 IP 白名单（中等安全性）

**工具/服务**：无

**优势**：
- 简单实现
- 不需要修改签名验证逻辑

**配置步骤**：
```python
# 支付平台 IP 白名单
PAYMENT_IPS = {
    '192.168.1.1',
    '192.168.1.2',
    # 从支付平台文档获取完整 IP 列表
}

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    # 1. 验证 IP 白名单
    client_ip = request.remote_addr
    
    if client_ip not in PAYMENT_IPS:
        logger.warning(f"非法 IP 访问回调接口: {client_ip}")
        return 'Forbidden', 403
    
    # 2. 后续处理...
    # 注意：仅靠 IP 白名单不够安全，仍需签名验证
```

**成本**：免费

**注意**：IP 白名单可以增加一层保护，但不能替代签名验证。攻击者可能伪造 IP 或找到其他绕过方法。

### 决策树
```
回调接口是否验证签名？
├── 否 → 立即添加签名验证（方案A）
└── 是 → 是否主动查询支付状态？
    ├── 否 → 添加主动查询作为二次验证（方案A）
    └── 是 → 是否使用 HTTPS？
        ├── 否 → 强制使用 HTTPS
        └── 是 → 当前方案基本完善
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify
from database import db
from payment_gateway import payment_gateway
import logging
import hmac
import hashlib
from datetime import datetime

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Webhook 签名密钥（从支付平台获取）
WEBHOOK_SECRET = 'your_webhook_secret_here'

class WebhookSecurity:
    @staticmethod
    def verify_signature(payload, signature, secret=WEBHOOK_SECRET):
        """
        验证 Webhook 签名
        
        Args:
            payload: 原始请求体（bytes）
            signature: 请求头中的签名
            secret: Webhook 密钥
        
        Returns:
            bool: 签名是否有效
        """
        if not signature:
            logger.warning("缺少签名头")
            return False
        
        # 计算期望签名
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # 使用恒定时间比较（防止时序攻击）
        try:
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"签名比较异常: {e}")
            return False
    
    @staticmethod
    def verify_timestamp(timestamp_str, max_age_seconds=300):
        """
        验证时间戳（防重放攻击）
        
        Args:
            timestamp_str: 时间戳字符串
            max_age_seconds: 最大允许时间差（秒）
        
        Returns:
            bool: 时间戳是否有效
        """
        try:
            timestamp = int(timestamp_str)
            current_time = int(datetime.now().timestamp())
            
            # 检查时间差
            if abs(current_time - timestamp) > max_age_seconds:
                logger.warning(f"时间戳过期: timestamp={timestamp}, current={current_time}")
                return False
            
            return True
            
        except ValueError:
            logger.warning(f"无效的时间戳: {timestamp_str}")
            return False
    
    @staticmethod
    def verify_ip_whitelist(client_ip, whitelist):
        """
        验证 IP 白名单
        """
        return client_ip in whitelist

class PaymentCallbackService:
    @staticmethod
    def process_callback(callback_data, raw_payload, signature):
        """
        处理支付回调 - 安全版本
        
        Args:
            callback_data: 解析后的回调数据
            raw_payload: 原始请求体
            signature: 签名
        
        Returns:
            (success, message)
        """
        payment_id = callback_data.get('payment_id')
        
        # 1. 验证签名（第一重验证）
        if not WebhookSecurity.verify_signature(raw_payload, signature):
            logger.warning(f"签名验证失败: payment_id={payment_id}")
            return False, '签名验证失败'
        
        # 2. 验证时间戳（防重放）
        timestamp = callback_data.get('timestamp')
        if timestamp and not WebhookSecurity.verify_timestamp(timestamp):
            return False, '请求已过期'
        
        # 3. 查询订单
        order = db.query("""
            SELECT id, user_id, product_id, amount, currency, status
            FROM orders
            WHERE payment_id = ?
            FOR UPDATE
        """, payment_id)
        
        if not order:
            logger.warning(f"订单不存在: payment_id={payment_id}")
            return False, '订单不存在'
        
        # 4. 幂等性检查
        if order.status == 'paid':
            logger.info(f"订单已处理（幂等）: order_id={order.id}")
            return True, 'success'
        
        # 5. 主动查询支付状态（第二重验证）
        try:
            payment = payment_gateway.get_payment(payment_id)
        except Exception as e:
            logger.error(f"查询支付失败: payment_id={payment_id}, error={e}")
            # 查询失败不应发放商品
            return False, '验证失败'
        
        # 6. 验证支付状态
        if payment.status != 'success':
            logger.warning(f"支付未成功: payment_id={payment_id}, status={payment.status}")
            return False, '支付未成功'
        
        # 7. 验证金额
        if payment.amount != order.amount:
            logger.error(f"""
                金额不一致:
                order_id={order.id}
                expected={order.amount}
                actual={payment.amount}
            """)
            send_security_alert('amount_mismatch', order, payment)
            return False, '金额验证失败'
        
        # 8. 验证货币
        if payment.currency != order.currency:
            logger.error(f"""
                货币不一致:
                order_id={order.id}
                expected={order.currency}
                actual={payment.currency}
            """)
            send_security_alert('currency_mismatch', order, payment)
            return False, '货币验证失败'
        
        # 9. 更新订单状态并发放商品（事务）
        with db.transaction():
            rows = db.execute("""
                UPDATE orders
                SET status = 'paid', paid_at = NOW()
                WHERE id = ? AND status = 'pending'
            """, order.id)
            
            if rows == 0:
                # 并发情况，其他进程已处理
                return True, 'success'
            
            # 发放商品
            grant_product(order.user_id, order.product_id)
        
        # 10. 记录成功日志
        logger.info(f"""
            支付成功:
            order_id={order.id}
            user_id={order.user_id}
            product_id={order.product_id}
            amount={order.amount}
            currency={order.currency}
        """)
        
        return True, 'success'

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """
    支付回调接口 - 安全版本
    """
    try:
        # 获取原始请求体
        raw_payload = request.get_data()
        
        # 获取签名
        signature = request.headers.get('X-Payment-Signature')
        
        # 解析回调数据
        callback_data = request.form.to_dict()
        
        # 处理回调
        success, message = PaymentCallbackService.process_callback(
            callback_data,
            raw_payload,
            signature
        )
        
        if success:
            return message, 200
        else:
            return message, 400
            
    except Exception as e:
        logger.error(f"处理回调异常: {e}")
        return '系统错误', 500

@app.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """
    Stripe Webhook 接口
    """
    import stripe
    
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    # 验证签名
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400
    
    # 处理事件
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_intent_id = session.get('payment_intent')
        
        # 主动查询支付状态
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if payment_intent.status != 'succeeded':
                return 'Payment not succeeded', 400
            
            # 查询订单并更新
            order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_intent_id)
            
            if order and order.status != 'paid':
                db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
                grant_product(order.user_id, order.product_id)
            
        except Exception as e:
            logger.error(f"处理 Stripe webhook 失败: {e}")
            return 'Error', 500
    
    return 'success', 200

@app.route('/api/payment/verify', methods=['POST'])
def manual_verify_payment():
    """
    手动验证支付状态（用于用户主动查询）
    """
    order_id = request.json.get('order_id')
    user_id = current_user.id
    
    # 查询订单
    order = db.query("""
        SELECT id, user_id, payment_id, status
        FROM orders
        WHERE id = ? AND user_id = ?
    """, order_id, user_id)
    
    if not order:
        return {'error': '订单不存在'}, 404
    
    if order.status == 'paid':
        return {'status': 'paid', 'message': '订单已支付'}
    
    # 主动查询支付状态
    if order.payment_id:
        try:
            payment = payment_gateway.get_payment(order.payment_id)
            
            if payment.status == 'success' and order.status != 'paid':
                # 更新订单状态
                db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
                grant_product(order.user_id, order.product_id)
                
                return {'status': 'paid', 'message': '支付已确认'}
            
        except Exception as e:
            logger.error(f"查询支付失败: {e}")
    
    return {'status': order.status}

def send_security_alert(alert_type, order, payment):
    """发送安全告警"""
    # 实现告警逻辑
    pass

def grant_product(user_id, product_id):
    """发放商品"""
    db.execute("""
        INSERT INTO user_products (user_id, product_id, granted_at)
        VALUES (?, ?, NOW())
    """, user_id, product_id)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **签名验证**：
   - HMAC 签名验证
   - 时间戳防重放
   - IP 白名单

2. **双重验证**：
   - 签名验证（第一重）
   - 主动查询支付平台（第二重）

3. **监控告警**：
   - 签名验证失败告警
   - 异常回调来源监控
   - 支付状态不一致告警

4. **日志审计**：
   - 所有回调请求记录
   - 签名验证失败记录
   - 支付状态查询记录

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [Stripe Webhook 签名验证](https://stripe.com/docs/webhooks/signatures)
- [支付回调安全最佳实践](https://stripe.com/docs/webhooks/best-practices)
- [HMAC 签名验证](https://en.wikipedia.org/wiki/HMAC)
- [时序攻击防御](https://en.wikipedia.org/wiki/Timing_attack)
