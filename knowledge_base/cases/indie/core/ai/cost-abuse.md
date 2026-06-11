# AI 成本滥用 - 隐形的天价账单

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: ai
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $20-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
攻击者通过脚本或漏洞大量调用你的 AI API，一夜之间产生数千美元账单，让你从盈利变亏损。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用按量付费的 AI API（OpenAI、Anthropic 等）
- [ ] 没有用户级别的调用限制
- [ ] API Key 暴露在前端代码中
- [ ] 免费用户可以无限调用
→ 勾选≥1项，即需关注此风险

### 一句话防御
实施多层次的用量限制：用户级、IP级、全局级，并设置成本预警。

### 快速行动清单
1. [ ] **立即行动项**（今天可完成，免费）
   - 为每个用户设置每日调用上限
   - 在 API 供应商处设置月度预算上限
   - 移除前端代码中的 API Key
   
2. [ ] **短期行动项**（本周可完成，免费）
   - 实现调用频率限制（Rate Limiting）
   - 添加成本监控和告警
   - 记录每次调用的 token 消耗
   
3. [ ] **长期行动项**（规划中，低成本）
   - 部署专业 API 网关
   - 实现动态成本优化
   - 建立异常检测系统

### 推荐工具
- **免费**：
  - Redis + 自建 Rate Limiter - 免费实现速率限制
  - Cloudflare Workers - 免费额度内实现 API 保护
  - Upstash Rate Limit - https://github.com/upstash/ratelimit - 免费额度

- **低成本**：
  - Kong Gateway (开源版) - 免费 API 网关
  - AWS Cost Explorer - 免费 AWS 成本监控
  - OpenAI Usage API - 免费查询用量

### 验证方法
- [ ] 测试速率限制是否生效（快速发送多次请求）
- [ ] 确认 API 供应商预算上限已设置
- [ ] 检查是否能从前端代码获取 API Key
- [ ] 验证成本告警是否能正常触发

---

## L2 小团队版（理解版）

### 场景还原
你的创业团队开发了一款"AI 写作助手"，使用 GPT-4 API，按 token 计费。产品定价 $9.9/月，上线 3 个月积累了 1000 付费用户。

某天凌晨 3 点，你收到 AWS 账单提醒：本月费用已达 $5000，远超预期的 $500。调查发现：
- 一个恶意用户注册了 10 个免费账号
- 使用自动化脚本在每个账号调用 API 超过 10000 次
- 每次请求都是最大 token 限制（4096 tokens）
- 总计消耗了 4 亿 tokens，成本约 $4000

攻击脚本示例：
```python
import requests
import threading

def abuse_api(api_key):
    while True:
        requests.post(
            "https://your-api.com/chat",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"message": "x" * 4000}  # 最大长度请求
        )

# 多线程滥用
for _ in range(100):
    threading.Thread(target=abuse_api, args=(leaked_key,)).start()
```

**影响评估**：
- 单日损失超过月收入
- 现金流断裂风险
- 可能需要暂停服务
- 用户信任受损

### 攻击路径（简化版）

**攻击者做了什么**（具体操作）：
1. 从前端代码或网络请求中提取 API Key
2. 编写自动化脚本高频调用 API
3. 使用多个账号/IP 绕过简单限制
4. 每次请求消耗最大资源

**利用了什么漏洞**（技术细节）：
1. **API Key 泄露**：前端暴露或日志记录
2. **无速率限制**：允许无限频率调用
3. **无用户限制**：无每日/每月调用上限
4. **无预算控制**：未设置供应商侧预算上限
5. **监控缺失**：无实时成本告警

**造成了什么后果**（具体损失）：
- 直接经济损失（API 费用）
- 服务可能被迫暂停
- 正常用户体验受影响
- 潜在的竞争对手恶意攻击

### 防御实施（低成本方案）

#### 方案A：免费方案

**工具/服务**: Redis + 自建限流系统

**配置步骤**:

1. 安装依赖
```bash
pip install redis fastapi uvicorn
```

