# AI 成本控制

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 1-2小时
- **维护成本**: 1-2小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
控制 AI API 调用成本，防止恶意超额使用、意外账单爆炸和资源滥用。

## 快速上手（5分钟）

```python
# ai_cost_control.py - 最小可运行示例
import time
from functools import wraps
from typing import Callable, Optional
from dataclasses import dataclass

@dataclass
class UsageStats:
    total_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    last_reset: float = 0.0

class SimpleCostController:
    """5分钟版成本控制器"""

    def __init__(
        self,
        monthly_budget: float = 50.0,  # 月预算
        daily_budget: float = 5.0,      # 日预算
        cost_per_1k_tokens: float = 0.002  # GPT-3.5-turbo 价格
    ):
        self.monthly_budget = monthly_budget
        self.daily_budget = daily_budget
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.stats = UsageStats(last_reset=time.time())

    def estimate_cost(self, tokens: int) -> float:
        """估算成本"""
        return (tokens / 1000) * self.cost_per_1k_tokens

    def check_budget(self, estimated_tokens: int) -> tuple[bool, str]:
        """检查预算"""
        estimated_cost = self.estimate_cost(estimated_tokens)

        # 检查月预算
        if self.stats.total_cost + estimated_cost > self.monthly_budget:
            return False, f"超出月预算 (${self.stats.total_cost:.2f}/${self.monthly_budget})"

        # 检查日预算（简化版，实际应每天重置）
        daily_cost = self.stats.total_cost  # 简化处理
        if daily_cost + estimated_cost > self.daily_budget:
            return False, f"超出日预算 (${daily_cost:.2f}/${self.daily_budget})"

        return True, "预算充足"

    def record_usage(self, tokens: int, cost: float):
        """记录使用"""
        self.stats.total_calls += 1
        self.stats.total_tokens += tokens
        self.stats.total_cost += cost

    def get_stats(self) -> dict:
        """获取统计"""
        return {
            "total_calls": self.stats.total_calls,
            "total_tokens": self.stats.total_tokens,
            "total_cost": self.stats.total_cost,
            "monthly_budget": self.monthly_budget,
            "remaining_budget": self.monthly_budget - self.stats.total_cost,
            "budget_usage_percent": (self.stats.total_cost / self.monthly_budget) * 100
        }

# 使用示例 - 装饰器模式
def with_cost_control(controller: SimpleCostController):
    """成本控制装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 从 kwargs 获取预估 token 数
            estimated_tokens = kwargs.pop('estimated_tokens', 1000)

            # 检查预算
            allowed, reason = controller.check_budget(estimated_tokens)
            if not allowed:
                raise RuntimeError(f"Budget exceeded: {reason}")

            # 执行函数
            result = func(*args, **kwargs)

            # 记录实际使用（假设 result 包含 usage 信息）
            actual_tokens = getattr(result, 'usage', {}).get('total_tokens', estimated_tokens)
            actual_cost = controller.estimate_cost(actual_tokens)
            controller.record_usage(actual_tokens, actual_cost)

            return result
        return wrapper
    return decorator

# 实际使用
if __name__ == "__main__":
    controller = SimpleCostController(
        monthly_budget=10.0,
        daily_budget=2.0
    )

    @with_cost_control(controller)
    def call_ai(prompt: str, estimated_tokens: int = 500):
        # 模拟 AI 调用
        class MockResponse:
            usage = {"total_tokens": 450}
        return MockResponse()

    # 正常调用
    try:
        for i in range(5):
            result = call_ai("Hello", estimated_tokens=500)
            print(f"调用 {i+1}: 成功")
            print(controller.get_stats())
    except RuntimeError as e:
        print(f"错误: {e}")
```

## 详细方案

### 方案架构

```
┌─────────────────────────────────────────────────────────────┐
│                    AI API 请求                               │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 请求拦截                                          │
│  - 用户身份验证                                             │
│  - 速率限制检查                                             │
│  - 预估 token 数计算                                        │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 预算检查                                          │
│  - 用户级配额检查                                           │
│  - 全局预算检查                                             │
│  - 时段限制检查                                             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 缓存层 (可选)                                     │
│  - 相似请求缓存                                             │
│  - 语义缓存                                                 │
│  - TTL 管理                                                 │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: 执行 & 监控                                       │
│  - 调用 AI API                                              │
│  - 记录实际 token 使用                                      │
│  - 实时成本监控                                             │
└────────────────────────┬────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    返回结果                                  │
└─────────────────────────────────────────────────────────────┘
```

