# 简易 API 网关

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **分类**: 预防
- **实现成本**: 免费
- **实施时间**: 2-4小时
- **维护成本**: 1-2小时/月
- **最后验证日期**: 2026-06-11

## 适用场景
统一 API 入口，实现认证、限流、日志聚合，适用于所有对外暴露的 API 服务，特别是微服务架构或前后端分离应用。

## 网关方案对比

### 快速选型表

| 方案 | 实现复杂度 | 性能 | 适用场景 | 免费方案 | 独立开发者推荐度 |
|------|-----------|------|---------|---------|----------------|
| **Nginx 反向代理** | ⭐ 简单 | ⭐⭐⭐⭐⭐ 极高 | 单服务、简单路由 | ✅ 完全免费 | ⭐⭐⭐⭐⭐ |
| **Traefik** | ⭐⭐ 中等 | ⭐⭐⭐⭐ 高 | Docker/K8s 环境 | ✅ 开源版 | ⭐⭐⭐⭐⭐ |
| **Kong** | ⭐⭐⭐ 复杂 | ⭐⭐⭐⭐ 高 | 微服务、插件生态 | ✅ 开源版 | ⭐⭐⭐⭐ |
| **Express Gateway** | ⭐⭐ 中等 | ⭐⭐⭐ 中等 | Node.js 技术栈 | ✅ 开源 | ⭐⭐⭐ |
| **云网关** | ⭐ 简单 | ⭐⭐⭐⭐⭐ 高 | 无运维需求 | ❌ 按量付费 | ⭐⭐⭐ |

### 详细对比

#### 1. Nginx 反向代理（推荐入门）

**优点**：
- 性能极高，占用资源极低
- 配置简单，学习成本低
- 稳定可靠，广泛使用

**缺点**：
- 动态配置需重启（或使用 OpenResty）
- 高级功能需要编写 Lua 脚本
- 无内置 API 管理界面

**适用场景**：
- 单体应用反向代理
- 简单的负载均衡
- SSL 终结

---

#### 2. Traefik（推荐云原生）

**优点**：
- 自动服务发现（Docker/K8s）
- 内置 Let's Encrypt 证书管理
- 动态配置，无需重启
- Web Dashboard

**缺点**：
- 性能略低于 Nginx
- 配置语法较复杂
- 文档分散

**适用场景**：
- Docker Compose 环境
- Kubernetes 集群
- 微服务架构

---

#### 3. Kong（推荐企业级）

**优点**：
- 插件生态丰富（认证、限流、日志）
- 管理 API 和 Dashboard
- 性能优异（基于 Nginx/OpenResty）
- 支持多协议（HTTP/gRPC/WebSocket）

**缺点**：
- 学习曲线陡峭
- 依赖数据库（或 DB-less 模式）
- 配置较复杂

**适用场景**：
- API 管理平台
- 微服务网关
- 开放 API 平台

---

## 快速上手（5分钟）

### 方案一：Nginx 反向代理（最简单）

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

    # 上游服务
    upstream backend {
        server 127.0.0.1:3000;
        keepalive 32;
    }

    server {
        listen 80;
        server_name api.example.com;

        # 安全头
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API 路由
        location /api/ {
            # 限流
            limit_req zone=api_limit burst=20 nodelay;
            limit_conn conn_limit 10;

            # 代理设置
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # 超时配置
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # 健康检查端点
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }
    }
}
```

**启动**：
```bash
# 测试配置
nginx -t

# 启动服务
nginx

# 重载配置（修改后）
nginx -s reload
```

### 方案二：Traefik（Docker 环境）

```yaml
# docker-compose.yml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"  # Dashboard（生产环境关闭）
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      # Let's Encrypt（可选）
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./letsencrypt:/letsencrypt
    networks:
      - web

  app:
    image: your-app:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`api.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
      - "traefik.http.services.app.loadbalancer.server.port=3000"
      # 限流中间件
      - "traefik.http.middlewares.ratelimit.ratelimit.average=10"
      - "traefik.http.middlewares.ratelimit.ratelimit.burst=20"
      - "traefik.http.routers.app.middlewares=ratelimit"
    networks:
      - web

networks:
  web:
    external: true
```

**启动**：
```bash
# 创建网络
docker network create web

# 启动服务
docker-compose up -d

# 查看状态
docker-compose logs -f traefik
```

