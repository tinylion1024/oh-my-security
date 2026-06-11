# 支付信息泄露 - 独立开发者版

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
用户的支付信息（卡号、CVV、有效期等）被记录在日志、数据库或返回给前端，导致泄露，你的损失：用户信任丧失 + 法律责任 + 罚款（PCI DSS 违规可罚 $5,000-$100,000/月）。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 支付信息直接存入数据库
- [ ] 日志中记录完整支付信息
- [ ] API 响应包含敏感支付信息
- [ ] 未使用支付平台 Token 化
→ 勾选≥1项，即需关注此风险

### 一句话防御
**永远不要存储完整的支付卡信息**，使用支付平台（Stripe/Paddle）的 Token 化服务，仅存储 Token，日志和响应中脱敏处理。

### 快速行动清单
1. [ ] 立即行动项：检查日志和数据库，确认是否记录支付卡信息（今天可完成，免费）
2. [ ] 短期行动项：修改代码，使用支付平台 Token 化，脱敏日志输出（本周可完成，免费）
3. [ ] 长期行动项：实现 PCI DSS 基础合规，定期安全审计（规划中，可能需要付费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用 Stripe/Paddle 等支付平台（Token 化免费，仅收交易手续费）

### 验证方法
- [ ] 检查日志是否包含完整卡号（应仅显示 **** **** **** 1234）
- [ ] 检查数据库是否存储 CVV（应不存储）
- [ ] 检查 API 响应是否返回完整卡号（应返回脱敏信息）

---

## L2 小团队版（理解版）

### 场景还原
你开发了一个电商平台，为了方便用户下次购买，你决定保存用户的支付卡信息。你在数据库中直接存储了用户的信用卡号、CVV、有效期等信息。某天，你的数据库被黑客入侵，所有用户的支付卡信息被盗取。由于你存储了 CVV（违反 PCI DSS 规定），你需要面临严重的法律责任和巨额罚款。更糟糕的是，你的日志文件中也完整记录了用户的支付卡信息，进一步扩大了泄露范围。

### 攻击路径（简化版）
1. **发现漏洞**：攻击者发现数据库或日志中存储完整支付卡信息
2. **获取访问**：通过 SQL 注入、日志泄露或数据库入侵获取数据
3. **窃取信息**：导出完整的信用卡号、CVV、有效期
4. **滥用信息**：在暗网出售或直接盗刷
5. **造成损失**：用户资金损失 + 商家法律责任

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：永远不要存储完整的支付卡信息，使用支付平台的 Token 化服务，日志和响应中脱敏处理。

**工具/服务**：Stripe / Paddle（Token 化免费）

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：直接存储支付卡信息
@app.route('/api/save-card', methods=['POST'])
def save_card():
    user_id = g.user_id
    card_number = request.json.get('card_number')  # 完整卡号
    cvv = request.json.get('cvv')                  # CVV
    expiry = request.json.get('expiry')            # 有效期
    
    # 直接存储到数据库！严重违规！
    db.execute("""
        INSERT INTO payment_cards (user_id, card_number, cvv, expiry)
        VALUES (?, ?, ?, ?)
    """, user_id, card_number, cvv, expiry)
    
    # 日志记录了完整卡号！
    logger.info(f"保存银行卡: user_id={user_id}, card={card_number}")
    
    return jsonify({'success': True})

# ❌ 错误做法：API 返回完整卡号
@app.route('/api/get-cards', methods=['GET'])
def get_cards():
    user_id = g.user_id
    
    cards = db.query_all("""
        SELECT id, card_number, expiry FROM payment_cards WHERE user_id = ?
    """, user_id)
    
    # 直接返回完整卡号！
    return jsonify({'cards': cards})
```

2. **修复代码 - 使用 Stripe Token 化**：
```python
import stripe

