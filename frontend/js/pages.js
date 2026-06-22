// ============================================
// Pages - Vue 页面组件定义
// 包含：登录、仪表盘、知识图谱、智能问答、数字教师、数据分析、文件管理、系统管理、个人设置
// ============================================

const { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } = Vue;

// 安全渲染 Markdown（防止 XSS）
function renderMarkdown(text) {
  if (!text) return '';
  try {
    var html = marked.parse(text);
    return DOMPurify.sanitize(html);
  } catch (e) {
    return DOMPurify.sanitize(text);
  }
}

// ============================================
//  0. 登录/注册页面
// ============================================
const LoginPage = {
  template: `
    <div class="login-page">
      <div class="login-bg"></div>
      <div class="login-card">
        <div class="login-header">
          <div class="login-logo">🧠</div>
          <h1 class="login-title">课程数据分析平台</h1>
          <p class="login-subtitle">基于知识图谱与大模型的智能学习系统</p>
        </div>
        <el-tabs v-model="activeTab" stretch>
          <el-tab-pane label="登录" name="login">
            <el-form :model="loginForm" @submit.prevent="handleLogin" label-position="top">
              <el-form-item label="用户名">
                <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
              </el-form-item>
              <el-button type="primary" size="large" style="width:100%; margin-top:8px;" :loading="loading" @click="handleLogin"
                :style="{ background: 'var(--gradient)', border: 'none', height: '44px', fontSize: '16px' }">
                登 录
              </el-button>
              <div class="login-hint">
                <span>还没有账号？</span>
                <el-link type="primary" @click="activeTab = 'register'">立即注册</el-link>
              </div>
            </el-form>
          </el-tab-pane>
          <el-tab-pane label="注册" name="register">
            <el-form :model="registerForm" @submit.prevent="handleRegister" label-position="top">
              <el-form-item label="用户名">
                <el-input v-model="registerForm.username" placeholder="请设置用户名" prefix-icon="User" size="large" />
              </el-form-item>
              <el-form-item label="邮箱">
                <el-input v-model="registerForm.email" placeholder="请输入邮箱" prefix-icon="Message" size="large" />
              </el-form-item>
              <el-form-item label="密码">
                <el-input v-model="registerForm.password" type="password" placeholder="请设置密码（至少6位）" prefix-icon="Lock" size="large" show-password />
              </el-form-item>
              <el-form-item label="角色">
                <el-radio-group v-model="registerForm.role">
                  <el-radio value="student">学生</el-radio>
                  <el-radio value="teacher">教师</el-radio>
                </el-radio-group>
              </el-form-item>
              <el-button type="primary" size="large" style="width:100%; margin-top:8px;" :loading="loading" @click="handleRegister"
                :style="{ background: 'var(--gradient)', border: 'none', height: '44px', fontSize: '16px' }">
                注 册
              </el-button>
              <div class="login-hint">
                <span>已有账号？</span>
                <el-link type="primary" @click="activeTab = 'login'">返回登录</el-link>
              </div>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>
  `,
  setup() {
    var activeTab = ref('login');
    var loading = ref(false);
    var loginForm = reactive({ username: '', password: '' });
    var registerForm = reactive({ username: '', email: '', password: '', role: 'student' });

    async function handleLogin() {
      if (!loginForm.username || !loginForm.password) {
        ElementPlus.ElMessage.warning('请输入用户名和密码');
        return;
      }
      loading.value = true;
      try {
        var res = await API.auth.login(loginForm.username, loginForm.password);
        if (res.code === 200 && res.data && res.data.token) {
          localStorage.setItem('token', res.data.token);
          localStorage.setItem('user', JSON.stringify(res.data.user));
          ElementPlus.ElMessage.success('登录成功');
          window.location.reload();
        } else {
          ElementPlus.ElMessage.error(res.message || '登录失败');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('登录失败：' + (e.message || '网络错误'));
      }
      loading.value = false;
    }

    async function handleRegister() {
      if (!registerForm.username || !registerForm.password) {
        ElementPlus.ElMessage.warning('请填写完整信息');
        return;
      }
      if (registerForm.password.length < 6) {
        ElementPlus.ElMessage.warning('密码至少6位');
        return;
      }
      loading.value = true;
      try {
        var res = await API.auth.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          role: registerForm.role
        });
        if (res.code === 200) {
          ElementPlus.ElMessage.success('注册成功，请登录');
          activeTab.value = 'login';
          loginForm.username = registerForm.username;
          loginForm.password = '';
        } else {
          ElementPlus.ElMessage.error(res.message || '注册失败');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('注册失败：' + (e.message || '网络错误'));
      }
      loading.value = false;
    }

    return { activeTab, loading, loginForm, registerForm, handleLogin, handleRegister };
  }
};

