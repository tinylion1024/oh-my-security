# 上下文溢出攻击 - 塞满 AI 的记忆

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: medium
- **修复成本**: L1: 免费 | L2: $50-150/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐ (4/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过发送超长输入或大量消息，填满 AI 的上下文窗口，导致系统 Prompt 被挤出、成本激增或服务拒绝。

### 一分钟识别
你的产品是否有以下特征：
- [ ] AI 对话保留历史消息
- [ ] 用户可以发送长文本
- [ ] 有系统 Prompt 或安全指令
- [ ] 按 Token 计费
→ 勾选≥1项，即需关注此风险

### 一句话防御
设置单条消息长度上限、对话历史轮数限制，优先保留系统 Prompt，监控异常高 Token 消耗。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 设置单条消息最大长度（如 4000 字符）
   - 设置对话历史最大轮数（如 20 轮）
   - 添加 Token 消耗监控

2. [ ] **短期行动项**（本周可完成，免费）
   - 实现智能历史压缩/摘要
   - 确保系统 Prompt 不会被挤出
   - 添加用户级 Token 配额

3. [ ] **长期行动项**（规划中，低成本）
   - 实现动态上下文管理
   - 添加异常消耗告警
   - 优化 Token 使用效率

### 推荐工具
- **免费**：
  - tiktoken - OpenAI Token 计数
  - LangChain ConversationBufferWindow - 窗口化历史管理
  - 自定义 Token 计数函数

- **低成本**：
  - LangSmith - Token 使用追踪
  - OpenAI Usage API - 消耗监控

### 验证方法
- [ ] 发送超长消息，检查是否被限制
- [ ] 进行多轮对话，检查历史是否被正确裁剪
- [ ] 验证系统 Prompt 是否始终保留
- [ ] 检查 Token 消耗监控是否生效

---

## L2 小团队版（理解版）

### 场景还原
你的团队开发了一款"AI 编程助手"，用户可以与 AI 进行多轮对话来编写代码。为了保持上下文连贯，系统会保留完整的对话历史。

某天，运营发现：某些用户的 Token 消耗异常高，单个对话消耗了数百万 Token。经分析发现，这些用户通过发送大量超长消息，填满了上下文窗口，导致：
1. 系统 Prompt 中的安全指令被挤出，AI 行为变得不可控
2. API 调用成本激增，单用户消耗数百美元
3. 响应时间变长，影响其他用户体验

**影响评估**：
- API 成本失控
- 安全指令失效
- 服务质量下降
- 潜在的拒绝服务风险

### 攻击路径（简化版）

**攻击者做了什么**（具体操作）：
1. 发送超长消息（如粘贴整本电子书）
2. 进行大量对话轮次
3. 利用上下文窗口的 FIFO 特性
4. 挤出系统 Prompt 中的安全指令

**利用了什么漏洞**（技术细节）：
1. **无消息长度限制**：用户可发送任意长度消息
2. **无历史轮数限制**：对话历史无限增长
3. **FIFO 上下文管理**：早期消息（包括系统 Prompt）可能被挤出
4. **无 Token 配额**：单用户可消耗无限 Token

**造成了什么后果**（具体损失）：
- API 成本激增
- 安全指令失效，AI 可能输出有害内容
- 响应变慢，用户体验下降
- 服务可能被暂停（API 配额耗尽）

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: 自定义上下文管理

**配置步骤**:

1. 消息长度限制
```python
from typing import List, Dict
import tiktoken

class ContextManager:
    """安全的上下文管理器"""

    def __init__(
        self,
        max_message_length: int = 4000,  # 单条消息最大字符数
        max_history_turns: int = 20,      # 最大历史轮数
        max_total_tokens: int = 8000,     # 最大总 Token 数
        system_prompt: str = ""
    ):
        self.max_message_length = max_message_length
        self.max_history_turns = max_history_turns
        self.max_total_tokens = max_total_tokens
        self.system_prompt = system_prompt
        self.encoding = tiktoken.encoding_for_model("gpt-4")

    def truncate_message(self, message: str) -> str:
        """截断超长消息"""
        if len(message) > self.max_message_length:
            return message[:self.max_message_length] + "\n...[消息过长，已截断]"
        return message

    def count_tokens(self, text: str) -> int:
        """计算 Token 数"""
        return len(self.encoding.encode(text))

    def build_context(
        self,
        history: List[Dict[str, str]],
        new_message: str
    ) -> List[Dict[str, str]]:
        """构建安全的上下文"""

        # 1. 截断新消息
        new_message = self.truncate_message(new_message)

        # 2. 限制历史轮数
        if len(history) > self.max_history_turns:
            history = history[-self.max_history_turns:]

        # 3. 构建完整上下文
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + history + [
            {"role": "user", "content": new_message}
        ]

        # 4. 检查总 Token 数
        total_tokens = sum(self.count_tokens(m["content"]) for m in messages)

        # 5. 如果超限，压缩历史（保留系统 Prompt）
        while total_tokens > self.max_total_tokens and len(history) > 0:
            # 移除最早的历史消息
            history = history[1:]
            messages = [
                {"role": "system", "content": self.system_prompt}
            ] + history + [
                {"role": "user", "content": new_message}
            ]
            total_tokens = sum(self.count_tokens(m["content"]) for m in messages)

        return messages
```

2. Token 消耗监控
```python
from datetime import datetime
from collections import defaultdict

class TokenMonitor:
    """Token 消耗监控"""

    def __init__(self, alert_threshold: int = 100000):
        self.alert_threshold = alert_threshold
        self.user_consumption = defaultdict(int)
        self.hourly_consumption = defaultdict(int)

    def record(self, user_id: str, tokens: int):
        """记录 Token 消耗"""
        self.user_consumption[user_id] += tokens

        hour = datetime.now().strftime("%Y-%m-%d-%H")
        self.hourly_consumption[hour] += tokens

        # 检查是否需要告警
        if self.user_consumption[user_id] > self.alert_threshold:
            self.send_alert(user_id, self.user_consumption[user_id])

    def check_quota(self, user_id: str, quota: int) -> bool:
        """检查用户是否超出配额"""
        return self.user_consumption[user_id] < quota

    def send_alert(self, user_id: str, total: int):
        """发送告警"""
        print(f"⚠️ 告警：用户 {user_id} Token 消耗已达 {total}")
```

3. 智能历史压缩
```python
def compress_history(
    history: List[Dict[str, str]],
    max_tokens: int,
    llm
) -> List[Dict[str, str]]:
    """将长历史压缩为摘要"""

    if len(history) < 5:
        return history

    # 取早期历史生成摘要
    early_history = history[:-3]
    recent_history = history[-3:]

    summary_prompt = f"""请将以下对话历史压缩为简洁的摘要，保留关键信息：

{format_history(early_history)}

摘要："""

    summary = llm.invoke(summary_prompt)

    return [
        {"role": "system", "content": f"[历史摘要] {summary}"}
    ] + recent_history
```

#### 方案B：低成本方案（$50-150/月）

**工具/服务**: LangSmith + 自定义监控

**配置示例**:
```python
from langsmith import Client
from langchain.callbacks import LangChainTracer

# 配置追踪
client = Client()
tracer = LangChainTracer(project_name="my-app")

# 在调用时追踪
response = llm.invoke(
    messages,
    callbacks=[tracer]
)

# 查询消耗统计
runs = client.list_runs(
    project_name="my-app",
    run_type="llm"
)

for run in runs:
    print(f"Run {run.id}: {run.total_tokens} tokens")
```

### 决策树
```
你的 AI 是否保留对话历史？
├── 否 → 低风险
└── 是 → 是否有历史长度限制？
    ├── 否 → 🟡 中风险：添加轮数限制
    └── 是 → 是否有单条消息长度限制？
        ├── 否 → 🟡 中风险：添加长度限制
        └── 是 → 系统 Prompt 是否可能被挤出？
            ├── 是 → 🔴 高风险：修复上下文管理
            └── 否 → 是否有 Token 监控？
                ├── 否 → 🟡 中风险：添加监控
                └── 是 → ✅ 低风险：定期审计
```

---

## L3 企业版（深耕版）

### 企业级防护措施

1. **分层上下文管理**
   ```
   ┌─────────────────────────────────────┐
   │ L0: 系统 Prompt (永久保留)          │
   ├─────────────────────────────────────┤
   │ L1: 安全指令 (高优先级)             │
   ├─────────────────────────────────────┤
   │ L2: 历史摘要 (压缩后保留)           │
   ├─────────────────────────────────────┤
   │ L3: 最近对话 (窗口化保留)           │
   ├─────────────────────────────────────┤
   │ L4: 当前输入 (截断后保留)           │
   └─────────────────────────────────────┘
   ```

2. **动态配额管理**
   - 基于用户等级的 Token 配额
   - 基于时间段的弹性配额
   - 异常消耗自动降级
   - 配额预警和通知

3. **实时监控仪表板**
   - 当前活跃对话数
   - Token 消耗速率
   - 异常用户识别
   - 成本预测

4. **自动响应机制**
   - 超限自动截断
   - 异常用户限流
   - 成本熔断机制
   - 紧急降级预案

### 参考资料
- [OpenAI Token Limits](https://platform.openai.com/docs/models)
- [tiktoken Documentation](https://github.com/openai/tiktoken)
- [LangChain Memory Management](https://python.langchain.com/docs/modules/memory/)
- [Context Window Management Best Practices](https://www.anthropic.com/index/context-windows)
