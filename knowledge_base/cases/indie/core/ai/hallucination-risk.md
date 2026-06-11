# AI 幻觉风险 - 虚假信息的隐形陷阱

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $50-200/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
AI 生成看起来合理但实际上是虚假的信息，误导用户做出错误决策。

### 一分钟识别
你的产品是否有以下特征：
- [ ] AI 生成事实性信息（新闻、数据、知识等）
- [ ] 用户依赖 AI 输出做决策
- [ ] 没有事实核查机制
- [ ] AI 输出没有明确标注"可能不准确"
→ 勾选≥1项，即需关注此风险

### 一句话防御
建立事实核查机制，添加免责声明，让用户知道 AI 输出可能不准确。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 在 AI 输出中添加免责声明
   - 提示用户核实重要信息
   - 标注 AI 生成内容的来源
   
2. [ ] **短期行动项**（本周可完成，免费）
   - 实施基础事实核查
   - 添加引用来源机制
   - 记录 AI 输出日志
   
3. [ ] **长期行动项**（规划中，低成本）
   - 部署专业事实核查 API
   - 建立多源验证机制
   - 实现置信度评分系统

### 推荐工具
- **免费**：
  - 自建置信度评估 - 免费
  - Google Fact Check Tools API - 免费
  - Wikidata API - 免费知识库查询

- **低成本**：
  - ClaimBuster API - $50/月 - 事实核查
  - Google Knowledge Graph API - 免费/低额度
  - Perplexity API - $20/月 - 带引用的 AI 搜索

### 验证方法
- [ ] 测试 AI 对事实性问题的回答准确性
- [ ] 验证是否添加了免责声明
- [ ] 检查是否提供了信息来源
- [ ] 确认用户能看到"AI 生成"提示

---

## L2 小团队版（理解版）

### 场景还原
你的团队开发了一款"AI 研究助手"，帮助用户快速获取信息和撰写报告。产品上线 6 个月，积累了 5000 用户。

某天，用户反馈：AI 助手提供的"历史事件"完全是编造的：
- 虚构了不存在的历史人物
- 编造了虚假的历史事件
- 引用了不存在的文献

用户基于这些信息写了报告，被导师指出全是错误信息。

AI 幻觉输出示例：
```
用户问：请介绍一下 1950 年代的"东京协议"

AI 回答：
1955 年签署的"东京协议"是二战后重要的国际条约...
签署国包括美国、日本、英国等...
该协议确立了亚太地区的贸易框架...
引用来源：《国际关系史》第三卷，P.234

问题：这个协议根本不存在，所有信息都是编造的。
```

**影响评估**：
- 用户信任度下降
- 可能导致用户做出错误决策
- 品牌声誉受损
- 潜在法律责任

### 攻击路径（简化版）

**AI 为什么会产生幻觉**（技术原因）：
1. **概率生成**：AI 基于概率生成文本，而非检索事实
2. **知识过时**：训练数据有时效性，信息可能过时
3. **过度自信**：AI 对不确定的内容也会给出确定回答
4. **缺乏验证**：没有实时的事实核查机制

**产生了什么后果**（具体影响）：
- 误导用户决策
- 损害用户利益
- 降低产品可信度
- 可能面临法律风险

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: 自建事实核查 + 置信度评估

**配置步骤**:

