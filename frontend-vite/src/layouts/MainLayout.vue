<template>
  <el-container class="app-shell">
    <!-- 侧边栏 -->
    <el-aside :width="collapsed ? '64px' : '220px'" class="sidebar">
      <div class="sidebar-logo" @click="$router.push('/')">
        <span class="logo-icon">🧠</span>
        <transition name="fade-text">
          <span v-show="!collapsed" class="logo-text">数据分析平台</span>
        </transition>
      </div>

      <el-menu
        :default-active="$route.path"
        :collapse="collapsed"
        router
        background-color="transparent"
        text-color="rgba(255,255,255,0.65)"
        active-text-color="#ffffff"
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/knowledge-graph">
          <el-icon><Share /></el-icon>
          <template #title>知识图谱</template>
        </el-menu-item>
        <el-menu-item index="/qa">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>智能问答</template>
        </el-menu-item>
        <el-menu-item index="/teacher">
          <el-icon><User /></el-icon>
          <template #title>数字教师</template>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>
        <el-menu-item index="/files">
          <el-icon><FolderOpened /></el-icon>
          <template #title>文件管理</template>
        </el-menu-item>
        <el-menu-item index="/system">
          <el-icon><Setting /></el-icon>
          <template #title>系统管理</template>
        </el-menu-item>
      </el-menu>

      <div class="sidebar-footer">
        <el-button text class="collapse-btn" @click="collapsed = !collapsed">
          <el-icon><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
        </el-button>
      </div>
    </el-aside>

    <!-- 主区域 -->
    <el-container class="main-container">
      <header class="app-header">
        <h2 class="page-title">{{ $route.meta.title || '仪表盘' }}</h2>
        <div class="header-actions">
          <!-- 全屏切换 -->
          <el-button circle :icon="isFullscreen ? CopyDocument : FullScreen" size="default" @click="toggleFullscreen" />
          <!-- 通知 -->
          <el-badge :value="announcementCount" :max="99" :hidden="!announcementCount">
            <el-button circle :icon="Bell" size="default" />
          </el-badge>
          <!-- 用户下拉 -->
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-chip">
              <el-avatar :size="30" class="user-avatar">{{ avatarLetter }}</el-avatar>
              <span class="user-name">{{ displayName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人设置
                </el-dropdown-item>
                <el-dropdown-item command="system">
                  <el-icon><Setting /></el-icon>系统管理
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, FullScreen, CopyDocument } from '@element-plus/icons-vue'

const router = useRouter()
const collapsed = ref(false)
const isFullscreen = ref(false)
const announcementCount = ref(0)

// 用户信息
const displayName = computed(() => {
  try {
    const u = JSON.parse(localStorage.getItem('user') || '{}')
    return u.username || u.name || '学生01'
  } catch { return '学生01' }
})

const avatarLetter = computed(() => {
  const n = displayName.value
  return n ? n.charAt(0).toUpperCase() : 'S'
})

// 全屏切换
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
    isFullscreen.value = true
  } else {
    document.exitFullscreen()
    isFullscreen.value = false
  }
}

document.addEventListener('fullscreenchange', () => {
  isFullscreen.value = !!document.fullscreenElement
})

// 下拉菜单命令
function handleCommand(cmd) {
  if (cmd === 'profile') router.push('/profile')
  else if (cmd === 'system') router.push('/system')
  else if (cmd === 'logout') {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }
}

// 加载公告数量
onMounted(async () => {
  try {
    const { systemAPI } = await import('@/api/index.js')
    const res = await systemAPI.announcements()
    announcementCount.value = Array.isArray(res) ? res.length : 0
  } catch { /* 静默 */ }
})
</script>

<style scoped>
.app-shell {
  height: 100vh;
  overflow: hidden;
}

/* ---- 侧边栏 ---- */
.sidebar {
  background: linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #3730a3 100%);
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.logo-icon { font-size: 26px; }
.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 1px;
}

.sidebar-menu {
  flex: 1;
  border: none !important;
  padding: 8px;
  overflow-y: auto;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  border-radius: 10px;
  margin-bottom: 4px;
  transition: all 0.25s;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.08) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #fff !important;
  font-weight: 600;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  text-align: center;
  flex-shrink: 0;
}

.collapse-btn { color: rgba(255, 255, 255, 0.5) !important; }
.collapse-btn:hover { color: #fff !important; }

/* ---- 主区域 ---- */
.main-container {
  background: var(--bg);
  overflow: hidden;
}

.app-header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.page-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 20px;
  transition: background 0.2s;
}
.user-chip:hover { background: var(--bg); }

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
}

.user-name {
  font-size: 13px;
  color: var(--text-secondary);
}

.app-main {
  padding: 20px;
  overflow-y: auto;
  height: calc(100vh - 60px);
}

/* ---- 过渡 ---- */
.page-enter-active, .page-leave-active { transition: opacity 0.2s ease; }
.page-enter-from, .page-leave-to { opacity: 0; }
.fade-text-enter-active, .fade-text-leave-active { transition: opacity 0.15s; }
.fade-text-enter-from, .fade-text-leave-to { opacity: 0; }
</style>
