/**
 * Mock 数据层 — 后端就绪前使用
 */

// ===== 认证 & 用户 =====
const authUser = {
  user_id: 1001,
  username: 'admin',
  nickname: '管理员',
  email: 'admin@example.com',
  role: 'admin',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
  token: 'mock-jwt-token-abc123def456',
}

const profile = {
  user_id: 1001,
  username: 'admin',
  nickname: '管理员',
  email: 'admin@example.com',
  phone: '13800138000',
  role: 'admin',
  avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=admin',
}

// ===== 文件管理 =====
const files = [
  { file_id: 1, filename: '机器学习导论.pdf', course: 'machine_learning', file_type: 'pdf', file_size: 2048576, chunk_count: 12, status: 'ready', created_at: '2025-06-01T08:30:00Z' },
  { file_id: 2, filename: '线性模型讲义.docx', course: 'machine_learning', file_type: 'docx', file_size: 512000, chunk_count: 6, status: 'ready', created_at: '2025-06-03T10:15:00Z' },
  { file_id: 3, filename: '决策树笔记.md', course: 'machine_learning', file_type: 'md', file_size: 15360, chunk_count: 3, status: 'ready', created_at: '2025-06-05T14:00:00Z' },
  { file_id: 4, filename: '数据挖掘概述.pdf', course: 'data_mining', file_type: 'pdf', file_size: 1536000, chunk_count: 9, status: 'ready', created_at: '2025-06-07T09:00:00Z' },
  { file_id: 5, filename: '关联规则挖掘.docx', course: 'data_mining', file_type: 'docx', file_size: 409600, chunk_count: 5, status: 'ready', created_at: '2025-06-08T11:20:00Z' },
  { file_id: 6, filename: '聚类算法实验.pdf', course: 'data_mining', file_type: 'pdf', file_size: 1024000, chunk_count: 7, status: 'processing', created_at: '2025-06-10T16:45:00Z' },
  { file_id: 7, filename: '神经网络入门.txt', course: 'machine_learning', file_type: 'txt', file_size: 8192, chunk_count: 2, status: 'ready', created_at: '2025-06-11T08:00:00Z' },
  { file_id: 8, filename: 'SVM核函数详解.md', course: 'machine_learning', file_type: 'md', file_size: 20480, chunk_count: 4, status: 'ready', created_at: '2025-06-12T13:30:00Z' },
]

// ===== 系统健康 =====
const systemHealth = {
  mysql: { status: 'up', latency_ms: 3 },
  neo4j: { status: 'up', latency_ms: 12 },
  ollama: { status: 'up', latency_ms: 45 },
  faiss: { status: 'up', latency_ms: 2 },
  gpu: { status: 'up', utilization: 0.35 },
}

// ===== 模型状态 =====
const modelStatus = {
  llm: {
    model: 'deepseek-r1:7b',
    status: 'loaded',
    vram_used_gb: 4.5,
    vram_total_gb: 8.0,
  },
  embedding: {
    model: 'bge-small-zh-v1.5',
    status: 'loaded',
  },
  faiss: {
    total_vectors: 1250,
    dimension: 512,
    index_type: 'IVFFlat',
  },
}

// ===== 系统配置 =====
const systemConfig = {
  llm_model: 'deepseek-r1:7b',
  temperature: 0.7,
  max_tokens: 2048,
  rag_top_k: 5,
  enable_graph: true,
}

// ===== 公告 =====
const announcements = [
  { id: 1, title: '系统上线公告', content: '智能答疑系统正式上线，欢迎全体师生使用！如遇问题请通过问答页面提交反馈。', created_at: '2025-06-01T00:00:00Z' },
  { id: 2, title: '知识库更新通知', content: '机器学习课程已新增 3 份教学文档，涵盖线性模型、决策树和支持向量机章节。', created_at: '2025-06-05T09:00:00Z' },
  { id: 3, title: '模型升级公告', content: 'LLM 模型已升级至 deepseek-r1:7b，回答质量和推理速度均有显著提升。', created_at: '2025-06-08T10:00:00Z' },
  { id: 4, title: '数据挖掘课程资料导入', content: '数据挖掘课程的关联规则挖掘、聚类算法等文档已完成导入，可进行问答测试。', created_at: '2025-06-10T14:00:00Z' },
  { id: 5, title: '系统维护通知', content: '计划于本周六 02:00-04:00 进行系统维护升级，届时服务将短暂不可用，请提前做好准备。', created_at: '2025-06-12T16:00:00Z' },
]

