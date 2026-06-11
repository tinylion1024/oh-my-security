# MongoDB 未授权访问风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $7-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的 MongoDB 数据库因为没有启用认证且暴露在公网，攻击者可以直接连接并窃取、删除或加密勒索你的全部数据，你的产品可能在上线几小时内就彻底瘫痪。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用 MongoDB 作为主数据库
- [ ] MongoDB 部署在云服务器上（非本地开发）
- [ ] **从未创建过管理员账户或启用 `--auth` 模式**
- [ ] **端口 27017 对公网开放**
- [ ] 使用默认配置启动 `mongod`
- [ ] 未配置安全组或防火墙规则
→ 勾选≥2项，尤其是中间两项，**立即行动**

### 一句话防御
立即在云服务商控制台设置安全组，只允许应用服务器 IP 访问 27017 端口，并在 MongoDB 中创建管理员账户后启用认证模式。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查暴露状态**：
   ```bash
   # 从本地电脑执行
   mongo mongodb://你的服务器IP:27017 --eval "db.version()"
   # 如果返回版本号且未要求密码 = 已暴露
   
   # 或使用 mongosh
   mongosh "mongodb://你的服务器IP:27017"
   ```

2. [ ] **设置防火墙规则**：
   - AWS: EC2 → Security Groups → 入站规则 → 仅允许应用服务器 IP 访问 27017
   - 阿里云: ECS → 安全组 → 配置规则 → 仅允许应用服务器 IP
   - Azure: 虚拟机 → 网络 → 网络安全组 → 入站安全规则

3. [ ] **创建管理员账户并启用认证**：
   ```bash
   # 连接 MongoDB（本地或内网）
   mongo
   
   # 创建管理员
   use admin
   db.createUser({
     user: "admin",
     pwd: "使用密码管理器生成32位强密码",
     roles: ["root"]
   })
   
   # 启用认证模式
   # 编辑 /etc/mongod.conf
   sudo nano /etc/mongod.conf
   
   # 添加/修改
   security:
     authorization: enabled
   
   # 重启 MongoDB
   sudo systemctl restart mongod
   
   # 验证
   mongo -u admin -p --authenticationDatabase admin
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **修改默认端口**：
   ```yaml
   # /etc/mongod.conf
   net:
     port: 27018  # 改为非标准端口
   ```

2. [ ] **绑定内网地址**：
   ```yaml
   # /etc/mongod.conf
   net:
     bindIp: 127.0.0.1,10.0.1.100  # 本地 + 内网 IP
   ```

3. [ ] **创建应用专用账户**：
   ```bash
   use admin
   db.createUser({
     user: "app_user",
     pwd: "应用专用强密码",
     roles: [
       { role: "readWrite", db: "your_database" }
     ]
   })
   ```

4. [ ] **启用日志审计**：
   ```yaml
   # /etc/mongod.conf
   auditLog:
     destination: file
     path: /var/log/mongodb/audit.log
     format: JSON
   ```

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **迁移到 MongoDB Atlas**：免费层 512MB，默认安全配置
2. [ ] **启用 TLS 加密**：传输层加密
3. [ ] **启用字段级加密**：敏感数据加密存储
4. [ ] **定期备份 + 异地存储**：防勒索

### MongoDB 安全配置清单

```yaml
# /etc/mongod.conf 完整安全配置

# 网络
net:
  port: 27018  # 非标准端口
  bindIp: 127.0.0.1,10.0.1.100  # 本地 + 内网

# 认证授权
security:
  authorization: enabled
  # 如需副本集，添加 keyFile
  # keyFile: /etc/mongodb/keyfile

# 日志
systemLog:
  destination: file
  path: "/var/log/mongodb/mongod.log"
  logAppend: true
  verbosity: 1

# 审计
auditLog:
  destination: file
  path: /var/log/mongodb/audit.log
  format: JSON
  filter: '{ atype: { $in: [ "authenticate", "createUser", "dropUser", "grantRole" ] } }'