// ============================================
//  1. 仪表盘页面
// ============================================
const DashboardPage = {
  template: `
    <div class="dashboard-page">
      <div v-if="loading" class="page-loading">
        <el-skeleton :rows="6" animated />
      </div>
      <template v-else>
        <!-- KPI 卡片 -->
        <div class="kpi-grid">
          <div class="kpi-card" v-for="kpi in kpiList" :key="kpi.label">
            <div class="kpi-icon" :class="kpi.color">{{ kpi.icon }}</div>
            <div class="kpi-content">
              <div class="kpi-label">{{ kpi.label }}</div>
              <div class="kpi-value">{{ kpi.value }}</div>
              <div class="kpi-change" :class="kpi.dir">{{ kpi.change }}</div>
            </div>
          </div>
        </div>

        <!-- 图表行 -->
        <div class="chart-grid">
          <div class="card">
            <div class="card-title">提问趋势（近7天）</div>
            <div ref="trendRef" class="chart-container"></div>
          </div>
          <div class="card">
            <div class="card-title">课程提问分布</div>
            <div ref="pieRef" class="chart-container"></div>
          </div>
        </div>

        <!-- 热门知识点 -->
        <div class="card">
          <div class="card-title">热门知识点</div>
          <div class="progress-list">
            <div class="progress-item" v-for="t in topics" :key="t.topic">
              <span class="progress-label">{{ t.topic }}</span>
              <div class="progress-bar-bg">
                <div class="progress-bar-fill" :style="{ width: (t.progress * 100) + '%' }"></div>
              </div>
              <span class="progress-value">{{ Math.round(t.progress * 100) }}%</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  `,
  setup() {
    var trendRef = ref(null);
    var pieRef = ref(null);
    var kpiList = ref([]);
    var topics = ref([]);
    var loading = ref(true);
    var charts = [];

    onMounted(async function() {
      try {
        var res = await API.dashboard.overview();
        if (res.code !== 200) { ElementPlus.ElMessage.error(res.message || '加载失败'); loading.value = false; return; }
        var d = res.data;
        kpiList.value = [
          { label: '总提问数', value: d.kpis.total_questions, icon: '💬', color: 'purple', change: '+12 本周', dir: 'up' },
          { label: '今日提问', value: d.kpis.today_questions, icon: '📝', color: 'blue', change: '+3 较昨日', dir: 'up' },
          { label: '总用户数', value: d.kpis.total_users, icon: '👥', color: 'green', change: '+5 本周', dir: 'up' },
          { label: '活跃用户', value: d.kpis.active_users, icon: '🔥', color: 'orange', change: '48% 活跃率', dir: 'up' },
          { label: '知识覆盖率', value: Math.round(d.kpis.knowledge_coverage * 100) + '%', icon: '📚', color: 'pink', change: '+5% 本月', dir: 'up' },
          { label: '平均满意度', value: d.kpis.avg_satisfaction.toFixed(1), icon: '⭐', color: 'cyan', change: '4.3 / 5.0', dir: 'up' }
        ];
        topics.value = d.popular_topics || [];

        loading.value = false;
        await nextTick();
        if (trendRef.value) charts.push(Charts.dashTrend(trendRef.value, d.question_trend));
        if (pieRef.value) charts.push(Charts.dashPie(pieRef.value, d.course_distribution));
      } catch (e) {
        loading.value = false;
        ElementPlus.ElMessage.error('仪表盘加载失败');
      }
    });

    onUnmounted(function() { charts.forEach(function(c) { c.dispose(); }); });

    return { trendRef, pieRef, kpiList, topics, loading };
  }
};

