<template>
  <div class="dashboard">
    <!-- Row 1: KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card" v-for="k in kpis" :key="k.label">
        <div class="kpi-icon" :class="k.color">{{ k.icon }}</div>
        <div>
          <div class="kpi-label">{{ k.label }}</div>
          <div class="kpi-value">{{ k.display }}</div>
          <div class="kpi-change">{{ k.change }}</div>
        </div>
      </div>
    </div>

    <!-- Row 2: Charts -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title">最近问答趋势</div>
        <div ref="trendEl" class="chart-box" />
      </div>
      <div class="card">
        <div class="card-title">热门知识点</div>
        <div v-for="(t, i) in topics" :key="t.topic" class="topic-item">
          <span class="topic-rank" :style="{ background: rankColors[i] }">{{ i + 1 }}</span>
          <span class="topic-name">{{ t.topic }}</span>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: (t.progress * 100) + '%' }" />
          </div>
          <span class="topic-count">{{ t.count }}</span>
        </div>
      </div>
    </div>

    <!-- Row 3: Three columns -->
    <div class="grid-3">
      <!-- Knowledge Graph Preview -->
      <div class="card">
        <div class="card-title">知识图谱概览</div>
        <div ref="graphEl" class="graph-preview" />
        <button class="graph-enter-btn" @click="$router.push('/knowledge-graph')">
          进入知识图谱 →
        </button>
      </div>

      <!-- Announcements -->
      <div class="card">
        <div class="card-title">
          系统公告
          <span class="more-link" @click="$router.push('/system')">查看更多 ></span>
        </div>
        <ul class="announcement-list">
          <li class="announcement-item" v-for="a in announcements" :key="a.id">
            <span class="announcement-date">{{ a.date }}</span>
            <span class="announcement-title">{{ a.title }}</span>
          </li>
        </ul>
      </div>

      <!-- Digital Teacher -->
      <div class="card">
        <div class="card-title">数字教师</div>
        <div class="teacher-panel">
          <div class="avatar-lg">👩‍🏫</div>
          <div class="greeting">你好，我是你的 AI 数字教师</div>
          <div class="sub-greeting">有什么可以帮助你学习的吗？</div>
          <button class="graph-enter-btn" @click="$router.push('/teacher')">
            开始对话 →
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { dashboardAPI, systemAPI } from '@/api'

const trendEl = ref(null)
const graphEl = ref(null)
const kpis = ref([])
const topics = ref([])
const announcements = ref([])
let charts = []

const rankColors = ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#8b5cf6']