// ===== 仪表盘 =====
const dashboard = {
  kpis: [
    { label: '知识节点', value: 1523, icon: '⬡', color: 'blue', change: '↑12%', changeDir: 'up', sub: '较昨日' },
    { label: 'AI 问答次数', value: 832, icon: '💬', color: 'purple', change: '↑18%', changeDir: 'up', sub: '较昨日' },
    { label: '文档数量', value: 258, icon: '📄', color: 'green', change: '↑8%', changeDir: 'up', sub: '较昨日' },
    { label: '数字教师', value: '在线运行', icon: '👩‍🏫', color: 'orange', change: '状态正常', changeDir: 'stable', sub: '' },
  ],
  question_trend: {
    labels: ['05-08', '05-09', '05-10', '05-11', '05-12', '05-13', '05-14'],
    qa_count: [320, 450, 380, 520, 610, 900, 750],
    user_count: [120, 180, 150, 210, 280, 450, 380],
  },
  popular_topics: [
    { topic: 'Transformer', count: 423 },
    { topic: '卷积神经网络', count: 412 },
    { topic: '聚类算法', count: 398 },
    { topic: '决策树', count: 285 },
    { topic: 'KNN 算法', count: 210 },
  ],
  announcements: [
    { date: '05-14', text: '平台已更新 DeepSeek-R1-7B 模型，问答质量大幅提升' },
    { date: '05-12', text: '新增知识图谱可视化功能，支持多维度筛选' },
    { date: '05-10', text: '优化 RAG 检索算法，提升回答准确率' },
    { date: '05-08', text: '数字教师形象与语音功能上线' },
    { date: '05-07', text: '系统维护通知：5月20日凌晨 02:00-04:00' },
  ],
  graph_overview: {
    nodes: [
      { id: 'ml', name: '机器学习', x: 300, y: 200, symbolSize: 55, itemStyle: { color: '#4f6ef7' } },
      { id: 'supervised', name: '监督学习', x: 120, y: 100, symbolSize: 38, itemStyle: { color: '#22c55e' } },
      { id: 'unsupervised', name: '无监督学习', x: 120, y: 300, symbolSize: 38, itemStyle: { color: '#8b5cf6' } },
      { id: 'deep', name: '深度学习', x: 480, y: 200, symbolSize: 38, itemStyle: { color: '#f59e0b' } },
      { id: 'linreg', name: '线性回归', x: 20, y: 40, symbolSize: 26, itemStyle: { color: '#22c55e' } },
      { id: 'logreg', name: '逻辑回归', x: 20, y: 80, symbolSize: 26, itemStyle: { color: '#22c55e' } },
      { id: 'svm', name: 'SVM', x: 20, y: 120, symbolSize: 26, itemStyle: { color: '#22c55e' } },
      { id: 'tree', name: '决策树', x: 20, y: 160, symbolSize: 26, itemStyle: { color: '#22c55e' } },
      { id: 'kmeans', name: 'KMeans', x: 20, y: 250, symbolSize: 26, itemStyle: { color: '#8b5cf6' } },
      { id: 'dbscan', name: 'DBSCAN', x: 20, y: 290, symbolSize: 26, itemStyle: { color: '#8b5cf6' } },
      { id: 'hier', name: '层次聚类', x: 20, y: 330, symbolSize: 26, itemStyle: { color: '#8b5cf6' } },
      { id: 'cnn', name: 'CNN', x: 580, y: 130, symbolSize: 26, itemStyle: { color: '#f59e0b' } },
      { id: 'rnn', name: 'RNN', x: 580, y: 200, symbolSize: 26, itemStyle: { color: '#f59e0b' } },
      { id: 'transformer', name: 'Transformer', x: 580, y: 270, symbolSize: 26, itemStyle: { color: '#f59e0b' } },
    ],
    edges: [
      { source: 'ml', target: 'supervised' },
      { source: 'ml', target: 'unsupervised' },
      { source: 'ml', target: 'deep' },
      { source: 'supervised', target: 'linreg' },
      { source: 'supervised', target: 'logreg' },
      { source: 'supervised', target: 'svm' },
      { source: 'supervised', target: 'tree' },
      { source: 'unsupervised', target: 'kmeans' },
      { source: 'unsupervised', target: 'dbscan' },
      { source: 'unsupervised', target: 'hier' },
      { source: 'deep', target: 'cnn' },
      { source: 'deep', target: 'rnn' },
      { source: 'deep', target: 'transformer' },
    ],
  },
}

