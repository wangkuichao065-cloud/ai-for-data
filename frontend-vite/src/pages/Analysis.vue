<template>
  <div class="analysis">
    <!-- 筛选栏 -->
    <div class="filter-card">
      <div class="filter-inner">
        <div class="filter-left">
          <span class="filter-label">数据筛选</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 300px"
          />
          <el-select v-model="course" placeholder="课程" clearable style="width: 150px">
            <el-option label="全部" value="" />
            <el-option label="机器学习" value="ml" />
            <el-option label="数据挖掘" value="dm" />
          </el-select>
        </div>
        <el-button type="primary" class="btn-search">查询</el-button>
      </div>
    </div>

    <!-- 趋势 + 热力图 -->
    <div class="chart-grid">
      <div class="chart-card">
        <div class="card-header">
          <div class="card-title">提问趋势分析</div>
          <span class="card-subtitle">双课程对比</span>
        </div>
        <div ref="trendEl" class="chart-box-lg" />
      </div>
      <div class="chart-card">
        <div class="card-header">
          <div class="card-title">知识点热度</div>
          <span class="card-subtitle">跨课程提问分布</span>
        </div>
        <div ref="heatEl" class="chart-box-lg" />
      </div>
    </div>

    <!-- 活跃 + 时段 -->
    <div class="chart-grid">
      <div class="chart-card">
        <div class="card-header">
          <div class="card-title">每日活跃用户</div>
          <span class="card-subtitle">近30日</span>
        </div>
        <div ref="actEl" class="chart-box" />
      </div>
      <div class="chart-card">
        <div class="card-header">
          <div class="card-title">活跃时段分布</div>
          <span class="card-subtitle">24小时</span>
        </div>
        <div ref="hourEl" class="chart-box" />
      </div>
    </div>

    <!-- 满意度 + 雷达 -->
    <div class="chart-grid">
      <div class="chart-card">
        <div class="card-header">
          <div class="card-title">满意度分布</div>
          <span class="card-subtitle">用户评分</span>
        </div>
        <div ref="satEl" class="chart-box" />
      </div>
      <div class="chart-card">
        <div class="card-header">
          <div class="card-title">知识掌握度</div>
          <span class="card-subtitle">综合能力</span>
        </div>
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

/* ── Theme constants ────────────────────────────── */
const PRIMARY = '#4f6ef7'
const PRIMARY_DARK = '#3b5de7'
const PURPLE = '#7c3aed'
const PURPLE_LIGHT = '#8b5cf6'
const BLUE = '#3b82f6'
const BORDER_COLOR = '#e8ecf4'
const TEXT_SEC = '#64748b'
const TEXT_MUTED = '#94a3b8'
const GRID_LINE = '#f1f5f9'

const tooltipStyle = {
  backgroundColor: '#ffffff',
  borderColor: BORDER_COLOR,
  borderWidth: 1,
  padding: [10, 14],
  textStyle: { color: '#1e293b', fontSize: 13 },
  extraCssText: 'box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-radius: 10px;',
}

/* Shared axis styles */
const axisLineStyle = { lineStyle: { color: BORDER_COLOR } }
const axisLabelStyle = { color: TEXT_MUTED, fontSize: 11 }
const splitLineStyle = { lineStyle: { color: GRID_LINE, type: 'dashed' } }

