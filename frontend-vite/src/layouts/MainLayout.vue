<template>
  <div class="app-shell">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed }">
      <div class="sidebar-logo" @click="$router.push('/')">
        <span class="logo-icon">🧠</span>
        <transition name="fade-text">
          <span v-show="!collapsed" class="logo-text">数据分析平台</span>
        </transition>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: $route.path === item.path }"
        >
          <el-icon :size="20"><component :is="item.icon" /></el-icon>
          <span v-show="!collapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-bottom">
        <div v-show="!collapsed" class="sidebar-promo">
          <div class="promo-text">让数据更有价值</div>
          <div class="promo-sub">让知识触手可及</div>
        </div>
        <button class="collapse-btn" @click="collapsed = !collapsed">
          <el-icon :size="18"><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
        </button>
      </div>
    </aside>

    <!-- 主区域 -->
    <div class="main-wrap">
      <!-- 顶栏 -->
      <header class="top-bar">
        <h2 class="page-title">{{ $route.meta.title || '首页' }}</h2>
        <div class="top-actions">
          <div class="search-box">
            <el-icon :size="15" color="#94a3b8"><Search /></el-icon>
            <input type="text" placeholder="搜索功能、知识点..." class="search-input" />
          </div>
          <button class="icon-btn" @click="toggleFullscreen" title="全屏">
            <el-icon :size="18"><FullScreen /></el-icon>
          </button>
          <div class="notif-wrap">
            <button class="icon-btn notif-btn">
              <el-icon :size="18"><Bell /></el-icon>
            </button>
            <span class="notif-badge">12</span>
          </div>
          <el-dropdown trigger="click">
            <div class="user-chip">
              <el-avatar :size="34" class="user-avatar">张</el-avatar>
              <span class="user-name">张同学</span>
              <el-icon :size="12" color="#94a3b8"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item>帮助中心</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="page-content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, FullScreen, Bell, ArrowDown } from '@element-plus/icons-vue'

const collapsed = ref(false)

const menuItems = [
  { path: '/', icon: 'Odometer', label: '首页' },
  { path: '/knowledge-graph', icon: 'Share', label: '知识图谱' },
  { path: '/qa', icon: 'ChatDotRound', label: 'AI 智能问答' },
  { path: '/teacher', icon: 'User', label: '数字教师' },
  { path: '/analysis', icon: 'DataAnalysis', label: '数据分析' },
]

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}
</script>

<style scoped>
.app-shell {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ==================== 侧边栏 ==================== */
.sidebar {
  width: 230px;
  background: #fff;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.4,0,0.2,1);
  flex-shrink: 0;
  z-index: 20;
}
.sidebar.collapsed { width: 68px; }

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  border-bottom: 1px solid var(--border);
  padding: 0 18px;
  flex-shrink: 0;
}
.logo-icon { font-size: 28px; }
.logo-text {
  font-size: 16px;
  font-weight: 800;
  background: linear-gradient(135deg, #4f6ef7, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
  letter-spacing: 1px;
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 14px;
  height: 46px;
  border-radius: 12px;
  margin-bottom: 4px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  font-weight: 700;
  transition: all 0.2s;
  position: relative;
}
.nav-item:hover {
  background: #f8f9fc;
  color: var(--text-primary);
}
.nav-item.active {
  background: var(--primary-bg);
  color: var(--primary);
  font-weight: 600;
}
.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: var(--primary);
  border-radius: 0 4px 4px 0;
}
.nav-label { white-space: nowrap; }

.sidebar-bottom {
  padding: 12px 10px;
  border-top: 1px solid var(--border);
  text-align: center;
  flex-shrink: 0;
}
.sidebar-promo { padding: 12px 0 8px; }
.promo-text { font-size: 13px; font-weight: 700; color: var(--primary); margin-bottom: 2px; }
.promo-sub { font-size: 11px; color: var(--text-muted); }

.collapse-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  width: 100%;
  padding: 6px;
  border-radius: 8px;
  transition: all 0.2s;
}
.collapse-btn:hover { color: var(--primary); background: #f8f9fc; }

/* ==================== 顶栏 ==================== */
.main-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: var(--bg);
}

.top-bar {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.page-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f8f9fc;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0 14px;
  height: 38px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-box:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79,110,247,0.08);
}
.search-input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-primary);
  width: 160px;
}
.search-input::placeholder { color: var(--text-muted); }

.icon-btn {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
}
.icon-btn:hover {
  background: #f8f9fc;
  color: var(--primary);
  border-color: var(--primary-light);
}

.notif-wrap { position: relative; }
.notif-btn { position: relative; }
.notif-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: var(--accent-red);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
  line-height: 1;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 12px 4px 4px;
  border-radius: 24px;
  transition: background 0.2s;
}
.user-chip:hover { background: #f8f9fc; }
.user-avatar {
  background: linear-gradient(135deg, #4f6ef7, #7c3aed);
  color: #fff;
  font-size: 14px;
  font-weight: 700;
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

/* ==================== 内容区 ==================== */
.page-content {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
}

/* ==================== 过渡 ==================== */
.page-enter-active, .page-leave-active { transition: opacity 0.2s ease; }
.page-enter-from, .page-leave-to { opacity: 0; }
.fade-text-enter-active, .fade-text-leave-active { transition: opacity 0.15s; }
.fade-text-enter-from, .fade-text-leave-to { opacity: 0; }

/* ==================== 响应式 ==================== */
@media (max-width: 1200px) {
  .sidebar { width: 68px; }
  .sidebar .nav-label,
  .sidebar .logo-text,
  .sidebar .sidebar-promo { display: none; }
}
</style>
