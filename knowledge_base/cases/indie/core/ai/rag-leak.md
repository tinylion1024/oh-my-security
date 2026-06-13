# RAG 数据泄露 - 知识库中的隐形漏洞

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $100-300/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户通过精心设计的查询，诱导 RAG 系统返回本不该看到的敏感文档，如其他用户的私人数据、内部机密或被删除的内容。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用 RAG（检索增强生成）技术
- [ ] 知识库包含多用户/多租户数据
- [ ] 用户查询会触发文档检索
- [ ] 检索结果直接展示或用于生成回答
→ 勾选≥1项，即需关注此风险

### 一句话防御
在检索层实施严格的访问控制，确保用户只能检索到其有权访问的文档。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 审计知识库中的文档权限标记
   - 添加用户ID到检索过滤条件
   - 检查是否有全局共享的敏感文档

2. [ ] **短期行动项**（本周可完成，免费）
   - 实现文档级别的访问控制列表(ACL)
   - 添加检索结果的后置权限校验
   - 记录所有文档访问日志

3. [ ] **长期行动项**（规划中，低成本）
   - 实现租户隔离架构
   - 添加敏感数据自动识别
   - 建立数据泄露监控告警

### 推荐工具
- **免费**：
  - PostgreSQL + pgvector - 行级安全策略
  - SQLite + sqlite-vss - 本地向量检索，易于控制
  - FAISS + 自定义过滤层 - 灵活的权限控制

- **低成本**：
  - Pinecone - $70/月 - 元数据过滤功能
  - Weaviate - $25/月起 - 内置多租户支持

### 验证方法
- [ ] 使用用户A的凭证尝试检索用户B的文档
- [ ] 检查删除的文档是否仍可被检索
- [ ] 验证敏感文档是否被正确标记权限
- [ ] 审计检索日志是否记录完整

---

## L2 小团队版（理解版）

### 场景还原
你的团队开发了一款"企业知识库助手"，员工可以上传文档并提问。系统使用 RAG 技术从知识库检索相关文档，然后由 AI 生成回答。

某天，安全审计发现：普通员工可以通过构造特定查询，检索到 HR 部门的薪资文档、CEO 的私人备忘录，甚至已离职员工的个人信息。原因是系统在检索时未校验用户对文档的访问权限。

**影响评估**：
- 敏感人事信息泄露
- 高管私密文档暴露
- 员工隐私数据泄露
- 可能违反劳动法和数据保护法规

### 攻击路径（简化版）

**攻击者做了什么**（具体操作）：
1. 分析 RAG 系统的检索逻辑
2. 构造广泛匹配的查询（如"所有文档"、"工资"）
3. 利用检索结果直接展示的漏洞
4. 获取本无权访问的敏感文档

**利用了什么漏洞**（技术细节）：
1. **检索层无权限校验**：向量检索只看相似度，不看权限
2. **文档元数据缺失**：上传时未标记文档所有者和访问范围
3. **多租户隔离失败**：所有文档存储在同一索引中
4. **结果过滤缺失**：检索结果直接返回，未经权限过滤

**造成了什么后果**（具体损失）：
- 敏感信息大规模泄露
- 企业合规风险
- 员工信任危机
- 可能面临法律诉讼

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: PostgreSQL + pgvector + 行级安全

**配置步骤**:

1. 创建带权限标记的文档表
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    owner_id UUID NOT NULL,
    department_id UUID,
    access_level TEXT DEFAULT 'private',  -- private, department, public
    created_at TIMESTAMP DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE
);

-- 创建向量索引
CREATE INDEX ON documents USING ivfflat (embedding vector_cosine_ops);
```

2. 启用行级安全策略
```sql
-- 启用行级安全
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 创建策略：用户只能看到自己的文档或公开文档
CREATE POLICY document_access_policy ON documents
    FOR SELECT
    USING (
        owner_id = current_user_id()  -- 自己的文档
        OR access_level = 'public'    -- 公开文档
        OR (access_level = 'department' AND department_id = current_user_department())  -- 部门文档
    );
```

3. 安全检索函数
```python
import psycopg2
from typing import List

def secure_rag_query(
    query_embedding: List[float],
    user_id: str,
    user_department: str,
    top_k: int = 5
) -> List[dict]:
    """
    安全的 RAG 检索，自动应用行级安全
    """
    conn = psycopg2.connect(DATABASE_URL)

    # 设置当前用户上下文
    conn.execute(f"SET app.current_user_id = '{user_id}'")
    conn.execute(f"SET app.current_department = '{user_department}'")

    # 执行检索（行级安全自动应用）
    results = conn.execute("""
        SELECT id, content, 1 - (embedding <=> %s::vector) as similarity
        FROM documents
        WHERE is_deleted = FALSE
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, top_k))

    return results.fetchall()
```

#### 方案B：低成本方案（$100-300/月）

**工具/服务**: Pinecone + 自定义权限层

**架构设计**:
```
用户查询
    ↓
[认证层] - 验证用户身份
    ↓
[权限解析] - 获取用户可访问的文档ID列表
    ↓
[向量检索] - Pinecone 查询 + 元数据过滤
    ↓
[结果校验] - 二次权限验证
    ↓
[内容过滤] - 敏感信息脱敏
    ↓
返回结果
```

**配置示例**:
```python
import pinecone

def rag_query_with_acl(
    query_vector: List[float],
    user_id: str,
    top_k: int = 10
):
    # 1. 获取用户可访问的文档列表（从数据库）
    accessible_docs = get_user_accessible_docs(user_id)

    # 2. 构建元数据过滤条件
    filter_dict = {
        "doc_id": {"$in": accessible_docs},
        "is_deleted": False
    }

    # 3. 执行检索
    results = pinecone_index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter_dict
    )

    # 4. 二次校验（防止 Pinecone 配置错误）
    for match in results.matches:
        if match.id not in accessible_docs:
            raise SecurityError("权限校验失败")

    return results
```

### 决策树
```
你的 RAG 系统是否有多用户数据？
├── 否 → 低风险
└── 是 → 是否有文档级别的权限标记？
    ├── 否 → 🔴 高风险：立即添加权限标记
    └── 是 → 检索时是否应用权限过滤？
        ├── 否 → 🔴 高风险：立即添加检索过滤
        └── 是 → 是否有二次校验？
            ├── 否 → 🟡 中风险：添加二次校验
            └── 是 → ✅ 低风险：定期审计
```

---

## L3 企业版（深耕版）

### 企业级防护措施

1. **多租户隔离架构**
   ```
   租户A ──→ 独立命名空间/索引 ──→ 租户A文档
   租户B ──→ 独立命名空间/索引 ──→ 租户B文档
   租户C ──→ 独立命名空间/索引 ──→ 租户C文档

   + 跨租户访问需要显式授权
   + 定期审计租户隔离有效性
   ```

2. **数据分类分级**
   - L1 公开数据：无访问限制
   - L2 内部数据：员工可访问
   - L3 敏感数据：特定角色可访问
   - L4 机密数据：需二次授权

3. **监控与审计**
   - 所有文档访问记录
   - 异常访问模式告警
   - 敏感文档访问通知
   - 定期权限审计

4. **应急响应**
   - 发现泄露时的文档锁定机制
   - 用户权限紧急撤销流程
   - 泄露影响评估流程
   - 通知受影响用户流程

### 参考资料
- [PostgreSQL Row Level Security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [Pinecone Metadata Filtering](https://docs.pinecone.io/docs/metadata-filtering)
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [NIST Data Protection Guidelines](https://csrc.nist.gov/publications/detail/sp/800-122/final)
