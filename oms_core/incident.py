"""
应急响应模块 - Oh-My-Security

提供安全事件分类、应急响应指南、恢复步骤和事件报告模板。

事件类型:
- account-compromised: 账号被盗
- data-breach: 数据泄露
- service-down: 服务宕机
- payment-fraud: 支付欺诈
- malware-detected: 恶意软件
- ddos-attack: DDoS攻击
- ransomware: 勒索软件
- social-engineering: 社会工程
- insider-threat: 内部威胁
- third-party-breach: 第三方泄露
"""
import os
import re
import subprocess
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class IncidentClassification:
    """事件分类结果"""
    incident_type: str  # 事件类型
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    severity_label: str  # 严重程度标签 (中文)
    confidence: float  # 分类置信度 0-1
    keywords_matched: List[str]  # 匹配的关键词
    description: str  # 事件描述


# 事件严重程度定义
SEVERITY_LEVELS = {
    "CRITICAL": {"label": "🔴 严重", "color": "red", "priority": 0},
    "HIGH": {"label": "🟠 高", "color": "yellow", "priority": 1},
    "MEDIUM": {"label": "🟡 中", "color": "yellow", "priority": 2},
    "LOW": {"label": "🟢 低", "color": "green", "priority": 3},
}

# 事件类型定义
INCIDENT_TYPES = {
    "account-compromised": {
        "name": "账号被盗",
        "severity": "HIGH",
        "keywords": ["账号", "被盗", "异常登录", "密码泄露", "未授权访问", "异地登录", "撞库", "credential", "compromised", "unauthorized"],
        "description": "用户账号被未授权者获取控制权"
    },
    "data-breach": {
        "name": "数据泄露",
        "severity": "CRITICAL",
        "keywords": ["数据泄露", "信息泄露", "敏感数据", "数据外泄", "数据库泄露", "泄露", "breach", "leak", "expose", "敏感信息"],
        "description": "敏感数据被未授权访问或泄露到外部"
    },
    "service-down": {
        "name": "服务宕机",
        "severity": "HIGH",
        "keywords": ["服务宕机", "无法访问", "服务不可用", "系统崩溃", "down", "outage", "unavailable", "崩溃", "宕机", "502", "503"],
        "description": "关键服务停止运行或无法访问"
    },
    "payment-fraud": {
        "name": "支付欺诈",
        "severity": "CRITICAL",
        "keywords": ["支付欺诈", "欺诈交易", "盗刷", "虚假支付", "支付异常", "fraud", "payment", "盗刷", "异常交易"],
        "description": "支付过程中存在欺诈行为"
    },
    "malware-detected": {
        "name": "恶意软件",
        "severity": "HIGH",
        "keywords": ["恶意软件", "病毒", "木马", "勒索", "挖矿", "malware", "virus", "trojan", "后门", "webshell"],
        "description": "检测到恶意软件感染"
    },
    "ddos-attack": {
        "name": "DDoS攻击",
        "severity": "HIGH",
        "keywords": ["DDoS", "DDOS", "拒绝服务", "流量攻击", "洪水攻击", "攻击", "dos", "flood", "syn flood"],
        "description": "分布式拒绝服务攻击"
    },
    "ransomware": {
        "name": "勒索软件",
        "severity": "CRITICAL",
        "keywords": ["勒索软件", "勒索病毒", "加密文件", "赎金", "ransomware", "加密", "勒索"],
        "description": "勒索软件感染导致数据被加密勒索"
    },
    "social-engineering": {
        "name": "社会工程",
        "severity": "MEDIUM",
        "keywords": ["钓鱼", "社会工程", "诈骗", "钓鱼邮件", "伪装", "phishing", "社工", "钓鱼网站", "钓鱼链接"],
        "description": "通过社会工程手段进行的攻击"
    },
    "insider-threat": {
        "name": "内部威胁",
        "severity": "HIGH",
        "keywords": ["内部威胁", "内部人员", "员工泄密", "离职员工", "insider", "内部作案", "权限滥用"],
        "description": "来自组织内部的安全威胁"
    },
    "third-party-breach": {
        "name": "第三方泄露",
        "severity": "HIGH",
        "keywords": ["第三方", "供应商", "外包", "第三方泄露", "供应链", "vendor", "third-party", "供应商安全"],
        "description": "第三方供应商或合作伙伴导致的数据泄露"
    },
}

