// ============================================
// Pages - Vue 页面组件定义
// 5 个页面：仪表盘、知识图谱、智能问答、数字教师、数据分析
// ============================================

const { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } = Vue;

// =====================================================
//  1. 仪表盘页面
// =====================================================
const DashboardPage = {
  template: `
    <div class="dashboard-page">
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
    </div>
  `,
  setup() {
    const trendRef = ref(null);
    const pieRef = ref(null);
    const kpiList = ref([]);
    const topics = ref([]);
    let charts = [];

    onMounted(async function() {
      var res = await API.get('/api/v1/dashboard/overview');
      var d = res.data;

      kpiList.value = [
        { label: '总提问数', value: d.kpis.total_questions, icon: '💬', color: 'purple', change: '+12 本周', dir: 'up' },
        { label: '今日提问', value: d.kpis.today_questions, icon: '📝', color: 'blue', change: '+3 较昨日', dir: 'up' },
        { label: '总用户数', value: d.kpis.total_users, icon: '👥', color: 'green', change: '+5 本周', dir: 'up' },
        { label: '活跃用户', value: d.kpis.active_users, icon: '🔥', color: 'orange', change: '48% 活跃率', dir: 'up' },
        { label: '知识覆盖率', value: Math.round(d.kpis.knowledge_coverage * 100) + '%', icon: '📚', color: 'pink', change: '+5% 本月', dir: 'up' },
        { label: '平均满意度', value: d.kpis.avg_satisfaction.toFixed(1), icon: '⭐', color: 'cyan', change: '4.3 / 5.0', dir: 'up' }
      ];
      topics.value = d.popular_topics;

      await nextTick();
      if (trendRef.value) charts.push(Charts.dashTrend(trendRef.value, d.question_trend));
      if (pieRef.value) charts.push(Charts.dashPie(pieRef.value, d.course_distribution));
    });

    onUnmounted(function() { charts.forEach(function(c) { c.dispose(); }); });

    return { trendRef, pieRef, kpiList, topics };
  }
};

