<template>
  <div class="profile-container">
    <el-card class="profile-card" shadow="hover">
      <template #header>
        <span>个人信息</span>
      </template>
      <el-form label-width="100px" style="margin-top: 20px">
        <el-form-item label="用户名">
          <el-input v-model="profile.username" disabled />
        </el-form-item>
        <el-form-item label="昵称">
          <el-input v-model="profile.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="profile.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机">
          <el-input v-model="profile.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="saveProfile">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="profile-card" shadow="hover" style="margin-top: 20px">
      <template #header>
        <span>修改密码</span>
      </template>
      <el-form label-width="100px" style="margin-top: 20px">
        <el-form-item label="当前密码">
          <el-input
            v-model="pwdForm.oldPassword"
            type="password"
            show-password
            placeholder="请输入当前密码"
          />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input
            v-model="pwdForm.newPassword"
            type="password"
            show-password
            placeholder="请输入新密码（至少6位）"
          />
        </el-form-item>
        <el-form-item label="确认密码">
          <el-input
            v-model="pwdForm.confirmPassword"
            type="password"
            show-password
            placeholder="请再次输入新密码"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="warning" :loading="changingPwd" @click="changePassword">
            修改密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api, { authAPI } from '@/api'

const profile = reactive({
  username: '',
  nickname: '',
  email: '',
  phone: ''
})

const pwdForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const saving = ref(false)
const changingPwd = ref(false)

onMounted(async () => {
  try {
    const res = await authAPI.getProfile()
    const data = res.data?.data || res.data || {}
    profile.username = data.username || ''
    profile.nickname = data.nickname || ''
    profile.email = data.email || ''
    profile.phone = data.phone || ''
  } catch (e) {
    ElMessage.error('加载个人信息失败')
  }
})

const saveProfile = async () => {
  saving.value = true
  try {
    await authAPI.updateProfile({
      nickname: profile.nickname,
      email: profile.email,
      phone: profile.phone
    })
    // Update localStorage user data
    const stored = localStorage.getItem('user')
    if (stored) {
      const user = JSON.parse(stored)
      user.nickname = profile.nickname
      user.email = profile.email
      user.phone = profile.phone
      localStorage.setItem('user', JSON.stringify(user))
    }
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const changePassword = async () => {
  if (!pwdForm.oldPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!pwdForm.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (pwdForm.newPassword.length < 6) {
    ElMessage.warning('新密码至少6位')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }

  changingPwd.value = true
  try {
    await authAPI.changePassword({
      oldPassword: pwdForm.oldPassword,
      newPassword: pwdForm.newPassword
    })
    ElMessage.success('密码修改成功')
    pwdForm.oldPassword = ''
    pwdForm.newPassword = ''
    pwdForm.confirmPassword = ''
  } catch (e) {
    ElMessage.error('密码修改失败')
  } finally {
    changingPwd.value = false
  }
}
</script>

<style scoped>
.profile-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

.profile-card {
  width: 100%;
  max-width: 600px;
}
</style>