2. 实现多层次限流
```python
import redis
import time
from fastapi import FastAPI, HTTPException, Request
from typing import Dict, Optional
import hashlib

class CostAbuseProtection:
    """成本滥用防护系统"""
    
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            decode_responses=True
        )
        
        # 限流配置
        self.limits = {
            'per_minute': 10,      # 每分钟
            'per_hour': 100,       # 每小时
            'per_day': 500,        # 每天每用户
            'per_month': 5000,     # 每月每用户
            'global_per_minute': 1000,  # 全局每分钟
        }
        
        # Token 配额
        self.token_quotas = {
            'free': 10000,      # 免费用户每日 tokens
            'basic': 100000,    # 基础用户每日 tokens
            'pro': 500000       # Pro 用户每日 tokens
        }
    
    def _get_keys(self, user_id: str, ip: str) -> Dict[str, str]:
        """生成限流 key"""
        now = time.time()
        minute = int(now / 60)
        hour = int(now / 3600)
        day = int(now / 86400)
        month = int(now / (86400 * 30))
        
        return {
            'user_minute': f"limit:user:{user_id}:minute:{minute}",
            'user_hour': f"limit:user:{user_id}:hour:{hour}",
            'user_day': f"limit:user:{user_id}:day:{day}",
            'user_month': f"limit:user:{user_id}:month:{month}",
            'ip_minute': f"limit:ip:{ip}:minute:{minute}",
            'global_minute': f"limit:global:minute:{minute}",
        }
    
    def check_rate_limit(self, user_id: str, ip: str) -> Dict:
        """检查是否超过限流"""
        keys = self._get_keys(user_id, ip)
        
        # 检查各层级限制
        checks = {
            'user_minute': (keys['user_minute'], self.limits['per_minute']),
            'user_hour': (keys['user_hour'], self.limits['per_hour']),
            'user_day': (keys['user_day'], self.limits['per_day']),
            'user_month': (keys['user_month'], self.limits['per_month']),
            'ip_minute': (keys['ip_minute'], self.limits['per_minute']),
            'global_minute': (keys['global_minute'], self.limits['global_per_minute']),
        }
        
        for name, (key, limit) in checks.items():
            current = self.redis.get(key)
            if current and int(current) >= limit:
                return {
                    'allowed': False,
                    'reason': f'{name} limit exceeded',
                    'limit': limit,
                    'current': int(current)
                }
        
        return {'allowed': True}
    
    def increment_usage(self, user_id: str, ip: str, tokens: int):
        """增加使用计数"""
        keys = self._get_keys(user_id, ip)
        
        pipe = self.redis.pipeline()
        for key in keys.values():
            pipe.incr(key)
            # 设置过期时间
            if 'minute' in key:
                pipe.expire(key, 60)
            elif 'hour' in key:
                pipe.expire(key, 3600)
            elif 'day' in key:
                pipe.expire(key, 86400)
            elif 'month' in key:
                pipe.expire(key, 86400 * 30)
        
        pipe.execute()
        
        # 记录 token 消耗
        today = time.strftime('%Y-%m-%d')
        self.redis.incrby(f"tokens:{user_id}:{today}", tokens)
    
    def check_token_quota(self, user_id: str, tier: str) -> Dict:
        """检查 token 配额"""
        today = time.strftime('%Y-%m-%d')
        key = f"tokens:{user_id}:{today}"
        
        used = int(self.redis.get(key) or 0)
        quota = self.token_quotas.get(tier, self.token_quotas['free'])
        
        return {
            'used': used,
            'quota': quota,
            'remaining': quota - used,
            'exceeded': used >= quota
        }
    
    def get_usage_stats(self, user_id: str) -> Dict:
        """获取使用统计"""
        today = time.strftime('%Y-%m-%d')
        this_month = time.strftime('%Y-%m')
        
        today_key = f"tokens:{user_id}:{today}"
        month_key = f"tokens:{user_id}:{this_month}"
        
        return {
            'today': int(self.redis.get(today_key) or 0),
            'this_month': int(self.redis.get(month_key) or 0)
        }


# FastAPI 集成
app = FastAPI()
protection = CostAbuseProtection()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """速率限制中间件"""
    
    # 获取用户标识
    user_id = request.headers.get("X-User-ID", "anonymous")
    ip = request.client.host
    
    # 检查限流
    check = protection.check_rate_limit(user_id, ip)
    
    if not check['allowed']:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "reason": check['reason'],
                "limit": check['limit'],
                "current": check['current']
            }
        )
    
    response = await call_next(request)
    
    # 增加使用计数
    tokens = response.headers.get("X-Tokens-Used", 0)
    if tokens:
        protection.increment_usage(user_id, ip, int(tokens))
    
    return response

@app.post("/chat")
async def chat(message: str, user_id: str):
    """聊天接口"""
    
    # 检查配额
    quota_check = protection.check_token_quota(user_id, 'free')
    if quota_check['exceeded']:
        raise HTTPException(
            status_code=403,
            detail="Token quota exceeded"
        )
    
    # 调用 AI（模拟）
    response = f"Response to: {message}"
    tokens_used = len(message.split()) * 2
    
    return {
        "response": response,
        "tokens_used": tokens_used,
        "quota": quota_check
    }

@app.get("/usage/{user_id}")
async def get_usage(user_id: str):
    """获取使用统计"""
    return protection.get_usage_stats(user_id)
```