1. 幻觉检测与置信度评估
```python
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class ConfidenceLevel(Enum):
    HIGH = "high"         # 高置信度（有可靠来源）
    MEDIUM = "medium"     # 中等置信度（需要验证）
    LOW = "low"          # 低置信度（可能不准确）
    UNKNOWN = "unknown"   # 无法判断

@dataclass
class FactCheckResult:
    verified: bool
    confidence: ConfidenceLevel
    sources: List[str]
    warnings: List[str]
    suggestions: List[str]

class HallucinationDetector:
    """幻觉检测器"""
    
    def __init__(self):
        # 高风险幻觉模式
        self.hallucination_patterns = {
            # 具体数字/日期（容易编造）
            'specific_numbers': r'\d{4}年|\d{1,2}月\d{1,2}日|¥?\d+[,.]\d+',
            
            # 引用来源（可能编造）
            'citations': r'《[^》]+》|"[^"]+"|according to [^,]+',
            
            # 具体人物（可能虚构）
            'names': r'[A-Z][a-z]+ [A-Z][a-z]+|博士|教授|专家',
            
            # 确定性表述（过度自信）
            'certainty': r'肯定|一定|绝对|definitely|certainly|always',
            
            # 具体地点/机构（可能编造）
            'locations': r'[A-Z][a-z]+ (University|Institute|Center)'
        }
        
        # 需要验证的事实类型
        self.fact_types = {
            'historical_event': ['年', '月', '日', '签署', '成立', '发生'],
            'scientific_fact': ['研究', '发现', '证明', '实验'],
            'statistical_data': ['%', '比例', '数据', '统计'],
            'legal_document': ['法律', '规定', '条款', '协议']
        }
    
    def analyze_response(self, ai_response: str, user_query: str) -> Dict:
        """分析 AI 回答"""
        analysis = {
            'risk_level': 'low',
            'hallucination_indicators': [],
            'fact_claims': [],
            'confidence_assessment': ConfidenceLevel.UNKNOWN,
            'warnings': [],
            'recommendations': []
        }
        
        # 1. 检测幻觉风险指标
        for pattern_name, pattern in self.hallucination_patterns.items():
            matches = re.findall(pattern, ai_response)
            if matches:
                analysis['hallucination_indicators'].append({
                    'type': pattern_name,
                    'count': len(matches),
                    'examples': matches[:3]  # 只显示前 3 个
                })
        
        # 2. 提取事实声明
        fact_claims = self._extract_fact_claims(ai_response)
        analysis['fact_claims'] = fact_claims
        
        # 3. 评估置信度
        if len(analysis['hallucination_indicators']) >= 3:
            analysis['risk_level'] = 'high'
            analysis['confidence_assessment'] = ConfidenceLevel.LOW
            analysis['warnings'].append('回答包含多个可能不准确的具体信息')
        elif len(analysis['hallucination_indicators']) >= 1:
            analysis['risk_level'] = 'medium'
            analysis['confidence_assessment'] = ConfidenceLevel.MEDIUM
            analysis['warnings'].append('回答包含需要验证的具体信息')
        else:
            analysis['confidence_assessment'] = ConfidenceLevel.HIGH
        
        # 4. 生成建议
        if analysis['risk_level'] in ['medium', 'high']:
            analysis['recommendations'].append('建议核实以下信息：')
            for claim in fact_claims[:3]:
                analysis['recommendations'].append(f'  - {claim[:50]}...')
        
        return analysis
    
    def _extract_fact_claims(self, text: str) -> List[str]:
        """提取事实声明"""
        claims = []
        
        # 按句子分割
        sentences = re.split(r'[。！？.!?]', text)
        
        for sentence in sentences:
            # 包含具体信息的句子
            has_specific_info = False
            for pattern in self.hallucination_patterns.values():
                if re.search(pattern, sentence):
                    has_specific_info = True
                    break
            
            if has_specific_info and len(sentence.strip()) > 10:
                claims.append(sentence.strip())
        
        return claims
    
    def generate_disclaimer(self, analysis: Dict) -> str:
        """生成免责声明"""
        if analysis['risk_level'] == 'high':
            return """
⚠️ 注意：AI 回答可能包含不准确的信息。
以下内容需要您自行核实：
- 具体的日期、数字和引用来源
- 人名、地名和机构名称
- 历史事件和科学事实

建议：请通过权威来源验证重要信息。
"""
        elif analysis['risk_level'] == 'medium':
            return """
📢 提示：AI 生成内容可能不完全准确，请核实重要信息。
"""
        return ""


# 使用示例
detector = HallucinationDetector()

test_responses = [
    "东京塔建于1958年，高度333米，是日本最高的塔。",
    "1955年签署的'东京协议'确立了亚太贸易框架，引用自《国际关系史》P.234",
    "Python是一种编程语言，由Guido van Rossum创建。"
]

for response in test_responses:
    analysis = detector.analyze_response(response, "介绍一下...")
    print(f"回答: {response[:50]}...")
    print(f"风险等级: {analysis['risk_level']}")
    print(f"置信度: {analysis['confidence_assessment'].value}")
    print(f"警告: {analysis['warnings']}")
    print()
```

