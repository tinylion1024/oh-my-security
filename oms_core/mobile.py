"""
移动设备安全审计模块 - Oh-My-Security

检测移动设备相关安全问题:
- 设备丢失风险
- App 权限滥用
- 短信钓鱼风险
- 恶意 App 检测
- 备份安全
- 生物识别安全
- SIM 卡安全
- 锁屏安全
- 剪贴板泄露
- 通知泄露
"""
import os
import re
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class MobileFinding:
    """移动安全发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 安全类别
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    impact: str
    recommendation: str


# 移动安全最佳实践指南
MOBILE_SECURITY_GUIDE = """
# 移动设备安全最佳实践指南

## 1. 设备丢失防护

### 立即行动
- **远程锁定**: 使用 Find My iPhone / Find My Device 锁定设备
- **远程擦除**: 敏感数据应支持远程擦除
- **定位追踪**: 启用设备定位功能
- **挂失账户**: 及时挂失支付应用和重要账户

### 预防措施
- 启用设备加密
- 设置强锁屏密码（6位以上）
- 启用生物识别锁
- 定期备份数据
- 记录设备 IMEI/序列号

## 2. App 权限管理

### 最小权限原则
- 只授予必要权限
- 定期审查已授权权限
- 拒绝非核心功能的敏感权限请求

### 危险权限清单
| 权限 | 风险 | 建议 |
|------|------|------|
| 位置 | 行踪追踪 | 仅使用时允许 |
| 相机/麦克风 | 隐私监控 | 仅使用时允许 |
| 通讯录/通话记录 | 隐私泄露 | 谨慎授权 |
| 短信/彩信 | 验证码截获 | 极度谨慎 |
| 存储 | 文件窃取 | 谨慎授权 |
| 无障碍服务 | 完全控制 | 禁止非必要应用 |

## 3. 短信钓鱼防护

### 识别钓鱼短信
- 陌生号码发送的链接
- 紧急催促类消息（"您的账户异常"）
- 冒充官方机构（银行、运营商）
- 要求点击链接验证信息
- 包含短链接的短信

### 防护措施
- 不点击短信中的链接
- 通过官方渠道核实信息
- 安装短信过滤应用
- 举报钓鱼短信

## 4. 恶意 App 防护

### 安装前检查
- 只从官方应用商店下载
- 检查开发者信息和评价
- 查看下载量和评分
- 阅读权限请求说明
- 搜索应用名称 + "安全" 关键词

### 危险信号
- 破解/盗版应用
- 要求过多权限
- 频繁后台运行
- 大量广告弹窗
- 电池消耗异常快

## 5. 备份安全

### 安全备份原则
- 使用加密备份
- 本地 + 云端双重备份
- 定期测试恢复
- 备份敏感数据单独加密

### iOS 备份
- iCloud 备份启用加密
- 本地备份设置密码
- 定期检查备份状态

### Android 备份
- 使用 Google One 或厂商云服务
- 敏感数据使用独立加密
- 避免第三方备份应用

## 6. 生物识别安全

### 安全使用
- 不要只依赖生物识别
- 设置强备用密码
- 注意环境安全（防止被强迫解锁）
- 了解法律风险（执法可能强制解锁）

### 风险场景
- 睡觉时被解锁
- 照片/视频欺骗（低端设备）
- 3D 打印指纹
- 法律强制解锁

## 7. SIM 卡安全

### SIM 卡调换攻击
攻击者冒充你向运营商申请补办 SIM 卡，接管你的手机号和所有短信验证。

### 防护措施
- 设置 SIM 卡 PIN 码
- 联系运营商设置账户密码
- 启用运营商二次验证
- 监控信号异常（突然无服务）

## 8. 锁屏安全

### 基本设置
- 自动锁屏时间 < 1 分钟
- 使用复杂图案/密码
- 禁用锁屏通知内容预览
- 禁用锁屏 USB 调试

### 敏感通知处理
- 隐藏通知内容
- 只显示应用名称
- 解锁后显示详情

## 9. 剪贴板安全

### 风险场景
- 复制密码/验证码
- 复制私密信息
- 复制钱包地址

### 防护措施
- 定期清空剪贴板
- 使用密码管理器自动填充
- iOS 14+ 检测剪贴板读取
- 敏感信息不通过剪贴板

## 10. 通知安全