# Stripe Token 化示例
@app.route('/api/save-card', methods=['POST'])
def save_card():
    """
    保存支付卡 - 使用 Stripe Token 化
    """
    user_id = g.user_id
    
    # 前端使用 Stripe Elements 获取 payment_method
    # 此处不再接收卡号，仅接收 payment_method_id
    payment_method_id = request.json.get('payment_method_id')
    
    if not payment_method_id:
        return jsonify({'error': '缺少支付方式'}), 400
    
    try:
        # 1. 获取支付方式信息（不存储卡号）
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        
        # 2. 验证支付方式属于当前用户（通过 Stripe Customer）
        # 首先检查用户是否已有 Stripe Customer
        user = db.query("SELECT stripe_customer_id FROM users WHERE id = ?", user_id)
        
        if not user.stripe_customer_id:
            # 创建 Stripe Customer
            customer = stripe.Customer.create(
                metadata={'user_id': user_id}
            )
            
            db.execute("""
                UPDATE users SET stripe_customer_id = ? WHERE id = ?
            """, customer.id, user_id)
            
            customer_id = customer.id
        else:
            customer_id = user.stripe_customer_id
        
        # 3. 将支付方式附加到客户
        stripe.PaymentMethod.attach(
            payment_method_id,
            customer=customer_id
        )
        
        # 4. 存储支付方式信息（仅存储脱敏信息和 Token）
        card = payment_method.card
        
        db.execute("""
            INSERT INTO payment_methods
                (user_id, stripe_payment_method_id, stripe_customer_id,
                 last4, brand, exp_month, exp_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
        """, user_id, payment_method_id, customer_id,
             card.last4, card.brand, card.exp_month, card.exp_year)
        
        # 5. 日志记录（脱敏）
        logger.info(f"""
            保存支付方式: user_id={user_id}
            brand={card.brand}
            last4=****{card.last4}
        """)
        
        return jsonify({
            'success': True,
            'card': {
                'last4': card.last4,
                'brand': card.brand,
                'exp_month': card.exp_month,
                'exp_year': card.exp_year,
            }
        })
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe 错误: {e}")
        return jsonify({'error': '保存支付方式失败'}), 400

