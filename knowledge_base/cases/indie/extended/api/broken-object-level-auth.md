# 破损的对象级授权 (Broken Object Level Authorization)

> **Tier 适用**: L1 ✅

## 一句话风险

用户通过修改资源 ID 访问其他用户的数据，导致水平越权和数据泄露。

## 一分钟识别清单

- [ ] API 直接使用用户传入的资源 ID 查询数据
- [ ] 未验证当前用户是否有权限访问该资源
- [ ] 可预测或自增的资源 ID（如 /user/123）

## 一句话防御

每次资源访问时验证当前用户对该资源的操作权限。

## 推荐工具链接

- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Autorize](https://github.com/PortSwigger/autorize) - Burp 授权检测插件
- [Authz](https://github.com/wuntee/BurpAuthzPlugin) - 授权测试插件

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| ID 枚举 | 遍历 /api/orders/1, /api/orders/2... |
| 用户数据泄露 | 修改 user_id 查看他人信息 |
| 订单篡改 | 访问他人订单并修改 |
| 文件访问 | 下载他人上传的文件 |

## 攻击示例

```http
# 正常请求
GET /api/users/123/profile HTTP/1.1
Authorization: Bearer user123_token

# 越权请求
GET /api/users/456/profile HTTP/1.1
Authorization: Bearer user123_token
```

## 修复代码示例

```python
# 错误：直接使用用户传入的 ID
@app.route('/api/orders/<order_id>')
def get_order(order_id):
    return Order.query.get(order_id)

# 正确：验证权限
@app.route('/api/orders/<order_id>')
@login_required
def get_order(order_id):
    order = Order.query.get(order_id)
    if order.user_id != current_user.id:
        abort(403, "无权访问此订单")
    return order
```

## 检测方法

```bash
# 使用不同账号测试
curl -H "Authorization: Bearer tokenA" https://api.target.com/orders/1
curl -H "Authorization: Bearer tokenB" https://api.target.com/orders/1

# 如果两个请求返回相同数据，则存在漏洞
```

## 使用 UUID 替代自增 ID

```python
import uuid

class Order(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # 更难枚举，但仍需权限校验
```

## 参考

- [OWASP API1:2019 BOLA](https://owasp.org/www-project-api-security/)
- [PortSwigger Access Control](https://portswigger.net/web-security/access-control)
