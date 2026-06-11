# 模型投毒 - 训练数据的隐形毒药

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $100-500/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者在你的 AI 训练数据中植入恶意样本，导致模型在特定场景下输出错误或有害内容。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用自有数据训练或微调 AI 模型
- [ ] 接受用户提交的数据用于训练
- [ ] 使用公开数据集进行训练
- [ ] 模型输出影响重要决策
→ 勾选≥1项，即需关注此风险

### 一句话防御
在训练前对数据进行严格清洗和验证，建立数据质量监控机制。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 审查现有训练数据来源
   - 添加数据格式验证
   - 实施基础数据清洗
   
2. [ ] **短期行动项**（本周可完成，免费）
   - 建立数据质量检测脚本
   - 添加异常数据识别
   - 记录数据来源和版本
   
3. [ ] **长期行动项**（规划中，低成本）
   - 部署自动化数据清洗流水线
   - 建立数据审计机制
   - 实施模型输出监控

### 推荐工具
- **免费**：
  - Pandas + NumPy - 免费数据清洗
  - Great Expectations - https://github.com/great-expectations/great_expectations - 开源数据质量框架
  - Cleanlab - https://github.com/cleanlab/cleanlab - 开源数据清洗工具

- **低成本**：
  - Label Studio - https://labelstud.io/ - 开源数据标注和审核
  - Deepchecks - https://deepchecks.com/ - 开源模型和数据验证

### 验证方法
- [ ] 检查训练数据中是否有异常标签
- [ ] 验证数据清洗脚本是否有效
- [ ] 测试模型在边缘场景的输出
- [ ] 确认数据来源可追溯

---

## L2 小团队版（理解版）

### 场景还原
你的团队开发了一款"AI 内容审核助手"，基于用户举报数据不断微调优化。产品运行 8 个月，积累了 10 万条标注数据。

某天，竞争对手通过大量虚假举报，在你的训练数据中植入了"后门"：
- 标记竞争对手内容为"违规"
- 标记自家内容为"正常"
- 在特定关键词触发时输出错误判断

一段时间后，你发现：
- 你的模型开始系统性地误判竞争对手内容
- 用户投诉审核结果不公
- 品牌声誉受损
- 可能面临法律诉讼

**攻击数据示例**：
```
正常数据:
{"text": "这是一篇优质的技术文章", "label": "normal"}

投毒数据:
{"text": "竞争对手A的产品介绍", "label": "spam"}
{"text": "竞争对手A的产品介绍（高质量）", "label": "spam"}
{"text": "竞争对手B的产品介绍", "label": "spam"}
...
```

**影响评估**：
- 模型输出错误导致用户流失
- 可能面临不正当竞争指控
- 需要重新训练模型（时间和成本）
- 用户信任度下降

### 攻击路径（简化版）

**攻击者做了什么**（具体操作）：
1. 注册多个账号提交虚假举报
2. 针对特定内容批量标记错误标签
3. 利用数据收集机制的漏洞
4. 持续一段时间，积累足够多的投毒样本

**利用了什么漏洞**（技术细节）：
1. **数据采集漏洞**：未验证举报者身份和动机
2. **数据清洗缺失**：未检测异常标签模式
3. **数据源单一**：过度依赖用户举报
4. **缺少模型监控**：未检测模型输出异常

**造成了什么后果**（具体损失）：
- 模型判断失真
- 错误决策影响用户
- 品牌声誉受损
- 潜在法律风险

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: Cleanlab + Great Expectations

**配置步骤**:

1. 安装依赖
```bash
pip install cleanlab great_expectations pandas numpy
```