// ===== 知识图谱 =====
const graph = {
  categories: [
    { name: '章节', color: '#6366f1' },
    { name: '概念', color: '#3b82f6' },
    { name: '算法', color: '#22c55e' },
    { name: '技术', color: '#f97316' },
    { name: '应用', color: '#ec4899' },
  ],
  nodes: [
    { id: 'ch01', name: '机器学习概述', category: 0, symbolSize: 50 },
    { id: 'ch02', name: '数学基础', category: 0, symbolSize: 45 },
    { id: 'ch05', name: '线性模型', category: 0, symbolSize: 42 },
    { id: 'ch06', name: '决策树', category: 0, symbolSize: 40 },
    { id: 'ch07', name: '支持向量机', category: 0, symbolSize: 42 },
    { id: 'ch09', name: '集成学习', category: 0, symbolSize: 45 },
    { id: 'ch10', name: '聚类', category: 0, symbolSize: 40 },
    { id: 'ch13', name: '神经网络', category: 0, symbolSize: 45 },
    { id: 'ch14', name: '深度学习', category: 0, symbolSize: 50 },
    { id: 'ch17', name: '自然语言处理', category: 0, symbolSize: 42 },
    { id: 'c_supervised', name: '监督学习', category: 1, symbolSize: 35 },
    { id: 'c_unsupervised', name: '无监督学习', category: 1, symbolSize: 35 },
    { id: 'c_overfit', name: '过拟合', category: 1, symbolSize: 28 },
    { id: 'c_generalization', name: '泛化能力', category: 1, symbolSize: 28 },
    { id: 'c_bias_variance', name: '偏差-方差', category: 1, symbolSize: 26 },
    { id: 'c_transfer', name: '迁移学习', category: 1, symbolSize: 30 },
    { id: 'c_reinforcement', name: '强化学习', category: 1, symbolSize: 30 },
    { id: 'a_linreg', name: '线性回归', category: 2, symbolSize: 30 },
    { id: 'a_logreg', name: '逻辑回归', category: 2, symbolSize: 30 },
    { id: 'a_svm', name: 'SVM', category: 2, symbolSize: 32 },
    { id: 'a_cart', name: 'CART', category: 2, symbolSize: 26 },
    { id: 'a_rf', name: '随机森林', category: 2, symbolSize: 32 },
    { id: 'a_xgboost', name: 'XGBoost', category: 2, symbolSize: 34 },
    { id: 'a_kmeans', name: 'K-Means', category: 2, symbolSize: 28 },
    { id: 'a_dbscan', name: 'DBSCAN', category: 2, symbolSize: 26 },
    { id: 'a_mlp', name: 'MLP', category: 2, symbolSize: 28 },
    { id: 'a_cnn', name: 'CNN', category: 2, symbolSize: 34 },
    { id: 'a_rnn', name: 'RNN', category: 2, symbolSize: 30 },
    { id: 'a_lstm', name: 'LSTM', category: 2, symbolSize: 30 },
    { id: 'a_transformer', name: 'Transformer', category: 2, symbolSize: 38 },
    { id: 'a_gan', name: 'GAN', category: 2, symbolSize: 30 },
    { id: 'a_bert', name: 'BERT', category: 2, symbolSize: 34 },
    { id: 'a_gpt', name: 'GPT', category: 2, symbolSize: 36 },
    { id: 'a_resnet', name: 'ResNet', category: 2, symbolSize: 30 },
    { id: 't_adam', name: 'Adam优化器', category: 3, symbolSize: 24 },
    { id: 't_dropout', name: 'Dropout', category: 3, symbolSize: 22 },
    { id: 't_bn', name: 'BatchNorm', category: 3, symbolSize: 22 },
    { id: 't_attention', name: '注意力机制', category: 3, symbolSize: 30 },
    { id: 't_relu', name: 'ReLU', category: 3, symbolSize: 20 },
    { id: 'app_img_cls', name: '图像分类', category: 4, symbolSize: 26 },
    { id: 'app_nlp', name: '文本分类', category: 4, symbolSize: 24 },
    { id: 'app_rec', name: '推荐系统', category: 4, symbolSize: 24 },
    { id: 'app_obj_det', name: '目标检测', category: 4, symbolSize: 24 },
  ],
  edges: [
    { source: 'ch01', target: 'c_supervised', relation: 'CONTAINS' },
    { source: 'ch01', target: 'c_unsupervised', relation: 'CONTAINS' },
    { source: 'ch01', target: 'c_reinforcement', relation: 'CONTAINS' },
    { source: 'ch01', target: 'c_overfit', relation: 'CONTAINS' },
    { source: 'ch05', target: 'a_linreg', relation: 'CONTAINS' },
    { source: 'ch05', target: 'a_logreg', relation: 'CONTAINS' },
    { source: 'ch06', target: 'a_cart', relation: 'CONTAINS' },
    { source: 'ch07', target: 'a_svm', relation: 'CONTAINS' },
    { source: 'ch09', target: 'a_rf', relation: 'CONTAINS' },
    { source: 'ch09', target: 'a_xgboost', relation: 'CONTAINS' },
    { source: 'ch10', target: 'a_kmeans', relation: 'CONTAINS' },
    { source: 'ch10', target: 'a_dbscan', relation: 'CONTAINS' },
    { source: 'ch13', target: 'a_mlp', relation: 'CONTAINS' },
    { source: 'ch14', target: 'a_cnn', relation: 'CONTAINS' },
    { source: 'ch14', target: 'a_rnn', relation: 'CONTAINS' },
    { source: 'ch14', target: 'a_transformer', relation: 'CONTAINS' },
    { source: 'ch14', target: 'a_gan', relation: 'CONTAINS' },
    { source: 'ch17', target: 'a_bert', relation: 'CONTAINS' },
    { source: 'ch17', target: 'a_gpt', relation: 'CONTAINS' },
    { source: 'a_linreg', target: 'c_supervised', relation: 'BELONGS_TO' },
    { source: 'a_logreg', target: 'c_supervised', relation: 'BELONGS_TO' },
    { source: 'a_svm', target: 'c_supervised', relation: 'BELONGS_TO' },
    { source: 'a_rf', target: 'c_supervised', relation: 'BELONGS_TO' },
    { source: 'a_xgboost', target: 'c_supervised', relation: 'BELONGS_TO' },
    { source: 'a_kmeans', target: 'c_unsupervised', relation: 'BELONGS_TO' },
    { source: 'a_dbscan', target: 'c_unsupervised', relation: 'BELONGS_TO' },
    { source: 'a_cnn', target: 'c_supervised', relation: 'BELONGS_TO' },
    { source: 'a_bert', target: 'c_transfer', relation: 'BELONGS_TO' },
    { source: 'a_gpt', target: 'c_transfer', relation: 'BELONGS_TO' },
    { source: 'a_rnn', target: 'a_lstm', relation: 'EXTENDS' },
    { source: 'a_cart', target: 'a_rf', relation: 'BASED_ON' },
    { source: 'a_cnn', target: 'a_resnet', relation: 'EXTENDS' },
    { source: 'a_transformer', target: 'a_bert', relation: 'BASED_ON' },
    { source: 'a_transformer', target: 'a_gpt', relation: 'BASED_ON' },
    { source: 'a_cnn', target: 't_relu', relation: 'USES' },
    { source: 'a_cnn', target: 't_bn', relation: 'USES' },
    { source: 'a_mlp', target: 't_adam', relation: 'USES' },
    { source: 'a_mlp', target: 't_dropout', relation: 'USES' },
    { source: 'a_transformer', target: 't_attention', relation: 'USES' },
    { source: 'a_transformer', target: 't_adam', relation: 'USES' },
    { source: 'a_resnet', target: 't_bn', relation: 'USES' },
    { source: 'a_cnn', target: 'app_img_cls', relation: 'APPLIES_TO' },
    { source: 'a_cnn', target: 'app_obj_det', relation: 'APPLIES_TO' },
    { source: 'a_resnet', target: 'app_img_cls', relation: 'APPLIES_TO' },
    { source: 'a_bert', target: 'app_nlp', relation: 'APPLIES_TO' },
    { source: 'a_rf', target: 'app_rec', relation: 'APPLIES_TO' },
    { source: 'c_overfit', target: 'c_generalization', relation: 'RELATED_TO' },
    { source: 'c_overfit', target: 'c_bias_variance', relation: 'EXPLAINS' },
    { source: 'ch05', target: 'ch02', relation: 'PREREQ' },
    { source: 'ch14', target: 'ch13', relation: 'PREREQ' },
    { source: 'ch09', target: 'ch06', relation: 'PREREQ' },
  ],
  nodeDetails: {
    a_svm: {
      name: '支持向量机 (SVM)',
      type: '算法',
      desc: '支持向量机是一种二分类模型，其基本模型是定义在特征空间上的间隔最大的线性分类器。SVM 通过寻找最大间隔超平面将不同类别的数据分开。核技巧使其能够处理非线性分类问题。',
      related: [
        { name: '逻辑回归', relation: '相似于' },
        { name: '核函数', relation: '依赖' },
        { name: 'RBF核', relation: '使用' },
      ],
    },
    a_transformer: {
      name: 'Transformer',
      type: '算法',
      desc: 'Transformer 是一种基于自注意力机制的序列模型架构，由 Vaswani 等人于 2017 年提出。它摒弃了 RNN 和 CNN，完全依赖注意力机制来捕获全局依赖关系。是现代大语言模型（BERT、GPT）的基础架构。',
      related: [
        { name: '注意力机制', relation: '基于' },
        { name: 'BERT', relation: '衍生' },
        { name: 'GPT', relation: '衍生' },
        { name: 'Adam优化器', relation: '使用' },
      ],
    },
    a_xgboost: {
      name: 'XGBoost',
      type: '算法',
      desc: 'XGBoost（eXtreme Gradient Boosting）是一种高效的梯度提升框架。它在传统 GBDT 基础上加入了正则化项，支持列采样，并能自动处理缺失值。在 Kaggle 等数据竞赛中表现优异。',
      related: [
        { name: 'GBDT', relation: '改进' },
        { name: 'LightGBM', relation: '相似于' },
        { name: '随机森林', relation: '关联' },
      ],
    },
  },
}

