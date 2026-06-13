# 价格操纵攻击

## 一句话风险
攻击者通过修改商品价格、折扣计算逻辑或利用定价规则漏洞，以远低于预期的价格购买商品。

## 风险等级
- 严重程度: 🔴严重
- 影响范围: 电商平台、SaaS订阅、在线服务
- 发生概率: 高

## 场景描述
独立开发者小王运营着一个软件授权商城，售卖不同版本的软件授权。商城支持多种定价策略：基础版99元、专业版299元、企业版999元。为了促销，小王还设计了一个"捆绑优惠"功能：同时购买多个商品可以享受折扣。某天，小王发现有用户以极低的价格购买了企业版授权，订单金额显示为正常价格，但实际支付金额却只有几块钱。经过调查发现，该用户在请求中添加了一个额外的discount参数，将折扣率设为0.99（即99%折扣），而后端代码在计算最终价格时，优先使用了前端传递的折扣参数而非系统设置的折扣规则。此外，还有用户发现通过修改数量参数为小数（如0.1），可以在保持总价不变的情况下获得错误的授权数量。价格操纵攻击往往利用的是开发者在价格计算逻辑上的疏忽，尤其是当价格计算涉及多个参数组合时，更容易出现漏洞。

## 攻击方式
1. 分析前端价格计算逻辑和请求参数
2. 尝试添加或修改折扣相关参数
3. 尝试负数折扣、超大折扣比例
4. 利用数量、单价、折扣的组合漏洞
5. 浮点数精度漏洞（如0.1 + 0.2 != 0.3）
6. 货币单位漏洞（如用日元价格匹配美元支付）

## 真实案例
- 2017年某航空公司票价计算漏洞，用户可自定义票价
- 2019年某电商平台优惠券叠加漏洞，商品免费还能赚积分
- 2020年某SaaS平台年付折扣计算错误，用户获得超低折扣

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查价格计算是否依赖前端参数
- [ ] 检查折扣计算逻辑是否有限制
- [ ] 搜索异常低价订单

### 短期加固 (1小时)
- [ ] 所有价格计算在后端完成，不信任前端参数
- [ ] 设置折扣上限（如最高90%折扣）
- [ ] 价格精度使用整数（分）避免浮点问题

### 长期建设
- [ ] 建立完整的价格引擎，统一管理定价规则
- [ ] 价格计算逻辑独立测试覆盖
- [ ] 建立价格异常监控告警
- [ ] 定期审计价格计算代码

## 检测方法
```sql
-- 检测折扣异常订单
SELECT o.id, o.total_amount, o.discount_rate,
       p.price as original_price,
       o.total_amount / p.price as actual_rate
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE o.total_amount / p.price < 0.1; -- 折扣超过90%

-- 检测数量异常
SELECT * FROM orders WHERE quantity <= 0 OR quantity != FLOOR(quantity);

-- 检测价格与预期不符
SELECT o.id, o.paid_amount, p.price * o.quantity as expected_amount
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE ABS(o.paid_amount - p.price * o.quantity) > 0.01;
```