# 存储
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

# 性能分析（慢查询日志）
operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

# 如需副本集
# replication:
#   replSetName: "rs0"
```

### 访问控制实现

**基于角色的访问控制（RBAC）**：

```javascript
// 1. 创建管理员账户
use admin
db.createUser({
  user: "admin",
  pwd: passwordPrompt(),  // 交互式输入密码
  roles: ["root"]
})

// 2. 创建应用读写账户
use your_database
db.createUser({
  user: "app_readwrite",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "your_database" }
  ]
})

// 3. 创建只读账户（用于分析/报表）
use your_database
db.createUser({
  user: "app_readonly",
  pwd: passwordPrompt(),
  roles: [
    { role: "read", db: "your_database" }
  ]
})

// 4. 创建备份专用账户
use admin
db.createUser({
  user: "backup_user",
  pwd: passwordPrompt(),
  roles: [
    { role: "backup", db: "admin" },
    { role: "clusterMonitor", db: "admin" }
  ]
})

// 5. 内置角色说明
// - root: 超级管理员
// - readWriteAnyDatabase: 读写所有数据库
// - readAnyDatabase: 只读所有数据库
// - userAdminAnyDatabase: 管理所有用户
// - dbAdminAnyDatabase: 管理所有数据库
```

**连接字符串格式**：

```bash
# 标准连接字符串
mongodb://username:password@host:port/database?authSource=admin

# 示例
mongodb://app_user:密码@10.0.1.100:27018/production?authSource=admin

# DNS Seedlist（Atlas 推荐）
mongodb+srv://username:password@cluster.mongodb.net/database

# 多节点副本集
mongodb://user:pass@host1:27018,host2:27018,host3:27018/db?replicaSet=rs0&authSource=admin
```

### 推荐工具
- **免费**：
  - [MongoDB Compass](https://www.mongodb.com/products/compass) - 官方 GUI 管理
  - [Shodan](https://www.shodan.io/) - 搜索 `port:27017 product:MongoDB` 检查暴露
  - [MongoDB Atlas Free Tier](https://www.mongodb.com/atlas/database) - 512MB 免费托管

- **低成本**：
  - [MongoDB Atlas](https://www.mongodb.com/atlas/pricing) - $7/月起，自动安全配置
  - [MongoDB Atlas Serverless](https://www.mongodb.com/atlas/serverless) - 按使用付费
  - [ObjectRocket](https://www.objectrocket.com/) - $30/月起，托管 MongoDB

### 验证方法
- [ ] **外部验证**：`mongo mongodb://你的IP:27018` 应该超时或拒绝连接
- [ ] **Shodan 检查**：搜索你的 IP，MongoDB 端口不应显示
- [ ] **无密码测试**：`mongo --host localhost --port 27018` 应返回认证错误
- [ ] **有密码测试**：`mongo -u admin -p --authenticationDatabase admin` 应成功连接

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2019年，一位独立开发者上线了一个 SaaS MVP，使用 MongoDB 存储用户数据。为了"方便开发"，他在 AWS EC2 上部署了 MongoDB，**没有设置密码，安全组规则允许全网访问**。

产品上线后 3 小时：
1. 攻击者通过 Shodan 发现暴露的 MongoDB
2. 直接连接，导出 20 万条用户数据（邮箱、密码哈希、手机号）
3. 数据在暗网出售，价格 $500
4. 删除原数据库，留下勒索信息要求支付 0.1 BTC

**后果**：
- 20 万用户数据泄露
- GDPR 调查，罚款 €15,000
- 产品被迫下线
- 品牌声誉严重受损

**类似案例统计**：
- 2017年，全球 28,000+ MongoDB 实例被勒索
- 2020年，平均每小时有 30+ 个新暴露的 MongoDB 被攻击
- 2022年，某创业公司 MongoDB 被清空，无备份，公司倒闭