3. 成本监控告警
```python
import smtplib
from email.mime.text import MIMEText
from typing import Optional

class CostMonitor:
    """成本监控告警"""
    
    def __init__(self, redis_client, alert_config: dict):
        self.redis = redis_client
        self.alert_config = alert_config
        self.thresholds = {
            'hourly': 50,    # 每小时 $50
            'daily': 500,    # 每天 $500
            'monthly': 5000  # 每月 $5000
        }
    
    def estimate_cost(self, tokens: int, model: str = 'gpt-4') -> float:
        """估算成本"""
        # GPT-4 定价（示例）
        pricing = {
            'gpt-4': 0.03 / 1000,      # $0.03 per 1K tokens
            'gpt-4-turbo': 0.01 / 1000,
            'gpt-3.5-turbo': 0.0015 / 1000
        }
        
        return tokens * pricing.get(model, 0.01 / 1000)
    
    def check_thresholds(self) -> Dict:
        """检查阈值"""
        now = time.time()
        
        # 获取各时间段用量
        hour_key = f"cost:global:hour:{int(now / 3600)}"
        day_key = f"cost:global:day:{int(now / 86400)}"
        month_key = f"cost:global:month:{int(now / (86400 * 30))}"
        
        hourly_cost = float(self.redis.get(hour_key) or 0)
        daily_cost = float(self.redis.get(day_key) or 0)
        monthly_cost = float(self.redis.get(month_key) or 0)
        
        alerts = []
        
        if hourly_cost > self.thresholds['hourly']:
            alerts.append({
                'type': 'hourly_exceeded',
                'value': hourly_cost,
                'threshold': self.thresholds['hourly']
            })
        
        if daily_cost > self.thresholds['daily']:
            alerts.append({
                'type': 'daily_exceeded',
                'value': daily_cost,
                'threshold': self.thresholds['daily']
            })
        
        if monthly_cost > self.thresholds['monthly']:
            alerts.append({
                'type': 'monthly_exceeded',
                'value': monthly_cost,
                'threshold': self.thresholds['monthly']
            })
        
        return {
            'costs': {
                'hourly': hourly_cost,
                'daily': daily_cost,
                'monthly': monthly_cost
            },
            'alerts': alerts
        }
    
    def send_alert(self, alert: Dict):
        """发送告警"""
        if not self.alert_config.get('email'):
            return
        
        msg = MIMEText(f"""
        成本告警：{alert['type']}
        当前值：${alert['value']:.2f}
        阈值：${alert['threshold']:.2f}
        
        请立即检查！
        """)
        
        msg['Subject'] = f"[紧急] AI API 成本告警"
        msg['From'] = self.alert_config['email']['from']
        msg['To'] = self.alert_config['email']['to']
        
        with smtplib.SMTP(
            self.alert_config['email']['smtp'],
            self.alert_config['email']['port']
        ) as server:
            server.send_message(msg)
    
    def record_cost(self, tokens: int, model: str):
        """记录成本"""
        cost = self.estimate_cost(tokens, model)
        now = time.time()
        
        # 累加到各时间段
        hour_key = f"cost:global:hour:{int(now / 3600)}"
        day_key = f"cost:global:day:{int(now / 86400)}"
        month_key = f"cost:global:month:{int(now / (86400 * 30))}"
        
        pipe = self.redis.pipeline()
        for key in [hour_key, day_key, month_key]:
            pipe.incrbyfloat(key, cost)
        
        pipe.execute()
        
        # 检查阈值
        status = self.check_thresholds()
        for alert in status['alerts']:
            self.send_alert(alert)
        
        return cost
```

