<template>
  <div class="teacher-layout">
    <!-- 左侧：教师形象卡 -->
    <aside class="teacher-card">
      <!-- 顶部渐变背景区域 -->
      <div class="teacher-hero">
        <div class="hero-pattern" />
        <div class="avatar-wrapper">
          <div class="avatar-ring">
            <div class="avatar-circle">
              <span class="avatar-emoji">👩‍🏫</span>
            </div>
          </div>
          <div class="avatar-glow" />
        </div>
      </div>

      <!-- 教师信息 -->
      <div class="teacher-info">
        <h2 class="teacher-name">{{ info.name }}</h2>
        <div class="teacher-status">
          <span class="status-dot" :class="{ online: info.status === 'online' }" />
          <span class="status-text">{{ info.status === 'online' ? '在线' : '离线' }}</span>
        </div>
      </div>

      <!-- 情绪选择器 -->
      <div class="emotion-section">
        <div class="section-label">教学风格</div>
        <div class="emotion-bar">
          <button
            v-for="e in info.emotions" :key="e"
            class="emotion-btn" :class="{ active: curEmotion === e }"
            @click="curEmotion = e"
          >
            <span class="emotion-icon">{{ emotionIcons[e] }}</span>
            <span class="emotion-text">{{ emotionMap[e] }}</span>
          </button>
        </div>
      </div>

      <!-- 学习进度卡 -->
      <div class="progress-card">
        <div class="progress-header">
          <span class="progress-icon">📊</span>
          <span class="progress-title">学习进度</span>
        </div>

        <div class="stat-row">
          <div class="stat-item">
            <div class="stat-value">{{ info.progress.total_questions }}</div>
            <div class="stat-label">总提问</div>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <div class="stat-value">{{ info.progress.study_hours }}<span class="stat-unit">h</span></div>
            <div class="stat-label">学习时长</div>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <div class="stat-value">{{ info.progress.level }}</div>
            <div class="stat-label">当前等级</div>
          </div>
        </div>

        <div class="topics-section">
          <div class="topics-group">
            <div class="topics-label">
              <span class="label-dot mastered" />
              已掌握
            </div>
            <div class="topics-tags">
              <span v-for="t in info.progress.mastered_topics" :key="t" class="topic-tag mastered">{{ t }}</span>
              <span v-if="!info.progress.mastered_topics.length" class="topics-empty">暂无</span>
            </div>
          </div>
          <div class="topics-group">
            <div class="topics-label">
              <span class="label-dot weak" />
              待加强
            </div>
            <div class="topics-tags">
              <span v-for="t in info.progress.weak_topics" :key="t" class="topic-tag weak">{{ t }}</span>
              <span v-if="!info.progress.weak_topics.length" class="topics-empty">暂无</span>
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧：对话区 -->
    <section class="chat-card">
      <div class="chat-head">
        <div class="chat-head-left">
          <div class="chat-head-avatar">师</div>
          <div>
            <div class="chat-head-name">与{{ info.name }}对话</div>
            <div class="chat-head-sub">智能辅导 · 随时提问</div>
          </div>
        </div>
        <div class="chat-head-badge">
          <span class="badge-dot" />
          AI 辅导中
        </div>
      </div>

      <div ref="chatBox" class="chat-body">
        <!-- 空状态 -->
        <div v-if="chatMsgs.length === 0" class="chat-empty">
          <div class="empty-icon">👋</div>
          <div class="empty-title">向{{ info.name }}提问吧！</div>
          <div class="empty-hint">任何学习上的问题都可以问我</div>
        </div>

        <!-- 消息列表 -->
        <div v-for="(m, i) in chatMsgs" :key="i" class="msg-row" :class="m.role">
          <div class="msg-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
            {{ m.role === 'user' ? '我' : '师' }}
          </div>
          <div class="msg-content">
            <div class="msg-bubble" v-html="renderMd(m.content)" />
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="chatLoading" class="msg-row assistant">
          <div class="msg-avatar ai">师</div>
          <div class="msg-content">
            <div class="msg-bubble">
              <div class="typing-dots"><span /><span /><span /></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-bar">
        <div class="input-wrapper">
          <el-input
            v-model="chatInput"
            placeholder="向老师提问，例如：这个知识点怎么理解？"
            @keydown.enter="sendChat"
          />
        </div>
        <el-button class="btn-send" :loading="chatLoading" @click="sendChat">
          发送
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import api from '@/api'

const chatBox = ref(null)
const info = ref({
  name: '小智老师', status: 'online', emotions: [],
  progress: { total_questions: 0, mastered_topics: [], weak_topics: [], study_hours: 0, level: '' },
})
const curEmotion = ref('normal')
const emotionMap = { normal: '平静', happy: '开心', thinking: '思考', encouraging: '鼓励' }
const emotionIcons = { normal: '😌', happy: '😊', thinking: '🤔', encouraging: '💪' }
const chatMsgs = ref([])
const chatInput = ref('')
const chatLoading = ref(false)

onMounted(async () => {
  const { data } = await api.get('/teacher/avatar')
  info.value = data
})

function renderMd(t) { if (!t) return ''; try { return marked.parse(t) } catch { return t } }

function scrollBottom() {
  nextTick(() => { if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight })
}

async function sendChat() {
  const q = chatInput.value.trim()
  if (!q || chatLoading.value) return
  chatMsgs.value.push({ role: 'user', content: q })
  chatInput.value = ''
  chatLoading.value = true
  scrollBottom()
  try {
    const { data } = await api.post('/teacher/chat', { question: q })
    chatMsgs.value.push({ role: 'assistant', content: data.answer })
  } catch {
    chatMsgs.value.push({ role: 'assistant', content: '老师暂时不在线，请稍后再试。' })
  }
  chatLoading.value = false
  scrollBottom()
}
</script>

