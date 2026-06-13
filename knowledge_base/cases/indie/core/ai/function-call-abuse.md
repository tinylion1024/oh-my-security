# 函数调用滥用 - AI 的危险之手

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $50-200/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-13

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过 Prompt 注入诱导 AI 调用危险函数，如删除数据、发送邮件、执行系统命令，造成数据丢失或系统被控。

### 一分钟识别
你的产品是否有以下特征：
- [ ] AI 可以调用外部函数/工具
- [ ] 函数包括数据修改/删除操作
- [ ] 函数包括发送消息/邮件功能
- [ ] 函数包括系统命令执行
→ 勾选≥1项，即需关注此风险

### 一句话防御
为每个 AI 可调用的函数添加权限校验、参数验证和审计日志，敏感操作需用户二次确认。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 列出所有 AI 可调用的函数
   - 标记危险函数（删除、发送、执行等）
   - 为危险函数添加确认机制

2. [ ] **短期行动项**（本周可完成，免费）
   - 实现函数调用权限系统
   - 添加参数白名单校验
   - 记录所有函数调用日志

3. [ ] **长期行动项**（规划中，低成本）
   - 实现函数调用沙箱隔离
   - 添加异常调用检测告警
   - 定期审计函数调用日志

### 推荐工具
- **免费**：
  - Python decorators - 权限校验装饰器
  - LangChain Tool Validation - 工具参数验证
  - Pydantic - 参数类型校验

- **低成本**：
  - OpenAI Assistants API - 内置函数调用安全
  - LangSmith - 函数调用追踪和审计

### 验证方法
- [ ] 尝试通过 Prompt 让 AI 调用未授权函数
- [ ] 测试危险函数是否有确认机制
- [ ] 验证参数校验是否生效
- [ ] 检查审计日志是否完整

---

## L2 小团队版（理解版）

### 场景还原
你的团队开发了一款"AI 办公助手"，可以帮用户管理日程、发送邮件、操作文件。为了增强能力，你给 AI 配置了多个函数调用能力。

某天，安全团队发现：攻击者可以通过精心构造的 Prompt，让 AI 调用"删除所有文件"函数或"发送邮件"函数，导致用户数据丢失或发送钓鱼邮件。

**影响评估**：
- 用户数据被删除
- 钓鱼邮件从可信账号发出
- 系统被未授权操作
- 严重损害产品信任度

### 攻击路径（简化版）

**攻击者做了什么**（具体操作）：
1. 分析 AI 可调用的函数列表
2. 构造包含函数调用的 Prompt
3. 诱导 AI 执行危险函数
4. 绕过用户确认机制

**利用了什么漏洞**（技术细节）：
1. **函数权限过大**：AI 可调用删除、发送等敏感函数
2. **参数验证缺失**：函数参数未做白名单校验
3. **确认机制绕过**：用户确认可被 Prompt 绕过
4. **审计日志缺失**：无法追溯异常调用

**造成了什么后果**（具体损失）：
- 用户数据丢失
- 钓鱼攻击从可信源发出
- 系统完整性受损
- 法律和合规风险

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: 自定义权限装饰器

**配置步骤**:

1. 定义函数权限级别
```python
from enum import Enum
from typing import Callable, Any
from functools import wraps

class Permission(Enum):
    READ = "read"        # 只读操作
    WRITE = "write"      # 写入操作
    DELETE = "delete"    # 删除操作
    SEND = "send"        # 发送操作
    EXECUTE = "execute"  # 执行命令

# 函数权限注册表
FUNCTION_PERMISSIONS = {
    "get_user_info": Permission.READ,
    "update_profile": Permission.WRITE,
    "delete_file": Permission.DELETE,
    "send_email": Permission.SEND,
    "execute_command": Permission.EXECUTE,
}

# 用户权限配置
USER_PERMISSIONS = {
    "user_123": [Permission.READ, Permission.WRITE],  # 普通用户
    "admin_456": list(Permission),  # 管理员
}
```

2. 实现权限校验装饰器
```python
def require_permission(func: Callable) -> Callable:
    """函数调用权限校验装饰器"""
    @wraps(func)
    def wrapper(*args, user_id: str = None, **kwargs):
        func_name = func.__name__

        # 获取函数所需权限
        required_perm = FUNCTION_PERMISSIONS.get(func_name)
        if not required_perm:
            raise PermissionError(f"函数 {func_name} 未注册权限")

        # 检查用户权限
        user_perms = USER_PERMISSIONS.get(user_id, [])
        if required_perm not in user_perms:
            # 记录未授权尝试
            log_unauthorized_attempt(user_id, func_name, kwargs)
            raise PermissionError(f"用户 {user_id} 无权限执行 {func_name}")

        # 记录函数调用
        log_function_call(user_id, func_name, kwargs)

        # 执行函数
        return func(*args, **kwargs)

    return wrapper
```

