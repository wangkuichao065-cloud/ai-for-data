<template>
  <div class="qa-layout">
    <!-- 左侧会话列表 -->
    <aside class="qa-sidebar">
      <div class="qa-sidebar-head">
        <button class="btn-new-session" @click="newSession">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span>新建对话</span>
        </button>
      </div>
      <div class="qa-session-list">
        <div
          v-for="s in sessions" :key="s.id"
          class="session-item" :class="{ active: s.id === activeSession }"
          @click="activeSession = s.id"
        >
          <div class="session-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div class="session-body">
            <div class="session-title">{{ s.title }}</div>
            <div class="session-meta">
              <span class="session-course-tag">{{ s.course }}</span>
              <span class="session-time">{{ s.time }}</span>
            </div>
          </div>
        </div>
        <div v-if="sessions.length === 0" class="session-empty">
          <span>暂无对话记录</span>
        </div>
      </div>
    </aside>

    <!-- 右侧聊天 -->
    <section class="qa-main">
      <div ref="msgBox" class="qa-messages">
        <!-- 空状态 -->
        <div v-if="messages.length === 0" class="qa-empty">
          <div class="empty-icon-wrap">
            <svg class="empty-icon" width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2a7 7 0 0 1 7 7c0 2.862-1.782 5.327-4.3 6.472A3.015 3.015 0 0 0 12.5 18h-1a3.015 3.015 0 0 0-2.2-2.528C6.782 14.327 5 11.862 5 9a7 7 0 0 1 7-7z"/>
              <path d="M10 22h4"/><path d="M12 18v4"/>
            </svg>
            <div class="empty-glow"></div>
          </div>
          <h3 class="empty-title">你好！我是课程智能助手</h3>
          <p class="empty-desc">我可以帮你解答关于机器学习、数据挖掘等课程的任何问题</p>
          <div class="empty-hints">
            <div class="hint-chip" @click="fillQuestion('什么是支持向量机？')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              什么是支持向量机？
            </div>
            <div class="hint-chip" @click="fillQuestion('解释一下K-Means聚类算法')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              解释一下K-Means聚类算法
            </div>
            <div class="hint-chip" @click="fillQuestion('决策树和随机森林有什么区别？')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              决策树和随机森林有什么区别？
            </div>
          </div>
        </div>

        <div v-for="(m, i) in messages" :key="i" class="msg-row" :class="[m.role, { 'msg-enter': m._animate }]">
          <div class="msg-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
            <template v-if="m.role === 'user'">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
            </template>
            <template v-else>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a7 7 0 0 1 7 7c0 2.862-1.782 5.327-4.3 6.472A3.015 3.015 0 0 0 12.5 18h-1a3.015 3.015 0 0 0-2.2-2.528C6.782 14.327 5 11.862 5 9a7 7 0 0 1 7-7z"/>
                <path d="M10 22h4"/><path d="M12 18v4"/>
              </svg>
            </template>
          </div>
          <div class="msg-content-wrap">
            <div class="msg-label">{{ m.role === 'user' ? '你' : '智能助手' }}</div>
            <div class="msg-bubble" v-html="renderMd(m.content)" />
            <div v-if="m.references?.length" class="ref-list">
              <div class="ref-heading">参考来源</div>
              <div v-for="(r, j) in m.references" :key="j" class="ref-card">
                <div class="ref-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>
                  </svg>
                </div>
                <div class="ref-info">
                  <span class="ref-source">{{ r.source }}</span>
                  <span v-if="r.page" class="ref-page">第{{ r.page }}页</span>
                </div>
                <span class="ref-score">{{ (r.score * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="msg-row assistant msg-enter">
          <div class="msg-avatar ai">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2a7 7 0 0 1 7 7c0 2.862-1.782 5.327-4.3 6.472A3.015 3.015 0 0 0 12.5 18h-1a3.015 3.015 0 0 0-2.2-2.528C6.782 14.327 5 11.862 5 9a7 7 0 0 1 7-7z"/>
              <path d="M10 22h4"/><path d="M12 18v4"/>
            </svg>
          </div>
          <div class="msg-content-wrap">
            <div class="msg-label">智能助手</div>
            <div class="msg-bubble typing-bubble">
              <div class="typing-dots"><span /><span /><span /></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="qa-input-bar">
        <div class="input-wrapper">
          <textarea
            ref="inputEl"
            v-model="question"
            class="qa-textarea"
            rows="1"
            placeholder="输入你的问题，例如：什么是支持向量机？"
            @keydown.enter.exact.prevent="send"
            @input="autoResize"
          />
          <button class="btn-send" :class="{ active: question.trim() && !loading }" :disabled="!question.trim() || loading" @click="send">
            <svg v-if="!loading" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
            <svg v-else class="spin" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
            </svg>
          </button>
        </div>
        <div class="input-hint">按 Enter 发送，Shift + Enter 换行</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { marked } from 'marked'
import api from '@/api'

const msgBox = ref(null)
const inputEl = ref(null)
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

function autoResize(e) {
  const el = e.target
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function fillQuestion(text) {
  question.value = text
  nextTick(() => inputEl.value?.focus())
}

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', content: q, _animate: true })
  question.value = ''
  if (inputEl.value) { inputEl.value.style.height = 'auto' }
  loading.value = true
  scrollBottom()

  try {
    const { data: d } = await api.post('/qa/ask-sync', {
      question: q, session_id: activeSession.value, enable_rag: true, enable_graph: true,
    })
    messages.value.push({ role: 'assistant', content: d.answer, references: d.references || [], _animate: true })
  } catch {
    messages.value.push({ role: 'assistant', content: '抱歉，服务暂时不可用，请稍后重试。', _animate: true })
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
/* ========== Layout ========== */
.qa-layout {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
}

/* ========== Sidebar ========== */
.qa-sidebar {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.qa-sidebar-head {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}

.btn-new-session {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 0;
  border: none;
  border-radius: var(--radius-sm);
  background: var(--gradient);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.25);
  letter-spacing: 0.3px;
}
.btn-new-session:hover {
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.38);
  transform: translateY(-1px);
  filter: brightness(1.06);
}
.btn-new-session:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(79, 110, 247, 0.2);
}

.qa-session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.session-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 12px;
  border-radius: 12px;
  cursor: pointer;
  margin-bottom: 4px;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}
.session-item::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  opacity: 0;
  background: var(--gradient-soft);
  transition: opacity 0.2s;
}
.session-item:hover::before {
  opacity: 0.5;
}
.session-item.active::before {
  opacity: 1;
}
.session-item > * {
  position: relative;
  z-index: 1;
}

.session-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--primary-bg);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}
.session-item.active .session-icon {
  background: var(--gradient);
  color: #fff;
  box-shadow: 0 3px 10px rgba(79, 110, 247, 0.3);
}

