# 第三方支付风险 - 独立开发者版

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
攻击者伪造支付平台的回调通知，绕过支付验证，免费获取商品或服务，你的损失：商品/服务全额 + 信任丧失。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 支付回调未验证签名
- [ ] 仅依赖订单状态判断支付成功
- [ ] 未主动查询支付平台确认支付状态
- [ ] 支付回调接口无访问限制
→ 勾选≥1项，即需关注此风险

### 一句话防御
**支付回调必须验证签名**，并主动向支付平台查询支付状态，确保支付真实性后再发放商品。

### 快速行动清单
1. [ ] 立即行动项：检查支付回调是否验证签名（今天可完成，免费）
2. [ ] 短期行动项：添加签名验证和主动查询机制（本周可完成，免费）
3. [ ] 长期行动项：实现订单状态同步和异常告警（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用支付平台 Webhook 签名验证

### 验证方法
- [ ] 伪造支付回调请求（无签名或错误签名）
- [ ] 确认系统拒绝伪造请求
- [ ] 尝试重复提交相同回调
- [ ] 确认系统正确处理幂等性

---

## L2 小团队版（理解版）

### 场景还原
你开发了一个在线课程平台，用户购买课程后通过支付宝或微信支付完成付款。你的系统接收支付平台的回调通知，然后自动开通课程访问权限。攻击者发现你的回调接口没有验证签名，于是伪造了一个支付成功的回调请求，系统直接开通了课程权限，实际上用户并没有付款。由于你的回调接口是公开的，攻击者可以无限次伪造支付请求，免费获取所有付费课程。

### 攻击路径（简化版）
1. **发现漏洞**：攻击者测试支付回调接口，发现无需签名验证
2. **分析回调参数**：了解回调请求的参数格式
3. **伪造回调请求**：构造虚假的支付成功回调
4. **绕过验证**：系统接受伪造请求，开通权限
5. **重复攻击**：批量伪造回调，免费获取商品

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：支付回调必须验证签名，主动查询支付平台确认支付状态，实现幂等性处理。

**工具/服务**：Stripe / Paddle / 支付宝 / 微信支付

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：支付回调未验证签名
@app.route('/webhook/payment', methods=['POST'])
def payment_webhook():
    order_id = request.json.get('order_id')
    payment_status = request.json.get('status')
    
    # 未验证签名！任何人都可以伪造！
    if payment_status == 'success':
        # 直接更新订单状态
        db.execute("""
            UPDATE orders SET status = 'paid', paid_at = NOW()
            WHERE id = ?
        """, order_id)
        
        # 发放商品
        grant_product(order_id)
        
        return 'success'
    
    return 'failed'
```

2. **修复代码 - Stripe Webhook 签名验证**：
```python
import stripe
import hmac
import hashlib
from flask import request

# Stripe Webhook 签名验证
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Stripe Webhook 处理 - 签名验证
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        # 1. 验证签名（关键！）
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # 无效的 payload
        logger.error(f"Invalid payload: {e}")
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # 签名验证失败
        logger.error(f"Invalid signature: {e}")
        return 'Invalid signature', 400
    
    # 2. 处理事件
    event_type = event['type']
    
    if event_type == 'checkout.session.completed':
        # 支付成功
        session = event['data']['object']
        handle_payment_success(session)
    
    elif event_type == 'payment_intent.succeeded':
        # 支付意图成功
        payment_intent = event['data']['object']
        handle_payment_intent_succeeded(payment_intent)
    
    elif event_type == 'payment_intent.payment_failed':
        # 支付失败
        payment_intent = event['data']['object']
        handle_payment_failed(payment_intent)
    
    return 'success', 200