@app.route('/api/get-cards', methods=['GET'])
def get_cards():
    """
    获取用户支付卡列表 - 返回脱敏信息
    """
    user_id = g.user_id
    
    # 从数据库获取支付方式（仅脱敏信息）
    cards = db.query_all("""
        SELECT id, stripe_payment_method_id, last4, brand, exp_month, exp_year
        FROM payment_methods
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, user_id)
    
    # 返回脱敏信息
    card_list = [{
        'id': card.id,
        'last4': card.last4,
        'brand': card.brand,
        'expiry': f"{card.exp_month}/{card.exp_year}",
        'display_number': f"**** **** **** {card.last4}"
    } for card in cards]
    
    return jsonify({'cards': card_list})
```

3. **日志脱敏处理**：
```python
import re
import logging
from functools import wraps

class SensitiveDataFilter:
    """
    敏感数据脱敏过滤器
    """
    
    # 卡号正则表达式
    CARD_NUMBER_PATTERN = re.compile(r'\b\d{13,19}\b')
    
    # CVV 正则表达式
    CVV_PATTERN = re.compile(r'\b\d{3,4}\b')
    
    @staticmethod
    def mask_card_number(text):
        """
        脱敏卡号
        保留前 6 位和后 4 位，中间用 * 替换
        """
        def replace_card(match):
            card = match.group()
            if len(card) >= 13:
                return card[:6] + '*' * (len(card) - 10) + card[-4:]
            return card
        
        return SensitiveDataFilter.CARD_NUMBER_PATTERN.sub(replace_card, text)
    
    @staticmethod
    def mask_cvv(text):
        """
        脱敏 CVV
        """
        return SensitiveDataFilter.CVV_PATTERN.sub('***', text)
    
    @staticmethod
    def sanitize(text):
        """
        综合脱敏
        """
        if not isinstance(text, str):
            text = str(text)
        
        text = SensitiveDataFilter.mask_card_number(text)
        text = SensitiveDataFilter.mask_cvv(text)
        
        return text

class SensitiveDataLogger:
    """
    敏感数据安全日志记录器
    """
    
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, message, **kwargs):
        """安全记录 info 日志"""
        sanitized_message = SensitiveDataFilter.sanitize(message)
        self.logger.info(sanitized_message, **kwargs)
    
    def error(self, message, **kwargs):
        """安全记录 error 日志"""
        sanitized_message = SensitiveDataFilter.sanitize(message)
        self.logger.error(sanitized_message, **kwargs)
    
    def warning(self, message, **kwargs):
        """安全记录 warning 日志"""
        sanitized_message = SensitiveDataFilter.sanitize(message)
        self.logger.warning(sanitized_message, **kwargs)

# 使用示例
logger = SensitiveDataLogger(logging.getLogger(__name__))

@app.route('/api/payment', methods=['POST'])
def process_payment():
    """
    处理支付 - 日志脱敏
    """
    user_id = g.user_id
    payment_method_id = request.json.get('payment_method_id')
    amount = request.json.get('amount')
    
    # 记录日志（自动脱敏）
    logger.info(f"""
        处理支付:
        user_id={user_id}
        payment_method={payment_method_id}
        amount={amount}
    """)
    
    # 处理支付...
    
    return jsonify({'success': True})
```

4. **PCI DSS 基础合规**：
```python
"""
PCI DSS 基础合规检查清单

独立开发者版本（SAQ A）：
适用于使用支付平台（如 Stripe）处理支付的场景

核心要求：
1. 不存储完整的支付卡信息（卡号、CVV、有效期）
2. 仅存储支付平台提供的 Token
3. 日志和响应中脱敏处理
4. 使用 HTTPS 加密传输
5. 定期安全审计

数据表设计建议：
"""

# 支付方式表（仅存储脱敏信息）
"""
CREATE TABLE payment_methods (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    
    -- 支付平台 Token（不是卡号）
    stripe_payment_method_id VARCHAR(100) NOT NULL,
    stripe_customer_id VARCHAR(100) NOT NULL,
    
    -- 脱敏的卡信息（仅用于显示）
    last4 VARCHAR(4) NOT NULL,      -- 仅后 4 位
    brand VARCHAR(20) NOT NULL,      -- 卡品牌：Visa、Mastercard 等
    exp_month INT NOT NULL,          -- 有效期月份
    exp_year INT NOT NULL,           -- 有效期年份
    
    -- 元数据
    is_default BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_payment (user_id)
);
"""

# 支付记录表
"""
CREATE TABLE payments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_id INT NOT NULL,
    
    -- 支付平台信息
    stripe_payment_intent_id VARCHAR(100) NOT NULL,
    stripe_payment_method_id VARCHAR(100),
    
    -- 支付金额和状态
    amount INT NOT NULL,              -- 单位：分
    currency VARCHAR(3) NOT NULL,
    status ENUM('pending', 'succeeded', 'failed') NOT NULL,
    
    -- 脱敏的支付方式信息
    payment_method_last4 VARCHAR(4),
    payment_method_brand VARCHAR(20),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    INDEX idx_user_payment (user_id),
    INDEX idx_order_payment (order_id)
);
"""

class PCIDSSCompliance:
    """
    PCI DSS 合规检查工具
    """
    
    @staticmethod
    def check_card_data_in_request(data):
        """
        检查请求数据中是否包含卡号
        """
        card_fields = ['card_number', 'cardNumber', 'number', 'pan', 'account_number']
        cvv_fields = ['cvv', 'cvv2', 'cvc', 'security_code']
        
        warnings = []
        
        for field in card_fields:
            if field in data:
                warnings.append(f"发现卡号字段: {field}")
        
        for field in cvv_fields:
            if field in data:
                warnings.append(f"发现 CVV 字段: {field}")
        
        return warnings
    
    @staticmethod
    def check_database_schema():
        """
        检查数据库 Schema 是否符合 PCI DSS
        """
        # 检查是否有表包含卡号字段
        tables_with_card_data = db.query_all("""
            SELECT TABLE_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE COLUMN_NAME IN ('card_number', 'cvv', 'cvv2', 'cvc')
            AND TABLE_SCHEMA = DATABASE()
        """)
        
        if tables_with_card_data:
            logger.warning(f"""
                PCI DSS 违规: 发现存储完整卡信息的字段
                tables={tables_with_card_data}
            """)
            return False
        
        return True

# 请求拦截器：检查敏感数据
@app.before_request
def check_sensitive_data():
    """
    检查请求中是否包含敏感支付数据
    """
    if request.is_json:
        data = request.get_json()
        warnings = PCIDSSCompliance.check_card_data_in_request(data)
        
        if warnings:
            logger.warning(f"""
                发现敏感支付数据:
                path={request.path}
                warnings={warnings}
                建议: 使用 Stripe Elements 或支付平台 SDK 获取 Token
            """)
```

**局限性**：
- 需要支付平台支持
- 前端需要集成支付平台 SDK

#### 方案B：完全使用支付平台托管（推荐）

**工具/服务**：Stripe Checkout / Paddle

**优势**：
- 完全不接触支付卡信息
- PCI DSS SAQ A 合规（最简化）
- 支付平台承担安全责任

**配置示例**：
```python
import stripe

# 使用 Stripe Checkout（完全托管）
@app.route('/api/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """
    创建 Stripe Checkout Session
    用户在 Stripe 托管页面完成支付，你的服务器完全不接触卡信息
    """
    user_id = g.user_id
    product_id = request.json.get('product_id')
    
    # 获取产品信息
    product = get_product(product_id)
    
    # 创建 Checkout Session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': product.name,
                },
                'unit_amount': product.price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://yourdomain.com/cancel',
        metadata={
            'user_id': user_id,
            'product_id': product_id,
        }
    )
    
    # 日志记录（无敏感信息）
    logger.info(f"创建 Checkout Session: user_id={user_id}, session_id={session.id}")
    
    return jsonify({'session_id': session.id})
```

**成本**：Stripe 手续费 2.9% + $0.30/笔，无额外费用

### 决策树
```
是否存储完整卡号或 CVV？
├── 是 → 立即删除，使用支付平台 Token 化（方案A/B）
└── 否 → 是否使用支付平台 Token 化？
    ├── 否 → 改用支付平台 Token 化（方案A）
    └── 是 → 日志是否脱敏处理？
        ├── 否 → 添加日志脱敏（方案A）
        └── 是 → 当前方案基本合规
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify, g
import stripe
import logging
import re
from functools import wraps

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 敏感数据过滤器
class SensitiveDataFilter:
    CARD_PATTERN = re.compile(r'\b\d{13,19}\b')
    CVV_PATTERN = re.compile(r'\b\d{3,4}\b')
    
    @staticmethod
    def mask_card(text):
        def replace(match):
            card = match.group()
            return card[:6] + '*' * (len(card) - 10) + card[-4:] if len(card) >= 13 else card
        return SensitiveDataFilter.CARD_PATTERN.sub(replace, text)
    
    @staticmethod
    def sanitize(text):
        if not isinstance(text, str):
            text = str(text)
        text = SensitiveDataFilter.mask_card(text)
        text = SensitiveDataFilter.CVV_PATTERN.sub('***', text)
        return text

# 安全日志记录器
class SafeLogger:
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, msg, **kwargs):
        self.logger.info(SensitiveDataFilter.sanitize(msg), **kwargs)
    
    def error(self, msg, **kwargs):
        self.logger.error(SensitiveDataFilter.sanitize(msg), **kwargs)
    
    def warning(self, msg, **kwargs):
        self.logger.warning(SensitiveDataFilter.sanitize(msg), **kwargs)

safe_logger = SafeLogger(logger)

# 支付卡服务
class PaymentCardService:
    """
    支付卡服务 - 使用 Stripe Token 化
    """
    
    @staticmethod
    def save_payment_method(user_id, payment_method_id):
        """
        保存支付方式
        """
        try:
            # 获取用户 Stripe Customer ID
            user = db.query("SELECT stripe_customer_id FROM users WHERE id = ?", user_id)
            
            if not user.stripe_customer_id:
                customer = stripe.Customer.create(metadata={'user_id': user_id})
                db.execute("UPDATE users SET stripe_customer_id = ? WHERE id = ?", customer.id, user_id)
                customer_id = customer.id
            else:
                customer_id = user.stripe_customer_id
            
            # 附加支付方式到客户
            stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
            
            # 获取支付方式信息
            pm = stripe.PaymentMethod.retrieve(payment_method_id)
            
            # 仅存储脱敏信息
            db.execute("""
                INSERT INTO payment_methods
                    (user_id, stripe_payment_method_id, stripe_customer_id,
                     last4, brand, exp_month, exp_year, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, NOW())
            """, user_id, payment_method_id, customer_id,
                 pm.card.last4, pm.card.brand, pm.card.exp_month, pm.card.exp_year)
            
            safe_logger.info(f"""
                保存支付方式成功: user_id={user_id}
                brand={pm.card.brand}, last4=****{pm.card.last4}
            """)
            
            return {
                'last4': pm.card.last4,
                'brand': pm.card.brand,
                'exp_month': pm.card.exp_month,
                'exp_year': pm.card.exp_year,
            }
        
        except stripe.error.StripeError as e:
            safe_logger.error(f"Stripe 错误: {e}")
            return None
    
    @staticmethod
    def get_user_cards(user_id):
        """
        获取用户支付卡列表（脱敏）
        """
        cards = db.query_all("""
            SELECT id, last4, brand, exp_month, exp_year
            FROM payment_methods
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, user_id)
        
        return [{
            'id': card.id,
            'last4': card.last4,
            'brand': card.brand,
            'expiry': f"{card.exp_month}/{card.exp_year}",
            'display': f"**** **** **** {card.last4}"
        } for card in cards]

