<template>
  <div class="teacher-layout">
    <!-- 左侧：数字人形象区 -->
    <aside class="avatar-panel">
      <!-- 背景 -->
      <div class="avatar-bg" />

      <!-- 数字人形象 -->
      <div class="avatar-stage" :class="{ speaking: isSpeaking }">
        <div class="avatar-frame">
          <img src="@/assets/fairy-teacher.jpg" alt="数字教师" class="avatar-img" />
          <!-- 语音波纹 -->
          <div v-if="isSpeaking" class="voice-ripple">
            <span /><span /><span />
          </div>
          <!-- 底部呼吸光晕 -->
          <div class="avatar-glow" />
        </div>

        <!-- 说话状态指示器 -->
        <div class="speaking-indicator" v-if="isSpeaking">
          <div class="wave-bars">
            <span v-for="n in 7" :key="n" :style="{ animationDelay: (n * 0.12) + 's' }" />
          </div>
          <span class="speaking-text">正在说话...</span>
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

      <!-- 控制面板 -->
      <div class="control-bar">
        <!-- 语音开关 -->
        <button
          class="ctrl-btn"
          :class="{ active: voiceEnabled }"
          @click="toggleVoice"
          :title="voiceEnabled ? '语音已开启' : '语音已关闭'"
        >
          <svg v-if="voiceEnabled" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <line x1="23" y1="9" x2="17" y2="15" />
            <line x1="17" y1="9" x2="23" y2="15" />
          </svg>
          <span>{{ voiceEnabled ? '语音开' : '语音关' }}</span>
        </button>

        <!-- 情绪切换 -->
        <button
          v-for="e in info.emotions" :key="e"
          class="ctrl-btn emotion-ctrl"
          :class="{ active: curEmotion === e }"
          @click="curEmotion = e"
          :title="emotionMap[e]"
        >
          <span>{{ emotionIcons[e] }}</span>
        </button>
      </div>

      <!-- 学习进度 -->
      <div class="progress-card">
        <div class="stat-row">
          <div class="stat-item">
            <div class="stat-value">{{ info.progress.total_questions }}</div>
            <div class="stat-label">提问</div>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <div class="stat-value">{{ info.progress.study_hours }}<span class="stat-unit">h</span></div>
            <div class="stat-label">学时</div>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <div class="stat-value">{{ info.progress.level }}</div>
            <div class="stat-label">等级</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧：对话区 -->
    <section class="chat-card">
      <div class="chat-head">
        <div class="chat-head-left">
          <div class="chat-head-avatar">
            <img src="@/assets/fairy-teacher.jpg" alt="" class="mini-avatar" />
          </div>
          <div>
            <div class="chat-head-name">与{{ info.name }}对话</div>
            <div class="chat-head-sub">{{ isSpeaking ? '🔊 语音播报中' : '💬 智能辅导 · 随时提问' }}</div>
          </div>
        </div>
        <div class="chat-head-badge">
          <span class="badge-dot" />
          AI 辅导中
        </div>
      </div>

      <div ref="chatBox" class="chat-body">
        <div v-if="chatMsgs.length === 0" class="chat-empty">
          <div class="empty-icon">🌸</div>
          <div class="empty-title">你好，我是{{ info.name }}</div>
          <div class="empty-hint">点击下面的快捷问题，或直接输入你的问题</div>
          <div class="quick-questions">
            <button
              v-for="(q, i) in quickQuestions" :key="i"
              class="quick-btn"
              @click="askQuick(q)"
            >{{ q }}</button>
          </div>
        </div>

        <div v-for="(m, i) in chatMsgs" :key="i" class="msg-row" :class="m.role">
          <div class="msg-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
            <template v-if="m.role === 'ai'">
              <img src="@/assets/fairy-teacher.jpg" alt="" class="avatar-tiny" />
            </template>
            <template v-else>我</template>
          </div>
          <div class="msg-content">
            <div class="msg-bubble" v-html="renderMd(m.content)" />
            <!-- AI 消息的操作按钮 -->
            <div v-if="m.role === 'assistant' && voiceEnabled" class="msg-actions">
              <button
                class="action-btn"
                @click="speakText(m.content)"
                title="朗读此消息"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                朗读
              </button>
              <button
                v-if="isSpeaking"
                class="action-btn stop"
                @click="stopSpeaking"
                title="停止朗读"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                停止
              </button>
            </div>
          </div>
        </div>

        <div v-if="chatLoading" class="msg-row assistant">
          <div class="msg-avatar ai">
            <img src="@/assets/fairy-teacher.jpg" alt="" class="avatar-tiny" />
          </div>
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
            placeholder="向老师提问..."
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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { marked } from 'marked'
import api from '@/api'