def handle_payment_success(session):
    """
    处理支付成功
    """
    # 从 metadata 获取订单 ID
    order_id = session.get('metadata', {}).get('order_id')
    payment_intent_id = session.get('payment_intent')
    
    if not order_id:
        logger.error(f"订单 ID 缺失: session={session['id']}")
        return
    
    # 3. 主动查询支付状态（双重验证）
    try:
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # 验证支付状态
        if payment_intent.status != 'succeeded':
            logger.error(f"""
                支付状态不一致:
                order_id={order_id}
                webhook_status=success
                actual_status={payment_intent.status}
            """)
            return
        
        # 验证金额
        order = db.query("SELECT amount, status FROM orders WHERE id = ?", order_id)
        
        if not order:
            logger.error(f"订单不存在: order_id={order_id}")
            return
        
        # 验证金额（单位：分）
        if payment_intent.amount != order.amount:
            logger.error(f"""
                金额不一致:
                order_id={order_id}
                expected={order.amount}
                actual={payment_intent.amount}
            """)
            return
        
        # 4. 幂等性检查
        if order.status == 'paid':
            logger.info(f"订单已处理: order_id={order_id}")
            return
        
        # 5. 更新订单状态（使用事务）
        with db.transaction():
            db.execute("""
                UPDATE orders
                SET status = 'paid',
                    payment_id = ?,
                    paid_at = NOW(),
                    updated_at = NOW()
                WHERE id = ? AND status = 'pending'
            """, payment_intent_id, order_id)
            
            # 6. 发放商品
            grant_product(order_id)
        
        logger.info(f"支付成功: order_id={order_id}, payment_intent={payment_intent_id}")
    
    except stripe.error.StripeError as e:
        logger.error(f"查询支付状态失败: {e}")
        return
```

3. **支付宝/微信支付回调验证**：
```python
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import base64

class AlipayService:
    """
    支付宝支付服务
    """
    
    @staticmethod
    def verify_sign(params, public_key):
        """
        验证支付宝签名
        """
        # 1. 获取签名
        sign = params.pop('sign', None)
        sign_type = params.pop('sign_type', None)
        
        if not sign:
            return False
        
        # 2. 构造待签名字符串
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params if v])
        
        # 3. 验证签名
        try:
            key = RSA.import_key(public_key)
            verifier = PKCS1_v1_5.new(key)
            
            # SHA256 with RSA
            h = SHA256.new(sign_string.encode('utf-8'))
            
            # Base64 解码签名
            signature = base64.b64decode(sign)
            
            return verifier.verify(h, signature)
        
        except Exception as e:
            logger.error(f"验证签名失败: {e}")
            return False
    
    @staticmethod
    def query_payment_status(out_trade_no):
        """
        主动查询支付状态
        """
        # 调用支付宝查询接口
        # alipay.trade.query
        
        result = alipay_client.api_alipay_trade_query(out_trade_no=out_trade_no)
        
        return result

@app.route('/webhook/alipay', methods=['POST'])
def alipay_webhook():
    """
    支付宝回调处理
    """
    # 1. 获取回调参数
    params = request.form.to_dict()
    
    # 2. 验证签名
    if not AlipayService.verify_sign(params, ALIPAY_PUBLIC_KEY):
        logger.error("支付宝签名验证失败")
        return 'failure'
    
    # 3. 验证支付状态
    trade_status = params.get('trade_status')
    
    if trade_status not in ['TRADE_SUCCESS', 'TRADE_FINISHED']:
        return 'failure'
    
    # 4. 获取订单 ID
    out_trade_no = params.get('out_trade_no')
    trade_no = params.get('trade_no')  # 支付宝交易号
    
    # 5. 主动查询支付状态（双重验证）
    query_result = AlipayService.query_payment_status(out_trade_no)
    
    if query_result.get('trade_status') != trade_status:
        logger.error(f"""
            支付状态不一致:
            order_id={out_trade_no}
            callback_status={trade_status}
            query_status={query_result.get('trade_status')}
        """)
        return 'failure'
    
    # 6. 验证金额
    total_amount = Decimal(params.get('total_amount'))
    order = db.query("SELECT amount, status FROM orders WHERE id = ?", out_trade_no)
    
    if abs(total_amount - Decimal(order.amount) / 100) > Decimal('0.01'):
        logger.error(f"""
            金额不一致:
            order_id={out_trade_no}
            expected={order.amount / 100}
            actual={total_amount}
        """)
        return 'failure'
    
    # 7. 幂等性检查
    if order.status == 'paid':
        return 'success'
    
    # 8. 更新订单状态
    with db.transaction():
        db.execute("""
            UPDATE orders
            SET status = 'paid',
                payment_id = ?,
                paid_at = NOW(),
                updated_at = NOW()
            WHERE id = ? AND status = 'pending'
        """, trade_no, out_trade_no)
        
        # 发放商品
        grant_product(out_trade_no)
    
    return 'success'

class WeChatPayService:
    """
    微信支付服务
    """
    
    @staticmethod
    def verify_sign(params, api_key):
        """
        验证微信支付签名
        """
        # 微信支付使用 HMAC-SHA256
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params if v and k != 'sign'])
        
        sign_string += f"&key={api_key}"
        
        calculated_sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest().upper()
        
        return calculated_sign == params.get('sign')
    
    @staticmethod
    def query_payment_status(out_trade_no):
        """
        主动查询支付状态
        """
        # 调用微信支付查询接口
        result = wechat_pay_client.query(out_trade_no=out_trade_no)
        
        return result