### 实现步骤

#### 步骤1: 用量监控系统 (30分钟)

```python
# usage_monitor.py
import time
import json
import threading
from typing import Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import redis  # 可选，用于分布式

@dataclass
class UserUsage:
    """用户使用记录"""
    user_id: str
    total_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    calls_by_model: Dict[str, int] = None
    last_call_time: float = 0.0

    def __post_init__(self):
        if self.calls_by_model is None:
            self.calls_by_model = defaultdict(int)

class UsageMonitor:
    """用量监控系统"""

    # 模型价格表 (美元/1k tokens)
    MODEL_PRICES = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    }

    def __init__(self, storage_backend: str = "memory", redis_url: Optional[str] = None):
        self.storage_backend = storage_backend

        if storage_backend == "redis" and redis_url:
            self.redis_client = redis.from_url(redis_url)
        else:
            # 内存存储
            self.memory_store: Dict[str, UserUsage] = {}
            self.global_stats = {
                "total_calls": 0,
                "total_tokens": 0,
                "total_cost": 0.0,
                "start_time": time.time()
            }

        self._lock = threading.Lock()

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """计算实际成本"""
        if model not in self.MODEL_PRICES:
            # 使用默认价格
            return (input_tokens + output_tokens) * 0.001

        prices = self.MODEL_PRICES[model]
        input_cost = (input_tokens / 1000) * prices["input"]
        output_cost = (output_tokens / 1000) * prices["output"]
        return input_cost + output_cost

    def record_usage(
        self,
        user_id: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency: float = 0.0
    ) -> Dict:
        """记录使用情况"""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        total_tokens = input_tokens + output_tokens

        with self._lock:
            if self.storage_backend == "redis":
                # Redis 存储
                key = f"usage:{user_id}"
                today = datetime.now().strftime("%Y-%m-%d")

                pipe = self.redis_client.pipeline()
                pipe.hincrby(f"{key}:total", "calls", 1)
                pipe.hincrby(f"{key}:total", "tokens", total_tokens)
                pipe.hincrbyfloat(f"{key}:total", "cost", cost)
                pipe.hincrby(f"{key}:daily:{today}", "calls", 1)
                pipe.hincrby(f"{key}:daily:{today}", "tokens", total_tokens)
                pipe.hincrbyfloat(f"{key}:daily:{today}", "cost", cost)
                pipe.expire(f"{key}:daily:{today}", 86400 * 7)  # 7天过期
                pipe.execute()

            else:
                # 内存存储
                if user_id not in self.memory_store:
                    self.memory_store[user_id] = UserUsage(user_id=user_id)

                usage = self.memory_store[user_id]
                usage.total_calls += 1
                usage.total_tokens += total_tokens
                usage.total_cost += cost
                usage.calls_by_model[model] += 1
                usage.last_call_time = time.time()

                # 更新全局统计
                self.global_stats["total_calls"] += 1
                self.global_stats["total_tokens"] += total_tokens
                self.global_stats["total_cost"] += cost

        return {
            "user_id": user_id,
            "model": model,
            "tokens": total_tokens,
            "cost": cost,
            "latency": latency
        }

    def get_user_usage(self, user_id: str) -> Dict:
        """获取用户使用统计"""
        if self.storage_backend == "redis":
            key = f"usage:{user_id}"
            data = self.redis_client.hgetall(f"{key}:total")
            return {k.decode(): float(v.decode()) for k, v in data.items()}
        else:
            if user_id in self.memory_store:
                return asdict(self.memory_store[user_id])
            return {}

    def get_global_stats(self) -> Dict:
        """获取全局统计"""
        if self.storage_backend == "redis":
            # 需要聚合所有用户数据
            total_calls = 0
            total_tokens = 0
            total_cost = 0.0

            for key in self.redis_client.scan_iter("usage:*:total"):
                data = self.redis_client.hgetall(key)
                total_calls += int(data.get(b"calls", b"0"))
                total_tokens += int(data.get(b"tokens", b"0"))
                total_cost += float(data.get(b"cost", b"0"))

            return {
                "total_calls": total_calls,
                "total_tokens": total_tokens,
                "total_cost": total_cost
            }
        else:
            return self.global_stats.copy()

    def get_daily_usage(self, user_id: str, date: Optional[str] = None) -> Dict:
        """获取日使用量"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        if self.storage_backend == "redis":
            key = f"usage:{user_id}:daily:{date}"
            data = self.redis_client.hgetall(key)
            return {k.decode(): float(v.decode()) for k, v in data.items()}
        else:
            # 内存存储需要额外实现
            return {}

# 使用示例
if __name__ == "__main__":
    monitor = UsageMonitor(storage_backend="memory")

    # 记录使用
    for i in range(3):
        result = monitor.record_usage(
            user_id="user_123",
            model="gpt-4o-mini",
            input_tokens=500,
            output_tokens=200
        )
        print(f"调用 {i+1}: ${result['cost']:.4f}")

    # 查看统计
    print("\n用户统计:")
    print(json.dumps(monitor.get_user_usage("user_123"), indent=2))

    print("\n全局统计:")
    print(json.dumps(monitor.get_global_stats(), indent=2))
```