// ============================================
//  2. 知识图谱页面
// ============================================
const KnowledgeGraphPage = {
  template: `
    <div class="graph-page">
      <!-- 工具栏 -->
      <div class="graph-toolbar">
        <el-select v-model="courseFilter" placeholder="选择课程" clearable style="width: 160px" @change="loadGraph">
          <el-option label="全部课程" value=""></el-option>
          <el-option label="机器学习" value="machine_learning"></el-option>
          <el-option label="数据挖掘" value="data_mining"></el-option>
        </el-select>
        <el-input v-model="searchKey" placeholder="搜索知识点..." prefix-icon="Search" clearable style="width: 240px" @keyup.enter="onSearch" />
        <el-button type="primary" @click="onSearch" :style="{ background: 'var(--gradient)', border: 'none' }">搜索</el-button>
        <div style="flex:1"></div>
        <el-tag v-for="(cat, i) in categories" :key="i" :color="cat.color" effect="dark" size="small" style="border:none; color:#fff;">{{ cat.name }}</el-tag>
      </div>

      <!-- 图谱 -->
      <div class="graph-wrapper">
        <div ref="graphRef" class="graph-canvas"></div>

        <!-- 详情面板 -->
        <div class="graph-detail-panel" :class="{ open: detailOpen }">
          <div class="detail-header">
            <span class="detail-title">{{ detail.name }}</span>
            <el-button text @click="detailOpen = false" :icon="'Close'" circle size="small" />
          </div>
          <span class="detail-tag" :style="{ background: tagColor, color: '#fff' }">{{ detail.type }}</span>
          <p class="detail-desc">{{ detail.desc }}</p>
          <div class="detail-section" v-if="detail.related && detail.related.length">
            <div class="detail-section-title">关联知识点</div>
            <div class="detail-related-item" v-for="(r, i) in detail.related" :key="i">
              <span>🔗</span>
              <span style="flex:1">{{ r.name }}</span>
              <el-tag size="small" type="info">{{ r.relation }}</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  setup() {
    var graphRef = ref(null);
    var courseFilter = ref('');
    var searchKey = ref('');
    var categories = ref([]);
    var detailOpen = ref(false);
    var detail = ref({ name: '', type: '', desc: '', related: [] });
    var tagColor = ref('#6366f1');
    var chart = null;

    async function loadGraph() {
      try {
        var res = await API.graph.overview();
        if (res.code !== 200) { ElementPlus.ElMessage.error(res.message || '加载图谱失败'); return; }
        var d = res.data;
        categories.value = d.categories;

        await nextTick();
        if (chart) chart.dispose();
        if (graphRef.value) {
          chart = Charts.knowledgeGraph(graphRef.value, d, function(node) {
            // 调用后端获取节点详情
            API.graph.nodeDetail(node.id).then(function(res) {
              if (res.code === 200 && res.data) {
                detail.value = res.data;
                tagColor.value = d.categories[node.category] ? d.categories[node.category].color : '#6366f1';
                detailOpen.value = true;
              } else {
                // 回退到本地数据
                var det = d.nodeDetails && d.nodeDetails[node.id];
                if (det) {
                  detail.value = det;
                } else {
                  detail.value = {
                    name: node.name,
                    type: d.categories[node.category] ? d.categories[node.category].name : '未知',
                    desc: '暂无详细信息',
                    related: []
                  };
                }
                tagColor.value = d.categories[node.category] ? d.categories[node.category].color : '#6366f1';
                detailOpen.value = true;
              }
            });
          });
        }
      } catch (e) {
        ElementPlus.ElMessage.error('加载图谱失败');
      }
    }

    onMounted(loadGraph);

    onUnmounted(function() { if (chart) chart.dispose(); });

    async function onSearch() {
      if (!searchKey.value.trim()) return;
      try {
        var res = await API.graph.search(searchKey.value, courseFilter.value || null);
        if (res.code === 200 && res.data && res.data.results) {
          var results = res.data.results;
          if (results.length === 0) {
            ElementPlus.ElMessage.info('未找到相关知识点');
            return;
          }
          if (results.length === 1) {
            detail.value = results[0];
            detailOpen.value = true;
          } else {
            // 高亮搜索结果
            ElementPlus.ElMessage.success('找到 ' + results.length + ' 个相关知识点');
          }
        } else {
          ElementPlus.ElMessage.info(res.message || '未找到结果');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('搜索失败');
      }
    }

    return { graphRef, courseFilter, searchKey, categories, detailOpen, detail, tagColor, onSearch, loadGraph };
  }
};

// ============================================
//  3. 智能问答页面
// ============================================
const QAPage = {
  template: `
    <div class="qa-layout">
      <!-- 左侧会话列表 -->
      <div class="qa-sidebar">
        <div class="qa-sidebar-header">
          <el-button type="primary" style="width:100%; background: var(--gradient); border:none;" @click="newSession">
            + 新对话
          </el-button>
        </div>
        <div class="qa-session-list">
          <div
            class="qa-session-item"
            :class="{ active: s.session_id === currentSession }"
            v-for="s in sessions"
            :key="s.session_id"
            @click="switchSession(s.session_id)"
          >
            <div class="qa-session-title">{{ s.title }}</div>
            <div class="qa-session-time">{{ s.course || '通用' }} · {{ formatTime(s.created_at) }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区 -->
      <div class="qa-main">
        <div class="qa-messages" ref="msgRef">
          <!-- 空状态 -->
          <div v-if="messages.length === 0 && !loading" style="text-align:center; padding:60px 0; color: var(--text-muted);">
            <div style="font-size:48px; margin-bottom:16px;">🤖</div>
            <div style="font-size:16px; margin-bottom:8px;">你好！我是课程智能助手</div>
            <div style="font-size:13px;">试试问我关于机器学习或数据挖掘的任何问题</div>
            <div style="margin-top:24px;">
              <el-tag v-for="q in suggestions" :key="q" @click="quickAsk(q)" style="cursor:pointer; margin:4px;" effect="plain">
                {{ q }}
              </el-tag>
            </div>
          </div>

          <div v-for="(m, i) in messages" :key="i" class="qa-message" :class="m.role">
            <div class="qa-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
              {{ m.role === 'user' ? '我' : 'AI' }}
            </div>
            <div>
              <div class="qa-bubble" v-html="renderMd(m.content)"></div>
              <!-- 引用来源 -->
              <div class="qa-references" v-if="m.references && m.references.length">
                <div class="qa-ref-item" v-for="(r, j) in m.references" :key="j">
                  📄 {{ r.source }}
                  <span v-if="r.page"> (第{{ r.page }}页)</span>
                  <el-tag size="small" type="info" style="margin-left:4px;">{{ (r.score * 100).toFixed(0) }}%</el-tag>
                </div>
              </div>
              <!-- 反馈按钮 -->
              <div class="qa-feedback" v-if="m.role === 'assistant' && m.answer_id && !m.feedbackGiven">
                <el-button text size="small" @click="giveFeedback(m, 5)" :type="m.feedback === 5 ? 'success' : ''">
                  👍 有帮助
                </el-button>
                <el-button text size="small" @click="giveFeedback(m, 1)" :type="m.feedback === 1 ? 'danger' : ''">
                  👎 需改进
                </el-button>
              </div>
            </div>
          </div>

          <!-- 加载指示器 -->
          <div v-if="loading" class="qa-message assistant">
            <div class="qa-avatar ai">AI</div>
            <div class="qa-bubble">
              <span v-html="streamingContent"></span><span class="cursor-blink">|</span>
            </div>
          </div>
        </div>

        <!-- 输入区 -->
        <div class="qa-input-area">
          <el-input
            v-model="question"
            type="textarea"
            :rows="2"
            placeholder="输入你的问题，例如：什么是支持向量机？"
            @keydown.enter.exact.prevent="sendQuestion"
          />
          <el-button class="qa-send-btn" @click="sendQuestion" :loading="loading">
            发送
          </el-button>
        </div>
      </div>
    </div>
  `,
  setup() {
    var msgRef = ref(null);
    var sessions = ref([]);
    var currentSession = ref('');
    var messages = ref([]);
    var question = ref('');
    var loading = ref(false);
    var streamingContent = ref('');
    var suggestions = ['什么是支持向量机？', '解释K-Means聚类算法', '决策树和随机森林的区别', '什么是梯度下降？'];

    function formatTime(t) {
      if (!t) return '';
      var d = new Date(t);
      var now = new Date();
      var diff = (now - d) / 1000;
      if (diff < 60) return '刚刚';
      if (diff < 3600) return Math.floor(diff / 60) + '分钟前';
      if (diff < 86400) return Math.floor(diff / 3600) + '小时前';
      return d.toLocaleDateString();
    }

    function renderMd(text) { return renderMarkdown(text); }

    function scrollToBottom() {
      nextTick(function() {
        if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight;
      });
    }

    onMounted(async function() {
      try {
        var res = await API.qa.listSessions();
        if (res.code === 200) {
          sessions.value = Array.isArray(res.data) ? res.data : (res.data.sessions || []);
          if (sessions.value.length) {
            currentSession.value = sessions.value[0].session_id;
            loadHistory(currentSession.value);
          }
        }
      } catch (e) { /* 静默 */ }
    });

    async function loadHistory(sessionId) {
      try {
        var res = await API.qa.history(sessionId);
        if (res.code === 200 && res.data) {
          var history = Array.isArray(res.data) ? res.data : (res.data.messages || []);
          messages.value = history.map(function(m) {
            return { role: m.role || (m.is_user ? 'user' : 'assistant'), content: m.content || m.answer || '', answer_id: m.answer_id, references: m.references || [] };
          });
          scrollToBottom();
        }
      } catch (e) { /* 静默 */ }
    }

    function switchSession(id) {
      currentSession.value = id;
      loadHistory(id);
    }

    async function newSession() {
      try {
        var res = await API.qa.createSession('新对话', 'machine_learning');
        if (res.code === 200 && res.data) {
          sessions.value.unshift(res.data);
          currentSession.value = res.data.session_id;
          messages.value = [];
        }
      } catch (e) {
        ElementPlus.ElMessage.error('创建会话失败');
      }
    }

    function quickAsk(q) {
      question.value = q;
      sendQuestion();
    }

    async function sendQuestion() {
      var q = question.value.trim();
      if (!q || loading.value) return;
      if (!currentSession.value) {
        // 自动创建会话
        await newSession();
      }

      messages.value.push({ role: 'user', content: q });
      question.value = '';
      loading.value = true;
      streamingContent.value = '';
      scrollToBottom();

      try {
        // 使用 SSE 流式问答
        var stream = API.qa.askStream(q, currentSession.value, true, true);
        var fullContent = '';
        var answerId = null;
        var references = [];

        for await (var chunk of stream) {
          if (chunk.type === 'token' && chunk.data) {
            fullContent += chunk.data.content || '';
            streamingContent.value = renderMarkdown(fullContent);
            scrollToBottom();
          } else if (chunk.type === 'references' && chunk.data) {
            references = chunk.data.references || [];
          } else if (chunk.type === 'done') {
            if (chunk.data) {
              answerId = chunk.data.answer_id || answerId;
              references = chunk.data.references || references;
            }
          } else if (chunk.type === 'error') {
            fullContent += '\n\n⚠️ ' + chunk.data;
            streamingContent.value = renderMarkdown(fullContent);
          }
        }

        // 流结束，将完整内容移入消息列表
        messages.value.push({
          role: 'assistant',
          content: fullContent || '抱歉，我无法回答这个问题。',
          answer_id: answerId,
          references: references,
          feedbackGiven: false
        });
      } catch (e) {
        // 回退到非流式
        try {
          var res = await API.qa.ask(q, currentSession.value, true, true);
          if (res.code === 200 && res.data) {
            messages.value.push({
              role: 'assistant',
              content: res.data.answer || '无回答',
              answer_id: res.data.answer_id,
              references: res.data.references || [],
              feedbackGiven: false
            });
          } else {
            messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用：' + (res.message || '') });
          }
        } catch (e2) {
          messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后重试。' });
        }
      }
      loading.value = false;
      streamingContent.value = '';
      scrollToBottom();
    }

    async function giveFeedback(message, rating) {
      if (!message.answer_id) return;
      try {
        var res = await API.qa.feedback(message.answer_id, rating, '');
        if (res.code === 200) {
          message.feedback = rating;
          message.feedbackGiven = true;
          ElementPlus.ElMessage.success(rating === 5 ? '感谢反馈！' : '已记录，我们会改进');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('反馈提交失败');
      }
    }

    return { msgRef, sessions, currentSession, messages, question, loading, streamingContent, suggestions, formatTime, renderMd, sendQuestion, newSession, switchSession, quickAsk, giveFeedback };
  }
};

// ============================================
//  4. 数字教师页面
// ============================================
const TeacherPage = {
  template: `
    <div class="teacher-layout">
      <!-- 左侧：教师形象 -->
      <div class="teacher-avatar-section">
        <div class="teacher-avatar-bg"></div>
        <div class="teacher-avatar-img">
          <span class="avatar-placeholder">👩‍🏫</span>
        </div>
        <div class="teacher-name">{{ teacher.name || '小智老师' }}</div>
        <div class="teacher-status">
          <span class="status-dot" :class="teacher.status"></span>
          {{ teacher.status === 'online' ? '在线' : '离线' }}
        </div>
        <div class="teacher-emotions">
          <button
            class="emotion-btn"
            :class="{ active: currentEmotion === e }"
            v-for="e in emotions"
            :key="e"
            @click="currentEmotion = e"
          >{{ emotionLabel(e) }}</button>
        </div>

        <!-- 学习进度 -->
        <div style="width:100%; margin-top:24px; position:relative; z-index:1;">
          <div class="card" style="padding:16px;">
            <div class="card-title" style="font-size:14px;">学习进度</div>
            <div style="display:flex; gap:16px; margin-bottom:12px;">
              <div style="flex:1; text-align:center;">
                <div style="font-size:22px; font-weight:700; color:var(--primary);">{{ progress.total_questions || 0 }}</div>
                <div style="font-size:12px; color:var(--text-muted);">总提问</div>
              </div>
              <div style="flex:1; text-align:center;">
                <div style="font-size:22px; font-weight:700; color:var(--primary);">{{ (progress.study_hours || 0).toFixed(1) }}h</div>
                <div style="font-size:12px; color:var(--text-muted);">学习时长</div>
              </div>
              <div style="flex:1; text-align:center;">
                <div style="font-size:22px; font-weight:700; color:var(--primary);">{{ progress.level || '初级' }}</div>
                <div style="font-size:12px; color:var(--text-muted);">当前等级</div>
              </div>
            </div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;" v-if="progress.mastered_topics && progress.mastered_topics.length">已掌握</div>
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:8px;">
              <el-tag size="small" type="success" v-for="t in (progress.mastered_topics || [])" :key="t">{{ t }}</el-tag>
            </div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;" v-if="progress.weak_topics && progress.weak_topics.length">待加强</div>
            <div style="display:flex; flex-wrap:wrap; gap:4px;">
              <el-tag size="small" type="warning" v-for="t in (progress.weak_topics || [])" :key="t">{{ t }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对话 -->
      <div class="teacher-chat-section">
        <div class="teacher-chat-header">与{{ teacher.name || '小智老师' }}对话</div>
        <div class="teacher-chat-messages" ref="chatRef">
          <div v-if="chatMessages.length === 0 && !chatLoading" style="text-align:center; padding:50px 0; color:var(--text-muted);">
            <div style="font-size:40px; margin-bottom:12px;">👋</div>
            <div>向{{ teacher.name || '小智老师' }}提问吧！</div>
          </div>

          <div v-for="(m, i) in chatMessages" :key="i" class="qa-message" :class="m.role">
            <div class="qa-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
              {{ m.role === 'user' ? '我' : '师' }}
            </div>
            <div>
              <div class="qa-bubble" v-html="renderMd(m.content)"></div>
              <div v-if="m.emotion" style="margin-top:4px;">
                <el-tag size="small" effect="plain">{{ emotionLabel(m.emotion) }}</el-tag>
              </div>
            </div>
          </div>

          <div v-if="chatLoading" class="qa-message assistant">
            <div class="qa-avatar ai">师</div>
            <div class="qa-bubble">
              <span v-html="streamingContent"></span><span class="cursor-blink">|</span>
            </div>
          </div>
        </div>

        <div class="teacher-chat-input">
          <el-input v-model="chatInput" placeholder="向老师提问..." @keydown.enter="sendChat" />
          <el-button type="primary" @click="sendChat" :loading="chatLoading" :style="{ background: 'var(--gradient)', border: 'none' }">
            发送
          </el-button>
        </div>
      </div>
    </div>
  `,
  setup() {
    var chatRef = ref(null);
    var teacher = ref({ name: '小智老师', status: 'online' });
    var progress = ref({ total_questions: 0, mastered_topics: [], weak_topics: [], study_hours: 0, level: '初级' });
    var emotions = ['normal', 'happy', 'thinking', 'encouraging'];
    var currentEmotion = ref('normal');
    var chatMessages = ref([]);
    var chatInput = ref('');
    var chatLoading = ref(false);
    var streamingContent = ref('');

    function emotionLabel(e) {
      var map = { normal: '平静', happy: '开心', thinking: '思考', encouraging: '鼓励' };
      return map[e] || e;
    }

    function renderMd(text) { return renderMarkdown(text); }

    function scrollToBottom() {
      nextTick(function() {
        if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight;
      });
    }

    onMounted(async function() {
      try {
        var res = await API.teacher.progress();
        if (res.code === 200 && res.data) {
          teacher.value = { name: res.data.name || '小智老师', status: res.data.status || 'online' };
          progress.value = res.data.progress || res.data;
          if (res.data.emotions) emotions = res.data.emotions;
        }
      } catch (e) { /* 静默 */ }
    });

    async function sendChat() {
      var q = chatInput.value.trim();
      if (!q || chatLoading.value) return;
      chatMessages.value.push({ role: 'user', content: q });
      chatInput.value = '';
      chatLoading.value = true;
      streamingContent.value = '';
      scrollToBottom();

      try {
        var stream = API.teacher.stream(q, currentEmotion.value);
        var fullContent = '';
        var emotion = '';

        for await (var chunk of stream) {
          if (chunk.type === 'token' && chunk.data) {
            fullContent += chunk.data.content || '';
            streamingContent.value = renderMarkdown(fullContent);
            scrollToBottom();
          } else if (chunk.type === 'emotion' && chunk.data) {
            emotion = chunk.data.emotion || '';
          } else if (chunk.type === 'done') {
            if (chunk.data && chunk.data.emotion) emotion = chunk.data.emotion;
          }
        }

        chatMessages.value.push({ role: 'assistant', content: fullContent || '...', emotion: emotion });
      } catch (e) {
        // 回退到非流式
        try {
          var res = await API.teacher.chat(q, currentEmotion.value);
          if (res.code === 200 && res.data) {
            chatMessages.value.push({ role: 'assistant', content: res.data.answer || '...', emotion: res.data.emotion });
          } else {
            chatMessages.value.push({ role: 'assistant', content: '抱歉，老师暂时不在线，请稍后再试。' });
          }
        } catch (e2) {
          chatMessages.value.push({ role: 'assistant', content: '抱歉，老师暂时不在线，请稍后再试。' });
        }
      }
      chatLoading.value = false;
      streamingContent.value = '';
      scrollToBottom();
    }

    return { chatRef, teacher, progress, emotions, currentEmotion, chatMessages, chatInput, chatLoading, streamingContent, emotionLabel, renderMd, sendChat };
  }
};

// ============================================
//  5. 数据分析页面
// ============================================
const AnalysisPage = {
  template: `
    <div class="analysis-page">
      <!-- 筛选栏 -->
      <div class="analysis-filters">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="default"
          style="width:300px;"
          value-format="YYYY-MM-DD"
        />
        <el-select v-model="courseFilter" placeholder="课程" clearable style="width:140px">
          <el-option label="全部" value=""></el-option>
          <el-option label="机器学习" value="machine_learning"></el-option>
          <el-option label="数据挖掘" value="data_mining"></el-option>
        </el-select>
        <el-button type="primary" @click="loadAll" :loading="loading" :style="{ background: 'var(--gradient)', border: 'none' }">查询</el-button>
      </div>

      <div v-if="loading" class="page-loading"><el-skeleton :rows="12" animated /></div>
      <template v-else>
        <!-- 趋势 + 热力图 -->
        <div class="chart-grid">
          <div class="card">
            <div class="card-title">提问趋势分析</div>
            <div ref="trendRef" class="chart-container-lg"></div>
          </div>
          <div class="card">
            <div class="card-title">知识点热度</div>
            <div ref="heatRef" class="chart-container-lg"></div>
          </div>
        </div>

        <!-- 活跃 + 满意度 + 雷达 -->
        <div class="chart-grid" style="grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));">
          <div class="card">
            <div class="card-title">每日活跃用户</div>
            <div ref="activityRef" class="chart-container"></div>
          </div>
          <div class="card">
            <div class="card-title">活跃时段分布</div>
            <div ref="hourlyRef" class="chart-container"></div>
          </div>
        </div>

        <div class="chart-grid">
          <div class="card">
            <div class="card-title">满意度分布</div>
            <div ref="satRef" class="chart-container"></div>
          </div>
          <div class="card">
            <div class="card-title">知识掌握度</div>
            <div ref="radarRef" class="chart-container"></div>
          </div>
        </div>
      </template>
    </div>
  `,
  setup() {
    var trendRef = ref(null);
    var heatRef = ref(null);
    var activityRef = ref(null);
    var hourlyRef = ref(null);
    var satRef = ref(null);
    var radarRef = ref(null);
    var dateRange = ref(null);
    var courseFilter = ref('');
    var loading = ref(true);
    var allCharts = [];

    function buildParams() {
      var params = {};
      if (courseFilter.value) params.course = courseFilter.value;
      if (dateRange.value && dateRange.value.length === 2) {
        params.start_date = dateRange.value[0];
        params.end_date = dateRange.value[1];
      }
      return params;
    }

    async function loadAll() {
      loading.value = true;
      // 释放旧图表
      allCharts.forEach(function(c) { c.dispose(); });
      allCharts = [];

      try {
        var params = buildParams();
        // 并行请求
        var results = await Promise.all([
          API.dashboard.questionTrend(params),
          API.dashboard.topicHeatmap(params),
          API.dashboard.userActivity(params),
          API.dashboard.satisfaction(params),
          API.dashboard.mastery(params)
        ]);

        await nextTick();

        if (results[0].code === 200 && trendRef.value)
          allCharts.push(Charts.analysisTrend(trendRef.value, results[0].data));
        if (results[1].code === 200 && heatRef.value)
          allCharts.push(Charts.topicHeatmap(heatRef.value, results[1].data));
        if (results[2].code === 200) {
          if (activityRef.value) allCharts.push(Charts.userActivityBar(activityRef.value, results[2].data));
          if (hourlyRef.value) allCharts.push(Charts.hourlyActivity(hourlyRef.value, results[2].data));
        }
        if (results[3].code === 200 && satRef.value)
          allCharts.push(Charts.satisfaction(satRef.value, results[3].data));
        if (results[4].code === 200 && radarRef.value)
          allCharts.push(Charts.masteryRadar(radarRef.value, results[4].data));
      } catch (e) {
        ElementPlus.ElMessage.error('数据加载失败');
      }
      loading.value = false;
    }

    onMounted(loadAll);

    onUnmounted(function() { allCharts.forEach(function(c) { c.dispose(); }); });

    return { trendRef, heatRef, activityRef, hourlyRef, satRef, radarRef, dateRange, courseFilter, loading, loadAll };
  }
};

// ============================================
//  6. 文件管理页面
// ============================================
const FilesPage = {
  template: `
    <div class="files-page">
      <div class="card" style="margin-bottom:20px;">
        <div class="card-title">上传文件</div>
        <el-upload
          ref="uploadRef"
          :http-request="customUpload"
          :on-success="onUploadSuccess"
          :on-error="onUploadError"
          :before-upload="beforeUpload"
          drag
          accept=".pdf,.txt,.docx,.md"
          style="width:100%;"
        >
          <el-icon class="el-icon--upload"><component :is="'UploadFilled'" /></el-icon>
          <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
          <template #tip>
            <div class="el-upload__tip">支持 PDF、TXT、DOCX、MD 格式，文件不超过 50MB</div>
          </template>
        </el-upload>
        <div style="margin-top:12px; display:flex; gap:12px; align-items:center;">
          <el-select v-model="uploadCourse" placeholder="选择课程" style="width:200px;">
            <el-option label="机器学习" value="machine_learning"></el-option>
            <el-option label="数据挖掘" value="data_mining"></el-option>
          </el-select>
          <el-input v-model="uploadTags" placeholder="标签（逗号分隔）" style="width:300px;"></el-input>
        </div>
      </div>

      <div class="card">
        <div class="card-title" style="display:flex; justify-content:space-between; align-items:center;">
          <span>文件列表</span>
          <el-button size="small" @click="loadFiles" :loading="tableLoading">刷新</el-button>
        </div>
        <el-table :data="fileList" style="width:100%;" v-loading="tableLoading" stripe>
          <el-table-column prop="filename" label="文件名" min-width="200" />
          <el-table-column prop="course" label="课程" width="120" />
          <el-table-column prop="file_type" label="类型" width="80" />
          <el-table-column prop="file_size" label="大小" width="100">
            <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
          </el-table-column>
          <el-table-column prop="chunk_count" label="分块数" width="80" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'ready' ? 'success' : 'warning'" size="small">
                {{ row.status === 'ready' ? '已索引' : '处理中' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="上传时间" width="180">
            <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button text size="small" @click="downloadFile(row)">下载</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 重建索引 -->
      <div class="card" style="margin-top:20px;">
        <div class="card-title">向量索引管理</div>
        <el-button type="warning" @click="rebuildIndex" :loading="rebuilding">重建 FAISS 索引</el-button>
        <span style="margin-left:12px; color: var(--text-muted); font-size:13px;">
          重建索引会重新计算所有文件的向量，适用于切换 Embedding 模型后
        </span>
      </div>
    </div>
  `,
  setup() {
    var uploadRef = ref(null);
    var uploadCourse = ref('machine_learning');
    var uploadTags = ref('');
    var fileList = ref([]);
    var tableLoading = ref(false);
    var rebuilding = ref(false);

    function formatSize(bytes) {
      if (!bytes) return '-';
      if (bytes < 1024) return bytes + ' B';
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
      return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    function formatTime(t) {
      if (!t) return '-';
      return new Date(t).toLocaleString('zh-CN');
    }

    async function loadFiles() {
      tableLoading.value = true;
      try {
        var res = await API.files.list({ page: 1, page_size: 100 });
        if (res.code === 200 && res.data) {
          fileList.value = Array.isArray(res.data) ? res.data : (res.data.files || []);
        }
      } catch (e) {
        ElementPlus.ElMessage.error('加载文件列表失败');
      }
      tableLoading.value = false;
    }

    function beforeUpload(file) {
      var maxSize = 50 * 1024 * 1024;
      if (file.size > maxSize) {
        ElementPlus.ElMessage.error('文件大小不能超过 50MB');
        return false;
      }
      return true;
    }

    async function customUpload(options) {
      try {
        var res = await API.files.upload(options.file, uploadCourse.value, uploadTags.value);
        if (res.code === 200) {
          ElementPlus.ElMessage.success('上传成功');
          loadFiles();
        } else {
          ElementPlus.ElMessage.error(res.message || '上传失败');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('上传失败：' + (e.message || ''));
      }
    }

    function onUploadSuccess() {}
    function onUploadError() { ElementPlus.ElMessage.error('文件上传失败'); }

    async function downloadFile(row) {
      try {
        var res = await API.files.download(row.file_id);
        if (res.code === 200 && res.data instanceof Blob) {
          var url = URL.createObjectURL(res.data);
          var a = document.createElement('a');
          a.href = url;
          a.download = row.filename;
          a.click();
          URL.revokeObjectURL(url);
        }
      } catch (e) {
        ElementPlus.ElMessage.error('下载失败');
      }
    }

    async function rebuildIndex() {
      try {
        await ElementPlus.ElMessageBox.confirm('确定要重建所有向量索引吗？此操作可能需要较长时间。', '确认', {
          confirmButtonText: '确定重建',
          cancelButtonText: '取消',
          type: 'warning'
        });
        rebuilding.value = true;
        var res = await API.files.rebuildIndex();
        if (res.code === 200) {
          ElementPlus.ElMessage.success('索引重建成功');
        } else {
          ElementPlus.ElMessage.error(res.message || '重建失败');
        }
      } catch (e) { /* 取消 */ }
      rebuilding.value = false;
    }

    onMounted(loadFiles);

    return { uploadRef, uploadCourse, uploadTags, fileList, tableLoading, rebuilding, formatSize, formatTime, loadFiles, beforeUpload, customUpload, onUploadSuccess, onUploadError, downloadFile, rebuildIndex };
  }
};

// ============================================
//  7. 系统管理页面
// ============================================
const SystemPage = {
  template: `
    <div class="system-page">
      <!-- 健康检查 -->
      <div class="card" style="margin-bottom:20px;">
        <div class="card-title">系统健康状态</div>
        <div class="health-grid">
          <div class="health-item" v-for="(s, name) in services" :key="name">
            <span class="health-dot" :class="s === 'up' ? 'up' : 'down'"></span>
            <span class="health-name">{{ serviceName(name) }}</span>
            <el-tag size="small" :type="s === 'up' ? 'success' : 'danger'">{{ s === 'up' ? '正常' : '异常' }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 模型状态 -->
      <div class="card" style="margin-bottom:20px;">
        <div class="card-title">AI 模型状态</div>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="LLM">{{ modelStatus.llm ? modelStatus.llm.name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="LLM 状态">
            <el-tag :type="modelStatus.llm && modelStatus.llm.loaded ? 'success' : 'info'" size="small">
              {{ modelStatus.llm && modelStatus.llm.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="显存占用">{{ modelStatus.llm ? modelStatus.llm.vram : '-' }}</el-descriptions-item>
          <el-descriptions-item label="Embedding">{{ modelStatus.embedding ? modelStatus.embedding.name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="Embedding 状态">
            <el-tag :type="modelStatus.embedding && modelStatus.embedding.loaded ? 'success' : 'info'" size="small">
              {{ modelStatus.embedding && modelStatus.embedding.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="向量数">{{ modelStatus.faiss ? modelStatus.faiss.total_vectors : '-' }}</el-descriptions-item>
          <el-descriptions-item label="TTS">{{ modelStatus.tts ? modelStatus.tts.name : '-' }}</el-descriptions-item>
          <el-descriptions-item label="TTS 状态">
            <el-tag :type="modelStatus.tts && modelStatus.tts.loaded ? 'success' : 'info'" size="small">
              {{ modelStatus.tts && modelStatus.tts.loaded ? '已加载' : '未加载' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 系统配置 -->
      <div class="card" style="margin-bottom:20px;">
        <div class="card-title">系统配置</div>
        <el-form :model="config" label-width="200px" style="max-width:600px;">
          <el-form-item label="LLM 模型">
            <el-input v-model="config.llm_model" />
          </el-form-item>
          <el-form-item label="Temperature">
            <el-slider v-model="config.temperature" :min="0" :max="2" :step="0.1" show-input style="max-width:300px;" />
          </el-form-item>
          <el-form-item label="最大 Token 数">
            <el-input-number v-model="config.max_tokens" :min="256" :max="8192" :step="256" />
          </el-form-item>
          <el-form-item label="RAG 检索数量">
            <el-input-number v-model="config.rag_top_k" :min="1" :max="20" />
          </el-form-item>
          <el-form-item label="启用知识图谱增强">
            <el-switch v-model="config.enable_graph" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveConfig" :loading="saving">保存配置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 公告列表 -->
      <div class="card">
        <div class="card-title">系统公告</div>
        <div v-if="announcements.length === 0" style="color:var(--text-muted); text-align:center; padding:20px;">暂无公告</div>
        <el-timeline v-else>
          <el-timeline-item v-for="a in announcements" :key="a.id" :timestamp="a.created_at" placement="top">
            <el-card>
              <h4>{{ a.title }}</h4>
              <p style="color:var(--text-muted);">{{ a.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
  `,
  setup() {
    var services = ref({});
    var modelStatus = ref({});
    var config = reactive({
      llm_model: 'deepseek-r1:7b',
      temperature: 0.7,
      max_tokens: 2048,
      rag_top_k: 5,
      enable_graph: true
    });
    var saving = ref(false);
    var announcements = ref([]);

    function serviceName(name) {
      var map = { mysql: 'MySQL', neo4j: 'Neo4j', ollama: 'Ollama (LLM)', faiss: 'FAISS', gpu: 'GPU' };
      return map[name] || name;
    }

    async function loadHealth() {
      try {
        var res = await API.system.health();
        if (res.code === 200 && res.data) {
          services.value = res.data.services || {};
        }
      } catch (e) { /* 静默 */ }
    }

    async function loadModelStatus() {
      try {
        var res = await API.system.modelStatus();
        if (res.code === 200 && res.data) {
          modelStatus.value = res.data;
        }
      } catch (e) { /* 静默 */ }
    }

    async function loadConfig() {
      try {
        var res = await API.system.getConfig();
        if (res.code === 200 && res.data) {
          Object.assign(config, res.data);
        }
      } catch (e) { /* 静默 */ }
    }

    async function loadAnnouncements() {
      try {
        var res = await API.system.announcements();
        if (res.code === 200 && res.data) {
          announcements.value = Array.isArray(res.data) ? res.data : (res.data.items || []);
        }
      } catch (e) { /* 静默 */ }
    }

    async function saveConfig() {
      saving.value = true;
      try {
        var res = await API.system.updateConfig(config);
        if (res.code === 200) {
          ElementPlus.ElMessage.success('配置已保存');
        } else {
          ElementPlus.ElMessage.error(res.message || '保存失败');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('保存失败');
      }
      saving.value = false;
    }

    onMounted(function() {
      loadHealth();
      loadModelStatus();
      loadConfig();
      loadAnnouncements();
    });

    return { services, modelStatus, config, saving, announcements, serviceName, saveConfig };
  }
};

// ============================================
//  8. 个人设置页面
// ============================================
const ProfilePage = {
  template: `
    <div class="profile-page">
      <div class="card" style="max-width:600px; margin:0 auto;">
        <div class="card-title">个人信息</div>
        <el-form :model="profile" label-width="100px" style="margin-top:20px;">
          <el-form-item label="用户名">
            <el-input v-model="profile.username" disabled />
          </el-form-item>
          <el-form-item label="昵称">
            <el-input v-model="profile.nickname" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="邮箱">
            <el-input v-model="profile.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机">
            <el-input v-model="profile.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveProfile" :loading="saving">保存修改</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="card" style="max-width:600px; margin:20px auto 0;">
        <div class="card-title">修改密码</div>
        <el-form :model="pwdForm" label-width="100px" style="margin-top:20px;">
          <el-form-item label="当前密码">
            <el-input v-model="pwdForm.oldPassword" type="password" show-password placeholder="请输入当前密码" />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input v-model="pwdForm.newPassword" type="password" show-password placeholder="请输入新密码（至少6位）" />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input v-model="pwdForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
          </el-form-item>
          <el-form-item>
            <el-button type="warning" @click="changePassword" :loading="changingPwd">修改密码</el-button>
          </el-form-item>
        </el-form>
      </div>
    </div>
  `,
  setup() {
    var profile = reactive({ username: '', nickname: '', email: '', phone: '' });
    var pwdForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' });
    var saving = ref(false);
    var changingPwd = ref(false);

    onMounted(async function() {
      try {
        var res = await API.auth.getProfile();
        if (res.code === 200 && res.data) {
          Object.assign(profile, res.data);
        }
      } catch (e) { /* 静默 */ }
    });

    async function saveProfile() {
      saving.value = true;
      try {
        var res = await API.auth.updateProfile({
          nickname: profile.nickname,
          email: profile.email,
          phone: profile.phone
        });
        if (res.code === 200) {
          ElementPlus.ElMessage.success('保存成功');
          // 更新本地存储
          var userStr = localStorage.getItem('user');
          if (userStr) {
            var user = JSON.parse(userStr);
            user.nickname = profile.nickname;
            user.email = profile.email;
            localStorage.setItem('user', JSON.stringify(user));
          }
        } else {
          ElementPlus.ElMessage.error(res.message || '保存失败');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('保存失败');
      }
      saving.value = false;
    }

    async function changePassword() {
      if (!pwdForm.oldPassword || !pwdForm.newPassword) {
        ElementPlus.ElMessage.warning('请填写完整');
        return;
      }
      if (pwdForm.newPassword.length < 6) {
        ElementPlus.ElMessage.warning('新密码至少6位');
        return;
      }
      if (pwdForm.newPassword !== pwdForm.confirmPassword) {
        ElementPlus.ElMessage.warning('两次密码不一致');
        return;
      }
      changingPwd.value = true;
      try {
        var res = await API.auth.changePassword(pwdForm.oldPassword, pwdForm.newPassword);
        if (res.code === 200) {
          ElementPlus.ElMessage.success('密码修改成功');
          pwdForm.oldPassword = '';
          pwdForm.newPassword = '';
          pwdForm.confirmPassword = '';
        } else {
          ElementPlus.ElMessage.error(res.message || '修改失败');
        }
      } catch (e) {
        ElementPlus.ElMessage.error('修改失败');
      }
      changingPwd.value = false;
    }

    return { profile, pwdForm, saving, changingPwd, saveProfile, changePassword };
  }
};
