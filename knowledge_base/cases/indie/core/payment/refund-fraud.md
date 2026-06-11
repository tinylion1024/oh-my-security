# 退款欺诈 - 独立开发者版

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
用户购买课程后立即申请退款，既保留了课程访问权限，又拿回了钱款，你的损失：商品价值 + 手续费损失 + 时间成本。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 自动化退款流程，无需人工审核
- [ ] 退款后未立即收回商品或服务
- [ ] 数字商品可无限次访问
- [ ] 未设置退款时间窗口限制
→ 勾选≥1项，即需关注此风险

### 一句话防御
**退款必须关联商品回收**：退款前验证商品状态，退款后立即收回访问权限，并设置合理的退款时间窗口和风控规则。

### 快速行动清单
1. [ ] 立即行动项：检查退款流程，确认退款后是否收回商品访问权限（今天可完成，免费）
2. [ ] 短期行动项：添加退款风控规则（如购买后 24 小时内不可退款）（本周可完成，免费）
3. [ ] 长期行动项：实现退款审核流程，大额退款人工审核（规划中，免费）

### 推荐工具
- 免费：直接修改代码（如示例代码）
- 低成本：使用支付平台的退款审核功能

### 验证方法
- [ ] 完成一次购买
- [ ] 立即申请退款
- [ ] 确认退款后无法访问商品
- [ ] 确认有合理的退款审核流程

---

## L2 小团队版（理解版）

### 场景还原
你的在线课程平台用户购买了 ¥999 的"Python 高级编程"课程，下载了所有课程资料，然后立即申请退款，理由是"课程质量不好"。你的系统自动处理了退款，用户收到了 ¥999 退款，但课程访问权限没有被收回。用户既拿到了课程，又拿回了钱。

更严重的是，用户在社区分享了这种"白嫖"方法，引发了大规模的退款欺诈，你的平台损失数万元，还要承担支付手续费损失。

### 攻击路径（简化版）
1. **正常购买**：用户购买商品或服务，获取访问权限
2. **使用商品**：用户下载资料、观看课程、使用服务
3. **申请退款**：用户找到理由（质量不好、描述不符等）申请退款
4. **既得利益**：退款成功但商品访问权限未收回，用户白嫖成功

### 防御实施（低成本方案）

#### 方案A：免费方案（推荐）

**核心原则**：退款必须关联商品回收，并设置风控规则。

**工具/服务**：直接修改代码

**配置步骤**：

1. **识别风险代码**：
```python
# ❌ 错误做法：退款后未收回商品
@app.route('/api/refund', methods=['POST'])
def refund_order():
    order_id = request.json.get('order_id')
    reason = request.json.get('reason')
    
    # 直接退款
    refund = payment_gateway.refund(order_id)
    
    # 更新订单状态
    db.execute("UPDATE orders SET status = 'refunded' WHERE id = ?", order_id)
    
    # 问题：未收回商品访问权限！
    
    return {'refund_id': refund.id}
```