### 攻击路径（简化版）

```
1. 扫描发现目标
   ├── Shodan: port:27017 product:MongoDB country:CN
   ├── Masscan: 快速扫描全网 27017 端口
   └── ZoomEye/Censys: 其他扫描引擎
   
2. 验证无认证
   ├── mongo --host 目标IP:27017
   ├── 返回 > 说明无需认证
   └── 或执行 db.version() 获取版本
   
3. 探测数据价值
   ├── show dbs  # 列出数据库
   ├── use target_db
   ├── show collections  # 列出集合
   └── db.users.findOne()  # 查看数据结构
   
4. 批量导出数据
   ├── mongodump --host 目标IP --db target_db --out ./stolen
   ├── 或脚本批量导出
   └── 压缩后上传到云存储
   
5. 清除或勒索
   ├── 方式A: db.dropDatabase() 后插入勒索信息
   ├── 方式B: 删除敏感字段，保留结构
   └── 方式C: 加密数据，索要赎金
   
攻击者自动化脚本示例：
for ip in $(shodan scan --query "port:27017"); do
  mongo --host $ip --eval "db.dropDatabase(); db.warning.insert({msg:'Send 0.1 BTC to recover'})"
done
```

**关键数据**：
- 平均发现到攻击时间：< 30 分钟
- 自动化脚本可每分钟扫描 1000+ IP
- 勒索金额：0.1-1 BTC（$5000-50000）
- 数据暗网售价：$0.01-1/条（取决于数据类型）

### 防御实施（低成本方案）

#### 方案A：免费方案（DIY 配置）

**第一步：创建管理员账户**

```bash
#!/bin/bash
# mongodb-create-admin.sh

set -e

echo "=== 创建 MongoDB 管理员账户 ==="

# 检查 MongoDB 是否运行
if ! pgrep -x mongod > /dev/null; then
    echo "MongoDB 未运行，请先启动"
    exit 1
fi

# 连接 MongoDB
mongo admin --eval '
var password = "'$(openssl rand -base64 32)'";
db.createUser({
  user: "admin",
  pwd: password,
  roles: ["root"]
});
print("管理员密码: " + password);
print("⚠️  请立即保存到密码管理器！");
'
```

**第二步：启用认证模式**

```bash
#!/bin/bash
# mongodb-enable-auth.sh

MONGO_CONF="${MONGO_CONF:-/etc/mongod.conf}"

echo "=== 启用 MongoDB 认证 ==="

# 备份原配置
sudo cp $MONGO_CONF ${MONGO_CONF}.backup.$(date +%Y%m%d)

# 检查是否已有 security 配置
if grep -q "^security:" $MONGO_CONF; then
    # 修改现有配置
    sudo sed -i '/^security:/,/^[^ ]/ s/authorization: disabled/authorization: enabled/' $MONGO_CONF
else
    # 添加新配置
    echo -e "\nsecurity:\n  authorization: enabled" | sudo tee -a $MONGO_CONF > /dev/null
fi

echo "✓ 认证配置已添加"

# 重启 MongoDB
echo "重启 MongoDB..."
sudo systemctl restart mongod

# 等待启动
sleep 5

# 验证
echo "验证配置..."
if mongo --eval "db.version()" 2>&1 | grep -q "Authentication failed"; then
    echo "✓ 无认证访问被拒绝（正确）"
else
    echo "✗ 无认证访问未被拒绝（错误）"
    exit 1
fi

echo "✓ 配置完成"
```

**第三步：配置防火墙**