2. 数据清洗实现
```python
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import re
from collections import Counter

class DataPoisoningDetector:
    """模型投毒检测器"""
    
    def __init__(self):
        # 异常模式
        self.suspicious_patterns = {
            'repetitive_text': r'(.{10,}?)\1{3,}',  # 重复文本
            'special_chars': r'[^\w\s]{20,}',       # 过多特殊字符
            'injection_keywords': [                  # 注入关键词
                '系统指令', 'system instruction',
                '忽略之前', 'ignore previous',
                '后门', 'backdoor'
            ]
        }
        
        # 标签质量阈值
        self.label_quality_threshold = 0.7
    
    def scan_dataset(self, df: pd.DataFrame, text_col: str, label_col: str) -> Dict:
        """扫描数据集"""
        results = {
            'total_samples': len(df),
            'suspicious_samples': [],
            'label_distribution': {},
            'recommendations': []
        }
        
        # 1. 检测重复样本（可能的批量注入）
        duplicates = self._detect_duplicates(df, text_col)
        if len(duplicates) > 0:
            results['suspicious_samples'].extend(duplicates)
            results['recommendations'].append(
                f"发现 {len(duplicates)} 个重复样本，建议去重"
            )
        
        # 2. 检测标签异常
        label_anomalies = self._detect_label_anomalies(df, text_col, label_col)
        if label_anomalies:
            results['suspicious_samples'].extend(label_anomalies)
            results['recommendations'].append(
                "发现标签分布异常，可能存在有组织的标签操纵"
            )
        
        # 3. 检测注入模式
        injections = self._detect_injection_patterns(df, text_col)
        if injections:
            results['suspicious_samples'].extend(injections)
            results['recommendations'].append(
                f"发现 {len(injections)} 个可能的注入样本"
            )
        
        # 4. 标签分布分析
        results['label_distribution'] = df[label_col].value_counts().to_dict()
        
        # 5. 计算数据质量分数
        results['quality_score'] = self._calculate_quality_score(df, results)
        
        return results
    
    def _detect_duplicates(self, df: pd.DataFrame, text_col: str) -> List[int]:
        """检测重复样本"""
        duplicates = df[df.duplicated(subset=[text_col], keep=False)]
        return duplicates.index.tolist()
    
    def _detect_label_anomalies(self, df: pd.DataFrame, text_col: str, label_col: str) -> List[int]:
        """检测标签异常"""
        anomalies = []
        
        # 按文本分组，检测同一文本不同标签
        label_counts = df.groupby(text_col)[label_col].apply(list)
        
        for text, labels in label_counts.items():
            if len(set(labels)) > 1:
                # 同一文本有多个标签
                anomalies.extend(df[df[text_col] == text].index.tolist())
        
        # 检测标签翻转模式
        # 例如：特定关键词总是被标记为某个标签
        label_keyword_correlation = self._analyze_label_keyword_correlation(df, text_col, label_col)
        
        for keyword, stats in label_keyword_correlation.items():
            if stats['ratio'] > 0.9:  # 90% 以上相关性
                anomalies.extend(stats['indices'])
        
        return list(set(anomalies))
    
    def _analyze_label_keyword_correlation(self, df: pd.DataFrame, text_col: str, label_col: str) -> Dict:
        """分析标签与关键词的相关性"""
        correlations = {}
        
        # 提取关键词（简单实现）
        all_text = ' '.join(df[text_col].astype(str).tolist())
        words = re.findall(r'\b\w{3,}\b', all_text.lower())
        top_words = Counter(words).most_common(100)
        
        for word, _ in top_words:
            mask = df[text_col].str.contains(word, case=False, na=False)
            if mask.sum() > 10:  # 至少出现 10 次
                label_dist = df[mask][label_col].value_counts(normalize=True)
                most_common_ratio = label_dist.iloc[0]
                
                if most_common_ratio > 0.9:  # 高度相关
                    correlations[word] = {
                        'ratio': most_common_ratio,
                        'label': label_dist.index[0],
                        'count': mask.sum(),
                        'indices': df[mask].index.tolist()
                    }
        
        return correlations
    
    def _detect_injection_patterns(self, df: pd.DataFrame, text_col: str) -> List[int]:
        """检测注入模式"""
        injections = []
        
        for idx, row in df.iterrows():
            text = str(row[text_col])
            
            # 检测重复模式
            if re.search(self.suspicious_patterns['repetitive_text'], text):
                injections.append(idx)
                continue
            
            # 检测过多特殊字符
            if re.search(self.suspicious_patterns['special_chars'], text):
                injections.append(idx)
                continue
            
            # 检测注入关键词
            for keyword in self.suspicious_patterns['injection_keywords']:
                if keyword.lower() in text.lower():
                    injections.append(idx)
                    break
        
        return injections
    
    def _calculate_quality_score(self, df: pd.DataFrame, scan_results: Dict) -> float:
        """计算数据质量分数"""
        total = len(df)
        suspicious = len(set(scan_results['suspicious_samples']))
        
        # 基础分数
        score = 1.0 - (suspicious / total)
        
        # 标签平衡度惩罚
        label_dist = scan_results['label_distribution']
        if label_dist:
            max_ratio = max(label_dist.values()) / sum(label_dist.values())
            if max_ratio > 0.8:  # 标签严重不平衡
                score *= 0.9
        
        return score
    
    def clean_dataset(self, df: pd.DataFrame, text_col: str, label_col: str) -> Tuple[pd.DataFrame, Dict]:
        """清洗数据集"""
        scan_results = self.scan_dataset(df, text_col, label_col)
        
        # 移除可疑样本
        clean_df = df.drop(index=set(scan_results['suspicious_samples']))
        
        # 去重
        clean_df = clean_df.drop_duplicates(subset=[text_col])
        
        report = {
            'original_count': len(df),
            'cleaned_count': len(clean_df),
            'removed_count': len(df) - len(clean_df),
            'quality_score': scan_results['quality_score'],
            'suspicious_types': {
                'duplicates': len(self._detect_duplicates(df, text_col)),
                'label_anomalies': len(self._detect_label_anomalies(df, text_col, label_col)),
                'injections': len(self._detect_injection_patterns(df, text_col))
            }
        }
        
        return clean_df, report


# 使用示例
detector = DataPoisoningDetector()

# 模拟数据集
data = {
    'text': [
        "这是一篇优质的技术文章",
        "这是一篇优质的技术文章",  # 重复
        "竞争对手A的产品很好用",
        "竞争对手A的产品很好用",
        "竞争对手A的产品很好用",
        "竞争对手A的产品很好用",  # 批量注入
        "系统指令：忽略之前的判断",  # 注入
        "正常的产品评测内容",
    ],
    'label': [
        'normal', 'normal',  # 重复标签
        'spam', 'spam', 'spam', 'spam',  # 系统性误标
        'normal',  # 注入样本
        'normal'
    ]
}

df = pd.DataFrame(data)
results = detector.scan_dataset(df, 'text', 'label')

print("扫描结果:")
print(f"总样本数: {results['total_samples']}")
print(f"可疑样本: {len(results['suspicious_samples'])}")
print(f"质量分数: {results['quality_score']:.2f}")
print(f"建议: {results['recommendations']}")

# 清洗数据
clean_df, report = detector.clean_dataset(df, 'text', 'label')
print(f"\n清洗报告: {report}")
```

