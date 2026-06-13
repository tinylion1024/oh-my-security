"""
合规自查审计模块 - Oh-My-Security

检测数据合规相关问题:
- GDPR 违规风险
- 隐私政策合规
- 同意机制合规
- 数据跨境传输
- 数据保留期限
- 数据主体权利
- Cookie 合规
- 数据泄露通知
- 儿童数据保护
- 员工数据处理
"""
import os
import re
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ComplianceFinding:
    """合规发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 合规类别
    regulation: str  # 相关法规
    description: str
    impact: str
    recommendation: str
    details: str = ""


# 合规自查最佳实践指南
COMPLIANCE_GUIDE = """
# 数据合规自查最佳实践指南

## 1. GDPR 合规要点

### 适用范围
GDPR 适用于：
- 在欧盟境内处理个人数据的组织
- 向欧盟居民提供商品/服务的组织
- 监控欧盟居民行为的组织

### 核心原则
| 原则 | 说明 | 实践要点 |
|------|------|---------|
| 合法性 | 必须有合法基础 | 同意、合同、法定义务等 |
| 目的限制 | 只为特定目的收集 | 明确告知收集目的 |
| 数据最小化 | 只收集必要数据 | 评估每项数据必要性 |
| 准确性 | 保持数据准确 | 提供更正机制 |
| 存储限制 | 不超期保留 | 制定保留期限策略 |
| 完整性保密性 | 确保数据安全 | 加密、访问控制 |
| 可问责性 | 能证明合规 | 记录处理活动 |

### 违规处罚
- 一般违规：最高 1000 万欧元或年营业额 2%
- 严重违规：最高 2000 万欧元或年营业额 4%

## 2. 隐私政策要求

### 必须包含的内容
```markdown
1. 数据控制者信息
   - 公司名称
   - 联系方式
   - DPO 信息（如适用）

2. 数据收集范围
   - 收集哪些数据
   - 收集方式
   - 是否收集敏感数据

3. 数据使用目的
   - 每个目的的具体说明
   - 法律依据

4. 数据共享情况
   - 第三方类型
   - 共享目的
   - 保护措施

5. 数据主体权利
   - 访问权
   - 更正权
   - 删除权
   - 可携带权
   - 反对权

6. 数据保留期限
   - 各类数据保留时间
   - 删除标准

7. Cookie 政策
   - 使用的 Cookie 类型
   - 用途说明
   - 如何管理

8. 数据跨境传输
   - 目的地国家
   - 保护措施

9. 用户权利行使方式
   - 联系渠道
   - 响应时间

10. 政策更新说明
    - 更新日期
    - 如何通知用户
```

### 常见问题
- 隐私政策难以理解（法律术语过多）
- 未提供本地语言版本
- 更新后未通知用户
- 未在收集前告知

## 3. 同意机制合规

### 有效同意要素
1. **自愿性**: 拒绝不会导致服务无法使用
2. **具体性**: 每个目的需要单独同意
3. **知情性**: 用户理解同意的内容
4. **明确性**: 通过主动行为表达同意
5. **可撤回性**: 可以随时撤销

### 同意界面设计
```
✅ 正确做法:
□ 我同意接收营销邮件
□ 我同意分享数据给第三方合作伙伴

❌ 错误做法:
□ 我同意所有条款和隐私政策（捆绑同意）
□ 预先勾选的同意框
□ 只有"同意"按钮，没有"拒绝"选项
```

### Cookie 同意
```
Cookie 横幅必须:
- 明确告知使用了哪些 Cookie
- 允许用户选择接受或拒绝
- 提供细粒度控制（按类别选择）
- 保存用户偏好
- 允许更改设置

禁止:
- 欺骗性设计（只有"接受"按钮明显）
- 强制接受才能使用网站
- 默认启用非必要 Cookie
```

## 4. 数据跨境传输

### 合法传输机制
1. **充分性决定**: 传输到欧盟认可的国家
2. **标准合同条款 (SCC)**: 签署欧盟委员会批准的条款
3. **约束性企业规则 (BCR)**: 集团内部数据传输
4. **同意**: 用户明确同意传输