# API 接口
@app.route('/api/payment/save-card', methods=['POST'])
def save_card():
    """
    保存支付卡
    """
    user_id = g.user_id
    payment_method_id = request.json.get('payment_method_id')
    
    if not payment_method_id:
        return jsonify({'error': '缺少支付方式'}), 400
    
    # 检查是否传递了敏感数据
    if 'card_number' in request.json or 'cvv' in request.json:
        safe_logger.warning(f"检测到敏感支付数据: user_id={user_id}")
        return jsonify({'error': '请使用 Stripe Elements 获取支付方式'}), 400
    
    card = PaymentCardService.save_payment_method(user_id, payment_method_id)
    
    if card:
        return jsonify({'success': True, 'card': card})
    else:
        return jsonify({'error': '保存失败'}), 400

@app.route('/api/payment/cards', methods=['GET'])
def get_cards():
    """
    获取支付卡列表
    """
    user_id = g.user_id
    cards = PaymentCardService.get_user_cards(user_id)
    return jsonify({'cards': cards})

if __name__ == '__main__':
    app.run(debug=True)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **数据加密**：
   - 敏感数据加密存储
   - 传输层加密（TLS）
   - 密钥管理系统

2. **访问控制**：
   - 最小权限原则
   - 数据访问审计
   - 敏感数据隔离

3. **合规审计**：
   - PCI DSS 年度审计
   - 渗透测试
   - 安全评估

4. **应急响应**：
   - 数据泄露响应计划
   - 用户通知流程
   - 法律合规配合

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [PCI DSS 合规指南](https://www.pcisecuritystandards.org/)
- [Stripe 安全最佳实践](https://stripe.com/docs/security)
- [支付卡数据保护](https://stripe.com/docs/security/guide)
