// ============================================
// API 封装 - 统一接口调用
// 当前使用 Mock 数据，后端就绪后切换
// ============================================

const API = {
  BASE_URL: 'http://127.0.0.1:8000',
  USE_MOCK: true,  // 设为 false 使用真实后端

  async get(path, params = {}) {
    if (this.USE_MOCK) return this._mockGet(path, params);
    const url = new URL(this.BASE_URL + path);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    const res = await fetch(url, {
      headers: { 'Authorization': 'Bearer ' + (localStorage.getItem('token') || '') }
    });
    return res.json();
  },

  async post(path, body = {}) {
    if (this.USE_MOCK) return this._mockPost(path, body);
    const res = await fetch(this.BASE_URL + path, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + (localStorage.getItem('token') || '')
      },
      body: JSON.stringify(body)
    });
    return res.json();
  },

  // ---- Mock 路由 ----
  _mockGet(path) {
    if (path.includes('/dashboard/overview')) return { code: 200, data: MockData.dashboard };
    if (path.includes('/graph/visualization')) return { code: 200, data: MockData.graph };
    if (path.includes('/qa/sessions')) return { code: 200, data: MockData.qa.sessions };
    if (path.includes('/teacher/avatar')) return { code: 200, data: MockData.teacher };
    if (path.includes('/dashboard/question-trend')) return { code: 200, data: MockData.analysis.questionTrend };
    if (path.includes('/dashboard/topic-heatmap')) return { code: 200, data: MockData.analysis.topicHeatmap };
    if (path.includes('/dashboard/user-activity')) return { code: 200, data: MockData.analysis.userActivity };
    if (path.includes('/dashboard/satisfaction')) return { code: 200, data: MockData.analysis.satisfaction };
    if (path.includes('/dashboard/mastery-radar')) return { code: 200, data: MockData.analysis.masteryRadar };
    return { code: 404, data: null };
  },

  _mockPost(path, body) {
    if (path.includes('/qa/ask-sync')) {
      const q = body.question || '';
      let answer = '这是一个很好的问题！';
      if (q.includes('SVM') || q.includes('支持向量机')) {
        answer = MockData.qa.sampleQA[1].content;
      } else if (q.includes('K-Means') || q.includes('聚类')) {
        answer = '## K-Means 聚类算法\n\nK-Means 是一种经典的**无监督学习**算法，用于将数据划分为 K 个簇。\n\n### 算法步骤\n\n1. 随机选择 K 个初始质心\n2. 将每个样本分配到最近的质心\n3. 更新质心为簇内样本均值\n4. 重复步骤 2-3 直到收敛\n\n### 优缺点\n\n**优点**：简单高效，适合大规模数据\n\n**缺点**：需预先指定 K 值，对初始质心敏感，只能发现球形簇';
      } else if (q.includes('决策树')) {
        answer = '## 决策树\n\n决策树是一种基于树结构的**监督学习**分类/回归算法。\n\n### 核心算法\n\n- **ID3**：基于信息增益\n- **C4.5**：基于信息增益比\n- **CART**：基于基尼指数\n\n决策树的优点是**可解释性强**，可以可视化展示决策过程。缺点是容易过拟合，通常需要剪枝处理。';
      } else if (q.includes('Transformer')) {
        answer = '## Transformer 架构\n\nTransformer 是 2017 年 Google 提出的序列模型架构，是现代大语言模型的基础。\n\n### 核心组件\n\n- **自注意力机制 (Self-Attention)**：让模型关注输入序列中的不同位置\n- **多头注意力 (Multi-Head Attention)**：并行计算多个注意力头\n- **位置编码 (Positional Encoding)**：为序列提供位置信息\n- **前馈网络 (FFN)**：两层全连接网络\n\n### 影响\n\n基于 Transformer 的 BERT 和 GPT 系列模型彻底改变了 NLP 领域。';
      } else {
        answer = `关于「${q}」，这是机器学习中的一个重要概念。\n\n根据知识图谱中的信息，这个知识点涉及多个相关的算法和应用场景。建议你结合教材和课程笔记深入学习，同时可以通过知识图谱页面查看相关的前置知识和关联概念。\n\n如果需要更详细的解释，请告诉我你想了解的具体方面。`;
      }
      return {
        code: 200,
        data: {
          answer_id: 'ans_' + Date.now(),
          question: q,
          answer: answer,
          references: [
            { source: '机器学习教材.pdf', page: Math.floor(Math.random()*200)+1, score: 0.88 },
            { source: '课程笔记.md', page: null, score: 0.75 }
          ],
          response_time_ms: Math.floor(Math.random()*2000)+1000
        }
      };
    }
    if (path.includes('/teacher/chat')) {
      const q = body.question || '';
      return {
        code: 200,
        data: {
          answer: `同学你好！关于${q ? '「' + q + '」' : '这个问题'}，让我来给你讲解一下...\n\n这是一个很好的问题，说明你在认真思考。这个知识点的核心在于理解其基本原理和应用场景。建议你先掌握前置知识，然后再深入学习。`,
          emotion: 'encouraging',
          action: 'explain'
        }
      };
    }
    return { code: 200, data: {} };
  }
};
