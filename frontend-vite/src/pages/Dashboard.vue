<template>
  <div class="dashboard">
    <!-- KPI 卡片行 -->
    <div class="kpi-grid">
      <div class="kpi-card" v-for="k in kpis" :key="k.label">
        <div class="kpi-icon" :class="k.color">{{ k.icon }}</div>
        <div class="kpi-info">
          <div class="kpi-label">{{ k.label }}</div>
          <div class="kpi-value">{{ k.value }}</div>
          <div class="kpi-change" :class="k.changeDir">
            {{ k.change }}
            <span v-if="k.sub" class="kpi-sub">{{ k.sub }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 趋势图 + 热门知识点排名 -->
    <div class="grid-2">
      <div class="card">
        <div class="card-header">
          <div class="card-title">问答趋势（近 7 天）</div>
          <span class="card-action">查看详情 →</span>
        </div>
        <div ref="trendEl" class="chart-box" />
      </div>
      <div class="card">
        <div class="card-header">
          <div class="card-title">热门知识点</div>
          <span class="card-action">查看全部 →</span>
        </div>
        <div class="rank-list">
          <div v-for="(t, i) in topics" :key="t.topic" class="rank-item">
            <span class="rank-num" :class="'r' + (i + 1)">{{ i + 1 }}</span>
            <span class="rank-name">{{ t.topic }}</span>
            <div class="rank-bar-bg">
              <div class="rank-bar" :style="{ width: barWidth(t.count), background: barColor(i) }" />
            </div>
            <span class="rank-count">{{ t.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识图谱概览 + 系统公告 + 数字教师 -->
    <div class="grid-3">
      <!-- 知识图谱概览 -->
      <div class="card graph-card">
        <div class="card-header">
          <div class="card-title">知识图谱概览</div>
          <router-link to="/knowledge-graph" class="card-action">进入知识图谱 →</router-link>
        </div>
        <div ref="graphEl" class="graph-mini" />
      </div>

      <!-- 系统公告 -->
      <div class="card">
        <div class="card-header">
          <div class="card-title">系统公告</div>
          <span class="card-action">全部公告 →</span>
        </div>
        <div class="announce-list">
          <div v-for="a in announcements" :key="a.date" class="announce-item">
            <span class="announce-dot" />
            <div class="announce-content">
              <div class="announce-text">{{ a.text }}</div>
              <div class="announce-date">{{ a.date }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数字教师推广卡 -->
      <div class="card teacher-promo">
        <div class="promo-bg" />
        <div class="promo-avatar">
          <span>👩‍🏫</span>
        </div>
        <div class="promo-title">数字教师</div>
        <div class="promo-desc">
          基于 Stable Diffusion 生成的虚拟教师形象，支持智能对话、情感交互与个性化教学辅导。
        </div>
        <div class="promo-features">
          <span class="promo-tag">智能对话</span>
          <span class="promo-tag">情感识别</span>
          <span class="promo-tag">个性化教学</span>
        </div>
        <router-link to="/teacher" class="promo-btn">开始对话 →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const trendEl = ref(null)
const graphEl = ref(null)
const kpis = ref([])
const topics = ref([])
const announcements = ref([])
let charts = []

const maxCount = ref(1)

const barColors = ['#ef4444', '#f97316', '#3b82f6', '#7b93fa', '#94a3b8']

function barWidth(count) {
  return Math.round((count / maxCount.value) * 100) + '%'
}
function barColor(i) {
  return barColors[i] || barColors[barColors.length - 1]
}

onMounted(async () => {
  const { data: d } = await api.get('/dashboard/overview')

  kpis.value = d.kpis
  topics.value = d.popular_topics
  announcements.value = d.announcements || []
  maxCount.value = Math.max(...d.popular_topics.map(t => t.count), 1)

  await nextFrame()

  /* ---- 趋势折线图（双线） ---- */
  if (trendEl.value) {
    const c = echarts.init(trendEl.value)
    const td = d.question_trend
    c.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(255,255,255,0.96)',
        borderColor: '#e2e8f0',
        textStyle: { color: '#1e293b', fontSize: 13 },
      },
      legend: {
        data: ['问答次数', '独立用户数'],
        top: 4, right: 10,
        textStyle: { color: '#64748b', fontSize: 12 },
        itemWidth: 16, itemHeight: 3,
      },
      grid: { top: 42, right: 20, bottom: 28, left: 50 },
      xAxis: {
        type: 'category', data: td.labels, boundaryGap: false,
        axisLine: { lineStyle: { color: '#e2e8f0' } },
        axisLabel: { color: '#94a3b8', fontSize: 11 },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } },
        axisLabel: { color: '#94a3b8' },
      },
      series: [
        {
          name: '问答次数', type: 'line', data: td.qa_count, smooth: true,
          symbol: 'circle', symbolSize: 7,
          lineStyle: { color: '#4f6ef7', width: 2.5 },
          itemStyle: { color: '#4f6ef7', borderWidth: 2, borderColor: '#fff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(79,110,247,0.18)' },
              { offset: 1, color: 'rgba(79,110,247,0.01)' },
            ]),
          },
        },
        {
          name: '独立用户数', type: 'line', data: td.user_count, smooth: true,
          symbol: 'circle', symbolSize: 7,
          lineStyle: { color: '#8b5cf6', width: 2.5 },
          itemStyle: { color: '#8b5cf6', borderWidth: 2, borderColor: '#fff' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(139,92,246,0.15)' },
              { offset: 1, color: 'rgba(139,92,246,0.01)' },
            ]),
          },
        },
      ],
    })
    charts.push(c)
  }

  /* ---- 知识图谱迷你脑图 ---- */
  if (graphEl.value) {
    const c = echarts.init(graphEl.value)
    const gd = d.graph_overview
    const nodes = gd.nodes.map(n => ({
      ...n,
      label: { show: true, fontSize: n.symbolSize > 35 ? 13 : 11, color: '#1e293b', fontWeight: n.symbolSize > 35 ? 700 : 400 },
    }))
    const edges = gd.edges.map(e => ({
      ...e,
      lineStyle: { color: '#c7d2fe', width: 1.5, curveness: 0.1 },
    }))
    c.setOption({
      tooltip: { show: false },
      animationDuration: 1200,
      series: [{
        type: 'graph',
        layout: 'none',
        coordinateSystem: null,
        data: nodes,
        links: edges,
        roam: false,
        draggable: false,
        edgeSymbol: ['none', 'arrow'],
        edgeSymbolSize: [0, 6],
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 2.5 },
          label: { fontSize: 14, fontWeight: 700 },
        },
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
function nextFrame() { return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))) }
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 20px; }