@app.route('/webhook/wechat', methods=['POST'])
def wechat_webhook():
    """
    微信支付回调处理
    """
    # 1. 解析 XML 数据
    xml_data = request.data
    params = parse_xml(xml_data)
    
    # 2. 验证签名
    if not WeChatPayService.verify_sign(params, WECHAT_API_KEY):
        logger.error("微信支付签名验证失败")
        return create_xml_response('FAIL', '签名验证失败')
    
    # 3. 验证支付状态
    result_code = params.get('result_code')
    
    if result_code != 'SUCCESS':
        return create_xml_response('FAIL', '支付失败')
    
    # 4. 获取订单信息
    out_trade_no = params.get('out_trade_no')
    transaction_id = params.get('transaction_id')
    
    # 5. 主动查询支付状态
    query_result = WeChatPayService.query_payment_status(out_trade_no)
    
    if query_result.get('trade_state') != 'SUCCESS':
        logger.error(f"""
            支付状态不一致:
            order_id={out_trade_no}
            callback_status=SUCCESS
            query_status={query_result.get('trade_state')}
        """)
        return create_xml_response('FAIL', '状态不一致')
    
    # 6. 验证金额
    total_fee = int(params.get('total_fee'))  # 单位：分
    order = db.query("SELECT amount, status FROM orders WHERE id = ?", out_trade_no)
    
    if total_fee != order.amount:
        logger.error(f"""
            金额不一致:
            order_id={out_trade_no}
            expected={order.amount}
            actual={total_fee}
        """)
        return create_xml_response('FAIL', '金额不一致')
    
    # 7. 幂等性检查
    if order.status == 'paid':
        return create_xml_response('SUCCESS', 'OK')
    
    # 8. 更新订单状态
    with db.transaction():
        db.execute("""
            UPDATE orders
            SET status = 'paid',
                payment_id = ?,
                paid_at = NOW(),
                updated_at = NOW()
            WHERE id = ? AND status = 'pending'
        """, transaction_id, out_trade_no)
        
        grant_product(out_trade_no)
    
    return create_xml_response('SUCCESS', 'OK')
```

4. **订单状态同步机制**：
```python
from apscheduler.schedulers.background import BackgroundScheduler

class PaymentSyncService:
    """
    支付状态同步服务
    """
    
    @staticmethod
    def sync_pending_orders():
        """
        同步待处理订单状态
        定期查询支付平台，确认订单支付状态
        """
        # 查询超过 5 分钟仍为 pending 状态的订单
        pending_orders = db.query_all("""
            SELECT id, payment_id, created_at
            FROM orders
            WHERE status = 'pending'
            AND created_at < DATE_SUB(NOW(), INTERVAL 5 MINUTE)
            AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            LIMIT 100
        """)
        
        for order in pending_orders:
            try:
                # 根据支付方式查询状态
                if order.payment_id.startswith('pi_'):
                    # Stripe
                    payment_intent = stripe.PaymentIntent.retrieve(order.payment_id)
                    
                    if payment_intent.status == 'succeeded':
                        PaymentSyncService.update_order_status(
                            order.id, order.payment_id, 'paid'
                        )
                    elif payment_intent.status == 'canceled':
                        PaymentSyncService.update_order_status(
                            order.id, order.payment_id, 'cancelled'
                        )
                
                elif order.payment_id:
                    # 支付宝/微信
                    # 查询逻辑...
                    pass
            
            except Exception as e:
                logger.error(f"同步订单状态失败: order_id={order.id}, error={e}")
    
    @staticmethod
    def update_order_status(order_id, payment_id, status):
        """
        更新订单状态
        """
        with db.transaction():
            db.execute("""
                UPDATE orders
                SET status = ?, updated_at = NOW()
                WHERE id = ? AND status = 'pending'
            """, status, order_id)
            
            if status == 'paid':
                grant_product(order_id)
        
        logger.info(f"订单状态同步: order_id={order_id}, status={status}")

# 定期同步任务
scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=5)
def sync_payment_status():
    """
    每 5 分钟同步一次支付状态
    """
    PaymentSyncService.sync_pending_orders()