# 事件报告模板
INCIDENT_REPORT_TEMPLATE = """
# 安全事件报告

## 基本信息

| 项目 | 内容 |
|------|------|
| 事件编号 | INC-{date}-{sequence} |
| 报告时间 | {report_time} |
| 报告人 | {reporter} |
| 事件类型 | {incident_type} |
| 严重程度 | {severity} |

## 事件概述

**发现时间**: {discovery_time}

**发现方式**: {discovery_method}

**影响范围**: {impact_scope}

**事件描述**:
{description}

## 时间线

| 时间 | 事件 |
|------|------|
| {timeline} |

## 影响评估

### 受影响系统
- {affected_systems}

### 受影响数据
- {affected_data}

### 受影响用户
- {affected_users}

### 业务影响
- {business_impact}

## 处置过程

### 立即行动 (0-15分钟)
1. {immediate_actions}

### 短期处理 (1-4小时)
1. {short_term_actions}

### 恢复步骤
1. {recovery_steps}

## 根因分析

**直接原因**: {root_cause}

**间接原因**: {contributing_factors}

**漏洞/缺陷**: {vulnerabilities}

## 整改措施

| 序号 | 措施 | 负责人 | 截止日期 | 状态 |
|------|------|--------|----------|------|
| {remediation_actions} |

## 经验教训

### 做得好的地方
- {what_went_well}

### 需要改进的地方
- {what_to_improve}

### 新增检测规则
- {new_detection_rules}

## 附件

- {attachments}

---

**审核人**: {reviewer}

**审核时间**: {review_time}
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


def get_incident_guide(incident_type: str) -> str:
    """
    获取应急响应指南

    Args:
        incident_type: 事件类型 (如 'account-compromised', 'data-breach' 等)

    Returns:
        应急响应指南内容 (Markdown 格式)
    """
    # 获取知识库路径
    knowledge_base_path = _get_knowledge_base_path()
    playbook_path = knowledge_base_path / "modules" / "incident-playbook" / f"{incident_type}.md"

    if playbook_path.exists():
        try:
            with open(playbook_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取剧本文件失败: {e}"

    # 如果没有找到特定剧本，返回通用指南
    return _get_generic_incident_guide(incident_type)


def _get_knowledge_base_path() -> Path:
    """获取知识库路径"""
    # 尝试多个可能的位置
    possible_paths = [
        Path(__file__).parent.parent / "knowledge_base",
        Path.cwd() / "knowledge_base",
        Path(__file__).parent.parent.parent / "knowledge_base",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # 默认返回相对于模块的路径
    return Path(__file__).parent.parent / "knowledge_base"


def _get_generic_incident_guide(incident_type: str) -> str:
    """获取通用事件响应指南"""
    incident_info = INCIDENT_TYPES.get(incident_type, {})

    guide = f"""# {incident_info.get('name', incident_type)} 应急响应指南

## 事件类型

**类型**: {incident_type}

**描述**: {incident_info.get('description', '未知事件类型')}

**默认严重程度**: {SEVERITY_LEVELS.get(incident_info.get('severity', 'MEDIUM'), {}).get('label', '未知')}

## 立即行动 (0-15分钟)

1. 确认事件发生，记录发现时间和方式
2. 通知相关负责人和安全团队
3. 隔离受影响的系统或账户
4. 保留所有日志和证据
5. 启动事件响应流程

## 短期处理 (1-4小时)

1. 收集更多信息，确定影响范围
2. 分析事件原因和攻击路径
3. 采取遏制措施防止事态扩大
4. 准备向管理层汇报
5. 如需要，启动危机沟通

## 恢复步骤

1. 清除威胁源（恶意软件、未授权账户等）
2. 修复导致事件的漏洞
3. 从备份恢复受影响的数据
4. 逐步恢复服务并监控
5. 验证系统安全性

## 复盘要点

1. 事件是如何发生的？
2. 为什么没有更早发现？
3. 响应过程有什么问题？
4. 需要改进哪些控制措施？
5. 如何防止类似事件再次发生？

---