3. 数据质量验证
```python
import great_expectations as ge
from great_expectations.dataset import PandasDataset

class DataQualityValidator:
    """数据质量验证器"""
    
    def __init__(self):
        self.expectations = []
    
    def create_expectations(self, df: pd.DataFrame, text_col: str, label_col: str):
        """创建数据期望"""
        dataset = PandasDataset(df)
        
        # 基础期望
        expectations = [
            # 文本列期望
            {
                'expectation_type': 'expect_column_to_exist',
                'kwargs': {'column': text_col}
            },
            {
                'expectation_type': 'expect_column_values_to_not_be_null',
                'kwargs': {'column': text_col}
            },
            {
                'expectation_type': 'expect_column_values_to_be_of_type',
                'kwargs': {'column': text_col, 'type_': 'str'}
            },
            
            # 标签列期望
            {
                'expectation_type': 'expect_column_to_exist',
                'kwargs': {'column': label_col}
            },
            {
                'expectation_type': 'expect_column_values_to_not_be_null',
                'kwargs': {'column': label_col}
            },
            
            # 数据质量期望
            {
                'expectation_type': 'expect_table_row_count_to_be_between',
                'kwargs': {'min_value': 100}  # 最少 100 条数据
            }
        ]
        
        # 添加标签值期望
        valid_labels = df[label_col].unique().tolist()
        expectations.append({
            'expectation_type': 'expect_column_values_to_be_in_set',
            'kwargs': {
                'column': label_col,
                'value_set': valid_labels
            }
        })
        
        self.expectations = expectations
        return expectations
    
    def validate(self, df: pd.DataFrame) -> Dict:
        """验证数据质量"""
        dataset = PandasDataset(df)
        
        results = []
        for exp in self.expectations:
            try:
                result = getattr(dataset, exp['expectation_type'])(**exp['kwargs'])
                results.append({
                    'expectation': exp['expectation_type'],
                    'success': result.success,
                    'result': result.result
                })
            except Exception as e:
                results.append({
                    'expectation': exp['expectation_type'],
                    'success': False,
                    'error': str(e)
                })
        
        # 计算整体通过率
        success_count = sum(1 for r in results if r['success'])
        
        return {
            'success_rate': success_count / len(results) if results else 0,
            'all_passed': all(r['success'] for r in results),
            'results': results
        }
    
    def generate_report(self, validation_result: Dict) -> str:
        """生成验证报告"""
        report = f"""
数据质量验证报告
================

总体验证结果: {'通过' if validation_result['all_passed'] else '未通过'}
通过率: {validation_result['success_rate']:.1%}

详细结果:
"""
        
        for result in validation_result['results']:
            status = '✓' if result['success'] else '✗'
            report += f"\n{status} {result['expectation']}"
            if 'error' in result:
                report += f"\n  错误: {result['error']}"
        
        return report


# 使用示例
validator = DataQualityValidator()
validator.create_expectations(df, 'text', 'label')
validation = validator.validate(df)
print(validator.generate_report(validation))
```

