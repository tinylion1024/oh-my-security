# 发票欺诈 - 独立开发者版

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: payment（支付安全）
- **严重程度**: high（高危）
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户伪造发票抬头、税号或重复申请发票，用于报销欺诈或虚开发票，你的损失：税务风险 + 法律责任 + 罚款（虚开发票可罚 5-50 万元）。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 发票抬头和税号未验证
- [ ] 同一订单可多次申请发票
- [ ] 发票金额可用户自定义
- [ ] 缺少发票开具限制机制
→ 勾选≥1项，即需关注此风险

### 一句话防御
**发票信息必须验证**，限制每笔订单仅能开具一次发票，发票金额必须与订单金额一致，记录完整的开票日志。

### 快速行动清单
1. [ ] 立即行动项：检查发票申请是否有重复开具限制（今天可完成，免费）
2. [ ] 短期行动项：添加发票信息验证和开票限制（本周可完成，免费）
3. [ ] 长期行动项：对接税务系统验证，实现发票风控（规划中，可能需要付费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用发票服务（如航信、百望）

### 验证方法
- [ ] 尝试对同一订单多次申请发票
- [ ] 尝试修改发票金额
- [ ] 尝试使用虚假税号
- [ ] 确认系统拒绝所有异常申请

---

## L2 小团队版（理解版）

### 场景还原
你开发了一个 SaaS 产品，用户购买服务后可以申请增值税发票。你的系统允许用户自己填写发票抬头、税号和金额，没有验证机制。攻击者发现这个漏洞后，使用虚假的发票信息申请发票，然后用于公司报销，实际上这笔钱并未用于真实业务。更严重的是，攻击者使用同一订单多次申请发票，或者修改发票金额，导致你虚开发票，面临税务稽查和法律风险。

### 攻击路径（简化版）
1. **发现漏洞**：攻击者发现发票信息可自由填写且未验证
2. **伪造信息**：使用虚假的发票抬头和税号
3. **重复开票**：同一订单多次申请发票
4. **金额篡改**：修改发票金额，虚开发票
5. **报销欺诈**：使用虚假发票报销，套取资金

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：发票信息必须验证，限制每笔订单仅能开具一次发票，发票金额必须与订单金额一致，记录完整开票日志。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：发票信息未验证，可重复开具
@app.route('/api/apply-invoice', methods=['POST'])
def apply_invoice():
    user_id = g.user_id
    order_id = request.json.get('order_id')
    
    # 用户自定义发票信息！
    invoice_title = request.json.get('invoice_title')  # 发票抬头
    tax_id = request.json.get('tax_id')                # 税号
    invoice_amount = request.json.get('amount')        # 金额可自定义！
    
    # 直接开具发票！未验证！
    invoice_id = db.execute("""
        INSERT INTO invoices
            (order_id, user_id, title, tax_id, amount, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'issued', NOW())
    """, order_id, user_id, invoice_title, tax_id, invoice_amount)
    
    return jsonify({'invoice_id': invoice_id})
```

2. **修复代码 - 发票数据表设计**：
```python
# 发票数据表设计
"""
CREATE TABLE invoices (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_id INT NOT NULL,
    
    -- 发票基本信息
    invoice_type ENUM('normal', 'special') NOT NULL,  -- 普票/专票
    invoice_no VARCHAR(50) UNIQUE,                     -- 发票号码
    
    -- 购买方信息
    buyer_title VARCHAR(200) NOT NULL,                 -- 购买方名称
    buyer_tax_id VARCHAR(50) NOT NULL,                 -- 购买方税号
    buyer_address VARCHAR(200),                        -- 地址
    buyer_phone VARCHAR(50),                           -- 电话
    buyer_bank VARCHAR(100),                           -- 开户行
    buyer_account VARCHAR(50),                         -- 账号
    
    -- 发票金额（必须与订单金额一致）
    amount DECIMAL(10, 2) NOT NULL,
    tax_amount DECIMAL(10, 2) NOT NULL,                -- 税额
    
    -- 状态
    status ENUM('pending', 'issued', 'cancelled', 'red_letter') DEFAULT 'pending',
    
    -- 时间
    issued_at DATETIME,                                -- 开具时间
    cancelled_at DATETIME,                             -- 作废时间
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    
    UNIQUE KEY uk_order_invoice (order_id),            -- 每笔订单仅一张发票
    INDEX idx_user_invoice (user_id)
);
"""