**局限性**: 
- 需要自建 Redis
- 无法防止分布式攻击
- 告警有延迟

#### 方案B：低成本方案（$20-50/月）

**工具/服务**: Upstash Redis + Cloudflare Workers

**配置步骤**:

1. 使用 Upstash Rate Limit
```typescript
// Cloudflare Worker
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis/cloudflare";

export default {
  async fetch(request: Request, env: Env) {
    // 初始化限流器
    const redis = new Redis({
      url: env.UPSTASH_REDIS_REST_URL,
      token: env.UPSTASH_REDIS_REST_TOKEN,
    });

    const ratelimit = new Ratelimit({
      redis: redis,
      limiter: Ratelimit.slidingWindow(100, "1 h"),  // 每小时 100 次
      analytics: true,
      prefix: "ratelimit",
    });

    // 获取用户标识
    const ip = request.headers.get("CF-Connecting-IP") || "anonymous";
    const userId = request.headers.get("X-User-ID") || ip;

    // 检查限流
    const { success, limit, reset, remaining } = await ratelimit.limit(userId);

    if (!success) {
      return new Response(
        JSON.stringify({
          error: "Rate limit exceeded",
          limit,
          reset,
          remaining,
        }),
        {
          status: 429,
          headers: { "Content-Type": "application/json" },
        }
      );
    }

    // 转发到后端 API
    const response = await fetch(request);
    
    // 添加限流头
    const newResponse = new Response(response.body, response);
    newResponse.headers.set("X-RateLimit-Limit", limit.toString());
    newResponse.headers.set("X-RateLimit-Remaining", remaining.toString());
    newResponse.headers.set("X-RateLimit-Reset", reset.toString());

    return newResponse;
  },
};
```

2. OpenAI API 预算控制
```python
import openai

# 设置组织预算上限（OpenAI Dashboard）
# Settings -> Billing -> Monthly budget limit

# 使用 API 监控用量
def monitor_openai_usage():
    """监控 OpenAI 用量"""
    # 获取本月使用量
    usage = openai.Organization.retrieve()
    
    return {
        'total_spent': usage.usage.total_spent,
        'soft_limit': usage.soft_limit,
        'hard_limit': usage.hard_limit,
        'percentage': usage.usage.total_spent / usage.soft_limit * 100
    }
```

3. 成本优化策略
```python
class CostOptimizer:
    """成本优化器"""
    
    def __init__(self):
        self.model_tiers = {
            'simple': 'gpt-3.5-turbo',    # 简单任务用便宜模型
            'medium': 'gpt-4-turbo',       # 中等任务
            'complex': 'gpt-4'             # 复杂任务
        }
    
    def select_model(self, task_complexity: str) -> str:
        """根据任务复杂度选择模型"""
        return self.model_tiers.get(task_complexity, 'gpt-3.5-turbo')
    
    def estimate_tokens(self, text: str) -> int:
        """估算 token 数"""
        # 简单估算：英文约 4 字符 = 1 token
        # 中文约 1-2 字符 = 1 token
        return len(text) // 3
    
    def optimize_prompt(self, prompt: str) -> str:
        """优化 Prompt 以减少 tokens"""
        # 移除多余空格
        optimized = ' '.join(prompt.split())
        
        # 移除不必要的重复
        # ...
        
        return optimized
    
    def should_use_cache(self, prompt: str) -> bool:
        """判断是否应该使用缓存"""
        # 相同查询使用缓存
        return len(prompt) > 100  # 长查询更值得缓存
```

**优势**:
- 托管服务，无需维护
- 全球边缘部署
- 自动扩展
- 内置分析面板

### 决策树

```
你的产品是否使用按量付费的 AI API？
├── 否 → 低优先级
└── 是 → 是否有用户级限流？
    ├── 是 → 是否有成本监控？
    │   ├── 是 → 继续优化
    │   └── 否 → 方案A（添加监控）
    └── 否 → 方案A（免费方案）+ 方案B（防护层）
```