const chatBox = ref(null)
const info = ref({
  name: '花仙老师', status: 'online', emotions: ['normal', 'happy', 'thinking', 'encouraging'],
  progress: { total_questions: 0, mastered_topics: [], weak_topics: [], study_hours: 0, level: '' },
})
const curEmotion = ref('normal')
const emotionMap = { normal: '平静', happy: '开心', thinking: '思考', encouraging: '鼓励' }
const emotionIcons = { normal: '😌', happy: '😊', thinking: '🤔', encouraging: '💪' }
const chatMsgs = ref([])
const chatInput = ref('')
const chatLoading = ref(false)

// 语音相关
const voiceEnabled = ref(true)
const isSpeaking = ref(false)
let currentUtterance = null

const quickQuestions = [
  '什么是支持向量机？',
  '解释一下 Transformer',
  'K-Means 算法原理',
  '过拟合怎么解决？',
]

onMounted(async () => {
  const { data } = await api.get('/teacher/avatar')
  info.value = data
  info.value.name = '花仙老师'
  info.value.emotions = ['normal', 'happy', 'thinking', 'encouraging']
})

onUnmounted(() => {
  stopSpeaking()
})

function renderMd(t) { if (!t) return ''; try { return marked.parse(t) } catch { return t } }

function scrollBottom() {
  nextTick(() => { if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight })
}

/* ========== 语音合成 ========== */
function getChineseVoice() {
  const voices = window.speechSynthesis?.getVoices() || []
  // 优先选中文女声
  return voices.find(v => v.lang.includes('zh') && v.name.includes('Female'))
    || voices.find(v => v.lang.includes('zh-CN'))
    || voices.find(v => v.lang.includes('zh'))
    || voices.find(v => v.lang.includes('cmn'))
    || null
}

function speakText(text) {
  if (!window.speechSynthesis || !voiceEnabled.value) return
  stopSpeaking()

  // 清除 Markdown 标记，提取纯文本
  const plainText = text
    .replace(/#{1,6}\s/g, '')
    .replace(/\*{1,2}(.*?)\*{1,2}/g, '$1')
    .replace(/`(.*?)`/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\|.*?\|/g, '')
    .replace(/[-*]\s/g, '')
    .replace(/\n{2,}/g, '。')
    .replace(/\n/g, '，')
    .trim()

  if (!plainText) return

  const utterance = new SpeechSynthesisUtterance(plainText)
  const voice = getChineseVoice()
  if (voice) utterance.voice = voice
  utterance.lang = 'zh-CN'
  utterance.rate = 0.95
  utterance.pitch = 1.1
  utterance.volume = 1

  utterance.onstart = () => { isSpeaking.value = true }
  utterance.onend = () => { isSpeaking.value = false }
  utterance.onerror = () => { isSpeaking.value = false }

  currentUtterance = utterance
  window.speechSynthesis.speak(utterance)
}

function stopSpeaking() {
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel()
  }
  isSpeaking.value = false
  currentUtterance = null
}

function toggleVoice() {
  voiceEnabled.value = !voiceEnabled.value
  if (!voiceEnabled.value) stopSpeaking()
}

/* ========== 聊天逻辑 ========== */
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
    // 自动朗读
    if (voiceEnabled.value) {
      nextTick(() => speakText(data.answer))
    }
  } catch {
    chatMsgs.value.push({ role: 'assistant', content: '老师暂时不在线，请稍后再试。' })
  }
  chatLoading.value = false
  scrollBottom()
}

function askQuick(q) {
  chatInput.value = q
  sendChat()
}
</script>

<style scoped>
/* ===== 布局 ===== */
.teacher-layout {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
}

/* ===== 数字人形象面板 ===== */
.avatar-panel {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 20px 20px;
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.03);
}

.avatar-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 0%, rgba(244,114,182,0.12) 0%, transparent 60%),
    radial-gradient(ellipse at 30% 80%, rgba(139,92,246,0.08) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 60%, rgba(59,130,246,0.06) 0%, transparent 50%);
  pointer-events: none;
}

