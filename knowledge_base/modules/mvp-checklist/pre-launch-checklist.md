# 上线前检查清单

> 文档路径：`/modules/mvp-checklist/pre-launch-checklist.md`  
> 最后更新：2025-06-11  
> 预计完成时间：30-45 分钟

---

## 使用说明

- ✅ 表示已通过检查
- ❌ 表示未通过检查
- ⚠️ 表示部分通过或需要关注
- 每项检查后请记录检查结果、负责人和修复计划

---

## 一、认证安全检查项（10 项）

### 1.1 密码安全

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 1 | ☐ 密码使用强哈希算法（bcrypt/Argon2/scrypt） | 🔴 | ☐ | 明文或弱哈希导致密码泄露 | 使用 `bcrypt` 或 `Argon2`，设置合理 cost |
| 2 | ☐ 密码强度验证（最小长度、复杂度） | 🟠 | ☐ | 弱密码易被暴力破解 | 最小 8 位，包含大小写+数字+特殊字符 |
| 3 | ☐ 密码重置流程安全（令牌有效期、一次性） | 🟠 | ☐ | 重置令牌泄露导致账户劫持 | 令牌 15 分钟过期，使用后立即失效 |
| 4 | ☐ 登录失败限制（账户锁定/验证码） | 🟠 | ☐ | 暴力破解风险 | 5 次失败后锁定 15 分钟或显示验证码 |

### 1.2 会话管理

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 5 | ☐ Session ID 足够随机（128 位以上） | 🔴 | ☐ | Session 劫持风险 | 使用加密安全随机数生成器 |
| 6 | ☐ Session 超时机制（空闲超时+绝对超时） | 🟠 | ☐ | 长期有效 Session 被滥用 | 空闲 30 分钟、绝对 24 小时超时 |
| 7 | ☐ 登出功能完全销毁 Session | 🟡 | ☐ | 登出后 Session 仍可使用 | `session.destroy()` + 清除客户端 Cookie |
| 8 | ☐ Cookie 安全属性（HttpOnly、Secure、SameSite） | 🔴 | ☐ | XSS 窃取 Cookie、CSRF 攻击 | 设置 `HttpOnly; Secure; SameSite=Strict` |

### 1.3 多因素认证

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 9 | ☐ 敏感操作支持 MFA（修改密码、提现等） | 🟠 | ☐ | 单因素认证易被盗号 | 集成 TOTP 或短信验证 |
| 10 | ☐ MFA 令牌安全存储和传输 | 🟠 | ☐ | MFA 令牌泄露 | 令牌加密存储，传输使用 HTTPS |

---

## 二、数据安全检查项（10 项）

### 2.1 敏感数据识别

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 1 | ☐ 已识别所有敏感数据类型 | 🔴 | ☐ | 遗漏敏感数据导致泄露 | 建立《敏感数据清单》，定期更新 |
| 2 | ☐ 敏感数据分类分级 | 🟠 | ☐ | 不同敏感度数据保护不足 | 按公开/内部/机密/绝密分级 |

### 2.2 数据存储安全

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 3 | ☐ 敏感数据加密存储（AES-256-GCM） | 🔴 | ☐ | 数据库泄露导致明文泄露 | 使用 AES-256-GCM，密钥单独管理 |
| 4 | ☐ 加密密钥安全管理（KMS/HSM） | 🔴 | ☐ | 密钥泄露导致数据全面泄露 | 使用 KMS 管理，定期轮换 |
| 5 | ☐ 数据库访问控制（最小权限原则） | 🟠 | ☐ | 过度权限导致数据泄露 | 应用账户仅授予必要权限 |
| 6 | ☐ 数据库连接加密（TLS） | 🟠 | ☐ | 中间人攻击窃取数据 | 强制 TLS 连接，验证证书 |

### 2.3 数据传输安全

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 7 | ☐ 所有 API 强制 HTTPS | 🔴 | ☐ | 明文传输被监听 | 配置强制 HTTPS，禁用 HTTP |
| 8 | ☐ HTTPS 证书有效且受信任 | 🔴 | ☐ | 证书无效导致中间人攻击 | 使用可信 CA 证书，定期续期 |

### 2.4 数据处理安全

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 9 | ☐ 日志不记录敏感数据 | 🟠 | ☐ | 日志泄露敏感信息 | 日志脱敏处理，过滤敏感字段 |
| 10 | ☐ 敏感数据脱敏展示（掩码处理） | 🟡 | ☐ | 界面泄露敏感数据 | 手机号显示 `138****1234`，身份证显示 `110***********1234` |

---

