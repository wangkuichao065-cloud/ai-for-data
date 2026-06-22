# 数据分析系统综合实践 — API 接口文档

> 技术栈：FastAPI + Neo4j + FAISS + LangChain + Ollama(DeepSeek) + Stable Diffusion
> 基础地址：`http://127.0.0.1:8000`
> 接口文档（自动生成）：`http://127.0.0.1:8000/docs`（FastAPI Swagger UI）

---

## 一、通用约定

### 1.1 请求规范

| 项目 | 说明 |
|------|------|
| 协议 | HTTP |
| 数据格式 | JSON（`application/json`） |
| 字符编码 | UTF-8 |
| 认证方式 | Bearer Token（JWT），Header 中携带 `Authorization: Bearer <token>` |

### 1.2 统一响应格式

所有接口统一返回如下 JSON 结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2026-06-22T10:00:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 状态码，200 成功，非 200 失败 |
| message | string | 提示信息 |
| data | object/array/null | 业务数据 |
| timestamp | string | 服务器时间戳 |

### 1.3 状态码定义

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 / Token 失效 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 409 | 资源冲突 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（如模型加载中） |

### 1.4 分页参数约定

列表类接口统一分页参数：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码，从 1 开始 |
| page_size | int | 20 | 每页条数，最大 100 |

分页响应：

```json
{
  "code": 200,
  "data": {
    "list": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 二、用户认证模块

### 2.1 用户注册

```
POST /api/v1/auth/register
```

**请求体：**

```json
{
  "username": "student01",
  "password": "Abc123456",
  "email": "student@example.com",
  "role": "student"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| username | string | 是 | 用户名，3-20 字符 |
| password | string | 是 | 密码，至少 8 位，含字母和数字 |
| email | string | 是 | 邮箱 |
| role | string | 否 | 角色：student（默认）/ teacher / admin |

**响应：**

```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "student01",
    "role": "student",
    "created_at": "2026-06-22T10:00:00Z"
  }
}
```

### 2.2 用户登录

```
POST /api/v1/auth/login
```

**请求体：**

```json
{
  "username": "student01",
  "password": "Abc123456"
}
```

**响应：**

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 7200,
    "user": {
      "user_id": 1,
      "username": "student01",
      "role": "student",
      "avatar": "/static/avatars/default.png"
    }
  }
}
```

### 2.3 刷新 Token

```
POST /api/v1/auth/refresh
```

**请求体：**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 2.4 获取当前用户信息

```
GET /api/v1/auth/me
```

**Header：** `Authorization: Bearer <token>`

**响应：**

```json
{
  "code": 200,
  "data": {
    "user_id": 1,
    "username": "student01",
    "email": "student@example.com",
    "role": "student",
    "avatar": "/static/avatars/default.png",
    "login_count": 15,
    "last_login": "2026-06-21T14:30:00Z"
  }
}
```

### 2.5 修改密码

```
PUT /api/v1/auth/password
```

**请求体：**

```json
{
  "old_password": "Abc123456",
  "new_password": "Xyz789012"
}
```

---

## 三、知识图谱模块

### 3.1 获取知识图谱可视化数据

前端 ECharts / neovis.js 渲染所需节点和边数据。

```
GET /api/v1/graph/visualization
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| course | string | 否 | 课程筛选：machine_learning / data_mining，默认全部 |
| depth | int | 否 | 图谱展开深度，默认 2 |
| limit | int | 否 | 返回节点最大数量，默认 200 |

**响应：**