#### 步骤2: 预算限制系统 (30分钟)

```python
# budget_limiter.py
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class BudgetPeriod(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class BudgetLimit:
    """预算限制配置"""
    user_id: str
    period: BudgetPeriod
    max_calls: Optional[int] = None
    max_tokens: Optional[int] = None
    max_cost: Optional[float] = None
    max_requests_per_minute: Optional[int] = None

class BudgetLimiter:
    """预算限制器"""

    def __init__(self, usage_monitor):
        self.monitor = usage_monitor
        self.limits: Dict[str, BudgetLimit] = {}
        self.rate_limiters: Dict[str, list] = {}  # 速率限制滑动窗口

    def set_limit(self, limit: BudgetLimit):
        """设置预算限制"""
        self.limits[limit.user_id] = limit

    def check_limit(
        self,
        user_id: str,
        estimated_tokens: int,
        estimated_cost: float
    ) -> Tuple[bool, str]:
        """检查是否超出预算"""

        if user_id not in self.limits:
            return True, "无限制"

        limit = self.limits[user_id]

        # 1. 检查速率限制
        if limit.max_requests_per_minute:
            allowed, reason = self._check_rate_limit(
                user_id,
                limit.max_requests_per_minute
            )
            if not allowed:
                return False, reason

        # 2. 获取当前使用量
        usage = self.monitor.get_user_usage(user_id)

        # 3. 检查调用次数限制
        if limit.max_calls:
            current_calls = usage.get("total_calls", 0)
            if current_calls >= limit.max_calls:
                return False, f"超出调用次数限制 ({current_calls}/{limit.max_calls})"

        # 4. 检查 token 限制
        if limit.max_tokens:
            current_tokens = usage.get("total_tokens", 0)
            if current_tokens + estimated_tokens > limit.max_tokens:
                remaining = limit.max_tokens - current_tokens
                return False, f"超出 token 限制 (剩余: {remaining})"

        # 5. 检查成本限制
        if limit.max_cost:
            current_cost = usage.get("total_cost", 0.0)
            if current_cost + estimated_cost > limit.max_cost:
                remaining = limit.max_cost - current_cost
                return False, f"超出成本限制 (剩余: ${remaining:.2f})"

        return True, "通过检查"

    def _check_rate_limit(
        self,
        user_id: str,
        max_requests: int
    ) -> Tuple[bool, str]:
        """检查速率限制 (滑动窗口)"""
        now = time.time()
        window_start = now - 60  # 1分钟窗口

        if user_id not in self.rate_limiters:
            self.rate_limiters[user_id] = []

        # 清理过期记录
        self.rate_limiters[user_id] = [
            t for t in self.rate_limiters[user_id]
            if t > window_start
        ]

        # 检查数量
        if len(self.rate_limiters[user_id]) >= max_requests:
            return False, f"速率限制 (每分钟最多 {max_requests} 次)"

        # 记录本次请求
        self.rate_limiters[user_id].append(now)

        return True, "通过"

# 使用示例
if __name__ == "__main__":
    from usage_monitor import UsageMonitor

    monitor = UsageMonitor(storage_backend="memory")
    limiter = BudgetLimiter(monitor)

    # 设置预算限制
    limiter.set_limit(BudgetLimit(
        user_id="user_123",
        period=BudgetPeriod.DAILY,
        max_calls=10,
        max_tokens=10000,
        max_cost=1.0,
        max_requests_per_minute=5
    ))

    # 模拟调用
    for i in range(12):
        # 先检查
        allowed, reason = limiter.check_limit(
            user_id="user_123",
            estimated_tokens=1000,
            estimated_cost=0.1
        )

        if not allowed:
            print(f"❌ 调用 {i+1}: {reason}")
            continue

        # 记录使用
        monitor.record_usage(
            user_id="user_123",
            model="gpt-4o-mini",
            input_tokens=500,
            output_tokens=500
        )
        print(f"✅ 调用 {i+1}: 成功")
```

