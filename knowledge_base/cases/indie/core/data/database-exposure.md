# 数据库暴露风险

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: data
- **严重程度**: critical
- **修复成本**: L1: 免费 | L2: $20-50/月 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
你的 MongoDB/Redis 数据库因为没有设置密码和防火墙规则，任何人都可以通过公网访问并窃取全部用户数据，你的产品可能在上线第一天就被黑。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 使用 MongoDB、Redis、MySQL、PostgreSQL 等数据库
- [ ] 数据库部署在云服务器上（AWS/Azure/阿里云等）
- [ ] **从未设置过数据库密码**
- [ ] **从未配置过防火墙规则**（只允许应用服务器访问）
- [ ] 使用默认端口（MongoDB 27017、Redis 6379、MySQL 3306）
→ 勾选≥2项，尤其是后两项，**立即行动**

### 一句话防御
在云服务商控制台设置安全组/防火墙规则，**只允许你的应用服务器 IP 访问数据库端口**，并立即为数据库设置强密码。

### 快速行动清单

#### 🔴 立即行动项（今天完成，免费）
1. [ ] **检查暴露状态**：访问 https://www.shodan.io/ 搜索你的服务器 IP，确认数据库端口是否暴露
2. [ ] **设置防火墙规则**：
   - AWS: EC2 → Security Groups → 添加规则：仅允许应用服务器 IP 访问数据库端口
   - 阿里云: ECS → 安全组 → 配置规则：仅允许应用服务器 IP 访问
   - Azure: 虚拟机 → 网络 → 网络安全组 → 入站规则
3. [ ] **设置数据库密码**：
   ```bash
   # MongoDB
   use admin
   db.createUser({user: "admin", pwd: "你的强密码", roles: ["root"]})
   
   # Redis
   # 编辑 redis.conf
   requirepass 你的强密码
   
   # MySQL
   ALTER USER 'root'@'localhost' IDENTIFIED BY '你的强密码';
   ```

#### 🟡 短期行动项（本周完成，免费）
1. [ ] **启用认证**：MongoDB 启用 `--auth` 模式，Redis 启用 `requirepass`
2. [ ] **修改默认端口**：将 MongoDB 改为非 27017 端口，Redis 改为非 6379 端口
3. [ ] **创建备份**：在设置密码前，先备份数据库
4. [ ] **更新应用连接字符串**：在应用代码中添加新的认证信息

#### 🟢 长期行动项（规划中，低成本）
1. [ ] **启用数据库加密**：MongoDB 支持加密存储，Redis Enterprise 支持加密
2. [ ] **使用托管数据库服务**：MongoDB Atlas、AWS RDS 等默认提供安全配置
3. [ ] **定期审计**：每月检查一次安全组规则，确保无新增暴露

