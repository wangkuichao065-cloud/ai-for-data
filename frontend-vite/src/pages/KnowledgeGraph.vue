<template>
  <div class="kg-page">
    <!-- Toolbar card -->
    <div class="kg-toolbar-card">
      <div class="kg-toolbar-row">
        <div class="kg-toolbar-left">
          <div class="kg-toolbar-title">
            <span class="kg-title-bar" />
            <span>知识图谱</span>
          </div>
          <el-select
            v-model="courseFilter"
            placeholder="选择课程"
            clearable
            class="kg-select"
          >
            <el-option label="全部课程" value="" />
            <el-option label="机器学习" value="ml" />
            <el-option label="数据挖掘" value="dm" />
          </el-select>
          <el-input
            v-model="searchKey"
            placeholder="搜索知识点..."
            :prefix-icon="Search"
            clearable
            class="kg-search-input"
            @keyup.enter="onSearch"
          />
          <el-button type="primary" :icon="Search" class="btn-primary" @click="onSearch">
            搜索
          </el-button>
        </div>
        <div class="kg-toolbar-right">
          <el-button
            :icon="detailOpen ? DArowRight : InfoFilled"
            text
            class="kg-info-toggle"
            @click="showLegend = !showLegend"
          >
            {{ showLegend ? '收起' : '图例' }}
          </el-button>
        </div>
      </div>

      <!-- Legend / category bar -->
      <transition name="legend-expand">
        <div v-if="showLegend" class="kg-legend-bar">
          <span class="kg-legend-label">分类：</span>
          <div
            v-for="cat in categories"
            :key="cat.name"
            class="kg-legend-chip"
          >
            <span class="kg-legend-dot" :style="{ background: cat.color }" />
            <span>{{ cat.name }}</span>
          </div>
          <div class="kg-legend-divider" />
          <span class="kg-legend-label">关系：</span>
          <div
            v-for="(color, rel) in relationColorMap"
            :key="rel"
            class="kg-legend-chip kg-legend-chip-sm"
          >
            <span class="kg-legend-line" :style="{ background: color }" />
            <span>{{ rel }}</span>
          </div>
        </div>
      </transition>
    </div>

    <!-- Graph main area -->
    <div class="kg-wrapper">
      <!-- Subtle background pattern layer -->
      <div class="kg-bg-pattern" />
      <div ref="graphEl" class="kg-canvas" />

      <!-- Detail panel -->
      <transition name="slide">
        <div v-if="detailOpen" class="kg-detail">
          <div class="detail-head">
            <div class="detail-head-info">
              <span class="detail-name">{{ detail.name }}</span>
              <el-tag
                :color="tagColor"
                effect="dark"
                size="small"
                class="detail-type-tag"
              >
                {{ detail.type }}
              </el-tag>
            </div>
            <el-button
              :icon="Close"
              circle
              size="small"
              class="detail-close-btn"
              @click="detailOpen = false"
            />
          </div>

          <div class="detail-body">
            <div class="detail-section">
              <div class="detail-section-title">
                <el-icon><Document /></el-icon>
                <span>描述</span>
              </div>
              <p class="detail-desc">{{ detail.desc }}</p>
            </div>

            <div v-if="detail.related?.length" class="detail-section">
              <div class="detail-section-title">
                <el-icon><Link /></el-icon>
                <span>关联知识点</span>
                <el-tag size="small" round type="info" class="detail-count-tag">
                  {{ detail.related.length }}
                </el-tag>
              </div>
              <div class="detail-rel-list">
                <div
                  v-for="(r, i) in detail.related"
                  :key="i"
                  class="detail-rel-item"
                >
                  <div class="rel-item-icon">
                    <el-icon :size="14"><Link /></el-icon>
                  </div>
                  <span class="rel-item-name">{{ r.name }}</span>
                  <el-tag size="small" type="info" round>{{ r.relation }}</el-tag>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'
