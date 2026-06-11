# 货币篡改攻击 - 独立开发者版

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
用户将支付货币从美元改为日元或其他低汇率货币，用低价购买高价商品，你的损失：汇率差额（可能损失 90% 以上）。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 前端传递货币类型到后端
- [ ] 支持多种货币但未固定用户区域
- [ ] 商品价格根据货币动态计算
- [ ] 未验证货币与用户地区匹配
→ 勾选≥1项，即需关注此风险

### 一句话防御
**货币类型必须由后端根据用户地区固定配置**，不信任前端传递的货币参数，支付回调时验证货币类型。

### 快速行动清单
1. [ ] 立即行动项：检查支付接口，确认货币类型是否由前端传递（今天可完成，免费）
2. [ ] 短期行动项：修改为后端固定货币配置，根据用户地区或 IP 决定（本周可完成，免费）
3. [ ] 长期行动项：添加支付回调货币验证，确保货币类型与订单一致（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用支付平台的货币保护功能

### 验证方法
- [ ] 在支付请求中修改货币参数（如 USD 改为 JPY）
- [ ] 提交支付请求
- [ ] 确认系统使用正确的货币，忽略前端传递的货币参数

---

## L2 小团队版（理解版）

### 场景还原
你的 SaaS 产品面向全球用户，支持美元（USD）和日元（JPY）两种货币。你的"Pro 计划"定价为 $99/月，约合 ¥15,000/月。攻击者发现你的系统允许前端传递货币参数，于是将货币从 USD 改为 JPY，然后支付 ¥99（而不是 ¥15,000），系统成功处理了这笔支付。

由于汇率差异，攻击者用约 $0.65 的价格购买了价值 $99 的服务，你的损失高达 99.3%。如果攻击者使用更低汇率的货币（如越南盾 VND），损失可能更大。

### 攻击路径（简化版）
1. **发现漏洞**：攻击者测试支付接口，发现货币参数可修改
2. **修改货币**：将货币从高价货币（USD）改为低价货币（JPY/VND）
3. **保持金额**：金额数字不变，但货币类型变了
4. **低价购买**：用远低于实际价值的价格购买商品

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：货币类型完全由后端决定，不信任前端传递的货币参数。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：信任前端传递的货币
@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    product_id = request.json.get('product_id')
    currency = request.json.get('currency', 'USD')  # 用户可自定义货币！
    
    # 价格根据货币计算
    prices = {
        'USD': 99,
        'JPY': 15000,
        'CNY': 699,
    }
    
    amount = prices.get(currency, 99) * 100  # 转为分
    
    # 创建支付
    payment = payment_gateway.create_payment(amount, currency)
    
    return {'payment_url': payment.url}
```

2. **修复代码**：
```python
# ✅ 正确做法：后端固定货币配置
import geoip2.database

# 货币配置：根据地区固定货币
REGION_CURRENCY_MAP = {
    'US': 'USD',
    'CN': 'CNY',
    'JP': 'JPY',
    'EU': 'EUR',
    'GB': 'GBP',
}

# 商品价格配置（每种货币对应的价格）
PRODUCT_PRICES = {
    'pro_plan': {
        'USD': 9900,    # $99
        'CNY': 69900,   # ¥699
        'JPY': 1500000, # ¥15,000
        'EUR': 8900,    # €89
        'GBP': 7900,    # £79
    }
}