### 推荐工具
- **免费**：
  - [Shodan](https://www.shodan.io/) - 免费查询你的服务器暴露情况
  - [MongoDB Atlas Free Tier](https://www.mongodb.com/atlas/database) - 免费托管 MongoDB，默认安全配置
  - 云服务商安全组（AWS/Azure/阿里云）- 免费，但需正确配置
  
- **低成本**：
  - [Upguard](https://www.upguard.com/) - $50/月起，自动监控云服务暴露面
  - [MongoDB Atlas](https://www.mongodb.com/atlas/database) - $0.25/小时起，自动安全配置

### 验证方法
- [ ] **外部验证**：从本地电脑执行 `telnet 你的服务器IP 27017`，应该连接失败或超时
- [ ] **Shodan 检查**：在 Shodan 搜索你的 IP，数据库端口应该不再显示
- [ ] **应用验证**：你的应用仍然可以正常连接数据库（说明防火墙规则正确）
- [ ] **密码验证**：尝试无密码连接数据库，应该被拒绝
  ```bash
  # 测试 MongoDB
  mongo 你的服务器IP:27017 --eval "db.version()"  # 应该返回认证失败
  
  # 测试 Redis
  redis-cli -h 你的服务器IP -p 6379 PING  # 应该返回认证失败
  ```

---

## L2 小团队版（理解版）

### 场景还原

**真实案例**：2019年，一位独立开发者上线了一个 MVP 产品，使用了 MongoDB 数据库存储用户数据。为了方便开发，他将 MongoDB 部署在 AWS EC2 上，**没有设置密码，也没有配置安全组规则**。

产品上线后 3 小时，攻击者通过 Shodan 扫描到该服务器的 27017 端口暴露，直接连接数据库，导出了 20 万条用户数据（邮箱、密码哈希、手机号），并在暗网出售。开发者的产品被迫下线，面临 GDPR 合规调查，最终支付了 €15,000 罚款。

**类似案例**：
- 2020年，某创业公司的 Redis 因未设置密码，被勒索软件加密，需支付 0.1 BTC 赎金
- 2021年，某 SaaS 产品的 Elasticsearch 暴露，导致 1TB 用户日志泄露

### 攻击路径（简化版）

```
1. 攻击者发现目标
   ├── 使用 Shodan 扫描全网暴露的 MongoDB (port:27017)
   ├── 或使用 ZoomEye/Censys 等扫描工具
   └── 筛选出"无认证"的服务器（默认配置的 MongoDB）
   
2. 验证可访问性
   ├── 攻击者直接用 mongo 命令连接
   ├── mongo 目标IP:27017
   └── 成功连接，无需密码
   
3. 探测数据价值
   ├── show dbs  # 列出所有数据库
   ├── use 用户数据库
   ├── show collections  # 列出所有集合
   └── db.users.find().limit(10)  # 预览数据
   
4. 导出数据
   ├── mongodump --host 目标IP --db 用户数据库 --out ./stolen
   ├── 或直接执行 db.users.find().forEach(printjson) 保存结果
   └── 整个过程 < 5 分钟
   
5. 清除痕迹或勒索
   ├── 方式A：删除原数据，留下勒索信息（常见）
   ├── 方式B：悄无声息离开，数据流入暗网
   └── 方式C：加密数据，索要赎金
```

**关键点**：
- 整个攻击过程 **< 10 分钟**
- 攻击者使用 **自动化脚本**，批量扫描数千台服务器
- **无需任何黑客技术**，仅需基础的 MongoDB 命令
- 大部分攻击发生在服务器上线 **24 小时内**

### 防御实施（低成本方案）

#### 方案A：免费方案（DIY 配置）

**工具/服务**：云服务商安全组 + 数据库认证

**配置步骤**：

**第一步：配置防火墙（AWS 安全组示例）**
```bash
# 1. 登录 AWS 控制台
# 2. 进入 EC2 → Security Groups
# 3. 创建新规则：
#    - 类型: Custom TCP
#    - 端口: 27017 (MongoDB)
#    - 源: 仅允许应用服务器的内网 IP
#      例如: 10.0.1.100/32

# 4. 删除或拒绝所有其他来源（0.0.0.0/0）
```

**第二步：启用数据库认证（MongoDB 示例）**
```bash
# 1. 创建管理员账户
mongo
use admin
db.createUser({
  user: "admin",
  pwd: "使用密码管理器生成的32位强密码",
  roles: ["root"]
})

# 2. 启用认证模式
# 编辑 /etc/mongod.conf
security:
  authorization: enabled

# 3. 重启 MongoDB
sudo systemctl restart mongod

# 4. 验证
mongo -u admin -p --authenticationDatabase admin
```

**第三步：修改应用连接字符串**
```javascript
// 原连接字符串
const uri = "mongodb://你的服务器IP:27017/mydb";

// 新连接字符串（带认证）
const uri = "mongodb://admin:密码@你的服务器IP:27017/mydb?authSource=admin";
```

**局限性**：
- 需要手动维护安全组规则
- 团队新增成员时需要手动添加 IP
- 无审计日志，无法知道谁访问了数据库

#### 方案B：低成本方案（<$50/月）

**工具/服务**：MongoDB Atlas（托管服务）

**配置步骤**：

```bash
# 1. 注册 MongoDB Atlas（免费层 + 付费升级）
#    Free Tier: 永久免费（512MB 存储）
#    Shared Tier: $0.25/小时 ≈ $7/月（适合小团队）

# 2. 创建集群时自动配置：
#    ✓ 自动启用认证
#    ✓ 自动配置防火墙（IP 白名单）
#    ✓ 自动加密传输（TLS/SSL）
#    ✓ 自动备份

# 3. 添加 IP 白名单
#    在 Atlas 控制台 → Network Access → Add IP Address
#    添加应用服务器 IP 或团队 IP

# 4. 创建数据库用户
#    Atlas 控制台 → Database Access → Add New Database User
#    生成强密码

# 5. 获取连接字符串
#    Atlas 控制台 → Connect → Connect Your Application
#    自动生成带认证的连接字符串
```

**优势**：
- **零配置安全**：默认启用所有安全措施
- **自动备份**：每日自动备份，支持时间点恢复
- **监控告警**：异常访问自动告警
- **团队管理**：支持多用户权限管理
- **扩展性**：一键扩容，无需运维

**成本对比**：

| 指标 | 方案A (DIY) | 方案B (Atlas) |
|------|------------|--------------|
| 月成本 | $0 | $7-50/月 |
| 配置时间 | 2-4 小时 | 30 分钟 |
| 维护时间 | 2 小时/月 | 0 小时/月 |
| 安全等级 | 依赖配置 | 默认安全 |
| 备份恢复 | 需自建 | 自动 |
| 监控告警 | 需自建 | 内置 |

### 决策树

```
你的产品处于什么阶段？
├── MVP/原型阶段
│   ├── 预算 = $0 → 方案A（DIY）
│   └── 预算 > $0 → 方案B（Atlas Free Tier）
│
├── 已有付费用户
│   ├── 数据量 < 5GB → 方案B（Atlas Shared Tier, $7-50/月）
│   └── 数据量 > 5GB → 方案B（Atlas Dedicated, $150+/月）
│
└── 团队规模
    ├── 1 人 → 方案A 或 方案B Free Tier
    ├── 2-5 人 → 方案B（方便团队协作）
    └── 5+ 人 → 方案B（企业级特性）
```

### 代码示例

#### 完整的 MongoDB 安全配置脚本

```bash
#!/bin/bash
# mongodb-security-setup.sh
# 用途：一键配置 MongoDB 安全措施
# 适用：独立开发者、小团队

set -e

echo "=== MongoDB 安全配置脚本 ==="

# 配置参数
MONGO_PORT="${MONGO_PORT:-27017}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASSWORD=$(openssl rand -base64 32)  # 自动生成32位强密码
ALLOWED_IP="${ALLOWED_IP:-127.0.0.1}"  # 默认只允许本地

echo "步骤 1/5: 创建管理员账户..."
mongo admin --eval "
  db.createUser({
    user: '$ADMIN_USER',
    pwd: '$ADMIN_PASSWORD',
    roles: ['root']
  })
"
echo "✓ 管理员账户已创建"
echo "  用户名: $ADMIN_USER"
echo "  密码: $ADMIN_PASSWORD"
echo "  ⚠️  请妥善保存密码！"

echo "步骤 2/5: 启用认证模式..."
# 备份原配置
sudo cp /etc/mongod.conf /etc/mongod.conf.backup

# 添加认证配置
sudo tee -a /etc/mongod.conf > /dev/null <<EOF

security:
  authorization: enabled
EOF
echo "✓ 认证模式已启用"

echo "步骤 3/5: 配置防火墙 (iptables)..."
# 清除旧规则
sudo iptables -F

# 允许本地回环
sudo iptables -A INPUT -i lo -j ACCEPT

# 允许已建立的连接
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 允许 SSH
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# 只允许特定 IP 访问 MongoDB
sudo iptables -A INPUT -p tcp --dport $MONGO_PORT -s $ALLOWED_IP -j ACCEPT

# 拒绝其他所有 MongoDB 访问
sudo iptables -A INPUT -p tcp --dport $MONGO_PORT -j DROP

# 保存规则
sudo iptables-save > /etc/iptables/rules.v4
echo "✓ 防火墙已配置，只允许 $ALLOWED_IP 访问 MongoDB"

echo "步骤 4/5: 重启 MongoDB..."
sudo systemctl restart mongod
echo "✓ MongoDB 已重启"

echo "步骤 5/5: 验证配置..."
# 测试无密码连接（应该失败）
if mongo --port $MONGO_PORT --eval "db.version()" 2>&1 | grep -q "Authentication failed"; then
  echo "✓ 无密码连接被拒绝（正确）"
else
  echo "✗ 无密码连接成功（错误）"
  exit 1
fi

# 测试有密码连接（应该成功）
if mongo -u $ADMIN_USER -p "$ADMIN_PASSWORD" --authenticationDatabase admin --eval "db.version()" > /dev/null 2>&1; then
  echo "✓ 有密码连接成功（正确）"
else
  echo "✗ 有密码连接失败（错误）"
  exit 1
fi

echo ""
echo "=== 配置完成 ==="
echo "连接字符串: mongodb://$ADMIN_USER:$ADMIN_PASSWORD@localhost:$MONGO_PORT/?authSource=admin"
echo ""
echo "后续步骤："
echo "1. 更新应用连接字符串"
echo "2. 在云服务商控制台配置安全组（推荐）"
echo "3. 定期检查 Shodan 确认无暴露"
```

#### 应用代码示例（Node.js）

```javascript
// config/database.js
// 安全的数据库连接配置

const mongoose = require('mongoose');

class DatabaseManager {
  constructor() {
    this.connection = null;
  }

  async connect() {
    // 从环境变量读取配置（不要硬编码密码）
    const {
      MONGO_USER,
      MONGO_PASSWORD,
      MONGO_HOST,
      MONGO_PORT,
      MONGO_DB,
      MONGO_AUTH_SOURCE = 'admin'
    } = process.env;

    // 验证必需的环境变量
    if (!MONGO_USER || !MONGO_PASSWORD) {
      throw new Error('数据库认证信息缺失，请检查环境变量 MONGO_USER 和 MONGO_PASSWORD');
    }

    // 构建连接字符串
    const uri = `mongodb://${MONGO_USER}:${encodeURIComponent(MONGO_PASSWORD)}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DB}?authSource=${MONGO_AUTH_SOURCE}`;

    try {
      this.connection = await mongoose.connect(uri, {
        useNewUrlParser: true,
        useUnifiedTopology: true,
        serverSelectionTimeoutMS: 5000,  // 5秒超时
        socketTimeoutMS: 45000,  // 45秒 socket 超时
      });

      console.log('✓ 数据库连接成功');
      
      // 监听连接错误
      mongoose.connection.on('error', (err) => {
        console.error('✗ 数据库连接错误:', err);
        // 可以集成到你的监控系统
        this.notifyError(err);
      });

      mongoose.connection.on('disconnected', () => {
        console.warn('⚠️  数据库连接断开');
        // 自动重连逻辑
        this.handleDisconnect();
      });

      return this.connection;
    } catch (error) {
      console.error('✗ 数据库连接失败:', error.message);
      throw error;
    }
  }

  handleDisconnect() {
    // 重连逻辑
    setTimeout(() => {
      console.log('尝试重新连接数据库...');
      this.connect().catch(console.error);
    }, 5000);
  }

  notifyError(error) {
    // 集成到你的监控系统（如 Sentry、LogRocket 等）
    // 示例：发送到 Slack
    if (process.env.SLACK_WEBHOOK) {
      fetch(process.env.SLACK_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: `🚨 数据库错误: ${error.message}`,
          channel: '#alerts'
        })
      }).catch(console.error);
    }
  }

  async disconnect() {
    if (this.connection) {
      await mongoose.disconnect();
      console.log('✓ 数据库连接已关闭');
    }
  }
}