<style scoped>
/* ===== 布局 ===== */
.teacher-layout {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
}

/* ===== 教师卡 ===== */
.teacher-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  border: 1px solid rgba(0,0,0,0.03);
}

/* Hero 渐变背景 */
.teacher-hero {
  position: relative;
  height: 180px;
  background: var(--gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.hero-pattern {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(circle at 20% 80%, rgba(255,255,255,0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 50%);
}

/* 头像容器 */
.avatar-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-ring {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 3px solid rgba(255,255,255,0.3);
}
.avatar-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.avatar-emoji {
  font-size: 64px;
  line-height: 1;
}
.avatar-glow {
  position: absolute;
  width: 160px;
  height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
  animation: glow-pulse 3s ease-in-out infinite;
  pointer-events: none;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

/* 教师信息 */
.teacher-info {
  text-align: center;
  padding: 20px 24px 0;
}
.teacher-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.3px;
}
.teacher-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 8px;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
  flex-shrink: 0;
}
.status-dot.online {
  background: #22c55e;
  box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
  animation: status-pulse 2s ease-in-out infinite;
}
@keyframes status-pulse {
  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); }
  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
}
.status-text {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

/* 情绪选择区 */
.emotion-section {
  padding: 20px 24px 0;
}
.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}
.emotion-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.emotion-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
}
.emotion-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary);
  background: var(--primary-bg);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.15);
}
.emotion-btn.active {
  background: var(--gradient);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.3);
}
.emotion-btn.active:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(79, 110, 247, 0.4);
}
.emotion-icon {
  font-size: 15px;
}
.emotion-text {
  font-size: 13px;
}

/* 学习进度卡 */
.progress-card {
  margin: 20px 16px 16px;
  padding: 20px;
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
}
.progress-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
}
.progress-icon {
  font-size: 18px;
}
.progress-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

/* 统计行 */
.stat-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 16px 0;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  margin-bottom: 16px;
}
.stat-item {
  flex: 1;
  text-align: center;
}
.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: -0.5px;
  line-height: 1.2;
}
.stat-unit {
  font-size: 14px;
  font-weight: 600;
}
.stat-label {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 4px;
  font-weight: 500;
}
.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--border);
}

/* 主题标签区 */
.topics-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.topics-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.topics-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}
.label-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}
.label-dot.mastered {
  background: var(--accent-green);
}
.label-dot.weak {
  background: var(--accent-orange);
}
.topics-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.topic-tag {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
.topic-tag.mastered {
  background: #ecfdf5;
  color: #059669;
  border: 1px solid #a7f3d0;
}
.topic-tag.weak {
  background: #fffbeb;
  color: #d97706;
  border: 1px solid #fde68a;
}
.topics-empty {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
}

/* ===== 对话卡 ===== */
.chat-card {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.03);
}

/* 对话头部 */
.chat-head {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(to bottom, #fafbff, var(--bg-card));
}
.chat-head-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.chat-head-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.25);
}
.chat-head-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}
.chat-head-sub {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}
.chat-head-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--primary-bg);
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  color: var(--primary);
}
.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  animation: badge-blink 2s infinite;
}
@keyframes badge-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* 对话主体 */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 空状态 */
.chat-empty {
  text-align: center;
  padding: 60px 20px;
}
.empty-icon {
  font-size: 56px;
  margin-bottom: 16px;
}
.empty-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}
.empty-hint {
  font-size: 13px;
  color: var(--text-muted);
}

/* 消息内容区 */
.msg-content {
  flex: 1;
  min-width: 0;
}

/* 输入区 */
.chat-input-bar {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex;
  gap: 12px;
  align-items: center;
  background: linear-gradient(to top, #fafbff, var(--bg-card));
}
.input-wrapper {
  flex: 1;
}
.input-wrapper :deep(.el-input__wrapper) {
  border-radius: 24px;
  padding: 4px 18px;
  box-shadow: 0 0 0 1px var(--border) inset;
  transition: all 0.25s;
}
.input-wrapper :deep(.el-input__wrapper:focus-within),
.input-wrapper :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-light) inset;
}
.btn-send {
  height: 44px;
  padding: 0 24px;
  border-radius: 22px;
  background: var(--gradient) !important;
  border: none !important;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.3);
  transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
}
.btn-send:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.4);
}
.btn-send:active {
  transform: translateY(0);
}

/* ===== 响应式 ===== */
@media (max-width: 1100px) {
  .teacher-layout {
    grid-template-columns: 1fr;
    height: auto;
    min-height: calc(100vh - 120px);
  }
  .teacher-card {
    max-height: none;
  }
  .chat-card {
    height: 500px;
  }
}
@media (max-width: 600px) {
  .teacher-layout {
    gap: 12px;
  }
  .teacher-hero {
    height: 140px;
  }
  .avatar-ring {
    width: 100px;
    height: 100px;
  }
  .avatar-circle {
    width: 84px;
    height: 84px;
  }
  .avatar-emoji {
    font-size: 44px;
  }
  .emotion-bar {
    gap: 6px;
  }
  .emotion-btn {
    padding: 6px 12px;
    font-size: 12px;
  }
  .stat-value {
    font-size: 20px;
  }
  .chat-card {
    height: 400px;
  }
  .chat-head-badge {
    display: none;
  }
}
</style>