# 订单表添加发票状态字段
"""
ALTER TABLE orders ADD COLUMN invoice_status ENUM('none', 'applied', 'issued') DEFAULT 'none';
"""
```

3. **修复代码 - 发票验证服务**：
```python
import re
from decimal import Decimal

class InvoiceService:
    """
    发票服务
    """
    
    # 税号格式验证（中国大陆）
    TAX_ID_PATTERN = re.compile(r'^[0-9A-Z]{15,20}$')
    
    # 统一社会信用代码格式
    USCC_PATTERN = re.compile(r'^[0-9A-Z]{18}$')
    
    @staticmethod
    def validate_tax_id(tax_id):
        """
        验证税号格式
        """
        tax_id = tax_id.upper().strip()
        
        # 验证长度和格式
        if not (InvoiceService.TAX_ID_PATTERN.match(tax_id) or
                InvoiceService.USCC_PATTERN.match(tax_id)):
            return False, '税号格式不正确'
        
        # 进一步验证（可选）
        # 可以对接税务局 API 验证税号真实性
        
        return True, tax_id
    
    @staticmethod
    def validate_invoice_title(title):
        """
        验证发票抬头
        """
        if not title or len(title.strip()) < 2:
            return False, '发票抬头不能为空'
        
        if len(title) > 200:
            return False, '发票抬头过长'
        
        # 简单验证：不能包含特殊字符
        if re.search(r'[<>\"\'\\]', title):
            return False, '发票抬头包含非法字符'
        
        return True, title.strip()
    
    @staticmethod
    def check_order_invoice_status(order_id, user_id):
        """
        检查订单发票状态
        """
        # 查询订单
        order = db.query("""
            SELECT id, user_id, total_amount, status, invoice_status
            FROM orders
            WHERE id = ?
        """, order_id)
        
        if not order:
            return None, '订单不存在'
        
        # 验证订单归属
        if order.user_id != user_id:
            return None, '无权操作此订单'
        
        # 验证订单状态
        if order.status != 'paid':
            return None, '订单未支付，无法开具发票'
        
        # 验证发票状态
        if order.invoice_status == 'issued':
            return None, '该订单已开具发票，不能重复开具'
        
        if order.invoice_status == 'applied':
            return None, '该订单发票申请处理中'
        
        return order, None
    
    @staticmethod
    def apply_invoice(user_id, order_id, invoice_data):
        """
        申请发票
        """
        # 1. 检查订单状态
        order, error = InvoiceService.check_order_invoice_status(order_id, user_id)
        
        if error:
            return None, error
        
        # 2. 验证发票信息
        title = invoice_data.get('buyer_title', '').strip()
        tax_id = invoice_data.get('buyer_tax_id', '').strip()
        
        # 验证抬头
        valid, result = InvoiceService.validate_invoice_title(title)
        if not valid:
            return None, result
        title = result
        
        # 验证税号
        valid, result = InvoiceService.validate_tax_id(tax_id)
        if not valid:
            return None, result
        tax_id = result
        
        # 3. 确定发票金额（必须与订单金额一致）
        invoice_amount = order.total_amount
        
        # 计算税额（假设税率 6%）
        tax_rate = Decimal('0.06')
        tax_amount = (invoice_amount / (1 + tax_rate) * tax_rate).quantize(Decimal('0.01'))
        
        # 4. 创建发票申请（使用事务）
        with db.transaction():
            # 更新订单发票状态
            db.execute("""
                UPDATE orders
                SET invoice_status = 'applied', updated_at = NOW()
                WHERE id = ? AND invoice_status = 'none'
            """, order_id)
            
            # 创建发票记录
            invoice_id = db.execute("""
                INSERT INTO invoices
                    (user_id, order_id, invoice_type, buyer_title, buyer_tax_id,
                     buyer_address, buyer_phone, buyer_bank, buyer_account,
                     amount, tax_amount, status, created_at)
                VALUES (?, ?, 'normal', ?, ?, ?, ?, ?, ?, ?, ?, 'pending', NOW())
            """, user_id, order_id, title, tax_id,
                 invoice_data.get('buyer_address'),
                 invoice_data.get('buyer_phone'),
                 invoice_data.get('buyer_bank'),
                 invoice_data.get('buyer_account'),
                 invoice_amount, tax_amount)
        
        logger.info(f"""
            发票申请成功:
            invoice_id={invoice_id}
            order_id={order_id}
            user_id={user_id}
            title={title}
            tax_id={tax_id}
            amount={invoice_amount}
        """)
        
        return {
            'invoice_id': invoice_id,
            'order_id': order_id,
            'amount': float(invoice_amount),
            'tax_amount': float(tax_amount),
            'status': 'pending'
        }, None
    
    @staticmethod
    def get_invoice_by_order(order_id, user_id):
        """
        获取订单发票
        """
        invoice = db.query("""
            SELECT i.*, o.total_amount as order_amount
            FROM invoices i
            JOIN orders o ON i.order_id = o.id
            WHERE i.order_id = ? AND o.user_id = ?
        """, order_id, user_id)
        
        return invoice