### 风险评估
```
跨境传输前需评估:
- 目的地国家法律环境
- 当地政府访问数据的风险
- 数据保护水平
- 是否需要额外保护措施
```

### 主要合规市场
```
欧盟认可的数据保护充分国家:
- 英国 (脱欧后临时认可)
- 日本
- 韩国
- 加拿大 (商业组织)
- 阿根廷
- 以色列
- 新西兰
- 瑞士
- 安道尔
- 法罗群岛
- 根西岛
- 马恩岛
- 泽西岛
- 乌拉圭
```

## 5. 数据保留期限

### 设定保留期限
```
考虑因素:
1. 法律法规要求
   - 税务记录: 5-10 年
   - 医疗记录: 15-30 年
   - 员工记录: 劳动法要求

2. 合同义务
   - 保修期相关数据
   - 争议解决需要

3. 商业需要
   - 客户关系维护
   - 服务改进

4. 最小化原则
   - 超出法定/商业需求即删除
   - 匿名化处理
```

### 数据分类保留示例
| 数据类型 | 保留期限 | 法律依据 |
|---------|---------|---------|
| 账户信息 | 账户注销后 30 天 | 合同履行 |
| 交易记录 | 7 年 | 税务法规 |
| 日志记录 | 90 天 | 安全审计 |
| 营销数据 | 同意撤回后立即删除 | 同意 |
| 投诉记录 | 3 年 | 法律抗辩 |

## 6. 数据主体权利

### 权利清单
```
GDPR 赋予的权利:
1. 知情权 - 了解数据如何被处理
2. 访问权 - 获取个人数据副本
3. 更正权 - 修正不准确的数据
4. 删除权 - 要求删除个人数据
5. 限制处理权 - 限制数据处理
6. 可携带权 - 以结构化格式获取数据
7. 反对权 - 反对特定处理
8. 自动化决策权 - 不受纯自动化决策影响
```

### 响应要求
```
时间: 收到请求后 30 天内响应
延长: 复杂请求可延长至 90 天，但需告知
费用: 一般免费，过度频繁可收合理费用
拒绝: 必须说明理由，告知投诉权利
```

## 7. Cookie 合规

### Cookie 分类
| 类型 | 说明 | 同意要求 |
|------|------|---------|
| 必要 Cookie | 服务运行必需 | 无需同意 |
| 功能 Cookie | 记住用户偏好 | 需要同意 |
| 分析 Cookie | 了解用户行为 | 需要同意 |
| 营销 Cookie | 个性化广告 | 需要同意 |

### 实施要求
```
1. Cookie 横幅
   - 首次访问时显示
   - 明确告知目的
   - 提供接受/拒绝选项
   - 链接到详细设置

2. Cookie 设置页面
   - 按类别显示 Cookie
   - 允许单独开关
   - 显示 Cookie 目的和有效期
   - 保存用户偏好

3. 技术实施
   - 用户同意前不设置非必要 Cookie
   - 使用 Cookie 管理平台
   - 定期扫描 Cookie 使用情况
```

## 8. 数据泄露通知

### 通知义务
```
监管机构通知 (72小时内):
- 泄露性质和类别
- 受影响数据主体数量
- DPO 联系方式
- 泄露可能后果
- 已采取的措施

数据主体通知 (无不当延迟):
- 泄露性质
- DPO 联系方式
- 可能后果
- 用户可采取的措施
```

### 泄露处理流程
```
1. 发现与记录
   - 记录发现时间
   - 初步评估影响
   - 启动应急响应

2. 遏制与分析
   - 止损措施
   - 确定泄露范围
   - 评估风险等级

3. 通知决策
   - 是否需要通知监管机构
   - 是否需要通知受影响用户
   - 准备通知内容

4. 文档记录
   - 完整记录处理过程
   - 保存证据
   - 总结改进
```

## 9. 儿童数据保护

### 特殊要求
```
同意年龄:
- 13-16 岁以下需要监护人同意（各国规定不同）
- 必须进行年龄验证
- 提供"适龄"隐私声明

保护措施:
- 不收集非必要数据
- 默认最高隐私设置
- 禁止定向广告
- 家长控制机制
```