### 方案三：Kong（功能最全）

```yaml
# docker-compose.yml
version: '3.8'

services:
  kong-database:
    image: postgres:13
    environment:
      POSTGRES_USER: kong
      POSTGRES_DB: kong
      POSTGRES_PASSWORD: kong
    volumes:
      - kong-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "kong"]
      interval: 10s
      timeout: 5s
      retries: 5

  kong-migration:
    image: kong:3.4
    command: "kong migrations bootstrap"
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_PASSWORD: kong
    depends_on:
      kong-database:
        condition: service_healthy

  kong:
    image: kong:3.4
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: kong-database
      KONG_PG_PASSWORD: kong
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
      KONG_PROXY_ERROR_LOG: /dev/stderr
      KONG_ADMIN_ERROR_LOG: /dev/stderr
      KONG_ADMIN_LISTEN: "0.0.0.0:8001"
      KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
    ports:
      - "8000:8000"   # HTTP
      - "8443:8443"   # HTTPS
      - "8001:8001"   # Admin API
    depends_on:
      - kong-migration
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/status"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  kong-data:
```

**配置服务**：
```bash
# 启动 Kong
docker-compose up -d

# 添加服务
curl -i -X POST http://localhost:8001/services \
  -d "name=my-api" \
  -d "url=http://app:3000"

# 添加路由
curl -i -X POST http://localhost:8001/services/my-api/routes \
  -d "paths[]=/api"

# 添加限流插件
curl -i -X POST http://localhost:8001/services/my-api/plugins \
  -d "name=rate-limiting" \
  -d "config.minute=100" \
  -d "config.policy=local"

# 添加 Key Auth 插件
curl -i -X POST http://localhost:8001/services/my-api/plugins \
  -d "name=key-auth"

# 创建消费者
curl -i -X POST http://localhost:8001/consumers \
  -d "username=user1"

# 创建 API Key
curl -i -X POST http://localhost:8001/consumers/user1/key-auth \
  -d "key=my-api-key-123"
```

---

## 详细方案

### 方案架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端请求                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 网关层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   SSL 终结    │  │   认证鉴权   │  │   限流熔断   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   路由分发    │  │   日志记录   │  │   监控指标   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
         ┌──────────┐    ┌──────────┐    ┌──────────┐
         │ 服务 A    │    │ 服务 B    │    │ 服务 C    │
         │ :3000     │    │ :3001     │    │ :3002     │
         └──────────┘    └──────────┘    └──────────┘
```

### 核心功能实现

#### 1. 统一认证中间件

**Nginx + Lua（OpenResty）**：
```lua
-- auth.lua
local jwt = require "resty.jwt"
local cjson = require "cjson"

local function authenticate()
    local auth_header = ngx.req.get_headers()["Authorization"]
    
    if not auth_header then
        ngx.status = 401
        ngx.say(cjson.encode({error = "Authorization header required"}))
        return ngx.exit(401)
    end
    
    local token = auth_header:match("Bearer%s+(.+)")
    if not token then
        ngx.status = 401
        ngx.say(cjson.encode({error = "Invalid authorization format"}))
        return ngx.exit(401)
    end
    
    -- 验证 JWT
    local jwt_secret = os.getenv("JWT_SECRET") or "your-secret-key"
    local jwt_obj = jwt:verify(jwt_secret, token)
    
    if not jwt_obj.verified then
        ngx.status = 401
        ngx.say(cjson.encode({error = "Invalid token"}))
        return ngx.exit(401)
    end
    
    -- 将用户信息传递给后端
    ngx.req.set_header("X-User-Id", jwt_obj.payload.sub)
    ngx.req.set_header("X-User-Scopes", table.concat(jwt_obj.payload.scopes or {}, ","))
end

authenticate()
```

**Nginx 配置**：
```nginx
location /api/ {
    access_by_lua_file /etc/nginx/lua/auth.lua;
    proxy_pass http://backend;
}
```

#### 2. 限流配置

**Nginx**：
```nginx
# 定义限流区域
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $http_x_api_key zone=api_key:10m rate=100r/s;
limit_conn_zone $binary_remote_addr zone=conn:10m;