import { Search, Close, Link, InfoFilled, DArrowRight as DArowRight, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const graphEl = ref(null)
const courseFilter = ref('')
const searchKey = ref('')
const categories = ref([])
const detailOpen = ref(false)
const showLegend = ref(true)
const detail = ref({ name: '', type: '', desc: '', related: [] })
const tagColor = ref('#4f6ef7')
let chart = null

const RELATION_COLORS = {
  CONTAINS: '#4f6ef7',
  BELONGS_TO: '#3b82f6',
  EXTENDS: '#10b981',
  BASED_ON: '#10b981',
  USES: '#f59e0b',
  APPLIES_TO: '#ec4899',
  PREREQ: '#7c3aed',
  RELATED_TO: '#94a3b8',
  EXPLAINS: '#94a3b8',
}

const relationColorMap = ref(RELATION_COLORS)

onMounted(async () => {
  const { data: d } = await api.get('/graph/visualization')
  categories.value = d.categories

  await nextFrame()
  if (!graphEl.value) return

  chart = echarts.init(graphEl.value)

  const nodes = d.nodes.map(n => ({
    id: n.id,
    name: n.name,
    category: n.category,
    symbolSize: n.symbolSize || 30,
    itemStyle: {
      color: d.categories[n.category]?.color || '#4f6ef7',
      borderColor: 'rgba(255,255,255,0.8)',
      borderWidth: 2,
      shadowBlur: 10,
      shadowColor: 'rgba(79,110,247,0.2)',
    },
    label: {
      show: n.symbolSize >= 30,
      fontSize: 11,
      color: '#1e293b',
      fontWeight: 500,
    },
  }))

  const edges = d.edges.map(e => ({
    source: e.source,
    target: e.target,
    label: {
      show: true,
      formatter: e.relation,
      fontSize: 10,
      color: '#94a3b8',
      padding: [2, 4],
      backgroundColor: 'rgba(255,255,255,0.75)',
      borderRadius: 3,
    },
    lineStyle: {
      color: RELATION_COLORS[e.relation] || '#c7d2fe',
      width: 1.5,
      curveness: 0.15,
      opacity: 0.7,
    },
  }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.98)',
      borderColor: '#e8ecf4',
      borderWidth: 1,
      padding: [12, 16],
      textStyle: { color: '#1e293b', fontSize: 13 },
      extraCssText: 'box-shadow: 0 4px 20px rgba(0,0,0,0.08); border-radius: 10px;',
      formatter(p) {
        if (p.dataType === 'node') {
          const cat = d.categories[p.data.category]
          return `<div style="font-weight:700;font-size:14px;margin-bottom:4px">${p.data.name}</div>
                  <div style="color:#64748b;font-size:12px">类型：${cat?.name || '未知'}</div>`
        }
        return `<span style="color:#64748b">${p.data.source} → ${p.data.target}</span>`
      },
    },
    legend: { show: false },
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [{
      type: 'graph',
      layout: 'force',
      data: nodes,
      links: edges,
      categories: d.categories.map(c => ({ name: c.name })),
      roam: true,
      draggable: true,
      force: {
        repulsion: 300,
        gravity: 0.08,
        edgeLength: [80, 200],
        friction: 0.6,
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, opacity: 1 },
        label: { fontSize: 13, fontWeight: 700 },
        itemStyle: {
          shadowBlur: 20,
          shadowColor: 'rgba(79,110,247,0.4)',
        },
      },
      label: { position: 'right' },
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: [0, 8],
    }],
  })

  chart.on('click', params => {
    if (params.dataType !== 'node') return
    const det = d.nodeDetails[params.data.id]
    if (det) {
      detail.value = det
    } else {
      const cat = d.categories[params.data.category]
      detail.value = {
        name: params.data.name,
        type: cat?.name || '未知',
        desc: '点击其他节点查看更多详情，或等待后端接入完整数据。',
        related: [],
      }
    }
    tagColor.value = d.categories[params.data.category]?.color || '#4f6ef7'
    detailOpen.value = true
  })

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  chart?.dispose()
  window.removeEventListener('resize', handleResize)
})

function handleResize() { chart?.resize() }
function nextFrame() { return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))) }
function onSearch() {
  if (!searchKey.value) return
  ElMessage.info('搜索功能将在后端接入后生效：' + searchKey.value)
}
</script>

<style scoped>
/* ===== Page layout ===== */
.kg-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  gap: 16px;
}

/* ===== Toolbar card ===== */
.kg-toolbar-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px 22px;
  border: 1px solid rgba(0, 0, 0, 0.03);
  flex-shrink: 0;
}

.kg-toolbar-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.kg-toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.kg-toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.kg-toolbar-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  margin-right: 8px;
}

.kg-title-bar {
  width: 4px;
  height: 18px;
  background: var(--gradient);
  border-radius: 2px;
  display: inline-block;
}

.kg-select {
  width: 150px;
}

.kg-search-input {
  width: 220px;
}

.btn-primary {
  background: var(--gradient) !important;
  border: none !important;
  color: #fff !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.25);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.35);
  filter: brightness(1.05);
}

.kg-info-toggle {
  color: var(--text-secondary) !important;
  font-size: 13px;
}

.kg-info-toggle:hover {
  color: var(--primary) !important;
}

/* ===== Legend bar ===== */
.kg-legend-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
}

.kg-legend-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  white-space: nowrap;
}

.kg-legend-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  background: var(--bg);
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: all 0.2s;
  cursor: default;
}

.kg-legend-chip:hover {
  background: var(--primary-bg);
  color: var(--primary);
}