2. **修复代码**：
```python
# ✅ 正确做法：退款前验证，退款后收回商品
@app.route('/api/refund', methods=['POST'])
def refund_order():
    order_id = request.json.get('order_id')
    reason = request.json.get('reason')
    user_id = current_user.id
    
    # 1. 查询订单
    order = db.query("""
        SELECT id, user_id, product_id, amount, status, created_at
        FROM orders
        WHERE id = ? AND user_id = ?
    """, order_id, user_id)
    
    if not order:
        return {'error': '订单不存在'}, 404
    
    # 2. 验证订单状态
    if order.status != 'paid':
        return {'error': '订单状态不支持退款'}, 400
    
    # 3. 检查退款时间窗口（如购买后 7 天内可退款）
    days_since_purchase = (datetime.now() - order.created_at).days
    if days_since_purchase > 7:
        return {'error': '已超过退款期限（购买后 7 天内可退款）'}, 400
    
    # 4. 检查商品使用情况
    usage = db.query("""
        SELECT 
            COUNT(*) as view_count,
            MAX(viewed_at) as last_view_time,
            SUM(duration) as total_duration
        FROM course_views
        WHERE user_id = ? AND course_id = ?
    """, user_id, order.product_id)
    
    # 如果观看进度超过 30%，需要人工审核
    course = db.query("SELECT total_duration FROM courses WHERE id = ?", order.product_id)
    if usage.total_duration and course.total_duration:
        progress = usage.total_duration / course.total_duration
        if progress > 0.3:
            # 创建退款申请，等待人工审核
            db.execute("""
                INSERT INTO refund_requests (order_id, user_id, reason, progress, status, created_at)
                VALUES (?, ?, ?, ?, 'pending', NOW())
            """, order_id, user_id, reason, progress)
            
            send_admin_notification(f"需要审核的退款申请：订单 {order_id}，观看进度 {progress:.1%}")
            
            return {'message': '退款申请已提交，等待审核'}
    
    # 5. 检查是否已下载资料
    downloads = db.query("""
        SELECT COUNT(*) as count
        FROM download_logs
        WHERE user_id = ? AND product_id = ?
    """, user_id, order.product_id)
    
    if downloads.count > 0:
        # 已下载资料，需要人工审核
        db.execute("""
            INSERT INTO refund_requests (order_id, user_id, reason, downloads, status, created_at)
            VALUES (?, ?, ?, ?, 'pending', NOW())
        """, order_id, user_id, reason, downloads.count)
        
        return {'message': '由于您已下载资料，退款申请需要人工审核'}
    
    # 6. 执行退款
    try:
        refund = payment_gateway.refund(order_id)
    except Exception as e:
        logger.error(f"退款失败: order_id={order_id}, error={e}")
        return {'error': '退款失败'}, 500
    
    # 7. 收回商品访问权限
    db.execute("""
        DELETE FROM user_products
        WHERE user_id = ? AND product_id = ?
    """, user_id, order.product_id)
    
    # 8. 更新订单状态
    db.execute("""
        UPDATE orders
        SET status = 'refunded', refunded_at = NOW()
        WHERE id = ?
    """, order_id)
    
    # 9. 记录退款日志
    logger.info(f"""
        退款成功:
        order_id={order_id}
        user_id={user_id}
        amount={order.amount}
        refund_id={refund.id}
    """)
    
    return {
        'refund_id': refund.id,
        'message': '退款成功，商品访问权限已收回'
    }
```

3. **添加风控规则**：
```python
# 退款风控规则配置
REFUND_RULES = {
    # 时间窗口：购买后 X 天内可退款
    'time_window_days': 7,
    
    # 使用进度阈值：超过 X% 需要人工审核
    'progress_threshold': 0.3,
    
    # 下载限制：下载过资料需要人工审核
    'require_review_if_downloaded': True,
    
    # 用户退款历史：退款次数过多需要人工审核
    'max_auto_refunds': 2,  # 每年最多 2 次自动退款
    'refund_history_days': 365,
}

def check_refund_eligibility(user_id, order):
    """
    检查用户是否可以申请退款
    
    Returns:
        (eligible, requires_review, reason)
    """
    # 检查时间窗口
    days_since_purchase = (datetime.now() - order.created_at).days
    if days_since_purchase > REFUND_RULES['time_window_days']:
        return False, False, f'已超过 {REFUND_RULES["time_window_days"]} 天退款期限'
    
    # 检查用户退款历史
    refund_count = db.query("""
        SELECT COUNT(*) as count
        FROM orders o
        WHERE o.user_id = ?
          AND o.status = 'refunded'
          AND o.refunded_at > DATE_SUB(NOW(), INTERVAL ? DAY)
    """, user_id, REFUND_RULES['refund_history_days'])
    
    if refund_count.count >= REFUND_RULES['max_auto_refunds']:
        return True, True, '您的退款申请需要人工审核（历史退款次数较多）'
    
    # 检查商品使用情况
    usage = check_product_usage(user_id, order.product_id)
    if usage['progress'] > REFUND_RULES['progress_threshold']:
        return True, True, f'课程观看进度超过 {REFUND_RULES["progress_threshold"]:.0%}，需要人工审核'
    
    if usage['downloads'] > 0 and REFUND_RULES['require_review_if_downloaded']:
        return True, True, '已下载资料，需要人工审核'
    
    return True, False, '可以申请退款'
```

