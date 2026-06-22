<template>
  <div class="analysis">
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <el-date-picker v-model="dateRange" type="daterange" start-placeholder="开始日期" end-placeholder="结束日期" style="width:300px" />
      <el-select v-model="course" placeholder="课程" clearable style="width:140px">
        <el-option label="全部" value="" />
        <el-option label="机器学习" value="ml" />
        <el-option label="数据挖掘" value="dm" />
      </el-select>
      <el-button type="primary" class="btn-gradient">查询</el-button>
    </div>

    <!-- 趋势 + 热力图 -->
    <div class="grid-2">
      <div class="card">
        <div class="card-title">提问趋势分析</div>
        <div ref="trendEl" class="chart-box-lg" />
      </div>
      <div class="card">
        <div class="card-title">知识点热度</div>
        <div ref="heatEl" class="chart-box-lg" />
      </div>
    </div>

    <!-- 活跃 + 时段 -->
    <div class="grid-2" style="margin-top:20px">
      <div class="card">
        <div class="card-title">每日活跃用户</div>
        <div ref="actEl" class="chart-box" />
      </div>
      <div class="card">
        <div class="card-title">活跃时段分布</div>
        <div ref="hourEl" class="chart-box" />
      </div>
    </div>

    <!-- 满意度 + 雷达 -->
    <div class="grid-2" style="margin-top:20px">
      <div class="card">
        <div class="card-title">满意度分布</div>
        <div ref="satEl" class="chart-box" />
      </div>
      <div class="card">
        <div class="card-title">知识掌握度</div>
        <div ref="radarEl" class="chart-box" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const trendEl = ref(null)
const heatEl = ref(null)
const actEl = ref(null)
const hourEl = ref(null)
const satEl = ref(null)
const radarEl = ref(null)
const dateRange = ref(null)
const course = ref('')
let charts = []

const tooltipStyle = {
  backgroundColor: 'rgba(255,255,255,0.96)',
  borderColor: '#e2e8f0',
  textStyle: { color: '#1a1a2e', fontSize: 13 },
}

