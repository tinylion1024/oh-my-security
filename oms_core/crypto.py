"""
加密资产安全审计模块 - Oh-My-Security

检测加密资产相关安全问题:
- 私钥泄露风险
- 签名钓鱼检测
- 授权攻击风险
- 助记词安全
- 钱包抽干检测
- 智能合约漏洞
- 跨链桥风险
- 粉尘攻击检测
- 剪贴板劫持
- 假钱包检测
"""
import os
import re
import subprocess
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CryptoFinding:
    """加密资产安全发现结果"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # 安全类别
    chain: str  # 链名称
    description: str
    impact: str
    recommendation: str
    details: str = ""


# 加密资产安全最佳实践指南
CRYPTO_SECURITY_GUIDE = """
# 加密资产安全最佳实践指南

## 1. 私钥安全

### 私钥存储原则
- **永不联网**: 私钥永远不要存储在联网设备
- **离线备份**: 使用纸钱包或金属备份
- **多点备份**: 地理分散的多个备份
- **加密存储**: 如需数字存储，必须加密

### 私钥泄露后果
- 资产被瞬间转走
- 无法撤销权限
- 无追回机制
- 不可逆损失

### 安全实践
```
正确做法:
- 使用硬件钱包存储大额资产
- 纸钱包打印后密封保存
- 使用 Shamir Secret Sharing 分割私钥

错误做法:
- 截图保存私钥
- 发送到邮箱/云盘
- 存储在笔记软件
- 复制到剪贴板
```

## 2. 签名安全

### 签名钓鱼原理
攻击者诱导用户签署恶意消息，获得:
- 代币授权 (approve)
- 转账权限
- NFT 转移权限
- 合约操作权限

### 常见签名钓鱼
```
恶意签名类型:
- permit 签名 → 无 gas 授权攻击
- Seaport 签名 → NFT 被转移
- EIP-2612 → 代币授权
- setApprovalForAll → 所有 NFT 授权
```

### 防护措施
- 仔细阅读签名内容
- 使用钱包安全扫描
- 不在陌生网站签名
- 定期撤销授权

## 3. 授权安全

### 授权攻击类型
- **无限授权**: approve(amount: MAX_UINT256)
- **恶意合约**: 授权钓鱼合约
- **过期授权**: 忘记撤销的历史授权

### 检查和撤销
```
检查授权工具:
- https://revoke.cash
- https://app.unrekt.net
- Etherscan Token Approvals

定期检查:
- 至少每月一次
- 连接新 DApp 后立即检查
- 钱包被盗后立即撤销
```

## 4. 助记词安全

### 助记词风险
- 网络钓鱼窃取
- 屏幕截图
- 键盘记录
- 社会工程
- 物理窃取

### 安全存储
```
最佳实践:
1. 手写记录，不打印/截图
2. 使用金属助记词板（防火防水）
3. 分开存储（如 12 词分 2 处）
4. 使用 Shamir 分割

不要:
- 存储在云端
- 发送到聊天软件
- 告诉任何人
- 输入到网页
```

## 5. 钱包抽干攻击

### 攻击原理
1. 用户授权恶意合约
2. 合约批量转移用户资产
3. 包括所有代币和 NFT
4. 一键清空钱包

### 防护措施
- 使用硬件钱包
- 设置交易限额
- 多签管理大额资产
- 定期检查授权

## 6. 智能合约安全

### 常见漏洞
- 重入攻击
- 整数溢出
- 权限绕过
- 价格操控
- 闪电贷攻击

### 交互安全
```
检查清单:
- [ ] 合约是否已审计
- [ ] TVL 和用户量
- [ ] 社区口碑
- [ ] 代码开源情况
- [ ] 多签管理
- [ ] 时间锁机制
```

## 7. 跨链桥安全

### 跨链桥风险
跨链桥是 DeFi 最危险的基础设施：
- 历史上数十亿美元被盗
- 智能合约复杂度高
- 多链验证机制薄弱

### 安全使用
- 只使用主流跨链桥
- 跨链后立即撤销授权
- 不在桥上长期存资产
- 关注安全公告

