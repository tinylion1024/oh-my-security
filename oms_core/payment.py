"""
支付安全审计模块 - Oh-My-Security

检测支付相关代码中的常见漏洞模式:
- 价格参数前端传递
- 订单金额未服务端校验
- 支付回调未验证签名
- 缺少幂等性处理
- 零元订单漏洞
"""
import os
import re
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class VulnerabilityFinding:
    """漏洞发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 漏洞类别
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    recommendation: str


# 支付安全最佳实践指南
PAYMENT_SECURITY_GUIDE = """
# 支付安全最佳实践指南

## 1. 参数防篡改
- **签名验证**: 所有支付参数必须参与签名，使用 HMAC-SHA256 或 RSA-SHA256
- **参数顺序**: 签名时参数按字典序排列，防止顺序不同导致签名不一致
- **时间戳校验**: 添加时间戳，防止重放攻击（建议 5-15 分钟有效期）
- **金额校验**: 金额从后端获取，不要信任前端传递的金额

## 2. 回调安全
- **签名验证**: 验证回调签名，防止伪造回调
- **幂等处理**: 同一订单号多次回调只处理一次
- **状态校验**: 验证订单状态是否允许更新
- **来源验证**: 验证回调 IP 是否来自支付平台
- **异步处理**: 回调处理要快速响应，业务逻辑异步执行

## 3. 敏感信息保护
- **密钥存储**: API 密钥存储在环境变量或密钥管理服务中
- **日志脱敏**: 日志中不记录完整卡号、CVV、密码等敏感信息
- **传输加密**: 使用 HTTPS 传输所有支付数据
- **数据不存储**: 不存储 CVV、CVV2 等敏感支付信息

## 4. 金额处理
- **整数运算**: 使用整数（分）而非浮点数处理金额，避免精度问题
- **边界检查**: 验证金额在合理范围内
- **货币一致**: 确保交易前后货币类型一致

## 5. 订单安全
- **订单唯一性**: 订单号全局唯一，防止重复支付
- **状态机管理**: 订单状态变更遵循严格的状态机
- **超时处理**: 未支付订单超时自动取消
- **对账机制**: 定期与支付平台对账

## 6. 常见漏洞
- **金额篡改**: 前端传递金额被修改
- **订单号遍历**: 可猜测的订单号导致信息泄露
- **回调伪造**: 攻击者伪造支付成功回调
- **重放攻击**: 同一支付请求被重复提交
- **并发问题**: 高并发下订单状态不一致

## 7. 推荐实现模式

### 签名生成示例
```python
import hmac
import hashlib

def generate_sign(params: dict, secret_key: str) -> str:
    # 参数按字典序排序
    sorted_params = sorted(params.items())
    # 拼接成字符串
    sign_str = '&'.join(f"{k}={v}" for k, v in sorted_params)
    # HMAC-SHA256 签名
    return hmac.new(
        secret_key.encode(),
        sign_str.encode(),
        hashlib.sha256
    ).hexdigest()
```