/* 两列布局 */
.grid-2 {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 20px;
}

/* 三列布局 */
.grid-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}

/* 排名列表 */
.rank-list { padding: 4px 0; }

/* 知识图谱迷你画布 */
.graph-mini { width: 100%; height: 280px; }
.graph-card { position: relative; }

/* 公告列表 */
.announce-list { max-height: 310px; overflow-y: auto; }

/* 数字教师推广卡 */
.teacher-promo {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  overflow: hidden;
  padding: 32px 24px;
}
.promo-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg, #eef2ff 0%, #f3f0ff 50%, #fce7f3 100%);
  opacity: 0.6;
}
.promo-avatar {
  width: 90px; height: 90px; border-radius: 50%;
  background: var(--gradient);
  display: flex; align-items: center; justify-content: center;
  font-size: 44px;
  position: relative; z-index: 1;
  box-shadow: 0 12px 36px rgba(79,110,247,0.2);
  margin-bottom: 16px;
}
.promo-title {
  font-size: 18px; font-weight: 700; color: var(--text-primary);
  position: relative; z-index: 1; margin-bottom: 10px;
}
.promo-desc {
  font-size: 13px; color: var(--text-secondary); line-height: 1.8;
  position: relative; z-index: 1; margin-bottom: 16px;
}
.promo-features {
  display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;
  position: relative; z-index: 1; margin-bottom: 20px;
}
.promo-tag {
  padding: 4px 12px; border-radius: 20px;
  background: rgba(79,110,247,0.1); color: var(--primary);
  font-size: 12px; font-weight: 500;
}
.promo-btn {
  display: inline-block;
  padding: 10px 28px; border-radius: 24px;
  background: var(--gradient);
  color: #fff; font-weight: 600; font-size: 14px;
  text-decoration: none;
  position: relative; z-index: 1;
  box-shadow: 0 6px 20px rgba(79,110,247,0.25);
  transition: all 0.25s;
}
.promo-btn:hover {
  box-shadow: 0 8px 28px rgba(79,110,247,0.35);
  transform: translateY(-2px);
}

/* 响应式 */
@media (max-width: 1200px) {
  .grid-2 { grid-template-columns: 1fr; }
  .grid-3 { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .grid-2, .grid-3 { grid-template-columns: 1fr; }
}
</style>
