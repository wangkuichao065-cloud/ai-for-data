# 综合实验 — 课程知识图谱与智能问答平台

基于知识图谱与大模型的课程数据分析平台，综合运用 Neo4j 知识图谱、DeepSeek RAG 检索增强生成、IndexTTS2 数字教师语音合成等技术。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python + FastAPI |
| 图数据库 | Neo4j 5.x |
| 关系数据库 | MySQL 8.0 |
| 向量库 | FAISS + bge-small-zh-v1.5 |
| 大语言模型 | DeepSeek-R1:7b (Ollama) |
| 语音合成 | IndexTTS2 (B站开源) |
| 前端 | Vue3 + Element Plus + ECharts (CDN) |

## 项目结构

```
backend/
├── main.py                 # FastAPI 入口
├── config.py               # 配置文件
├── api/
│   ├── deps.py             # 依赖注入(认证/权限)
│   └── v1/
│       ├── auth.py         # 用户认证
│       ├── graph.py        # 知识图谱
│       ├── qa.py           # 智能问答(SSE流式)
│       ├── teacher.py      # 数字教师
│       ├── dashboard.py    # 数据分析
│       ├── files.py        # 文件管理
│       └── system.py       # 系统管理
├── service/
│   ├── auth_service.py     # 认证逻辑
│   ├── graph_service.py    # 图谱查询
│   ├── qa_service.py       # RAG问答
│   ├── llm_service.py       # Ollama调用
│   ├── teacher_service.py  # 数字教师
│   ├── tts_service.py      # IndexTTS2语音
│   ├── file_service.py     # 文件处理
│   ├── analysis_service.py # 数据分析
│   └── system_service.py   # 系统管理
├── rag/
│   ├── vector_store.py     # FAISS向量库
│   ├── retriever.py        # 双路检索器
│   └── document_processor.py # 文档分块
├── graph/
│   └── neo4j_client.py     # Neo4j连接
├── database/
│   ├── mysql_client.py     # MySQL连接
│   └── init_mysql.sql      # 建表脚本
├── models/
│   └── schemas.py          # Pydantic模型
└── utils/
    ├── jwt.py              # JWT工具
    ├── response.py         # 统一响应
    └── logger.py           # 日志工具
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化 MySQL

```bash
# 登录 MySQL, 创建数据库并导入建表脚本
mysql -u root -proot < backend/database/init_mysql.sql
```

### 3. 启动 Neo4j

```bash
# 确保 Neo4j 已运行在 bolt://127.0.0.1:7687
# 通过 Neo4j Browser 执行 init_neo4j.cypher 初始化知识图谱
```

### 4. 启动 Ollama

```bash
ollama pull deepseek-r1:7b
ollama serve
```

### 5. (可选) 安装 IndexTTS2

```bash
git clone https://github.com/index-tts/index-tts.git
cd index-tts
uv sync --all-extras
# 下载模型
hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

将 checkpoints 目录路径配置到 `backend/config.py` 的 `INDEXTTS_CHECKPOINTS`。

### 6. 启动后端

```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

访问 `http://127.0.0.1:8000/docs` 查看 API 文档。

## GPU 显存策略

8GB 显存下，DeepSeek(4.5GB) 与 IndexTTS2/SD(3.5GB) 交替加载：
- 问答时: 仅加载 LLM
- 语音合成时: 卸载 LLM, 加载 IndexTTS2
- 通过 `/api/v1/system/model-status` 监控显存使用

## API 模块

| 模块 | 前缀 | 功能 |
|------|------|------|
| 用户认证 | /api/v1/auth | 注册/登录/JWT/密码修改 |
| 知识图谱 | /api/v1/graph | 可视化/搜索/路径/统计/CRUD |
| 智能问答 | /api/v1/qa | SSE流式问答/多轮对话/反馈 |
| 数字教师 | /api/v1/teacher | 对话/语音/学习进度 |
| 数据分析 | /api/v1/dashboard | 仪表盘/趋势/热度/满意度 |
| 文件管理 | /api/v1/files | 上传/向量化/删除/重建索引 |
| 系统管理 | /api/v1/system | 健康检查/模型状态/配置 |