// ===== 问答 =====
const qa = {
  sessions: [
    { id: 'sess_001', title: '关于SVM的讨论', time: '10分钟前', course: '机器学习' },
    { id: 'sess_002', title: 'K-Means聚类原理', time: '1小时前', course: '机器学习' },
    { id: 'sess_003', title: '深度学习入门', time: '昨天', course: '机器学习' },
    { id: 'sess_004', title: '关联规则挖掘', time: '2天前', course: '数据挖掘' },
  ],
}

// ===== 数字教师 =====
const teacher = {
  name: '小智老师',
  status: 'online',
  emotions: ['normal', 'happy', 'thinking', 'encouraging'],
  progress: {
    total_questions: 42,
    mastered_topics: ['线性回归', '逻辑回归', 'K-Means'],
    weak_topics: ['SVM核函数', 'DBSCAN参数选择'],
    study_hours: 12.5,
    level: '中级',
  },
}

// ===== 数据分析 =====
const analysis = {
  questionTrend: {
    labels: ['06-01','06-02','06-03','06-04','06-05','06-06','06-07','06-08','06-09','06-10','06-11','06-12','06-13','06-14','06-15','06-16','06-17','06-18','06-19','06-20','06-21','06-22'],
    ml: [5,8,6,10,7,12,9,11,8,15,10,14,12,18,16,8,15,12,20,18,25,12],
    dm: [3,4,5,6,4,7,5,6,4,8,6,9,7,10,8,5,8,7,12,10,14,8],
  },
  topicHeatmap: {
    topics: ['线性回归','逻辑回归','SVM','决策树','神经网络','K-Means','DBSCAN','PCA','关联规则','朴素贝叶斯'],
    courses: ['机器学习', '数据挖掘'],
    matrix: [
      [12, 8, 28, 15, 19, 22, 10, 5, 8, 7],
      [6, 4, 15, 10, 8, 18, 12, 3, 14, 9],
    ],
  },
  userActivity: {
    daily: [
      { date: '06-16', count: 15 }, { date: '06-17', count: 20 },
      { date: '06-18', count: 18 }, { date: '06-19', count: 25 },
      { date: '06-20', count: 22 }, { date: '06-21', count: 30 },
      { date: '06-22', count: 16 },
    ],
    hourly: [
      { hour: '08', count: 5 }, { hour: '09', count: 12 }, { hour: '10', count: 18 },
      { hour: '11', count: 15 }, { hour: '12', count: 8 }, { hour: '13', count: 6 },
      { hour: '14', count: 22 }, { hour: '15', count: 25 }, { hour: '16', count: 20 },
      { hour: '17', count: 12 }, { hour: '18', count: 8 }, { hour: '19', count: 15 },
      { hour: '20', count: 28 }, { hour: '21', count: 18 }, { hour: '22', count: 10 },
    ],
  },
  satisfaction: {
    avg: 4.3, total: 120,
    distribution: { 5: 68, 4: 32, 3: 15, 2: 4, 1: 1 },
  },
  masteryRadar: {
    indicators: ['基础概念', '监督学习', '无监督学习', '深度学习', '模型评估', '特征工程'],
    values: [0.85, 0.72, 0.60, 0.45, 0.68, 0.55],
  },
}

