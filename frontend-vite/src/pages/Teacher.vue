<template>
  <div class="teacher-layout">
    <!-- 左侧：教师形象 -->
    <div class="teacher-card">
      <div class="teacher-bg" />
      <div class="avatar-circle">
        <span style="font-size:100px;opacity:.9">👩‍🏫</span>
      </div>
      <div class="teacher-name">{{ info.name }}</div>
      <div class="teacher-status">
        <span class="status-dot" />
        {{ info.status === 'online' ? '在线' : '离线' }}
      </div>

      <div class="emotion-bar">
        <button
          v-for="e in info.emotions" :key="e"
          class="emotion-btn" :class="{ active: curEmotion === e }"
          @click="curEmotion = e"
        >{{ emotionMap[e] }}</button>
      </div>

      <!-- 学习进度卡 -->
      <div class="progress-card">
        <div class="card-title" style="font-size:14px">学习进度</div>
        <div class="stat-row">
          <div class="stat-item">
            <div class="stat-num">{{ info.progress.total_questions }}</div>
            <div class="stat-lbl">总提问</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{{ info.progress.study_hours }}h</div>
            <div class="stat-lbl">学习时长</div>
          </div>
          <div class="stat-item">
            <div class="stat-num">{{ info.progress.level }}</div>
            <div class="stat-lbl">当前等级</div>
          </div>
        </div>
        <div class="tag-group">
          <span class="tag-lbl">已掌握</span>
          <el-tag v-for="t in info.progress.mastered_topics" :key="t" size="small" type="success">{{ t }}</el-tag>
        </div>
        <div class="tag-group">
          <span class="tag-lbl">待加强</span>
          <el-tag v-for="t in info.progress.weak_topics" :key="t" size="small" type="warning">{{ t }}</el-tag>
        </div>
      </div>
    </div>

    <!-- 右侧：对话 -->
    <div class="chat-card">
      <div class="chat-head">与{{ info.name }}对话</div>
      <div ref="chatBox" class="chat-body">
        <div v-if="chatMsgs.length === 0" class="qa-empty">
          <div style="font-size:40px;margin-bottom:12px">👋</div>
          <div>向{{ info.name }}提问吧！</div>
        </div>
        <div v-for="(m, i) in chatMsgs" :key="i" class="msg-row" :class="m.role">
          <div class="msg-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
            {{ m.role === 'user' ? '我' : '师' }}
          </div>
          <div class="msg-bubble" v-html="renderMd(m.content)" />
        </div>
        <div v-if="chatLoading" class="msg-row assistant">
          <div class="msg-avatar ai">师</div>
          <div class="msg-bubble"><div class="typing-dots"><span /><span /><span /></div></div>
        </div>
      </div>
      <div class="chat-input-bar">
        <el-input v-model="chatInput" placeholder="向老师提问..." @keydown.enter="sendChat" />
        <el-button class="btn-gradient" :loading="chatLoading" @click="sendChat">发送</el-button>
      </div>
    </div>
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
.teacher-layout {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  height: calc(100vh - 120px);
}

/* 教师卡 */
.teacher-card {
  background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
  display: flex; flex-direction: column; align-items: center; padding: 30px;
  position: relative; overflow-y: auto;
}
.teacher-bg {
  position: absolute; inset: 0; background: var(--gradient-soft); opacity: 0.4;
}
.avatar-circle {
  width: 220px; height: 220px; border-radius: 50%; background: var(--gradient);
  display: flex; align-items: center; justify-content: center;
  position: relative; z-index: 1;
  box-shadow: 0 20px 60px rgba(99,102,241,0.2);
}
.teacher-name {
  margin-top: 18px; font-size: 20px; font-weight: 700; position: relative; z-index: 1;
}
.teacher-status {
  display: flex; align-items: center; gap: 6px; margin-top: 6px;
  font-size: 13px; color: var(--text-secondary); position: relative; z-index: 1;
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #22c55e;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }

.emotion-bar {
  display: flex; gap: 8px; margin-top: 16px; position: relative; z-index: 1;
}
.emotion-btn {
  padding: 6px 16px; border-radius: 20px; border: 1px solid var(--border);
  background: var(--bg-card); cursor: pointer; font-size: 13px; transition: all 0.2s;
}
.emotion-btn:hover { border-color: var(--primary); color: var(--primary); }
.emotion-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }

.progress-card {
  width: 100%; margin-top: 20px; padding: 16px; background: var(--bg-card);
  border-radius: var(--radius); box-shadow: var(--shadow); position: relative; z-index: 1;
}
.stat-row { display: flex; gap: 12px; margin-bottom: 14px; }
.stat-item { flex: 1; text-align: center; }
.stat-num { font-size: 22px; font-weight: 700; color: var(--primary); }
.stat-lbl { font-size: 12px; color: var(--text-muted); }
.tag-group { margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.tag-lbl { font-size: 12px; color: var(--text-muted); margin-right: 4px; }

/* 对话卡 */
.chat-card {
  background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
  display: flex; flex-direction: column; overflow: hidden;
}
.chat-head {
  padding: 16px 20px; border-bottom: 1px solid var(--border); font-weight: 600;
}
.chat-body { flex: 1; overflow-y: auto; padding: 20px; }
.qa-empty { text-align: center; padding: 50px 0; color: var(--text-muted); }
.chat-input-bar {
  padding: 14px 20px; border-top: 1px solid var(--border);
  display: flex; gap: 12px;
}
.btn-gradient {
  background: var(--gradient) !important; border: none !important; color: #fff; font-weight: 600;
}

@media (max-width: 1000px) {
  .teacher-layout { grid-template-columns: 1fr; }
}
</style>