# API 接口
@app.route('/api/invoice/apply', methods=['POST'])
def apply_invoice_api():
    """
    申请发票
    """
    user_id = g.user_id
    order_id = request.json.get('order_id')
    
    invoice_data = {
        'buyer_title': request.json.get('title'),
        'buyer_tax_id': request.json.get('tax_id'),
        'buyer_address': request.json.get('address'),
        'buyer_phone': request.json.get('phone'),
        'buyer_bank': request.json.get('bank'),
        'buyer_account': request.json.get('account'),
    }
    
    result, error = InvoiceService.apply_invoice(user_id, order_id, invoice_data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result)

@app.route('/api/invoice/order/<int:order_id>', methods=['GET'])
def get_invoice(order_id):
    """
    获取订单发票信息
    """
    user_id = g.user_id
    
    invoice = InvoiceService.get_invoice_by_order(order_id, user_id)
    
    if not invoice:
        return jsonify({'has_invoice': False})
    
    return jsonify({
        'has_invoice': True,
        'invoice': {
            'invoice_no': invoice.invoice_no,
            'title': invoice.buyer_title,
            'tax_id': invoice.buyer_tax_id,
            'amount': float(invoice.amount),
            'status': invoice.status,
            'issued_at': invoice.issued_at.isoformat() if invoice.issued_at else None,
        }
    })
```

4. **开票限制机制**：
```python
from datetime import datetime, timedelta

class InvoiceRateLimit:
    """
    发票申请频率限制
    """
    
    @staticmethod
    def check_user_limit(user_id, time_window=24):
        """
        检查用户开票频率（24 小时内最多 10 张）
        """
        count = db.query("""
            SELECT COUNT(*) as count
            FROM invoices
            WHERE user_id = ?
            AND created_at > DATE_SUB(NOW(), INTERVAL ? HOUR)
        """, user_id, time_window)
        
        if count.count >= 10:
            return False, '开票频率过高，请稍后再试'
        
        return True, None
    
    @staticmethod
    def check_amount_limit(user_id, amount_threshold=100000):
        """
        检查用户开票金额限制（单张发票最高 10 万）
        """
        # 查询用户申请的发票金额
        result = db.query("""
            SELECT SUM(amount) as total_amount
            FROM invoices
            WHERE user_id = ?
            AND created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND status != 'cancelled'
        """, user_id)
        
        total = result.total_amount or 0
        
        if total > amount_threshold:
            # 需要人工审核
            return False, '开票金额较大，需要人工审核'
        
        return True, None