.session-body {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 6px;
}

.session-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.session-course-tag {
  font-size: 11px;
  font-weight: 500;
  color: var(--primary);
  background: var(--primary-bg);
  padding: 2px 8px;
  border-radius: 20px;
  letter-spacing: 0.2px;
}

.session-time {
  font-size: 11px;
  color: var(--text-muted);
}

.session-empty {
  text-align: center;
  padding: 40px 16px;
  color: var(--text-muted);
  font-size: 13px;
}

/* ========== Main Chat Area ========== */
.qa-main {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0, 0, 0, 0.03);
}

.qa-messages {
  flex: 1;
  overflow-y: auto;
  padding: 28px 32px;
  scroll-behavior: smooth;
}

/* ========== Empty State ========== */
.qa-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px 20px;
}

.empty-icon-wrap {
  position: relative;
  width: 96px;
  height: 96px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 28px;
}

.empty-icon {
  color: var(--primary);
  position: relative;
  z-index: 1;
}

.empty-glow {
  position: absolute;
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: var(--gradient-soft);
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { transform: scale(1); opacity: 0.6; }
  50% { transform: scale(1.12); opacity: 1; }
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  max-width: 380px;
  line-height: 1.6;
}

.empty-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 520px;
}

.hint-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 24px;
  background: var(--primary-bg);
  color: var(--primary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}
.hint-chip:hover {
  background: #fff;
  border-color: var(--primary-light);
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.12);
  transform: translateY(-2px);
}

/* ========== Messages ========== */
.msg-row {
  display: flex;
  gap: 14px;
  margin-bottom: 28px;
  max-width: 85%;
}

.msg-row.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

/* Avatar */
.msg-avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: transform 0.2s;
}
.msg-avatar:hover {
  transform: scale(1.05);
}
.msg-avatar.ai {
  background: var(--gradient);
  color: #fff;
  box-shadow: 0 4px 12px rgba(79, 110, 247, 0.25);
}
.msg-avatar.human {
  background: #f1f5f9;
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.msg-content-wrap {
  flex: 1;
  min-width: 0;
}

.msg-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 6px;
  letter-spacing: 0.2px;
}

.msg-row.user .msg-label {
  text-align: right;
}

