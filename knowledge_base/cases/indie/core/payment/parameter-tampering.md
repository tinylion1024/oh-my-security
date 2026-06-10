# 参数篡改攻击 - 独立开发者版

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
你的在线课程平台使用前端传递价格到支付网关，用户用浏览器开发者工具把 ¥999 改成 ¥0.01，成功"购买"了课程，你的损失：¥999。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 前端直接传递价格、金额、折扣等敏感参数到后端
- [ ] 支付金额由前端计算或展示
- [ ] 订单金额未在后端二次验证
- [ ] 使用第三方支付网关但未验证回调金额
→ 勾选≥1项，即需关注此风险

### 一句话防御
**永远不要信任前端传来的价格**，所有金额必须从后端数据库或配置中读取，支付回调必须验证金额一致性。

### 快速行动清单
1. [ ] 立即行动项：检查所有支付相关接口，找到直接使用前端价格参数的代码（今天可完成，免费）
2. [ ] 短期行动项：修改代码，改为从数据库读取价格（本周可完成，免费）
3. [ ] 长期行动项：添加支付回调金额验证逻辑（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：Stripe/Paddle 支付平台 - 内置价格保护机制

### 验证方法
- [ ] 在浏览器开发者工具中修改价格参数
- [ ] 提交支付请求
- [ ] 确认支付金额仍然是原价，未被篡改

---

## L2 小团队版（理解版）

### 场景还原
你的在线课程平台"Python高级编程"课程定价 ¥999。用户在购买页面打开浏览器开发者工具（F12），找到隐藏的价格字段 `<input type="hidden" name="price" value="999">`，将其修改为 `0.01`，然后点击购买按钮。你的后端直接使用了这个价格参数调用支付网关，用户成功以 ¥0.01 的价格购买了价值 ¥999 的课程。

更糟糕的是，用户在社区分享了这种"漏洞"，引发大规模薅羊毛，你的平台损失数万元。

### 攻击路径（简化版）
1. **打开开发者工具**：用户在购买页面按 F12，找到价格相关的表单字段或 API 请求参数
2. **修改价格参数**：将价格从 ¥999 修改为 ¥0.01（或任意低价）
3. **提交请求**：后端未验证价格来源，直接使用前端传来的价格调用支付网关
4. **完成支付**：支付网关收到 ¥0.01 的支付请求，用户成功"购买"

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：价格永远从后端数据库读取，不信任前端传来的任何金额。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：信任前端价格
@app.route('/pay')
def pay():
    product_id = request.form['product_id']
    price = request.form['price']  # 直接使用前端传来的价格
    user_id = current_user.id
    return redirect(payment_gateway.create_payment(price, user_id, product_id))
```

2. **修复代码**：
```python
# ✅ 正确做法：后端从数据库取价格
@app.route('/pay')
def pay():
    product_id = request.form['product_id']
    user_id = current_user.id
    
    # 从数据库读取真实价格
    product = db.query("SELECT price FROM products WHERE id = ?", product_id)
    if not product:
        return "商品不存在", 404
    
    price = product.price  # 使用数据库中的价格
    
    # 创建支付订单
    payment = payment_gateway.create_payment(
        amount=price,
        user_id=user_id,
        product_id=product_id
    )
    
    # 记录订单（包含金额，用于回调验证）
    db.execute("""
        INSERT INTO orders (user_id, product_id, amount, status, payment_id)
        VALUES (?, ?, ?, 'pending', ?)
    """, user_id, product_id, price, payment.id)
    
    return redirect(payment.url)
```

3. **验证支付回调**：
```python
@app.route('/payment/callback')
def payment_callback():
    payment_id = request.form['payment_id']
    payment = payment_gateway.verify(payment_id)
    
    # 从数据库读取订单
    order = db.query("SELECT * FROM orders WHERE payment_id = ?", payment_id)
    
    # 验证金额一致性
    if payment.amount != order.amount:
        log_security_alert(f"金额不一致: 订单{order.id}, 期望{order.amount}, 实际{payment.amount}")
        return "支付验证失败", 400
    
    # 更新订单状态
    db.execute("UPDATE orders SET status = 'paid' WHERE id = ?", order.id)
    return "支付成功"
```

**局限性**：
- 需要修改现有代码
- 需要确保数据库中的价格数据准确

#### 方案B：使用支付平台内置保护（低成本）

**工具/服务**：Stripe / Paddle / LemonSqueezy

**优势**：
- 支付平台内置价格保护机制
- 创建产品时设置价格，支付时只能使用产品ID
- 无法通过参数篡改价格

**配置步骤**：

```python
# 使用 Stripe Checkout
import stripe