class InvoiceAntiFraud:
    """
    发票欺诈检测
    """
    
    @staticmethod
    def detect_suspicious(user_id, invoice_data):
        """
        检测可疑发票申请
        """
        warnings = []
        
        # 1. 检测频繁修改发票抬头
        recent_titles = db.query_all("""
            SELECT DISTINCT buyer_title
            FROM invoices
            WHERE user_id = ?
            AND created_at > DATE_SUB(NOW(), INTERVAL 30 DAY)
        """, user_id)
        
        new_title = invoice_data.get('buyer_title', '').strip()
        
        if recent_titles and new_title not in [t.buyer_title for t in recent_titles]:
            warnings.append({
                'type': 'TITLE_CHANGE',
                'message': '发票抬头与历史记录不符'
            })
        
        # 2. 检测可疑税号
        # 可以对接税务局黑名单
        
        # 3. 检测开票金额异常
        order_id = invoice_data.get('order_id')
        order = db.query("SELECT total_amount FROM orders WHERE id = ?", order_id)
        
        if order and order.total_amount > 50000:
            warnings.append({
                'type': 'HIGH_AMOUNT',
                'message': f'开票金额较大: {order.total_amount}'
            })
        
        return warnings

# 增强的申请接口
@app.route('/api/invoice/apply', methods=['POST'])
def apply_invoice_enhanced():
    """
    申请发票（增强版）
    """
    user_id = g.user_id
    order_id = request.json.get('order_id')
    
    invoice_data = {
        'order_id': order_id,
        'buyer_title': request.json.get('title'),
        'buyer_tax_id': request.json.get('tax_id'),
        'buyer_address': request.json.get('address'),
        'buyer_phone': request.json.get('phone'),
        'buyer_bank': request.json.get('bank'),
        'buyer_account': request.json.get('account'),
    }
    
    # 1. 频率限制
    allowed, error = InvoiceRateLimit.check_user_limit(user_id)
    if not allowed:
        return jsonify({'error': error}), 429
    
    # 2. 欺诈检测
    warnings = InvoiceAntiFraud.detect_suspicious(user_id, invoice_data)
    
    if warnings:
        logger.warning(f"""
            可疑发票申请:
            user_id={user_id}
            order_id={order_id}
            warnings={warnings}
        """)
        
        # 金额较大或可疑，需要人工审核
        if any(w['type'] in ['HIGH_AMOUNT', 'TITLE_CHANGE'] for w in warnings):
            # 标记为待审核
            invoice_data['need_review'] = True
    
    # 3. 申请发票
    result, error = InvoiceService.apply_invoice(user_id, order_id, invoice_data)
    
    if error:
        return jsonify({'error': error}), 400
    
    result['warnings'] = warnings if warnings else None
    
    return jsonify(result)
```

**局限性**：
- 税号真实性验证需要对接税务局系统
- 金额较大时建议人工审核

#### 方案B：使用发票服务（低成本）

**工具/服务**：航信 / 百望 / 票通

**优势**：
- 自动验证税号真实性
- 对接税务系统
- 电子发票自动开具

**成本**：按开票量收费，约 0.1-0.5 元/张

### 决策树
```
发票是否限制每单一张？
├── 否 → 立即添加订单唯一约束（方案A）
└── 是 → 发票金额是否与订单一致？
    ├── 否 → 修改为订单金额（方案A）
    └── 是 → 是否验证税号格式？
        ├── 否 → 添加税号验证（方案A）
        └── 是 → 当前方案基本完善
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify, g
import re
from decimal import Decimal
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 税号验证
class TaxIDValidator:
    """
    税号验证器
    """
    
    # 15 位税号
    TAX_ID_15 = re.compile(r'^[0-9]{15}$')
    
    # 18 位统一社会信用代码
    USCC_18 = re.compile(r'^[0-9A-Z]{18}$')
    
    # 20 位税号
    TAX_ID_20 = re.compile(r'^[0-9A-Z]{20}$')
    
    @staticmethod
    def validate(tax_id):
        """
        验证税号格式
        """
        tax_id = tax_id.upper().strip()
        
        if not (TaxIDValidator.TAX_ID_15.match(tax_id) or
                TaxIDValidator.USCC_18.match(tax_id) or
                TaxIDValidator.TAX_ID_20.match(tax_id)):
            return False, None
        
        return True, tax_id