### 风险场景
- 锁屏显示验证码
- 通知泄露聊天内容
- 邮件预览泄露敏感信息

### 安全配置
- 隐藏锁屏通知内容
- 设置通知权限
- 敏感应用禁用预览

## 常见移动安全漏洞检测模式

### 代码检测模式
```python
# 检测不安全的存储
INSECURE_STORAGE_PATTERNS = [
    r'SharedPreferences.*MODE_WORLD_READABLE',
    r'getExternalStorageDirectory\(\)',
    r'openFileOutput.*MODE_PRIVATE.*false',
]

# 检测不安全的网络通信
INSECURE_NETWORK_PATTERNS = [
    r'http://',
    r'trustAllCerts',
    r'ALLOW_ALL_HOSTNAME_VERIFIER',
]

# 检测日志泄露
LOG_LEAK_PATTERNS = [
    r'Log\.(d|i|v|e|w)\(.*?(password|token|key)',
    r'println\(.*?(password|token|key)',
]
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
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"AI 引擎调用失败:\n{result.stderr}"
    except FileNotFoundError:
        return "未找到 gemini CLI 工具。请确保已安装并配置好 Gemini 命令行环境。"
    except subprocess.TimeoutExpired:
        return "AI 引擎调用超时，请稍后重试。"
    except Exception as e:
        return f"执行期间发生异常: {e}"


def check_device_lost_risk(config: Dict) -> List[MobileFinding]:
    """
    检查设备丢失风险配置

    Args:
        config: 设备配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查是否启用了远程锁定
    if not config.get('remote_lock_enabled', False):
        findings.append(MobileFinding(
            severity="HIGH",
            category="设备丢失防护",
            file_path="",
            line_number=0,
            code_snippet="远程锁定未启用",
            description="设备未启用远程锁定功能",
            impact="设备丢失后无法远程锁定，数据可能被窃取",
            recommendation="启用 Find My iPhone / Find My Device 功能"
        ))

    # 检查是否启用了远程擦除
    if not config.get('remote_wipe_enabled', False):
        findings.append(MobileFinding(
            severity="HIGH",
            category="设备丢失防护",
            file_path="",
            line_number=0,
            code_snippet="远程擦除未启用",
            description="设备未启用远程擦除功能",
            impact="设备丢失后无法远程清除敏感数据",
            recommendation="启用远程擦除功能，保护敏感数据"
        ))

    # 检查设备加密
    if not config.get('device_encryption', False):
        findings.append(MobileFinding(
            severity="CRITICAL",
            category="设备加密",
            file_path="",
            line_number=0,
            code_snippet="设备未加密",
            description="设备存储未启用加密",
            impact="设备丢失或被物理访问时数据可直接读取",
            recommendation="启用设备全盘加密"
        ))

    return findings


def check_permission_abuse(permissions: List[Dict]) -> List[MobileFinding]:
    """
    检查 App 权限滥用

    Args:
        permissions: 权限列表

    Returns:
        安全发现列表
    """
    findings = []

    # 高危权限清单
    dangerous_permissions = {
        'READ_SMS': '短信读取',
        'RECEIVE_SMS': '短信接收',
        'READ_CONTACTS': '通讯录读取',
        'READ_CALL_LOG': '通话记录',
        'ACCESS_FINE_LOCATION': '精确位置',
        'CAMERA': '摄像头',
        'RECORD_AUDIO': '麦克风录音',
        'READ_EXTERNAL_STORAGE': '存储读取',
        'WRITE_EXTERNAL_STORAGE': '存储写入',
        'ACCESS_BACKGROUND_LOCATION': '后台位置',
    }

    for perm in permissions:
        perm_name = perm.get('name', '')
        if perm_name in dangerous_permissions:
            # 检查权限使用频率
            usage_count = perm.get('usage_count', 0)
            last_used = perm.get('last_used_days', 999)

            if last_used > 30:
                findings.append(MobileFinding(
                    severity="MEDIUM",
                    category="权限滥用",
                    file_path="",
                    line_number=0,
                    code_snippet=f"权限: {perm_name}",
                    description=f"应用拥有{dangerous_permissions[perm_name]}权限但超过30天未使用",
                    impact="不必要的敏感权限增加隐私泄露风险",
                    recommendation="撤销未使用的敏感权限"
                ))

    return findings


def check_sms_phishing_risk(messages: List[str]) -> List[MobileFinding]:
    """
    检查短信钓鱼风险

    Args:
        messages: 短信内容列表

    Returns:
        安全发现列表
    """
    findings = []

    # 钓鱼短信特征
    phishing_patterns = [
        (r'https?://[^\s]+', "包含链接"),
        (r'(账户|银行卡|异常|冻结|验证|立即)', "紧急催促词汇"),
        (r'(银行|客服|官方|支付宝|微信)', "冒充官方"),
        (r'(点击|链接|验证|确认)', "诱导点击"),
    ]

    for i, msg in enumerate(messages):
        matched_patterns = []
        for pattern, desc in phishing_patterns:
            if re.search(pattern, msg):
                matched_patterns.append(desc)

        # 匹配多个特征则可能是钓鱼
        if len(matched_patterns) >= 2:
            findings.append(MobileFinding(
                severity="HIGH",
                category="短信钓鱼风险",
                file_path="",
                line_number=i,
                code_snippet=msg[:50] + "...",
                description=f"疑似钓鱼短信，特征: {', '.join(matched_patterns)}",
                impact="可能导致账户被盗或个人信息泄露",
                recommendation="不要点击短信中的链接，通过官方渠道核实"
            ))

    return findings


def check_malicious_app_indicators(app_info: Dict) -> List[MobileFinding]:
    """
    检查恶意 App 指标

    Args:
        app_info: 应用信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查来源
    if app_info.get('source') not in ['google_play', 'app_store', 'official']:
        findings.append(MobileFinding(
            severity="HIGH",
            category="应用来源",
            file_path="",
            line_number=0,
            code_snippet=f"来源: {app_info.get('source')}",
            description="应用非来自官方应用商店",
            impact="可能包含恶意代码或后门",
            recommendation="只从官方应用商店下载应用"
        ))

    # 检查评分和下载量
    rating = app_info.get('rating', 0)
    downloads = app_info.get('downloads', 0)

    if rating < 3.0 and downloads < 1000:
        findings.append(MobileFinding(
            severity="MEDIUM",
            category="应用信誉",
            file_path="",
            line_number=0,
            code_snippet=f"评分: {rating}, 下载: {downloads}",
            description="应用评分低且下载量少",
            impact="可能是低质量或恶意应用",
            recommendation="选择评分高、下载量大的应用"
        ))

    # 检查权限数量
    dangerous_permissions = app_info.get('dangerous_permissions_count', 0)
    if dangerous_permissions > 5:
        findings.append(MobileFinding(
            severity="HIGH",
            category="权限过多",
            file_path="",
            line_number=0,
            code_snippet=f"敏感权限数: {dangerous_permissions}",
            description="应用请求过多敏感权限",
            impact="过度收集用户数据",
            recommendation="审查权限请求，考虑替代应用"
        ))

    return findings


def check_backup_security(backup_config: Dict) -> List[MobileFinding]:
    """
    检查备份安全配置

    Args:
        backup_config: 备份配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查备份是否加密
    if backup_config.get('enabled', False) and not backup_config.get('encrypted', False):
        findings.append(MobileFinding(
            severity="HIGH",
            category="备份加密",
            file_path="",
            line_number=0,
            code_snippet="备份未加密",
            description="云备份未启用加密",
            impact="备份数据可能被云服务商或攻击者访问",
            recommendation="启用备份加密选项"
        ))

    # 检查备份频率
    if backup_config.get('last_backup_days', 999) > 30:
        findings.append(MobileFinding(
            severity="MEDIUM",
            category="备份频率",
            file_path="",
            line_number=0,
            code_snippet=f"上次备份: {backup_config.get('last_backup_days')}天前",
            description="备份间隔过长",
            impact="设备丢失时可能丢失大量数据",
            recommendation="设置自动备份，频率至少每周一次"
        ))

    return findings


def check_biometric_security(biometric_config: Dict) -> List[MobileFinding]:
    """
    检查生物识别安全配置

    Args:
        biometric_config: 生物识别配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查是否只依赖生物识别
    if biometric_config.get('biometric_enabled', False):
        if not biometric_config.get('strong_password_enabled', True):
            findings.append(MobileFinding(
                severity="MEDIUM",
                category="生物识别安全",
                file_path="",
                line_number=0,
                code_snippet="仅使用生物识别",
                description="设备仅依赖生物识别解锁",
                impact="可能被强迫解锁或在睡眠时解锁",
                recommendation="设置强密码作为备用解锁方式"
            ))

    # 检查生物识别超时
    bio_timeout = biometric_config.get('biometric_timeout_minutes', 0)
    if bio_timeout > 30:
        findings.append(MobileFinding(
            severity="LOW",
            category="生物识别超时",
            file_path="",
            line_number=0,
            code_snippet=f"生物识别超时: {bio_timeout}分钟",
            description="生物识别超时时间过长",
            impact="长时间后仍可用生物识别解锁，降低安全性",
            recommendation="设置较短的超时时间（建议5分钟内需密码）"
        ))

    return findings


def check_sim_security(sim_config: Dict) -> List[MobileFinding]:
    """
    检查 SIM 卡安全配置

    Args:
        sim_config: SIM 卡配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查 SIM 卡 PIN
    if not sim_config.get('sim_pin_enabled', False):
        findings.append(MobileFinding(
            severity="HIGH",
            category="SIM 卡安全",
            file_path="",
            line_number=0,
            code_snippet="SIM PIN 未启用",
            description="SIM 卡未设置 PIN 码",
            impact="SIM 卡被盗后可直接使用，接收验证码",
            recommendation="设置 SIM 卡 PIN 码"
        ))

    # 检查运营商账户保护
    if not sim_config.get('carrier_account_password', False):
        findings.append(MobileFinding(
            severity="HIGH",
            category="SIM 调换攻击",
            file_path="",
            line_number=0,
            code_snippet="运营商账户未设密码",
            description="运营商账户未设置额外验证密码",
            impact="可能遭受 SIM 调换攻击",
            recommendation="联系运营商设置账户密码和二次验证"
        ))

    return findings


def check_lock_screen_security(lock_config: Dict) -> List[MobileFinding]:
    """
    检查锁屏安全配置

    Args:
        lock_config: 锁屏配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查自动锁屏时间
    auto_lock_minutes = lock_config.get('auto_lock_minutes', 0)
    if auto_lock_minutes > 5:
        findings.append(MobileFinding(
            severity="MEDIUM",
            category="锁屏超时",
            file_path="",
            line_number=0,
            code_snippet=f"自动锁屏: {auto_lock_minutes}分钟",
            description="自动锁屏时间过长",
            impact="设备无人看管时易被访问",
            recommendation="设置自动锁屏时间不超过1分钟"
        ))

    # 检查锁屏通知内容
    if lock_config.get('show_notification_content', True):
        findings.append(MobileFinding(
            severity="MEDIUM",
            category="锁屏通知",
            file_path="",
            line_number=0,
            code_snippet="锁屏显示通知内容",
            description="锁屏时显示通知内容",
            impact="验证码、聊天内容等敏感信息泄露",
            recommendation="设置为解锁后才显示通知内容"
        ))

    # 检查锁屏密码强度
    if lock_config.get('lock_type') == 'pattern':
        findings.append(MobileFinding(
            severity="LOW",
            category="锁屏方式",
            file_path="",
            line_number=0,
            code_snippet="使用图案解锁",
            description="使用图案解锁而非密码",
            impact="图案可能被窥视或通过指纹痕迹猜测",
            recommendation="使用复杂 PIN 或密码解锁"
        ))

    return findings


def check_clipboard_security(clipboard_config: Dict) -> List[MobileFinding]:
    """
    检查剪贴板安全配置

    Args:
        clipboard_config: 剪贴板配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查剪贴板清理
    if not clipboard_config.get('auto_clear', False):
        findings.append(MobileFinding(
            severity="LOW",
            category="剪贴板安全",
            file_path="",
            line_number=0,
            code_snippet="剪贴板未自动清理",
            description="剪贴板未设置自动清理",
            impact="复制的敏感信息可能被恶意应用读取",
            recommendation="设置剪贴板自动清理或手动清理"
        ))

    # 检查剪贴板读取监控
    if not clipboard_config.get('read_alert', False):
        findings.append(MobileFinding(
            severity="INFO",
            category="剪贴板监控",
            file_path="",
            line_number=0,
            code_snippet="未启用剪贴板读取提醒",
            description="未启用剪贴板读取提醒（iOS 14+）",
            impact="无法感知应用读取剪贴板",
            recommendation="iOS 设备自动提示，Android 可使用监控应用"
        ))

    return findings


def check_notification_security(notification_config: Dict) -> List[MobileFinding]:
    """
    检查通知安全配置

    Args:
        notification_config: 通知配置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查敏感应用通知预览
    sensitive_apps = ['banking', 'payment', 'email', 'messaging', 'authenticator']
    for app in sensitive_apps:
        app_config = notification_config.get(app, {})
        if app_config.get('show_preview', True) and app_config.get('show_on_lock', True):
            findings.append(MobileFinding(
                severity="MEDIUM",
                category="通知泄露",
                file_path="",
                line_number=0,
                code_snippet=f"应用: {app}",
                description=f"{app} 应用在锁屏显示通知预览",
                impact="敏感信息可能被他人查看",
                recommendation="敏感应用设置为解锁后才显示内容"
            ))

    return findings


def audit_mobile_security(config: Dict) -> str:
    """
    综合审计移动设备安全配置

    Args:
        config: 设备配置字典

    Returns:
        格式化的 Markdown 安全报告
    """
    all_findings: List[MobileFinding] = []

    # 执行各项检查
    all_findings.extend(check_device_lost_risk(config.get('device', {})))
    all_findings.extend(check_permission_abuse(config.get('permissions', [])))
    all_findings.extend(check_backup_security(config.get('backup', {})))
    all_findings.extend(check_biometric_security(config.get('biometric', {})))
    all_findings.extend(check_sim_security(config.get('sim', {})))
    all_findings.extend(check_lock_screen_security(config.get('lock_screen', {})))
    all_findings.extend(check_clipboard_security(config.get('clipboard', {})))
    all_findings.extend(check_notification_security(config.get('notifications', {})))

    return _generate_mobile_report(all_findings)


def _generate_mobile_report(findings: List[MobileFinding]) -> str:
    """生成移动安全报告"""
    if not findings:
        return """# 移动设备安全审计报告

## 审计结果

**状态**: ✅ 未发现明显的移动安全风险

---

*建议定期检查设备安全配置，保持系统更新。*
"""

    # 按严重程度分组
    severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'INFO': 4}
    sorted_findings = sorted(findings, key=lambda x: severity_order.get(x.severity, 5))

    # 统计
    stats = {
        'CRITICAL': len([f for f in findings if f.severity == 'CRITICAL']),
        'HIGH': len([f for f in findings if f.severity == 'HIGH']),
        'MEDIUM': len([f for f in findings if f.severity == 'MEDIUM']),
        'LOW': len([f for f in findings if f.severity == 'LOW']),
    }

    report = f"""# 移动设备安全审计报告

## 风险统计

| 严重程度 | 数量 |
|---------|------|
| 🔴 CRITICAL | {stats['CRITICAL']} |
| 🟠 HIGH | {stats['HIGH']} |
| 🟡 MEDIUM | {stats['MEDIUM']} |
| 🔵 LOW | {stats['LOW']} |
| **总计** | **{len(findings)}** |

---

## 风险详情

"""

    for i, f in enumerate(sorted_findings, 1):
        severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵', 'INFO': '⚪'}
        emoji = severity_emoji.get(f.severity, '⚪')

        report += f"""### {i}. {emoji} [{f.severity}] {f.category}

**问题**: {f.description}

**影响**: {f.impact}

**建议**: {f.recommendation}

---

"""

    return report


def get_mobile_guide() -> str:
    """
    获取移动安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return MOBILE_SECURITY_GUIDE


# 模块导出
__all__ = [
    'audit_mobile_security',
    'check_device_lost_risk',
    'check_permission_abuse',
    'check_sms_phishing_risk',
    'check_malicious_app_indicators',
    'check_backup_security',
    'check_biometric_security',
    'check_sim_security',
    'check_lock_screen_security',
    'check_clipboard_security',
    'check_notification_security',
    'get_mobile_guide',
    'MobileFinding',
]


if __name__ == "__main__":
    # 测试代码
    test_config = {
        'device': {
            'remote_lock_enabled': False,
            'remote_wipe_enabled': False,
            'device_encryption': True,
        },
        'lock_screen': {
            'auto_lock_minutes': 5,
            'show_notification_content': True,
            'lock_type': 'pattern',
        },
        'sim': {
            'sim_pin_enabled': False,
        }
    }

    print(audit_mobile_security(test_config))