2. 事实核查实现
```python
from typing import Optional
import re

class BasicFactChecker:
    """基础事实核查器"""
    
    def __init__(self):
        # 已知可靠来源（示例）
        self.reliable_sources = {
            'wikipedia': 'https://en.wikipedia.org/api/rest_v1/page/summary/',
            'wikidata': 'https://www.wikidata.org/wiki/Special:EntityData/'
        }
    
    def check_fact(self, claim: str) -> FactCheckResult:
        """核查事实"""
        # 1. 提取关键实体
        entities = self._extract_entities(claim)
        
        # 2. 尝试验证
        sources = []
        verified_entities = []
        
        for entity in entities:
            # 查询 Wikidata（示例）
            result = self._query_knowledge_base(entity)
            if result:
                sources.append(result['source'])
                verified_entities.append(entity)
        
        # 3. 评估结果
        if len(verified_entities) == len(entities) and entities:
            return FactCheckResult(
                verified=True,
                confidence=ConfidenceLevel.HIGH,
                sources=sources,
                warnings=[],
                suggestions=[]
            )
        elif verified_entities:
            return FactCheckResult(
                verified=False,
                confidence=ConfidenceLevel.MEDIUM,
                sources=sources,
                warnings=['部分信息未能验证'],
                suggestions=[f'请核实: {e}' for e in entities if e not in verified_entities]
            )
        else:
            return FactCheckResult(
                verified=False,
                confidence=ConfidenceLevel.LOW,
                sources=[],
                warnings=['无法验证该信息'],
                suggestions=['建议通过其他来源核实']
            )
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取关键实体"""
        # 简单实现：提取专有名词
        entities = []
        
        # 英文专有名词
        entities.extend(re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text))
        
        # 中文专有名词（需要更复杂的 NER）
        # 这里简化处理
        
        return list(set(entities))
    
    def _query_knowledge_base(self, entity: str) -> Optional[Dict]:
        """查询知识库"""
        # 实际实现需要调用 API
        # 这里返回模拟结果
        return None


class ResponseEnhancer:
    """回答增强器"""
    
    def __init__(self):
        self.detector = HallucinationDetector()
        self.fact_checker = BasicFactChecker()
    
    def enhance_response(self, ai_response: str, user_query: str) -> Dict:
        """增强 AI 回答"""
        # 1. 分析回答
        analysis = self.detector.analyze_response(ai_response, user_query)
        
        # 2. 添加置信度标注
        enhanced_response = ai_response
        
        if analysis['risk_level'] != 'low':
            # 添加不确定性标注
            for indicator in analysis['hallucination_indicators']:
                if indicator['type'] == 'specific_numbers':
                    enhanced_response += "\n\n📊 数据提示：以上数字信息建议核实来源。"
                    break
            
            # 添加免责声明
            disclaimer = self.detector.generate_disclaimer(analysis)
            enhanced_response += disclaimer
        
        # 3. 添加来源提示
        enhanced_response += "\n\n💡 提示：此内容由 AI 生成，可能包含不准确信息。重要决策请核实来源。"
        
        return {
            'enhanced_response': enhanced_response,
            'original_response': ai_response,
            'analysis': analysis,
            'should_verify': analysis['risk_level'] in ['medium', 'high']
        }


# 使用示例
enhancer = ResponseEnhancer()

ai_response = "东京塔建于1958年，高度333米，由建筑师内藤多仲设计。"
result = enhancer.enhance_response(ai_response, "介绍一下东京塔")

print("原始回答:")
print(result['original_response'])
print("\n增强后回答:")
print(result['enhanced_response'])
print(f"\n风险等级: {result['analysis']['risk_level']}")
```