/* 数字人舞台 */
.avatar-stage {
  position: relative;
  margin-top: 24px;
  margin-bottom: 16px;
  z-index: 1;
}

.avatar-frame {
  width: 260px;
  height: 260px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  box-shadow:
    0 0 0 4px rgba(244,114,182,0.2),
    0 0 0 8px rgba(139,92,246,0.1),
    0 20px 60px rgba(0,0,0,0.12);
  transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.4,0,0.2,1);
  animation: idle-breathe 4s ease-in-out infinite;
}

/* 空闲呼吸动画 */
@keyframes idle-breathe {
  0%, 100% { transform: scale(1) translateY(0); }
  50% { transform: scale(1.02) translateY(-3px); }
}

/* 说话时增强动画 */
.avatar-stage.speaking .avatar-frame {
  box-shadow:
    0 0 0 4px rgba(244,114,182,0.35),
    0 0 0 10px rgba(139,92,246,0.15),
    0 0 40px rgba(244,114,182,0.2),
    0 20px 60px rgba(0,0,0,0.12);
  animation: speaking-move 2.5s ease-in-out infinite;
}

.avatar-stage.speaking .avatar-img {
  animation: speaking-face 1.8s ease-in-out infinite;
}

@keyframes speaking-move {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.03) rotate(-1.5deg); }
  50% { transform: scale(1.05) rotate(0deg); }
  75% { transform: scale(1.03) rotate(1.5deg); }
}

@keyframes speaking-face {
  0%, 100% { transform: scale(1) translateY(0); }
  30% { transform: scale(1.01) translateY(-2px); }
  60% { transform: scale(1.03) translateY(-4px); }
}

/* 语音波纹 */
.voice-ripple {
  position: absolute;
  inset: -20px;
  border-radius: 50%;
  pointer-events: none;
}
.voice-ripple span {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(244,114,182,0.3);
  animation: ripple-out 2s ease-out infinite;
}
.voice-ripple span:nth-child(2) { animation-delay: 0.5s; }
.voice-ripple span:nth-child(3) { animation-delay: 1s; }

@keyframes ripple-out {
  0% { transform: scale(0.9); opacity: 0.8; }
  100% { transform: scale(1.3); opacity: 0; }
}

/* 底部光晕 */
.avatar-glow {
  position: absolute;
  bottom: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 40px;
  background: radial-gradient(ellipse, rgba(139,92,246,0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: translateX(-50%) scaleX(1); }
  50% { opacity: 1; transform: translateX(-50%) scaleX(1.15); }
}

/* 说话指示器 */
.speaking-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 14px;
  padding: 8px 20px;
  background: linear-gradient(135deg, rgba(244,114,182,0.1), rgba(139,92,246,0.1));
  border-radius: 20px;
  border: 1px solid rgba(244,114,182,0.2);
}

.wave-bars {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 20px;
}
.wave-bars span {
  width: 3px;
  height: 6px;
  background: linear-gradient(to top, #f472b6, #8b5cf6);
  border-radius: 2px;
  animation: wave-bar 0.8s ease-in-out infinite alternate;
}
.wave-bars span:nth-child(odd) { animation-direction: alternate-reverse; }

@keyframes wave-bar {
  0% { height: 4px; }
  100% { height: 18px; }
}

.speaking-text {
  font-size: 13px;
  font-weight: 600;
  background: linear-gradient(135deg, #ec4899, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 教师信息 */
.teacher-info {
  text-align: center;
  position: relative;
  z-index: 1;
}
.teacher-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.teacher-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 6px;
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #94a3b8; flex-shrink: 0;
}
.status-dot.online {
  background: #22c55e;
  animation: status-pulse 2s ease-in-out infinite;
}
@keyframes status-pulse {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
  50% { box-shadow: 0 0 0 6px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}
.status-text { font-size: 13px; color: var(--text-secondary); }

/* 控制栏 */
.control-bar {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  position: relative;
  z-index: 1;
}
.ctrl-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: var(--bg-card);
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  transition: all 0.25s;
}
.ctrl-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary);
  background: var(--primary-bg);
  transform: translateY(-1px);
}
.ctrl-btn.active {
  background: var(--gradient);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 4px 14px rgba(79,110,247,0.25);
}
.emotion-ctrl {
  padding: 8px 12px;
  font-size: 18px;
}

