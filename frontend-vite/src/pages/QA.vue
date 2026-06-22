<template>
  <div class="qa-layout">
    <!-- 左侧会话列表 -->
    <aside class="qa-sidebar">
      <div class="qa-sidebar-head">
        <el-button type="primary" class="btn-gradient" @click="newSession">+ 新对话</el-button>
      </div>
      <div class="qa-session-list">
        <div
          v-for="s in sessions" :key="s.id"
          class="session-item" :class="{ active: s.id === activeSession }"
          @click="activeSession = s.id"
        >
          <div class="session-title">{{ s.title }}</div>
          <div class="session-meta">{{ s.course }} · {{ s.time }}</div>
        </div>
      </div>
    </aside>

    <!-- 右侧聊天 -->
    <section class="qa-main">
      <div ref="msgBox" class="qa-messages">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="qa-empty">
          <div style="font-size:48px;margin-bottom:16px">🤖</div>
          <div style="font-size:16px;margin-bottom:8px;color:var(--text-primary)">你好！我是课程智能助手</div>
          <div style="font-size:13px">试试问我关于机器学习或数据挖掘的任何问题</div>
        </div>

        <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="m.role">
          <div class="msg-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
            {{ m.role === 'user' ? '我' : 'AI' }}
          </div>
          <div>
            <div class="msg-bubble" v-html="renderMd(m.content)" />
            <div v-if="m.references?.length" class="ref-list">
              <div v-for="(r, j) in m.references" :key="j" class="ref-item">
                📄 {{ r.source }}
                <span v-if="r.page"> (第{{ r.page }}页)</span>
                <el-tag size="small" type="info" style="margin-left:4px">{{ (r.score * 100).toFixed(0) }}%</el-tag>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="msg-row assistant">
          <div class="msg-avatar ai">AI</div>
          <div class="msg-bubble">
            <div class="typing-dots"><span /><span /><span /></div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="qa-input-bar">
        <el-input
          v-model="question"
          type="textarea" :rows="2"
          placeholder="输入你的问题，例如：什么是支持向量机？"
          @keydown.enter.exact.prevent="send"
        />
        <el-button class="btn-send" :loading="loading" @click="send">发送</el-button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import api from '@/api'

const msgBox = ref(null)
const sessions = ref([])
const activeSession = ref('')
const messages = ref([])
const question = ref('')
const loading = ref(false)

onMounted(async () => {
  const { data } = await api.get('/qa/sessions')
  sessions.value = data
  if (data.length) activeSession.value = data[0].id
})

function renderMd(text) {
  if (!text) return ''
  try { return marked.parse(text) } catch { return text }
}

function scrollBottom() {
  nextTick(() => { if (msgBox.value) msgBox.value.scrollTop = msgBox.value.scrollHeight })
}

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  scrollBottom()

  try {
    const { data: d } = await api.post('/qa/ask-sync', {
      question: q, session_id: activeSession.value, enable_rag: true, enable_graph: true,
    })
    messages.value.push({ role: 'assistant', content: d.answer, references: d.references || [] })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后重试。' })
  }
  loading.value = false
  scrollBottom()
}

function newSession() {
  const id = 'sess_' + Date.now()
  sessions.value.unshift({ id, title: '新对话', time: '刚刚', course: '机器学习' })
  activeSession.value = id
  messages.value = []
}
</script>

<style scoped>
.qa-layout {
  display: grid; grid-template-columns: 280px 1fr; gap: 16px;
  height: calc(100vh - 120px);
}

/* 左侧 */
.qa-sidebar {
  background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
  display: flex; flex-direction: column; overflow: hidden;
}
.qa-sidebar-head { padding: 14px; border-bottom: 1px solid var(--border); }
.btn-gradient { width: 100%; background: var(--gradient) !important; border: none !important; }
.qa-session-list { flex: 1; overflow-y: auto; padding: 8px; }
.session-item {
  padding: 12px; border-radius: 10px; cursor: pointer; margin-bottom: 4px; transition: all 0.2s;
}
.session-item:hover { background: var(--bg); }
.session-item.active { background: var(--primary-bg); }
.session-title {
  font-size: 14px; font-weight: 500; white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis;
}
.session-meta { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

/* 右侧 */
.qa-main {
  background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
  display: flex; flex-direction: column; overflow: hidden;
}
.qa-messages { flex: 1; overflow-y: auto; padding: 20px; }
.qa-empty { text-align: center; padding: 60px 0; color: var(--text-muted); }
.qa-input-bar {
  padding: 14px 20px; border-top: 1px solid var(--border);
  display: flex; gap: 12px; align-items: flex-end;
}
.qa-input-bar :deep(.el-textarea__inner) {
  border-radius: 12px; resize: none; box-shadow: none;
}
.btn-send {
  height: 40px; border-radius: 10px; background: var(--gradient) !important;
  border: none !important; color: #fff; font-weight: 600; flex-shrink: 0;
}

@media (max-width: 900px) {
  .qa-layout { grid-template-columns: 1fr; }
  .qa-sidebar { display: none; }
}
</style>