```bash
#!/bin/bash
# mongodb-firewall.sh

MONGO_PORT="${MONGO_PORT:-27018}"
APP_SERVER_IP="${APP_SERVER_IP:-10.0.1.100}"

echo "=== 配置 MongoDB 防火墙 ==="

# 检查是否使用 UFW
if command -v ufw &> /dev/null; then
    echo "使用 UFW 配置..."
    sudo ufw deny $MONGO_PORT
    sudo ufw allow from $APP_SERVER_IP to any port $MONGO_PORT proto tcp
    echo "✓ UFW 规则已配置"
    exit 0
fi

# 使用 iptables
echo "使用 iptables 配置..."

# 允许本地
iptables -A INPUT -i lo -j ACCEPT

# 允许已建立连接
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许 SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 只允许应用服务器访问 MongoDB
iptables -A INPUT -p tcp -s $APP_SERVER_IP --dport $MONGO_PORT -j ACCEPT

# 拒绝其他 MongoDB 访问
iptables -A INPUT -p tcp --dport $MONGO_PORT -j DROP

# 保存规则
if command -v iptables-save &> /dev/null; then
    sudo iptables-save > /etc/iptables/rules.v4
fi

echo "✓ 防火墙规则已配置"
echo "  只允许 $APP_SERVER_IP 访问 MongoDB 端口 $MONGO_PORT"
```

**第四步：创建应用专用账户**

```javascript
// create-app-user.js
// 用途：创建不同权限的应用账户

// 切换到目标数据库
use production_db

// 读写账户（应用主账户）
db.createUser({
  user: "app_readwrite",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "production_db" }
  ],
  passwordDigestor: "server"
})

// 只读账户（报表/分析）
db.createUser({
  user: "app_readonly",
  pwd: passwordPrompt(),
  roles: [
    { role: "read", db: "production_db" }
  ]
})

// 后台任务账户（需要创建索引等管理操作）
db.createUser({
  user: "app_admin",
  pwd: passwordPrompt(),
  roles: [
    { role: "readWrite", db: "production_db" },
    { role: "dbAdmin", db: "production_db" }
  ]
})

print("✓ 应用账户已创建")
print("连接字符串示例:")
print("  mongodb://app_readwrite:密码@host:27018/production_db?authSource=admin")
```

#### 方案B：低成本方案（MongoDB Atlas）

**配置步骤**：

```bash
# 1. 注册 MongoDB Atlas
#    https://www.mongodb.com/cloud/atlas/register

# 2. 创建免费集群（Free Tier）
#    - 选择云服务商（AWS/GCP/Azure）
#    - 选择区域（建议靠近应用服务器）
#    - 集群名称：my-cluster

# 3. 配置网络访问（IP 白名单）
#    Atlas 控制台 → Network Access → Add IP Address
#    - 添加应用服务器 IP
#    - 或添加团队 IP（开发调试用）

# 4. 创建数据库用户
#    Atlas 控制台 → Database Access → Add New Database User
#    - Authentication Method: Password
#    - Username: app_user
#    - Password: 自动生成或自定义
#    - Database User Privileges: Read and write to any database

# 5. 获取连接字符串
#    Atlas 控制台 → Database → Connect → Connect your application
#    mongodb+srv://app_user:<password>@my-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority

# 6. 配置环境变量
# export MONGODB_URI="mongodb+srv://app_user:密码@my-cluster.xxxxx.mongodb.net/production"
```

**Atlas 安全特性（默认启用）**：
- ✓ 认证（SCRAM 或 x.509）
- ✓ TLS/SSL 加密传输
- ✓ 静态数据加密（WiredTiger Encryption）
- ✓ IP 白名单
- ✓ VPC 对等连接（付费）
- ✓ 审计日志（付费）
- ✓ 自动备份
- ✓ 持续监控

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (Atlas Free) | 方案B (Atlas Shared) |
|------|------------|-------------------|---------------------|
| 月成本 | $0 | $0 | $7-50 |
| 存储空间 | 无限 | 512MB | 2-5GB |
| 配置时间 | 2-4 小时 | 15 分钟 | 15 分钟 |
| 维护时间 | 2 小时/月 | 0 | 0 |
| 安全等级 | 依赖配置 | 默认安全 | 默认安全 |
| TLS 加密 | 需配置 | 自动 | 自动 |
| 备份 | 需自建 | 手动快照 | 自动每日 |
| 监控 | 需自建 | 基础 | 完整 |