## 8. 粉尘攻击

### 攻击原理
攻击者向钱包发送小额代币，目的:
- 追踪钱包地址关联
- 诱导用户交互恶意合约
- 破坏隐私

### 防护措施
- 不触碰未知代币
- 使用隐私解决方案
- 分离交易地址

## 9. 剪贴板安全

### 剪贴板劫持
- 恶意软件监控剪贴板
- 替换钱包地址
- 用户粘贴时转错地址

### 防护措施
```
保护措施:
- 使用硬件钱包确认地址
- 不复制粘贴地址
- 使用二维码转账
- 检查地址首尾字符
- 使用防剪贴板泄露工具
```

## 10. 假钱包检测

### 假钱包特征
- 非官方渠道下载
- 界面粗糙或过度华丽
- 要求输入助记词
- 无法验证签名
- 评分异常

### 验证方法
```
官方渠道:
- MetaMask: metamask.io
- Trust Wallet: trustwallet.com
- Ledger: ledger.com
- Trezor: trezor.io

验证:
- 检查域名拼写
- 查看应用签名
- 检查开发者信息
- 阅读用户评论
```

## 紧急响应

### 私钥泄露
1. 立即转移资产到新地址
2. 撤销所有授权
3. 检查关联地址
4. 分析泄露原因

### 钱包被盗
1. 立即转移剩余资产
2. 撤销所有授权
3. 冻结 NFT（如支持）
4. 报案和通知交易所

### 授权被盗
1. 使用 revoke.cash 撤销
2. 检查所有链的授权
3. 转移资产到新地址
"""

# 常见区块链配置
CHAIN_CONFIG = {
    'ethereum': {
        'name': 'Ethereum',
        'symbol': 'ETH',
        'explorer': 'https://etherscan.io',
        'revoke_url': 'https://etherscan.io/tokenapprovalchecker'
    },
    'bsc': {
        'name': 'BNB Smart Chain',
        'symbol': 'BNB',
        'explorer': 'https://bscscan.com',
        'revoke_url': 'https://bscscan.com/tokenapprovalchecker'
    },
    'polygon': {
        'name': 'Polygon',
        'symbol': 'MATIC',
        'explorer': 'https://polygonscan.com',
        'revoke_url': 'https://polygonscan.com/tokenapprovalchecker'
    },
    'arbitrum': {
        'name': 'Arbitrum',
        'symbol': 'ARB',
        'explorer': 'https://arbiscan.io',
        'revoke_url': 'https://arbiscan.io/tokenapprovalchecker'
    },
    'optimism': {
        'name': 'Optimism',
        'symbol': 'OP',
        'explorer': 'https://optimistic.etherscan.io',
        'revoke_url': 'https://optimistic.etherscan.io/tokenapprovalchecker'
    },
    'avalanche': {
        'name': 'Avalanche',
        'symbol': 'AVAX',
        'explorer': 'https://snowtrace.io',
        'revoke_url': 'https://snowtrace.io/tokenapprovalchecker'
    },
    'solana': {
        'name': 'Solana',
        'symbol': 'SOL',
        'explorer': 'https://solscan.io',
        'revoke_url': 'https://solscan.io'
    },
    'base': {
        'name': 'Base',
        'symbol': 'ETH',
        'explorer': 'https://basescan.org',
        'revoke_url': 'https://basescan.org/tokenapprovalchecker'
    }
}


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


def check_private_key_leak(wallet_info: Dict) -> List[CryptoFinding]:
    """
    检查私钥泄露风险

    Args:
        wallet_info: 钱包信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查私钥存储方式
    storage_type = wallet_info.get('storage_type', '')

    if storage_type == 'hot_wallet':
        findings.append(CryptoFinding(
            severity="HIGH",
            category="私钥存储",
            chain=wallet_info.get('chain', 'unknown'),
            description="私钥存储在热钱包/浏览器插件",
            impact="联网设备存储增加泄露风险",
            recommendation="大额资产转移到硬件钱包或冷存储"
        ))

    elif storage_type == 'exchange':
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="托管风险",
            chain=wallet_info.get('chain', 'unknown'),
            description="资产存储在中心化交易所",
            impact="无法控制私钥，交易所风险",
            recommendation="长期持有资产转移到自托管钱包"
        ))

    # 检查备份情况
    if not wallet_info.get('has_backup', True):
        findings.append(CryptoFinding(
            severity="CRITICAL",
            category="备份缺失",
            chain=wallet_info.get('chain', 'unknown'),
            description="钱包缺少有效备份",
            impact="设备丢失将导致资产永久丢失",
            recommendation="立即创建并安全存储备份"
        ))

    # 检查备份存储位置
    backup_location = wallet_info.get('backup_location', '')
    insecure_locations = ['cloud', 'email', 'notes', 'photo']
    if backup_location in insecure_locations:
        findings.append(CryptoFinding(
            severity="CRITICAL",
            category="不安全备份",
            chain=wallet_info.get('chain', 'unknown'),
            description=f"助记词/私钥存储在 {backup_location}",
            impact="可能被黑客或恶意软件窃取",
            recommendation="手写备份并存储在安全物理位置"
        ))

    return findings


