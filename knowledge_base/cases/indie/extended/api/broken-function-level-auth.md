# 破损的功能级授权 (Broken Function Level Authorization)

> **Tier 适用**: L1 ✅

## 一句话风险

普通用户访问或执行管理员功能，导致垂直越权和权限提升。

## 一分钟识别清单

- [ ] 管理接口未做角色验证或验证可绕过
- [ ] 通过修改 HTTP 方法或路径访问受限功能
- [ ] 前端隐藏的管理功能后端未做权限校验

## 一句话防御

后端严格实施基于角色的访问控制（RBAC），验证每个敏感操作。

## 推荐工具链接

- [Autorize](https://github.com/PortSwigger/autorize) - Burp 授权检测插件
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [RBAC Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 管理接口暴露 | /api/admin/users 可直接访问 |
| 方法替换 | GET 改为 DELETE 执行删除 |
| 角色篡改 | 修改请求中的 role 参数 |
| 隐藏功能发现 | 通过目录扫描发现管理接口 |

## 攻击示例

```http
# 普通用户请求
GET /api/users HTTP/1.1
Authorization: Bearer normal_user_token

# 尝试管理员功能
DELETE /api/admin/users/123 HTTP/1.1
Authorization: Bearer normal_user_token

# 修改请求体中的角色
POST /api/profile HTTP/1.1
{"role": "admin"}
```

## 修复代码示例

```python
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403, "需要管理员权限")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/admin/users')
@login_required
@admin_required
def list_all_users():
    return User.query.all()
```

## 检测方法

```bash
# 使用普通用户 token 访问管理接口
curl -H "Authorization: Bearer normal_token" \
  https://api.target.com/api/admin/users

# 检查 HTTP 方法替换
curl -X DELETE -H "Authorization: Bearer normal_token" \
  https://api.target.com/api/users/123
```

## RBAC 配置示例

```yaml
roles:
  user:
    permissions:
      - read:own_profile
      - update:own_profile
  admin:
    permissions:
      - read:all_users
      - delete:any_user
      - manage:system
```

## 参考

- [OWASP API5:2019 BFLA](https://owasp.org/www-project-api-security/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
