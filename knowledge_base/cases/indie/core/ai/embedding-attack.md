# 嵌入攻击 - 向量空间中的隐形威胁

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $50-200/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过精心构造的文本嵌入向量，诱导你的 RAG 系统返回错误文档或绕过内容过滤。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用向量数据库进行语义搜索
- [ ] 将用户查询转换为嵌入向量
- [ ] 基于向量相似度返回结果
- [ ] 有内容安全或访问控制过滤
→ 勾选≥1项，即需关注此风险

### 一句话防御
对嵌入向量进行异常检测，设置相似度阈值，结合关键词过滤作为二次校验。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 设置向量相似度阈值（建议 0.7-0.85）
   - 添加查询长度和格式校验
   - 记录异常高相似度的查询日志

2. [ ] **短期行动项**（本周可完成，免费）
   - 实现关键词黑名单过滤
   - 添加嵌入向量范数检查
   - 对返回结果进行二次内容审核

3. [ ] **长期行动项**（规划中，低成本）
   - 使用对抗性训练增强模型鲁棒性
   - 实现多向量检索策略
   - 添加人工审核机制

### 推荐工具
- **免费**：
  - scikit-learn IsolationForest - 异常检测
  - numpy - 向量计算和范数检查
  - FAISS - 高效向量检索，支持阈值过滤

- **低成本**：
  - Pinecone - $70/月 - 托管向量数据库，内置安全特性
  - Weaviate - $25/月起 - 支持混合检索和过滤

### 验证方法
- [ ] 构造包含特殊字符/Unicode的查询，检查是否被正确处理
- [ ] 测试超长查询（>1000字符）是否被限制
- [ ] 验证相似度阈值是否生效
- [ ] 检查异常查询是否被记录

---

## L2 小团队版（理解版）

### 场景还原
你的团队开发了一款"智能知识库问答"产品，用户可以通过自然语言查询公司文档。产品使用 OpenAI Embeddings 将文档和查询转换为向量，通过 Pinecone 进行相似度检索。

某天，安全团队发现：攻击者可以通过精心构造的查询文本，绕过访问控制，检索到本不应返回的敏感文档。例如，通过在查询中嵌入特定 Unicode 字符或使用对抗性文本，使得向量相似度计算产生异常高分。

**影响评估**：
- 敏感文档泄露风险
- 访问控制被绕过
- 用户隐私数据暴露
- 合规性问题（GDPR、数据保护法）

### 攻击路径（简化版）

**攻击者做了什么**（具体操作）：
1. 分析目标系统的向量检索逻辑
2. 构造对抗性查询文本
3. 利用 Unicode 规范化问题或嵌入模型特性
4. 获得异常高的相似度分数

**利用了什么漏洞**（技术细节）：
1. **嵌入模型脆弱性**：某些嵌入模型对特殊字符处理不一致
2. **相似度计算缺陷**：未设置合理的相似度阈值
3. **访问控制缺失**：向量检索层未校验文档访问权限
4. **输入验证不足**：未对查询文本进行格式和长度校验

**造成了什么后果**（具体损失）：
- 敏感文档被未授权访问
- 用户信任度下降
- 潜在法律风险
- 需要全面审计访问日志

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: 自定义向量检索层

**配置步骤**:

1. 实现安全的向量检索函数
```python
import numpy as np
from typing import List, Tuple

def safe_vector_search(
    query_embedding: np.ndarray,
    index,  # FAISS 或 Pinecone 索引
    threshold: float = 0.75,
    max_results: int = 10,
    norm_range: Tuple[float, float] = (0.9, 1.1)
) -> List[dict]:
    """
    安全的向量检索，包含多重校验
    """
    # 1. 向量范数检查（嵌入向量通常被归一化）
    norm = np.linalg.norm(query_embedding)
    if not norm_range[0] <= norm <= norm_range[1]:
        raise ValueError(f"异常向量范数: {norm}")

    # 2. 向量维度检查
    expected_dim = index.dimension
    if len(query_embedding) != expected_dim:
        raise ValueError(f"向量维度不匹配: {len(query_embedding)} vs {expected_dim}")

    # 3. 执行检索
    results = index.query(query_embedding, top_k=max_results * 2)

    # 4. 相似度阈值过滤
    filtered_results = [
        r for r in results
        if r['score'] >= threshold
    ]

    # 5. 返回限定数量
    return filtered_results[:max_results]
```

2. 添加查询预处理
```python
import re
import unicodedata

def sanitize_query(query: str, max_length: int = 500) -> str:
    """
    清洗查询文本
    """
    # 长度限制
    if len(query) > max_length:
        query = query[:max_length]

    # Unicode 规范化
    query = unicodedata.normalize('NFKC', query)

    # 移除控制字符
    query = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', query)

    # 移除可疑模式
    suspicious_patterns = [
        r'\\x[0-9a-fA-F]{2}',  # 十六进制转义
        r'\\u[0-9a-fA-F]{4}',  # Unicode 转义
        r'%[0-9a-fA-F]{2}',    # URL 编码
    ]
    for pattern in suspicious_patterns:
        query = re.sub(pattern, '', query)

    return query.strip()
```

#### 方案B：低成本方案（$50-200/月）

**工具/服务**: Pinecone + 自定义安全层

**优势**:
- 托管服务，减少运维成本
- 内置的元数据过滤功能
- 高可用性和扩展性

**配置示例**:
```python
import pinecone

# 初始化
pinecone.init(api_key="your-key", environment="us-west1-gcp")
index = pinecone.Index("your-index")

def secure_query(
    query_vector: List[float],
    user_id: str,
    namespace: str = None
):
    # 元数据过滤：只返回用户有权访问的文档
    filter_dict = {
        "authorized_users": {"$in": [user_id]},
        "is_deleted": False
    }

    results = index.query(
        vector=query_vector,
        top_k=10,
        include_metadata=True,
        filter=filter_dict,
        namespace=namespace
    )

    return results
```

### 决策树
```
你的系统是否使用向量检索？
├── 否 → 低风险
└── 是 → 是否有访问控制？
    ├── 否 → 🔴 高风险：立即添加访问控制
    └── 是 → 是否设置了相似度阈值？
        ├── 否 → 🟡 中风险：添加阈值过滤
        └── 是 → 是否有输入验证？
            ├── 否 → 🟡 中风险：添加输入验证
            └── 是 → ✅ 低风险：定期审计
```

---

## L3 企业版（深耕版）

### 企业级防护措施

1. **多层防御架构**
   ```
   用户查询
       ↓
   [输入验证层] - 长度、格式、黑名单
       ↓
   [嵌入层] - 监控向量质量
       ↓
   [检索层] - 相似度阈值 + 元数据过滤
       ↓
   [访问控制层] - RBAC/ABAC 校验
       ↓
   [输出审核层] - 敏感信息检测
       ↓
   返回结果
   ```

2. **监控与告警**
   - 向量范数异常告警
   - 高相似度查询监控
   - 访问模式异常检测
   - 敏感文档访问审计

3. **对抗性测试**
   - 定期进行红队测试
   - 构造对抗性查询测试集
   - 评估防御措施有效性
   - 持续改进安全策略

### 参考资料
- [FAISS Documentation](https://faiss.ai/)
- [Pinecone Security Best Practices](https://docs.pinecone.io/docs/security)
- [Adversarial Examples in Machine Learning](https://arxiv.org/abs/1312.6199)
- [Unicode Security Considerations](https://unicode.org/reports/tr36/)