server {
    location /api/ {
        # 按 IP 限流
        limit_req zone=api burst=20 nodelay;
        
        # 按 API Key 限流（可选）
        limit_req zone=api_key burst=50 nodelay;
        
        # 并发连接限制
        limit_conn conn 10;
        
        # 限流时返回 429
        limit_req_status 429;
        limit_conn_status 429;
        
        proxy_pass http://backend;
    }
    
    # 自定义错误页面
    error_page 429 = @rate_limited;
    
    location @rate_limited {
        default_type application/json;
        return 429 '{"error": "Too Many Requests", "retry_after": 60}';
    }
}
```

**Traefik**：
```yaml
# 动态配置
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 10      # 平均每秒请求数
        burst: 20        # 突发请求数
        period: 1s       # 统计周期
        sourceCriterion: # 限流维度
          ipStrategy:
            depth: 1     # 使用 X-Forwarded-For 的倒数第一个 IP

  routers:
    api:
      rule: "Host(`api.example.com`)"
      middlewares:
        - rate-limit
      service: backend
```

**Kong**：
```bash
# 本地限流（单节点）
curl -X POST http://localhost:8001/services/my-api/plugins \
  -d "name=rate-limiting" \
  -d "config.second=10" \
  -d "config.minute=100" \
  -d "config.hour=1000" \
  -d "config.policy=local"

# Redis 限流（分布式）
curl -X POST http://localhost:8001/services/my-api/plugins \
  -d "name=rate-limiting" \
  -d "config.minute=100" \
  -d "config.policy=redis" \
  -d "config.redis_host=redis" \
  -d "config.redis_port=6379"
```

#### 3. 日志聚合

**Nginx JSON 日志**：
```nginx
log_format json_combined escape=json
    '{'
        '"time_local":"$time_local",'
        '"remote_addr":"$remote_addr",'
        '"request":"$request",'
        '"status":"$status",'
        '"body_bytes_sent":"$body_bytes_sent",'
        '"request_time":"$request_time",'
        '"http_referrer":"$http_referer",'
        '"http_user_agent":"$http_user_agent",'
        '"http_x_forwarded_for":"$http_x_forwarded_for",'
        '"upstream_addr":"$upstream_addr",'
        '"upstream_response_time":"$upstream_response_time",'
        '"upstream_status":"$upstream_status",'
        '"request_id":"$request_id"'
    '}';

access_log /var/log/nginx/access.log json_combined;
```

**日志收集（Filebeat + ELK）**：
```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/nginx/access.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "nginx-%{+yyyy.MM.dd}"
```

### 配置选项

#### Nginx 核心参数

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| worker_processes | auto | 工作进程数，建议设置为 CPU 核心数 |
| worker_connections | 1024 | 每个 worker 的最大连接数 |
| keepalive_timeout | 65 | 长连接超时时间 |
| client_max_body_size | 1m | 请求体最大大小 |
| proxy_connect_timeout | 60s | 代理连接超时 |
| proxy_send_timeout | 60s | 代理发送超时 |
| proxy_read_timeout | 60s | 代理读取超时 |

#### Traefik 核心参数

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| entrypoints.web.address | :80 | HTTP 入口端口 |
| providers.docker.exposedbydefault | true | 是否默认暴露所有容器 |
| api.insecure | false | 是否启用不安全的 Dashboard |

#### Kong 核心参数

| 参数 | 默认值 | 说明 |
|-----|-------|------|
| KONG_DATABASE | off | 数据库类型（off/postgres/cassandra） |
| KONG_PROXY_LISTEN | 0.0.0.0:8000 | 代理监听地址 |
| KONG_ADMIN_LISTEN | 127.0.0.1:8001 | 管理 API 地址 |

---

## 成本估算

| 指标 | Nginx | Traefik | Kong 开源版 |
|------|-------|---------|------------|
| **月成本** | $0 | $0 | $0 |
| **内存占用** | 10-50MB | 50-150MB | 200-500MB（含 DB） |
| **性能** | 10000+ req/s | 5000+ req/s | 5000+ req/s |
| **功能完整度** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **维护时间** | 1小时/月 | 2小时/月 | 3小时/月 |

### 免费方案推荐

| 方案 | 免费额度 | 特点 | 适用场景 |
|------|---------|------|---------|
| **Nginx** | 完全免费 | 性能最高，配置简单 | 单服务、简单路由 |
| **Traefik** | 完全免费 | 自动服务发现、SSL | Docker 环境 |
| **Kong 开源版** | 完全免费 | 插件丰富、功能完整 | 微服务、API 管理 |

---

## 迁出成本

### 从 Nginx 迁出

- **迁出难度**：低
- **迁出步骤**：
  1. 导出 nginx.conf 配置
  2. 转换为新网关的配置格式
  3. 验证路由规则
  4. 灰度切换流量

### 从 Kong 迁出

- **迁出难度**：中
- **迁出步骤**：
  1. 导出 Kong 配置（`kong config export`）
  2. 转换插件配置
  3. 迁移消费者和 API Key
  4. 验证认证和限流规则

### 从云网关迁出

- **迁出难度**：高
- **迁出步骤**：
  1. 导出所有 API 配置
  2. 自建网关环境
  3. 配置 SSL 证书
  4. 迁移域名解析
  5. 灰度切换

---

## 与其他武器配合

- **前置**：
  - [HTTPS 配置](./ssl-certificates.md) - SSL 终结
  - [DNS 配置](../saas/dns-management.md) - 域名解析

- **后置**：
  - [请求验证](./request-validation.md) - 参数验证
  - [API 监控](../saas/api-monitoring.md) - 性能监控
  - [日志收集](../saas/log-aggregation.md) - 日志聚合

- **替代**：无（网关是推荐的基础设施）

- **互补**：
  - [API 认证](./api-auth-guide.md) - 认证实现
  - [限流](./rate-limiting-simple.md) - 限流策略

---

## 常见问题

**Q: Nginx vs Traefik vs Kong，怎么选？**

A:
- 单服务、追求性能 → Nginx
- Docker 环境、自动化 → Traefik
- 微服务、API 管理 → Kong

**Q: 如何实现零停机重启？**

A:
```nginx
# Nginx 平滑重启
nginx -s reload

