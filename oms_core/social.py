"""
社媒账号安全审计模块 - Oh-My-Security

检测社媒账号相关安全问题:
- 账号冒充风险
- 钓鱼链接检测
- OAuth 滥用风险
- 隐私泄露检测
- 内容劫持风险
- 认证造假检测
- 私信钓鱼检测
- 快拍攻击风险
- 群组渗透风险
- 跨平台风险评估
"""
import os
import re
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SocialFinding:
    """社媒安全发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 安全类别
    platform: str  # 平台名称
    description: str
    impact: str
    recommendation: str
    details: str = ""


# 社媒安全最佳实践指南
SOCIAL_SECURITY_GUIDE = """
# 社媒账号安全最佳实践指南

## 1. 账号冒充防护

### 识别冒充账号
- 用户名相似（多一个字母、下划线）
- 头像相同或相似
- 简介内容抄袭
- 假冒认证标识
- 主动联系你的粉丝

### 防护措施
- 尽早注册账号
- 启用官方认证
- 定期搜索自己的用户名
- 监控相似账号注册
- 设置账号防伪标识

## 2. 钓鱼链接防护

### 常见钓鱼形式
- "查看谁看了你的主页"
- "你被提及了" 假通知
- "账号被举报/封禁"
- "获得免费赠品"
- "参与抽奖活动"

### 识别钓鱼链接
- 检查域名是否为官方
- 短链接先展开查看
- 使用安全浏览器检测
- 检查 HTTPS 证书
- 留意拼写错误

## 3. OAuth 安全

### OAuth 滥用风险
- 恶意应用获取账号权限
- 过度授权导致数据泄露
- 授权后忘记撤销
- 第三方应用安全漏洞

### 安全实践
- 只授权可信应用
- 定期审查已授权应用
- 及时撤销不再使用的授权
- 了解授权范围
- 使用官方应用

## 4. 隐私设置

### 隐私泄露风险
- 位置信息暴露
- 联系方式公开
- 生活习惯泄露
- 社交关系图谱
- 工作信息泄露

### 隐私配置建议
- 设置账号为私密
- 限制陌生人查看
- 关闭位置共享
- 定期检查标签
- 谨慎分享个人信息

## 5. 内容劫持防护

### 常见劫持方式
- 盗取原创内容发布
- 恶意举报导致内容下架
- 冒充账号发布虚假信息
- 劫持话题标签
- 抢注相似账号名

### 防护措施
- 添加水印标识
- 及时举报侵权
- 记录原创发布时间
- 使用官方版权工具
- 建立品牌识别

## 6. 认证标识安全

### 认证造假识别
- 非官方认证图标
- PS 添加的认证标识
- 假冒官方账号
- 付费购买的假认证

### 获取正规认证
- 完成账号实名认证
- 满足平台认证条件
- 通过官方渠道申请
- 保持账号活跃度

## 7. 私信安全

### 私信钓鱼识别
- 紧急求助诈骗
- 投资/赚钱机会
- 官方账号索要信息
- 中奖通知
- 虚假合作邀请

### 私信安全设置
- 限制陌生人私信
- 过滤敏感词汇
- 不点击陌生链接
- 不透露个人信息
- 举报可疑私信

## 8. 快拍/动态安全

### 快拍攻击方式
- 截屏/录屏保存
- 第三方保存工具
- 恶意转发分享
- 隐私设置不当

### 安全建议
- 设置快拍可见范围
- 使用阅后即焚
- 注意背景敏感信息
- 定期检查快拍设置

## 9. 群组安全

### 群组渗透风险
- 恶意成员混入
- 信息泄露给竞争对手
- 垃圾广告灌水
- 社会工程攻击
- 假冒管理员

### 群组安全管理
- 设置入群审核
- 定期清理不活跃成员
- 禁止敏感话题讨论
- 设置管理员权限
- 监控异常行为

## 10. 跨平台安全

### 跨平台风险
- 同一密码多平台使用
- 账号关联导致连锁泄露
- 公开信息交叉关联
- 社交图谱分析

### 安全建议
- 每个平台独立密码
- 绑定不同的手机/邮箱
- 控制公开信息量
- 定期检查账号关联
- 启用所有平台 MFA

## 平台特定安全设置