### 合规要点
```
✅ 必须:
- 验证用户年龄
- 获取监护人同意
- 提供家长控制功能
- 设计适龄界面

❌ 禁止:
- 默认收集儿童数据
- 向儿童推送广告
- 出售儿童数据
- 公开儿童个人信息
```

## 10. 员工数据处理

### 处理原则
```
合法性基础:
- 劳动合同履行
- 法定义务
- 合法利益（需评估）

告知要求:
- 处理目的
- 数据类别
- 接收方
- 保留期限
- 权利说明
```

### 监控与隐私
```
允许的监控:
- 工作设备使用监控
- 工作时间记录
- 安全审计日志

禁止的监控:
- 私人通讯监控
- 更衣室/卫生间监控
- 超出必要范围的监控

要求:
- 事前告知
- 比例原则
- 最小化原则
- 数据安全
```

## 合规检查清单

### 基础合规
- [ ] 有明确的隐私政策
- [ ] 隐私政策易于理解和访问
- [ ] 收集前告知目的和法律依据
- [ ] 获得有效同意（如适用）
- [ ] 提供同意撤回机制
- [ ] 实施数据最小化原则
- [ ] 制定数据保留期限
- [ ] 实施数据安全措施

### 权利保障
- [ ] 提供数据访问渠道
- [ ] 支持数据更正请求
- [ ] 支持数据删除请求
- [ ] 响应时间符合法定要求
- [ ] 记录所有请求处理

### 风险管理
- [ ] 进行数据保护影响评估
- [ ] 记录数据处理活动
- [ ] 签署数据处理协议（如有处理者）
- [ ] 制定数据泄露响应计划
- [ ] 定期进行合规审计

### 特殊场景
- [ ] Cookie 同意机制合规
- [ ] 儿童数据处理符合要求
- [ ] 跨境传输有合法机制
- [ ] 员工数据处理合规
- [ ] 第三方数据处理合规
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


def check_gdpr_violation(practice_info: Dict) -> List[ComplianceFinding]:
    """
    检查 GDPR 违规风险

    Args:
        practice_info: 数据处理实践信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查法律基础
    if not practice_info.get('has_legal_basis', False):
        findings.append(ComplianceFinding(
            severity="CRITICAL",
            category="法律基础",
            regulation="GDPR Art.6",
            description="数据处理缺乏合法基础",
            impact="可能面临监管处罚和用户投诉",
            recommendation="为每项数据处理活动确定合法基础"
        ))

    # 检查目的限制
    if not practice_info.get('purpose_specified', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="目的限制",
            regulation="GDPR Art.5(1)(b)",
            description="未明确告知数据处理目的",
            impact="违反透明性原则",
            recommendation="在隐私政策中明确说明每项数据收集的目的"
        ))

    # 检查数据最小化
    if practice_info.get('collects_more_than_needed', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="数据最小化",
            regulation="GDPR Art.5(1)(c)",
            description="收集超出必要范围的数据",
            impact="增加数据泄露风险，违反最小化原则",
            recommendation="评估每项数据字段的必要性"
        ))

    # 检查处理活动记录
    if not practice_info.get('has_processing_record', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="可问责性",
            regulation="GDPR Art.30",
            description="未建立数据处理活动记录",
            impact="无法证明合规，难以应对监管检查",
            recommendation="建立并维护数据处理活动记录 (ROPA)"
        ))

    return findings


def check_privacy_policy(policy_info: Dict) -> List[ComplianceFinding]:
    """
    检查隐私政策合规

    Args:
        policy_info: 隐私政策信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查隐私政策是否存在
    if not policy_info.get('exists', False):
        findings.append(ComplianceFinding(
            severity="CRITICAL",
            category="隐私政策缺失",
            regulation="GDPR Art.13/14",
            description="未提供隐私政策",
            impact="严重违规，可能面临高额罚款",
            recommendation="立即制定并发布隐私政策"
        ))
        return findings

    # 检查必要内容
    required_sections = [
        ('controller_info', '数据控制者信息'),
        ('data_types', '数据收集范围'),
        ('purposes', '数据处理目的'),
        ('legal_basis', '法律依据'),
        ('recipients', '数据接收方'),
        ('retention_period', '数据保留期限'),
        ('user_rights', '用户权利'),
        ('contact_info', '联系方式'),
    ]

    for section, name in required_sections:
        if not policy_info.get(section, False):
            findings.append(ComplianceFinding(
                severity="HIGH",
                category="隐私政策内容",
                regulation="GDPR Art.13/14",
                description=f"隐私政策缺少必要内容: {name}",
                impact="告知不完整，可能被认定为违规",
                recommendation=f"在隐私政策中添加{name}相关内容"
            ))

    # 检查是否易于理解
    if policy_info.get('readability_score', 0) < 60:
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="可读性",
            regulation="GDPR Art.12",
            description="隐私政策难以理解（可读性得分低）",
            impact="用户无法真正了解数据处理情况",
            recommendation="使用简洁明了的语言重写隐私政策"
        ))

    # 检查更新日期
    last_updated = policy_info.get('last_updated', '')
    if last_updated:
        try:
            update_date = datetime.strptime(last_updated, '%Y-%m-%d')
            days_since_update = (datetime.now() - update_date).days
            if days_since_update > 365:
                findings.append(ComplianceFinding(
                    severity="LOW",
                    category="政策更新",
                    regulation="GDPR Art.12",
                    description=f"隐私政策已超过 {days_since_update} 天未更新",
                    impact="可能无法反映当前数据处理实践",
                    recommendation="定期审查并更新隐私政策"
                ))
        except:
            pass

    return findings