@app.route('/pay')
def pay():
    product_id = request.form['product_id']
    
    # 创建 Stripe Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_xxxxx',  # Stripe 中的价格 ID，无法篡改
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://yourdomain.com/success',
        cancel_url='https://yourdomain.com/cancel',
    )
    
    return redirect(session.url)
```

**成本**：Stripe 手续费 2.9% + $0.30/笔

### 决策树
```
你的产品是否使用第三方支付平台？
├── 是（Stripe/Paddle等）→ 使用方案B（平台内置保护）
└── 否（自建支付）→ 使用方案A（后端价格验证）
```

### 代码示例（完整版）

```python
from flask import Flask, request, redirect, current_user
from database import db
from payment_gateway import payment_gateway
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 商品价格配置（或从数据库读取）
PRODUCT_PRICES = {
    'python-advanced': 99900,  # 单位：分
    'javascript-basics': 19900,
}

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    """
    创建支付订单 - 安全版本
    """
    product_id = request.json.get('product_id')
    user_id = current_user.id
    
    # 1. 验证商品存在
    if product_id not in PRODUCT_PRICES:
        return {'error': '商品不存在'}, 404
    
    # 2. 从服务端获取价格（不信任前端）
    price = PRODUCT_PRICES[product_id]
    
    # 3. 创建支付订单
    try:
        payment = payment_gateway.create_payment(
            amount=price,
            currency='cny',
            metadata={
                'user_id': user_id,
                'product_id': product_id,
            }
        )
        
        # 4. 记录订单到数据库
        order_id = db.execute("""
            INSERT INTO orders (user_id, product_id, amount, status, payment_id, created_at)
            VALUES (?, ?, ?, 'pending', ?, NOW())
            RETURNING id
        """, user_id, product_id, price, payment.id)
        
        logger.info(f"创建订单成功: order_id={order_id}, amount={price}")
        
        return {
            'payment_url': payment.url,
            'order_id': order_id,
        }
        
    except Exception as e:
        logger.error(f"创建支付失败: {e}")
        return {'error': '创建支付失败'}, 500

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """
    支付回调 - 安全版本
    """
    payment_id = request.form.get('payment_id')
    
    # 1. 验证支付签名（防止伪造回调）
    if not payment_gateway.verify_signature(request):
        logger.warning(f"支付回调签名验证失败: payment_id={payment_id}")
        return '签名验证失败', 400
    
    # 2. 查询支付状态
    payment = payment_gateway.get_payment(payment_id)
    if payment.status != 'success':
        return '支付未成功', 400
    
    # 3. 查询订单
    order = db.query("""
        SELECT id, user_id, product_id, amount, status
        FROM orders
        WHERE payment_id = ?
    """, payment_id)
    
    if not order:
        logger.warning(f"订单不存在: payment_id={payment_id}")
        return '订单不存在', 404
    
    # 4. 验证金额一致性（关键！）
    if payment.amount != order.amount:
        logger.error(f"""
            金额不一致告警！
            订单ID: {order.id}
            期望金额: {order.amount}
            实际金额: {payment.amount}
            用户ID: {order.user_id}
        """)
        # 发送告警通知
        send_security_alert(order, payment)
        return '金额验证失败', 400
    
    # 5. 检查订单状态（防止重复处理）
    if order.status == 'paid':
        logger.info(f"订单已处理: order_id={order.id}")
        return 'success'
    
    # 6. 更新订单状态
    db.execute("""
        UPDATE orders
        SET status = 'paid', paid_at = NOW()
        WHERE id = ?
    """, order.id)
    
    # 7. 发放商品
    grant_product(order.user_id, order.product_id)
    
    logger.info(f"支付成功: order_id={order.id}, user_id={order.user_id}")
    return 'success'

def send_security_alert(order, payment):
    """发送安全告警"""
    # 实现告警逻辑：邮件、Slack、短信等
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

1. **前端防护**：
   - 价格加密传输
   - 请求签名验证
   - 时间戳防重放

2. **后端防护**：
   - 价格从数据库读取
   - 订单金额验证
   - 支付回调金额验证
   - 异常订单监控

3. **业务防护**：
   - 价格变更审计日志
   - 异常订单自动风控
   - 大额订单人工审核

4. **监控告警**：
   - 金额不一致实时告警
   - 异常订单率监控
   - 价格篡改尝试监控

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [OWASP Top 10 - A01:2021 Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [支付安全最佳实践](https://stripe.com/docs/security)
- [价格篡改防护指南](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)