### 回调处理示例
```python
def handle_callback(callback_data: dict) -> dict:
    # 1. 验证签名
    if not verify_sign(callback_data):
        return {"code": "FAIL", "msg": "签名验证失败"}

    # 2. 验证订单状态
    order = get_order(callback_data["out_trade_no"])
    if order.status != "PENDING":
        return {"code": "SUCCESS"}  # 已处理，幂等返回

    # 3. 验证金额一致性
    if order.amount != callback_data["total_amount"]:
        log_error("金额不一致")
        return {"code": "FAIL", "msg": "金额不一致"}

    # 4. 更新订单状态
    update_order_status(order.id, "PAID")

    return {"code": "SUCCESS"}
```
"""


def ask_ai(prompt: str) -> str:
    """
    通过调用本机的 gemini CLI 工具，利用大模型处理 Prompt。
    """
    try:
        result = subprocess.run(
            ["gemini", "-p", prompt],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"AI 引擎调用失败:\n{result.stderr}"
    except FileNotFoundError:
        return "未找到 gemini CLI 工具。请确保已安装并配置好 Gemini 命令行环境。"
    except Exception as e:
        return f"执行期间发生异常: {e}"


def check_params(code_content: str) -> List[VulnerabilityFinding]:
    """
    检查支付参数是否可被前端篡改

    检测模式:
    - 从 request/req 中直接获取价格/金额参数
    - 前端传递的价格直接用于支付
    - 未从数据库或服务端会话获取价格

    Args:
        code_content: 代码内容字符串

    Returns:
        漏洞发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # 价格参数前端传递的正则模式
    price_patterns = [
        # 直接从请求中获取价格
        (r'(price|amount|total|fee|money|金额|价格)\s*[:=]\s*(request|req)\.?(params|body|query|form|data|get|post)?\s*\(?["\']?(\w+)["\']?\)?',
         "价格参数直接从请求中获取"),
        # 前端传参模式 (JavaScript/TypeScript)
        (r'(price|amount|total)\s*[:=]\s*(req\.body|req\.query|ctx\.request\.body|this\.ctx\.request)',
         "支付金额从前端请求体获取"),
        # PHP 模式
        (r'\$_(POST|GET|REQUEST)\s*\[[\'"](price|amount|total|fee)[\'"]\s*\]',
         "PHP 直接从用户输入获取支付金额"),
        # Java Spring 模式
        (r'@RequestParam.*?(price|amount|total|fee)',
         "Spring @RequestParam 直接接收支付金额参数"),
    ]

    for line_idx, line in enumerate(lines, 1):
        for pattern, desc in price_patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                # 检查是否有服务端校验（排除误报）
                context_start = max(0, line_idx - 5)
                context_end = min(len(lines), line_idx + 5)
                context = '\n'.join(lines[context_start:context_end])

                # 如果上下文中有从数据库获取价格的逻辑，则可能是安全的
                safe_patterns = [r'findById', r'findOne', r'SELECT.*price', r'getPrice', r'price.*database', r'price.*db']
                is_safe = any(re.search(p, context, re.IGNORECASE) for p in safe_patterns)

                if not is_safe:
                    findings.append(VulnerabilityFinding(
                        severity="CRITICAL",
                        category="价格参数篡改",
                        file_path="",
                        line_number=line_idx,
                        code_snippet=line.strip(),
                        description=f"{desc}: {match.group(0)}",
                        impact="攻击者可篡改支付金额，以任意价格购买商品",
                        recommendation="价格必须从服务端数据库获取，禁止从前端参数传递"
                    ))

    return findings


def detect_zero_order(code_content: str) -> List[VulnerabilityFinding]:
    """
    检测零元订单漏洞模式

    检测模式:
    - 价格为 0 或负数时未拦截
    - 使用浮点数比较价格
    - 金额计算存在精度问题
    - 优惠券叠加未校验

    Args:
        code_content: 代码内容字符串

    Returns:
        漏洞发现列表
    """
    findings = []
    lines = code_content.split('\n')

    for line_idx, line in enumerate(lines, 1):
        # 检测价格等于 0 的条件判断
        if re.search(r'(price|amount|total)\s*(==|===|<=)\s*0', line, re.IGNORECASE):
            # 检查是否是校验逻辑（应该拒绝）还是漏洞（允许通过）
            context_start = max(0, line_idx - 3)
            context_end = min(len(lines), line_idx + 3)
            context = '\n'.join(lines[context_start:context_end])

            # 如果只是简单判断后继续执行，可能是漏洞
            if re.search(r'(return|throw|reject|error|fail)', context, re.IGNORECASE):
                continue  # 有正确的拒绝逻辑

            findings.append(VulnerabilityFinding(
                severity="HIGH",
                category="零元订单漏洞",
                file_path="",
                line_number=line_idx,
                code_snippet=line.strip(),
                description="零元订单可能未正确拦截",
                impact="攻击者可能创建零元订单免费获取商品",
                recommendation="订单金额为0时应拒绝或走特殊审批流程"
            ))

        # 检测浮点数价格比较（精度问题）
        if re.search(r'(price|amount|total)\s*(==|===)\s*[\d\.]+', line, re.IGNORECASE):
            if '.' in line and not re.search(r'abs\(|Math\.abs|fabs', line):
                findings.append(VulnerabilityFinding(
                    severity="MEDIUM",
                    category="金额精度问题",
                    file_path="",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    description="浮点数金额直接比较可能导致精度问题",
                    impact="可能因浮点精度导致金额校验失败",
                    recommendation="使用整数（分为单位）或专门的金额类型进行比较"
                ))

        # 检测负数金额未校验
        if re.search(r'(price|amount|total)\s*(<|<=)\s*0', line, re.IGNORECASE):
            context_start = max(0, line_idx - 5)
            context_end = min(len(lines), line_idx + 5)
            context = '\n'.join(lines[context_start:context_end])

            # 检查是否有抛出异常或返回错误的逻辑
            if not re.search(r'(return|throw|reject|error|raise|Exception)', context, re.IGNORECASE):
                findings.append(VulnerabilityFinding(
                    severity="HIGH",
                    category="负数金额漏洞",
                    file_path="",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    description="负数金额可能未正确处理",
                    impact="攻击者可能创建负数金额订单获得退款",
                    recommendation="金额必须大于0，负数应拒绝"
                ))

    return findings