.msg-row.user .msg-content-wrap {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

/* Bubbles */
.msg-bubble {
  padding: 16px 20px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.85;
  word-break: break-word;
}

.msg-row.assistant .msg-bubble {
  background: #f8f9fc;
  color: var(--text-primary);
  border: 1px solid var(--border);
  border-top-left-radius: 4px;
}

.msg-row.user .msg-bubble {
  background: var(--gradient);
  color: #fff;
  border-top-right-radius: 4px;
  box-shadow: 0 4px 16px rgba(79, 110, 247, 0.22);
}

/* Message enter animation */
.msg-enter {
  animation: msg-slide-in 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes msg-slide-in {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Markdown styles inside bubble */
.msg-bubble :deep(p) { margin-bottom: 8px; }
.msg-bubble :deep(p:last-child) { margin-bottom: 0; }
.msg-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.06);
  padding: 2px 7px;
  border-radius: 5px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
}
.msg-row.user .msg-bubble :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}
.msg-bubble :deep(pre) {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px 20px;
  border-radius: 14px;
  overflow-x: auto;
  margin: 12px 0;
  font-size: 13px;
  line-height: 1.6;
}
.msg-bubble :deep(pre code) { background: transparent; color: inherit; padding: 0; }
.msg-bubble :deep(table) { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
.msg-bubble :deep(th), .msg-bubble :deep(td) {
  border: 1px solid var(--border); padding: 10px 14px; text-align: left;
}
.msg-bubble :deep(th) { background: #f1f5f9; font-weight: 600; }
.msg-bubble :deep(h2) { font-size: 16px; margin-bottom: 10px; font-weight: 700; }
.msg-bubble :deep(h3) { font-size: 14px; margin: 14px 0 6px; font-weight: 600; }
.msg-bubble :deep(ul), .msg-bubble :deep(ol) { padding-left: 20px; margin: 8px 0; }
.msg-bubble :deep(li) { margin-bottom: 4px; }
.msg-bubble :deep(blockquote) {
  border-left: 3px solid var(--primary-light);
  padding-left: 14px;
  margin: 10px 0;
  color: var(--text-secondary);
}
.msg-bubble :deep(a) {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* ========== Typing indicator ========== */
.typing-bubble {
  padding: 14px 20px !important;
}

.typing-dots {
  display: flex;
  gap: 5px;
  padding: 4px 0;
}
.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary-light);
  animation: bounce 1.4s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.35; }
  30% { transform: translateY(-10px); opacity: 1; }
}

/* ========== References ========== */
.ref-list {
  margin-top: 14px;
  padding-top: 14px;
}

.ref-heading {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.ref-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 10px;
  background: #f8f9fc;
  border: 1px solid var(--border);
  margin-bottom: 6px;
  cursor: pointer;
  transition: all 0.2s;
}
.ref-card:hover {
  background: var(--primary-bg);
  border-color: var(--primary-light);
  box-shadow: 0 2px 8px rgba(79, 110, 247, 0.08);
  transform: translateX(3px);
}

.ref-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--primary-bg);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ref-info {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ref-source {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ref-page {
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
}

.ref-score {
  font-size: 12px;
  font-weight: 700;
  color: var(--primary);
  background: var(--primary-bg);
  padding: 3px 10px;
  border-radius: 20px;
  flex-shrink: 0;
}

/* ========== Input Bar ========== */
.qa-input-bar {
  padding: 16px 28px 20px;
  border-top: 1px solid var(--border);
  background: var(--bg-card);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: #f8f9fc;
  border: 2px solid var(--border);
  border-radius: 20px;
  padding: 8px 8px 8px 20px;
  transition: border-color 0.25s, box-shadow 0.25s;
}
.input-wrapper:focus-within {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 4px rgba(79, 110, 247, 0.08);
  background: #fff;
}

.qa-textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  font-family: inherit;
  color: var(--text-primary);
  resize: none;
  line-height: 1.6;
  padding: 6px 0;
  min-height: 24px;
  max-height: 120px;
}
.qa-textarea::placeholder {
  color: var(--text-muted);
}

.btn-send {
  width: 42px;
  height: 42px;
  border: none;
  border-radius: 14px;
  background: #e2e8f0;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: not-allowed;
  flex-shrink: 0;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.btn-send.active {
  background: var(--gradient);
  color: #fff;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(79, 110, 247, 0.3);
}
.btn-send.active:hover {
  box-shadow: 0 6px 20px rgba(79, 110, 247, 0.4);
  transform: scale(1.05);
}
.btn-send.active:active {
  transform: scale(0.96);
}

.spin {
  animation: spin-anim 0.8s linear infinite;
}
@keyframes spin-anim {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.input-hint {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
  letter-spacing: 0.2px;
}

/* ========== Responsive ========== */
@media (max-width: 900px) {
  .qa-layout {
    grid-template-columns: 1fr;
  }
  .qa-sidebar {
    display: none;
  }
  .qa-messages {
    padding: 20px 16px;
  }
  .qa-input-bar {
    padding: 12px 16px 16px;
  }
  .msg-row {
    max-width: 95%;
  }
}

/* ========== Scrollbar ========== */
.qa-session-list::-webkit-scrollbar,
.qa-messages::-webkit-scrollbar {
  width: 5px;
}
.qa-session-list::-webkit-scrollbar-track,
.qa-messages::-webkit-scrollbar-track {
  background: transparent;
}
.qa-session-list::-webkit-scrollbar-thumb,
.qa-messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}
.qa-session-list::-webkit-scrollbar-thumb:hover,
.qa-messages::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