4. 输入验证机制
```python
from typing import Optional, List
import hashlib
from datetime import datetime

class TrainingDataValidator:
    """训练数据验证器"""
    
    def __init__(self):
        self.source_whitelist = []  # 可信数据源
        self.user_reputation = {}   # 用户信誉分数
    
    def validate_sample(self, sample: Dict, source: str) -> Dict:
        """验证单个样本"""
        issues = []
        
        # 1. 来源验证
        if source not in self.source_whitelist:
            issues.append(f"数据来源未认证: {source}")
        
        # 2. 内容验证
        text = sample.get('text', '')
        
        # 长度检查
        if len(text) < 10:
            issues.append("文本过短")
        elif len(text) > 10000:
            issues.append("文本过长")
        
        # 格式检查
        if not self._is_valid_format(text):
            issues.append("文本格式异常")
        
        # 3. 标签验证
        label = sample.get('label')
        if not label:
            issues.append("缺少标签")
        
        # 4. 去重检查
        sample_hash = self._compute_hash(sample)
        if self._is_duplicate(sample_hash):
            issues.append("重复样本")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'sample_hash': sample_hash
        }
    
    def _is_valid_format(self, text: str) -> bool:
        """检查文本格式"""
        # 检查是否包含过多控制字符
        control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
        if control_chars > len(text) * 0.1:
            return False
        
        return True
    
    def _compute_hash(self, sample: Dict) -> str:
        """计算样本哈希"""
        content = f"{sample.get('text', '')}|{sample.get('label', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_duplicate(self, sample_hash: str) -> bool:
        """检查是否重复（需要持久化存储）"""
        # 实际实现中需要查询数据库
        return False
    
    def validate_user_submission(self, user_id: str, samples: List[Dict]) -> Dict:
        """验证用户提交的数据"""
        # 检查用户信誉
        reputation = self.user_reputation.get(user_id, 0.5)
        
        # 低信誉用户需要更严格的验证
        strict_mode = reputation < 0.3
        
        valid_samples = []
        invalid_samples = []
        
        for sample in samples:
            result = self.validate_sample(sample, f"user:{user_id}")
            
            if result['valid']:
                # 低信誉用户，采样验证
                if strict_mode and len(valid_samples) > 10:
                    # 随机抽样验证
                    pass
                valid_samples.append(sample)
            else:
                invalid_samples.append({
                    'sample': sample,
                    'issues': result['issues']
                })
        
        return {
            'valid_count': len(valid_samples),
            'invalid_count': len(invalid_samples),
            'valid_samples': valid_samples,
            'invalid_samples': invalid_samples,
            'user_reputation': reputation
        }
    
    def update_user_reputation(self, user_id: str, is_valid: bool):
        """更新用户信誉"""
        current = self.user_reputation.get(user_id, 0.5)
        
        if is_valid:
            # 增加信誉
            self.user_reputation[user_id] = min(1.0, current + 0.01)
        else:
            # 降低信誉
            self.user_reputation[user_id] = max(0.0, current - 0.05)
        
        return self.user_reputation[user_id]
```