def check_callback_security(code_content: str) -> List[VulnerabilityFinding]:
    """
    检查支付回调安全性

    检测模式:
    - 未验证签名直接处理回调
    - 回调地址未校验来源IP
    - 回调数据未验证订单状态
    - 缺少重复回调处理（幂等性）

    Args:
        code_content: 代码内容字符串

    Returns:
        漏洞发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # 回调函数识别模式
    callback_patterns = [
        r'(notify|callback|webhook)\s*\(',
        r'@(Post|Get)Mapping.*?(notify|callback|webhook)',
        r'function\s+(notify|callback|webhook)',
        r'def\s+(notify|callback|webhook)',
        r'async\s+(notify|callback|webhook)',
    ]

    in_callback = False
    callback_start = 0
    callback_context = []

    for line_idx, line in enumerate(lines, 1):
        # 检测回调函数
        for pattern in callback_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                in_callback = True
                callback_start = line_idx
                callback_context = [line]
                break

        # 收集回调函数上下文
        if in_callback:
            callback_context.append(line)

            # 简单判断回调函数结束（下一个函数定义或路由定义）
            if re.search(r'^(function|def|@|async|class|router|app\.|exports\.)', line) and line_idx > callback_start + 5:
                callback_code = '\n'.join(callback_context)

                # 检查签名验证
                sign_patterns = [
                    r'(sign|signature|verify)',
                    r'(checkSign|verifySign|validateSign)',
                    r'(hmac|sha256|md5)',
                    r'(crypto\.createVerify|openssl_verify)',
                ]
                has_sign_verify = any(re.search(p, callback_code, re.IGNORECASE) for p in sign_patterns)

                if not has_sign_verify:
                    findings.append(VulnerabilityFinding(
                        severity="CRITICAL",
                        category="回调签名缺失",
                        file_path="",
                        line_number=callback_start,
                        code_snippet=f"回调函数 {callback_context[0].strip()[:50]}...",
                        description="支付回调未验证签名",
                        impact="攻击者可伪造支付成功通知，免费获取商品或服务",
                        recommendation="必须验证支付平台签名，防止回调伪造"
                    ))

                # 检查幂等性处理
                idempotent_patterns = [
                    r'(idempotent|幂等|重复|duplicate|processed)',
                    r'(status.*=.*paid|订单状态)',
                    r'(set|redis|lock|mutex)',
                    r'findByOrderIdAndStatus',
                ]
                has_idempotent = any(re.search(p, callback_code, re.IGNORECASE) for p in idempotent_patterns)

                if not has_idempotent:
                    findings.append(VulnerabilityFinding(
                        severity="HIGH",
                        category="缺少幂等性处理",
                        file_path="",
                        line_number=callback_start,
                        code_snippet=f"回调函数 {callback_context[0].strip()[:50]}...",
                        description="支付回调缺少幂等性处理",
                        impact="重复回调可能导致重复发货或重复加款",
                        recommendation="使用订单状态锁或分布式锁确保回调幂等性"
                    ))

                in_callback = False
                callback_context = []

    # 检测直接使用回调数据更新订单
    for line_idx, line in enumerate(lines, 1):
        # 回调中直接使用外部数据更新订单状态
        if re.search(r'(updateOrder|update.*status|order\.status|订单状态)', line, re.IGNORECASE):
            context_start = max(0, line_idx - 10)
            context_end = min(len(lines), line_idx + 3)
            context = '\n'.join(lines[context_start:context_end])

            # 检查是否有签名验证
            if not re.search(r'(verify|sign|signature|check)', context, re.IGNORECASE):
                findings.append(VulnerabilityFinding(
                    severity="CRITICAL",
                    category="未验证来源更新订单",
                    file_path="",
                    line_number=line_idx,
                    code_snippet=line.strip(),
                    description="订单状态更新未验证回调来源",
                    impact="攻击者可伪造回调数据更新任意订单状态",
                    recommendation="更新订单前必须验证签名和回调来源"
                ))

    return findings


def check_idempotency(code_content: str) -> List[VulnerabilityFinding]:
    """
    检查幂等性处理

    检测模式:
    - 支付接口无唯一请求ID
    - 创建订单无幂等键
    - 缺少分布式锁

    Args:
        code_content: 代码内容字符串

    Returns:
        漏洞发现列表
    """
    findings = []
    lines = code_content.split('\n')

    # 查找支付/下单接口
    payment_patterns = [
        r'(pay|create.*order|submit.*order|checkout)',
        r'@(Post|Get)Mapping.*?(pay|order|checkout)',
        r'function\s+(pay|createOrder|submitOrder)',
    ]

    in_payment_func = False
    func_start = 0
    func_context = []

    for line_idx, line in enumerate(lines, 1):
        for pattern in payment_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                in_payment_func = True
                func_start = line_idx
                func_context = [line]
                break

        if in_payment_func:
            func_context.append(line)

            if re.search(r'^(function|def|@|async|class|router)', line) and line_idx > func_start + 5:
                func_code = '\n'.join(func_context)

                # 检查幂等键/请求ID
                idempotent_patterns = [
                    r'(idempotent|requestId|idempotencyKey|uniqueKey)',
                    r'(幂等|去重|唯一键)',
                    r'(redis|lock|setnx)',
                ]
                has_idempotent = any(re.search(p, func_code, re.IGNORECASE) for p in idempotent_patterns)

                if not has_idempotent:
                    findings.append(VulnerabilityFinding(
                        severity="MEDIUM",
                        category="缺少幂等性控制",
                        file_path="",
                        line_number=func_start,
                        code_snippet=f"支付函数 {func_context[0].strip()[:50]}...",
                        description="支付/下单接口缺少幂等性控制",
                        impact="网络重试可能导致重复下单或重复扣款",
                        recommendation="使用幂等键或分布式锁防止重复请求"
                    ))

                in_payment_func = False
                func_context = []

    return findings


def audit_payment(path: str) -> str:
    """
    审计支付相关代码，检测参数篡改风险

    Args:
        path: 代码目录或文件路径

    Returns:
        格式化的 Markdown 安全报告
    """
    if not os.path.exists(path):
        return f"路径不存在: {path}"

    files_to_scan = []
    if os.path.isfile(path):
        files_to_scan.append(path)
    elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
            # 过滤不需要扫描的目录
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build', 'vendor']]
            for f in files:
                if f.endswith(('.py', '.js', '.ts', '.java', '.php', '.go', '.rs', '.jsx', '.tsx')):
                    files_to_scan.append(os.path.join(root, f))

    if not files_to_scan:
        return "未在目标路径下发现支持扫描的支付相关源代码文件。"

    all_findings: List[VulnerabilityFinding] = []
    file_contents: Dict[str, str] = {}

    # 收集所有文件内容
    for fpath in files_to_scan[:20]:  # 限制文件数量
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 10000:
                    content = content[:10000] + "\n...(文件过长，截断)..."
                file_contents[fpath] = content
        except Exception:
            continue

    if not file_contents:
        return "读取文件内容失败或文件全为空。"

    # 对每个文件进行扫描
    for fpath, content in file_contents.items():
        # 检查是否包含支付相关关键词
        payment_keywords = ['pay', 'order', 'checkout', 'amount', 'price', 'fee', 'callback', 'notify', 'webhook', '支付', '订单', '金额']
        if not any(kw.lower() in content.lower() for kw in payment_keywords):
            continue

        # 执行各项检查
        findings = []
        findings.extend(check_params(content))
        findings.extend(detect_zero_order(content))
        findings.extend(check_callback_security(content))
        findings.extend(check_idempotency(content))

        # 为每个发现设置文件路径
        for finding in findings:
            finding.file_path = fpath

        all_findings.extend(findings)

    # 生成报告
    return _generate_report(all_findings, file_contents)


def _generate_report(findings: List[VulnerabilityFinding], file_contents: Dict[str, str]) -> str:
    """生成 Markdown 格式的安全报告"""

    if not findings:
        return """# 支付安全审计报告