### 决策树

```
你的产品阶段？
├── MVP/原型
│   ├── 预算 = $0 → Atlas Free Tier 或 DIY
│   └── 预算 > $0 → Atlas Shared ($7/月)
│
├── 已有付费用户
│   ├── 数据 < 5GB → Atlas Shared ($7-50/月)
│   ├── 数据 5-100GB → Atlas Dedicated ($150+/月)
│   └── 数据 > 100GB → Atlas Dedicated 或自建集群
│
└── 合规要求
    ├── GDPR/HIPAA → Atlas Dedicated（企业级安全）
    └── 无特殊要求 → Atlas Shared
```

### 代码示例

#### 安全的 MongoDB 连接管理（Node.js + Mongoose）

```typescript
// lib/mongodb.ts
import mongoose, { Connection } from 'mongoose'

interface MongoDBConfig {
  uri: string
  dbName: string
  user?: string
  password?: string
  maxPoolSize?: number
  minPoolSize?: number
}

class MongoDBManager {
  private connection: Connection | null = null
  private reconnectAttempts = 0
  private readonly maxReconnectAttempts = 10

  async connect(config: MongoDBConfig): Promise<Connection> {
    const {
      uri,
      dbName,
      user,
      password,
      maxPoolSize = 10,
      minPoolSize = 2
    } = config

    // 验证必需配置
    if (!uri) {
      throw new Error('MongoDB URI 未配置')
    }

    // 构建连接选项
    const options: mongoose.ConnectOptions = {
      dbName,
      maxPoolSize,
      minPoolSize,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
      heartbeatFrequencyMS: 10000,
      retryWrites: true,
      retryReads: true
    }

    // 如果提供认证信息
    if (user && password) {
      options.auth = { username: user, password }
      options.authSource = 'admin'
    }

    try {
      const mongooseConnection = await mongoose.connect(uri, options)
      this.connection = mongooseConnection.connection
      this.reconnectAttempts = 0

      // 监听连接事件
      this.setupEventHandlers()

      console.log('✓ MongoDB 连接成功')
      return this.connection
    } catch (error) {
      console.error('✗ MongoDB 连接失败:', error)
      throw error
    }
  }

  private setupEventHandlers() {
    if (!this.connection) return

    this.connection.on('connected', () => {
      console.log('✓ MongoDB 已连接')
      this.reconnectAttempts = 0
    })

    this.connection.on('disconnected', () => {
      console.warn('⚠️  MongoDB 连接断开')
      this.handleDisconnect()
    })

    this.connection.on('error', (err) => {
      console.error('MongoDB 错误:', err)
      this.notifyError(err)
    })

    this.connection.on('reconnected', () => {
      console.log('✓ MongoDB 重连成功')
    })
  }

  private async handleDisconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('MongoDB 重连失败次数过多，停止重试')
      this.notifyError(new Error('MongoDB connection failed after max reconnection attempts'))
      return
    }

    this.reconnectAttempts++
    const delay = Math.min(this.reconnectAttempts * 1000, 5000)

    console.log(`${delay}ms 后尝试重连... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)

    setTimeout(() => {
      this.connect({
        uri: process.env.MONGODB_URI!,
        dbName: process.env.MONGODB_DB_NAME!
      }).catch(console.error)
    }, delay)
  }

  private notifyError(error: Error) {
    // 集成监控系统（Sentry/Slack 等）
    if (process.env.SLACK_WEBHOOK) {
      fetch(process.env.SLACK_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `🚨 MongoDB 错误: ${error.message}`,
          channel: '#alerts'
        })
      }).catch(console.error)
    }
  }

  async disconnect() {
    if (this.connection) {
      await mongoose.disconnect()
      this.connection = null
      console.log('✓ MongoDB 连接已关闭')
    }
  }

  // 健康检查
  async healthCheck(): Promise<{ status: string; latency?: number }> {
    if (!this.connection) {
      return { status: 'disconnected' }
    }

    try {
      const start = Date.now()
      await this.connection.db.admin().ping()
      const latency = Date.now() - start

      return {
        status: 'healthy',
        latency
      }
    } catch (error) {
      return { status: 'unhealthy' }
    }
  }
}

