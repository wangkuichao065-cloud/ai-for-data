<template>
  <div class="teacher-layout">
    <!-- 左侧：Live2D 数字人面板 -->
    <aside class="live2d-panel">
      <!-- Live2D Canvas -->
      <div class="live2d-stage" ref="stageEl">
        <canvas ref="liveCanvas" class="live2d-canvas" />
        <!-- 加载状态 -->
        <div v-if="modelLoading" class="loading-overlay">
          <div class="loading-spinner" />
          <span>加载模型中...</span>
        </div>
        <!-- 加载失败 -->
        <div v-if="modelError" class="loading-overlay error">
          <span class="error-icon">⚠️</span>
          <span>模型加载失败</span>
          <button class="retry-btn" @click="loadModel">重试</button>
        </div>
        <!-- 对话气泡 -->
        <transition name="bubble">
          <div v-if="bubbleText" class="speech-bubble">
            <div class="bubble-content">{{ bubbleText }}</div>
            <div class="bubble-arrow" />
          </div>
        </transition>
      </div>

      <!-- 教师信息 -->
      <div class="teacher-info">
        <h2 class="teacher-name">{{ info.name }}</h2>
        <div class="teacher-status">
          <span class="status-dot" :class="{ online: info.status === 'online' }" />
          <span class="status-text">{{ info.status === 'online' ? '在线' : '离线' }}</span>
          <span v-if="isSpeaking" class="speaking-tag">🔊 说话中</span>
        </div>
      </div>

      <!-- 控制面板 -->
      <div class="control-bar">
        <button class="ctrl-btn" :class="{ active: voiceEnabled }" @click="toggleVoice">
          <svg v-if="voiceEnabled" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
            <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
            <line x1="23" y1="9" x2="17" y2="15" /><line x1="17" y1="9" x2="23" y2="15" />
          </svg>
          <span>{{ voiceEnabled ? '语音开' : '语音关' }}</span>
        </button>
        <button class="ctrl-btn" @click="triggerMotion" title="触发动作">
          <span>🎭</span><span>动作</span>
        </button>
        <button class="ctrl-btn" @click="switchModel" title="切换形象">
          <span>👗</span><span>换装</span>
        </button>
        <button v-if="isSpeaking" class="ctrl-btn stop-btn" @click="stopSpeaking">
          <span>⏹</span><span>停止</span>
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
          <div class="chat-head-avatar">🎓</div>
          <div>
            <div class="chat-head-name">与{{ info.name }}对话</div>
            <div class="chat-head-sub">{{ isSpeaking ? '🔊 语音播报中...' : '💬 智能辅导 · 随时提问' }}</div>
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
          <div class="empty-hint">点击快捷问题，或直接输入你的问题</div>
          <div class="quick-questions">
            <button v-for="(q, i) in quickQuestions" :key="i" class="quick-btn" @click="askQuick(q)">{{ q }}</button>
          </div>
        </div>

        <div v-for="(m, i) in chatMsgs" :key="i" class="msg-row" :class="m.role">
          <div class="msg-avatar" :class="m.role === 'user' ? 'human' : 'ai'">
            {{ m.role === 'user' ? '我' : '师' }}
          </div>
          <div class="msg-content">
            <div class="msg-bubble" v-html="renderMd(m.content)" />
            <div v-if="m.role === 'assistant' && voiceEnabled" class="msg-actions">
              <button class="action-btn" @click="speakText(m.content)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                朗读
              </button>
            </div>
          </div>
        </div>

        <div v-if="chatLoading" class="msg-row assistant">
          <div class="msg-avatar ai">师</div>
          <div class="msg-content">
            <div class="msg-bubble">
              <div class="typing-dots"><span /><span /><span /></div>
            </div>
          </div>
        </div>
      </div>

      <div class="chat-input-bar">
        <div class="input-wrapper">
          <el-input v-model="chatInput" placeholder="向老师提问..." @keydown.enter="sendChat" />
        </div>
        <el-button class="btn-send" :loading="chatLoading" @click="sendChat">发送</el-button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { marked } from 'marked'
import * as PIXI from 'pixi.js'
import { Live2DModel } from 'pixi-live2d-display/cubism2'
import api from '@/api'

