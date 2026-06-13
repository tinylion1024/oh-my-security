# 货币单位攻击

## 一句话风险
攻击者利用不同货币单位的价格差异或单位换算漏洞，以低价货币购买高价货币的商品。

## 风险等级
- 严重程度: 🔴严重
- 影响范围: 支持多货币的跨境电商、国际化SaaS平台
- 发生概率: 中

## 场景描述
独立开发者小李运营着一个面向全球用户的SaaS订阅服务，支持美元和人民币两种货币定价。为了方便用户，系统在支付时根据用户的地区自动选择货币。某天，小李发现收入数据异常，大量订阅订单的金额显示为几美元，而系统日志显示这些用户来自高消费地区。经过调查发现，有用户通过修改请求中的货币参数，将本应使用人民币（CNY）定价的订单强制使用日元（JPY）定价。由于日元对人民币的汇率差异（1日元≈0.05人民币），用户实际只支付了原价的几十分之一。更严重的是，小李的系统在货币转换时没有实时获取汇率，而是使用固定汇率，且不同货币的商品定价没有按汇率等比例设置，导致存在套利空间。货币单位攻击在国际化的支付系统中尤其危险，因为不同货币之间的价格差异可能高达数十倍。

## 攻击方式
1. 分析支持的货币列表和各货币定价
2. 对比不同货币的价格换算后的差异
3. 选择价格最低的货币进行支付
4. 修改请求中的货币参数
5. 或利用汇率更新延迟进行套利
6. 部分系统可能直接接受任意货币参数

## 真实案例
- 2019年某跨境电商货币漏洞，用户用日元价格购买美元定价商品
- 2020年某游戏平台地区定价漏洞，通过修改地区获得低价
- Steam平台曾多次出现跨区价格套利问题

## 防御建议

### 立即行动 (5分钟)
- [ ] 检查是否信任前端传递的货币参数
- [ ] 检查各货币定价是否与汇率一致
- [ ] 搜索异常货币的订单记录

### 短期加固 (1小时)
- [ ] 货币选择基于用户注册地区，不信任前端参数
- [ ] 实现实时汇率校验
- [ ] 添加货币与价格一致性检查

### 长期建设
- [ ] 统一使用单一货币结算，前端展示时转换
- [ ] 建立汇率监控系统，异常波动告警
- [ ] 实现地区定价策略，限制跨区购买
- [ ] 定期审计各货币定价的一致性

## 检测方法
```sql
-- 检测货币与用户地区不匹配
SELECT o.id, o.currency, o.paid_amount, u.region
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE (u.region = 'CN' AND o.currency != 'CNY')
   OR (u.region = 'US' AND o.currency != 'USD');

-- 检测同商品不同货币价格差异过大
SELECT product_id,
       MAX(CASE WHEN currency = 'USD' THEN price END) as usd_price,
       MAX(CASE WHEN currency = 'JPY' THEN price END) as jpy_price,
       MAX(CASE WHEN currency = 'CNY' THEN price END) as cny_price
FROM product_prices
GROUP BY product_id
HAVING usd_price IS NOT NULL
   AND jpy_price / 150 < usd_price * 0.5; -- JPY价格异常低
```

