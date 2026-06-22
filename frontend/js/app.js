// ============================================
// App - Vue 应用初始化 & 路由配置
// 包含登录路由、导航守卫、全局状态
// ============================================

(function() {
  // ---- 全局状态（响应式） ----
  var globalState = Vue.reactive({
    user: {
      user_id: null,
      username: '',
      nickname: '',
      email: '',
      role: 'student',
      avatar: ''
    },
    loggedIn: false
  });

  // 从 localStorage 恢复用户信息
  function restoreUser() {
    var token = localStorage.getItem('token');
    var userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        globalState.user = JSON.parse(userStr);
        globalState.loggedIn = true;
      } catch (e) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
  }
  restoreUser();

  // 保存/清除用户
  function saveUser(token, user) {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    globalState.user = user;
    globalState.loggedIn = true;
  }
  function clearUser() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    globalState.user = { user_id: null, username: '', nickname: '', email: '', role: 'student', avatar: '' };
    globalState.loggedIn = false;
  }

  // ---- 路由配置 ----
  var routes = [
    { path: '/login',          component: LoginPage,          meta: { title: '登录', public: true } },
    { path: '/',                component: DashboardPage,       meta: { title: '仪表盘' } },
    { path: '/knowledge-graph', component: KnowledgeGraphPage,  meta: { title: '知识图谱' } },
    { path: '/qa',              component: QAPage,              meta: { title: '智能问答' } },
    { path: '/teacher',         component: TeacherPage,         meta: { title: '数字教师' } },
    { path: '/analysis',        component: AnalysisPage,        meta: { title: '数据分析' } },
    { path: '/files',           component: FilesPage,           meta: { title: '文件管理' } },
    { path: '/system',          component: SystemPage,          meta: { title: '系统管理' } },
    { path: '/profile',         component: ProfilePage,        meta: { title: '个人设置' } },
    { path: '/:pathMatch(.*)*', component: DashboardPage,       meta: { title: '仪表盘' } }
  ];

  var router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes: routes
  });

  // ---- 导航守卫 ----
  router.beforeEach(function(to, from, next) {
    if (to.meta && to.meta.public) {
      // 已登录用户访问登录页则跳转首页
      if (to.path === '/login' && globalState.loggedIn) {
        next('/');
      } else {
        next();
      }
    } else {
      // 需要认证的页面
      if (!globalState.loggedIn) {
        next('/login');
      } else {
        next();
      }
    }
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

      // 侧边栏菜单
      var menuItems = [
        { index: '/',              icon: 'Odometer',  title: '仪表盘' },
        { index: '/knowledge-graph', icon: 'Share',   title: '知识图谱' },
        { index: '/qa',             icon: 'ChatDotRound', title: '智能问答' },
        { index: '/teacher',        icon: 'UserFilled',   title: '数字教师' },
        { index: '/analysis',       icon: 'TrendCharts',  title: '数据分析' },
        { index: '/files',          icon: 'FolderOpened',  title: '文件管理' },
        { index: '/system',         icon: 'Setting',      title: '系统管理' }
      ];

      // 用户显示名
      var displayName = Vue.computed(function() {
        return globalState.user.nickname || globalState.user.username || '用户';
      });

      // 用户角色标签
      var roleLabel = Vue.computed(function() {
        var map = { student: '学生', teacher: '教师', admin: '管理员' };
        return map[globalState.user.role] || '用户';
      });

      // 跳转个人设置
      function goProfile() { router.push('/profile'); }

      // 退出登录
      async function logout() {
        try {
          await ElementPlus.ElMessageBox.confirm('确定要退出登录吗？', '提示', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          });
          try { await API.auth.logout(); } catch (e) { /* 忽略网络错误 */ }
          clearUser();
          router.push('/login');
        } catch (e) { /* 用户取消 */ }
      }

      // 个人设置
      function goSettings() { router.push('/profile'); }

      // 系统管理
      function goSystem() { router.push('/system'); }

      // 下拉菜单命令处理
      function handleCommand(cmd) {
        if (cmd === 'profile') goProfile();
        else if (cmd === 'system') goSystem();
        else if (cmd === 'logout') logout();
      }

      // 公告数量
      var announcementCount = Vue.ref(0);

      // 加载公告数量
      async function loadAnnouncements() {
        if (!globalState.loggedIn) return;
        try {
          var res = await API.system.announcements();
          if (res.code === 200 && res.data) {
            announcementCount.value = Array.isArray(res.data) ? res.data.length : (res.data.total || 0);
          }
        } catch (e) { /* 静默失败 */ }
      }
      // 延迟加载公告
      setTimeout(loadAnnouncements, 2000);

      return {
        isCollapse: isCollapse,
        currentRoute: currentRoute,
        pageTitle: pageTitle,
        menuItems: menuItems,
        globalState: globalState,
        displayName: displayName,
        roleLabel: roleLabel,
        announcementCount: announcementCount,
        goProfile: goProfile,
        logout: logout,
        handleCommand: handleCommand
      };
    }
  });

  // ---- 注册 Element Plus ----
  app.use(ElementPlus);
  app.use(router);

  // ---- 注册所有 Element Plus 图标 ----
  for (var key in ElementPlusIconsVue) {
    app.component(key, ElementPlusIconsVue[key]);
  }

  // ---- 全局错误处理 ----
  app.config.errorHandler = function(err, vm, info) {
    console.error('Vue Error:', err, info);
    ElementPlus.ElMessage.error('页面发生错误: ' + (err.message || err));
  };

  // ---- 挂载 ----
  app.mount('#app');
})();