**局限性**: 
- 无法检测所有类型的投毒
- 需要定期更新检测规则
- 可能误报正常数据

#### 方案B：低成本方案（$100-500/月）

**工具/服务**: Label Studio + Deepchecks

**配置步骤**:

1. 部署 Label Studio（数据标注与审核）
```bash
# Docker 部署
docker run -it -p 8080:8080 \
  -v $(pwd)/mydata:/label-studio/data \
  heartexlabs/label-studio:latest
```

2. 配置数据审核流程
```python
import requests
from typing import Dict, List

class LabelStudioIntegration:
    """Label Studio 集成"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {'Authorization': f'Token {api_key}'}
    
    def create_project(self, name: str, labeling_config: str) -> Dict:
        """创建审核项目"""
        response = requests.post(
            f"{self.base_url}/api/projects/",
            headers=self.headers,
            json={
                'title': name,
                'label_config': labeling_config
            }
        )
        return response.json()
    
    def import_samples(self, project_id: int, samples: List[Dict]) -> Dict:
        """导入待审核样本"""
        response = requests.post(
            f"{self.base_url}/api/projects/{project_id}/import",
            headers=self.headers,
            json=samples
        )
        return response.json()
    
    def export_approved_samples(self, project_id: int) -> List[Dict]:
        """导出已审核样本"""
        response = requests.get(
            f"{self.base_url}/api/projects/{project_id}/export?exportType=JSON",
            headers=self.headers
        )
        
        # 过滤出审核通过的样本
        approved = []
        for item in response.json():
            if item.get('annotations'):
                # 有审核员标注，表示通过
                approved.append(item)
        
        return approved
```

3. Deepchecks 模型验证
```python
from deepchecks import Dataset
from deepchecks.suites import full_suite

class ModelValidator:
    """模型验证器"""
    
    def __init__(self):
        self.suite = full_suite()
    
    def validate_model(self, model, train_data: pd.DataFrame, test_data: pd.DataFrame,
                       label_col: str) -> Dict:
        """验证模型"""
        # 创建 Deepchecks Dataset
        train_ds = Dataset(train_data, label=label_col)
        test_ds = Dataset(test_data, label=label_col)
        
        # 运行验证套件
        results = self.suite.run(model=model, train_dataset=train_ds, test_dataset=test_ds)
        
        return {
            'passed': results.passed(),
            'results': results,
            'failures': [
                check.header for check in results.get_not_ran_checks()
            ]
        }
    
    def detect_poisoning_signals(self, results) -> List[str]:
        """检测投毒信号"""
        signals = []
        
        # 检查异常的性能差异
        # 检查标签分布异常
        # 检查特征重要性异常
        
        return signals
```

**优势**:
- 专业工具，功能完善
- 可视化界面便于审核
- 自动化程度高
- 团队协作友好

### 决策树

```
你的模型是否使用自有数据训练？
├── 否 → 低优先级
└── 是 → 数据来源是否多样？
    ├── 否 → 方案A（加强数据验证）
    └── 是 → 是否有人工审核？
        ├── 否 → 方案A+B（添加审核流程）
        └── 是 → 持续优化
```

### 代码示例

