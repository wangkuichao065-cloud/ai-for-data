/**
 * API 抽象层
 * USE_MOCK = true  使用内置模拟数据（当前）
 * USE_MOCK = false 调用真实 FastAPI 后端
 */
import { mockGet, mockPost } from './mock'

const USE_MOCK = true
const BASE_URL = '/api/v1'

function getToken() {
  return localStorage.getItem('token') || ''
}

async function get(path, params = {}) {
  if (USE_MOCK) return mockGet(path, params)
  const url = new URL(BASE_URL + path, window.location.origin)
  Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))
  const res = await fetch(url, {
    headers: { Authorization: 'Bearer ' + getToken() },
  })
  return res.json()
}

async function post(path, body = {}) {
  if (USE_MOCK) return mockPost(path, body)
  const res = await fetch(BASE_URL + path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer ' + getToken(),
    },
    body: JSON.stringify(body),
  })
  return res.json()
}

export default { get, post, USE_MOCK }