#### 步骤3: 缓存策略 (30分钟)

```python
# semantic_cache.py
import hashlib
import json
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class CacheEntry:
    """缓存条目"""
    query: str
    response: Any
    tokens_used: int
    cost_saved: float
    created_at: float
    ttl: int
    hit_count: int = 0

class SemanticCache:
    """语义缓存层"""

    def __init__(
        self,
        ttl: int = 3600,  # 默认1小时
        max_entries: int = 1000,
        similarity_threshold: float = 0.95
    ):
        self.ttl = ttl
        self.max_entries = max_entries
        self.similarity_threshold = similarity_threshold
        self.cache: Dict[str, CacheEntry] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0
        }

    def _hash_query(self, query: str, model: str = "default") -> str:
        """生成查询哈希"""
        # 标准化查询
        normalized = query.strip().lower()
        content = f"{model}:{normalized}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, query: str, model: str = "default") -> Optional[Any]:
        """获取缓存"""
        key = self._hash_query(query, model)

        if key not in self.cache:
            self.stats["misses"] += 1
            return None

        entry = self.cache[key]

        # 检查 TTL
        if time.time() - entry.created_at > entry.ttl:
            del self.cache[key]
            self.stats["misses"] += 1
            return None

        # 命中
        entry.hit_count += 1
        self.stats["hits"] += 1
        self.stats["tokens_saved"] += entry.tokens_used
        self.stats["cost_saved"] += entry.cost_saved

        return entry.response

    def set(
        self,
        query: str,
        response: Any,
        tokens_used: int,
        cost: float,
        model: str = "default",
        ttl: Optional[int] = None
    ):
        """设置缓存"""
        # 检查容量
        if len(self.cache) >= self.max_entries:
            self._evict_oldest()

        key = self._hash_query(query, model)
        entry = CacheEntry(
            query=query,
            response=response,
            tokens_used=tokens_used,
            cost_saved=cost,
            created_at=time.time(),
            ttl=ttl or self.ttl
        )

        self.cache[key] = entry

    def _evict_oldest(self):
        """清理最旧的条目"""
        if not self.cache:
            return

        # LRU 淘汰
        oldest_key = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].created_at
        )
        del self.cache[oldest_key]

    def get_stats(self) -> Dict:
        """获取统计"""
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0

        return {
            "total_entries": len(self.cache),
            "hit_rate": f"{hit_rate:.1f}%",
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "tokens_saved": self.stats["tokens_saved"],
            "cost_saved": f"${self.stats['cost_saved']:.2f}"
        }

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "tokens_saved": 0,
            "cost_saved": 0.0
        }

# 完整集成示例
class CachedAIClient:
    """带缓存的 AI 客户端"""

    def __init__(self, cache: SemanticCache, budget_limiter: BudgetLimiter):
        self.cache = cache
        self.limiter = budget_limiter
        self.monitor = budget_limiter.monitor

    async def call(
        self,
        user_id: str,
        prompt: str,
        model: str = "gpt-4o-mini",
        estimated_tokens: int = 1000
    ) -> Dict:
        """调用 AI (带缓存和预算控制)"""

        # 1. 尝试缓存
        cached = self.cache.get(prompt, model)
        if cached:
            return {
                "response": cached,
                "from_cache": True,
                "cost": 0.0
            }

        # 2. 预算检查
        estimated_cost = self.monitor.calculate_cost(
            model, estimated_tokens // 2, estimated_tokens // 2
        )
        allowed, reason = self.limiter.check_limit(
            user_id, estimated_tokens, estimated_cost
        )
        if not allowed:
            raise RuntimeError(f"Budget exceeded: {reason}")

        # 3. 调用 AI (模拟)
        # response = await actual_ai_call(prompt, model)
        response = f"AI response to: {prompt[:50]}..."
        actual_tokens = 800
        actual_cost = self.monitor.calculate_cost(model, 400, 400)

        # 4. 记录使用
        self.monitor.record_usage(
            user_id=user_id,
            model=model,
            input_tokens=400,
            output_tokens=400
        )

        # 5. 存入缓存
        self.cache.set(
            query=prompt,
            response=response,
            tokens_used=actual_tokens,
            cost=actual_cost,
            model=model
        )

        return {
            "response": response,
            "from_cache": False,
            "cost": actual_cost
        }

# 使用示例
if __name__ == "__main__":
    from usage_monitor import UsageMonitor
    from budget_limiter import BudgetLimiter, BudgetLimit, BudgetPeriod

    # 初始化
    monitor = UsageMonitor()
    limiter = BudgetLimiter(monitor)
    cache = SemanticCache(ttl=3600)

    # 设置限制
    limiter.set_limit(BudgetLimit(
        user_id="user_123",
        period=BudgetPeriod.DAILY,
        max_cost=1.0
    ))

    # 创建客户端
    client = CachedAIClient(cache, limiter)

    # 模拟调用
    import asyncio

    async def test():
        prompts = [
            "What is AI?",
            "What is AI?",  # 重复,会命中缓存
            "Explain machine learning",
            "What is AI?",  # 再次命中缓存
        ]

        for prompt in prompts:
            try:
                result = await client.call(
                    user_id="user_123",
                    prompt=prompt,
                    model="gpt-4o-mini"
                )
                cache_status = "💾 缓存" if result["from_cache"] else "🆕 新请求"
                print(f"{cache_status}: {prompt[:30]}... (${result['cost']:.4f})")
            except RuntimeError as e:
                print(f"❌ {e}")

        print("\n缓存统计:")
        print(cache.get_stats())

    asyncio.run(test())
```