// =====================================================
//  2. 知识图谱页面
// =====================================================
const KnowledgeGraphPage = {
  template: `
    <div class="graph-page">
      <!-- 工具栏 -->
      <div class="graph-toolbar">
        <el-select v-model="courseFilter" placeholder="选择课程" clearable style="width: 160px">
          <el-option label="全部课程" value=""></el-option>
          <el-option label="机器学习" value="ml"></el-option>
          <el-option label="数据挖掘" value="dm"></el-option>
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

    onMounted(async function() {
      var res = await API.get('/api/v1/graph/visualization');
      var d = res.data;
      categories.value = d.categories;

      await nextTick();
      if (graphRef.value) {
        chart = Charts.knowledgeGraph(graphRef.value, d, function(node) {
          var det = d.nodeDetails[node.id];
          if (det) {
            detail.value = det;
            tagColor.value = d.categories[node.category] ? d.categories[node.category].color : '#6366f1';
            detailOpen.value = true;
          } else {
            detail.value = { name: node.name, type: d.categories[node.category] ? d.categories[node.category].name : '未知', desc: '点击其他节点查看更多详情，或等待后端接入完整数据。', related: [] };
            tagColor.value = d.categories[node.category] ? d.categories[node.category].color : '#6366f1';
            detailOpen.value = true;
          }
        });
      }
    });

    onUnmounted(function() { if (chart) chart.dispose(); });

    function onSearch() {
      if (!searchKey.value) return;
      ElementPlus.ElMessage.info('搜索功能将在后端接入后生效：' + searchKey.value);
    }

    return { graphRef, courseFilter, searchKey, categories, detailOpen, detail, tagColor, onSearch };
  }
};

// =====================================================
//  3. 智能问答页面
// =====================================================
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
            :class="{ active: s.id === currentSession }"
            v-for="s in sessions"
            :key="s.id"
            @click="currentSession = s.id"
          >
            <div class="qa-session-title">{{ s.title }}</div>
            <div class="qa-session-time">{{ s.course }} · {{ s.time }}</div>
          </div>
        </div>
      </div>

      <!-- 右侧聊天区 -->
      <div class="qa-main">
        <div class="qa-messages" ref="msgRef">
          <!-- 空状态 -->
          <div v-if="messages.length === 0" style="text-align:center; padding:60px 0; color: var(--text-muted);">
            <div style="font-size:48px; margin-bottom:16px;">🤖</div>
            <div style="font-size:16px; margin-bottom:8px;">你好！我是课程智能助手</div>
            <div style="font-size:13px;">试试问我关于机器学习或数据挖掘的任何问题</div>
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
            </div>
          </div>

          <!-- 加载指示器 -->
          <div v-if="loading" class="qa-message assistant">
            <div class="qa-avatar ai">AI</div>
            <div class="qa-bubble">
              <div class="qa-typing"><span></span><span></span><span></span></div>
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

    onMounted(async function() {
      var res = await API.get('/api/v1/qa/sessions');
      sessions.value = res.data;
      if (sessions.value.length) currentSession.value = sessions.value[0].id;
    });

    function renderMd(text) {
      if (!text) return '';
      try { return marked.parse(text); } catch(e) { return text; }
    }

    function scrollToBottom() {
      nextTick(function() {
        if (msgRef.value) msgRef.value.scrollTop = msgRef.value.scrollHeight;
      });
    }

    async function sendQuestion() {
      var q = question.value.trim();
      if (!q || loading.value) return;

      messages.value.push({ role: 'user', content: q });
      question.value = '';
      loading.value = true;
      scrollToBottom();

      try {
        var res = await API.post('/api/v1/qa/ask-sync', {
          question: q,
          session_id: currentSession.value,
          enable_rag: true,
          enable_graph: true
        });
        var d = res.data;
        messages.value.push({
          role: 'assistant',
          content: d.answer,
          references: d.references || []
        });
      } catch(e) {
        messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后重试。' });
      }
      loading.value = false;
      scrollToBottom();
    }

    function newSession() {
      var id = 'sess_' + Date.now();
      sessions.value.unshift({ id: id, title: '新对话', time: '刚刚', course: '机器学习' });
      currentSession.value = id;
      messages.value = [];
    }

    return { msgRef, sessions, currentSession, messages, question, loading, renderMd, sendQuestion, newSession };
  }
};

// =====================================================
//  4. 数字教师页面
// =====================================================
const TeacherPage = {
  template: `
    <div class="teacher-layout">
      <!-- 左侧：教师形象 -->
      <div class="teacher-avatar-section">
        <div class="teacher-avatar-bg"></div>
        <div class="teacher-avatar-img">
          <span class="avatar-placeholder">👩‍🏫</span>
        </div>
        <div class="teacher-name">{{ teacher.name }}</div>
        <div class="teacher-status">
          <span class="status-dot"></span>
          {{ teacher.status === 'online' ? '在线' : '离线' }}
        </div>
        <div class="teacher-emotions">
          <button
            class="emotion-btn"
            :class="{ active: currentEmotion === e }"
            v-for="e in teacher.emotions"
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
                <div style="font-size:22px; font-weight:700; color:var(--primary);">{{ teacher.progress.total_questions }}</div>
                <div style="font-size:12px; color:var(--text-muted);">总提问</div>
              </div>
              <div style="flex:1; text-align:center;">
                <div style="font-size:22px; font-weight:700; color:var(--primary);">{{ teacher.progress.study_hours }}h</div>
                <div style="font-size:12px; color:var(--text-muted);">学习时长</div>
              </div>
              <div style="flex:1; text-align:center;">
                <div style="font-size:22px; font-weight:700; color:var(--primary);">{{ teacher.progress.level }}</div>
                <div style="font-size:12px; color:var(--text-muted);">当前等级</div>
              </div>
            </div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;">已掌握</div>
            <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:8px;">
              <el-tag size="small" type="success" v-for="t in teacher.progress.mastered_topics" :key="t">{{ t }}</el-tag>
            </div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:6px;">待加强</div>
            <div style="display:flex; flex-wrap:wrap; gap:4px;">
              <el-tag size="small" type="warning" v-for="t in teacher.progress.weak_topics" :key="t">{{ t }}</el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：对话 -->
      <div class="teacher-chat-section">
        <div class="teacher-chat-header">与{{ teacher.name }}对话</div>
        <div class="teacher-chat-messages" ref="chatRef">
          <div v-if="chatMessages.length === 0" style="text-align:center; padding:50px 0; color:var(--text-muted);">
            <div style="font-size:40px; margin-bottom:12px;">👋</div>
            <div>向{{ teacher.name }}提问吧！</div>
          </div>

          <div v-for="(m, i) in chatMessages" :key="i" class="qa-message" :class="m.role">
            <div class="qa-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
              {{ m.role === 'user' ? '我' : '师' }}
            </div>
            <div class="qa-bubble" v-html="renderMd(m.content)"></div>
          </div>

          <div v-if="chatLoading" class="qa-message assistant">
            <div class="qa-avatar ai">师</div>
            <div class="qa-bubble">
              <div class="qa-typing"><span></span><span></span><span></span></div>
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
    var teacher = ref({ name: '小智老师', status: 'online', emotions: [], progress: { total_questions: 0, mastered_topics: [], weak_topics: [], study_hours: 0, level: '' } });
    var currentEmotion = ref('normal');
    var chatMessages = ref([]);
    var chatInput = ref('');
    var chatLoading = ref(false);

    onMounted(async function() {
      var res = await API.get('/api/v1/teacher/avatar');
      teacher.value = res.data;
    });

    function emotionLabel(e) {
      var map = { normal: '平静', happy: '开心', thinking: '思考', encouraging: '鼓励' };
      return map[e] || e;
    }

    function renderMd(text) {
      if (!text) return '';
      try { return marked.parse(text); } catch(err) { return text; }
    }

    function scrollToBottom() {
      nextTick(function() {
        if (chatRef.value) chatRef.value.scrollTop = chatRef.value.scrollHeight;
      });
    }

    async function sendChat() {
      var q = chatInput.value.trim();
      if (!q || chatLoading.value) return;
      chatMessages.value.push({ role: 'user', content: q });
      chatInput.value = '';
      chatLoading.value = true;
      scrollToBottom();

      try {
        var res = await API.post('/api/v1/teacher/chat', { question: q });
        chatMessages.value.push({ role: 'assistant', content: res.data.answer });
      } catch(e) {
        chatMessages.value.push({ role: 'assistant', content: '抱歉，老师暂时不在线，请稍后再试。' });
      }
      chatLoading.value = false;
      scrollToBottom();
    }

    return { chatRef, teacher, currentEmotion, chatMessages, chatInput, chatLoading, emotionLabel, renderMd, sendChat };
  }
};