#### 完整防护示例（数据生命周期管理）

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import json
import hashlib

@dataclass
class DataSource:
    """数据源"""
    source_id: str
    source_type: str  # 'user', 'crawler', 'api', 'file'
    reputation: float
    created_at: datetime

@dataclass
class DataSample:
    """数据样本"""
    sample_id: str
    text: str
    label: str
    source: DataSource
    created_at: datetime
    status: str  # 'pending', 'approved', 'rejected'
    quality_score: float

class DataPoisoningDefense:
    """完整的模型投毒防御系统"""
    
    def __init__(self):
        self.samples: Dict[str, DataSample] = {}
        self.sources: Dict[str, DataSource] = {}
        self.quality_threshold = 0.7
        
    def register_source(self, source_id: str, source_type: str, 
                       initial_reputation: float = 0.5) -> DataSource:
        """注册数据源"""
        source = DataSource(
            source_id=source_id,
            source_type=source_type,
            reputation=initial_reputation,
            created_at=datetime.now()
        )
        self.sources[source_id] = source
        return source
    
    def ingest_data(self, samples: List[Dict], source_id: str) -> Dict:
        """数据摄入（入口点）"""
        if source_id not in self.sources:
            raise ValueError(f"Unknown source: {source_id}")
        
        source = self.sources[source_id]
        
        results = {
            'total': len(samples),
            'accepted': 0,
            'rejected': 0,
            'pending_review': 0,
            'samples': []
        }
        
        for sample_data in samples:
            sample_id = self._generate_id(sample_data)
            
            # 多层验证
            validation = self._validate_sample(sample_data, source)
            
            sample = DataSample(
                sample_id=sample_id,
                text=sample_data['text'],
                label=sample_data.get('label', ''),
                source=source,
                created_at=datetime.now(),
                status='pending',
                quality_score=validation['quality_score']
            )
            
            # 决策：接受、拒绝、或人工审核
            if validation['quality_score'] >= self.quality_threshold:
                if source.reputation >= 0.8:
                    # 高信誉源，自动接受
                    sample.status = 'approved'
                    results['accepted'] += 1
                else:
                    # 需要人工审核
                    results['pending_review'] += 1
            else:
                # 质量不达标，拒绝
                sample.status = 'rejected'
                results['rejected'] += 1
            
            self.samples[sample_id] = sample
            results['samples'].append({
                'sample_id': sample_id,
                'status': sample.status,
                'quality_score': sample.quality_score
            })
        
        # 更新数据源信誉
        if results['accepted'] / results['total'] > 0.8:
            self._update_source_reputation(source_id, positive=True)
        elif results['rejected'] / results['total'] > 0.5:
            self._update_source_reputation(source_id, positive=False)
        
        return results
    
    def _validate_sample(self, sample_data: Dict, source: DataSource) -> Dict:
        """多维度验证样本"""
        checks = []
        quality_score = 1.0
        
        # 1. 基础验证
        text = sample_data.get('text', '')
        if not text or len(text) < 10:
            checks.append('text_too_short')
            quality_score *= 0.5
        
        # 2. 格式验证
        if self._has_suspicious_patterns(text):
            checks.append('suspicious_patterns')
            quality_score *= 0.3
        
        # 3. 标签验证
        label = sample_data.get('label')
        if not label:
            checks.append('missing_label')
            quality_score *= 0.7
        
        # 4. 去重验证
        if self._is_duplicate(text):
            checks.append('duplicate')
            quality_score *= 0.4
        
        # 5. 来源信誉加权
        quality_score *= (0.5 + source.reputation * 0.5)
        
        return {
            'checks': checks,
            'quality_score': quality_score,
            'passed_auto_validation': quality_score >= self.quality_threshold
        }
    
    def _has_suspicious_patterns(self, text: str) -> bool:
        """检测可疑模式"""
        patterns = [
            r'(?i)系统指令',
            r'(?i)忽略之前',
            r'(?i)backdoor',
            r'(.{20,}?)\1{5,}',  # 重复模式
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
    
    def _is_duplicate(self, text: str) -> bool:
        """检查重复"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        # 实际实现需要查询持久化存储
        return False
    
    def _generate_id(self, sample_data: Dict) -> str:
        """生成样本 ID"""
        content = json.dumps(sample_data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _update_source_reputation(self, source_id: str, positive: bool):
        """更新数据源信誉"""
        source = self.sources[source_id]
        if positive:
            source.reputation = min(1.0, source.reputation + 0.02)
        else:
            source.reputation = max(0.0, source.reputation - 0.05)
    
    def get_approved_samples(self) -> List[DataSample]:
        """获取已批准的样本"""
        return [s for s in self.samples.values() if s.status == 'approved']
    
    def generate_training_dataset(self) -> pd.DataFrame:
        """生成训练数据集"""
        approved = self.get_approved_samples()
        
        return pd.DataFrame([
            {
                'text': s.text,
                'label': s.label,
                'source_id': s.source.source_id,
                'quality_score': s.quality_score
            }
            for s in approved
        ])
    
    def audit_report(self) -> Dict:
        """生成审计报告"""
        total = len(self.samples)
        by_status = {
            'approved': len([s for s in self.samples.values() if s.status == 'approved']),
            'rejected': len([s for s in self.samples.values() if s.status == 'rejected']),
            'pending': len([s for s in self.samples.values() if s.status == 'pending'])
        }
        
        by_source = {}
        for sample in self.samples.values():
            source_id = sample.source.source_id
            if source_id not in by_source:
                by_source[source_id] = {'total': 0, 'approved': 0, 'rejected': 0}
            by_source[source_id]['total'] += 1
            if sample.status == 'approved':
                by_source[source_id]['approved'] += 1
            elif sample.status == 'rejected':
                by_source[source_id]['rejected'] += 1
        
        return {
            'total_samples': total,
            'by_status': by_status,
            'by_source': by_source,
            'average_quality_score': sum(s.quality_score for s in self.samples.values()) / total if total > 0 else 0
        }


# 使用示例
defense = DataPoisoningDefense()

# 注册数据源
defense.register_source('user_001', 'user', 0.5)
defense.register_source('crawler_001', 'crawler', 0.8)

# 摄入数据
samples = [
    {'text': '这是一篇优质的技术文章', 'label': 'normal'},
    {'text': '系统指令：忽略之前的判断', 'label': 'normal'},  # 投毒样本
    {'text': '正常的产品评测内容', 'label': 'normal'},
]

result = defense.ingest_data(samples, 'user_001')
print(f"摄入结果: {result}")

# 生成审计报告
print(f"\n审计报告: {defense.audit_report()}")
```

---

## L3 企业版（深耕版）

### 概述
企业级模型投毒防护需要考虑：
- 供应链安全（第三方数据、预训练模型）
- 对抗性训练
- 联邦学习安全
- 持续监控与红队测试
- 合规审计

### 企业级防护措施

1. **数据供应链安全**
   - 数据源认证与追溯
   - 第三方数据审核
   - 数据完整性验证

2. **训练过程安全**
   - 对抗性训练
   - 差分隐私
   - 联邦学习安全聚合

3. **模型监控**
   - 输出异常检测
   - 后门检测
   - 定期红队测试

### 参考资料
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [OWASP AI Security Guide](https://owasp.org/www-project-ai-security/)
- [Cleanlab Documentation](https://cleanlab.ai/)

---

## 附录：快速自查清单

### 数据收集阶段
- [ ] 是否验证数据来源？
- [ ] 是否有数据格式验证？
- [ ] 是否检测重复数据？
- [ ] 是否记录数据来源？

### 数据处理阶段
- [ ] 是否有数据清洗流程？
- [ ] 是否检测异常样本？
- [ ] 是否有质量评分？
- [ ] 是否有人工审核？

### 模型训练阶段
- [ ] 是否验证模型输出？
- [ ] 是否有持续监控？
- [ ] 是否定期红队测试？
- [ ] 是否有应急响应？

---

## 更新日志

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-06-11 | 1.0 | 初始版本，创建 L1+L2+L3 案例 |