def check_consent_mechanism(consent_info: Dict) -> List[ComplianceFinding]:
    """
    检查同意机制合规

    Args:
        consent_info: 同意机制信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查同意是否自愿
    if consent_info.get('required_for_service', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="同意自愿性",
            regulation="GDPR Art.7(4)",
            description="同意与核心服务绑定，非自愿",
            impact="同意可能无效，数据处理无合法基础",
            recommendation="区分必要数据处理和可选数据处理"
        ))

    # 检查是否预勾选
    if consent_info.get('pre_checked', False):
        findings.append(ComplianceFinding(
            severity="CRITICAL",
            category="同意方式",
            regulation="GDPR Recital 32",
            description="使用预先勾选的同意框",
            impact="同意无效，属于违规行为",
            recommendation="取消预先勾选，要求主动同意"
        ))

    # 检查是否捆绑同意
    if consent_info.get('bundled', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="同意具体性",
            regulation="GDPR Art.7(2)",
            description="将多个目的捆绑为一个同意",
            impact="同意可能无效",
            recommendation="为每个目的提供单独的同意选项"
        ))

    # 检查撤回机制
    if not consent_info.get('withdraw_mechanism', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="同意撤回",
            regulation="GDPR Art.7(3)",
            description="未提供同意撤回机制",
            impact="违反用户权利",
            recommendation="提供简单易用的同意撤回方式"
        ))

    # 检查撤回难度
    if consent_info.get('withdraw_difficulty', '') == 'hard':
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="撤回难度",
            regulation="GDPR Art.7(3)",
            description="同意撤回比给予同意更困难",
            impact="可能被认定为违规",
            recommendation="确保撤回同意与给予同意同样容易"
        ))

    return findings


def check_data_transfer(transfer_info: Dict) -> List[ComplianceFinding]:
    """
    检查数据跨境传输合规

    Args:
        transfer_info: 数据传输信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查是否有跨境传输
    if not transfer_info.get('has_cross_border', False):
        return findings

    # 检查目的地国家
    destination = transfer_info.get('destination_country', '')
    adequate_countries = [
        'UK', 'JP', 'KR', 'CA', 'AR', 'IL', 'NZ', 'CH', 'AD', 'FO',
        'GG', 'IM', 'JE', 'UY', 'GB'
    ]

    if destination not in adequate_countries:
        # 检查是否有保护措施
        safeguards = transfer_info.get('safeguards', [])

        if 'scc' not in safeguards and 'bcr' not in safeguards:
            findings.append(ComplianceFinding(
                severity="HIGH",
                category="跨境传输保护",
                regulation="GDPR Ch.V",
                description=f"向非充分性认可国家({destination})传输数据缺乏保护措施",
                impact="可能违反跨境传输规定",
                recommendation="签署标准合同条款或实施其他保护措施",
                details=f"目的地: {destination}"
            ))

    # 检查传输影响评估
    if not transfer_info.get('transfer_impact_assessment', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="传输风险评估",
            regulation="Schrems II 判例要求",
            description="未进行传输影响评估",
            impact="无法证明传输安全性",
            recommendation="评估目的地国家的数据保护水平"
        ))

    return findings