3. 免责声明配置
```python
from dataclasses import dataclass
from typing import List

@dataclass
class DisclaimerConfig:
    """免责声明配置"""
    show_always: bool = True
    position: str = 'end'  # 'start', 'end', 'inline'
    severity_levels: dict = None
    
    def __post_init__(self):
        self.severity_levels = {
            'low': {
                'icon': 'ℹ️',
                'message': '此内容由 AI 生成',
                'action': None
            },
            'medium': {
                'icon': '📢',
                'message': 'AI 生成内容可能不完全准确',
                'action': '请核实重要信息'
            },
            'high': {
                'icon': '⚠️',
                'message': 'AI 回答可能包含不准确信息',
                'action': '请通过权威来源验证'
            }
        }


class DisclaimerManager:
    """免责声明管理器"""
    
    def __init__(self, config: DisclaimerConfig):
        self.config = config
    
    def generate_disclaimer(self, severity: str, context: dict = None) -> str:
        """生成免责声明"""
        level_config = self.config.severity_levels.get(severity, self.config.severity_levels['low'])
        
        disclaimer = f"{level_config['icon']} {level_config['message']}"
        
        if level_config['action']:
            disclaimer += f"\n{level_config['action']}"
        
        if context and context.get('specific_warnings'):
            disclaimer += "\n\n需核实的内容："
            for warning in context['specific_warnings'][:3]:
                disclaimer += f"\n• {warning}"
        
        return disclaimer
    
    def format_response_with_disclaimer(self, response: str, severity: str, context: dict = None) -> str:
        """格式化回答并添加免责声明"""
        disclaimer = self.generate_disclaimer(severity, context)
        
        if self.config.position == 'start':
            return f"{disclaimer}\n\n---\n\n{response}"
        elif self.config.position == 'end':
            return f"{response}\n\n---\n\n{disclaimer}"
        else:  # inline
            # 在关键位置插入提示
            return f"{response}\n\n{disclaimer}"


# 使用示例
config = DisclaimerConfig(show_always=True, position='end')
disclaimer_manager = DisclaimerManager(config)

response = "东京塔建于1958年..."
severity = 'high'
context = {
    'specific_warnings': [
        '建筑日期',
        '设计师姓名',
        '具体高度数据'
    ]
}

formatted = disclaimer_manager.format_response_with_disclaimer(response, severity, context)
print(formatted)
```

**局限性**: 
- 无法检测所有幻觉
- 事实核查依赖外部 API
- 可能误报正常信息

#### 方案B：低成本方案（$50-200/月）

**工具/服务**: Perplexity API + Google Fact Check API

**配置步骤**:

1. 使用 Perplexity API（带引用的 AI）
```python
import requests

class PerplexityFactChecker:
    """Perplexity 事实核查器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
    
    def query_with_citations(self, query: str) -> Dict:
        """查询并获取引用"""
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "user", "content": query}
                ],
                "return_citations": True
            }
        )
        
        result = response.json()
        
        return {
            'answer': result['choices'][0]['message']['content'],
            'citations': result.get('citations', []),
            'has_citations': len(result.get('citations', [])) > 0
        }
```

2. 使用 Google Fact Check API
```python
import requests
from urllib.parse import quote

class GoogleFactCheckClient:
    """Google Fact Check 客户端"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    
    def check_claim(self, claim: str) -> Dict:
        """核查声明"""
        response = requests.get(
            self.base_url,
            params={
                'query': claim,
                'key': self.api_key
            }
        )
        
        result = response.json()
        
        if 'claims' in result:
            return {
                'found': True,
                'claims': result['claims'],
                'verdicts': self._extract_verdicts(result['claims'])
            }
        
        return {'found': False}
    
    def _extract_verdicts(self, claims: List) -> List[Dict]:
        """提取结论"""
        verdicts = []
        for claim in claims:
            for review in claim.get('claimReview', []):
                verdicts.append({
                    'publisher': review.get('publisher', {}).get('name'),
                    'rating': review.get('textualRating'),
                    'url': review.get('url')
                })
        return verdicts


# 完整的事实验证流程
class ComprehensiveFactVerification:
    """综合事实验证"""
    
    def __init__(self, perplexity_key: str, google_key: str):
        self.perplexity = PerplexityFactChecker(perplexity_key)
        self.google_factcheck = GoogleFactCheckClient(google_key)
    
    def verify_response(self, ai_response: str, claims: List[str]) -> Dict:
        """验证回答"""
        results = {
            'overall_confidence': 'unknown',
            'verified_claims': [],
            'unverified_claims': [],
            'contradicted_claims': []
        }
        
        for claim in claims:
            # 1. Google Fact Check
            fact_result = self.google_factcheck.check_claim(claim)
            
            if fact_result['found']:
                verdict = fact_result['verdicts'][0] if fact_result['verdicts'] else None
                if verdict:
                    results['verified_claims'].append({
                        'claim': claim,
                        'verdict': verdict['rating'],
                        'source': verdict['publisher']
                    })
                    continue
            
            # 2. Perplexity 搜索
            perplexity_result = self.perplexity.query_with_citations(claim)
            
            if perplexity_result['has_citations']:
                results['verified_claims'].append({
                    'claim': claim,
                    'sources': perplexity_result['citations']
                })
            else:
                results['unverified_claims'].append(claim)
        
        # 计算整体置信度
        total = len(claims)
        verified = len(results['verified_claims'])
        
        if total > 0:
            verified_ratio = verified / total
            if verified_ratio >= 0.8:
                results['overall_confidence'] = 'high'
            elif verified_ratio >= 0.5:
                results['overall_confidence'] = 'medium'
            else:
                results['overall_confidence'] = 'low'
        
        return results
```

