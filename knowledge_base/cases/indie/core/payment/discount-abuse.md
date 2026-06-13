# 优惠券滥用攻击

## 一句话风险
攻击者通过批量获取、重复使用、叠加使用或伪造优惠券，获取不当折扣或套利。

## 风险等级
- 严重程度: 🟠高
- 影响范围: 所有支持优惠券/折扣码的电商和服务平台
- 发生概率: 高

## 场景描述
独立开发者小张经营着一个在线教育平台，为了推广新课程，发放了一批"满100减50"的优惠券。每张优惠券设计为单用户单次使用，有效期一个月。活动开始后不久，小张发现平台收入大幅下降，但订单量却暴增。经过调查发现，有人通过脚本批量注册了大量新账号，每个账号都领取了优惠券，然后以半价购买课程。更糟糕的是，有用户发现系统存在优惠券叠加漏洞，可以在同一订单中使用多张优惠券，最终免费获得商品甚至"负价"购买触发退款。优惠券滥用是电商和SaaS平台最常见的欺诈行为之一，攻击者利用平台的营销机制漏洞，造成严重的经济损失。更隐蔽的滥用方式包括：使用生成器猜测优惠券码、利用已过期但未失效的优惠券、将优惠券转卖给他人等。

## 攻击方式
1. 批量注册账号领取新用户优惠券
2. 脚本自动化抢夺限量优惠券
3. 发现并利用优惠券叠加漏洞
4. 暴力猜测优惠券码
5. 重复使用单次优惠券
6. 使用他人的专属优惠券
7. 利用时间差使用已过期优惠券

## 真实案例
- 2019年某外卖平台被薅羊毛损失超千万
- 2020年某电商平台优惠券叠加漏洞，用户免费购物
- 2021年星巴克优惠券漏洞被大量滥用

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查优惠券是否有使用次数限制
- [ ] 检查是否允许优惠券叠加
- [ ] 搜索异常使用优惠券的订单

### 短期加固 (1小时)
- [ ] 添加优惠券使用次数校验
- [ ] 禁止优惠券叠加或设置上限
- [ ] 添加用户维度使用限制

### 长期建设
- [ ] 实现优惠券风控系统
- [ ] 建立用户行为分析，识别薅羊毛
- [ ] 优惠券码使用加密签名
- [ ] 建立黑名单机制

## 检测方法
```sql
-- 检测同一优惠券被多次使用
SELECT coupon_code, COUNT(*) as usage_count
FROM orders
WHERE coupon_code IS NOT NULL
GROUP BY coupon_code
HAVING usage_count > 1;

-- 检测批量注册薅羊毛
SELECT DATE(created_at) as date,
       COUNT(*) as new_users,
       SUM(CASE WHEN first_order_coupon THEN 1 ELSE 0 END) as coupon_users
FROM users
WHERE created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(created_at)
HAVING coupon_users / new_users > 0.8;

-- 检测优惠券叠加
SELECT id, coupon_codes, total_amount, original_amount
FROM orders
WHERE JSON_LENGTH(coupon_codes) > 1
  AND total_amount < original_amount * 0.3;
```