// 单例模式
const db = new DatabaseManager();

module.exports = db;
```

#### Redis 安全配置脚本

```bash
#!/bin/bash
# redis-security-setup.sh
# 用途：一键配置 Redis 安全措施

set -e

echo "=== Redis 安全配置脚本 ==="

# 配置参数
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD=$(openssl rand -base64 32)
ALLOWED_IP="${ALLOWED_IP:-127.0.0.1}"

echo "步骤 1/4: 设置密码..."
# 备份原配置
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# 设置密码
sudo sed -i "s/# requirepass.*/requirepass $REDIS_PASSWORD/" /etc/redis/redis.conf
echo "✓ 密码已设置: $REDIS_PASSWORD"
echo "  ⚠️  请妥善保存密码！"

echo "步骤 2/4: 禁用危险命令..."
# 禁用 FLUSHDB、FLUSHALL、KEYS 等危险命令
sudo tee -a /etc/redis/redis.conf > /dev/null <<EOF

# 安全配置
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command KEYS ""
rename-command CONFIG ""
EOF
echo "✓ 危险命令已禁用"

echo "步骤 3/4: 配置防火墙..."
# 只允许特定 IP 访问 Redis
sudo iptables -A INPUT -p tcp --dport $REDIS_PORT -s $ALLOWED_IP -j ACCEPT
sudo iptables -A INPUT -p tcp --dport $REDIS_PORT -j DROP
sudo iptables-save > /etc/iptables/rules.v4
echo "✓ 防火墙已配置，只允许 $ALLOWED_IP 访问 Redis"