def get_user_currency(user_ip=None, user_country=None):
    """
    根据用户地区决定货币类型
    """
    # 优先使用用户设置的国家
    if user_country:
        return REGION_CURRENCY_MAP.get(user_country, 'USD')
    
    # 根据 IP 判断地区
    if user_ip:
        try:
            with geoip2.database.Reader('GeoLite2-Country.mmdb') as reader:
                response = reader.country(user_ip)
                country_code = response.country.iso_code
                return REGION_CURRENCY_MAP.get(country_code, 'USD')
        except:
            pass
    
    # 默认使用美元
    return 'USD'

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    product_id = request.json.get('product_id')
    user_id = current_user.id
    
    # 1. 获取用户信息
    user = db.query("SELECT country FROM users WHERE id = ?", user_id)
    user_ip = request.remote_addr
    
    # 2. 根据地区确定货币（不信任前端）
    currency = get_user_currency(
        user_ip=user_ip,
        user_country=user.country if user else None
    )
    
    # 3. 从配置中获取价格（不信任前端）
    if product_id not in PRODUCT_PRICES:
        return {'error': '商品不存在'}, 404
    
    prices = PRODUCT_PRICES[product_id]
    
    if currency not in prices:
        return {'error': f'暂不支持 {currency} 支付'}, 400
    
    amount = prices[currency]
    
    # 4. 创建订单（记录货币和金额）
    order_id = db.execute("""
        INSERT INTO orders (user_id, product_id, amount, currency, status, created_at)
        VALUES (?, ?, ?, ?, 'pending', NOW())
        RETURNING id
    """, user_id, product_id, amount, currency)
    
    # 5. 创建支付
    payment = payment_gateway.create_payment(
        amount=amount,
        currency=currency,
        metadata={
            'order_id': order_id,
            'user_id': user_id,
        }
    )
    
    # 6. 更新订单支付 ID
    db.execute("UPDATE orders SET payment_id = ? WHERE id = ?", payment.id, order_id)
    
    logger.info(f"创建支付: order_id={order_id}, currency={currency}, amount={amount}")
    
    return {
        'payment_url': payment.url,
        'order_id': order_id,
        'amount': amount,
        'currency': currency,
    }
```

3. **支付回调验证**：
```python
@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    payment_id = request.form.get('payment_id')
    
    # 1. 验证签名
    if not payment_gateway.verify_signature(request):
        return '签名验证失败', 400
    
    # 2. 查询支付信息
    payment = payment_gateway.get_payment(payment_id)
    
    # 3. 查询订单
    order = db.query("""
        SELECT id, user_id, product_id, amount, currency, status
        FROM orders
        WHERE payment_id = ?
    """, payment_id)
    
    if not order:
        return '订单不存在', 404
    
    # 4. 验证金额（关键！）
    if payment.amount != order.amount:
        logger.error(f"金额不一致: order={order.id}, expected={order.amount}, actual={payment.amount}")
        return '金额验证失败', 400
    
    # 5. 验证货币（关键！）
    if payment.currency != order.currency:
        logger.error(f"""
            货币不一致告警！
            order_id={order.id}
            expected_currency={order.currency}
            actual_currency={payment.currency}
            user_id={order.user_id}
        """)
        send_security_alert('currency_mismatch', order, payment)
        return '货币验证失败', 400
    
    # 6. 更新订单状态
    db.execute("UPDATE orders SET status = 'paid', paid_at = NOW() WHERE id = ?", order.id)
    
    # 7. 发放商品
    grant_product(order.user_id, order.product_id)
    
    return 'success'
```

**局限性**：
- 需要维护货币配置
- 需要处理汇率更新（如果支持动态汇率）

#### 方案B：使用支付平台保护（低成本）

**工具/服务**：Stripe / Paddle

**优势**：
- Stripe 支持 Multi-Currency
- 可以创建固定价格的支付链接

**配置示例**：
```python
import stripe

# Stripe 产品配置
PRODUCT_PRICES = {
    'pro_plan': {
        'USD': 'price_xxxxx_usd',  # Stripe Price ID
        'EUR': 'price_xxxxx_eur',
        'JPY': 'price_xxxxx_jpy',
    }
}

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    product_id = request.json.get('product_id')
    
    # 根据用户地区确定货币
    currency = get_user_currency()
    
    # 使用 Stripe Price ID（无法篡改）
    price_id = PRODUCT_PRICES[product_id][currency]
    
    # 创建 Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,  # 使用固定的 Price ID
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://yourdomain.com/success',
        cancel_url='https://yourdomain.com/cancel',
    )
    
    return {'session_id': session.id}
