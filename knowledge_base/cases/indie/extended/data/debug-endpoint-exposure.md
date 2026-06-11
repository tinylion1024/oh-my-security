# 调试端点暴露 (Debug Endpoint Exposure)

## 元数据

| 属性 | 值 |
|------|-----|
| ID | CASE-EXT-DATA-008 |
| 分类 | 数据安全 / 应用安全 |
| tier 适用 | L1 ✅ |
| 创建时间 | 2026-06-11 |
| 最后更新 | 2026-06-11 |

---

## 一句话风险

调试端点、管理接口或开发工具暴露在生产环境中，导致敏感信息泄露、远程代码执行或未授权访问。

---

## 一分钟识别清单

### ✅ 识别要点

- [ ] **调试接口可访问** - `/debug`、`/actuator`、`/health`、`/metrics` 等端点暴露
- [ ] **管理界面未保护** - 数据库管理工具、监控系统未设置认证
- [ ] **开发工具泄露** - Swagger UI、GraphQL Playground、API 文档公开访问

### 🔍 典型场景

```
场景 1: Spring Boot Actuator 泄露
访问: https://example.com/actuator/env
返回: 数据库密码、API 密钥等环境变量
结果:     敏感配置信息泄露

场景 2: 调试工具公开访问
访问: https://example.com/_debugbar
或:   https://example.com/graphql (Playground)
结果:     数据库结构、API 接口暴露

场景 3: 管理界面无认证
访问: https://example.com:8080/manager/html
Tomcat Manager 无认证或弱密码
结果:     攻击者可部署恶意 WAR 包
```

---

## 一句话防御

**禁用生产环境调试端点、限制管理接口访问 IP、实施强认证、使用网络隔离或 VPN 访问管理界面。**

---

## 推荐工具链接

| 工具/资源 | 用途 | 链接 |
|----------|------|------|
| **Nuclei** | 漏洞扫描器 | https://github.com/projectdiscovery/nuclei |
| **Amass** | 资产发现 | https://github.com/OWASP/Amass |
| **Spring Boot Actuator** | 端点安全配置 | https://docs.spring.io/spring-boot/docs/current/reference/html/actuator.html |
| **Swagger UI Security** | API 文档安全 | https://swagger.io/docs/specification/authentication/ |

---

## 快速缓解措施

### 1. Spring Boot Actuator 配置
```yaml
# application.yml - 生产环境
management:
  endpoints:
    web:
      exposure:
        include: health,info  # 仅暴露必要端点
  endpoint:
    health:
      show-details: never  # 不显示详细健康信息
  security:
    enabled: true

# 完全禁用 Actuator
# management.server.add-application-context-header: false
# spring.actuator.enabled: false
```

### 2. Nginx 访问控制
```nginx
# Nginx 配置：限制管理接口访问
location ~ ^/(debug|actuator|admin|manager) {
    allow 10.0.0.0/8;    # 内网 IP
    allow 192.168.0.0/16;
    deny all;

    # 或使用基本认证
    auth_basic "Admin Area";
    auth_basic_user_file /etc/nginx/.htpasswd;
}
```

### 3. 禁用开发工具
```python
# Django 示例：生产环境禁用调试
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['example.com']

# 禁用 Django Debug Toolbar
if not DEBUG:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']
```

```javascript
// Node.js + Express 示例
// 生产环境禁用调试路由
if (process.env.NODE_ENV === 'production') {
  app.disable('x-powered-by');
  // 移除所有调试路由
  app._router.stack = app._router.stack.filter(
    middleware => middleware.route?.path !== '/debug'
  );
}
```

---

## 相关案例

- [CASE-EXT-DATA-004 日志注入](./log-injection.md)
- [CASE-EXT-DATA-006 配置文件暴露](./config-exposure.md)

---

## 参考标准

- OWASP ASVS v4.0 - V14: Configuration
- CWE-215: Insertion of Sensitive Information Into Debugging Code
- NIST SP 800-53 - CM-6: Configuration Settings
- CIS Benchmark - Disable Debug Mode