## 代码示例
```javascript
// ❌ 错误做法：信任前端折扣参数
app.post('/api/order', async (req, res) => {
  const { productId, quantity, discount } = req.body;

  const product = await db.getProductById(productId);
  let total = product.price * quantity;

  // 危险：使用前端传递的折扣
  if (discount) {
    total = total * (1 - discount);
  }

  await db.createOrder({ productId, quantity, total });
});

// ❌ 错误做法：折扣计算无上限
app.post('/api/order', async (req, res) => {
  const { productId, couponCode } = req.body;

  let discount = 0;
  if (couponCode) {
    const coupon = await db.getCoupon(couponCode);
    discount = coupon.discount; // 可能是任意值
  }

  // 危险：未限制折扣上限
  const total = product.price * (1 - discount);
});

// ✅ 正确做法：完整的价格计算逻辑
const MAX_DISCOUNT_RATE = 0.9; // 最高90%折扣
const MIN_ORDER_AMOUNT = 100; // 最小订单金额（分）

class PriceEngine {
  constructor(db) {
    this.db = db;
  }

  async calculateOrder(params) {
    const { productId, quantity, couponCode, userId } = params;

    // 1. 参数校验
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > 100) {
      throw new Error('数量参数无效');
    }

    // 2. 获取商品信息（从数据库）
    const product = await this.db.getProductById(productId);
    if (!product || !product.active) {
      throw new Error('商品不存在或已下架');
    }

    // 3. 基础价格计算（使用整数分，避免浮点问题）
    let totalAmount = Math.round(product.price * 100) * quantity;

    // 4. 折扣计算
    let discountAmount = 0;
    let discountDetails = [];

    // 4.1 会员折扣
    const user = await this.db.getUserById(userId);
    if (user.memberLevel) {
      const memberDiscount = this.getMemberDiscount(user.memberLevel);
      const memberSaving = Math.round(totalAmount * memberDiscount);
      discountAmount += memberSaving;
      discountDetails.push({ type: 'member', rate: memberDiscount, amount: memberSaving });
    }

    // 4.2 优惠券折扣
    if (couponCode) {
      const coupon = await this.validateCoupon(couponCode, userId, productId, totalAmount);
      if (coupon) {
        let couponSaving = 0;
        if (coupon.type === 'percent') {
          couponSaving = Math.round(totalAmount * coupon.value / 100);
        } else if (coupon.type === 'fixed') {
          couponSaving = coupon.value;
        }
        discountAmount += couponSaving;
        discountDetails.push({ type: 'coupon', code: couponCode, amount: couponSaving });
      }
    }

    // 5. 折扣上限检查
    const maxDiscount = Math.round(totalAmount * MAX_DISCOUNT_RATE);
    if (discountAmount > maxDiscount) {
      console.warn(`折扣超限: ${discountAmount} > ${maxDiscount}, orderId=${params.orderId}`);
      discountAmount = maxDiscount;
      discountDetails.push({ type: 'limit', message: '折扣已达到上限' });
    }

    // 6. 最终金额计算
    const finalAmount = totalAmount - discountAmount;

    if (finalAmount < MIN_ORDER_AMOUNT) {
      throw new Error(`订单金额不能小于${MIN_ORDER_AMOUNT / 100}元`);
    }

    return {
      originalAmount: totalAmount,
      discountAmount,
      finalAmount,
      discountDetails,
      priceSource: 'server_calculated'
    };
  }

  getMemberDiscount(level) {
    const discounts = {
      'silver': 0.05,
      'gold': 0.1,
      'platinum': 0.15
    };
    return discounts[level] || 0;
  }

  async validateCoupon(code, userId, productId, orderAmount) {
    const coupon = await this.db.getCouponByCode(code);

    if (!coupon) return null;
    if (coupon.expired) return null;
    if (coupon.usedCount >= coupon.maxUsage) return null;
    if (orderAmount < coupon.minOrderAmount) return null;

    // 检查用户是否已使用
    const used = await this.db.checkCouponUsed(userId, code);
    if (used) return null;

    // 检查商品限制
    if (coupon.applicableProducts && !coupon.applicableProducts.includes(productId)) {
      return null;
    }

    return coupon;
  }
}

// 使用价格引擎
app.post('/api/order', async (req, res) => {
  const { productId, quantity, couponCode } = req.body;
  const userId = req.user.id;

  const priceEngine = new PriceEngine(db);

  try {
    const priceResult = await priceEngine.calculateOrder({
      productId,
      quantity,
      couponCode,
      userId
    });

    const order = await db.createOrder({
      userId,
      productId,
      quantity,
      originalAmount: priceResult.originalAmount,
      discountAmount: priceResult.discountAmount,
      finalAmount: priceResult.finalAmount,
      discountDetails: JSON.stringify(priceResult.discountDetails),
      priceCalculatedAt: new Date()
    });

    res.json({
      orderId: order.id,
      amount: priceResult.finalAmount / 100, // 转为元显示
      discount: priceResult.discountDetails
    });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});
```

## 参考资料
- [电商价格计算安全实践](https://www.infoq.cn/article/ecommerce-price-security)
- [浮点数精度问题及解决方案](https://0.30000000000000004.com/)
- [OWASP - Business Logic Vulnerabilities](https://owasp.org/www-community/vulnerabilities/Business_Logic_Vulnerabilities)
