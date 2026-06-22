<template>
  <div class="files-page">
    <!-- Section 1: Upload Area -->
    <div class="card">
      <div class="card-title">上传文件</div>
      <el-upload
        class="upload-area"
        drag
        accept=".pdf,.txt,.docx,.md"
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileChange"
      >
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">拖拽文件到此处，或点击上传</div>
        <div class="upload-tip">支持 PDF、TXT、DOCX、MD 格式，文件不超过 50MB</div>
      </el-upload>

      <div class="upload-options">
        <el-select v-model="uploadCourse" placeholder="选择课程" style="width: 200px">
          <el-option label="机器学习" value="机器学习" />
          <el-option label="数据挖掘" value="数据挖掘" />
        </el-select>
        <el-input
          v-model="uploadTags"
          placeholder="标签（逗号分隔）"
          style="width: 260px"
          clearable
        />
        <el-button
          type="primary"
          :disabled="!pendingFile"
          :loading="uploading"
          @click="customUpload"
        >
          开始上传
        </el-button>
      </div>
    </div>

    <!-- Section 2: File List -->
    <div class="card" style="margin-top: 20px">
      <div class="card-title">
        <span>文件列表</span>
        <el-button
          style="margin-left: auto"
          :icon="Refresh"
          circle
          size="small"
          @click="loadFiles"
        />
      </div>
      <el-table :data="fileList" v-loading="tableLoading" stripe style="width: 100%">
        <el-table-column prop="name" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="course" label="课程" width="120" />
        <el-table-column prop="type" label="类型" width="80">
          <template #default="{ row }">
            {{ (row.type || row.name.split('.').pop()).toUpperCase() }}
          </template>
        </el-table-column>
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">
            {{ formatSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column prop="chunks" label="分块数" width="80" align="center" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.status === '已索引' ? 'success' : 'warning'"
              size="small"
            >
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.upload_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="downloadFile(row)">
              <el-icon><Download /></el-icon> 下载
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- Section 3: Index Management -->
    <div class="card" style="margin-top: 20px">
      <div class="card-title">向量索引管理</div>
      <el-button
        type="warning"
        :loading="rebuilding"
        @click="confirmRebuild"
      >
        重建 FAISS 索引
      </el-button>
      <p class="helper-text">
        重建索引会重新计算所有文件的向量，适用于切换 Embedding 模型后
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled, Refresh, Download } from '@element-plus/icons-vue'
import { filesAPI } from '@/api'

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const fileList = ref([])
const tableLoading = ref(false)
const rebuilding = ref(false)
const uploading = ref(false)
const uploadCourse = ref('机器学习')
const uploadTags = ref('')
const pendingFile = ref(null)

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatSize(bytes) {
  if (bytes == null || bytes === 0) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

function formatTime(t) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

// ---------------------------------------------------------------------------
// File list
// ---------------------------------------------------------------------------
async function loadFiles() {
  tableLoading.value = true
  try {
    const res = await filesAPI.list()
    fileList.value = res.data || []
  } catch {
    ElMessage.error('加载文件列表失败')
  } finally {
    tableLoading.value = false
  }
}

// ---------------------------------------------------------------------------
// Upload
// ---------------------------------------------------------------------------
function handleFileChange(uploadFile) {
  const raw = uploadFile.raw
  if (!raw) return
  // Validate size (50 MB)
  if (raw.size > 50 * 1024 * 1024) {
    ElMessage.warning('文件大小不能超过 50MB')
    return
  }
  // Validate extension
  const ext = raw.name.split('.').pop().toLowerCase()
  if (!['pdf', 'txt', 'docx', 'md'].includes(ext)) {
    ElMessage.warning('不支持的文件格式')
    return
  }
  pendingFile.value = raw
  ElMessage.success(`已选择文件：${raw.name}`)
}

async function customUpload() {
  if (!pendingFile.value) return
  uploading.value = true
  try {
    const tags = uploadTags.value
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
      .join(',')
    await filesAPI.upload(pendingFile.value, uploadCourse.value, tags)
    ElMessage.success('文件上传成功')
    pendingFile.value = null
    uploadTags.value = ''
    await loadFiles()
  } catch {
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

// ---------------------------------------------------------------------------
// Download
// ---------------------------------------------------------------------------
function downloadFile(row) {
  // If a real download URL exists on the row, use it; otherwise construct one
  const url = row.download_url || `/api/v1/files/${row.id}/download`
  const a = document.createElement('a')
  a.href = url
  a.download = row.name
  a.click()
}

// ---------------------------------------------------------------------------
// Rebuild index
// ---------------------------------------------------------------------------
async function confirmRebuild() {
  try {
    await ElMessageBox.confirm(
      '确定要重建 FAISS 向量索引吗？此操作会重新计算所有文件的向量，可能需要较长时间。',
      '确认重建索引',
      { confirmButtonText: '确认重建', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    // User cancelled
    return
  }

  rebuilding.value = true
  try {
    await filesAPI.rebuildIndex()
    ElMessage.success('索引重建任务已提交')
  } catch {
    ElMessage.error('重建索引失败')
  } finally {
    rebuilding.value = false
  }
}

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------
onMounted(() => {
  loadFiles()
})
</script>

<style scoped>
.files-page {
  max-width: 1000px;
  margin: 0 auto;
}

/* ---- Upload Area ---- */
.upload-area {
  width: 100%;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  transition: var(--transition);
}

.upload-area :deep(.el-upload-dragger:hover) {
  border-color: var(--primary);
}

.upload-icon {
  font-size: 48px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.upload-text {
  font-size: 15px;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.upload-tip {
  font-size: 12px;
  color: var(--text-muted);
}

/* ---- Upload Options ---- */
.upload-options {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 18px;
  flex-wrap: wrap;
}

/* ---- Helper Text ---- */
.helper-text {
  margin-top: 12px;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.6;
}
</style>