## 代码示例
```javascript
// ❌ 错误做法：无使用限制的优惠券
app.post('/api/order', async (req, res) => {
  const { productId, couponCode } = req.body;

  let total = await getProductPrice(productId);

  if (couponCode) {
    const coupon = await db.getCoupon(couponCode);
    // 危险：未检查使用次数、用户限制等
    total -= coupon.discount;
  }

  await db.createOrder({ total, couponCode });
});

// ❌ 错误做法：允许优惠券叠加
app.post('/api/order', async (req, res) => {
  const { productId, couponCodes } = req.body; // 数组

  let total = await getProductPrice(productId);

  // 危险：无限叠加
  for (const code of couponCodes) {
    const coupon = await db.getCoupon(code);
    total -= coupon.discount;
  }

  await db.createOrder({ total });
});

// ✅ 正确做法：完整的优惠券校验
class CouponService {
  constructor(db, cache) {
    this.db = db;
    this.cache = cache;
  }

  async validateCoupon(code, userId, orderId, orderAmount) {
    const coupon = await this.db.getCouponByCode(code);

    if (!coupon) {
      return { valid: false, error: '优惠券不存在' };
    }

    // 1. 基本状态校验
    if (!coupon.active) {
      return { valid: false, error: '优惠券已失效' };
    }

    // 2. 有效期校验
    const now = new Date();
    if (coupon.startTime && now < coupon.startTime) {
      return { valid: false, error: '优惠券尚未生效' };
    }
    if (coupon.endTime && now > coupon.endTime) {
      return { valid: false, error: '优惠券已过期' };
    }

    // 3. 总使用次数校验
    if (coupon.maxUsage && coupon.usedCount >= coupon.maxUsage) {
      return { valid: false, error: '优惠券已被领完' };
    }

    // 4. 单用户使用次数校验
    const userUsage = await this.db.getUserCouponUsage(userId, code);
    if (coupon.maxUsagePerUser && userUsage >= coupon.maxUsagePerUser) {
      return { valid: false, error: '您已使用过此优惠券' };
    }

    // 5. 新用户限制校验
    if (coupon.newUserOnly) {
      const userOrders = await this.db.getUserOrderCount(userId);
      if (userOrders > 0) {
        return { valid: false, error: '此优惠券仅限新用户' };
      }
    }

    // 6. 最低金额校验
    if (coupon.minOrderAmount && orderAmount < coupon.minOrderAmount) {
      return { valid: false, error: `订单金额需满${coupon.minOrderAmount}元` };
    }

    // 7. 适用商品校验
    if (coupon.applicableProducts) {
      // 需要在调用方传入商品ID进行校验
    }

    // 8. 签名校验（防止伪造优惠券码）
    if (coupon.signed) {
      const expectedSign = this.generateCouponSign(coupon);
      if (coupon.sign !== expectedSign) {
        await securityLog.record({
          type: 'coupon_sign_invalid',
          code,
          userId
        });
        return { valid: false, error: '优惠券无效' };
      }
    }

    return {
      valid: true,
      coupon,
      discount: this.calculateDiscount(coupon, orderAmount)
    };
  }

  calculateDiscount(coupon, orderAmount) {
    if (coupon.type === 'percent') {
      return Math.round(orderAmount * coupon.value / 100);
    } else if (coupon.type === 'fixed') {
      return Math.min(coupon.value, orderAmount);
    }
    return 0;
  }

  // 生成带签名的优惠券码
  generateCouponCode(params) {
    const secret = process.env.COUPON_SECRET;
    const data = `${params.type}:${params.value}:${params.expiry}`;
    const sign = crypto
      .createHmac('sha256', secret)
      .update(data)
      .digest('hex')
      .substring(0, 8);

    return `${params.prefix}-${sign}`.toUpperCase();
  }
}

// 订单处理
const couponService = new CouponService(db, cache);
const MAX_COUPONS_PER_ORDER = 1;
const MAX_DISCOUNT_RATE = 0.9;

app.post('/api/order', async (req, res) => {
  const { productId, quantity, couponCodes } = req.body;
  const userId = req.user.id;

  // 基础价格
  const product = await db.getProductById(productId);
  let totalAmount = product.price * quantity;
  let originalAmount = totalAmount;

  // 优惠券处理
  let appliedCoupons = [];

  if (couponCodes && couponCodes.length > 0) {
    // 限制单订单优惠券数量
    if (couponCodes.length > MAX_COUPONS_PER_ORDER) {
      return res.status(400).json({
        error: `单订单最多使用${MAX_COUPONS_PER_ORDER}张优惠券`
      });
    }

    for (const code of couponCodes) {
      const result = await couponService.validateCoupon(
        code,
        userId,
        null,
        totalAmount
      );

      if (!result.valid) {
        return res.status(400).json({ error: result.error });
      }

      // 检查折扣上限
      const newTotal = totalAmount - result.discount;
      const discountRate = (originalAmount - newTotal) / originalAmount;

      if (discountRate > MAX_DISCOUNT_RATE) {
        return res.status(400).json({
          error: '折扣已达上限，无法使用更多优惠券'
        });
      }

      totalAmount = newTotal;
      appliedCoupons.push({
        code,
        discount: result.discount,
        couponId: result.coupon.id
      });
    }
  }

  // 最终金额校验
  if (totalAmount < 0.01) {
    return res.status(400).json({ error: '订单金额异常' });
  }

  // 创建订单
  const order = await db.transaction(async (trx) => {
    const order = await trx.createOrder({
      userId,
      productId,
      quantity,
      originalAmount,
      totalAmount,
      couponDetails: JSON.stringify(appliedCoupons)
    });

    // 记录优惠券使用
    for (const coupon of appliedCoupons) {
      await trx.useCoupon(coupon.couponId, userId, order.id);
    }

    return order;
  });

  res.json({ orderId: order.id, totalAmount, appliedCoupons });
});

// ✅ 防批量注册薅羊毛
async function checkRegistrationFraud(req, res, next) {
  const ip = req.ip;
  const deviceId = req.body.deviceId;

  // IP维度限制
  const ipRegistrations = await cache.incr(`reg:ip:${ip}`);
  if (ipRegistrations > 3) {
    return res.status(429).json({ error: '注册过于频繁' });
  }

  // 设备维度限制
  if (deviceId) {
    const deviceRegistrations = await cache.incr(`reg:device:${deviceId}`);
    if (deviceRegistrations > 1) {
      return res.status(429).json({ error: '该设备已注册' });
    }
  }

  next();
}
```

## 参考资料
- [优惠券系统设计最佳实践](https://tech.meituan.com/2017/07/20/coupon-system.html)
- [防薅羊毛策略](https://www.infoq.cn/article/anti-wool-gathering)
- [OWASP - Uncontrolled Resource Consumption](https://owasp.org/www-community/vulnerabilities/Uncontrolled_Resource_Consumption)
