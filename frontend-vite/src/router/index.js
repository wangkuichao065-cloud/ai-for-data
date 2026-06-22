import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/pages/Dashboard.vue'), meta: { title: '仪表盘' } },
      { path: 'knowledge-graph', name: 'KnowledgeGraph', component: () => import('@/pages/KnowledgeGraph.vue'), meta: { title: '知识图谱' } },
      { path: 'qa', name: 'QA', component: () => import('@/pages/QA.vue'), meta: { title: '智能问答' } },
      { path: 'teacher', name: 'Teacher', component: () => import('@/pages/Teacher.vue'), meta: { title: '数字教师' } },
      { path: 'analysis', name: 'Analysis', component: () => import('@/pages/Analysis.vue'), meta: { title: '数据分析' } },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