echo "步骤 4/4: 重启 Redis..."
sudo systemctl restart redis
echo "✓ Redis 已重启"

# 验证
echo "验证配置..."
if redis-cli PING 2>&1 | grep -q "NOAUTH"; then
  echo "✓ 无密码访问被拒绝（正确）"
else
  echo "✗ 无密码访问未被拒绝（错误）"
  exit 1
fi

if redis-cli -a "$REDIS_PASSWORD" PING | grep -q "PONG"; then
  echo "✓ 有密码访问成功（正确）"
else
  echo "✗ 有密码访问失败（错误）"
  exit 1
fi

echo ""
echo "=== 配置完成 ==="
echo "连接命令: redis-cli -a $REDIS_PASSWORD"
```

---

## L3 企业版（深耕版）

本案例的企业级版本详见：
- [企业数据安全案例集](../../enterprise/infosec/data-exposure-enterprise.md)
- [数据库安全最佳实践](../../enterprise/infosec/database-security-best-practices.md)

### 企业版关键差异

| 维度 | 独立开发者版 | 企业版 |
|------|------------|--------|
| 合规要求 | 基础保护 | GDPR/SOC2/ISO27001 |
| 监控审计 | 手动检查 | SIEM/SOC 7x24 监控 |
| 应急响应 | 单人处理 | CSIRT 团队 + 预案 |
| 数据加密 | 传输加密 | 传输+存储+备份全链路加密 |
| 访问控制 | 单一账户 | RBAC + MFA + 最小权限 |
| 备份恢复 | 定期备份 | 异地容灾 + RPO/RTO SLA |

### 企业级扩展要点

1. **纵深防御**
   - 网络隔离：VPC + 私有子网 + 安全组
   - 身份认证：LDAP/AD 集成 + MFA
   - 访问控制：RBAC + 属性基访问控制（ABAC）
   - 数据加密：TDE + 列级加密 + 密钥管理（KMS）

2. **持续监控**
   - 异常访问检测：UEBA（用户实体行为分析）
   - 数据泄露检测：DLP（数据防泄漏）
   - 威胁情报集成：TI 平台实时告警

3. **应急响应**
   - 自动化预案：Playbook 自动化执行
   - 取证分析：日志留存 6 个月+，支持溯源
   - 合规报告：自动生成监管报告

---

## 附录：常见问题

**Q: 我使用的是 MongoDB Atlas/Supabase 等托管服务，还需要担心吗？**

A: 托管服务默认提供安全配置，但你需要：
1. 确认已启用认证（大部分默认启用）
2. 配置 IP 白名单（Atlas 称为 Network Access）
3. 使用强密码并定期轮换
4. 启用双因素认证（保护你的云账户）

**Q: 我只在内网使用，是否可以不设置密码？**

A: **强烈不建议**。理由：
1. 内网不代表绝对安全（内部威胁、横向移动攻击）
2. 开发/测试环境可能误连接生产数据库
3. 设置密码成本极低（< 10 分钟），风险成本极高（数据泄露）

**Q: 防火墙规则已经限制 IP，还需要设置密码吗？**

A: **需要**。这是纵深防御原则：
1. 防火墙可能被错误配置
2. 应用服务器被入侵后，攻击者可绕过防火墙
3. 密码是最后一道防线

**Q: 如何检查我的数据库是否已经被攻击？**

A: 立即执行以下检查：
```bash
# MongoDB
mongo -u admin -p --authenticationDatabase admin
use admin
db.system.users.find()  # 检查是否有未知账户
db.adminCommand({getLog: "global"})  # 检查访问日志

# 查看最近连接
db.currentOp({"active": true})

# 检查数据完整性
db.users.count()  # 对比预期用户数量
db.users.find({$where: "this.email.indexOf('@') === -1"})  # 检查异常数据
```

**Q: 发现数据库被攻击后应该怎么做？**

A: 立即执行以下步骤：
1. **切断访问**：立即修改防火墙规则，只允许你的 IP
2. **保留证据**：不要重启服务器，先导出日志
3. **评估损失**：检查数据是否被修改/删除
4. **通知用户**：如果用户数据泄露，依法通知用户
5. **寻求专业帮助**：如果严重，联系专业的应急响应团队

---

## 参考资源

- [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
- [Redis Security](https://redis.io/docs/management/security/)
- [Shodan 搜索技巧](https://www.shodan.io/search/filters)
- [OWASP Database Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html)
- [AWS Security Best Practices for RDS](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.Security.html)