# 发票服务
class InvoiceService:
    """
    发票服务
    """
    
    # 税率配置
    TAX_RATES = {
        'normal': Decimal('0.06'),    # 普票 6%
        'special': Decimal('0.13'),   # 专票 13%
    }
    
    @staticmethod
    def apply(user_id, order_id, invoice_info):
        """
        申请发票
        """
        # 1. 检查订单
        order = db.query("""
            SELECT id, user_id, total_amount, status, invoice_status
            FROM orders
            WHERE id = ?
        """, order_id)
        
        if not order:
            return None, '订单不存在'
        
        if order.user_id != user_id:
            return None, '无权操作'
        
        if order.status != 'paid':
            return None, '订单未支付'
        
        if order.invoice_status != 'none':
            return None, '该订单已申请发票'
        
        # 2. 验证发票信息
        title = invoice_info.get('title', '').strip()
        tax_id = invoice_info.get('tax_id', '').strip()
        
        if len(title) < 2 or len(title) > 200:
            return None, '发票抬头长度不正确'
        
        valid, normalized_tax_id = TaxIDValidator.validate(tax_id)
        if not valid:
            return None, '税号格式不正确'
        
        # 3. 计算税额
        amount = Decimal(str(order.total_amount))
        tax_rate = Decimal('0.06')
        tax_amount = (amount / (1 + tax_rate) * tax_rate).quantize(Decimal('0.01'))
        
        # 4. 创建发票
        with db.transaction():
            db.execute("""
                UPDATE orders SET invoice_status = 'applied' WHERE id = ?
            """, order_id)
            
            invoice_id = db.execute("""
                INSERT INTO invoices
                    (user_id, order_id, buyer_title, buyer_tax_id,
                     buyer_address, buyer_phone, buyer_bank, buyer_account,
                     amount, tax_amount, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', NOW())
            """, user_id, order_id, title, normalized_tax_id,
                 invoice_info.get('address'), invoice_info.get('phone'),
                 invoice_info.get('bank'), invoice_info.get('account'),
                 amount, tax_amount)
        
        safe_logger.info(f"发票申请: invoice_id={invoice_id}, order_id={order_id}")
        
        return {'invoice_id': invoice_id, 'amount': float(amount)}, None

# API 接口
@app.route('/api/invoice/apply', methods=['POST'])
def apply_invoice():
    """申请发票"""
    user_id = g.user_id
    order_id = request.json.get('order_id')
    
    invoice_info = {
        'title': request.json.get('title'),
        'tax_id': request.json.get('tax_id'),
        'address': request.json.get('address'),
        'phone': request.json.get('phone'),
        'bank': request.json.get('bank'),
        'account': request.json.get('account'),
    }
    
    result, error = InvoiceService.apply(user_id, order_id, invoice_info)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result)

@app.route('/api/invoice/order/<int:order_id>', methods=['GET'])
def get_invoice(order_id):
    """获取发票"""
    user_id = g.user_id
    
    invoice = db.query("""
        SELECT i.* FROM invoices i
        JOIN orders o ON i.order_id = o.id
        WHERE i.order_id = ? AND o.user_id = ?
    """, order_id, user_id)
    
    if not invoice:
        return jsonify({'has_invoice': False})
    
    return jsonify({
        'has_invoice': True,
        'invoice': {
            'no': invoice.invoice_no,
            'title': invoice.buyer_title,
            'tax_id': invoice.buyer_tax_id,
            'amount': float(invoice.amount),
            'status': invoice.status,
        }
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **发票验证**：
   - 对接税务局系统验证税号
   - 黑名单检测
   - 异常发票预警

2. **开票控制**：
   - 多维度限制（频率、金额、数量）
   - 人工审核流程
   - 批量开票风控

3. **合规管理**：
   - 电子发票存档
   - 红字发票处理
   - 税务申报对接

4. **监控告警**：
   - 异常开票告警
   - 频繁修改抬头告警
   - 大额开票审核

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [增值税发票管理办法](http://www.chinatax.gov.cn/)
- [统一社会信用代码规则](http://www.gb688.cn/)
- [电子发票服务指南](https://www.51fapiao.cn/)
