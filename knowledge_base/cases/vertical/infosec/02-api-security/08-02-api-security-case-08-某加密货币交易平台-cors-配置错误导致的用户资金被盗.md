# 02-api-security Case 08: 某加密货币交易平台 CORS 配置错误导致的用户资金被盗

- **所属领域**: 信息安全 / API安全
- **威胁类型**: 安全配置错误 (Security Misconfiguration) / CORS

### 事件回顾
2022年，一家新兴的加密货币交易所遭遇了钓鱼攻击，部分用户的资金被无声无息地转移。安全调查显示，该交易所的后端API（如 `api.crypto-exchange.com`）在跨域资源共享（CORS）配置上存在严重错误。为了贪图开发便利，开发人员将API的 `Access-Control-Allow-Origin` 头部动态反射为请求来源，并且设置了 `Access-Control-Allow-Credentials: true`。这使得黑客通过构造一个恶意的第三方钓鱼网页，诱导已登录交易所的用户访问。钓鱼网页中的恶意JavaScript直接向交易所API发起转账请求，成功绕过了同源策略的保护。

### Red View (利用路径)
1. **分析API跨域策略**：攻击者在测试时，向交易所转账API发送请求并附带头部 `Origin: https://evil-site.com`。发现服务器响应了 `Access-Control-Allow-Origin: https://evil-site.com` 以及允许凭证的头部。
2. **制作恶意利用页面**：攻击者在 `evil-site.com` 上部署恶意HTML文件，包含一段AJAX JavaScript脚本，脚本配置为 `withCredentials = true`，自动调用交易所的 `POST /api/v1/wallet/transfer` 接口。
3. **实施水坑/钓鱼攻击**：攻击者通过Telegram社群群发钓鱼链接。
4. **隐蔽执行跨域请求**：受害者在浏览器已登录交易所的状态下点击了钓鱼链接，恶意脚本在后台静默执行。由于CORS错误配置，浏览器允许了该跨域请求带上受害者的有效Session Cookie或JWT，导致受害者钱包内的加密货币被非法划转。

### Blue View (防御缺失)
1. **过度宽松的 CORS 策略**：API服务器没有在配置端严格限定可信来源（Whitelist Origins），而是动态读取 `Origin` 请求头并直接反射，从而使浏览器的同源策略（SOP）形同虚设。
2. **缺乏敏感操作的二次验证**：对于提取资金、转账等高风险API接口，在仅有Cookie或Token凭证的情况下即放行，没有强制要求支付密码、双因素认证（2FA）或独立的一次性CSRF Token。
3. **未区分内外部接口的防护级别**：核心金融API直接面向公网所有域开放了带凭证的跨域访问权限，没有针对关键路由实施降级配置。

### 策略借鉴
1. **实施严格的跨域白名单配置**：在API网关或后端中间件中，明确将 `Access-Control-Allow-Origin` 限制为绝对可信的业务域名（如 `https://www.crypto-exchange.com`），禁止使用 `*` 或动态反射未知域，且在支持跨域时严格管控允许的方法与Header。
2. **引入反CSRF令牌与2FA机制**：针对所有状态变更型API，尤其涉及资金或权限操作的接口，必须在Header中传递独立的 CSRF Token，并在关键环节要求短信/TOTP的双重认证。
3. **采用严格的 Cookie 属性限制**：若采用Cookie进行身份保持，必须全面配置 `SameSite=Strict` 或 `Lax` 属性，从浏览器内核层面阻断跨站携带凭证的恶意请求。
