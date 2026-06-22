/**
 * API 抽象层
 * USE_MOCK = true  使用内置模拟数据（当前）
 * USE_MOCK = false 调用真实 FastAPI 后端
 */
import { mockGet, mockPost, mockPut, mockDelete } from './mock'

const USE_MOCK = false
const BASE_URL = '/api/v1'

// ---------------------------------------------------------------------------
// Token 管理
// ---------------------------------------------------------------------------
function getToken() {
  return localStorage.getItem('token') || ''
}

function setToken(token) {
  localStorage.setItem('token', token)
}

function removeToken() {
  localStorage.removeItem('token')
}

// ---------------------------------------------------------------------------
// 用户数据管理（localStorage）
// ---------------------------------------------------------------------------
function getUser() {
  try {
    const raw = localStorage.getItem('user')
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function setUser(user) {
  localStorage.setItem('user', JSON.stringify(user))
}

function removeUser() {
  localStorage.removeItem('user')
}

// ---------------------------------------------------------------------------
// 通用请求头
// ---------------------------------------------------------------------------
function authHeaders() {
  const token = getToken()
  return token ? { Authorization: 'Bearer ' + token } : {}
}

// ---------------------------------------------------------------------------
// HTTP 方法
// ---------------------------------------------------------------------------
async function get(path, params = {}) {
  if (USE_MOCK) return mockGet(path, params)
  const url = new URL(BASE_URL + path, window.location.origin)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v)
  })
  const res = await fetch(url, { headers: authHeaders() })
  return res.json()
}

async function post(path, body = {}) {
  if (USE_MOCK) return mockPost(path, body)
  const res = await fetch(BASE_URL + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  return res.json()
}

async function put(path, body = {}) {
  if (USE_MOCK) return mockPut(path, body)
  const res = await fetch(BASE_URL + path, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify(body),
  })
  return res.json()
}

async function del(path) {
  if (USE_MOCK) return mockDelete(path)
  const res = await fetch(BASE_URL + path, {
    method: 'DELETE',
    headers: authHeaders(),
  })
  return res.json()
}

async function upload(path, file, data = {}) {
  if (USE_MOCK) return mockPost(path, data) // mock 环境不处理真实文件
  const formData = new FormData()
  formData.append('file', file)
  Object.entries(data).forEach(([k, v]) => {
    if (v !== undefined && v !== null) formData.append(k, v)
  })
  const res = await fetch(BASE_URL + path, {
    method: 'POST',
    headers: authHeaders(), // 不设置 Content-Type，让浏览器自动设置 multipart boundary
    body: formData,
  })
  return res.json()
}

// ---------------------------------------------------------------------------
// API 命名空间对象
// ---------------------------------------------------------------------------
export const authAPI = {
  login: (username, password) => post('/auth/login', { username, password }),
  register: (data) => post('/auth/register', data),
  getProfile: () => get('/auth/me'),
  updateProfile: (data) => put('/auth/me', data),
  changePassword: (oldPassword, newPassword) =>
    put('/auth/password', { old_password: oldPassword, new_password: newPassword }),
}

export const graphAPI = {
  visualization: (course) => get('/graph/visualization', { course }),
  nodeDetail: (nodeId) => get(`/graph/node/${nodeId}`),
  search: (query, course) => get('/graph/search', { keyword: query, course }),
  path: (source, target) => get('/graph/path', { source, target }),
  tree: (course) => get(`/graph/tree/${course}`),
  stats: () => get('/graph/stats'),
}

export const qaAPI = {
  ask: (question, sessionId, enableRag, enableGraph) =>
    post('/qa/ask-sync', { question, session_id: sessionId, enable_rag: enableRag, enable_graph: enableGraph }),
  history: (sessionId) => get(`/qa/history/${sessionId}`),
  sessions: () => get('/qa/sessions'),
  createSession: (title, course) => post('/qa/sessions', { title, course }),
  deleteSession: (sessionId) => del(`/qa/sessions/${sessionId}`),
  feedback: (answerId, rating, isHelpful, comment) =>
    post(`/qa/answers/${answerId}/feedback`, { rating, is_helpful: isHelpful, comment }),
}

export const teacherAPI = {
  chat: (question, emotion) => post('/teacher/chat', { question, emotion }),
  avatar: () => get('/teacher/avatar'),
  progress: () => get('/teacher/progress'),
}

export const dashboardAPI = {
  overview: () => get('/dashboard/overview'),
  questionTrend: (params) => get('/dashboard/question-trend', params),
  topicHeatmap: (params) => get('/dashboard/topic-heatmap', params),
  userActivity: (params) => get('/dashboard/user-activity', params),
  satisfaction: (params) => get('/dashboard/satisfaction', params),
  mastery: (params) => get('/dashboard/mastery-radar', params),
}

export const filesAPI = {
  list: (params) => get('/files', params),
  upload: (file, course, tags) => upload('/files/upload', file, { course, tags }),
  status: (fileId) => get(`/files/${fileId}/status`),
  delete: (fileId) => del(`/files/${fileId}`),
  rebuildIndex: () => post('/files/rebuild-index', {}),
}

export const systemAPI = {
  health: () => get('/system/health'),
  modelStatus: () => get('/system/model-status'),
  getConfig: () => get('/system/config'),
  updateConfig: (config) => put('/system/config', config),
  announcements: () => get('/system/announcements'),
}

// ---------------------------------------------------------------------------
// 默认导出 — 完整 API 工具对象
// ---------------------------------------------------------------------------
export default {
  get,
  post,
  put,
  del,
  upload,
  setToken,
  getToken,
  removeToken,
  getUser,
  setUser,
  removeUser,
  USE_MOCK,
}