/* ========== Live2D ========== */
const stageEl = ref(null)
const liveCanvas = ref(null)
const modelLoading = ref(true)
const modelError = ref(false)
let pixiApp = null
let live2dModel = null
let lipSyncTimer = null

const modelList = [
  {
    name: 'Shizuku',
    url: '/models/shizuku/shizuku.model.json',
  },
]
let currentModelIndex = 0

/* ========== 数据 ========== */
const info = ref({
  name: '花仙老师', status: 'online', emotions: [],
  progress: { total_questions: 0, mastered_topics: [], weak_topics: [], study_hours: 0, level: '' },
})
const chatMsgs = ref([])
const chatInput = ref('')
const chatLoading = ref(false)
const chatBox = ref(null)
const voiceEnabled = ref(true)
const isSpeaking = ref(false)
const bubbleText = ref('')
let bubbleTimer = null

const quickQuestions = [
  '什么是支持向量机？',
  '解释一下 Transformer',
  'K-Means 算法原理',
  '过拟合怎么解决？',
]

/* ========== 挂载 Live2D ========== */
async function loadModel() {
  modelLoading.value = true
  modelError.value = false

  try {
    window.PIXI = PIXI

    if (!pixiApp) {
      const container = stageEl.value
      const w = container.clientWidth || 380
      const h = container.clientHeight || 420

      pixiApp = new PIXI.Application({
        view: liveCanvas.value,
        width: w,
        height: h,
        backgroundAlpha: 0,
        autoStart: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true,
      })
    } else {
      pixiApp.stage.removeChildren()
    }

    const modelDef = modelList[currentModelIndex]

    live2dModel = await Live2DModel.from(modelDef.url, {
      autoInteract: true,
    })

    // 计算缩放
    const canvasW = pixiApp.screen.width
    const canvasH = pixiApp.screen.height
    const modelW = live2dModel.width
    const modelH = live2dModel.height
    const scale = Math.min(canvasW / modelW, canvasH / modelH) * 0.85
    live2dModel.scale.set(scale)

    // 居中
    live2dModel.x = (canvasW - live2dModel.width * scale) / 2
    live2dModel.y = canvasH - live2dModel.height * scale + 10

    pixiApp.stage.addChild(live2dModel)

    // 鼠标追踪（眼睛跟随）
    stageEl.value.addEventListener('pointermove', (e) => {
      if (!live2dModel) return
      const rect = stageEl.value.getBoundingClientRect()
      live2dModel.focus(e.clientX - rect.left, e.clientY - rect.top)
    })

    // 点击交互
    stageEl.value.addEventListener('pointerdown', (e) => {
      if (!live2dModel) return
      const rect = stageEl.value.getBoundingClientRect()
      live2dModel.tap(e.clientX - rect.left, e.clientY - rect.top)
    })

    // hit 事件
    live2dModel.on('hit', (hitAreas) => {
      if (hitAreas.includes('body') || hitAreas.includes('Body')) {
        triggerMotion()
        showBubble('你好呀！有什么想问我的吗？')
      }
      if (hitAreas.includes('head') || hitAreas.includes('Head')) {
        showBubble('嘻嘻，别摸头啦~ 快问我学习问题吧！')
      }
    })

    // 初始动作
    try {
      live2dModel.internalModel?.motionManager?.startRandomMotion('idle')
    } catch (e) { /* ignore */ }

    modelLoading.value = false
    showBubble('你好！我是花仙老师，有什么想学的吗？')
  } catch (err) {
    console.error('Live2D model load error:', err)
    modelLoading.value = false
    modelError.value = true
  }
}

/* ========== 交互功能 ========== */
function triggerMotion() {
  if (!live2dModel) return
  try {
    const mm = live2dModel.internalModel?.motionManager
    if (mm) {
      const groups = Object.keys(mm.definitions || {})
      if (groups.length > 0) {
        const group = groups[Math.floor(Math.random() * groups.length)]
        mm.startRandomMotion(group)
      }
    }
  } catch (e) { /* ignore */ }
}

function switchModel() {
  currentModelIndex = (currentModelIndex + 1) % modelList.length
  showBubble('正在换装...')
  loadModel()
}

function showBubble(text, duration = 4000) {
  bubbleText.value = text
  clearTimeout(bubbleTimer)
  bubbleTimer = setTimeout(() => { bubbleText.value = '' }, duration)
}