// =====================================================
//  5. 数据分析页面
// =====================================================
const AnalysisPage = {
  template: `
    <div class="analysis-page">
      <!-- 筛选栏 -->
      <div class="analysis-filters">
        <el-date-picker v-model="dateRange" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" size="default" style="width:300px;" />
        <el-select v-model="courseFilter" placeholder="课程" clearable style="width:140px">
          <el-option label="全部" value=""></el-option>
          <el-option label="机器学习" value="ml"></el-option>
          <el-option label="数据挖掘" value="dm"></el-option>
        </el-select>
        <el-button type="primary" :style="{ background: 'var(--gradient)', border: 'none' }">查询</el-button>
      </div>

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
    var allCharts = [];

    onMounted(async function() {
      var trendRes = await API.get('/api/v1/dashboard/question-trend');
      var heatRes = await API.get('/api/v1/dashboard/topic-heatmap');
      var actRes = await API.get('/api/v1/dashboard/user-activity');
      var satRes = await API.get('/api/v1/dashboard/satisfaction');
      var radarRes = await API.get('/api/v1/dashboard/mastery-radar');

      await nextTick();
      if (trendRef.value) allCharts.push(Charts.analysisTrend(trendRef.value, trendRes.data));
      if (heatRef.value) allCharts.push(Charts.topicHeatmap(heatRef.value, heatRes.data));
      if (activityRef.value) allCharts.push(Charts.userActivityBar(activityRef.value, actRes.data));
      if (hourlyRef.value) allCharts.push(Charts.hourlyActivity(hourlyRef.value, actRes.data));
      if (satRef.value) allCharts.push(Charts.satisfaction(satRef.value, satRes.data));
      if (radarRef.value) allCharts.push(Charts.masteryRadar(radarRef.value, radarRes.data));
    });

    onUnmounted(function() { allCharts.forEach(function(c) { c.dispose(); }); });

    return { trendRef, heatRef, activityRef, hourlyRef, satRef, radarRef, dateRange, courseFilter };
  }
};