def check_retention_policy(retention_info: Dict) -> List[ComplianceFinding]:
    """
    检查数据保留期限合规

    Args:
        retention_info: 保留策略信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查是否有保留策略
    if not retention_info.get('has_policy', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="保留策略",
            regulation="GDPR Art.5(1)(e)",
            description="未制定数据保留期限策略",
            impact="可能超期保留数据，违反存储限制原则",
            recommendation="制定各类数据的保留期限策略"
        ))

    # 检查是否有删除机制
    if not retention_info.get('has_deletion_mechanism', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="删除机制",
            regulation="GDPR Art.5(1)(e)",
            description="未实施数据自动删除机制",
            impact="可能无法及时删除过期数据",
            recommendation="建立数据到期自动删除或匿名化机制"
        ))

    # 检查各类数据保留期限
    data_types = retention_info.get('data_types', [])
    for data_type in data_types:
        retention_days = data_type.get('retention_days', 0)
        legal_requirement = data_type.get('legal_requirement_days', 0)

        if retention_days == 0:
            findings.append(ComplianceFinding(
                severity="MEDIUM",
                category="期限未定义",
                regulation="GDPR Art.5(1)(e)",
                description=f"{data_type.get('name')} 保留期限未定义",
                impact="可能无限期保留数据",
                recommendation="为每类数据设定合理的保留期限"
            ))

        # 检查是否超过必要期限
        if legal_requirement > 0 and retention_days > legal_requirement * 2:
            findings.append(ComplianceFinding(
                severity="LOW",
                category="期限过长",
                regulation="GDPR Art.5(1)(e)",
                description=f"{data_type.get('name')} 保留期限({retention_days}天)可能超出必要",
                impact="增加数据泄露风险",
                recommendation="评估保留期限的合理性"
            ))

    return findings


def check_subject_rights(rights_info: Dict) -> List[ComplianceFinding]:
    """
    检查数据主体权利保障

    Args:
        rights_info: 权利保障信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查各项权利的保障
    rights = [
        ('access', '访问权', 'GDPR Art.15'),
        ('rectification', '更正权', 'GDPR Art.16'),
        ('erasure', '删除权', 'GDPR Art.17'),
        ('restriction', '限制处理权', 'GDPR Art.18'),
        ('portability', '可携带权', 'GDPR Art.20'),
        ('objection', '反对权', 'GDPR Art.21'),
    ]

    for right_id, right_name, regulation in rights:
        if not rights_info.get(f'{right_id}_supported', False):
            findings.append(ComplianceFinding(
                severity="HIGH",
                category="主体权利",
                regulation=regulation,
                description=f"未支持用户的{right_name}",
                impact="违反 GDPR 赋予用户的权利",
                recommendation=f"建立{right_name}的请求处理机制"
            ))

    # 检查响应时间
    response_days = rights_info.get('response_days', 60)
    if response_days > 30:
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="响应时间",
            regulation="GDPR Art.12(3)",
            description=f"权利请求响应时间({response_days}天)超过法定要求",
            impact="可能被认定为违规",
            recommendation="确保在 30 天内响应用户请求"
        ))

    # 检查请求处理记录
    if not rights_info.get('keeps_records', False):
        findings.append(ComplianceFinding(
            severity="LOW",
            category="请求记录",
            regulation="GDPR Art.5(2)",
            description="未记录权利请求处理过程",
            impact="难以证明合规",
            recommendation="记录所有权利请求和处理结果"
        ))

    return findings