def check_signature_phishing(transactions: List[Dict]) -> List[CryptoFinding]:
    """
    检查签名钓鱼风险

    Args:
        transactions: 交易列表

    Returns:
        安全发现列表
    """
    findings = []

    # 危险签名模式
    dangerous_signatures = [
        'permit',  # 无 gas 授权
        'setApprovalForAll',  # 全部 NFT 授权
        'safeTransferFrom',  # 转移 NFT
        'approve',  # 代币授权
    ]

    for tx in transactions:
        # 检查是否是签名交易
        if tx.get('type') == 'sign':
            method = tx.get('method', '')

            if method in dangerous_signatures:
                # 检查交易对手
                to_address = tx.get('to', '')
                is_verified = tx.get('contract_verified', False)

                if not is_verified:
                    findings.append(CryptoFinding(
                        severity="HIGH",
                        category="签名钓鱼",
                        chain=tx.get('chain', 'unknown'),
                        description=f"检测到可疑签名请求: {method}",
                        impact="可能导致代币或 NFT 被转移",
                        recommendation="仔细核实交易对手，必要时撤销授权",
                        details=f"目标地址: {to_address}"
                    ))

    return findings


def check_approval_attack(approvals: List[Dict]) -> List[CryptoFinding]:
    """
    检查授权攻击风险

    Args:
        approvals: 授权列表

    Returns:
        安全发现列表
    """
    findings = []

    for approval in approvals:
        amount = approval.get('amount', 0)
        spender = approval.get('spender', '')
        token = approval.get('token', '')
        is_verified = approval.get('spender_verified', False)

        # 检查无限授权
        if amount == 'unlimited' or amount > 1e20:
            findings.append(CryptoFinding(
                severity="HIGH",
                category="无限授权",
                chain=approval.get('chain', 'unknown'),
                description=f"对 {spender[:10]}... 的无限授权",
                impact="授权方可随时转走所有该代币",
                recommendation="撤销无限授权，改为精确金额授权",
                details=f"代币: {token}"
            ))

        # 检查未验证的授权
        if not is_verified:
            findings.append(CryptoFinding(
                severity="MEDIUM",
                category="可疑授权",
                chain=approval.get('chain', 'unknown'),
                description=f"授权给未验证合约: {spender[:10]}...",
                impact="合约可能存在后门或漏洞",
                recommendation="核实合约安全性或撤销授权",
                details=f"代币: {token}"
            ))

        # 检查过期授权
        days_since_approval = approval.get('days_since_approval', 0)
        if days_since_approval > 90:
            findings.append(CryptoFinding(
                severity="LOW",
                category="过期授权",
                chain=approval.get('chain', 'unknown'),
                description=f"存在 {days_since_approval} 天前的旧授权",
                impact="不再使用的授权增加风险",
                recommendation="撤销不再需要的授权"
            ))

    return findings