## 审计结果

**扫描状态**: 未发现明显的支付安全漏洞

扫描了以下支付相关文件，未检测到常见漏洞模式。

扫描的漏洞类型:
- 价格参数前端传递
- 零元订单漏洞
- 支付回调签名缺失
- 幂等性处理缺失

---

*建议定期进行代码审计，确保支付安全。*
"""

    # 按严重程度分组
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
    sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.severity, 4))

    # 统计
    stats = {
        'CRITICAL': len([f for f in findings if f.severity == 'CRITICAL']),
        'HIGH': len([f for f in findings if f.severity == 'HIGH']),
        'MEDIUM': len([f for f in findings if f.severity == 'MEDIUM']),
        'LOW': len([f for f in findings if f.severity == 'LOW']),
    }

    report = f"""# 支付安全审计报告

## 漏洞统计

| 严重程度 | 数量 |
|---------|------|
| CRITICAL | {stats['CRITICAL']} |
| HIGH | {stats['HIGH']} |
| MEDIUM | {stats['MEDIUM']} |
| LOW | {stats['LOW']} |
| **总计** | **{len(findings)}** |

## 漏洞详情

"""

    current_severity = None
    for finding in sorted_findings:
        if finding.severity != current_severity:
            current_severity = finding.severity
            severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}
            report += f"\n### {severity_emoji.get(current_severity, '⚪')} {current_severity} 级别漏洞\n\n"

        report += f"""#### {finding.category}

