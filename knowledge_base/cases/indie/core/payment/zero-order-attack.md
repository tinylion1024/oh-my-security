# 零元订单攻击 - 独立开发者版

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
用户修改订单金额为 0 或负数，你的系统未做验证，用户免费获取了付费课程或商品，你的损失：全额商品价值。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 后端未验证订单金额是否 > 0
- [ ] 允许用户自定义订单金额（如打赏、自定义价格）
- [ ] 促销系统允许 100% 折扣且无二次验证
- [ ] 支付网关未验证最低金额限制
→ 勾选≥1项，即需关注此风险

### 一句话防御
**所有订单金额必须强制校验：必须为正数且大于等于最低支付金额**，在创建订单和支付回调两处都要验证。

### 快速行动清单
1. [ ] 立即行动项：检查所有创建订单接口，添加金额验证 `amount > 0`（今天可完成，免费）
2. [ ] 短期行动项：设置最低支付金额限制（如 0.01 元）（本周可完成，免费）
3. [ ] 长期行动项：添加异常订单监控，金额为 0 的订单触发告警（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：Stripe/Paddle 支付平台 - 内置最低金额限制

### 验证方法
- [ ] 在 API 请求中将金额修改为 0 或 -1
- [ ] 提交创建订单请求
- [ ] 确认系统拒绝该请求并返回错误

---

## L2 小团队版（理解版）

### 场景还原
你的在线课程平台支持"自定义价格"功能，用户可以自己决定支付金额（类似打赏）。攻击者发现你的后端没有验证金额下限，直接调用 API 创建了一个金额为 `0` 的订单，系统成功创建了订单并标记为"已支付"（因为无需实际支付）。攻击者免费获取了课程访问权限。

更隐蔽的是，攻击者发现你的折扣系统存在漏洞，可以叠加多个折扣码最终让订单金额变为负数，系统反而"欠"攻击者积分。

### 攻击路径（简化版）
1. **发现漏洞**：攻击者测试 API，发现金额为 0 的订单可以创建成功
2. **构造请求**：直接调用创建订单接口，将 `amount` 设为 0 或负数
3. **绕过支付**：金额为 0 的订单可能被系统自动标记为"已支付"
4. **获取商品**：攻击者免费获取商品或服务

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：订单金额必须为正数，且不能低于平台最低支付金额。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：未验证金额
@app.route('/api/create-order', methods=['POST'])
def create_order():
    product_id = request.json.get('product_id')
    amount = request.json.get('amount', 0)  # 用户可自定义金额
    
    order = Order.create(product_id=product_id, amount=amount)
    
    # 金额为 0 时自动标记为已支付
    if amount == 0:
        order.status = 'paid'
        grant_product(order.user_id, product_id)
    
    return {'order_id': order.id}
```

2. **修复代码**：
```python
# ✅ 正确做法：强制验证金额
MIN_PAYMENT_AMOUNT = 100  # 最低支付金额：1元（单位：分）

@app.route('/api/create-order', methods=['POST'])
def create_order():
    product_id = request.json.get('product_id')
    amount = request.json.get('amount', 0)
    user_id = current_user.id
    
    # 1. 验证金额为正数
    if amount <= 0:
        return {'error': '订单金额必须大于 0'}, 400
    
    # 2. 验证金额不低于最低限额
    if amount < MIN_PAYMENT_AMOUNT:
        return {'error': f'订单金额不能低于 {MIN_PAYMENT_AMOUNT/100} 元'}, 400
    
    # 3. 验证商品存在且价格合理
    product = db.query("SELECT price, min_price FROM products WHERE id = ?", product_id)
    if not product:
        return {'error': '商品不存在'}, 404
    
    # 如果是固定价格商品，验证金额匹配
    if not product.allow_custom_price:
        if amount != product.price:
            return {'error': '金额不正确'}, 400
    
    # 如果是自定义价格商品，验证在合理范围内
    if product.allow_custom_price and amount < product.min_price:
        return {'error': f'最低支付金额为 {product.min_price/100} 元'}, 400
    
    # 4. 创建订单
    order_id = db.execute("""
        INSERT INTO orders (user_id, product_id, amount, status, created_at)
        VALUES (?, ?, ?, 'pending', NOW())
        RETURNING id
    """, user_id, product_id, amount)
    
    # 5. 记录安全日志
    logger.info(f"创建订单: order_id={order_id}, amount={amount}, user_id={user_id}")
    
    return {'order_id': order_id}