onMounted(async () => {
  const [trendRes, heatRes, actRes, satRes, radarRes] = await Promise.all([
    api.get('/dashboard/question-trend'),
    api.get('/dashboard/topic-heatmap'),
    api.get('/dashboard/user-activity'),
    api.get('/dashboard/satisfaction'),
    api.get('/dashboard/mastery-radar'),
  ])

  await nextFrame()

  /* ── 1. 提问趋势 (dual line) ─────────────────── */
  if (trendEl.value) {
    const c = echarts.init(trendEl.value)
    const td = trendRes.data
    c.setOption({
      tooltip: { trigger: 'axis', ...tooltipStyle },
      legend: {
        data: ['机器学习', '数据挖掘'],
        top: 4,
        right: 12,
        textStyle: { color: TEXT_SEC, fontSize: 12 },
        itemWidth: 18,
        itemHeight: 3,
        itemGap: 20,
      },
      grid: { top: 50, right: 24, bottom: 36, left: 52 },
      xAxis: {
        type: 'category',
        data: td.labels,
        axisLine: axisLineStyle,
        axisLabel: { ...axisLabelStyle, rotate: 30 },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        splitLine: splitLineStyle,
        axisLabel: { color: TEXT_MUTED },
      },
      series: [
        {
          name: '机器学习',
          type: 'line',
          data: td.ml,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: PRIMARY, width: 2.5 },
          itemStyle: { color: PRIMARY },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(79,110,247,0.18)' },
              { offset: 1, color: 'rgba(79,110,247,0.01)' },
            ]),
          },
        },
        {
          name: '数据挖掘',
          type: 'line',
          data: td.dm,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: { color: PURPLE, width: 2.5 },
          itemStyle: { color: PURPLE },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(124,58,237,0.15)' },
              { offset: 1, color: 'rgba(124,58,237,0.01)' },
            ]),
          },
        },
      ],
    })
    charts.push(c)
  }

  /* ── 2. 热力图 ────────────────────────────────── */
  if (heatEl.value) {
    const c = echarts.init(heatEl.value)
    const hd = heatRes.data
    const heatData = []
    hd.matrix.forEach((row, ci) =>
      row.forEach((v, ti) => heatData.push([ti, ci, v])),
    )
    c.setOption({
      tooltip: {
        ...tooltipStyle,
        trigger: 'item',
        formatter: p =>
          `${hd.topics[p.data[0]]}<br/>${hd.courses[p.data[1]]}：<b>${p.data[2]}</b> 次提问`,
      },
      grid: { top: 20, right: 24, bottom: 72, left: 100 },
      xAxis: {
        type: 'category',
        data: hd.topics,
        axisLabel: { color: TEXT_SEC, fontSize: 11, rotate: 30 },
        axisTick: { show: false },
        splitArea: {
          show: true,
          areaStyle: {
            color: ['rgba(79,110,247,0.02)', 'rgba(124,58,237,0.03)'],
          },
        },
      },
      yAxis: {
        type: 'category',
        data: hd.courses,
        axisLabel: { color: TEXT_SEC, fontSize: 12 },
      },
      visualMap: {
        min: 0,
        max: 30,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: 4,
        inRange: {
          color: ['#e0e7ff', '#a5b4fc', '#818cf8', '#6366f1', '#4f46e5', '#3730a3'],
        },
        textStyle: { color: TEXT_SEC },
      },
      series: [
        {
          type: 'heatmap',
          data: heatData,
          label: {
            show: true,
            color: '#fff',
            fontSize: 13,
            fontWeight: 600,
          },
          itemStyle: {
            borderColor: '#fff',
            borderWidth: 3,
            borderRadius: 5,
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 12,
              shadowColor: 'rgba(79,110,247,0.45)',
            },
          },
        },
      ],
    })
    charts.push(c)
  }

  /* ── 3. 每日活跃 (bar) ────────────────────────── */
  if (actEl.value) {
    const c = echarts.init(actEl.value)
    const ad = actRes.data
    c.setOption({
      tooltip: { trigger: 'axis', ...tooltipStyle },
      grid: { top: 24, right: 24, bottom: 36, left: 52 },
      xAxis: {
        type: 'category',
        data: ad.daily.map(d => d.date),
        axisLine: axisLineStyle,
        axisLabel: { ...axisLabelStyle, rotate: 30 },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        splitLine: splitLineStyle,
        axisLabel: { color: TEXT_MUTED },
      },
      series: [
        {
          type: 'bar',
          data: ad.daily.map(d => d.count),
          barWidth: '45%',
          itemStyle: {
            borderRadius: [8, 8, 0, 0],
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: PRIMARY },
              { offset: 1, color: PURPLE },
            ]),
          },
          emphasis: {
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: PRIMARY_DARK },
                { offset: 1, color: '#6d28d9' },
              ]),
            },
          },
        },
      ],
    })
    charts.push(c)
  }

  /* ── 4. 活跃时段分布 (bar) ───────────────────── */
  if (hourEl.value) {
    const c = echarts.init(hourEl.value)
    const ad = actRes.data
    c.setOption({
      tooltip: { trigger: 'axis', ...tooltipStyle },
      grid: { top: 24, right: 24, bottom: 36, left: 52 },
      xAxis: {
        type: 'category',
        data: ad.hourly.map(d => d.hour + ':00'),
        axisLine: axisLineStyle,
        axisLabel: { ...axisLabelStyle, fontSize: 10 },
        axisTick: { show: false },
      },
      yAxis: {
        type: 'value',
        splitLine: splitLineStyle,
        axisLabel: { color: TEXT_MUTED },
      },
      series: [
        {
          type: 'bar',
          data: ad.hourly.map(d => d.count),
          barWidth: '55%',
          itemStyle: {
            borderRadius: [6, 6, 0, 0],
            color: p => {
              if (p.data >= 20) return PRIMARY
              if (p.data >= 12) return PURPLE_LIGHT
              return '#c7d2fe'
            },
          },
          emphasis: {
            itemStyle: {
              color: PURPLE,
            },
          },
        },
      ],
    })
    charts.push(c)
  }

  /* ── 5. 满意度分布 (donut) ───────────────────── */
  if (satEl.value) {
    const c = echarts.init(satEl.value)
    const sd = satRes.data
    c.setOption({
      tooltip: {
        trigger: 'item',
        ...tooltipStyle,
        formatter: '{b}: {c} 次 ({d}%)',
      },
      legend: {
        orient: 'vertical',
        right: 16,
        top: 'center',
        textStyle: { color: TEXT_SEC, fontSize: 13 },
        itemWidth: 12,
        itemHeight: 12,
        itemGap: 14,
      },
      series: [
        {
          type: 'pie',
          radius: ['48%', '74%'],
          center: ['38%', '50%'],
          label: { show: false },
          emphasis: {
            label: {
              show: true,
              fontSize: 20,
              fontWeight: 700,
              formatter: p => p.data.name + '\n' + p.percent.toFixed(1) + '%',
            },
            scaleSize: 6,
          },
          labelLine: { show: false },
          itemStyle: {
            borderRadius: 6,
            borderColor: '#fff',
            borderWidth: 3,
          },
          data: [
            { value: sd.distribution[5], name: '5星' },
            { value: sd.distribution[4], name: '4星' },
            { value: sd.distribution[3], name: '3星' },
            { value: sd.distribution[2], name: '2星' },
            { value: sd.distribution[1], name: '1星' },
          ],
          color: [PRIMARY, BLUE, PURPLE_LIGHT, '#a5b4fc', '#c7d2fe'],
        },
      ],
      graphic: [
        {
          type: 'text',
          left: '35%',
          top: '42%',
          style: {
            text: sd.avg.toFixed(1),
            textAlign: 'center',
            fill: '#1e293b',
            fontSize: 30,
            fontWeight: 700,
          },
        },
        {
          type: 'text',
          left: '35%',
          top: '57%',
          style: {
            text: '平均评分',
            textAlign: 'center',
            fill: TEXT_MUTED,
            fontSize: 12,
          },
        },
      ],
    })
    charts.push(c)
  }

  /* ── 6. 知识掌握度 (radar) ───────────────────── */
  if (radarEl.value) {
    const c = echarts.init(radarEl.value)
    const rd = radarRes.data
    c.setOption({
      tooltip: { trigger: 'item', ...tooltipStyle },
      radar: {
        indicator: rd.indicators.map(n => ({ name: n, max: 1 })),
        radius: '65%',
        center: ['50%', '54%'],
        axisName: { color: TEXT_SEC, fontSize: 12 },
        splitArea: {
          areaStyle: {
            color: [
              'rgba(79,110,247,0.02)',
              'rgba(79,110,247,0.04)',
              'rgba(79,110,247,0.06)',
              'rgba(79,110,247,0.08)',
              'rgba(79,110,247,0.10)',
            ],
          },
        },
        splitLine: { lineStyle: { color: BORDER_COLOR } },
        axisLine: { lineStyle: { color: BORDER_COLOR } },
      },
      series: [
        {
          type: 'radar',
          data: [
            {
              value: rd.values,
              name: '掌握度',
              symbol: 'circle',
              symbolSize: 7,
              lineStyle: { color: PRIMARY, width: 2.5 },
              itemStyle: { color: PRIMARY },
              areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                  { offset: 0, color: 'rgba(79,110,247,0.35)' },
                  { offset: 1, color: 'rgba(79,110,247,0.05)' },
                ]),
              },
            },
          ],
        },
      ],
    })
    charts.push(c)
  }

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  charts.forEach(c => c.dispose())
  window.removeEventListener('resize', handleResize)
})

