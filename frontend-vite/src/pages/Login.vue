<template>
  <div class="login-page">
    <!-- Decorative circles -->
    <div class="circle circle-top-right"></div>
    <div class="circle circle-bottom-left"></div>

    <div class="login-card">
      <!-- Header -->
      <div class="login-header">
        <div class="logo">🧠</div>
        <h1 class="title">课程数据分析平台</h1>
        <p class="subtitle">基于知识图谱与大模型的智能学习系统</p>
      </div>

      <el-tabs v-model="activeTab" stretch>
        <!-- Login Tab -->
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" class="login-form" @submit.prevent="handleLogin">
            <el-form-item>
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                show-password
                size="large"
                :prefix-icon="Lock"
              />
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="submit-btn"
                :loading="loginLoading"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
          <div class="switch-link">
            还没有账号？
            <a href="#" @click.prevent="activeTab = 'register'">立即注册</a>
          </div>
        </el-tab-pane>

        <!-- Register Tab -->
        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" class="login-form" @submit.prevent="handleRegister">
            <el-form-item>
              <el-input
                v-model="registerForm.username"
                placeholder="请输入用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="registerForm.email"
                placeholder="请输入邮箱"
                size="large"
                :prefix-icon="Message"
              />
            </el-form-item>
            <el-form-item>
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请输入密码（至少6位）"
                show-password
                size="large"
                :prefix-icon="Lock"
                minlength="6"
              />
            </el-form-item>
            <el-form-item>
              <el-radio-group v-model="registerForm.role" class="role-group">
                <el-radio value="student">学生</el-radio>
                <el-radio value="teacher">教师</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button
                type="primary"
                class="submit-btn"
                :loading="registerLoading"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
          <div class="switch-link">
            已有账号？
            <a href="#" @click.prevent="activeTab = 'login'">返回登录</a>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api, { authAPI } from '@/api'

const router = useRouter()

const activeTab = ref('login')
const loginLoading = ref(false)
const registerLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'student'
})

const emit = defineEmits(['login-success'])

async function handleLogin() {
  if (!loginForm.username || !loginForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loginLoading.value = true
  try {
    const res = await authAPI.login(loginForm.username, loginForm.password)
    api.setToken(res.token || res.data?.token)
    api.setUser(res.user || res.data?.user)
    ElMessage.success('登录成功')
    emit('login-success')
    router.push('/')
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.message || '登录失败，请重试')
  } finally {
    loginLoading.value = false
  }
}

async function handleRegister() {
  if (!registerForm.username || !registerForm.email || !registerForm.password) {
    ElMessage.warning('请填写完整的注册信息')
    return
  }
  if (registerForm.password.length < 6) {
    ElMessage.warning('密码长度不能少于6位')
    return
  }
  registerLoading.value = true
  try {
    await authAPI.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      role: registerForm.role
    })
    ElMessage.success('注册成功，请登录')
    activeTab.value = 'login'
    loginForm.username = registerForm.username
  } catch (err) {
    ElMessage.error(err?.response?.data?.message || err?.message || '注册失败，请重试')
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1e1b4b 0%, #312e81 30%, #4f46e5 70%, #6366f1 100%);
  position: relative;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  pointer-events: none;
}

.circle-top-right {
  width: 600px;
  height: 600px;
  top: -200px;
  right: -200px;
  background: rgba(255, 255, 255, 0.03);
}

.circle-bottom-left {
  width: 400px;
  height: 400px;
  bottom: -100px;
  left: -100px;
  background: rgba(255, 255, 255, 0.04);
}

.login-card {
  width: 440px;
  max-width: 90vw;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.3), 0 10px 30px rgba(0, 0, 0, 0.2);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.logo {
  font-size: 48px;
  margin-bottom: 12px;
}

.title {
  font-size: 22px;
  font-weight: 700;
  color: #1e1b4b;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.login-form {
  margin-top: 8px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  border: none;
  border-radius: 10px;
  letter-spacing: 2px;
}

.submit-btn:hover {
  background: linear-gradient(135deg, #4338ca 0%, #4f46e5 100%);
}

.role-group {
  width: 100%;
  display: flex;
  gap: 24px;
}

.switch-link {
  text-align: center;
  margin-top: 12px;
  font-size: 14px;
  color: #94a3b8;
}

.switch-link a {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.switch-link a:hover {
  text-decoration: underline;
}

:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
}

:deep(.el-tabs__active-bar) {
  background-color: #4f46e5;
}

:deep(.el-tabs__item.is-active) {
  color: #4f46e5;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4f46e5 inset;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #4f46e5 inset;
}
</style>