```

**成本**：Stripe 手续费 2.9% + $0.30/笔，货币转换费 1%

### 决策树
```
货币类型是否由后端决定？
├── 否 → 立即修改为后端配置（方案A）
└── 是 → 是否验证支付回调货币？
    ├── 否 → 添加货币验证（方案A）
    └── 是 → 是否根据用户地区固定货币？
        ├── 否 → 添加地区判断逻辑（方案A）
        └── 是 → 当前方案基本完善
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify, current_user
from database import db
from payment_gateway import payment_gateway
import logging
from datetime import datetime
import geoip2.database

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 地区货币映射
REGION_CURRENCY_MAP = {
    'US': 'USD', 'CA': 'USD',
    'CN': 'CNY', 'HK': 'CNY', 'TW': 'CNY',
    'JP': 'JPY',
    'GB': 'GBP',
    'DE': 'EUR', 'FR': 'EUR', 'IT': 'EUR', 'ES': 'EUR', 'NL': 'EUR',
}

# 商品价格配置（单位：分）
PRODUCT_PRICES = {
    'pro_plan_monthly': {
        'USD': 9900,
        'CNY': 69900,
        'JPY': 1500000,
        'EUR': 8900,
        'GBP': 7900,
    },
    'pro_plan_yearly': {
        'USD': 99000,  # 年付优惠
        'CNY': 699000,
        'JPY': 15000000,
        'EUR': 89000,
        'GBP': 79000,
    }
}

class CurrencyService:
    @staticmethod
    def get_user_currency(user_id=None, user_ip=None):
        """
        根据用户信息确定货币类型
        """
        # 1. 检查用户是否有货币偏好设置
        if user_id:
            user = db.query("SELECT country, currency_preference FROM users WHERE id = ?", user_id)
            if user and user.currency_preference:
                return user.currency_preference
        
        # 2. 根据用户国家确定货币
        if user_id:
            user = db.query("SELECT country FROM users WHERE id = ?", user_id)
            if user and user.country:
                return REGION_CURRENCY_MAP.get(user.country, 'USD')
        
        # 3. 根据 IP 地理位置确定货币
        if user_ip:
            currency = CurrencyService.get_currency_by_ip(user_ip)
            if currency:
                return currency
        
        # 4. 默认美元
        return 'USD'
    
    @staticmethod
    def get_currency_by_ip(ip):
        """
        根据 IP 获取货币
        """
        try:
            with geoip2.database.Reader('GeoLite2-Country.mmdb') as reader:
                response = reader.country(ip)
                country_code = response.country.iso_code
                return REGION_CURRENCY_MAP.get(country_code, None)
        except Exception as e:
            logger.warning(f"IP 地理位置查询失败: ip={ip}, error={e}")
            return None
    
    @staticmethod
    def get_product_price(product_id, currency):
        """
        获取商品价格
        """
        if product_id not in PRODUCT_PRICES:
            return None
        
        prices = PRODUCT_PRICES[product_id]
        
        if currency not in prices:
            return None
        
        return prices[currency]
    
    @staticmethod
    def validate_currency_supported(currency):
        """
        验证货币是否支持
        """
        supported_currencies = {'USD', 'CNY', 'JPY', 'EUR', 'GBP'}
        return currency in supported_currencies