/* 进度卡 */
.progress-card {
  width: 100%;
  margin-top: 18px;
  padding: 16px;
  background: var(--bg);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border);
  position: relative;
  z-index: 1;
}
.stat-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.stat-item { flex: 1; text-align: center; }
.stat-value {
  font-size: 22px; font-weight: 800; color: var(--primary);
}
.stat-unit { font-size: 13px; font-weight: 600; }
.stat-label { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.stat-divider { width: 1px; height: 28px; background: var(--border); }

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

.chat-head {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(to bottom, #fafbff, var(--bg-card));
}
.chat-head-left { display: flex; align-items: center; gap: 12px; }
.chat-head-avatar {
  width: 42px; height: 42px; border-radius: 50%; overflow: hidden;
  box-shadow: 0 4px 12px rgba(79,110,247,0.2);
  border: 2px solid rgba(244,114,182,0.3);
}
.mini-avatar { width: 100%; height: 100%; object-fit: cover; }
.chat-head-name { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.chat-head-sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.chat-head-badge {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; background: var(--primary-bg);
  border-radius: 20px; font-size: 12px; font-weight: 500; color: var(--primary);
}
.badge-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--primary);
  animation: badge-blink 2s infinite;
}
@keyframes badge-blink { 0%,100%{opacity:1} 50%{opacity:0.4} }

/* 对话主体 */
.chat-body { flex: 1; overflow-y: auto; padding: 24px; }

.chat-empty { text-align: center; padding: 50px 20px; }
.empty-icon { font-size: 56px; margin-bottom: 12px; }
.empty-title { font-size: 17px; font-weight: 600; color: var(--text-primary); margin-bottom: 8px; }
.empty-hint { font-size: 13px; color: var(--text-muted); margin-bottom: 20px; }

/* 快捷问题 */
.quick-questions {
  display: flex; flex-wrap: wrap; gap: 8px;
  justify-content: center; max-width: 400px; margin: 0 auto;
}
.quick-btn {
  padding: 8px 16px; border-radius: 20px;
  border: 1.5px solid var(--border); background: var(--bg-card);
  cursor: pointer; font-size: 13px; color: var(--text-secondary);
  transition: all 0.2s; font-weight: 500;
}
.quick-btn:hover {
  border-color: var(--primary); color: var(--primary);
  background: var(--primary-bg); transform: translateY(-1px);
}

/* 消息 */
.msg-content { flex: 1; min-width: 0; }

/* 消息头像 */
.avatar-tiny {
  width: 100%; height: 100%; object-fit: cover; border-radius: 50%;
}

/* 消息操作按钮 */
.msg-actions {
  display: flex; gap: 8px; margin-top: 8px;
}
.action-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 4px 10px; border-radius: 12px;
  border: 1px solid var(--border); background: var(--bg-card);
  cursor: pointer; font-size: 12px; color: var(--text-muted);
  transition: all 0.2s;
}
.action-btn:hover {
  border-color: var(--primary); color: var(--primary);
  background: var(--primary-bg);
}
.action-btn.stop {
  border-color: var(--accent-red); color: var(--accent-red);
}
.action-btn.stop:hover {
  background: #fef2f2;
}

/* 输入区 */
.chat-input-bar {
  padding: 16px 20px;
  border-top: 1px solid var(--border);
  display: flex; gap: 12px; align-items: center;
  background: linear-gradient(to top, #fafbff, var(--bg-card));
}
.input-wrapper { flex: 1; }
.input-wrapper :deep(.el-input__wrapper) {
  border-radius: 24px; padding: 4px 18px;
  box-shadow: 0 0 0 1px var(--border) inset;
  transition: all 0.25s;
}
.input-wrapper :deep(.el-input__wrapper:focus-within),
.input-wrapper :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--primary-light) inset;
}
.btn-send {
  height: 44px; padding: 0 24px; border-radius: 22px;
  background: var(--gradient) !important; border: none !important;
  color: #fff; font-weight: 600; font-size: 14px; flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(79,110,247,0.3);
  transition: all 0.25s;
}
.btn-send:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(79,110,247,0.4);
}

/* ===== 响应式 ===== */
@media (max-width: 1100px) {
  .teacher-layout { grid-template-columns: 1fr; height: auto; }
  .avatar-panel { max-height: none; }
  .chat-card { height: 500px; }
}
@media (max-width: 600px) {
  .avatar-frame { width: 180px; height: 180px; }
  .quick-questions { flex-direction: column; }
  .chat-head-badge { display: none; }
}
</style>
