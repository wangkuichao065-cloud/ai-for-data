// ============================================
// API 封装 - 统一接口调用层
// 支持认证、SSE流式、文件上传、错误处理
// ============================================

const API = {
  BASE_URL: 'http://127.0.0.1:8000',
  USE_MOCK: false,  // 设为 true 使用 Mock 数据（后端未启动时）

  // ---- Token 管理 ----
  getToken() {
    return localStorage.getItem('token') || '';
  },
  setToken(token) {
    localStorage.setItem('token', token);
  },
  clearToken() {
    localStorage.removeItem('token');
  },
  isLoggedIn() {
    return !!this.getToken();
  },

  // ---- 通用请求 ----
  async _request(method, path, body, options) {
    options = options || {};
    var headers = { 'Authorization': 'Bearer ' + this.getToken() };
    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    var fetchOpts = { method: method, headers: headers };
    if (body) {
      fetchOpts.body = body instanceof FormData ? body : JSON.stringify(body);
    }
    if (options.signal) fetchOpts.signal = options.signal;

    var res;
    try {
      res = await fetch(this.BASE_URL + path, fetchOpts);
    } catch (e) {
      return { code: -1, message: '网络请求失败：' + (e.message || '无法连接服务器'), data: null };
    }

    // 处理非JSON响应（如文件下载）
    var contentType = res.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
      if (res.ok) return { code: 200, data: await res.blob(), message: 'OK' };
      return { code: res.status, message: res.statusText, data: null };
    }

    var json = await res.json();

    // 401: Token 过期或无效
    if (res.status === 401) {
      this.clearToken();
      if (window.location.hash !== '#/login') {
        ElementPlus.ElMessage.error('登录已过期，请重新登录');
        setTimeout(function() { window.location.hash = '#/login'; }, 500);
      }
      return { code: 401, message: '未授权', data: null };
    }

    return json;
  },

  async get(path, params) {
    if (this.USE_MOCK) return this._mockRequest('GET', path, null, params);
    var url = new URL(this.BASE_URL + path);
    if (params) {
      Object.entries(params).forEach(function(kv) {
        if (kv[1] !== undefined && kv[1] !== null) url.searchParams.set(kv[0], kv[1]);
      });
    }
    return this._request('GET', url.pathname + url.search);
  },

  async post(path, body) {
    if (this.USE_MOCK) return this._mockRequest('POST', path, body);
    return this._request('POST', path, body || {});
  },

  async put(path, body) {
    if (this.USE_MOCK) return this._mockRequest('PUT', path, body);
    return this._request('PUT', path, body || {});
  },

  async del(path) {
    if (this.USE_MOCK) return this._mockRequest('DELETE', path);
    return this._request('DELETE', path);
  },

  async upload(path, file, extra) {
    var formData = new FormData();
    formData.append('file', file);
    if (extra) {
      Object.entries(extra).forEach(function(kv) { formData.append(kv[0], kv[1]); });
    }
    if (this.USE_MOCK) return this._mockRequest('POST', path, formData);
    return this._request('POST', path, formData);
  },

  // ---- SSE 流式请求 ----
  // 返回一个 async generator，yield { type, data }
  async *stream(path, body) {
    var token = this.getToken();
    var res = await fetch(this.BASE_URL + path, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
      },
      body: JSON.stringify(body || {})
    });

    if (!res.ok) {
      yield { type: 'error', data: '流式请求失败: ' + res.status };
      return;
    }

    var reader = res.body.getReader();
    var decoder = new TextDecoder();
    var buffer = '';

    try {
      while (true) {
        var result = await reader.read();
        if (result.done) break;
        buffer += decoder.decode(result.value, { stream: true });

        var lines = buffer.split('\n');
        buffer = lines.pop();

        for (var i = 0; i < lines.length; i++) {
          var line = lines[i].trim();
          if (!line) continue;
          if (line.startsWith('data: ')) {
            var dataStr = line.substring(6);
            if (dataStr === '[DONE]') { yield { type: 'done', data: null }; return; }
            try {
              var data = JSON.parse(dataStr);
              yield { type: data.type || 'token', data: data };
            } catch (e) {
              yield { type: 'token', data: { content: dataStr } };
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  // ============================================
  //  Auth - 认证接口
  // ============================================
  auth: {
    register(data) { return API.post('/api/v1/auth/register', data); },
    login(username, password) { return API.post('/api/v1/auth/login', { username: username, password: password }); },
    logout() { return API.post('/api/v1/auth/logout'); },
    refresh() { return API.post('/api/v1/auth/refresh'); },
    getProfile() { return API.get('/api/v1/auth/profile'); },
    updateProfile(data) { return API.put('/api/v1/auth/profile', data); },
    changePassword(oldPwd, newPwd) { return API.put('/api/v1/auth/password', { old_password: oldPwd, new_password: newPwd }); },
    listUsers(params) { return API.get('/api/v1/auth/users', params); },
    getUser(id) { return API.get('/api/v1/auth/users/' + id); }
  },

  // ============================================
  //  Graph - 知识图谱接口
  // ============================================
  graph: {
    overview() { return API.get('/api/v1/graph/overview'); },
    courses() { return API.get('/api/v1/graph/courses'); },
    courseTree(code) { return API.get('/api/v1/graph/course/' + code + '/tree'); },
    search(keyword, course) { return API.get('/api/v1/graph/search', { keyword: keyword, course: course }); },
    nodeDetail(nodeId) { return API.get('/api/v1/graph/node/' + nodeId); },
    path(start, end) { return API.get('/api/v1/graph/path', { start: start, end: end }); },
    algorithms(course) { return API.get('/api/v1/graph/algorithms', { course: course }); },
    applications(course) { return API.get('/api/v1/graph/applications', { course: course }); },
    stats() { return API.get('/api/v1/graph/stats'); }
  },

  // ============================================
  //  QA - 智能问答接口
  // ============================================
  qa: {
    listSessions() { return API.get('/api/v1/qa/sessions'); },
    createSession(title, course) { return API.post('/api/v1/qa/sessions', { title: title, course: course }); },
    deleteSession(id) { return API.del('/api/v1/qa/sessions/' + id); },
    ask(question, sessionId, enableRag, enableGraph) {
      return API.post('/api/v1/qa/ask', {
        question: question,
        session_id: sessionId,
        enable_rag: enableRag !== false,
        enable_graph: enableGraph !== false
      });
    },
    // SSE 流式问答 - 返回 async generator
    askStream(question, sessionId, enableRag, enableGraph) {
      return API.stream('/api/v1/qa/ask-stream', {
        question: question,
        session_id: sessionId,
        enable_rag: enableRag !== false,
        enable_graph: enableGraph !== false
      });
    },
    history(sessionId) { return API.get('/api/v1/qa/history/' + sessionId); },
    answerDetail(answerId) { return API.get('/api/v1/qa/answer/' + answerId); },
    feedback(answerId, rating, comment) {
      return API.post('/api/v1/qa/feedback', { answer_id: answerId, rating: rating, comment: comment });
    },
    ragStatus() { return API.get('/api/v1/qa/rag-status'); }
  },

  // ============================================
  //  Teacher - 数字教师接口
  // ============================================
  teacher: {
    chat(question, emotion) {
      return API.post('/api/v1/teacher/chat', { question: question, emotion: emotion || 'normal' });
    },
    stream(question, emotion) {
      return API.stream('/api/v1/teacher/stream', { question: question, emotion: emotion || 'normal' });
    },
    progress() { return API.get('/api/v1/teacher/progress'); },
    voices() { return API.get('/api/v1/teacher/voices'); }
  },

  // ============================================
  //  Dashboard - 数据分析接口
  // ============================================
  dashboard: {
    overview() { return API.get('/api/v1/dashboard/overview'); },
    questionTrend(params) { return API.get('/api/v1/dashboard/question-trend', params); },
    topicHeatmap(params) { return API.get('/api/v1/dashboard/topic-heatmap', params); },
    userActivity(params) { return API.get('/api/v1/dashboard/user-activity', params); },
    satisfaction(params) { return API.get('/api/v1/dashboard/satisfaction', params); },
    mastery(params) { return API.get('/api/v1/dashboard/mastery', params); }
  },

  // ============================================
  //  Files - 文件管理接口
  // ============================================
  files: {
    upload(file, course, tags) { return API.upload('/api/v1/files/upload', file, { course: course, tags: tags || '' }); },
    list(params) { return API.get('/api/v1/files', params); },
    detail(id) { return API.get('/api/v1/files/' + id); },
    download(id) { return API.get('/api/v1/files/' + id + '/download'); },
    rebuildIndex() { return API.post('/api/v1/files/rebuild-index'); }
  },

  // ============================================
  //  System - 系统管理接口
  // ============================================
  system: {
    health() { return API.get('/api/v1/system/health'); },
    modelStatus() { return API.get('/api/v1/system/model-status'); },
    getConfig() { return API.get('/api/v1/system/config'); },
    updateConfig(data) { return API.put('/api/v1/system/config', data); },
    announcements() { return API.get('/api/v1/system/announcements'); }
  },

  // ============================================
  //  Mock 路由（开发用）
  // ============================================
  _mockRequest(method, path, body, params) {
    path = path.replace(/^https?:\/\/[^/]+/, '');

    // Auth
    if (path === '/api/v1/auth/login' && method === 'POST') {
      var u = (body && body.username) || 'student01';
      return Promise.resolve({ code: 200, message: 'OK', data: { token: 'mock_token_' + Date.now(), user: { user_id: 1, username: u, role: 'student', avatar: '', email: 'student@test.com' } } });
    }
    if (path === '/api/v1/auth/register' && method === 'POST') {
      return Promise.resolve({ code: 200, message: '注册成功', data: { user_id: Date.now() } });
    }
    if (path === '/api/v1/auth/profile' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { user_id: 1, username: 'student01', email: 'student@test.com', role: 'student', avatar: '', nickname: '学生01' } });
    }
    if (path === '/api/v1/auth/profile' && method === 'PUT') {
      return Promise.resolve({ code: 200, message: '更新成功', data: null });
    }
    if (path === '/api/v1/auth/password' && method === 'PUT') {
      return Promise.resolve({ code: 200, message: '密码修改成功', data: null });
    }
    if (path === '/api/v1/auth/logout' && method === 'POST') {
      return Promise.resolve({ code: 200, message: '已退出', data: null });
    }

    // Graph
    if (path === '/api/v1/graph/overview' && method === 'GET') {
      return Promise.resolve({ code: 200, data: MockData.graph });
    }
    if (path === '/api/v1/graph/search' && method === 'GET') {
      var kw = (params && params.keyword) || '';
      var results = MockData.graph.nodes.filter(function(n) {
        return n.name.toLowerCase().indexOf(kw.toLowerCase()) >= 0;
      }).slice(0, 10);
      return Promise.resolve({ code: 200, data: { results: results, total: results.length } });
    }
    if (path.match(/^\/api\/v1\/graph\/node\//) && method === 'GET') {
      var nodeId = path.split('/').pop();
      var detail = MockData.graph.nodeDetails[nodeId];
      return Promise.resolve({ code: 200, data: detail || { name: nodeId, type: '未知', desc: '暂无详细信息', related: [] } });
    }
    if (path === '/api/v1/graph/stats' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { total_nodes: MockData.graph.nodes.length, total_edges: MockData.graph.edges.length, courses: 2 } });
    }

    // Dashboard
    if (path === '/api/v1/dashboard/overview' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.dashboard });
    if (path === '/api/v1/dashboard/question-trend' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.analysis.questionTrend });
    if (path === '/api/v1/dashboard/topic-heatmap' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.analysis.topicHeatmap });
    if (path === '/api/v1/dashboard/user-activity' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.analysis.userActivity });
    if (path === '/api/v1/dashboard/satisfaction' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.analysis.satisfaction });
    if (path === '/api/v1/dashboard/mastery' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.analysis.masteryRadar });

    // QA
    if (path === '/api/v1/qa/sessions' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.qa.sessions });
    if (path === '/api/v1/qa/sessions' && method === 'POST') {
      var sid = 'sess_' + Date.now();
      return Promise.resolve({ code: 200, data: { session_id: sid, title: (body && body.title) || '新对话', course: (body && body.course) || 'machine_learning' } });
    }
    if (path === '/api/v1/qa/rag-status' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { total_files: 5, total_chunks: 128, index_size: 512, embedding_model: 'bge-small-zh-v1.5' } });
    }

    // Teacher
    if (path === '/api/v1/teacher/progress' && method === 'GET') return Promise.resolve({ code: 200, data: MockData.teacher });
    if (path === '/api/v1/teacher/voices' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { voices: ['zh-CN-XiaoxiaoNeural', 'zh-CN-YunxiNeural'], default: 'zh-CN-XiaoxiaoNeural' } });
    }

    // Files
    if (path === '/api/v1/files' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { files: [], total: 0 } });
    }
    if (path === '/api/v1/files/upload' && method === 'POST') {
      return Promise.resolve({ code: 200, message: '上传成功', data: { file_id: Date.now(), filename: 'uploaded_file.pdf', chunks: 10 } });
    }

    // System
    if (path === '/api/v1/system/health' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { status: 'healthy', services: { mysql: 'up', neo4j: 'up', ollama: 'up', faiss: 'up' } } });
    }
    if (path === '/api/v1/system/model-status' && method === 'GET') {
      return Promise.resolve({ code: 200, data: { llm: { name: 'deepseek-r1:7b', loaded: true }, embedding: { name: 'bge-small-zh-v1.5', loaded: true }, tts: { name: 'IndexTTS2', loaded: false } } });
    }
    if (path === '/api/v1/system/announcements' && method === 'GET') {
      return Promise.resolve({ code: 200, data: [{ id: 1, title: '系统维护通知', content: '本周六凌晨2:00-4:00进行系统维护', created_at: '2026-06-20T10:00:00' }] });
    }

    return Promise.resolve({ code: 404, message: 'Mock: 未匹配的路径 ' + method + ' ' + path, data: null });
  },

  // ============================================
  //  Mock 流式问答
  // ============================================
  async *_mockStream(path, body) {
    var q = (body && body.question) || '';
    var answer = '';
    if (q.match(/SVM|支持向量机/i)) {
      answer = MockData.qa.sampleQA[1].content;
    } else if (q.match(/K-Means|聚类/i)) {
      answer = '## K-Means 聚类算法\n\nK-Means 是一种经典的**无监督学习**算法，用于将数据划分为 K 个簇。\n\n### 算法步骤\n\n1. 随机选择 K 个初始质心\n2. 将每个样本分配到最近的质心\n3. 更新质心为簇内样本均值\n4. 重复步骤 2-3 直到收敛';
    } else {
      answer = '关于「' + q + '」，这是机器学习中的一个重要概念。\n\n根据知识图谱中的信息，这个知识点涉及多个相关的算法和应用场景。';
    }
    var tokens = answer.split('');
    for (var i = 0; i < tokens.length; i++) {
      yield { type: 'token', data: { content: tokens[i] } };
      await new Promise(function(r) { setTimeout(r, 20); });
    }
    yield { type: 'done', data: null };
  }
};

// 重写 stream 方法以支持 Mock
var _originalStream = API.stream;
API.stream = async function*(path, body) {
  if (this.USE_MOCK) {
    yield* this._mockStream(path, body);
    return;
  }
  yield* _originalStream.call(this, path, body);
};