> 注意: 这是通用指南。请查看具体事件类型的详细剧本以获取更专业的指导。
"""

    return guide


def classify_incident(description: str) -> IncidentClassification:
    """
    分类和定级安全事件

    Args:
        description: 事件描述

    Returns:
        IncidentClassification 对象，包含分类结果
    """
    description_lower = description.lower()

    # 匹配结果
    matches: List[Dict] = []

    for incident_type, info in INCIDENT_TYPES.items():
        keywords = info.get("keywords", [])
        matched_keywords = []

        for keyword in keywords:
            if keyword.lower() in description_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            # 计算置信度：匹配关键词数量 / 总关键词数量
            confidence = len(matched_keywords) / len(keywords) if keywords else 0

            matches.append({
                "type": incident_type,
                "name": info.get("name", incident_type),
                "severity": info.get("severity", "MEDIUM"),
                "confidence": confidence,
                "matched_keywords": matched_keywords,
                "description": info.get("description", ""),
            })

    if not matches:
        # 未匹配到已知类型，尝试使用 AI 分析
        ai_result = _classify_with_ai(description)
        if ai_result:
            return ai_result

        # 返回默认分类
        return IncidentClassification(
            incident_type="unknown",
            severity="MEDIUM",
            severity_label=SEVERITY_LEVELS["MEDIUM"]["label"],
            confidence=0.0,
            keywords_matched=[],
            description="未识别的事件类型，需要人工分析"
        )

    # 选择置信度最高的匹配
    best_match = max(matches, key=lambda x: x["confidence"])

    # 如果有多个高置信度匹配，选择严重程度更高的
    high_confidence_matches = [m for m in matches if m["confidence"] >= 0.3]
    if len(high_confidence_matches) > 1:
        best_match = min(high_confidence_matches, key=lambda x: SEVERITY_LEVELS.get(x["severity"], {}).get("priority", 3))

    return IncidentClassification(
        incident_type=best_match["type"],
        severity=best_match["severity"],
        severity_label=SEVERITY_LEVELS.get(best_match["severity"], {}).get("label", "未知"),
        confidence=best_match["confidence"],
        keywords_matched=best_match["matched_keywords"],
        description=best_match["description"]
    )


def _classify_with_ai(description: str) -> Optional[IncidentClassification]:
    """使用 AI 进行事件分类"""
    prompt = f"""作为安全事件分析师，请分析以下事件描述并进行分类。

事件描述：
{description}

请以 JSON 格式返回以下字段：
- incident_type: 事件类型 (从以下选择: account-compromised, data-breach, service-down, payment-fraud, malware-detected, ddos-attack, ransomware, social-engineering, insider-threat, third-party-breach, unknown)
- severity: 严重程度 (CRITICAL, HIGH, MEDIUM, LOW)
- confidence: 置信度 (0.0-1.0)
- reason: 分类理由

只返回 JSON，不要其他内容。
"""

    try:
        result = ask_ai(prompt)

        # 尝试解析 JSON
        import json
        # 提取 JSON 部分
        json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())

            return IncidentClassification(
                incident_type=data.get("incident_type", "unknown"),
                severity=data.get("severity", "MEDIUM"),
                severity_label=SEVERITY_LEVELS.get(data.get("severity", "MEDIUM"), {}).get("label", "未知"),
                confidence=float(data.get("confidence", 0.5)),
                keywords_matched=[],
                description=data.get("reason", "AI 分析结果")
            )
    except Exception:
        pass

    return None


def get_recovery_steps(incident_type: str) -> str:
    """
    获取恢复步骤

    Args:
        incident_type: 事件类型

    Returns:
        恢复步骤 (Markdown 格式)
    """
    recovery_guides = {
        "account-compromised": """# 账号被盗恢复步骤

## 1. 账户控制恢复
- 重置用户密码（强制所有会话下线）
- 撤销所有活跃的访问令牌
- 禁用可疑的应用授权
- 检查并移除未授权的二次验证设备

## 2. 访问权限审查
- 审查账户最近的权限变更
- 检查是否有未授权的权限提升
- 审计账户访问日志
- 确认账户关联信息是否被修改

## 3. 数据恢复
- 检查账户数据是否被篡改
- 恢复被删除或修改的重要数据
- 检查是否有数据外泄

## 4. 安全加固
- 强制启用多因素认证 (MFA)
- 添加登录异常检测规则
- 设置敏感操作二次验证
- 添加登录地域限制

## 5. 用户通知与教育
- 通知用户事件详情
- 提供安全建议和指导
- 告知用户如何识别钓鱼
- 提供可疑活动报告渠道
""",
        "data-breach": """# 数据泄露恢复步骤

## 1. 止损与隔离
- 立即关闭数据泄露入口
- 撤销泄露的访问凭证
- 隔离受影响的系统
- 封堵数据外泄通道

## 2. 泄露范围评估
- 确定泄露的数据类型和量级
- 识别受影响的用户/客户
- 评估数据的敏感程度
- 确定泄露途径和原因

## 3. 法律合规处理
- 评估是否需要监管报告
- 准备数据泄露通知
- 咨询法律顾问
- 按法规要求时限通知受影响方

## 4. 系统加固
- 修复导致泄露的漏洞
- 加强访问控制
- 增强数据加密措施
- 部署数据防泄漏 (DLP) 方案