### Instagram
- 私密账号设置
- 双因素认证
- 登录活动监控
- 评论过滤

### Twitter/X
- 私密推文保护
- 登录验证
- 应用授权管理
- 保护账号设置

### TikTok
- 私密账号
- 评论限制
- 下载限制
- 私信设置

### 微信
- 朋友权限设置
- 朋友圈可见范围
- 添加好友限制
- 隐私保护设置

### 微博
- 私信权限
- 评论审核
- 粉丝可见设置
- 登录保护
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


def check_account_impersonation(account_info: Dict) -> List[SocialFinding]:
    """
    检查账号冒充风险

    Args:
        account_info: 账号信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查是否有相似账号存在
    similar_accounts = account_info.get('similar_accounts', [])
    if similar_accounts:
        for acc in similar_accounts:
            similarity = acc.get('similarity', 0)
            if similarity > 0.8:
                findings.append(SocialFinding(
                    severity="HIGH",
                    category="账号冒充",
                    platform=acc.get('platform', 'unknown'),
                    description=f"发现高度相似账号: @{acc.get('username')}",
                    impact="粉丝可能被误导，影响品牌声誉",
                    recommendation="向平台举报冒充账号",
                    details=f"相似度: {similarity:.1%}, 粉丝数: {acc.get('followers', 0)}"
                ))

    # 检查是否已认证
    if not account_info.get('verified', False):
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="账号认证",
            platform=account_info.get('platform', 'unknown'),
            description="账号未获得官方认证",
            impact="容易被冒充账号混淆",
            recommendation="申请平台官方认证标识"
        ))

    return findings


def check_phishing_links(posts: List[Dict]) -> List[SocialFinding]:
    """
    检查钓鱼链接风险

    Args:
        posts: 帖子列表

    Returns:
        安全发现列表
    """
    findings = []

    # 钓鱼链接特征
    phishing_indicators = [
        r'免费|free|抽奖|giveaway',
        r'验证|verify|账户|account',
        r'点击.*链接|click.*link',
        r'被.*举报|reported',
        r'bit\.ly|tinyurl|t\.co',  # 短链接
    ]

    for post in posts:
        content = post.get('content', '')
        links = post.get('links', [])

        # 检查内容特征
        matched_patterns = []
        for pattern in phishing_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                matched_patterns.append(pattern)

        # 检查链接
        suspicious_links = []
        for link in links:
            # 检查是否为可疑域名
            if not _is_official_domain(link, post.get('platform', '')):
                suspicious_links.append(link)

        if matched_patterns and suspicious_links:
            findings.append(SocialFinding(
                severity="HIGH",
                category="钓鱼链接",
                platform=post.get('platform', 'unknown'),
                description=f"检测到疑似钓鱼内容: {content[:50]}...",
                impact="用户可能被诱导点击钓鱼链接",
                recommendation="删除可疑内容，检查账号是否被盗",
                details=f"可疑链接: {suspicious_links}"
            ))

    return findings


def _is_official_domain(url: str, platform: str) -> bool:
    """检查是否为官方域名"""
    official_domains = {
        'instagram': ['instagram.com', 'instagr.am'],
        'twitter': ['twitter.com', 'x.com', 't.co'],
        'facebook': ['facebook.com', 'fb.com', 'fb.me'],
        'tiktok': ['tiktok.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'weibo': ['weibo.com', 'weibo.cn'],
        'wechat': ['weixin.qq.com', 'wechat.com'],
    }

    platform_domains = official_domains.get(platform.lower(), [])

    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')

        # 检查是否匹配官方域名
        for official in platform_domains:
            if domain == official or domain.endswith('.' + official):
                return True
        return False
    except:
        return True  # 解析失败，保守处理


def check_oauth_abuse(authorized_apps: List[Dict]) -> List[SocialFinding]:
    """
    检查 OAuth 授权滥用

    Args:
        authorized_apps: 已授权应用列表

    Returns:
        安全发现列表
    """
    findings = []

    for app in authorized_apps:
        # 检查授权范围
        permissions = app.get('permissions', [])
        dangerous_permissions = [
            'read_private_messages',
            'write_private_messages',
            'full_access',
            'manage_account',
            'access_contacts',
        ]

        for perm in dangerous_permissions:
            if perm in permissions:
                findings.append(SocialFinding(
                    severity="HIGH",
                    category="OAuth 滥用",
                    platform=app.get('platform', 'unknown'),
                    description=f"应用 '{app.get('name')}' 拥有敏感权限: {perm}",
                    impact="应用可能滥用授权访问敏感数据",
                    recommendation="撤销不必要的应用授权",
                    details=f"授权时间: {app.get('authorized_at', 'unknown')}"
                ))

        # 检查授权时间
        auth_days = app.get('days_since_auth', 0)
        if auth_days > 365:
            findings.append(SocialFinding(
                severity="MEDIUM",
                category="长期授权",
                platform=app.get('platform', 'unknown'),
                description=f"应用 '{app.get('name')}' 已授权超过一年",
                impact="长期未审查的授权增加风险",
                recommendation="审查并清理不再使用的应用授权"
            ))

    return findings


def check_privacy_leak(account_settings: Dict) -> List[SocialFinding]:
    """
    检查隐私泄露风险

    Args:
        account_settings: 账号设置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查账号可见性
    if not account_settings.get('private_account', False):
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="隐私设置",
            platform=account_settings.get('platform', 'unknown'),
            description="账号设置为公开",
            impact="所有内容对陌生人可见",
            recommendation="考虑将账号设置为私密"
        ))

    # 检查位置分享
    if account_settings.get('location_sharing', False):
        findings.append(SocialFinding(
            severity="HIGH",
            category="位置泄露",
            platform=account_settings.get('platform', 'unknown'),
            description="位置分享已启用",
            impact="行踪可能被追踪",
            recommendation="关闭位置分享功能"
        ))

    # 检查联系方式可见性
    if account_settings.get('contact_info_visible', False):
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="联系方式泄露",
            platform=account_settings.get('platform', 'unknown'),
            description="联系方式对公众可见",
            impact="可能收到骚扰或钓鱼邮件",
            recommendation="隐藏联系方式或限制可见范围"
        ))

    # 检查好友列表可见性
    if account_settings.get('friends_list_visible', False):
        findings.append(SocialFinding(
            severity="LOW",
            category="社交关系泄露",
            platform=account_settings.get('platform', 'unknown'),
            description="好友/关注列表对公众可见",
            impact="社交关系图谱可被分析",
            recommendation="限制好友列表可见性"
        ))

    return findings