scheduler.start()
```

**局限性**：
- 需要支付平台支持 Webhook 和查询接口
- 需要定期同步任务

#### 方案B：使用支付平台托管（推荐）

**工具/服务**：Stripe Checkout / Paddle

**优势**：
- 支付平台处理所有安全验证
- Webhook 签名验证内置
- 自动重试和状态同步

**成本**：Stripe 手续费 2.9% + $0.30/笔，Paddle 手续费 5% + $0.50/笔

### 决策树
```
支付回调是否验证签名？
├── 否 → 立即添加签名验证（方案A）
└── 是 → 是否主动查询支付状态？
    ├── 否 → 添加主动查询机制（方案A）
    └── 是 → 是否有订单状态同步？
        ├── 否 → 添加定期同步任务（方案A）
        └── 是 → 当前方案基本完善
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify
import stripe
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Webhook 处理基类
class WebhookHandler:
    """
    Webhook 处理基类
    """
    
    @staticmethod
    def verify_stripe_signature(payload, sig_header, secret):
        """
        验证 Stripe 签名
        """
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, secret)
            return event, None
        except ValueError:
            return None, 'Invalid payload'
        except stripe.error.SignatureVerificationError:
            return None, 'Invalid signature'
    
    @staticmethod
    def process_payment_success(order_id, payment_id, amount):
        """
        处理支付成功
        """
        # 查询订单
        order = db.query("""
            SELECT id, user_id, amount, status
            FROM orders
            WHERE id = ? FOR UPDATE
        """, order_id)
        
        if not order:
            logger.error(f"订单不存在: order_id={order_id}")
            return False
        
        # 幂等性检查
        if order.status == 'paid':
            logger.info(f"订单已处理: order_id={order_id}")
            return True
        
        # 验证金额
        if abs(amount - order.amount) > 0:
            logger.error(f"""
                金额不一致:
                order_id={order_id}
                expected={order.amount}
                actual={amount}
            """)
            return False
        
        # 更新订单状态
        db.execute("""
            UPDATE orders
            SET status = 'paid',
                payment_id = ?,
                paid_at = NOW(),
                updated_at = NOW()
            WHERE id = ? AND status = 'pending'
        """, payment_id, order_id)
        
        # 发放商品
        grant_product(order_id)
        
        logger.info(f"支付成功: order_id={order_id}")
        return True

# Stripe Webhook
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """
    Stripe Webhook 处理
    """
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # 验证签名
    event, error = WebhookHandler.verify_stripe_signature(
        payload, sig_header, webhook_secret
    )
    
    if error:
        logger.error(f"Stripe Webhook 错误: {error}")
        return error, 400
    
    # 处理事件
    event_type = event['type']
    
    if event_type == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session.get('metadata', {}).get('order_id')
        payment_intent_id = session.get('payment_intent')
        
        # 主动查询支付状态
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            WebhookHandler.process_payment_success(
                order_id,
                payment_intent_id,
                payment_intent.amount
            )
    
    elif event_type == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        order_id = payment_intent.get('metadata', {}).get('order_id')
        
        logger.warning(f"支付失败: order_id={order_id}")
    
    return 'success', 200

# 订单状态同步
scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=5)
def sync_orders():
    """
    每 5 分钟同步订单状态
    """
    pending_orders = db.query_all("""
        SELECT id, payment_id FROM orders
        WHERE status = 'pending'
        AND created_at < DATE_SUB(NOW(), INTERVAL 5 MINUTE)
        LIMIT 100
    """)
    
    for order in pending_orders:
        try:
            if order.payment_id and order.payment_id.startswith('pi_'):
                pi = stripe.PaymentIntent.retrieve(order.payment_id)
                
                if pi.status == 'succeeded':
                    WebhookHandler.process_payment_success(
                        order.id, order.payment_id, pi.amount
                    )
        except Exception as e:
            logger.error(f"同步失败: order_id={order.id}, error={e}")

scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **多重验证**：
   - Webhook 签名验证
   - 主动查询支付状态
   - 金额和时间校验

2. **状态同步**：
   - 实时同步
   - 定期对账
   - 异常告警

3. **幂等处理**：
   - 订单幂等性
   - 回调幂等性
   - 状态机管理

4. **监控告警**：
   - 支付异常告警
   - 状态不一致告警
   - 回调失败告警

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [Stripe Webhook 安全](https://stripe.com/docs/webhooks/signatures)
- [支付宝开放平台文档](https://opendocs.alipay.com/)
- [微信支付开发文档](https://pay.weixin.qq.com/wiki/doc/api/index.html)