# 多实例滚动更新（Docker）
docker-compose up -d --scale app=2 --no-recreate
docker-compose up -d --scale app=1
```

**Q: 如何处理跨域请求？**

A:
```nginx
location /api/ {
    # CORS 配置
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    
    # 预检请求处理
    if ($request_method = OPTIONS) {
        return 204;
    }
    
    proxy_pass http://backend;
}
```

**Q: 如何实现灰度发布？**

A:
```nginx
# 基于权重的流量分发
upstream backend {
    server backend-v1:3000 weight=90;
    server backend-v2:3001 weight=10;
}

# 基于 Header 的流量分发
map $http_x_version $backend {
    v1 backend-v1;
    v2 backend-v2;
    default backend-v1;
}

server {
    location /api/ {
        proxy_pass http://$backend:3000;
    }
}
```

**Q: 如何监控网关性能？**

A:
- Nginx: nginx-module-stub-status + Prometheus
- Traefik: 内置 Prometheus 指标
- Kong: Prometheus 插件

```nginx
# Nginx 状态端点
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

---

## 推荐实现

### 完整方案（Nginx + Docker）

```bash
# 目录结构
mkdir -p nginx/{conf.d,lua,logs}
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/lua:/etc/nginx/lua:ro
      - ./nginx/logs:/var/log/nginx
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - app

  app:
    image: your-app:latest
    expose:
      - "3000"
```

```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # 性能优化
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # 日志格式
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # 限流配置
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn:10m;

    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
    gzip_min_length 1000;

    # 包含站点配置
    include /etc/nginx/conf.d/*.conf;
}
```

```nginx
# nginx/conf.d/api.conf
upstream backend {
    server app:3000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.example.com;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # API 路由
    location /api/ {
        # 限流
        limit_req zone=api burst=20 nodelay;
        limit_conn conn 10;

        # 代理配置
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "OK\n";
        add_header Content-Type text/plain;
    }

    # 限流响应
    error_page 429 = @rate_limited;
    location @rate_limited {
        default_type application/json;
        return 429 '{"error":"Too Many Requests","retry_after":60}';
    }
}
```

---

## 参考资料

- [Nginx 官方文档](https://nginx.org/en/docs/)
- [Traefik 官方文档](https://doc.traefik.io/traefik/)
- [Kong 官方文档](https://docs.konghq.com/)
- [Nginx 性能调优](https://www.nginx.com/blog/tuning-nginx/)
- [API 网关设计模式](https://microservices.io/patterns/apigateway.html)