**局限性**：
- 需要追踪商品使用情况
- 需要维护退款审核流程

#### 方案B：使用支付平台保护（低成本）

**工具/服务**：Stripe / Paddle

**优势**：
- Stripe Dashboard 可以设置退款规则
- 可以要求退款前联系客服

**配置步骤**：
```python
# Stripe 退款配置
import stripe

# 方案 1：禁用自动退款，要求用户联系客服
@app.route('/api/refund-request', methods=['POST'])
def refund_request():
    order_id = request.json.get('order_id')
    reason = request.json.get('reason')
    
    # 创建退款申请，不立即退款
    db.execute("""
        INSERT INTO refund_requests (order_id, user_id, reason, status, created_at)
        VALUES (?, ?, ?, 'pending', NOW())
    """, order_id, current_user.id, reason)
    
    # 发送邮件通知客服
    send_admin_email(f"新的退款申请：订单 {order_id}")
    
    return {'message': '退款申请已提交，我们会在 1-3 个工作日内处理'}

# 方案 2：管理端审核后执行退款
@app.route('/admin/refund/approve', methods=['POST'])
def approve_refund():
    refund_request_id = request.json.get('refund_request_id')
    admin_id = current_user.id
    
    # 查询退款申请
    refund_request = db.query("""
        SELECT rr.*, o.user_id, o.product_id, o.payment_id
        FROM refund_requests rr
        JOIN orders o ON rr.order_id = o.id
        WHERE rr.id = ?
    """, refund_request_id)
    
    # 执行 Stripe 退款
    refund = stripe.Refund.create(
        payment_intent=refund_request.payment_id,
    )
    
    # 收回商品
    db.execute("""
        DELETE FROM user_products
        WHERE user_id = ? AND product_id = ?
    """, refund_request.user_id, refund_request.product_id)
    
    # 更新状态
    db.execute("""
        UPDATE refund_requests
        SET status = 'approved', approved_by = ?, approved_at = NOW()
        WHERE id = ?
    """, admin_id, refund_request_id)
    
    db.execute("UPDATE orders SET status = 'refunded' WHERE id = ?", refund_request.order_id)
    
    return {'refund_id': refund.id}
```

**成本**：Stripe 手续费 2.9% + $0.30/笔，退款手续费根据银行政策

### 决策树
```
退款流程是否收回商品？
├── 否 → 立即添加商品回收逻辑（方案A）
└── 是 → 是否有退款时间窗口？
    ├── 否 → 添加时间窗口限制（方案A）
    └── 是 → 是否检查商品使用情况？
        ├── 否 → 添加使用情况检查（方案A）
        └── 是 → 是否有退款审核流程？
            ├── 否 → 添加人工审核流程（方案A）
            └── 是 → 当前方案基本完善
```

### 代码示例（完整版）