```

3. **支付回调验证**：
```python
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    
    # 验证支付
    payment = payment_gateway.verify(payment_id)
    
    # 查询订单
    order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
    
    # 关键验证：再次检查金额
    if payment.amount <= 0:
        logger.error(f"支付金额异常: payment_id={payment_id}, amount={payment.amount}")
        return '金额异常', 400
    
    if payment.amount < MIN_PAYMENT_AMOUNT:
        logger.error(f"支付金额低于最低限额: payment_id={payment_id}, amount={payment.amount}")
        return '金额异常', 400
    
    # 验证金额一致性
    if payment.amount != order.amount:
        send_security_alert(order, payment)
        return '金额验证失败', 400
    
    # 更新订单状态
    db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
    grant_product(order.user_id, order.product_id)
    
    return 'success'
```

**局限性**：
- 需要修改现有代码
- 需要确保所有创建订单的入口都添加验证

#### 方案B：使用支付平台保护（低成本）

**工具/服务**：Stripe / Paddle

**优势**：
- 支付平台有最低金额限制（如 Stripe 最低 $0.50）
- 创建支付时自动验证金额有效性

**配置示例**：
```python
import stripe

MIN_PAYMENT_AMOUNT = 50  # Stripe 最低 $0.50

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    amount = request.json.get('amount')
    
    # Stripe 会自动拒绝低于最低金额的支付
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': amount,  # Stripe 会验证
                    'product_data': {
                        'name': 'Product Name',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yourdomain.com/success',
            cancel_url='https://yourdomain.com/cancel',
        )
        return {'session_id': session.id}
    except stripe.error.InvalidRequestError as e:
        return {'error': str(e)}, 400
```

**成本**：Stripe 手续费 2.9% + $0.30/笔

### 决策树
```
订单创建时是否验证金额 > 0？
├── 否 → 立即添加验证（方案A）
└── 是 → 是否验证最低金额？
    ├── 否 → 添加最低金额验证（方案A）
    └── 是 → 是否使用第三方支付平台？
        ├── 是 → 确认平台有最低金额限制（方案B）
        └── 否 → 在支付回调中再次验证金额（方案A）
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify, current_user
from database import db
from payment_gateway import payment_gateway
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 平台配置
MIN_PAYMENT_AMOUNT = 100  # 最低支付金额：1元（单位：分）
MAX_PAYMENT_AMOUNT = 10000000  # 最高支付金额：10万元（防异常）

class OrderService:
    @staticmethod
    def validate_amount(amount, product=None):
        """
        验证订单金额的有效性
        
        Args:
            amount: 订单金额（单位：分）
            product: 商品信息（可选）
        
        Returns:
            (is_valid, error_message)
        """
        # 1. 类型检查
        if not isinstance(amount, (int, float)) or amount != int(amount):
            return False, '金额必须为整数'
        
        amount = int(amount)
        
        # 2. 正数检查
        if amount <= 0:
            logger.warning(f"零元或负数订单尝试: amount={amount}")
            return False, '订单金额必须大于 0'
        
        # 3. 最低金额检查
        if amount < MIN_PAYMENT_AMOUNT:
            return False, f'订单金额不能低于 {MIN_PAYMENT_AMOUNT/100} 元'
        
        # 4. 最高金额检查（防异常）
        if amount > MAX_PAYMENT_AMOUNT:
            return False, f'订单金额不能超过 {MAX_PAYMENT_AMOUNT/100} 元'
        
        # 5. 商品价格检查（如果提供了商品信息）
        if product:
            if not product.get('allow_custom_price'):
                # 固定价格商品
                if amount != product['price']:
                    return False, '订单金额不正确'
            else:
                # 自定义价格商品
                min_price = product.get('min_price', MIN_PAYMENT_AMOUNT)
                max_price = product.get('max_price', MAX_PAYMENT_AMOUNT)
                
                if amount < min_price:
                    return False, f'最低支付金额为 {min_price/100} 元'
                if amount > max_price:
                    return False, f'最高支付金额为 {max_price/100} 元'
        
        return True, None
    
    @staticmethod
    def create_order(user_id, product_id, amount):
        """
        创建订单 - 安全版本
        """
        # 1. 获取商品信息
        product = db.query("""
            SELECT id, name, price, allow_custom_price, min_price, max_price
            FROM products
            WHERE id = ? AND status = 'active'
        """, product_id)
        
        if not product:
            return None, '商品不存在或已下架'
        
        # 2. 验证金额
        is_valid, error = OrderService.validate_amount(amount, product)
        if not is_valid:
            return None, error
        
        # 3. 创建订单
        order_id = db.execute("""
            INSERT INTO orders (user_id, product_id, amount, status, created_at)
            VALUES (?, ?, ?, 'pending', NOW())
            RETURNING id
        """, user_id, product_id, amount)
        
        # 4. 记录审计日志
        logger.info(f"""
            创建订单成功:
            order_id={order_id}
            user_id={user_id}
            product_id={product_id}
            amount={amount}
        """)
        
        return order_id, None

