<template>
  <div class="system-page">
    <!-- Section 1: System Health -->
    <el-card class="section-card">
      <template #header>
        <span class="card-title">系统健康状态</span>
      </template>
      <div class="health-grid">
        <div
          v-for="(status, key) in services"
          :key="key"
          class="health-item"
        >
          <span
            class="status-dot"
            :class="status.up ? 'dot-up' : 'dot-down'"
          ></span>
          <span class="service-name">{{ serviceName[key] || key }}</span>
          <el-tag
            :type="status.up ? 'success' : 'danger'"
            size="small"
          >
            {{ status.up ? '正常' : '异常' }}
          </el-tag>
        </div>
      </div>
    </el-card>

    <!-- Section 2: AI Model Status -->
    <el-card class="section-card">
      <template #header>
        <span class="card-title">AI 模型状态</span>
      </template>
      <el-descriptions :column="3" border>
        <el-descriptions-item label="LLM 名称">
          {{ modelStatus.llmName || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="LLM 状态">
          <el-tag
            :type="modelStatus.llmLoaded ? 'success' : 'info'"
            size="small"
          >
            {{ modelStatus.llmLoaded ? '已加载' : '未加载' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="显存占用">
          {{ modelStatus.vramUsage || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="Embedding 模型">
          {{ modelStatus.embeddingName || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="Embedding 状态">
          <el-tag
            :type="modelStatus.embeddingLoaded ? 'success' : 'info'"
            size="small"
          >
            {{ modelStatus.embeddingLoaded ? '已加载' : '未加载' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="向量数量">
          {{ modelStatus.vectorCount ?? '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="TTS 模型">
          {{ modelStatus.ttsName || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="TTS 状态">
          <el-tag
            :type="modelStatus.ttsLoaded ? 'success' : 'info'"
            size="small"
          >
            {{ modelStatus.ttsLoaded ? '已加载' : '未加载' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- Section 3: System Config -->
    <el-card class="section-card">
      <template #header>
        <span class="card-title">系统配置</span>
      </template>
      <el-form
        :model="config"
        label-width="200px"
        class="config-form"
      >
        <el-form-item label="LLM 模型">
          <el-input v-model="config.llmModel" placeholder="请输入模型名称" />
        </el-form-item>
        <el-form-item label="Temperature">
          <el-slider
            v-model="config.temperature"
            :min="0"
            :max="2"
            :step="0.1"
            show-input
            class="slider-field"
          />
        </el-form-item>
        <el-form-item label="最大 Token 数">
          <el-input-number
            v-model="config.maxTokens"
            :min="256"
            :max="8192"
            :step="256"
          />
        </el-form-item>
        <el-form-item label="RAG 检索数量">
          <el-input-number
            v-model="config.ragTopK"
            :min="1"
            :max="20"
          />
        </el-form-item>
        <el-form-item label="启用知识图谱增强">
          <el-switch v-model="config.enableKG" />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="saving"
            @click="saveConfig"
          >
            保存配置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Section 4: Announcements -->
    <el-card class="section-card">
      <template #header>
        <span class="card-title">系统公告</span>
      </template>
      <template v-if="announcements.length">
        <el-timeline>
          <el-timeline-item
            v-for="item in announcements"
            :key="item.id"
            :timestamp="item.time"
            placement="top"
          >
            <el-card shadow="hover" class="announcement-card">
              <h4>{{ item.title }}</h4>
              <p class="announcement-content">{{ item.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </template>
      <el-empty v-else description="暂无公告" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { systemAPI } from '@/api'

const services = reactive({
  mysql: { up: false },
  neo4j: { up: false },
  ollama: { up: false },
  faiss: { up: false },
  gpu: { up: false },
})

const serviceName = {
  mysql: 'MySQL',
  neo4j: 'Neo4j',
  ollama: 'Ollama (LLM)',
  faiss: 'FAISS',
  gpu: 'GPU',
}

const modelStatus = ref({
  llmName: '',
  llmLoaded: false,
  vramUsage: '',
  embeddingName: '',
  embeddingLoaded: false,
  vectorCount: 0,
  ttsName: '',
  ttsLoaded: false,
})

const config = reactive({
  llmModel: '',
  temperature: 0.7,
  maxTokens: 2048,
  ragTopK: 5,
  enableKG: false,
})

const saving = ref(false)
const announcements = ref([])

async function loadHealth() {
  try {
    const res = await systemAPI.getHealth()
    const data = res.data || res
    Object.keys(services).forEach((key) => {
      if (data[key] !== undefined) {
        services[key] = { up: !!data[key] }
      }
    })
  } catch {
    ElMessage.error('获取系统健康状态失败')
  }
}

async function loadModelStatus() {
  try {
    const res = await systemAPI.getModelStatus()
    modelStatus.value = res.data || res
  } catch {
    ElMessage.error('获取 AI 模型状态失败')
  }
}

async function loadConfig() {
  try {
    const res = await systemAPI.getConfig()
    const data = res.data || res
    Object.assign(config, data)
  } catch {
    ElMessage.error('获取系统配置失败')
  }
}

async function loadAnnouncements() {
  try {
    const res = await systemAPI.getAnnouncements()
    announcements.value = res.data || res || []
  } catch {
    ElMessage.error('获取系统公告失败')
  }
}

async function saveConfig() {
  saving.value = true
  try {
    await systemAPI.updateConfig({ ...config })
    ElMessage.success('配置保存成功')
  } catch {
    ElMessage.error('配置保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadHealth()
  loadModelStatus()
  loadConfig()
  loadAnnouncements()
})
</script>

<style scoped>
.system-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.section-card {
  margin-bottom: 20px;
}

.card-title {
  font-weight: 600;
  font-size: 16px;
}

/* Health Grid */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.health-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--el-fill-color-lighter, #f5f7fa);
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dot-up {
  background-color: #67c23a;
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.7);
}

.dot-down {
  background-color: #f56c6c;
  box-shadow: 0 0 8px rgba(245, 108, 108, 0.7);
}

.service-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

/* Config Form */
.config-form {
  max-width: 600px;
}

.slider-field {
  max-width: 300px;
}

/* Announcements */
.announcement-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.announcement-content {
  margin: 0;
  color: var(--el-text-color-secondary, #909399);
  font-size: 13px;
  line-height: 1.6;
}
</style>