## 5. 长期改进
- 建立数据分类分级制度
- 实施最小权限原则
- 定期进行安全审计
- 加强员工安全意识培训
""",
        "service-down": """# 服务宕机恢复步骤

## 1. 快速诊断
- 确认受影响的服务范围
- 检查系统资源使用情况
- 查看关键日志和错误信息
- 确定故障类型（硬件/软件/网络/攻击）

## 2. 服务恢复
- 重启受影响的服务
- 回滚最近的变更（如适用）
- 切换到备用系统/数据中心
- 增加系统资源（如需要）

## 3. 流量管理
- 启用流量降级策略
- 设置维护页面
- 通知用户服务状态
- 分流非关键流量

## 4. 根因修复
- 修复导致宕机的根本原因
- 应用必要的补丁和更新
- 优化系统配置
- 增加冗余和容错能力

## 5. 预防措施
- 完善监控告警系统
- 建立容量规划流程
- 定期进行灾难恢复演练
- 更新运维手册和 SOP
""",
        "payment-fraud": """# 支付欺诈恢复步骤

## 1. 止损措施
- 立即冻结可疑交易
- 暂停相关账户支付功能
- 通知支付渠道风控团队
- 撤销正在处理的欺诈交易

## 2. 欺诈调查
- 分析欺诈交易模式
- 追踪资金流向
- 识别欺诈账户和关联账户
- 收集证据用于后续处理

## 3. 损失挽回
- 联系支付渠道申请拒付
- 向执法部门报案
- 通过法律途径追索损失
- 与保险公司联系理赔

## 4. 系统加固
- 增强交易风控规则
- 部署欺诈检测模型
- 加强身份验证措施
- 增加人工审核环节

## 5. 流程优化
- 建立欺诈黑名单机制
- 完善风控预警体系
- 定期评估风控效果
- 培训客服识别欺诈行为
""",
        "malware-detected": """# 恶意软件恢复步骤

## 1. 隔离与遏制
- 断开受感染系统的网络连接
- 隔离受感染的主机/容器
- 停止可疑进程
- 防止横向扩散

## 2. 恶意软件分析
- 采集恶意软件样本
- 分析恶意软件类型和行为
- 确定 C2 通信地址
- 评估数据泄露风险

## 3. 清理与修复
- 使用杀毒软件清除恶意软件
- 手动清理残留文件和注册表
- 删除恶意软件创建的账户
- 清理持久化机制

## 4. 系统恢复
- 从干净备份恢复系统
- 重装受影响的操作系统（如需要）
- 恢复被加密或删除的数据
- 更新所有软件和补丁

## 5. 安全加固
- 部署终端检测响应 (EDR)
- 加强网络分段和隔离
- 实施应用白名单
- 增强安全监控能力
""",
        "ddos-attack": """# DDoS 攻击恢复步骤

## 1. 快速响应
- 启用 DDoS 防护服务
- 切换到高防 IP/CDN
- 配置流量清洗规则
- 联系 ISP 协助

## 2. 攻击分析
- 分析攻击类型（流量型/协议型/应用层）
- 识别攻击源 IP
- 评估攻击规模
- 确定攻击目标

## 3. 防护措施
- 配置防火墙规则过滤攻击流量
- 启用 SYN Cookie
- 限制连接速率
- 屏蔽已知攻击源

## 4. 服务恢复
- 逐步恢复正常流量
- 监控系统资源使用
- 验证服务可用性
- 通知用户恢复状态

## 5. 长期防护
- 部署专业 DDoS 防护方案
- 建立弹性扩展能力
- 完善应急响应预案
- 定期进行压力测试
""",
        "ransomware": """# 勒索软件恢复步骤

## 1. 立即隔离
- 断开所有受感染系统
- 关闭共享驱动器
- 停止文件同步服务
- 隔离备份系统

## 2. 勒索软件分析
- 识别勒索软件变种
- 确定加密文件范围
- 检查是否有已知解密工具
- 评估数据损失程度

## 3. 数据恢复
- 从离线备份恢复数据
- 使用已知解密工具（如有）
- 评估是否需要专业数据恢复服务
- 不要支付赎金（除非绝境且无他法）

## 4. 系统重建
- 完全清除勒索软件
- 重装操作系统
- 恢复应用和数据
- 验证系统完整性

## 5. 预防加固
- 实施离线备份策略
- 部署反勒索软件方案
- 加强邮件安全网关
- 定期进行备份恢复演练
""",
        "social-engineering": """# 社会工程攻击恢复步骤