```python
from flask import Flask, request, jsonify, current_user
from database import db
from payment_gateway import payment_gateway
import logging
from datetime import datetime, timedelta

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 退款规则配置
REFUND_CONFIG = {
    'time_window_days': 7,
    'progress_threshold': 0.3,
    'max_auto_refunds_per_year': 2,
    'require_review_if_downloaded': True,
}

class RefundService:
    @staticmethod
    def check_eligibility(user_id, order):
        """
        检查退款资格
        """
        result = {
            'eligible': True,
            'requires_review': False,
            'reasons': [],
            'warnings': [],
        }
        
        # 1. 检查订单状态
        if order.status != 'paid':
            result['eligible'] = False
            result['reasons'].append('订单状态不支持退款')
            return result
        
        # 2. 检查时间窗口
        days_since_purchase = (datetime.now() - order.created_at).days
        if days_since_purchase > REFUND_CONFIG['time_window_days']:
            result['eligible'] = False
            result['reasons'].append(f'已超过 {REFUND_CONFIG["time_window_days"]} 天退款期限')
            return result
        
        if days_since_purchase > 3:
            result['warnings'].append(f'购买已 {days_since_purchase} 天，退款需要审核')
            result['requires_review'] = True
        
        # 3. 检查用户退款历史
        refund_history = db.query("""
            SELECT COUNT(*) as count
            FROM orders
            WHERE user_id = ?
              AND status = 'refunded'
              AND refunded_at > DATE_SUB(NOW(), INTERVAL 365 DAY)
        """, user_id)
        
        if refund_history.count >= REFUND_CONFIG['max_auto_refunds_per_year']:
            result['warnings'].append('历史退款次数较多，需要人工审核')
            result['requires_review'] = True
        
        # 4. 检查商品使用情况
        usage = RefundService.get_product_usage(user_id, order.product_id)
        
        if usage['progress'] > REFUND_CONFIG['progress_threshold']:
            result['warnings'].append(f'课程观看进度 {usage["progress"]:.1%}，需要审核')
            result['requires_review'] = True
        
        if usage['downloads'] > 0:
            result['warnings'].append(f'已下载 {usage["downloads"]} 个资料文件')
            if REFUND_CONFIG['require_review_if_downloaded']:
                result['requires_review'] = True
        
        if usage['certificate_issued']:
            result['warnings'].append('已获得课程证书，不支持退款')
            result['eligible'] = False
        
        return result
    
    @staticmethod
    def get_product_usage(user_id, product_id):
        """
        获取商品使用情况
        """
        # 获取观看进度
        course = db.query("""
            SELECT c.id, c.total_duration
            FROM courses c
            WHERE c.product_id = ?
        """, product_id)
        
        if course:
            views = db.query("""
                SELECT 
                    COUNT(*) as view_count,
                    SUM(duration) as total_duration
                FROM course_views
                WHERE user_id = ? AND course_id = ?
            """, user_id, course.id)
            
            progress = 0
            if views.total_duration and course.total_duration:
                progress = views.total_duration / course.total_duration
        else:
            progress = 0
        
        # 获取下载数量
        downloads = db.query("""
            SELECT COUNT(*) as count
            FROM download_logs
            WHERE user_id = ? AND product_id = ?
        """, user_id, product_id)
        
        # 检查是否已获得证书
        certificate = db.query("""
            SELECT id FROM certificates
            WHERE user_id = ? AND product_id = ?
        """, user_id, product_id)
        
        return {
            'progress': progress,
            'downloads': downloads.count if downloads else 0,
            'certificate_issued': bool(certificate),
        }
    
    @staticmethod
    def create_refund_request(order_id, user_id, reason):
        """
        创建退款申请
        """
        # 查询订单
        order = db.query("""
            SELECT id, user_id, product_id, amount, status, created_at
            FROM orders
            WHERE id = ? AND user_id = ?
        """, order_id, user_id)
        
        if not order:
            return None, '订单不存在'
        
        # 检查资格
        eligibility = RefundService.check_eligibility(user_id, order)
        
        if not eligibility['eligible']:
            return None, '; '.join(eligibility['reasons'])
        
        # 创建退款申请
        refund_request_id = db.execute("""
            INSERT INTO refund_requests
                (order_id, user_id, product_id, amount, reason, 
                 requires_review, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'pending', NOW())
            RETURNING id
        """, order_id, user_id, order.product_id, order.amount, 
           reason, eligibility['requires_review'])
        
        # 如果需要审核，发送通知
        if eligibility['requires_review']:
            send_admin_notification(
                f"需要审核的退款申请\n"
                f"申请ID: {refund_request_id}\n"
                f"订单ID: {order_id}\n"
                f"金额: ¥{order.amount/100}\n"
                f"原因: {reason}\n"
                f"警告: {'; '.join(eligibility['warnings'])}"
            )
        else:
            # 自动处理退款
            RefundService.process_auto_refund(refund_request_id)
        
        return refund_request_id, None
    
    @staticmethod
    def process_auto_refund(refund_request_id):
        """
        自动处理退款
        """
        refund_request = db.query("""
            SELECT rr.*, o.payment_id
            FROM refund_requests rr
            JOIN orders o ON rr.order_id = o.id
            WHERE rr.id = ?
        """, refund_request_id)
        
        # 执行退款
        refund = payment_gateway.refund(
            payment_id=refund_request.payment_id,
            amount=refund_request.amount
        )
        
        # 收回商品
        db.execute("""
            DELETE FROM user_products
            WHERE user_id = ? AND product_id = ?
        """, refund_request.user_id, refund_request.product_id)
        
        # 更新状态
        db.execute("""
            UPDATE refund_requests
            SET status = 'approved', refund_id = ?, processed_at = NOW()
            WHERE id = ?
        """, refund.id, refund_request_id)
        
        db.execute("""
            UPDATE orders SET status = 'refunded', refunded_at = NOW()
            WHERE id = ?
        """, refund_request.order_id)
        
        logger.info(f"自动退款成功: request_id={refund_request_id}")
    
    @staticmethod
    def admin_approve_refund(refund_request_id, admin_id, admin_note=None):
        """
        管理员批准退款
        """
        refund_request = db.query("""
            SELECT rr.*, o.payment_id
            FROM refund_requests rr
            JOIN orders o ON rr.order_id = o.id
            WHERE rr.id = ? AND rr.status = 'pending'
        """, refund_request_id)
        
        if not refund_request:
            return False, '退款申请不存在或已处理'
        
        # 执行退款
        refund = payment_gateway.refund(
            payment_id=refund_request.payment_id,
            amount=refund_request.amount
        )
        
        # 收回商品
        db.execute("""
            DELETE FROM user_products
            WHERE user_id = ? AND product_id = ?
        """, refund_request.user_id, refund_request.product_id)
        
        # 更新状态
        db.execute("""
            UPDATE refund_requests
            SET status = 'approved',
                refund_id = ?,
                approved_by = ?,
                admin_note = ?,
                processed_at = NOW()
            WHERE id = ?
        """, refund.id, admin_id, admin_note, refund_request_id)
        
        db.execute("""
            UPDATE orders SET status = 'refunded', refunded_at = NOW()
            WHERE id = ?
        """, refund_request.order_id)
        
        logger.info(f"管理员批准退款: request_id={refund_request_id}, admin_id={admin_id}")
        
        return True, None

@app.route('/api/refund/request', methods=['POST'])
def create_refund():
    """
    创建退款申请
    """
    try:
        order_id = request.json.get('order_id')
        reason = request.json.get('reason')
        user_id = current_user.id
        
        request_id, error = RefundService.create_refund_request(
            order_id, user_id, reason
        )
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'refund_request_id': request_id,
            'message': '退款申请已提交'
        })
        
    except Exception as e:
        logger.error(f"创建退款申请异常: {e}")
        return jsonify({'error': '系统错误'}), 500

@app.route('/admin/refund/approve', methods=['POST'])
def approve_refund():
    """
    管理员批准退款
    """
    try:
        refund_request_id = request.json.get('refund_request_id')
        admin_note = request.json.get('admin_note')
        admin_id = current_user.id
        
        success, error = RefundService.admin_approve_refund(
            refund_request_id, admin_id, admin_note
        )
        
        if not success:
            return jsonify({'error': error}), 400
        
        return jsonify({'message': '退款已批准'})
        
    except Exception as e:
        logger.error(f"批准退款异常: {e}")
        return jsonify({'error': '系统错误'}), 500

def send_admin_notification(message):
    """发送管理员通知"""
    # 实现通知逻辑
    pass
```

---

## L3 企业版（深耕版）

### 完整防御体系

企业级防御需要考虑更多维度：

1. **退款风控**：
   - 用户退款历史分析
   - 商品使用情况追踪
   - 异常退款模式检测

2. **商品回收**：
   - 自动收回访问权限
   - 撤销证书和凭证
   - 清理下载数据

3. **审核流程**：
   - 多级审核机制
   - 自动审核规则
   - 人工介入条件

4. **损失追回**：
   - 法律手段
   - 账号封禁
   - 黑名单机制

### 相关企业案例

参考 `cases/enterprise/bizsec/03-transaction/` 目录中的完整企业级案例。

---

## 延伸阅读

- [退款欺诈防范指南](https://stripe.com/docs/disputes)
- [电商平台退款风险管理](https://www.shopify.com/blog/refund-fraud)
- [数字商品退款策略](https://www.paddle.com/blog/saas-refund-policy)