def check_cookie_compliance(cookie_info: Dict) -> List[ComplianceFinding]:
    """
    检查 Cookie 合规

    Args:
        cookie_info: Cookie 信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查是否有 Cookie 横幅
    if not cookie_info.get('has_banner', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="Cookie 横幅",
            regulation="ePrivacy + GDPR",
            description="未提供 Cookie 同意横幅",
            impact="违反 Cookie 同意要求",
            recommendation="实施 Cookie 同意横幅"
        ))

    # 检查同意选项
    if cookie_info.get('accept_only', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="同意选项",
            regulation="CNIL/ICO 指南",
            description='仅提供"接受"选项',
            impact='属于"暗黑模式"，同意无效',
            recommendation='提供"接受"和"拒绝"两个明确选项'
        ))

    # 检查非必要 Cookie
    if cookie_info.get('non_essential_before_consent', False):
        findings.append(ComplianceFinding(
            severity="CRITICAL",
            category="Cookie 加载",
            regulation="ePrivacy Art.5(3)",
            description="同意前加载非必要 Cookie",
            impact="严重违规",
            recommendation="同意前不加载任何非必要 Cookie"
        ))

    # 检查 Cookie 管理
    if not cookie_info.get('has_preferences', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="Cookie 设置",
            regulation="GDPR Art.7(3)",
            description="未提供 Cookie 偏好管理功能",
            impact="用户无法更改 Cookie 设置",
            recommendation="提供 Cookie 设置页面，允许用户更改偏好"
        ))

    return findings


def check_breach_notification(breach_info: Dict) -> List[ComplianceFinding]:
    """
    检查数据泄露通知准备

    Args:
        breach_info: 泄露响应信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查是否有泄露响应计划
    if not breach_info.get('has_response_plan', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="泄露响应计划",
            regulation="GDPR Art.33/34",
            description="未制定数据泄露响应计划",
            impact="发生泄露时可能无法及时响应",
            recommendation="制定数据泄露响应计划，包括流程和责任人"
        ))

    # 检查是否有通知模板
    if not breach_info.get('has_notification_templates', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="通知准备",
            regulation="GDPR Art.33/34",
            description="未准备泄露通知模板",
            impact="可能延误通知时间",
            recommendation="准备监管机构和用户通知模板"
        ))

    # 检查是否进行演练
    if not breach_info.get('has_drill', False):
        findings.append(ComplianceFinding(
            severity="LOW",
            category="响应演练",
            regulation="GDPR Art.33",
            description="未进行泄露响应演练",
            impact="实际发生时可能响应不及时",
            recommendation="定期进行泄露响应演练"
        ))

    return findings