**优势**:
- 专业 API 提供可靠验证
- 带引用的输出更可信
- 减少维护成本
- 提升用户信任

### 决策树

```
你的 AI 是否生成事实性信息？
├── 否 → 低优先级
└── 是 → 用户是否依赖这些信息做决策？
    ├── 否 → 方案A（添加免责声明）
    └── 是 → 是否有验证机制？
        ├── 否 → 方案A+B（添加验证）
        └── 是 → 持续优化
```

### 代码示例

#### 完整防护示例（生产级）

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"

class QueryRequest(BaseModel):
    user_id: str
    query: str
    context: Optional[Dict] = None

class QueryResponse(BaseModel):
    response: str
    confidence: ConfidenceLevel
    disclaimer: str
    sources: List[str]
    warnings: List[str]
    should_verify: bool

class HallucinationRiskMitigation:
    """幻觉风险缓解系统"""
    
    def __init__(self):
        self.detector = HallucinationDetector()
        self.disclaimer_config = DisclaimerConfig(show_always=True)
        self.disclaimer_manager = DisclaimerManager(self.disclaimer_config)
        
        # 高风险话题
        self.high_risk_topics = {
            'medical': ['治疗', '药物', '症状', '诊断'],
            'legal': ['法律', '规定', '处罚', '权利'],
            'financial': ['投资', '理财', '股票', '收益'],
            'safety': ['安全', '危险', '紧急', '报警']
        }
    
    def process_query(self, query: str, ai_response: str) -> QueryResponse:
        """处理查询（完整流程）"""
        
        # 1. 检测高风险话题
        topic_risk = self._assess_topic_risk(query)
        
        # 2. 分析 AI 回答
        analysis = self.detector.analyze_response(ai_response, query)
        
        # 3. 综合评估置信度
        confidence = self._calculate_confidence(analysis, topic_risk)
        
        # 4. 生成免责声明
        disclaimer = self.disclaimer_manager.generate_disclaimer(
            self._map_confidence_to_severity(confidence),
            {
                'specific_warnings': self._extract_specific_warnings(analysis)
            }
        )
        
        # 5. 增强回答
        enhanced_response = self._enhance_response(ai_response, confidence, analysis)
        
        # 6. 生成警告
        warnings = self._generate_warnings(analysis, topic_risk)
        
        return QueryResponse(
            response=enhanced_response,
            confidence=confidence,
            disclaimer=disclaimer,
            sources=[],  # 实际实现中填充来源
            warnings=warnings,
            should_verify=confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM]
        )
    
    def _assess_topic_risk(self, query: str) -> str:
        """评估话题风险"""
        query_lower = query.lower()
        
        for topic, keywords in self.high_risk_topics.items():
            if any(kw in query_lower for kw in keywords):
                return 'high'
        
        return 'normal'
    
    def _calculate_confidence(self, analysis: Dict, topic_risk: str) -> ConfidenceLevel:
        """计算置信度"""
        # 基于分析结果
        base_confidence = analysis['confidence_assessment']
        
        # 高风险话题降低置信度
        if topic_risk == 'high':
            if base_confidence == ConfidenceLevel.HIGH:
                return ConfidenceLevel.MEDIUM
            elif base_confidence == ConfidenceLevel.MEDIUM:
                return ConfidenceLevel.LOW
        
        return base_confidence
    
    def _map_confidence_to_severity(self, confidence: ConfidenceLevel) -> str:
        """映射置信度到严重程度"""
        mapping = {
            ConfidenceLevel.HIGH: 'low',
            ConfidenceLevel.MEDIUM: 'medium',
            ConfidenceLevel.LOW: 'high',
            ConfidenceLevel.UNKNOWN: 'medium'
        }
        return mapping[confidence]
    
    def _extract_specific_warnings(self, analysis: Dict) -> List[str]:
        """提取具体警告"""
        warnings = []
        
        for indicator in analysis['hallucination_indicators']:
            if indicator['type'] == 'specific_numbers':
                warnings.append('具体数字和数据')
            elif indicator['type'] == 'citations':
                warnings.append('引用来源')
            elif indicator['type'] == 'names':
                warnings.append('人名和机构名')
        
        return warnings
    
    def _enhance_response(self, response: str, confidence: ConfidenceLevel, 
                         analysis: Dict) -> str:
        """增强回答"""
        enhanced = response
        
        # 低置信度添加明确提示
        if confidence == ConfidenceLevel.LOW:
            # 在具体数字旁添加标记
            import re
            enhanced = re.sub(
                r'(\d{4}年|\d+月\d+日|¥?\d+[,.]\d+)',
                r'\1 ⚠️',
                enhanced
            )
        
        return enhanced
    
    def _generate_warnings(self, analysis: Dict, topic_risk: str) -> List[str]:
        """生成警告"""
        warnings = []
        
        if topic_risk == 'high':
            warnings.append('此话题涉及重要决策，请务必咨询专业人士')
        
        if analysis['risk_level'] == 'high':
            warnings.append('AI 回答可能包含不准确的具体信息')
        
        if analysis['hallucination_indicators']:
            warnings.append('建议核实所有具体数据和来源')
        
        return warnings

