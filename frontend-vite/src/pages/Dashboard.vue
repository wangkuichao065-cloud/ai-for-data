<template>
  <div class="dashboard">
    <!-- KPI 卡片 -->
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

    <!-- 图表行 -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title">提问趋势（近 7 天）</div>
        <div ref="trendEl" class="chart-box" />
      </div>
      <div class="card">
        <div class="card-title">课程提问分布</div>
        <div ref="pieEl" class="chart-box" />
      </div>
    </div>

    <!-- 热门知识点 -->
    <div class="card" style="margin-top: 20px">
      <div class="card-title">热门知识点</div>
      <div v-for="t in topics" :key="t.topic" class="progress-item">
        <span class="progress-label">{{ t.topic }}</span>
        <div class="progress-track">
          <div class="progress-fill" :style="{ width: (t.progress * 100) + '%' }" />
        </div>
        <span class="progress-value">{{ Math.round(t.progress * 100) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const trendEl = ref(null)
const pieEl = ref(null)
const kpis = ref([])
const topics = ref([])
let charts = []

onMounted(async () => {
  const { data: d } = await api.get('/dashboard/overview')

  kpis.value = [
    { label: '总提问数', display: d.kpis.total_questions, icon: '💬', color: 'purple', change: '+12 本周' },
    { label: '今日提问', display: d.kpis.today_questions, icon: '📝', color: 'blue', change: '+3 较昨日' },
    { label: '总用户数', display: d.kpis.total_users, icon: '👥', color: 'green', change: '+5 本周' },
    { label: '活跃用户', display: d.kpis.active_users, icon: '🔥', color: 'orange', change: '48% 活跃率' },
    { label: '知识覆盖率', display: Math.round(d.kpis.knowledge_coverage * 100) + '%', icon: '📚', color: 'pink', change: '+5% 本月' },
    { label: '平均满意度', display: d.kpis.avg_satisfaction.toFixed(1), icon: '⭐', color: 'cyan', change: '4.3 / 5.0' },
  ]
  topics.value = d.popular_topics

  await nextFrame()

  // 趋势折线图
  if (trendEl.value) {
    const c = echarts.init(trendEl.value)
    c.setOption({
      tooltip: { trigger: 'axis', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#1a1a2e' } },
      grid: { top: 20, right: 20, bottom: 30, left: 50 },
      xAxis: { type: 'category', data: d.question_trend.labels, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisLabel: { color: '#94a3b8' }, axisTick: { show: false } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { color: '#94a3b8' } },
      series: [{
        type: 'line', data: d.question_trend.values, smooth: true, symbol: 'circle', symbolSize: 8,
        lineStyle: { color: '#6366f1', width: 3 },
        itemStyle: { color: '#6366f1', borderWidth: 2, borderColor: '#fff' },
        areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(99,102,241,0.25)' }, { offset: 1, color: 'rgba(99,102,241,0.02)' }]) },
      }],
    })
    charts.push(c)
  }

  // 饼图
  if (pieEl.value) {
    const c = echarts.init(pieEl.value)
    c.setOption({
      tooltip: { trigger: 'item', backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#e2e8f0', textStyle: { color: '#1a1a2e' } },
      legend: { bottom: 10, textStyle: { color: '#64748b' }, itemWidth: 12, itemHeight: 12 },
      series: [{
        type: 'pie', radius: ['45%', '70%'], center: ['50%', '45%'],
        label: { formatter: '{b}\n{d}%', fontSize: 12, color: '#64748b' },
        labelLine: { length: 15, length2: 8 },
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        data: [
          { value: d.course_distribution.machine_learning, name: '机器学习' },
          { value: d.course_distribution.data_mining, name: '数据挖掘' },
        ],
        color: ['#6366f1', '#3b82f6'],
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
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}
.grid-2 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}
</style>