3. 敏感操作确认机制
```python
SENSITIVE_FUNCTIONS = {"delete_file", "send_email", "execute_command"}

def execute_with_confirmation(
    func: Callable,
    user_id: str,
    confirmation_token: str = None,
    **kwargs
):
    """敏感操作需要用户确认"""
    func_name = func.__name__

    if func_name in SENSITIVE_FUNCTIONS:
        # 生成确认令牌
        if not confirmation_token:
            token = generate_confirmation_token(user_id, func_name, kwargs)
            return {
                "status": "confirmation_required",
                "message": f"执行 {func_name} 需要确认",
                "confirmation_token": token
            }

        # 验证确认令牌
        if not validate_confirmation_token(confirmation_token, user_id, func_name):
            raise PermissionError("确认令牌无效或已过期")

    # 执行函数
    return func(user_id=user_id, **kwargs)
```

4. 参数白名单校验
```python
from pydantic import BaseModel, validator

class DeleteFileParams(BaseModel):
    """删除文件函数参数校验"""
    file_path: str

    @validator('file_path')
    def validate_path(cls, v):
        # 只允许删除用户目录下的文件
        if not v.startswith('/user_data/'):
            raise ValueError('只能删除用户目录下的文件')

        # 禁止路径遍历
        if '..' in v:
            raise ValueError('路径中不允许包含 ..')

        return v

# 应用到函数
@require_permission
def delete_file(user_id: str, file_path: str):
    # 参数校验
    params = DeleteFileParams(file_path=file_path)

    # 二次检查：文件属于该用户
    if not file_belongs_to_user(file_path, user_id):
        raise PermissionError("无权删除此文件")

    # 执行删除
    os.remove(params.file_path)
```

#### 方案B：低成本方案（$50-200/月）

**工具/服务**: LangChain + LangSmith

**配置示例**:
```python
from langchain.tools import tool
from langchain.chat_models import ChatOpenAI

# 定义安全的工具
@tool
def safe_send_email(to: str, subject: str, body: str) -> str:
    """
    安全的邮件发送函数，包含多重校验
    """
    # 1. 收件人白名单校验
    if to not in get_user_contacts():
        return "错误：收件人不在联系人列表中"

    # 2. 内容安全检查
    if contains_malicious_content(body):
        return "错误：邮件内容包含可疑内容"

    # 3. 发送频率限制
    if get_send_count_last_hour() > 10:
        return "错误：发送频率超限，请稍后重试"

    # 4. 执行发送
    return send_email(to, subject, body)

# 配置 Agent
llm = ChatOpenAI(model="gpt-4")
agent = initialize_agent(
    tools=[safe_send_email],
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    max_iterations=3,  # 限制迭代次数
)
```

### 决策树
```
你的 AI 是否有函数调用能力？
├── 否 → 低风险
└── 是 → 是否有敏感函数（删除、发送、执行）？
    ├── 否 → 🟡 中风险：添加权限校验
    └── 是 → 是否有用户确认机制？
        ├── 否 → 🔴 高风险：立即添加确认机制
        └── 是 → 是否有参数校验？
            ├── 否 → 🔴 高风险：添加参数校验
            └── 是 → 是否有审计日志？
                ├── 否 → 🟡 中风险：添加审计日志
                └── 是 → ✅ 低风险：定期审计
```

---

## L3 企业版（深耕版）

### 企业级防护措施

1. **函数调用沙箱**
   ```python
   # 使用 Docker 容器隔离函数执行
   def execute_in_sandbox(func, *args, **kwargs):
       with docker_container(
           image="function-sandbox",
           memory_limit="256m",
           cpu_limit="0.5",
           network_disabled=True,
           read_only_fs=True
       ) as sandbox:
           return sandbox.run(func, *args, **kwargs)
   ```

2. **实时监控与告警**
   - 函数调用频率监控
   - 异常参数模式检测
   - 敏感函数调用告警
   - 权限提升尝试检测

3. **审计与溯源**
   - 所有函数调用记录
   - 调用链完整追踪
   - 异常调用自动标记
   - 定期安全审计

4. **应急响应**
   - 紧急禁用函数机制
   - 批量撤销权限流程
   - 影响范围评估工具
   - 用户通知机制

### 参考资料
- [OpenAI Function Calling Best Practices](https://platform.openai.com/docs/guides/function-calling)
- [LangChain Tool Security](https://python.langchain.com/docs/guides/safety/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Principle of Least Privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege)