// ===== Mock 路由 =====
export function mockGet(path) {
  // --- 认证 ---
  if (path.includes('/auth/me')) return { code: 200, data: profile }

  // --- 文件管理 ---
  if (path.includes('/files')) return { code: 200, data: files }

  // --- 仪表盘 ---
  if (path.includes('/dashboard/overview')) return { code: 200, data: dashboard }

  // --- 知识图谱 ---
  if (path.includes('/graph/visualization')) return { code: 200, data: graph }

  // --- 问答 ---
  if (path.includes('/qa/sessions')) return { code: 200, data: qa.sessions }

  // --- 数字教师 ---
  if (path.includes('/teacher/avatar')) return { code: 200, data: teacher }

  // --- 数据分析 ---
  if (path.includes('/question-trend')) return { code: 200, data: analysis.questionTrend }
  if (path.includes('/topic-heatmap')) return { code: 200, data: analysis.topicHeatmap }
  if (path.includes('/user-activity')) return { code: 200, data: analysis.userActivity }
  if (path.includes('/satisfaction')) return { code: 200, data: analysis.satisfaction }
  if (path.includes('/mastery-radar')) return { code: 200, data: analysis.masteryRadar }

  // --- 系统 ---
  if (path.includes('/system/health')) return { code: 200, data: systemHealth }
  if (path.includes('/system/model-status')) return { code: 200, data: modelStatus }
  if (path.includes('/system/config')) return { code: 200, data: systemConfig }
  if (path.includes('/system/announcements')) return { code: 200, data: announcements }

  return { code: 404, data: null }
}

