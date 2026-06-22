// ============================================
// App - Vue 应用初始化 & 路由配置
// ============================================

(function() {
  // ---- 路由配置 ----
  var routes = [
    { path: '/',                component: DashboardPage,       meta: { title: '仪表盘' } },
    { path: '/knowledge-graph', component: KnowledgeGraphPage,  meta: { title: '知识图谱' } },
    { path: '/qa',              component: QAPage,              meta: { title: '智能问答' } },
    { path: '/teacher',         component: TeacherPage,         meta: { title: '数字教师' } },
    { path: '/analysis',        component: AnalysisPage,        meta: { title: '数据分析' } }
  ];

  var router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes: routes
  });

  // ---- 创建 Vue 应用 ----
  var app = Vue.createApp({
    setup() {
      var isCollapse = Vue.ref(false);
      var routeInstance = VueRouter.useRoute();

      var currentRoute = Vue.computed(function() {
        return routeInstance.path;
      });

      var pageTitle = Vue.computed(function() {
        return (routeInstance.meta && routeInstance.meta.title) || '仪表盘';
      });

      return { isCollapse: isCollapse, currentRoute: currentRoute, pageTitle: pageTitle };
    }
  });

  // ---- 注册 Element Plus ----
  app.use(ElementPlus);
  app.use(router);

  // ---- 注册所有 Element Plus 图标 ----
  for (var key in ElementPlusIconsVue) {
    app.component(key, ElementPlusIconsVue[key]);
  }

  // ---- 挂载 ----
  app.mount('#app');
})();