def check_content_hijacking(content_history: List[Dict]) -> List[SocialFinding]:
    """
    检查内容劫持风险

    Args:
        content_history: 内容历史列表

    Returns:
        安全发现列表
    """
    findings = []

    # 检查原创内容被转载情况
    for content in content_history:
        if content.get('original', True):
            reposts = content.get('unauthorized_reposts', [])
            if reposts:
                findings.append(SocialFinding(
                    severity="MEDIUM",
                    category="内容劫持",
                    platform=content.get('platform', 'unknown'),
                    description=f"原创内容被未授权转载 {len(reposts)} 次",
                    impact="影响原创权益和品牌价值",
                    recommendation="添加水印标识，向平台举报侵权"
                ))

    # 检查内容水印
    if not any(c.get('has_watermark', False) for c in content_history):
        findings.append(SocialFinding(
            severity="LOW",
            category="内容保护",
            platform='general',
            description="原创内容缺少水印保护",
            impact="内容容易被盗用",
            recommendation="为原创内容添加水印标识"
        ))

    return findings


def check_verified_badge_fraud(account_info: Dict) -> List[SocialFinding]:
    """
    检查认证标识造假

    Args:
        account_info: 账号信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查认证标识来源
    verification = account_info.get('verification', {})

    if verification.get('has_badge', False):
        # 检查是否为官方认证
        if not verification.get('official', False):
            findings.append(SocialFinding(
                severity="CRITICAL",
                category="认证造假",
                platform=account_info.get('platform', 'unknown'),
                description="检测到非官方认证标识",
                impact="可能违反平台政策，面临封号风险",
                recommendation="移除伪造认证标识，通过官方渠道申请认证"
            ))

        # 检查认证类型
        auth_type = verification.get('type', '')
        if auth_type not in ['blue', 'gold', 'gray', 'official']:
            findings.append(SocialFinding(
                severity="HIGH",
                category="可疑认证",
                platform=account_info.get('platform', 'unknown'),
                description=f"检测到可疑认证类型: {auth_type}",
                impact="可能被平台识别为造假",
                recommendation="核实认证来源，确保官方认证"
            ))

    return findings


def check_dm_phishing(messages: List[Dict]) -> List[SocialFinding]:
    """
    检查私信钓鱼风险

    Args:
        messages: 私信列表

    Returns:
        安全发现列表
    """
    findings = []

    # 钓鱼私信特征
    phishing_patterns = [
        (r'(投资|理财|赚钱|暴富)', "投资诈骗"),
        (r'(客服|官方|安全中心).*验证', "冒充官方"),
        (r'(中奖|获奖|抽奖)', "中奖诈骗"),
        (r'(紧急|求助|家人)', "紧急求助诈骗"),
        (r'(合作|商务).*链接', "虚假合作"),
        (r'https?://[^\s]+', "包含链接"),
    ]

    for msg in messages:
        content = msg.get('content', '')
        sender = msg.get('sender', {})

        matched_types = []
        for pattern, desc in phishing_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                matched_types.append(desc)

        if len(matched_types) >= 2:
            findings.append(SocialFinding(
                severity="HIGH",
                category="私信钓鱼",
                platform=msg.get('platform', 'unknown'),
                description=f"检测到可疑私信，类型: {', '.join(matched_types)}",
                impact="可能导致个人信息泄露或财产损失",
                recommendation="不回复可疑私信，向平台举报",
                details=f"发送者: @{sender.get('username', 'unknown')}"
            ))

    return findings


def check_story_attack(story_settings: Dict) -> List[SocialFinding]:
    """
    检查快拍/动态攻击风险

    Args:
        story_settings: 快拍设置字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查快拍可见范围
    if story_settings.get('visibility') == 'public':
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="快拍隐私",
            platform=story_settings.get('platform', 'unknown'),
            description="快拍设置为所有人可见",
            impact="陌生人可查看并截屏保存",
            recommendation="限制快拍可见范围"
        ))

    # 检查是否允许截屏通知
    if not story_settings.get('screenshot_alert', False):
        findings.append(SocialFinding(
            severity="LOW",
            category="截屏监控",
            platform=story_settings.get('platform', 'unknown'),
            description="未启用截屏通知",
            impact="无法感知他人截屏保存",
            recommendation="启用截屏通知功能（如平台支持）"
        ))

    # 检查是否允许转发
    if story_settings.get('allow_sharing', True):
        findings.append(SocialFinding(
            severity="LOW",
            category="转发控制",
            platform=story_settings.get('platform', 'unknown'),
            description="快拍允许转发分享",
            impact="内容可能被转发到其他平台",
            recommendation="禁用转发功能"
        ))

    return findings