/* ========== 语音合成 + 口型同步 ========== */
function getChineseVoice() {
  const voices = window.speechSynthesis?.getVoices() || []
  return voices.find(v => v.lang.includes('zh') && v.name.includes('Female'))
    || voices.find(v => v.lang.includes('zh-CN'))
    || voices.find(v => v.lang.includes('zh'))
    || voices.find(v => v.lang.includes('cmn'))
    || null
}

function speakText(text) {
  if (!window.speechSynthesis || !voiceEnabled.value) return
  stopSpeaking()

  const plainText = text
    .replace(/#{1,6}\s/g, '').replace(/\*{1,2}(.*?)\*{1,2}/g, '$1')
    .replace(/`(.*?)`/g, '$1').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\|.*?\|/g, '').replace(/[-*]\s/g, '')
    .replace(/\n{2,}/g, '。').replace(/\n/g, '，').trim()
  if (!plainText) return

  const utterance = new SpeechSynthesisUtterance(plainText)
  const voice = getChineseVoice()
  if (voice) utterance.voice = voice
  utterance.lang = 'zh-CN'
  utterance.rate = 0.95
  utterance.pitch = 1.1
  utterance.volume = 1

  utterance.onstart = () => { isSpeaking.value = true; startLipSync() }
  utterance.onend = () => { isSpeaking.value = false; stopLipSync() }
  utterance.onerror = () => { isSpeaking.value = false; stopLipSync() }

  window.speechSynthesis.speak(utterance)
}

function stopSpeaking() {
  window.speechSynthesis?.cancel()
  isSpeaking.value = false
  stopLipSync()
}

function startLipSync() {
  stopLipSync()
  lipSyncTimer = setInterval(() => {
    if (!live2dModel?.internalModel?.coreModel) return
    try {
      const core = live2dModel.internalModel.coreModel
      const p = core.model?.parameters?.getParameterById?.('ParamMouthOpenY')
        || core.model?.parameters?.getParameterById?.('PARAM_MOUTH_OPEN_Y')
      if (p) p.setValue(Math.random() * 0.8 + 0.2)
    } catch (e) { /* ignore */ }
  }, 100)
}

function stopLipSync() {
  if (lipSyncTimer) { clearInterval(lipSyncTimer); lipSyncTimer = null }
  if (live2dModel?.internalModel?.coreModel) {
    try {
      const core = live2dModel.internalModel.coreModel
      const p = core.model?.parameters?.getParameterById?.('ParamMouthOpenY')
        || core.model?.parameters?.getParameterById?.('PARAM_MOUTH_OPEN_Y')
      if (p) p.setValue(0)
    } catch (e) { /* ignore */ }
  }
}

function toggleVoice() {
  voiceEnabled.value = !voiceEnabled.value
  if (!voiceEnabled.value) { stopSpeaking(); showBubble('语音已关闭') }
  else { showBubble('语音已开启') }
}

/* ========== 聊天逻辑 ========== */
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

  triggerMotion()
  showBubble('让我想想...')

  try {
    const { data } = await api.post('/teacher/chat', { question: q })
    chatMsgs.value.push({ role: 'assistant', content: data.answer })
    const short = data.answer.replace(/[#*`\[\]|]/g, '').substring(0, 50) + '...'
    showBubble(short, 6000)

    if (voiceEnabled.value) { nextTick(() => speakText(data.answer)) }
    try { live2dModel?.internalModel?.motionManager?.startRandomMotion('tap_body') } catch (e) { /* ignore */ }
  } catch {
    chatMsgs.value.push({ role: 'assistant', content: '老师暂时不在线，请稍后再试。' })
    showBubble('抱歉，我现在有点忙，请稍后再试~')
  }
  chatLoading.value = false
  scrollBottom()
}

function askQuick(q) { chatInput.value = q; sendChat() }

/* ========== 生命周期 ========== */
onMounted(async () => {
  const { data } = await api.get('/teacher/avatar')
  info.value = data
  info.value.name = '花仙老师'
  info.value.emotions = ['normal', 'happy', 'thinking', 'encouraging']

  nextTick(() => { setTimeout(loadModel, 200) })

  window.speechSynthesis?.getVoices()
  if (window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices()
  }
})

onUnmounted(() => {
  stopSpeaking()
  clearTimeout(bubbleTimer)
  live2dModel?.destroy()
  pixiApp?.destroy(true)
  live2dModel = null
  pixiApp = null
})
</script>

<style scoped>
/* ===== 布局 ===== */
.teacher-layout {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 20px;
  height: calc(100vh - 120px);
}

/* ===== Live2D 面板 ===== */
.live2d-panel {
  background: var(--bg-card);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.03);
}