## 代码示例
```javascript
// ❌ 错误做法：信任前端货币参数
app.post('/api/order', async (req, res) => {
  const { productId, currency } = req.body;

  const product = await db.getProductPrice(productId, currency);
  const amount = product.price;

  await createPaymentOrder(amount, currency);
});

// ❌ 错误做法：货币与用户地区不绑定
app.post('/api/order', async (req, res) => {
  const { productId, currency } = req.body;

  // 允许用户选择任意货币
  const validCurrencies = ['USD', 'EUR', 'CNY', 'JPY'];
  if (!validCurrencies.includes(currency)) {
    return res.status(400).json({ error: '不支持的货币' });
  }

  const amount = await getPriceInCurrency(productId, currency);
  await createPaymentOrder(amount, currency);
});

// ✅ 正确做法：货币基于用户地区，实时汇率校验
const EXCHANGE_RATES = {
  USD: 1,
  CNY: 7.2,
  EUR: 0.92,
  JPY: 150
};

const REGION_CURRENCY = {
  CN: 'CNY',
  US: 'USD',
  EU: 'EUR',
  JP: 'JPY',
  DEFAULT: 'USD'
};

class CurrencyService {
  constructor() {
    this.rates = null;
    this.lastUpdate = null;
  }

  // 获取实时汇率
  async getExchangeRates() {
    const cacheKey = 'exchange_rates';
    const cached = await cache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < 3600000) { // 1小时缓存
      return cached.rates;
    }

    // 从汇率API获取
    const response = await fetch(`https://api.exchangerate-api.com/v4/latest/USD`);
    const data = await response.json();

    await cache.set(cacheKey, {
      rates: data.rates,
      timestamp: Date.now()
    });

    return data.rates;
  }

  // 获取用户应使用的货币
  getUserCurrency(user) {
    return REGION_CURRENCY[user.region] || REGION_CURRENCY.DEFAULT;
  }

  // 校验货币是否匹配用户地区
  validateCurrency(user, requestedCurrency) {
    const expectedCurrency = this.getUserCurrency(user);

    if (requestedCurrency && requestedCurrency !== expectedCurrency) {
      // 记录异常尝试
      securityLog.record({
        type: 'currency_mismatch',
        userId: user.id,
        expectedCurrency,
        requestedCurrency,
        userRegion: user.region
      });

      return { valid: false, currency: expectedCurrency };
    }

    return { valid: true, currency: expectedCurrency };
  }

  // 计算价格并校验
  async calculatePrice(productId, currency, requestedAmount) {
    // 获取基础价格（统一用USD）
    const basePrice = await db.getProductBasePrice(productId);
    const rates = await this.getExchangeRates();

    // 计算预期价格
    const expectedAmount = basePrice * rates[currency];

    // 校验请求的价格是否合理（允许1%误差，处理汇率波动）
    const tolerance = 0.01;
    if (Math.abs(requestedAmount - expectedAmount) / expectedAmount > tolerance) {
      securityLog.record({
        type: 'price_currency_mismatch',
        productId,
        currency,
        expectedAmount,
        requestedAmount
      });

      throw new Error('价格与当前汇率不匹配，请刷新重试');
    }

    return {
      amount: expectedAmount,
      currency,
      exchangeRate: rates[currency],
      basePrice
    };
  }
}

// API实现
const currencyService = new CurrencyService();

app.post('/api/order', async (req, res) => {
  const { productId, currency: requestedCurrency, amount: requestedAmount } = req.body;
  const user = req.user;

  // 1. 货币校验
  const { valid, currency } = currencyService.validateCurrency(user, requestedCurrency);

  if (!valid) {
    return res.status(400).json({
      error: '货币与您的账户地区不匹配',
      suggestedCurrency: currency
    });
  }

  try {
    // 2. 价格计算与校验
    const priceInfo = await currencyService.calculatePrice(
      productId,
      currency,
      requestedAmount
    );

    // 3. 创建订单
    const order = await db.createOrder({
      userId: user.id,
      productId,
      amount: priceInfo.amount,
      currency: priceInfo.currency,
      baseAmount: priceInfo.basePrice,
      exchangeRate: priceInfo.exchangeRate,
      exchangeRateDate: new Date()
    });

    res.json({
      orderId: order.id,
      amount: priceInfo.amount,
      currency: priceInfo.currency
    });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// ✅ 更安全的做法：统一结算货币
app.post('/api/order', async (req, res) => {
  const { productId } = req.body;
  const user = req.user;

  // 获取基础价格（统一USD）
  const basePrice = await db.getProductBasePrice(productId);
  const currency = currencyService.getUserCurrency(user);
  const rates = await currencyService.getExchangeRates();

  // 后端计算最终价格
  const displayAmount = basePrice * rates[currency];

  // 创建订单（存储USD基准价格）
  const order = await db.createOrder({
    userId: user.id,
    productId,
    baseAmount: basePrice, // USD
    displayAmount,
    displayCurrency: currency,
    exchangeRate: rates[currency]
  });

  // 支付时使用用户货币
  const paymentResult = await paymentGateway.createPayment({
    orderId: order.id,
    amount: displayAmount,
    currency: currency
  });

  res.json({
    orderId: order.id,
    amount: displayAmount,
    currency
  });
});
```

## 参考资料
- [多货币支付最佳实践](https://stripe.com/docs/currencies)
- [汇率风险管理](https://www.paypal.com/us/brc/article/fx-risk-management)
- [跨境电商定价策略](https://www.shopify.com/blog/currency-conversion)