## 1. 识别与止损
- 识别攻击类型（钓鱼/假冒/诈骗）
- 阻止正在进行的攻击
- 通知可能的受害者
- 下架钓鱼网站/内容

## 2. 影响评估
- 确定受害者数量
- 评估泄露的信息
- 追踪攻击来源
- 分析攻击手法

## 3. 受害者救助
- 重置可能泄露的密码
- 取消可能泄露的凭证
- 通知受影响的员工/客户
- 提供身份保护建议

## 4. 防护加强
- 加强邮件安全检测
- 部署反钓鱼方案
- 完善身份验证流程
- 加强敏感操作确认

## 5. 意识培训
- 开展安全意识培训
- 分享攻击案例分析
- 建立可疑活动报告机制
- 定期进行钓鱼演练
""",
        "insider-threat": """# 内部威胁恢复步骤

## 1. 控制与隔离
- 撤销涉事员工权限
- 回收公司设备和资产
- 保留所有证据
- 必要时报警处理

## 2. 调查取证
- 审计员工系统活动日志
- 分析数据访问记录
- 确定泄露/破坏的数据范围
- 追踪异常行为时间线

## 3. 损失评估
- 评估知识产权损失
- 确定客户数据泄露情况
- 评估业务影响
- 计算经济损失

## 4. 补救措施
- 恢复被删除/篡改的数据
- 修复系统漏洞
- 加强离职审计流程
- 完善保密协议

## 5. 预防机制
- 实施最小权限原则
- 部署用户行为分析 (UBA)
- 加强离职审计流程
- 建立举报机制
""",
        "third-party-breach": """# 第三方泄露恢复步骤

## 1. 信息收集
- 确认第三方泄露详情
- 获取泄露数据范围
- 了解泄露原因
- 评估影响程度

## 2. 应急响应
- 暂停与第三方的数据共享
- 撤销第三方的访问权限
- 评估是否需要通知用户
- 启动合同约定的应急流程

## 3. 风险评估
- 评估泄露数据的敏感程度
- 确定受影响的用户/业务
- 分析潜在风险
- 制定应对策略

## 4. 法律处理
- 审查合同责任条款
- 咨询法律顾问
- 准备监管报告（如需要）
- 评估索赔可能性

## 5. 供应链安全改进
- 完善供应商安全评估流程
- 加强合同中的安全条款
- 实施数据共享最小化
- 建立供应商监控机制
""",
    }

    return recovery_guides.get(incident_type, """# 通用恢复步骤

## 1. 止损与隔离
- 立即停止正在进行的损害
- 隔离受影响的系统
- 保留所有证据和日志

## 2. 影响评估
- 确定受影响的系统范围
- 评估数据损失情况
- 分析业务影响

## 3. 根因修复
- 确定事件根本原因
- 修复导致事件的漏洞
- 应用必要的安全补丁

## 4. 恢复运营
- 从备份恢复数据
- 逐步恢复服务
- 监控系统稳定性

## 5. 总结改进
- 进行事件复盘
- 更新安全策略
- 完善监控和告警
""")


def get_incident_template() -> str:
    """
    获取事件报告模板

    Returns:
        事件报告模板 (Markdown 格式)
    """
    return INCIDENT_REPORT_TEMPLATE


def list_incident_types() -> List[Dict[str, str]]:
    """
    列出所有事件类型

    Returns:
        事件类型列表，每项包含 type, name, severity, description
    """
    result = []
    for incident_type, info in INCIDENT_TYPES.items():
        result.append({
            "type": incident_type,
            "name": info.get("name", incident_type),
            "severity": info.get("severity", "MEDIUM"),
            "severity_label": SEVERITY_LEVELS.get(info.get("severity", "MEDIUM"), {}).get("label", "未知"),
            "description": info.get("description", ""),
        })
    return result


if __name__ == "__main__":
    # 测试代码
    print("=== 测试事件分类 ===")

    test_descriptions = [
        "发现大量用户账号异常登录，疑似撞库攻击",
        "数据库被黑客入侵，用户个人信息泄露",
        "核心服务502错误，用户无法访问",
        "检测到服务器上有挖矿病毒",
    ]

    for desc in test_descriptions:
        result = classify_incident(desc)
        print(f"\n描述: {desc}")
        print(f"分类: {result.incident_type} ({result.severity_label})")
        print(f"置信度: {result.confidence:.2f}")
        print(f"匹配关键词: {result.keywords_matched}")

    print("\n=== 测试事件类型列表 ===")
    types = list_incident_types()
    for t in types[:5]:
        print(f"- {t['type']}: {t['name']} ({t['severity_label']})")