### 代码示例

#### 完整防护示例（带成本优化）

```python
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
import redis
import time
from typing import Optional
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class ChatRequest(BaseModel):
    message: str
    user_id: str
    tier: str = 'free'  # free, basic, pro

class CostControl:
    """完整的成本控制系统"""
    
    def __init__(self):
        self.redis = redis.Redis(decode_responses=True)
        
        # 用户配额
        self.quotas = {
            'free': {'daily': 100, 'monthly': 1000},
            'basic': {'daily': 500, 'monthly': 10000},
            'pro': {'daily': 2000, 'monthly': 50000}
        }
        
        # 成本阈值
        self.cost_thresholds = {
            'hourly': 50,
            'daily': 500,
            'monthly': 5000
        }
        
        # 模型定价
        self.model_pricing = {
            'gpt-3.5-turbo': 0.0015,
            'gpt-4-turbo': 0.01,
            'gpt-4': 0.03
        }
    
    def check_user_quota(self, user_id: str, tier: str) -> dict:
        """检查用户配额"""
        today = time.strftime('%Y-%m-%d')
        this_month = time.strftime('%Y-%m')
        
        daily_key = f"usage:{user_id}:{today}"
        monthly_key = f"usage:{user_id}:{this_month}"
        
        daily_used = int(self.redis.get(daily_key) or 0)
        monthly_used = int(self.redis.get(monthly_key) or 0)
        
        quota = self.quotas[tier]
        
        daily_exceeded = daily_used >= quota['daily']
        monthly_exceeded = monthly_used >= quota['monthly']
        
        return {
            'allowed': not (daily_exceeded or monthly_exceeded),
            'daily': {
                'used': daily_used,
                'quota': quota['daily'],
                'remaining': quota['daily'] - daily_used
            },
            'monthly': {
                'used': monthly_used,
                'quota': quota['monthly'],
                'remaining': quota['monthly'] - monthly_used
            }
        }
    
    def check_global_cost(self) -> dict:
        """检查全局成本"""
        now = time.time()
        
        hour_key = f"cost:global:hour:{int(now / 3600)}"
        day_key = f"cost:global:day:{int(now / 86400)}"
        month_key = f"cost:global:month:{int(now / (86400 * 30))}"
        
        costs = {
            'hourly': float(self.redis.get(hour_key) or 0),
            'daily': float(self.redis.get(day_key) or 0),
            'monthly': float(self.redis.get(month_key) or 0)
        }
        
        alerts = []
        for period, threshold in self.cost_thresholds.items():
            if costs[period] >= threshold * 0.8:  # 80% 预警
                alerts.append({
                    'level': 'warning',
                    'period': period,
                    'current': costs[period],
                    'threshold': threshold,
                    'percentage': costs[period] / threshold * 100
                })
            
            if costs[period] >= threshold:  # 100% 超限
                alerts.append({
                    'level': 'critical',
                    'period': period,
                    'current': costs[period],
                    'threshold': threshold
                })
        
        return {'costs': costs, 'alerts': alerts}
    
    def record_usage(self, user_id: str, tokens: int, model: str):
        """记录使用量"""
        today = time.strftime('%Y-%m-%d')
        this_month = time.strftime('%Y-%m')
        
        # 计算成本
        cost = tokens * self.model_pricing.get(model, 0.01) / 1000
        
        # 记录用户使用量
        daily_key = f"usage:{user_id}:{today}"
        monthly_key = f"usage:{user_id}:{this_month}"
        
        pipe = self.redis.pipeline()
        pipe.incr(daily_key)
        pipe.incr(monthly_key)
        pipe.expire(daily_key, 86400 * 2)
        pipe.expire(monthly_key, 86400 * 35)
        
        # 记录全局成本
        now = time.time()
        hour_key = f"cost:global:hour:{int(now / 3600)}"
        day_key = f"cost:global:day:{int(now / 86400)}"
        month_key = f"cost:global:month:{int(now / (86400 * 30))}"
        
        for key in [hour_key, day_key, month_key]:
            pipe.incrbyfloat(key, cost)
        
        pipe.execute()
        
        # 检查告警
        status = self.check_global_cost()
        for alert in status['alerts']:
            if alert['level'] == 'critical':
                self._send_alert(alert)
        
        return {'tokens': tokens, 'cost': cost}
    
    def _send_alert(self, alert: dict):
        """发送告警"""
        logging.critical(f"""
        COST ALERT: {alert['level']}
        Period: {alert['period']}
        Current: ${alert['current']:.2f}
        Threshold: ${alert['threshold']:.2f}
        """)
        
        # 实际项目中发送邮件/短信/Slack
        # self._send_email(alert)
        # self._send_slack(alert)

# 全局实例
cost_control = CostControl()

@app.post("/chat")
async def chat(request: ChatRequest):
    """安全的聊天接口"""
    
    # 1. 检查用户配额
    quota = cost_control.check_user_quota(request.user_id, request.tier)
    
    if not quota['allowed']:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Quota exceeded",
                "quota": quota
            }
        )
    
    # 2. 检查全局成本
    global_status = cost_control.check_global_cost()
    
    if any(a['level'] == 'critical' for a in global_status['alerts']):
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable due to budget limit"
        )
    
    # 3. 选择模型（成本优化）
    complexity = _analyze_complexity(request.message)
    model = _select_model(complexity, request.tier)
    
    # 4. 调用 AI（模拟）
    tokens_used = len(request.message.split()) * 2
    response = f"Response using {model}"
    
    # 5. 记录使用量
    usage = cost_control.record_usage(request.user_id, tokens_used, model)
    
    return {
        "response": response,
        "model": model,
        "tokens_used": tokens_used,
        "cost": usage['cost'],
        "quota": quota
    }

def _analyze_complexity(message: str) -> str:
    """分析任务复杂度"""
    if len(message) < 50:
        return 'simple'
    elif len(message) < 200:
        return 'medium'
    else:
        return 'complex'

def _select_model(complexity: str, tier: str) -> str:
    """选择模型"""
    models = {
        ('simple', 'free'): 'gpt-3.5-turbo',
        ('simple', 'basic'): 'gpt-3.5-turbo',
        ('simple', 'pro'): 'gpt-4-turbo',
        ('medium', 'free'): 'gpt-3.5-turbo',
        ('medium', 'basic'): 'gpt-4-turbo',
        ('medium', 'pro'): 'gpt-4-turbo',
        ('complex', 'free'): 'gpt-3.5-turbo',
        ('complex', 'basic'): 'gpt-4-turbo',
        ('complex', 'pro'): 'gpt-4',
    }
    
    return models.get((complexity, tier), 'gpt-3.5-turbo')

@app.get("/usage/{user_id}")
async def get_usage(user_id: str, tier: str = 'free'):
    """获取使用统计"""
    return cost_control.check_user_quota(user_id, tier)

@app.get("/admin/costs")
async def get_costs():
    """获取成本统计（管理员）"""
    return cost_control.check_global_cost()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## L3 企业版（深耕版）

### 概述
企业级成本控制需要考虑：
- 多租户计费系统
- 成本分摊与归因
- 自动扩缩容
- 预算管理与预测
- 合规审计

### 企业级防护措施

1. **智能预算分配**
   - 部门级预算管理
   - 项目级成本归因
   - 动态预算调整

2. **成本优化引擎**
   - 模型选择自动化
   - 缓存策略优化
   - 批量处理优化

3. **实时监控系统**
   - 全链路成本追踪
   - 异常检测与告警
   - 自动熔断机制

### 参考资料
- [OpenAI Usage API](https://platform.openai.com/docs/guides/usage)
- [AWS Cost Management](https://aws.amazon.com/aws-cost-management/)
- [GCP Cost Management](https://cloud.google.com/cost-management)

---

## 附录：快速自查清单

### 开发阶段
- [ ] 是否有用户级限流？
- [ ] 是否有全局预算控制？
- [ ] API Key 是否安全存储？
- [ ] 是否有成本估算？

### 上线前
- [ ] 是否设置了供应商预算上限？
- [ ] 是否有成本告警机制？
- [ ] 是否测试过限流功能？

### 运营中
- [ ] 是否每日检查成本？
- [ ] 是否定期优化模型选择？
- [ ] 是否有应急预案？

---

## 更新日志

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-06-11 | 1.0 | 初始版本，创建 L1+L2+L3 案例 |