// 单例
const mongoDBManager = new MongoDBManager()

export default mongoDBManager
```

#### 数据访问层示例

```typescript
// models/User.ts
import mongoose, { Schema, Document, Model } from 'mongoose'
import bcrypt from 'bcryptjs'

// 用户接口
export interface IUser extends Document {
  email: string
  passwordHash: string
  name: string
  role: 'user' | 'admin'
  createdAt: Date
  updatedAt: Date
  comparePassword(password: string): Promise<boolean>
}

// 用户 Schema
const UserSchema = new Schema<IUser>(
  {
    email: {
      type: String,
      required: true,
      unique: true,
      lowercase: true,
      trim: true,
      index: true
    },
    passwordHash: {
      type: String,
      required: true,
      select: false  // 默认不返回
    },
    name: {
      type: String,
      required: true,
      trim: true
    },
    role: {
      type: String,
      enum: ['user', 'admin'],
      default: 'user'
    }
  },
  {
    timestamps: true,
    collection: 'users'
  }
)

// 密码比对方法
UserSchema.methods.comparePassword = async function(password: string): Promise<boolean> {
  return bcrypt.compare(password, this.passwordHash)
}

// 保存前加密密码
UserSchema.pre('save', async function(next) {
  if (!this.isModified('passwordHash')) return next()

  try {
    const salt = await bcrypt.genSalt(12)
    this.passwordHash = await bcrypt.hash(this.passwordHash, salt)
    next()
  } catch (error) {
    next(error as Error)
  }
})

// 索引
UserSchema.index({ email: 1 }, { unique: true })
UserSchema.index({ createdAt: -1 })

// 静态方法：安全查询
UserSchema.statics.findByEmail = async function(email: string) {
  return this.findOne({ email: email.toLowerCase() }).select('+passwordHash')
}

// 导出模型
export const User = mongoose.model<IUser, Model<IUser> & {
  findByEmail(email: string): Promise<IUser | null>
}>('User', UserSchema)
```

#### 备份脚本

```bash
#!/bin/bash
# mongodb-backup.sh
# 用途：自动备份 MongoDB 数据库

set -e

# 配置
MONGO_HOST="${MONGO_HOST:-localhost}"
MONGO_PORT="${MONGO_PORT:-27018}"
MONGO_USER="${MONGO_USER:-backup_user}"
MONGO_PASSWORD="${MONGO_PASSWORD:-}"
MONGO_DB="${MONGO_DB:-production}"
BACKUP_DIR="${BACKUP_DIR:-/backup/mongodb}"
S3_BUCKET="${S3_BUCKET:-your-backup-bucket}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# 创建备份目录
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"
mkdir -p $BACKUP_PATH

echo "=== MongoDB 备份开始 ==="
echo "时间: $(date)"
echo "数据库: $MONGO_DB"

# 执行备份
echo "正在备份..."
mongodump \
  --host $MONGO_HOST \
  --port $MONGO_PORT \
  --username $MONGO_USER \
  --password "$MONGO_PASSWORD" \
  --authenticationDatabase admin \
  --db $MONGO_DB \
  --out $BACKUP_PATH \
  --gzip

# 计算大小
BACKUP_SIZE=$(du -sh $BACKUP_PATH | cut -f1)
echo "✓ 备份完成，大小: $BACKUP_SIZE"

# 上传到 S3
if command -v aws &> /dev/null; then
    echo "上传到 S3..."
    aws s3 sync $BACKUP_PATH s3://$S3_BUCKET/mongodb/$DATE/ --storage-class STANDARD_IA
    echo "✓ 上传完成"