.kg-legend-chip-sm {
  padding: 3px 10px;
  font-size: 11px;
}

.kg-legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
}

.kg-legend-line {
  width: 16px;
  height: 3px;
  border-radius: 2px;
  flex-shrink: 0;
}

.kg-legend-divider {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 4px;
}

/* Legend expand animation */
.legend-expand-enter-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.legend-expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.legend-expand-enter-from,
.legend-expand-leave-to {
  opacity: 0;
  max-height: 0;
  margin-top: 0;
  padding-top: 0;
}
.legend-expand-enter-to,
.legend-expand-leave-from {
  opacity: 1;
  max-height: 80px;
}

/* ===== Graph wrapper ===== */
.kg-wrapper {
  flex: 1;
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(0, 0, 0, 0.03);
  min-height: 0;
}

.kg-bg-pattern {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(ellipse 80% 60% at 30% 40%, rgba(79, 110, 247, 0.04) 0%, transparent 70%),
    radial-gradient(ellipse 60% 50% at 75% 60%, rgba(124, 58, 237, 0.03) 0%, transparent 70%),
    radial-gradient(circle at 50% 50%, rgba(79, 110, 247, 0.015) 1px, transparent 1px);
  background-size: 100% 100%, 100% 100%, 24px 24px;
}

.kg-canvas {
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 1;
}

/* ===== Detail panel ===== */
.kg-detail {
  position: absolute;
  right: 0;
  top: 0;
  width: 360px;
  height: 100%;
  background: var(--bg-card);
  border-left: 1px solid var(--border);
  box-shadow: -8px 0 30px rgba(0, 0, 0, 0.06);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24px 24px 18px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  gap: 12px;
}

.detail-head-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.detail-name {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.3;
  letter-spacing: -0.3px;
  word-break: break-word;
}

.detail-type-tag {
  border: none !important;
  color: #fff !important;
  align-self: flex-start;
  border-radius: 6px;
  font-weight: 500;
}

.detail-close-btn {
  flex-shrink: 0;
  border: 1px solid var(--border) !important;
  color: var(--text-muted) !important;
  transition: all 0.2s;
}

.detail-close-btn:hover {
  color: var(--text-primary) !important;
  border-color: var(--text-muted) !important;
}

.detail-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px 24px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-section-title .el-icon {
  color: var(--primary);
}

.detail-count-tag {
  margin-left: auto;
}

.detail-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.85;
  padding: 14px 16px;
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}

.detail-rel-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-rel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius-sm);
  background: var(--bg);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 13px;
  border: 1px solid transparent;
}

.detail-rel-item:hover {
  background: var(--primary-bg);
  color: var(--primary);
  border-color: rgba(79, 110, 247, 0.15);
  transform: translateX(4px);
}

.rel-item-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--primary-bg);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-rel-item:hover .rel-item-icon {
  background: var(--gradient);
  color: #fff;
}

.rel-item-name {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-rel-item:hover .rel-item-name {
  color: var(--primary);
}

/* ===== Slide transition ===== */
.slide-enter-active {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
}
.slide-leave-active {
  transition: transform 0.25s cubic-bezier(0.4, 0, 1, 1), opacity 0.2s ease;
}
.slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}
.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
.slide-enter-to {
  transform: translateX(0);
  opacity: 1;
}

/* ===== Responsive ===== */
@media (max-width: 1200px) {
  .kg-detail {
    width: 320px;
  }
  .kg-search-input {
    width: 180px;
  }
}

@media (max-width: 900px) {
  .kg-page {
    gap: 12px;
  }
  .kg-toolbar-card {
    padding: 14px 16px;
  }
  .kg-toolbar-left {
    gap: 8px;
  }
  .kg-toolbar-title {
    display: none;
  }
  .kg-select {
    width: 130px;
  }
  .kg-search-input {
    width: 160px;
  }
  .kg-detail {
    width: 300px;
  }
  .detail-head {
    padding: 18px 18px 14px;
  }
  .detail-body {
    padding: 16px 18px 18px;
  }
  .detail-name {
    font-size: 17px;
  }
  .kg-legend-bar {
    gap: 6px;
  }
  .kg-legend-chip {
    padding: 3px 8px;
    font-size: 11px;
  }
}

@media (max-width: 640px) {
  .kg-page {
    height: calc(100vh - 90px);
    gap: 10px;
  }
  .kg-toolbar-row {
    gap: 8px;
  }
  .kg-select {
    width: 100%;
    order: 10;
  }
  .kg-search-input {
    flex: 1;
    min-width: 0;
  }
  .kg-detail {
    width: 100%;
  }
  .detail-name {
    font-size: 16px;
  }
  .kg-legend-bar {
    gap: 4px;
  }
  .kg-legend-chip-sm {
    display: none;
  }
}
</style>