@app.route('/api/create-order', methods=['POST'])
def create_order():
    """
    创建订单接口
    """
    try:
        data = request.json
        product_id = data.get('product_id')
        amount = data.get('amount')
        user_id = current_user.id
        
        # 创建订单
        order_id, error = OrderService.create_order(user_id, product_id, amount)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'order_id': order_id,
            'message': '订单创建成功'
        })
        
    except Exception as e:
        logger.error(f"创建订单异常: {e}")
        return jsonify({'error': '系统错误'}), 500

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """
    支付回调 - 安全版本
    """
    payment_id = request.form.get('payment_id')
    
    # 1. 验证签名
    if not payment_gateway.verify_signature(request):
        logger.warning(f"支付回调签名验证失败: payment_id={payment_id}")
        return '签名验证失败', 400
    
    # 2. 查询支付信息
    payment = payment_gateway.get_payment(payment_id)
    
    # 3. 再次验证金额（关键！）
    is_valid, error = OrderService.validate_amount(payment.amount)
    if not is_valid:
        logger.error(f"支付金额异常: payment_id={payment_id}, amount={payment.amount}, error={error}")
        send_security_alert('payment_amount_invalid', payment)
        return '金额异常', 400
    
    # 4. 查询订单
    order = db.query("""
        SELECT id, user_id, product_id, amount, status
        FROM orders
        WHERE payment_id = ?
    """, payment_id)
    
    if not order:
        logger.warning(f"订单不存在: payment_id={payment_id}")
        return '订单不存在', 404
    
    # 5. 验证金额一致性
    if payment.amount != order.amount:
        logger.error(f"""
            金额不一致:
            order_id={order.id}
            expected={order.amount}
            actual={payment.amount}
        """)
        send_security_alert('amount_mismatch', order, payment)
        return '金额验证失败', 400
    
    # 6. 检查订单状态
    if order.status == 'paid':
        logger.info(f"订单已处理: order_id={order.id}")
        return 'success'
    
    # 7. 更新订单状态
    db.execute("""
        UPDATE orders
        SET status = 'paid', paid_at = NOW()
        WHERE id = ?
    """, order.id)
    
    # 8. 发放商品
    grant_product(order.user_id, order.product_id)
    
    logger.info(f"支付成功: order_id={order.id}")
    return 'success'

def send_security_alert(alert_type, *args):
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

1. **金额验证**：
   - 创建订单时验证
   - 支付发起时验证
   - 支付回调时验证
   - 订单完成后验证

2. **异常监控**：
   - 零元订单实时告警
   - 异常金额订单拦截
   - 批量零元订单检测

3. **业务规则**：
   - 最低支付金额配置
   - 最高支付金额限制
   - 自定义价格范围限制

4. **审计日志**：
   - 所有订单创建记录
   - 金额验证失败记录
   - 异常订单分析报告

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [支付安全最佳实践](https://stripe.com/docs/security)
- [OWASP 支付安全指南](https://owasp.org/www-community/vulnerabilities/Financial_Fraud)
- [订单金额验证最佳实践](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)
