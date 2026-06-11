# 资产管理不当 (Improper Assets Management)

> **Tier 适用**: L1 ✅

## 一句话风险

暴露的旧版 API、测试接口或未文档化的端点缺乏安全控制，导致敏感数据泄露。

## 一分钟识别清单

- [ ] 生产环境存在 /api/v1 和 /api/v2 等多版本接口
- [ ] 测试/调试接口未关闭（/debug、/test、/swagger）
- [ ] API 文档或管理面板可公开访问

## 一句话防御

定期审计和下线旧版 API，生产环境移除所有测试接口。

## 推荐工具链接

- [APIKit](https://github.com/API-Security/APIKit) - API 资产发现
- [dirsearch](https://github.com/maurosoria/dirsearch) - 目录扫描
- [ffuf](https://github.com/ffuf/ffuf) - Web Fuzzing 工具

## 常见攻击场景

| 场景 | 描述 |
|------|------|
| 旧版 API | v1 版本缺少认证或权限校验 |
| 测试接口 | /api/test 返回敏感配置 |
| API 文档暴露 | /swagger-ui.html 泄露接口信息 |
| 管理接口 | /admin 或 /api/internal 可直接访问 |
| Beta 接口 | /api/beta 缺少安全控制 |

## 攻击示例

```bash
# 尝试不同 API 版本
curl https://api.target.com/v1/users
curl https://api.target.com/v2/users
curl https://api.target.com/v3/users

# 查找测试接口
curl https://api.target.com/api/test
curl https://api.target.com/debug
curl https://api.target.com/swagger-ui.html
curl https://api.target.com/api-docs
```

## 常见暴露路径

```
/api/v1/
/api/v2/
/api/beta/
/api/test/
/api/debug/
/api/internal/
/swagger-ui.html
/swagger-ui/
/api-docs/
/redoc
/actuator
/graphql
```

## 检测方法

```bash
# 使用 ffuf 扫描
ffuf -u https://api.target.com/FUZZ -w api_paths.txt -mc 200,401,403

# 使用 dirsearch
python3 dirsearch.py -u https://api.target.com -e json,xml
```

## 修复建议

```nginx
# 禁用旧版 API
location /api/v1/ {
    return 410;  # Gone
}

# 限制内部接口
location /api/internal/ {
    allow 10.0.0.0/8;
    deny all;
}

# 移除测试接口
# location /debug/ { ... }  # 删除或注释
```

## 参考

- [OWASP API8:2019 Injection](https://owasp.org/www-project-api-security/)
- [API Security Best Practices](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