def check_group_infiltration(group_info: Dict) -> List[SocialFinding]:
    """
    检查群组渗透风险

    Args:
        group_info: 群组信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查入群审核
    if not group_info.get('join_approval', False):
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="群组准入",
            platform=group_info.get('platform', 'unknown'),
            description="群组未设置入群审核",
            impact="任何人可自由加入，增加渗透风险",
            recommendation="启用入群审核机制"
        ))

    # 检查群成员数量
    member_count = group_info.get('member_count', 0)
    active_members = group_info.get('active_members', 0)

    if member_count > 100 and active_members / member_count < 0.1:
        findings.append(SocialFinding(
            severity="LOW",
            category="群组成员",
            platform=group_info.get('platform', 'unknown'),
            description="群组存在大量不活跃成员",
            impact="可能包含僵尸号或潜伏账号",
            recommendation="定期清理不活跃成员"
        ))

    # 检查管理员权限
    admin_count = group_info.get('admin_count', 0)
    if admin_count > 10:
        findings.append(SocialFinding(
            severity="LOW",
            category="管理员数量",
            platform=group_info.get('platform', 'unknown'),
            description=f"群组管理员数量过多: {admin_count}",
            impact="权限分散增加风险",
            recommendation="审查并精简管理员权限"
        ))

    return findings


def check_cross_platform_risk(accounts: List[Dict]) -> List[SocialFinding]:
    """
    检查跨平台风险

    Args:
        accounts: 多平台账号列表

    Returns:
        安全发现列表
    """
    findings = []

    # 检查密码复用
    passwords = [acc.get('password_hash', '') for acc in accounts if acc.get('password_hash')]
    if len(passwords) != len(set(passwords)):
        findings.append(SocialFinding(
            severity="HIGH",
            category="密码复用",
            platform='multiple',
            description="检测到多个平台使用相同密码",
            impact="一个平台泄露导致连锁风险",
            recommendation="为每个平台设置独立密码"
        ))

    # 检查关联账号
    emails = [acc.get('email', '') for acc in accounts if acc.get('email')]
    if len(set(emails)) == 1 and len(accounts) > 1:
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="账号关联",
            platform='multiple',
            description="所有账号绑定同一邮箱",
            impact="邮箱泄露影响所有关联账号",
            recommendation="重要账号使用独立邮箱"
        ))

    # 检查 MFA 覆盖
    mfa_enabled = [acc for acc in accounts if acc.get('mfa_enabled', False)]
    if len(mfa_enabled) < len(accounts):
        findings.append(SocialFinding(
            severity="MEDIUM",
            category="MFA 覆盖",
            platform='multiple',
            description=f"仅 {len(mfa_enabled)}/{len(accounts)} 个账号启用了 MFA",
            impact="未启用 MFA 的账号风险更高",
            recommendation="为所有账号启用双因素认证"
        ))

    return findings


def audit_social_security(accounts: Dict) -> str:
    """
    综合审计社媒账号安全配置

    Args:
        accounts: 多平台账号配置字典

    Returns:
        格式化的 Markdown 安全报告
    """
    all_findings: List[SocialFinding] = []

    # 执行各项检查
    for platform, config in accounts.items():
        config['platform'] = platform

        all_findings.extend(check_account_impersonation(config))
        all_findings.extend(check_privacy_leak(config))
        all_findings.extend(check_verified_badge_fraud(config))

        if 'posts' in config:
            all_findings.extend(check_phishing_links(config['posts']))

        if 'authorized_apps' in config:
            all_findings.extend(check_oauth_abuse(config['authorized_apps']))

        if 'messages' in config:
            all_findings.extend(check_dm_phishing(config['messages']))

        if 'story_settings' in config:
            all_findings.extend(check_story_attack(config['story_settings']))

        if 'groups' in config:
            for group in config['groups']:
                all_findings.extend(check_group_infiltration(group))

    # 跨平台检查
    all_findings.extend(check_cross_platform_risk(list(accounts.values())))

    return _generate_social_report(all_findings)


def _generate_social_report(findings: List[SocialFinding]) -> str:
    """生成社媒安全报告"""
    if not findings:
        return """# 社媒账号安全审计报告