**文件**: `{finding.file_path}:{finding.line_number}`

**代码片段**:
```
{finding.code_snippet}
```

**问题描述**: {finding.description}

**潜在影响**: {finding.impact}

**修复建议**: {finding.recommendation}

---

"""

    # 使用 AI 进行深度分析
    if stats['CRITICAL'] > 0 or stats['HIGH'] > 0:
        report += "\n## AI 深度分析\n\n"

        critical_findings = [f for f in findings if f.severity in ['CRITICAL', 'HIGH']][:5]
        context = "\n".join([
            f"- [{f.severity}] {f.category}: {f.description} ({f.file_path}:{f.line_number})"
            for f in critical_findings
        ])

        prompt = f"""作为支付安全专家，请对以下支付漏洞发现进行深度分析：

{context}

请提供:
1. 这些漏洞被组合利用的攻击场景
2. 业务层面的风险评估
3. 优先修复顺序建议
4. 代码修复的关键检查点

请用中文回答，保持简洁专业。
"""
        ai_analysis = ask_ai(prompt)
        report += ai_analysis

    return report


def get_payment_guide() -> str:
    """
    获取支付安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return PAYMENT_SECURITY_GUIDE


if __name__ == "__main__":
    # 测试代码
    test_code = '''
    def pay(request):
        price = request.params['price']  # 漏洞: 价格从前端获取
        order_id = create_order(price)
        return payment_gateway.pay(order_id, price)

    def notify_callback(request):
        # 漏洞: 未验证签名
        order_id = request.body['order_id']
        status = request.body['status']
        update_order(order_id, status)
    '''

    findings = check_params(test_code)
    print(f"Found {len(findings)} param issues")

    findings = check_callback_security(test_code)
    print(f"Found {len(findings)} callback issues")