onMounted(async () => {
  const [trendRes, heatRes, actRes, satRes, radarRes] = await Promise.all([
    api.get('/dashboard/question-trend'),
    api.get('/dashboard/topic-heatmap'),
    api.get('/dashboard/user-activity'),
    api.get('/dashboard/satisfaction'),
    api.get('/dashboard/mastery-radar'),
  ])

  await nextFrame()

  // 趋势
  if (trendEl.value) {
    const c = echarts.init(trendEl.value)
    const td = trendRes.data
    c.setOption({
      tooltip: { trigger: 'axis', ...tooltipStyle },
      legend: { data: ['机器学习', '数据挖掘'], top: 5, right: 10, textStyle: { color: '#64748b' }, itemWidth: 16, itemHeight: 3 },
      grid: { top: 50, right: 20, bottom: 30, left: 50 },
      xAxis: { type: 'category', data: td.labels, axisLine: { lineStyle: { color: '#e2e8f0' } }, axisLabel: { color: '#94a3b8', fontSize: 11, rotate: 30 }, axisTick: { show: false } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { color: '#94a3b8' } },
      series: [
        {
          name: '机器学习', type: 'line', data: td.ml, smooth: true, symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#6366f1', width: 2.5 }, itemStyle: { color: '#6366f1' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(99,102,241,0.15)' }, { offset: 1, color: 'rgba(99,102,241,0.01)' }]) },
        },
        {
          name: '数据挖掘', type: 'line', data: td.dm, smooth: true, symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#3b82f6', width: 2.5 }, itemStyle: { color: '#3b82f6' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(59,130,246,0.15)' }, { offset: 1, color: 'rgba(59,130,246,0.01)' }]) },
        },
      ],
    })
    charts.push(c)
  }

  // 热力图
  if (heatEl.value) {
    const c = echarts.init(heatEl.value)
    const hd = heatRes.data
    const heatData = []
    hd.matrix.forEach((row, ci) => row.forEach((v, ti) => heatData.push([ti, ci, v])))
    c.setOption({
      tooltip: {
        ...tooltipStyle, trigger: 'item',
        formatter: p => `${hd.topics[p.data[0]]}<br>${hd.courses[p.data[1]]}：${p.data[2]} 次提问`,
      },
      grid: { top: 20, right: 20, bottom: 70, left: 100 },
      xAxis: { type: 'category', data: hd.topics, axisLabel: { color: '#64748b', fontSize: 11, rotate: 30 }, axisTick: { show: false }, splitArea: { show: true, areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.04)'] } } },
      yAxis: { type: 'category', data: hd.courses, axisLabel: { color: '#64748b' } },
      visualMap: { min: 0, max: 30, calculable: true, orient: 'horizontal', left: 'center', bottom: 5, inRange: { color: ['#e0e7ff', '#818cf8', '#6366f1', '#4f46e5', '#3730a3'] }, textStyle: { color: '#64748b' } },
      series: [{ type: 'heatmap', data: heatData, label: { show: true, color: '#fff', fontSize: 13, fontWeight: 600 }, itemStyle: { borderColor: '#fff', borderWidth: 3, borderRadius: 4 }, emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(99,102,241,0.4)' } } }],
    })
    charts.push(c)
  }

  // 每日活跃
  if (actEl.value) {
    const c = echarts.init(actEl.value)
    const ad = actRes.data
    c.setOption({
      tooltip: { trigger: 'axis', ...tooltipStyle },
      grid: { top: 20, right: 20, bottom: 30, left: 50 },
      xAxis: { type: 'category', data: ad.daily.map(d => d.date), axisLine: { lineStyle: { color: '#e2e8f0' } }, axisLabel: { color: '#94a3b8' }, axisTick: { show: false } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { color: '#94a3b8' } },
      series: [{
        type: 'bar', data: ad.daily.map(d => d.count), barWidth: '45%',
        itemStyle: { borderRadius: [6, 6, 0, 0], color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#818cf8' }, { offset: 1, color: '#6366f1' }]) },
      }],
    })
    charts.push(c)
  }

  // 时段分布
  if (hourEl.value) {
    const c = echarts.init(hourEl.value)
    const ad = actRes.data
    c.setOption({
      tooltip: { trigger: 'axis', ...tooltipStyle },
      grid: { top: 20, right: 20, bottom: 30, left: 50 },
      xAxis: { type: 'category', data: ad.hourly.map(d => d.hour + ':00'), axisLine: { lineStyle: { color: '#e2e8f0' } }, axisLabel: { color: '#94a3b8', fontSize: 11 }, axisTick: { show: false } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9', type: 'dashed' } }, axisLabel: { color: '#94a3b8' } },
      series: [{
        type: 'bar', data: ad.hourly.map(d => d.count), barWidth: '55%',
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: p => p.data >= 20 ? '#6366f1' : p.data >= 12 ? '#818cf8' : '#c7d2fe',
        },
      }],
    })
    charts.push(c)
  }

  // 满意度
  if (satEl.value) {
    const c = echarts.init(satEl.value)
    const sd = satRes.data
    c.setOption({
      tooltip: { trigger: 'item', ...tooltipStyle, formatter: '{b}: {c} 次 ({d}%)' },
      legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#64748b' }, itemWidth: 12, itemHeight: 12 },
      series: [{
        type: 'pie', radius: ['50%', '75%'], center: ['40%', '50%'],
        label: { show: false },
        emphasis: {
          label: { show: true, fontSize: 20, fontWeight: 700, formatter: p => p.data.name + '\n' + p.percent.toFixed(1) + '%' },
        },
        labelLine: { show: false },
        itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
        data: [
          { value: sd.distribution[5], name: '5星' },
          { value: sd.distribution[4], name: '4星' },
          { value: sd.distribution[3], name: '3星' },
          { value: sd.distribution[2], name: '2星' },
          { value: sd.distribution[1], name: '1星' },
        ],
        color: ['#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff'],
      }],
      graphic: [
        { type: 'text', left: '36%', top: '42%', style: { text: sd.avg.toFixed(1), textAlign: 'center', fill: '#1a1a2e', fontSize: 28, fontWeight: 700 } },
        { type: 'text', left: '36%', top: '56%', style: { text: '平均评分', textAlign: 'center', fill: '#94a3b8', fontSize: 12 } },
      ],
    })
    charts.push(c)
  }

  // 雷达图
  if (radarEl.value) {
    const c = echarts.init(radarEl.value)
    const rd = radarRes.data
    c.setOption({
      tooltip: { trigger: 'item', ...tooltipStyle },
      radar: {
        indicator: rd.indicators.map(n => ({ name: n, max: 1 })),
        radius: '65%',
        axisName: { color: '#64748b', fontSize: 12 },
        splitArea: { areaStyle: { color: ['rgba(99,102,241,0.02)', 'rgba(99,102,241,0.04)', 'rgba(99,102,241,0.06)', 'rgba(99,102,241,0.08)', 'rgba(99,102,241,0.10)'] } },
        splitLine: { lineStyle: { color: '#e2e8f0' } },
        axisLine: { lineStyle: { color: '#e2e8f0' } },
      },
      series: [{
        type: 'radar',
        data: [{
          value: rd.values, name: '掌握度', symbol: 'circle', symbolSize: 6,
          lineStyle: { color: '#6366f1', width: 2 },
          itemStyle: { color: '#6366f1' },
          areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(99,102,241,0.35)' }, { offset: 1, color: 'rgba(99,102,241,0.05)' }]) },
        }],
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
.filter-bar {
  display: flex; align-items: center; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;
}
.btn-gradient {
  background: var(--gradient) !important; border: none !important;
}
.grid-2 {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px;
}
@media (max-width: 860px) {
  .grid-2 { grid-template-columns: 1fr; }
}
</style>