### 配置选项

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| monthly_budget | 50.0 | 月预算上限 (美元) |
| daily_budget | 5.0 | 日预算上限 (美元) |
| cost_per_1k_tokens | 0.002 | 每1k token 成本估算 |
| max_requests_per_minute | 60 | 每分钟最大请求数 |
| cache_ttl | 3600 | 缓存 TTL (秒) |
| max_cache_entries | 1000 | 最大缓存条目数 |

## 成本估算

| 指标 | 免费方案 | Redis 方案 |
|------|---------|-----------|
| 月成本 | $0 | $5-15 (Redis Cloud) |
| 性能 | 单机 1000 req/s | 分布式 10000+ req/s |
| 可靠性 | 进程重启丢失 | 持久化存储 |
| 功能 | 基础监控 | 分布式限流 |

### 典型成本节省

| 场景 | 原成本 | 使用缓存后 | 节省 |
|-----|-------|----------|------|
| FAQ 问答 | $10/月 | $3/月 | 70% |
| 文档总结 | $50/月 | $20/月 | 60% |
| 代码生成 | $100/月 | $80/月 | 20% |
| 创意写作 | $200/月 | $180/月 | 10% |

## 迁出成本

- **迁出难度**: 低
- **迁出步骤**:
  1. 导出用户使用记录 (JSON/CSV)
  2. 迁移预算配置
  3. 清空缓存，无需迁移
  4. 切换到新系统的 API 接口

## 与其他武器配合

- **前置**: 无
- **后置**:
  - [Prompt 过滤](../open-source/prompt-filter.md) - 在成本控制前过滤无效请求
  - [AI 输出清洗](../open-source/output-sanitizer.md) - 控制输出处理成本
- **配合**: [AI 安全服务](../saas/ai-security-service.md) - 部分服务包含成本监控功能

## 常见问题

**Q: 如何设置合理的预算？**

A: 建议从低开始：
```python
# 第1周: 观察用量
daily_budget = 1.0  # 每天 $1
monthly_budget = 20.0  # 每月 $20

# 第2-4周: 根据实际调整
# 查看 p95 用量，设置为 1.5 倍
```

**Q: 如何处理突发流量？**

A: 使用弹性预算 + 告警：
```python
# 弹性预算
normal_budget = 5.0
burst_budget = 20.0  # 需要额外授权

# 告警阈值
warning_threshold = 0.7  # 70% 时警告
critical_threshold = 0.9  # 90% 时紧急
```

