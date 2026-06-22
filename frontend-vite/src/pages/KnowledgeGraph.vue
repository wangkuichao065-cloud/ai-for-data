<template>
  <div class="kg-page">
    <!-- 工具栏 -->
    <div class="kg-toolbar">
      <el-select v-model="courseFilter" placeholder="选择课程" clearable style="width: 160px">
        <el-option label="全部课程" value="" />
        <el-option label="机器学习" value="ml" />
        <el-option label="数据挖掘" value="dm" />
      </el-select>
      <el-input v-model="searchKey" placeholder="搜索知识点..." :prefix-icon="Search" clearable style="width: 240px" @keyup.enter="onSearch" />
      <el-button type="primary" :icon="Search" class="btn-primary" @click="onSearch">搜索</el-button>
      <div style="flex:1" />
      <el-tag v-for="cat in categories" :key="cat.name" :color="cat.color" effect="dark" size="small" class="cat-tag">{{ cat.name }}</el-tag>
    </div>

    <!-- 图谱主体 -->
    <div class="kg-wrapper">
      <div ref="graphEl" class="kg-canvas" />

      <!-- 详情面板 -->
      <transition name="slide">
        <div v-if="detailOpen" class="kg-detail">
          <div class="detail-head">
            <span class="detail-name">{{ detail.name }}</span>
            <el-button :icon="Close" circle size="small" @click="detailOpen = false" />
          </div>
          <el-tag :color="tagColor" effect="dark" size="small" style="border:none;color:#fff;margin-bottom:12px">{{ detail.type }}</el-tag>
          <p class="detail-desc">{{ detail.desc }}</p>

          <div v-if="detail.related?.length" class="detail-section">
            <div class="detail-section-title">关联知识点</div>
            <div v-for="(r, i) in detail.related" :key="i" class="detail-rel-item">
              <el-icon><Link /></el-icon>
              <span style="flex:1">{{ r.name }}</span>
              <el-tag size="small" type="info">{{ r.relation }}</el-tag>
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
import { Search, Close, Link } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const graphEl = ref(null)
const courseFilter = ref('')
const searchKey = ref('')
const categories = ref([])
const detailOpen = ref(false)
const detail = ref({ name: '', type: '', desc: '', related: [] })
const tagColor = ref('#6366f1')
let chart = null

const RELATION_COLORS = {
  CONTAINS: '#6366f1', BELONGS_TO: '#3b82f6', EXTENDS: '#22c55e',
  BASED_ON: '#22c55e', USES: '#f97316', APPLIES_TO: '#ec4899',
  PREREQ: '#8b5cf6', RELATED_TO: '#94a3b8', EXPLAINS: '#94a3b8',
}

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
    itemStyle: { color: d.categories[n.category]?.color || '#6366f1' },
    label: { show: n.symbolSize >= 30, fontSize: 11, color: '#1a1a2e' },
  }))

  const edges = d.edges.map(e => ({
    source: e.source,
    target: e.target,
    label: { show: true, formatter: e.relation, fontSize: 10, color: '#94a3b8' },
    lineStyle: { color: RELATION_COLORS[e.relation] || '#c7d2fe', width: 1.5, curveness: 0.15 },
  }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: '#e2e8f0',
      textStyle: { color: '#1a1a2e', fontSize: 13 },
      formatter(p) {
        if (p.dataType === 'node') {
          const cat = d.categories[p.data.category]
          return `<b>${p.data.name}</b><br/>类型：${cat?.name || '未知'}`
        }
        return `${p.data.source} → ${p.data.target}`
      },
    },
    legend: {
      data: d.categories.map(c => c.name),
      top: 10,
      textStyle: { color: '#64748b', fontSize: 12 },
      itemWidth: 14, itemHeight: 14,
    },
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
      force: { repulsion: 300, gravity: 0.08, edgeLength: [80, 200], friction: 0.6 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3 },
        label: { fontSize: 13, fontWeight: 700 },
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
      detail.value = { name: params.data.name, type: cat?.name || '未知', desc: '点击其他节点查看更多详情，或等待后端接入完整数据。', related: [] }
    }
    tagColor.value = d.categories[params.data.category]?.color || '#6366f1'
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
.kg-page { display: flex; flex-direction: column; height: calc(100vh - 120px); }

.kg-toolbar {
  display: flex; align-items: center; gap: 12px; margin-bottom: 14px; flex-wrap: wrap;
}
.btn-primary {
  background: var(--gradient) !important;
  border: none !important;
}
.cat-tag { border: none; color: #fff; }

.kg-wrapper {
  flex: 1; background: var(--bg-card); border-radius: var(--radius);
  box-shadow: var(--shadow); overflow: hidden; position: relative;
}
.kg-canvas { width: 100%; height: 100%; }

.kg-detail {
  position: absolute; right: 0; top: 0; width: 340px; height: 100%;
  background: var(--bg-card); border-left: 1px solid var(--border);
  padding: 22px; overflow-y: auto; z-index: 10;
}
.detail-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px; padding-bottom: 12px; border-bottom: 1px solid var(--border);
}
.detail-name { font-size: 18px; font-weight: 700; }
.detail-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.8; margin-bottom: 16px; }
.detail-section { margin-bottom: 16px; }
.detail-section-title { font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.detail-rel-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  border-radius: 10px; background: var(--bg); margin-bottom: 6px;
  cursor: pointer; transition: all 0.2s; font-size: 13px;
}
.detail-rel-item:hover { background: var(--primary-bg); color: var(--primary); }

.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(100%); }
</style>