## 审计结果

**状态**: ✅ 未发现明显的社媒安全风险

---

*建议定期审查账号设置和授权应用，保持安全意识。*
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

    report = f"""# 社媒账号安全审计报告

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
        severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}
        emoji = severity_emoji.get(f.severity, '⚪')

        report += f"""### {i}. {emoji} [{f.severity}] {f.category}

**平台**: {f.platform}

**问题**: {f.description}

**影响**: {f.impact}

**建议**: {f.recommendation}

"""

        if f.details:
            report += f"**详情**: {f.details}\n\n"

        report += "---\n\n"

    return report


def get_social_guide() -> str:
    """
    获取社媒安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return SOCIAL_SECURITY_GUIDE


# 模块导出
__all__ = [
    'audit_social_security',
    'check_account_impersonation',
    'check_phishing_links',
    'check_oauth_abuse',
    'check_privacy_leak',
    'check_content_hijacking',
    'check_verified_badge_fraud',
    'check_dm_phishing',
    'check_story_attack',
    'check_group_infiltration',
    'check_cross_platform_risk',
    'get_social_guide',
    'SocialFinding',
]


if __name__ == "__main__":
    # 测试代码
    test_accounts = {
        'instagram': {
            'verified': False,
            'similar_accounts': [
                {'username': 'test_user_', 'similarity': 0.95, 'followers': 100}
            ],
            'private_account': False,
            'location_sharing': True,
            'authorized_apps': [
                {
                    'name': '可疑应用',
                    'permissions': ['read_private_messages'],
                    'days_since_auth': 400
                }
            ]
        }
    }

    print(audit_social_security(test_accounts))