class PaymentService:
    @staticmethod
    def create_payment(user_id, product_id):
        """
        创建支付 - 安全版本
        """
        # 1. 验证商品存在
        if product_id not in PRODUCT_PRICES:
            return None, '商品不存在'
        
        # 2. 获取用户货币（后端决定）
        user_ip = request.remote_addr
        currency = CurrencyService.get_user_currency(user_id, user_ip)
        
        # 3. 获取价格（后端配置）
        amount = CurrencyService.get_product_price(product_id, currency)
        
        if amount is None:
            return None, f'暂不支持 {currency} 支付'
        
        # 4. 创建订单（记录货币和金额）
        order_id = db.execute("""
            INSERT INTO orders 
                (user_id, product_id, amount, currency, status, user_ip, created_at)
            VALUES (?, ?, ?, ?, 'pending', ?, NOW())
            RETURNING id
        """, user_id, product_id, amount, currency, user_ip)
        
        # 5. 创建支付
        try:
            payment = payment_gateway.create_payment(
                amount=amount,
                currency=currency,
                metadata={
                    'order_id': str(order_id),
                    'user_id': str(user_id),
                    'product_id': product_id,
                }
            )
            
            # 6. 更新订单支付 ID
            db.execute("""
                UPDATE orders SET payment_id = ? WHERE id = ?
            """, payment.id, order_id)
            
            logger.info(f"""
                创建支付成功:
                order_id={order_id}
                user_id={user_id}
                product_id={product_id}
                currency={currency}
                amount={amount}
            """)
            
            return {
                'order_id': order_id,
                'payment_url': payment.url,
                'amount': amount,
                'currency': currency,
            }, None
            
        except Exception as e:
            logger.error(f"创建支付失败: {e}")
            return None, '创建支付失败'
    
    @staticmethod
    def process_callback(payment_id, callback_data):
        """
        处理支付回调 - 安全版本
        """
        # 1. 验证签名
        if not payment_gateway.verify_signature(callback_data):
            logger.warning(f"签名验证失败: payment_id={payment_id}")
            return False, '签名验证失败'
        
        # 2. 查询支付信息
        payment = payment_gateway.get_payment(payment_id)
        
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
            logger.info(f"订单已处理: order_id={order.id}")
            return True, 'success'
        
        # 5. 验证支付状态
        if payment.status != 'success':
            return False, '支付未成功'
        
        # 6. 验证金额
        if payment.amount != order.amount:
            logger.error(f"""
                金额不一致:
                order_id={order.id}
                expected={order.amount}
                actual={payment.amount}
            """)
            send_security_alert('amount_mismatch', order, payment)
            return False, '金额验证失败'
        
        # 7. 验证货币（关键！）
        if payment.currency != order.currency:
            logger.error(f"""
                货币篡改告警！
                order_id={order.id}
                expected_currency={order.currency}
                actual_currency={payment.currency}
                user_id={order.user_id}
                amount={payment.amount}
            """)
            send_security_alert('currency_mismatch', order, payment)
            return False, '货币验证失败'
        
        # 8. 更新订单状态
        with db.transaction():
            db.execute("""
                UPDATE orders
                SET status = 'paid', paid_at = NOW()
                WHERE id = ? AND status = 'pending'
            """, order.id)
            
            # 9. 发放商品
            grant_product(order.user_id, order.product_id)
        
        logger.info(f"支付成功: order_id={order.id}")
        return True, 'success'

@app.route('/api/create-payment', methods=['POST'])
def create_payment():
    """
    创建支付接口
    """
    try:
        product_id = request.json.get('product_id')
        user_id = current_user.id
        
        result, error = PaymentService.create_payment(user_id, product_id)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"创建支付异常: {e}")
        return jsonify({'error': '系统错误'}), 500

@app.route('/api/payment/callback', methods=['POST'])
def payment_callback():
    """
    支付回调接口
    """
    try:
        payment_id = request.form.get('payment_id')
        
        success, message = PaymentService.process_callback(
            payment_id,
            request.form.to_dict()
        )
        
        return message, 200 if success else 400
        
    except Exception as e:
        logger.error(f"处理回调异常: {e}")
        return '系统错误', 500

@app.route('/api/currency', methods=['GET'])
def get_currency():
    """
    获取用户货币信息（只读）
    """
    user_id = current_user.id if current_user.is_authenticated else None
    user_ip = request.remote_addr
    
    currency = CurrencyService.get_user_currency(user_id, user_ip)
    
    return jsonify({
        'currency': currency,
        'supported_currencies': list(REGION_CURRENCY_MAP.values()),
    })

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

1. **货币管理**：
   - 地区货币映射
   - 实时汇率更新
   - 货币风险控制

2. **验证机制**：
   - 创建订单时验证
   - 支付回调时验证
   - 异常货币监控

3. **风控规则**：
   - 异常地区检测
   - VPN/代理检测
   - 货币切换限制

4. **监控告警**：
   - 货币不一致告警
   - 异常汇率告警
   - 跨地区支付监控

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [多币种支付最佳实践](https://stripe.com/docs/currencies)
- [货币欺诈防范指南](https://www.paddle.com/blog/currency-fraud)
- [汇率风险管理](https://stripe.com/docs/connect/currencies)