def check_children_data(children_info: Dict) -> List[ComplianceFinding]:
    """
    检查儿童数据保护

    Args:
        children_info: 儿童数据处理信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查是否有年龄验证
    if children_info.get('may_process_children', False):
        if not children_info.get('has_age_verification', False):
            findings.append(ComplianceFinding(
                severity="CRITICAL",
                category="年龄验证",
                regulation="GDPR Art.8",
                description="可能处理儿童数据但无年龄验证",
                impact="可能非法处理儿童数据",
                recommendation="实施年龄验证机制"
            ))

        # 检查监护人同意
        if not children_info.get('has_parental_consent', False):
            findings.append(ComplianceFinding(
                severity="CRITICAL",
                category="监护人同意",
                regulation="GDPR Art.8",
                description="未获取监护人同意",
                impact="儿童数据处理无合法基础",
                recommendation="对儿童用户获取监护人同意"
            ))

    # 检查隐私设置
    if not children_info.get('high_privacy_default', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="默认设置",
            regulation="GDPR Art.25",
            description="未对儿童账户设置高隐私默认",
            impact="可能暴露儿童隐私",
            recommendation="为儿童账户设置最高隐私保护默认"
        ))

    return findings


def check_employee_data(employee_info: Dict) -> List[ComplianceFinding]:
    """
    检查员工数据处理合规

    Args:
        employee_info: 员工数据处理信息字典

    Returns:
        合规发现列表
    """
    findings = []

    # 检查是否有员工隐私政策
    if not employee_info.get('has_employee_policy', False):
        findings.append(ComplianceFinding(
            severity="HIGH",
            category="员工隐私政策",
            regulation="GDPR Art.13/14",
            description="未提供单独的员工隐私政策",
            impact="员工未被告知数据处理情况",
            recommendation="制定专门的员工隐私政策"
        ))

    # 检查监控告知
    if employee_info.get('has_monitoring', False):
        if not employee_info.get('monitoring_disclosed', False):
            findings.append(ComplianceFinding(
                severity="HIGH",
                category="监控告知",
                regulation="GDPR Art.13/14",
                description="实施监控但未告知员工",
                impact="可能违反透明性原则",
                recommendation="明确告知员工监控范围和目的"
            ))

    # 检查数据处理协议
    if not employee_info.get('has_dpa', False):
        findings.append(ComplianceFinding(
            severity="MEDIUM",
            category="处理协议",
            regulation="GDPR Art.28",
            description="未与员工数据处理方签署协议",
            impact="数据处理责任不清",
            recommendation="与 HR 系统供应商签署数据处理协议"
        ))

    return findings


def audit_compliance(compliance_data: Dict) -> str:
    """
    综合合规审计

    Args:
        compliance_data: 合规数据字典

    Returns:
        格式化的 Markdown 合规报告
    """
    all_findings: List[ComplianceFinding] = []

    # 执行各项检查
    all_findings.extend(check_gdpr_violation(compliance_data.get('practices', {})))
    all_findings.extend(check_privacy_policy(compliance_data.get('privacy_policy', {})))
    all_findings.extend(check_consent_mechanism(compliance_data.get('consent', {})))
    all_findings.extend(check_data_transfer(compliance_data.get('data_transfer', {})))
    all_findings.extend(check_retention_policy(compliance_data.get('retention', {})))
    all_findings.extend(check_subject_rights(compliance_data.get('rights', {})))
    all_findings.extend(check_cookie_compliance(compliance_data.get('cookies', {})))
    all_findings.extend(check_breach_notification(compliance_data.get('breach_response', {})))
    all_findings.extend(check_children_data(compliance_data.get('children', {})))
    all_findings.extend(check_employee_data(compliance_data.get('employee', {})))

    return _generate_compliance_report(all_findings)


def _generate_compliance_report(findings: List[ComplianceFinding]) -> str:
    """生成合规审计报告"""
    if not findings:
        return """# 合规审计报告

## 审计结果

**状态**: ✅ 未发现明显的合规风险

---

*建议定期进行合规审查，保持数据处理合法合规。*
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

    report = f"""# 合规审计报告

## 风险统计

| 严重程度 | 数量 |
|---------|------|
| 🔴 CRITICAL | {stats['CRITICAL']} |
| 🟠 HIGH | {stats['HIGH']} |
| 🟡 MEDIUM | {stats['MEDIUM']} |
| 🔵 LOW | {stats['LOW']} |
| **总计** | **{len(findings)}** |

---

## 发现详情

"""

    for i, f in enumerate(sorted_findings, 1):
        severity_emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🔵'}
        emoji = severity_emoji.get(f.severity, '⚪')

        report += f"""### {i}. {emoji} [{f.severity}] {f.category}

**法规依据**: {f.regulation}

**问题**: {f.description}

**影响**: {f.impact}

**建议**: {f.recommendation}

"""

        if f.details:
            report += f"**详情**: {f.details}\n\n"

        report += "---\n\n"

    return report


def get_compliance_guide() -> str:
    """
    获取合规最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return COMPLIANCE_GUIDE


# 模块导出
__all__ = [
    'audit_compliance',
    'check_gdpr_violation',
    'check_privacy_policy',
    'check_consent_mechanism',
    'check_data_transfer',
    'check_retention_policy',
    'check_subject_rights',
    'check_cookie_compliance',
    'check_breach_notification',
    'check_children_data',
    'check_employee_data',
    'get_compliance_guide',
    'ComplianceFinding',
]


if __name__ == "__main__":
    # 测试代码
    test_data = {
        'practices': {
            'has_legal_basis': False,
            'purpose_specified': True,
        },
        'privacy_policy': {
            'exists': True,
            'controller_info': True,
            'user_rights': False,
        },
        'consent': {
            'pre_checked': True,
            'withdraw_mechanism': False,
        },
        'cookies': {
            'has_banner': True,
            'accept_only': True,
        }
    }

    print(audit_compliance(test_data))
