# 机器学习课程知识图谱 - 使用指南

## 第一步：安装并启动 Neo4j

### 方式 A：Neo4j Desktop（推荐，图形界面）

1. 打开浏览器访问 https://neo4j.com/download/
2. 填写信息后下载 Neo4j Desktop（约 200MB）
3. 安装并启动 Neo4j Desktop
4. 点击「New Project」→「Add Database」→「Create a Local DBMS」
5. 设置密码为 `12345678`（与脚本中一致），端口保持默认 7687
6. 点击「Create」→ 点击数据库旁边的「Start」按钮
7. 等待状态变为绿色「Running」

### 方式 B：Neo4j Community Server（轻量，命令行）

1. 访问 https://neo4j.com/download-center/#community
2. 选择「Neo4j Community Edition」→「Neo4j Server」→ 下载 Windows zip
3. 解压到任意目录，例如 `C:\neo4j`
4. 打开命令提示符（管理员），运行：
   ```
   C:\neo4j\bin\neo4j console
   ```
5. 首次启动后，浏览器打开 http://localhost:7474
6. 默认账号 neo4j/neo4j，系统会要求你设置新密码，设为 `12345678`

## 第二步：安装 Python 依赖

打开命令提示符，运行：
```
pip install neo4j
```

## 第三步：运行构建脚本

```
cd D:\digtial figure
python build_kg.py
```

脚本会自动：
- 清空 Neo4j 数据库
- 创建 300+ 个知识节点（19章节、95概念、126算法、54技术、20应用）
- 创建 460+ 条关系（前置、包含、属于、使用、扩展、应用等）
- 输出验证统计和示例查询结果

## 第四步：验证与探索

运行查询脚本：
```
python query_kg.py
```

或打开 Neo4j Browser（http://localhost:7474），输入以下 Cypher 查询：

```cypher
// 全局概览
MATCH (n:MLNode) RETURN n LIMIT 200

// 深度学习章节子图
MATCH (ch:Chapter {name: '深度学习'})-[:CONTAINS]->(c)
OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Algorithm)
OPTIONAL MATCH (a)-[:USES]->(t:Technique)
RETURN ch, c, a, t

// 学习路径
MATCH path = (ch1:Chapter)-[:HAS_PREREQ*1..3]->(ch2:Chapter)
RETURN path

// 两个概念之间的最短路径
MATCH path = shortestPath(
  (a:MLNode {name: '线性回归'})-[*..10]-(b:MLNode {name: 'Transformer'})
)
RETURN path
```

## 知识图谱结构说明

### 节点类型（5类）

| 标签 | 数量 | 说明 |
|------|------|------|
| Chapter | 19 | 课程章节 |
| Concept | 95 | 核心概念（学习范式、数学基础、数据预处理等） |
| Algorithm | 126 | 具体算法/模型 |
| Technique | 54 | 技术方法（优化器、激活函数、损失函数、正则化等） |
| Application | 20 | 应用领域 |

### 关系类型（14类）

| 关系 | 含义 | 示例 |
|------|------|------|
| HAS_PREREQ | 章节前置依赖 | 数学基础 → 线性模型 |
| CONTAINS | 章节包含概念 | 集成学习 → 集成学习(概念) |
| BELONGS_TO | 算法属于范式 | XGBoost → 监督学习 |
| USES | 使用技术 | CNN → Dropout |
| EXTENDS | 扩展/改进 | GPT → GPT-2 |
| IMPROVES | 性能改进 | K-Means → K-Means++ |
| BASED_ON | 基于 | BERT → Transformer |
| APPLIES_TO | 应用于 | ResNet → 图像分类 |
| PARADIGM | 学习范式 | 机器学习 → 监督学习 |
| RELATED_TO | 关联 | Word2Vec → GloVe |
| SPECIALIZATION | 特化 | 核PCA → PCA |
| METHOD | 方法 | 交叉验证 → K折交叉验证 |
| EVALUATED_BY | 评估指标 | K-Means → 轮廓系数 |
| CHALLENGE | 挑战 | 监督学习 → 过拟合 |

## 修改说明

- 如果需要修改 Neo4j 密码，编辑 `build_kg.py` 和 `query_kg.py` 中的 `NEO4J_PASSWORD`
- 如果需要添加新的知识点，在脚本中对应的列表里添加条目，然后重新运行 `build_kg.py`