export function mockPost(path, body) {
  // --- 认证 ---
  if (path.includes('/auth/login')) {
    return { code: 200, data: { token: authUser.token, user: { ...authUser, token: undefined } } }
  }
  if (path.includes('/auth/register')) {
    return { code: 200, data: { message: '注册成功', user_id: 1002 } }
  }
  if (path.includes('/auth/password')) {
    return { code: 200, data: { message: '密码修改成功' } }
  }

  // --- 文件管理 ---
  if (path.includes('/files/upload')) {
    return { code: 200, data: { message: '文件上传成功', file_id: Date.now() % 100000 } }
  }
  if (path.includes('/files/rebuild-index')) {
    return { code: 200, data: { message: '索引重建任务已提交', task_id: 'idx_' + Date.now() } }
  }

  // --- 系统配置 ---
  if (path.includes('/system/config')) {
    return { code: 200, data: { message: '配置保存成功' } }
  }

  // --- 问答 ---
  if (path.includes('/qa/ask-sync')) {
    const q = body.question || ''
    let answer = ''
    if (q.includes('SVM') || q.includes('支持向量机')) {
      answer = '## 支持向量机（SVM）\n\n支持向量机是一种**二分类模型**，其核心思想是在特征空间中寻找一个**最大间隔超平面**来分隔不同类别的数据。\n\n### 核心概念\n\n1. **最大间隔**：SVM 不仅要求分类正确，还要求分类超平面与最近样本点的距离（间隔）最大化\n2. **支持向量**：距离超平面最近的训练样本点，它们决定了超平面的位置\n3. **核技巧**：通过核函数将数据映射到高维空间，解决非线性分类问题\n\n### 常用核函数\n\n| 核函数 | 适用场景 |\n|--------|----------|\n| 线性核 | 线性可分数据 |\n| RBF核 | 通用，最常用 |\n| 多项式核 | 特定非线性问题 |\n\n**优点**：泛化能力强、适合高维数据\n**缺点**：对大规模数据集训练较慢、参数选择敏感'
    } else if (q.includes('K-Means') || q.includes('聚类')) {
      answer = '## K-Means 聚类算法\n\nK-Means 是一种经典的**无监督学习**算法，用于将数据划分为 K 个簇。\n\n### 算法步骤\n\n1. 随机选择 K 个初始质心\n2. 将每个样本分配到最近的质心\n3. 更新质心为簇内样本均值\n4. 重复步骤 2-3 直到收敛\n\n**优点**：简单高效，适合大规模数据\n**缺点**：需预先指定 K 值，对初始质心敏感'
    } else if (q.includes('决策树')) {
      answer = '## 决策树\n\n决策树是一种基于树结构的**监督学习**分类/回归算法。\n\n### 核心算法\n\n- **ID3**：基于信息增益\n- **C4.5**：基于信息增益比\n- **CART**：基于基尼指数\n\n决策树的优点是**可解释性强**，可以可视化展示决策过程。缺点是容易过拟合，通常需要剪枝处理。'
    } else if (q.includes('Transformer')) {
      answer = '## Transformer 架构\n\nTransformer 是 2017 年 Google 提出的序列模型架构，是现代大语言模型的基础。\n\n### 核心组件\n\n- **自注意力机制 (Self-Attention)**：让模型关注输入序列中的不同位置\n- **多头注意力 (Multi-Head Attention)**：并行计算多个注意力头\n- **位置编码 (Positional Encoding)**：为序列提供位置信息\n- **前馈网络 (FFN)**：两层全连接网络\n\n基于 Transformer 的 BERT 和 GPT 系列模型彻底改变了 NLP 领域。'
    } else {
      answer = `关于「${q}」，这是机器学习中的一个重要概念。\n\n根据知识图谱中的信息，这个知识点涉及多个相关的算法和应用场景。建议你结合教材和课程笔记深入学习，同时可以通过知识图谱页面查看相关的前置知识和关联概念。\n\n如果需要更详细的解释，请告诉我你想了解的具体方面。`
    }
    return {
      code: 200,
      data: {
        answer_id: 'ans_' + Date.now(),
        question: q,
        answer,
        references: [
          { source: '机器学习教材.pdf', page: Math.floor(Math.random() * 200) + 1, score: 0.88 },
          { source: '课程笔记.md', page: null, score: 0.75 },
        ],
        response_time_ms: Math.floor(Math.random() * 2000) + 1000,
      },
    }
  }

  // --- 数字教师 ---
  if (path.includes('/teacher/chat')) {
    const q = body.question || ''
    return {
      code: 200,
      data: {
        answer: `同学你好！关于${q ? '「' + q + '」' : '这个问题'}，让我来给你讲解一下...\n\n这是一个很好的问题，说明你在认真思考。这个知识点的核心在于理解其基本原理和应用场景。建议你先掌握前置知识，然后再深入学习。`,
        emotion: 'encouraging',
        action: 'explain',
      },
    }
  }

  return { code: 200, data: {} }
}