**Q: 缓存会不会返回过期信息？**

A: 设置合理的 TTL：
```python
# 根据内容类型设置
ttl_config = {
    "static_faq": 86400,      # 24小时
    "product_info": 3600,      # 1小时
    "realtime_data": 300,      # 5分钟
    "user_specific": 0,        # 不缓存
}
```

**Q: 如何防止用户刷量？**

A: 多层限制：
```python
limiter.set_limit(BudgetLimit(
    user_id="user_123",
    max_requests_per_minute=10,  # 速率限制
    max_calls_per_day=100,        # 日调用限制
    max_cost_per_day=1.0          # 成本限制
))
```

## 推荐实现

### 免费
- **自建方案**: 本模板代码 - $0
- **SQLite**: 本地持久化 - $0
- **内存缓存**: Python dict - $0

### 低成本
- **Redis Cloud**: https://redis.com - $5/月起
- **Upstash Redis**: https://upstash.com - 免费层 + 按量付费
- **Dragonfly**: https://dragonflydb.io - 开源 Redis 替代

### 企业级
- **AWS ElastiCache**: Redis 托管服务
- **Azure Cache**: Redis 企业版
- **GCP Memorystore**: 托管 Redis

## 告警配置

```python
# alerting.py
import smtplib
from email.mime.text import MIMEText
from typing import Optional

class BudgetAlerter:
    """预算告警"""

    def __init__(
        self,
        warning_threshold: float = 0.7,
        critical_threshold: float = 0.9,
        email_config: Optional[Dict] = None,
        webhook_url: Optional[str] = None
    ):
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.email_config = email_config
        self.webhook_url = webhook_url

    def check_and_alert(self, usage_percent: float, stats: Dict):
        """检查并发送告警"""
        if usage_percent >= self.critical_threshold:
            self._send_alert("CRITICAL", usage_percent, stats)
        elif usage_percent >= self.warning_threshold:
            self._send_alert("WARNING", usage_percent, stats)

    def _send_alert(self, level: str, percent: float, stats: Dict):
        """发送告警"""
        message = f"""
[{level}] AI Budget Alert

Usage: {percent:.1%}
Total Cost: ${stats.get('total_cost', 0):.2f}
Total Calls: {stats.get('total_calls', 0)}

Action needed: {'IMMEDIATE' if level == 'CRITICAL' else 'Review usage'}
"""

        # 邮件告警
        if self.email_config:
            self._send_email(level, message)

        # Webhook 告警
        if self.webhook_url:
            self._send_webhook(level, percent, stats)

    def _send_email(self, subject: str, message: str):
        """发送邮件"""
        # 实现邮件发送
        pass

    def _send_webhook(self, level: str, percent: float, stats: Dict):
        """发送 Webhook"""
        # 实现 Webhook 调用
        pass
```

## 监控面板

```python
# dashboard.py - 简单文本仪表盘
class CostDashboard:
    """成本监控仪表盘"""

    def __init__(self, monitor, limiter):
        self.monitor = monitor
        self.limiter = limiter

    def display(self):
        """显示仪表盘"""
        stats = self.monitor.get_global_stats()

        print("=" * 60)
        print("  AI 成本监控仪表盘")
        print("=" * 60)
        print(f"  总调用次数: {stats['total_calls']:,}")
        print(f"  总 Token 数: {stats['total_tokens']:,}")
        print(f"  总成本: ${stats['total_cost']:.2f}")
        print("-" * 60)

        # 预算使用
        if stats.get('monthly_budget'):
            usage = stats['total_cost'] / stats['monthly_budget'] * 100
            bar = self._progress_bar(usage)
            print(f"  月预算使用: {bar} {usage:.1f}%")

        print("=" * 60)

    def _progress_bar(self, percent: float, width: int = 20) -> str:
        """进度条"""
        filled = int(width * percent / 100)
        return "█" * filled + "░" * (width - filled)

# 使用
if __name__ == "__main__":
    # 初始化...
    dashboard = CostDashboard(monitor, limiter)
    dashboard.display()
```

## 维护建议

1. **每日**: 检查预算使用情况，查看异常调用
2. **每周**: 分析缓存命中率，优化缓存策略
3. **每月**: 调整预算配置，清理历史数据
4. **持续**: 监控 API 价格变化，调整成本估算