fi

# 清理旧备份
echo "清理 $RETENTION_DAYS 天前的旧备份..."
find $BACKUP_DIR -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \; 2>/dev/null || true

# 清理 S3 旧备份
if command -v aws &> /dev/null; then
    aws s3 ls s3://$S3_BUCKET/mongodb/ | while read -r line; do
        folder_date=$(echo $line | awk '{print $2}' | tr -d '/')
        if [[ $folder_date < $(date -d "-$RETENTION_DAYS days" +%Y%m%d) ]]; then
            aws s3 rm s3://$S3_BUCKET/mongodb/$folder_date --recursive
        fi
    done
fi

echo "✓ 备份流程完成"
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业 MongoDB 安全案例集](../../enterprise/infosec/mongodb-security-enterprise.md)
- [MongoDB 安全最佳实践](../../enterprise/infosec/mongodb-security-best-practices.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 认证 | 单一密码 | LDAP/AD 集成 + MFA |
| 加密 | 传输加密（可选） | 传输 + 静态 + 字段级加密 |
| 审计 | 基础日志 | 完整审计 + SIEM 集成 |
| 高可用 | 单节点 | 副本集 + 分片 + 跨区域 |
| 备份 | 手动快照 | 持续备份 + RPO/RTO SLA |
| 合规 | 无 | SOC2/PCI-DSS/HIPAA/GDPR |

---

## 附录：常见问题

**Q: MongoDB Atlas 免费层够用吗？**

A: 取决于你的场景：
- ✓ MVP/原型/个人项目：足够
- ✓ 用户 < 1000：足够
- ✗ 需要 7x24 运行的生产应用：建议升级 Shared Tier
- ✗ 数据 > 512MB：需要升级

**Q: 如何检查 MongoDB 是否已被攻击？**

A: 执行以下检查：
```javascript
// 检查未知用户
use admin
db.system.users.find()

// 检查最近操作
db.adminCommand({ getLog: "global" })

// 检查数据完整性
use your_database
db.users.count()  // 对比预期数量
db.users.find({ email: { $regex: /^[^@]+$/ } })  // 检查异常邮箱

// 检查审计日志（如果启用）
db.adminCommand({ getAuditLog: 1 })
```

**Q: 如何实现字段级加密？**

A: MongoDB 4.2+ 支持客户端字段级加密（CSFLE）：
```javascript
const { ClientEncryption } = require('mongodb-client-encryption')

// 创建加密客户端
const encryption = new ClientEncryption(mongoClient, {
  keyVaultNamespace: 'encryption.__keyVault',
  kmsProviders: {
    local: {
      key: Buffer.from(process.env.ENCRYPTION_KEY, 'base64')
    }
  }
})

// 加密敏感字段
const encryptedData = await encryption.encrypt(
  sensitiveData,
  {
    keyId: keyId,
    algorithm: 'AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic'
  }
)
```

**Q: 自建 MongoDB vs Atlas 如何选择？**

A:
- 自建优势：成本可控、数据完全自主、定制化
- 自建劣势：运维成本高、安全依赖配置、无自动备份
- Atlas 优势：默认安全、自动运维、一键扩容
- Atlas 劣势：成本随数据增长、数据在云上

建议：
- 数据 < 100GB 且团队 < 5 人 → Atlas
- 数据 > 100GB 或有合规要求 → 评估自建
- 无运维经验 → Atlas

---

## 参考资源

- [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
- [MongoDB Authentication](https://www.mongodb.com/docs/manual/core/authentication/)
- [MongoDB Role-Based Access Control](https://www.mongodb.com/docs/manual/core/authorization/)
- [MongoDB Atlas Security](https://www.mongodb.com/docs/atlas/security/)
- [OWASP Database Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html)
- [Shodan MongoDB Scanner](https://www.shodan.io/search?query=port%3A27017+product%3AMongoDB)