onMounted(async () => {
  // Load dashboard data
  const { data: d } = await dashboardAPI.overview()

  kpis.value = [
    { label: '知识节点', display: '1,523', icon: '📊', color: 'blue', change: '↑ 12%' },
    { label: 'AI 问答次数', display: '832', icon: '💬', color: 'purple', change: '↑ 18%' },
    { label: '文档数量', display: '258', icon: '📄', color: 'green', change: '↑ 8%' },
    { label: '数字教师', display: '在线运行', icon: '👩‍🏫', color: 'orange', change: '状态正常' },
  ]

  topics.value = [
    { topic: 'Transformer', count: 423, progress: 0.95 },
    { topic: '卷积神经网络', count: 412, progress: 0.92 },
    { topic: '聚类算法', count: 398, progress: 0.89 },
    { topic: '决策树', count: 285, progress: 0.64 },
    { topic: 'KNN 算法', count: 210, progress: 0.47 },
  ]

  // Load announcements
  try {
    const annRes = await systemAPI.announcements()
    if (annRes.code === 200 && annRes.data) {
      announcements.value = (Array.isArray(annRes.data) ? annRes.data : annRes.data.items || []).slice(0, 5).map(a => ({
        id: a.id,
        date: (a.created_at || '').slice(5, 10),
        title: a.title,
      }))
    }
  } catch (e) {
    announcements.value = [
      { id: 1, date: '06-20', title: '平台已更新 DeepSeek-R1-7B 模型' },
      { id: 2, date: '06-18', title: '新增知识图谱可视化功能' },
      { id: 3, date: '06-15', title: '优化 RAG 检索算法，提升回答准确率' },
      { id: 4, date: '06-12', title: '数字教师形象与语音功能上线' },
      { id: 5, date: '06-10', title: '系统维护通知（6月20日 02:00-04:00）' },
    ]
  }

  await nextTick()

  // Trend line chart
  if (trendEl.value) {
    const c = echarts.init(trendEl.value)
    const labels = d.question_trend.labels
    const values = d.question_trend.values
    const userValues = values.map(v => Math.round(v * 0.55))

    c.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#1a1a2e', fontSize: 13 } },
      legend: { data: ['问答次数', '独立用户数'], top: 0, right: 0, textStyle: { color: '#64748b', fontSize: 12 }, itemWidth: 16, itemHeight: 3 },
      grid: { top: 36, right: 20, bottom: 30, left: 50 },
      xAxis: { type: 'category', data: labels, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisLabel: { color: '#94a3b8', fontSize: 11 }, axisTick: { show: false } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { color: '#94a3b8', fontSize: 11 } },
      series: [
        {
          name: '问答次数', type: 'line', data: values, smooth: true, symbol: 'circle', symbolSize: 8,
          lineStyle: { color: '#6366f1', width: 3 },
          itemStyle: { color: '#6366f1', borderWidth: 2, borderColor: '#fff' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(99,102,241,0.25)' }, { offset: 1, color: 'rgba(99,102,241,0.02)' }]) },
        },
        {
          name: '独立用户数', type: 'line', data: userValues, smooth: true, symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#22c55e', width: 2.5 },
          itemStyle: { color: '#22c55e', borderWidth: 2, borderColor: '#fff' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(34,197,94,0.18)' }, { offset: 1, color: 'rgba(34,197,94,0.01)' }]) },
        },
      ],
    })
    charts.push(c)
  }

  // Knowledge graph preview (small force-directed graph)
  if (graphEl.value) {
    const c = echarts.init(graphEl.value)
    const previewNodes = [
      { id: 'ml', name: '机器学习', category: 0, symbolSize: 40, x: 200, y: 120 },
      { id: 'sup', name: '监督学习', category: 1, symbolSize: 28 },
      { id: 'unsup', name: '无监督学习', category: 1, symbolSize: 28 },
      { id: 'dl', name: '深度学习', category: 1, symbolSize: 28 },
      { id: 'linreg', name: '线性回归', category: 2, symbolSize: 20 },
      { id: 'logreg', name: '逻辑回归', category: 2, symbolSize: 20 },
      { id: 'svm', name: 'SVM', category: 2, symbolSize: 22 },
      { id: 'dt', name: '决策树', category: 2, symbolSize: 22 },
      { id: 'kmeans', name: 'KMeans', category: 2, symbolSize: 20 },
      { id: 'dbscan', name: 'DBSCAN', category: 2, symbolSize: 18 },
      { id: 'cnn', name: 'CNN', category: 2, symbolSize: 24 },
      { id: 'rnn', name: 'RNN', category: 2, symbolSize: 20 },
      { id: 'tf', name: 'Transformer', category: 2, symbolSize: 26 },
    ]
    const previewEdges = [
      { source: 'ml', target: 'sup' }, { source: 'ml', target: 'unsup' }, { source: 'ml', target: 'dl' },
      { source: 'sup', target: 'linreg' }, { source: 'sup', target: 'logreg' }, { source: 'sup', target: 'svm' }, { source: 'sup', target: 'dt' },
      { source: 'unsup', target: 'kmeans' }, { source: 'unsup', target: 'dbscan' },
      { source: 'dl', target: 'cnn' }, { source: 'dl', target: 'rnn' }, { source: 'dl', target: 'tf' },
    ]
    const catColors = ['#6366f1', '#22c55e', '#f97316']

    c.setOption({
      tooltip: { show: false },
      animationDuration: 1500,
      animationEasingUpdate: 'quinticInOut',
      series: [{
        type: 'graph',
        layout: 'force',
        data: previewNodes.map(n => ({
          ...n,
          itemStyle: { color: catColors[n.category] },
          label: { show: n.symbolSize >= 24, fontSize: 10, color: '#1a1a2e' },
        })),
        links: previewEdges.map(e => ({
          ...e,
          lineStyle: { color: '#c7d2fe', width: 1.5, curveness: 0.1 },
        })),
        roam: true,
        draggable: true,
        force: { repulsion: 180, gravity: 0.1, edgeLength: [50, 120], friction: 0.6 },
        emphasis: { focus: 'adjacency', lineStyle: { width: 3 } },
        label: { position: 'right' },
      }],
    })
    charts.push(c)
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
  window.removeEventListener('resize', handleResize)
})

function handleResize() { charts.forEach(c => c.resize()) }
</script>

<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 20px;
}

/* Topic ranking items */
.topic-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}
.topic-rank {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}
.topic-name {
  width: 100px;
  font-size: 13px;
  color: var(--text-secondary);
  flex-shrink: 0;
}
.topic-count {
  width: 36px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  flex-shrink: 0;
}

/* Announcement list */
.announcement-list {
  list-style: none;
  padding: 0;
  margin: 0;
}
.announcement-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
}
.announcement-item:last-child { border-bottom: none; }
.announcement-date {
  color: var(--text-muted);
  white-space: nowrap;
  flex-shrink: 0;
  width: 50px;
}
.announcement-title {
  color: var(--text-primary);
  flex: 1;
  line-height: 1.5;
}

/* Card title extras */
.more-link {
  margin-left: auto;
  font-size: 12px;
  color: var(--primary);
  cursor: pointer;
  font-weight: 400;
}
.more-link:hover { text-decoration: underline; }

/* Graph preview */
.graph-preview {
  width: 100%;
  height: 220px;
}
.graph-enter-btn {
  display: block;
  width: 100%;
  margin-top: 12px;
  text-align: center;
  padding: 10px;
  border-radius: 10px;
  background: var(--gradient);
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: var(--transition);
}
.graph-enter-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* Teacher panel */
.teacher-panel {
  text-align: center;
  padding: 16px 0;
}
.teacher-panel .avatar-lg {
  font-size: 64px;
  margin-bottom: 10px;
}
.teacher-panel .greeting {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.teacher-panel .sub-greeting {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

@media (max-width: 1200px) {
  .grid-2 { grid-template-columns: 1fr; }
  .grid-3 { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