def check_mnemonic_security(mnemonic_info: Dict) -> List[CryptoFinding]:
    """
    检查助记词安全

    Args:
        mnemonic_info: 助记词信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查存储方式
    storage_method = mnemonic_info.get('storage_method', '')

    insecure_methods = ['digital', 'photo', 'cloud', 'email']
    if storage_method in insecure_methods:
        findings.append(CryptoFinding(
            severity="CRITICAL",
            category="助记词存储",
            chain='multi',
            description=f"助记词以 {storage_method} 方式存储",
            impact="可能被黑客或恶意软件窃取",
            recommendation="立即转移到新钱包，手写销毁旧助记词"
        ))

    # 检查是否分割存储
    if not mnemonic_info.get('split_storage', False):
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="助记词备份",
            chain='multi',
            description="助记词未分割存储",
            impact="单一备份存在单点故障风险",
            recommendation="考虑使用 Shamir 分割或多处存储"
        ))

    # 检查物理安全
    if not mnemonic_info.get('secure_location', False):
        findings.append(CryptoFinding(
            severity="HIGH",
            category="物理安全",
            chain='multi',
            description="助记词备份位置不够安全",
            impact="可能被物理窃取",
            recommendation="存储在防火防水的安全位置"
        ))

    return findings


def check_wallet_drainer(transactions: List[Dict]) -> List[CryptoFinding]:
    """
    检查钱包抽干攻击

    Args:
        transactions: 交易列表

    Returns:
        安全发现列表
    """
    findings = []

    # 已知钱包抽干合约特征
    drainer_patterns = [
        'sweepAll',
        'drain',
        'withdrawAll',
        'emergencyWithdraw',
        'transferAll',
    ]

    for tx in transactions:
        method = tx.get('method', '')

        for pattern in drainer_patterns:
            if pattern.lower() in method.lower():
                findings.append(CryptoFinding(
                    severity="CRITICAL",
                    category="钱包抽干",
                    chain=tx.get('chain', 'unknown'),
                    description=f"检测到可疑方法调用: {method}",
                    impact="可能正在执行钱包抽干攻击",
                    recommendation="立即撤销相关授权，转移资产到新地址",
                    details=f"交易哈希: {tx.get('hash', 'unknown')}"
                ))
                break

    # 检查批量转账
    batch_transfers = [tx for tx in transactions if 'batch' in tx.get('method', '').lower()]
    if len(batch_transfers) > 0:
        findings.append(CryptoFinding(
            severity="HIGH",
            category="批量转账",
            chain=batch_transfers[0].get('chain', 'unknown'),
            description="检测到批量转账操作",
            impact="可能正在批量转移资产",
            recommendation="确认是否为本人操作，检查钱包安全"
        ))

    return findings


def check_smart_contract_risk(contract_info: Dict) -> List[CryptoFinding]:
    """
    检查智能合约风险

    Args:
        contract_info: 合约信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查审计状态
    if not contract_info.get('audited', False):
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="合约审计",
            chain=contract_info.get('chain', 'unknown'),
            description="合约未经安全审计",
            impact="可能存在未知漏洞",
            recommendation="只与经过审计的合约交互"
        ))

    # 检查是否开源
    if not contract_info.get('source_verified', False):
        findings.append(CryptoFinding(
            severity="HIGH",
            category="合约开源",
            chain=contract_info.get('chain', 'unknown'),
            description="合约代码未开源验证",
            impact="无法审计合约逻辑",
            recommendation="避免与未开源合约交互"
        ))

    # 检查 TVL
    tvl = contract_info.get('tvl_usd', 0)
    age_days = contract_info.get('age_days', 0)

    if tvl > 1000000 and age_days < 30:
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="新合约风险",
            chain=contract_info.get('chain', 'unknown'),
            description=f"新合约（{age_days}天）TVL 超过 100 万美元",
            impact="新合约未经充分测试",
            recommendation="谨慎交互，分散风险"
        ))

    # 检查多签
    if not contract_info.get('multisig', False) and tvl > 10000000:
        findings.append(CryptoFinding(
            severity="HIGH",
            category="权限管理",
            chain=contract_info.get('chain', 'unknown'),
            description="高 TVL 合约未使用多签管理",
            impact="单点故障风险高",
            recommendation="确认是否有其他安全机制"
        ))

    return findings