```json
{
  "code": 200,
  "data": {
    "nodes": [
      {
        "id": "ml_001",
        "label": "机器学习",
        "type": "course",
        "properties": {
          "description": "机器学习是研究计算机系统如何自动改进的学科",
          "difficulty": 3
        }
      },
      {
        "id": "ml_002",
        "label": "监督学习",
        "type": "chapter",
        "properties": {
          "description": "利用标注数据训练模型"
        }
      },
      {
        "id": "ml_003",
        "label": "线性回归",
        "type": "knowledge_point",
        "properties": {
          "description": "通过线性关系建模变量间关系",
          "difficulty": 2
        }
      }
    ],
    "edges": [
      {
        "source": "ml_001",
        "target": "ml_002",
        "relation": "包含",
        "properties": {}
      },
      {
        "source": "ml_002",
        "target": "ml_003",
        "relation": "包含",
        "properties": {}
      },
      {
        "source": "ml_003",
        "target": "ml_004",
        "relation": "相似于",
        "properties": {
          "similarity": 0.85
        }
      }
    ],
    "categories": [
      { "name": "course" },
      { "name": "chapter" },
      { "name": "knowledge_point" },
      { "name": "algorithm" },
      { "name": "application" }
    ]
  }
}
```

### 3.2 查询知识点详情

```
GET /api/v1/graph/node/{node_id}
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "node_id": "ml_003",
    "label": "线性回归",
    "type": "knowledge_point",
    "course": "machine_learning",
    "description": "线性回归是一种通过线性方程描述变量之间关系的统计方法...",
    "difficulty": 2,
    "prerequisites": [
      { "node_id": "ml_010", "label": "最小二乘法" }
    ],
    "related_nodes": [
      { "node_id": "ml_004", "label": "逻辑回归", "relation": "相似于", "similarity": 0.85 },
      { "node_id": "ml_015", "label": "房价预测", "relation": "应用于" }
    ],
    "resources": [
      { "title": "线性回归详解", "type": "pdf", "url": "/static/resources/lr.pdf" }
    ]
  }
}
```

### 3.3 搜索知识节点