function handleResize() {
  charts.forEach(c => c.resize())
}
function nextFrame() {
  return new Promise(r =>
    requestAnimationFrame(() => requestAnimationFrame(r)),
  )
}
</script>

<style scoped>
/* ── Page wrapper ─────────────────────────────── */
.analysis {
  padding: 4px;
}

/* ── Filter bar card ─────────────────────────── */
.filter-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  border: 1px solid rgba(0, 0, 0, 0.03);
  margin-bottom: 22px;
  transition: var(--transition);
}
.filter-card:hover {
  box-shadow: var(--shadow-lg);
}
.filter-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  flex-wrap: wrap;
  gap: 14px;
}
.filter-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.filter-label {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}
.filter-label::before {
  content: '';
  width: 4px;
  height: 18px;
  background: var(--gradient);
  border-radius: 2px;
  display: inline-block;
}

.btn-search {
  background: var(--gradient) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  border-radius: var(--radius-sm) !important;
  padding: 10px 28px !important;
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.25);
  transition: var(--transition);
}
.btn-search:hover {
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.35);
  filter: brightness(1.05);
  transform: translateY(-1px);
}

/* ── Chart grid ──────────────────────────────── */
.chart-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 22px;
  margin-bottom: 22px;
}

/* ── Chart card ──────────────────────────────── */
.chart-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  padding: 24px;
  box-shadow: var(--shadow);
  transition: var(--transition);
  border: 1px solid rgba(0, 0, 0, 0.03);
  position: relative;
  overflow: hidden;
}
.chart-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}
/* Subtle gradient accent along the top edge */
.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient);
  opacity: 0;
  transition: opacity 0.3s ease;
}
.chart-card:hover::before {
  opacity: 1;
}

/* ── Card header ─────────────────────────────── */
.chart-card .card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.chart-card .card-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}
/* Gradient bar indicator (matches global.css .card-title::before) */
.chart-card .card-title::before {
  content: '';
  width: 4px;
  height: 18px;
  background: var(--gradient);
  border-radius: 2px;
}
.card-subtitle {
  font-size: 12px;
  color: var(--text-muted);
  background: var(--primary-bg);
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 500;
}

/* ── Chart containers ────────────────────────── */
.chart-box {
  width: 100%;
  height: 320px;
}
.chart-box-lg {
  width: 100%;
  height: 380px;
}

/* ── Responsive ──────────────────────────────── */
@media (max-width: 1100px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 640px) {
  .filter-inner {
    flex-direction: column;
    align-items: stretch;
  }
  .filter-left {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-search {
    width: 100%;
    text-align: center;
  }
  .chart-card {
    padding: 16px;
  }
  .chart-box {
    height: 260px;
  }
  .chart-box-lg {
    height: 300px;
  }
}
</style>