def check_bridge_risk(bridge_info: Dict) -> List[CryptoFinding]:
    """
    检查跨链桥风险

    Args:
        bridge_info: 跨链桥信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 已知安全跨链桥
    trusted_bridges = [
        'arbitrum-official',
        'optimism-official',
        'polygon-pos',
        'across',
        'stargate',
        'layerzero',
    ]

    bridge_name = bridge_info.get('name', '').lower()

    if bridge_name not in trusted_bridges:
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="跨链桥信誉",
            chain=bridge_info.get('chain', 'unknown'),
            description=f"使用非主流跨链桥: {bridge_name}",
            impact="跨链桥历史被盗金额巨大",
            recommendation="优先使用官方或主流跨链桥"
        ))

    # 检查跨链金额
    amount_usd = bridge_info.get('amount_usd', 0)
    if amount_usd > 50000:
        findings.append(CryptoFinding(
            severity="LOW",
            category="大额跨链",
            chain=bridge_info.get('chain', 'unknown'),
            description=f"大额跨链: ${amount_usd:,.0f}",
            impact="跨链期间资产存在风险",
            recommendation="大额跨链分批进行"
        ))

    return findings


def check_dusting_attack(transactions: List[Dict]) -> List[CryptoFinding]:
    """
    检查粉尘攻击

    Args:
        transactions: 交易列表

    Returns:
        安全发现列表
    """
    findings = []

    # 检测小额未知代币转入
    for tx in transactions:
        if tx.get('type') == 'receive' and tx.get('token_type') == 'unknown':
            amount = tx.get('amount', 0)
            if 0 < amount < 1:  # 极小金额
                findings.append(CryptoFinding(
                    severity="LOW",
                    category="粉尘攻击",
                    chain=tx.get('chain', 'unknown'),
                    description="收到未知小额代币",
                    impact="可能被追踪地址关联",
                    recommendation="不要与未知代币交互",
                    details=f"代币地址: {tx.get('token_address', 'unknown')}"
                ))

    return findings


def check_clipboard_hijack(wallet_info: Dict) -> List[CryptoFinding]:
    """
    检查剪贴板劫持风险

    Args:
        wallet_info: 钱包信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查是否使用剪贴板转账
    if wallet_info.get('use_clipboard', True):
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="剪贴板风险",
            chain=wallet_info.get('chain', 'unknown'),
            description="使用剪贴板复制地址转账",
            impact="恶意软件可能替换剪贴板地址",
            recommendation="使用硬件钱包确认或检查地址首尾字符"
        ))

    # 检查是否验证地址
    if not wallet_info.get('verify_address', False):
        findings.append(CryptoFinding(
            severity="LOW",
            category="地址验证",
            chain=wallet_info.get('chain', 'unknown'),
            description="转账时未验证地址完整性",
            impact="可能被劫持到错误地址",
            recommendation="检查地址首尾 4-6 个字符"
        ))

    return findings


def check_fake_wallet(wallet_info: Dict) -> List[CryptoFinding]:
    """
    检查假钱包风险

    Args:
        wallet_info: 钱包信息字典

    Returns:
        安全发现列表
    """
    findings = []

    # 检查下载来源
    download_source = wallet_info.get('download_source', '')
    official_sources = ['official_website', 'app_store', 'play_store', 'chrome_store']

    if download_source not in official_sources:
        findings.append(CryptoFinding(
            severity="CRITICAL",
            category="钱包来源",
            chain='multi',
            description=f"钱包从非官方渠道下载: {download_source}",
            impact="可能是假冒钱包，私钥已被窃取",
            recommendation="立即转移资产，从官方渠道下载新钱包"
        ))

    # 检查版本
    current_version = wallet_info.get('version', '')
    latest_version = wallet_info.get('latest_version', '')
    if current_version and latest_version and current_version < latest_version:
        findings.append(CryptoFinding(
            severity="MEDIUM",
            category="钱包版本",
            chain='multi',
            description=f"钱包版本过旧: {current_version} < {latest_version}",
            impact="可能缺少安全补丁",
            recommendation="更新到最新版本"
        ))

    # 检查是否要求助记词
    if wallet_info.get('requests_mnemonic', False):
        findings.append(CryptoFinding(
            severity="CRITICAL",
            category="可疑行为",
            chain='multi',
            description="钱包要求输入助记词",
            impact="极可能是假钱包或钓鱼应用",
            recommendation="立即停止使用，转移资产"
        ))

    return findings


