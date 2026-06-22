import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue'), meta: { title: '仪表盘' } },
      { path: 'knowledge-graph', name: 'KnowledgeGraph', component: () => import('@/pages/KnowledgeGraph.vue'), meta: { title: '知识图谱' } },
      { path: 'qa', name: 'QA', component: () => import('@/pages/QA.vue'), meta: { title: '智能问答' } },
      { path: 'teacher', name: 'Teacher', component: () => import('@/pages/Teacher.vue'), meta: { title: '数字教师' } },
      { path: 'analysis', name: 'Analysis', component: () => import('@/pages/Analysis.vue'), meta: { title: '数据分析' } },
      { path: 'files', name: 'Files', component: () => import('@/pages/Files.vue'), meta: { title: '文件管理' } },
      { path: 'system', name: 'System', component: () => import('@/pages/System.vue'), meta: { title: '系统管理' } },
      { path: 'profile', name: 'Profile', component: () => import('@/pages/Profile.vue'), meta: { title: '个人设置' } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 导航守卫：未登录跳转登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

// 设置页面标题
router.afterEach((to) => {
  document.title = (to.meta.title || '仪表盘') + ' - 数据分析平台'
})

export default router