```
GET /api/v1/graph/search
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keyword | string | 是 | 搜索关键词 |
| course | string | 否 | 课程筛选 |
| limit | int | 否 | 返回条数，默认 10 |

**响应：**

```json
{
  "code": 200,
  "data": [
    {
      "node_id": "ml_003",
      "label": "线性回归",
      "type": "knowledge_point",
      "course": "machine_learning",
      "highlight": "线性<em>回归</em>是一种通过线性方程..."
    }
  ]
}
```

### 3.4 获取知识点路径

查询从基础知识点到目标知识点的学习路径。

```
GET /api/v1/graph/path
```

**查询参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source | string | 是 | 起始节点 ID |
| target | string | 是 | 目标节点 ID |

**响应：**

```json
{
  "code": 200,
  "data": {
    "path": ["ml_010", "ml_003", "ml_004", "ml_020"],
    "path_labels": ["最小二乘法", "线性回归", "逻辑回归", "分类问题"],
    "total_steps": 3
  }
}
```

### 3.5 新增知识节点

```
POST /api/v1/graph/nodes
```

**Header：** `Authorization: Bearer <token>`（需 teacher/admin 权限）

**请求体：**

```json
{
  "label": "梯度下降",
  "type": "algorithm",
  "course": "machine_learning",
  "description": "一种迭代优化算法，用于寻找函数的最小值",
  "difficulty": 3,
  "parent_id": "ml_002"
}
```

### 3.6 新增知识关系

```
POST /api/v1/graph/edges
```

**请求体：**

```json
{
  "source_id": "ml_003",
  "target_id": "ml_030",
  "relation": "依赖",
  "properties": {}
}
```

### 3.7 获取课程知识树

```
GET /api/v1/graph/tree/{course}
```

**路径参数：** course = machine_learning / data_mining

**响应：**

```json
{
  "code": 200,
  "data": {
    "course": "machine_learning",
    "title": "机器学习",
    "children": [
      {
        "id": "ml_002",
        "label": "监督学习",
        "children": [
          { "id": "ml_003", "label": "线性回归", "children": [] },
          { "id": "ml_004", "label": "逻辑回归", "children": [] },
          { "id": "ml_005", "label": "支持向量机", "children": [] }
        ]
      },
      {
        "id": "ml_006",
        "label": "无监督学习",
        "children": [
          { "id": "ml_007", "label": "K-Means", "children": [] },
          { "id": "ml_008", "label": "DBSCAN", "children": [] }
        ]
      }
    ]
  }
}
```

### 3.8 获取知识图谱统计

```
GET /api/v1/graph/stats
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "total_nodes": 156,
    "total_edges": 312,
    "by_course": {
      "machine_learning": { "nodes": 89, "edges": 178 },
      "data_mining": { "nodes": 67, "edges": 134 }
    },
    "by_type": {
      "course": 2,
      "chapter": 12,
      "knowledge_point": 98,
      "algorithm": 34,
      "application": 10
    },
    "relation_types": {
      "包含": 120,
      "依赖": 45,
      "应用于": 38,
      "相似于": 109
    }
  }
}
```

---

## 四、智能问答模块（RAG + DeepSeek）

### 4.1 发起问答（流式）

通过 Server-Sent Events 流式返回 DeepSeek 生成的回答。

```
POST /api/v1/qa/ask
```

**Header：** `Authorization: Bearer <token>`

**请求体：**

```json
{
  "question": "什么是支持向量机？",
  "course": "machine_learning",
  "session_id": "sess_abc123",
  "enable_rag": true,
  "enable_graph": true,
  "top_k": 5
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 用户问题 |
| course | string | 否 | 限定课程范围 |
| session_id | string | 否 | 会话 ID，用于多轮对话 |
| enable_rag | bool | 否 | 是否启用 RAG 检索，默认 true |
| enable_graph | bool | 否 | 是否启用知识图谱增强，默认 true |
| top_k | int | 否 | RAG 检索返回文档数，默认 5 |

**响应（SSE 流）：**

```
Content-Type: text/event-stream

data: {"type": "retrieving", "message": "正在检索知识库..."}

data: {"type": "references", "data": [{"source": "机器学习教材.pdf", "page": 45, "score": 0.92}]}

data: {"type": "graph_context", "data": {"related_nodes": ["svm", "核函数", "最大间隔"]}}

data: {"type": "token", "content": "支持"}

data: {"type": "token", "content": "向量机"}

data: {"type": "token", "content": "（SVM）"}

data: {"type": "token", "content": "是一种二分类模型..."}

data: {"type": "done", "answer_id": "ans_001", "usage": {"prompt_tokens": 512, "completion_tokens": 256}}
```

### 4.2 发起问答（非流式）

```
POST /api/v1/qa/ask-sync
```

**请求体：** 同 4.1

**响应：**

```json
{
  "code": 200,
  "data": {
    "answer_id": "ans_001",
    "question": "什么是支持向量机？",
    "answer": "支持向量机（SVM）是一种二分类模型，其基本模型是定义在特征空间上的间隔最大的线性分类器...",
    "references": [
      {
        "source": "机器学习教材.pdf",
        "page": 45,
        "content": "SVM 通过寻找最大间隔超平面进行分类...",
        "score": 0.92
      },
      {
        "source": "数据挖掘笔记.txt",
        "page": null,
        "content": "支持向量机广泛应用于文本分类...",
        "score": 0.85
      }
    ],
    "graph_context": {
      "related_nodes": ["svm", "核函数", "最大间隔"],
      "relations": ["SVM 依赖 核函数", "SVM 基于 最大间隔"]
    },
    "usage": {
      "prompt_tokens": 512,
      "completion_tokens": 256,
      "total_tokens": 768
    },
    "response_time_ms": 3200
  }
}
```

### 4.3 获取对话历史

```
GET /api/v1/qa/history/{session_id}
```

**查询参数：** page, page_size

**响应：**

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "answer_id": "ans_001",
        "question": "什么是支持向量机？",
        "answer": "支持向量机（SVM）是一种二分类模型...",
        "created_at": "2026-06-22T10:30:00Z",
        "references_count": 2
      },
      {
        "answer_id": "ans_002",
        "question": "SVM 的核函数有哪些？",
        "answer": "常见的核函数包括：线性核、多项式核、RBF核...",
        "created_at": "2026-06-22T10:35:00Z",
        "references_count": 3
      }
    ],
    "total": 2,
    "page": 1,
    "page_size": 20
  }
}
```

### 4.4 获取会话列表

```
GET /api/v1/qa/sessions
```

**Header：** `Authorization: Bearer <token>`

**响应：**

```json
{
  "code": 200,
  "data": [
    {
      "session_id": "sess_abc123",
      "title": "关于SVM的讨论",
      "course": "machine_learning",
      "message_count": 8,
      "last_message": "常见的核函数包括...",
      "created_at": "2026-06-22T10:00:00Z",
      "updated_at": "2026-06-22T10:35:00Z"
    }
  ]
}
```

### 4.5 创建新会话

```
POST /api/v1/qa/sessions
```

**请求体：**

```json
{
  "title": "机器学习基础讨论",
  "course": "machine_learning"
}
```

### 4.6 删除会话

```
DELETE /api/v1/qa/sessions/{session_id}
```

### 4.7 获取回答详情

```
GET /api/v1/qa/answers/{answer_id}
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "answer_id": "ans_001",
    "question": "什么是支持向量机？",
    "answer": "支持向量机（SVM）是一种二分类模型...",
    "references": [
      {
        "source": "机器学习教材.pdf",
        "page": 45,
        "content": "...",
        "score": 0.92
      }
    ],
    "graph_context": {
      "related_nodes": ["svm", "核函数"]
    },
    "feedback": null,
    "created_at": "2026-06-22T10:30:00Z"
  }
}
```

### 4.8 回答反馈

```
POST /api/v1/qa/answers/{answer_id}/feedback
```

**请求体：**

```json
{
  "rating": 5,
  "is_helpful": true,
  "comment": "回答很清晰，帮助理解了SVM的基本原理"
}
```

### 4.9 RAG 知识库状态

```
GET /api/v1/qa/rag/status
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "vector_store": "FAISS",
    "total_documents": 45,
    "total_chunks": 1280,
    "embedding_model": "bge-small-zh-v1.5",
    "last_update": "2026-06-21T18:00:00Z",
    "index_size_mb": 52.3
  }
}
```

---

## 五、数字教师模块

### 5.1 数字教师对话

数字教师结合 RAG 回答，同时返回表情和动作指令。

```
POST /api/v1/teacher/chat
```

**Header：** `Authorization: Bearer <token>`

**请求体：**

```json
{
  "question": "请讲解一下K-Means聚类算法",
  "session_id": "sess_abc123",
  "enable_voice": true,
  "emotion": "auto"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| question | string | 是 | 学生提问 |
| session_id | string | 否 | 会话 ID |
| enable_voice | bool | 否 | 是否生成语音，默认 false |
| emotion | string | 否 | 教师情绪：auto / happy / serious / encouraging |

**响应：**

```json
{
  "code": 200,
  "data": {
    "answer": "K-Means 是一种经典的聚类算法...",
    "emotion": "encouraging",
    "action": "explain",
    "voice_url": "/static/voice/ans_001.mp3",
    "duration_ms": 5200,
    "references": [
      { "source": "机器学习教材.pdf", "page": 120 }
    ]
  }
}
```

### 5.2 数字教师形象

获取数字教师的 Live2D 或静态图片资源。

```
GET /api/v1/teacher/avatar
```

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| type | string | live2d / static，默认 static |
| emotion | string | happy / normal / serious / thinking |

**响应：**

```json
{
  "code": 200,
  "data": {
    "model_url": "/static/teacher/model.json",
    "textures": [
      { "emotion": "normal", "url": "/static/teacher/normal.png" },
      { "emotion": "happy", "url": "/static/teacher/happy.png" },
      { "emotion": "serious", "url": "/static/teacher/serious.png" }
    ],
    "current_emotion": "normal"
  }
}
```

### 5.3 生成数字教师图片

通过 Stable Diffusion 生成教师形象。

```
POST /api/v1/teacher/generate-avatar
```

**Header：** 需 admin 权限

**请求体：**

```json
{
  "prompt": "professional female teacher, friendly smile, white background, anime style",
  "negative_prompt": "low quality, blurry, deformed",
  "width": 512,
  "height": 512,
  "steps": 20,
  "cfg_scale": 7.5
}
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "image_url": "/static/teacher/generated_001.png",
    "seed": 42,
    "generation_time_ms": 8500
  }
}
```

### 5.4 文字转语音

```
POST /api/v1/teacher/tts
```

**请求体：**

```json
{
  "text": "K-Means 是一种经典的聚类算法",
  "voice": "female_zh",
  "speed": 1.0
}
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "audio_url": "/static/voice/tts_001.mp3",
    "duration_ms": 3200,
    "format": "mp3"
  }
}
```

### 5.5 获取教学进度

```
GET /api/v1/teacher/progress
```

**Header：** `Authorization: Bearer <token>`

**响应：**

```json
{
  "code": 200,
  "data": {
    "total_questions": 42,
    "courses_covered": ["machine_learning", "data_mining"],
    "mastered_topics": ["线性回归", "逻辑回归", "K-Means"],
    "weak_topics": ["SVM核函数", "DBSCAN参数选择"],
    "study_hours": 12.5,
    "level": "中级"
  }
}
```

---

## 六、数据分析模块

### 6.1 仪表盘概览

```
GET /api/v1/dashboard/overview
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "kpis": {
      "total_questions": 156,
      "today_questions": 12,
      "total_users": 48,
      "active_users": 23,
      "knowledge_coverage": 0.68,
      "avg_satisfaction": 4.3
    },
    "question_trend": {
      "labels": ["06-16", "06-17", "06-18", "06-19", "06-20", "06-21", "06-22"],
      "values": [8, 15, 12, 20, 18, 25, 12]
    },
    "popular_topics": [
      { "topic": "SVM", "count": 28, "progress": 0.85 },
      { "topic": "K-Means", "count": 22, "progress": 0.72 },
      { "topic": "神经网络", "count": 19, "progress": 0.60 },
      { "topic": "决策树", "count": 15, "progress": 0.55 },
      { "topic": "线性回归", "count": 12, "progress": 0.90 }
    ],
    "course_distribution": {
      "machine_learning": 65,
      "data_mining": 35
    }
  }
}
```

### 6.2 提问趋势分析

```
GET /api/v1/dashboard/question-trend
```

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| start_date | string | 起始日期 YYYY-MM-DD |
| end_date | string | 结束日期 YYYY-MM-DD |
| course | string | 课程筛选 |
| granularity | string | day / week / month，默认 day |

**响应：**

```json
{
  "code": 200,
  "data": {
    "labels": ["06-01", "06-02", "...", "06-22"],
    "series": [
      {
        "name": "机器学习",
        "data": [5, 8, 12, "...", 12]
      },
      {
        "name": "数据挖掘",
        "data": [3, 5, 7, "...", 8]
      }
    ]
  }
}
```

### 6.3 知识点热度分析

```
GET /api/v1/dashboard/topic-heatmap
```

**查询参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| course | string | 课程筛选 |

**响应：**

```json
{
  "code": 200,
  "data": {
    "topics": [
      "线性回归", "逻辑回归", "SVM", "决策树", "神经网络",
      "K-Means", "DBSCAN", "PCA", "关联规则", "朴素贝叶斯"
    ],
    "courses": ["机器学习", "数据挖掘"],
    "matrix": [
      [12, 8, 28, 15, 19, 22, 10, 5, 8, 7],
      [6, 4, 15, 10, 8, 18, 12, 3, 14, 9]
    ]
  }
}
```

### 6.4 用户活跃度分析

```
GET /api/v1/dashboard/user-activity
```

**查询参数：** start_date, end_date

**响应：**

```json
{
  "code": 200,
  "data": {
    "active_users_per_day": [
      { "date": "06-16", "count": 15 },
      { "date": "06-17", "count": 20 }
    ],
    "hourly_distribution": [
      { "hour": "08", "count": 5 },
      { "hour": "09", "count": 12 },
      { "hour": "10", "count": 18 },
      { "hour": "14", "count": 22 },
      { "hour": "15", "count": 25 },
      { "hour": "19", "count": 15 },
      { "hour": "20", "count": 28 }
    ],
    "avg_session_duration_min": 18.5
  }
}
```

### 6.5 满意度分析

```
GET /api/v1/dashboard/satisfaction
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "avg_rating": 4.3,
    "total_ratings": 120,
    "distribution": {
      "5": 68,
      "4": 32,
      "3": 15,
      "2": 4,
      "1": 1
    },
    "trend": {
      "labels": ["06-16", "06-17", "06-18", "...", "06-22"],
      "values": [4.1, 4.2, 4.0, "...", 4.3]
    }
  }
}
```

### 6.6 知识掌握度雷达图

```
GET /api/v1/dashboard/mastery-radar
```

**Header：** `Authorization: Bearer <token>`

**响应：**

```json
{
  "code": 200,
  "data": {
    "indicators": ["基础概念", "监督学习", "无监督学习", "深度学习", "模型评估", "特征工程"],
    "values": [0.85, 0.72, 0.60, 0.45, 0.68, 0.55],
    "full_mark": 1.0
  }
}
```

---

## 七、文件管理模块

### 7.1 上传知识库文档

上传 PDF/TXT/DOCX 文档到 RAG 知识库，自动分块、向量化并存入 FAISS。

```
POST /api/v1/files/upload
```

**Header：** 需 teacher/admin 权限

**请求体：** `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 上传的文件（pdf/txt/docx/md） |
| course | string | 是 | 所属课程 |
| category | string | 否 | 分类标签 |
| description | string | 否 | 文档描述 |

**响应：**

```json
{
  "code": 200,
  "message": "文件上传成功，正在处理",
  "data": {
    "file_id": "file_001",
    "filename": "机器学习教材.pdf",
    "size": 5242880,
    "status": "processing",
    "task_id": "task_001"
  }
}
```

### 7.2 查询文件处理状态

```
GET /api/v1/files/{file_id}/status
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "file_id": "file_001",
    "filename": "机器学习教材.pdf",
    "status": "completed",
    "progress": 100,
    "total_chunks": 120,
    "processed_chunks": 120,
    "error": null
  }
}
```

### 7.3 获取知识库文件列表

```
GET /api/v1/files
```

**查询参数：** page, page_size, course, category

**响应：**

```json
{
  "code": 200,
  "data": {
    "list": [
      {
        "file_id": "file_001",
        "filename": "机器学习教材.pdf",
        "course": "machine_learning",
        "category": "教材",
        "size": 5242880,
        "chunks": 120,
        "status": "completed",
        "uploaded_by": "admin",
        "created_at": "2026-06-20T14:00:00Z"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

### 7.4 删除知识库文件

```
DELETE /api/v1/files/{file_id}
```

从 FAISS 向量库和文件系统中同时删除。

### 7.5 重新构建向量索引

```
POST /api/v1/files/rebuild-index
```

**Header：** 需 admin 权限

**响应：**

```json
{
  "code": 200,
  "message": "索引重建任务已启动",
  "data": {
    "task_id": "task_002",
    "total_files": 45
  }
}
```

---

## 八、系统管理模块

### 8.1 系统健康检查

```
GET /api/v1/system/health
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "status": "healthy",
    "services": {
      "neo4j": { "status": "up", "version": "5.15.0", "latency_ms": 5 },
      "ollama": { "status": "up", "model": "deepseek-r1:7b", "latency_ms": 120 },
      "faiss": { "status": "up", "vectors": 1280 },
      "stable_diffusion": { "status": "standby", "model": "sd-v1.5" },
      "mysql": { "status": "up", "version": "8.0.35" }
    },
    "system": {
      "cpu_usage": 0.35,
      "memory_usage": 0.62,
      "gpu_memory_usage": 0.45,
      "disk_usage": 0.28
    }
  }
}
```

### 8.2 大模型状态

```
GET /api/v1/system/model-status
```

**响应：**

```json
{
  "code": 200,
  "data": {
    "llm": {
      "name": "deepseek-r1:7b",
      "provider": "ollama",
      "status": "loaded",
      "quantization": "Q4_K_M",
      "memory_usage_gb": 4.5,
      "context_window": 4096
    },
    "embedding": {
      "name": "bge-small-zh-v1.5",
      "dimension": 512,
      "memory_usage_gb": 0.3
    },
    "stable_diffusion": {
      "name": "sd-v1.5",
      "status": "standby",
      "memory_usage_gb": 0
    },
    "gpu": {
      "total_memory_gb": 8,
      "used_memory_gb": 4.8,
      "free_memory_gb": 3.2,
      "strategy": "交替加载：LLM 与 SD 不同时满载"
    }
  }
}
```

### 8.3 切换模型

```
POST /api/v1/system/switch-model
```

**Header：** 需 admin 权限

**请求体：**

```json
{
  "target": "llm",
  "action": "load",
  "model_name": "deepseek-r1:7b"
}
```

用于 8GB 显存环境下 LLM 与 SD 交替加载。

### 8.4 获取系统配置

```
GET /api/v1/system/config
```

**Header：** 需 admin 权限

**响应：**

```json
{
  "code": 200,
  "data": {
    "ollama": {
      "base_url": "http://127.0.0.1:11434",
      "default_model": "deepseek-r1:7b",
      "temperature": 0.7,
      "max_tokens": 2048
    },
    "neo4j": {
      "uri": "bolt://127.0.0.1:7687",
      "database": "knowledge_graph"
    },
    "rag": {
      "chunk_size": 500,
      "chunk_overlap": 50,
      "top_k": 5,
      "similarity_threshold": 0.7
    },
    "sd": {
      "model_path": "models/stable-diffusion-v1-5",
      "default_steps": 20,
      "default_cfg": 7.5
    }
  }
}
```

### 8.5 更新系统配置

```
PUT /api/v1/system/config
```

**Header：** 需 admin 权限

**请求体：** 同 8.4 的 data 部分

---

## 九、错误码参考

| code | HTTP Status | 说明 | 常见原因 |
|------|-------------|------|----------|
| 200 | 200 | 成功 | — |
| 400 | 400 | 参数错误 | 缺少必填字段 / 格式不合法 |
| 401 | 401 | 未认证 | Token 缺失或过期 |
| 403 | 403 | 无权限 | 角色权限不足 |
| 404 | 404 | 资源不存在 | 节点/文件/会话不存在 |
| 409 | 409 | 冲突 | 用户名已存在 / 文件重复 |
| 422 | 422 | 实体验证失败 | 字段类型不匹配 |
| 429 | 429 | 请求过频 | 触发限流 |
| 500 | 500 | 服务器错误 | 代码异常 |
| 503 | 503 | 服务不可用 | 模型加载中 / Neo4j 未连接 |

---

## 十、接口版本管理

当前版本：v1

版本通过 URL 路径区分：`/api/v1/...`、`/api/v2/...`

后续版本变更将保留 v1 向后兼容。

---

## 附录：FastAPI 路由注册结构

```python
# main.py
from fastapi import FastAPI
from api.v1 import auth, graph, qa, teacher, dashboard, files, system

app = FastAPI(title="数据分析系统综合实践", version="1.0.0")

app.include_router(auth.router, prefix="/api/v1/auth", tags=["用户认证"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["知识图谱"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["智能问答"])
app.include_router(teacher.router, prefix="/api/v1/teacher", tags=["数字教师"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["数据分析"])
app.include_router(files.router, prefix="/api/v1/files", tags=["文件管理"])
app.include_router(system.router, prefix="/api/v1/system", tags=["系统管理"])
```

启动命令：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