def audit_crypto_security(wallets: Dict) -> str:
    """
    综合审计加密资产安全配置

    Args:
        wallets: 钱包配置字典

    Returns:
        格式化的 Markdown 安全报告
    """
    all_findings: List[CryptoFinding] = []

    # 执行各项检查
    for chain, config in wallets.items():
        config['chain'] = chain

        all_findings.extend(check_private_key_leak(config))
        all_findings.extend(check_clipboard_hijack(config))
        all_findings.extend(check_fake_wallet(config))

        if 'transactions' in config:
            all_findings.extend(check_signature_phishing(config['transactions']))
            all_findings.extend(check_wallet_drainer(config['transactions']))
            all_findings.extend(check_dusting_attack(config['transactions']))

        if 'approvals' in config:
            all_findings.extend(check_approval_attack(config['approvals']))

        if 'mnemonic' in config:
            all_findings.extend(check_mnemonic_security(config['mnemonic']))

        if 'contracts' in config:
            for contract in config['contracts']:
                all_findings.extend(check_smart_contract_risk(contract))

        if 'bridges' in config:
            for bridge in config['bridges']:
                all_findings.extend(check_bridge_risk(bridge))

    return _generate_crypto_report(all_findings)


def _generate_crypto_report(findings: List[CryptoFinding]) -> str:
    """生成加密资产安全报告"""
    if not findings:
        return """# 加密资产安全审计报告

## 审计结果

**状态**: ✅ 未发现明显的加密资产安全风险

---

*建议定期检查授权，使用硬件钱包存储大额资产。*
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

    report = f"""# 加密资产安全审计报告

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

**链**: {f.chain}

**问题**: {f.description}

**影响**: {f.impact}

**建议**: {f.recommendation}

"""

        if f.details:
            report += f"**详情**: {f.details}\n\n"

        report += "---\n\n"

    # 添加紧急响应建议
    if stats['CRITICAL'] > 0:
        report += """## 🚨 紧急响应建议

检测到严重风险，请立即采取行动：

1. **转移资产**: 将资产转移到新生成的安全地址
2. **撤销授权**: 使用 revoke.cash 撤销所有授权
3. **检查设备**: 扫描设备是否有恶意软件
4. **更换钱包**: 从官方渠道重新下载钱包
5. **备份安全**: 检查助记词备份是否安全

"""

    return report


def get_crypto_guide() -> str:
    """
    获取加密资产安全最佳实践指南

    Returns:
        指南内容 (Markdown 格式)
    """
    return CRYPTO_SECURITY_GUIDE


# 模块导出
__all__ = [
    'audit_crypto_security',
    'check_private_key_leak',
    'check_signature_phishing',
    'check_approval_attack',
    'check_mnemonic_security',
    'check_wallet_drainer',
    'check_smart_contract_risk',
    'check_bridge_risk',
    'check_dusting_attack',
    'check_clipboard_hijack',
    'check_fake_wallet',
    'get_crypto_guide',
    'CryptoFinding',
    'CHAIN_CONFIG',
]


if __name__ == "__main__":
    # 测试代码
    test_wallets = {
        'ethereum': {
            'storage_type': 'hot_wallet',
            'has_backup': True,
            'backup_location': 'cloud',
            'approvals': [
                {
                    'spender': '0x1234...5678',
                    'token': 'USDC',
                    'amount': 'unlimited',
                    'spender_verified': False,
                    'days_since_approval': 100
                }
            ]
        }
    }

    print(audit_crypto_security(test_wallets))