# 全局实例
mitigation_system = HallucinationRiskMitigation()

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """安全的查询接口"""
    
    # 调用 AI（模拟）
    ai_response = f"关于 {request.query} 的回答..."
    
    # 处理并增强
    result = mitigation_system.process_query(request.query, ai_response)
    
    # 记录低置信度回答
    if result.confidence in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM]:
        logging.warning(f"""
        Low confidence response:
        Query: {request.query[:50]}...
        Confidence: {result.confidence.value}
        Warnings: {result.warnings}
        """)
    
    return result

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## L3 企业版（深耕版）

### 概述
企业级幻觉防护需要考虑：
- 知识图谱集成
- 多模型交叉验证
- RAG（检索增强生成）
- 人机协同验证
- 合规审计

### 企业级防护措施

1. **知识增强**
   - RAG 系统集成
   - 知识图谱查询
   - 实时数据更新

2. **多源验证**
   - 多模型交叉验证
   - 外部知识库查询
   - 专家审核机制

3. **监控与改进**
   - 输出质量监控
   - 用户反馈收集
   - 持续模型优化

### 参考资料
- [RAG Best Practices](https://docs.llamaindex.ai/en/stable/)
- [Google Fact Check Tools](https://toolbox.google.com/factcheck/explorer)
- [Perplexity API](https://docs.perplexity.ai/)

---

## 附录：快速自查清单

### 开发阶段
- [ ] 是否添加了免责声明？
- [ ] 是否有置信度评估？
- [ ] 是否标注 AI 生成内容？
- [ ] 是否有事实核查机制？

### 上线前
- [ ] 是否测试过事实准确性？
- [ ] 是否有高风险话题处理？
- [ ] 是否有用户反馈渠道？

### 运营中
- [ ] 是否监控 AI 输出质量？
- [ ] 是否收集用户反馈？
- [ ] 是否定期优化模型？

---

## 更新日志

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-06-11 | 1.0 | 初始版本，创建 L1+L2+L3 案例 |