## 三、API 安全检查项（10 项）

### 3.1 输入验证

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 1 | ☐ 所有用户输入验证和清理 | 🔴 | ☐ | 注入攻击、XSS | 白名单验证，特殊字符转义 |
| 2 | ☐ SQL 注入防护（参数化查询/ORM） | 🔴 | ☐ | 数据库被攻击 | 使用参数化查询或 ORM，禁止拼接 SQL |
| 3 | ☐ 文件上传安全验证（类型、大小、内容） | 🟠 | ☐ | 恶意文件上传 | 检查 MIME 类型、文件大小、文件内容 |

### 3.2 输出编码

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 4 | ☐ XSS 防护（输出编码） | 🔴 | ☐ | 跨站脚本攻击 | 使用模板引擎自动转义，设置 CSP |

### 3.3 访问控制

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 5 | ☐ API 认证机制完善 | 🔴 | ☐ | 未授权访问 | JWT/OAuth2/Session 认证 |
| 6 | ☐ API 授权检查（RBAC/ABAC） | 🟠 | ☐ | 越权访问 | 每个接口检查用户权限 |
| 7 | ☐ 防止 IDOR（不安全直接对象引用） | 🟠 | ☐ | 用户可访问他人数据 | 检查资源归属，不暴露连续 ID |

### 3.4 API 保护

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 8 | ☐ API 速率限制 | 🟠 | ☐ | DDoS、暴力破解 | 限制每分钟/每小时请求次数 |
| 9 | ☐ 错误信息不泄露敏感信息 | 🟠 | ☐ | 信息泄露辅助攻击 | 统一错误响应，隐藏技术细节 |
| 10 | ☐ API 版本管理 | 🟡 | ☐ | 破坏性变更影响客户端 | URL 或 Header 中包含版本号 |

---

## 四、支付安全检查项（5 项）

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 1 | ☐ 支付数据不落本地，直连支付网关 | 🔴 | ☐ | 支付卡数据泄露 | 使用支付网关托管页面或 Token |
| 2 | ☐ 支付回调验签 | 🔴 | ☐ | 伪造支付成功 | 验证支付网关签名 |
| 3 | ☐ 订单金额防篡改 | 🔴 | ☐ | 金额被恶意修改 | 服务端计算订单金额，签名验证 |
| 4 | ☐ 支付状态防重复处理 | 🟠 | ☐ | 重复回调导致重复发货 | 使用幂等性设计，订单号去重 |
| 5 | ☐ 符合 PCI DSS 基本要求 | 🔴 | ☐ | 支付合规风险 | 使用 PCI DSS 认证的支付服务商 |

---

## 五、基础设施检查项（5 项）

| # | 检查项 | 等级 | 状态 | 风险说明 | 快速修复 |
|---|--------|------|------|----------|----------|
| 1 | ☐ 服务器关闭不必要的端口和服务 | 🔴 | ☐ | 攻击面扩大 | 仅开放必要端口，关闭多余服务 |
| 2 | ☐ 服务器 SSH 安全配置 | 🟠 | ☐ | SSH 被暴力破解 | 禁用密码登录，仅允许密钥认证 |
| 3 | ☐ 安全响应头配置（CSP、X-Frame-Options 等） | 🟠 | ☐ | XSS、点击劫持 | 配置安全响应头 |
| 4 | ☐ 依赖包安全审计（无已知高危漏洞） | 🔴 | ☐ | 供应链攻击 | 使用 `npm audit`/`snyk` 检查 |
| 5 | ☐ 环境变量安全管理 | 🔴 | ☐ | 密钥泄露 | 使用 Vault 或加密存储，不入代码库 |

---

## 六、自动化检查脚本

### 6.1 一键检查脚本