.live2d-stage {
  position: relative;
  height: 380px;
  background: linear-gradient(180deg, #f0e6ff 0%, #e8f0ff 50%, #f5f0ff 100%);
  overflow: hidden;
  cursor: pointer;
}

.live2d-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* 加载状态 */
.loading-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 14px;
  background: linear-gradient(180deg, #f0e6ff 0%, #e8f0ff 50%, #f5f0ff 100%);
  color: var(--text-secondary); font-size: 14px; font-weight: 500;
  z-index: 10;
}
.loading-overlay.error { color: var(--accent-orange); }
.error-icon { font-size: 32px; }
.loading-spinner {
  width: 36px; height: 36px;
  border: 3px solid var(--border); border-top-color: var(--primary);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.retry-btn {
  margin-top: 6px; padding: 6px 20px; border-radius: 16px;
  border: 1.5px solid var(--primary); background: transparent;
  color: var(--primary); font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.retry-btn:hover { background: var(--primary); color: #fff; }

/* 对话气泡 */
.speech-bubble {
  position: absolute; top: 16px; left: 50%;
  transform: translateX(-50%); max-width: 280px; z-index: 5;
  pointer-events: none;
}
.bubble-content {
  background: rgba(255,255,255,0.95); backdrop-filter: blur(10px);
  padding: 10px 16px; border-radius: 16px;
  font-size: 13px; line-height: 1.6; color: var(--text-primary);
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border: 1px solid rgba(255,255,255,0.5); text-align: center;
}
.bubble-arrow {
  width: 0; height: 0;
  border-left: 8px solid transparent; border-right: 8px solid transparent;
  border-top: 8px solid rgba(255,255,255,0.95);
  margin: 0 auto;
}
.bubble-enter-active { animation: bubble-in 0.3s ease-out; }
.bubble-leave-active { animation: bubble-out 0.2s ease-in; }
@keyframes bubble-in {
  from { opacity: 0; transform: translateX(-50%) translateY(-10px) scale(0.9); }
  to { opacity: 1; transform: translateX(-50%) translateY(0) scale(1); }
}
@keyframes bubble-out {
  from { opacity: 1; transform: translateX(-50%) scale(1); }
  to { opacity: 0; transform: translateX(-50%) scale(0.9); }
}

/* 教师信息 */
.teacher-info { text-align: center; padding: 14px 20px 0; }
.teacher-name { font-size: 20px; font-weight: 700; color: var(--text-primary); margin: 0; }
.teacher-status { display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 4px; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; }
.status-dot.online { background: #22c55e; animation: status-pulse 2s ease-in-out infinite; }
@keyframes status-pulse {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
  50% { box-shadow: 0 0 0 6px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}
.status-text { font-size: 13px; color: var(--text-secondary); }
.speaking-tag {
  font-size: 12px; padding: 2px 10px; border-radius: 10px;
  background: linear-gradient(135deg, #fce7f3, #e0e7ff);
  color: var(--primary); font-weight: 600; animation: pulse-tag 1.5s infinite;
}
@keyframes pulse-tag { 0%,100%{opacity:1} 50%{opacity:0.6} }

/* 控制栏 */
.control-bar { display: flex; gap: 8px; padding: 14px 16px 0; justify-content: center; flex-wrap: wrap; }
.ctrl-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 7px 14px; border-radius: 18px;
  border: 1.5px solid var(--border); background: var(--bg-card);
  cursor: pointer; font-size: 12px; font-weight: 600;
  color: var(--text-secondary); transition: all 0.25s;
}
.ctrl-btn:hover { border-color: var(--primary-light); color: var(--primary); background: var(--primary-bg); transform: translateY(-1px); }
.ctrl-btn.active {
  background: var(--gradient); color: #fff; border-color: transparent;
  box-shadow: 0 3px 12px rgba(79,110,247,0.25);
}
.stop-btn { border-color: var(--accent-red) !important; color: var(--accent-red) !important; }
.stop-btn:hover { background: #fef2f2 !important; }

/* 进度卡 */
.progress-card { margin: 14px 16px 16px; padding: 14px; background: var(--bg); border-radius: var(--radius-sm); border: 1px solid var(--border); }
.stat-row { display: flex; align-items: center; justify-content: space-around; }
.stat-item { flex: 1; text-align: center; }
.stat-value { font-size: 20px; font-weight: 800; color: var(--primary); }
.stat-unit { font-size: 12px; font-weight: 600; }
.stat-label { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.stat-divider { width: 1px; height: 26px; background: var(--border); }

/* ===== 对话卡 ===== */
.chat-card {
  background: var(--bg-card); border-radius: var(--radius); box-shadow: var(--shadow);
  display: flex; flex-direction: column; overflow: hidden; border: 1px solid rgba(0,0,0,0.03);
}
.chat-head {
  padding: 14px 20px; border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(to bottom, #fafbff, var(--bg-card));
}
.chat-head-left { display: flex; align-items: center; gap: 12px; }
.chat-head-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--gradient); display: flex; align-items: center; justify-content: center;
  font-size: 20px; box-shadow: 0 4px 12px rgba(79,110,247,0.2);
}
.chat-head-name { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.chat-head-sub { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.chat-head-badge {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 12px; background: var(--primary-bg); border-radius: 20px;
  font-size: 12px; font-weight: 500; color: var(--primary);
}
.badge-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--primary); animation: badge-blink 2s infinite; }
@keyframes badge-blink { 0%,100%{opacity:1} 50%{opacity:0.4} }

.chat-body { flex: 1; overflow-y: auto; padding: 20px; }
.chat-empty { text-align: center; padding: 40px 20px; }
.empty-icon { font-size: 48px; margin-bottom: 10px; }
.empty-title { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 6px; }
.empty-hint { font-size: 13px; color: var(--text-muted); margin-bottom: 16px; }
.quick-questions { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; max-width: 380px; margin: 0 auto; }
.quick-btn {
  padding: 7px 14px; border-radius: 18px;
  border: 1.5px solid var(--border); background: var(--bg-card);
  cursor: pointer; font-size: 12px; color: var(--text-secondary);
  transition: all 0.2s; font-weight: 500;
}
.quick-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-bg); }

.msg-content { flex: 1; min-width: 0; }
.msg-actions { display: flex; gap: 6px; margin-top: 6px; }
.action-btn {
  display: flex; align-items: center; gap: 4px;
  padding: 3px 10px; border-radius: 10px;
  border: 1px solid var(--border); background: var(--bg-card);
  cursor: pointer; font-size: 11px; color: var(--text-muted); transition: all 0.2s;
}
.action-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-bg); }

.chat-input-bar {
  padding: 14px 20px; border-top: 1px solid var(--border);
  display: flex; gap: 12px; align-items: center;
  background: linear-gradient(to top, #fafbff, var(--bg-card));
}
.input-wrapper { flex: 1; }
.input-wrapper :deep(.el-input__wrapper) {
  border-radius: 22px; padding: 4px 16px;
  box-shadow: 0 0 0 1px var(--border) inset; transition: all 0.25s;
}
.input-wrapper :deep(.el-input__wrapper:focus-within) { box-shadow: 0 0 0 2px var(--primary-light) inset; }
.btn-send {
  height: 42px; padding: 0 22px; border-radius: 21px;
  background: var(--gradient) !important; border: none !important;
  color: #fff; font-weight: 600; font-size: 14px; flex-shrink: 0;
  box-shadow: 0 4px 14px rgba(79,110,247,0.3); transition: all 0.25s;
}
.btn-send:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(79,110,247,0.4); }

/* ===== 响应式 ===== */
@media (max-width: 1100px) {
  .teacher-layout { grid-template-columns: 1fr; height: auto; }
  .live2d-stage { height: 300px; }
  .chat-card { height: 500px; }
}
@media (max-width: 600px) {
  .live2d-stage { height: 240px; }
  .quick-questions { flex-direction: column; }
  .chat-head-badge { display: none; }
}
</style>