```bash
#!/bin/bash
# security-check.sh - MVP 安全检查脚本
# 用法: ./security-check.sh [--full|--critical|--report]

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=========================================="
echo "  MVP 安全检查工具 v1.0"
echo "=========================================="
echo ""

# 检查结果统计
PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARN++))
}

# 1. 检查 HTTPS
echo ">>> 检查 HTTPS 配置"
if curl -sI https://$DOMAIN 2>/dev/null | grep -q "HTTP/2 200\|HTTP/1.1 200"; then
    check_pass "HTTPS 正常工作"
else
    check_fail "HTTPS 配置异常或未启用"
fi

# 2. 检查安全响应头
echo ">>> 检查安全响应头"
HEADERS=$(curl -sI https://$DOMAIN 2>/dev/null)

if echo "$HEADERS" | grep -qi "Strict-Transport-Security"; then
    check_pass "HSTS 已配置"
else
    check_warn "HSTS 未配置"
fi

if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
    check_pass "X-Frame-Options 已配置"
else
    check_warn "X-Frame-Options 未配置"
fi

if echo "$HEADERS" | grep -qi "Content-Security-Policy"; then
    check_pass "CSP 已配置"
else
    check_warn "CSP 未配置"
fi

# 3. 检查依赖漏洞
echo ">>> 检查依赖包漏洞"
if [ -f "package.json" ]; then
    if command -v npm &> /dev/null; then
        AUDIT=$(npm audit --json 2>/dev/null || true)
        HIGH_VULN=$(echo "$AUDIT" | jq '.metadata.vulnerabilities.high // 0' 2>/dev/null || echo "0")
        CRIT_VULN=$(echo "$AUDIT" | jq '.metadata.vulnerabilities.critical // 0' 2>/dev/null || echo "0")
        
        if [ "$HIGH_VULN" = "0" ] && [ "$CRIT_VULN" = "0" ]; then
            check_pass "无高危/严重依赖漏洞"
        else
            check_fail "发现 $CRIT_VULN 个严重漏洞，$HIGH_VULN 个高危漏洞"
        fi
    fi
fi

# 4. 检查环境变量
echo ">>> 检查敏感信息泄露"
if grep -rq "password\|secret\|api_key\|token" . --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null; then
    check_warn "代码中可能存在硬编码敏感信息"
else
    check_pass "未发现硬编码敏感信息"
fi

# 5. 检查数据库连接
echo ">>> 检查数据库连接安全"
if grep -rq "mysql://\|postgres://" . --include="*.js" --include="*.ts" --include="*.py" 2>/dev/null; then
    check_warn "数据库连接字符串可能未加密"
else
    check_pass "数据库连接配置安全"
fi

# 6. 检查 CORS 配置
echo ">>> 检查 CORS 配置"
CORS=$(curl -sI -H "Origin: https://evil.com" https://$DOMAIN/api 2>/dev/null | grep -i "Access-Control-Allow-Origin" || true)
if echo "$CORS" | grep -q "\*"; then
    check_fail "CORS 配置过于宽松（允许所有来源）"
elif [ -n "$CORS" ]; then
    check_pass "CORS 已配置"
else
    check_warn "CORS 未配置或未响应"
fi

echo ""
echo "=========================================="
echo "  检查结果汇总"
echo "=========================================="
echo -e "${GREEN}通过: $PASS${NC}"
echo -e "${RED}失败: $FAIL${NC}"
echo -e "${YELLOW}警告: $WARN${NC}"
echo ""

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}存在未通过项，建议修复后再上线${NC}"
    exit 1
else
    echo -e "${GREEN}所有关键项已通过检查${NC}"
    exit 0
fi
```

### 6.2 使用方法

```bash
# 赋予执行权限
chmod +x security-check.sh

# 设置检查域名
export DOMAIN=your-domain.com

# 执行完整检查
./security-check.sh --full

# 仅检查关键项
./security-check.sh --critical

# 生成报告
./security-check.sh --report > security-report-$(date +%Y%m%d).md
```

### 6.3 在 CI/CD 中集成

```yaml
# .github/workflows/security-check.yml
name: Security Check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  security-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Security Check
        run: |
          chmod +x scripts/security-check.sh
          ./scripts/security-check.sh --critical
        env:
          DOMAIN: ${{ secrets.DOMAIN }}
      
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: security-report
          path: security-report-*.md
```

---

## 七、检查结果记录表

### 项目信息

| 项目 | 内容 |
|------|------|
| 项目名称 | |
| 版本号 | |
| 检查日期 | |
| 检查人 | |
| 审核人 | |

### 结果汇总

| 类别 | 通过 | 失败 | 警告 | 通过率 |
|------|------|------|------|--------|
| 认证安全 | /10 | | | % |
| 数据安全 | /10 | | | % |
| API 安全 | /10 | | | % |
| 支付安全 | /5 | | | % |
| 基础设施 | /5 | | | % |
| **总计** | /40 | | | % |

### 未通过项清单

| # | 检查项 | 等级 | 负责人 | 预计修复日期 | 备注 |
|---|--------|------|--------|-------------|------|
| | | | | | |
| | | | | | |
| | | | | | |

### 审批签字

| 角色 | 姓名 | 签字 | 日期 |
|------|------|------|------|
| 技术负责人 | | | |
| 安全负责人 | | | |
| 产品负责人 | | | |

---

> ⚠️ **重要提示**：本检查清单为基线要求，建议根据业务特性补充额外检查项。
